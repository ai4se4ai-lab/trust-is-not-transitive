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

GNU make users can use equivalent targets. Smoke takes about five seconds.
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
