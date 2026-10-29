"""Refresh primary bibliographic evidence; candidates require human review.

Run with --fetch to archive arXiv pages and Crossref responses. Never rewrites
the bibliography or treats a search result as a verified publication match.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from difflib import SequenceMatcher
import json
from pathlib import Path
import re
import time
import unicodedata

import bibtexparser
from bs4 import BeautifulSoup
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/literature/audit-2026-10-29'


def normalized(value):
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]', '', value.lower())


def fetch(entry):
    key = entry['ID']
    record = {'key': key, 'original': entry, 'sources': [], 'errors': []}
    url = entry.get('url', '')
    if 'arxiv.org/abs/' in url:
        try:
            r = requests.get(url, timeout=35)
            r.raise_for_status()
            (OUT / (key + '.html')).write_text(r.text, encoding='utf-8')
            soup = BeautifulSoup(r.text, 'html.parser')
            meta = {}
            for item in soup.select('meta[name]'):
                meta.setdefault(item['name'], []).append(item.get('content', ''))
            details = {}
            for name in ['title', 'authors', 'dateline', 'comments', 'jref', 'metatable']:
                node = soup.select_one('.' + name)
                if node:
                    details[name] = node.get_text(' ', strip=True)
            record['arxiv'] = {'meta': meta, 'details': details}
            record['sources'].append(url)
        except Exception as exc:
            record['errors'].append(str(exc))
    try:
        doi = entry.get('doi')
        endpoint = 'https://api.crossref.org/works'
        if doi:
            endpoint += '/' + doi
            r = requests.get(endpoint, timeout=40)
        else:
            r = requests.get(endpoint, params={'query.title': entry['title'].replace('{', '').replace('}', ''), 'rows': 5}, timeout=40)
        r.raise_for_status()
        payload = r.json()
        (OUT / (key + '.crossref.json')).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
        candidates = [payload['message']] if doi else payload['message']['items']
        record['crossref'] = [{k: c.get(k) for k in ['DOI', 'type', 'title', 'author', 'container-title', 'volume', 'issue', 'page', 'article-number', 'published', 'published-print', 'published-online', 'publisher', 'URL', 'event', 'ISBN', 'relation']} | {'title_similarity': round(SequenceMatcher(None, normalized(entry['title']), normalized(' '.join(c.get('title', [])))).ratio(), 3)} for c in candidates]
        record['sources'].append(r.url)
    except Exception as exc:
        record['errors'].append(str(exc))
    (OUT / (key + '.json')).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true')
    parser.add_argument('--retry', action='store_true', help='Retry failed Crossref queries sequentially')
    args = parser.parse_args()
    entries = bibtexparser.loads((ROOT / 'paper/references.bib').read_text(encoding='utf-8')).entries
    OUT.mkdir(parents=True, exist_ok=True)
    if args.fetch:
        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = [pool.submit(fetch, e) for e in entries]
            for future in as_completed(futures):
                record = future.result()
                print(record['key'], 'errors=' + str(len(record['errors'])), flush=True)
    records = [json.loads((OUT / (e['ID'] + '.json')).read_text(encoding='utf-8')) for e in entries]
    if args.retry:
        for record in records:
            if record.get('crossref'):
                continue
            entry = record['original']
            r = requests.get('https://api.crossref.org/works', params={'query.title': entry['title'].replace('{', '').replace('}', ''), 'rows': 6}, timeout=40)
            if r.ok:
                payload = r.json()
                (OUT / (entry['ID'] + '.crossref.json')).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
                record['crossref'] = [{k: c.get(k) for k in ['DOI', 'type', 'title', 'author', 'container-title', 'volume', 'issue', 'page', 'article-number', 'published', 'published-print', 'published-online', 'publisher', 'URL', 'event', 'ISBN', 'relation']} | {'title_similarity': round(SequenceMatcher(None, normalized(entry['title']), normalized(' '.join(c.get('title', [])))).ratio(), 3)} for c in payload['message']['items']]
                record['sources'].append(r.url)
                record['errors'] = [err for err in record['errors'] if 'crossref.org' not in err]
                (OUT / (entry['ID'] + '.json')).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
            print('Retry', entry['ID'], r.status_code, flush=True)
            time.sleep(1)
    (OUT / 'records.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    for record in records:
        arxiv = record.get('arxiv', {})
        candidates = record.get('crossref', [])
        matches = [c for c in candidates if c['title_similarity'] >= .8]
        print(record['key'], arxiv.get('details', {}).get('comments', ''), arxiv.get('details', {}).get('jref', ''), json.dumps(matches, ensure_ascii=True))


if __name__ == '__main__':
    main()
