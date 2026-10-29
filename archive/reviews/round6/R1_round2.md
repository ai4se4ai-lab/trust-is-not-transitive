# Re-review (Round 2) — Reviewer 1 (formal methods, runtime verification, assume-guarantee/contract-based design)

**Manuscript:** "Trust Is Not Transitive: Making Inter-Layer Assumptions Explicit in Hierarchical Guardrails for LLM Agents" (revised; 19 pages)

Line numbers refer to the revised `paper/main.tex`. I compared it against `reviews/round6/before_main.tex.txt`.

What I re-ran:
- `scripts/post_review_analysis.py --verify` reported "Post-review analysis re-derived byte-for-byte".
- I checked `results/processed/post_review.json` against the new macros (l. 317–327). They match: B7 risk 0.00%, utility 66.41% / 66.46%, shift risk 0; 0 disagreements in 18,000 calibration replays.
- I counted coverage replications with no feasible candidate. There are 0 of 1000 in both studies.

No file under `src/`, `tests/` or `formal/` changed in this revision. All changes are to the manuscript, the amendments, the scripts and the processed results.

---

## 1. Overall assessment of the revision

This is a serious, good-faith revision. The authors accepted essentially every criticism I made of overclaiming:
- the title no longer promises "checked composition";
- the countermodel is rebuilt on a rule-respecting trace, T_j′;
- the certificate binding is described as binding *declared* identities;
- the PRISM model is demoted to an illustration;
- the complexity claim is corrected;
- the quarantine result is relabelled "as designed".

They also added a post hoc provenance-only comparator (B7) that *beats* their own method in the sandbox, and they report it prominently, including in the abstract. That is rare and commendable.

The formal part is now mostly correct and honestly scoped. It is also, as the authors say, elementary. Lemma 1 and Lemma 2 are essentially restatements of definitions. The obligation "kinds", which are now the paper's main conceptual contribution, exist only as a hand-written table (Table 4), not in the DSL or the checker.

The empirical part now says plainly that it validates designed behaviour and cannot exercise the semantic layers (l. 918, l. 1125, l. 1183). But l. 1191 lists three changes *within the scripted sandbox* that would make the semantic trade-off observable:
1. benign issue-derived actions;
2. a raw-text judge that benefits from text;
3. several paraphrases per family.

None of these requires API access or licensed models. The authors' stated reason for not evaluating the semantic layers ("no API access or licensed guard models", l. 461) therefore does not cover them. In my view this is the one remaining blocking issue (see Section 5).

## 2. Status of Round-1 major issues

