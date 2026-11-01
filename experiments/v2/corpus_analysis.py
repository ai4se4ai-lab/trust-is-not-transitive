"""E15: the shape of public guardrail configurations.

Input: experiments/v2/corpus/nemo_rails.json, from corpus_fetch.py. Each rail is classified by
name, a judgment recorded in the rules below. The framework runs a stage's rails as a chain in
which any rail can stop the request, or in parallel with the same effect; it has no escalation
construct, so a configuration is a chain of veto stages by the framework's own semantics.
Rails are counted as they appear; a per-tool rail counts once per tool.
"""
from __future__ import annotations
from collections import Counter
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[2]
STAGES = ('input', 'dialog', 'retrieval', 'tool_call', 'tool_result', 'tool_output', 'tool_input', 'execution', 'output')
PLACEHOLDER = ('dummy', 'allow input', 'allow output', 'some other', 'block ')
DETERMINISTIC = ('heuristics', 'tool call validation', 'tool result validation', 'regex')
LLM = ('self check', 'content safety', 'topic safety', 'llama guard')
TRANSFORM = ('mask ',)


def classify(flow: str) -> str:
    if any(x in flow for x in PLACEHOLDER):
        return 'placeholder'
    if any(x in flow for x in TRANSFORM):
        return 'transforming'
    if any(x in flow for x in DETERMINISTIC):
        return 'deterministic'
    if any(x in flow for x in LLM):
        return 'llm_prompted'
    return 'model_or_service'


def main() -> None:
    data = json.loads((ROOT / 'experiments/v2/corpus/nemo_rails.json').read_text(encoding='utf-8'))
    rows = data['configurations']
    active, kinds, used = [], Counter(), Counter()
    for row in rows:
        rails = [(flow, classify(flow)) for stage in STAGES for flow in (row['rails'].get(stage) or [])]
        kinds.update(kind for _, kind in rails)
        real = [(f, k) for f, k in rails if k != 'placeholder']
        if real:
            active.append({'path': row['path'], 'rails': real, 'colang2': row['colang2'], 'tool': bool(row['rails'].get('tool_call') or row['rails'].get('tool_result'))})
            used.update(s for s in STAGES if row['rails'].get(s))
    depth = [len(a['rails']) for a in active]
    all_stat = sum(all(k in ('llm_prompted', 'model_or_service') for _, k in a['rails']) for a in active)
    summary = {'repository': data['repository'], 'commit': data['commit'], 'configurations': len(rows), 'unreadable': sum('error' in r for r in rows),
               'with_rails': len(active), 'colang2_with_rails': sum(a['colang2'] for a in active), 'median_stages': statistics.median(depth), 'max_stages': max(depth),
               'distinct_flows': len({f.split(' [')[0] for a in active for f, _ in a['rails']}), 'kinds': dict(kinds), 'stages_used': dict(used),
               'declared_parallel': sum(any(k.endswith('.parallel') for k in r['rails']) for r in rows),
               'with_transforming': sum(any(k == 'transforming' for _, k in a['rails']) for a in active),
               'with_deterministic': sum(any(k == 'deterministic' for _, k in a['rails']) for a in active),
               'all_deterministic': sum(all(k == 'deterministic' for _, k in a['rails']) for a in active),
               'all_statistical': all_stat, 'with_tool_rails': sum(a['tool'] for a in active)}
    (ROOT / 'results/v2/e15_corpus.json').write_text(json.dumps(summary, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
