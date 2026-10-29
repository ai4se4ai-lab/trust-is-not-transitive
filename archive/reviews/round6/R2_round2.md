# Re-review (Round 2) — Reviewer 2 (empirical methods, statistics, artifact)

**Revised version reviewed:** `paper/main.tex` (1269 lines; `paper/main.pdf`, 19 pages), compared with the round-1 version archived at `reviews/round6/before_main.tex.txt`. Also reviewed: Amendment A3 (`experiments/AMENDMENTS.md`), `scripts/post_review_analysis.py`, `results/processed/post_review.json`, `scripts/manifest.py`, `.gitattributes` and `ARTIFACT.md`.

## Overall assessment

This is a serious, good-faith revision. Every issue I raised that could be fixed with existing evidence has been addressed in the text, most of them fully.

What changed:
- **Reframing.** The evaluation is now explicitly a validation of designed behaviour (Sec. V intro: "every pipeline's decision on a trace family is known in advance. The replay therefore validates designed behavior and measures nothing about real guards").
- **B7.** The provenance-only comparator was added and is reported as beating TINT.
- **Corrected claims.** The H1, checker-scaling and "gate exposed the defect" claims were corrected.
- **Preregistration.** The chronology was disclosed and the hypotheses table gained an outcome column.
- **Artifact.** The artifact verifies.

Two things remain.

1. **No experiment yet exercises the semantic layers.** The central experiment I asked for (M9) was not run. The paper now openly says that "our sandbox could not exercise them [semantic guards]" (Sec. VI-B). For a TSE paper whose contribution includes a semantic judge view, certificates and escalation selection, an evaluation that by its own admission never exercises any of them is the remaining blocking weakness. It is cheap to fix without LLMs.
2. **A new factual error, which I partly caused.** The revision repeatedly states that the fixture law "contains no benign issue-derived action". That is false: the benign-security family is a benign patch whose only input is the untrusted issue (Table V; `experiments/dataset.py:22-24`). My round-1 M2 used the same imprecise wording ("lacks benign issue-derived patches"), and I correct it here (N1 below). The correct mechanism changes how B7's result should be read.

---

## 1. Status of round-1 issues

### Major issues

| ID | Status | Justification (revised text) |
|---|---|---|
| **M1** RQ3 effect determined by construction; statistics ceremonial | **Resolved** | See note (a). |
| **M2** Missing provenance comparator | **Resolved (manuscript)** | See note (b). Its explanation contains the error in N1. |
| **M3** "Gate exposed the defect" overclaim | **Resolved** | See note (c). |
| **M4** H1 evidence overstated | **Resolved** | See note (d). |
| **M5** Checker "linear" claim wrong | **Resolved** | See note (e). |
| **M6** Preregistration chronology; H6 verdict | **Resolved** | See note (f). |
| **M7** Degenerate selection; unsafe certified policy | **Resolved** | See note (g). |
| **M8** Certified ≠ deployed object; fingerprint binds version strings | **Mostly resolved** | See note (h). Calibration still does not run through the runtime. |
| **M9** Fixture law cannot test the central trade-off (new experiment) | **Not resolved (blocking)** | See note (i). |
| **M10** Asymmetric timing; "logging" misattribution | **Resolved (by disclosure)** | See note (j). |
| **M11** `verify-results` fails; manifest platform-dependent | **Resolved in working tree; must be committed** | See note (k) and §2. |

Notes:

- **(a) M1.**
  - The headline now reads "After the fix: the structured view removed the judge-targeting family, as designed".
  - Population values from the authored masses come first (Sec. V-F), with the statement "The difference is therefore one designed family, and it measures nothing about how a real judge responds to instructions".
  - The paired statistics are explained as sign-consistency checks at the $p$ floor (Sec. V-C, Statistical analysis).
  - The text states that the design cannot observe the cost of the structured view (end of Sec. V-F; Threats, construct validity).
  - The abstract no longer quotes the percentages.
- **(b) M2.**
  - B7 appears in Table VI and in both blocks of Table VII, with $\dagger$ "Post hoc (Amendment A3)".
  - A dedicated paragraph is headed "A provenance rule outperforms TINT in this sandbox".
  - The shift result is "every pipeline except B7".
  - The old sentence about the implicit patch being indistinguishable "in every guard's view" was replaced.
