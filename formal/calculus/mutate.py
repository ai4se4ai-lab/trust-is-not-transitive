"""Show that the proofs depend on the definitions: each mutant must break an obligation.

A vacuous or over-assumed proof script would survive these mutations. The expected
theorem is the one the mutation should invalidate.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MUTANTS = {
    'check-ignores-obligations': 'T1-soundness', 'check-ignores-scope': 'T1-soundness',
    'gate-does-not-establish': 'T2-completeness', 'switch-checks-one-branch': 'T1-soundness',
    'check-always-needs-obligations': 'T2-completeness', 'contract-ignores-assumption': 'T2-completeness',
    'evidence-not-realized': 'T1-soundness', 'gate-credits-without-obligations': 'T1-soundness', 'gate-fails-open': 'T1-soundness', 'block-falls-through': 'T1-soundness',
    'evidence-inherited': 'T1-soundness', 'facts-not-realized': 'T1-soundness', 'uniq-allows-repeats': 'T2-completeness'}


def main():
    rows = []
    for mutant, expected in MUTANTS.items():
        output = subprocess.run([sys.executable, str(HERE / 'prove.py'), '--z3-only'], env={**os.environ, 'TINT_MUTANT': mutant},
                                capture_output=True, text=True, check=True).stdout
        broken = json.loads(output.strip().splitlines()[-1])
        killed = any(theorem == expected and answer == 'sat' for theorem, _, answer in broken)  # a countermodel, not a timeout
        rows.append({'mutant': mutant, 'expected_theorem': expected, 'broken': broken, 'killed': killed})
        print(mutant, 'broken obligations:', len(broken), 'killed' if killed else 'SURVIVED', sorted({t for t, _, _ in broken}), flush=True)
    out = ROOT / 'results/v2/proof_mutants.json'
    out.write_text(json.dumps(rows, indent=1) + '\n', encoding='utf-8')
    print(sum(r['killed'] for r in rows), 'of', len(rows), 'mutants killed')
    sys.exit(0 if all(r['killed'] for r in rows) else 1)


if __name__ == '__main__':
    main()
