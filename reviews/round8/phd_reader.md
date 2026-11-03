# Round 8: comprehension review by a non-specialist PhD reader

Reader profile: second-year SE PhD student. I know testing, basic program analysis and basic probability, and I have used LLM coding agents. I have no background in contracts, dataflow theory or conformal statistics.

Method: I read `paper/main.tex` once, in order, from `\begin{document}` to the end. I skimmed `paper/main.pdf` for figures and rendered tables and read no other file. Line numbers refer to `main.tex`. Where a problem may be a real inconsistency and not just my confusion, I mark it **[possible error]**. I cannot settle those without the code, so the author should check them.

Overall verdict. The paper is short, honest and well organised. I followed the intuition of Sections 1 to 3 and the shape of the main theorems. I lost the thread in three places:
- what an obligation like `miss_rate_bounded` means inside a per-proposal semantics;
- how the exact safety story connects to the statistical story;
- why DevAgent needs both switch `s` and gate `c`.

The last of these is the paper's central lesson, and it is never stated.

---

## Part 1. Section-by-section notes

### Abstract (l.581)

- Mostly clear. On first read I could not place "credited gate", "routing switches" or "discharges". The sentence "complete relative to contracts and freely behaving stages" means nothing yet, but the follow-up "an accepted hierarchy ... a rejected one ..." rescues it.
- Read twice: "a rejected one has an execution in which every stage keeps its contract and a violating action is accepted". The word "accepted" is doing two jobs in one sentence, one for hierarchies and one for actions (see the global issue G1).
- The last sentence ("for which that list of assumptions is the main result") is surprisingly modest after all those theorems. I liked it, but I went into the body not knowing how seriously to take the graph machinery.

### 1. Introduction (l.593-616)

- **Terms used before they are introduced.** "the judge" and "the scorer" appear in the list of engineer's questions (l.595) with a definite article, before anything has named them. The DevAgent paragraph (l.597) describes gates and a goal, and it also never says that DevAgent has a judge or a scorer. Then "`T_j` ... addressed to the judge" and "Suppose the judge reads the raw issue". I had to infer that an LLM check is called the judge.
- **"Trace" versus "proposal".** The introduction uses traces. Section 3 uses proposals without defining them. I do not know whether a proposal is one tool call or a whole trace. I assume one action.
- **The traces.** "its action has the same shape" (T_b) puzzled me. Same shape in what sense? They later diverge at a deterministic gate because of labels, so the shape is evidently not what the gate looks at. The point of T_b is never stated. I guess it is "structure alone cannot separate benign from malicious", but this is a guess. Also T* and T_j are stopped by a deterministic rule, so only T_jp matters for the argument. It would help to say so.
- **The key paragraph (l.599) is good.** "Every component met its contract ... and yet the stack accepted an unsafe action" is the sentence I remembered best. I did read it twice, though: the contract is met *because* its assumption was false, and that is an unusual idea for a tester. A one-clause gloss would help: "a contract with a false assumption cannot be broken".
- **Nothing here is transitive.** The example has one judge with one false assumption. The title's claim of a chain of trust does not appear in the example.
- "Compositional reasoning excludes this step" (l.599): which step? I had to look back to "relied on".
- The gap paragraph and Contributions are fine. "flow of facts" and "correlated conditions" in contribution 2 are opaque at this point, which is acceptable in a contributions list.

### 2. Background (l.623-631)

- Useful but very compressed. It tells me what things are called, not why I need them.
- **Contracts.** "sound only when every assumption is established by the environment or by another component's guarantee": this is the crucial sentence and it is buried. I also do not know what "environment" is here. Is the deployer the environment?
- **Dataflow.** "distributive transfer functions", "meet over all paths". I remember must-analysis from a course, so it was OK. Without that course this paragraph would not teach anything.
- **Statistics.** Clopper-Pearson is named but not explained in words, and "exchangeable" is unexplained. There is no sentence saying "you may treat this as a function that takes N and k and returns a number p such that the true rate is below p with confidence 1-delta". That one sentence is what I needed. `conformal` is used repeatedly in the paper as a known term and never explained.
- There is no background on what soundness and completeness mean for a *checker* versus a *logic*, and that is the frame of the whole paper.
- There is no statement of the threat model. Attackers appear in prose only.

### 3. Calculus (l.640-745)

**Syntax.**
- "layer" is defined as "the interface of a learned or human component". So far the words have been guard, stage, guardrail and component. What is the difference between a layer, a stage, a node and a guard? I settled on: a layer is a contract (requires + scope) and a node is a use of it. The paper never says this.
- "obligation" is defined only as "a set of obligation names". There is no example at the moment of definition. It took me until the listing to see that an obligation is a named claim like `config_match`.
- "the evidence, the obligations the deployment supplies for this one invocation". Supplies how? Is it a data object, a test result, or a line in a config file? I initially thought it was data passed at runtime. I only learned in Section 4 that it is a *declaration*. This misled me for several pages.
- A gate "provides the facts D, which are obligations that hold from then on". So facts are obligations too. OK, but now I hold four sets of the same type: req, Omega, D/F/B and E(n). See "Notation" below.
- "a stack with no such stage is modelled with a final guard of empty scope that releases what reaches it" (l.647): I read this three times. Why is empty scope OK? Only after `ok` did I see the guard then needs all goals already established.
- Why can a gate establish things and a guard not? I understand *that* escalation carries nothing. The paper does not say *why* a guard's acceptance or escalation should not count while a veto stage's pass does. My guess is that a pass from a veto stage is a promise about the proposal, whereas escalating is an admission of not knowing.

