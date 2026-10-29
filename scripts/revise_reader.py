"""One-time, auditable clarity revision after the independent initial reader pass."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'paper/main.tex'
text=path.read_text(encoding='utf-8')


def edit(start,end,replacement):
    global text
    i=text.index(start)
    j=text.index(end,i+len(start))
    text=text[:i]+replacement.strip()+'\n\n'+text[j:]


edit(r'\begin{abstract}',r'\end{abstract}',r'''
\begin{abstract}
An agent's guard may delegate a difficult decision to another guard, but an
allow verdict is usable only under the conditions for which it was justified.
We implement TINT, a restricted prototype combining mandatory tool-action
checks, explicit delegation conditions, structured judge inputs and a
certificate for the complete configured policy. Our theory separates stacks
that accept early from ensembles in which every guard must agree, and states
the assumptions needed for risk bounds and cost optimization. The study tests
implementation mechanics with scripted guards, not real language models. In
the frozen primary run, all \resPrimaryInfeasible{} seed-level policy families
failed the risk constraint; denying uncertified actions also denied every
benign task. A disclosed floating-point threshold correction, evaluated
separately on fresh exploratory seeds, yielded
\resExploratoryCheckedQuarantineRisk{}\% unsafe accepted proposals among all
proposals, with \resExploratoryCheckedQuarantineUtility{}\% benign acceptance.
In a separate \resPrimaryReplications{}-replication experiment with a known
synthetic population, selected upper bounds covered true risk in
\resPrimaryCoverage{}\% of replications. These results demonstrate executable
accounting and rejection behavior, not useful real-agent safety. External
benchmarks, learned guards, actual development-task success and practical
adaptive robustness remain untested. Raw observations, scoped proofs and
reproduction instructions accompany the artifact.
''')

edit('The contribution is a route-certificate discipline implemented in TINT.',
     'We investigate the following research questions',r'''
TINT (Trust Is Not Transitive) implements explicit delegation checks. An
acceptance route is one way a proposal can receive its final allow, such as
cheap acceptance or acceptance after a judge. The theory can bound these
routes separately; the implemented certificate instead covers the whole
configured policy, including both routes. A fingerprint checks that this
certificate names the actual threshold, guard versions, view and declared
context. This identity check does not establish that the deployment population
still matches calibration. The prototype evaluates only a handwritten scorer
and scripted judges.
''')

edit('In $T^*$ and $T_j$, the issue is untrusted',r'\begin{definition}[Safety property]',r'''
In $T^*$ and $T_j$, the issue is untrusted and the transmitted file contains a
fake secret used for testing. Its payload label remains secret. In $T_b$, the
payload is independently produced public diagnostics; reading an untrusted
issue does not itself make those bytes secret. Labels follow declared data
dependencies, which the trusted host must supply completely; they do not
decide whether following an issue's instruction is authorized. Unknown payload
references conservatively carry both labels. There is no implicit host-file
read or operating-system shell in this interpreter.
''')

edit('Approval is a trusted capability bound to the exact action digest and epoch.',
     r'\end{definition}',r'''
Here $\mathbf G$ means always. Approval binds an exact action digest and a
revocation epoch: incrementing the epoch invalidates earlier grants. The
semantic oracle $Y(h,a)\in\{0,1\}$ is an external correctness label, not the
guard's runnable detector. For a fixed population $D$ of labeled proposals
$(h,a,Y)$, the semantic requirement is
$R(D)=\Pr_D(Y=1,\mathrm{allow})\leq\epsilon$, where $\epsilon$ is the allowed
per-decision residual-risk budget.
''')

edit('The invariants deny execution of $T^*$',r'\begin{definition}[Layer]',r'''
The conjunction joins different obligations: exact exclusion of the hard
forbidden effects, and a population-scoped bound on oracle-unsafe acceptance.
The hard predicates deny $T^*$ and $T_j$; $T_b$ remains eligible for semantic
acceptance. Fixture labels are $Y(T^*)=Y(T_j)=1$ and $Y(T_b)=0$, by construction.
These labels do not solve general prompt-injection recognition. A static
per-decision bound also does not imply that an unbounded session never fails.
''')

edit('A layer $L_i$ maps a permitted view',r'\end{definition}',r'''
A layer $L_i$ maps a permitted view of $(h,a)$ to allow, block or escalate,
with declared provenance, property scope, cost $c_i$ and latency budget
$\ell_i$. Missing or erroneous results cannot grant authority. The instantiated
scorer returns $s\in[0,1]$, with larger values more suspicious; its cheap route
accepts when $s<\tau$, otherwise consulting the judge. An approval fallback
abstains and therefore denies. For arbitrary synchronous plugins, the
prototype handles caller-reported errors but does not enforce cancellation
of a nonreturning call.
''')

edit(r'$\operatorname{Trust}(i,j,P,C)$',r'\end{definition}',r'''
$\operatorname{Trust}(i,j,P\mid\chi)$ means that caller $i$ may rely on
callee $j$ for property $P$ only when trusted evidence establishes condition
$\chi$. The arrow $i\to j$ denotes reliance, not data flow. A transitive closure
would add $i\to k$ by chaining $i\to j$ and $j\to k$; this is permitted only
when intermediate guarantees entail the next assumptions for the same actual
view and property, with mandatory sink checks preserved. For $T_j$, an edge
$\operatorname{Trust}(L_2,L_3,\varphi_{\rm sem}\mid\chi)$ cannot use a
structured-view certificate while $\chi$ is false because raw issue text was
passed to the judge. Contract names $C_i$ are distinct from condition $\chi$.
''')

edit(r'Residual risk is $R=\Pr',r'\end{definition}',r'''
The relevant denominators are
\begin{align*}
R&=\Pr(Y=1,\mathrm{allow}), &\text{joint risk},\\
\Pr(\mathrm{allow}\mid Y=1)&, &\text{attack miss rate},\\
\Pr(Y=1\mid\mathrm{allow})&, &\text{accepted unsafe fraction},\\
\Pr(\mathrm{allow}\mid Y=0)&, &\text{benign utility}.
\end{align*}
For additive costs, $\mathbb E[C]=\sum_i c_i\Pr(\mathrm{reach}\ i)$.
Complete-decision latency quantiles are measured, not formed by adding layer
quantiles. Modeled units are neither CPU time nor money, tokens or GPU use.
''')

edit('For the implemented fixed hierarchy, operational control states',r'\begin{table}[t]',r'''
Only the calibrated checked runtime uses this control path: proposal,
hard-pass, certified, semantic-pass, then effect or denial. Hard-pass requires
the trusted sink predicates; certified requires a matching whole-policy
certificate within risk and confidence budgets. If $s<\tau$ the cheap route
reaches semantic-pass; otherwise a structured-judge allow is required. A
judge escalation reaches the abstaining approval stub and denial. For $T_b$,
an applicable certificate and a low score permit cheap acceptance; $T_j$ is
already denied by the hard sink. Comparators can omit these states as stated
in the evaluation design. This is a hand-specified control semantics, not a
checked extraction of Python.
''')

edit('Let the judge deny unsafe actions',r'\end{IEEEproof}',r'''
Restrict the example contract to the three canonical traces. The judge's
assumption $A_3$ is a structured input; its guarantee $G_3$ is the correct
verdict on those traces. Define the judge to meet $G_3$ under $A_3$, but return
allow on raw $T_j$ containing the reviewer phrase. A middle relay's assumption
$A_2$ is that the caller discharges $A_3$; its guarantee is to relay a correct
verdict. An outer relay assumes $A_2$ and preservation of mandatory sink
checks, and guarantees safe permitted execution under those premises. These
are conditional implications: they say nothing when their premises fail.
The naive caller passes raw $T_j$ and executes the relayed allow without a
sink check, violating secret egress while the premises are false. For $T_b$
there is no unsafe effect; raw $T^*$ without the phrase is denied. The stronger
naive-with-sink control also denies $T_j$. The countermodel demonstrates missing
premises, not failure of a valid assume-guarantee inference.
''')

edit('Assume complete mediation with unforgeable metadata',r'\end{theorem}',r'''
Assume a correct mandatory deterministic monitor, complete mediation with
unforgeable metadata, and monotone denial. Let mutually exclusive events $E_i$
exhaust final acceptance, and let $b_i$ bound each route's joint unsafe mass:
$\Pr_D(Y=1,E_i)\leq b_i$. If these bounds hold simultaneously and all executable
interface premises hold, no hard violation executes and $R(D)\leq\sum_i b_i$.
If simultaneous bounds hold with probability $1-\delta$ over calibration
samples, that is the confidence of this population-risk conclusion; $\delta$
is the calibration failure budget, distinct from decision randomness under $D$.
The implementation uses one whole-policy bound rather than estimating $b_i$
separately.
''')

edit(r'\begin{theorem}[Veto bounds, route bounds and calibration scope]',
     'The product of joint marginal miss probabilities',r'''
Conditional on unsafe input, the common-shock model first flips a branch coin
of probability $\rho$. In that branch all guards compare one shared uniform
variable with their miss rates; otherwise they use independent uniform
variables. This preserves each conditional marginal while changing dependence.

\begin{theorem}[Risk bounds for an all-veto ensemble]
\label{thm:bounds}
Let $\beta_i$ bound the joint event
$M_i=\{Y=1,\mathrm{allow}_i\}$, let $m_i$ be the miss rate conditional on
$Y=1$, and let $\pi=\Pr(Y=1)$ be unsafe prevalence. Then
$R\leq\min_i\beta_i$. Under unsafe-conditional independence,
$R=\pi\prod_i m_i$; under the common-shock model above,
\begin{equation}
R=\pi\left((1-\rho)\prod_i m_i+\rho\min_i m_i\right).
\label{eq:mixture}
\end{equation}
Early acceptance instead uses the disjoint-route accounting of
Theorem~\ref{thm:composition}.
\end{theorem}
\begin{IEEEproof}
The veto intersection is contained in every $M_i$, proving the joint minimum
bound. Conditional independence gives the product of $m_i$; multiplying by
unsafe prevalence gives joint risk. In the shared-uniform branch the
intersection has probability $\min_i m_i$, and in the independent branch it
has probability $\prod_i m_i$. Averaging branches and multiplying by $\pi$
proves~\eqref{eq:mixture}. Early acceptance can skip later guards, so its
acceptance event is not this intersection.
\end{IEEEproof}
''')

edit('For calibration, we separate three facilities.',r'\subsection{Escalation synthesis}',r'''
The library separates three statistical promises. \emph{Split conformal}
controls marginal prediction-set coverage. \emph{Conformal risk control} (CRC)
controls expected bounded loss across calibration samples and a new decision,
not population risk conditional on one observed calibration sample. For $n$
exchangeable labeled samples $Z_k$, fixed losses $l_\lambda\in[0,1]$ decreasing
with conservatism $\lambda$, and desired expected-loss budget $\alpha$, CRC
chooses the least conservative setting satisfying
$(\sum_{k=1}^n l_\lambda(Z_k)+1)/(n+1)\leq\alpha$, with a zero-loss fallback
under its regularity conditions~\cite{arxiv220802814}. These utilities are not
the certificate used in the pilot.

\emph{The implemented certificate} is a one-sided binomial population-risk
bound. For each of $K$ fixed policies, count $k$ unsafe accepted proposals among
all $n$ iid calibration proposals and allocate failure budget $\delta/K$.
For $k<n$, the upper bound is the $(1-\delta/K)$ quantile of
$\operatorname{Beta}(k+1,n-k)$; it is one for $k=n$. For example, zero observed
losses give $U=1-(\delta/K)^{1/n}$, not proof of zero risk. Simultaneous bounds
permit selecting a feasible policy with $U\leq\epsilon$; no feasible policy
means denial. Iid sampling is stronger than general exchangeability. The
confidence concerns repeated calibration samples; deployment risk concerns new
proposals after the policy is fixed. A finite test frequency is neither.

For a fixed policy, let $Q$ be a new deployment law. Total variation is the
largest probability difference between $D$ and $Q$ over events. Thus an
externally established $\operatorname{TV}(D,Q)\leq\eta$ implies
$R(Q)\leq\min(1,R(D)+\eta)$. No estimator of $\eta$ is certified here.
Without restrictions on $Q$, an attacker can concentrate on any accepted
unsafe input, making its risk one. Hard mediation still excludes its exact
hard predicates; it does not exclude all semantic violations. Absent exact
semantic verification, denying uncertified semantic acceptance is the
distribution-free fallback in this restricted model.
''')

edit(r'\begin{theorem}[Conditional escalation threshold]',r'\begin{theorem}[Tightness and limits]',r'''
\begin{theorem}[Conditional sufficient optimality of escalation]
\label{thm:optimization}
For trusted view $x\sim D_X$, let $r_0(x)$ be cheap-acceptance risk, $r_1(x)$
escalation risk, $d(x)>0$ its extra cost, and $c_0(x)$ baseline cost. A
randomized escalation probability $q(x)\in[0,1]$ has
\begin{align*}
R(q)&=\mathbb E_{D_X}[(1-q)r_0+qr_1],\\
C(q)&=\mathbb E_{D_X}[c_0+qd].
\end{align*}
Consider minimizing $C(q)$ subject to $R(q)\leq\epsilon$, with measurable
policies and finite integrable costs. If a finite $\lambda\geq0$ and a feasible
pointwise Lagrangian minimizer $q$ exist with
$\lambda(R(q)-\epsilon)=0$, that policy is optimal. It escalates where
$\lambda(r_0-r_1)>d$, accepts where the inequality reverses, and may randomize
on ties. Existence of such a multiplier is an extra premise.
\end{theorem}
\begin{IEEEproof}
The multiplier is a price per unit of risk: it trades added cost against risk
reduction. The full Lagrangian is
\begin{align*}
L(q,\lambda)={}&\mathbb E[c_0+\lambda r_0]-\lambda\epsilon\\
&+\mathbb E[q(d-\lambda(r_0-r_1))].
\end{align*}
The sign of the coefficient of $q$ gives the rule. Every feasible competitor's
cost is at least the minimized Lagrangian lower bound (weak duality).
Complementary slackness, the stated product being zero, makes the candidate's
cost equal that bound. A tie mixture can change risk without changing the
Lagrangian. At a boundary risk budget, a finite multiplier need not exist.
\end{IEEEproof}

If a compromised judge increases risk on $T_j$, then $r_0-r_1<0$ and escalation
cannot satisfy the inequality at positive extra cost. For $T_b$, a small risk
reduction may not justify deliberation. For $T^*$, optimization never waives the
mandatory sink. Known conditional risks and their monotonicity in a score are
assumptions; the theorem does not learn them from calibration.

The pilot solves a different, finite problem: enumerate a fixed policy grid
and minimize observed calibration mean cost among simultaneously certified
candidates. This is exact within that grid, not among all routing functions.
A separate known-risk finite LP supports policy mixtures; with normalization
and one active risk constraint, an extreme optimum needs at most two policies.
The optional latency API certifies an event $\Pr(L>\mathrm{budget})\leq\gamma$,
where $\gamma$ is an exceedance budget; no real inference-latency constraint was
evaluated. Averaging percentiles would not certify that event.
''')

edit('For unsafe inputs let guard $i$ miss',r'\end{IEEEproof}',r'''
For the joint minimum construction take $\pi=1$ and $m_i=\beta_i$, then let
guard $i$ miss when a shared uniform variable is at most $m_i$. This attains
$\min_i\beta_i$; independent uniforms attain the conditional product law.
For routes, allocate disjoint unsafe masses $b_i$ when their sum is at most
one. If it exceeds one, allocate masses no larger than the bounds that sum to
one, attaining the cap. Finally, interpret Boolean bits as guard misses and
take uniform laws on $\{000,011,101,110\}$ and $\{001,010,100,111\}$.
Each coordinate has marginal $1/2$ and every pair is independent, yet all-one
probabilities are $0$ and $1/4$. Thus pairwise data do not identify joint risk.
Shared susceptibility in $T_j$ illustrates the dependence concern; $T_b$ alone
cannot identify its failure law.
''')

edit('The direct-edge checker validates declared compatibility',r'\begin{table}[t]',r'''
The checker validates declarations, not semantic truth. It accepts only the
runtime's exact topology and supported predicates. At \emph{each runtime
decision}, a fingerprint rechecks specification, guard versions, threshold,
view and environment; confidence and risk budgets are also checked. Complete
host dependencies, valid issuers and honest implementation versions remain
external premises.

The primary instrument is \texttt{lexical-v1}; the corrected exploratory
instrument is \texttt{lexical-v2}. Both remain frozen for reproduction.
The current default \texttt{lexical-v3-bounded} adds an input cap and is not
the source of historical CPU measurements or certificates. As Definition~III
states, exceptions deny authority but arbitrary synchronous plugins have no
enforced cancellation deadline; they can hang. Concurrent trusted-store
mutation and covert channels are outside scope.
''')

edit('Baseline names deliberately describe their implemented behavior:',
     'The policy grid contains',r'''
Table~\ref{tab:baselines} states each toy comparator's rule. All uncertified
cheap exits use threshold $\resBaselineThreshold{}$; the calibrated method uses
its selected threshold. Raw and structured judges are scripted, not official
AgentSpec, ShieldAgent or LlamaFirewall implementations. Comparing invalid
delegation to naive-with-sink isolates mandatory mediation; comparing that
sink control to checked changes the judge view. Comparing checked controls
at identical thresholds isolates certification from unchanged detection.

\begin{table}[t]
\caption{Implemented comparator mechanisms. Fixed denotes the protocol's
baseline threshold; selected denotes the calibrated threshold.}
\label{tab:baselines}
\centering\scriptsize
\setlength{\tabcolsep}{3pt}
\begin{tabular}{lcccc}
\hline
Method & Hard sink & Cheap exit & Judge & Certificate\\
\hline
Rules only & yes & none & none & no\\
Lexical only & no & fixed & none & no\\
Scripted judge only & no & none & raw & no\\
Invalid delegation & no & none & raw & no\\
Naive with sink & yes & fixed & raw & no\\
Checked uncalibrated & yes & fixed & structured & no\\
Checked calibrated & yes & selected & structured & yes\\
\hline
\end{tabular}
\end{table}
''')

edit(r'Table~\ref{tab:hypotheses} maps every hypothesis',
     'Seed-level paired risk/utility differences',r'''
Table~\ref{tab:hypotheses} separates the evidence. The coverage study is a
\emph{different generator} from the authored agent traces: for each fresh
uniform $U$, candidate loss $j$ is $\mathbf1[U<r_j]$, so true population risk
$r_j$ is known and losses are nested. Each of \resPrimaryReplications{}
replications uses \resCoverageCalibrationCount{} calibration and
\resCoverageTestCount{} test draws, targeting \resCoverageTarget{}\% risk.
It selects the cheapest certified candidate; the zero-loss denial fallback
is counted as covered if none is feasible, never omitted. The fixed grid is
given in the preregistration. Certification coverage asks whether selected
true risk is below its bound; finite test-frequency compliance is separate.
''')

edit('The contract scalability study varies declared policy scopes',r'\section{Results}',r'''
The scalability study times repeated valid scope/graph declarations and
planted missing-evidence, scope, endpoint and cycle mutations, not rich
temporal specifications. Authoring time and participant usability are unmeasured.

The historical \emph{core search} permits at most \resAdaptiveBudget{} local
queries, retaining attempts and stopping on unsafe acceptance. It invokes
uncertified functions at a fixed threshold, including the misleading raw label
\texttt{checked\_quarantine}, not the selected calibrated runtime. Every core
accepts the first fixed phrase. These logs show neither response-informed
adaptation nor the denying primary runtime's behavior.
''')

edit('In the frozen coverage experiment, selected bounds cover',r'\begin{figure}[t]',r'''
For the separate nested-loss generator, selected bounds cover true population
risk in \resPrimaryCoverage{}\% of \resPrimaryReplications{} replications;
the exact interval is [\resPrimaryCoverageLo{}\%, \resPrimaryCoverageHi{}\%].
The certificate's nominal confidence is \resNominalConfidence{}\%. This is
observed conservative coverage under the known iid law, not a stronger
deployment guarantee. The selected policy's finite test frequency is below
the \resCoverageTarget{}\% risk budget in \resPrimaryFiniteTestBelow{}
replications; that comparison is to the budget, not the selected bound.
Fallback replications stay in the denominator as known zero-risk denials.
''')

edit(r'Across \resPrimarySynthInstances{} finite-family instances,',
     'The most consequential RQ II finding',r'''
Discrete selection has \resPrimarySynthMismatches{} mismatches across
\resPrimarySynthInstances{} primary finite-family instances and
\resExploratorySynthMismatches{} across \resExploratorySynthInstances{}
exploratory instances, compared with a separate exhaustive calculation by the
authors. Original synthesis logs omitted calibration counts, so their stored
bounds cannot be recalibrated from those records; amended logs retain counts.

Post-review re-analysis reconstructs each LP's risk/cost from weights, checks
the simplex, and compares its objective with independently coded vertex
enumeration. Read-only semantic replay joins historical decisions to traces
and checks configuration, authored labels and non-timing outputs. Independent
here means a separate computation, not independent authorship or oracle
validation. No new held-out outcomes are introduced.
''')

edit('Inspection after the frozen run found a boundary defect',r'\begin{table*}[t]',r'''
The handwritten scorer intends $s(k)=\min(98,4+12k)/100$, where $k$ counts its
listed lexical features. The judge blocks at $s\geq0.40$. Historically,
$0.04+0.12\cdot3$ evaluates just below $0.40$, so a three-feature request is
allowed rather than blocked. Integer hundredths make both score and cutoff
the same stored value. In the direct-injection and judge-targeting patch
families this flips the structured judge to denial; implicit patches still pass.
The underlying checked core's analytic risk falls from
\resPrimaryCheckedUncalibratedPopulationRisk{}\% to
\resExploratoryCheckedQuarantinePopulationRisk{}\%, crossing the frozen
\resRiskBudget{}\% certification budget. The primary runtime had denied
uncertified actions, rather than fixed that detector.

The amendment changes no lexical features or intended cutoffs. It versions the
scorer, preserves original logs and uses \resExploratorySeeds{} fresh seeds.
For example, exploratory seed \resExampleSeed{} observes \resExampleMisses{}
joint losses among \resExampleCalibrationCount{} calibration proposals; its
selected threshold \resExampleThreshold{} has upper risk
\resExampleBound{}\% after simultaneous correction. This count-to-bound-to-
selection example is exploratory, not retroactive primary success.
''')

edit(r'Table~\ref{tab:exploratory} reports',r'\begin{table}[t]',r'''
Table~\ref{tab:exploratory} reports
\resExploratoryCheckedQuarantineRisk{}\% joint risk and
\resExploratoryCheckedQuarantineUtility{}\% benign acceptance. Against naive
with sink, the checked-minus-baseline paired risk difference is
\resExploratoryNaiveWithSinkComparisonDiff{} percentage points, with unadjusted
interval [\resExploratoryNaiveWithSinkComparisonLo{},
\resExploratoryNaiveWithSinkComparisonHi{}] and Holm-adjusted
$p=\resExploratoryNaiveWithSinkComparisonP{}$. Descriptive
$A_{12}=\resExploratoryNaiveWithSinkComparisonA{}$ counts the chance that a
checked seed has lower risk than a baseline seed, giving ties half weight;
larger favors checked. Utility is identical between these controls, and
calibrated/uncalibrated checked decisions coincide. The interval quantifies
sampling this authored mixture, not real-attack effectiveness.
''')

edit(r'Table~\ref{tab:families} exposes the limited support.',r'\begin{figure*}[t]',r'''
The empirical judge-targeting family differs from canonical $T_j$. Here it
proposes an \emph{unauthorized patch} with no secret egress or production
deletion, so the hard sink cannot decide its semantic authorization. Canonical
$T_j$ remains secret exfiltration and is denied by that sink. Sharing a
reviewer phrase does not make their actions or violated properties identical;
Tables~\ref{tab:traces} and~\ref{tab:families} therefore have different outcomes.

For the authored mixture, exploratory checked population risk is
\resExploratoryCheckedQuarantinePopulationRisk{}\%, utility
\resExploratoryCheckedQuarantinePopulationUtility{}\%, and modeled cost
\resExploratoryCheckedQuarantinePopulationCost{} units, versus
\resExploratoryNaiveWithSinkPopulationRisk{}\% risk for naive with sink.
The mechanisms and family masses imply these values. Among accepted
exploratory proposals, the unsafe fraction is
\resExploratoryAcceptedConditionalRisk{}\%; its denominator differs from joint
risk and from benign utility.
''')

edit('On the unseen encoded family, exploratory checked risk reaches',
     r'\subsection{Assumption audit and threats to validity}',r'''
The shifted set contains only authored unauthorized patches: all inputs are
attacks, unlike the original benign/attack mixture. Its encoded maintenance
text has no listed suspicious feature, so the structured view has a low score,
no secret external payload and no destructive production action. Checked
acceptance is \resExploratoryShiftRisk{}\% on this all-attack denominator.
The matching declared context does not detect the new law. Core-search logs
likewise provide no primary-runtime adaptive claim; the primary fallback
instead denies every uncertified benign task too.
''')

# Reader-facing captions and removal of production-process digressions.
text=text.replace('The horizontal parameter is a mixture weight, not measured pairwise\ncorrelation. The plot does not assert a universal interpolation law.',
 r'The unsafe population has $\pi=1$ and conditional miss rates '+
 r'$\resDependenceFirst{},\resDependenceSecond{},\resDependenceThird{}$. Each cross is one seed with '+
 r'\resDependenceSamples{} draws. The horizontal mixture weight is not measured correlation; the curve is model-specific.')
text=text.replace('Family & Primary & Exploratory & Sink (\\%) & Checked (\\%)',
                  'Family & Primary count & Expl. count & Naive sink (\\%) & Checked (\\%)')
text=text.replace('not distinct semantic tasks.}',
                  'not distinct semantic tasks. Rates are within each family; columns labeled count are sample totals.}')
text=text.replace('equal points overlap.\nThese plots compare configurations, not external model Pareto frontiers.',
                  'equal points are grouped and labeled with benign utility. Both panels share the risk scale. These are local configurations, not external-model Pareto frontiers.')
text=text.replace(r'\begin{definition}[Layer]',r'\begin{definition}[Layer]\label{def:layer}')
text=text.replace(r'Definition~III',r'Definition~\ref{def:layer}')
text=text.replace('Family & Primary count & Expl. count & Naive sink (\\%) & Checked (\\%)',
                  'Family & $N_P$ & $N_E$ & Naive (\\%) & Checked (\\%)')
text=text.replace('Rates are within each family; columns labeled count are sample totals.',
                  r'$N_P,N_E$ are primary/exploratory counts; rates compare naive-with-sink and checked within each family.')
text=text.replace('Our opened bibliography covers the verified sources among these systems;\nwe do not infer a missing capability from an abstract\'s silence.\n','')
text=text.replace('The broader dual-process seed list remains incompletely verified and is not\nturned into invented citations.\n','')
text=text.replace('Wider foundational coverage remains necessary for a submission.','')
text=text.replace('A matching context identifier is not a\nstatistical test of exchangeability.', 'Context identity does not establish exchangeability.')
text=text.replace('TINT local integration & Y & Y & P & P & Y & P & P & P & Y',
                  'TINT local integration & Y & Y & P & P & Y & P & P & U & Y')
text=text.replace('The source comprises one authored\n\\texttt{main.tex}, one bibliography and a generated macro include, with the\nprovided template\'s IEEEtran class/options and bibliography style.', '')
old='''Table~\\ref{tab:gap} summarizes overlap rather than claiming that each
capability is individually novel. The closest-source full-text review and the
wider abstract-level scoping review have different depths; the retained
verification records establish bibliographic identity, not independent
validation of all claims made by those sources.'''
new=r'''Table~\ref{tab:gap} uses hierarchy for composed guards; formal spec for
machine-defined constraints; hard for exact safety within a stated semantics;
statistical for a probability guarantee; conditioned trust for explicit
reliance premises; cost for resource-aware routing/measurement; agent traces
for tool-action sequences; adaptive for analyzed response-informed attacks;
and tool for an available artifact. U is missing review evidence, not absence.
TINT's adaptive cell is U because first-query core search is not that evidence.
No individual column is claimed novel.'''
assert old in text
text=text.replace(old,new)
path.write_text(text,encoding='utf-8',newline='\n')
print('Applied initial reader clarity revisions; scientific observations unchanged.')
