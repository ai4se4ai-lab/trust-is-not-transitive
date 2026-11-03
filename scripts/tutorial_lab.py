"""Undergraduate lab: exercise the existing library without changing study results.

Run from the repository root: python scripts/tutorial_lab.py
The certificate below is genuinely computed on authored, independent fixtures.
It is evidence for that fixture law only, not for arbitrary agent traffic.
"""
from pathlib import Path
import itertools
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

import numpy as np

from experiments.dataset import sample
from tint.agents import fixture_store
from tint.baselines import decide
from tint.calibration import Certificate, binomial_upper, veto_bound
from tint.layers import LexicalScorer, StructuredJudge
from tint.model import ApprovalStore, action_view, Verdict
from tint.runtime import GuardRuntime, policy_fingerprint
from tint.spec import parse
from tint.synthesis import Candidate, select


def main() -> None:
    print("1. Same guard miss rates, different joint risks (attack prevalence = 1)")
    rates = [0.1, 0.2, 0.3]
    for shock in [0.0, 0.5, 1.0]:
        print(f"   common-shock weight {shock:.1f}: {veto_bound(rates, common_shock=shock):.3f}")

    print("\n2. Pairwise independence does not determine triple risk")
    for parity in [0, 1]:
        states = [s for s in itertools.product([0, 1], repeat=3) if sum(s) % 2 == parity]
        triple = sum(all(s) for s in states) / len(states)
        print(f"   parity {parity}: {states}; triple miss = {triple:.2f}")

    print("\n3. Zero observed errors still leave uncertainty")
    print(f"   0 errors / 100 examples, one fixed policy, delta=.05: upper = {binomial_upper(0, 100):.5f}")

    spec = parse((ROOT / "experiments/configs/devagent.json").read_text(encoding="utf-8"))
    store, approvals = fixture_store(), ApprovalStore()
    thresholds = [i / 10 for i in range(11)]
    candidates = [Candidate(f"threshold-{t}", t, 3) for t in thresholds]
    layer_costs = {"L1": 1, "L2": 20, "L3": 1000, "L4": 5000}
    calibration = sample(10, "calibration", 1800)
    losses, costs = [], []
    for trace in calibration:
        view = action_view(trace.action, store, approvals)
        outcomes = [decide("checked_quarantine", trace.issue, view, t) for t in thresholds]
        losses.append([int(trace.unsafe and allowed) for allowed, _ in outcomes])
        costs.append([sum(layer_costs[layer] for layer in layers) for _, layers in outcomes])

    print("\n4. Calibrate a fixed family, then deploy through GuardRuntime")
    chosen, upper = select(np.array(losses), np.array(costs), candidates, epsilon=.2, delta=.05)
    policy_id = policy_fingerprint(spec, chosen.threshold)
    certificate = Certificate(policy_id, "teaching-fixtures-v1", "structured-v1", upper, .05, len(calibration))
    runtime = GuardRuntime(spec, store, approvals, certificate=certificate,
                           context_id="teaching-fixtures-v1", threshold=chosen.threshold, epsilon=.2)
    print(f"   selected {chosen.identifier}; simultaneous upper bound = {upper:.5f}")
    # Verify the teaching lab's calibration function and deployed function agree
    # on these fixtures. This finite check is not a universal refinement proof.
    disagreements = 0
    for trace in calibration:
        expected, _ = decide("checked_quarantine", trace.issue,
                             action_view(trace.action, store, approvals), chosen.threshold)
        actual = runtime.evaluate(trace.action, trace.issue).verdict == Verdict.ALLOW
        disagreements += actual != expected
    assert disagreements == 0, "calibration/runtime mismatch invalidates this demonstration"
    print(f"   calibration/runtime disagreements: {disagreements}")
    seen = set()
    for trace in sample(10, "test", 1200):
        if trace.family not in seen:
            seen.add(trace.family)
            result = runtime.evaluate(trace.action, trace.issue)
            print(f"   {trace.family:20s} score={str(result.score):4s} {result.verdict.value:5s} route={result.route}")

    print("\n5. Same configuration, changed data distribution")
    shifted = sample(10, "shift", 600)
    unsafe_accepts = sum(t.unsafe and runtime.evaluate(t.action, t.issue).verdict == Verdict.ALLOW
                         for t in shifted)
    print(f"   shifted joint risk = {unsafe_accepts / len(shifted):.1%}; configuration still matches")

    print("\n6. Floating-point boundary from the historical study")
    historical = .04 + .12 * 3
    corrected = (4 + 12 * 3) / 100
    print(f"   historical={historical!r}, corrected={corrected!r}, cutoff=0.40")
    print(f"   historical >= cutoff: {historical >= .4}; corrected >= cutoff: {corrected >= .4}")
    print(f"   current scorer: {LexicalScorer().version}; judge: {StructuredJudge.version}")
    print("\nNo study files were written. These results concern authored fixtures only.")


if __name__ == "__main__":
    main()
