import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test, { after, before } from 'node:test';
import { fileURLToPath } from 'node:url';

const serverScript = fileURLToPath(new URL('./live-server.mjs', import.meta.url));
const workspace = fs.realpathSync(
  fs.mkdtempSync(path.join(os.tmpdir(), 'impeccable-live-root-')),
);
const sibling = `${workspace}-sibling`;
let connection;

before(() => {
  fs.mkdirSync(sibling);
  fs.writeFileSync(path.join(workspace, 'inside.html'), 'inside workspace');
  fs.writeFileSync(path.join(sibling, 'secret.html'), 'outside workspace');
  fs.symlinkSync(path.join(sibling, 'secret.html'), path.join(workspace, 'escape.html'));

  const output = execFileSync(process.execPath, [serverScript, '--background'], {
    cwd: workspace,
    encoding: 'utf8',
  });
  connection = JSON.parse(output.trim().split('\n').at(-1));
});

after(() => {
  try {
    execFileSync(process.execPath, [serverScript, 'stop', '--keep-inject'], {
      cwd: workspace,
      encoding: 'utf8',
    });
  } finally {
    fs.rmSync(workspace, { recursive: true, force: true });
    fs.rmSync(sibling, { recursive: true, force: true });
  }
});

test('rejects browser requests from a non-loopback origin', async () => {
  const response = await fetch(`http://localhost:${connection.port}/live.js`, {
    headers: {
      Origin: 'https://attacker.example',
      'Sec-Fetch-Site': 'cross-site',
    },
  });

  assert.equal(response.status, 403);
  assert.equal(response.headers.get('access-control-allow-origin'), null);
});

test('allows browser requests from a loopback origin without a wildcard', async () => {
  const origin = 'http://localhost:3000';
  const response = await fetch(`http://localhost:${connection.port}/live.js`, {
    headers: { Origin: origin },
  });

  assert.equal(response.status, 200);
  assert.equal(response.headers.get('access-control-allow-origin'), origin);
});

test('allows an IPv6 loopback origin', async () => {
  const origin = 'http://[::1]:3000';
  const response = await fetch(`http://localhost:${connection.port}/live.js`, {
    headers: { Origin: origin },
  });

  assert.equal(response.status, 200);
  assert.equal(response.headers.get('access-control-allow-origin'), origin);
});

test('allows a same-site localhost script request without origin or referer', async () => {
  const response = await fetch(`http://localhost:${connection.port}/live.js`, {
    headers: { 'Sec-Fetch-Site': 'same-site' },
  });

  assert.equal(response.status, 200);
});

test('rejects a cross-site script request that only carries a referer', async () => {
  const response = await fetch(`http://localhost:${connection.port}/live.js`, {
    headers: {
      Referer: 'https://attacker.example/page',
      'Sec-Fetch-Site': 'cross-site',
    },
  });

  assert.equal(response.status, 403);
});

test('allows a token-authorized source file inside the workspace', async () => {
  const response = await fetch(
    `http://localhost:${connection.port}/source?token=${connection.token}&path=inside.html`,
  );

  assert.equal(response.status, 200);
  assert.equal(await response.text(), 'inside workspace');
});

test('rejects an absolute sibling path that shares the workspace prefix', async () => {
  const target = path.join(sibling, 'secret.html');
  const response = await fetch(
    `http://localhost:${connection.port}/source?token=${connection.token}&path=${encodeURIComponent(target)}`,
  );

  assert.equal(response.status, 403);
});

test('rejects a symlink that resolves outside the workspace', async () => {
  const response = await fetch(
    `http://localhost:${connection.port}/source?token=${connection.token}&path=escape.html`,
  );

  assert.equal(response.status, 403);
});
