"""Build review indexes from opened primary-source metadata and explicit annotations."""
from __future__ import annotations
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANNOTATIONS = {
 'contracts': ('Conditional contract satisfaction; see closest-work analysis', 'unknown', 'y', 'y', 'y', 'y', 'unknown', 'reported'),
 'cascades': ('Selective/cascade prediction; statistical scope differs by source', 'routing or inference cost', 'y', 'unknown', 'unknown', 'unknown', 'unknown', 'reported'),
 'guards': ('Empirical detection quality; no deployment certificate inferred from abstract', 'inference overhead where reported', 'unknown', 'unknown', 'unknown', 'unknown', 'unknown', 'reported'),
 'runtime': ('Runtime rule or probabilistic monitoring of specified predicates', 'runtime monitoring', 'unknown', 'y', 'unknown', 'y', 'unknown', 'reported'),
 'isolation': ('Policy-mediated information flow under trusted instrumentation', 'task utility / monitoring', 'unknown', 'y', 'unknown', 'y', 'y', 'reported'),
 'statistics': ('Finite-sample or online risk/coverage under source-specific assumptions', 'calibration samples', 'unknown', 'y', 'y', 'unknown', 'unknown', 'reported'),
 'attacks_evaluation': ('Evaluation or attack construction; not an enforcement guarantee', 'evaluation budget where reported', 'unknown', 'unknown', 'unknown', 'unknown', 'unknown', 'reported'),
 'dual_process': ('Survey taxonomy; not an enforcement theorem', 'qualitative compute', 'unknown', 'unknown', 'unknown', 'unknown', 'unknown', 'survey'),
 'foundations': ('Enforcement of formally specified safety under model assumptions', 'synthesis/runtime', 'unknown', 'y', 'unknown', 'unknown', 'unknown', 'reported'),
 'runtime_extra': ('Structured constraints, monitoring or recovery; source-specific scope', 'runtime/synthesis', 'unknown', 'y', 'unknown', 'y', 'unknown', 'reported'),
 'guards_extra': ('Empirical guardrail engineering or robustness', 'runtime where reported', 'unknown', 'unknown', 'unknown', 'unknown', 'unknown', 'reported'),
 'snowball_candidate': ('Relevant supporting work; abstract screening only, full-text claim audit pending', 'unknown', 'unknown', 'unknown', 'unknown', 'unknown', 'unknown', 'unknown'),
}


def escape(text: str) -> str:
    for before, after in [('&', r'\&'), ('%', r'\%'), ('_', r'\_'), ('#', r'\#')]:
        text = text.replace(before, after)
    return text


def main() -> None:
    records = json.loads((ROOT/'docs/literature/metadata.json').read_text(encoding='utf-8'))
    paper = ROOT/'paper'
    paper.mkdir(exist_ok=True)
    fields = ['key','title','venue','year','category','what_it_guarantees','cost_model','hierarchy',
              'formal_spec','statistical_guarantee','agentic_traces','adaptive_attack_analysis','tool_support','URL','verified','review_depth']
    with (ROOT/'docs/lit_review.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for r in records:
            a = ANNOTATIONS[r['category']]
            writer.writerow(dict(zip(fields, [r['key'],r['title'],'arXiv preprint (versioned primary source)',r['year'],r['category'],
                                             *a,r['url'],'yes','full text for closest five; otherwise abstract screen'])))
    with (paper/'refs_verification.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=['key','URL','date_checked','verified','evidence_sha256'])
        writer.writeheader()
        for r in records:
            writer.writerow(dict(key=r['key'],URL=r['url'],date_checked=r['checked'],verified='yes',evidence_sha256=r['evidence_sha256']))
    entries = []
    for r in records:
        entries.append('@misc{'+r['key']+',\n  title = {{'+escape(r['title'])+'}},\n  author = {'+
                       ' and '.join(escape(a) for a in r['authors'])+'},\n  year = {'+r['year']+'},\n  howpublished = {arXiv preprint},\n  url = {'+r['url']+'}\n}')
    (paper/'references.bib').write_text('\n\n'.join(entries)+'\n', encoding='utf-8')
    print(f'{len(records)} opened-source entries; unknown means unestablished, never absent.')


if __name__ == '__main__':
    main()
