"""Analysis parity, boundary handling, and a real stdio MCP session."""
import asyncio
from copy import deepcopy
from dataclasses import asdict
from importlib.resources import files
import json
import subprocess
import sys

import pytest

from tint.hsl import check, parse
from tint.mcp.analysis import analyse, json_value, load, MAX_BYTES


def example(name='fallback-review'):
    return json.loads(files('tint.mcp').joinpath('examples', name + '.json').read_text(encoding='utf-8'))


@pytest.mark.parametrize('name', ['fallback-review', 'workspace-write', 'approval-branch'])
def test_reports_and_witnesses_match_existing_checker(name):
    case = example(name)
    for variant in ('broken', 'repaired'):
        specification = json.dumps(case[variant])
        result = analyse('check_hierarchy', specification)
        expected = asdict(check(parse(specification)))
        assert result['ok'] is case['expected'][variant]
        for field, value in expected.items():
            assert result[field] == value
        assert result['specification_sha256'] == analyse('check_hierarchy', json.dumps(case[variant], indent=3))['specification_sha256']
    explained = analyse('explain_finding', json.dumps(case['broken']))
    assert explained['countermodel']['violated'] == explained['finding']['goal']
    assert explained['countermodel']['verdict'][explained['finding']['node']] == 'acc'
    result = analyse('necessary_obligations', json.dumps(case['repaired']))
    assert 'necessary' in result


def test_comparison_tracks_changed_prefixes_and_discloses_limit():
    old = example('workspace-write')['repaired']
    new = deepcopy(old)
    new['nodes'][0]['rule'] = 'new_boundary_implementation'
    result = analyse('compare_hierarchies', json.dumps(old), revised_specification=json.dumps(new))
    assert result['changed_nodes'] == ['boundary']
    assert result['potentially_affected_routes'] == ['accept']
    assert 'not compared' in result['interpretation']
    unchanged = analyse('compare_hierarchies', json.dumps(old), revised_specification=json.dumps(old))
    assert unchanged['potentially_affected_routes'] == []
    # Removing an old prefix is still a dependency change of the retained route.
    old = example('fallback-review')['repaired']
    new = deepcopy(old)
    new['entry'] = 'second_review'
    new['nodes'].pop(0)
    changed = analyse('compare_hierarchies', json.dumps(old), revised_specification=json.dumps(new))
    assert 'second_review' in changed['potentially_affected_routes']


@pytest.mark.parametrize('bad', ['[]', 'null', '{}', '{', '{"nodes":false}', 'x' * (MAX_BYTES + 1)],
                         ids=['array', 'null', 'empty', 'syntax', 'collection-type', 'oversized'])
def test_malformed_or_oversized_inputs_fail_without_verdict(bad):
    with pytest.raises(ValueError):
        load(bad)


def test_limits_and_invalid_analysis_requests():
    data = example()['broken']
    too_many = deepcopy(data)
    too_many['nodes'] *= 65
    with pytest.raises(ValueError, match='limit'):
        load(json.dumps(too_many))
    specification = json.dumps(data)
    with pytest.raises(ValueError, match='finding_index'):
        analyse('explain_finding', specification, finding_index=-1)
    with pytest.raises(ValueError, match='Repair'):
        analyse('necessary_obligations', specification)
    with pytest.raises(ValueError, match='Both'):
        analyse('compare_hierarchies', specification, revised_specification=specification)
    with pytest.raises(ValueError, match='Unknown'):
        analyse('invented', specification)


def test_structural_findings_have_no_behavioural_countermodel():
    data = example('workspace-write')['broken']
    data['entry'] = 'missing'
    result = analyse('explain_finding', json.dumps(data))
    assert result['finding']['code'] == 'dangling'
    assert result['countermodel'] is None


def test_worker_is_a_json_protocol_and_invalid_inputs_are_errors():
    worker = subprocess.run([sys.executable, '-m', 'tint.mcp.analysis'],
                            input=json.dumps({'operation': 'check_hierarchy', 'specification': '{}'}),
                            text=True, capture_output=True, timeout=20)
    assert worker.returncode == 0
    assert 'error' in json.loads(worker.stdout)
    assert 'result' not in json.loads(worker.stdout)


def test_timeout_and_size_errors_never_report_a_verdict(monkeypatch):
    pytest.importorskip('mcp')
    from tint.mcp import server
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired('worker', 10)
    monkeypatch.setattr(server.subprocess, 'run', timeout)
    with pytest.raises(ValueError, match='no verdict'):
        server.run_analysis('check_hierarchy', json.dumps(example()['broken']))
    with pytest.raises(ValueError, match='exceeds'):
        server.run_analysis('check_hierarchy', 'x' * (MAX_BYTES + 1))


def test_real_stdio_client_discovers_and_calls_tools():
    pytest.importorskip('mcp')
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    async def exercise():
        parameters = StdioServerParameters(command=sys.executable, args=['-m', 'tint.mcp.server'])
        async with stdio_client(parameters) as (reader, writer):
            async with ClientSession(reader, writer, read_timeout_seconds=__import__('datetime').timedelta(seconds=30)) as session:
                await session.initialize()
                tools = (await session.list_tools()).tools
                assert {tool.name for tool in tools} == {
                    'list_examples', 'get_example', 'check_hierarchy', 'explain_finding',
                    'necessary_obligations', 'compare_hierarchies'}
                assert all(tool.annotations.readOnlyHint for tool in tools)
                async def call(name, **arguments):
                    result = await session.call_tool(name, arguments)
                    assert not result.isError, result
                    assert result.structuredContent is not None
                    return result.structuredContent
                examples = await call('list_examples')
                assert len(examples['examples']) == 3
                case = await call('get_example', example_id='fallback-review')
                broken, repaired = json.dumps(case['broken']), json.dumps(case['repaired'])
                assert not (await call('check_hierarchy', specification=broken))['ok']
                assert (await call('check_hierarchy', specification=repaired))['ok']
                assert (await call('explain_finding', specification=broken))['countermodel']
                assert len((await call('necessary_obligations', specification=repaired))['necessary']) == 2
                assert (await call('compare_hierarchies', specification=repaired, revised_specification=repaired))['potentially_affected_routes'] == []
                assert (await session.call_tool('check_hierarchy', {'specification': '{}'})).isError
                assert (await session.call_tool('get_example', {'example_id': '../guide'})).isError
                resources = await session.list_resources()
                assert any(str(item.uri) == 'tint://guide' for item in resources.resources)
                resource = await session.read_resource('tint://guide')
                assert 'hsl-1' in resource.contents[0].text
                prompt = await session.get_prompt('review_guardrail_pipeline', {'description': 'review → fallback'})
                assert 'review → fallback' in prompt.messages[0].content.text
    asyncio.run(exercise())
