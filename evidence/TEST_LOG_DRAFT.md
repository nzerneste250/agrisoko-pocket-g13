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

OWNER-REPORTED: APK installation and launch succeeded; online API connectivity failed and remains unresolved. No installation was performed by the finalization agent. NOT VERIFIED: device UI/TalkBack/rotation; storage kill/relaunch; successful phone-to-API integration; genuine tester feedback. Device model/version and tester signatures are unavailable. See current artifact hash and evidence provenance below.

Complete the manual rows after actual testing: device/model, Android version, APK SHA-256, tester/date, scenario, expected behavior, observed behavior, pass/fail, screenshot/video reference and fix/retest evidence. Use docs/DEVICE_TEST_CHECKLIST.md.

## Submission status - 2026-10-23: INCOMPLETE

Repository: https://github.com/nzerneste250/agrisoko-pocket-g13
Release: https://github.com/nzerneste250/agrisoko-pocket-g13/releases/tag/v1.0.0
Confirmed source commit: ccc89860d7bd589f028357afe1fd90371b76c498 (ccc8986).
Repository and published release were read on 2026-10-23; the release points to ccc8986. These documentation/packaging updates are local changes after that commit; no new commit, push or release update is claimed. APK provenance is not independently linked to an EAS build or this exact source commit.

Verified locally: build/AgriSokoPocket_G13.apk exists (68,902,179 bytes).
APK SHA-256: f54de6242dd259b68005707c1a186a5e9f7b08493bb87679af1ff614c4a1faee.
The APK was not rebuilt or modified during finalization.

Recorded Android result: the owner reports successful installation and launch; the published release repeats that result. This is genuine owner-reported evidence, not an agent-observed installation or independent second test. Online API connectivity failed in the recorded phone test and remains unresolved. The workstation /health 200 in docs/DEVICE_FIX_REPORT.md does not prove phone connectivity. No device model/version, logcat, installed manifest, screenshots or signed test record is available here. Full offline/cache/accessibility/reconnection acceptance remains unverified.

Evidence status: automated results are historical recorded measurements (backend 54 tests, localhost HTTP 11 checks, identity evaluation 12/12 and no-match 5/5; latest follow-up mobile 25 tests, TypeScript, Expo Doctor 20/20, four sync tests and JS export). They were not rerun in this documentation-only finalization. PDFs are readable draft records/templates, not signed final evidence. Contributions have no verified assessed issues, substantial member PRs or meaningful peer reviews; feedback count is zero. No signatures, reviewers, testers, quotations, individual implementation ownership or demonstration evidence have been invented.

Known limitations and missing evidence:
- Official assignment PDF absent: rubric compliance cannot be certified.
- All four profile approvals pending; other members' registrations/accounts and technical facts remain unverified. Agricultural target users, problem, delivered agricultural features and outcomes lack supplied facts; current product is team lookup.
- Genuine per-member issue/PR/review/explanation evidence and any required signatures absent.
- Genuine independent tester feedback and full device acceptance records/screenshots absent.
- Required evidence/COMBO_A3_G13_DEMO.mp4 absent; no placeholder video supplied.
- Phone-to-API failure unresolved; private preview address 172.30.114.74:8000 needs LAN/VPN routing. Preview cleartext exception is app-wide; production requires HTTPS. Installed APK policy and original cancellation cause unverified.
- Sparse roster evaluation covers easy identities only; skill/feature tests use synthetic fixtures. Scores are not probabilities; offline search is exact matching, not TF-IDF. Pending technical claims are excluded.
- Historical npm audit records 15 high affected dependency nodes from two advisories; no fresh audit or remediation is claimed. Existing upstream Starlette/httpx test warning remains.
- Published APK/source correspondence, signing/build provenance and physical-device retest of latest UI/network changes unverified.

Submission remains incomplete until genuine missing evidence is supplied. Publication and readable PDFs do not establish assignment completion.
