#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const pkg = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
const server = JSON.parse(readFileSync(join(root, 'server.json'), 'utf8'));
const init = readFileSync(join(root, 'src/mcp_seo_auditor/__init__.py'), 'utf8');
const pyproject = readFileSync(join(root, 'pyproject.toml'), 'utf8');
const serverPy = readFileSync(join(root, 'src/mcp_seo_auditor/server.py'), 'utf8');

const m = init.match(/__version__\s*=\s*"([^"]+)"/);
const py = pyproject.match(/^version\s*=\s*"([^"]+)"/m);
const failures = [];

if (!m) failures.push('__version__ missing in __init__.py');
if (!py) failures.push('version missing in pyproject.toml');
if (m && m[1] !== pkg.version) failures.push(`__version__ ${m[1]} != package.json ${pkg.version}`);
if (py && py[1] !== pkg.version) failures.push(`pyproject ${py[1]} != package.json ${pkg.version}`);
if (server.version !== pkg.version) failures.push(`server.json version ${server.version} != ${pkg.version}`);
for (const p of server.packages || []) {
  if (p.version && p.version !== pkg.version) failures.push(`server.json package version ${p.version} != ${pkg.version}`);
}
if (/serverInfo['\"]:\s*\{[^}]*version['\"]:\s*['\"]0\.\d+\.\d+['\"]/.test(serverPy)) {
  failures.push('server.py appears to hardcode serverInfo.version; use __version__');
}
if (!serverPy.includes('__version__')) {
  failures.push('server.py must import and use __version__ for serverInfo.version');
}

if (failures.length) {
  console.error('check:rules failed:');
  for (const f of failures) console.error(' -', f);
  process.exit(1);
}
console.log(`check:rules ok (${pkg.version})`);
