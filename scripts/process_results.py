"""Deterministically derive aggregates and inference from preserved raw decisions."""
from __future__ import annotations
from collections import defaultdict
import gzip
import json
from pathlib import Path
import sys
import numpy as np
from scipy.stats import beta, wilcoxon
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from tint.calibration import binomial_upper
from experiments.dataset import FAMILIES,WEIGHTS


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def read_lines(path):
    with gzip.open(path,'rt',encoding='utf-8') as stream:
        for line in stream:
            yield json.loads(line)


def serialize(value):
    return json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n'


def proportion_ci(successes,n):
    return [float(beta.ppf(.025,successes,n-successes+1)) if successes else 0.,
            float(beta.ppf(.975,successes+1,n-successes)) if successes<n else 1.]


def bootstrap(values):
    values=np.array(values,dtype=float)
    rng=np.random.default_rng(20261029)
    means=values[rng.integers(0,len(values),size=(10000,len(values)))].mean(axis=1)
    return [float(x) for x in np.quantile(means,[.025,.975])]


def aggregate(rows):
    n=len(rows)
    unsafe=sum(r['unsafe'] for r in rows)
    benign=n-unsafe
    misses=sum(r['unsafe'] and r['allowed'] for r in rows)
    allowed_benign=sum(not r['unsafe'] and r['allowed'] for r in rows)
    allowed=sum(r['allowed'] for r in rows)
    timing=np.array([r['elapsed_ns'] for r in rows],dtype=float)
    return {'n':n,'unsafe':unsafe,'benign':benign,'misses':misses,'allowed':allowed,'joint_risk':misses/n,
            'accepted_conditional_risk':misses/allowed if allowed else None,
            'attack_success':misses/unsafe if unsafe else None,
            'benign_utility':allowed_benign/benign if benign else None,
            'false_block_rate':1-allowed_benign/benign if benign else None,
            'modeled_cost_units':float(np.mean([r['cost_units'] for r in rows])),
            'cpu_p50_us':float(np.quantile(timing,.5)/1000),'cpu_p95_us':float(np.quantile(timing,.95)/1000),
            'cpu_p99_us':float(np.quantile(timing,.99)/1000),
            'hard_violations':sum(r['hard_violation'] for r in rows),
            'reach_rates':{layer:sum(layer in r['layers'] for r in rows)/n for layer in ['L1','L2','L3','L4']}}


def verify_mixture_record(row):
    r=np.r_[0.,row['risks']]
    c=np.r_[1001.,row['costs']]
    w=np.asarray(row['mixture_weights'],dtype=float)
    assert w.shape==r.shape and np.isfinite(w).all()
    assert np.all(w>=-1e-9) and np.all(w<=1+1e-9) and abs(w.sum()-1)<=1e-8
    risk,cost=float(w@r),float(w@c)
    assert risk<=.1+1e-9
    assert abs(risk-row['mixture_risk'])<=1e-8
    assert abs(cost-row['mixture_cost'])<=1e-6
    # Independent vertex enumeration, not a second call to the same LP solver.
    vertices=[c[i] for i in range(len(r)) if r[i]<=.1]
    for i in range(len(r)):
        for j in range(i+1,len(r)):
            if min(r[i],r[j])<=.1<=max(r[i],r[j]) and abs(r[i]-r[j])>1e-12:
                wi=(r[j]-.1)/(r[j]-r[i])
                vertices.append(wi*c[i]+(1-wi)*c[j])
    assert abs(cost-min(vertices))<=1e-6


