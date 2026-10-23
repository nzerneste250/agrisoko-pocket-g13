"""Pytest suite for the deterministic TF-IDF matching engine (matching.py).

These tests exercise the engine directly with synthetic member datasets so they
do not depend on the committed roster data staying unchanged.
"""

import json
import math
import os
import tempfile
from pathlib import Path

import pytest

from matching import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    MemberIndex,
    current_git_commit,
    dataset_fingerprint,
    load_members,
    member_document,
    normalize_member_records,
    normalize_text,
)

SYNTHETIC_MEMBERS = [
    {
        "id": "m-alice",
        "fullName": "ALICE UWIMANA",
        "registrationNumber": "25/10001",
        "aliases": ["Alice", "Uwimana"],
        "githubUsername": "alice-dev",
        "role": "Frontend developer",
        "skills": ["React Native", "TypeScript", "Expo"],
        "targetUser": "Smallholder farmers",
        "problem": "Farmers lack market price information.",
        "contribution": "Built the Ask the Team screen.",
        "feature": "Member directory",
        "outcomeMetric": None,
        "evidenceLinks": ["https://github.com/alice-dev/agrisoko"],
        "testerFeedback": None,
        "introductionDraft": None,
        "_meta": {
            "approvalStatus": "approved",
            "approvedBy": "synthetic fixture",
            "approvedAt": "2026-10-23",
            "source": "synthetic test data",
        },
    },
    {
        "id": "m-bob",
        "fullName": "BOB KAMANZI",
        "registrationNumber": None,
        "aliases": [],
        "githubUsername": None,
        "role": "AI engineer",
        "skills": ["Python", "scikit-learn", "FastAPI"],
        "targetUser": "Cooperative members",
        "problem": "No reliable team member lookup.",
        "contribution": "Implemented TF-IDF matching engine.",
        "feature": "AI search",
        "outcomeMetric": None,
        "evidenceLinks": [],
        "testerFeedback": None,
        "introductionDraft": None,
        "_meta": {
            "approvalStatus": "approved",
            "approvedBy": "synthetic fixture",
            "approvedAt": "2026-10-23",
            "source": "synthetic test data",
        },
    },
    {
        "id": "m-carla",
        "fullName": "CARLA MUTONI",
        "registrationNumber": None,
        "aliases": [],
        "githubUsername": None,
        "role": None,
        "skills": [],
        "targetUser": None,
        "problem": None,
        "contribution": None,
        "feature": None,
        "outcomeMetric": None,
        "evidenceLinks": [],
        "testerFeedback": None,
        "introductionDraft": None,
        "_meta": {
            "approvalStatus": "approved",
            "approvedBy": "synthetic fixture",
            "approvedAt": "2026-10-23",
            "source": "synthetic test data",
        },
    },
]


def build_synthetic_index(threshold=DEFAULT_CONFIDENCE_THRESHOLD):
    return MemberIndex.build(SYNTHETIC_MEMBERS, threshold=threshold)


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------


def test_normalize_text_lowercases_and_strips_accents():
    assert normalize_text("  Nzayisenga  ") == "nzayisenga"
    assert normalize_text("Caf\u00e9 M\u00e9lange") == "cafe melange"
    assert normalize_text("25/27341!") == "25 27341"
    assert normalize_text(None) == ""
    assert normalize_text("") == ""


# ---------------------------------------------------------------------------
# Schema validation / empty dataset
# ---------------------------------------------------------------------------


def test_member_schema_validation_required_fields():
    incomplete = dict(SYNTHETIC_MEMBERS[0])
    del incomplete["role"]
    with pytest.raises(ValueError, match="missing required fields"):
        MemberIndex.build([incomplete])


def test_member_schema_validation_empty_ids():
    bad = dict(SYNTHETIC_MEMBERS[0])
    bad["id"] = ""
    with pytest.raises(ValueError, match="non-empty id and fullName"):
        MemberIndex.build([bad])


def test_empty_dataset_fails_clearly():
    with pytest.raises(ValueError, match="non-empty 'members' list"):
        MemberIndex.build([])


def test_dataset_without_indexable_text_fails_clearly():
    empty_docs = [
        {
            **SYNTHETIC_MEMBERS[0],
            "fullName": "",
            "aliases": [],
            "role": None,
            "skills": [],
        }
    ]
    with pytest.raises(ValueError, match="non-empty id and fullName"):
        MemberIndex.build(empty_docs)


def test_load_members_validates_file(tmp_path):
    p = tmp_path / "members.json"
    p.write_text("{\"members\": []}", encoding="utf-8")
    with pytest.raises(ValueError):
        load_members(p)


# ---------------------------------------------------------------------------
# Exact full-name and alias matching
# ---------------------------------------------------------------------------


