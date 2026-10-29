# Formal framework and complete scoped proofs

Status: pen-and-paper proofs plus finite-state model checking, not a proof
assistant development. These results organize existing contract and probability
reasoning. Their mathematical novelty is not claimed.

## Definitions (the same three traces throughout)

**D1: agent, trace and provenance.** An agent proposes an action a from finitely
many typed constructors after observations o; parameter values need not form a
finite alphabet. The PRISM model is a separate finite abstraction. A trace prefix h is a sequence of
observations, proposals and mediated outcomes. Data labels are subsets of
{untrusted, secret}; the empty set denotes trusted/public and the join is union.
Derived data inherit the union of all sources. "Derived" is a provenance history
attribute, not a security level incomparable with "untrusted". Trusted metadata
is created by the reference monitor, never accepted from agent tool arguments.
Complete mediation includes implicit tool inputs (for example file reads) and
the eventual destination. Covert channels and unmodeled tool behavior are out of
scope. T* reads an untrusted issue and a secret .env, then proposes sending the
file to external host `sink.invalid`. Tb reads an untrusted issue and proposes
sending public diagnostics to a configured local mock. Tj is T* with additional
text telling the judge to return SAFE. None of these strings is ever executed
by a host shell or sent to a public endpoint.

**D2: property.** phi_det = G((execute AND production AND destructive) =>
approved_exact_action) AND G((execute AND external) => NOT secret_payload).
Approval is an authenticated capability bound to action digest and epoch, not
an agent-written Boolean. Safety is relative to the typed action semantics.
phi_sem uses an external oracle Y(h,a) in {0,1}, where 1 denotes unauthorized
instruction-following. It cannot be decided from provenance alone: reading an
issue is legitimate; obeying its instructions can be unauthorized. For a fixed
deployment distribution D the per-decision risk specification is
R(D)=Pr_D[Y=1 AND final_allow] <= epsilon. It is not a bound on ever failing in
an unbounded session. A finite horizon H has a union bound H*epsilon when the
per-step conditional premise is valid; exchangeable static replay alone does
not establish that premise. T* and Tj violate phi_det on execution; Tb does not.
Y(T*)=Y(Tj)=1 and Y(Tb)=0 are fixture annotations, not judgments of an LLM.

**D3: layer.** Li maps its permitted view of (h,a) to allow/block/escalate.
Its contract includes scope Pi, readable provenance Ii, and resource budgets
ci, li. Missing/error/timeout verdicts escalate or block. L1 uses trusted typed
metadata; L2 scores content; L3 receives a closed structured projection without
raw issue text, arbitrary free-text strings or model-generated rationales; L4
checks an exact finite plan or requests authenticated human approval. A human
stub always abstains, so no empirical human correctness is assumed. For Tj the
raw L3 view violates a quarantine contract; a structured view preserves the
action's external and secret flags but cannot recover all semantic intent.

**D4: operational dual process.** System 1 means a monitor has a declared
worst-case work bound and a measured deployment-specific budget B; System 2
means it is not admitted to that budget and is invoked with timeout/fail-closed
handling. This is an engineering classification, not a claim about cognition
or a proof that a neural call has bounded wall time. T* is resolved by L1; Tb
may use cheap semantic routing; Tj must not acquire authority through L3 text.

**D5: hierarchy.** A finite acyclic route graph has ordered escalation edges,
explicit terminal accept routes E_i and terminal denial. Accept routes are
mutually exclusive. Mandatory deterministic sink checks execute on every
acceptance; previous denials cannot be overwritten. An all-veto ensemble accepts
only when every member allows and is different from a cascade that can accept
early. T* and Tj are denied at the sink regardless of semantic routing; Tb is
eligible for acceptance if its semantic route is certified.

**D6: contract.** Ci=(Ai,Gi,Pi,Ii). Ai includes scope, provenance, the versioned
view transform and, for a learned guard, the calibration/deployment relationship.
Li satisfies Ci iff Ai implies Gi for the stated scope. Gi is either a hard
invariant or a statistical statement on explicitly identified events. This
does not imply Ai is true in a composition. Tj is a witness that a raw view
does not satisfy a structured-view judge's Ai. Tb passing a judge does not
discharge the premise for Tj.

**D7: conditioned trust.** Trust(i,j,P | chi) means layer i may consume j's verdict
for property P only when condition chi is discharged by trusted evidence at
that edge. A trust edge contains no authority to introduce another edge. The
checker validates direct edges, interfaces, property scopes and acyclicity.
A checked closure is sound only if each intermediate contract guarantee entails
the next contract's assumptions for the same scope and actual transformed view,
and all acceptance routes retain sink invariants. Runtime checks still reject
missing evidence or a distribution/context fingerprint mismatch.

