"""Apply reviewed November 2 corrections and build the per-entry audit manifest."""
import csv
import gzip
import hashlib
import json
from pathlib import Path
import re

import bibtexparser
from bs4 import BeautifulSoup
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/literature/audit-2026-11-02'
DATE = '2026-11-02'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    path = ROOT / 'paper/references.bib'
    bib = path.read_text(encoding='utf-8')
    original = {e['ID']: e for e in bibtexparser.loads(bib).entries}
    fetched = {r['key']: r for r in json.loads((OUT / 'records.json').read_text(encoding='utf-8'))}
    previous = {r['key']: r for r in json.loads((OUT.parent / 'audit-2026-11-01/audit.json').read_text(encoding='utf-8'))}
    cff = yaml.safe_load(gzip.decompress((OUT / 'empirical-citation.supplement.gz').read_bytes()))
    updates = {
        'jackson2019alloy': {'title': '{Alloy: A Language and Tool for Exploring Software Designs}'},
        'tian2019differential': {'title': '{Differential Testing of Certificate Validation in SSL/TLS Implementations: An RFC-guided Approach}'},
        'ralph2020empirical': {'author': ' and '.join(a['family-names'] + ', ' + a['given-names'] for a in cff['preferred-citation']['authors'])},
        'arxiv230518404': {'author': 'Kumar, Bhavesh and Lu, Charles and Gupta, Gauri and Palepu, Anil and Bellamy, David and Raskar, Ramesh and Beam, Andrew'},
        'arxiv251221220': {
            'ENTRYTYPE': 'inproceedings', 'howpublished': None,
            'author': 'Wang, Le and Ying, Zonghao and Yang, Xiao and Zou, Quanchen and Yin, Zhenfei and Li, Tianlin and Yang, Jian and Yang, Yaodong and Sheng, Lu and Liu, Aishan and Liu, Xianglong',
            'year': '2026',
            'booktitle': 'The First Workshop on Efficient Spatial Reasoning at ICLR 2026',
            'url': 'https://openreview.net/forum?id=wyKCkQ2GyO',
        },
    }
    # Add arXiv DOIs only when the exact DOI link appears in the archived primary page.
    for key, e in original.items():
        if e.get('howpublished', '').startswith('arXiv:') and key != 'arxiv251221220':
            source = OUT / (key + '.primary.html.gz')
            soup = BeautifulSoup(gzip.decompress(source.read_bytes()), 'html.parser')
            doi = '10.48550/arXiv.' + e['howpublished'].split(':')[1]
            assert any(a['href'].lower() == ('https://doi.org/' + doi).lower() for a in soup.select('a[href]')), key
            updates.setdefault(key, {})['doi'] = doi
    notes = {
        'jackson2019alloy': 'Restored the subtitle from the DOI registry: A Language and Tool for Exploring Software Designs.',
        'tian2019differential': 'Restored the subtitle from the DOI registry: An RFC-guided Approach.',
        'ralph2020empirical': 'Replaced “and others” with all 42 authors in the official ACM SIGSOFT CITATION.cff preferred citation. This avoids the duplicate Davide Taibi in the arXiv metadata. The official citation specifies 2020 and the arXiv report; no journal version was confirmed.',
        'arxiv230518404': 'Used Bhavesh Kumar and Charles Lu as printed in the indexed primary workshop PDF, rather than mixing Bhawesh (arXiv) with Charles (workshop). Workshop footnote confirms ICML 2023 TEACH. Direct OpenReview PDF access remains HTTP 403; author spelling is checked against the web index of the primary PDF, not a newly downloaded PDF.',
        'arxiv251221220': 'Replaced the 2025 arXiv citation with the 2026 Efficient Spatial Reasoning workshop version. The official workshop confirms acceptance and an outstanding paper award; coauthor Yaodong Yang’s publication page confirms the workshop designation and all 11 authors, including Lu Sheng. This is an ICLR workshop paper, not a main-conference paper. OpenReview itself remains blocked; no DOI or pagination was verified.',
        'holm1979simple': 'JSTOR currently returns HTTP 420. Identity and fields retain the earlier archived audit evidence; current primary revalidation is incomplete. No DOI was located.',
        'arxiv251005156': 'Google Research confirms ACL 2026 and all seven authors. No final ACL Anthology record, DOI or pagination was located. Retained the institutional conference citation without inventing missing fields.',
        'arxiv250816481': 'Official COLM 2026 page still labels itself pre-proceedings. Title and three authors confirmed; retained the explicit pre-proceedings note. No final pagination verified.',
        'arxiv251102164': 'arXiv still describes a submission to TACAS 2026. No matching published record was confirmed; submission is not publication.',
        'arxiv230505176': 'Published TMLR version confirmed using the author-hosted December 2024 published PDF. OpenReview responds with a browser challenge, which was not treated as verification.',
        'carnevali2022compositional': 'Retained final volume 48, issue 12, pages 4762–4788 from coauthor institution FAU. The Crossref placeholder 1–1 is not the final pagination.',
        'efron1994introduction': 'Retained 1994 for this exact Chapman and Hall/CRC DOI edition, as registered by the publisher; the original 1993 edition is frequently cited under other edition records.',
    }
    supplements = json.loads((OUT / 'supplements.json').read_text(encoding='utf-8'))
    extra = {
        'ralph2020empirical': ['empirical-citation'],
        'arxiv251221220': ['robosafe-workshop'],
        'arxiv230505176': ['frugalgpt-published'],
        'carnevali2022compositional': ['statecharts-final'],
    }
    indexed = {'url': 'https://openreview.net/pdf?id=0yN9RW1Vac', 'access': 'Primary PDF indexed by web search on 2026-11-02; direct download blocked with HTTP 403', 'title': 'Conformal Prediction with Large Language Models for Multi-Choice Question Answering', 'authors': ['Bhavesh Kumar', 'Charles Lu', 'Gauri Gupta', 'Anil Palepu', 'David Bellamy', 'Ramesh Raskar', 'Andrew Beam'], 'venue': 'ICML 2023 (Neural Conversational AI TEACH) workshop'}
    (OUT / 'mcqa-indexed-primary.json').write_text(json.dumps(indexed, indent=2), encoding='utf-8')
    for key, changes in updates.items():
        entry = original[key].copy()
        for field, value in changes.items():
            if value is None:
                entry.pop(field, None)
            else:
                entry[field] = value
        fields = ['author', 'title', 'journal', 'booktitle', 'series', 'volume', 'number', 'pages', 'year', 'month', 'publisher', 'institution', 'doi', 'url', 'howpublished', 'note']
        assert set(entry) <= set(fields) | {'ID', 'ENTRYTYPE'}
        block = '@' + entry['ENTRYTYPE'] + '{' + key + ',\n' + ',\n'.join('  ' + field + ' = {' + entry[field] + '}' for field in fields if field in entry) + '\n}'
        bib = re.sub(r'@\w+\{' + re.escape(key) + r',.*?\n\}', lambda _: block, bib, flags=re.S)
    bib = bib.replace('Rechecked against primary records on 2026-11-01', 'Rechecked against primary records on 2026-11-02')
    bib = bib.replace('% Google Scholar returned HTTP 429; see the audit for access limitations.', '% Source-access limitations and remaining uncertainties are documented in the audit.')
    path.write_text(bib, encoding='utf-8')
    audit = []
    for e in bibtexparser.loads(bib).entries:
        key = e['ID']
        r = fetched[key]
        files = [s['file'] for s in r['sources']] + [key + '.json']
        sources = [s['url'] for s in r['sources'] if s['status'] == 200]
        for s in supplements:
            if s['key'] in extra.get(key, []) or s['key'] == key + '-bibtex':
                files.append(s['file'])
                if s['status'] == 200:
                    sources.append(s['url'])
        if key == 'arxiv251221220':
            files += ['robosafe-author.supplement.gz', 'robosafe-author.json', 'iclr2026-index.html.gz']
            sources += ['https://yangyaodong.com/en/publications?kw=RoboSafe']
        if key == 'arxiv230518404':
            files += ['mcqa-indexed-primary.json']
            sources += [indexed['url']]
        status = 'preprint' if e.get('howpublished', '').startswith('arXiv:') else 'published'
        if key == 'arxiv251221220': status = 'workshop publication; author/institution confirmed'
        if key == 'arxiv230518404': status = 'workshop publication; indexed primary PDF'
        if key == 'arxiv250816481': status = 'pre-proceedings'
        if key == 'arxiv251005156': status = 'institution-confirmed conference citation; final record incomplete'
        if key == 'holm1979simple': status = 'historical evidence; current access blocked'
        if e['ENTRYTYPE'] == 'techreport': status = 'technical report'
        if key == 'willison2023dual': status = 'blog post'
        note = notes.get(key, 'Checked identity, author order, title, year and available volume/issue/pages against the publisher-deposited DOI record or official proceedings metadata. Expanded author names and diacritics retained where the registry abbreviates them.')
        if status == 'preprint' and key not in notes:
            note = 'Title, author list, year and arXiv DOI checked on the primary arXiv page. Publication discovery did not confirm a matching published version; this is not proof of nonpublication.'
        block = re.search(r'@\w+\{' + re.escape(key) + r',.*?\n\}', bib, re.S).group()
        record = dict(key=key, checked=DATE, status=status, entry=e, entry_sha256=digest(block.encode()), sources=sources,
                      evidence={f: digest((OUT / f).read_bytes()) for f in files}, note=note,
                      changed=e != fetched[key]['entry'], upgraded_from_arxiv=key == 'arxiv251221220',
                      access_errors=r['errors'])
        if key == 'holm1979simple':
            record['historical_audit'] = previous[key]['historical_audit']
        audit.append(record)
    (OUT / 'audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
    with (ROOT / 'paper/refs_verification.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['key', 'URL', 'date_checked', 'verified', 'evidence_sha256'], lineterminator='\n')
        writer.writeheader()
        for r in audit:
            writer.writerow(dict(key=r['key'], URL=r['entry'].get('url', 'https://doi.org/' + r['entry'].get('doi', '')), date_checked=DATE,
                                 verified='audited', evidence_sha256=digest(json.dumps(r, ensure_ascii=False, sort_keys=True).encode())))
    substantive = ['jackson2019alloy', 'tian2019differential', 'ralph2020empirical', 'arxiv230518404', 'arxiv251221220']
    report = ['# Reference audit — 2026-11-02', '',
              'Reviewed all 124 bibliography entries and preserved all citation keys. No fabricated study was identified. Corrected five substantive records and added verified arXiv DOIs to the 23 retained preprints.', '',
              'Fresh requests covered every entry: DOI-specific Crossref records for the 80 existing DOIs, official proceedings/arXiv/author pages, and title searches for publication discovery. Initial Crossref HTTP 429 responses were retried sequentially; all registry requests ultimately succeeded. A search hit or an HTTP 200 browser challenge was not treated as a verified publication. Search discovery cannot establish that a publication does not exist.', '',
              '## Corrections', '']
    report += ['- **' + k + ':** ' + notes[k] for k in substantive]
    report += ['', '## Remaining limitations and publication decisions', '']
    report += ['- **' + k + ':** ' + notes[k] for k in ['holm1979simple', 'arxiv230518404', 'arxiv251005156', 'arxiv250816481', 'arxiv251102164', 'arxiv230505176', 'carnevali2022compositional', 'efron1994introduction']]
    report += ['', 'Workshop author lists are version-specific. RoboSafe is now the confirmed 2026 workshop version, including Lu Sheng; it is not presented as an ICLR main-track publication. No DOI, pages or venue were inferred merely from an arXiv submission or a similarly titled follow-up study. The remaining preprints are explicitly labeled arXiv. Google Scholar was not used as a verification source.', '', '## Per-entry evidence', '', '| Citation key | Result | Primary record | Notes |', '|---|---|---|---|']
    for r in audit:
        url = r['entry'].get('url') or 'https://doi.org/' + r['entry'].get('doi', '')
        report.append('| `' + r['key'] + '` | ' + r['status'] + ' | [Record](' + url + ') | ' + r['note'] + ' |')
    report += ['', '## Validation and reproducibility', '',
               'The manifest in `audit-2026-11-02/audit.json` records final entry hashes, source URLs, access errors and hashes of archived responses. `paper/refs_verification.csv` points to those reviewed records. Earlier audits remain historical evidence. `python scripts/check_refs.py` passed for all 124 entries, evidence hashes and TeX citation keys. A separate IEEEtran BibTeX run rendered all 124 entries, exited successfully and reported no bibliography warnings; its log is `audit-2026-11-02/bibtex-validation.blg`. These checks do not resolve the source-access limitations above.', '',
               'Collection reused `scripts/refresh_reference_audit.py` with its OUT directory set to this audit date, followed by sequential retries of HTTP 429 requests. `scripts/collect_reference_supplements.py` collects additional primary records. `scripts/apply_reference_followup.py` applies the explicitly reviewed corrections and generates this report.', '']
    # Compute the count from the original fetched snapshot, rather than the updated bibliography.
    report = [line.replace('80 existing DOIs', str(sum(bool(r['entry'].get('doi')) for r in fetched.values())) + ' existing DOIs') for line in report]
    (ROOT / 'docs/literature/REFERENCE_AUDIT.md').write_text('\n'.join(report), encoding='utf-8')
    print('Entries:', len(audit), 'Changed:', sum(r['changed'] for r in audit), 'Retained preprints:', sum(r['status'] == 'preprint' for r in audit))


if __name__ == '__main__':
    main()
