# Codex change record ? 2026-10-23

- Preserved the existing backend, tests, Git repository and temporary diagnostic scripts; did not restart/reinitialize.
- Wrote the initial audit before changing implementation. No README, PDF assignment or mobile source existed initially.
- Filled missing null/list fields for KIRENGA Alain Thierry without adding unknown facts or approvals.
- Replaced crashing undefined identifier boost with explicit whole-phrase identifier precedence and deterministic ranking. Added field-level cosine to avoid biography dilution; English stop words prevent common-word false positives.
- Added strict record types, duplicate ID, approval metadata, threshold and HTTPS evidence validation. Suppressed pending technical claims/evidence while retaining labelled supplied roster facts.
- Fixed index directory handling and fingerprint verification; API rebuilds from source per process. Added API env/build CLI threshold configuration.
- Fixed directory response omissions, added model version/group metadata and strict question payloads; removed unreachable code and unused imports.
- Corrected broken original test assertions/dangling statements; made synthetic approved fixtures explicit. Added regression coverage and measured evaluation.
- Decoded the original UTF-16 requirements list and retained a readable copy in docs/ORIGINAL_REQUIREMENTS.txt. Pinned direct runtime/test dependencies to installed tested versions and verified pip consistency.
- Implemented six-screen Expo/TypeScript application with local navigation/back handling, safe-area/responsive layout, accessible controls, timeout/retry, safe evidence opening and explicit data sources.
- Added bundled roster, exact offline matching, AsyncStorage directory/profile/last-useful-result cache, cache read validation and NetInfo recovery. Pending profiles remain labelled.
- Aligned native/tooling dependencies to installed Expo SDK 58 requirements; added lockfile, icon, environment template and EAS internal APK profile.
- Added mobile domain tests and prepared GitHub CI; CI has not run remotely.
- Recorded unresolved transitive dependency advisories rather than forcing an incompatible Expo downgrade.
- Prepared README, collaboration plan, device checklist, real measured outputs, labelled draft PDFs and packaging scripts. No feedback, device tests, video, member authorship, signatures or remote PR evidence fabricated.
- EAS identity check succeeded. User chose to keep the build local; no remote project was linked/created and no cloud build was submitted. No APK exists.

## Controlled HTTP preview follow-up ? 2026-10-23

Added preview-only URL configuration and a dependency-free Expo manifest plugin. Production explicitly disables cleartext. Verified four actual generated-manifest combinations, TypeScript, 10 mobile tests and Expo Doctor 20/20. No APK built/installed or remote build submitted. Full scope/results: ANDROID_HTTP_PREVIEW.md. Existing submission archive/PDFs remain the prior draft snapshot.

## Physical-device follow-up - 2026-10-23

Fixed MAIN mobile error classification, device/backend health separation, source mojibake and six-screen layout. Added network/encoding/roster regressions and a plan-only, hash-checked source sync utility. Results: TypeScript passed; mobile 25/25 including four Android manifest checks; Expo Doctor 20/20; unchanged backend 54/54; sync safety 4/4; Android JS export passed. Workstation health returned HTTP 200, but phone-to-API connectivity is not claimed. No build-copy code was changed, and no APK was rebuilt or published. Full details: DEVICE_FIX_REPORT.md.
