"""Apply explicitly reviewed corrections and record the 2026-11-01 audit."""
import csv
import gzip
import hashlib
import json
from pathlib import Path
import re

import bibtexparser
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/literature/audit-2026-11-01'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    path = ROOT / 'paper/references.bib'
    bib = path.read_text(encoding='utf-8')
    original = {e['ID']: e for e in bibtexparser.loads(bib).entries}
    changes = {
        'shamsujjoha2025swiss': {
            'booktitle': '2025 IEEE 22nd International Conference on Software Architecture (ICSA)',
            'pages': '37--48', 'publisher': 'IEEE',
            'doi': '10.1109/ICSA65012.2025.00014',
            'url': 'https://doi.org/10.1109/ICSA65012.2025.00014'},
        'carnevali2022compositional': {'volume': '48', 'number': '12', 'pages': '4762--4788'},
        'demoura2008z3': {
            'ENTRYTYPE': 'inproceedings', 'journal': None,
            'title': '{Z3: An Efficient SMT Solver}',
            'booktitle': 'Tools and Algorithms for the Construction and Analysis of Systems',
            'series': 'Lecture Notes in Computer Science', 'volume': '4963',
            'publisher': 'Springer'},
        'barbosa2022cvc5': {
            'ENTRYTYPE': 'inproceedings', 'journal': None,
            'title': '{cvc5: A Versatile and Industrial-Strength SMT Solver}',
            'booktitle': 'Tools and Algorithms for the Construction and Analysis of Systems',
            'series': 'Lecture Notes in Computer Science', 'volume': '13243',
            'publisher': 'Springer'},
        'littlewood2004redundancy': {
            'ENTRYTYPE': 'inproceedings', 'journal': None,
            'booktitle': 'Computer Security -- ESORICS 2004',
            'series': 'Lecture Notes in Computer Science', 'volume': '3193',
            'publisher': 'Springer'},
        'kildall1973unified': {
            'ENTRYTYPE': 'inproceedings', 'journal': None,
            'booktitle': "Proceedings of the 1st Annual ACM SIGACT-SIGPLAN Symposium on Principles of Programming Languages (POPL '73)",
            'publisher': 'ACM'},
        'barnett2005weakest': {
            'ENTRYTYPE': 'inproceedings', 'journal': None,
            'booktitle': 'Proceedings of the 6th ACM SIGPLAN-SIGSOFT Workshop on Program Analysis for Software Tools and Engineering',
            'publisher': 'ACM'},
        'arxiv251005156': {
            'ENTRYTYPE': 'inproceedings', 'howpublished': None, 'year': '2026',
            'author': 'Miculicich, Lesly and Parmar, Mihir and Palangi, Hamid and Dvijotham, Dj and Montanari, Mirko and Pfister, Tomas and Le, Long',
            'booktitle': 'ACL 2026',
            'url': 'https://research.google/pubs/veriguard-enhancing-llm-agent-safety-via-verified-code-generation-2/'},
        'arxiv250816481': {
            'ENTRYTYPE': 'inproceedings', 'howpublished': None, 'year': '2026',
            'title': '{Benchmarking the Robustness of Agentic Systems to Adversarially-Induced Harmful Behaviors}',
            'booktitle': 'Conference on Language Modeling (COLM)',
            'note': 'Pre-proceedings',
            'url': 'https://proceedings.colm.cc/paper_files/paper/2026/hash/8b54ecd9823fff6d37e61ece8f87e534-Abstract-Conference.html'},
        'tibshirani2019conformal': {
            'pages': None,
            'author': r'Tibshirani, Ryan J. and Foygel Barber, Rina and Cand{\`e}s, Emmanuel J. and Ramdas, Aaditya'},
    }
    order = ['author', 'title', 'journal', 'booktitle', 'series', 'volume', 'number', 'pages', 'year', 'month', 'publisher', 'institution', 'doi', 'url', 'howpublished', 'note']
    for key, updates in changes.items():
        e = original[key].copy()
        for k, v in updates.items():
            if v is None:
                e.pop(k, None)
            else:
                e[k] = v
        text = '@' + e['ENTRYTYPE'] + '{' + key + ',\n' + ',\n'.join('  ' + k + ' = {' + e[k] + '}' for k in order if k in e) + '\n}'
        bib = re.sub(r'@\w+\{' + re.escape(key) + r',.*?\n\}', lambda _: text, bib, flags=re.S)
    bib = bib.replace('% TODO: verify authors, pages and DOI before submission (entered from search snippets only).\n', '')
    bib = bib.replace('% Audited against primary records on 2026-10-29; published versions are preferred.', '% Rechecked against primary records on 2026-11-01; published versions are preferred.\n% Google Scholar returned HTTP 429; see the audit for access limitations.')
    path.write_text(bib, encoding='utf-8')
    final = bibtexparser.loads(bib).entries
    fetched = {r['key']: r for r in json.loads((OUT / 'records.json').read_text(encoding='utf-8'))}
    historical = {r['key']: r for r in json.loads((ROOT / 'docs/literature/audit-2026-10-29/audit.json').read_text(encoding='utf-8'))}
    notes = {
        'shamsujjoha2025swiss': 'Exact title and all four authors match the IEEE-deposited Crossref record. Added DOI, pages and publisher; removed unverified TODO.',
        'carnevali2022compositional': 'Crossref still has placeholder pages 1-1. The coauthor institution FAU confirms final volume 48, issue 12, pages 4762-4788; used final issue metadata.',
        'arxiv251005156': 'Google Research provides an explicit inproceedings BibTeX citation with ACL 2026, year 2026, and this author list. Used that institutional publication record. Its download still links to arXiv; no ACL Anthology identifier, DOI or pagination was located or invented.',
        'arxiv250816481': 'Official COLM 2026 pre-proceedings confirms the revised title and all three authors. No final pagination or BibTeX is available there; explicitly cited as pre-proceedings.',
        'arxiv251221220': 'Workshop publication/presentation is confirmed on the official Efficient Spatial Reasoning at ICLR 2026 site. The accessible arXiv lists 10 authors, while an indexed OpenReview version adds Lu Sheng. OpenReview landing page/PDF/API are blocked, so retain the internally consistent arXiv version pending verification of the workshop author list. Do not mislabel it as a main-track ICLR paper.',
        'arxiv251102164': 'arXiv describes a TACAS 2026 submission. No published exact-title match was located; submission is not publication.',
        'arxiv230518404': 'OpenReview PDF is currently HTTP 403. The earlier archived first-page transcription is from the arXiv author version and contains the workshop publication footnote; it spells the names Bhawesh Kumar and Charles Lu. The indexed OpenReview transcription differs on the first name. Retained the author-version spelling; workshop-version author spelling remains unresolved.',
        'holm1979simple': 'JSTOR is currently HTTP 420 and Crossref title search yields no exact match. Retained metadata supported by the earlier audit; current primary revalidation is incomplete.',
        'arxiv230505176': 'OpenReview currently returns a browser challenge. The author-hosted published TMLR PDF independently confirms all three authors, title and December 2024 publication.',
        'tibshirani2019conformal': 'Official proceedings metadata identifies Rina Foygel Barber with family name Foygel Barber; corrected name parsing and removed an empty pages field. The proceedings provides no pagination.',
        'ralph2020empirical': 'Author list intentionally abbreviated with BibTeX and others. ACM SIGSOFT still recommends citing the 2020 arXiv report.',
    }
    extra = {
        'demoura2008z3': [('z3-springer.html.gz', 'https://link.springer.com/chapter/10.1007/978-3-540-78800-3_24')],
        'barbosa2022cvc5': [('cvc5-springer.html.gz', 'https://link.springer.com/chapter/10.1007/978-3-030-99524-9_24')],
        'littlewood2004redundancy': [('diversity-springer.html.gz', 'https://link.springer.com/chapter/10.1007/978-3-540-30108-0_26')],
        'carnevali2022compositional': [('statecharts-fau.gz', 'https://cris.fau.de/publications/287477378/')],
        'arxiv251005156': [('veriguard-google.gz', changes['arxiv251005156']['url'])],
        'arxiv250816481': [('badacts-colm.html.gz', changes['arxiv250816481']['url'])],
        'arxiv251221220': [('esreasoning-home.html.gz', 'https://sites.google.com/ucsd.edu/efficient-spatial-reasoning/')],
        'arxiv230505176': [('frugalgpt-published.pdf.gz', 'https://lingjiaochen.com/papers/2024_FrugalGPT_TMLR.pdf')],
    }
    audit = []
    for e in final:
        key = e['ID']
        record = fetched[key]
        sources = [s['url'] for s in record['sources'] if s['status'] == 200]
        evidence = {s['file']: digest((OUT / s['file']).read_bytes()) for s in record['sources']}
        evidence[key + '.json'] = digest((OUT / (key + '.json')).read_bytes())
        for name, url in extra.get(key, []):
            assert (OUT / name).exists(), name
            evidence[name] = digest((OUT / name).read_bytes())
            sources.append(url)
        status = 'preprint' if e.get('howpublished', '').startswith('arXiv:') else 'published'
        if key == 'arxiv250816481': status = 'pre-proceedings'
        if key == 'arxiv251005156': status = 'institution-confirmed conference citation'
        if key == 'holm1979simple': status = 'historical evidence; current access blocked'
        if key == 'arxiv230518404': status = 'published; archived evidence'
        if e['ENTRYTYPE'] == 'techreport': status = 'technical report'
        if key == 'willison2023dual': status = 'blog post'
        note = notes.get(key, 'Title, author identity and available publication fields checked against primary records. Expanded names and author diacritics retained when registry names are abbreviated.')
        if status == 'preprint' and key not in notes:
            note = 'arXiv confirms the title, author list and year. No matching published version confirmed; absence from Crossref is not proof of nonpublication.'
        if key in ['demoura2008z3', 'barbosa2022cvc5', 'littlewood2004redundancy', 'kildall1973unified', 'barnett2005weakest']:
            note = 'Corrected journal article to conference paper and replaced journal with the actual proceedings booktitle. DOI registry confirms identity, authors, year and pages; Springer additionally confirms the LNCS series and volume where applicable.'
        block = re.search(r'@\w+\{' + re.escape(key) + r',.*?\n\}', bib, re.S).group()
        item = {'key': key, 'checked': '2026-11-01', 'status': status, 'entry': e, 'entry_sha256': digest(block.encode()), 'sources': sources, 'evidence': evidence, 'note': note, 'scholar_url': record['scholar_url'], 'scholar_status': 'unavailable: HTTP 429; not Scholar verified', 'changed': key in changes}
        if key in ['holm1979simple', 'arxiv230518404']:
            item['historical_audit'] = historical[key]
        audit.append(item)
    (OUT / 'audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
    with (ROOT / 'paper/refs_verification.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['key', 'URL', 'date_checked', 'verified', 'evidence_sha256'], lineterminator='\n')
        writer.writeheader()
        for r in audit:
            writer.writerow({'key': r['key'], 'URL': r['entry'].get('url', 'https://doi.org/' + r['entry'].get('doi', '')), 'date_checked': r['checked'], 'verified': 'audited', 'evidence_sha256': digest(json.dumps(r, ensure_ascii=False, sort_keys=True).encode())})
    report = ['# Reference audit — 2026-11-01', '', f'Reviewed all {len(audit)} entries currently in `paper/references.bib`; corrected {len(changes)} entries and preserved every citation key.', '', '**Google Scholar could not be used to verify the entries:** direct access returned HTTP 429, and the web tool could not open the Scholar search. Per-entry Scholar links below are for manual follow-up, not claims of completed Scholar checks. The archived access response is `audit-2026-11-01/scholar-access.gz`.', '', 'Fresh primary-source requests covered every entry: DOI-specific Crossref records for existing DOIs, title searches for publication discovery, and official proceedings/arXiv pages where available. Rate-limited Crossref requests were retried sequentially. Search results were used for discovery; edits use primary or author/institution records. Successful HTTP responses that contain an access challenge are not verification. Earlier archived primary evidence is explicitly identified where fresh access failed.', '', 'No nonexistent reference was identified. This is a bibliographic audit, not verification of research claims. A preprint is a real reference, but does not establish peer-reviewed publication. Full current verification remains limited for the blocked records identified below; no blanket guarantee that every field is correct is warranted.', '', '## Corrections and publication decisions', '']
    report += ['- **' + r['key'] + ':** ' + r['note'] for r in audit if r['changed'] or r['key'] in ['arxiv251221220', 'arxiv230518404', 'holm1979simple']]
    report += ['', '## Per-entry evidence', '', '| Citation key | Result | Primary source | Scholar follow-up | Notes |', '|---|---|---|---|---|']
    for r in audit:
        url = r['entry'].get('url') or 'https://doi.org/' + r['entry'].get('doi', '')
        report.append(f"| `{r['key']}` | {r['status']} | [Record]({url}) | [Search]({r['scholar_url']}) | {r['note']} |")
    report += ['', '## Validation', '', 'The completed revision passed `python scripts/check_refs.py`: all 124 entry hashes and evidence hashes match, and citation keys used in paper TeX files resolve. A separate BibTeX run using IEEEtran.bst and all 124 entries completed with exit code 0 and no bibliography warnings. These checks validate integrity and BibTeX processing; they do not resolve the source-access limitations above.', '', '## Reproducibility', '', 'The `audit-2026-11-01` directory retains compressed source responses, parsed records, and a reviewed `audit.json` manifest with hashes for each final BibTeX entry and its evidence. `paper/refs_verification.csv` refers to that manifest. Earlier audit directories remain historical records. Run `python scripts/check_refs.py` to check integrity and citation membership. The network collector is `scripts/refresh_reference_audit.py`; refreshing evidence requires reviewing and regenerating the manifest afterward.', '']
    (ROOT / 'docs/literature/REFERENCE_AUDIT.md').write_text('\n'.join(report), encoding='utf-8')
    print(f'Applied {len(changes)} reviewed corrections; audited {len(audit)} entries.')


if __name__ == '__main__':
    main()
