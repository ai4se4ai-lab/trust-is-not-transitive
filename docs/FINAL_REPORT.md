# Final report — local pilot, 2026-10-29 UTC

The research idea has been developed into a scoped formal framework, executable
prototype, reproducible local evaluation and IEEE-format manuscript. **The full
TSE effectiveness objective is not achieved.** All final automated referees
recommend rejection: substantial novelty and independent real-agent evidence
remain unestablished. No result, reviewer score, human study or publication is
invented to satisfy the master prompt. This is a useful research starting point,
not a production guard or submission-ready validation.

## Deliverables

- [Paper PDF](../paper/main.pdf), [single authored LaTeX source](../paper/main.tex),
  [bibliography](../paper/references.bib), generated result macros and vector figures.
- [Artifact guide](../ARTIFACT.md), [quick start](../README.md), exact Python locks,
  Docker smoke recipe (unvalidated engine), core CI workflow (not remotely run).
- [Framework/proofs](../formal/FRAMEWORK.md), real PRISM model/transcripts,
  independent finite checks and seeded sanity tests; no Lean/Isabelle proof.
- [Library](../src/tint): immutable actions/provenance, closed contract DSL,
  exact fixed-topology checks, deterministic sink, structured judge interface,
  confidence/configuration binding, calibration and finite-family synthesis.
- [Preregistration](../experiments/PREREGISTRATION.md), local tag `prereg-v1`,
  [amendments](../experiments/AMENDMENTS.md), datasheet and benchmark code-license audit.
- Original and exploratory compressed trace/decision logs, raw-derived
  [summary](../results/processed/summary.json), file-hash manifest and semantic replay.
- Four rounds of three independent automated reviews, response letters and
  actual latexdiff PDFs; fresh-context student logs and reassessment.
- [Next substantive study](NEXT_STUDY.md), stating a falsifiable path toward a
  stronger contribution without asserting unverified novelty.

## Actual results and interpretation

The two studies preserve 168,000 and
168,000 per-decision records, respectively,
including development, test and shift replays of seven toy comparators. Each
test split has 12,000 proposals; repeated identifier suffixes do not create
independent semantic tasks. The authored fixture law is deliberately simple.

The primary candidate family was uncertifiable in every seed. Its checked
runtime has 0.00% joint unsafe acceptance and
0.00% benign utility because it denies uncertified actions.
That is a negative service-utility result, not useful Pareto superiority.

After a disclosed floating-point boundary correction, a separate fresh-seed
exploratory replication has 10.16% joint unsafe acceptance,
66.46% benign utility and
25.40% unsafe fraction among accepted proposals.
The uncalibrated checked control makes identical decisions. Its designed
all-attack encoded shift is accepted at
100.00%.
These observations do not establish learned-guard effectiveness or robustness.

A separate known nested-loss law gives 99.60%
true-risk bound coverage over 1,000 calibration replications,
with exact interval [98.98%,
99.89%]. This is static iid synthetic
coverage, not a bound on an adaptive deployment. The original search target
was an uncertified fixed-threshold core, mislabeled checked_quarantine; the
attribution is corrected without rewriting raw observations. First-query
success supplies no observed response-informed adaptation.

The restricted DSL fully supports only the two declared deterministic rules;
semantic injection is a statistical proxy and path confinement/spending are
unsupported. The claim of full expressiveness is refuted. Theoretical risk
accounting and finite-family selection are scoped standard constructions,
not claimed new mathematical laws.

## RQs and hypotheses

RQ I has scoped definitions, conditional proofs, canonical countermodel,
syntactic obligation checking and mutation/inventory evidence. It does not
provide general decomposition or a proved implementation/adapter refinement.
RQ II has corrected route versus veto bounds, explicit dependence premises,
calibration utilities, conditional escalation optimality, and finite-family
experiments. RQ III has local feasibility/negative evidence only; practical
real-agent engineering value remains inconclusive.

| ID | Recorded outcome | Scope/limitation |
|---|---|---|
| H1 | supported within tested typed semantics | finite abstraction is not a runtime refinement proof |
| H2 | supported for planted mutation classes | not real-world specification precision/recall |
| H3 | supported for the synthetic iid law | not an adaptive deployment guarantee |
| H4 | supported; strong naive-with-sink control also prevents Tj | scripted counterexample |
| H5 | supported within the finite family | no unrestricted n-layer optimum/approximation claim |
| H6 | inconclusive for useful safety-utility improvement in primary; exploratory tradeoffs reported | primary method blocks all; exploratory follows disclosed bug fix |
| H7 | inconclusive/not run | no real LLM or external benchmark execution |
| H8 | refuted | only the two declared deterministic policy classes fully supported by the DSL |

## Deviations and corrections

- Literature is a scoping review with 67 bibliographically verified
  primary-source records, not an exhaustive systematic review. Broad records
  were abstract-screened; closest-work full-text comparison was strengthened
  during the project. Initial log wording overstated that depth at the initial
  gate and is corrected here. No blanket first-cascade/contracts novelty claim.
- A1 preserves primary arithmetic/infeasibility and runs numeric correction
  on fresh seeds as exploratory. No thresholds or risk budgets were retuned.
- A2 labels post-review family/population/conditional-risk analyses descriptive
  exploratory and corrects search attribution. LP checks and read-only replay
  strengthen validation without creating new held-out outcomes.
- Original synthesis calibration counts were not logged. Those original bounds
  cannot be recalibrated from their records; amended instrumentation retains
  counts. This provenance limitation remains disclosed.
