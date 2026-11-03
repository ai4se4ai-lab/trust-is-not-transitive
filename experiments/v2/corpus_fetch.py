"""Build experiments/v2/corpus/nemo_rails.json from the public NeMo Guardrails repository.

Keeps only rail lists, from `config.yml` (Colang 1, and per-tool hook rails) and from
`flow input rails` and `flow output rails` blocks in `.co` files (Colang 2). Files are
read as data; nothing from the repository is run. Needs network access and PyYAML.
"""
from __future__ import annotations
from collections import defaultdict
import json
from pathlib import Path, PurePosixPath
import re
import time
import urllib.parse
import urllib.request
import yaml

ROOT = Path(__file__).resolve().parents[2]
REPOSITORY = 'NVIDIA-NeMo/Guardrails'
HEADERS = {'User-Agent': 'research'}
BLOCK = re.compile(r'^flow (input|output) rails.*\n((?:[ \t]+.*\n|[ \t]*\n)+)', re.M)


def fetch(url: str) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=30).read()


def rail_lines(block: str) -> list[str]:
    """The statements of a rails flow: one rail each, without docstrings, comments or `await`."""
    block = re.sub(r'"""[\s\S]*?"""', '', block)
    lines = [x.split('#')[0].strip() for x in block.splitlines()]
    return [re.sub(r'^await\s+', '', x) for x in lines if x]


def yaml_rails(data: dict) -> dict:
    rails = data.get('rails')
    found: dict = {}
    if not isinstance(rails, dict):
        return found
    for stage, value in rails.items():
        if stage == 'config' or not isinstance(value, dict):
            continue
        flows = [str(x) for x in value.get('flows') or []]
        for tool, listed in (value.get('per_tool') or {}).items():
            flows += [f'{x} [{tool}]' for x in listed]
        if flows:
            found[stage] = flows
        if value.get('parallel'):
            found[stage + '.parallel'] = True
    return found


def main() -> None:
    commit = json.loads(fetch(f'https://api.github.com/repos/{REPOSITORY}/commits/develop'))['sha']
    tree = json.loads(fetch(f'https://api.github.com/repos/{REPOSITORY}/git/trees/{commit}?recursive=1'))['tree']
    paths = [x['path'] for x in tree if x['type'] == 'blob' and x['path'].startswith('examples/')]
    raw = lambda p: fetch(f'https://raw.githubusercontent.com/{REPOSITORY}/{commit}/' + urllib.parse.quote(p)).decode('utf-8')
    directories: dict = defaultdict(lambda: {'rails': {}, 'colang2': False})
    for path in paths:
        directory = str(PurePosixPath(path).parent)
        try:
            if path.endswith(('config.yml', 'config.yaml')):
                directories[directory]['config'] = True
                data = yaml.safe_load(raw(path))
                if isinstance(data, dict):
                    directories[directory]['colang2'] |= str(data.get('colang_version', '')).startswith('2')
                    directories[directory]['rails'].update(yaml_rails(data))
            elif path.endswith('.co'):
                for stage, block in BLOCK.findall(raw(path)):
                    directories[directory]['colang2'] = True
                    directories[directory]['rails'].setdefault(stage, []).extend(rail_lines(block))
        except Exception as exc:
            directories[directory]['error'] = type(exc).__name__
        time.sleep(.02)
    rows = [{'path': k, **v} for k, v in sorted(directories.items()) if v.get('config') or v['rails']]
    out = ROOT / 'experiments/v2/corpus/nemo_rails.json'
    out.write_text(json.dumps({'repository': REPOSITORY, 'commit': commit, 'configurations': rows}, indent=1) + '\n', encoding='utf-8', newline='\n')
    print(len(rows), sum(bool(r['rails']) for r in rows), sum(r['colang2'] for r in rows), sum('error' in r for r in rows))


if __name__ == '__main__':
    main()
