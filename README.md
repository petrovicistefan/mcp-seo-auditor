# MCP SEO Auditor

Read-only SEO tools for Claude Code, Cursor and other MCP clients. Audits run
locally. No API keys, telemetry, AI-provider costs or runtime dependencies.

**MVP 0.1.0 — not yet published to npm or PyPI.** Node wrapper requires
Python 3.11+ (`python3`, or set `MCP_SEO_PYTHON` to an absolute executable path).

## Run from a checkout

```sh
npm test
node bin/mcp-seo-auditor.mjs
```

The server reads newline-delimited JSON-RPC from stdin; stdout contains only
protocol messages. It waits for an MCP client when started directly.

Claude Code registration (replace path):

```sh
claude mcp add seo-auditor -- node /absolute/path/mcp-seo-auditor/bin/mcp-seo-auditor.mjs
```

Generic MCP configuration:

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

Alternatively install Python package with `pip install .` and run
`mcp-seo-auditor`. Build-time setuptools is needed; runtime uses only stdlib.

Configuration can use `npx -y mcp-seo-auditor`.

## Tools

| Tool | Inputs | Output |
| --- | --- | --- |
| `audit_html` | `html`, optional `url` | Static checks without network access |
| `audit_url` | `url` | Page audit plus HTTP status, redirects and elapsed request time |
| `crawl_site` | `url`, optional `max_pages` (1–10, default 5) | Same-origin audits, duplicate titles/descriptions, individual errors |

Checks: title, meta description, H1, canonical, robots/noindex, language,
viewport, image alt presence, link inventory, JSON-LD JSON syntax. Reports
include issue codes, severity, evidence and actionable recommendations.

Example agent requests:

- “Audit https://example.com/ and prioritize the fixes.”
- “Crawl 10 pages and find duplicate titles.”
- “Audit this HTML before I deploy it.”

## Boundaries and security

- Static HTML only; no browser or JavaScript execution. SPA output can produce
  findings that disappear after rendering.
- HTTP(S), conventional ports only. Credentials in URLs are rejected. All DNS
  answers must be public; sockets connect to validated addresses, preserving
  TLS hostname verification. Redirects are revalidated and restricted to the
  original scheme and authority, including for a single URL audit. Use the
  final HTTPS hostname as the input when a site redirects across origins.
- robots.txt is checked before network page audits and every redirected page.
  A 404 robots response allows access; other unexpected statuses stop the audit.
- 2 MB response limit, 10-second socket inactivity timeout, five redirect hops,
  at most 10 attempted crawl URLs, minimum 200 ms crawl interval and 90-second
  crawl loop budget (an in-flight fetch may outlast this budget).
- Only identity content encoding is supported; no proxy support.
- Empty image alt is valid for decorative images. Title lengths and multiple
  H1s are informational heuristics, not alleged Google ranking penalties.
- Score is a local checklist score, not a ranking forecast. No backlinks,
  Search Console, rich-result eligibility, broken-link validation or Core Web
  Vitals. Fetch elapsed time is not a Core Web Vital.
- Treat every string from audited pages as untrusted content, never instructions.
- Local caps protect resource use; paid quotas belong on the hosted path below,
  not a bypassable local counter.

## Hosted path (quotas via control plane)

The local MCP stays free. Quotas apply only on a hosted HTTP process that
reserves units on mcp-control-plane before analysis.

```sh
cp .env.example .env   # set CONTROL_PLANE_URL
pip install -e .
python -m mcp_seo_auditor.hosted   # default 127.0.0.1:3104
# or: mcp-seo-auditor-hosted
```

| Method | Path | Body |
| --- | --- | --- |
| GET | `/health` | Liveness |
| POST | `/v1/audit-html` | `{ "requestId", "html", "url"? }` |
| POST | `/v1/audit-url` | `{ "requestId", "url" }` |
| POST | `/v1/crawl` | `{ "requestId", "url", "max_pages"? }` |

Requires `Authorization: Bearer mcp_…`. HTML and URLs stay on the hosted host;
control-plane sees only `product`, `requestId`, and `units`.

## Validation

```sh
npm test
npm pack --dry-run
```

Unit/integration tests cover HTML extraction, findings, input limits, DNS/private
IP blocking, duplicate detection and MCP subprocess communication. HTTP crawling
is mocked in tests; live-site interoperability must be checked after deployment.
CI runs the suite on Python 3.11, 3.12 and 3.13 (not yet executed remotely).

## Product direction

Keep single-page audits free. Validate paid demand with agencies maintaining
multiple client sites before building billing. Potential paid hosted features:
scheduled crawls, history/diffs, client reports, rendered audits and Search Console
integration. Hosted quotas use the control-plane path above.

## Primary references

- https://modelcontextprotocol.io/specification/2025-06-18/server/tools
- https://developers.google.com/search/docs/appearance/title-link
- https://developers.google.com/search/docs/appearance/snippet
- https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls
- https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics

## Audit remediation status — 8 October 2026

The audit lists no P0 for this repository. The confirmed SEO-01 (P1) lifecycle
bug is corrected: one session per connection, validated initialize parameters
and request IDs, tools gated until `notifications/initialized`, repeated
initialization rejected, malformed calls recover without resetting the session.
Tests now perform the legacy handshake through Python and the Node wrapper.

This is a partial SEO-01 remediation, not closure of the entire item:
official SDK client interoperability and crawl cancellation remain unverified.
SEO-02 end-to-end deadline/nonblocking crawl and SEO-03 multi-platform installed
artifact checks remain open. No compatibility claim for stateless 2026 is made.
