# Instructor notes: Trust Is Not Transitive

Companion to the [student tutorial](tutorial.md) and [runnable lab](../scripts/tutorial_lab.py). Keep these notes separate when distributing prediction questions. Times in the student tutorial are suggestions for a short unit, not a requirement to teach the entire work in one sitting.

## Teaching plan

Start with the four traces rather than the theorem statements. Have students vote on which layer should stop each action. Insist on a reason: secret egress, missing exact approval, or unauthorized intent. This exposes the common confusion between provenance and meaning.

Teach lessons 1–4 before running code. In lesson 4, ask students to enumerate the parity tables on paper. In lesson 5, distinguish randomness in the calibration sample from randomness in future proposals. The loss is joint unsafe acceptance, so every proposal remains in the denominator. Reserve the CRC proof and Lagrangian argument for a second pass if students have limited probability experience; do not remove their assumptions from any simplified explanation.

The lab is deliberately small and uses the current library. It does not regenerate, overwrite or claim to reproduce the historical primary study. For historical reproduction, use the artifact guide and frozen instruments. During source reading, ask students to identify which facts come from code, which from an experiment, and which remain assumptions.

## Answers to the pauses

**Q1.** A security guide can quote “delete the database” to explain what not to do. A malicious issue can use it to demand unauthorized deletion. Words alone do not establish intent or authority.

**Q2.** Providing `Trace.unsafe` would leak the evaluation answer into the guard. A patch may send no secret and delete nothing in production, yet change the wrong file or implement an attacker-chosen task.

**Q3.** The summary must carry `{U,S}`. Generating a new string does not remove information derived from a secret or make the source authoritative. Automatic relabeling could launder both confidentiality and authority.

**Q4.** (a) Block: approval does not override secret-egress policy. (b) Allow under the deterministic rules, assuming exact current approval; a sandbox-configured runtime separately rejects a production environment. (c) Allow under the deterministic rules. Cases (b) and (c) may still need semantic review; deterministic approval is not a universal semantic guarantee.

**Q5.** String equality is a property of available values. The future data-generating process is a population property; one matching string or observation cannot establish it. Even a successful drift test does not generally certify equality of distributions.

**Q6.** `Tj` is already denied by the secret-egress gate. `Tjp` passes that gate and isolates misuse of the semantic judge. Complete the sentence with “its required structured-view assumption is false.” A conditional contract imposes no guarantee outside its assumptions.

**Q7.** Yes. The interface is a lossy summary. If opposite semantic labels map to the same view, a deterministic function of that view must give them the same verdict, so it cannot classify both correctly. A stochastic function also cannot be correct with certainty on both. The view can still improve robustness against a particular raw-text channel without preserving full meaning.

**Q8.** The checker can accept the declaration. The distributional part of `calibrated_context` is false, so the edge is not realized in the sense needed by the contract. The JSON does not record or verify a distribution proof.

**Q9.** Yes. A new runtime could drop many benign acceptances but add a few unsafe ones. Containment requires a pointwise subset of accepted proposals, not merely a smaller total acceptance rate.

**Q10.** Bypass breaks P1 (complete mediation) and may break P2. A changed judge view breaks P4 and removes the basis for P5's contracted-view containment. The checker establishes well-formed declarations, not implementation realization, trusted host behavior, atomicity or distributional validity.

**Q11.** Hold total proposals at 1,000: 200 are now unsafe and 800 benign. With the same conditional rates, 40 unsafe and 640 benign proposals are accepted. Miss rate stays 20% and utility stays 80%. Joint risk becomes 4%, and accepted conditional risk becomes `40/680`, about 5.88%. If students instead add unsafe proposals without holding total size fixed, accept a consistent denominator calculation; the key invariant is the two conditional rates.

**Q12.** `0.40 * 0.10 * 0.20 * 0.30 = 0.0024`, or 0.24% joint risk. This requires a veto ensemble and mutual conditional independence of guard passes given `Y=1`, not merely pairwise zero correlation.

