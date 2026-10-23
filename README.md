# AgriSoko Pocket G13

INES Ruhengeri Integrated Mobile and Artificial Intelligence, Group Assignment 3.
Leader: NZAYISENGA Erneste (25/27341; GitHub nzerneste250).
Members: INEZA Benitha, MANZI Cedrick, KIRENGA Alain Thierry.

A transparent team lookup application for classmates, assessors and group members. The agricultural target users, problem statement, individual implementation ownership and measured agricultural outcomes still need member-supplied facts. All four profile approvals are pending. The official 10-page assignment PDF was not present; compliance is provisional.

## Architecture

`mobile/`: Expo SDK 58, React Native, TypeScript, six screens with a small typed navigation stack and Android back handling. `ai-api/`: FastAPI and deterministic scikit-learn TF-IDF/cosine search. No generative model or paid AI service. Both use the supplied roster. A bundled safe directory and AsyncStorage directory/profile/last-useful-result caches support offline use. NetInfo triggers reconnection refresh. Offline search handles exact full names, supplied aliases, registration/GitHub identifiers and roles, not TF-IDF similarity.

Backend ranking takes the maximum cosine of a full profile and individual role/skills/feature/contribution fields, with English stop words removed. Whole-phrase exact identifiers score 1, threshold defaults to 0.45, ties follow dataset order. Scores are not calibrated probabilities. Configure the API threshold with CONFIDENCE_THRESHOLD or build artifacts with `python build_index.py --threshold 0.45`. Pending technical claims and evidence are excluded. Synthetic approved fixtures test skills/features without inventing real member contributions.

## Backend setup (PowerShell, repository root)

```powershell
python -m venv ai-api/.venv
ai-api/.venv/Scripts/python.exe -m pip install -r ai-api/requirements.txt
Set-Location ai-api
.venv/Scripts/python.exe build_index.py
.venv/Scripts/python.exe -m pytest -q --basetemp=.pytest-tmp-local
.venv/Scripts/python.exe evaluate.py
.venv/Scripts/python.exe -m uvicorn app:app --host 0.0.0.0 --port 8000
```

Validated in the existing Python 3.14 environment. Use a fresh temporary pytest directory if filesystem permissions prevent cleanup. Dependencies are pinned; the original verbose dependency list is retained in docs/ORIGINAL_REQUIREMENTS.txt. Rebuild the index after edits; API processes rebuild from source at startup. Only load locally generated joblib artifacts. Restart the API after dataset changes.

Routes: `GET /health`, `GET /members`, `GET /members/{id}`, `POST /ask` with `{"question":"Who is NZAYISENGA Erneste?"}`, `GET /model-info`. Missing/wrong-type/overlong payloads return 422; whitespace-only returns 400; unknown member returns 404. API documentation: http://127.0.0.1:8000/docs.

## Mobile setup

```powershell
Set-Location mobile
npm ci
# Set to an actual reachable API address. This is a placeholder, not a deployment:
$env:EXPO_PUBLIC_API_URL = 'https://YOUR-ACTUAL-API-HOST'
npm start
npm run typecheck
npm test
npx expo-doctor@latest
```

Omit the API variable for offline-only operation. Expo Go development may use `http://<computer-LAN-IP>:8000` on the same network, subject to the device's cleartext policy and Windows firewall. `127.0.0.1` on a phone refers to that phone. The EAS preview profile now sets `EXPO_PUBLIC_API_URL=http://172.30.114.74:8000`. A local Expo config plugin enables Android cleartext only when `EAS_BUILD_PROFILE=preview` and that exact API URL is configured. This preview exception is app-wide within that build; production and all other configuration combinations explicitly disable cleartext and require HTTPS. See docs/ANDROID_HTTP_PREVIEW.md. Native policy changes require rebuilding/reinstalling the APK; restarting Metro alone is insufficient. Never put credentials in EXPO_PUBLIC variables because they are bundled publicly. API configuration changes require a Metro restart/rebuild. The preview URL is a supplied local development address, not a deployed public API.

No lint tool was previously configured; TypeScript and focused unit tests are the automated mobile checks. Device rendering, accessibility behavior, AsyncStorage persistence and connectivity switching require the manual checklist in docs/DEVICE_TEST_CHECKLIST.md.

## Android APK

`mobile/eas.json` preview profile uses internal distribution and `android.buildType: apk`, producing a standalone release without Expo Go. Package: `com.agrisoko.pocket.g13`; app name: `AgriSoko Pocket G13`; version 1.0.0, Android versionCode 1.

```powershell
Set-Location mobile
npx eas-cli@latest login
npx eas-cli@latest whoami
# After the authorized owner configures the real API URL and reviews any build charges:
npx eas-cli@latest build --platform android --profile preview
# Download the actual successful artifact from the returned build page, then:
Copy-Item -LiteralPath 'PATH-TO-DOWNLOADED.apk' -Destination '../build/AgriSokoPocket_G13.apk'
Get-Item ../build/AgriSokoPocket_G13.apk | Select-Object Name,Length
adb install -r ../build/AgriSokoPocket_G13.apk
```

EAS project linking/signing belongs to the authenticated owner. No build may be represented as complete until its real artifact exists. No device has been tested in this session. Repository URL, release URL and final commit are unavailable: local master initially had no commits or remotes. No push, history rewrite or external publication was performed.

## Evidence and submission

Read docs/CODEX_AUDIT.md, docs/AI_EVALUATION.json, docs/HTTP_TEST_RESULTS.json and docs/COMPLETION.md for measured results. Reports and evidence PDFs are explicitly marked drafts/templates. docs/COLLABORATION_PLAN.md contains proposed assignments, not verified work. evidence/AI_USE.md discloses Cline and Codex assistance.

Required deliverables: build/AgriSokoPocket_G13.apk, docs/COMBO_A3_G13_REPORT.pdf, evidence/CONTRIBUTIONS.pdf, evidence/TEST_LOG.pdf, evidence/FEEDBACK.pdf, evidence/AI_USE.md and a real evidence/COMBO_A3_G13_DEMO.mp4. The video and device/feedback/collaboration evidence must be collected honestly. A draft ZIP may contain incomplete deliverables and must not be submitted as final.

Sources for release configuration: [Expo APK documentation](https://docs.expo.dev/build-reference/apk/) and [eas.json reference](https://docs.expo.dev/eas/json/). Dependency compatibility is checked against the installed SDK's bundledNativeModules.json and Expo diagnostics.

## Physical-device follow-up

The current UI separates device/internet status from validated G13 API health, classifies timeout/cancellation/HTTP/network failures and retains offline fallback. See [DEVICE_FIX_REPORT.md](docs/DEVICE_FIX_REPORT.md) for actual findings, test results and device-retest instructions. MAIN is authoritative. [sync_build_copy.py](scripts/sync_build_copy.py) defaults to a reviewed plan for the temporary build copy, excludes dependencies/caches/secrets and refuses stale plans or newer differing files. No automatic APK build or publication is performed.