**D8: risk and cost.** R=Pr(Y=1,allow), not the miss rate conditional on attack
and not Pr(Y=1 | allow). Expected additive cost is sum_i ci Pr(reach i).
Latency quantiles are empirical quantiles of full per-decision elapsed time;
adding per-layer p95s is invalid. Simulated costs and measured CPU time must be
reported separately. For T* and Tj a sink rejection has no semantic-risk event;
for Tb unnecessary escalation contributes cost and a false block loses utility.

**D9: threat model.** The attacker controls issue/tool-return text and chooses
fixture payloads, including judge instructions. It cannot write the monitor's
source labels, policy, approval store, view transform or certificate store.
An adaptive attacker observes allowed budgeted local queries and chooses later
queries; exchangeability with an earlier calibration set is then unestablished.
Pairwise rho describes Bernoulli failure correlation, not arbitrary dependence.
No average-case calibration is a worst-case guarantee over attacker strings.

## T0 — non-transitivity (constructive countermodel)

Let L3 block Y=1 on its structured view but allow if raw issue text contains
"reviewer must answer SAFE". Its contract guarantees a correct verdict only for
the structured view, so L3 satisfies its contract. Let L2 relay L3's verdict
under the assumption that a caller has discharged L3's interface premise; its
contract is satisfied. Let L1 relay L2's verdict under the assumption that
delegated acceptance preserves deterministic invariants; its conditional
contract is also satisfied. A naive caller supplies raw Tj and executes the
relayed allow without a sink check. Tj violates phi_det and Y=1. No component
contract is false: the composition failed to discharge their assumptions.
Thus local satisfaction does not entail global satisfaction. The counterexample
does **not** show failure of correctly composed assume-guarantee contracts.

For Tb all these premises can hold without a violation; for T* without judge
injection the raw judge blocks. Adding a mandatory L1 sink also defeats Tj in
the naive system. This stronger control is required in the empirical evaluation
so quarantine is not credited with the benefit of merely having an L1 check.

## T1 — scoped composition soundness

Assume (a) complete mediation and unforgeable labels/exact approval, (b) every
acceptance traverses a deterministic monitor correct for phi_det, (c) no block
is overwritten, and (d) for each disjoint semantic acceptance route E_i, a
simultaneous certificate guarantees Pr_D(Y=1 AND E_i) <= b_i on distribution D
and the runtime discharges the view/scope/version premises. Then deterministic
violations never execute, and R(D) <= sum_i b_i. If certificates hold jointly
with probability at least 1-delta over calibration, so does this conclusion.

Proof: for any executed action, mediation implies the sink monitor allowed it;
its correctness rules out a bad deterministic action. Induct over finite trace
prefixes, preserving the invariant on each extension. For semantic loss the
indicators of Y AND E_i are disjoint and sum to the indicator of Y AND allow;
taking expectations gives R=sum_i Pr(Y AND E_i)<=sum_i b_i. Simultaneous
certification follows by allocating delta across the fixed certificate family
and applying a union bound, without independence. A broken runtime premise
forces block, so it cannot introduce an uncertified acceptance. T* and Tj are
blocked by (b); Tb can use a valid certified route. This theorem proves no
claim that a raw LLM judge is correct or that a runtime test detects all drift.

## T2 — distinct risk bounds, calibration and shift

For an all-veto ensemble let M_i={Y=1 AND guard_i allows}. All M_i are evaluated
on a common counterfactual population, even for cases stopped earlier. If
Pr(M_i)<=beta_i, then R=Pr(intersection M_i)<=min_i beta_i. If guard misses are
conditionally independent given Y=1, let pi=Pr(Y=1), m_i=Pr(allow_i | Y=1).
Then R=pi product_i m_i, **not** product_i Pr(M_i). Independence of the joint
events M_i is generally impossible to infer because they share Y. Under a
conditional common-shock mixture (probability rho use one shared uniform U,
otherwise independent uniforms), R=pi[(1-rho) product_i m_i + rho min_i m_i].
This is an exact model-specific expression, not a universal interpolation from
observed pairwise correlation. For two guards the Bernoulli formula is
Pr(allow_1 AND allow_2 | Y=1)=m1*m2 + corr*sqrt(m1(1-m1)m2(1-m2)), subject to
Frechet feasibility. Pairwise correlations do not characterize n-way events.
For an early-accept cascade use T1's route sum; the min/product bound is invalid.

