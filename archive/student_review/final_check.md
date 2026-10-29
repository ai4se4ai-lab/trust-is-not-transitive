# Final brief student-reader clarity check

Automated development-reader check of only the final small manuscript edits and immediate context, using current `paper/main.tex` and `paper/main.pdf`. No external artifact/code/docs/results/review files were opened. Initial reading logs, fix list and reassessment remain unchanged. The PDF remains 12 pages; revised wording was checked against extracted PDF text, with visual inspection of the score/infeasibility material on PDF p7. This is a comprehension check, not independent validation of implementation or results.

Scores: 0 clear; 1 minor friction; 2 unclear; 3 lost.

| Edited item | Current source location | Score | Reading outcome |
|---|---|---:|---|
| Guarantee reuse under changed input | Background:L233 | 0 | The object being improperly reused is now a guarantee, rather than an individual benign verdict; a structured-view premise cannot justify raw `T_j`. |
| Raw judge view and DSL | Approach/Specification:L305 | 0 | DSL is expanded and rejection now clearly applies when a raw view violates the contract's quarantine requirement. |
| Whole-policy versus route reasoning | Approach/Specification:L369 | 0 | Whole-policy certification avoids the described selection-accounting problem; the unqualified claim that it is generally more conservative has been removed. |
| Conditional risk events in optimization | Approach/Synthesis:L447 | 0 | Both alternatives refer to the same joint unsafe-acceptance loss conditional on the trusted view, making their difference meaningful in the objective. |
| Rules-only acceptance and delegation charge | Design/Datasets:L599 | 0 | Rules-only allows after the hard sink passes; invalid delegation's extra scorer cost is a protocol charge despite equal verdicts, so I no longer infer extra detector effectiveness or actual profiling from that cost difference. |
| Upper-bound infeasibility | Results/RQII:L774 | 1 | It now explicitly means no candidate's simultaneous upper bound meets the budget, resolving true-risk versus certification feasibility. Minor new wording issue: “It denies routes” has no clear singular antecedent; write “The runtime denies uncertified routes.” |
| Eight lexical matches and threshold correction | Results/RQIII:L807 | 1 | I can now name the eight strings and compute the intended score from distinct matches after case-folding; the three-match boundary mechanism remains clear. Minor precision issue: “matches” does not explicitly say substring versus token matching, so `send` within a longer word remains unspecified from this wording alone. This does not obscure the reported correction's causal chain. |
| Archival status | Availability:L1106/L1111 | 0 | No archival release/DOI is a clear narrower statement than the former ambiguous “no remote publication.” Repository availability and local preserved instrument status are understandable together; no repository contents were verified. |

The eight strings are `ignore`, `override`, `secret`, `.env`, `reviewer`, `instruction`, `send` and `upload`. “Distinct” makes clear that repeated instances of a single listed match do not automatically count as several features. Stating “distinct substring matches” would close the only remaining matching-granularity ambiguity if that is the intended mechanism.

The revised score paragraph is legible in the PDF, with no apparent clipping or overlap. The newly clarified bound-based infeasibility sentence appears in the expected RQ II context. No new score-2 or score-3 issue was identified.

## Does the prior comprehension recall remain correct?

Yes, with two refinements: primary infeasibility is specifically failure of the simultaneous upper-risk bounds to meet the budget, and the invalid-delegation modeled-cost increment is a nominal protocol charge rather than evidence of distinct inference behavior. I can now also state the scorer's actual feature strings, which the earlier recall explicitly could not name.

The central recall remains unchanged: valid reliance needs actual premises; canonical `T_j` is sink-blocked exfiltration while empirical judge targeting is a semantic-only unauthorized patch; theoretical route sums and implemented whole-policy certification are distinct; calibration confidence does not validate distribution stability; the primary calibrated fallback has zero utility; corrected exploratory decisions reduce the authored-mixture risk but do not show real-agent effectiveness; the designed shift and lack of adaptive evidence retain their stated limits. The explicit conditional-event definition strengthens rather than changes my reconstruction of the optimization objective. No new empirical inference is warranted by these wording edits.
