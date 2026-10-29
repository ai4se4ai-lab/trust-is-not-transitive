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