def test_exact_full_name_match():
    index = build_synthetic_index()
    result = index.search("ALICE UWIMANA")
    assert result["matched"] is True
    assert result["member"]["id"] == "m-alice"
    assert result["confidence"] >= DEFAULT_CONFIDENCE_THRESHOLD


def test_accepted_aliases_match():
    index = build_synthetic_index()
    result = index.search("Alice")
    assert result["matched"] is True
    assert result["member"]["id"] == "m-alice"
    assert "exact" in result["reason"].lower()


def test_case_insensitive_name_match():
    index = build_synthetic_index()
    result = index.search("alice uwimana")
    assert result["matched"] is True
    assert result["member"]["id"] == "m-alice"


def test_registration_number_match():
    index = build_synthetic_index()
    result = index.search("25 10001")
    assert result["matched"] is True
    assert result["member"]["id"] == "m-alice"


# ---------------------------------------------------------------------------
# Role / skill / feature / contribution search
# ---------------------------------------------------------------------------


def test_role_search():
    index = build_synthetic_index()
    result = index.search("AI engineer")
    assert result["matched"] is True
    assert result["member"]["id"] == "m-bob"


def test_skill_search():
    index = build_synthetic_index()
    result = index.search("scikit-learn FastAPI")
    assert result["matched"] is True
    assert result["member"]["id"] == "m-bob"


def test_feature_search():
    index = build_synthetic_index()
    result = index.search("member directory")
    assert result["matched"] is True
    assert result["member"]["id"] == "m-alice"


def test_contribution_search():
    index = build_synthetic_index()
    result = index.search("TF-IDF matching engine")
    assert result["matched"] is True
    assert result["member"]["id"] == "m-bob"


# ---------------------------------------------------------------------------
# No-match questions
# ---------------------------------------------------------------------------


def test_no_match_question_returns_safe_response():
    index = build_synthetic_index()
    result = index.search("what is the weather forecast for Kigali tomorrow")
    assert result["matched"] is False
    assert result["member"] is None
    assert result["introduction"] == ""
    assert result["evidenceLinks"] == []
    assert 0.0 <= result["confidence"] <= 1.0


def test_no_match_gibberish():
    index = build_synthetic_index()
    result = index.search("asdfghjkl qwerty uiop")
    assert result["matched"] is False
    assert result["member"] is None


# ---------------------------------------------------------------------------
# Confidence threshold behavior
# ---------------------------------------------------------------------------


def test_threshold_rejects_weak_matches():
    index = build_synthetic_index(threshold=0.9)
    result = index.search("developer")
    assert result["matched"] is False


def test_threshold_accepts_strong_matches():
    index = build_synthetic_index(threshold=0.1)
    result = index.search("developer")
    assert result["matched"] is True


def test_threshold_is_configurable():
    index = build_synthetic_index(threshold=0.6)
    assert index.threshold == 0.6


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_deterministic_results():
    index = build_synthetic_index()
    first = index.search("ALICE UWIMANA")
    second = index.search("ALICE UWIMANA")
    assert first == second


def test_deterministic_tie_handling():
    index = build_synthetic_index(threshold=0.1)
    r1 = index.search("developer")
    r2 = index.search("developer")
    assert r1 == r2
    assert r1["member"]["id"] in ("m-alice", "m-bob")


# ---------------------------------------------------------------------------
# Dataset fingerprint
# ---------------------------------------------------------------------------


def test_dataset_fingerprint_is_stable():
    fp1 = dataset_fingerprint(SYNTHETIC_MEMBERS)
    fp2 = dataset_fingerprint(SYNTHETIC_MEMBERS)
    assert fp1 == fp2
    assert len(fp1) == 64  # SHA-256 hex


def test_fingerprint_changes_when_data_changes():
    fp1 = dataset_fingerprint(SYNTHETIC_MEMBERS)
    changed = [dict(m, fullName=m["fullName"] + " X") for m in SYNTHETIC_MEMBERS]
    fp2 = dataset_fingerprint(changed)
    assert fp1 != fp2


# ---------------------------------------------------------------------------
# Introduction is evidence-grounded (no invented content)
# ---------------------------------------------------------------------------


def test_introduction_contains_only_dataset_fields():
    index = build_synthetic_index()
    result = index.search("ALICE UWIMANA")
    intro = result["introduction"]
    assert "ALICE UWIMANA" in intro
    assert "Frontend developer" in intro
    assert "25/10001" in intro
    assert "alice-dev" in intro
    # Carla's record is empty: introduction must not invent details.
    result_c = index.search("CARLA MUTONI")
    assert "No additional profile information is available yet" in result_c["introduction"]


def test_no_invented_evidence_fields():
    index = build_synthetic_index()
    result = index.search("BOB KAMANZI")
    assert result["evidenceLinks"] == []
    result_a = index.search("ALICE UWIMANA")
    assert result_a["evidenceLinks"] == ["https://github.com/alice-dev/agrisoko"]