| Issue | Status | Justification (revised text) |
|---|---|---|
| **M1** No theorem linking checker to guarantee | **Partly resolved** | Lemma 1 (l. 757–764), Lemma 2 (l. 783–790) and premise P4 (l. 798) were added, and l. 766 states that the checker does not verify that every route passes the gate. However, the proof of Prop. 2 does not use P4 (see N-R1 below), and Lemma 1 is a definitional unfolding. Acceptable for a paper that says its mathematics is "deliberately elementary" (l. 449), but the link between checker and guarantee is still nominal. |
| **M2** Evidence atoms uninterpreted; distributional obligations; who provides evidence; shift is F1 | **Partly resolved** | Def. 2 now gives obligations a meaning ⟦o⟧ (l. 573). Kinds are introduced (l. 576). Table 4 (l. 714–729) splits `calibrated_context` into a checked configuration part and an assumed distribution part. l. 712 concedes that `provides` is attached to the caller "by convention" while the mediator establishes it. l. 1127 concedes that shift is exactly an assumed-obligation failure. Still open: kinds are not in the DSL ("adding a kind field … is straightforward future work", l. 731), so the checker cannot output the residual set of assumed obligations. The runtime still ignores the declared `requires`/`provides` (`src/tint/runtime/__init__.py:38-42`); a specification that drops `quarantine` everywhere gets identical runtime behaviour, and this is not stated. |
| **M3** Contract semantics mixed per-run and distributional; ambiguous composite guarantee | **Mostly resolved** | Def. 2 now separates hard (per invocation) from statistical (for every D satisfying the obligations) contracts (l. 569–574). l. 583 states that a caller relies on the *composite* guarantee of its sub-hierarchy and that what is forbidden is the "short cut". l. 1213 positions this against Delahaye et al. and Nuzzo et al. and disclaims a contract algebra. Residual typing issue in "realizes" (N-R2). |
| **M4** Countermodel trivial / wrong mechanism | **Mostly resolved** | Prop. 1 now uses T_j′, which satisfies φ_det (l. 589). It names the violated rule ("L2 used G3 although the obligation of C3 was not established", l. 596). It makes Y view-measurable explicit (l. 593). Fig. 1 is redrawn. Residual: the contracts of L1 and L2 are described only by their obligations, and their guarantees are never written down, so "every layer satisfies its contract" cannot be checked for L1 and L2 (N-R4). |
| **M5** Props. 3/4 premises, unproved claim, citations | **Resolved** | (c) states the threshold model V_i < m_i (l. 820). (d) has a concrete counterexample (l. 825). "passes" is defined as "does not block" (l. 564). Fréchet–Hoeffding and Bernstein are cited by name (l. 836, l. 839). The quantifier for route-sum tightness is stated (l. 839). Nit: (b) "differs … when N>1 and θ<1" also needs ∏ m_i > 0. |
| **M6** Certificate binding overclaimed; calibration path ≠ deployed path | **Resolved (in text)** | l. 887: "the *declared* version strings … It does not hash code … The context identifier and view version are configuration constants". The Fig. 2 caption is corrected (l. 678). The calibration-path equivalence is reported (l. 963, 0/18,000) and audited as "checked by replay, not by shared code" (Table 9, l. 1154; Threats, l. 1200). The structural weakness remains, but it is now disclosed accurately. |
| **M7** Vacuous formal evidence | **Resolved (in text)** | H1 attributes the 64-input enumeration to `test_all_deterministic_cases` and calls it "a regression check … not an independent oracle" (l. 1056). PRISM "encodes each trace's routing in its transitions, so it illustrates the countermodel rather than verifying the runtime" (l. 1056). Table 5 says "illustration only" (l. 982). The tautological `formal/check.py` still ships, but the paper no longer relies on it. The meaningful model (N3) was not built. |
| **M8** Checker complexity claim false | **Resolved** | l. 733 now gives O(\|L\| + Σ_e(\|P_caller\| + \|E_e\|)) and attributes the cost to the per-edge intersection. l. 1058 reports a fitted log–log slope of 1.5 and says two membership tests would make the check linear. The code was not changed, which is acceptable now that the claim is correct. |
| **M9** Empirical results true by construction; overclaims | **Resolved** | The abstract now says "inspecting its calibration counts revealed a floating-point defect" (l. 416). l. 1104 gives three qualifications, including that any budget ≥ 35.0% would have certified the defect. The heading now reads "as designed" (l. 1106). Population values are reported first (l. 1048, l. 1106). "Certification changed no decision" and "a raw-text judge here can never use text to do better" are now stated. The tie-break is disclosed (l. 1072). The judge reducing to a second threshold is stated (l. 959, l. 1175). One new terminology problem was introduced (N-R5). |
| **M10** Novelty / missing prior work / Table 10 | **Resolved** | Added: Christianson & Harbison (l. 430, l. 461, l. 1213), Ligatti et al. (l. 478), the dual-LLM pattern with a careful note that CaMeL's "quarantined" component is the *opposite* component (l. 567), Delahaye et al., Nuzzo et al. (l. 482), Learn-then-Test "with Bonferroni correction and binomial tail p-values" (l. 885), and Lindemann et al. (l. 1221). Table 10 now rates TINT S/S/S on Spec/Stat/Trust/Agent, with a footnote. The contribution is restated as operational (l. 1213). The new references are marked `metadata` rather than `yes` in `paper/refs_verification.csv`; please verify them against the sources. |
| **M11** Unproved / imprecise statements | **Resolved** | Adaptive-attacker argument (l. 909); TV bound for the selected policy, u_j + η (l. 908); horizon premise "every decision's proposal has marginal distribution D" (l. 559); atomicity of check and effect in P1 (l. 773, l. 795); i.i.d. in Prop. 5 (l. 878); Background now says "independent or exchangeable" (l. 486). Nit on l. 909: if the attacker plays x every time, the attack distribution has Pr[Y=1] = 1 and R = 1. Say "obtains R equal to the attack rate", as the rest of the sentence does. |

