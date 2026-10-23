"""AgriSoko Pocket G13 — AI information-retrieval API (FastAPI).

Endpoints:
  GET    /health           service status, version and group code
  GET    /members          safe directory fields for all members
  GET    /members/{id}     one member profile (HTTP 404 if not found)
  POST   /ask              natural-language question -> top match
  GET    /model-info       vectorizer type, threshold, fingerprint, limitations
"""

from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException, Path as PathParam, status
from pydantic import BaseModel, Field, ConfigDict

from matching import (
    GROUP_CODE,
    INDEX_DIR,
    MEMBERS_FILE,
    MemberIndex,
    MAX_QUESTION_LENGTH,
    current_git_commit,
    load_members,
)

app = FastAPI(
    title="AgriSoko Pocket G13 AI API",
    description="Deterministic TF-IDF member directory lookup for AgriSoko Pocket G13.",
    version="1.0.0",
)

_index: MemberIndex | None = None


def get_index() -> MemberIndex:
    global _index
    if _index is None:
        # Rebuild from source at process start; never serve a stale persisted roster.
        _index = MemberIndex.build(load_members(MEMBERS_FILE), threshold=float(os.getenv("CONFIDENCE_THRESHOLD", "0.45")), build_commit=current_git_commit())
        _index.save(INDEX_DIR)
    return _index


class AskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    question: str = Field(
        min_length=1,
        max_length=MAX_QUESTION_LENGTH,
        description="Natural-language question about a team member.",
        examples=["Who is NZAYISENGA Erneste?", "Tell me about the group leader"],
    )


class MemberDirectoryItem(BaseModel):
    skills: list[str] = Field(default_factory=list)
    aliases: list[str] = Field(default_factory=list)
    approvalStatus: str = "pending"
    id: str
    fullName: str
    role: str | None = None
    githubUsername: str | None = None

class MemberProfile(BaseModel):
    id: str
    fullName: str
    registrationNumber: str | None = None
    aliases: list[str] = Field(default_factory=list)
    githubUsername: str | None = None
    role: str | None = None
    skills: list[str] = Field(default_factory=list)
    targetUser: str | None = None
    problem: str | None = None
    contribution: str | None = None
    feature: str | None = None
    outcomeMetric: str | None = None
    evidenceLinks: list[str] = Field(default_factory=list)
    testerFeedback: str | None = None
    introductionDraft: str | None = None
    approvalStatus: str | None = None


class AskResponse(BaseModel):
    matched: bool
    member: dict[str, Any] | None = None
    confidence: float
    reason: str
    introduction: str
    evidenceLinks: list[str]
    modelVersion: str
    groupCode: str


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "version": "1.0.0",
        "groupCode": GROUP_CODE,
    }


@app.get("/members", response_model=list[MemberDirectoryItem], tags=["directory"])
def list_members() -> list[dict[str, Any]]:
    index = get_index()
    directory: list[dict[str, Any]] = []
    for member in index.members:
        directory.append(
            {
                "id": member["id"],
                "fullName": member["fullName"],
                "role": member.get("role"),
                "githubUsername": member.get("githubUsername"),
                "aliases": member.get("aliases") or [],
                "skills": member.get("skills") or [],
                "approvalStatus": member.get("_meta", {}).get("approvalStatus", "pending"),
            }
        )
    return directory


@app.get("/members/{member_id}", response_model=MemberProfile, tags=["directory"])
def get_member(
    member_id: str = PathParam(..., description="Member id from the directory."),
) -> dict[str, Any]:
    index = get_index()
    for member in index.members:
        if member["id"] == member_id:
            meta = member.get("_meta", {}) or {}
            return {
                "id": member["id"],
                "fullName": member["fullName"],
                "registrationNumber": member.get("registrationNumber"),
                "aliases": member.get("aliases") or [],
                "githubUsername": member.get("githubUsername"),
                "role": member.get("role"),
                "skills": member.get("skills") or [],
                "targetUser": member.get("targetUser"),
                "problem": member.get("problem"),
                "contribution": member.get("contribution"),
                "feature": member.get("feature"),
                "outcomeMetric": member.get("outcomeMetric"),
                "evidenceLinks": member.get("evidenceLinks") or [],
                "testerFeedback": member.get("testerFeedback"),
                "introductionDraft": member.get("introductionDraft"),
                "approvalStatus": meta.get("approvalStatus", "pending"),
            }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Member with id '{member_id}' not found.",
    )


@app.post("/ask", response_model=AskResponse, tags=["ask"])
def ask(payload: AskRequest) -> dict[str, Any]:
    question = payload.question.strip()
    if len(question) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question must not be empty.",
        )
    if len(question) > MAX_QUESTION_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Question is too long (maximum {MAX_QUESTION_LENGTH} characters).",
        )

    index = get_index()
    result = index.search(question)
    return {
        "matched": result["matched"],
        "member": result["member"],
        "confidence": result["confidence"],
        "reason": result["reason"],
        "introduction": result["introduction"],
        "evidenceLinks": result["evidenceLinks"],
        "modelVersion": result["modelVersion"],
        "groupCode": result["groupCode"],
    }


@app.get("/model-info", tags=["system"])
def model_info() -> dict[str, Any]:
    index = get_index()
    meta_path = INDEX_DIR / "meta.json"
    limitations: list[str] = []
    if meta_path.exists():
        try:
            import json

            with meta_path.open("r", encoding="utf-8") as fh:
                limitations = json.load(fh).get("limitations", [])
        except Exception:  # noqa: BLE001 - degrade gracefully
            limitations = []
    return {
        "version": "1.0.0",
        "groupCode": GROUP_CODE,
        "modelVersion": index.model_version,
        "vectorizerType": "tfidf-word-ngram-(1,2)",
        "confidenceThreshold": index.threshold,
        "datasetFingerprint": index.fingerprint,
        "limitations": limitations,
        "buildCommit": index.build_commit,
    }