**Semantics.**
- "We do not model what a stage computes. We model what could happen." Very good sentence.
- "model" has been a word for LLMs up to here. `M` is a logical model, which I only realised after a paragraph (G2).
- "free" and "These components are free": I took this to mean "arbitrary", but the phrase "stages are independent of each other unless a contract relates them" sounds statistical to me, and I wondered if it was a probabilistic assumption. It is not (I think).
- The attacker is not in the semantics. Nowhere does the paper say "an attack is a model in which an obligation fails". I had to construct this for myself, and I am not sure it is right.
- **Fig. 1, gate rule.** It reads, as printed, `P(n) => R(n) AND if req ⊆ E(n): ... otherwise ...`. I could not tell whether the `P(n) =>` scopes over the whole rest or only `R(n)`. If only `R(n)`, a gate that *denies* would still have to satisfy `φ ∈ S`, which makes no sense. The caption's "All premises concern only the invocations this proposal reaches" apparently resolves this, but I had to guess. **[possible error in typesetting/parenthesisation]**
- **Conditional requirement vs. checker requirement.** The semantic test is `req ⊆ E(n)`, what is true. The checker test is `req ⊆ Ω∪B`, what is declared. This difference is the heart of the paper and it is not called out anywhere. A gate may in fact have its contract apply while being uncredited. I only noticed this inside the Soundness proof.
- The paragraph with Realization, Conditionality and Locality is the best in the section. I would like it before the figure. "A verdict of esc asks nothing of a guard and adds nothing to F" is clear.
- **What does an obligation at an invocation mean?** `E(n)` is "the set of obligations that actually hold on invocation n". But the running obligations are `miss_rate_bounded` and `config_match`. A miss rate is a property of a population, not of one invocation of one proposal. I could not make sense of "`miss_rate_bounded` holds on this invocation but not that one", and this confusion stayed to the end.
- Definition of safety: "safe from (A,B)" is fine once I saw that A and B are just "what is already known". `A ⊆ S` needs a moment.

**Table I (l.688).** It appears before risk, certificate and drift exist. The text says the terms are defined in Section 5, but **η is not defined there or anywhere**. It appears only in this table and in Table IV ("a shift of size η adds at most η"). Size in what measure? "complete mediation" is also not defined as a phrase. I could not fully read this table on first pass, and I do not think it belongs here.

**HSL (l.707).**
- "An obligation may be tied to a view. Evidence tied to another view than the stage's layer is dropped before analysis, with a warning." **"view" has not been defined**, and the calculus syntax has no views. I did not understand this sentence, and I still do not understand when one would tie an obligation to a view. A view is finally explained around Theorem 8, 200 lines later.
- The three kinds (checked, construction, assumed) are clear.

**Fig. 2 and Listing 1.**
- The figure is clear and I used it constantly. I looked back at it about ten times.
- Node names are irregular: `g1 g2 g3 s v2 n4 c n3`. Where are `v1`, `n1`, `n2`? I wondered if they had been cut.
- Gate `c` "provides robustness", while the listing says it provides `contract_holds_on_adversarial_text`. I took a moment to link these.
- The listing has `"establishes": null`, but the calculus has `gate(n, φ, ...)` with a mandatory φ. What does a null goal map to?
- **[possible error]** In the listing, layer `L3` requires only `miss_rate_bounded` and `config_match`. The fact provided by `c`, `contract_holds_on_adversarial_text`, is therefore required by nobody in the shown fragment. So why does `c` exist? Section 6 explains the adversarial reading, but at this point the listing contradicts the caption's story.
- **The biggest gap, for me.** Switch `s` tests "tainted?". Then gate `c` tests "no untrusted input". The two appear to do the same thing. Why does the "no" arm need a gate that re-tests what the switch just tested? I suspect the answer is the deep point of the paper: *a switch is free, so taking a branch gives the checker no knowledge; only a gate creates a fact*. The paper never says this. I reconstructed it around Section 4.E and I am not fully sure of it.

### 4. Verifying a Hierarchy (l.752-934)

**4.A Composition condition.**
- Good opening sentence. The `check` equations in the PDF are readable, though the gate case with the "with"/"if"/"else" broken across lines needed careful parsing.
- `ok(ℓ,e,A)` has parameter `e` for evidence, called with `Ω∪B`. So the "evidence" of `ok` is not the "evidence" Ω of the syntax. Small, but I looked back.
- `check` at a guard requires `ok` *and* checks the continuation, even if the guard may accept. Clear after a moment.
- **No running example here, and this is where one is needed.** A six-line walk of `check` on DevAgent, showing A and B at each node, would have taught me the whole mechanism. Instead the walk appears only as a result in Section 6.

**Soundness (Thm 1).** I followed the structure. I could not follow, on first reading, *why* there is an F distinct from B. The step "If it is not credited, (A,B) is unchanged, and the hypothesis applies with F or F∪D, whichever the contract gives, since B is contained in both" took a long time. It exists because the checker's credit and the semantics' condition can differ. A sentence stating that would have saved me. F = facts truly provided at runtime; B = facts the checker can count on; B ⊆ F.

