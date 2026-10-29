"""Smoke test uses an explicitly synthetic demo certificate, never empirical evidence."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from tint.agents import Sandbox,canonical_traces,fixture_store
from tint.baselines import decide
from tint.calibration import Certificate
from tint.model import ApprovalStore, action_view
from tint.runtime import GuardRuntime, policy_fingerprint
from tint.spec import parse


def main():
    spec=parse((ROOT/'experiments/configs/devagent.json').read_text())
    # Fixture certificate tests runtime plumbing only. It is NOT a calibrated claim.
    certificate=Certificate(policy_fingerprint(spec,.2),'demo-only','structured-v1',.01,.05,1000)
    rt=GuardRuntime(spec,fixture_store(),ApprovalStore(),certificate=certificate,context_id='demo-only')
    box=Sandbox(rt)
    results=[]
    for trace in canonical_traces():
        a=trace.action
        response=box.call(json.dumps({'kind':a.kind.value,'target':a.target,'inputs':a.inputs,'environment':a.environment}),trace.issue)
        view=action_view(a,rt.store,rt.approvals)
        results.append({'trace':trace.identifier,'checked_execute':response['executed'],
                        'naive_execute':decide('naive_delegation',trace.issue,view)[0],
                        'naive_with_sink_execute':decide('naive_with_sink',trace.issue,view)[0],
                        'route':response['decision']['route']})
    assert [r['checked_execute'] for r in results]==[False,True,False]
    assert results[2]['naive_execute'] and not results[2]['naive_with_sink_execute']
    print(json.dumps({'scope':'fixture demonstration; certificate is synthetic test data','traces':results},indent=2))


if __name__=='__main__':main()
