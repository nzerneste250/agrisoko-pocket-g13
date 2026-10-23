import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import members from '../src/members.json';

test('mobile source files decode as UTF-8 and contain no known mojibake or replacement characters', () => {
  const root = path.resolve(__dirname, '..');
  const files = ['App.tsx', 'index.ts', 'app.config.js', 'app.json', 'eas.json'];
  function walk(relative: string) {
    for (const item of readdirSync(path.join(root, relative), { withFileTypes: true })) {
      const target = path.join(relative, item.name);
      if (item.isDirectory()) walk(target);
      else if (/\.(tsx?|js|json)$/.test(item.name)) files.push(target);
    }
  }
  for (const dir of ['src', 'tests', 'plugins']) walk(dir);
  for (const file of files) {
    const source = new TextDecoder('utf-8', { fatal: true }).decode(readFileSync(path.join(root, file)));
    assert.doesNotMatch(source, /\ufffd|\u00c2[\u00a0\u00b7]|\u00c3[\u0080-\u00bf]|\u00e2\u20ac/, file);
  }
});
test('all four confirmed names remain unchanged and missing facts stay unknown', () => {
  assert.deepEqual(members.map(m => m.fullName), ['NZAYISENGA Erneste', 'INEZA Benitha', 'MANZI Cedrick', 'KIRENGA Alain Thierry']);
  for (const member of members) {
    assert.equal(member.approvalStatus, 'pending'); assert.deepEqual(member.skills, []); assert.deepEqual(member.evidenceLinks, []);
    assert.equal(member.contribution, null); assert.equal(member.outcomeMetric, null);
  }
  for (const member of members.slice(1)) { assert.equal(member.registrationNumber, null); assert.equal(member.githubUsername, null); assert.equal(member.role, null); }
});