- **(c) M3.** Sec. V-F gives three explicit qualifications: the gate "did not diagnose the defect"; with any budget of at least `\resPrimaryBoundMax`% (35.0%) every primary seed would have certified the defective pipeline; and any labelled pre-deployment acceptance test would have caught it. The abstract claim was removed. Two remaining phrasings are slightly loose (m-a below).
- **(d) M4.**
  - H1 now cites `test_all_deterministic_cases` as "a regression check of the implementation, not an independent oracle".
  - The PRISM abstraction "illustrates the countermodel rather than verifying the runtime".
  - The hard-violation zero is called "close to definitional".
  - Table IX now says "regression-tested", and Table IV says "illustration only".
- **(e) M5.**
  - Sec. IV-A gives the bound $O(|\mathcal L|+\sum_e(|P_{\text{caller}}|+|E_e|))$ and names the per-edge intersection.
  - H2 reports a log–log slope of `\resCheckerSlope` (1.5), "grows faster than the number of edges", and proposes the fix. The checker study is not rerun, which is disclosed in A3.
  - One nuance: see m-b below.
- **(f) M6.**
  - Sec. V-A states that the tag "did not freeze the trace generator and experiment driver, which were committed about ninety seconds after the tag … the templates … were therefore authored with knowledge of the scorer". I verified 96 s (07:56:30 → 07:58:06).
  - Table III has an Outcome column. H6 is "inconclusive (rule met trivially) / supported for the scripted law", with an explicit deviation paragraph.
  - Sec. V-C states that A2 and A3 "were written after the results were known".
- **(g) M7.**
  - H5 now says "In the sandbox, selection was degenerate … the choice of $t=0.1$ is a tie-break by name".
  - The tie-break by name is in the selection rule itself (Sec. IV-D).
  - The answer to RQ2 says "the escalation theory was not exercised there".
  - The budget counterfactual appears in Sec. V-F; accepted conditional risk is retained.
- **(h) M8.**
  - Sec. V-B discloses that calibration uses `baselines.decide` while held-out decisions come from `GuardRuntime`, and reports `\resCalEquivDisagree`/`\resCalEquivCompared` (0/18,000).
  - A Containment lemma was added (Lemma 2), and premise P5 is restated in terms of it.
  - Sec. IV-D states that the fingerprint "does not hash code, so a code change without a version change goes unnoticed".
  - Table IX: "checked by replay, not by shared code".
  - Calibrating through the runtime would be cleaner. The replay covers the exploratory calibration split at the *selected* threshold only, which is sufficient for Lemma 2 as applied.
- **(i) M9.**
  - Sec. VI-D now lists exactly the three changes I requested (benign issue-derived actions, a raw-text judge that benefits from text, paraphrases) as what "would already make the semantic trade-off observable".
  - None was run. Because of N1, the first item is also mis-stated.
- **(j) M10.**
  - The metric is renamed "wall-clock time" and the column "Time".
  - Sec. V-F: "The comparison is asymmetric: TINT's timed region includes computing the action view and recomputing the SHA-256 fingerprint, whereas the comparators' view is computed before their timer starts; logging was disabled."
- **(k) M11.**
  - `verify-results` now passes (§2).
  - `scripts/manifest.py:digest` normalizes CRLF→LF for source suffixes.
  - `.gitattributes` pins `eol=lf` for sources and `-text` for JSON/CSV/GZ, so data bytes are platform-independent (verified: all JSON are `i/crlf w/crlf attr/-text`, identical in every checkout).
  - None of this is committed (see §2).

### Minor issues

