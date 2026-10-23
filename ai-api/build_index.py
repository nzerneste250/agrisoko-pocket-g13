"""Build the TF-IDF search index for the AgriSoko Pocket G13 member directory.

Usage:
    python build_index.py

The command:
  1. Validates members.json (schema fields, non-empty dataset).
  2. Normalizes member records.
  3. Builds the TF-IDF index (word unigrams+bigrams, cosine similarity).
  4. Produces a SHA-256 fingerprint of the dataset.
  5. Saves model metadata and version information.
  6. Records limitations.
  7. Fails clearly on invalid or empty datasets.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from matching import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    INDEX_DIR,
    MEMBERS_FILE,
    MemberIndex,
    current_git_commit,
    load_members,
    normalize_member_records,
)

CONFIDENCE_THRESHOLD = 0.45


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--threshold", type=float, default=DEFAULT_CONFIDENCE_THRESHOLD)
    args = parser.parse_args()
    try:
        members = load_members(MEMBERS_FILE)
    except FileNotFoundError:
        print(f"ERROR: dataset file not found: {MEMBERS_FILE}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"ERROR: members.json is not valid JSON: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"ERROR: invalid members dataset: {exc}", file=sys.stderr)
        return 1

    try:
        normalized = members
        if len(normalized) == 0:
            print("ERROR: dataset contains no members", file=sys.stderr)
            return 1
        index = MemberIndex.build(
            normalized,
            threshold=args.threshold,
            build_commit=current_git_commit(),
        )
        index.save(INDEX_DIR)
    except ValueError as exc:
        print(f"ERROR: index build failed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 - report unexpected failures clearly
        print(f"ERROR: unexpected index build failure: {exc}", file=sys.stderr)
        return 1

    meta = {
        "modelVersion": index.model_version,
        "groupCode": index.group_code,
        "vectorizerType": "tfidf-word-ngram-(1,2)",
        "confidenceThreshold": index.threshold,
        "datasetFingerprint": index.fingerprint,
        "memberCount": len(index.members),
        "memberIds": [m["id"] for m in index.members],
        "buildCommit": index.build_commit,
    }
    print("Index built successfully.")
    print(f"  members: {index.fingerprint[:16]}... (SHA-256 fingerprint: {index.fingerprint})")
    print(f"  threshold: {index.threshold}")
    print(f"  model version: {index.model_version}")
    print(f"  group code: {index.group_code}")
    print(f"  build commit: {index.build_commit or 'not available'}")
    print(f"  artifacts: {INDEX_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