def study(directory):
    rows=list(read_lines(directory/'decisions.jsonl.gz'))
    grouped=defaultdict(list)
    by_seed=defaultdict(list)
    for row in rows:
        grouped[(row['split'],row['policy'])].append(row)
        by_seed[(row['split'],row['policy'],row['seed'])].append(row)
    metrics={}
    for (split,policy),items in sorted(grouped.items()):
        metrics.setdefault(split,{})[policy]=aggregate(items)
    family_metrics={}
    for family in sorted({r['family'] for r in rows if r['split']=='test'}):
        family_metrics[family]={policy:aggregate([r for r in grouped[('test',policy)] if r['family']==family]) for policy in metrics['test']}
    population={}
    weights=dict(zip(FAMILIES,WEIGHTS))
    for policy in metrics['test']:
        # Verify suffix variations do not alter this program's family decisions.
        assert all(m['allowed'] in {0,m['n']} for family in family_metrics.values() for m in [family[policy]])
        acceptance={family:m[policy]['allowed']/m[policy]['n'] for family,m in family_metrics.items()}
        population[policy]={'joint_risk':sum(weights[f]*acceptance[f] for f in FAMILIES if f not in {'benign','benign_security'}),
                            'benign_utility':sum(weights[f]*acceptance[f] for f in ['benign','benign_security'])/(weights['benign']+weights['benign_security']),
                            'modeled_cost_units':sum(weights[f]*family_metrics[f][policy]['modeled_cost_units'] for f in FAMILIES)}
    seed_metrics={f'{split}/{policy}/{seed}':aggregate(items) for (split,policy,seed),items in sorted(by_seed.items())}
    seeds=sorted({r['seed'] for r in rows})
    comparisons=[]
    checked='checked_quarantine'
    for policy in sorted(metrics['test']):
        if policy==checked:continue
        a=np.array([seed_metrics[f'test/{checked}/{seed}']['joint_risk'] for seed in seeds])
        b=np.array([seed_metrics[f'test/{policy}/{seed}']['joint_risk'] for seed in seeds])
        differences=a-b
        p=float(wilcoxon(differences,zero_method='wilcox',method='auto').pvalue) if np.any(differences) else 1.
        a12=float(np.mean((a[:,None]<b[None,:])+.5*(a[:,None]==b[None,:])))
        utility_diffs=[seed_metrics[f'test/{checked}/{seed}']['benign_utility']-seed_metrics[f'test/{policy}/{seed}']['benign_utility'] for seed in seeds]
        comparisons.append({'baseline':policy,'risk_difference':float(differences.mean()),'risk_difference_ci':bootstrap(differences),
                            'utility_difference':float(np.mean(utility_diffs)),'utility_difference_ci':bootstrap(utility_diffs),
                            'wilcoxon_p':p,'A12_lower_risk':a12})
    previous=0.
    for rank,index in enumerate(sorted(range(len(comparisons)),key=lambda i:comparisons[i]['wilcoxon_p'])):
        previous=max(previous,min(1,(len(comparisons)-rank)*comparisons[index]['wilcoxon_p']))
        comparisons[index]['holm_p']=previous
    coverage=list(read_lines(directory/'coverage.jsonl.gz'))
    true_covered=target_covered=test_below=0
    for row in coverage:
        k=len(row['bounds'])
        recomputed=[binomial_upper(count,row['n_calibration'],.05/k) for count in row['calibration_counts']]
        assert np.allclose(recomputed,row['bounds'],rtol=0,atol=1e-14)
        selected=row['selected']
        if selected is None:
            true_covered+=1;target_covered+=1;test_below+=1
        else:
            true_covered+=row['true_risks'][selected]<=row['bounds'][selected]
            target_covered+=row['true_risks'][selected]<=.1
            test_below+=row['test_counts'][selected]/row['n_test']<=.1
    checker=list(read_lines(directory/'checker.jsonl.gz'))
    tp=sum(r['invalid'] and r['rejected'] for r in checker)
    fp=sum(not r['invalid'] and r['rejected'] for r in checker)
    fn=sum(r['invalid'] and not r['rejected'] for r in checker)
    tn=sum(not r['invalid'] and not r['rejected'] for r in checker)
    clean=[r for r in checker if not r['invalid']]
    scalability=[{'policies':count,'layers':depth,'median_us':float(np.median([r['elapsed_ns'] for r in clean if r['policies']==count and r['layers']==depth])/1000)}
                 for count in sorted({r['policies'] for r in clean}) for depth in sorted({r['layers'] for r in clean})]
    synthesis=read_json(directory/'synthesis.json')
    for row in synthesis:
        if 'calibration_counts' in row:
            actual=[binomial_upper(c,row['n_calibration'],.05/len(row['bounds'])) for c in row['calibration_counts']]
            assert np.allclose(actual,row['bounds'],rtol=0,atol=1e-14)
        feasible=[i for i,v in enumerate(row['bounds']) if v<=.1]
        expected=min(feasible,key=lambda i:(row['costs'][i],str(i))) if feasible else None
        assert expected==row['exhaustive']
        verify_mixture_record(row)
    corr=list(read_lines(directory/'correlation.jsonl.gz'))
    for row in corr:
        assert sum(row['pattern_counts'])==row['samples']
        assert row['empirical_joint']==row['pattern_counts'][-1]/row['samples']
    adaptive=list(read_lines(directory/'adaptive.jsonl.gz'))
    adaptive_summary={policy:{'queries':sum(r['policy']==policy for r in adaptive),
                             'successful_seeds':sum(any(r['policy']==policy and r['seed']==seed and r['allowed'] for r in adaptive) for seed in seeds)} for policy in metrics['test']}
    selections=read_json(directory/'selections.json')
    config=read_json(ROOT/'experiments/configs/pilot.json')
    for row in selections:
        actual=[binomial_upper(c,row['n'],config['delta']/len(row['bounds'])) for c in row['calibration_misses']]
        assert np.allclose(actual,row['bounds'],rtol=0,atol=1e-14)
        feasible=[i for i,v in enumerate(actual) if v<=config['epsilon']]
        if row['candidate']:
            best=min(feasible,key=lambda i:(row['calibration_cost_mean'][i],f"threshold-{config['thresholds'][i]}"))
            assert row['candidate']['threshold']==config['thresholds'][best]
        else:
            assert not feasible
    # Behaviorally distinct grid points: thresholds with equal calibration
    # losses and costs are the same policy on this fixture law.
    grid={'distinct_policies':max(len(set(zip(r['calibration_misses'],r['calibration_cost_mean']))) for r in selections),
          'distinct_risk_levels':max(len(set(r['calibration_misses'])) for r in selections),
          'min_upper_risk':min(min(r['bounds']) for r in selections)}
    return {'scope':read_json(directory/'run.json')['scope'],'seeds':seeds,'decision_records':len(rows),
            'baseline_threshold':next(r['threshold'] for r in rows if r['policy']=='classifier_only'),
            'metrics':metrics,'family_metrics':family_metrics,'family_weights':weights,'analytic_fixture_population':population,
            'seed_metrics':seed_metrics,'comparisons':comparisons,'selections':selections,'grid_structure':grid,
            'environment':read_json(directory/'environment.json'),
            'coverage':{'n':len(coverage),'true_risk_bound_covered':int(true_covered),'coverage':true_covered/len(coverage),
                        'coverage_ci':proportion_ci(true_covered,len(coverage)),'target_covered':int(target_covered),
                        'finite_test_frequency_below_target':int(test_below)},
            'checker':{'tp':tp,'fp':fp,'fn':fn,'tn':tn,'precision':tp/(tp+fp),'recall':tp/(tp+fn),'scalability':scalability,
                       'unique_invalid':len({(r['policies'],r['layers'],r['mutation']) for r in checker if r['invalid']}),
                       'unique_clean':len({(r['policies'],r['layers']) for r in checker if not r['invalid']})},
            'synthesis':{'instances':len(synthesis),'mismatches':sum(r['selected']!=r['exhaustive'] for r in synthesis),
                         'original_calibration_counts_available':all('calibration_counts' in r for r in synthesis)},
            'correlation':{'cells':len(corr),'points':[[r['mixture_weight'],r['empirical_joint']] for r in corr],'max_absolute_sampling_gap':max(abs(r['empirical_joint']-r['model_joint']) for r in corr),
                           'conditional_miss_rates':corr[0]['miss_rates'],'samples_per_cell':corr[0]['samples']},
            'adaptive':adaptive_summary,
            'adaptive_scope':'uncertified decision-core functions at fixed threshold; checked_quarantine raw label is not GuardRuntime or its selected certificate',
            'runtime_seconds':read_json(directory/'run.json')['elapsed_seconds']}


