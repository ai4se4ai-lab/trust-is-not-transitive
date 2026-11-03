# TINT website

A dependency-free static site explaining the TINT MCP server and portable review
skill. It includes client-specific setup, three practical examples, before/after
HSL, checker-generated observations, countermodels, prompts, tool reference and
limitations. The design is original; the use-hpc site informed the requested
structure and static build approach. No source or assets were copied from it.

## Develop

Node.js 20+; no npm dependencies or external fonts:

```sh
cd website
npm run dev
# http://127.0.0.1:4321
npm test
npm run build
```

The preview builds once at startup; restart it after edits. Build output is
`website/dist/`. All public asset links are relative, including downloads, so the
site works under `/trust-is-not-transitive/` on GitHub Pages. The server binds to
loopback; `PORT` changes the default 4321. The website requires no backend and
does not call the MCP server. Example observations are precomputed with the real
Python checker, not live browser verification. Arbitrary JSON editing is not a
website feature: use the MCP tools for your own specifications.

Theme switching, scenario/version selection, client/OS setup selection and copy
buttons work in the browser. Tabs support arrow keys, Home and End. Clipboard
failure selects the source text for manual copying. Browser storage failure does
not disable theme switching. With JavaScript disabled, the connection instructions,
tool reference and downloadable data remain available.

## Keep examples current

From the repository root, with the Python package dependencies installed:

```sh
python scripts/export_mcp_examples.py
python scripts/export_mcp_examples.py --check
```

This generates `website/data/examples.json` and the skill's bundled guide from the
source examples/checker and canonical guide. Commit intentional generated changes.
It does not change the paper, results, protocol or research locks. Node-only builds
use the committed observations; CI checks them against Python before deploying.

## GitHub Pages

The `.github/workflows/website.yml` workflow:

- tests the server (including a real stdio client), verifies example drift, tests
  the site and builds on pull requests and pushes affecting this integration;
- uploads a downloadable `tint-website` build artifact;
- deploys the default branch to GitHub Pages on push or manual dispatch.

One-time repository setup: **Settings → Pages → Build and deployment → Source →
GitHub Actions**. Ensure repository/organization Actions permissions and the
`github-pages` environment allow default-branch deployments. Then commit/push the
changes and run **website** from the Actions tab if needed. No PAT or custom secret
is required. PR jobs do not receive Pages deployment permissions and do not deploy.

Expected URL after the first successful deployment:
https://ai4se4ai-lab.github.io/trust-is-not-transitive/

The static site can also be deployed by publishing `website/dist/` on another
static host. Deployment of the MCP server is separate: this release uses local
stdio and supplies no public HTTP endpoint.
