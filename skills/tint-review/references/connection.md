# Connect the TINT tools

Requires Python 3.11+ and a local stdio-capable MCP client. In a local clone:

```text
python -m venv .venv
```

Install with `.venv/bin/python -m pip install -e ".[mcp]"` on macOS/Linux,
or `.venv\Scripts\python.exe -m pip install -e ".[mcp]"` on Windows.
Use that interpreter's **absolute path** in the client configuration:

```text
codex mcp add tint -- /absolute/path/to/.venv/bin/python -m tint.mcp.server
claude mcp add --transport stdio tint -- /absolute/path/to/.venv/bin/python -m tint.mcp.server
```

On Windows substitute the absolute `.venv\Scripts\python.exe` path and quote
paths containing spaces. Restart the client and inspect `codex mcp list` or
`claude mcp list`. Ask the agent to call `list_examples` as a connection test.
The CLI entry point `tint-mcp` is equivalent when its installation is on PATH.

Copy the complete `tint-review` directory into your target project's
`.agents/skills/` for Codex or `.claude/skills/` for Claude Code. Keep references
and metadata beside `SKILL.md`. A skill alone does not install or connect the server.
Other clients can use the same stdio command with their own configuration format.

Source: https://github.com/ai4se4ai-lab/trust-is-not-transitive
Documentation: https://ai4se4ai-lab.github.io/trust-is-not-transitive/
The documentation URL is static hosting, not an MCP endpoint.
