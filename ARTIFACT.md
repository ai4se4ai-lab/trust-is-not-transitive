# Artifact guide and scope

Round-1 corrections: verify-results now also performs read-only semantic replay
of all retained decisions against traces/historical configurations, checks LP
weights/risk/cost/simplex constraints, and enumerates the finite LP's vertices
independently. Historical adaptive records labeled checked_quarantine query
an uncertified fixed-threshold decision core, not GuardRuntime or its selected
certificate; original logs remain unchanged. Their first fixed phrase succeeds,
so no observed response-informed adaptation occurred. Current lexical-v3-bounded
caps input size; historical v1/v2 remain frozen for reproduction. Arbitrary
synchronous plugins still have no enforced cancellation deadline. See docs/ERRATA.md.

This is a local feasibility artifact and an IEEE-formatted scoped manuscript,
not a completed real-LLM/TSE effectiveness evaluation. The frozen primary study
found no useful certified policy. Original logs are retained alongside a
separately labeled fresh-seed exploratory numeric correction.

## Setup and offline checks

Recorded host: Windows 11, Python 3.13.14, 22 logical CPUs; RTX 2050 with 4096 MiB
VRAM but CPU-only PyTorch. No paid API call, real model inference, external
benchmark execution, human study, host-shell action or network tool effect
occurred. Modeled cost units are not money, tokens, milliseconds or GPU time.

```sh
python -m pip install -r requirements-paper.lock
python scripts/tasks.py smoke
python scripts/tasks.py test
python scripts/tasks.py verify-results
python scripts/tasks.py paper
python scripts/tasks.py verify-paper
```

Make targets are equivalent when GNU make is available (absent on the recorded
Windows host). Scripts add src to Python paths; installing the project itself
is unnecessary. For an editable installation, use setuptools 80.9.0 and
`pip install --no-build-isolation --no-deps -e .`.

Smoke takes about five seconds; allow a minute for analysis plus semantic replay;
paper generation/build normally under a minute on this host. TeX requires
pdflatex/bibtex (MiKTeX or TeX Live) and ordinary IEEEtran packages. Vendored
IEEEtran.cls and IEEEtran.bst retain upstream licenses and have hashes in
paper/template_provenance.json. Template originals are unchanged. The manuscript
is twelve pages including references, within the conservative twelve-page IEEE
CS regular-paper budget; authors must verify current journal-specific rules
before any submission.

`verify-results` re-derives summary bytes from raw observations, recomputes
binomial family bounds, checks selection independently and verifies the hash
manifest. `paper` regenerates the empirical macro block inside `paper/main.tex` before
TeX; all figures are TikZ/pgfplots in `main.tex` and plot only those macros.
`verify-paper` checks empirical source-number provenance, bibliography evidence,
notation registry, cross-references and PDF layout properties. It does not
prove glyph-level origin of every PDF numeral. Mathematical constants have
written-proof provenance, bibliography metadata have opened-source provenance,
and page/theorem/citation numbers are structural TeX output. Registry lint is
not a semantic proof checker. Visual page inspection is also performed.

## Formal checks and full regeneration

`python formal/check.py` runs an independent exhaustive finite-state checker;
`python formal/sanity.py` runs seeded probability sanity checks. Detailed proofs
are in formal/FRAMEWORK.md. No Lean/Isabelle mechanization or Python refinement
proof is claimed.

`python scripts/run_prism.py` invokes real PRISM, compares both reachability
properties in all canonical configurations and preserves stdout. Configure
PRISM_HOME and Java on PATH or use the local ignored .tools layout. Recorded
PRISM 4.11 and Temurin 21.0.9+10 hashes/downloads are in formal/toolchain.json;
see formal/README.md. Binaries are not redistributed. Retained real PRISM logs
can be inspected offline without installing it.

`python scripts/tasks.py all` / `make all` archives existing raw observations
inside results/archive and regenerates the historical-primary and exploratory
studies, executable formal checks, summaries, figures and PDF. It needs PRISM,
Java and TeX. The primary compatibility instrument intentionally preserves its
arithmetic defect; current library/smoke use the corrected scorer. Rerunning is
a reproduction operation, not a repeated held-out test for tuning. Allow a few
minutes of CPU time after dependencies/tools are installed; no API/GPU needed.

Timing and environment identifiers change across hosts/runs. The original
synthesis raw log omitted calibration counts; the repaired instrument includes
them on regeneration, so that provenance-availability flag improves. Original
logs remain archived; re-analysis of preserved observations is byte-reproducible.

## Provenance and limitations

- prereg-v1: local protocol freeze, not an external timestamped registry.
- experiments/PREREGISTRATION.md and AMENDMENTS.md: fixed design and dated changes.
- results/raw: compressed per-decision/trace JSONL, sufficient counts and raw checks.
- results/raw/exploratory_numeric: separate fresh-seed numeric-correction replication.
- results/processed/summary.json: deterministic raw-derived metrics and hypothesis outcomes.
- results/manifest.json: source/config/raw/processed hashes; each environment record identifies its execution commit.
- paper/generated/macro_provenance.json: source hash and JSON pointer per empirical macro.
- experiments/DATASHEET.md: authored-label and template-reuse limitations.
- docs/BASELINE_FIDELITY.md: actual toy comparators and unexecuted named systems.

No real base LLM, pretrained guard/probe, official SOTA baseline, external
benchmark, real task success, practitioner study, full policy language, real
inference-load test or temporal deployment audit is available. No statistical
adaptive/shift robustness guarantee is made. Quarantine can remove useful
semantics; matching context strings cannot detect a new distribution. The
synchronous sandbox trusts host/version/provenance/approval stores; it does
not claim concurrency safety or protection for an actual OS shell.

Generated fixture data are CC0-1.0; code MIT. IEEEtran, PRISM, Java, source papers
and external datasets retain their licenses. Literature evidence HTML is
local-only/ignored; verification metadata/hashes are distributed. A code-license
audit does not authorize redistribution of every upstream dataset. R-Judge
repository-license retrieval failed; its project website states CC BY-NC-SA.
AgentHarm has an additional safety-use restriction. No external data are bundled.

Docker recipe is unvalidated because the engine was unavailable. No remote
push, publication, archival DOI or release was created. Automated reviews are
development critiques, not peer-review endorsements. See docs/FINAL_REPORT.md
for residual concerns and unfinished master-prompt requirements.
