#!/usr/bin/env node
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { delimiter } from 'node:path';
const source = fileURLToPath(new URL('../src/', import.meta.url));
const child = spawn(process.env.MCP_SEO_PYTHON || 'python3', ['-m', 'mcp_seo_auditor.server'], {
  stdio: 'inherit', env: { ...process.env, PYTHONPATH: [source, process.env.PYTHONPATH].filter(Boolean).join(delimiter) }
});
child.on('error', error => { console.error(`MCP SEO Auditor needs Python 3.11+: ${error.message}`); process.exitCode = 1; });
child.on('exit', code => { process.exitCode = code ?? 1; });
for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => child.kill(signal));
