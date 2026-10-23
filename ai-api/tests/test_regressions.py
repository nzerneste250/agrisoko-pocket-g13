import copy
import json
import pytest
from matching import MemberIndex, load_members, MEMBERS_FILE
from tests.test_matching import SYNTHETIC_MEMBERS

@pytest.mark.parametrize('change', [
    {'skills': 'Python'}, {'aliases': [1]}, {'evidenceLinks': ['javascript:alert(1)']},
    {'_meta': {'approvalStatus': 'approved'}}, {'fullName': 42},
])
def test_rejects_invalid_member_values(change):
    m = copy.deepcopy(SYNTHETIC_MEMBERS[0]); m.update(change)
    with pytest.raises(ValueError): MemberIndex.build([m])

def test_duplicate_ids_rejected():
    with pytest.raises(ValueError, match='duplicate'): MemberIndex.build([SYNTHETIC_MEMBERS[0]] * 2)

@pytest.mark.parametrize('threshold', [-1, 0, 1.1, float('nan')])
def test_invalid_threshold(threshold):
    with pytest.raises(ValueError): MemberIndex.build(SYNTHETIC_MEMBERS, threshold=threshold)

def test_pending_claims_excluded():
    m = copy.deepcopy(SYNTHETIC_MEMBERS[0]); m['_meta']['approvalStatus'] = 'pending'
    index = MemberIndex.build([m]); result = index.search(m['fullName'])
    assert index.members[0]['skills'] == []
    assert index.members[0]['contribution'] is None
    assert result['evidenceLinks'] == []
    assert 'Frontend developer' in result['introduction']  # supplied roster role
    assert 'Built the Ask' not in result['introduction']
    assert 'pending' in result['introduction']

def test_identifier_word_boundaries():
    index = MemberIndex.build(SYNTHETIC_MEMBERS)
    assert not index._exact_name_or_alias_hit('malice', index.members[0])

def test_real_roster_validates():
    index = MemberIndex.build(load_members(MEMBERS_FILE))
    assert len(index.members) == 4

def test_persistence_honors_directory(tmp_path):
    index = MemberIndex.build(SYNTHETIC_MEMBERS); index.save(tmp_path)
    loaded = MemberIndex.load(tmp_path)
    assert loaded.search('Alice') == index.search('Alice')
    meta = json.loads((tmp_path / 'meta.json').read_text()); meta['datasetFingerprint'] = 'invalid'
    (tmp_path / 'meta.json').write_text(json.dumps(meta))
    with pytest.raises(ValueError, match='fingerprint'): MemberIndex.load(tmp_path)

def test_real_tie():
    a = copy.deepcopy(SYNTHETIC_MEMBERS[0]); b = copy.deepcopy(a); b['id'] = 'second'
    result = MemberIndex.build([a,b]).search(a['fullName'])
    assert result['member']['id'] == a['id']
