# Response to the round-6 reviews (rewritten manuscript)

The manuscript was rewritten from scratch on 2026-10-29 using the TSE template in
`docs/TSE/` (single `paper/main.tex`, single `paper/references.bib`). Draft v1 is
archived as `before_main.tex.txt`; the revision as `after_main.tex.txt`. All three
referees recommended major revision. Below, each major issue is mapped to the
change made. Issues that need new experiments are listed at the end and are stated
as limitations in the paper rather than resolved.

## Cross-cutting changes

| Concern (reviewers) | Change |
|---|---|
| Checker/trust edges carry no weight in the soundness result (R1 M1, R3 M2) | New Def. 2 with named obligations, their meaning and a *kind* (checked / by construction / assumed); Def. 3 distinguishes *well-formed* (checked by Alg. 1) from *realized* (implementation property); new Lemma 1 (checked and realized edges ⇒ callee obligations hold); new Lemma 2 (containment of certified vs. deployed decision function); Prop. 2 restated with premises P1–P5, P4 = edges realized, P5 = i.i.d. calibration + containment; worked two-route DevAgent example showing that an unrealized `quarantine` obligation invalidates the route-2 certificate (the T_j^p failure). |
| Evidence items are uninterpreted; distributional assumption cannot be discharged at an edge; shift is F1 inside TINT (R1 M2) | New Table III classifies every DevAgent obligation by kind and who establishes it (trusted mediator, not the calling layer); `calibrated_context` split into a checked configuration part and an assumed distribution part; shift result now explicitly described as an assumed obligation that was false and that the discipline made visible but did not prevent. |
| Contract semantics mix per-run and distributional assumptions; meaning of non-transitivity (R1 M3, R3 M2) | Hard vs. statistical contracts defined separately; text states that trust *is* composed along declared edges via the composite guarantee of a sub-hierarchy, and that TINT forbids only short-cut edges. Position vs. probabilistic/stochastic contracts added. |
| Prop. 1 trivial and about the wrong mechanism (R1 M4, R3 comprehension) | Prop. 1 rebuilt on T_j^p (a rule-respecting patch with an instruction for the judge); names the violated composition rule; idealized-judge premise made explicit; T_j now explicitly handled by the gate. Fig. 1 redrawn with calls left-to-right and verdicts returning, consistent with Fig. 2. |
| Prop. 3/4 missing premises, citations (R1 M5) | Threshold model added to (c); "passes" defined; concrete numeric instance for (d); Fréchet–Hoeffding and Bernstein's example named; tightness quantifier stated. |
| Certificate binding overclaimed; calibration path ≠ deployed path (R1 M6, R2 M8) | Text now says the fingerprint binds *declared* versions, does not hash code, and that view/context are configuration constants; calibration via `baselines.decide` disclosed; new post hoc replay of the calibration split through `GuardRuntime` (A3): 0 disagreements in 18,000; audit row added. |
| H1 formal evidence vacuous (R1 M7, R2 M4) | H1 now cites `test_all_deterministic_cases` (regression check against a re-typed formula); PRISM abstraction described as an illustration that encodes each trace's routing; `formal/check.py` no longer cited as verification; hard-violation metric acknowledged to share the gate's predicate; environment double-block disclosed. |
| Checker "linear" claim false (R1 M8, R2 M5) | Complexity stated as O(|L| + Σ_e(|P_caller| + |E_e|)); fitted log–log slope reported from existing data (macro `CheckerSlope`); cause and one-line fix stated; scaling figure removed. Checker study not rerun. |
| RQ3 effect holds by construction; statistics uninformative (R1 M9, R2 M1, R3 M3) | Abstract and headings rewritten ("removed the judge-targeting family, as designed"); population values from authored masses lead, replay confirms; statistics reduced to one sign-consistency sentence; scale claim (336,000 decisions) removed from the abstract; construct-validity threat that the design cannot observe the cost of the structured view. |
| Missing provenance comparator dominates TINT (R2 M2) | Added as post hoc B7 (Amendment A3) to Tables VII–VIII and text: 0% risk, same utility, 0% shift risk in both studies. Fixture-law property (no benign issue-derived action) stated in the setup; "observability limit" sentence corrected; new lesson "try provenance first". |
| Gate "exposed the defect" overclaimed (R1 M9c, R2 M3, R3 M6) | Reworded everywhere: the gate refused to deploy; humans found the defect by reading counts; budget counterfactual (any ε ≥ max per-seed bound would have certified the defect, macro `PrimaryBoundMax`); any acceptance test against a budget would also have caught it; degenerate-grid diagnostic suggested. |
| Prereg chronology, H6 verdict (R2 M6) | Disclosed that `dataset.py`/`run.py` were committed after the tag; outcome column added to Table V; H6 deviation explained (literal rule met trivially by block-all); H7/H8 registration justified. |
| Selection degenerate in sandbox (R2 M7, R1 M9b) | H5 paragraph and RQ2 answer state that sandbox selection reduced to feasibility with a name tie-break; escalation theory not exercised empirically; deployable LP must use u_j. |
| Latency asymmetric, logging misattributed (R1 m7, R2 M10) | "CPU" → wall-clock "Time"; asymmetric timing boundaries and disabled logging disclosed; attribution sentence removed. |
| Artifact `verify-results` failed; CRLF manifest (R2 M11) | Manifest hashing normalizes CRLF→LF for source files; manifest refreshed; `verify-results` and `verify-paper` pass; post-review analysis added to `verify-results`; ARTIFACT.md stale page count and vendored-template statements fixed. |
| Quarantine term inverted vs. CaMeL/dual-LLM; lesson not actionable (R3 M4, R1 M10) | Renamed "structured-view judge"; explicit contrast with CaMeL's quarantined LLM; dual-LLM pattern cited; Lesson 3 rewritten as a design trade-off with a concrete projection for coding agents. |
| No real guardrail stack mapped (R3 M5) | New Discussion subsection mapping a hypothetical deployment of LlamaFirewall's published components onto TINT edges and obligation kinds; "most stacks we examined" removed; stated as not validated with practitioners. |
| Notation/label overloading (R3 M1, R1 m1–m4) | Comparator A1 → B6; assumptions → P1–P5; amendments A1–A3 only; π → θ (prevalence), multiplier λ → μ, guards N, routes q/r, token count c; F1–F3 merged into C1–C3; "sink" → "deterministic gate". |
| Figures (R3 M7) | Fig. 1 redrawn; scaling and dependence plots removed (results in text); new route figure (Fig. 4) showing DevAgent masses on acceptance routes; Fig. 3 caption/text explains the four oddities of the spec. |
| Missing prior work (R1 M10) | Added and verified (Crossref/author page): Christianson & Harbison 1997; Delahaye et al. 2011; Nuzzo et al. 2019; Ligatti et al. 2005; Lindemann et al. 2023; Willison 2023. Prop. 5 identified as a special case of Learn-then-Test. Related-work table re-rated (TINT gets S for Spec., Stat., Trust, Agent) with rating procedure stated. |
| Section IV-E imprecise statements (R1 M11) | Adaptive-attacker argument given; TV bound stated for the selected policy (u_j + η); horizon premise stated; atomicity added to P1; i.i.d. (not exchangeability) for Clopper–Pearson. |

