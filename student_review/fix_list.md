# Prioritized clarity fixes from the initial student reading

Automated development-reader feedback, not a human study, correctness audit, literature validation or effectiveness evaluation. Restricted inputs: the manuscript PDF/source and generated macro expansion only. No implementation, artifact documentation/results, previous reviews or project logs were read. Manuscript unchanged. Scores and source starts refer to the initial reading recorded in `reading_log.md`; the recommendations do not infer author intent where the manuscript is ambiguous.

## P0: Resolve the apparent canonical/empirical judge-targeting conflict

**Locators:** Background:L58/L133/L252; Results/RQIII:L767/L781/L811. **Highest associated confusion: 2.**

The canonical `T_j` adds a reviewer instruction to a secret-exfiltration action, and Table I says naive-with-sink denies it. Table VI says naive-with-sink accepts 100% of the judge-targeting family. I cannot tell whether these are different actions, a differently defined family, different comparator behavior, or an inconsistency. This blocks causal interpretation of the empirical benefit and may make an attentive reader conclude that the tables disagree.

**Concrete edit:** state the action and violated property for the canonical trace and each empirical attack family, especially judge targeting and implicit patching; explicitly say whether family members differ from `T_j`. Give one example of a semantic-only unsafe action that passes the hard sink if that is what the empirical family contains. Distinguish the encoded shift family's all-attack denominator from the original mixture's joint-risk denominator. Do not silently rename/reinterpret the canonical trace to make the tables appear consistent.

**Reassessment check:** a reader should explain why each of the canonical and empirical judge-targeting cases is allowed/denied by naive-with-sink without guessing an action.

## P1: Explain the arithmetic correction through actual routing behavior

**Locators:** Abstract:L21; Results/RQIII:L731, with Design/Datasets:L550/L558 and Results/RQII:L698. **Highest confusion: 2.**

A change around `0.04+0.12*3 = 0.40` apparently changes all ten families from infeasible to a useful certified configuration, but the score function, branch comparison, relevant family and selected threshold never appear. I understand floating-point boundary errors; I cannot explain why this error has this safety effect in this system.

**Concrete edit:** show the score components and branch condition, actual historical floating value, corrected value, and the resulting old/new route and verdict for one concrete action. Explain which family contributes the changed unsafe mass and why the upper bound then crosses the risk budget. State the exploratory threshold/version/seed count and retain the separation from frozen primary evidence. If only bounds rather than true risk made the primary family infeasible, say that explicitly.

**Reassessment check:** the reader can narrate the causal chain from the numerical defect to judge exposure, risk, certification and utility without artifact lookup.

## P1: Give one complete policy example and distinguish route theory from whole-policy implementation

**Locators:** Introduction:L86; Background:L191/L208/L242; Approach:L272; Approach/Specification:L279/L316/L336; Approach/Implementation:L508; Design/Datasets:L550/L558. **Highest confusion: 2.**

“Route-certificate discipline” implies separately estimated route certificates, but the pilot certifies the complete policy; the clarification comes only after Theorem 1. The linear pipeline figure does not show early acceptance, escalation, or denial exits. Neither the configured cheap-route rule nor direct-edge evidence is instantiated. The all-effects-must-be-certified prose also sounds as though it applies to explicitly uncalibrated comparators.

**Concrete edit:** define “acceptance route” and “whole-policy certificate” together at first use; label route-specific estimation as theoretical only there. Show a small configuration with hard sink, cheap threshold, structured-judge fallback, final denial, applicable certificate and explicit edge condition. Add cheap/judge branches and early denials to Figure 1. Qualify certification-required state semantics as applying to the calibrated checked runtime. Use distinct notation for a contract `C_i`, trust condition and monetary/modeled cost if possible.

**Reassessment check:** the reader draws the implemented policy correctly and identifies which checks apply to each comparator.

## P1: Make the implemented certificate reconstructable and separate the experiments

**Locators:** Approach/Specification:L316/L324/L336; Approach/Risk:L385; Design/Evidence:L596; Results/RQII:L657/L683/L698. **Highest confusion: 2.**

I know the intended guarantee is high-confidence population joint risk after policy selection, but cannot reconstruct the actual bound from counts or tell exactly how the coverage experiment relates to the seven-family replay. “Its target” in the 998-replication statement is ambiguous, and coverage fallback/selection denominators are unspecified. Original synthesis-count omissions and later re-analysis are important but are mixed with several other checks in one paragraph.

