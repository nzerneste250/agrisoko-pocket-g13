"""Deterministic grounded retrieval.

English stop words are removed from normalized unigram/bigram TF-IDF vectors.
Ranking uses the maximum cosine over the full profile and role/skills/feature/
contribution fields; exact whole-phrase roster identifiers take precedence with
score 1. Scores are retrieval scores, not probabilities. Threshold defaults to
0.45, with dataset-order tie breaking. Pending technical facts are excluded;
supplied roster identity and role remain visible with a pending approval label.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import unicodedata
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DEFAULT_CONFIDENCE_THRESHOLD = 0.45
MAX_QUESTION_LENGTH = 500
MODEL_VERSION = "1.0.0"
GROUP_CODE = "G13"
VECTORIZER_TYPE = "tfidf-word-ngram-(1,2)"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
INDEX_DIR = DATA_DIR / "index"
MEMBERS_FILE = DATA_DIR / "members.json"
VECTORIZER_FILE = INDEX_DIR / "vectorizer.pkl"
MATRIX_FILE = INDEX_DIR / "tfidf_matrix.npz"
INDEXED_MEMBERS_FILE = INDEX_DIR / "members.json"
META_FILE = INDEX_DIR / "meta.json"

REQUIRED_MEMBER_FIELDS = [
    "id",
    "fullName",
    "registrationNumber",
    "aliases",
    "githubUsername",
    "role",
    "skills",
    "targetUser",
    "problem",
    "contribution",
    "feature",
    "outcomeMetric",
    "evidenceLinks",
    "testerFeedback",
    "introductionDraft",
    "_meta",
]

DOCUMENT_FIELDS = [
    "fullName",
    "aliases",
    "registrationNumber",
    "githubUsername",
    "role",
    "skills",
    "targetUser",
    "problem",
    "contribution",
    "feature",
    "introductionDraft",
]


def normalize_text(text: str | None) -> str:
    if text is None:
        return ""
    text = str(text).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_members(path: Path = MEMBERS_FILE) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("dataset must be an object")
    members = data.get("members", [])
    if not isinstance(members, list) or len(members) == 0:
        raise ValueError("members.json must contain a non-empty 'members' list")
    return members


def validate_members(members: list[dict[str, Any]]) -> None:
    if not isinstance(members, list) or not members:
        raise ValueError("dataset requires a non-empty 'members' list")
    seen = set()
    for member in members:
        if not isinstance(member, dict):
            raise ValueError("each member record must be an object")
        missing = [f for f in REQUIRED_MEMBER_FIELDS if f not in member]
        if missing:
            raise ValueError(
                f"member record missing required fields: {', '.join(missing)}"
            )
        if not all(isinstance(member.get(k), str) and member[k].strip() for k in ("id", "fullName")):
            raise ValueError("each member must have a non-empty id and fullName")
        if member['id'] in seen:
            raise ValueError('duplicate member id')
        seen.add(member['id'])
        for field in ('aliases', 'skills', 'evidenceLinks'):
            if not isinstance(member[field], list) or any(not isinstance(v, str) or not v.strip() for v in member[field]):
                raise ValueError(f'{field} must be a list of non-empty strings')
        for field in REQUIRED_MEMBER_FIELDS:
            if field not in ('id','fullName','aliases','skills','evidenceLinks','_meta'):
                if member[field] is not None and not isinstance(member[field], str):
                    raise ValueError(f'{field} must be string or null')
        meta = member['_meta']
        if not isinstance(meta, dict) or meta.get('approvalStatus') not in ('pending', 'approved'):
            raise ValueError('invalid approvalStatus')
        if meta.get('approvalStatus') == 'approved' and not (meta.get('approvedBy') and meta.get('approvedAt')):
            raise ValueError('approved records require approvedBy and approvedAt')
        from urllib.parse import urlparse
        for link in member['evidenceLinks']:
            u = urlparse(link)
            if u.scheme != 'https' or not u.hostname or u.username or u.password:
                raise ValueError('evidenceLinks require safe HTTPS URLs')



def normalize_member_records(members: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for member in members:
        record = dict(member)
        if member.get("_meta", {}).get("approvalStatus") != "approved":
            for field in ("skills", "targetUser", "problem", "contribution", "feature", "outcomeMetric", "evidenceLinks", "testerFeedback", "introductionDraft"):
                record[field] = [] if field in ("skills", "evidenceLinks") else None
        for field in ("aliases", "skills", "evidenceLinks"):
            val = record.get(field)
            record[field] = list(val) if isinstance(val, list) else []
        for field in (
            "registrationNumber",
            "githubUsername",
            "role",
            "targetUser",
            "problem",
            "contribution",
            "feature",
            "outcomeMetric",
            "testerFeedback",
            "introductionDraft",
        ):
            record.setdefault(field, None)
        meta = record.get("_meta")
        record["_meta"] = meta if isinstance(meta, dict) else {}
        normalized.append(record)
    return normalized


def member_document(member: dict[str, Any]) -> str:
    parts: list[str] = []
    for field in DOCUMENT_FIELDS:
        value = member.get(field)
        if value is None:
            continue
        if isinstance(value, list):
            parts.extend(str(v) for v in value if v)
        else:
            parts.append(str(value))
    return " ".join(parts).strip()


def dataset_fingerprint(members: list[dict[str, Any]]) -> str:
    canonical = json.dumps(
        members, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def current_git_commit() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            cwd=BASE_DIR.parent,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return None

class MemberIndex:
    """In-memory TF-IDF index over member documents."""

    def __init__(
        self,
        members: list[dict[str, Any]],
        vectorizer: TfidfVectorizer,
        matrix: np.ndarray,
        fingerprint: str,
        threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
        build_commit: str | None = None,
    ) -> None:
        self.members = members
        self.vectorizer = vectorizer
        self.matrix = matrix
        self.fingerprint = fingerprint
        self.threshold = threshold
        self.build_commit = build_commit
        self.model_version = MODEL_VERSION
        self.group_code = GROUP_CODE
        # Pre-computed normalized token sets per member, used for the query
        # coverage component of the match score.
        self._member_token_sets: list[set[str]] = [
            set(normalize_text(member_document(m)).split()) for m in members
        ]

    @classmethod
    def build(
        cls,
        members: list[dict[str, Any]],
        threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
        build_commit: str | None = None,
    ) -> "MemberIndex":
        if not isinstance(threshold, (int, float)) or not np.isfinite(threshold) or not 0 < threshold <= 1:
            raise ValueError("threshold must be in (0, 1]")
        validate_members(members)
        normalized = normalize_member_records(members)
        if len(normalized) == 0:
            raise ValueError("cannot build an index from an empty dataset")

        documents = [normalize_text(member_document(m)) for m in normalized]
        if all(len(doc) == 0 for doc in documents):
            raise ValueError("dataset contains no indexable text")

        vectorizer = TfidfVectorizer(
            lowercase=False,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
            dtype=np.float64,
            use_idf=True,
            smooth_idf=True,
            norm="l2",
            token_pattern=r"(?u)\b\w\w+\b",
        )
        matrix = vectorizer.fit_transform(documents)
        fingerprint = dataset_fingerprint(normalized)
        return cls(
            members=normalized,
            vectorizer=vectorizer,
            matrix=matrix,
            fingerprint=fingerprint,
            threshold=threshold,
            build_commit=build_commit,
        )

    def save(self, index_dir: Path = INDEX_DIR) -> None:
        index_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.vectorizer, (index_dir / "vectorizer.pkl"))
        from scipy import sparse

        sparse.save_npz(str((index_dir / "tfidf_matrix.npz")), self.matrix)
        with (index_dir / "members.json").open("w", encoding="utf-8") as fh:
            json.dump(self.members, fh, ensure_ascii=False, indent=2)
        meta = {
            "modelVersion": self.model_version,
            "groupCode": self.group_code,
            "vectorizerType": VECTORIZER_TYPE,
            "confidenceThreshold": self.threshold,
            "datasetFingerprint": self.fingerprint,
            "memberCount": len(self.members),
            "memberIds": [m["id"] for m in self.members],
            "buildCommit": self.build_commit,
            "limitations": [
                "Roster facts were supplied by the user; individual approval is pending. Pending technical claims and evidence are excluded.",
                "Matching is lexical: English stop words removed, TF-IDF word unigrams/bigrams, maximum cosine over profile or role/skills/feature/contribution field. Exact identifiers score 1. Ties use dataset order. Scores are not probabilities.",
                "With sparse profile data, queries match primarily on member names, registration numbers, aliases and GitHub usernames.",
                "No generative model is used; introductions are assembled strictly from dataset fields.",
            ],
        }
        with (index_dir / "meta.json").open("w", encoding="utf-8") as fh:
            json.dump(meta, fh, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, index_dir: Path = INDEX_DIR) -> "MemberIndex":
        import scipy.sparse as sparse

        vectorizer = joblib.load((index_dir / "vectorizer.pkl"))
        matrix = sparse.load_npz(str(index_dir / "tfidf_matrix.npz"))
        with (index_dir / "members.json").open("r", encoding="utf-8") as fh:
            members = json.load(fh)
        with (index_dir / "meta.json").open("r", encoding="utf-8") as fh:
            meta = json.load(fh)
        validate_members(members)
        if dataset_fingerprint(members) != meta.get("datasetFingerprint"):
            raise ValueError("persisted dataset fingerprint mismatch")
        return cls(
            members=members,
            vectorizer=vectorizer,
            matrix=matrix,
            fingerprint=meta.get("datasetFingerprint", ""),
            threshold=meta.get("confidenceThreshold", DEFAULT_CONFIDENCE_THRESHOLD),
            build_commit=meta.get("buildCommit"),
        )


    def _exact_name_or_alias_hit(self, question_norm: str, member: dict[str, Any]) -> bool:
        name_norm = normalize_text(member.get("fullName", ""))
        if name_norm and (question_norm == name_norm or f" {name_norm} " in f" {question_norm} "):
            return True
        for alias in member.get("aliases", []) or []:
            alias_norm = normalize_text(alias)
            if alias_norm and (question_norm == alias_norm or f" {alias_norm} " in f" {question_norm} "):
                return True
        reg = member.get("registrationNumber")
        if reg:
            reg_norm = normalize_text(reg)
            if reg_norm and (question_norm == reg_norm or f" {reg_norm} " in f" {question_norm} "):
                return True
        github = member.get("githubUsername")
        if github:
            gh_norm = normalize_text(github)
            if gh_norm and (question_norm == gh_norm or f" {gh_norm} " in f" {question_norm} "):
                return True
        return False

    def search(self, question: str) -> dict[str, Any]:
        if not isinstance(question, str) or not question.strip():
            return {
                "matched": False,
                "member": None,
                "confidence": 0.0,
                "reason": "Question is empty.",
                "introduction": "",
                "evidenceLinks": [],
                "modelVersion": self.model_version,
                "groupCode": self.group_code,
            }

        question_norm = normalize_text(question)
        if not question_norm:
            return {
                "matched": False,
                "member": None,
                "confidence": 0.0,
                "reason": "Question contained no indexable text.",
                "introduction": "",
                "evidenceLinks": [],
                "modelVersion": self.model_version,
                "groupCode": self.group_code,
            }

        q_vec = self.vectorizer.transform([question_norm])
        sims = cosine_similarity(q_vec, self.matrix)[0]

        scores = []
        for i, member in enumerate(self.members):
            exact = self._exact_name_or_alias_hit(question_norm, member)
            # Exact roster identifiers are authoritative; lexical scores are separate.
            # Short field vectors avoid diluting a skill/role by a long biography.
            fields = []
            for field in ('role', 'skills', 'feature', 'contribution'):
                value = member.get(field)
                if value:
                    fields.append(normalize_text(' '.join(value) if isinstance(value, list) else value))
            field_score = 0.0
            if fields:
                field_score = float(cosine_similarity(q_vec, self.vectorizer.transform(fields)).max())
            score = 1.0 if exact else max(float(sims[i]), field_score)
            scores.append(score)
        top_idx = max(range(len(scores)), key=lambda i: (scores[i], -i))
        top_score = scores[top_idx]
        top_member = self.members[top_idx]
        boosted = self._exact_name_or_alias_hit(question_norm, top_member)
        reason_parts = ["exact name/alias/registration/github match" if boosted else
                        f"TF-IDF cosine similarity (best profile or field) {top_score:.3f}"]
        confidence = round(top_score, 4)
        matched = top_score >= self.threshold

        if matched:
            reason = "; ".join(reason_parts) if reason_parts else "best profile match"
            if boosted:
                reason += " (exact identifier precedence)"
            return {
                "matched": True,
                "member": {
                    "id": top_member["id"],
                    "fullName": top_member["fullName"],
                    "registrationNumber": top_member.get("registrationNumber"),
                    "role": top_member.get("role"),
                    "githubUsername": top_member.get("githubUsername"),
                    "approvalStatus": top_member.get("_meta", {}).get("approvalStatus", "pending"),
                },
                "confidence": confidence,
                "reason": reason,
                "introduction": self._build_introduction(top_member),
                "evidenceLinks": list(top_member.get("evidenceLinks", []) or []),
                "modelVersion": self.model_version,
                "groupCode": self.group_code,
            }

        reason = (
            f"Best match ({top_member['fullName']}) scored {top_score:.3f}, "
            f"below the confidence threshold of {self.threshold}."
        )
        return {
            "matched": False,
            "member": None,
            "confidence": confidence,
            "reason": reason,
            "introduction": "",
            "evidenceLinks": [],
            "modelVersion": self.model_version,
            "groupCode": self.group_code,
        }

    def _matching_token_count(self, question_norm: str, member: dict[str, Any]) -> int:
        doc = normalize_text(member_document(member))
        q_tokens = set(question_norm.split())
        doc_tokens = set(doc.split())
        return len(q_tokens & doc_tokens)

    def _build_introduction(self, member: dict[str, Any]) -> str:
        name = member.get("fullName", "this member")
        parts: list[str] = [name]
        if member.get("_meta", {}).get("approvalStatus") != "approved":
            parts.append("Profile pending member approval; only supplied roster facts are shown.")
        role = member.get("role")
        if role:
            parts.append(f"{name} is the {role} of AgriSoko Pocket G13.")
        reg = member.get("registrationNumber")
        if reg:
            parts.append(f"Registration number: {reg}.")
        github = member.get("githubUsername")
        if github:
            parts.append(f"GitHub: {github}.")
        skills = [s for s in (member.get("skills") or []) if s]
        if skills:
            parts.append(f"Skills: {', '.join(skills)}.")
        contribution = member.get("contribution")
        if contribution:
            parts.append(f"Contribution: {contribution}.")
        if len(parts) == 1:
            parts.append("No additional profile information is available yet.")
        else:
            parts.append(
                "Remaining profile fields are awaiting member approval and are not displayed."
            )
        return " ".join(parts)
