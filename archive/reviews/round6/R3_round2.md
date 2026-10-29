# Re-review (Round 2) — Reviewer 3 (SE for AI / LLM developer tools; presentation and relevance)

Manuscript (revised): "Trust Is Not Transitive: Making Inter-Layer Assumptions Explicit in Hierarchical Guardrails for LLM Agents". The PDF has 19 pages; references start on p. 17, so the body is about 16 pages.

I compared the revised `paper/main.tex` with the version I reviewed (`reviews/round6/before_main.tex.txt`), read the revised paper in full, and re-ran the test suite (56 passed). The build log has no undefined references and no overfull boxes.

## Overall impression

This is a substantial and, for the most part, honest revision. The authors did more than relabel things:

- They added a containment lemma and an explicit route example (Fig. 4).
- They rewrote the abstract and the RQ3 section, which now say the RQ3 outcome follows from the design.
- They added a post hoc provenance comparator (B7) that beats their own method, and they report it prominently.
- They corrected the checker's complexity claim (log–log slope 1.5, not linear) and disclosed that the trace templates were committed about 90 s *after* the preregistration tag.
- They explained the role of the budget in the primary result: any budget of at least 35% would have certified the defective pipeline.

These changes raise Rigor and Presentation clearly.

The same honesty also exposes the paper's central weakness for a TSE audience:

- The deterministic gate is classical.
- The structured-view judge is, by the authors' own description, "a second threshold on the score".
- Certification changed no decision after the fix.
- A provenance rule dominates TINT in the sandbox.

What remains as TINT's own engineering contribution is the *classification of obligations by kind* (checked / by construction / assumed) and the audit that results from it. That idea is now the key idea, but it is not implemented in the tool: "The current DSL does not record kinds; Table III classifies them by hand". It is also not exercised on any real configuration; the LlamaFirewall walk-through is hypothetical and prose-only. This is the main remaining issue.

## 1. Status of Round-1 issues

### Major issues

| ID | Status | Justification (revised text) |
|---|---|---|
| **M1** Label/notation overloading | **Mostly resolved; new collisions introduced** | The assumptions are now (P1)–(P5), the comparator is B6, F1–F3 are gone, and the base rate is now θ, the multiplier μ, the guard count N and the token count c. Obligations are now a named set $O_i$ with a meaning $\llbracket o\rrbracket$ (Def. 2), which fixes the "$A_j\subseteq E$" type confusion. Amendments keep the names A1–A3, which is harmless now that nothing else is called A1. New collisions: (a) **"gate"** now means both the deterministic $L_1$ gate and the certification "risk gate". This yields a wrong-sounding sentence in V-F: "Pipelines without the gate shipped the defect: B6, identical to TINT except for the certificate requirement" — but B6 *has* the (deterministic) gate. The abstract has the same ambiguity ("the same pipeline without the gate would have shipped"). (b) **$q$** is the number of routes ($E_1,\dots,E_q$) and also the escalation probability $q(x)$ in Prop. 6. (c) **$r$** indexes routes ($E_r$, $b_r$) and also names the conditional risks $r_0(x)$, $r_1(x)$. (d) **$E$** is still both the obligation set of an edge ($i\xrightarrow{p,E}j$) and the route events $E_r$. (e) **$c$** is the token count and also the layer cost $c_i$ in Def. 1. See N1. |
| **M2** Trust edges not load-bearing | **Largely resolved** | The new Lemma 1 (checked and realized edges) and Lemma 2 (containment) are what was missing. (P4) now names the edges in the soundness result. The DevAgent two-route discussion after Prop. 2 explains exactly how an unrealized `quarantine` obligation invalidates the $E_2$ certificate. The text "Chains of trust remain possible ... What TINT forbids is the short cut" fixes the title tension. Residual: in the proof, (P4) is used only in prose ("P4 ensures that each route's certificate is about the layers' contracted views"). The formal step goes through the containment premise in (P5), and in the implementation containment is *checked by replay* (0 of 18,000 disagreements), not derived from the edges. State plainly that, for $q=1$, (P4) is a sufficient condition for the containment premise, and say how. |
| **M3** RQ3 effect by construction, stats foregrounded | **Resolved** | The abstract now says "validated the designed behaviors" and "removed the one family that targets the judge, as designed"; 336,000 has been removed from the abstract. The section heading reads "...as designed". Population values lead, and the stats are one sentence with the floor noted. The new sentence "the design also cannot observe the cost of the structured view: a raw-text judge here can never use text to do better" is an important and welcome admission. |
| **M4** Quarantine defeats the judge; term inversion | **Resolved in the prose; partly in the artifact** | The terms are now "structured-view judge" and "exposed judge", with an explicit contrast to CaMeL's Q-LLM, and the dual-LLM pattern (Willison) is cited (II-B, III-B). Lesson 3 is recast with concrete typed fields for coding agents. Residual: the DSL obligation, the function and Table III still use the name **`quarantine`** for "the judge does *not* read untrusted text", which is exactly the inverted sense. Rename it to `structured_view` in the DSL and code, or at least add a footnote at Fig. 3. |
| **M5** No mapping of a real stack; "most stacks we examined" | **Partly resolved** | The unsupported claim is gone. The new VI-C walks through a *hypothetical* LlamaFirewall deployment and raises three good questions. But it is prose only: there is no specification, no checker output and no obligation/kind table for that configuration, and "We have not validated such a mapping with practitioners." Because the key idea is now obligation *kinds* (abstract, Key idea, Lesson 1), the tool should implement them. See **B1** below. |
| **M6** Certification-gate claim overstated | **Resolved** | V-F now gives "Three qualifications": the gate did not diagnose the defect, the refusal depended on the budget (any budget of at least 35% would have certified), and any acceptance test would have caught it. The degenerate-grid diagnostic I asked about (Q5) is now suggested. Lesson 4 credits "measure the pipeline against a budget". |
| **M7** Figures | **Resolved** | Fig. 1 is redrawn left to right with dashed verdict returns and uses $T_j^{p}$. The scaling and dependence figures are removed and replaced by text. The new Fig. 4 (routes with family masses) is the teaching figure I asked for and is correct: 25% + 40% + 35% = 100%, and the route contents match Table VII. Four Fig. 3 oddities are explained ("Four details of Fig. 3 deserve explanation"). Small residual: Fig. 4 is placed in IV-C but first referenced in IV-B, after Prop. 2. |

