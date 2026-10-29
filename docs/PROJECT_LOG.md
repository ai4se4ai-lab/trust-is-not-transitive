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
