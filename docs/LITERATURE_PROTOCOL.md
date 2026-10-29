# Search and inclusion protocol (2026-10-29 UTC)

This is a reproducible scoping review, not a PRISMA systematic review. Search
window: 2022 onward plus foundational enforcement, shielding and statistics.
Searches used the web search tool with arXiv, ACM DL, IEEE Xplore, DBLP and
Semantic Scholar domain queries. Queries included `guardrail cascade conformal`,
`LLM guardrails assume guarantee contracts`, the named seed systems, and
`contracts system design`, `edit automata`, `runtime verification`, and
`shield synthesis`. DBLP and Semantic Scholar are discovery aids, not the
verification source. No authenticated bulk search of paywalled indexes was done.

Primary arXiv pages are opened with `scripts/collect_literature.py --expand`.
Metadata must include title, authors, date and abstract. URL, retrieval date and
response hash are retained. Snowballing follows direct references from the
closest papers. Read titles and abstracts to remove unrelated identifiers;
read full text of closest work for novelty analysis. `build_literature.py`
builds the CSV and bibliography. `unknown` records missing evidence, not a
negative capability claim. Bibliographic verification does not establish that
an author's empirical or theoretical claims are correct.

Corrections: candidate IDs 2408.16229, 2409.08776, 2406.07690, 2406.07190,
2310.06767 and 1801.02518 are unrelated and excluded. The prompt's 2508.00500
is currently titled ProbGuard, not Pro2Guard. Additional seed systems without
confirmed primary-source details remain unverified; no invented bibliography
entries are used to fill gaps. Exhaustiveness is not claimed.

Evidence HTML is kept locally for audit and is not a redistributable dataset.
The distributed metadata index retains bibliographic facts, verification flags
and response hashes rather than verbatim abstracts. Abstracts are inspected in
the ignored local source evidence; the CSV review notes are our own summaries.
All bibliography entries refer to the opened arXiv version, without inventing
publisher venues. Classical context is additionally grounded in Schneider's
author-hosted paper, Leucker/Schallhart's author-hosted paper and publisher
contract metadata; a wider foundational bibliography remains useful follow-up.