### Minor issues

| ID | Status | Justification |
|---|---|---|
| m1 abstract key sentence | Resolved | Now "In the frozen primary run the risk gate refused to deploy any policy, and inspecting its calibration counts revealed a floating-point defect..." (but see N1 on "gate"). |
| m2 comparator naming | Resolved | "B5 Gate + scorer + exposed judge" and "strong control" are used consistently, and "rule-plus-judge" and "naive relay" are gone. "naive routing" survives once (H1/PRISM) and "naive hierarchical guardrails" once (RQ3, verbatim RQ); both are acceptable. |
| m3 "sink" vs taint sink | Partly resolved | Renamed to "gate", which is good. The host is still `sink.invalid` (harmless now), but the rename created the gate/risk-gate collision (N1). |
| m4 System 1/2 | Resolved | Removed. |
| m5 repetition of "does not transfer" | Partly resolved | "Ten seeds" repetition is gone and Scope is shortened. The disclaimer still appears in the abstract, the Section V intro, Answer to RQ3, VI-D, Threats/External and the Conclusion. Acceptable, but the V-intro and RQ3-answer copies could go. |
| m6 H7/H8 justification | Resolved | "registered ... to bind ourselves to reporting them." |
| m7 H6 vague | Resolved by acknowledgment | Kept "as registered", with the outcome column and a paragraph explaining that the literal rule was ill-posed. This is the right way to treat a preregistered text. |
| m8 over-precision | Partly resolved | The text now leads with population values (10%, 20%), but Table V still prints two decimals. |
| m9 Table VIII caption | Resolved | Retitled. |
| m10 six vs seven pipelines | Resolved | "TINT, six preregistered comparators B1–B6, and one post hoc comparator B7." |
| m11 Prop. 1 idealized judge | Resolved | "Fix a fixture law in which Y is a function of the structured view ... an idealized judge". |
| m12 "drives to its sign" | Resolved | Rewritten exactly as suggested. |
| m13 horizon $HR$ | Resolved | Now states the marginal-distribution condition and why agent sessions rarely satisfy it. |
| m14 "Most stacks we examined" | Resolved | Removed. |
| m15 artifact link | Resolved for verifiability, but **new problem** | A link is given, but it is `github.com/ai4se4ai-lab/...` while the title page says "Author Names Withheld". If the submission is double-anonymous, this de-anonymizes it. See N6. |
| m16 CPU sentence | Resolved | The timing asymmetry is now disclosed (view and fingerprint inside TINT's timer only). This is better than what I asked for. |
| m17 Fig. 3 oddities | Resolved | See M7. |
| m18 "What we do not claim" | Resolved | Replaced by a three-sentence "Scope". |
| m19 related-work self-rating | Resolved | The coding procedure is stated, and TINT is now rated "S" in four columns with footnoted reasons. |

### Round-1 list of unnatural sentences

| # | Sentence (round 1) | Status |
|---|---|---|
| 1 | "we did not relabel synthetic evidence as such" | Resolved (removed) |
| 2 | "The mathematics is elementary by design; ..." | Resolved (rewritten essentially as suggested) |
| 3 | "Non-transitivity is a design rule here, not a theorem ..." | Resolved (replaced by the composed-along-declared-edges paragraph) |
| 4 | "This design buys internal validity ..." | Resolved |
| 5 | "naming a regular expression after them would mislead" | Resolved |
| 6 | "A local tag is a timestamp under our control ..." | Resolved, with additional honest disclosure |
| 7 | "It is uninformative." | Resolved ("turned out to be uninformative for two reasons") |
| 8 | "turned a silent defect into a visible, safe failure" | Resolved |
| 9 | "of no service value" | Resolved |
| 10 | "adapters alone, however, are not evidence" | Resolved |
| 11 | "Both laws have the same per-guard miss rates." | Resolved (merged) |
| 12 | "This is where trust enters." | Resolved |
| 13 | run of short declaratives in III-A | Partly resolved ("The monitor writes the labels, and the agent cannot." is still clipped) |
| 14 | "Text addressed to the judge cannot reach it. The price is ..." | Resolved (joined with "but") |
| 15 | "The gap is not academic." | Resolved |
| 16 | "The practical consequence is simple" / "The premises matter." | Resolved (both removed) |

The ", not " count dropped from 18 to 13, and the prose now reads much more naturally overall.

## 2. Comprehension check on the revised paper

| Earlier answer | Now |
|---|---|
| Q2(a): in what sense is TINT "non-transitive" if verdicts are relayed? (vague) | **Clear.** The Key idea and the paragraph after Def. 3 say that chains are allowed along declared, realized edges and that what is forbidden is deriving $i\to k$. The title change ("Making Inter-Layer Assumptions Explicit") also matches the content better. |
| Q2(b): believing that quarantine stops $T_j$ (wrong) | **Clear.** The new trace $T_j^{p}$ (a judge-targeting patch that breaks no rule) separates the two mechanisms. The running example, Prop. 1, Fig. 1 and H4 now all say that the gate stops $T_j$ and that only $T_j^{p}$ needs the view obligation. |
| Q3: answer to the escalation half of RQ2 (vague) | **Clear.** Answer to RQ2 now states the risk-reduction-per-cost rule and that selection in the sandbox "reduced to a feasibility decision, so the escalation theory was not exercised there". That is honest, and it is the right answer. |
| Q4: exchangeability hidden in the soundness result (wrong) | **Clear.** (P5) now says "computed from $n$ i.i.d. calibration proposals drawn from $D$", and Table III splits `calibrated_context` into a checked configuration part and an assumed distribution part. This is the best single improvement for the target reader. |
| Q4: confusing (A1) with comparator A1 | **Clear** (P1–P5, B6). |
| Q5: "six comparators" vs "seven pipelines"; 10-point drop read as an empirical effect | **Clear** on both counts. |

New comprehension friction a PhD student would hit:

- **"Gate".** "Pipelines without the gate shipped the defect: B6..." made me reread twice, because B6 is listed in Table VI with Gate = yes.
- **What the tool does vs. what the paper does.** The abstract says obligations "are classified as checked at runtime, true by construction, or assumed". A reader will assume the library does this. Only in IV-A does one learn that the DSL does not record kinds and the classification is by hand.

## 3. New problems introduced by the revision

**N1. "Gate" now has two meanings (blocking for clarity).** "Deterministic gate" ($L_1$) appears throughout. "Risk gate" (the certification step) appears in the abstract, the V-F heading, V-F body and VI-B. "The gate" is used unqualified 18 times. In the abstract, both appear within three sentences.
*Fix:* keep "gate" for $L_1$ only, and call the certification step the "certificate check" or "risk check". Change "Pipelines without the gate shipped the defect" to "Pipelines without the certificate check shipped the defect".

**N2. Obligation kinds are the key idea but are not in the tool (blocking for relevance).** The abstract, Key idea, Problem (ii), Lesson 1 and the Conclusion all present kinds as part of TINT, but "The current DSL does not record kinds; Table III classifies them by hand, and adding a kind field to the DSL is straightforward future work." If it is straightforward, it should be done for this paper, because it is what distinguishes TINT from ContrAgent and the layered-A/G position. Concretely, the change needs four parts:
- a `kind` field per obligation;
- a checker rule that every `checked` obligation names a runtime predicate;
- a generated audit listing the `assumed` obligations;
- the same applied to the LlamaFirewall spec of VI-C, with the generated list shown.

Otherwise, the abstract should say "we classify obligations (manually, in this paper) as...".

**N3. "Preregistered" in the abstract needs qualification.** The honest new disclosure in V-A ("[the generator and driver] were committed about ninety seconds after the tag ...; the templates, which determine every scripted outcome, were therefore authored with knowledge of the scorer") means that the scripted outcomes, which are the RQ3 results, were not frozen by the preregistration. Amendments A2 and A3 were also written after results were known. The abstract and Contribution 4 still say "A preregistered study" without qualification.
*Suggest:* "A study whose hypotheses, thresholds and analyses were preregistered (the trace templates were not)".

**N4. Lesson 1 contradicts the results.** It says "in our study it predicted the one failure, shift, that no mechanism prevented". But B7 had 0.00% risk on the shift split (V-F, "Shift": "every pipeline except B7"), and the Conclusion correctly says "no *semantic* mechanism". The claim that the edge exercise "predicted" the shift failure is also generous: exchangeability is a generic premise of every calibrated guard and is listed in IV-E independently of any edge.
*Fix:* "...it lists the distributional assumption that the shift experiment then violated; no semantic mechanism prevented that failure."

**N5. B7 generalization claims.** "our post hoc comparator B7 suggests that, where provenance suffices, these systems' data-flow guarantees are the stronger tool" (Related Work) and "a deployment should exhaust deterministic provenance policies before relying on semantic guards" (V-F). Both rest on a law that, as the authors say, "contains no benign issue-derived action", a property chosen by the authors. The V-F paragraph qualifies this well, but the Related Work sentence and Lesson 2 drop the qualifier. Keep "in our sandbox" attached wherever B7 is used to argue.

**N6. De-anonymization.** The Data Availability statement links to `github.com/ai4se4ai-lab/trust-is-not-transitive` while the author block says "Author Names Withheld". Check the venue's review policy. If the review is double-anonymous, use an anonymized mirror for review and restore the archival DOI sentence that was dropped ("An archival copy with a persistent identifier will be created on acceptance").

**N7. Abstract length.** The abstract is 323 words (previously 309, which I should have flagged in round 1). IEEE recommends 150–250 words. Candidates for cutting: the four-item list of mechanisms could become one sentence, and "give a composition result that states exactly which premises bound end-to-end risk" overlaps with the following clause.

**N8. Residual notation collisions** ($q$, $r$, $E$, $c$; see M1). Add the escalation probability and conditional risks to Table II, or rename them: routes $E_1..E_q$ → $\mathcal{A}_1..\mathcal{A}_\ell$ with index $\ell$, keeping $E$ for edge obligations; escalation probability $q(x)$ → $\eta(x)$. Note that $\eta$ is already the TV-shift size, so $\gamma(x)$ is better.

**N9. P4 in the proof.** See M2 residual. A short sentence would make the dependency precise: "For $q=1$, P4 implies the containment premise of P5 because the calibrated decision core and the runtime then evaluate the same views; we additionally check it by replay."

**N10. PRISM abstraction scope.** H1/H4 check "the three canonical traces" ($T^*$, $T_b$, $T_j$), but the trace that now carries the argument, $T_j^{p}$, is not in the abstraction. Either add it or say why not. Since the abstraction is now described as "illustration only", one sentence would be enough.

### Remaining sentences that read mechanically

These are far fewer than in round 1, and none is serious:

- "Three qualifications keep this observation in proportion." → "This observation needs three qualifications."
- "A cheap diagnostic suggests itself: ..." → "A simple diagnostic would have flagged the problem earlier: ..."
- "This is a property of our law, and a fair one to report: ..." → "This is a property of our fixture law, but it is worth reporting: ..."
- "The figure says only that the runtime's bookkeeping costs tens of microseconds in Python." → "The measurement shows only that ..."
- "Four details of Fig. 3 deserve explanation." This is fine, but the paragraph then mixes explanation with a caveat about who establishes obligations. Split it into two paragraphs.
- "The monitor writes the labels, and the agent cannot." → "Labels are written by the monitor; the agent cannot write them."
- "It does not show that semantic guards are useless; it shows that our sandbox could not exercise them." This is the "X, not Y" pattern again, but here the contrast is meaningful. Keep it.

## 4. Updated scores and recommendation

| Criterion | Round 1 | Round 2 | Reason for change |
|---|---|---|---|
| i) Novelty | 2 | **2** | The framing is clearer and more honestly scoped, with Related Work now positioned against stochastic contracts and LTT. The distinctive idea (obligation kinds plus a certificate-applicability obligation) is modest and not yet implemented in the tool (N2). |
| ii) Rigor | 3 | **4** | Containment lemma, replay check of calibration/runtime agreement, corrected complexity, budget sensitivity, honest prereg disclosure, the B7 control, and the H6 deviation handled properly. Not 5: (P4) is used informally (N9), and "preregistered" needs qualification (N3). |
| iii) Relevance | 3 | **3** | The LlamaFirewall walk-through and the redesigned Lesson 3 help. But the evidence now says plainly that the gate (classical) and provenance did the work, that the semantic layers "were never needed" in the sandbox, and that the obligation audit has been applied to no real configuration (N2, M5). A practitioner gains a useful checklist, but not yet a tool. |
| iv) Verifiability / Transparency | 5 | **5** | Still exemplary: new verified post-review analyses, a calibration-equivalence replay, and a public link. Subject to the anonymity check (N6). |
| v) Presentation | 3 | **4** | A large improvement: notation table, P1–P5/B6 labels, $T_j^{p}$, Fig. 1 redrawn, Fig. 4 added, RQ answers complete, prose natural. Held back by the gate/risk-gate collision (N1), the remaining symbol collisions (N8) and the abstract length (N7). |

