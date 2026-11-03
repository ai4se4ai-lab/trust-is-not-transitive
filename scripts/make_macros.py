"""Generate every experimental number/table/figure with JSON-pointer provenance."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from process_results import read_json,serialize

BEGIN='% BEGIN GENERATED MACROS'
END='% END GENERATED MACROS'

LABELS={'rules_only':'B1 Gate only','classifier_only':'B2 Scorer only','judge_only_scripted':'B3 Exposed judge only',
        'naive_delegation':'B4 Invalid delegation','naive_with_sink':'B5 Gate + scorer + exposed judge',
        'checked_uncalibrated':'B6 TINT without certificate','checked_quarantine':'TINT (full)'}


def scientific(value):
    exponent=len(str(value))-1
    return f'{value/10**exponent:.1f}\\times 10^{{{exponent}}}'


def verification(macro,macros,tables):
    """Macros and tables of the verification study, from results/v2."""
    def group(name):
        path=ROOT/'results/v2'/(name+'.json')
        source,sha='results/v2/'+name+'.json',hashlib.sha256(path.read_bytes()).hexdigest()
        def put(macro_name,value,pointer,fmt='d'):
            macro(macro_name,value,pointer,fmt)
            macros['res'+macro_name].update(source=source,source_sha256=sha)
        return read_json(path),put
    proofs,put=group('proofs')
    rows=proofs['obligations']
    put('ProofObligations',len(rows),'/obligations#length')
    put('ProofZthree',sum(r['z3']=='unsat' for r in rows),'/obligations#z3-unsat')
    put('ProofCvc',sum(r['cvc5']=='unsat' for r in rows),'/obligations#cvc5-unsat')
    assert not any(r['hypotheses']=='unsat' for r in rows)
    put('ProofSatisfiable',sum(r['hypotheses']=='sat' for r in rows),'/obligations#premises-sat')
    put('ProofUnknown',sum(r['hypotheses']=='unknown' for r in rows),'/obligations#premises-unknown')
    put('ProofNoPremise',sum(r['hypotheses']=='n/a' for r in rows),'/obligations#no-premises')
    order=[('T1-soundness','Soundness (Thm.~\\ref{thm:sound})'),('T2-completeness','Completeness (Thm.~\\ref{thm:complete})'),('L1','Frame (Lem.~\\ref{lem:frame})'),
           ('T10-meet','Meet (Lem.~\\ref{lem:meet})'),('T11-transitive','Transitive reasoning (Thm.~\\ref{thm:transitive})'),('T12-order','Order (Thm.~\\ref{thm:order})'),
           ('T3-monotonicity','Monotonicity'),('T4-routes','Routes'),('T5-prefix-locality','Prefix locality'),('T6-noninterference','Non-interference (Thm.~\\ref{thm:ni})'),
           ('T7-decision-cost','Decision cost'),('T8-budget','Budget'),('T9-taint','Taint')]
    proof_rows=[]
    for key,label in order:
        chosen=[r for r in rows if r['theorem'].startswith(key)]
        proof_rows.append(f"{label} & {len(chosen)} & {sum(r['z3']=='unsat' for r in chosen)} & {sum(r['cvc5']=='unsat' for r in chosen)} \\\\")
    assert sum(sum(r['theorem'].startswith(k) for r in rows) for k,_ in order)==len(rows)
    tables['proofs']='\n'.join(proof_rows)
    mutants,put=group('proof_mutants')
    put('ProofMutants',len(mutants),'#length')
    put('ProofMutantsKilled',sum(m['killed'] for m in mutants),'#killed')
    d,put=group('e14_reduction')
    put('ReductionFormulas',d['formulas'],'/formulas');put('ReductionSatisfiable',d['satisfiable'],'/satisfiable');put('ReductionDisagreements',d['disagreements'],'/disagreements');put('ReductionFalseAlarms',d['false_alarms_of_fast_analysis'],'/false_alarms_of_fast_analysis')
    exhaustive,put=group('e3_exhaustive')
    put('ExhaustiveNodes',max(r['nodes'] for r in exhaustive),'#max-nodes')
    put('ExhaustiveTotal',sum(r['hierarchies'] for r in exhaustive),'#sum-hierarchies')
    put('ExhaustiveAccepted',sum(r['accepted'] for r in exhaustive),'#sum-accepted')
    put('ExhaustiveDisagreements',sum(r['equation_disagreements'] for r in exhaustive),'#sum-equation-disagreements')
    put('ExhaustiveSearches',sum(r['model_searches'] for r in exhaustive),'#sum-searches')
    put('ExhaustiveSearchDisagreements',sum(r['semantic_disagreements'] for r in exhaustive),'#sum-semantic-disagreements')
    d,put=group('e4_differential')
    put('DiffSpecs',d['specs'],'/specs');put('DiffAccepted',d['accepted'],'/accepted');put('DiffRejected',d['rejected'],'/rejected')
    put('DiffDecisions',d['decisions'],'/decisions');put('DiffWitnesses',d['witnesses'],'/witnesses');put('DiffWitnessFailures',d['witness_failures'],'/witness_failures')
    put('DiffDisagreements',d['check_disagreements']+d['engine_disagreements']+d['route_disagreements'],'#sum-disagreements')
    put('DiffSemantic',d['semantic_compared'],'/semantic_compared');put('DiffSemanticDisagreements',d['semantic_disagreements'],'/semantic_disagreements')
    put('DiffContractRuns',d['contract_runs'],'/contract_runs');put('DiffAcceptingRuns',d['contract_accepting_runs'],'/contract_accepting_runs');put('DiffRejectedFound',d['rejected_with_sampled_violation'],'/rejected_with_sampled_violation');put('DiffResidualDisagreements',d['residual_disagreements'],'/residual_disagreements');put('DiffUnsafeAccepted',d['unsafe_accepted'],'/unsafe_accepted');put('DiffUnsafeRejected',d['unsafe_rejected'],'/unsafe_rejected')
    put('DiffMeanReachable',d['mean_reachable_nodes'],'/mean_reachable_nodes','.1f')
    put('AdequacyTerms',d['z3_adequacy']['terms'],'/z3_adequacy/terms');put('AdequacyFailures',sum(d['z3_adequacy']['failures'].values()),'/z3_adequacy/failures#sum')
    m,put=group('e5_mutation')
    survived=[r for r in m['rows'] if r['status']=='survived']
    put('MutationTotal',m['mutants'],'/mutants');put('MutationKilled',m['killed'],'/killed');put('MutationSurvived',len(survived),'/rows#survived')
    put('MutationEquivalent',sum(r.get('classification')=='equivalent' for r in survived),'/rows#equivalent')
    put('MutationGaps',sum(r.get('classification')=='gap' for r in survived),'/rows#gap')
    put('MutationDifferential',m['modes']['differential_only'],'/modes/differential_only');put('MutationCrash',m['modes']['crash_or_timeout'],'/modes/crash_or_timeout');put('MutationUnit',m['modes']['unit_only'],'/modes/unit_only')
    d,put=group('e7_monolithic')
    put('MonoZthree',d['z3']['compared'],'/z3/compared');put('MonoPrism',d['prism']['compared'],'/prism/compared')
    put('MonoDisagreements',d['z3']['disagreements']+d['prism']['disagreements'],'#sum')
    d,put=group('e8_continuity')
    put('ContinuityCompared',d['primary']['compared']+d['exploratory']['compared'],'#sum-compared')
    put('ContinuityDisagreements',d['primary']['disagreements']+d['exploratory']['disagreements'],'#sum-disagreements')
    d,put=group('timing/e9_scalability')
    put('SlopeChain',d['slopes']['chain'],'/slopes/chain','.2f');put('SlopeDiamonds',d['slopes']['diamonds'],'/slopes/diamonds','.2f')
    put('SlopeRejectedDecision',d['slopes']['rejected_decision'],'/slopes/rejected_decision','.2f');put('SlopeRejectedWitness',d['slopes']['rejected_witnesses'],'/slopes/rejected_witnesses','.2f')
    big=[r for r in d['by_nodes'] if r['nodes']==max(x['nodes'] for x in d['by_nodes'])]
    put('MillionNodes',big[0]['nodes'],'/by_nodes#max-nodes')
    put('MillionSeconds',max(r['seconds'] for r in big),'/by_nodes#max-seconds','.1f')
    rejected=d['rejected'][-1]
    put('RejectedDecisionNodes',rejected['nodes'],'/rejected/-1/nodes');put('RejectedDecision',rejected['decision_seconds'],'/rejected/-1/decision_seconds','.1f')
    witnessed=[r for r in d['rejected'] if r['with_witnesses_seconds']][-1]
    put('RejectedWitnessNodes',witnessed['nodes'],'/rejected#witness-nodes');put('RejectedWitness',witnessed['with_witnesses_seconds'],'/rejected#witness-seconds','.1f')
    goals=d['by_goals']
    put('GoalsMax',goals[-1]['goals'],'/by_goals/-1/goals');put('GoalsNodes',goals[-1]['nodes'],'/by_goals/-1/nodes');put('GoalsMaxSeconds',goals[-1]['seconds'],'/by_goals/-1/seconds','.2f')
    layers=d['many_layers'][-1]
    put('LayersCount',layers['layers'],'/many_layers/-1/layers');put('LayersGoals',layers['goals'],'/many_layers/-1/goals');put('LayersSeconds',layers['seconds'],'/many_layers/-1/seconds','.2f')
    flow=d['flow'][-1]
    put('FlowDepth',flow['depth'],'/flow/-1/depth');put('FlowStates',flow['states'],'/flow/-1/states');put('FlowSeconds',flow['seconds'],'/flow/-1/seconds','.2f')
    for family,name in [('chain','Chain'),('diamonds','Diamonds')]:
        put('Plot'+name,' '.join(f"({r['nodes']},{r['seconds']:.4f})" for r in d['by_nodes'] if r['family']==family),'/by_nodes#family='+family)
    versus=d['versus']
    solved=lambda key:max(r['depth'] for r in versus if r.get(key) in ('sat','unsat'))
    put('PathMaxDepth',solved('path_answer'),'/versus#path-max-depth');put('PrismMaxDepth',solved('prism_answer'),'/versus#prism-max-depth')
    put('VersusMaxDepth',max(r['depth'] for r in versus),'/versus#max-depth')
    last=[r for r in versus if r['depth']==max(x['depth'] for x in versus)]
    put('VersusTintMs',1000*max(r['tint_seconds'] for r in last),'/versus#tint-ms','.1f');put('VersusZthreeMs',1000*max(r['z3_seconds'] for r in last),'/versus#z3-ms','.0f')
    put('VersusPaths',scientific(last[0]['paths']),'/versus#paths')
    rows=[]
    for depth in [8,20,64,256]:
        picked=[r for r in versus if r['depth']==depth]
        def cell(key):
            if any(r.get(key+'_answer')=='timeout' for r in picked):return 'timeout'
            if not any(key+'_seconds' in r for r in picked):return 'skipped'
            return f"{1000*max(r[key+'_seconds'] for r in picked if key+'_seconds' in r):.1f}"
        tint=f"{1000*max(r['tint_seconds'] for r in picked):.1f}"
        rows.append(f"{depth} & {picked[0]['nodes']} & ${scientific(picked[0]['paths'])}$ & {tint} & {cell('z3')} & {cell('path')} & {cell('prism')} \\\\")
    tables['versus']='\n'.join(rows)
    d,put=group('timing/e10_overhead')
    put('StageMicroseconds',d[-1]['per_stage_microseconds'],'/-1/per_stage_microseconds','.1f');put('OverheadDepth',d[-1]['depth'],'/-1/depth')
    put('DecisionMs',d[-1]['decision_microseconds']/1000,'/-1/decision_microseconds#ms','.1f');put('ConstructorSeconds',d[-1]['constructor_seconds'],'/-1/constructor_seconds','.2f')
    d,put=group('e11_recertification')
    put('RecertHierarchies',d['random_hierarchies'],'/random_hierarchies');put('RecertMeanRoutes',d['mean_routes'],'/mean_routes','.1f')
    put('RecertMeanFraction',100*d['mean_fraction_affected'],'/mean_fraction_affected#percent','.0f')
    put('LocalityChecks',d['locality_checks'],'/locality_checks');put('LocalityViolations',d['locality_violations'],'/locality_violations')
    c=d['cascade'][-1]
    put('CascadeRoutes',c['routes'],'/cascade/-1/routes');put('CascadeLast',100*c['last_layer_fraction'],'/cascade/-1/last_layer_fraction#percent','.1f');put('CascadeMean',100*c['mean_fraction'],'/cascade/-1/mean_fraction#percent','.1f')
    put('CascadeStale',c['routes']*c['mean_fraction'],'/cascade/-1#mean-stale-routes','.1f')
    small,large=d['by_size'][0],d['by_size'][-1]
    put('RecertSmallRoutes',small['mean_routes'],'/by_size/0/mean_routes','.1f');put('RecertSmallStale',small['mean_affected'],'/by_size/0/mean_affected','.1f');put('RecertSmallFraction',100*small['mean_fraction'],'/by_size/0/mean_fraction#percent','.0f')
    put('RecertLargeRoutes',large['mean_routes'],'/by_size/-1/mean_routes','.1f');put('RecertLargeStale',large['mean_affected'],'/by_size/-1/mean_affected','.1f');put('RecertLargeFraction',100*large['mean_fraction'],'/by_size/-1/mean_fraction#percent','.0f')
    rows=[f"Random, {b['min_nodes']}--{b['max_nodes']} nodes & {b['hierarchies']:,} & {b['mean_routes']:.1f} & {b['mean_affected']:.1f} & {100*b['mean_fraction']:.0f} \\\\".replace(',','{,}').replace('Random{,}','Random,') for b in d['by_size']]
    rows+=[f"Cascade & 1 & {b['routes']} & {b['routes']*b['mean_fraction']:.1f} & {100*b['mean_fraction']:.0f} \\\\" for b in d['cascade']]
    tables['recert']='\n'.join(rows)
    d,put=group('e12_route_bounds')
    put('BoundLaws',d['laws'],'/laws')
    put('BoundCoverageRoutes',d['min_coverage_routes'],'/min_coverage_routes','.3f')
    put('BoundProductUnder',d['product_understates_laws'],'/product_understates_laws');put('BoundMinUnder',d['min_understates_laws'],'/min_understates_laws')
    put('BoundSumRatio',d['mean_ratio_sum_to_whole'],'/mean_ratio_sum_to_whole','.2f')
    put('BoundMaxUnder',max(r['true_risk']/r['product_estimate'] for r in d['rows'] if r['product_estimate']>0),'/rows#max-risk-over-product','.1f')
    put('BoundBelowNominal',sum(r['coverage_routes_simultaneous']<.95 for r in d['rows']),'/rows#below-nominal')
    d,put=group('e12b_pipeline')
    put('PipelineLaws',d['laws'],'/laws');put('PipelineCoverageRoutes',d['min_coverage_routes'],'/min_coverage_routes','.3f');put('PipelineCoverageSum',d['min_coverage_sum'],'/min_coverage_sum','.3f')
    put('PipelineWilson',d['wilson_upper_of_worst_law'],'/wilson_upper_of_worst_law','.3f')
    d,put=group('worked_example')
    put('WorkPrevalence',d['prevalence'],'/prevalence','.3f');put('WorkBudget',d['budget'],'/budget','.2f');put('WorkSamples',d['samples'],'/samples');put('WorkShareTotal',d['share']*2,'/share#times-routes','.2f');put('WorkShare',d['share'],'/share','.3f')
    put('WorkBlindLosses',d['expected_losses_blind_guard'],'/expected_losses_blind_guard');put('WorkBlindUpper',d['upper_blind_guard'],'/upper_blind_guard','.4f')
    put('WorkUpperZero',d['upper_by_losses']['0'],'/upper_by_losses/0','.4f');put('WorkUpperTen',d['upper_by_losses']['10'],'/upper_by_losses/10','.4f')
    d,put=group('e15_corpus')
    put('CorpusConfigs',d['configurations'],'/configurations');put('CorpusWithRails',d['with_rails'],'/with_rails');put('CorpusFlows',d['distinct_flows'],'/distinct_flows')
    put('CorpusMedian',d['median_stages'],'/median_stages','.0f');put('CorpusMax',d['max_stages'],'/max_stages')
    put('CorpusLlm',d['kinds']['llm_prompted'],'/kinds/llm_prompted');put('CorpusService',d['kinds']['model_or_service'],'/kinds/model_or_service')
    put('CorpusDeterministic',d['kinds']['deterministic'],'/kinds/deterministic');put('CorpusTransforming',d['kinds']['transforming'],'/kinds/transforming')
    put('CorpusAllDet',d['all_deterministic'],'/all_deterministic');put('CorpusAllStat',d['all_statistical'],'/all_statistical');put('CorpusTool',d['with_tool_rails'],'/with_tool_rails')
    d,put=group('e13_cases')
    labels={'devagent':'DevAgent','devagent_exposed_judge':'DevAgent, exposed judge','llamafirewall_composition':'LlamaFirewall',
            'nemo_rails':'NeMo rails','camel_style':'CaMeL-style','trust_or_escalate':'Trust or Escalate','conformal_arbitrage':'Conformal Arbitrage'}
    tex=lambda name:'\\ob{'+name.replace('_','\\_')+'}'
    by={r['case']:r for r in d}
    rows=[]
    for key,label in labels.items():
        r=by[key]
        adverse=r['adversarial']
        if adverse['accepted']:
            text='rests on: '+(', '.join(sorted({tex(x[1]) for x in adverse['necessary']})) or ', '.join(sorted({tex(x[1]) for x in adverse['residual']})) or 'nothing assumed')
        else:
            text='supply: '+', '.join(sorted({tex(x[1]) for x in r['repair_adversarial']['supply']}))
            if r['repair_adversarial']['uncovered']:
                text+='; goals with no stage: '+', '.join(sorted(tex(x) for x in r['repair_adversarial']['uncovered']))
        rows.append(f"{label} & {'accepted' if r['benign']['accepted'] else 'rejected'} & {'accepted' if adverse['accepted'] else 'rejected'} & {adverse['routes']} & {text} \\\\")
    tables['cases']='\n'.join(rows)
    env,put=group('environment')
    put('EnvVersionPython',env['python'],'/python');put('EnvCpus',env['cpus'],'/cpus');put('EnvZthree',env['versions']['z3-solver'],'/versions/z3-solver');put('EnvCvc',env['versions']['cvc5'],'/versions/cvc5')


def generate():
    summary=read_json(ROOT/'results/processed/summary.json')
    source_hash=hashlib.sha256((ROOT/'results/processed/summary.json').read_bytes()).hexdigest()
    macros={}
    lines=['% GENERATED by scripts/make_macros.py. Do not hand-edit.']

    def macro(name,value,pointer,fmt='.2f'):
        rendered=format(value,fmt) if isinstance(value,(int,float)) else str(value)
        if fmt=='d' and isinstance(value,int) and abs(value)>=10000:
            rendered=format(value,',d').replace(',','{,}')  # IEEE style, safe in text and math
        command='res'+name
        if command in macros:raise ValueError('duplicate macro '+command)
        macros[command]={'value':value,'rendered':rendered,'source':'results/processed/summary.json','pointer':pointer,'source_sha256':source_hash}
        lines.append('\\newcommand{\\'+command+'}{'+rendered+'}')
        return '\\'+command+'{}'

    tables={}
    for study,prefix in [('primary','Primary'),('exploratory','Exploratory')]:
        s=summary['studies'][study]
        base=f'/studies/{study}'
        macro(prefix+'Seeds',len(s['seeds']),base+'/seeds#length','d')
        macro(prefix+'TestCount',s['metrics']['test']['checked_quarantine']['n'],base+'/metrics/test/checked_quarantine/n','d')
        macro(prefix+'Records',s['decision_records'],base+'/decision_records','d')
        macro(prefix+'Infeasible',sum(x['candidate'] is None for x in s['selections']),base+'/selections#infeasible','d')
        macro(prefix+'Runtime',s['runtime_seconds'],base+'/runtime_seconds','.2f')
        macro(prefix+'Replications',s['coverage']['n'],base+'/coverage/n','d')
        macro(prefix+'Coverage',100*s['coverage']['coverage'],base+'/coverage/coverage#percent')
        macro(prefix+'CoverageLo',100*s['coverage']['coverage_ci'][0],base+'/coverage/coverage_ci/0#percent')
        macro(prefix+'CoverageHi',100*s['coverage']['coverage_ci'][1],base+'/coverage/coverage_ci/1#percent')
        macro(prefix+'FiniteTestBelow',s['coverage']['finite_test_frequency_below_target'],base+'/coverage/finite_test_frequency_below_target','d')
        macro(prefix+'CheckerTP',s['checker']['tp'],base+'/checker/tp','d')
        macro(prefix+'CheckerTN',s['checker']['tn'],base+'/checker/tn','d')
        macro(prefix+'CheckerFP',s['checker']['fp'],base+'/checker/fp','d')
        macro(prefix+'CheckerFN',s['checker']['fn'],base+'/checker/fn','d')
        macro(prefix+'CheckerUniqueInvalid',s['checker']['unique_invalid'],base+'/checker/unique_invalid','d')
        macro(prefix+'CheckerUniqueClean',s['checker']['unique_clean'],base+'/checker/unique_clean','d')
        macro(prefix+'CheckerMax',max(x['median_us'] for x in s['checker']['scalability']),base+'/checker/scalability#max-median-us')
        macro(prefix+'SynthInstances',s['synthesis']['instances'],base+'/synthesis/instances','d')
        macro(prefix+'SynthMismatches',s['synthesis']['mismatches'],base+'/synthesis/mismatches','d')
        macro(prefix+'SeedFirst',min(s['seeds']),base+'/seeds#min','d')
        macro(prefix+'SeedLast',max(s['seeds']),base+'/seeds#max','d')
        macro(prefix+'Commit',s['environment']['code_commit'][:7],base+'/environment/code_commit#short')
        macro(prefix+'DistinctPolicies',s['grid_structure']['distinct_policies'],base+'/grid_structure/distinct_policies','d')
        macro(prefix+'DistinctRiskLevels',s['grid_structure']['distinct_risk_levels'],base+'/grid_structure/distinct_risk_levels','d')
        macro(prefix+'MinBound',100*s['grid_structure']['min_upper_risk'],base+'/grid_structure/min_upper_risk#percent','.1f')
        rows=[]
        for index,(policy,label) in enumerate(LABELS.items()):
            m=s['metrics']['test'][policy]
            stem=prefix+''.join(x.title() for x in policy.split('_'))
            path=base+'/metrics/test/'+policy
            risk=macro(stem+'Risk',100*m['joint_risk'],path+'/joint_risk#percent')
            utility=macro(stem+'Utility',100*m['benign_utility'],path+'/benign_utility#percent')
            cost=macro(stem+'Cost',m['modeled_cost_units'],path+'/modeled_cost_units')
            p95=macro(stem+'Cpu',m['cpu_p95_us'],path+'/cpu_p95_us')
            hard=macro(stem+'Hard',m['hard_violations'],path+'/hard_violations','d')
            rows.append(f'{label} & {risk} & {utility} & {cost} & {p95} & {hard} \\\\')
        tables[study]='\n'.join(rows)
        for policy in ['checked_quarantine','checked_uncalibrated','naive_with_sink','rules_only']:
            population=s['analytic_fixture_population'][policy]
            stem=prefix+''.join(x.title() for x in policy.split('_'))+'Population'
            for field,suffix,scale in [('joint_risk','Risk',100),('benign_utility','Utility',100),('modeled_cost_units','Cost',1)]:
                macro(stem+suffix,population[field]*scale,base+'/analytic_fixture_population/'+policy+'/'+field)
        for comparison in s['comparisons']:
            stem=prefix+''.join(x.title() for x in comparison['baseline'].split('_'))+'Comparison'
            path=base+'/comparisons#baseline='+comparison['baseline']
            for field,suffix,transform,fmt in [('risk_difference','Diff',100,'.2f'),('holm_p','P',1,'.5f'),('A12_lower_risk','A',1,'.2f')]:
                macro(stem+suffix,comparison[field]*transform,path+'/'+field,fmt)
            for index,suffix in [(0,'Lo'),(1,'Hi')]:
                macro(stem+suffix,comparison['risk_difference_ci'][index]*100,path+'/risk_difference_ci/'+str(index)+'#percent')
        checked=s['metrics']['test']['checked_quarantine']
        for layer,suffix in [('L2','Two'),('L3','Three')]:
            macro(prefix+'CheckedReach'+suffix,100*checked['reach_rates'][layer],base+'/metrics/test/checked_quarantine/reach_rates/'+layer+'#percent','.1f')
        macro(prefix+'CheckedCpuMedian',checked['cpu_p50_us'],base+'/metrics/test/checked_quarantine/cpu_p50_us','.1f')
        macro(prefix+'NaiveWithSinkCpuMedian',s['metrics']['test']['naive_with_sink']['cpu_p50_us'],base+'/metrics/test/naive_with_sink/cpu_p50_us','.1f')
        macro(prefix+'Certified',sum(x['candidate'] is not None for x in s['selections']),base+'/selections#certified','d')
        bounds=[x['bounds'] for x in s['selections']]
        macro(prefix+'BoundMin',100*min(min(b) for b in bounds),base+'/selections/*/bounds#min-percent','.1f')
        macro(prefix+'BoundMax',100*max(min(b) for b in bounds),base+'/selections/*/bounds#max-of-min-percent','.1f')
        misses=[min(x['calibration_misses']) for x in s['selections']]
        macro(prefix+'MissMin',min(misses),base+'/selections/*/calibration_misses#min','d')
        macro(prefix+'MissMax',max(misses),base+'/selections/*/calibration_misses#max','d')
        adaptive=s['adaptive']
        macro(prefix+'AdaptiveSuccessSeeds',adaptive['checked_quarantine']['successful_seeds'],base+'/adaptive/checked_quarantine/successful_seeds','d')
        macro(prefix+'AdaptiveQueries',adaptive['checked_quarantine']['queries'],base+'/adaptive/checked_quarantine/queries','d')
        macro(prefix+'AdaptiveAllSucceed',int(all(v['successful_seeds']==len(s['seeds']) and v['queries']==len(s['seeds']) for v in adaptive.values())),base+'/adaptive#all-first-query','d')
        macro(prefix+'SynthLpOk',int(s['synthesis']['mismatches']==0),base+'/synthesis/mismatches#zero','d')
        macro(prefix+'CoverageCovered',s['coverage']['true_risk_bound_covered'],base+'/coverage/true_risk_bound_covered','d')
        shifted=s['metrics']['shift']['checked_quarantine']
        macro(prefix+'ShiftRisk',100*shifted['joint_risk'],base+'/metrics/shift/checked_quarantine/joint_risk#percent')
        accepted=s['metrics']['test']['checked_quarantine']['accepted_conditional_risk']
        if accepted is not None:macro(prefix+'AcceptedConditionalRisk',accepted*100,base+'/metrics/test/checked_quarantine/accepted_conditional_risk#percent')
    family_rows=[]
    families={'benign':'Benign report','benign_security':'Benign security text','exfiltration':'Secret exfiltration',
              'production_delete':'Production deletion','direct_injection':'Direct injection',
              'implicit_patch':'Implicit patch','judge_injection':'Judge targeting'}
    for family,label in families.items():
        stem='Family'+''.join(x.title() for x in family.split('_'))
        primary=summary['studies']['primary']['family_metrics'][family]['checked_quarantine']
        exp=summary['studies']['exploratory']['family_metrics'][family]
        n1=macro(stem+'Primary',primary['n'],f'/studies/primary/family_metrics/{family}/checked_quarantine/n','d')
        n2=macro(stem+'Exploratory',exp['checked_quarantine']['n'],f'/studies/exploratory/family_metrics/{family}/checked_quarantine/n','d')
        mass=macro(stem+'Mass',100*summary['studies']['exploratory']['family_weights'][family],f'/studies/exploratory/family_weights/{family}#percent','.0f')
        vals=[]
        for policy,suffix in [('naive_with_sink','Naive'),('checked_quarantine','Checked')]:
            m=exp[policy]
            vals.append(macro(stem+suffix,100*m['allowed']/m['n'],f'/studies/exploratory/family_metrics/{family}/{policy}/allowed#fraction-percent','.0f'))
        family_rows.append(f'{label} & {n1} & {n2} & {mass} & {vals[0]} & {vals[1]} \\\\')
    tables['family']='\n'.join(family_rows)
    macro('FormalStates',summary['formal']['invariant_states'],'/formal/invariant_states','d')
    macro('FormalInstances',summary['sanity']['instances'],'/sanity/instances','d')
    macro('PrismCases',summary['prism']['cases'],'/prism/cases','d')
    ex=summary['studies']['exploratory']['selections'][0]
    position=summary['design']['thresholds'].index(ex['candidate']['threshold'])
    for name,value,pointer,fmt in [
        ('ExampleSeed',ex['seed'],'/studies/exploratory/selections/0/seed','d'),
        ('ExampleMisses',ex['calibration_misses'][position],f'/studies/exploratory/selections/0/calibration_misses/{position}','d'),
        ('ExampleCalibrationCount',ex['n'],'/studies/exploratory/selections/0/n','d'),
        ('ExampleThreshold',ex['candidate']['threshold'],'/studies/exploratory/selections/0/candidate/threshold','.2f'),
        ('ExampleBound',100*ex['upper_risk'],'/studies/exploratory/selections/0/upper_risk#percent','.2f'),
        ('BaselineThreshold',summary['studies']['primary']['baseline_threshold'],'/studies/primary/baseline_threshold','.2f'),
        ('CoverageTarget',100*summary['design']['coverage_target'],'/design/coverage_target#percent','.0f'),
        ('CoverageCalibrationCount',summary['design']['coverage_n_cal'],'/design/coverage_n_cal','d'),
        ('CoverageTestCount',summary['design']['coverage_n_test'],'/design/coverage_n_test','d'),
        ('DependenceSamples',summary['studies']['primary']['correlation']['samples_per_cell'],'/studies/primary/correlation/samples_per_cell','d')]:
        macro(name,value,pointer,fmt)
    for index,name in enumerate(['First','Second','Third']):
        macro('Dependence'+name,summary['studies']['primary']['correlation']['conditional_miss_rates'][index],f'/studies/primary/correlation/conditional_miss_rates/{index}')
    points=summary['studies']['primary']['correlation']['points']
    macro('DependencePoints',' '.join(f'({x:.2f},{y:.4f})' for x,y in points),'/studies/primary/correlation/points')
    macro('DependenceGap',summary['studies']['primary']['correlation']['max_absolute_sampling_gap'],'/studies/primary/correlation/max_absolute_sampling_gap','.4f')
    scaling=summary['studies']['primary']['checker']['scalability']
    for depth,name in [(2,'Two'),(4,'Four'),(6,'Six')]:
        pts=sorted((x['policies'],x['median_us']/1000) for x in scaling if x['layers']==depth)
        macro('CheckerScaling'+name,' '.join(f'({p},{t:.4f})' for p,t in pts),'/studies/primary/checker/scalability#layers='+str(depth)+'-ms')
    import math
    xs=[math.log((x['layers']-1)*x['policies']) for x in scaling if x['policies']>=50]
    ys=[math.log(x['median_us']) for x in scaling if x['policies']>=50]
    mx,my=sum(xs)/len(xs),sum(ys)/len(ys)
    slope=sum((a-mx)*(b-my) for a,b in zip(xs,ys))/sum((a-mx)**2 for a in xs)
    macro('CheckerSlope',slope,'/studies/primary/checker/scalability#loglog-slope-vs-edges-policies>=50','.1f')
    xs=[math.log(x['policies']) for x in scaling if x['policies']>=50 and x['layers']==6]
    ys=[math.log(x['median_us']) for x in scaling if x['policies']>=50 and x['layers']==6]
    mx,my=sum(xs)/len(xs),sum(ys)/len(ys)
    macro('CheckerSlopeSix',sum((a-mx)*(b-my) for a,b in zip(xs,ys))/sum((a-mx)**2 for a in xs),'/studies/primary/checker/scalability#loglog-slope-layers=6-policies>=50','.1f')
    post=read_json(ROOT/'results/processed/post_review.json')
    post_hash=hashlib.sha256((ROOT/'results/processed/post_review.json').read_bytes()).hexdigest()
    def post_macro(name,value,pointer,fmt):
        macro(name,value,pointer,fmt)
        macros['res'+name].update(source='results/processed/post_review.json',source_sha256=post_hash)
    for study,prefix in [('primary','Primary'),('exploratory','Exploratory')]:
        pc=post['provenance_control'][study]
        post_macro(prefix+'ProvRisk',100*pc['test']['joint_risk'],f'/provenance_control/{study}/test/joint_risk#percent','.2f')
        post_macro(prefix+'ProvUtility',100*pc['test']['benign_utility'],f'/provenance_control/{study}/test/benign_utility#percent','.2f')
        post_macro(prefix+'ProvShiftRisk',100*pc['shift']['joint_risk'],f'/provenance_control/{study}/shift/joint_risk#percent','.2f')
        post_macro(prefix+'ProvCost',pc['test']['modeled_cost_units'],f'/provenance_control/{study}/test/modeled_cost_units','.2f')
    eq=post['calibration_equivalence']['exploratory']
    post_macro('CalEquivCompared',eq['compared'],'/calibration_equivalence/exploratory/compared','d')
    post_macro('CalEquivDisagree',eq['disagreements'],'/calibration_equivalence/exploratory/disagreements','d')
    macro('CheckerMaxEdges',max((x['layers']-1)*x['policies'] for x in scaling),'/studies/primary/checker/scalability#max-edges','d')
    macro('CheckerMaxMs',max(x['median_us'] for x in scaling)/1000,'/studies/primary/checker/scalability#max-median-ms','.1f')
    macro('ReplayDecisions',summary['studies']['primary']['decision_records']+summary['studies']['exploratory']['decision_records'],'/studies/*/decision_records#sum','d')
    env=summary['studies']['primary']['environment']
    for name,key in [('EnvPython','python'),('EnvCpuCount','cpu_count'),('EnvPlatform','platform'),('EnvProcessor','processor')]:
        macro(name,env[key],'/studies/primary/environment/'+key,'d')
    for name,key in [('EnvNumpy','numpy'),('EnvScipy','scipy'),('EnvPytest','pytest')]:
        macro(name,env['versions'][key],'/studies/primary/environment/versions/'+key)
    for name,layer in [('CostRules','L1'),('CostScorer','L2'),('CostJudge','L3'),('CostApproval','L4')]:
        macro(name,summary['design']['layer_costs'][layer],'/design/layer_costs/'+layer,'d')
    grid=summary['design']['thresholds']
    macro('ThresholdMin',grid[0],'/design/thresholds/0','.1f')
    macro('ThresholdMax',grid[-1],'/design/thresholds/-1','.1f')
    macro('ThresholdStep',grid[1]-grid[0],'/design/thresholds#step','.1f')
    macro('CoveragePerSeed',summary['design']['coverage_replications_per_seed'],'/design/coverage_replications_per_seed','d')
    macro('CoreCoverage',summary['core_coverage'],'/core_coverage')
    macro('NominalConfidence',100*(1-summary['design']['delta']),'/design/delta#one-minus-percent','.0f')
    macro('PolicyClasses',len(summary['policy_inventory']['policies']),'/policy_inventory/policies#length','d')
    macro('SupportedClasses',sum(x['dsl_fully_supported'] for x in summary['policy_inventory']['policies']),'/policy_inventory/policies#fully-supported','d')
    for name,key,multiplier,fmt in [('RiskBudget','epsilon',100,'.0f'),('ConfidenceFailure','delta',100,'.0f'),
                                  ('CalibrationCount','n_calibration',1,'d'),('DevelopmentCount','n_development',1,'d'),
                                  ('TestPerSeed','n_test',1,'d'),('ShiftPerSeed','n_shift',1,'d'),
                                  ('ThresholdCount','thresholds',1,'d'),('AdaptiveBudget','adaptive_budget',1,'d'),
                                  ('BootstrapCount','bootstrap_replicates',1,'d')]:
        value=summary['design'][key]
        if isinstance(value,list):value=len(value)
        macro(name,value*multiplier,'/design/'+key,fmt)
    verification(macro,macros,tables)
    out=ROOT/'paper/generated'
    out.mkdir(parents=True,exist_ok=True)
    # Keep one content tex file and a single generated macro include. Tables
    # are macros rather than separate authored section/table files.
    for name,rows in tables.items():
        lines.append('\\newcommand{\\res'+name.title()+'Table}{%\n'+rows+'\n}')
    # Macros live inside the single main.tex, between fixed markers.
    tex=ROOT/'paper/main.tex'
    source=tex.read_text(encoding='utf-8')
    head,rest=source.split(BEGIN,1)
    _,tail=rest.split(END,1)
    tex.write_text(head+BEGIN+'\n'+'\n'.join(lines)+'\n'+END+tail,encoding='utf-8')
    (out/'macro_provenance.json').write_text(serialize(macros),encoding='utf-8')
    print(len(macros),'numeric macros generated from raw-derived summary; figures are TikZ in main.tex.')


if __name__=='__main__':generate()
