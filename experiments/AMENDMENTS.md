# Dated amendments (original preregistration and results remain immutable)

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
