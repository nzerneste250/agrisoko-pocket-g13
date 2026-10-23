# AgriSoko Pocket G13 ? REPORT DRAFT

INES Ruhengeri Integrated Mobile and Artificial Intelligence, Group Assignment 3.
Prepared 2026-10-23. This is not a signed final report or proof of complete submission.

Group G13: leader NZAYISENGA Erneste, registration 25/27341, GitHub nzerneste250. Members INEZA Benitha, MANZI Cedrick, KIRENGA Alain Thierry. Individual profile approval and technical ownership are pending.

Purpose and scope
The current application provides transparent team lookup for classmates, assessors and group members. Agricultural target users, problem, delivered features and outcome metrics must be supplied by members. The official 10-page assignment was absent and has not been verified.

Architecture and AI method
Expo SDK 58 / React Native / TypeScript provides six screens: Home, Ask the Team, AI Result, Member Directory, Member Profile, About and Evidence. FastAPI exposes health, member list/profile, ask and model-info routes. scikit-learn creates normalized unigram/bigram TF-IDF vectors with English stop words removed. Cosine ranking uses the maximum of full-profile and declared role/skill/feature/contribution field scores. Exact whole-phrase roster identifiers take precedence at score 1. Threshold starts at 0.45; dataset order breaks ties. Scores are not calibrated probabilities. No generative language model is used by the product.

Grounding and approval
Unknown facts stay null/empty. Pending technical claims, evidence and introduction drafts are excluded from indexed/output facts. Supplied roster identity/leader role remain visible with pending labels. SHA-256 fingerprints the canonical indexed records. APIs rebuild from source at process startup; saved artifacts include metadata.

Offline behavior and limitations
The app bundles all four roster entries and caches the directory, successful profile and last useful search. Offline matching supports exact names, supplied aliases, registration/GitHub identifiers and roles; no offline TF-IDF. NetInfo refreshes after reconnection. Requests time out at ten seconds and fall back safely. Storage persistence and recovery require actual Android acceptance testing.

Executed verification
54 backend tests passed, including validation, threshold, exact/alias/role/skill/feature lookup, no-match, determinism, grounding, fingerprint/save-load and API contracts. Eleven actual localhost HTTP checks passed across the five routes and expected 200/404/422/400 statuses. pip check passed. One upstream TestClient deprecation warning remains.
Six mobile domain tests passed. TypeScript noEmit passed. Expo Doctor passed all 20 checks. Local Android production JavaScript compilation succeeded; this is not native APK build/install evidence.
Real sparse-roster evaluation measured top-1 12/12 identity queries and no-match rejection 5/5. There were no observed errors. These are easy identity paraphrases, not broad AI accuracy; real aliases/skill/features are unavailable. Synthetic fixtures test those engine mechanisms without claiming real contributions.
Fingerprint: 2cdc122b5bdf7a696654fc10e492011aa7e492d4bce0ca87a1b50378bf467577.

Security/release risks
npm audit reports 15 high affected dependency nodes arising from braces and node-forge advisories. Registry latest versions remained affected; no forced incompatible Expo downgrade was applied. Review upstream fixes before final release. Only HTTPS evidence links without credentials are opened. No hardcoded credentials or invented deployed API URL were added.

Android delivery, publication and remaining evidence
See the current status below. Earlier automated results above are historical records; the later device follow-up recorded 25 passing mobile tests. They do not establish APK/source correspondence or successful phone-to-API integration.

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