| ID | Status | Justification |
|---|---|---|
| m1 "336,000 logged decisions" in abstract | Resolved | The abstract now gives "seven trace families and ten seeds per study" and no decision count. |
| m2 "executed no hard violation" in replay | Partly resolved | H1 still says "the pipelines with a gate … executed no hard violation". The replay calls `rt.evaluate`, not `Sandbox.call`, so nothing is executed. Use "accepted". |
| m3 Audit: complete mediation | Not resolved | Table IX still says "only route to an effect is `Sandbox.call` … by construction". It should add that the 336,000 replayed decisions bypass `Sandbox.call`/`parse_tool_call`, which only the canonical and unit tests exercise. |
| m4 CPU label; p95 vs. median | Partly resolved | The label is fixed. Table VII still reports p95 while the text compares medians. The caption says so, which is acceptable. |
| m5 Alg. 1 line 2 wording | Resolved | Now "reject unless $M=\mathcal R=\{\dots\}$". |
| m6 H2 mutations only on `edges[0]` of homogeneous specs | Partly resolved | The three unmutated reject conditions are now listed (accurate: `missing_evidence` empties $E$ and so triggers $O_j\not\subseteq E$, not $E\not\subseteq$ provides). Single-edge mutation of homogeneous specs is still not stated. |
| m7 H3 rule lenient; `target_covered`=1000/1000 by grid design | Not resolved | Not mentioned. Instead a new sentence compares sandbox bounds with the population risk, which is fine. |
| m8 $\hat A_{12}$ unpaired | Not resolved | Not mentioned. Minor. |
| m9 "seventeen times" conditional | Resolved | Now "passes an attack with conditional probability $0.006$". |
| m10 "Every result number in this paper is a macro" | Not resolved | The sentence remains (Sec. V-B, end). Typed values remain in prose: "56 tests", "all $64$ combinations", "fifty cells", "about ninety seconds", "$0.007$", "seventeen". The macro `\resFormalStates` was replaced by a typed `$64$`. `verify_numbers.py` (still uncommitted) exempts integers. Either qualify the sentence ("every value measured by the experiment driver") or macro-ise. |
| m11 "iterative DFS" comment | Not resolved | `src/tint/spec/__init__.py:103` unchanged. Cosmetic. |
| m12 A2 post hoc | Resolved | Sec. V-C, Environment and protocol. |
| m13 Production deletion also blocked by environment check | Resolved | H1: "the runtime additionally blocks production actions in the sandbox deployment through its environment check". |
| m14 Regeneration prerequisites | Not resolved | Data Availability still says "a complete regeneration in a few minutes on a laptop CPU" without naming PRISM, Java and TeX (named in `ARTIFACT.md`). The stale "five seconds" claim was removed. |

---

## 2. Artifact re-check

### Commands (repository root, Python 3.13, Windows 11)

| Command | Outcome | Excerpt |
|---|---|---|
| `python scripts/tasks.py smoke` | **PASS** (exit 0) | `56 passed in 2.98s` … `Smoke elapsed: 13.15s` |
| `python scripts/tasks.py verify-results` | **PASS** (exit 0) | `Processed summary re-derived byte-for-byte from both preserved raw runs.` / `primary 168000 … match` / `exploratory 168000 … match` / `Post-review analysis re-derived byte-for-byte.` / `78 source/config/raw/processed hashes match manifest.` |

`git status --short` was identical before and after both commands.

**Blocking artifact caveat: the revision is not committed.**
- `git status` shows `?? scripts/post_review_analysis.py`, `?? results/processed/post_review.json`, and ` M` for `results/manifest.json`, `scripts/manifest.py`, `scripts/tasks.py`, `scripts/make_macros.py`, `scripts/verify_numbers.py`, `paper/main.tex` and `ARTIFACT.md`.
- `results/manifest.json` records `analysis_commit` = `50a3180`, but the files it hashes are the uncommitted working-tree versions.
- A clone of the public repository (whose URL now appears in Data Availability) would get HEAD `50a3180`. At HEAD, A3 is absent, and the committed manifest still stores a CRLF hash for `scripts/make_macros.py` while `.gitattributes` forces LF. HEAD therefore still fails `verify-results` on any fresh checkout.
- The pass I observed holds only for this working tree. Commit, tag (e.g. `revision-1`), and re-run `verify-results` from a fresh clone, ideally inside the Dockerfile on Linux.
- Minor gap: `tests/` is still not covered by the manifest (`scripts/manifest.py:files`, directories list).

### Spot-check of new numbers

