"""Transport-independent operations; the MCP host runs these in a timed worker.

No supplied rule, condition, component or pathname is executed or opened.
"""
from __future__ import annotations

from dataclasses import asdict
import hashlib
from importlib.metadata import version, PackageNotFoundError
import json
import sys

from tint.hsl import Gate, Guard, SpecError, check, necessary, parse, successors, witness_model

MAX_BYTES = 131_072
MAX_NODES = 128
MAX_NAMES = 32
LIMITATION = (
    'Composition verdict under the declared contracts and evidence. '
    'Evidence is a declaration, not a verified fact. No real guard, tool action, '
    'runtime certificate or calibration data is validated by this service.'
)


def json_value(value):
    if isinstance(value, (set, frozenset)):
        return sorted(value)
    raise TypeError(type(value).__name__)


def load(specification: str):
    if len(specification.encode('utf-8')) > MAX_BYTES:
        raise ValueError(f'Specification exceeds {MAX_BYTES} bytes')
    # Check collection types before the research parser, which assumes iterable rows.
    try:
        data = json.loads(specification)
        if not isinstance(data, dict):
            raise ValueError('Specification must be a JSON object')
        for field in ('nodes', 'layers', 'obligations', 'goals'):
            rows = data.get(field)
            if not isinstance(rows, list):
                raise ValueError(f'{field} must be an array')
            limit = MAX_NODES if field == 'nodes' else MAX_NAMES
            if len(rows) > limit:
                raise ValueError(f'{field} exceeds service limit {limit}')
        return parse(specification)
    except (SpecError, TypeError, KeyError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError(f'Invalid HSL specification: {exc}') from exc


def identity(specification):
    canonical = json.dumps(json.loads(specification), sort_keys=True, separators=(',', ':'))
    try:
        release = version('tint-guardrails')
    except PackageNotFoundError:
        release = 'source-checkout'
    return {'service_version': '1', 'package_version': release,
            'specification_sha256': hashlib.sha256(canonical.encode()).hexdigest(),
            'limitation': LIMITATION}


def analyse(operation: str, specification: str, finding_index: int = 0,
            revised_specification: str | None = None) -> dict:
    h = load(specification)
    report = check(h)
    meta = identity(specification)
    if operation == 'check_hierarchy':
        return {**meta, 'ok': report.ok, **asdict(report)}
    if operation == 'explain_finding':
        if finding_index < 0 or finding_index >= len(report.findings):
            raise ValueError('finding_index must select a finding from check_hierarchy')
        finding = report.findings[finding_index]
        model = witness_model(h, finding) if finding.code in ('coverage', 'obligation') else None
        return {**meta, 'finding': asdict(finding), 'countermodel': model,
                'interpretation': 'An abstract contract-respecting counterexample, not an observed attack.'
                if model else 'Structural error; repair the specification before behavioural analysis.'}
    if operation == 'necessary_obligations':
        if not report.ok:
            raise ValueError('Repair composition findings before necessity analysis')
        return {**meta, 'necessary': necessary(h), 'residual': report.residual,
                'interpretation': 'One-entry-at-a-time removal; jointly necessary sets are not computed.'}
    if operation == 'compare_hierarchies':
        if revised_specification is None:
            raise ValueError('revised_specification is required')
        revised = load(revised_specification)
        new_report = check(revised)
        if not report.ok or not new_report.ok:
            raise ValueError('Both hierarchies must pass composition checking before comparison')
        # Conservative structural dependency comparison, deliberately not runtime fingerprints.
        changed = {name for name in h.nodes.keys() | revised.nodes.keys()
                   if h.nodes.get(name) != revised.nodes.get(name)}
        changed_layers = {name for name in h.layers.keys() | revised.layers.keys()
                          if h.layers.get(name) != revised.layers.get(name)}
        for graph in (h, revised):
            changed.update(name for name, node in graph.nodes.items()
                           if isinstance(node, (Gate, Guard)) and node.layer in changed_layers)
        global_change = (h.goals != revised.goals or h.obligations != revised.obligations
                         or h.entry != revised.entry)
        def downstream(graph):
            seen, pending = set(), list(changed & graph.nodes.keys())
            while pending:
                name = pending.pop()
                if name not in seen:
                    seen.add(name)
                    pending.extend(successors(graph.nodes[name]))
            return seen
        candidates = set(report.routes) | set(new_report.routes)
        affected = candidates if global_change else candidates & (downstream(h) | downstream(revised))
        return {**meta, 'revised_specification_sha256': identity(revised_specification)['specification_sha256'],
                'changed_nodes': sorted(changed), 'changed_layers': sorted(changed_layers),
                'potentially_affected_routes': sorted(affected),
                'interpretation': 'Conservative specification dependency analysis only. Component code, '
                'configuration, external dependencies and runtime certificate freshness are not compared.'}
    raise ValueError('Unknown analysis operation')


def main():
    try:
        request = json.loads(sys.stdin.read(MAX_BYTES * 2 + 4096))
        result = analyse(**request)
        response = {'result': result}
    except (ValueError, TypeError, KeyError, RecursionError) as exc:
        response = {'error': str(exc)}
    print(json.dumps(response, default=json_value, sort_keys=True))


if __name__ == '__main__':
    main()
