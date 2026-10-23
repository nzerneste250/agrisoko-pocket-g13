# Independent audit ? 2026-10-23

Official 10-page assignment PDF is absent. Requirements are provisional, based on the supplied master prompt. Initial inspection covered all source, tests, debug scripts, dataset, requirements and .gitignore. No README or mobile implementation existed. Git master has no commits or remotes. No source has been deleted.

| Area / requirement | Existing implementation | Evidence | Initial status | Required action | Priority |
|---|---|---|---|---|---|
| AI matching | TF-IDF/cosine exists; undefined NAME_ALIAS_BOOST crashes identifier searches | ai-api/matching.py | FAIL | Repair ranking and exact identifiers | P0 |
| AI validation / approval | Missing fields in fourth member; shallow validation; pending facts exposed | data/members.json, matching.py | FAIL | Validate types and restrict pending technical claims | P0 |
| FastAPI | Five routes exist; directory response drops approval fields; stale persisted index possible | ai-api/app.py | PARTIAL | Repair schema and index lifecycle | P0 |
| Mobile UI | Empty folder | mobile/ | FAIL | Implement six screens and API integration | P0 |
| Offline support | No implementation | mobile/ | FAIL | Bundle roster, persistent cache and local lookup | P0 |
| Testing | Existing tests contain invalid assertions and dangling code | ai-api/tests/ | FAIL | Correct contracts, execute and evaluate | P0 |
| APK release | No Expo/EAS config or APK | build/, mobile/ | FAIL | Configure, diagnose and attempt build | P1 |
| GitHub collaboration | No commits/remotes; no verified collaboration | git status/log/remote | BLOCKED | Prepare plan; members perform actual work | P1 |
| Documentation | No README/report | docs/ | FAIL | Write reproducible instructions and truthful drafts | P1 |
| Submission evidence | Empty evidence directory; no device/video/feedback evidence | evidence/ | BLOCKED | Prepare templates; collect real evidence | P1 |


## Post-repair verification

Statuses below supersede the initial snapshot. PASS means the specified automated or inspection scope passed; it never implies a device test or official-PDF check.