**Completeness (Thm 2).** Followable, and the more satisfying proof. I had to stop at:
- "let every obligation hold at n; the contract asks for φ ∈ S, which holds because A' ⊆ S in the witness". This is fine once you recall that A' includes φ.
- "Let S be everything but ψ": everything including non-goals? Section 8 confirms it but it is odd here.
- The Frame lemma's role: I understand why uniqueness is needed only from the sentence before the lemma, which is nicely stated.

**After the theorem (l.797).** "A rejected hierarchy may be fine for the guards actually deployed": good. "Declaring an assumption as supplied evidence silences the rejection, by design" is the moment I finally understood evidence. It should come 150 lines earlier. Until here I worried that the theory is empty, since anyone can write down anything. Now I see that it *is* empty unless someone answers for the list, and that this is the honest position.

**Residual (l.799).**
- "the set of (stage, assumed obligation) pairs supplied at a stage that some goal depends on". "depends on" is undefined, and `assumed` requires recalling the kinds. I read this three times.
- Does removal testing handle two redundant entries? If A and B each suffice, removing either alone keeps acceptance, so both look unnecessary, while removing both fails. The Corollary is one-directional so it is not false, but the conclusion's "each tested for necessity" made me think that the list marks what is needed. I do not know what happens in this case.

**4.C Transitive reasoning.**
- "L1 trusts L2, L2 trusts L3, and each was shown sound": what is the formal counterpart? `check*` adds Ω to B "at every stage". It is a nice tiny definition.
- Part (a) surprised me as a *theorem about unsoundness*: it says `check*` accepts more. Why do I care? It only sets up that (b) is strict. One sentence would help: "the transitive rule accepts everything ours does and more".
- Proof (b) says "a goal in the scope of both"; I think it must be the only goal, or `check*` would not accept.
- **Broken callback:** "The instance in the proof is the judge of the introduction: a sanitized input to the scorer says nothing about what the judge reads." The introduction says nothing about a sanitized input or a scorer's input. I went back and looked. The example that would make this theorem vivid does not exist in the text.
- **Is this a result or a definition?** Locality says E is indexed by node, by definition. So of course evidence at n1 says nothing about n2. I could not tell whether Theorem 3 is a discovery or an immediate consequence of the modelling choice. I think the honest content is: "if you model evidence per invocation then chaining is unsound, and here is why per-invocation is the right model: each stage reads a different input". The justification for per-invocation modelling is not given explicitly.

**4.D Order.**
- "`ok` is antitone in its goals and evidence (Lemma 2)": Lemma 2(a) says that bigger sets preserve `ok`, which is monotone. **[possible error]** Unless "antitone" means something else here, it is the wrong word. I lost several minutes on it, thinking I had misread the lemma.
- There is no intuition for why gates go first. I worked out: a guard that accepts ends the decision, so a gate after it does not protect that route. That one sentence belongs next to the theorem. There is also no example of DevAgent.
- "preserves acceptance": of the hierarchy by the checker, not of proposals. See G1. I first read it the wrong way.
- "put gates first" conflicts with my mental picture of DevAgent, where `c` is after a switch. Fine, but only `c` needs that.

**4.E Algorithm and complexity.**
- Algorithm 1: line 2 initialises only the entry. Line 6 intersects into `avail(c)`, which has no initial value. I assumed "all goals", the standard top. "gate transfer" is used but never named as such in 4.A.
- Lemma 2: proof of (b) took two reads but was OK. The paragraph after it (l.869) is excellent: "One path may have every goal and no evidence, and another path the reverse" is the most illuminating sentence in the section. It is the true reason for the first-pass false alarm, but the paper does not link it to the hardness result explicitly.
- "the unfolding" is defined *after* being used at l.838 and l.707. "Entry e" reuses `e` from `ok`.
- Theorem 5 proof: "because unions distribute over intersections": read twice. I accept it. "General case" I followed. I had to look up what the "pairs" were.
- **Theorem 6.** (a) `|V|`, `|E|` and `|O|` collide with the model's V, E and with big-O. I wondered briefly whether E is the same E. (b) "coNP-complete": I know NP. I know coNP is "the complement", but I would like a phrase: "a rejection has a short certificate (a bad path), an acceptance does not". The reduction is terse. It needs a small picture or a two-variable instance. The phrase "the facts falsifying its literals" took three reads. Once I wrote it out with x, y and one clause it was neat, and I think a reader who does not write it out will just skip it.
- l.894: "one can treat each (open goal, missing obligation) pair as a single fact in a must-analysis, which is polynomial". I could not reconstruct this. Is DevAgent in this polynomial middle case? (`c` provides a fact and only a guard consumes it.) It looks like it, and the paper does not say so.
- Proposition 1 ("Correlated conditions") proof: the hardness sketch "use one switch per clause, on literals" is too short. A clause has several literals, so how does one switch handle it? I could not follow this. The incompleteness example I followed by drawing it.
- "A second source of hardness lies outside the calculus": I read this as a limitation of the model and got confused why it is a hardness result. It concerns a richer problem that the paper does not solve.

