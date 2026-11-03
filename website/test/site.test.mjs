import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, access } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { connection, install, displayReport } from '../app.js';
import '../scripts/build.mjs';

const dist = new URL('../dist/', import.meta.url);

test('all client/OS combinations use the installed Python module', () => {
  for (const os of ['unix', 'windows']) {
    assert.match(install(os), /pip install -e "\.\[mcp\]"/);
    for (const client of ['codex', 'claude', 'cursor', 'vscode']) {
      const { code } = connection(client, os);
      assert.match(code, /tint\.mcp\.server/);
      assert.ok(!code.includes('--url'));
      if (['cursor', 'vscode'].includes(client)) {
        const config = JSON.parse(code);
        const entry = (config.servers || config.mcpServers).tint;
        assert.deepEqual(entry.args, ['-m', 'tint.mcp.server']);
        assert.match(entry.command, os === 'windows' ? /Scripts\/python.exe$/ : /bin\/python$/);
      }
    }
  }
});

test('examples show saved checker findings and disclose remaining premises', async () => {
  const examples = JSON.parse(await readFile(new URL('data/examples.json', dist), 'utf8'));
  assert.equal(examples.length, 3);
  for (const example of examples) {
    const broken = displayReport(example, 'broken'), repaired = displayReport(example, 'repaired');
    assert.equal(broken.report.ok, false);
    assert.equal(repaired.report.ok, true);
    assert.ok(broken.report.findings.length > 0);
    assert.ok(repaired.report.residual.length || repaired.report.claims.length);
    assert.ok(broken.explanation.includes(broken.report.findings[0].node));
    const bundled = JSON.parse(await readFile(new URL(`examples/${example.id}.json`, dist), 'utf8'));
    assert.deepEqual(bundled.broken, example.broken);
    assert.deepEqual(bundled.repaired, example.repaired);
  }
});

test('built page local links and fragment targets exist under a repository subpath', async () => {
  const html = await readFile(new URL('index.html', dist), 'utf8');
  const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(match => match[1]);
  assert.equal(new Set(ids).size, ids.length);
  for (const match of html.matchAll(/\b(?:href|src)="([^"]+)"/g)) {
    const target = match[1];
    if (/^https?:/.test(target) || target === '#') continue;
    assert.ok(!target.startsWith('/'), `Root-relative URL breaks Pages: ${target}`);
    if (target.startsWith('#')) assert.ok(ids.includes(target.slice(1)), target);
    else await access(new URL(target, dist));
  }
  for (const file of ['skill/references/guide.md', 'skill/references/connection.md', 'skill/agents/openai.yaml']) {
    await access(new URL(file, dist));
  }
});

test('preview serves HTML and data, reports missing files, and confines paths', async t => {
  const child = spawn(process.execPath, [fileURLToPath(new URL('../scripts/serve.mjs', import.meta.url))],
    { env: { ...process.env, PORT: '0' }, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'] });
  t.after(() => child.kill());
  const url = await new Promise((resolve, reject) => {
    let output = '';
    const timeout = setTimeout(() => reject(new Error('Preview did not start')), 10000);
    child.on('error', error => { clearTimeout(timeout); reject(error); });
    child.stdout.on('data', data => {
      output += data;
      const match = output.match(/Local: (http:\/\/127\.0\.0\.1:\d+)/);
      if (match) { clearTimeout(timeout); resolve(match[1]); }
    });
  });
  const home = await fetch(url);
  assert.equal(home.status, 200);
  assert.match(await home.text(), /Trust Is Not Transitive/);
  const examples = await fetch(`${url}/data/examples.json`);
  assert.equal((await examples.json()).length, 3);
  assert.equal((await fetch(`${url}/missing.txt`)).status, 404);
  assert.equal((await fetch(`${url}/..%2fpackage.json`)).status, 403);
});
