import { mkdir, copyFile, cp } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = fileURLToPath(new URL('../', import.meta.url));
const dist = path.join(root, 'dist');
// An explicit allowlist keeps source scripts and local files out of the public site.
await mkdir(dist, { recursive: true });
for (const file of ['index.html', 'styles.css', 'app.js', 'favicon.svg', 'llms.txt']) {
  await copyFile(path.join(root, file), path.join(dist, file));
}
await cp(path.join(root, 'data'), path.join(dist, 'data'), { recursive: true });
await cp(path.join(root, '../skills/tint-review'), path.join(dist, 'skill'), { recursive: true });
await cp(path.join(root, '../src/tint/mcp/examples'), path.join(dist, 'examples'), { recursive: true });
await copyFile(path.join(root, '../src/tint/mcp/guide.md'), path.join(dist, 'guide.md'));
await copyFile(path.join(root, '../docs/MCP.md'), path.join(dist, 'connect.md'));
await copyFile(path.join(root, '../LICENSE'), path.join(dist, 'LICENSE'));
await copyFile(path.join(root, '.nojekyll'), path.join(dist, '.nojekyll'));
console.log(`Built ${dist}`);