**4.F Structural properties.**
- Theorem 7 is a grab-bag. Monotonicity, Routes and Prefix locality are used later. **Budget and Taint come from nowhere**: there is no cost, no budget, no label in the calculus. I did not know why they are here. "Budget" also collides with the risk budget ε later. "gate that accepts cost c" is a term I could not place.
- The Monotonicity premise `V'(n)=esc ⇒ V(n) ∈ {esc,acc}` needs a gloss, for example: "M' is the same as M with some stages made stricter".
- Corollary 2: uses "route" and "ancestor". This is where I realised that **a route is a guard node and not a path**: `accepted(r)`, "r is a guard". The word "route" made me picture a path until very late, and "every path to r" in Section 5 then seemed contradictory.
- Theorem 8 and the paragraph after it are excellent, a real insight, and the first time "view" makes sense.
- **[possible error / confusion]** The paragraph says a judge on the structured view "cannot decide φ3 on a patch" because malicious and benign patches may have equal views. Yet Fig. 2 labels the human `n4` as "structured", and tainted input goes to that person. By the same theorem, how can the person decide φ3? Maybe the person sees more than the view; "human_sees_provenance" suggests it. The paper does not address this and it undercuts the design resolution in the very paragraph.

### 5. From Safety to Risk (l.941-992)

- **"Learned stages do not meet exact contracts."** This opening jolted me. For two sections the guards' contracts have been exact. Are the DevAgent acceptance and the proofs about it then not about the real system? I never got a clear statement of how to read the exact check for a statistical stage. My best guess: the exact theory is a *pretend-exact* reading in which a statistical guard is treated as if it met its scope, and the error is accounted for separately on routes. Is `miss_rate_bounded` true when a bound exists? What does "contract holds" mean when it misses 1%? This is the largest conceptual hole for me.
- "`Φ = Φ_d ⊎ Φ_s` into hard and statistical goals": who splits them, and by what criterion? "hard" is not defined. Then "A route r is hard if deterministic gates establish every goal of `Φ_s`": so a hard route is about the *statistical* goals. Then "a hard route may still have a goal of `Φ_d` covered by a guard's exact contract": what is a guard's exact contract, if learned stages do not meet exact ones? And "fully gated" is a third category. I needed a table. I read this paragraph four times.
- `R` was realization in Fig. 1, and is now risk. `D` was the set of facts, and is now the distribution.
- Theorem 9: statement OK. Proof: I lost it at "Let `H_d` be H with goals `Φ_d`, every scope intersected ... With goals restricted, ok is implied at each guard by its value in H". I accept but could not verify. Premise (ii) "realization holds": this includes realization of `miss_rate_bounded`? See the population/invocation problem.
- "No statistical contract, independence assumption or per-layer rate appears here": good, but its importance is lost. I think the point is "you need not multiply layer rates", which is a strong and practical message. Say that.
- Proposition 2: "guards" are in a veto chain, though veto stages are gates. Fréchet-Hoeffding is unknown to me. I accepted the statement. Part (b) is a nice example.
- l.965 "Note what the composition check does not do here" is an important paragraph. "a certificate for a raw-text judge is valid under D whether or not the check accepts the hierarchy": I read this twice. Then what does the check buy for statistical goals? The three items are given, and the third ("by rejecting, the warning") is the clearest statement of what the rejection means. I would put this at the start of Section 5.
- **Route certificates.** The tuple has "context" `c`, never mentioned again. Is it the training context? The configuration? Equation (1): I treat Beta⁻¹ as a black box. "with certificates ignored" read twice (it means "gate off, so all routes are measured").
- "closed" is defined, "open" is not defined explicitly. "confidence share" is intelligible only from the formula.
- Theorem 10: good. **[possible gap]** Table IV lists "Stateless prefix" as needed by Theorem 10, but the theorem's statement does not mention it, and "ledger" has not appeared. Is this hidden in "fix a configuration"?
- Does `miss_rate_bounded` get discharged by a certificate? Table III suggests so ("calibration"). This link is never stated, and it is the bridge between Sections 3 to 4 and Section 5.
- Prevalence paragraph (l.986): the most striking practical point in the paper: a guard that misses every attack passes the budget. I would have liked a more prominent treatment. Is the joint measure then even the right one? The paper keeps using it.
- No DevAgent: which routes are in Q? Is n4 (a human route) calibrated too? A certificate for a person's decisions sounds odd and is never shown. No numeric certificate is worked for `n3`.
- Recertification: fingerprint paragraph is dense and Python-specific ("closure values, defaults, partial arguments"). I skimmed it. "The cost is a tighter guarantee foregone" read twice.

### 6. Worked Example (l.999-1012)

- This is the section that made the rest make sense. It should come earlier, or be split up across earlier sections. It opens by forward-referencing Section 7 for the adversarial reading, so the example depends on a rule I haven't read.
- "under the adversarial reading": threat model is new as a formal notion. It turns out a threat model is *just an added obligation*. Very clean and never stated this way.
- "Checking": the residual has one entry `miss_rate_bounded` at n3. What about `v2`? It is a raw-text stage on tainted input and so needs the adversarial claim under the rule. I infer that `v2` is uncredited and nothing depends on it, so the checker ignores it. So the **scorer contributes nothing to the composition**. Then why is it there? The paper doesn't say. And doesn't n4 need `miss_rate_bounded`, as a guard? Presumably it is human, and Table III lists different obligations, but the worked example is silent.
- **[possible error]** The exposed variant. "Now remove gate c, so that all input reaches the judge." But `s` stays, and in Fig. 2 tainted input goes to `v2`. So *not* all input reaches the judge: only input on the "no" arm does. The witness path is `g1 g2 g3 s n3`, "s takes the untainted branch". And then "This is T_jp reconstructed mechanically". But earlier in the same section "On T_jp the patch is tainted" and takes the human arm. So how can an untainted-branch run be T_jp? The only reading that works: the switch is free, so the model may send attacker text down the "no" arm, and only gate `c` could rule that out. If that is the point, it is the deepest idea in the paper, and it should be said in those words. As written, it reads as a contradiction, and I am not certain that my reading is correct.
- "Change": clear and useful. "Placing rules after the split would not help either, since Theorem 4 favors them first": read twice, not sure I understand. Would it not reduce staleness? Theorem 4 says a gate-first order is at least as good for checking, not that later placement fails.
- `config_match` is mentioned as being "checked at runtime" but I never learned what configuration it matches.