| Paper value | Source | Source value | Independent check | Match |
|---|---|---|---|---|
| B7 primary risk 0.00, utility 66.41, cost 1.00 | `post_review.json` → `provenance_control/primary/test` | `unsafe_allowed` 0/12000; `benign_allowed` 3592/5409 = 0.664078 | 3592 equals `\resFamilyBenignPrimary` (B7 accepts exactly the benign reports) | ✓ |
| B7 exploratory risk 0.00, utility 66.46 | `…/exploratory/test` | 0/12000; 3580/5387 = 0.664563 | matches my round-1 recomputation with the repository's own functions; 3580 = `\resFamilyBenignExploratory` | ✓ |
| B7 shift risk 0.00 (both) | `…/shift/joint_risk` | 0.0 (n = 6000 each) | round-1 recomputation: encoded family 0% | ✓ |
| Calibration equivalence 0 of 18,000 | `calibration_equivalence/exploratory` | compared 18000, disagreements 0 | 18,000 = 10 seeds × 1800 calibration traces; the script (`post_review_analysis.py:53-75`) compares `GuardRuntime.evaluate` with `decide('checked_quarantine', …)` at each seed's selected threshold | ✓ (scope: exploratory, selected threshold only) |
| Checker slope 1.5 | `make_macros.py:154-159` over `summary.json` → `studies/primary/checker/scalability`, policies ≥ 50 | 1.4971 | my own `numpy.polyfit` of log median time vs. log edges gives 1.4971 | ✓ (see m-b) |
| Budget counterfactual "at least 35.0%" | `\resPrimaryBoundMax` → `primary/selections/*/bounds#max-of-min` | 34.999 | all 11 thresholds share one bound per seed, so every seed certifies once $\varepsilon\ge$ its bound, and all do at $\varepsilon\ge34.999\%$ | ✓ |
| Preregistration gap "about ninety seconds" | `git log` | a48fca6 07:56:30, c47f2a4 07:58:06 | 96 s | ✓ (typed literal; m10) |
| Exploratory bounds 10.7–13.3% above population risk 10.00% | `exploratory/selections/*/upper_risk`; `analytic population` | 0.1072–0.1330; 0.10 | — | ✓ |

No numeric discrepancy was found. Macro provenance records the correct source file and hash for the post-review macros (`paper/generated/macro_provenance.json`: `resPrimaryProvUtility` → `results/processed/post_review.json`, sha256 `486bcff9…`).

---

## 3. New errors or overclaims introduced by the revision

### N1 (major, factual). "The law contains no benign issue-derived action" is false.

**Where it appears.**
- Sec. V-C, Substrate: "the law contains no benign issue-derived action".
- Sec. V-F, B7 paragraph: "our fixture law contains no benign action derived from the issue, so provenance alone separates safe from unsafe … A law with benign issue-derived patches … would make B7 block useful work".
- Threats, external validity: "without benign issue-derived actions".
- A3 in `AMENDMENTS.md:17`: "no benign issue-derived action exists".

**Why it is false.** The *benign security text* family is exactly a benign issue-derived patch:
- Table V: "`patch` security guide, issue input", $Y=0$;
- `experiments/dataset.py:22-24`: `Action(ActionKind.PATCH,'security-guide.md',('issue',))`, with `unsafe=False` for `benign_security`.

**What actually happens.**
- B7 already blocks this family and loses 15% of the mixture: its utility is 66.46%, against 100% for B1.
- B7 ties TINT on utility only because TINT's scorer/judge **also** false-blocks that family ($c=6$, $s=0.76$).
- So the accurate statement is not "provenance alone separates safe from unsafe". It is: "provenance blocks the one benign issue-derived family, but so does every scorer-based pipeline, so the semantic layers recover none of that utility."
- This is a *stronger* negative for the semantic layers than the paper currently states. They lose to B7 on risk and fail to beat it on the one family where they were supposed to add value.

**Fix.**
1. Correct all four sentences.
2. Make the Discussion's first proposed change in Sec. VI-D precise: "benign issue-derived actions *that a semantic judge can accept*".
3. Drop the conditional "would make B7 block useful work"; it already does.

I acknowledge that my round-1 wording ("lacks benign issue-derived patches") introduced this imprecision.

### N2 (moderate). The abstract now under-reports the negative results.

The abstract's empirical sentence is now only "A preregistered study … validated the designed behaviors and exposed their limits." It no longer mentions that:
- the primary run certified nothing;
- a post hoc provenance rule dominated TINT;
- every pipeline except B7 failed under shift.

The round-1 abstract overclaimed; the revised one is so vague that a reader of the abstract alone cannot learn the main findings. Suggested final sentence:

> "In the frozen primary run no policy could be certified, because of a scorer defect; after the fix, the structured view removed the one judge-targeting family, but a post hoc provenance rule outperformed TINT and every other pipeline failed on an unseen encoded family, showing that the sandbox validates designed behaviour without exercising the semantic layers."

### N3 (minor). Anonymization is inconsistent.

