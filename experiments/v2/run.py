"""Experiments E3-E13 of experiments/v2/PROTOCOL.md. Usage: run.py [e3 e4 ...]. No LLM or network."""
from __future__ import annotations
from dataclasses import replace
import gzip
import json
import math
import multiprocessing as mp
import os
from pathlib import Path
import platform
import random
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'experiments/v2'), str(ROOT)]
import harness
from harness import *
import numpy as np
import z3
from tint.calibration import binomial_upper
from tint.hsl import Layer, gated, necessary, parse, successors, credited
from tint.hsl.engine import Engine, Proposal, RouteCertificate, affected_routes, certify, prefix_fingerprints
import tint.hsl.rules as rules_module

OUT = ROOT / 'results/v2'
MASTER = 20261031
TIMEOUT = 60.0
WORKERS = max(os.cpu_count() - 2, 1)


def save(name, value):
    (OUT / (name + '.json')).parent.mkdir(parents=True, exist_ok=True)
    (OUT / (name + '.json')).write_text(json.dumps(value, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    print(name, json.dumps(value)[:400], flush=True)


# ---------------------------------------------------------------- E3 bounded exhaustive
def e3_worker(args):
    size, first, stride = args
    count = accepted = equation = semantic = searched = 0
    pick = random.Random(MASTER + 3 + size * 1000 + first)
    for h in enumerate_small(size, first):
        search = stride == 1 or pick.randrange(stride) == 0
        a, b, c = check_agreement(h, search)
        count += 1; accepted += a; equation += a != b
        if search:
            searched += 1; semantic += a != c
    return count, accepted, equation, semantic, searched


def e3():
    """Every reachable hierarchy of up to four nodes: checker vs. equations for all; model search
    through wf and evaluate for all up to three nodes and a systematic sample of those of four."""
    rows = []
    with mp.Pool(WORKERS) as pool:
        for size, stride in [(1, 1), (2, 1), (3, 1), (4, 64)]:
            start = time.perf_counter()
            parts = pool.map(e3_worker, [(size, i, stride) for i in range(len(small_options(size, 0)))], chunksize=1)
            rows.append({'nodes': size, 'hierarchies': sum(p[0] for p in parts), 'accepted': sum(p[1] for p in parts),
                         'equation_disagreements': sum(p[2] for p in parts), 'semantic_disagreements': sum(p[3] for p in parts),
                         'model_searches': sum(p[4] for p in parts), 'seconds': round(time.perf_counter() - start, 1)})
            print(rows[-1], flush=True)
    save('e3_exhaustive', rows)


# ---------------------------------------------------------------- E4/E6 differential, witnesses
def e4_worker(args):
    seed, specs, models = args
    return differential(seed, specs, models)


def adequacy(seed, count):
    """The reference and the SMT definitions agree on concrete terms and models: check, eval and wf."""
    from z3 import Solver, Const, Store, K, ForAll, Or, And, Distinct, unsat, IntSort, IntVal
    import core
    rng = random.Random(seed)
    failures = {'check': 0, 'eval': 0, 'wf': 0}
    for _ in range(count):
        h = random_hierarchy(rng, n=rng.randint(2, 7))
        req, scope = tables(h)
        term = term_of(h)
        table = random_model(rng, h)
        passes, verdict, branch = split_model(h, table)
        everything = sorted(h.obligations)
        holds = {n: frozenset(x for x in everything if rng.random() < .85) for n in h.nodes}
        safe = frozenset(x for x in sorted(h.goals) if rng.random() < .7)
        names = sorted(set(h.goals) | set(h.obligations) | {'-'})
        obs = {x: Const('ob_' + x, core.Ob) for x in names}
        any_ob = Const('any_ob', core.Ob)
        lay = {x: Const('lay_' + x, core.Lay) for x in list(h.layers) + ['none']}
        def setz(items):
            value = K(core.Ob, False)
            for x in sorted(items):
                value = Store(value, obs[x], True)
            return value
        s = Solver()
        s.set('timeout', 30000)
        s.add(Distinct(*obs.values()), ForAll(any_ob, Or(*[any_ob == v for v in obs.values()])))
        if len(lay) > 1:
            s.add(Distinct(*lay.values()))
        s.add(core.G == setz(h.goals))
        for name, layer in lay.items():
            s.add(core.req(layer) == setz(req.get(name, frozenset())), core.scp(layer) == setz(scope.get(name, frozenset())))
        P = K(IntSort(), False); V = K(IntSort(), core.blk); W = K(IntSort(), False)
        E = K(IntSort(), K(core.Ob, False))
        for name in h.nodes:
            i = IntVal(int(name[1:]))
            if name in passes:
                P = Store(P, i, passes[name])
            if name in verdict:
                V = Store(V, i, {'acc': core.acc, 'esc': core.esc, 'blk': core.blk}[verdict[name]])
            if name in branch:
                W = Store(W, i, branch[name])
            E = Store(E, i, setz(holds[name]))
        S = setz(set(safe) | {'-'})
        def union(x, y):
            s.add(core.unionF(setz(x), setz(y)) == setz(x | y))
            return x | y
        built: dict = {}
        def z(t):
            """The z3 term of t, with the eval equation at this model."""
            if id(t) in built:
                return built[id(t)]
            if t[0] == 'deny':
                result = core.H.deny
            elif t[0] == 'gate':
                result = core.H.gate(IntVal(int(t[1][1:])), obs[t[2] or '-'], lay[t[3] or 'none'], setz(t[4]), setz(t[5]), z(t[6]))
            elif t[0] == 'guard':
                result = core.H.guard(IntVal(int(t[1][1:])), lay[t[2]], setz(t[3]), z(t[4]))
            else:
                result = core.H.switch(IntVal(int(t[1][1:])), z(t[2]), z(t[3]))
            built[id(t)] = result
            s.add(core.eval_def(result, P, V, W))
            return result
        def chk(t, a, b):
            r = z(t)
            s.add(core.check_def(r, setz(a), setz(b)))
            if t[0] == 'gate':
                e = union(t[4], b)
                credit = (t[3] is None) or req[t[3]] <= e
                if credit:
                    chk(t[6], a | ({t[2]} if t[2] else set()) | ({'-'} if t[2] is None else set()), union(b, t[5]))
                else:
                    chk(t[6], a, b)
                chk_other = None
            elif t[0] == 'guard':
                union(t[3], b)
                chk(t[4], a, b)
            elif t[0] == 'switch':
                chk(t[2], a, b); chk(t[3], a, b)
        def wfz(t, f):
            r = z(t)
            s.add(core.wf_def(r, P, V, W, E, S, setz(f)))
            if t[0] == 'gate':
                union(f, t[5])
                wfz(t[6], f); wfz(t[6], f | t[5])
            elif t[0] == 'guard':
                wfz(t[4], f)
            elif t[0] == 'switch':
                wfz(t[2], f); wfz(t[3], f)
        top = z(term)
        expected_eval = reference.evaluate(term, passes, verdict, branch)
        chk(term, frozenset(), frozenset())
        wfz(term, frozenset())
        s.push()
        s.add(core.checkF(top, setz(()), setz(())) == (not reference.check(term, frozenset(), h.goals, req, scope)))
        failures['check'] += s.check() != unsat
        s.pop(); s.push()
        value = core.Out.denied if expected_eval[0] == 'denied' else core.Out.accepted(IntVal(int(expected_eval[1][1:])))
        s.add(core.evalF(top, P, V, W) != value)
        failures['eval'] += s.check() != unsat
        s.pop(); s.push()
        s.add(core.wfF(top, P, V, W, E, S, setz(())) == (not reference.wf(term, passes, verdict, branch, holds, safe, req, scope)))
        failures['wf'] += s.check() != unsat
        s.pop()
    return {'terms': count, 'failures': failures}


def e4():
    tasks, per_task, models = 40, 1000, 20
    with mp.Pool(WORKERS) as pool:
        parts = pool.map(e4_worker, [(MASTER + i, per_task, models) for i in range(tasks)], chunksize=1)
    total = {k: sum(p[k] for p in parts) for k in parts[0]}
    total['mean_reachable_nodes'] = total['reachable_nodes'] / total['specs']
    total['z3_adequacy'] = adequacy(MASTER, 600)
    save('e4_differential', total)


# ---------------------------------------------------------------- E7 monolithic verifiers
def z3_violation(h: Hierarchy, timeout_ms=int(TIMEOUT * 1000)) -> str:
    """Monolithic SMT encoding of Figure 2 over the DAG: does a contract-respecting unsafe run exist?

    One Boolean per stage behaviour, per obligation at each invocation and per fact at each
    node. It uses neither `check` nor the crediting rule; the same author wrote both.
    """
    from z3 import Bool, Solver, And, Or, Not, Implies
    s = Solver()
    s.set('timeout', timeout_ms)
    order, _ = tint.hsl._order(h)
    if not order:
        return 'unsat'
    goal = {g: Bool('S_' + g) for g in sorted(h.goals)}
    outgoing: dict = {n: [] for n in order}
    incoming_fact: dict = {n: {o: [] for o in h.obligations} for n in order}
    accepts = []
    def leaves(n, target, condition, adds=()):
        if target is None:
            return
        outgoing[target].append(condition)
        for o in h.obligations:
            incoming_fact[target][o].append(And(condition, Or(Bool(f'fact_{n}_{o}'), *[x for name, x in adds if name == o])))
    for n in order:
        node = h.nodes[n]
        reach = Bool('reach_' + n)
        hold = {o: Bool(f'hold_{n}_{o}') for o in h.obligations}
        evidence = tint.hsl.usable(h, n, getattr(node, 'layer', None)) if not isinstance(node, Switch) else frozenset()
        for o in evidence:
            s.add(Implies(reach, hold[o]))
        for o in h.obligations:
            s.add(Implies(And(reach, Bool(f'fact_{n}_{o}')), hold[o]))
        if isinstance(node, Gate):
            go = Bool('pass_' + n)
            requires = h.layers[node.layer].requires if node.layer else frozenset()
            bound = And(reach, go, *[hold[o] for o in requires])
            if node.establishes is not None:
                s.add(Implies(bound, goal[node.establishes]))
            leaves(n, node.next, And(reach, go), [(o, And(*[hold[x] for x in requires])) for o in node.provides])
        elif isinstance(node, Guard):
            acc_, esc_ = Bool('acc_' + n), Bool('esc_' + n)
            s.add(Not(And(acc_, esc_)))
            layer = h.layers[node.layer]
            s.add(Implies(And(reach, acc_, *[hold[o] for o in layer.requires]), And(*[goal[g] for g in layer.scope])))
            accepts.append(And(reach, acc_))
            leaves(n, node.next, And(reach, esc_))
        else:
            b = Bool('br_' + n)
            leaves(n, node.then, And(reach, b))
            leaves(n, node.otherwise, And(reach, Not(b)))
    for n in order:
        ways = outgoing[n] + ([z3.BoolVal(True)] if n == h.entry else [])
        s.add(Bool('reach_' + n) == Or(*ways))
        for o in h.obligations:
            s.add(Bool(f'fact_{n}_{o}') == Or(*incoming_fact[n][o]))
    s.add(Or(*accepts) if accepts else z3.BoolVal(False))
    s.add(Not(And(*goal.values())) if goal else z3.BoolVal(False))
    return str(s.check())


def prism_model(h: Hierarchy) -> str:
    """PRISM MDP: choose the safe set, then walk. Each stage chooses which obligations hold there."""
    order, _ = tint.hsl._order(h)
    index = {n: i for i, n in enumerate(order)}
    done, bad = len(order), len(order) + 1
    goals, obligations = sorted(h.goals), sorted(h.obligations)
    lines = ['mdp', 'module hierarchy', f'  pos : [0..{bad}] init 0;']
    lines += [f'  s{i} : bool init false;' for i in range(len(goals))]
    lines += [f'  f{i} : bool init false;' for i in range(len(obligations))]
    lines += ['  chosen : bool init false;']
    all_safe = ' & '.join(f's{i}' for i in range(len(goals))) or 'true'
    for i in range(len(goals)):
        lines.append(f"  [] !chosen & !s{i} -> (s{i}'=true);")
    lines.append("  [] !chosen -> (chosen'=true);")
    target = lambda n: done if n is None else index[n]
    subsets = [frozenset(x for i, x in enumerate(obligations) if mask >> i & 1) for mask in range(1 << len(obligations))]
    def facts_within(here):
        return ''.join(f' & !f{i}' for i, x in enumerate(obligations) if x not in here)
    def update(position, gained=frozenset()):
        return f"(pos'={position})" + ''.join(f" & (f{obligations.index(x)}'=true)" for x in sorted(gained))
    for n in order:
        node = h.nodes[n]
        at = f'chosen & pos={index[n]}'
        if isinstance(node, Switch):
            lines.append(f"  [] {at} -> {update(target(node.then))};")
            lines.append(f"  [] {at} -> {update(target(node.otherwise))};")
            continue
        evidence = tint.hsl.usable(h, n, node.layer)
        requires = h.layers[node.layer].requires if node.layer else frozenset()
        for here in subsets:
            if not evidence <= here:
                continue
            within = at + facts_within(here)
            lines.append(f"  [] {within} -> {update(done)};")
            if isinstance(node, Gate):
                if requires <= here:
                    needs = '' if node.establishes is None else f' & s{goals.index(node.establishes)}'
                    lines.append(f"  [] {within}{needs} -> {update(target(node.next), node.provides)};")
                else:
                    lines.append(f"  [] {within} -> {update(target(node.next))};")
            else:
                scope = h.layers[node.layer].scope
                lines.append(f"  [] {within} -> {update(target(node.next))};")
                promise = ' & '.join(f's{goals.index(g)}' for g in sorted(scope)) or 'true'
                if not requires <= here:
                    promise = 'true'
                lines.append(f"  [] {within} & ({promise}) & !({all_safe}) -> {update(bad)};")
    lines += [f'  [] chosen & pos>={done} -> true;', 'endmodule', f'label "bad" = pos={bad};']
    return '\n'.join(lines) + '\n'


def prism_home():
    return Path(os.environ.get('PRISM_HOME', ROOT / '.tools/prism'))


def prism_available():
    return prism_home().exists()


def prism_violation(h: Hierarchy, timeout=TIMEOUT) -> dict:
    """Explicit engine: the symbolic engines' native library does not load in this installation."""
    home = prism_home()
    java = os.environ.get('PRISM_JAVA') or next(str(p) for p in (ROOT / '.tools/java').glob('*/bin/java.exe' if os.name == 'nt' else '*/bin/java'))
    with tempfile.TemporaryDirectory() as tmp:
        model, props = Path(tmp) / 'm.pm', Path(tmp) / 'm.pctl'
        model.write_text(prism_model(h), encoding='utf-8')
        props.write_text('Pmax=? [ F "bad" ]\n', encoding='utf-8')
        command = [java, '-Xss4M', '-Xmx8g', '-Djava.library.path=' + str(home / 'lib'), '-cp', str(home / 'lib/*'), 'prism.PrismCL',
                   str(model), str(props), '-explicit']
        start = time.perf_counter()
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return {'answer': 'timeout', 'seconds': timeout, 'states': None}
    found = re.search(r'Result: ([\d.Ee+-]+)', result.stdout)
    states = re.search(r'States:\s+(\d+)', result.stdout)
    if not found:
        return {'answer': 'error:' + (result.stdout + result.stderr)[-200:], 'seconds': time.perf_counter() - start, 'states': None}
    return {'answer': 'sat' if float(found.group(1)) > 0 else 'unsat', 'seconds': time.perf_counter() - start,
            'states': int(states.group(1)) if states else None}


def e7():
    rng = random.Random(MASTER + 7)
    rows = {'z3': {'compared': 0, 'disagreements': 0, 'not_decided': 0}, 'prism': {'compared': 0, 'disagreements': 0, 'not_decided': 0}, 'with_flow': 0}
    for i in range(3000):
        h = random_hierarchy(rng)
        report = check(h, witnesses=False)
        behavioural = report.ok or any(f.code in ('obligation', 'coverage') for f in report.findings)
        assert behavioural, report.findings
        expected = 'unsat' if report.ok else 'sat'
        answer = z3_violation(h)
        rows['with_flow'] += report.exact_states > 0
        rows['z3']['compared'] += 1
        rows['z3']['disagreements'] += answer != expected
        rows['z3']['not_decided'] += answer not in ('sat', 'unsat')
    if prism_available():
        rng = random.Random(MASTER + 8)
        specs = [random_hierarchy(rng, n=rng.randint(2, 8), obligations=2) for _ in range(200)]
        with mp.Pool(10) as pool:
            answers = pool.map(prism_violation, specs)
        for h, r in zip(specs, answers):
            expected = 'unsat' if check(h).ok else 'sat'
            rows['prism']['compared'] += 1
            rows['prism']['disagreements'] += r['answer'] != expected
            rows['prism']['not_decided'] += r['answer'] not in ('sat', 'unsat')
    save('e7_monolithic', rows)


# ---------------------------------------------------------------- E8 continuity with preserved study
def devagent_spec(threshold_stage=True) -> Hierarchy:
    return parse((ROOT / 'experiments/v2/devagent_study.json').read_text(encoding='utf-8'))


def e8():
    from experiments.run import ExploratoryLexicalScorer, HistoricalLexicalScorer
    from tint.layers import StructuredJudge, quarantine
    from tint.model import ActionView
    from tint.hsl.rules import production_approval, secret_egress
    rows = {}
    for study, directory, scorer_type, policy in [('exploratory', 'results/raw/exploratory_numeric', ExploratoryLexicalScorer, 'checked_quarantine'),
                                                  ('primary', 'results/raw', HistoricalLexicalScorer, 'checked_uncalibrated')]:
        traces, decisions = {}, []
        with gzip.open(ROOT / directory / 'traces.jsonl.gz', 'rt', encoding='utf-8') as f:
            for line in f:
                r = json.loads(line)
                if r['split'] != 'calibration':
                    traces[r['identifier']] = r
        with gzip.open(ROOT / directory / 'decisions.jsonl.gz', 'rt', encoding='utf-8') as f:
            for line in f:
                r = json.loads(line)
                if r['policy'] == policy:
                    decisions.append(r)
        compared = disagreements = 0
        engines = {}
        scorer_call = scorer_type()
        for row in decisions:
            threshold = row['threshold']
            if threshold not in engines:
                def l2(text, t=threshold):
                    s = scorer_call(text)
                    return (Verdict.ALLOW, s) if s < t else (Verdict.ESCALATE, s)
                judge = StructuredJudge()
                def l3(record):
                    view = {k: record[k] for k in ('destructive', 'production', 'approved', 'external', 'secret', 'untrusted')}
                    return judge(quarantine(ActionView(**view), record['score']))
                def env(facts, proposal, ledger):
                    return proposal.action.environment == 'sandbox'
                engines[threshold] = Engine(devagent_spec(), fixture_store(), ApprovalStore(),
                                            {'production_approval': production_approval, 'secret_egress': secret_egress, 'environment': env},
                                            {'L2': l2, 'L3': l3}, checks={'config_match': lambda *a: True}, context='local-fixtures-v1')
            data = traces[row['trace_id']]['action']
            action = Action(ActionKind(data['kind']), data['target'], tuple(data['inputs']), data['environment'])
            outcome = engines[threshold].shadow(Proposal(action, traces[row['trace_id']]['issue']))
            compared += 1
            disagreements += outcome.accepted != row['allowed']
        rows[study] = {'policy': policy, 'compared': compared, 'disagreements': disagreements}
    save('e8_continuity', rows)


# ---------------------------------------------------------------- E9 scalability
def chain(n: int, goals: int) -> Hierarchy:
    names = [f'g{i}' for i in range(goals)]
    layer = Layer('L', frozenset(names), frozenset({'o'}), 'structured')
    nodes = {}
    ids = [f'n{i}' for i in range(n)]
    for i, name in enumerate(ids):
        following = ids[i + 1] if i + 1 < n else None
        nodes[name] = Guard(name, 'L', frozenset({'o'}), following) if i >= goals // 2 and i % 2 else Gate(name, 'r', names[i % goals], following)
    return Hierarchy(frozenset(names), {'o': Obligation('o', 'assumed')}, {'L': layer}, nodes, ids[0])


def diamonds(depth: int, broken: bool = False, shared_goals: int | None = None) -> Hierarchy:
    """Switches with one gate on each arm: 2^depth paths, each establishing a different goal set."""
    goal_names = [f'{side}{i}' for i in range(depth) for side in 'xy'] if shared_goals is None else [f'g{i}' for i in range(shared_goals)]
    scope = frozenset(goal_names) - ({goal_names[0]} if broken else set())
    nodes: dict = {}
    for i in range(depth):
        following = f's{i + 1}' if i + 1 < depth else 'final'
        x, y = (f'x{i}', f'y{i}') if shared_goals is None else (goal_names[i % shared_goals], goal_names[(i + 1) % shared_goals])
        nodes[f's{i}'] = Switch(f's{i}', 'c', f'a{i}', f'b{i}')
        nodes[f'a{i}'] = Gate(f'a{i}', 'r', x, following)
        nodes[f'b{i}'] = Gate(f'b{i}', 'r', y, following)
    nodes['final'] = Guard('final', 'L', frozenset(), None)
    return Hierarchy(frozenset(goal_names), {}, {'L': Layer('L', scope, frozenset(), 'structured')}, nodes, 's0' if depth else 'final')


def path_enumeration(h: Hierarchy, deadline: float) -> str:
    """The obvious alternative: walk every path, tracking gates passed."""
    bits = {g: 1 << i for i, g in enumerate(sorted(h.goals))}
    full = (1 << len(bits)) - 1
    ok = True
    stack = [(h.entry, 0)]
    steps = 0
    while stack:
        steps += 1
        if steps % 4096 == 0 and time.perf_counter() > deadline:
            return 'timeout'
        name, avail = stack.pop()
        if name is None:
            continue
        node = h.nodes[name]
        if isinstance(node, Gate):
            stack.append((node.next, avail | (bits.get(node.establishes, 0) if credited(h, node) else 0)))
        elif isinstance(node, Guard):
            layer = h.layers[node.layer]
            if avail != full and (not layer.requires <= node.evidence or any(not avail & m and g not in layer.scope for g, m in bits.items())):
                ok = False
            stack.append((node.next, avail))
        else:
            stack.append((node.then, avail)); stack.append((node.otherwise, avail))
    return 'unsat' if ok else 'sat'


def median_time(call, repetitions=7):
    times = []
    for _ in range(repetitions):
        start = time.perf_counter()
        value = call()
        times.append(time.perf_counter() - start)
    return statistics.median(times), value


def loglog_slope(points):
    xs = [math.log(a) for a, _ in points]; ys = [math.log(b) for _, b in points]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    return sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / sum((a - mx) ** 2 for a in xs)


def rejecting_chain(n: int) -> Hierarchy:
    """Every guard misses its obligation: n findings, each with a path of up to n stages."""
    ids = [f'n{i}' for i in range(n)]
    nodes = {name: Guard(name, 'L', frozenset(), ids[i + 1] if i + 1 < n else None) for i, name in enumerate(ids)}
    return Hierarchy(frozenset({'g'}), {'o': Obligation('o', 'assumed')}, {'L': Layer('L', frozenset({'g'}), frozenset({'o'}), 'structured')}, nodes, ids[0])


def many_layers(n: int, goals: int) -> Hierarchy:
    """Each guard has its own full-scope layer, which stresses the per-layer masks."""
    names = frozenset(f'g{i}' for i in range(goals))
    ids = [f'n{i}' for i in range(n)]
    nodes = {name: Guard(name, 'L' + name, frozenset(), ids[i + 1] if i + 1 < n else None) for i, name in enumerate(ids)}
    return Hierarchy(names, {}, {f'L{x}': Layer(f'L{x}', names, frozenset(), 'structured') for x in ids}, nodes, ids[0])


def fan_in(leaves: int) -> Hierarchy:
    """A balanced switch tree into one guard with `leaves` missing obligations: witness paths and in-degree."""
    obligations = {f'o{i}': Obligation(f'o{i}', 'assumed') for i in range(leaves)}
    layer = Layer('L', frozenset({'g'}), frozenset(obligations), 'structured')
    nodes: dict = {'final': Guard('final', 'L', frozenset(), None)}
    def build(prefix, size):
        if size == 1:
            return 'final'
        name = 's' + prefix
        nodes[name] = Switch(name, 'c' + prefix, build(prefix + '0', size // 2), build(prefix + '1', size - size // 2))
        return name
    return Hierarchy(frozenset({'g'}), obligations, {'L': layer}, nodes, build('', leaves))


def flow_diamonds(depth: int) -> Hierarchy:
    """Each diamond chooses one of two facts, so 2^depth (goals, facts) states reach the final guard."""
    obligations = {f'{side}{i}': Obligation(f'{side}{i}', 'assumed') for i in range(depth) for side in 'xy'}
    obligations['never'] = Obligation('never', 'assumed')
    layer = Layer('L', frozenset({'g'}), frozenset({'never'}), 'structured')
    nodes: dict = {}
    for i in range(depth):
        following = f's{i + 1}' if i + 1 < depth else 'final'
        nodes[f's{i}'] = Switch(f's{i}', 'c', f'a{i}', f'b{i}')
        nodes[f'a{i}'] = Gate(f'a{i}', 'r', None, following, None, frozenset(), frozenset({f'x{i}'}))
        nodes[f'b{i}'] = Gate(f'b{i}', 'r', None, following, None, frozenset(), frozenset({f'y{i}'}))
    nodes['final'] = Guard('final', 'L', frozenset(), None)
    return Hierarchy(frozenset({'g'}), obligations, {'L': layer}, nodes, 's0')


def e9():
    nodes_rows = []
    for family, build in [('chain', lambda n: chain(n, 8)), ('diamonds', lambda n: diamonds(n // 3, shared_goals=8))]:
        for n in [1000, 3162, 10000, 31623, 100000, 316228, 1000000]:
            h = build(n)
            seconds, report = median_time(lambda: check(h))
            assert report.ok, report.findings[:2]
            nodes_rows.append({'family': family, 'target_nodes': n, 'nodes': len(h.nodes), 'edges': sum(len(successors(x)) for x in h.nodes.values()), 'seconds': seconds})
            print(nodes_rows[-1], flush=True)
    rejected_rows = []
    for n in [1000, 2000, 4000, 8000, 16000, 32000]:
        h = rejecting_chain(n)
        decision, report = median_time(lambda: check(h, witnesses=False))
        full, _ = median_time(lambda: check(h), 3)
        rejected_rows.append({'nodes': n, 'findings': len(report.findings), 'decision_seconds': decision, 'with_witnesses_seconds': full})
        print(rejected_rows[-1], flush=True)
    for n in [64000, 128000, 256000, 512000, 1000000]:
        h = rejecting_chain(n)
        decision, report = median_time(lambda: check(h, witnesses=False), 3)
        rejected_rows.append({'nodes': n, 'findings': len(report.findings), 'decision_seconds': decision, 'with_witnesses_seconds': None})
        print(rejected_rows[-1], flush=True)
    goal_rows = []
    for goals in [1, 8, 64, 512, 4096, 32768]:
        h = chain(100000, goals)
        seconds, report = median_time(lambda: check(h))
        assert report.ok
        goal_rows.append({'goals': goals, 'nodes': len(h.nodes), 'seconds': seconds})
        print(goal_rows[-1], flush=True)
    layer_rows = []
    for goals in [512, 4096, 32768, 262144]:
        h = many_layers(200, goals)
        seconds, report = median_time(lambda: check(h), 3)
        assert report.ok, report.findings[:2]
        layer_rows.append({'layers': 200, 'goals': goals, 'seconds': seconds})
        print(layer_rows[-1], flush=True)
    fan_rows = []
    for leaves in [2000, 4000, 8000, 16000]:
        h = fan_in(leaves)
        decision, report = median_time(lambda: check(h, witnesses=False), 3)
        full, _ = median_time(lambda: check(h), 3)
        fan_rows.append({'leaves': leaves, 'nodes': len(h.nodes), 'findings': len(report.findings), 'decision_seconds': decision, 'with_witnesses_seconds': full})
        print(fan_rows[-1], flush=True)
    flow_rows = []
    for depth in [2, 4, 6, 8, 10, 12, 14, 16]:
        h = flow_diamonds(depth)
        seconds, report = median_time(lambda: check(h, witnesses=False), 3)
        flow_rows.append({'depth': depth, 'nodes': len(h.nodes), 'states': report.exact_states, 'seconds': seconds})
        print(flow_rows[-1], flush=True)
    slopes = {family: loglog_slope([(r['nodes'], r['seconds']) for r in nodes_rows if r['family'] == family and r['nodes'] >= 10000])
              for family in ['chain', 'diamonds']}
    slopes['rejected_decision'] = loglog_slope([(r['nodes'], r['decision_seconds']) for r in rejected_rows if r['nodes'] >= 8000])
    slopes['rejected_witnesses'] = loglog_slope([(r['nodes'], r['with_witnesses_seconds']) for r in rejected_rows if r['with_witnesses_seconds']])
    compare = []
    alive = {'path': True, 'z3': True, 'prism': prism_available()}
    for depth in [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 40, 48, 64, 128, 256]:
        for broken in [False, True]:
            h = diamonds(depth, broken, shared_goals=8)
            expected = 'sat' if broken else 'unsat'
            row = {'depth': depth, 'broken': broken, 'nodes': len(h.nodes), 'paths': 2 ** depth}
            row['tint_seconds'] = median_time(lambda: check(h), 3)[0]
            assert check(h).ok == (not broken)
            if alive['path']:
                start = time.perf_counter()
                answer = path_enumeration(h, start + TIMEOUT)
                row['path_seconds'] = time.perf_counter() - start
                row['path_answer'] = answer
                assert answer in (expected, 'timeout')
                alive['path'] = answer != 'timeout'
            if alive['z3']:
                start = time.perf_counter()
                answer = z3_violation(h)
                row['z3_seconds'] = time.perf_counter() - start
                row['z3_answer'] = answer
                assert answer in (expected, 'unknown'), answer
                alive['z3'] = answer != 'unknown'
            if alive['prism']:
                r = prism_violation(h)
                row['prism_seconds'], row['prism_answer'], row['prism_states'] = r['seconds'], r['answer'], r['states']
                alive['prism'] = r['answer'] == expected
            compare.append(row)
            print(row, flush=True)
    save('timing/e9_scalability', {'by_nodes': nodes_rows, 'rejected': rejected_rows, 'by_goals': goal_rows, 'many_layers': layer_rows, 'fan_in': fan_rows,
                                   'flow': flow_rows, 'slopes': slopes, 'versus': compare})


def e10():
    """A realistic mix: gates with a checked obligation, then guards, on one run of each depth."""
    rows = []
    for depth in [4, 8, 32, 128, 512, 2048]:
        ids = [f'n{i}' for i in range(depth)]
        def stage(i, name):
            following = ids[i + 1] if i + 1 < depth else None
            return Gate(name, 'r', 'g', following, None, frozenset({'c'})) if i % 2 == 0 else Guard(name, 'L', frozenset({'c'}), following)
        nodes = {name: stage(i, name) for i, name in enumerate(ids)}
        h = Hierarchy(frozenset({'g'}), {'c': Obligation('c', 'checked')}, {'L': Layer('L', frozenset({'g'}), frozenset({'c'}), 'structured')}, nodes, ids[0])
        calls = [0]
        def guard(view):
            calls[0] += 1
            return Verdict.ALLOW if calls[0] % (depth // 2) == 0 else Verdict.ESCALATE
        def rule(facts, proposal, ledger):
            return True
        def predicate(node, facts, proposal):
            return True
        build, engine = median_time(lambda: Engine(h, fixture_store(), ApprovalStore(), {'r': rule}, {'L': guard}, checks={'c': predicate}))
        decision, _ = median_time(lambda: [engine.shadow(PROPOSAL) for _ in range(200)], 7)
        rows.append({'depth': depth, 'constructor_seconds': build, 'decision_microseconds': decision / 200 * 1e6, 'per_stage_microseconds': decision / 200 * 1e6 / depth})
        print(rows[-1], flush=True)
    save('timing/e10_overhead', rows)


# ---------------------------------------------------------------- E11 incremental recertification
def stage_key(h, name):
    node = h.nodes[name]
    return node.rule if isinstance(node, Gate) else node.layer if isinstance(node, Guard) else node.condition


def wired_engine_stat(h: Hierarchy, table: dict, change: str | None = None, **options) -> Engine:
    """Wired engine; `change` names one node whose component gets a new version."""
    rules, guards, conditions, checks = wiring(h, table)
    if change is not None:
        for mapping in (rules, guards, conditions):
            if stage_key(h, change) in mapping:
                mapping[stage_key(h, change)].version = 'changed'
    return Engine(h, fixture_store(), ApprovalStore(), rules, guards, conditions, checks, statistical=frozenset(h.goals), delta=1.0, **options)


def e11():
    rng = random.Random(MASTER + 11)
    rows = []
    locality_checks = locality_violations = attempts = 0
    while len(rows) < 2000:
        attempts += 1
        h = random_hierarchy(rng, n=rng.randint(10, 40), goals=2, obligations=2)
        report = check(h, witnesses=False)
        if not report.ok or len(report.routes) < 2:
            continue
        table: dict = {}
        base = wired_engine_stat(h, table)
        changed = rng.choice(list(report.order))
        variant = wired_engine_stat(h, table, change=changed)
        affected = affected_routes(base, variant)
        rows.append({'routes': len(report.routes), 'affected': len(affected), 'stage': type(h.nodes[changed]).__name__})
        term = term_of(h)
        for _ in range(40):
            table.clear()
            table.update(random_model(rng, h))
            a = reference.evaluate(term, *split_model(h, table))
            other = dict(table)
            other[changed] = rng.choice(['acc', 'esc', 'blk']) if isinstance(h.nodes[changed], Guard) else not table[changed]
            b = reference.evaluate(term, *split_model(h, other))
            for r in report.routes:
                if r not in affected and base.needs_certificate[r]:
                    locality_checks += 1
                    locality_violations += (a == ('accepted', r)) != (b == ('accepted', r))
    cascade = []
    for q in [2, 4, 8, 16, 32, 64]:
        ids = [f'n{i}' for i in range(q)]
        nodes = {name: Guard(name, 'L' + name, frozenset(), ids[i + 1] if i + 1 < q else None) for i, name in enumerate(ids)}
        layers = {f'L{n}': Layer(f'L{n}', frozenset({'g'}), frozenset(), 'structured') for n in ids}
        h = Hierarchy(frozenset({'g'}), {}, layers, nodes, ids[0])
        fractions = []
        table: dict = {}
        base = wired_engine_stat(h, table)
        for name in ids:
            fractions.append(len(affected_routes(base, wired_engine_stat(h, table, change=name))) / q)
        cascade.append({'routes': q, 'mean_fraction': sum(fractions) / q, 'last_layer_fraction': fractions[-1]})
    devagent = parse((ROOT / 'experiments/v2/cases/devagent.json').read_text(encoding='utf-8'))
    table = {}
    base = wired_engine_stat(devagent, table)
    matrix = {name: sorted(affected_routes(base, wired_engine_stat(devagent, table, change=name))) for name in check(devagent).order}
    summary = {'random_hierarchies': len(rows), 'attempts': attempts, 'mean_routes': statistics.mean(r['routes'] for r in rows),
               'mean_fraction_affected': statistics.mean(r['affected'] / r['routes'] for r in rows),
               'median_fraction_affected': statistics.median(r['affected'] / r['routes'] for r in rows),
               'locality_checks': locality_checks, 'locality_violations': locality_violations, 'cascade': cascade, 'devagent_matrix': matrix}
    save('e11_recertification', summary)


# ---------------------------------------------------------------- E12 validity of route bounds
def e12():
    delta, n, replications, laws, support = .05, 1000, 1000, 40, 300
    rng = np.random.default_rng(MASTER + 12)
    rows = []
    for law in range(laws):
        q = int(rng.integers(2, 6))
        ids = [f'n{i}' for i in range(q)]
        nodes = {name: Guard(name, 'L' + name, frozenset(), ids[i + 1] if i + 1 < q else None) for i, name in enumerate(ids)}
        layers = {f'L{x}': Layer(f'L{x}', frozenset({'g'}), frozenset(), 'structured') for x in ids}
        h = Hierarchy(frozenset({'g'}), {}, layers, nodes, ids[0])
        table: dict = {}
        engine = wired_engine_stat(h, table)
        weights = rng.dirichlet(np.ones(support))
        unsafe = rng.random(support) < rng.uniform(.1, .6)
        shared = rng.random(support)
        correlation = rng.uniform(0, 1)
        escalate = rng.uniform(.3, .8, size=q)
        accept = rng.uniform(.05, .3, size=q)
        routes = np.full(support, -1)
        passes = np.zeros((support, q), dtype=bool)
        for i in range(support):
            for j, name in enumerate(ids):
                u = shared[i] if rng.random() < correlation else rng.random()
                table[name] = 'acc' if u < accept[j] else 'esc' if u < accept[j] + escalate[j] else 'blk'
                passes[i, j] = table[name] != 'blk'
            outcome = engine.shadow(PROPOSAL)
            routes[i] = ids.index(outcome.route) if outcome.accepted else -1
        risk_route = np.array([weights[(routes == j) & unsafe].sum() for j in range(q)])
        risk = float(risk_route.sum())
        theta = float(weights[unsafe].sum())
        miss = [float(weights[unsafe & passes[:, j]].sum() / theta) for j in range(q)]
        product = theta * math.prod(miss)
        minimum = min(theta * m for m in miss)
        counts = rng.multinomial(n, weights, size=replications)
        covered_sum = covered_each = covered_whole = 0
        sums, wholes = [], []
        for row in counts:
            losses = [int(row[(routes == j) & unsafe].sum()) for j in range(q)]
            bounds = [binomial_upper(k, n, delta / q) for k in losses]
            whole = binomial_upper(sum(losses), n, delta)
            sums.append(sum(bounds)); wholes.append(whole)
            covered_sum += risk <= sum(bounds)
            covered_each += all(risk_route[j] <= bounds[j] for j in range(q))
            covered_whole += risk <= whole
        rows.append({'law': law, 'routes': q, 'true_risk': risk, 'product_estimate': product, 'min_estimate': minimum,
                     'coverage_routes_simultaneous': covered_each / replications, 'coverage_sum': covered_sum / replications,
                     'coverage_whole': covered_whole / replications, 'mean_sum_bound': float(np.mean(sums)), 'mean_whole_bound': float(np.mean(wholes))})
    summary = {'laws': laws, 'replications': replications, 'n': n, 'delta': delta,
               'min_coverage_routes': min(r['coverage_routes_simultaneous'] for r in rows), 'min_coverage_sum': min(r['coverage_sum'] for r in rows),
               'product_understates_laws': sum(r['true_risk'] > r['product_estimate'] for r in rows),
               'min_understates_laws': sum(r['true_risk'] > r['min_estimate'] for r in rows),
               'median_understatement_ratio_product': statistics.median(r['true_risk'] / r['product_estimate'] for r in rows if r['product_estimate'] > 0),
               'mean_ratio_sum_to_whole': statistics.mean(r['mean_sum_bound'] / r['mean_whole_bound'] for r in rows), 'rows': rows}
    save('e12_route_bounds', summary)


# ---------------------------------------------------------------- E12b the certificate pipeline, end to end
def e12b_worker(args):
    """One random DAG and finite law. Certify, change one stage, recertify the stale routes only,
    rebuild the engine from those certificates, and compare its risk with the sum of open bounds.

    The law respects the premises of the Route risk theorem: an outcome on a hard route is safe.
    """
    seed, replications, n, delta = args
    rng = random.Random(seed)
    while True:
        h = random_hierarchy(rng, n=rng.randint(6, 14), goals=2, obligations=1)
        report = check(h, witnesses=False)
        if report.ok and len(report.routes) >= 2:
            break
    support = 200
    weights = np.random.default_rng(seed).dirichlet(np.ones(support))
    table: dict = {}
    models = [random_model(rng, h) for _ in range(support)]
    changed = rng.choice(list(report.order))
    altered = [dict(m) for m in models]
    for m in altered:
        if rng.random() < .3:
            m[changed] = rng.choice(['acc', 'esc', 'blk']) if isinstance(h.nodes[changed], Guard) else not m[changed]
    base = wired_engine_stat(h, table)
    variant = wired_engine_stat(h, table, change=changed)
    needing = [r for r in report.routes if base.needs_certificate[r]]
    if not needing:
        return None
    def run_on(engine, model):
        table.clear()
        table.update(model)
        return engine.shadow(PROPOSAL)
    def safe_by_premise(i):
        """True if this proposal ends on a hard route under either version, where Y must be 0."""
        return any((o := run_on(e, m[i])).accepted and o.route not in needing for e, m in ((base, models), (variant, altered)))
    unsafe = [rng.random() < .3 and not safe_by_premise(i) for i in range(support)]
    stale = set(affected_routes(base, variant))
    share = delta / len(needing)
    numpy_rng = np.random.default_rng(seed + 1)
    def draw(model_list):
        for i in numpy_rng.choice(support, size=n, p=weights):
            table.clear()
            table.update(model_list[int(i)])
            yield PROPOSAL, unsafe[int(i)]
    covered_sum = covered_routes = 0
    sums = []
    route_risk = {r: sum(float(weights[i]) for i in range(support) if unsafe[i] and (o := run_on(variant, altered[i])).accepted and o.route == r) for r in needing}
    for _ in range(replications):
        kept = [c for c in certify(base, draw(models), delta, share=share) if c.route not in stale]
        fresh = certify(variant, draw(altered), delta, routes=stale, share=share)
        table.clear()  # stages hash their state, and the table is empty when the versions are built
        deployed = Engine(h, fixture_store(), ApprovalStore(), *wiring_of(variant), statistical=frozenset(h.goals), delta=delta, certificates=kept + fresh)
        assert set(deployed.open) == set(needing)
        deployed_risk = 0.0
        for i in range(support):
            table.clear()
            table.update(altered[i])
            outcome = deployed.evaluate(PROPOSAL)
            if unsafe[i] and outcome.accepted:
                deployed_risk += float(weights[i])
        total = sum(c.upper for c in deployed.open.values())
        sums.append(total)
        covered_sum += deployed_risk <= total
        covered_routes += all(route_risk[c.route] <= c.upper for c in deployed.open.values())
    return {'routes': len(needing), 'stale': len(stale), 'true_risk': sum(route_risk.values()), 'coverage_sum': covered_sum / replications,
            'coverage_routes': covered_routes / replications, 'mean_sum_bound': float(np.mean(sums))}


def wiring_of(engine: Engine) -> tuple:
    return engine.rules, engine.guards, engine.conditions, engine.checks


def e12b():
    with mp.Pool(WORKERS) as pool:
        rows = [r for r in pool.map(e12b_worker, [(MASTER + 1200 + i, 300, 400, .05) for i in range(48)], chunksize=1) if r]
    summary = {'laws': len(rows), 'replications': 300, 'n': 400, 'delta': .05, 'min_coverage_sum': min(r['coverage_sum'] for r in rows),
               'min_coverage_routes': min(r['coverage_routes'] for r in rows), 'mean_stale_fraction': statistics.mean(r['stale'] / r['routes'] for r in rows),
               'wilson_upper_of_worst_law': wilson_upper(min(r['coverage_routes'] for r in rows), 300), 'rows': rows}
    save('e12b_pipeline', summary)


def wilson_upper(p, n, z=3.09):
    """Upper Wilson limit, with z Bonferroni-corrected over the laws: is coverage credibly below nominal?"""
    centre = p + z * z / (2 * n)
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (centre + margin) / (1 + z * z / n)


# ---------------------------------------------------------------- E13 published designs, one encoding rule
ROBUST = 'safe_on_this_text'


def adversarial(h: Hierarchy) -> Hierarchy:
    """The encoding rule, applied mechanically: under an adversary, the contract of any stage
    that reads raw text needs the claim that it still holds on text the adversary wrote."""
    obligations = dict(h.obligations)
    obligations.setdefault(ROBUST, Obligation(ROBUST, 'assumed'))
    layers = {k: replace(v, requires=v.requires | ({ROBUST} if v.view == 'raw' else frozenset())) for k, v in h.layers.items()}
    return replace(h, obligations=obligations, layers=layers)


def repair(h: Hierarchy) -> dict:
    """The obligations to supply for acceptance: at guards from findings, and at veto stages whose goal stays open."""
    current = h
    supplied = []
    for _ in range(len(h.nodes) * max(len(h.obligations), 1) + 1):
        report = check(current, witnesses=False)
        pending = {(f.node, f.detail) for f in report.findings if f.code == 'obligation'}
        open_goals = {f.detail for f in report.findings if f.code == 'coverage'}
        pending |= {(name, x) for name, node in current.nodes.items() if isinstance(node, Gate) and node.layer is not None and node.establishes in open_goals
                    for x in current.layers[node.layer].requires - node.evidence}
        if not pending:
            break
        nodes = dict(current.nodes)
        for name, item in sorted(pending):
            nodes[name] = replace(nodes[name], evidence=nodes[name].evidence | {item})
            supplied.append([name, item])
        current = replace(current, nodes=nodes)
    final = check(current, witnesses=False)
    return {'supply': supplied, 'accepted_after': final.ok, 'uncovered': sorted(f.detail for f in final.findings if f.code == 'coverage')}


def case_row(name: str, h: Hierarchy) -> dict:
    report = check(h)
    table: dict = {}
    hard = None
    if report.ok or report.routes:
        statistical = frozenset(g for g in h.goals if not any(isinstance(n, Gate) and n.layer is None and n.establishes == g for n in h.nodes.values()))
        guarded = gated(h, report.order, statistical)
        hard = sum(not (statistical - guarded[r]) for r in report.routes)
    return {'case': name, 'accepted': report.ok, 'routes': len(report.routes), 'hard_routes': hard,
            'findings': [[f.code, f.node, f.detail, list(f.path)] for f in report.findings], 'residual': [list(x) for x in report.residual], 'claims': [list(x) for x in report.claims],
            'necessary': [list(x) for x in necessary(h)] if report.ok else [], 'checked': len(report.checked), 'construction': len(report.construction)}


def e13():
    rows = []
    for path in sorted((ROOT / 'experiments/v2/cases').glob('*.json')):
        h = parse(path.read_text(encoding='utf-8'))
        row = {'benign': case_row(path.stem, h), 'adversarial': case_row(path.stem, adversarial(h)), 'repair_adversarial': repair(adversarial(h))}
        row['case'] = path.stem
        rows.append(row)
    save('e13_cases', rows)


# ---------------------------------------------------------------- E14 the hardness reduction, tested
def cnf_hierarchy(variables: int, clauses: list[list[int]]) -> Hierarchy:
    """A guard is rejected iff the formula is satisfiable: a path picks an assignment, and a clause
    stage provides `bad` when the assignment falsifies it. The guard needs `bad`."""
    obligations = {'bad': Obligation('bad', 'assumed')}
    for v in range(1, variables + 1):
        for side in 'tf':
            obligations[f'{side}{v}'] = Obligation(f'{side}{v}', 'assumed')
    layers = {'Final': Layer('Final', frozenset({'g'}), frozenset({'bad'}), 'structured')}
    nodes: dict = {}
    def clause_id(j):
        return f'c{j}' if j < len(clauses) else 'final'
    for v in range(1, variables + 1):
        following = f's{v + 1}' if v < variables else clause_id(0)
        nodes[f's{v}'] = Switch(f's{v}', f'x{v}', f't{v}', f'f{v}')
        nodes[f't{v}'] = Gate(f't{v}', 'r', None, following, None, frozenset(), frozenset({f't{v}'}))
        nodes[f'f{v}'] = Gate(f'f{v}', 'r', None, following, None, frozenset(), frozenset({f'f{v}'}))
    for j, clause in enumerate(clauses):
        # Falsified means: every literal of the clause is false on this path.
        requires = frozenset(f'f{x}' if x > 0 else f't{-x}' for x in clause)
        layers[f'C{j}'] = Layer(f'C{j}', frozenset(), requires, 'structured')
        nodes[f'c{j}'] = Gate(f'c{j}', 'r', None, clause_id(j + 1), f'C{j}', frozenset(), frozenset({'bad'}))
    nodes['final'] = Guard('final', 'Final', frozenset(), None)
    return Hierarchy(frozenset({'g'}), obligations, layers, nodes, 's1')


def satisfiable(variables: int, clauses: list[list[int]]) -> bool:
    return any(all(any((mask >> (abs(x) - 1) & 1) == (x > 0) for x in c) for c in clauses) for mask in range(1 << variables))


def e14():
    rng = random.Random(MASTER + 14)
    rows = {'formulas': 0, 'satisfiable': 0, 'disagreements': 0, 'false_alarms_of_fast_analysis': 0}
    for _ in range(3000):
        variables = rng.randint(3, 10)  # around the satisfiability threshold, so both answers occur
        clauses = [[rng.choice([1, -1]) * x for x in rng.sample(range(1, variables + 1), 3)] for _ in range(round(rng.uniform(3.5, 5.5) * variables))]
        h = cnf_hierarchy(variables, clauses)
        report = check(h, witnesses=False)
        truth = satisfiable(variables, clauses)
        rows['formulas'] += 1
        rows['satisfiable'] += truth
        rows['disagreements'] += report.ok == truth
        rows['false_alarms_of_fast_analysis'] += report.exact_states > 0 and report.ok
    save('e14_reduction', rows)


def environment():
    versions = {}
    import importlib.metadata as md
    for name in ['z3-solver', 'cvc5', 'numpy', 'scipy']:
        versions[name] = md.version(name)
    git = lambda *a: subprocess.check_output(['git', *a], cwd=ROOT, text=True).strip()
    save('environment', {'platform': platform.platform(), 'python': platform.python_version(), 'cpus': os.cpu_count(), 'versions': versions,
                         'commit': git('rev-parse', 'HEAD'), 'tree_clean': not git('status', '--porcelain'), 'llm_calls': 0})


EXPERIMENTS = {'e3': e3, 'e4': e4, 'e7': e7, 'e8': e8, 'e9': e9, 'e10': e10, 'e11': e11, 'e12': e12, 'e12b': e12b, 'e13': e13, 'e14': e14, 'environment': environment}

if __name__ == '__main__':
    for name in sys.argv[1:] or list(EXPERIMENTS):
        start = time.perf_counter()
        EXPERIMENTS[name]()
        print(name, 'finished in', round(time.perf_counter() - start, 1), 's', flush=True)