### 7. Using the Approach (l.1021-1101)

- Readable and useful for me as an engineer. "CodeShield" is unexplained, but fine.
- The second rule, "An obligation that the input is clean makes no sense for a detector of unclean input", is great. It should appear near the definition of an obligation.
- `miss_rate_bounded`, "supplied only if a bound is available": so it is an obligation only in a declarative sense, confirming my reading that Ω is a config statement. Still population-level.
- Table III "Discharged by" vs Table IV "How to discharge": the word "discharge" is used without definition. Abstract says "discharges a later stage's assumption", §8 "discharged by SMT solvers".
- Table IV is great, the single most useful page for a sceptical reader. New terms appear here for the first time: "Stateless prefix", "ledger-reading gate", "labels independent of the guards".
- "Rail frameworks", "reask": framework jargon, unexplained. "reask" is OK from the context.

### 8. Mechanized Proofs (l.1108-1114)

- Readable for a tester, because mutants are familiar. "obligation" now means **proof obligation**. In §10 "66 obligations" is about proofs, in §6 obligations are contract claims. This caught me out more than once (G1).
- Third paragraph (l.1112), "Goals and obligations share one sort ... S is not constrained": I could not see why I needed to know this.
- "What is trusted" is admirably clear.
- "union unfolded to its definition": opaque, skipped.

### 9. Implementation (l.1121-1123)

No problems. Section is short. "fails closed" fine.

### 10. Evaluation (l.1151-1307)

- The first paragraph is a wall, but it is well argued.
- Experiment IDs are out of numeric order within RQ1 (E1, E2, E14, E12, E12b). Trivial, but I kept checking Table VI.
- **Statistics jargon:** "laws", "coverage", "simultaneous route coverage", "Wilson limit", "Monte Carlo error", "nominal". Coverage is never defined. I inferred: in repeated calibration, how often the bound truly holds. "laws" threw me: I thought of legal or algebraic laws, and "known laws" in Table VI ambiguously suggests that too.
- E12 paragraph is hard: "this is within Monte Carlo error but failed the protocol's literal rule. E12b is the test that matters." So what is E12 for?
- E5: complex accounting (68 + 163 + 114 + survivors) that I could follow only slowly, and it is honest. A small table would be easier.
- E9 is good. "These limits are of interest mainly as bounds on continuous-integration cost" is honest.
- E15 and E13: these were the most interesting for me. "rails", "flows" are NeMo's terms. "leave a goal open" OK. E15 conclusion is the real pay-off, and the paper is brave here.
- Table of cases: I could not interpret entries without §7's two uniform obligations. OK since §7 is read already.
- §10.F "Failures" is unusually candid and I respect it, but "An earlier preregistered scripted study of one fixed pipeline" (l.1296) has no context. What pipeline? What "primary seeds"? "certification changed no decision". I could not reconstruct what happened, nor what I should conclude, except the last sentence.

### 11. Related work and 12. Conclusion

- Related work is fine as a reference. Table IX: "Exact: a completeness result" helps.
- Conclusion is a good summary, but it is the first place where I see all the pieces together, and it does not say the single takeaway a practitioner should carry. "Gates belong before guards" is a slogan without the reason.

---

## Part 2. Global problems

### G1. Overloaded words

| Word | Meanings in the paper | Harm |
|---|---|---|
| accept / reject | the checker on a hierarchy; a guard on a proposal; a mutant/solver context | **high**: abstract, Thm 4, Cor 1 |
| obligation | contract claim; SMT proof obligation | **high** in §8, §10 |
| evidence | Ω; parameter `e` of `ok` (Ω∪B); statistical data for a route; the paper's own experimental support | **high** |
| model | LLM; semantic model M; threat model; design model; "model search" | **medium/high** |
| route | sounds like a path; is a guard node | **high** |
| hard | hard goal; hard route; complexity hardness | **medium** |
| guard | formal constructor; informal "any guardrail" (Prop 2, Table III, "third-party guards") | **medium** |
| budget | cost budget in Thm 7; risk budget ε; confidence budget δ | **medium** |
| stage / layer / node / component | not distinguished | **medium** |
| stack / hierarchy / pipeline / cascade / chain | partly synonyms | **low** |
| discharge | used for facts, proofs, premises | **low** |

### G2. Notation collisions I had to look back for

- `D`: provided facts of a gate; the proposal distribution; also `Pr_D`.
- `R`: realization `R(n)`; joint risk `R`; `R_r`.
- `E`: obligations at a node; graph edges in `|E|`.
- `V`: verdict; graph vertices in `|V|`.
- `O`: obligations in `|O|`; big-O in the same formula.
- `e`: evidence argument of `ok`; graph entry.
- `c`: gate in DevAgent; context in a certificate; changed stage in Cor 2; cost in Budget; successor in Alg 1; condition in Prop 1.
- `s`: switch in DevAgent; cost accumulator in Budget. `S` and `s_1`.
- `k`: continuation; number of losses `k_r`.
- `A, B, F, Ω, D, E(n), req`: all sets of the same sort, differing by who knows what. I kept a sheet: **Ω** declared per stage; **D** what a gate would provide; **F** provided on this run (truth); **B** what the checker has counted (B ⊆ F); **E(n)** what is really true at n; **req** what the stage needs; **A** goals counted so far; **S** goals truly satisfied. The paper should give me this sheet.

