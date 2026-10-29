# Formal artifacts

- FRAMEWORK.md: definitions, explicit assumptions and detailed scoped proofs.
- cascade.pm / cascade.pctl: real PRISM canonical DTMC and reachability queries.
- check.py: independent exhaustive checker, never labeled as a PRISM run.
- sanity.py: seeded probability sanity checks, not a theorem prover.
- toolchain.json: exact PRISM/JRE download/JAR hashes used for recorded runs.

Download official PRISM 4.11 from https://www.prismmodelchecker.org/download.php
or the pinned URL in toolchain.json. The Windows silent NSIS installer was
scoped to .tools/prism. Extract the recorded official Temurin ZIP under
.tools/java after validating its SHA-256. Alternatively set PRISM_HOME to a
separate installation and put Java on PATH. scripts/run_prism.py invokes the
explicit engine directly and retains stdout in results/raw/prism.json.

No Lean/Isabelle mechanization, full Python model, arbitrary shell model or
proved abstraction/refinement relation exists. Finite-state success is not
a proof of deployment safety.
