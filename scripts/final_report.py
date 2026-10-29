"""Generate the project report from actual results and unchanged reviewer scores."""
from __future__ import annotations
import csv
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]


def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))


def main():
    summary=load('results/processed/summary.json')
    scores=[]
    for round_number in range(1,5):
        for reviewer in ['R1','R2','R3']:
            path=ROOT/'archive/reviews'/f'round{round_number}'/(reviewer+'.md')
            found={}
            for line in path.read_text(encoding='utf-8').splitlines():
                match=re.match(r'\|\s*([^|]+)\|\s*(\d)(?:/5)?\s*\|',line)
                if not match:continue
                key=match[1].strip().lower()
                if key in {'se relevance','relevance'}:key='relevance'
                if key in {'novelty','rigor','relevance','transparency','presentation'}:found[key]=int(match[2])
            assert len(found)==5,(path,found)
            scores.append({'round':round_number,'reviewer':reviewer,**found,'recommendation':'reject',
                           'source':path.relative_to(ROOT).as_posix()})
    with (ROOT/'archive/reviews/score_history.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(scores[0]))
        writer.writeheader();writer.writerows(scores)
    reader=(ROOT/'archive/student_review/reading_log.md').read_text(encoding='utf-8')
    initial=[int(x) for x in re.findall(r'^- \*\*.*?— ([0-3])\.\*\*',reader,re.M)]
    reassessment=(ROOT/'archive/student_review/reassessment.md').read_text(encoding='utf-8')
    revised=[int(x) for x in re.findall(r'^\d+\. \*\*.*?, ([0-3])\.\*\*',reassessment,re.M)]
    assert len(initial)==103 and len(revised)==28 and max(revised)<=1
    primary=summary['studies']['primary'];exploratory=summary['studies']['exploratory']
    p=primary['metrics']['test']['checked_quarantine']
    e=exploratory['metrics']['test']['checked_quarantine']
    count_refs=len(load('docs/literature/metadata.json'))
    review_rows='\n'.join(f"| {x['round']} | {x['reviewer']} | {x['novelty']} | {x['rigor']} | {x['relevance']} | {x['transparency']} | {x['presentation']} | Reject |" for x in scores)
    hypothesis_rows='\n'.join(f"| {key} | {value['result']} | {value['limitation']} |" for key,value in summary['hypotheses'].items())
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    report=f'''# Final report — local pilot, 2026-10-29 UTC

The research idea has been developed into a scoped formal framework, executable
prototype, reproducible local evaluation and IEEE-format manuscript. **The full
TSE effectiveness objective is not achieved.** All final automated referees
recommend rejection: substantial novelty and independent real-agent evidence
remain unestablished. No result, reviewer score, human study or publication is
invented to satisfy the master prompt. This is a useful research starting point,
not a production guard or submission-ready validation.

## Deliverables

- [Paper PDF](../paper/main.pdf), [single authored LaTeX source](../paper/main.tex),
  [bibliography](../paper/references.bib), generated result macros and vector figures.
- [Artifact guide](../ARTIFACT.md), [quick start](../README.md), exact Python locks,
  Docker smoke recipe (unvalidated engine), core CI workflow (not remotely run).
- [Framework/proofs](../formal/FRAMEWORK.md), real PRISM model/transcripts,
  independent finite checks and seeded sanity tests; no Lean/Isabelle proof.
- [Library](../src/tint): immutable actions/provenance, closed contract DSL,
  exact fixed-topology checks, deterministic sink, structured judge interface,
  confidence/configuration binding, calibration and finite-family synthesis.
- [Preregistration](../experiments/PREREGISTRATION.md), local tag `prereg-v1`,
  [amendments](../experiments/AMENDMENTS.md), datasheet and benchmark code-license audit.
- Original and exploratory compressed trace/decision logs, raw-derived
  [summary](../results/processed/summary.json), file-hash manifest and semantic replay.
- Four rounds of three independent automated reviews, response letters and
  actual latexdiff PDFs; fresh-context student logs and reassessment.
- [Next substantive study](NEXT_STUDY.md), stating a falsifiable path toward a
  stronger contribution without asserting unverified novelty.

## Actual results and interpretation

The two studies preserve {primary['decision_records']:,} and
{exploratory['decision_records']:,} per-decision records, respectively,
including development, test and shift replays of seven toy comparators. Each
test split has {p['n']:,} proposals; repeated identifier suffixes do not create
independent semantic tasks. The authored fixture law is deliberately simple.

The primary candidate family was uncertifiable in every seed. Its checked
runtime has {100*p['joint_risk']:.2f}% joint unsafe acceptance and
{100*p['benign_utility']:.2f}% benign utility because it denies uncertified actions.
That is a negative service-utility result, not useful Pareto superiority.

After a disclosed floating-point boundary correction, a separate fresh-seed
exploratory replication has {100*e['joint_risk']:.2f}% joint unsafe acceptance,
{100*e['benign_utility']:.2f}% benign utility and
{100*e['accepted_conditional_risk']:.2f}% unsafe fraction among accepted proposals.
The uncalibrated checked control makes identical decisions. Its designed
all-attack encoded shift is accepted at
{100*exploratory['metrics']['shift']['checked_quarantine']['joint_risk']:.2f}%.
These observations do not establish learned-guard effectiveness or robustness.

A separate known nested-loss law gives {100*primary['coverage']['coverage']:.2f}%
true-risk bound coverage over {primary['coverage']['n']:,} calibration replications,
with exact interval [{100*primary['coverage']['coverage_ci'][0]:.2f}%,
{100*primary['coverage']['coverage_ci'][1]:.2f}%]. This is static iid synthetic
coverage, not a bound on an adaptive deployment. The original search target
was an uncertified fixed-threshold core, mislabeled checked_quarantine; the
attribution is corrected without rewriting raw observations. First-query
success supplies no observed response-informed adaptation.

The restricted DSL fully supports only the two declared deterministic rules;
semantic injection is a statistical proxy and path confinement/spending are
unsupported. The claim of full expressiveness is refuted. Theoretical risk
accounting and finite-family selection are scoped standard constructions,
not claimed new mathematical laws.

## RQs and hypotheses

RQ I has scoped definitions, conditional proofs, canonical countermodel,
syntactic obligation checking and mutation/inventory evidence. It does not
provide general decomposition or a proved implementation/adapter refinement.
RQ II has corrected route versus veto bounds, explicit dependence premises,
calibration utilities, conditional escalation optimality, and finite-family
experiments. RQ III has local feasibility/negative evidence only; practical
real-agent engineering value remains inconclusive.

| ID | Recorded outcome | Scope/limitation |
|---|---|---|
{hypothesis_rows}

## Deviations and corrections

- Literature is a scoping review with {count_refs} bibliographically verified
  primary-source records, not an exhaustive systematic review. Broad records
  were abstract-screened; closest-work full-text comparison was strengthened
  during the project. Initial log wording overstated that depth at the initial
  gate and is corrected here. No blanket first-cascade/contracts novelty claim.
- A1 preserves primary arithmetic/infeasibility and runs numeric correction
  on fresh seeds as exploratory. No thresholds or risk budgets were retuned.
- A2 labels post-review family/population/conditional-risk analyses descriptive
  exploratory and corrects search attribution. LP checks and read-only replay
  strengthen validation without creating new held-out outcomes.
- Original synthesis calibration counts were not logged. Those original bounds
  cannot be recalibrated from their records; amended instrumentation retains
  counts. This provenance limitation remains disclosed.
- Runtime hardening rejects unknown mandatory predicates/extra edges, enforces
  a confidence budget and versions input bounds. Historical scorers remain
  frozen; their CPU times do not describe the hardened default.
- Missing real models, official baselines, external datasets, human pilot,
  actual inference costs and meaningful adaptive attacks are not relabeled as
  completed experiments. Docker execution and archival publication are absent.

## Reviewer history (reported without adjustment)

Scores are each referee's 1–5 ratings; automated development critiques are not
independent human peer review. The four-round stopping limit was reached
without rubric convergence. All final recommendations remain reject.

| Round | Referee | Novelty | Rigor | SE relevance | Transparency | Presentation | Recommendation |
|---|---|---|---|---|---|---|---|
{review_rows}

Technical/reporting defects were repaired. Residual major concerns require new
research: a distinctive benefit over competent matched controls, independently
authored real-agent tasks and learned guards, meaningful attack evaluation,
and stronger data-flow/executor assurance. No additional seed sampling of the
same scripted law resolves these concerns.

## Student-reader outcome

The fresh automated reader assessed {len(initial)} paragraph/definition/proof/
caption entries, with {sum(x>=2 for x in initial)} initially scoring 2 or 3.
After substantive rewrites, every one of those {len(revised)} entries scores
0 or 1. The reader correctly reconstructs the different canonical exfiltration
and empirical patch cases, theorem premises, risk denominators, optimization
objective, calibration mechanism and scoped results. Initial scores remain
unchanged in the preserved log. Optional score-1 precision edits followed;
this is a clarity pass, not a human usability study or scientific endorsement.

## Reproduction and checks actually executed

- 56 tests passed, including provenance/approval/contract/certificate faults,
  numeric boundary and independent LP-evidence tampering. Recorded core
  statement/branch coverage is {summary['core_coverage']:.2f}%.
- Real PRISM checks {summary['prism']['cases']} canonical configurations and both
  reachability properties; independent enumeration covers
  {summary['formal']['invariant_states']} hard-predicate cases and seeded
  probability sanity tests cover {summary['sanity']['instances']:,} instances.
- Raw summaries re-derive byte-for-byte. Read-only replay validates all
  {primary['decision_records']+exploratory['decision_records']:,} historical decisions
  against trace identities/configurations/non-timing semantics. Mixture weights,
  constraints and objectives are checked against separate vertex enumeration.
- Full exact-lock installation succeeded in a fresh Python environment. The
  complete `tasks.py all` pipeline passed in a separate detached checkout,
  including real PRISM, both historical instruments, analyses, PDF and checks.
  Non-timing scientific metrics match; timing/environment bytes need not.
  See [author reproduction record](../results/reproduction_check.json).
- `verify-paper` checks generated empirical source values, bibliography
  records, notation registry, cross-references and extractable layout. It
  does not prove the provenance of every PDF glyph or semantic notation
  consistency. Mathematical constants and structural/citation numbers have
  different provenance. Rendered PDF pages were visually inspected.
- Git attributes preserve recorded JSON/CSV bytes and normalize source line
  endings for portable hash verification. Original experiment files remain
  original observations; only current unit-test coverage records are refreshed.

## Section-zero compliance checklist

- [x] No fabricated experiment, citation, proof mechanization or favorable score.
- [x] Negative primary, arithmetic correction, shift failure and unavailable
  evidence reported rather than hidden.
- [x] Empirical paper values generated from raw-derived results with macro
  provenance and file hashes; mathematical constants come from specification/proofs.
- [~] Number verification is source-level. The literal every-PDF-glyph/CI claim
  is not established; remote CI was written but not run.
- [x] All bibliography entries have opened-source verification records;
  unverified seed identities are not invented.
- [x] Empirical studies use seeded replications and a frozen protocol; changes
  are amended/labeled, and originals preserved.
- [~] Exact Python locks and tool provenance provided and tested locally;
  Docker image and cross-platform production deployment remain unvalidated.
- [x] Phase commits/logs and review/student records retained. Scoped gate
  qualifications and unfulfilled full-study requirements are explicit.
- [x] Attacks remain local toy inputs, secrets artificial, no human participants,
  no access-condition acceptance or third-party exploit publication.
- [x] Blockers/limits documented, with feasible substitute execution and honest
  final disclosure.
- [ ] Full external/real-model TSE evaluation, general refinement, all ablations,
  complete policy language and independently demonstrated novelty.
- [ ] Reviewer convergence, remote release, Zenodo DOI, production readiness.

## Release state

This is a local **v0.1.0 pilot**, not the requested completed-research v1.0.
No remote push/release or DOI was made. The original definition of done remains
partly unmet; reasons and the next substantive study are stated above.
Analysis baseline before this generated report: `{commit}`. The release tag
identifies the final local commit; raw records identify actual execution commits.
'''
    (ROOT/'docs/FINAL_REPORT.md').write_text(report,encoding='utf-8',newline='\n')
    print('Final report and unaltered score history generated.')


if __name__=='__main__':main()