### G3. The missing conceptual sentences

Each of these took me pages to derive, and each could be one sentence in the paper:
1. A declaration (Ω) is not a truth; the check works on declarations and soundness is conditional on them. Soundness is relative to the deployers' honesty about Ω.
2. A switch gives the checker no knowledge. Taking the "untainted" arm proves nothing; only a gate can.
3. An attacker is not in the calculus; an attack is a model where some obligation fails at some node.
4. A threat model is expressed by which obligations layers require.
5. Evidence does not persist because each stage reads different input and is a different component; a fact does, because a gate verified it about the one fixed proposal.
6. The exact contracts of §3 to §4 are idealisations for statistical stages; the check tells you the structure, and §5 prices the error.

---

## Part 3. Closed-book explanation (written without looking back)

**Gate.** A stage that can only say stop or pass. If it passes *and* its assumptions hold, then the goal it covers is true of the proposal, and it can pass along facts. Deterministic gates have no assumptions and decide exactly. A veto classifier is also a gate, with assumptions. *Confident.*

**Guard.** A stage with three verdicts: accept (ends the whole decision), block, or escalate (hand it on). If it accepts and its assumptions hold, the goals in its scope hold. If it escalates it promises nothing. *Confident.*

**Switch.** A branch on some condition. The theory treats the branch as arbitrary, so it gives no information. *Fairly confident, but this is my inference. The paper says "routes on a condition" and "free".*

**Route.** One of the ways a proposal can get accepted. It is identified by the guard that accepted it, so several paths can be one route. Risk is summed across them. *Confident now, but only since Section 5.*

**Evidence.** The obligations that a deployment declares to be true at this one stage for this one invocation, for example that the config matches. It is a claim, not necessarily verified. It applies only at that node. If declared, the formal model assumes it is true there. *Moderately confident. I am unsure if evidence is meant to be checked data or a declaration; apparently either, by "kind".*

**Provided fact.** An obligation that a credited gate establishes, which then holds for every later stage on that run. This is the only way that anything moves forward. *Confident.*

**Residual.** The list of assumed (not checked, not constructed) obligations that the acceptance depends on, per stage. Someone must answer for them. Each can be tested for necessity by removing it and re-checking. *Confident about the use. Unsure about exactly what "depends on" means, and about checked and construction kinds: are they in the list? The worked example suggests no.*

**Soundness.** If the checker passes a hierarchy, then in every behaviour in which all stages keep their contracts and all declared evidence is true, nothing that violates a goal gets accepted. It does *not* say that the guards really meet their contracts. *Confident.*

**Completeness.** If the checker fails a hierarchy (and no node repeats on a path), there is a concrete behaviour keeping every contract in which a violating proposal is accepted. It is "relative": real guards may do more than their contract, or stages may be correlated, so the real system may be fine. It is not completeness about the real world. *Confident.*

**Why transitive reasoning fails.** Evidence for a contract is about one stage's invocation, mainly what that stage reads. If `n1` has its assumption and escalates, `n2`'s same-named assumption is a separate claim, possibly false, for example the scorer read sanitised text while the judge reads raw text. The stage then promises nothing and may accept anything. So assuming "it was fine upstream" accepts a hierarchy that has a run where every stage obeys its contract and yet a violation is accepted. *Confident about the logic. Unsure whether the theorem is deep or just a restatement of the per-node definition. The sanitised-scorer story I took from one sentence, and I could not find its setup.*

**Why the problem becomes hard with facts.** Without facts, whether a gate is credited does not depend on the path, so you can merge paths by intersection and lose nothing. With facts, credit depends on which path you came on, so one path may have what another lacks, and merging loses combinations. That lets you encode SAT: a path is a truth assignment, and facts record it. So in the worst case you have to consider all combinations. Note: this is only about *facts that gates depend on*. Facts consumed only by guards are apparently still polynomial, by some trick that I cannot explain. *Confident in the outline. Cannot explain the middle case. Unclear on whether the correlated-conditions result is the same kind of thing. I think it is a separate reason: if two switches share a condition, the paths aren't all real.*

**What a route certificate gives.** For one route and one exact prefix (by hash), a high-confidence upper bound on the probability that a proposal is unsafe and accepted there, from a sample from a distribution D. The bounds are added over open routes to bound total risk, with confidence shared by a union bound. The runtime closes a route without a valid certificate, and a change closes only the affected routes.

**What it does not give.** It gives nothing under an adaptive attacker or outside D. It says nothing about conditional miss rate: with rare attacks a blind guard can pass. It does not show that the guard meets a contract. It says nothing about model weights or callees not declared. It offers no guarantee across many versions, nor after repeated recalibration unless charged. It is per decision, not per session. It does not supply the labels. It does not rely on the composition check for validity under D. *Fairly confident. I do not know what the `context` field is, nor how a certificate relates to the obligation `miss_rate_bounded`. I think a certificate is how one justifies it, but I am guessing.*