## Not resolved (require new experiments; stated as limitations)

- A judge that can add information under a structured view; per-route certificates
  with q > 1 in the sandbox; benign issue-derived actions and paraphrased templates
  (R1 N1/N2, R2 M9, R3 Q3).
- A non-trivial PRISM MDP with nondeterministic scorer/judge (R1 N3, N4 bounded-exhaustive checker validation).
- Meaningful adaptive attacks (R1 N5).
- Rerunning the checker study after the linearity fix; symmetric re-timing.
- Real LLMs, learned guards and external benchmarks (H7).

## Deliberate choices that differ from a reviewer's suggestion

- R2 noted that the relaxed `verify_numbers.py` no longer flags integers typed in
  prose. This is intentional: empirical results are decimals/percentages and are all
  macros; the integer ban had forced unnatural prose ("ten", spelled-out section
  references). Integer result counts in the paper are still macros.

## Round 2 (re-review of the revision) and final changes

| Reviewer | Round 1 (N/R/Rel/V&T/P) | Round 2 | Recommendation |
|---|---|---|---|
| R1 formal methods | 2/2/4/4/4 major | 2/3/4/5/4 | major (narrow): one blocking request, a new sandbox experiment exercising the semantic layers |
| R2 empirical SE + artifact | 3/2/4/3/4 major | 3/3/4/4/4 | major (narrow); minor if RQ3 is re-scoped instead of running the experiment |
| R3 SE4AI + presentation | 2/3/3/5/3 major | 2/4/3/5/4 | minor |

Applied after round 2 (47 text edits): RQ3 re-scoped to engineering feasibility, with the
registered value question stated as open; abstract shortened, qualified ("protocol-registered",
manual obligation audit) and restored to report all negative results; R2's factual correction
(the benign-security family *is* a benign issue-derived patch) fixed in the paper and in A3;
"gate" now means only the deterministic L1 gate (certification is "the certificate
requirement"); B7 described as the strictest taint policy, not CaMeL/Fides; Def. 3 now includes
the `provides` condition and per-invocation vs. distributional realization; P4 now used in the
proof of Prop. 2 via Lemma 1; G1, G2 written out in Prop. 1; runtime's non-use of declared
`requires`/`provides` disclosed; notation clashes removed (Ω edge obligations, ℓ route index,
γ escalation probability, w token count); per-depth checker slope added; synthesis LP's use of
true risks disclosed; macro-provenance claim narrowed; GitHub URL withheld for anonymous review.

Still open (author decision needed): the new exploratory sandbox experiment requested by R1/R2
(benign issue-derived patches a judge can accept, a text-using judge, paraphrased templates);
kind field in the DSL; committing and tagging the revision and a clean-clone/Docker
verification; refreshing formal/FRAMEWORK.md to the new premises.
