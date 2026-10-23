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

Android delivery
The app name is AgriSoko Pocket G13, Android package com.agrisoko.pocket.g13, version 1.0.0. EAS preview uses internal APK distribution without Expo Go. EAS account status was checked; the user explicitly chose local preparation only. No cloud build was submitted, no APK exists and no device installation was verified. Use the README instructions after owner authorization or local Android toolchain setup.

Collaboration and evidence gaps
Git has no commits/remotes; no repository/release URL or final commit exists. Proposed assignments are plans only. Every member must perform an assessed issue, substantial PR, meaningful peer review and contribution explanation. No signatures, tester feedback, screenshots, video or individual technical ownership were fabricated. Evidence PDFs are draft templates. Cline/Codex assistance is disclosed in evidence/AI_USE.md.

Before submission
Reconcile the official assignment, approve real profiles, resolve/review dependency findings, configure a real API, build/install/test the APK, collect genuine feedback/demo and collaboration evidence, then finalize PDFs and COMBO_A3_G13.zip. Required video evidence/COMBO_A3_G13_DEMO.mp4 remains absent.