**Main conclusion of the paper.** You cannot justify a guardrail stack by measuring its parts and assuming that each one's assumptions carry over. There is a precise, cheap check of a stack's structure that says exactly which assumptions each goal rests on, proved sound and complete against contracts. Deterministic gates should go first and establish facts; statistical stages should be accounted for per route. It does not show that any guard works. For real stacks today, which are short veto chains of statistical stages, the useful output is not the graph analysis but the explicit list of assumptions, and whether that helps engineers is untested. *Confident, though I am not sure if the author's main message is the theorem or the list.*

### What my uncertainties show the paper failed to teach

1. Whether evidence is checked data or a declaration, and that the theory is about declarations.
2. How a statistical obligation can "hold at an invocation".
3. How the exact contract relates to a statistical guard, and how a certificate discharges an obligation.
4. That switches give no knowledge, and therefore why `c` must exist alongside `s`.
5. Why per-invocation evidence is the right modelling choice, as opposed to being merely a definition.
6. What `context`, `η`, "depends on" and "hard" mean.

---

## Part 4. Ranked changes (most helpful first)

1. **State that a switch gives no knowledge, and use DevAgent's `s` versus `c` to teach it.**
   Location: Fig. 2 caption (l.728), after the Semantics paragraph (l.679) or after the `check` equations (l.770), and §6 exposed variant (l.1010).
   Suggestion: add "A switch's condition is not a check. The calculus lets a switch take either branch, so being on the untainted arm proves nothing about the proposal. This is why DevAgent needs gate `c`, which re-establishes as a fact what `s` merely routed on. If the taint condition were misread or forged, `s` would send attacker text down this arm, and without `c` the judge's assumption rests on nothing."

2. **Fix the exposed variant so that it agrees with the traces.**
   Location: l.1001 and l.1005-1010.
   The text says "all input reaches the judge", and `T_jp` is tainted, yet the witness takes the untainted branch and is called `T_jp`. Suggestion: either remove `s` as well for the variant, so all input really reaches the judge, or rewrite as "remove gate c, so that nothing establishes that input on the untainted arm is free of attacker text; the free switch can route `T_jp` there, for example under a mislabelled taint". Author to check against the actual spec.

3. **Add one paragraph bridging exact contracts and statistical stages, and resolve the population/invocation mismatch of `miss_rate_bounded`.**
   Location: at the end of §3.B, repeated at the start of §5 (l.941).
   Suggestion: state explicitly how a contract of a learned stage is to be read: for example, "In Sections 3 to 4 a learned stage's contract is an idealisation: we check the structure as if it held exactly. Its obligation `miss_rate_bounded` is a claim about the deployed stage on a population, not about one proposal; in `E(n)` it stands for 'this stage is inside the regime where its bound applies'. Section 5 replaces the idealisation with a measured bound on each route." And state the link: "A route certificate is what discharges `miss_rate_bounded` for the guard on that route", if true. Move l.965's "Note what the composition check does not do" paragraph up to the opening of §5.

4. **Introduce a "cheat sheet" of the sets and a declared/true distinction.**
   Location: right after Fig. 1 or at the start of §4.
   Suggestion: a small table:
   | Symbol | Meaning | Who knows it |
   Ω = declared at stage; D = gate's promised facts; `req` = stage's needs; E(n) = truly holding at n; F = truly provided on this run; B = counted by checker; A = goals counted; S = goals truly satisfied.
   Add: "Semantics speaks of what is true (E, F, S); the checker of what is declared (Ω, B, A). Soundness says the second is a safe approximation of the first." This one sentence would also explain why the Soundness proof needs F.

5. **Say what Ω is, and why it can't be abused, when it is defined.**
   Location: l.645.
   Suggestion: "Evidence is a *declaration* in the specification, for example 'this judge's calibration bound is available'. Declaring something false is not prevented; it is recorded (Section 4) and someone must answer for it. Guarantees hold only under the declarations." Add an example at the definition of obligation.

6. **Give a step-by-step `check` trace on DevAgent, and on the exposed variant.**
   Location: after the `check` equations (l.770).
   Suggestion: a small table with one row per node: `node, A, B, verdict of ok`. Walk `g1,g2,g3,s`, then both arms. Forward-link to §6. This is the most valuable missing use of the running example.

7. **Rebuild the transitive-reasoning example around DevAgent and fix the dangling callback.**
   Location: intro (l.599) and after Thm 3 (l.821).
   "a sanitized input to the scorer says nothing about what the judge reads" refers to something the introduction lacks. Suggestion: add to l.599: "Suppose the scorer's contract assumes sanitized input, and the deployment sanitizes what the scorer reads. It is tempting to conclude that the judge is covered too. It reads the raw issue." Then state in §4.C why per-invocation evidence is the right model, and not just a definition: "Each stage has its own input and its own component, so a claim about one is not a claim about another. Locality is a modelling decision; Theorem 3 shows that dropping it admits real violations." Say that (a) means "transitive reasoning accepts strictly more".

8. **Separate words: use "passes/fails the check" for hierarchies and "accept/deny" for proposals. Rename the proof-side "obligation".**
   Location: global; abstract, Thm 4, Cor 1, §8, §10. In §8 and §10, write "proof goal" or "verification condition". Reserve "evidence" for Ω and use "calibration data" or "support" elsewhere.

9. **Define "route" explicitly, in one sentence, early.**
   Location: §3.A or Fig. 2 caption, before Thm 7.
   Suggestion: "A route is a guard at which a run can end in acceptance; it may be reached by several paths. A route's prefix is its set of ancestors." Consider renaming "route" to "acceptance point", or at least say "not a path". Similarly define "open", "stale".