**Concrete edit:** introduce number of unsafe accepted calibration decisions `k`, sample size `n`, candidate count `K`, total failure budget `delta`, and one-sided binomial upper bound at allocated `delta/K` (or the actual allocation). Supply one small count-to-bound-to-selection example. State whether the coverage law is a separate synthetic nested-loss generator, its candidate risks/selection rule, and how no-feasible-candidate replications are counted. Distinguish certificate coverage `true R <= selected bound` from test frequency `<= risk budget` or `<= bound`, whichever is measured. Separate selection consistency, recalibration reproducibility, LP verification and trace replay, with their run/version attribution.

**Reassessment check:** the reader can state the two probability spaces, reproduce the intended certificate inputs, and distinguish conservative certification failure from true-risk infeasibility.

## P1: Rewrite the optimization theorem around an explicit objective

**Locators:** Approach/Synthesis:L403 (**score 3**), L415/L433 (**score 2**).

The threshold intuition is memorable, but the theorem has a syntactically awkward “if” clause, an undefined `R(q)` and no displayed primal optimization problem. The proof suppresses the baseline terms needed to see why the Lagrangian has that form. Familiarity with basic formal methods does not imply working knowledge of complementary slackness or weak duality.

**Concrete edit:** first define the expectation law of `x`, `R(q) = E[(1-q)r_0 + q r_1]`, baseline-plus-incremental expected cost, and the constrained problem (using the actual intended definitions). State sufficient premises in a complete conditional sentence. Briefly explain the multiplier as the price of risk reduction, retaining the finite-multiplier existence limitation. Give two views/policies with concrete risk/cost values, including a nonbeneficial escalation and a tie/mixture. Separate ideal known-risk theory, implemented finite-grid selection, supported LP mixtures and hypothetical latency certification; explain why the two-policy support fact applies under its precise constraints.

**Reassessment check:** the reader can derive the sign of the escalation inequality and state exactly which optimization problem the pilot solves.

## P1: Make the conformal detour optional and translate its guarantee

**Locators:** Approach/Risk:L376 (**score 3**), L385; Related/Statistics:L920.

The CRC formula introduces `Z_k`, `n`, `alpha`, nested loss, parameter orientation, fallback and marginal expected risk in one paragraph. I cannot reconstruct the guarantee and briefly lose track of what TINT uses. The phrase “three facilities” does not enumerate the facilities.

**Concrete edit:** lead with “The pilot uses finite-family binomial certification.” Then either shorten CRC to a plain-language contrast or define each symbol and place a small guarantee comparison nearby: marginal predictive coverage, expected-loss control averaged over calibration randomness, and high-confidence population-risk bound for a selected fixed policy. Explicitly say which are utilities/background and which produce reported certificates. No need to reproduce a CRC proof if it is not part of the contribution.

**Reassessment check:** the reader can say what the pilot's 95% confidence means and why that is different from CRC expected-risk control.

## P1: Instantiate the conditional contracts in the nontransitivity proof

**Locators:** Background:L199/L208/L215; Approach/Specification:L295 (**score 2**), L309.

The existential result is clear, but the proof verbally assigns assumptions to an intermediate layer, outer layer and caller without writing their guarantees. “Both conditional relay contracts are satisfied” is difficult to verify. The strong naive sink control correctly prevents attributing ordinary hard mediation to a special trust mechanism.

**Concrete edit:** give each layer a name and one-row `(assumption, guarantee, actual view)` contract. State which premise is false for the failing execution and which valid implications remain satisfied. Include one fully instantiated `Trust(i,j,P,C)` tuple and clarify edge direction. Avoid presenting a valid benign verdict as if that individual verdict were reused on a malicious trace; identify guarantee/certificate reuse instead.

**Reassessment check:** the reader can independently check each local implication and identify the exact missing global obligation.

## P2: Clarify data/control provenance and safety notation

**Locators:** Background:L124/L133/L141/L149/L155/L163/L170/L178/L191. **Highest confusion: 2.**

“Their joins” is ambiguous, and I cannot tell which dependencies taint which data: the benign issue remains untrusted but its diagnostics are public. Safety is written as a conjunction of a trace invariant and a distribution-level requirement without defining `phi_sem` directly. Epoch, sink, quarantine, oracle, `G`, `D` and risk budget arrive before plain-language explanations.

