import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import path from 'node:path';
import test from 'node:test';

const expoCli = path.join(path.dirname(require.resolve('expo/package.json')), 'bin', 'cli');
const previewApi = 'http://172.30.114.74:8000';

for (const [profile, apiUrl, expected] of [
  ['preview', previewApi, 'true'],
  ['production', previewApi, 'false'],
  ['', previewApi, 'false'],
  ['preview', 'http://example.com:8000', 'false'],
]) {
  test(`generated Android manifest: ${profile || 'no profile'}, ${apiUrl} -> cleartext ${expected}`, () => {
    const output = execFileSync(process.execPath, [expoCli, 'config', '--type', 'introspect', '--json'], {
      cwd: path.resolve(__dirname, '..'),
      env: { ...process.env, EAS_BUILD_PROFILE: profile, EXPO_PUBLIC_API_URL: apiUrl },
      encoding: 'utf8',
      timeout: 30000,
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    const config = JSON.parse(output);
    const manifest = config._internal.modResults.android.manifest.manifest;
    assert.equal(manifest.application[0].$['android:usesCleartextTraffic'], expected);
    assert.equal(manifest.application[0].$['android:networkSecurityConfig'], undefined);
    assert.equal(manifest.$.package, 'com.agrisoko.pocket.g13');
    assert.ok(manifest['uses-permission'].some(
      (permission: { $: Record<string, string> }) => permission.$['android:name'] === 'android.permission.INTERNET',
    ));
  });
}
