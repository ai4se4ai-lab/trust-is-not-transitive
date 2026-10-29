# Dated amendments (original preregistration and results remain immutable)

## 2026-10-29 — A3: post-review descriptive analyses (manuscript rewrite)

After the round-6 automated reviews of the rewritten manuscript, add two
**descriptive, post hoc** analyses of the preserved raw traces, computed by
`scripts/post_review_analysis.py` into `results/processed/post_review.json`.
No trace is sampled, no decision of either study is replaced, and nothing
here is confirmatory.

1. *Provenance-only control.* A reviewer observed that every unsafe family
   that passes the deterministic gate proposes a patch from the untrusted
   `issue` input, while the only benign issue-derived family (benign security
   text) is blocked by every scorer-based pipeline anyway.
   We therefore evaluate "deterministic gate, then block any action with an
   untrusted input" on the logged test and shift traces of both studies.
   It was not preregistered; it exposes a property of the authored fixture law
   (no benign issue-derived action is accepted by the judge), not an effect of
   the method. (Corrected after round-2 review: an earlier wording said that no
   benign issue-derived action exists, which is false.)
2. *Calibration-path equivalence.* Calibration losses were computed with the
   decision core `tint.baselines.decide('checked_quarantine', ...)`, while
   held-out decisions came from `GuardRuntime`. Replay the exploratory
   calibration split through both at each seed's selected threshold and
   count disagreements.

Also disclosed in the manuscript: `experiments/dataset.py` and
`experiments/run.py` were first committed (c47f2a4, 07:58:06 -0700) after the
`prereg-v1` tag (a48fca6, 07:56:30 -0700), so the fixture templates were not
frozen by the tag. The H6 decision rule is satisfied trivially by a block-all
policy; the recorded "inconclusive" verdict is a deviation from the literal
rule, explained in the paper. The checker-scaling statement is corrected from
"linear" to the measured super-linear growth (per-edge set intersection);
the checker study is not rerun.

## 2026-10-29 — A2: post-review analyses and attribution correction

After round-1 automated review, add **exploratory descriptive** family-level
acceptance and exact fixture-law risk/utility/cost calculations from existing
raw logs. Explain that uncertainty reflects mixture sampling, not independent
semantic tasks. Add accepted-action conditional risk. Strengthen validation
with read-only semantic replay and independent finite LP vertex checks. These
are not new held-out experiments; no trace or outcome is replaced.

Correct the historical search target: the raw policy label checked_quarantine
refers to an uncertified fixed-threshold decision core, not calibrated runtime.
Add explicit processed scope metadata and correct prose. Retain original
records. First-candidate success means no observed response-informed adaptation.
Current runtime confidence/input/topology checks are separately hardened;
historical v1/v2 scorer identities remain frozen for reproduction. None of
these changes supplies missing real-model or external effectiveness evidence.

## 2026-10-29 — A1: numerical boundary correction; exploratory replication

Observed after the initial frozen run: every selected family was infeasible
under epsilon 0.20; the runtime correctly blocked uncertified acceptance.
Investigating raw counts exposed a numerical defect in the handwritten scorer:
`0.04 + 0.12*3` evaluates below the representable `0.40` comparison threshold.
Thus cases authored with three lexical features incorrectly pass the scripted
judge. Correct the score computation to integer hundredths divided once by 100;
do not change any lexical feature, threshold, cost, budget or judge rule.
Add a regression test at the exact boundary. Version the scorer as lexical-v2
so old certificates cannot apply. Preserve the original files in `results/raw/`.

Run **exploratory**, not confirmatory, replication on fresh seeds 10 through 19,
with the same split sizes, mixture, thresholds, alpha/delta and analysis. Save
under `results/raw/exploratory_numeric/`. Do not pool it with the original run or
present it as preregistered success. The effect of this defect is an internal
validity limitation. A successful replication remains synthetic evidence, not
generalization to real LLMs. This amendment is committed before that run.

Instrument additions: retain calibration counts in synthesis raw records so
the processed bounds can be independently recomputed; fixed checker mutation
outcomes and sufficient statistics remain unchanged. For the original run,
stored synthesis bounds remain raw observations; the comparison to exhaustive
selection can be checked but their calibration cannot be independently
reconstructed without these counts. State this provenance limitation.