**Concrete edit:** show issue, payload and action labels separately for `T_b` and `T_j`, distinguishing control from data dependence and stating what the monitor tracks. Gloss `G` as always, define `phi_sem`, name the sample space and the `epsilon` budget, and explain action epoch with one stale-approval example. Define sink as the mandatory effect-boundary checks and quarantine as the closed structured-view transformation. Explain whether the approval fallback runs, abstains or is merely a supported interface. Tie operational System I/II to actual resource declarations or remove unnecessary terminology.

**Reassessment check:** the reader assigns labels and approval validity to the benign and malicious actions and explains hard versus statistical safety without mixing semantic labels with detection.

## P2: Define the common-shock model before using it and finish the joint-probability bridge

**Locators:** Background:L230; Approach/Risk:L345/L359/L369; Approach/Synthesis:L445/L450; Results/RQII:L669/L675. **Highest confusion: 2.**

The theorem refers to “the specified” mixture before it is specified; later the tightness proof constructs conditional `min m_i` while claiming the joint `min beta_i` bound. I can fill in the prevalence step but should not have to. The dependence figure lacks the parameter values that set its vertical scale.

**Concrete edit:** define the mixture generator first: conditional unsafe input, branch probability, Uniform(0,1) variables, preserved conditional marginals and resulting prevalence multiplication. Give a short numerical example demonstrating why products of joint marginals are wrong. In the tightness proof explicitly attain the theorem's joint bound, identifying what marginal information/prevalence is held fixed. Enumerate the four even/odd parity triples or supply a tiny table. Put `pi`, miss rates, simulation repetitions and point meaning in the dependence caption or adjacent text.

**Reassessment check:** the reader computes both the conditional and joint miss risk and understands that mixture weight is not measured correlation.

## P2: Narrow or justify the unrestricted-adversary fallback claim

**Locators:** Approach/Risk:L393 (**score 2**); Results/RQIII:L811; Related/Attacks:L957.

The total-variation transfer inequality is understandable, but `Q`/TV are not introduced, and “only universal fallback” sounds like a general impossibility result. Hard mediation covers hard predicates, not every semantic unsafe label. Table VII's Adaptive=P can look like successful adaptive testing despite the explicit first-query uncertified-core limitation.

**Concrete edit:** name `Q` as the deployment law and explain TV as the largest probability change over events. State precisely which loss events exact mediation excludes and which semantic events require denial for a distribution-free guarantee; give a brief adversarial point-mass argument or scope the prose to the defined model. Relabel the table cell/column to reflect core-only attack-search capability rather than demonstrated adaptive robustness, and state that no response-informed adaptation was observed.

**Reassessment check:** the reader distinguishes a coverage theorem, a distribution-shift assumption, an available attack-search hook and an empirical robustness result.

## P2: Supply an ablation matrix and fixture-law summary

**Locators:** Design/Datasets:L540/L550/L558; Design/Evidence:L613; Results/RQIII:L767/L781. **Highest confusion: 2.**

Comparator names do not reveal hard checks, view type, score threshold, certificate use or route rule. The family probabilities needed to derive analytic 10%/20% population risks are missing. “Two proposal sources,” adaptive core search and complete runtime replay can be mentally conflated.

**Concrete edit:** add a matrix for each comparator with mandatory sink, scorer, raw/structured judge, cheap acceptance threshold and certificate enforcement. State authored family masses and one representative semantic action each. Provide a compact evidence map separating fixture replay, coverage-law replications, finite synthesis/LP tests, model checks and uncertified core search. Include version/run and sampling unit in that map.

**Reassessment check:** the reader predicts family-level comparator decisions and derives the population risk/utility from the declared mixture.

## P2: Report metric denominators, aggregation and effect-size direction explicitly

**Locators:** Background:L155/L222; Design/Evidence:L603; Results/RQII:L657; Results/RQIII:L708/L754/L781/L811; Results/Threats:L836. **Highest confusion: 2.**

The paper repeatedly distinguishes three risk concepts verbally, but no adjacent formula set fixes them for a new reader. Utility's benign denominator and timing aggregation are not explicit. `A_12=1` next to a negative risk difference is uninterpretable without outcome ordering.

**Concrete edit:** define joint risk `P(Y=1,allow)`, attack miss `P(allow|Y=1)`, accepted conditional risk `P(Y=1|allow)` and benign utility `P(allow|Y=0)` together. Say how CPU p95 and costs are pooled/averaged across seeds, and identify hard-count totals. Define which method/outcome direction makes `A_12=1` favorable. State what confidence the displayed exact coverage interval uses if not already implied. Name the two PRISM reachability properties, graph-grid axes/ranges and code coverage metric.

