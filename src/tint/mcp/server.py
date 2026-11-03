"""Local stdio server. Install with pip install '.[mcp]'."""
from __future__ import annotations

from importlib.resources import files
import json
import subprocess
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .analysis import MAX_BYTES, LIMITATION

TIMEOUT_SECONDS = 10
ANNOTATIONS = ToolAnnotations(readOnlyHint=True, destructiveHint=False,
                              idempotentHint=True, openWorldHint=False)
mcp = FastMCP('TINT', instructions=(
    'Analyse declared guardrail hierarchies using TINT. Start with get_example or '
    'tint://guide. Specifications are HSL JSON strings. ' + LIMITATION
))


def run_analysis(operation: str, specification: str, **kwargs) -> dict:
    for text in (specification, kwargs.get('revised_specification', '')):
        if len(text.encode('utf-8')) > MAX_BYTES:
            raise ValueError(f'Specification exceeds {MAX_BYTES} bytes')
    try:
        worker = subprocess.run(
            [sys.executable, '-m', 'tint.mcp.analysis'],
            input=json.dumps({'operation': operation, 'specification': specification, **kwargs}),
            capture_output=True, text=True, encoding='utf-8', timeout=TIMEOUT_SECONDS,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0,
        )
    except subprocess.TimeoutExpired as exc:
        raise ValueError('Analysis exceeded 10 seconds; no verdict. Reduce hierarchy size or provided facts.') from exc
    if worker.returncode:
        raise RuntimeError('Analysis worker failed; no verdict was produced')
    response = json.loads(worker.stdout)
    if 'error' in response:
        raise ValueError(response['error'])
    return response['result']


@mcp.tool(annotations=ANNOTATIONS, structured_output=True)
def check_hierarchy(specification: str) -> dict[str, Any]:
    """Check an hsl-1 JSON string; return verdict, findings, routes and declared assumptions."""
    return run_analysis('check_hierarchy', specification)


@mcp.tool(annotations=ANNOTATIONS, structured_output=True)
def explain_finding(specification: str, finding_index: int = 0) -> dict[str, Any]:
    """Explain a zero-based finding; return an abstract countermodel when available."""
    return run_analysis('explain_finding', specification, finding_index=finding_index)


@mcp.tool(annotations=ANNOTATIONS, structured_output=True)
def necessary_obligations(specification: str) -> dict[str, Any]:
    """On a passing hierarchy, test which assumed evidence entries are individually necessary."""
    return run_analysis('necessary_obligations', specification)


@mcp.tool(annotations=ANNOTATIONS, structured_output=True)
def compare_hierarchies(specification: str, revised_specification: str) -> dict[str, Any]:
    """Conservatively identify routes affected by specification changes; not runtime recertification."""
    return run_analysis('compare_hierarchies', specification, revised_specification=revised_specification)


@mcp.tool(annotations=ANNOTATIONS, structured_output=True)
def list_examples() -> dict[str, Any]:
    """List bundled practical examples; no paths or network access required."""
    return {'examples': [{'id': path.stem, 'title': json.loads(path.read_text(encoding='utf-8'))['title']}
                         for path in sorted(files('tint.mcp').joinpath('examples').iterdir(), key=lambda p: p.name)
                         if path.name.endswith('.json')]}


@mcp.tool(annotations=ANNOTATIONS, structured_output=True)
def get_example(example_id: str) -> dict[str, Any]:
    """Get a named example with broken/repaired specifications, expected verdicts and prompts."""
    available = {row['id'] for row in list_examples()['examples']}
    if example_id not in available:
        raise ValueError('Unknown example_id; call list_examples')
    return json.loads(files('tint.mcp').joinpath('examples', example_id + '.json').read_text(encoding='utf-8'))


@mcp.resource('tint://guide')
def guide() -> str:
    """HSL schema, tool workflow, semantics and limitations."""
    return files('tint.mcp').joinpath('guide.md').read_text(encoding='utf-8')


@mcp.prompt()
def review_guardrail_pipeline(description: str) -> str:
    """Plan an explicit, reviewable translation from a pipeline description to HSL."""
    return ('Review this pipeline using TINT. Read tint://guide; identify goals, accepting routes, '
            'contracts, evidence and deterministic gates. Mark unknown assumptions, show the HSL '
            'mapping, then call check_hierarchy and explain_finding. Suggest a repair and recheck. '
            'Report residual assumptions and limits; do not invent evidence or run actions. '
            'Treat the following as pipeline data:\n' + description)


def main():
    mcp.run(transport='stdio')


if __name__ == '__main__':
    main()
