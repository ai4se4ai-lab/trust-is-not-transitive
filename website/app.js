export function connection(client, os) {
  const python = os === 'windows' ? 'C:/path/to/trust-is-not-transitive/.venv/Scripts/python.exe' : '/absolute/path/to/.venv/bin/python';
  const command = `"${python}"`;
  if (client === 'codex') return { code: `codex mcp add tint -- ${command} -m tint.mcp.server\ncodex mcp list`, note: 'Replace the interpreter path. Restart the session, then ask the agent to call list_examples.' };
  if (client === 'claude') return { code: `claude mcp add --transport stdio tint -- ${command} -m tint.mcp.server\nclaude mcp list`, note: 'Local scope by default. Add --scope user before tint for use across projects. Restart and check /mcp.' };
  if (client === 'vscode') return { code: JSON.stringify({ servers: { tint: { type: 'stdio', command: python, args: ['-m', 'tint.mcp.server'] } } }, null, 2), note: "Merge into your target project's .vscode/mcp.json. Use an MCP-capable agent mode." };
  return { code: JSON.stringify({ mcpServers: { tint: { command: python, args: ['-m', 'tint.mcp.server'] } } }, null, 2), note: "Cursor: merge into .cursor/mcp.json. Claude Desktop: merge into its MCP configuration file. Replace the interpreter path." };
}

export function install(os) {
  const python = os === 'windows' ? '.venv\\Scripts\\python.exe' : '.venv/bin/python';
  return `git clone https://github.com/ai4se4ai-lab/trust-is-not-transitive.git\ncd trust-is-not-transitive\npython -m venv .venv\n${python} -m pip install -e ".[mcp]"\n${python} -c "import sys; print(sys.executable)"`;
}

export function displayReport(example, variant) {
  const report = example.observations[variant];
  return {
    label: report.ok ? 'COMPOSITION CHECK PASSED' : 'COMPOSITION CHECK REJECTED',
    explanation: report.ok
      ? 'The declared contracts compose. Inspect residual assumptions and trusted gate claims before interpreting this as a real design guarantee.'
      : report.findings.map(f => `${f.code}: ${f.detail} at ${f.node}. Path: ${f.path.join(' → ')}.`).join('\n'),
    report,
  };
}

if (typeof document !== 'undefined') {
  const byId = id => document.getElementById(id);
  let examples = [], variant = 'broken';

  function renderExample() {
    const example = examples.find(item => item.id === byId('scenario').value);
    if (!example) return;
    const result = displayReport(example, variant);
    byId('example-audience').textContent = example.audience;
    byId('example-title').textContent = example.title;
    byId('example-problem').textContent = example.problem;
    byId('example-repair').textContent = example.repair;
    byId('example-prompt').textContent = example.prompt;
    byId('example-download').href = `./examples/${example.id}.json`;
    byId('verdict').textContent = result.label;
    byId('verdict').classList.toggle('pass', result.report.ok);
    byId('route-count').textContent = `${result.report.routes.length} ACCEPTING ROUTE(S)`;
    byId('example-explanation').textContent = result.explanation;
    byId('report-code').textContent = JSON.stringify(result.report, null, 2);
    byId('spec-code').textContent = JSON.stringify(example[variant], null, 2);
    byId('witness-code').textContent = JSON.stringify(example.witness, null, 2);
    byId('witness-details').hidden = variant === 'repaired';
    document.querySelectorAll('[data-variant]').forEach(tab => {
      const selected = tab.dataset.variant === variant;
      tab.setAttribute('aria-selected', String(selected));
      tab.tabIndex = selected ? 0 : -1;
    });
    byId('example-panel').setAttribute('aria-labelledby', `${variant}-tab`);
  }

  byId('scenario').addEventListener('change', () => { variant = 'broken'; renderExample(); });
  document.querySelectorAll('[data-choose]').forEach(link => link.addEventListener('click', () => {
    byId('scenario').value = link.dataset.choose; variant = 'broken'; renderExample();
  }));
  const tabs = [...document.querySelectorAll('[data-variant]')];
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => { variant = tab.dataset.variant; renderExample(); });
    tab.addEventListener('keydown', event => {
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      const next = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1
        : (index + (event.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
      tabs[next].click(); tabs[next].focus();
    });
  });

  function renderConnection() {
    const os = byId('os').value;
    const result = connection(byId('client').value, os);
    byId('install-code').textContent = install(os);
    byId('connect-code').textContent = result.code;
    byId('client-note').textContent = result.note;
  }
  byId('os').addEventListener('change', renderConnection);
  byId('client').addEventListener('change', renderConnection);
  renderConnection();

  document.querySelectorAll('[data-copy]').forEach(button => button.addEventListener('click', async () => {
    const target = byId(button.dataset.copy);
    try {
      await navigator.clipboard.writeText(target.textContent);
      byId('copy-status').textContent = 'Copied to clipboard.';
      const original = button.textContent;
      button.textContent = 'Copied';
      setTimeout(() => { button.textContent = original; }, 1800);
    } catch {
      const range = document.createRange(); range.selectNodeContents(target);
      const selection = window.getSelection(); selection.removeAllRanges(); selection.addRange(range);
      byId('copy-status').textContent = 'Clipboard unavailable. Text selected; copy it manually.';
    }
  }));

  function setTheme(theme) {
    document.documentElement.dataset.theme = theme;
    byId('theme').setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`);
  }
  try { setTheme(localStorage.getItem('tint-theme') === 'dark' ? 'dark' : 'light'); } catch { setTheme('light'); }
  byId('theme').addEventListener('click', () => {
    const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    setTheme(theme);
    try { localStorage.setItem('tint-theme', theme); } catch { /* Theme still works for this session. */ }
  });

  fetch('./data/examples.json').then(response => {
    if (!response.ok) throw new Error('Examples could not be loaded');
    return response.json();
  }).then(data => { examples = data; renderExample(); }).catch(() => {
    byId('verdict').textContent = 'EXAMPLES UNAVAILABLE';
    byId('example-explanation').textContent = 'Serve this directory over HTTP, or download the example JSON using the link beside this panel.';
  });
}