**Recommendation: Minor revision.** This is an upgrade from major revision, conditional on the blocking items below. I would accept the paper as an honest, well-engineered design-and-feasibility study once the obligation-kind idea it now leads with is actually implemented and demonstrated, or else described as a manual method.

### Remaining blocking issues

1. **B1 (N2 + M5): implement or de-claim obligation kinds.** Either add a `kind` field and a generated assumed-obligation audit to the DSL and checker, and apply it to a concrete spec of the VI-C LlamaFirewall design (spec listing plus checker output plus audit list), or rewrite the abstract, Key idea and Contributions to say that the classification is a manual method supported by the checker.
2. **B2 (N1): remove the "gate" ambiguity**, in particular "Pipelines without the gate shipped the defect", which is literally false for B6.
3. **B3 (N3, N4, N5): calibrate three claims.** Qualify "preregistered" in the abstract and Contribution 4. Fix Lesson 1's "no mechanism prevented" (B7 did). Keep "in our sandbox" attached to the B7-based recommendations.
4. **B4 (N6): resolve the anonymity conflict** between "Author Names Withheld" and the GitHub organization link, according to venue policy.

Non-blocking but recommended: N7 (abstract ≤ 250 words), N8 (symbol collisions), N9 (one sentence on P4 ⇒ containment), N10 (put $T_j^{p}$ in the PRISM abstraction or say why not), and renaming the `quarantine` obligation (M4 residual).