**Q13.** In the even table the third bit is determined by the first two: it is their exclusive OR. Pairwise independence concerns observing one other bit, not the whole pair jointly. This is a useful place to distinguish “independent pairs” from “mutually independent.”

**Q14.** Total joint risk is 5%. The 2% is unsafe mass on one route among all traffic; it is neither the full pipeline risk nor necessarily the judge's attack-conditional miss rate. Students should specify both event and denominator.

**Q15.** You would estimate acceptance conditional on an unsafe proposal, the attack miss rate. Joint risk also needs the attack prevalence. The binomial experiment in the paper keeps all proposals and records joint-loss indicators.

**Q16.** Selection favors candidates with unusually favorable sampling noise. A confidence bound for a fixed policy does not automatically remain valid when the same data choose that policy. The union-bound proof needs no independence between candidate errors; each fixed candidate's binomial calibration still needs its stated sampling assumptions.

**Q17.** A declared configuration mismatch is checked and blocks. A changed input distribution may leave all configuration values unchanged and pass the applicability check. The latter defeats an assumed statistical premise. Also mention dishonest or stale version identifiers and trusted certificate construction.

**Q18.** The binomial family method has an explicit confidence failure allowance delta. CRC here promises marginal expected loss at most alpha. More expense does not imply lower pointwise loss; the CRC proof needs nested loss for each possible example. Checking only the calibration matrix cannot establish nesting outside that sample.

**Q19.** Only 35% of proposals reach the judge at the chosen routing in the population example. The expected contribution is therefore 350 units. Percentiles are nonlinear; layers can have slow cases on different proposals, and layers can be skipped. Full-decision elapsed samples, with consistent timer boundaries, are needed for a pipeline percentile.

**Q20.** Since `r0-r1 < 0`, a nonnegative multiplier cannot make `mu*(r0-r1) > d` for positive d. The rule does not escalate. Cost is not evidence of lower risk. If an already infeasible system has no useful review option, this formula does not create feasibility; blocking or changing the design may be necessary.

**Q21.** If w is the cheaper policy's weight, its bound is `.05*(1-w)+.15*w = .05+.10*w`. Hence `w <= .5`. Cost decreases as w increases, so the cheapest feasible choice uses half of each: cost 60. The random candidate choice must be independent of the current proposal for this simple weighted-risk calculation, and the bounds must hold simultaneously.

**Q22.** On the valid certificate event, shifted risk is at most 0.12. Without a justified eta there is no useful transfer bound from that inequality beyond probability's upper bound 1. A configuration match supplies no eta.

**Q23.** No. If each of the 100 decision events separately has probability at most 0.01, the union bound is at most 1, which is uninformative. Sufficient per-history conditional bounds would also imply the per-step marginal bounds. An evolving agent session does not acquire these premises from a static calibration replay. Independence would allow a sharper calculation in suitable models but is not needed for the union bound itself.

**Q24.** It quotes suspicious terms to warn against them. The scorer sees their presence, not their semantic role. False blocking limits utility, even though the task is legitimate. The current scorer counts matched substrings among eight indicators, not word frequencies.

**Q25.** No. The paper reports primary per-seed best bounds between 31.1% and 35.0%; a 40% budget would certify candidates. Refusal depends on the budget. Block-all protects joint risk by sacrificing every benign task and therefore cannot by itself establish a useful trade-off. Certification did not automatically locate the defect.

**Q26.** Example: an untrusted issue correctly reports a typo and requests an authorized documentation patch. The typed patch uses `issue`, inherits `{U}`, carries no secret and has an independently justified benign label. The useful comparison requires a semantic pipeline that actually accepts this family, not merely a new family that every system blocks. Do not choose the label based on which pipeline wins.

**Q27.** The parity construction is a mathematical proof about distributions. The 64 gate cases are an exhaustive regression test of a small Boolean interface. PRISM's trace model is a verified finite illustration whose relationship to Python has not been proved. Fresh-seed replay is empirical evidence for the scripted law. None alone proves safety for arbitrary real LLM tool behavior.

