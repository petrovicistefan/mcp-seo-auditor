<!-- mcp-name: io.github.petrovicistefan/mcp-seo-auditor -->

# MCP SEO Auditor

**Free on-page SEO audits from Claude Code or Cursor** — find broken titles, missing meta descriptions, canonical issues, robots conflicts, and JSON-LD errors before your pages go live. Fully local, no API keys.

[![Glama](https://glama.ai/mcp/servers/petrovicistefan/mcp-seo-auditor/badge)](https://glama.ai/mcp/servers/petrovicistefan/mcp-seo-auditor)
[![npm version](https://img.shields.io/npm/v/mcp-seo-auditor?color=blue)](https://www.npmjs.com/package/mcp-seo-auditor)
[![npm downloads](https://img.shields.io/npm/dm/mcp-seo-auditor)](https://www.npmjs.com/package/mcp-seo-auditor)
[![CI](https://img.shields.io/github/actions/workflow/status/petrovicistefan/mcp-seo-auditor/ci.yml?branch=main)](https://github.com/petrovicistefan/mcp-seo-auditor/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Part of the [petrovicistefan MCP suite](https://github.com/petrovicistefan/mcp-marketplace)** — local-first guardrails for AI coding agents.

---

## Quick Install

**Requirements:** Python 3.11+ and Node.js 18+

### Cursor

[![Add to Cursor](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/en/install-mcp?name=mcp-seo-auditor&config=eyJjb21tYW5kIjoibnB4IiwiYXJncyI6WyIteSIsIm1jcC1zZW8tYXVkaXRvciJdfQo=)

Or use the deeplink directly:

```
cursor://anysphere.cursor-deeplink/mcp/install?name=mcp-seo-auditor&config=eyJjb21tYW5kIjoibnB4IiwiYXJncyI6WyIteSIsIm1jcC1zZW8tYXVkaXRvciJdfQo=
```

Or add manually to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "mcp-seo-auditor": {
      "command": "npx",
      "args": ["-y", "mcp-seo-auditor"]
    }
  }
}
```

### Claude Code

```sh
claude mcp add mcp-seo-auditor -- npx -y mcp-seo-auditor
```

If this server is on [Claude MCP Marketplace](https://github.com/petrovicistefan/mcp-marketplace):

```sh
/plugin marketplace add petrovicistefan/mcp-marketplace
```

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-seo-auditor": {
      "command": "npx",
      "args": ["-y", "mcp-seo-auditor"]
    }
  }
}
```

### VS Code

Use the [MCP install link](https://insiders.vscode.dev/redirect/mcp/install?id=io.github.petrovicistefan%2Fmcp-seo-auditor&origin=github), or add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "mcp-seo-auditor": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "mcp-seo-auditor"]
    }
  }
}
```

### npx (any MCP client)

```sh
npx -y mcp-seo-auditor
```

### uvx (PyPI, coming soon)

```sh
uvx mcp-seo-auditor
```

*PyPI package not yet published. See [PyPI Publishing](#pypi-publishing) below.*

---

<details>
<summary><strong>Other MCP clients</strong> (Windsurf, Cline, Zed, Gemini CLI, Codex CLI)</summary>

### Codex CLI

```sh
codex mcp add mcp-seo-auditor -- npx -y mcp-seo-auditor
```

### Windsurf

Add to `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "mcp-seo-auditor": {
      "command": "npx",
      "args": ["-y", "mcp-seo-auditor"]
    }
  }
}
```

### Zed

Add to `settings.json`:

```json
{
  "context_servers": {
    "mcp-seo-auditor": {
      "command": "npx",
      "args": ["-y", "mcp-seo-auditor"]
    }
  }
}
```

### Gemini CLI

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "mcp-seo-auditor": {
      "command": "npx",
      "args": ["-y", "mcp-seo-auditor"]
    }
  }
}
```

</details>

---

**⭐ Found this useful? [Star this repository](https://github.com/petrovicistefan/mcp-seo-auditor) to help others discover it!**

---

<!-- TODO: Add demo GIF/screenshot showing AI agent using the SEO auditor -->

## Why MCP SEO Auditor?

Catch SEO issues **before you deploy** by asking your AI coding assistant to audit your HTML:

- **"Audit this page before I push it"** — find missing titles, broken meta descriptions, or canonical conflicts
- **"Crawl example.com and check for duplicate titles"** — spot content duplication across your site
- **"What SEO issues does this HTML have?"** — get actionable recommendations with severity levels

Unlike hosted SEO tools that require API keys, cloud accounts, and monthly fees, MCP SEO Auditor runs **entirely on your machine**. No data leaves your computer unless you explicitly crawl a public URL.

## Tools

MCP SEO Auditor exposes **3 MCP tools** your AI agent can call:

| Tool | Description | Inputs | Network |
|------|-------------|--------|---------|
| **`audit_html`** | Audit supplied static HTML without network access. Returns evidence and prioritized recommendations. | `html` (string, max 2 MB), `url` (string, optional base URL) | ❌ No |
| **`audit_url`** | Fetch a public page and audit static SEO. Respects robots.txt; blocks private addresses. | `url` (string, required) | ✅ Yes |
| **`crawl_site`** | Crawl up to 10 pages on the exact same origin, respecting robots.txt. Detect duplicate titles and descriptions. | `url` (string, required), `max_pages` (integer, 1–10, default 5) | ✅ Yes |

### What Gets Checked

Each audit scans for:

- **Title**: presence, length (50–60 chars recommended), uniqueness
- **Meta description**: presence, length (150–160 chars recommended), uniqueness
- **H1 headings**: presence, count (multiple H1s flagged as informational)
- **Canonical URL**: presence, validity, self-referencing vs cross-domain
- **Robots directives**: `<meta name="robots">` conflicts (e.g., `noindex` + canonical)
- **Language declaration**: `<html lang="...">` presence
- **Viewport**: mobile-friendly `<meta name="viewport">` tag
- **Image alt attributes**: presence check (empty alt is valid for decorative images)
- **JSON-LD structured data**: JSON syntax validation
- **Internal/external link inventory**: counts for context

**Output**: Findings with severity (`error`, `warning`, `info`), issue codes, evidence snippets, and actionable recommendations. Plus a local checklist score (not a ranking forecast).

## Use Cases

### Individual Developers

```
"Audit the homepage HTML in index.html and prioritize the fixes."
"Check https://staging.example.com for SEO issues before I merge this PR."
"Does this landing page have a proper canonical tag?"
```

### Before Deployment

```
"Audit all HTML files in dist/ and list any errors."
"Crawl the staging site and find duplicate meta descriptions."
```

### Content Review

```
"What's the title and description for this blog post HTML?"
"Does this page have structured data errors?"
```

### Site Audits

```
"Crawl 10 pages starting at https://example.com and report duplicate titles."
"Which pages are missing H1 tags?"
```

## Comparison with Alternatives

How does MCP SEO Auditor compare to other SEO tools for AI agents?

| Feature | **MCP SEO Auditor** | [Ryze open-seo-mcp-skills](https://github.com/Ryze-AI-Adgent/open-seo-mcp-skills) | [AminForou/mcp-gsc](https://github.com/AminForou/mcp-gsc) | [iannuttall/seo](https://github.com/iannuttall/seo) |
|---------|---------------------|-----------------------------------------------------------------------------------|-----------------------------------------------------------|------------------------------------------------------|
| **On-page HTML audits** | ✅ Local, no setup | ❌ Hosted connector required | ❌ GSC-focused, no static audits | ✅ Crawl + audits (local) |
| **Google Search Console** | ❌ Not integrated | ✅ Via hosted Ryze MCP | ✅ OAuth/service account required | ✅ OAuth setup |
| **Google Analytics** | ❌ Not integrated | ✅ GA4 via hosted MCP | ❌ Not included | ✅ CLI + local MCP |
| **Keyword research** | ❌ Not included | ✅ DataForSEO built-in | ❌ Not included | ✅ DataForSEO/Ahrefs key |
| **Setup complexity** | ✅ `npx` one-liner | ⚠️ Hosted sign-in + approval | ⚠️ Google Cloud OAuth | ⚠️ OAuth + optional API keys |
| **Cost** | ✅ Free, local | ⚠️ Free tier, then paid | ✅ Free (your Google API costs) | ✅ Free (your API costs) |
| **Network required** | ❌ Not for `audit_html` | ✅ Yes (hosted) | ✅ Yes (GSC API) | ✅ Yes (GSC/GA APIs) |
| **Privacy** | ✅ Fully local option | ⚠️ Sends requests to Ryze | ⚠️ Google Cloud credentials | ⚠️ Hosted option available |

**When to use MCP SEO Auditor:** You want instant, zero-setup on-page audits of local HTML files or staging sites without external API dependencies.

**When to use alternatives:** You need live Google Search Console data, rank tracking, backlink analysis, or keyword research — those tools excel at connecting your agent to external SEO data sources.

## Table of Contents

- [Quick Start](#quick-start)
- [Why MCP SEO Auditor?](#why-mcp-seo-auditor)
- [Features](#features)
- [Use Cases](#use-cases)
- [Comparison with Alternatives](#comparison-with-alternatives)
- [Requirements](#requirements)
- [Installation](#installation)
  - [From npm](#from-npm)
  - [From a Checkout](#from-a-checkout)
- [Tools Reference](#tools-reference)
- [Boundaries and Security](#boundaries-and-security)
- [Limitations](#limitations)
- [Hosted Path (Quotas via Control Plane)](#hosted-path-quotas-via-control-plane)
- [Product Direction](#product-direction)
- [Testing and Validation](#testing-and-validation)
- [References](#references)
- [More MCP Servers by the Author](#more-mcp-servers-by-the-author)
- [Contributing](#contributing)
- [FAQ](#faq)
- [License](#license)

## Requirements

- **Python 3.11+** on `PATH` (defaults to `python3` executable)
- **Node.js 18+** (for the npm wrapper)

If `python3` is not available or you need a specific Python executable, set the `MCP_SEO_PYTHON` environment variable to an absolute path.

## Installation

### From npm

The quickstart examples use `npx -y mcp-seo-auditor` which downloads and runs the package on demand. For persistent installations, add the MCP server to your client's configuration as shown in the [Quick Start](#quick-start) section.

### From a Checkout

Clone the repository and run tests:

```sh
git clone https://github.com/petrovicistefan/mcp-seo-auditor.git
cd mcp-seo-auditor
npm test
```

Run the server directly:

```sh
node bin/mcp-seo-auditor.mjs
```

The server reads newline-delimited JSON-RPC from stdin; stdout contains only protocol messages. It waits for an MCP client when started directly.

**Register with Claude Code** (replace with your absolute path):

```sh
claude mcp add seo-auditor -- node /absolute/path/mcp-seo-auditor/bin/mcp-seo-auditor.mjs
```

**Or add to any MCP client config**:

```json
{
  "mcpServers": {
    "seo-auditor": {
      "command": "node",
      "args": ["/absolute/path/mcp-seo-auditor/bin/mcp-seo-auditor.mjs"]
    }
  }
}
```

**Install the Python package directly** (optional):

```sh
pip install .
mcp-seo-auditor
```

Build-time setuptools is needed; runtime uses only stdlib.

## PyPI Publishing

This package is configured for PyPI Trusted Publishing (OIDC) but not yet published. The maintainer must complete a one-time setup at https://pypi.org/manage/account/publishing/:

- **PyPI Project Name**: `mcp-seo-auditor`
- **Owner**: `petrovicistefan`
- **Repository name**: `mcp-seo-auditor`
- **Workflow name**: `publish-pypi.yml`
- **Environment name**: (leave blank)

After setup, pushing a version tag (e.g., `v0.1.3`) will automatically publish to PyPI via the `.github/workflows/publish-pypi.yml` workflow.

## Tools Reference

### `audit_html`

**Inputs:**
- `html` (string, required, max 2 MB): The HTML content to audit
- `url` (string, optional): Base URL for resolving relative links

**Output:** JSON with findings, metadata, score, and link inventory

**Example:**

```
"Audit this HTML and tell me what's wrong: <html>...</html>"
```

### `audit_url`

**Inputs:**
- `url` (string, required): Public HTTP(S) URL to fetch and audit

**Output:** Same as `audit_html`, plus `http` object with `status`, `redirects`, and `elapsedMs`

**Example:**

```
"Audit https://example.com and prioritize the issues."
```

Respects `robots.txt`. Redirects are revalidated and must stay on the original scheme + authority. HTTP 4xx/5xx adds an error finding and reduces the score.

### `crawl_site`

**Inputs:**
- `url` (string, required): Starting URL (same-origin crawl)
- `max_pages` (integer, optional, 1–10, default 5): Max pages to crawl

**Output:** JSON with:
- `pages`: Array of per-page audit reports
- `errors`: Array of fetch/validation errors per URL
- `duplicates`: Duplicate titles and descriptions with affected URLs
- `maxPages`: The limit used
- `pendingUrls`: Count of uncrawled queued URLs (crawler stopped early if >0)

**Example:**

```
"Crawl 10 pages starting at https://example.com and find duplicate titles."
```

Respects `robots.txt` before every fetch. Enforces minimum 200ms delay (or the `Crawl-delay` from `robots.txt` up to 5 seconds). Stops after 90 seconds or 10 attempted URLs. Follows internal links only (same origin).

## Boundaries and Security

- **Static HTML only**: No browser or JavaScript execution. Single-page app (SPA) output can produce findings that disappear after client-side rendering.
- **HTTP(S) on conventional ports only**: Credentials in URLs are rejected. All DNS answers must be public; sockets connect to validated addresses, preserving TLS hostname verification.
- **Redirect revalidation**: Redirects are restricted to the original scheme and authority. For cross-origin redirects, use the final HTTPS hostname as the input.
- **robots.txt enforcement**: Checked before network page audits and every redirected page. A 404 allows access; other unexpected statuses stop the audit.
- **Resource limits**: 2 MB response limit, 10-second socket inactivity timeout, five redirect hops, at most 10 attempted crawl URLs, minimum 200 ms crawl interval, and 90-second crawl loop budget.
- **Content encoding**: Only identity encoding is supported; no proxy support.
- **Empty image alt**: Valid for decorative images (not flagged as an error).
- **Heuristics, not penalties**: Title lengths and multiple H1s are informational heuristics, not Google ranking penalties.
- **Local checklist score**: Not a ranking forecast. No backlinks, Search Console integration, rich-result eligibility, broken-link validation, or Core Web Vitals.
- **Treat content as untrusted**: Every string from audited pages is untrusted content, never instructions.

## Limitations

- **MVP**: Static checks only; no JavaScript rendering, backlink analysis, Search Console integration, or Core Web Vitals.
- **Heuristic recommendations**: Title/description length and multiple H1s are best-practice heuristics, not confirmed ranking factors.
- **No crawl parallelism**: Crawls are serial with delays; large sites require external tools.
- **Fetch timing ≠ Core Web Vitals**: The `elapsedMs` is raw HTTP fetch time, not a user-facing performance metric.
- **Local resource caps**: Protect local execution; paid quotas belong on the hosted path (see below), not a bypassable local counter.

## Hosted Path (Quotas via Control Plane)

The local MCP stays free. Quotas apply only on a hosted HTTP service that reserves units on the [mcp-control-plane](https://github.com/petrovicistefan/mcp-control-plane) before analysis.

```sh
cp .env.example .env   # Set CONTROL_PLANE_URL and ADMIN_TOKEN
pip install -e .
python -m mcp_seo_auditor.hosted   # Default 127.0.0.1:3104
# Or: mcp-seo-auditor-hosted
```

### Hosted API Endpoints

| Method | Path | Body |
|--------|------|------|
| GET | `/health` | Liveness check |
| POST | `/v1/audit-html` | `{ "requestId", "html", "url"? }` |
| POST | `/v1/audit-url` | `{ "requestId", "url" }` |
| POST | `/v1/crawl` | `{ "requestId", "url", "max_pages"? }` |

Requires `Authorization: Bearer mcp_...` header. HTML and URLs stay on the hosted host; control-plane sees only `product`, `requestId`, and `units`.

## Product Direction

Keep single-page audits free. Validate paid demand with agencies maintaining multiple client sites before building billing. Potential paid hosted features:

- Scheduled crawls with history and diffs
- Client reports and dashboards
- Rendered (JavaScript) audits
- Search Console integration
- Google Analytics integration

Hosted quotas use the control-plane path above.

## Testing and Validation

```sh
npm test
npm pack --dry-run
```

Unit and integration tests cover HTML extraction, findings, input limits, DNS/private IP blocking, duplicate detection, and MCP subprocess communication. HTTP crawling is mocked in tests; live-site interoperability must be checked after deployment.

CI runs the test suite on Python 3.11, 3.12, and 3.13 across Linux, macOS, and Windows.

## References

- [Model Context Protocol Specification (2025-06-18)](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
- [Google Search: Title Links](https://developers.google.com/search/docs/appearance/title-link)
- [Google Search: Snippets](https://developers.google.com/search/docs/appearance/snippet)
- [Google Search: Canonical URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)
- [Google Search: JavaScript SEO Basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)

## More MCP Servers by the Author

Part of the **petrovicistefan MCP suite** — local-first guardrails for AI coding agents:

- **[mcp-security-guard](https://github.com/petrovicistefan/mcp-security-guard)** — Audit MCP servers for tool poisoning, rug pulls, shadowing, and leaked secrets (OWASP MCP Top 10)
- **[mcp-cost-optimizer](https://github.com/petrovicistefan/mcp-cost-optimizer)** — Identify expensive cloud resources and suggest cost savings
- **[mcp-database-doctor](https://github.com/petrovicistefan/mcp-database-doctor)** — Find slow queries, missing indexes, and schema issues
- **[mcp-dependency-doctor](https://github.com/petrovicistefan/mcp-dependency-doctor)** — Detect outdated packages, license conflicts, and supply-chain risks
- **[mcp-api-guardian](https://github.com/petrovicistefan/mcp-api-guardian)** — Validate OpenAPI specs, detect breaking changes, suggest versioning
- **[mcp-marketplace](https://github.com/petrovicistefan/mcp-marketplace)** — Browse and install all servers in the suite

**⭐ Support this project: [Star this repository](https://github.com/petrovicistefan/mcp-seo-auditor) if it saves you time!**

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. By contributing, you agree to license your contributions under the MIT License.

For security issues, see [SECURITY.md](SECURITY.md).

## FAQ

### Do I need API keys or cloud accounts?

No. The local MCP server uses only Python standard library and runs entirely on your machine. The `audit_html` tool never touches the network. The `audit_url` and `crawl_site` tools fetch public pages but require no authentication.

### Can I audit pages behind authentication?

Not directly. `audit_html` accepts raw HTML, so you can fetch authenticated pages yourself (e.g., `curl` with cookies) and pass the HTML to the tool.

### Why does `audit_html` flag issues that disappear after rendering?

`audit_html` analyzes static HTML. Single-page apps (SPAs) often render content client-side after the initial HTML loads. For accurate SPA audits, use a headless browser to capture the rendered DOM (future feature) or audit the server-side rendered version.

### How is the score calculated?

The score is a local checklist (0–100) based on present/absent best practices: title, meta description, H1, canonical, robots, language, viewport. Errors reduce the score more than warnings. The score is **not** a ranking forecast or SEO performance metric.

### What's the difference between `audit_url` and `crawl_site`?

`audit_url` fetches and audits a single page. `crawl_site` starts at a URL, follows internal links (same origin), and audits up to 10 pages, detecting duplicate titles and descriptions across pages.

### Can I crawl more than 10 pages?

Not in the current MVP. The local resource cap protects your machine. Paid hosted plans may offer higher limits in the future.

### Does this replace Google Search Console?

No. MCP SEO Auditor audits static HTML for on-page issues. It does not provide Search Console data (impressions, clicks, indexing status) or ranking insights. Use [AminForou/mcp-gsc](https://github.com/AminForou/mcp-gsc) or [iannuttall/seo](https://github.com/iannuttall/seo) if you need Search Console integration.

### How do I update the Python version?

Set `MCP_SEO_PYTHON=/path/to/python3.12` before running the server, or export it in your shell profile:

```sh
export MCP_SEO_PYTHON=/usr/local/bin/python3.12
npx -y mcp-seo-auditor
```

### Is this compatible with the MCP specification?

Yes. The server implements the legacy MCP lifecycle (initialize → notifications/initialized → tools/list → tools/call). Official SDK client interoperability is tested but not exhaustively verified (see [docs/audit-remediation.md](docs/audit-remediation.md)).

## License

MIT License — free to use, modify, and distribute. See [LICENSE](LICENSE) for full terms.

---

**Part of the [petrovicistefan MCP suite](https://github.com/petrovicistefan/mcp-marketplace)** — local-first guardrails for AI coding agents.

**⭐ [Star this repo](https://github.com/petrovicistefan/mcp-seo-auditor) if it saves you time!**
