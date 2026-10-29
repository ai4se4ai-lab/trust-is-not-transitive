"""Apply the reviewed 2026-10-29 reference audit without changing citation keys.

Uses archived primary records. No network calls and no fuzzy-match edits.
"""
import csv
import hashlib
import html
import json
from pathlib import Path
import re

import bibtexparser
from bibtexparser.latexenc import string_to_latex

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/literature/audit-2026-10-29'

# Each DOI below was reviewed for title, author identity, and publication venue.
REVIEWED = {
    'arxiv250600911', 'arxiv240618495', 'arxiv231010501',
    'arxiv250213458', 'arxiv250318666', 'arxiv250800500',
    'arxiv250318813', 'arxiv240613352', 'arxiv240110019',
    'arxiv230212173', 'arxiv241107781', 'arxiv250217419',
    'arxiv170808611', 'arxiv190805402', 'arxiv240604184',
    'arxiv250307885', 'arxiv250300600', 'arxiv250315707',
    'arxiv210907958', 'arxiv240301216', 'arxiv241216682',
    'angelopoulos2021learn',
}


def tex(value):
    value = html.unescape(re.sub('<[^>]+>', '', str(value)))
    return string_to_latex(value).replace('&', r'\&').replace('%', r'\%')


def from_crossref(c, original):
    kind = 'article' if c['type'] == 'journal-article' else 'inproceedings'
    title = c['title'][0]
    if c.get('subtitle'):
        title = title.rstrip(': ') + ': ' + c['subtitle'][0]
    e = {'ID': original['ID'], 'ENTRYTYPE': kind,
         'title': '{' + tex(title) + '}',
         'author': ' and '.join(tex(a['family']) + (', ' + tex(a['given']) if a.get('given') else '') for a in c['author']),
         'doi': c['DOI'], 'url': 'https://doi.org/' + c['DOI']}
    date = c.get('published-print') or c.get('published') or c.get('published-online')
    e['year'] = str(date['date-parts'][0][0])
    containers = c.get('container-title') or []
    if kind == 'article':
        e['journal'] = ' '.join(tex(containers[0]).replace(r'\textregistered', '').split())
    else:
        e['booktitle'] = tex(containers[-1])
    for source, field in [('volume', 'volume'), ('issue', 'number'), ('page', 'pages'), ('publisher', 'publisher')]:
        if c.get(source):
            e[field] = tex(c[source])
    if 'pages' in e:
        e['pages'] = e['pages'].replace('-', '--')
    if c.get('article-number'):
        e['eid'] = str(c['article-number'])
    return e


def format_entry(e):
    order = ['author', 'title', 'journal', 'booktitle', 'series', 'volume', 'number', 'pages', 'eid', 'year', 'month', 'publisher', 'institution', 'doi', 'url', 'howpublished', 'note']
    return '@' + e['ENTRYTYPE'] + '{' + e['ID'] + ',\n' + ',\n'.join('  ' + k + ' = {' + e[k] + '}' for k in order if k in e) + '\n}'