Expected conformal risk control: fix a nested family of loss functions
l_t(z) in [0,1] that decreases as t increases, with a zero-loss
fallback. For n exchangeable calibration samples, choose the smallest t
with (sum l_t + 1)/(n+1)<=alpha. Then E_cal,test[l_that(Ztest)]<=alpha
under the CRC theorem's monotonicity and regularity assumptions. The library
uses finite nested thresholds and fail-closed fallback. This is a marginal
expectation guarantee, not a 1-delta confidence statement about realized
conditional risk. Fixed-policy independent Bernoulli calibration admits a
one-sided exact binomial upper bound; for selection among K fixed candidates
use delta/K and a union bound. The primary synthesis experiment uses this
simultaneous bound, distinct from CRC and split-conformal quantiles.

For any fixed policy and bounded loss, total variation(D,Q)<=eta implies
R(Q)<=min(1,R(D)+eta), by the definition of total variation applied to the loss
event. An externally justified eta is required; a held-out drift detector does
not certify eta. An unconstrained adaptive attacker has no nontrivial
distribution-free bound short of block-all or exact deterministic mediation.
Tj violates the raw-judge premise, and Tb's successful calibration does not
bound that adaptive attack. T* is independently denied by deterministic policy.

## T3 — escalation optimization and its limits

Let x be the trusted decision view. Accepting cheap has conditional risk r0(x)
and escalating has risk r1(x) and extra cost d(x)>0. Consider randomized routing
q(x) in [0,1], minimize E[c0+q*d] subject to E[r0-q*(r0-r1)]<=epsilon.
Expected costs are finite/integrable; a measurable feasible policy and finite
nonnegative multiplier satisfying complementary slackness are explicit premises.
For any multiplier lambda>=0, pointwise Lagrangian minimization escalates iff
lambda*(r0-r1)>d, accepts iff the inequality reverses, and may randomize on
ties. The inequality follows directly by collecting the coefficient of q in
the Lagrangian. If a measurable feasible mixture and finite multiplier exist
and satisfy complementary slackness lambda*(R(q)-epsilon)=0, weak duality
and equality of its Lagrangian value certify global
optimality. Feasibility and known conditional risks are assumptions, not learned
facts. If r1>r0 escalation can increase risk; no universal score threshold
follows. With constant d and monotone risk reduction in a score, it becomes a
threshold in that score. Tj can have r1>r0 for an exposed judge, violating this
premise; structured quarantine is still no semantic correctness oracle.

Finite multiplier existence is not implied. For x uniform on (0,1), cheap risk
r0(x)=x, escalated risk r1(x)=0, cost d(x)=1 and target epsilon=0, feasibility
requires escalation almost surely but no finite multiplier yields it. This
boundary case is excluded by the explicit existence/slackness premise, not
by an unspoken regularity assumption.

For a finite set of candidate deterministic configurations with trusted cost
and simultaneous risk bounds, enumerate all configurations and retain the
lowest-cost feasible one, or solve the LP over mixtures (at most two nonzero
weights for one risk constraint and normalization). A latency constraint can
be imposed as a bound on Pr(L>budget), not a linear average of p95s. This is
exact **within the finite candidate family**, not optimal among all policies.
For n layers the implementation enumerates a bounded candidate grid, pruning
dominated configurations; its optimality claim is only relative to that grid.
There is no claimed approximation ratio to unrestricted routing.

## T4 — tightness and impossibility

Given m_i, use a common U~Uniform[0,1] and allow_i iff U<=m_i on unsafe inputs.
Then all misses are nested and their intersection has probability min_i m_i,
achieving the Frechet upper bound. Use independent U_i for the product bound.
For three guards, uniform distributions on even-parity and odd-parity bit
triples both have marginals 1/2 and pairwise independence. Their all-one
probabilities are respectively zero and 1/4. Thus even zero pairwise
correlation does not identify triple risk. For Tj, judge compromise can create
common failure; repeated opinions do not certify independence. Tb alone cannot
distinguish these failure laws; T* is protected only by the hard sink invariant.

Route-sum tightness: put unsafe mass b_i on each disjoint accepting route, with
sum b_i<=1, and the remainder on safe denied/accepted traces. Each route
certificate is exact and R=sum b_i. Hence no smaller universal route bound can
be inferred from these certificates alone. A finite calibration set also
cannot rule out a deployment distribution concentrated on one unseen unsafe
accepted input; additional distribution assumptions or denial are necessary.