- Runtime hardening rejects unknown mandatory predicates/extra edges, enforces
  a confidence budget and versions input bounds. Historical scorers remain
  frozen; their CPU times do not describe the hardened default.
- Missing real models, official baselines, external datasets, human pilot,
  actual inference costs and meaningful adaptive attacks are not relabeled as
  completed experiments. Docker execution and archival publication are absent.

## Reviewer history (reported without adjustment)

Scores are each referee's 1–5 ratings; automated development critiques are not
independent human peer review. The four-round stopping limit was reached
without rubric convergence. All final recommendations remain reject.

| Round | Referee | Novelty | Rigor | SE relevance | Transparency | Presentation | Recommendation |
|---|---|---|---|---|---|---|---|
| 1 | R1 | 2 | 3 | 3 | 4 | 4 | Reject |
| 1 | R2 | 2 | 2 | 4 | 5 | 4 | Reject |
| 1 | R3 | 2 | 2 | 3 | 5 | 4 | Reject |
| 2 | R1 | 2 | 3 | 3 | 4 | 4 | Reject |
| 2 | R2 | 2 | 2 | 4 | 5 | 4 | Reject |
| 2 | R3 | 2 | 3 | 3 | 5 | 4 | Reject |
| 3 | R1 | 2 | 3 | 3 | 4 | 4 | Reject |
| 3 | R2 | 2 | 2 | 4 | 5 | 4 | Reject |
| 3 | R3 | 2 | 3 | 3 | 5 | 4 | Reject |
| 4 | R1 | 2 | 3 | 3 | 4 | 4 | Reject |
| 4 | R2 | 2 | 2 | 4 | 5 | 4 | Reject |
| 4 | R3 | 2 | 3 | 3 | 5 | 4 | Reject |

Technical/reporting defects were repaired. Residual major concerns require new
research: a distinctive benefit over competent matched controls, independently
authored real-agent tasks and learned guards, meaningful attack evaluation,
and stronger data-flow/executor assurance. No additional seed sampling of the
same scripted law resolves these concerns.

## Student-reader outcome

The fresh automated reader assessed 103 paragraph/definition/proof/
caption entries, with 28 initially scoring 2 or 3.
After substantive rewrites, every one of those 28 entries scores
0 or 1. The reader correctly reconstructs the different canonical exfiltration
and empirical patch cases, theorem premises, risk denominators, optimization
objective, calibration mechanism and scoped results. Initial scores remain
unchanged in the preserved log. Optional score-1 precision edits followed;
this is a clarity pass, not a human usability study or scientific endorsement.

## Reproduction and checks actually executed

- 56 tests passed, including provenance/approval/contract/certificate faults,
  numeric boundary and independent LP-evidence tampering. Recorded core
  statement/branch coverage is 99.85%.
- Real PRISM checks 6 canonical configurations and both
  reachability properties; independent enumeration covers
  64 hard-predicate cases and seeded
  probability sanity tests cover 10,000 instances.
- Raw summaries re-derive byte-for-byte. Read-only replay validates all
  336,000 historical decisions
  against trace identities/configurations/non-timing semantics. Mixture weights,
  constraints and objectives are checked against separate vertex enumeration.
- Full exact-lock installation succeeded in a fresh Python environment. The
  complete `tasks.py all` pipeline passed in a separate detached checkout,
  including real PRISM, both historical instruments, analyses, PDF and checks.
  Non-timing scientific metrics match; timing/environment bytes need not.
  See [author reproduction record](../results/reproduction_check.json).
- `verify-paper` checks generated empirical source values, bibliography
  records, notation registry, cross-references and extractable layout. It
  does not prove the provenance of every PDF glyph or semantic notation
  consistency. Mathematical constants and structural/citation numbers have
  different provenance. Rendered PDF pages were visually inspected.
- Git attributes preserve recorded JSON/CSV bytes and normalize source line
  endings for portable hash verification. Original experiment files remain
  original observations; only current unit-test coverage records are refreshed.

## Section-zero compliance checklist

- [x] No fabricated experiment, citation, proof mechanization or favorable score.
- [x] Negative primary, arithmetic correction, shift failure and unavailable
  evidence reported rather than hidden.
- [x] Empirical paper values generated from raw-derived results with macro
  provenance and file hashes; mathematical constants come from specification/proofs.
- [~] Number verification is source-level. The literal every-PDF-glyph/CI claim
  is not established; remote CI was written but not run.
- [x] All bibliography entries have opened-source verification records;
  unverified seed identities are not invented.
- [x] Empirical studies use seeded replications and a frozen protocol; changes
  are amended/labeled, and originals preserved.
- [~] Exact Python locks and tool provenance provided and tested locally;
  Docker image and cross-platform production deployment remain unvalidated.
- [x] Phase commits/logs and review/student records retained. Scoped gate
  qualifications and unfulfilled full-study requirements are explicit.
- [x] Attacks remain local toy inputs, secrets artificial, no human participants,
  no access-condition acceptance or third-party exploit publication.
- [x] Blockers/limits documented, with feasible substitute execution and honest
  final disclosure.
- [ ] Full external/real-model TSE evaluation, general refinement, all ablations,
  complete policy language and independently demonstrated novelty.
- [ ] Reviewer convergence, remote release, Zenodo DOI, production readiness.

## Release state

This is a local **v0.1.0 pilot**, not the requested completed-research v1.0.
No remote push/release or DOI was made. The original definition of done remains
partly unmet; reasons and the next substantive study are stated above.
Analysis baseline before this generated report: `1187502d00c0a68600d72bf5f330cab20c899d85`. The release tag
identifies the final local commit; raw records identify actual execution commits.
