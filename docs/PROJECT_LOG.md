# Project log

## 2026-10-29 — audit (before Phase 1)

Repository HEAD was `329ee30` (initial commit). README and untracked user-supplied
`docs/TSE-PROMPT.md` plus three IEEE template files were present. There was no
implementation, data, formal model, paper, CI, dependency lock, or experiment.
No applicable AGENTS.md was found in the workspace or checked ancestors.
Python 3.13, Git, MiKTeX pdflatex/latexmk, NumPy, SciPy, pytest, coverage,
BeautifulSoup, matplotlib and PyMuPDF are installed. GNU make is absent.
The supplied template uses `IEEEtran` with `lettersize,journal`; IEEEtran.cls
and IEEEtran.bst are installed. Original template files will remain unchanged.

## Phase 1 — in progress

Primary-source searches immediately found close work: ContrAgent (2609.18128),
probabilistic three-layer assume-guarantee architecture (2605.18672), Conformal
Arbitrage (2506.00911), Trust or Escalate (2407.18370), and AgentSpec (2503.18666).
The prompt's blanket claim that nobody gives cascade guarantees is false.
Novelty must be narrowed to executable discharge of provenance/interface and
routing obligations with separately certified route risk, rather than contracts,
non-transitivity, calibrated cascades, or IFC themselves.

### Phase 1 gate — passed with review-scope qualification

67 relevant arXiv primary-source records were opened and bibliographically
verified; unrelated seed IDs were removed. CSV, verification hashes,
eight-family gap analysis and a narrowed novelty paragraph are present.
Closest five full texts were opened; other records are abstract-level screens,
explicitly marked. Search is a scoping review, not an exhaustive systematic
review; unknown capability cells are not negative claims. This limitation is
carried into the eventual paper. Original template files are unchanged.

Phase 2 starts after this gate. Java is absent, Docker daemon is unavailable,
and only Docker's WSL distribution exists. Checking whether official PRISM can
be provisioned locally; otherwise record the independent finite-state checker
as a scoped substitute, never as a PRISM/Storm run.

### Phase 2 gate — passed (scoped theory)

Definitions D1–D9 and detailed proofs T0–T4 are in `formal/FRAMEWORK.md`.
Corrected unsafe-conditional independence, routing selection, per-decision
versus session risk, pairwise versus higher-order dependence, and threshold
optimality assumptions. No new mathematical novelty claimed. Registry lint
passes but is explicitly not a semantic notation proof. Independent exhaustive
checking passes; 10,000 seeded random-law sanity checks pass.
Official PRISM 4.11 was provisioned into ignored `.tools/`; real explicit-engine
runs of all six trace/configuration cases match the independent checker on
both properties. Exact installer/JAR/model hashes and Java release provenance
are retained. Adoptium's API returned 403; a pinned official GitHub release
worked. Lean/Isabelle mechanization omitted in favor of the allowed detailed
proof alternative. The PRISM abstraction does not verify the Python runtime.

### Phase 3 gate — passed for the explicitly lightweight substitute

Typed model/taint, closed JSON contract DSL, direct-edge assumption checker,
lexical classifier, raw/structured scripted judge, approval stub, calibration,
finite-family synthesis, tool-call argument adapter and in-memory DevAgent
are implemented. Core coverage measured 99% with 51 passing tests. Smoke
completed in 4.62 seconds. T*, Tb, Tj behave as required; stronger naive-with-sink
control also blocks Tj and is retained. Certificate configuration drift,
agent-forged approval/labels/environment and taint erasure have regression tests.
GitHub Actions workflow written, not remotely executed.

Scope deviations: no real shell interpreter, pretrained guard, activation
probe or human experiment. No named SOTA baseline is falsely reimplemented by
a regex; fidelity notes identify every surrogate. Synthesis is exact within a
finite family, with no unrestricted n-layer approximation claim. Test fixtures
contain synthetic certificates solely to exercise plumbing and are not used as
calibrated empirical evidence. These substitutions follow the prompt's
feasibility/future-work provisions but do not satisfy a full real-LLM study.

### Phase 4 gate — frozen

Protocol and config committed as `a48fca6`, tagged `prereg-v1`, before empirical
calibration/dev/test execution. Ten seeds, fixed sample sizes/thresholds,
1000 repeated calibration splits, paired statistics, strong controls and
stopping rules specified. Eight hypotheses include an explicitly unavailable
real-model/external-validation hypothesis. Benchmark code license audit stored;
data terms are not inferred from code terms. No participant study fabricated.
GPU is present but installed torch is CPU-only; no API credentials established.
Phase 5 execution begins only after this frozen protocol.

### Phase 5 initial run and A1 amendment

Original run completed without infrastructure failure. All candidate families
were infeasible at the frozen budget; fail-closed runtime therefore denied all
uncertified benign actions too. This is a negative utility outcome, retained.
Post-run inspection discovered floating-point boundary arithmetic in lexical-v1.
A1 documents a numeric-only correction (integer hundredths), fresh seeds 10–19
and separate exploratory output. No primary thresholds/budgets are retuned and
original held-out results are not overwritten. Synthesis sufficient-count
logging is strengthened; original count omission is disclosed.
