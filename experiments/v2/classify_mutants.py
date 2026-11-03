"""Record the hand classification of E5 survivors in results/v2/e5_mutation.json.

Rules are (file suffix, source fragment before mutation, kind) -> (class, reason), written
after reading each survivor. `equivalent`: no verdict, decision or fingerprint distinction can
change. `gap`: a real but untested difference in the form of a digest. A survivor without a rule
stops the script, so a new survivor cannot go unread.
"""
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
ANNOTATION = 'annotation; never evaluated under postponed annotations'
REPAIRED = 'weakens only the first pass, whose rejections exact exploration settles'
RULES: list[tuple[str, str, str, str, str]] = [
    ('.py', ' | None', 'binop', 'equivalent', ANNOTATION),
    ('__init__.py', 'missing & -missing', 'binop', 'equivalent', 'x | -x is minus the lowest set bit of x, whose bit_length equals that of x & -x'),
    ('__init__.py', 'flow and any(', 'boolop', 'equivalent', 'exploration is exact with or without facts, only slower'),
    ('__init__.py', '_mask(node.provides, fact_rank) if node.provides else 0', 'negate-if', 'equivalent', REPAIRED),
    ('__init__.py', 'known | gained', 'binop', 'equivalent', REPAIRED),
    ('__init__.py', 'witnesses or any(', 'boolop', 'equivalent', 'refinement runs in fewer or more cases; exact either way'),
    ('__init__.py', "f.code in ('obligation', 'coverage')", 'compare', 'equivalent', 'refinement runs in fewer or more cases; exact either way'),
    ('__init__.py', '', 'const', 'equivalent', 'read individually: a state counter, a root sentinel, or witnesses=False in a helper with the same result'),
    ('engine.py', "hasattr(value, 'tobytes')", 'boolop', 'gap', 'an object with one attribute only; none in the tests'),
    ('engine.py', '0', 'const', 'gap', 'default share for a route outside the allocation; only the order of two refusals changes'),
    ('engine.py', 'name == order[0]', 'compare', 'equivalent', 'the entry alone has no predecessors, so the flag adds nothing'),
    ('engine.py', 'name == order[0]', 'const', 'equivalent', 'the entry alone has no predecessors, so the flag adds nothing'),
    ('engine.py', 'True', 'const', 'equivalent', 'the entry flag compares with a constant; the entry alone has no predecessors'),
    ('engine.py', 'parent.then == name', 'compare', 'equivalent', 'swaps the names of the two edge labels consistently'),
    ('engine.py', 'parent.otherwise == name', 'compare', 'equivalent', 'swaps the names of the two edge labels consistently'),
    ('engine.py', "'then' if parent.then == name", 'negate-if', 'equivalent', 'swaps the names of the two edge labels consistently'),
    ('engine.py', "'else' if parent.otherwise == name", 'negate-if', 'equivalent', 'swaps the names of the two edge labels consistently'),
    ('engine.py', 'isinstance(value, (str, bytes', 'negate-if', 'gap', 'digest form changes; no test separates values through this branch alone'),
    ('engine.py', 'isinstance(value, (list, tuple', 'negate-if', 'gap', 'digest form changes; containers still differ through repr'),
    ('engine.py', 'type(value).__repr__', 'negate-if', 'gap', 'digest form changes; objects still differ through their state'),
    ('engine.py', 'type(value).__repr__', 'compare', 'gap', 'digest form changes; objects still differ through their state'),
]


def main() -> None:
    path = ROOT / 'results/v2/e5_mutation.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    for row in data['rows']:
        if row['status'] != 'survived':
            continue
        for suffix, fragment, kind, label, reason in RULES:
            if row['file'].endswith(suffix) and fragment in row['before'] and row['kind'] == kind:
                row['classification'], row['reason'] = label, reason
                break
        else:
            raise SystemExit(f"unclassified survivor: {row}")
    path.write_text(json.dumps(data, indent=1) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
