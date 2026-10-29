# Research direction after the feasibility result

The broad thesis is not yet a sufficient novelty claim. Conditional contracts,
reference monitors, information-flow isolation and calibrated cascades already
exist. The four automated reviews consistently require a distinctive capability
or independent engineering benefit. This document proposes follow-up work;
none of the evidence below is claimed to have been collected.

## Candidate contribution to test, rather than assume

Develop a verdict-receipt discipline in which an allow carries machine-checkable
bindings to the actual action/trace, property scope, view transformation,
provenance dependencies, routing policy and calibration epoch. The effect
dispatcher should consume that receipt only after checking the corresponding
obligations. Known context/version changes invalidate a receipt; unknown
distribution shift remains outside the statistical guarantee. This is not a
claim that receipts, proof-carrying authorization or assurance evidence are new.
Compare explicitly against ContrAgent, ScenicProver, CaMeL/Fides and ordinary
reference-monitor plus policy-certificate implementations before claiming novelty.

The first question is falsifiable: can this mechanism prevent an independently
observed cross-component applicability failure that a comparably engineered
monitor/certificate baseline does not prevent, without changing the semantic
detector or merely denying all useful tasks? If not, report an integration
experience or negative result rather than treating a new vocabulary as a new
formal contribution.

## Technical obligations missing from the current pilot

Specify a small-step operational semantics for the actual dispatcher, receipt
creation/consumption, approvals and every supported tool field. Establish a
checked correspondence to code, or bounded implementation verification with
independently injected faults. Extend the finite model to include stale
approvals, altered views, wrong property scopes, missing provenance, certificate
epochs and fallback transitions; the existing canonical PRISM model does not.

A real adapter must construct dependencies from trusted data handles instead
of accepting a model's declaration that data are public. Cover read, derive,
write and send, including secret-bearing destinations/arguments and derived
outputs. State what is overtainted, what declassification authorizes, and which
covert/control channels remain outside the model. Match guarantees to that
semantics instead of extrapolating from the current constant PATCH operation.

Keep deterministic authority separate from semantic correctness. A statistical
receipt remains conditioned on its calibration law and label quality. Neither
a context string nor a cryptographic digest can certify exchangeability or
resistance to a new adaptive attacker. Human approval is authority for the
specified action, not an assumed infallible semantic judge.

## Independent evaluation design

Use real proposal-generating agents and learned guards whose versions, access
terms and weights/checkpoints are pinned. Validate external dataset terms
separately from repository code licenses. The current machine's small GPU and
CPU-only framework do not establish a usable production-size inference setup;
API/model access and compute must be established explicitly.

Obtain independently authored software-development tasks with executable
completion oracles and policy labels. Hold out task/policy and attack families,
not just identifier suffixes. Include authorized tasks requiring untrusted
content, semantic-only violations that the hard sink cannot decide, and
multi-step secret flows. Keep the canonical traces as unit tests, not the main
effectiveness dataset. Assess labels without showing annotators guard outputs.

Required strong controls use the same tool privileges, hard sink, detector,
judge view and inference budget: a simple sink plus classifier; a matched
whole-policy calibrated monitor; the proposed receipt checks; and an official
maintained relevant defense when accessible. Remove or corrupt one obligation
at a time. The naive missing-sink counterexample remains explanatory, not the
primary competitive baseline.

Attack the exact configured runtime, not an uncertified helper bearing its
name. Log selected certificates, thresholds, context, query budget and every
attempt. Include guard-targeting paraphrases, transfer and attacks that observe
responses; use independent attackers where feasible. Separate static workload
certification from adversarial robustness and measure their utility separately.

Measure completed tasks and failure severity, not just acceptance. Report joint
risk, attack-conditioned success, accepted conditional risk and benign utility
with their denominators. Measure real inference calls/tokens/load latency and
middleware overhead; retain arbitrary cost models only as sensitivity analyses.
Fix calibration/dev decisions before fresh held-out testing and preregister
amendments before execution. A failed or infeasible policy is a valid outcome.

## Publication decision

A TSE submission needs either a substantive technical advance or convincing
independent engineering evidence, ideally both. Current proofs organize
established reasoning and current experiments validate mechanics. If the
stronger matched baseline achieves the same protection, explicitly narrow the
claim. Preserve the negative primary run, the arithmetic correction and all
reviewer concerns as part of the research record.
