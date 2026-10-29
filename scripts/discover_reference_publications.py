"""Discover exact title matches in official conference proceedings indexes."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from urllib.parse import urljoin

import bibtexparser
from bs4 import BeautifulSoup
import requests

from audit_references import ROOT, OUT, normalized

entries = bibtexparser.loads((ROOT / 'paper/references.bib').read_text(encoding='utf-8')).entries
titles = {normalized(e['title']): e['ID'] for e in entries}
indexes = [f'https://proceedings.neurips.cc/paper_files/paper/{year}' for year in [2019, 2020, 2021, 2023, 2024, 2025]]
indexes += [f'https://proceedings.iclr.cc/paper_files/paper/{year}' for year in [2024, 2025, 2026]]
indexes += [f'https://proceedings.mlr.press/v{volume}/' for volume in [235, 238, 258, 267]]


def scan(url):
    result = []
    cache = OUT / ('index-' + url.replace('https://', '').replace('/', '_') + '.html')
    if cache.exists():
        content = cache.read_bytes()
    else:
        r = requests.get(url, timeout=60)
        print(url, r.status_code, len(r.content), flush=True)
        if not r.ok:
            return result
        content = r.content
        cache.write_bytes(content)
    soup = BeautifulSoup(content, 'html.parser')
    for a in soup.select('a[href]'):
        key = titles.get(normalized(a.get_text(' ', strip=True)))
        if key and ('hash/' in a['href'] or 'mlr.press' in url):
            result.append({'key': key, 'url': urljoin(url, a['href'])})
    if 'mlr.press' in url:
        for paper in soup.select('div.paper'):
            title = paper.select_one('.title')
            key = titles.get(normalized(title.get_text(' ', strip=True))) if title else None
            a = paper.select_one('.links a[href]')
            if key and a:
                result.append({'key': key, 'url': urljoin(url, a['href'])})
    return result


def retrieve(item):
    r = requests.get(item['url'], timeout=40)
    r.raise_for_status()
    (OUT / (item['key'] + '.publication.html')).write_bytes(r.content)
    soup = BeautifulSoup(r.content, 'html.parser')
    a = soup.find('a', string=lambda s: s and s.strip().lower() == 'bibtex')
    if a:
        item['bibtex_url'] = urljoin(item['url'], a['href'])
        b = requests.get(item['bibtex_url'], timeout=40)
        b.raise_for_status()
        item['bibtex'] = b.text
        (OUT / (item['key'] + '.publication.bib')).write_text(b.text, encoding='utf-8')
    elif 'mlr.press' in item['url']:
        node = soup.select_one('#bibtex')
        if node:
            item['bibtex'] = node.get_text()
            (OUT / (item['key'] + '.publication.bib')).write_text(item['bibtex'], encoding='utf-8')
    print('Matched', item['key'], item['url'], flush=True)
    return item


if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=3) as pool:
        matches = [item for group in pool.map(scan, indexes) for item in group]
        results = list(pool.map(retrieve, matches))
    (OUT / 'proceedings.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