| Area / requirement | Final implementation and evidence | Status | Remaining action | Priority |
|---|---|---|---|---|
| AI: TF-IDF and cosine | matching.py; unigram/bigram TF-IDF, English stop words, profile/field cosine; synthetic role/skill/feature tests executed | PASS | Broaden real-data evaluation after approvals | P1 |
| AI: names/aliases/boundaries | Exact identifiers take precedence; word boundaries; synthetic alias and all roster name tests | PASS | Obtain actual aliases | P1 |
| AI: threshold/ties/determinism | Default 0.45, constructor/env/CLI configuration; deterministic dataset-order ties and repeatability tests | PASS | None within tested scope | P2 |
| AI: validation | Empty/malformed data, duplicate IDs, list types, metadata, HTTPS evidence and threshold tests | PASS | Members supply missing facts | P1 |
| AI: fingerprint/artifacts | SHA-256 canonical indexed dataset; custom-directory save/load and fingerprint mismatch tests | PASS | Restart after dataset changes | P2 |
| AI: grounding | Pending technical claims/evidence removed; introductions use roster facts and approved fields; regression tests | PASS | Four real approvals outstanding | P0 |
| AI: real evaluation | evaluate.py, AI_EVALUATION.json: 12/12 identity queries; 5/5 deliberate no-matches; zero observed errors | PARTIAL | Add real role/skill/feature/alias queries; current data too sparse | P0 |
| API: five routes | app.py; all endpoints tested through TestClient and actual uvicorn TCP HTTP | PASS | Reconcile exact schema against missing official PDF | P1 |
| API: request/errors | 200, 404, 422 and whitespace 400 tested; strict payload and forbidden extra fields | PASS | None within tested scope | P2 |
| API: directory approval | Response exposes aliases, skills and approvalStatus instead of silently dropping fields | PASS | None | P2 |
| API: metadata | Version, group, approach, limitations, threshold, fingerprint and truthful null build commit | PASS | Final commit unavailable | P1 |
| Mobile: six screens | App.tsx: Home, Ask, Result, Directory, Profile, About; TypeScript and Android bundling pass | PARTIAL | Device UI/navigation acceptance test | P0 |
| Mobile: request integration | src/api.ts sends POST /ask JSON matching tested backend contract; configured EXPO_PUBLIC_API_URL | PARTIAL | Live app-to-API device test | P0 |
| Mobile: input/loading/no-match | 1?500 bounds, spinner, retry, no-match view and API error fallback inspected; domain tests execute | PARTIAL | Device interaction test | P1 |
| Mobile: timeout/error recovery | AbortController 10-second timeout, errors shown, local fallback, last useful result retained | PARTIAL | Test stalled/unavailable server on Android | P0 |
| Mobile: evidence links | HTTPS/no-credentials allowlist, URL unit tests, rejected open handled | PARTIAL | Test actual approved evidence on device | P1 |
| Mobile: accessibility/responsive | Safe areas, scroll/max width, scalable text, labelled controls, button roles, live error region | PARTIAL | TalkBack/large font/rotation test | P1 |
| Offline: bundled directory | Four roster entries; full-name/role/identifier tests; synthetic accented alias/boundary tests | PASS | Actual device offline cold launch | P0 |
| Offline: cache persistence | AsyncStorage directory/profile/last useful result; corrupted-cache fallback; cached profile readback | PARTIAL | Kill/relaunch persistence test on device | P0 |
| Offline: data source labels | Live/cached/offline bundled/offline cached displayed; device does exact lookup only | PARTIAL | Connection transitions on device | P1 |
| Offline: recovery | NetInfo subscription triggers directory refresh on reconnection | PARTIAL | Device network switching | P0 |
| Tests: backend | 54 passed; one Starlette/httpx deprecation warning; pip check passed | PASS | Monitor upstream TestClient warning | P2 |
| Tests: mobile unit/TypeScript | Six focused domain tests passed; tsc --noEmit passed | PASS | Storage/UI/device integration still manual | P1 |
| Tests: Expo Doctor | 20/20 checks passed after SDK-required dependency alignment | PASS | Rerun after dependency changes | P2 |
| Tests: Android compilation | Metro Android production export succeeded; no native APK built | PASS | Native build/device test | P0 |
| Security: dependencies | npm audit reports 15 high dependency nodes from two advisories; latest registry packages still affected | BLOCKED | Await/review patched compatible dependencies; see SECURITY_FINDINGS.md | P0 |
| APK: release configuration | Name, icon, package, version and EAS internal APK profile inspected | PASS | Owner performs approved release build | P0 |
| APK: artifact and install | No APK; no Android SDK/adb available; EAS authenticated but user explicitly chose local preparation only | BLOCKED | User authorizes remote build later or supplies local Android toolchain | P0 |
| GitHub: history/remote | master has no commits/remotes; no push or history mutation | BLOCKED | Owner establishes remote and meaningful commits | P0 |
| GitHub: collaboration | Proposed assessed issues/PR/reviews in COLLABORATION_PLAN.md; no actual evidence asserted | PARTIAL | Each member performs required collaboration | P0 |
| GitHub: CI | checks.yml prepared for backend/mobile verification; not executed on GitHub | NOT TESTED | Run after authorized remote publication | P1 |
| Documentation | README, completion, change record, evaluation, security findings, report/evidence draft PDFs and checklists | PASS | Replace drafts with real evidence | P0 |
| Submission: official PDF | No official assignment PDF in original workspace | BLOCKED | Supply and reconcile all requirements | P0 |
| Submission: feedback/video | Templates only; zero feedback collected; no demo MP4 | BLOCKED | Collect genuine feedback and record demo | P0 |
| Submission: archive | COMBO_A3_G13.zip is explicitly incomplete; source/evidence draft only | PARTIAL | Add APK/video/final evidence and regenerate | P0 |
