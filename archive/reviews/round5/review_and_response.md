# Round 5: critical TSE-style review and response

Reviewer stance: TSE referee, with a PhD student in software engineering as
the intended reader. The pre-revision manuscript is preserved in
`before_main.tex.txt`.

## Major concerns

**M1. The contribution is hard to find.** The introduction spent more space on
what was *not* claimed than on what was. It had no contribution list, no
statement of the key insight, and no challenges list, all of which
`docs/TSE-PROMPT.md` asks for.
*Change:* The introduction was rewritten as motivation, then the running
example, then the gap ("formal but flat" versus "hierarchical but empirical"),
then challenges C1–C3, the key insight, four contributions mapped to the RQs,
the RQs quoted verbatim from the prompt, a short preview of the answers, and a
roadmap.

**M2. Elementary results were called theorems, starting from "Theorem 0".**
*Change:* They are now Propositions 1–5. The text calls them standard
arguments that make premises explicit, and the artifact section maps them to
`T0`–`T4` in `formal/FRAMEWORK.md`.

**M3. The agent-trace statistics are deterministic, and the paper never said
so.** Each comparator is a pure function of a trace's family. Every population
number therefore follows from the family masses, and every non-tied Holm p
equals the smallest value attainable with ten seeds.
*Change:* There is a new caution paragraph in the evaluation design. A new
Table VIII traces each family through the pipeline (string matches k, score s,
sink result, TINT outcome). A "Where the numbers come from" paragraph derives
the 66.67% utility ceiling (benign security text always denied) and the 10%
risk floor (implicit patches always accepted).

**M4. The primary infeasibility was never explained.** *Analysis (new code):*
`scripts/process_results.py` now records `grid_structure`. In the primary
run, all 11 thresholds give identical calibration losses (1 risk level and 4
distinct policies). The smallest upper bound across all seeds is 31.1%,
against a 20% budget. No threshold could have succeeded, so the failure lies
in the detector, not in calibration. This is cited in the paper through the
new macros `\resPrimaryDistinctPolicies`, `\resPrimaryDistinctRiskLevels`,
`\resPrimaryMinBound` and their exploratory counterparts. The rest of
`summary.json` is byte-identical.

**M5. The RQs were never answered explicitly.** *Change:* Each results
subsection now ends with a bold "Answer to RQ …" paragraph.

**M6. The CPU overhead of the calibrated runtime (about 20×) was unexplained.**
*Analysis:* A microbenchmark shows that recomputing the fingerprint costs
about 78 µs per call, which accounts for most of the gap. *Change:* The paper
explains this and states the trade-off of caching the fingerprint.

**M7. The prose was hard to read.** Terms were used before being defined
("sink", "quarantine", "acceptance route", "fingerprint"), hedges were stacked
on top of each other, and some phrases read as machine-written ("not accepted
on the user's behalf", "post-review re-analysis").
*Change:* Every term is now defined where it first appears and illustrated
with T*, T_b or T_j. Intuition comes before each formal statement. A
joint-risk versus miss-rate example was added. The lessons for engineers were
moved into the Discussion, and the ethics text was rewritten.

## Concerns acknowledged but not resolvable without new research

Novelty against ContrAgent and the layered probabilistic architecture. No real
LLMs, guards or benchmarks. No adaptive attacker. No proved refinement link.
All of these are stated in the Limitations section and in the "What a
convincing evaluation needs" paragraph.

## Verification

`tasks.py verify-results` and `tasks.py verify-paper` pass, as do all 56
tests. The build has no overfull boxes. The 12-page assertion was removed at
the author's request; the PDF is now 14 pages.