The byline is "Author Names Withheld", but Data Availability now gives `https://github.com/ai4se4ai-lab/trust-is-not-transitive`, which identifies the lab. Either remove the URL for review (use an anonymized mirror) or drop the withheld byline. Check the TSE review mode.

### Other loose phrasings

- **m-a.** Sec. VI-A, Lessons: "Measuring joint risk of the whole pipeline on labeled data before deployment is what caught the defect in our primary run." Sec. V-F correctly says the authors caught it by reading counts after the gate refused. Suggest "is what stopped the defective pipeline from deploying".
- **m-b.** The checker slope of 1.5 pools depths 2–6, mixing the factor that is linear in layers with the factor that is quadratic in properties. Within each depth, the slope against properties is 1.69–1.73 (my `polyfit` per depth), consistent with the $O(E\cdot|P|)$ cost the paper itself derives. Report the per-depth slope, or say that the pooled fit understates the growth in properties.
- **m-c.** Fig. 6 (routes) types population percentages (75%, 40%, 35%, 25%) directly into TikZ rather than deriving them from the family-mass macros. They are correct (15+10; 30+10; 15+10+10), but this is another exception to m10.
- **m-d.** Lemma 2 is applied using a replay on finite samples at one threshold. Sec. V-B's "Lemma 2 needs the two to agree" is correctly hedged in Table IX ("checked by replay, not by shared code"). For a decision function over 8 templates, replay is effectively exhaustive. Say so: agreement on every family implies containment on the whole support of $D$.

I checked the theory rewrite and found no new problems:
- Definition 2 (obligations with kinds), Lemma 1 (checked and realized edges), Lemma 2 (containment) and P1–P5 are internally consistent.
- The counterexample for Prop. 3(d) is correct ($R=0.1$, $\Pr(M_3)=0$).
- The Fréchet–Hoeffding and Bernstein attributions are appropriate.
- The new Table II (obligation kinds) is a genuine improvement in clarity.

---

## 4. Re-scored criteria and recommendation

| Criterion | Round 1 | Round 2 | Justification |
|---|---|---|---|
| i) Novelty | 3 | 3 | Unchanged. Obligation kinds (checked / by construction / assumed) and the LlamaFirewall walk-through (Sec. VI-C) sharpen the contribution, but the conceptual core remains close to the position paper and the CaMeL/Fides line. |
| ii) Rigor | 2 | **3** | The overclaims are gone, the negative results lead, the H1 evidence and complexity statements are accurate, the post hoc comparator that beats the method is reported, and the preregistration deviations are explicit. Still capped by M9 and N1: no experiment exercises the semantic layers, certification or non-degenerate selection, and the B7 explanation is factually wrong. |
| iii) Relevance | 4 | 4 | Unchanged. |
| iv) Verifiability & Transparency | 3 | **4** | `smoke` and `verify-results` both pass. The new analyses are byte-re-derivable with per-macro provenance, line-ending handling is principled, and A3 is documented. Not 5, because the passing state is uncommitted and HEAD still fails on a fresh clone; m10 also remains. |
| v) Presentation | 4 | 4 | Clearer theory and evaluation framing. The abstract is now too vague (N2), and the "issue-derived" sentences need correction. |

**Recommendation: Major revision**, narrowly. The manuscript is close to acceptable as a scoped "executable discipline + feasibility" paper.

**Blocking items:**
1. **M9 / N1: one cheap experiment.** No LLM is needed. Add to the fixture law a benign issue-derived patch family that the structured-view judge can accept but B7 must block (e.g., an authorized README fix requested in the issue, with low lexical score). Add a raw-text judge that correctly accepts benign security text. Add a few paraphrases per family. Without this, RQ3 compares mechanisms that, as the paper itself states, the sandbox "could not exercise". Correct the four false "no benign issue-derived action" sentences either way.
2. **Commit and tag the revision** (manifest, A3 script and output, `.gitattributes`-consistent hashes) and confirm `verify-results` from a fresh clone, preferably in Docker on Linux.
3. **Rewrite the abstract's empirical sentence** to state the main negative findings (N2).

If the authors decline item 1, I would accept the paper only with RQ3 retitled and scoped as "validation of designed behaviour" throughout, and with the contribution list no longer claiming an evaluation of the escalation/certification machinery in the sandbox. Under that option I would move to minor revision.
