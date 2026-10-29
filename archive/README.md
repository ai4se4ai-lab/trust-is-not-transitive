# Archived development material

These files are preserved for project history; the active reproduction entry
points are [README.md](../README.md) and [ARTIFACT.md](../ARTIFACT.md).

| Former root path | Current path | Contents |
|---|---|---|
| `reviews/` | [reviews/](reviews/) | Automated critiques, response letters, manuscript snapshots and latexdiff PDFs, including round 6 |
| `student_review/` | [student_review/](student_review/) | Reading logs, assessments and editorial fixes |
| `build/` | `local/build/` (ignored) | Old page renders, a local environment and detached reproduction worktrees |
| `.pytest_cache/` | `local/.pytest_cache/` (ignored) | Disposable pytest cache |
| `.coverage` | `local/.coverage` (ignored) | Local coverage database |

Review and reader records retain their original bytes, including historical
paths and line numbers. Resolve their old `reviews/` and `student_review/`
paths through the table above; other paths remain relative to the repository
root. `scripts/make_review_diff.py` and `scripts/final_report.py` use the new
locations. The latter regenerates the historical report and score table.
Pytest and coverage now write their caches into `archive/local/`.

Local environments and old checkouts are historical convenience copies, not
portable dependencies. Use the root lock files to install a new environment.
Registered Git worktrees were relocated with `git worktree move` so their Git
metadata still resolves. Local material is excluded from Git and Docker builds.

Do not confuse this directory with `results/archive/`, which the full experiment
runner uses to preserve prior raw observations. All inputs needed for the
experiments and manuscript remain in their active locations; the paper source
requires no path changes for this reorganization.

## Reorganization validation (2026-10-29 UTC)

The root `test`, `smoke`, `paper`, `verify-results` and `verify-paper` tasks
passed: 56 tests, 99% reported coverage, replay of 336,000 retained decisions,
and a 20-page paper without unresolved references or overfull boxes. PDF phrase
verification now normalizes extracted whitespace to tolerate line breaks.

The full `python scripts/tasks.py all` pipeline also passed in the ignored
`archive/local/reproduction-validation/` copy, including real PRISM, both
studies and all final verification tasks. A recursive comparison matched
10,538 scientific scalar values in the summaries, excluding measured timing,
environment records and the documented calibration-count availability flag.
The post-review analysis matched byte for byte. All 25 original raw files
were checked against the pre-regeneration snapshot and retained unchanged in
the active artifact. The 43 tracked review/reader records matched their
original content; the uncommitted round-6 records were also moved intact.
The root `paper/main.tex` and bibliography matched the starting snapshot.
