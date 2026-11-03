# Use TINT from an AI agent

TINT helps developers review whether a declared set of guardrail contracts covers
every accepting route. Use it when adding a fallback reviewer, checking approval
branches, or deciding where a deterministic action boundary belongs. The assistant
helps model and explain the system; the existing Python checker supplies the verdict.

This is a local **stdio MCP server**, not a hosted API. The website is static
documentation. No API key, GPU, model subscription or listening socket is required
by TINT itself; your chosen assistant has its own requirements.

## Install

Requires Python 3.11+. Clone the repository and use a dedicated environment:

```sh
git clone https://github.com/ai4se4ai-lab/trust-is-not-transitive.git
cd trust-is-not-transitive
python -m venv .venv
# macOS / Linux
.venv/bin/python -m pip install -e ".[mcp]"
# Windows PowerShell
.venv\Scripts\python.exe -m pip install -e ".[mcp]"
```

Run only the install line for your OS. The optional extra pins the MCP SDK without
changing the frozen research dependency locks. For reproducibility, check out a
specific repository commit before installation. Keep the clone at its installed path.

Find the environment's absolute interpreter path:

```sh
# macOS / Linux
.venv/bin/python -c "import sys; print(sys.executable)"
# Windows PowerShell
.venv\Scripts\python.exe -c "import sys; print(sys.executable)"
```

## Connect clients

Replace `/absolute/path/to/.venv/bin/python` below with that path; quote paths
containing spaces. On Windows use the absolute `.venv\Scripts\python.exe` path.
The command works from any directory after installation.

### Codex

```sh
codex mcp add tint -- /absolute/path/to/.venv/bin/python -m tint.mcp.server
codex mcp list
```

Alternatively add to Codex's MCP configuration:

```toml
[mcp_servers.tint]
command = "/absolute/path/to/.venv/bin/python"
args = ["-m", "tint.mcp.server"]
```

### Claude Code

```sh
claude mcp add --transport stdio tint -- /absolute/path/to/.venv/bin/python -m tint.mcp.server
claude mcp list
```

Use `--scope user` before `tint` for availability across projects, or `--scope
project` to save a team configuration. Absolute paths are machine-specific.

### Cursor or Claude Desktop

Merge into the client's MCP JSON settings (Cursor: `.cursor/mcp.json` in the target
project; Claude Desktop: its MCP configuration file):

```json
{
  "mcpServers": {
    "tint": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["-m", "tint.mcp.server"]
    }
  }
}
```

### VS Code / GitHub Copilot

Merge into the target project's `.vscode/mcp.json`:

```json
{
  "servers": {
    "tint": {
      "type": "stdio",
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["-m", "tint.mcp.server"]
    }
  }
}
```

Use the client's MCP-capable mode, complete its normal trust/setup prompts, and
restart or refresh the session. Ask it to call `list_examples` as a smoke test.
On Windows JSON uses forward slashes or escaped backslashes in paths. If startup
fails, run the configured interpreter with `-c "import tint.mcp.server"` and verify
that you installed `.[mcp]` into that exact environment. Running the server directly
waits for protocol input; it is not an interactive terminal application.

Official setup references: [Codex](https://developers.openai.com/codex/mcp),
[Claude Code](https://code.claude.com/docs/en/mcp),
[Cursor](https://docs.cursor.com/context/model-context-protocol),
[VS Code](https://code.visualstudio.com/docs/copilot/customization/mcp-servers).

## Install the skill

Copy the **entire** `skills/tint-review` folder from the clone into the target
project's `.agents/skills/tint-review` for Codex or
`.claude/skills/tint-review` for Claude Code. Both can use the same content; their
discovery locations differ. Other skill-capable clients use their own locations.
This is a project-local copy; no global settings are changed by the repository.
The skill does not install or connect the MCP server for you.

For example, from the clone, after creating the target `.agents/skills` directory:

```sh
# macOS / Linux — replace /path/to/your/project
cp -R skills/tint-review /path/to/your/project/.agents/skills/
# Windows PowerShell — replace C:\path\to\your\project
Copy-Item -Recurse skills/tint-review C:\path\to\your\project\.agents\skills\
```

Restart the session. Invoke `$tint-review` in Codex or `/tint-review` in Claude Code,
or explicitly ask the agent to follow the TINT review skill. You can also use the
MCP tools without any skill.

## Practical prompts

**Review a fallback:** “Use tint-review. Load `get_example("fallback-review")`.
Check both versions and explain why evidence for the primary reviewer does not
transfer to the fallback. Which assumptions remain in the repaired version?”

**Review file writes:** “Load `get_example("workspace-write")`. Show an accepting
path without a workspace boundary, check the repair, and list what the actual
path-check implementation would still need to guarantee.”

**Review an approval branch:** “Load `get_example("approval-branch")`. Our policy
requires approval on every accepting route. Find the bypass and recheck the fix.”

**Use your own pipeline:** “Use tint-review to model our pipeline: [describe goals,
stages, branching, contracts and evidence]. Show the mapping before interpreting
the result. Check it, explain findings, suggest a repair and recheck. Mark unknown
premises rather than assuming they hold.”

## Tool contract

| Tool | Inputs | Result |
| --- | --- | --- |
| `list_examples` | none | IDs and titles |
| `get_example` | `example_id` | broken/repaired objects, prompts, expected verdicts |
| `check_hierarchy` | `specification`: JSON **string** | verdict, findings, routes, assumptions, trusted claims |
| `explain_finding` | string, zero-based `finding_index` | finding and abstract countermodel, when available |
| `necessary_obligations` | passing specification string | individually necessary assumed evidence entries |
| `compare_hierarchies` | two passing specification strings | conservatively affected structural routes |

`get_example` returns specifications as objects; serialize the chosen object before
passing it to analysis tools. Read the `tint://guide` resource for HSL semantics or
the [source guide](../src/tint/mcp/guide.md). The optional MCP prompt
`review_guardrail_pipeline(description)` prepares a model-review workflow.

Each analysis result includes a specification hash, package/service versions and
limits of interpretation. The hash is input identity, not a runtime certificate.
Comparison examines HSL dependencies only; real component changes require the
engine's actual fingerprint/certificate lifecycle and declared external dependencies.

The service limits each specification to 128 KiB, 128 nodes and 32 goals, layers
and obligations each. Analyses time out after 10 seconds in a child process.
Timeouts and malformed inputs return MCP tool errors, not negative or positive
composition verdicts. Exact analysis with provided facts can be exponential.

## Scope of the guarantee

This integration wraps the existing checker. It does not change the calculus or
the frozen studies, prove real guard contracts, issue risk certificates, or enforce
an assistant's actions. A deterministic gate in a specification is a trusted claim
about an implementation. A skill is guidance. Runtime enforcement needs complete
mediation by a trusted host. The current research sandbox is not a production guard
for arbitrary shell, filesystem or network tools.

The shipped transport is local stdio. Public HTTP hosting, authentication, rate
limits, tenant isolation and real-tool enforcement are separate deployment work.
Do not put the GitHub Pages URL into an MCP client's server URL field.

## Development

```sh
python -m pip install -e ".[mcp]"
python -m pytest tests/test_mcp.py
python scripts/export_mcp_examples.py --check
cd website
npm test
npm run build
```

Regenerate observations and the skill guide with `python scripts/export_mcp_examples.py`
after an intentional checker/example change. The generated files are checked in;
website builds require only Node.js. This integration is not an additional v2
experiment and does not establish cross-agent effectiveness.
