import assert from 'node:assert/strict';
import test from 'node:test';
import {localSearch, safeEvidenceUrl, validQuestion} from '../src/domain';
import bundled from '../src/members.json';
import type {Member} from '../src/domain';
const members = bundled as Member[];
test('all bundled full names work offline', () => {
  for (const m of members) assert.equal(localSearch(`Who is ${m.fullName}?`, members).member?.id, m.id);
});
test('offline role and identifier lookup', () => {
  assert.equal(localSearch('group leader',members).member?.id, members[0].id);
  assert.equal(localSearch('nzerneste250',members).member?.id, members[0].id);
});
test('alias boundaries and accent normalization use a synthetic fixture', () => {
  const fixture: Member = {...members[0], aliases:['Erné']};
  assert.equal(localSearch('Who is Erne?', [fixture]).matched, true);
  assert.equal(localSearch('Ernestine', [fixture]).matched, false);
});
test('no-match contains no claims or evidence', () => {
  const result = localSearch('weather tomorrow',members);
  assert.equal(result.matched,false); assert.equal(result.member,null); assert.deepEqual(result.evidenceLinks,[]);
});
test('question bounds', () => {
  assert.equal(validQuestion('  '), false); assert.equal(validQuestion('a'.repeat(501)),false);
  assert.equal(validQuestion('a'.repeat(500)),true);
});
test('safe evidence URLs', () => {
  assert.equal(safeEvidenceUrl('javascript:alert(1)'),false);
  assert.equal(safeEvidenceUrl('http://example.com'),false);
  assert.equal(safeEvidenceUrl('https://name:secret@example.com'),false);
  assert.equal(safeEvidenceUrl('https://github.com'),true);
});