### New-experiment items (N1–N5)

| Item | Status | Comment |
|---|---|---|
| **N1** Judge that adds information on a richer structured view | **Not resolved** | Discussed only (l. 1175, l. 1191). As argued in Section 5, this does not need a real LLM: a scripted judge that reads typed fields extracted from the issue would do. |
| **N2** Per-route certificates (q > 1) | **Not resolved, acceptably handled** | Prop. 2 keeps the route form. Fig. 5 now shows two routes, and l. 807 explains how the route form connects to the edges. The implementation still uses only q = 1. Acceptable as stated. |
| **N3** Meaningful model checking (nondeterministic judge) | **Not resolved** | The PRISM model is demoted rather than replaced. Acceptable, but the cheap MDP model I suggested would still be the right way to make H1 non-definitional. |
| **N4** Bounded-exhaustive checker validation | **Not resolved, disclosed** | l. 1058 now lists the three unmutated conditions. |
| **N5** Response-informed adaptive attacker | **Not resolved, disclosed** | l. 1129. |

## 3. Status of Round-1 minor issues

| # | Status | Note |
|---|---|---|
| m1 π clash | Resolved | θ = Pr[Y=1] (Table 2, l. 528, l. 814). |
| m2 m/n clashes | Resolved, but a new clash was introduced | N guards, q routes. However, q(x) is the escalation probability in Prop. 6 (l. 889). See N-R6. |
| m3 R(q) undefined | Resolved | R_D(q) is defined at l. 889. |
| m4 λ clash | Resolved | μ is the multiplier (l. 893). |
| m5 Alg. 1 line 2; metadata view requiring quarantine | Partly | Line 2 is fixed (l. 742). The metadata-view case is neither addressed nor justified (l. 748). |
| m6 "iterative DFS" comment | Not resolved | Code is unchanged (`src/tint/spec/__init__.py:103`). Trivial. |
| m7 timing asymmetry, "logging" | Resolved | l. 1131. |
| m8 block-all counted as covered | Resolved (moot) | I checked: 0 of 1000 replications in both studies had no feasible candidate. |
| m9 replay bound vs population risk | Resolved | l. 1068. |
| m10 LP uses true risks | Partly | l. 900 states the deployable LP must use u_j. The synthesis study still solves on true risks (`experiments/run.py:208`), and H5 (l. 1072) does not say so. |
| m11 approval reuse | Resolved | l. 547. |
| m12 environment check double-blocks | Resolved | l. 957, l. 1056. |
| m13 L1 provides quarantine | Resolved | l. 712. |
| m14 Fig. 4 axis | Resolved | The figure was replaced by a fitted slope in the text (l. 1058). |
| m15 H8 framing | Resolved | l. 923. |
| m16 Def. 1 vs FRAMEWORK.md D3 | Not resolved | `formal/FRAMEWORK.md` was not updated. Its T1 still has premises (a)–(d), not P1–P5. Sync it or mark it superseded. |
| m17 conditional probabilities | Resolved | l. 828. |
| m18 "in the implemented topology" | Resolved | l. 775. |
| m19 title | Resolved | l. 404. |
| m20 tie-break | Resolved | l. 874, l. 1072. |
| m21 encoded family size | Resolved | The size is given in the splits paragraph (l. 1018). |

## 4. New problems introduced or exposed by the revision

**N-R1 (rigor). P4 does no work in the proof of Prop. 2.**
The proof's last sentence (l. 804) says: "P4 ensures that each route's certificate is about the layers' contracted views, which is what makes the certified decision function the one that is deployed." This is a non sequitur. Containment of the deployed decision function in the certified one *is* the content of P5 and Lemma 2, and P4 does not imply it. Similarly, the remark at l. 807 says that if the quarantine obligation were not realized, the deployed function "would no longer be contained" in the certified one. This is too strong: a raw-text judge could coincidentally make identical decisions. The correct phrase is "would no longer be *guaranteed* to be contained".

*Fix.* Either drop P4 from the premises and present Lemma 1 as the engineering argument for why P5's containment is plausible, or make the dependence formal. For example: "if every edge is realized and the certified function was computed with the same contracted views, then the deployed function equals the certified one on all invocations satisfying the per-invocation obligations". Then cite that step in the proof.

