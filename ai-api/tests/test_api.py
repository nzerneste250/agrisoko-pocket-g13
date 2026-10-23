"""Pytest suite for the FastAPI endpoints (app.py).

Tests hit the real API through Starlette's TestClient. The API loads (or
auto-builds) the TF-IDF index from ai-api/data/index on first use.
"""

from starlette.testclient import TestClient

from app import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == "1.0.0"
    assert body["groupCode"] == "G13"


# ---------------------------------------------------------------------------
# GET /members
# ---------------------------------------------------------------------------


def test_members_list():
    response = client.get("/members")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 4
    ids = {item["id"] for item in body}
    assert ids == {
        "nzayisenga-erneste",
        "ineza-benitha",
        "manzi-cedrick",
        "kirenga-alain-thierry",
    }
    # Safe directory fields only.
    for item in body:
        assert set(item.keys()) <= {
            "id",
            "fullName",
            "role",
            "githubUsername",
            "skills",
            "aliases",
            "approvalStatus",
        }
    erneste = next(i for i in body if i["id"] == "nzayisenga-erneste")
    assert erneste["fullName"] == "NZAYISENGA Erneste"
    assert erneste["role"] == "Group leader"
    assert erneste["githubUsername"] == "nzerneste250"
    # Records awaiting approval are marked as such.
    for item in body:
        assert item["approvalStatus"] == "pending"


# ---------------------------------------------------------------------------
# GET /members/{id}
# ---------------------------------------------------------------------------


def test_get_member_by_id():
    response = client.get("/members/nzayisenga-erneste")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "nzayisenga-erneste"
    assert body["fullName"] == "NZAYISENGA Erneste"
    assert body["registrationNumber"] == "25/27341"
    assert body["githubUsername"] == "nzerneste250"
    assert body["approvalStatus"] == "pending"


def test_unknown_member_returns_404():
    response = client.get("/members/no-such-member-id")
    assert response.status_code == 404

# ---------------------------------------------------------------------------
# POST /ask
# ---------------------------------------------------------------------------


def test_ask_missing_question():
    response = client.post("/ask", json={})
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "missing"


def test_ask_empty_question():
    response = client.post("/ask", json={"question": "   "})
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_ask_too_long_question():
    response = client.post("/ask", json={"question": "x" * 501})
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "string_too_long"


def test_ask_valid_member_question():
    response = client.post("/ask", json={"question": "Who is NZAYISENGA Erneste?"})
    assert response.status_code == 200
    body = response.json()
    assert body["matched"] is True
    assert body["member"]["id"] == "nzayisenga-erneste"
    assert body["member"]["fullName"] == "NZAYISENGA Erneste"
    assert body["confidence"] >= 0.45
    assert "NZAYISENGA Erneste" in body["introduction"]
    assert body["modelVersion"] == "1.0.0"
    assert body["groupCode"] == "G13"
    assert isinstance(body["evidenceLinks"], list)


def test_ask_no_match_question():
    response = client.post(
        "/ask", json={"question": "What is the weather forecast in Kigali?"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["matched"] is False
    assert body["member"] is None
    assert body["introduction"] == ""
    assert body["evidenceLinks"] == []


def test_ask_deterministic():
    a = client.post("/ask", json={"question": "INEZA Benitha"}).json()
    b = client.post("/ask", json={"question": "INEZA Benitha"}).json()
    assert a == b


def test_ask_safe_response_schema():
    response = client.post("/ask", json={"question": "NZAYISENGA Erneste"})
    body = response.json()
    assert set(body.keys()) <= {
        "matched",
        "member",
        "confidence",
        "reason",
        "introduction",
        "evidenceLinks",
        "modelVersion",
        "groupCode",
    }
    assert isinstance(body["confidence"], float)


def test_ask_no_invented_evidence_fields():
    response = client.post("/ask", json={"question": "NZAYISENGA Erneste"})
    body = response.json()
    if body["matched"]:
        assert body["evidenceLinks"] == []


# ---------------------------------------------------------------------------
# GET /model-info
# ---------------------------------------------------------------------------


def test_model_info():
    response = client.get("/model-info")
    assert response.status_code == 200
    body = response.json()
    assert body["vectorizerType"] == "tfidf-word-ngram-(1,2)"
    assert body["confidenceThreshold"] == 0.45
    assert isinstance(body["datasetFingerprint"], str)
    assert len(body["datasetFingerprint"]) == 64
    assert isinstance(body["limitations"], list)
    assert len(body["limitations"]) > 0
    # buildCommit is None until the repo has a commit; that is truthful.
    assert body["buildCommit"] is None or isinstance(body["buildCommit"], str)



def test_ask_rejects_wrong_type_and_extra_fields():
    for body in ({"question": 42}, {"question": None}, {"question": []}, {"question": "Erneste", "unknown": True}):
        assert client.post("/ask", json=body).status_code == 422
