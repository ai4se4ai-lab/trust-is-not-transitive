"""Archive fresh primary records for every reference without making fuzzy edits."""
from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher
import gzip
import json
from pathlib import Path
import re
from urllib.parse import quote_plus
import sys
import time

import bibtexparser
from bs4 import BeautifulSoup
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/literature/audit-2026-11-01'


def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


def fetch(e):
    key = e['ID']
    result = {'key': key, 'entry': e, 'scholar_url': 'https://scholar.google.com/scholar?q=' + quote_plus(e['title'].replace('{', '').replace('}', '')), 'sources': [], 'errors': []}
    targets = [('crossref', 'https://api.crossref.org/works/' + e['doi'], {})] if e.get('doi') else [('crossref', 'https://api.crossref.org/works', {'query.title': e['title'].replace('{', '').replace('}', ''), 'rows': 3})]
    if e.get('url') and not e['url'].startswith('https://doi.org/'):
        targets.append(('primary', e['url'], {}))
    for kind, url, params in targets:
        try:
            r = requests.get(url, params=params, timeout=40)
            name = key + '.' + kind + ('.json.gz' if kind == 'crossref' else '.html.gz')
            (OUT / name).write_bytes(gzip.compress(r.content, mtime=0))
            result['sources'].append({'url': r.url, 'status': r.status_code, 'file': name})
            r.raise_for_status()
            if kind == 'crossref':
                message = r.json()['message']
                items = [message] if e.get('doi') else message['items']
                result['candidates'] = [{k: c.get(k) for k in ['DOI', 'type', 'title', 'subtitle', 'author', 'container-title', 'volume', 'issue', 'page', 'article-number', 'published', 'published-print', 'published-online', 'publisher', 'event']} | {'similarity': round(SequenceMatcher(None, norm(e['title']), norm(' '.join(c.get('title', [])))).ratio(), 3)} for c in items]
            elif not r.content.startswith(b'%PDF'):
                soup = BeautifulSoup(r.content, 'html.parser')
                result['meta'] = {}
                for m in soup.select('meta[name]'):
                    if m['name'].startswith(('citation_', 'DC.')):
                        result['meta'].setdefault(m['name'], []).append(m.get('content', ''))
                result['details'] = {c: n.get_text(' ', strip=True) for c in ['title', 'authors', 'comments', 'jref', 'dateline'] if (n := soup.select_one('.' + c))}
                result['bibtex_links'] = [a['href'] for a in soup.select('a[href]') if a.get_text(strip=True).lower() == 'bibtex']
        except Exception as exc:
            result['errors'].append(kind + ': ' + str(exc))
    (OUT / (key + '.json')).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    print(key, 'errors=' + str(len(result['errors'])), flush=True)
    return result


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    entries = bibtexparser.loads((ROOT / 'paper/references.bib').read_text(encoding='utf-8')).entries
    with ThreadPoolExecutor(max_workers=5) as pool:
        if '--retry' not in sys.argv:
            records = list(pool.map(fetch, entries))
        else:
            records = []
            for e in entries:
                record = json.loads((OUT / (e['ID'] + '.json')).read_text(encoding='utf-8'))
                if any('429' in error for error in record['errors']):
                    time.sleep(1)
                    record = fetch(e)
                records.append(record)
    (OUT / 'records.json').write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding='utf-8')