**N-R2 (rigor). "Realizes" is ill-typed for distributional obligations.**
Def. 3 (l. 580) says an implementation realizes an edge if every obligation in E "holds, in its meaning, on every invocation". Def. 2 allows obligations whose meaning is a predicate on a *distribution* (l. 573), such as the distribution part of `calibrated_context`. Such an obligation cannot hold "on an invocation". Lemma 1's second consequence ("provided its distributional obligations hold") silently patches this.

*Fix.* Define realization separately for the two sorts:
- per-invocation obligations hold on every invocation through the edge;
- distributional obligations hold for the law of invocations through the edge.

Also state that, in a statistical contract, per-invocation obligations are required D-almost surely.

**N-R3 (rigor/presentation). Def. 3 and Alg. 1 now disagree.**
Def. 3 dropped "every item of E is provided by i" (l. 580), but Alg. 1 line 7 still rejects when E ⊄ provides(i) (l. 747). The prose at l. 733 describes acceptance without mentioning the `provides` check. Either restore the condition in Def. 3 or say that Alg. 1 checks a stricter condition than well-formedness, and why (given l. 712 calls `provides` a convention).

**N-R4 (rigor). Prop. 1 leaves the L1 and L2 contracts unspecified.**
The proof gives L2's obligation but never its guarantee, and gives neither obligation nor guarantee for L1 (l. 593). Since the proposition claims "every layer satisfies its contract", write G_1 and G_2 out, e.g., G_2: "L2 returns L3's verdict". One sentence suffices.

**N-R5 (presentation; new ambiguity). "Gate" now means two different things.**
"Gate" is the deterministic L1 gate throughout Sec. III–IV and Tables 6–7. The abstract and Sec. V-RQ3 also use "risk gate" and bare "the gate" for the certificate requirement:
- l. 416: "the same pipeline without the gate would have shipped";
- l. 1104: "Pipelines without the gate shipped the defect: B6 … and B5". Both B6 and B5 *have* the deterministic gate.

A reader will misparse these sentences. Use "certificate check" or "certification step" consistently for the statistical part, and keep "gate" for L1.

**N-R6 (notation; new clashes).**
- q is both the number of routes (Table 2; l. 799, l. 807) and the escalation probability q(x) (l. 889–897).
- E denotes both acceptance routes E_r and the obligation set E of an edge (Def. 3; Alg. 1). In P4–P5 both appear in the same proposition.
- e is the action environment (l. 545) and the edge index in Σ_e (l. 733).
- c is the matched-token count (l. 959, Table 7) and the layer cost c_i (Def. 1).

Rename the routes (e.g., A_r or 𝓔_r) and their count.

**N-R7 (overclaim, new). B7 is described as "the policy that provenance-based isolation would apply [CaMeL, Fides]" (l. 1020).**
This mischaracterizes both systems. CaMeL does not block every action whose inputs are untrusted. It prevents untrusted data from influencing *control flow* and checks capability-based policies on data flows to tools, so untrusted values may well reach tools. Fides likewise tracks labels and enforces policies rather than blocking all tainted actions. B7 is the strictest possible taint policy. Say "the strictest taint policy (block any action with an untrusted input)". Also qualify l. 1219 ("these systems' data-flow guarantees are the stronger tool"): B7 is not these systems.

**N-R8 (overclaim, minor). The abstract overstates in two places.**
- "Each inter-layer trust relation is a declared edge whose obligations are classified as checked at runtime, true by construction, or assumed" (l. 416). The DSL does not record kinds; the classification is a hand-written table (l. 731). Say "… whose obligations we classify …" or add the kind field.
- The study is called "preregistered" (l. 416) although l. 923 discloses that the trace generator and templates, "which determine every scripted outcome", were committed after the preregistration tag. The disclosure in the body is exemplary. The abstract should carry a qualifier, e.g., "a study with preregistered hypotheses and analyses".

**N-R9 (verifiability).**
- The Data Availability section now gives a named GitHub organization URL (l. 1260). If the venue's review is meant to be anonymous ("Author Names Withheld", l. 406), this de-anonymizes the submission.
- The newly added references are only metadata-checked in `paper/refs_verification.csv`.

**N-R10 (minor).** "Contribution 4 … compare against six controlled comparators" (l. 451) versus seven pipelines including B7 (l. 1020). Consistent with "six preregistered", but say so in the contribution.

