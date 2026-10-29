# Trust Is Not Transitive (TINT)

Executable conditioned-trust contracts for a local typed agent sandbox,
scoped composition proofs, reproducible experiments and an IEEE-format
manuscript. This is a feasibility artifact; real-LLM/external validation is
unfinished. The frozen primary study found no useful certified policy; a
disclosed numeric correction is evaluated separately on fresh seeds.

```powershell
python -m pip install -r requirements-paper.lock
python scripts/tasks.py smoke
python scripts/tasks.py verify-results
python scripts/tasks.py paper
python scripts/tasks.py verify-paper
```

GNU make users can use equivalent targets. Smoke takes about five to fifteen seconds.
No API key/GPU is required for the local pipeline. [ARTIFACT.md](ARTIFACT.md)
documents full reproduction, PRISM/TeX setup, licensing and limitations.

Read the [manuscript](paper/main.pdf), [formal framework](formal/FRAMEWORK.md),
[preregistration](experiments/PREREGISTRATION.md),
[amendments](experiments/AMENDMENTS.md) and [final report](docs/FINAL_REPORT.md).
The paper is a single [main.tex](paper/main.tex) with one bibliography,
[references.bib](paper/references.bib). Result macros are generated into a marked block at
the top of `main.tex` by `scripts/make_macros.py`; do not hand-edit that block.

The library supplies immutable provenance/action types, a closed JSON DSL,
direct-edge obligation checks, mandatory sink mediation, structured judge views,
calibration and finite-family synthesis. Its lexical scorer and judges are
explicit test doubles. The in-memory sandbox executes no OS shell or network
request and is not a production guard for arbitrary tools.

## Repository layout and reproduction

The active artifact stays at the root: `src/` and `tests/` contain the library
and tests, `experiments/` the frozen protocols and runners, `formal/` the proofs
and model checks, `results/` the retained observations and derived results,
`paper/` the manuscript, `scripts/` the build and verification tools, and
`docs/` the supporting evidence. Keep the dependency locks, `pyproject.toml`,
`Makefile`, Docker recipe, CI configuration, license and citation files here.
The optional ignored `.tools/` directory supplies local PRISM/Java binaries.

Development reviews and student reading records are preserved in
[`archive/`](archive/README.md). Old local build outputs, reproduction checkouts
and test caches are under ignored `archive/local/`; they are not required to
reproduce the artifact. Historical records retain their original path text.
`results/archive/` separately preserves prior raw runs when experiments rerun.

To check the retained results, run the quick start above and
`python scripts/tasks.py test`. To regenerate **both** the historical primary
study and the fresh-seed exploratory study, plus formal checks, analyses and
the paper, install PRISM/Java/TeX as described in [ARTIFACT.md](ARTIFACT.md), then
run `python scripts/tasks.py all`. Existing raw observations are preserved
automatically. Timing and environment fields vary across runs; the guide
explains the comparison limits and the post-review analyses.
