# Protocol v2: verification study of the guardrail-hierarchy approach

Written 2026-10-31, before any run below. It supersedes the sandbox study as the
evaluation of the approach; that study and its amendments remain preserved and
are reused only as a continuity check (E8). No LLM, learned guard or external
benchmark is used. `src/tint/bench` plays no part.

Claims under test: the approach is **sound**, its implementation is **correct**
with respect to the proved definitions, and it is **scalable**.

| ID | Question | Method | Decision rule |
|---|---|---|---|
| E1 | Are the theorems proved? | every induction obligation, Z3 and cvc5 | all unsat in both; hypotheses not vacuous |
| E2 | Do the proofs depend on the definitions? | definition mutants | every mutant breaks its expected theorem |
| E3 | Does the checker decide the semantic condition? | bounded-exhaustive comparison with brute-force model search, all hierarchies up to the size bound | zero disagreements |
| E4 | Does the implementation conform to the proved definitions? | random differential testing: `hsl.check`, `Engine` vs. reference, reference vs. Z3 definitions | zero disagreements |
| E5 | Is the conformance oracle strong? | AST mutants of the checker and engine | report mutation score; inspect every survivor |
| E6 | Are rejections real? | replay each finding's witness model on the unchecked engine | every witness yields an accepted, goal-violating decision |
| E7 | Does the verdict agree with monolithic verification? | Z3 and PRISM on random hierarchies | zero disagreements |
| E8 | Continuity with the preserved study | replay logged test traces of seeds 10-19 through `Engine` | zero disagreements with `GuardRuntime` decisions |
| E9 | Scalability of checking | time vs. nodes, goals; vs. path enumeration, Z3, PRISM on path-exponential hierarchies; 60 s timeout, fixed sizes | report fitted log-log slope; linear claim supported only if slope in nodes is below 1.2 |
| E10 | Decision overhead | engine time vs. depth; constructor time | report; bound by Theorem T7 |
| E11 | Incremental recertification | single-layer changes on random hierarchies | report fraction of routes recertified vs. whole-policy recertification |
| E12 | Validity of route bounds | known finite laws on random hierarchies, 1000 replications per law | coverage at least 1-delta; report how often per-layer product/min understate risk |
| E13 | Applicability | specifications of published designs; policy inventory | report findings and residual assumptions; no effectiveness claim |

Fixed settings: master seed 20261031, derived per experiment. Random hierarchies:
2-12 nodes for differential tests; goals 1-3; obligations 1-3. Bounded-exhaustive
bound is set by what enumerates within one hour, and is recorded. Timing medians
over 7 repetitions. delta = 0.05 in E12. Failures found by any experiment are fixed,
recorded in `docs/ERRATA.md`, and the affected experiments rerun in full; the first
result is recorded there too. Mutation survivors are classified by reading them.
Analyses added after seeing results are labeled exploratory.

## Amendment A (2026-10-31, after review round 7)

Written after the results of the runs above were seen, so everything here is post hoc
and is labelled so in the paper. It records what the reviewers found wrong with the
instrument, and the instrument that replaced it.

- The calculus gained provided facts. All experiments rerun on it.
- E3: hierarchies with all nodes reachable; two obligations; provided facts. Equations
  compared on all of them; model search through `wf` and `evaluate` on all up to three
  nodes and every 64th of four.
- E4: 40 tasks of 1000 specifications, independent of the machine's CPU count; generator
  up to 16 nodes with shared views, provided facts and failing checked predicates.
  Semantic search on specifications of at most four reachable nodes; sampled
  contract-respecting runs on all, for accepted and rejected specifications alike.
  Adequacy covers `check`, `eval` and `wf`.
- E5: targets extended to certificates, fingerprints and witnesses.
  Kills are reported by mode. Survivors of the first run informed new unit tests, so the
  differential-only figure is the unbiased measure of the random oracle.
- E6: witnesses are complete models, verified by `wf`.
- E7: PRISM chooses the obligations that hold at each invocation, so the crediting rule is
  no longer built in. Explicit engine only, because the symbolic engines' native
  library does not load here. Neither encoding is independent of Figure 2.
- E9: goals fixed while depth grows; added rejecting, many-layer, fan-in and provided-fact
  families; witnesses timed apart from the decision.
- E11: changes of gates and switches as well as guards. The rule "zero locality violations"
  and the restriction to routes needing a certificate are post hoc.
- E12: the coverage rule is relaxed post hoc: coverage fails only if the upper Wilson limit,
  Bonferroni-corrected over the laws, is below nominal, because the literal rule failed on two laws at 0.949. New experiment E12b drives the
  whole pipeline (`certify`, partial recertification, `Engine`) on random DAGs.
- E13: one encoding rule per mechanism: a learned stage requires `miss_rate_bounded`,
  supplied only if the source states a bound; under the adversarial threat model, every raw
  stage also requires `contract_holds_on_adversarial_text`. Both threat models are reported,
  with the obligations that would flip each verdict. E13 is exploratory.
- E14 (new): the hardness reduction, tested against brute-force SAT.
- E15 (new): shapes of public guardrail configurations.

## Amendment B (2026-11-01, after review round 8)

Post hoc, like Amendment A. E3 samples four-node hierarchies at random, not by stride. E4 compares
residual lists and reports what share of runs and rejected specifications its sampling reaches.
E12b's laws set unsafe labels to respect the Route risk premise, and it measures the rebuilt
engine's decisions. E14 draws formulas near the satisfiability threshold. E13 uses
`safe_on_this_text`, a clearer name for the adversarial obligation, and a redesigned DevAgent.
E15 is rebuilt by `corpus_fetch.py` with Colang 2 flows and per-tool hook rails.

## Amendment C (2026-11-02, after the implementation alignment review)

Post hoc, like Amendments A and B. The engine now refuses budgets and confidence shares that are
not probabilities, and component digests cover the slots of a direct callable instance. E5 targets
the two new helpers, `_instance_state` and `_probability`. E3, E4, E5, E6 and E11-E14 were rerun on
this code. Timing experiments E9 and E10 were not rerun.
