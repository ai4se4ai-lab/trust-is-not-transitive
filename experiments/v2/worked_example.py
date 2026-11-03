"""The DevAgent walk-through of the paper: checker output, a countermodel, sample sizes, traces."""
from __future__ import annotations
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'experiments/v2'), str(ROOT / 'formal/calculus')]
import reference
from harness import tables, term_of
import run
from tint.calibration import binomial_upper
from tint.hsl import check, parse, witness_model


def load(name: str):
    return parse((ROOT / 'experiments/v2/cases' / (name + '.json')).read_text(encoding='utf-8'))


def main() -> None:
    safe_spec, exposed = run.adversarial(load('devagent')), run.adversarial(load('devagent_exposed_judge'))
    report, rejected = check(safe_spec), check(exposed)
    finding = rejected.findings[0]
    model = witness_model(exposed, finding)
    term = term_of(exposed)
    req, scope = tables(exposed)
    passes = {**{k: False for k, n in exposed.nodes.items() if type(n).__name__ == 'Gate'}, **model['passes']}
    verdict = {**{k: 'blk' for k, n in exposed.nodes.items() if type(n).__name__ == 'Guard'}, **model['verdict']}
    branch = {**{k: False for k, n in exposed.nodes.items() if type(n).__name__ == 'Switch'}, **model['branch']}
    assert reference.wf(term, passes, verdict, branch, model['holds'], model['safe'], req, scope)
    assert reference.evaluate(term, passes, verdict, branch) == ('accepted', finding.node)
    share, n = .025, 1800
    sizes = {str(k): binomial_upper(k, n, share) for k in (0, 10)}
    prevalence, budget = .001, .01
    expected = round(prevalence * n)
    result = {'routes': list(report.routes), 'accepted': report.ok, 'residual': [list(x) for x in report.residual], 'checked': [list(x) for x in report.checked],
              'construction': [list(x) for x in report.construction], 'finding': {'code': finding.code, 'node': finding.node, 'detail': finding.detail, 'goal': finding.goal, 'path': list(finding.path)},
              'witness_holds_final': sorted(model['holds'][finding.node]), 'witness_safe': sorted(model['safe']),
              'share': share, 'samples': n, 'upper_by_losses': sizes, 'prevalence': prevalence, 'budget': budget, 'expected_losses_blind_guard': expected,
              'upper_blind_guard': binomial_upper(expected, n, share)}
    result['claims'] = [list(x) for x in report.claims]
    (ROOT / 'results/v2/worked_example.json').write_text(json.dumps(result, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(result)[:900])


if __name__ == '__main__':
    main()