No arithmetic errors were found in the revision:
- Fig. 5's percentages (25/40/35) agree with the family masses.
- "With any budget of at least 35.0%" matches the primary bound maximum.
- The B7 macros agree with `post_review.json`.
- The slope of 1.5 is consistent with the super-linear growth I computed in Round 1.

## 5. Remaining blocking issue

**B1. The study cannot evaluate the semantic half of the discipline, and the obstacle is not the one the paper cites.**

After the revision, the empirical record is:
- the deterministic gate does the work;
- B7, a one-line provenance rule, dominates TINT on risk, utility, cost and shift (l. 1125);
- certification changed no decision after the fix (l. 1123);
- selection was degenerate (l. 1072);
- the structured-view judge is a second threshold on the scorer (l. 959);
- the quarantine result holds by construction (l. 1106).

The authors acknowledge every one of these points. Together they mean that no evidence in the paper bears on the parts of TINT that go beyond a reference monitor plus a held-out acceptance test: trust edges over statistical guards, escalation, and certificate-bound routing.

The paper attributes this to the lack of LLM or API access (l. 461, l. 918). But l. 1191 itself lists three changes that would make the trade-off observable inside the scripted sandbox, and none needs a model:
1. benign issue-derived patches, so that B7 is no longer free;
2. a raw-text judge that genuinely uses text, for instance one that accepts authorized issue-derived patches by reading the request, so that the structured view has a measurable utility cost;
3. a dual-LLM-style typed projection (l. 1175) as a third judge view;

plus paraphrased templates so the threshold grid is not degenerate.

This is a modest extension of `experiments/dataset.py` and `tint.layers`. It would be labelled exploratory, like A1. It would give the paper at least one non-trivial result about the trade-off it was built to study, namely how much utility the structured view costs and how much risk it removes once provenance alone no longer suffices. It would also exercise Prop. 6 and per-route accounting.

Without such a result, the paper is a well-written, honest account of a design discipline whose distinctive mechanisms are untested even within the paper's own methodology. For a TSE full paper I consider that insufficient. With it, I would move to accept or minor revision.

Text-level fixes still requested (not blocking): N-R1, N-R2, N-R3, N-R5, N-R6, N-R7, N-R8.

## 6. Updated scores and recommendation

| Criterion | Round 1 | Round 2 | Justification |
|---|---|---|---|
| i) Novelty | 2 | **2** | Positioning is now accurate and honest (l. 885, l. 1213, Table 10), which I credit. But that accuracy shows a modest increment. The new conceptual element, typed obligation kinds, is a hand-written classification not supported by the tool. The evidence shows a provenance rule suffices in the evaluated setting. |
| ii) Rigor | 2 | **3** | The statements are now correct and premises are explicit (Props. 2–6, M5, M11). Remaining problems: P4 is decorative in the Prop. 2 proof (N-R1), "realizes" is ill-typed for distributional obligations (N-R2), and Def. 3 and Alg. 1 disagree (N-R3). The lemmas are near-definitional. |
| iii) Relevance | 4 | **4** | Unchanged. The LlamaFirewall walk-through (l. 1187) helps practitioners. |
| iv) Verifiability & transparency | 4 | **5** | Exemplary. A3 is dated and re-derivable byte for byte (verified). Calibration-path equivalence is checked and reported. The prereg timing gap is disclosed (l. 923). The H6 rule deviation is disclosed (l. 946). Formal artifacts are described accurately. Small caveats: FRAMEWORK.md is out of sync, and the new references are metadata-only. |
| v) Presentation | 4 | **4** | Clearer framing, better figures (Fig. 1, Fig. 5), and the CaMeL/dual-LLM terminology explained. New "gate" ambiguity (N-R5) and notation clashes q, E, e, c (N-R6). |

**Recommendation: Major revision.**

This is a narrow major revision. The formal and presentational issues are now minor and fixable in text. The single blocking request is B1: an exploratory extension of the scripted sandbox (benign issue-derived actions, a text-using raw judge, a typed-projection judge, paraphrased templates). It needs no model access and is the minimum evidence that the paper's semantic mechanisms do anything a provenance rule does not. If the editor judges the paper as a design-discipline contribution with feasibility evidence only, my recommendation would be minor revision conditional on N-R1 to N-R8.