10. **Make the terminology of §5's opening a small table, and rename "hard".**
    Location: l.941-945.
    Suggestion: define who chooses `Φ_d`/`Φ_s`. Rename to "exact goals" and "statistical goals", and "hard route" to "gate-covered route". Then a table: route class, what it needs, what it survives. Apply it to DevAgent: `Φ_d = {φ1, φ2, φ_env}`, `Φ_s = {φ3}`, `Q = {n3, n4}`.

11. **Show a certificate on DevAgent, and say how the human route is handled.**
    Location: after Theorem 10 (l.984) or in §6.
    Suggestion: three lines: N, k, δ_r, u_r for `n3`, the sum against ε, and what closes when `v2` changes. State whether `n4` needs a certificate, and how a human's decisions are calibrated. Explain `context` or drop it from the tuple (l.969).

12. **Resolve the structured-view human.**
    Location: Fig. 2 (`n4 human structured`) and l.934.
    Thm 8's discussion says a structured view cannot decide φ3. Suggestion: state what the person sees and why that escapes the argument, for example "a person is given more than the structured view", or relabel the node. Also explain what `v2` contributes: "the scorer is uncredited on this arm; it can only remove proposals and the composition does not rest on it."

13. **Rename colliding symbols.**
    Location: global.
    Priorities: distribution `D` → `\mathcal{P}` or `\mathcal{D}`; risk/realization `R` → `\mathrm{Real}(n)`; graph `|V|,|E|` → `|N|,|Edges|` or "nodes, edges"; DevAgent gate `c` → `p` (provenance) and certificate context dropped; regularise node names (`n3,n4,v2` → `judge`, `human`, `scorer`, or number them consecutively).

14. **Fix the listing's inconsistency with the worked example.**
    Location: Listing 1 (l.734-735), §6 opening.
    Show `contract_holds_on_adversarial_text` in `requires` of L3, or state that the listing shows the benign variant. Explain `"establishes": null` (add a "gate without a goal" clause to the calculus, or a note). Say what `config_match` is.

15. **Fix "antitone" in Theorem 4's proof, and add the one-line intuition.**
    Location: l.830, l.833.
    Lemma 2(a) is monotonicity in the available sets. Add: "A guard's acceptance ends the decision, so a gate placed after it does not protect that route."

16. **Define `η` or remove it; move Table I after §5.**
    Location: l.686-703, Table IV.
    Suggestion: define drift, for example total-variation distance at most η, and state the "adds at most η" result where it is used. Table I fits better right after Theorem 10. In the meantime "the terms defined in Section V" is untrue for η.

17. **State the threat model formally and early.**
    Location: end of §3.B and §6 opening.
    Suggestion: "An attacker is not a term of the calculus. Text written to manipulate a stage is modelled as the failure of an obligation at that stage, so a threat model is a choice of which obligations layers require. An adversarial threat model adds `contract_holds_on_adversarial_text` to every raw-text stage (§7)." Bring the two uniform obligations of §7 forward so §6 does not depend on a later section.

18. **Make the hardness result concrete.**
    Location: Thm 6(b) proof (l.891), paragraph at l.894, Prop 1 (l.903).
    Suggestion: a two-variable instance or a small figure, a one-line gloss of coNP ("a rejection has a short witness; an acceptance need not"), and link to l.869: "the reason the meet can fail is the reason the problem is hard". State that DevAgent lies in the polynomial middle case, if so. Expand Prop 1's "one switch per clause, on literals" by one or two sentences, or drop the hardness proof and state it as a remark.

19. **Add a plain-words line for Clopper-Pearson, coverage and laws.**
    Location: Background (l.631), E12 (l.1211).
    Suggestion: "Treat it as a function: given k losses in N samples and δ, it returns a number that exceeds the true rate with probability at least 1-δ. *Coverage* is the fraction of repeated calibrations in which this is true." Use "distributions" for "laws".

20. **Move Budget and Taint out of Theorem 7, or motivate them.**
    Location: l.915-919.
    Put them in a separate "Properties of the host" proposition, with a line saying that the calculus does not model cost and labels, and these are facts about specific gates. Add a gloss of Monotonicity: "M' is M with some stages stricter."

21. **Define "residual" with less compression, and specify joint redundancy.**
    Location: l.799, Cor 1.
    Replace "that some goal depends on" with an operational definition, for example "entries of kind *assumed* in the Ω of a stage whose credit is used on some path". State that removal tests one entry at a time, and what two mutually redundant entries look like in the output.

22. **Trim or contextualise the earlier-study paragraph.**
    Location: l.1296.
    A reader without the artifact cannot use this. Either give two sentences of context, or cut to the final conclusion.

23. **Minor.**
    - Algorithm 1 line 2: state that others start at the full set.
    - Add a parenthesis or line break in the gate rule of Fig. 1 so the scope of `P(n) ⇒` is unambiguous.
    - In Thm 3(b), say "the only goal".
    - Add a one-line glossary of guard / layer / stage / node at l.640.
    - Say that Table IV's "Stateless prefix" is a premise of Theorem 10 in the theorem itself, and gloss "ledger".
    - State the role of `T_b` in the introduction ("the same action shape; no syntactic rule can separate it from `T*` without provenance"), and say only `T_jp` reaches a learned stage's weakness.
