# Product: MCP SEO Auditor

## What it is

Read-only static SEO audits for AI agents over MCP. Tools analyze supplied HTML or fetch public pages (with robots.txt and SSRF protections) and return findings, scores and crawl summaries.

## What it is NOT

- Not a full SEO suite (no rankings, backlinks, Search Console, or paid keyword data).
- Not a headless browser — SPA client-rendered content is out of scope for accurate audits.
- Not a write tool — it does not modify sites.

## Users

Developers and AI coding agents (Claude Code, Cursor, VS Code, Claude Desktop) that need on-page SEO checks before shipping pages.

## Tools

- `audit_html` — audit supplied HTML without network access
- `audit_url` — fetch one public URL and audit (respects robots.txt; blocks private addresses)
- `crawl_site` — crawl up to 10 same-origin pages with robots.txt and duplicate title/description detection

## Install

Requires **Python 3.11+** and **Node.js 18+**. Primary path: `npx -y mcp-seo-auditor` (npm wrapper runs the Python package). PyPI/`uvx` is prepared but not yet the primary published path.

## Pricing / limits

Local stdio use is free. Hosted consume path (if used) goes through mcp-control-plane quotas.

## Known limitations

- Static HTML / server-rendered content only
- Crawl max 10 pages; crawl-delay > 5s aborts
- Marketplace/README pins must track the published npm version after each release
