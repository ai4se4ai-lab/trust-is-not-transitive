# Remaining clarity fixes after student reassessment

This automated manuscript-only reassessment leaves the initial reading/fix files unchanged. New scores and all 28 original high-confusion mappings are in `reassessment.md`. No implementation, artifact records, documentation or earlier review files were consulted.

**No remaining score 2 or 3 was identified.** All items below are score 1: optional precision/reproducibility improvements, not barriers to explaining the central argument. This conclusion is about comprehension, not correctness, novelty or real-agent usefulness.

## Highest-value small edits

1. **State the missing comparator details.** At revised Design/Datasets:L597 and Table III:L606-L622, say rules-only allows after hard pass and explain why invalid delegation incurs more modeled cost than scripted-judge-only despite identical table entries. If invalid delegation computes/relays a score without an early cheap exit, say so explicitly; do not infer that mechanism from this review. The new ablation matrix resolves the decision-comparison confusion but does not fully explain those cost differences.

2. **Make the correction's input features concrete.** At Results/RQIII:L803, replace “listed lexical features” with an actual short feature list or one exact three-feature example, and optionally report the historical stored score. The causal chain now makes sense; the remaining gap is reproducing the string-to-score step from manuscript text.

3. **Name certification infeasibility precisely.** At Results/RQII:L770-L776, replace “no candidate below the frozen risk budget” with “no candidate's simultaneous upper-risk bound met the budget,” if that is the intended observation. True-risk feasibility and confidence-bound feasibility should not be conflated after the careful certificate definition.

4. **Add the coverage candidate grid or a compact range summary.** At Design/Evidence:L665-L674, the generator, denominator and selection/fallback meaning are clear, but the exact `r_j` and candidate-cost list remains outside the manuscript. A compact vector/table would let readers reconstruct the actual 1000-replication experiment without preregistration lookup. This is not needed to interpret the reported confidence statement correctly.

5. **Explicitly name optimization risk events.** At Approach/Synthesis:L447, say that `r_0(x)` and `r_1(x)` are conditional probabilities/expected losses for the same joint unsafe-acceptance event under cheap acceptance or escalation given `x`. The displayed objective and full Lagrangian resolve the earlier score-3 confusion; a tiny numerical two-view example would still make multiplier/tie behavior easier to teach.

6. **Qualify the unrestricted-law fallback.** At Approach/Risk:L434-L442, make clear that “uncertified” means lacking a valid guarantee for the actual unrestricted deployment law. An old iid certificate alone cannot provide that guarantee. The point-concentration argument and hard-versus-semantic distinction are now clear.

## Small terminology and figure improvements

- **Background:L221:** assign `L_2` and `L_3` named roles in the trust tuple, or use “caller” and “judge.” The arrow and `chi` notation are otherwise clear.
- **Background:L233:** replace the contrast between two individual verdicts with a contrast between the judge guarantee's valid and invalid interface conditions, avoiding an implication that a benign action's verdict is literally reused.
- **Approach/Specification:L305:** rewrite “raw judge interfaces that require quarantine” as the intended explicit requirement on structured views; expand DSL on first use if space permits.
- **Approach/Specification:L369:** specify what whole-policy certification is “more conservative” than, or omit that unqualified comparison. Avoid a general ordering claim not explained locally.
- **Figure 1, caption L298, PDF p4:** uncross the cheap-to-effect and judge-to-denial diagonals and separate hard-failure/mismatch labels. All branches are now interpretable; this is layout polish.
- **Family table caption L854:** optionally add “empirical judge targeting is an unauthorized patch, unlike canonical exfiltration `T_j`.” The full explanation at L869 resolves the prior inconsistency, but a float-local note would help readers who inspect the table first.
- **Closest-work table L1038/L1060:** split CaMeL/Fides if their capabilities differ and improve small type if feasible. Adaptive=U and the new operational column criteria are clear and consistent with the evidence.
- **Approach/Risk:L412:** “regularity conditions” is acceptable cited background, but no reader should infer that the short CRC paragraph alone proves the cited theorem. The pilot's distinct binomial guarantee is now explicit.

## Low-priority presentation/reproducibility cleanup

- Name both PRISM reachability properties at Results/RQI:L702, give graph-grid axes/ranges at L709 and identify the core coverage metric at L720. This improves reproducibility without changing the finite-check limitations.
- Introduce full-expressiveness as a criterion before Table IV's hypothesis row, or frame it explicitly as an inventory question; explain the counterexample's relevance to both RQ I and II rather than alternating assignments without comment.
- Move “PDF glyph”/“notation registry” lint caveats from scientific conclusion validity at L931 into artifact-production discussion, or define why they matter to the claims. They are workflow terms rather than reader-facing statistical limitations.
- Replace the unexplained TSE effectiveness phrase at Discussion:L1089 with the actual scientific claim the present evidence does not support.
- Replace “No remote publication” at Availability:L1106 with the intended narrower statement, such as no archival release/DOI, if accurate. The adjacent repository URL otherwise makes the phrase ambiguous.

## What now works and should be preserved

The canonical exfiltration versus empirical patch distinction, route-theory/whole-policy distinction at first use, revocation-epoch/oracle/denominator definitions, separate coverage-law/fallback description, exact binomial formula with actual example, full optimization objective/Lagrangian, explicit parity states and joint-risk bridge, scorer versions, comparator matrix, family masses, effect-size orientation, and common-scale utility-labeled trade-off plots all improve comprehension. The paper continues to make its negative primary utility result, exploratory status, shift failure and absence of real-agent effectiveness evidence visible. Further polish should preserve these concrete explanations rather than replacing them with additional general caveats.
