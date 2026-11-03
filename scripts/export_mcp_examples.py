"""Regenerate website observations and the portable skill's bundled guide.

Use --check in CI to fail on drift without writing any files.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from tint.mcp.analysis import analyse, json_value


def outputs():
    examples = []
    for path in sorted((ROOT / 'src/tint/mcp/examples').glob('*.json')):
        example = json.loads(path.read_text(encoding='utf-8'))
        example['observations'] = {}
        for variant in ('broken', 'repaired'):
            spec = json.dumps(example[variant])
            report = analyse('check_hierarchy', spec)
            if report['ok'] != example['expected'][variant]:
                raise RuntimeError(f'{path.name}: unexpected {variant} verdict')
            # Package install metadata is environment-specific, not fixture evidence.
            report.pop('package_version')
            example['observations'][variant] = report
        example['witness'] = analyse('explain_finding', json.dumps(example['broken']))['countermodel']
        examples.append(example)
    return {
        ROOT / 'website/data/examples.json': json.dumps(examples, default=json_value, indent=2, sort_keys=True) + '\n',
        ROOT / 'skills/tint-review/references/guide.md': (ROOT / 'src/tint/mcp/guide.md').read_text(encoding='utf-8'),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for path, content in outputs().items():
        if args.check:
            if not path.exists() or path.read_text(encoding='utf-8') != content:
                raise SystemExit(f'Stale generated file: {path.relative_to(ROOT)}')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
    print('MCP examples and skill guide are current.')
