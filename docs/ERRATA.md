# Scientific and instrument errata

## Round 1 automated review — 2026-10-29

1. **Adaptive target attribution.** Preserved adaptive logs use the policy
   label checked_quarantine but actually call fixed-threshold uncertified
   decision-core functions. They do not query GuardRuntime or selected per-seed
   certificates. Primary runtime denies all; its adaptive robustness was not
   measured by that instrument. Processing adds explicit scope metadata and
   paper/guide text corrects attribution; original logs are not rewritten.
   Every first fixed phrase succeeds, so no response-informed adaptation was
   actually observed. These observations are only weak detector-core examples.
2. **Escalation theorem.** Finite Lagrange multiplier existence and complementary
   slackness must be explicit sufficient-optimality premises. They do not follow
   from feasibility. The theorem/proof now state them and give the boundary
   counterexample in the formal appendix.
3. **LP evidence validation.** Re-analysis originally checked stored risk only.
   It now recomputes risk/objective from weights, checks simplex/feasibility and
   independently enumerates vertices to certify the finite-family LP optimum.
   Tampering regression tests cover weights, risk and objective.
4. **Runtime hardening, no historical retuning.** Reject unknown mandatory
   predicates, enforce a host confidence budget, and cap lexical input size.
   Current scorer is versioned lexical-v3-bounded. Reproduction retains frozen
   v1 and v2 experimental scorers. No primary/exploratory observations rerun.
5. **Evidence scope.** Family decision tables and analytic mixture metrics
   reveal the handful of authored behaviors. Intervals measure sampling of
   their prevalences, not independent semantic diversity. Declaration checks,
   actual runtime checks and external assumptions are now tabulated separately.

## Verification study (protocol v2) -- 2026-10-31

1. **E11 harness defect.** The first E11 run reported 12 locality violations in
   7,880 comparisons. All 12 were on routes that need no certificate, which
   `affected_routes` does not list and the harness treated as unaffected; none was
   on a certified route (diagnosed by rerunning the same seed with a per-cause
   count). The harness now compares certified routes only, and E11 was rerun in full.
   Theorem T5 and the implementation were not at fault.
2. **Checker exactness.** Designing the completeness proof showed that the first
   checker demanded a guard's obligations even when gates had established every
   goal, which is a false alarm. The condition is now exact: obligations and scope are
   required only for goals still open at the guard. The mutant
   `check-always-needs-obligations` shows completeness fails without this.
3. **Earlier claim corrected.** The earlier study's checker in `tint.spec` is retained
   unchanged for reproduction; the linear checker of the paper is `tint.hsl.check`.

- E9, first run (2026-10-31): `check` took 20.1 s at 4096 goals and 539.7 s at 32768 goals on 100000 nodes, roughly quadratic in goals, which contradicted the bound in its docstring. Cause: a per-guard `min` scan over all goals and a per-guard set difference. Fixed with a per-layer mask and lowest-bit extraction; findings are unchanged. E3, E4, E5, E6, E9, E10 and E13 rerun on the fixed code. First-run node slopes were 1.158 (chain) and 1.198 (diamonds).

- E13, first run (2026-10-31): the LlamaFirewall, NeMo and CaMeL-style specifications ended in an accepting stage whose layer claimed every goal with no obligation, so they passed trivially. The accepting stage now has an empty scope, because releasing an action promises nothing. The LlamaFirewall goals were also restricted to those its publication states, and PromptGuard's missing distribution-bound guarantee is modelled as an unsupplied obligation. The first run's accepted verdicts for the NeMo and LlamaFirewall models were artefacts of the specification.

- Certificate rule (2026-10-31, found while proving the route-risk theorem): a route's need for a certificate depended only on the accepting layer's scope, so a route whose statistical goal was established by a veto stage opened without a certificate. A route now needs one unless deterministic gates establish every statistical goal on every path to it (`hsl.gated`). No earlier experiment exercised this case. E11 reruns on the new rule. The theorem T10 was added to the proof script at the same time, to machine-check the step of the DAG argument that it covers.

- E5, first run (2026-10-31): 102 of 141 mutants killed by the differential oracle alone. Reading the 39 survivors showed real oracle gaps: its generator never produces cycles, dangling references, view-restricted obligations, gates outside the goals, raising stages or missing certificates, and it does not compare residual lists. `tests/test_hsl_oracle.py` was added and the oracle now also runs the unit tests of the hierarchy language. No mutant exposed a defect in the code itself.

- Round 7 review (2026-10-31): `unsafe_accepted` in E4 was a constant 0; it is now measured. `reference.wf` had no caller; E3 and E6 now run it. E3's first figures: 34,444,800 size-4 specifications of which 6.8% had every node reachable. E7's PRISM model hard-wired the crediting rule. The E13 verdicts were sensitive to the modeller's choice of obligations, so the first two sets of verdicts are withdrawn. E5's first figures, 102 of 141 by the differential oracle and 136 of 141 with tests, covered neither certificates nor fingerprints. Fingerprints ignored checked predicates, goals, closures and partial arguments. Theorem "Route risk" as first stated was false. A generalized meet lemma was false: goals and facts cannot be intersected independently, which led to the coNP-hardness result and exact refinement. Veto stages saw raw text regardless of their view, a raising switch condition escaped `evaluate`, and costs were spent without a budget gate.

- Round 8 review (2026-11-01): residual lists omitted veto stages valued for their facts and all provided facts; a claims list and exact residuals were added. Fingerprints omitted a veto stage's view; digests were hidden by custom reprs, slots and elided arrays. Certificate shares were summed over open routes only, which allowed data-dependent opening; shares are now allocated over all statistical routes in advance. E3's four-node sample was aliased to one goal set. E12b dropped hard routes from risk while its law violated the theorem's premise, and did not use the rebuilt engine. E15's first extraction lost the Colang 2 and per-tool hook rails, hard-coded zero for escalation and reported a tautology as "open under adversary". The first E15 summary (43 configurations, 3 deterministic rails of 93) is withdrawn.