def process():
    output={'design':read_json(ROOT/'experiments/configs/pilot.json'),
            'studies':{'primary':study(ROOT/'results/raw'),'exploratory':study(ROOT/'results/raw/exploratory_numeric')},
            'formal':read_json(ROOT/'results/raw/formal.json'),'sanity':read_json(ROOT/'results/raw/formal_sanity.json'),
            'prism':{'cases':len(read_json(ROOT/'results/raw/prism.json')['runs']),'properties_per_case':2}}
    # Outcomes are interpretation, separated from numerical aggregates.
    output['hypotheses']={
        'H1':{'result':'supported within tested typed semantics','limitation':'finite abstraction is not a runtime refinement proof'},
        'H2':{'result':'supported for planted mutation classes','limitation':'not real-world specification precision/recall'},
        'H3':{'result':'supported for the synthetic iid law','limitation':'not an adaptive deployment guarantee'},
        'H4':{'result':'supported; strong naive-with-sink control also prevents Tj','limitation':'scripted counterexample'},
        'H5':{'result':'supported within the finite family','limitation':'no unrestricted n-layer optimum/approximation claim'},
        'H6':{'result':'inconclusive for useful safety-utility improvement in primary; exploratory tradeoffs reported','limitation':'primary method blocks all; exploratory follows disclosed bug fix'},
        'H7':{'result':'inconclusive/not run','limitation':'no real LLM or external benchmark execution'},
        'H8':{'result':'refuted','limitation':'only the two declared deterministic policy classes fully supported by the DSL'}}
    inventory=ROOT/'results/raw/policy_inventory.json'
    if inventory.exists():output['policy_inventory']=read_json(inventory)
    test_coverage=ROOT/'results/raw/coverage_tests.json'
    if test_coverage.exists():output['core_coverage']=read_json(test_coverage)['totals']['percent_covered']
    return output


if __name__=='__main__':
    result=process()
    path=ROOT/'results/processed/summary.json'
    encoded=serialize(result)
    if '--verify' in sys.argv:
        assert path.read_text(encoding='utf-8')==encoded,'processed outputs differ from raw re-derivation'
        print('Processed summary re-derived byte-for-byte from both preserved raw runs.')
    else:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(encoded,encoding='utf-8')
        for name,s in result['studies'].items():
            print(name,'coverage',s['coverage'],'checked test',s['metrics']['test']['checked_quarantine'])
