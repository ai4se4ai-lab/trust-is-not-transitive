"""E5: is the conformance oracle strong? AST mutants of the checker and engine.

Each mutant is a copy of src/ with one operator changed in `tint.hsl`. A mutant is
killed if the differential oracle reports a disagreement, a unit test of the hierarchy
language fails, or the mutant crashes. The result records which of these killed it.
Every survivor is listed for inspection, because some mutants are equivalent.
"""
from __future__ import annotations
import ast
import copy
import json
import multiprocessing as mp
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
ROOT = Path(__file__).resolve().parents[2]
TARGETS = {'src/tint/hsl/__init__.py': {'check', 'credited', 'usable', '_order', '_structure', '_refine', '_mask', '_bits', 'successors', 'gated', 'necessary', 'witness_model', 'ancestors'},
           'src/tint/hsl/engine.py': {'_run', '_unestablished', '_holds', '_condition', '_established', '_consult', 'view_for', 'evaluate', 'certify', 'affected_routes',
                                      'prefix_fingerprints', 'component_digest', '_value_digest', '_instance_state', '_probability', 'valid', '_identities', '__init__'}}
SWAPS = {ast.In: ast.NotIn, ast.NotIn: ast.In, ast.Eq: ast.NotEq, ast.NotEq: ast.Eq, ast.LtE: ast.Lt, ast.Is: ast.IsNot, ast.IsNot: ast.Is}
BIN = {ast.BitAnd: ast.BitOr, ast.BitOr: ast.BitAnd, ast.Sub: ast.BitOr}


def sites(tree: ast.AST, functions: set[str]):
    """Yield (kind, node index in walk order, detail) for every mutation site."""
    for function in ast.walk(tree):
        if not (isinstance(function, ast.FunctionDef) and function.name in functions):
            continue
        for node in ast.walk(function):
            if isinstance(node, ast.Compare) and type(node.ops[0]) in SWAPS:
                yield node, 'compare'
            elif isinstance(node, ast.BoolOp):
                yield node, 'boolop'
            elif isinstance(node, ast.BinOp) and type(node.op) in BIN:
                yield node, 'binop'
            elif isinstance(node, ast.AugAssign) and type(node.op) in BIN:
                yield node, 'augop'
            elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
                yield node, 'dropnot'
            elif isinstance(node, (ast.If, ast.IfExp)):
                yield node, 'negate-if'
            elif isinstance(node, ast.Constant) and node.value in (True, False, 0, 1) and type(node.value) in (bool, int):
                yield node, 'const'
            elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Name) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                yield node, 'noop-assign'


def apply(node, kind):
    if kind == 'compare':
        node.ops[0] = SWAPS[type(node.ops[0])]()
    elif kind == 'boolop':
        node.op = ast.Or() if isinstance(node.op, ast.And) else ast.And()
    elif kind in ('binop', 'augop'):
        node.op = BIN[type(node.op)]()
    elif kind == 'dropnot':
        node.op = ast.UAdd()  # + on a bool keeps it truthy-equivalent to the operand
    elif kind == 'negate-if':
        node.test = ast.UnaryOp(ast.Not(), node.test)
    elif kind == 'const':
        node.value = (not node.value) if isinstance(node.value, bool) else 1 - node.value
    elif kind == 'noop-assign':
        node.value = ast.Constant(None)


def all_mutants():
    result = []
    for relative, functions in TARGETS.items():
        source = (ROOT / relative).read_text(encoding='utf-8')
        count = sum(1 for _ in sites(ast.parse(source), functions))
        for index in range(count):
            result.append((relative, index))
    return result


ORACLE = """
import sys, json
sys.path.insert(0, sys.argv[1] + '/experiments/v2')
sys.path.insert(0, sys.argv[1] + '/src')
sys.path.insert(0, sys.argv[1] + '/formal/calculus')
try:
    import harness
    r = harness.differential(4242, 400, 4)
    bad = sum(r[k] for k in ['check_disagreements', 'semantic_disagreements', 'engine_disagreements', 'route_disagreements', 'witness_failures', 'unsafe_accepted', 'residual_disagreements'])
    differential = 'detected' if bad else 'missed'
except Exception:
    differential = 'crash'
import pytest
unit = pytest.main(['-x', '-q', '-p', 'no:cacheprovider', sys.argv[1] + '/tests/test_hsl.py', sys.argv[1] + '/tests/test_hsl_oracle.py'])
print(json.dumps({'differential': differential, 'unit': unit != 0}))
"""


def run_mutant(item):
    relative, index = item
    functions = TARGETS[relative]
    source = (ROOT / relative).read_text(encoding='utf-8')
    tree = ast.parse(source)
    node, kind = list(sites(tree, functions))[index]
    line = getattr(node, 'lineno', 0)
    before = ast.unparse(node)[:90]
    apply(node, kind)
    after = ast.unparse(node)[:90]
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        shutil.copytree(ROOT / 'src', base / 'src', ignore=shutil.ignore_patterns('__pycache__'))
        (base / 'experiments/v2').mkdir(parents=True)
        shutil.copy(ROOT / 'experiments/v2/harness.py', base / 'experiments/v2/harness.py')
        (base / 'tests').mkdir()
        for name in ['test_hsl.py', 'test_hsl_oracle.py']:
            shutil.copy(ROOT / 'tests' / name, base / 'tests' / name)
        (base / 'formal/calculus').mkdir(parents=True)
        shutil.copy(ROOT / 'formal/calculus/reference.py', base / 'formal/calculus/reference.py')
        (base / relative).write_text(ast.unparse(tree), encoding='utf-8')
        (base / 'oracle.py').write_text(ORACLE, encoding='utf-8')
        try:
            done = subprocess.run([sys.executable, str(base / 'oracle.py'), str(base)], capture_output=True, text=True, timeout=240, cwd=tmp, env={**os.environ, 'PYTHONPATH': str(base / 'src')})
            if done.returncode != 0:
                differential, unit = 'crash', True
            else:
                result = json.loads(done.stdout.strip().splitlines()[-1])
                differential, unit = result['differential'], result['unit']
            status = 'survived' if differential == 'missed' and not unit else 'killed'
        except subprocess.TimeoutExpired:
            status, differential, unit = 'killed', 'timeout', False
    return {'file': relative, 'index': index, 'line': line, 'kind': kind, 'before': before, 'after': after, 'status': status, 'differential': differential, 'unit': unit}


def main():
    items = all_mutants()
    print(len(items), 'mutants', flush=True)
    with mp.Pool(max(os.cpu_count() // 2, 2)) as pool:
        rows = pool.map(run_mutant, items, chunksize=1)
    survived = [r for r in rows if r['status'] == 'survived']
    modes = {'differential_only': sum(r['differential'] == 'detected' for r in rows), 'crash_or_timeout': sum(r['differential'] in ('crash', 'timeout') for r in rows),
             'unit_only': sum(r['differential'] == 'missed' and r['unit'] for r in rows)}
    (ROOT / 'results/v2/e5_mutation.json').write_text(json.dumps({'mutants': len(rows), 'killed': len(rows) - len(survived), 'modes': modes, 'rows': rows}, indent=1) + '\n', encoding='utf-8')
    print(len(rows) - len(survived), 'of', len(rows), 'killed')
    for r in survived:
        print(r['file'].split('/')[-1], r['line'], r['kind'], '|', r['before'], '=>', r['after'])


if __name__ == '__main__':
    main()
