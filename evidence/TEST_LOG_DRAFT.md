# TEST LOG ? DRAFT WITH ACTUAL AUTOMATED RESULTS

Project: AgriSoko Pocket G13 / Group G13. Date: 2026-10-23.
Environment: Windows PowerShell, existing Python 3.14 virtual environment, Node 24.16.0, npm 11.13.0, Expo SDK 58.0.17.

Executed backend: python -m pytest -q --basetemp=.pytest-tmp-final
Result: 54 passed; one upstream Starlette TestClient/httpx deprecation warning. pip check: no broken requirements found.
Coverage: record/schema validation, empty dataset, thresholds, exact identifiers, aliases, role/skill/feature/contribution, no-match, deterministic ties, persistence/fingerprint, grounding and all API routes.

Executed real HTTP: 11 urllib requests over actual TCP to uvicorn on 127.0.0.1:8013. Expected 200/404/422/400 statuses passed. Full bodies recorded in docs/HTTP_TEST_RESULTS.json.

Executed evaluation: python evaluate.py. 12/12 identity-query top-1 matches, 5/5 deliberate no-match rejections; zero observed errors. Three identity paraphrases per member. Not a measure of real skill/feature generalization; technical records await approval. See docs/AI_EVALUATION.json for every query.

Executed mobile: six focused domain unit tests passed. tsc --noEmit passed. Expo Doctor: 20/20 checks passed. Android production Metro export succeeded. These results do not validate physical-device rendering, navigation, persistence, connectivity transitions or installation.

Security check: npm audit reports 15 high affected nodes from two underlying transitive advisories; unresolved. See docs/SECURITY_FINDINGS.md. Initial diagnostics/test attempts and their corrections are documented in docs/CHANGELOG.md.

NOT EXECUTED: real Android APK installation; device UI/TalkBack/rotation; storage kill/relaunch; real phone-to-API integration; genuine tester feedback. No tested device, tester signature or APK hash is asserted.

Complete the manual rows after actual testing: device/model, Android version, APK SHA-256, tester/date, scenario, expected behavior, observed behavior, pass/fail, screenshot/video reference and fix/retest evidence. Use docs/DEVICE_TEST_CHECKLIST.md.
