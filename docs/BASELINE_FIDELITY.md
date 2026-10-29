# Baseline fidelity and model status

`rules_only`, `classifier_only`, `judge_only_scripted`, `naive_delegation`,
`naive_with_sink` and `checked_uncalibrated` are controlled toy comparators.
The exposed judge deliberately responds to a fixture phrase. This is a unit
countermodel, not an observed vulnerability in any model or vendor system.
`naive_with_sink` retains deterministic complete mediation and is the essential
stronger control. `checked_uncalibrated` and `checked_quarantine` have identical
decisions at equal thresholds; calibration changes policy selection/certification,
not the truth of individual semantic judgments.

The lexical classifier is handwritten, not fine-tuned. The structured judge is
a deterministic surrogate, not an LLM. Quarantine removes raw text entirely; it
may discard useful semantic evidence and it does not prove semantic safety.
No activation probe, Prompt Guard model, ShieldAgent, LlamaFirewall or official
AgentSpec implementation is executed in this pilot. No toy comparator is named
after these systems in empirical tables. Implementing a regex and calling it a
faithful replica would be misleading. Scorer/judge callables permit a future
host integration, but adapters alone are not external-model evaluation.

The sandbox is an in-memory typed interpreter, not a containerized real shell.
Its safety guarantee is explicitly relative to that semantics. The repository's
Docker image can additionally deny network egress at invocation (`--network
none`); this does not establish shell parsing or covert-channel safety.
