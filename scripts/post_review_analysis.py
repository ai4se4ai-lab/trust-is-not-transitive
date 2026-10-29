"""Amendment A3: descriptive post-review analyses of the preserved raw traces.

No new traces are sampled and no decision of the original studies is replaced.
Outputs results/processed/post_review.json:
  * provenance_control: a comparator suggested in review ("deterministic gate,
    then block every action with an untrusted input"), evaluated on the logged
    test and shift traces of both studies;
  * calibration_equivalence: the calibration split replayed through the deployed
    GuardRuntime and through the decision core used to compute calibration
    losses, at each seed's selected threshold (exploratory study only, because
    the primary study certified nothing).
"""
from __future__ import annotations
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from scripts.process_results import read_json,read_lines
from experiments.run import ExploratoryLexicalScorer
from tint.agents import fixture_store
import tint.baselines as baselines
from tint.calibration import Certificate
from tint.layers import deterministic
from tint.model import Action,ActionKind,ApprovalStore,Verdict,action_view
from tint.runtime import GuardRuntime
from tint.spec import parse


def action_of(record):
    data=record['action']
    return Action(ActionKind(data['kind']),data['target'],tuple(data['inputs']),data['environment'])


def provenance_control(directory):
    store,approvals=fixture_store(),ApprovalStore()
    counts={}
    for trace in read_lines(directory/'traces.jsonl.gz'):
        if trace['split'] not in {'test','shift'}:continue
        view=action_view(action_of(trace),store,approvals)
        allowed=deterministic(view)[0]==Verdict.ALLOW and not view.untrusted
        c=counts.setdefault(trace['split'],{'n':0,'unsafe_allowed':0,'benign':0,'benign_allowed':0})
        c['n']+=1
        if trace['unsafe']:c['unsafe_allowed']+=int(allowed)
        else:
            c['benign']+=1
            c['benign_allowed']+=int(allowed)
    return {split:{**c,'joint_risk':c['unsafe_allowed']/c['n'],
                   'benign_utility':c['benign_allowed']/c['benign'] if c['benign'] else None,
                   'modeled_cost_units':1.0} for split,c in counts.items()}


def calibration_equivalence(directory):
    spec=parse((ROOT/'experiments/configs/devagent.json').read_text())
    original=baselines.LexicalScorer
    baselines.LexicalScorer=ExploratoryLexicalScorer
    selections={s['seed']:s for s in read_json(directory/'selections.json')}
    compared=disagreements=0
    try:
        runtimes={}
        for seed,s in selections.items():
            runtimes[seed]=(GuardRuntime(spec,fixture_store(),ApprovalStore(),certificate=Certificate(**s['certificate']),
                                         threshold=s['candidate']['threshold'],epsilon=.2,scorer=ExploratoryLexicalScorer()),
                            s['candidate']['threshold'])
        for trace in read_lines(directory/'traces.jsonl.gz'):
            if trace['split']!='calibration':continue
            runtime,threshold=runtimes[trace['seed']]
            action=action_of(trace)
            deployed=runtime.evaluate(action,trace['issue']).verdict==Verdict.ALLOW
            core=baselines.decide('checked_quarantine',trace['issue'],action_view(action,runtime.store,runtime.approvals),threshold)[0]
            compared+=1
            disagreements+=int(deployed!=core)
    finally:
        baselines.LexicalScorer=original
    return {'compared':compared,'disagreements':disagreements}


def main():
    raw=ROOT/'results/raw'
    result={'amendment':'A3 (post-review, descriptive, no new samples)',
            'provenance_control':{'primary':provenance_control(raw),'exploratory':provenance_control(raw/'exploratory_numeric')},
            'calibration_equivalence':{'exploratory':calibration_equivalence(raw/'exploratory_numeric')}}
    out=ROOT/'results/processed/post_review.json'
    text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if '--verify' in sys.argv:
        assert out.read_text(encoding='utf-8')==text,'post_review.json differs from re-derivation'
        print('Post-review analysis re-derived byte-for-byte.')
    else:
        out.write_text(text,encoding='utf-8')
        print(text)


if __name__=='__main__':main()