**Reassessment check:** the reader can explain 10.16%, 25.40%, 66.46% and 100% without changing denominator silently.

## P2: Improve figures and table criteria without adding more caveats

**Locators:** Approach:L272; Approach/Implementation:L489; Results/RQII:L669; Results/RQIII:L767/L797; Related/Attacks:L957/L979. **Highest confusion: 2.**

Figure 1 omits the actual branch logic. Figure 3 hides identical points and utility, uses different y scales, and its legend does not explicitly identify checked-uncalibrated. Table VII uses broad undefined feature labels, and the tiny comparison/family tables need zooming. No clipping or overlapping text was apparent in the 12-page rendered PDF.

**Concrete edit:** label branches and failed-premise exits in Figure 1; group overlapping scatter points with all method labels, add utility labels or a companion panel, and use a common risk scale or emphasize its difference. Define each comparison-table capability operationally, especially Adaptive, Cost, Tool and Conditioned trust; cite the basis for close-source judgments locally. Consider separating CaMeL and Fides if the joint row masks distinct capabilities. Expand the family-table count/rate headings and increase table font size where possible.

**Reassessment check:** figures can be understood without repeatedly consulting full-width tables and each comparison entry has a defined interpretation.

## P2: Separate declared interfaces, current runtime and historical instruments

**Locators:** Background:L163/L178/L242; Approach/Implementation:L474/L508/L514; Design/Evidence:L613; Results/Threats:L821. **Highest confusion: 2.**

Timeout requirements initially sound enforced, whereas a nonreturning plugin can hang. The current bounded scorer differs from historical scorers, but version/run applicability is scattered. “At evaluation” could mean experimental evaluation or runtime evaluation. Core search is not the certified runtime despite a similar raw label.

**Concrete edit:** say at the first layer definition that failure results deny authority but the prototype does not enforce cancellation for arbitrary plugins. Put primary scorer, corrected exploratory scorer, current bounded default and their certificate applicability in a short version table. Say “each runtime decision” or the intended operation instead of “evaluation.” Keep the core/runtime qualification adjacent to every search result label.

**Reassessment check:** the reader knows which implementation each empirical number describes and does not infer availability or adaptive-runtime guarantees.

## P3: Replace development-process vocabulary with reader-facing scientific prose

**Locators:** Design/Evidence:L575; Results/Threats:L844; Related/Guardrails:L855; Related/DualProcess:L880; Related/Layered:L932; Related/Attacks:L979; Discussion:L1002; Availability:L1021. **Highest confusion: mostly 1, except the table-criteria issue above.**

“Opened bibliography,” “seed list,” “structural glyph,” “wider coverage remains necessary for a submission,” template class options and “completed TSE effectiveness claim” expose manuscript-production history without helping explain the scientific result. “No remote publication” beside a repository URL is ambiguous. Full expressiveness first becomes a hypothesis in the table, and invalid delegation moves between RQ I and II without explanation.

**Concrete edit:** replace process notes with concrete scope statements or move reproducibility machinery into availability material. Say “no archival release/DOI” if that is intended. Introduce the expressiveness criterion before claiming it refuted, and give the counterexample a consistent or explicitly cross-cutting RQ assignment. Use saved space for the policy/certificate/correction examples above rather than additional warnings.

**Reassessment check:** a reader unfamiliar with the drafting workflow can interpret all scientific claims and evidence categories from the paper itself.

## Coverage of high-confusion paragraphs

Every initial score-3 paragraph has a dedicated fix above: **L376** (statistical guarantee detour) and **L403** (optimization theorem). Every initial score-2 paragraph is retained in one or more recommendations: **L21, L86, L133, L149, L208, L242, L295, L316, L345, L385, L393, L415, L433, L450, L474, L550, L596, L613, L657, L683, L731, L754, L767, L797, L811, L957**. These scores should not be flattened to minor friction simply because a specialist can infer the intended meaning.

## Suggested reassessment order

1. Resolve canonical versus family actions and show the arithmetic correction's causal trace.
2. Present the implemented policy/ablation matrix and one actual certificate calculation.
3. Rewrite the two score-3 passages and instantiate the counterexample contracts.
4. Reassess only changed paragraphs and their immediate context, explicitly preserving any remaining confusion.

Successful revision would let this reader explain what the runtime actually checks, why the exploratory decisions change, what the selected risk bound promises, and why none of that establishes real-agent effectiveness. It need not add a larger experiment or stronger scientific claim to solve the current clarity problems.
