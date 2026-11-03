"""Archive official BibTeX and targeted primary records for the November 2 audit."""
from concurrent.futures import ThreadPoolExecutor
import gzip
import json
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/literature/audit-2026-11-02'


def fetch(target):
    key, url = target
    response = requests.get(url, timeout=40)
    name = key + '.supplement.gz'
    (OUT / name).write_bytes(gzip.compress(response.content, mtime=0))
    result = dict(key=key, url=response.url, status=response.status_code, file=name)
    if response.ok and not response.content.startswith(b'%PDF'):
        soup = BeautifulSoup(response.content, 'html.parser')
        result['text'] = soup.get_text(' ', strip=True)[:6000]
        result['links'] = [urljoin(url, a['href']) for a in soup.select('a[href]')
                           if a.get_text(strip=True).lower() == 'bibtex']
    print(key, response.status_code, flush=True)
    return result


if __name__ == '__main__':
    records = json.loads((OUT / 'records.json').read_text(encoding='utf-8'))
    targets = [(r['key'] + '-bibtex', urljoin(r['entry']['url'], link))
               for r in records for link in r.get('bibtex_links', [])]
    targets += [
        ('robosafe-workshop', 'https://sites.google.com/ucsd.edu/efficient-spatial-reasoning/'),
        ('robosafe-openreview', 'https://api2.openreview.net/notes?id=wyKCkQ2GyO'),
        ('mcqa-openreview', 'https://api.openreview.net/notes?id=0yN9RW1Vac'),
        ('empirical-citation', 'https://raw.githubusercontent.com/acmsigsoft/EmpiricalStandards/master/CITATION.cff'),
        ('frugalgpt-published', 'https://lingjiaochen.com/papers/2024_FrugalGPT_TMLR.pdf'),
        ('statecharts-final', 'https://cris.fau.de/publications/287477378/'),
        ('bootstrap-publisher', 'https://www.taylorfrancis.com/books/mono/10.1201/9780429246593/introduction-bootstrap-bradley-efron-tibshirani'),
    ]
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(fetch, targets))
    (OUT / 'supplements.json').write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8')
