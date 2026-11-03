---
name: tint-review
description: Analyse guardrail pipelines with the TINT MCP composition checker, explain counterexamples, and recheck proposed repairs. Use for trust propagation, fallback guards, approval branches, and action-boundary design reviews.
---

# TINT pipeline review

Use the connected `tint` MCP tools to check an explicit model of the user's
guardrail pipeline. This is a composition analysis, conditional on contracts.
If tools are unavailable, use [connection instructions](references/connection.md);
do not present an unexecuted analysis as a checker verdict.

Read `tint://guide` for the closed HSL schema and semantics. If the client cannot
read MCP resources, use [the bundled guide](references/guide.md). `list_examples`
and `get_example` provide complete broken/repaired specifications.

Translate the pipeline into goals, accepting routes, layer scopes, per-invocation
evidence, gates and switches. Show the mapping so the user can assess whether it
represents their real system. Preserve unknowns: a model's confidence, an upstream
approval or the presence of another guard does not establish a downstream contract.
Identify any declared evidence whose truth has not been independently established.

Call `check_hierarchy` with the HSL JSON serialized as a string. On rejection,
call `explain_finding` for relevant finding indices. Explain the path and missing
goal/obligation. The witness is an abstract countermodel, not an observed attack.
Structural errors need model repair before behavioural interpretation.

Propose a repair that addresses the missing premise or mediates the effect. Do
not make the check pass by inventing evidence or giving a learned stage an
unconditional contract. If a deterministic gate is proposed, state that its
correctness and host mediation remain obligations for the actual implementation.
Recheck the proposed specification; distinguish proposed changes from deployed ones.

For passing specifications, inspect `routes`, `residual`, `claims`, `checked`,
`construction`, and `warnings`. A passing graph with no accepting routes is vacuous
for usefulness. Use `necessary_obligations` when the user wants assumption analysis;
it removes one evidence entry at a time, not combinations. Use `compare_hierarchies`
only to discuss structural change impact on two passing specifications; it cannot
certify runtime freshness or detect changes in component code/configuration.

Report the verdict, specification hash, relevant findings/witnesses, proposed
repair, remaining assumptions, and practical next step. A timeout or tool failure
means no verdict. TINT does not validate guard accuracy, prompt safety, calibration,
or the assistant's real actions. Do not imply that invoking the skill enforces policy.