def main():
    records = json.loads((OUT / 'records.json').read_text(encoding='utf-8'))
    originals = {r['key']: r['original'] for r in records}
    selected = {k: dict(e) for k, e in originals.items()}
    sources = {r['key']: [r['original'].get('url') or 'https://doi.org/' + r['original']['doi']] for r in records if r['original'].get('url') or r['original'].get('doi')}
    notes = {}
    changed = set()
    for r in records:
        if r['key'] in REVIEWED:
            matches = [c for c in r['crossref'] if c['title_similarity'] > .94]
            assert len(matches) == 1, r['key']
            selected[r['key']] = from_crossref(matches[0], originals[r['key']])
            sources[r['key']].append('https://api.crossref.org/works/' + matches[0]['DOI'])
            changed.add(r['key'])
    # Publisher-generated BibTeX takes precedence over the corresponding registry
    # search metadata. Preserve complete accents/initials from the verified arXiv
    # names when the proceedings merely omit them (without changing author order).
    for item in json.loads((OUT / 'proceedings.json').read_text(encoding='utf-8')):
        e = bibtexparser.loads(item['bibtex']).entries[0]
        key = item['key']
        original = originals[key]
        e = {k: v for k, v in e.items() if k in ['ENTRYTYPE', 'title', 'author', 'booktitle', 'year', 'volume', 'series', 'pages', 'publisher', 'doi']}
        e['ID'] = key
        e['url'] = item['url']
        if len(e['author'].split(' and ')) == len(original['author'].split(' and ')):
            e['author'] = original['author']
        e['title'] = '{' + e['title'] + '}'
        if selected[key].get('doi'):
            e['doi'] = selected[key]['doi']
        selected[key] = e
        sources[key].extend([item['url'], item.get('bibtex_url', item['url'])])
        changed.add(key)
    for key in ['arxiv210707511', 'arxiv150102573']:
        c = json.loads((OUT / (key + '.selected-crossref.json')).read_text(encoding='utf-8'))['message']
        selected[key] = from_crossref(c, originals[key])
        sources[key].append('https://api.crossref.org/works/' + c['DOI'])
        changed.add(key)
    # Springer lists the LNCS series before the conference title; record its
    # confirmed volume separately rather than inferring it from an ISBN.
    selected['arxiv150102573'].update(series='Lecture Notes in Computer Science', volume='9035')
    key = 'arxiv250411168'
    e = bibtexparser.loads((OUT / (key + '.publication.bib')).read_text(encoding='utf-8')).entries[0]
    selected[key] = {k: v for k, v in e.items() if k in ['ENTRYTYPE', 'title', 'author', 'booktitle', 'year', 'pages', 'publisher', 'url']}
    selected[key]['ID'] = key
    selected[key]['author'] = originals[key]['author']
    selected[key]['title'] = '{' + selected[key]['title'] + '}'
    sources[key].append(e['url'])
    notes[key] = 'ACL Anthology provides no DOI for this workshop paper; none added.'
    changed.add(key)
    key = 'arxiv230505176'
    selected[key] = {k: originals[key][k] for k in ['ID', 'title', 'author']}
    selected[key].update(ENTRYTYPE='article', journal='Transactions on Machine Learning Research', year='2024', url='https://openreview.net/forum?id=cSimKw5p6R')
    sources[key].append('https://lingjiaochen.com/')
    notes[key] = 'TMLR 2024 confirmed by the author publication list; OpenReview currently serves a browser challenge. No page range or DOI invented.'
    changed.add(key)
    key = 'arxiv240314720'
    selected[key] = {k: originals[key][k] for k in ['ID', 'title', 'author']}
    selected[key].update(ENTRYTYPE='inproceedings', booktitle='Proceedings of the Conference on Applied Machine Learning in Information Security (CAMLIS 2024)', series='CEUR Workshop Proceedings', volume='3920', pages='48--62', year='2025', url='https://ceur-ws.org/Vol-3920/paper03.pdf')
    sources[key].append('https://ceur-ws.org/Vol-3920/')
    notes[key] = 'Conference held in 2024; proceedings published 2025-02-09. Bibliographic year uses the proceedings publication year.'
    changed.add(key)
    key = 'arxiv230518404'
    selected[key] = {k: originals[key][k] for k in ['ID', 'title', 'author']}
    selected[key].update(ENTRYTYPE='inproceedings', booktitle='ICML 2023 Workshop on Neural Conversational AI (TEACH)', year='2023', url='https://openreview.net/pdf?id=0yN9RW1Vac')
    selected[key]['author'] = selected[key]['author'].replace('Lu, Charlie', 'Lu, Charles')
    sources[key].append(selected[key]['url'])
    notes[key] = 'Workshop publication confirmed on the author-uploaded paper first page. That directly retrieved PDF spells the first author Bhawesh Kumar and the second Charles Lu; retained these names despite a differing search-index transcription. No formal proceedings pagination located.'
    changed.add(key)
    # Acceptance alone does not supply an archival published version.
    notes['arxiv251005156'] = 'Google Research lists ACL 2026, but links only to arXiv; no archival proceedings entry located. Retain the verified preprint rather than fabricate publication metadata.'
    sources['arxiv251005156'].append('https://research.google/pubs/veriguard-enhancing-llm-agent-safety-via-verified-code-generation-2/')
    notes['arxiv250816481'] = 'Author publication list says to appear at COLM 2026. Secondary indexes disagree (ICLR 2026); retain arXiv until a primary published record is available.'
    sources['arxiv250816481'].append('https://people.mpi-sws.org/~gradanovic/publications.html')
    notes['arxiv251221220'] = 'Search-indexed final PDF reports ICLR 2026 and adds Lu Sheng, but its OpenReview landing page/PDF are challenge-blocked and the official proceedings index has no matching entry. Retain arXiv author list and year pending directly verifiable publication metadata.'
    sources['arxiv251221220'].append('https://openreview.net/pdf?id=wyKCkQ2GyO')
    selected['holm1979simple']['url'] = 'https://www.jstor.org/stable/4615733'
    sources['holm1979simple'] = ['https://www.ime.usp.br/~abe/lista/pdf4R8xPVzCnX.pdf', 'https://www.jstor.org/stable/4615733']
    selected['anderson1972computer']['url'] = 'https://conferences.computer.org/sp/pdfs/early/ande72.pdf'
    sources['anderson1972computer'] = [selected['anderson1972computer']['url']]
    notes['anderson1972computer'] = 'Primary scan confirms October 1972 and ESD-TR-73-51 (a two-volume report). The retained URL is the Volume II scan.'
    sources['willison2023dual'] = [selected['willison2023dual']['url']]

    bib = ROOT / 'paper/references.bib'
    current = bib.read_text(encoding='utf-8')
    for key, e in selected.items():
        if e != originals[key]:
            pattern = r'@\w+\{' + re.escape(key) + r',.*?\n\}'
            current, count = re.subn(pattern, lambda _: format_entry(e), current, flags=re.S)
            assert count == 1, key
    current = re.sub(r'\A% Bibliography.*?(?=@)', '% Bibliography for "Trust Is Not Transitive".\n% Audited against primary records on 2026-10-29; published versions are preferred.\n% Per-entry sources, limitations, and archived evidence: docs/literature/REFERENCE_AUDIT.md\n% Citation keys retain their original names even when the cited version is published.\n\n', current, count=1, flags=re.S)
    bib.write_text(current, encoding='utf-8')
    actual = {e['ID']: e for e in bibtexparser.loads(current).entries}
    audit = []
    for r in records:
        key = r['key']
        evidence = [key + '.json']
        for suffix in ['.html', '.crossref.json', '.crossref.json.gz', '.publication.html', '.publication.bib', '.selected-crossref.json', '.first-page.txt', '.author-page.html']:
            path = OUT / (key + suffix)
            if path.exists() and not (suffix == '.selected-crossref.json' and key == 'arxiv250411168'):
                evidence.append(path.name)
        if key in ['anderson1972computer', 'holm1979simple', 'willison2023dual', 'arxiv230505176', 'arxiv230518404', 'arxiv240314720', 'arxiv251005156', 'arxiv250816481', 'arxiv251221220']:
            evidence.append('supplemental-web-evidence.json')
        status = 'published' if actual[key]['ENTRYTYPE'] in ['article', 'inproceedings', 'book'] else ('preprint' if 'arxiv.org' in actual[key].get('url', '') else actual[key]['ENTRYTYPE'])
        entry_text = re.search(r'@\w+\{' + re.escape(key) + r',.*?\n\}', current, flags=re.S).group()
        audit.append({'key': key, 'checked': '2026-10-29', 'status': status, 'upgraded_from_arxiv': key in changed, 'entry': actual[key], 'entry_sha256': hashlib.sha256(entry_text.encode()).hexdigest(), 'sources': list(dict.fromkeys(sources[key])), 'note': notes.get(key, 'No published version confirmed; retain the verified arXiv record.' if status == 'preprint' else 'Metadata checked against primary bibliographic records.'), 'evidence': {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in evidence}})
    (OUT / 'audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    with (ROOT / 'paper/refs_verification.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=['key', 'URL', 'date_checked', 'verified', 'evidence_sha256'], lineterminator='\n')
        writer.writeheader()
        for a in audit:
            writer.writerow({'key': a['key'], 'URL': a['entry'].get('url') or a['sources'][0], 'date_checked': a['checked'], 'verified': 'primary', 'evidence_sha256': hashlib.sha256(json.dumps(a, ensure_ascii=False, sort_keys=True).encode()).hexdigest()})
    lines = ['# Reference audit — 2026-10-29', '', f'Checked all {len(audit)} entries in `paper/references.bib`. Replaced {len(changed)} arXiv citations with confirmed journal, conference, or workshop versions. Citation keys are unchanged.', '', 'The check concerns bibliographic identity and metadata, not the truth of scientific claims or the quality of peer review. No nonexistent reference was identified. Entries without a confirmed published version remain explicitly arXiv preprints; a missing publication match is not proof that no publication exists.', '', 'Sources: arXiv abstract-page metadata; Crossref DOI records; official ICLR, NeurIPS, PMLR, ACL Anthology and CEUR proceedings; primary report/article scans; and author publication pages. Search results were used for discovery, not as sole authority for guessed publication metadata.', '', '## Notable corrections and limitations', '', '- The published survey “From System 1 to System 2” has a revised author list/order and a 2026 journal issue; the entry now follows that journal record.', '- The conformal-prediction tutorial has the published title “Conformal Prediction: A Gentle Introduction” (2023).', '- The multiple-choice workshop paper first page confirms Bhawesh Kumar and Charles Lu. A differing search-index spelling was rejected in favor of the directly retrieved paper.', '- Spotlighting appeared at CAMLIS 2024; CEUR published the proceedings in February 2025. Its entry distinguishes the event year from the publication year.', '- No DOI was invented for the LLMSec workshop paper or for OpenReview-only publications.', '- VeriGuard: author page reports ACL 2026, but links only to arXiv; no archival version located.', '- BAD-ACTS: the author page says COLM 2026 (to appear), whereas secondary indexes say ICLR 2026. Retained the verified arXiv entry.', '- RoboSafe: a search-indexed ICLR 2026 final PDF appears to add Lu Sheng; access is currently challenge-blocked and the official proceedings index has no matching entry. Retained the verified arXiv entry instead of mixing versions.', '', '## Per-entry verification', '', '| Citation key | Result | Cited source | Notes |', '|---|---|---|---|']
    for a in audit:
        result = 'Published version substituted' if a['upgraded_from_arxiv'] else a['status'].capitalize()
        url = a['entry'].get('url') or a['sources'][0]
        lines.append(f"| `{a['key']}` | {result} | [Primary record]({url}) | {a['note']} |")
    lines += ['', 'Machine-readable field snapshots, source URLs, and SHA-256 evidence hashes are in `audit-2026-10-29/audit.json`. `metadata.json` and `evidence/` retain the earlier arXiv audit as historical evidence. Run `python scripts/check_refs.py` to check the current bibliography against this audit without network access.', '']
    (ROOT / 'docs/literature/REFERENCE_AUDIT.md').write_text('\n'.join(lines), encoding='utf-8')
    print(f'Updated {len(changed)} preprints; audited {len(audit)} entries.')


if __name__ == '__main__':
    main()
