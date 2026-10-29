"""Open primary arXiv sources and preserve metadata/evidence, never invented citations.

Network collection is an explicit refresh step, not part of offline reproduction.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
from pathlib import Path
import re
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
# Known identifiers are candidates, not verified until fetched and inspected.
SEEDS = {
    'contracts': ['2609.18128', '2605.18672'],
    'cascades': ['2506.00911', '2407.18370', '2602.15391', '2305.05176'],
    'guards': ['2505.03574', '2312.06674', '2406.18495',
               '2501.18837', '2509.26238', '2310.10501', '2502.13458'],
    'runtime': ['2503.18666', '2508.00500'],
    'isolation': ['2503.18813', '2505.23643'],
    'statistics': ['2208.02814', '2107.07511', '2006.02544', '2106.00170'],
    'attacks_evaluation': ['2406.13352', '2410.09024', '2309.15817',
                           '2401.10019', '2302.12173', '2410.02644', '2411.07781',
                           '2307.15043', '2412.09565', '2503.05264', '2504.11168',
                           '2510.02609', '2610.03585'],
    'dual_process': ['2502.17419'],
    'foundations': ['1501.02573', '1708.08611', '1908.05402', '2406.04184'],
    'runtime_extra': ['2503.22738', '2510.05156', '2602.22302', '2506.13028',
                      '2503.07885', '2503.00600'],
    'guards_extra': ['2510.05310', '2507.21170'],
}


def fetch(url: str) -> str:
    request = urllib.request.Request(url, headers={'User-Agent': 'TINT-research/0.1 (primary-source verification)'})
    with urllib.request.urlopen(request, timeout=40) as response:
        return response.read().decode('utf-8', errors='replace')


def clean(text: str) -> str:
    return re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', ' ', text))).strip()


def metadata(text: str, identifier: str, category: str) -> dict:
    def metas(name: str) -> list[str]:
        return [html.unescape(v) for v in re.findall(r'<meta\s+name="'+name+r'"\s+content="([^"]+)"', text)]
    title = metas('citation_title')
    authors = metas('citation_author')
    date = metas('citation_date')
    abstract = re.search(r'<blockquote[^>]*class="abstract[^>]*>(.*?)</blockquote>', text, re.S)
    if not (title and authors and date and abstract):
        raise ValueError('Missing primary-source bibliographic metadata: '+identifier)
    return dict(key='arxiv'+identifier.replace('.', ''), title=title[0], authors=authors,
                year=date[0][:4], category=category, url='https://arxiv.org/abs/'+identifier,
                abstract=clean(abstract.group(1)).removeprefix('Abstract:'), verified='yes',
                checked='2026-10-29', evidence_sha256=hashlib.sha256(text.encode()).hexdigest())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--expand', action='store_true')
    args = parser.parse_args()
    directory = ROOT/'docs/literature/evidence'
    directory.mkdir(parents=True, exist_ok=True)
    candidates = [(identifier, cat) for cat, ids in SEEDS.items() for identifier in ids]
    if args.expand:
        # Follow direct primary-source references from the closest papers. Candidates
        # are not counted as included literature without subsequent relevance review.
        for identifier in ['2609.18128', '2605.18672', '2506.00911', '2505.03574', '2505.23643']:
            path = directory/(identifier+'.full.html')
            try:
                text = path.read_text(encoding='utf-8') if path.exists() else fetch('https://arxiv.org/html/'+identifier)
                path.write_text(text, encoding='utf-8')
                ids = list(dict.fromkeys(re.findall(r'https?://arxiv.org/(?:abs|html)/(\d{4}\.\d{4,5})', text)))
                candidates += [(i, 'snowball_candidate') for i in ids]
            except Exception as exc:
                print('FULLTEXT FAILED', identifier, type(exc).__name__, flush=True)
    records = []
    seen = set()
    for identifier, category in candidates:
        if identifier in seen:
            continue
        seen.add(identifier)
        path = directory/(identifier+'.html')
        try:
            text = path.read_text(encoding='utf-8') if path.exists() else fetch('https://arxiv.org/abs/'+identifier)
            record = metadata(text, identifier, category)
            path.write_text(text, encoding='utf-8')
            records.append(record)
            print(identifier, record['title'], flush=True)
        except Exception as exc:
            print('FAILED', identifier, str(exc), flush=True)
        time.sleep(0.2)
    (ROOT/'docs/literature/metadata.json').write_text(json.dumps(records, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print('Verified primary-source metadata records:', len(records), flush=True)


if __name__ == '__main__':
    main()