**Q28.** A changed threshold changes the recomputed fingerprint, so the old certificate should be rejected. A code change with an unchanged declared version can leave that fingerprint unchanged. Version discipline and trusted host practices are therefore premises, not results of SHA-256 equality.

## Suggested board work

**Containment versus fewer acceptances.** Draw calibrated accepted set `{benign_A, benign_B}` and new accepted set `{unsafe_C}`. The second has fewer elements but greater unsafe mass. Then draw a true subset and explain why the event argument works for every fixed D.

**Veto versus cascade.** Put a perfect judge after a cheap route that accepts some attacks. Have students mark which attacks never reach the judge. This is often more memorable than an equation.

**Confidence versus risk budget.** Write `epsilon=.20`, `delta=.05`, `K=11`, `n=1800`. Epsilon bounds joint unsafe acceptance under D on a valid confidence event. Delta controls repeated-calibration undercoverage. K is the family size fixed in advance. n counts all calibration proposals. None of these says that 95% of individual actions are safe.

**A stronger comparator.** Ask why comparing against naive delegation without a gate can over-credit the new architecture. Then reveal the strict provenance comparator and ask whether its dominance refutes the composition theorem. It does not: a theorem about conditional validity is separate from an empirical claim about useful trade-offs.

## Lab extensions

Use scratch files or in-memory copies, leaving retained study evidence intact.

1. Re-run selection at epsilon=0.01 and explain why `select` raises `ValueError`. Write explicit host fallback code that blocks; do not relax the target automatically.
2. Construct two candidates with identical losses and different costs. Verify that the cheaper eligible candidate wins. Then tie costs and inspect the identifier tie-break.
3. Add a derived observation without its parent's secret label. Locate the rejection in `ProvenanceStore.add`. Repeat with the correct joined label.
4. Change only `context_id` or threshold and inspect the certificate rejection route. Separately run shifted inputs with the original configuration and explain why acceptance persists.
5. Enumerate the parity tables' marginal and pair probabilities directly. Monte Carlo is unnecessary for a distribution with four equally likely outcomes.
6. Create a fixed candidate mixture with certified upper bounds and verify weighted feasibility before using `optimal_mixture`. Contrast it with using known synthetic true risks solely to test the solver.

## Final exercise rubric

| Criterion | Points | Look for |
|---|---:|---|
| Typed actions, authority and deterministic enforcement | 20 | Exact approval, complete mediation, trusted metadata, no overwrite |
| Semantic labels and evaluation plan | 15 | Independent justified labels, legitimate untrusted tasks, no oracle leakage |
| Trust edges and evidence | 20 | Property scope, complete obligations, truthful distinction among evidence kinds |
| Probability and certificate reasoning | 20 | Correct denominators, disjoint route accounting, fixed-family selection, stated sampling assumptions |
| Cost, comparisons and useful work | 10 | Strong control, meaningful utility, no latency/modeled-cost confusion |
| Counterexample and limits | 15 | Concrete failed premise, distribution/configuration distinction, realistic scope |

Award credit for explicitly unresolved assumptions. Do not reward absolute safety claims unsupported by the student's model. Equivalent correct formulations and carefully justified alternative architectures should receive full credit.

## Fidelity notes for instructors

All named propositions and lemmas from `paper/main.tex` appear in the student tutorial's map. Supporting arguments include binomial inversion, tightness, CRC in the finite nested setting, finite mixture support, total variation transfer and adaptive/session limitations. The tutorial expands explanations; it does not add a claim that the library is formally verified.

The source paper's supporting [formal framework](../formal/FRAMEWORK.md) still uses the secret-upload example for its original countermodel. The current manuscript uses the stronger patch-based `Tjp` example with a gate. Teach the current manuscript's version and explain why the gate-preserving example matters.

The runnable lab uses current library versions, genuinely computed calibration bounds, fixed authored fixtures and a finite agreement check. It is a teaching demonstration, not an additional preregistered experiment or independent validation of the authored semantic labels. Its displayed certificate should never be described as evidence for real-world traffic.
