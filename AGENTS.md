# Agent rules

Hard rules for changes in this repository:

1. **Version sync** — `package.json` version, `pyproject.toml` version, `src/mcp_seo_auditor/__init__.py` `__version__`, both version fields in `server.json`, and `serverInfo.version` must match. Runtime version comes from `__version__`, never a hardcoded stale literal.
2. **Local-first** — stdio MCP path needs no accounts or API keys. Do not add telemetry or analytics.
3. **No secrets in logs** — never print API keys, tokens, cookies, or raw user HTML payloads to stderr/stdout beyond MCP protocol responses.
4. **English** — code, comments, commits and docs stay in English.
5. **Tests** — bug fixes add a regression test; do not weaken existing tests to make them pass.

`npm run check:rules` must stay green.
