# Physical-device follow-up — 2026-10-23

All implementation changes were made in **F:\COMBO_A3_G13**. F:\G13_EAS_CLEAN was inspected read-only. No APK build, upload, publication or installation was performed. The owner reports that the previous APK installed and launched; this is user-reported evidence, not an agent-performed test.

## Confirmed findings and unresolved device cause

- The original UI derived “Connected” from NetInfo and set API availability after arbitrary requests. It did not require a valid API health response. Device/internet availability and backend health were conflated.
- The original requests used a ten-second AbortController timer, but recognized timeout only when the error name was AbortError. Native fetch can instead reject with generic cancellation wording. Executed regression tests reproduce that case. The exact cause of the phone's cancellation cannot be established from that message alone; no device timing trace, logcat or installed-APK manifest was obtained.
- Literal mojibake was present in App.tsx, including corrupted separators and ellipses. The UI now uses plain separators. Strict UTF-8/source-pattern checks pass, and valid accented names remain supported.
- The workstation's Wi-Fi address is currently 172.30.114.74. An actual workstation request to http://172.30.114.74:8000/health returned **200** with `{"status":"ok","version":"1.0.0","groupCode":"G13"}`. This proves workstation reachability only. Mobile internet alone does not normally route to this private address.
- Existing Expo/EAS security configuration is retained. Generated-manifest tests show cleartext enabled only for preview with the supplied exact URL. Production, an unset profile and a different preview URL disable it. No generated networkSecurityConfig overrides the flag. This does not establish the policy in the already-installed APK.

## Files changed

- `mobile/App.tsx`: all six screens retain navigation/back handling, four-member directory, offline lookup, caches, last useful result, evidence links and model information. Added explicit search cancellation, classified errors/fallback messages and stale-response guards. Green/cream cards, readable sections, compact wrapping buttons with 48dp minimum touch targets, labelled fields, safe areas and scalable text improve hierarchy without removing features. About has Project, Group members, AI approach, Offline support, API status, GitHub evidence and Limitations sections. Unknown facts remain pending verification.
- `mobile/src/api.ts`: transport delegates to the new tested module. Existing API payloads, AsyncStorage keys and directory/profile/result caches remain intact.
- `mobile/src/network.ts` (new): distinct configuration, offline, timeout, explicit user cancellation, HTTP, reported Android cleartext denial, network and response failures. Tracks our abort cause rather than relying on native error names. Timeout covers body decoding; listeners/timers are cleaned up. Generic cancellation wording alone is classified as an interrupted network request, not invented user cancellation. Includes LAN guidance, validated G13 health checks, separate device/backend labels and a connectivity reducer.
- `mobile/src/useConnectivity.ts` (new): NetInfo and API health are independent. Network changes trigger health checks and invalidate stale checks. Public internet detection is not required to try a local LAN API. Only a valid successful /health marks the backend reachable.
- `mobile/tests/network.test.ts`, `mobile/tests/encoding.test.ts` (new): timeout/cancellation, response-body timeout, HTTP/security/network distinctions, health validation, mobile-data independence, LAN-without-internet, retry/reset, UTF-8/mojibake and unchanged member facts.
- `scripts/sync_build_copy.py`, `scripts/tests/test_sync_build_copy.py` (new): reviewed one-way sync, plan-only default, path containment, hash preflight and recheck, newer-file protection, backups and verified copies. No deletion, mirroring or build operations.
- `docs/BUILD_SYNC_PLAN.json`: read-only comparison plan identifying six differing mobile files at preparation time. This report, README and CHANGELOG document the follow-up.

Backend source, matching engine, dataset, member records, dependency manifests/lockfile, Expo security plugin, EAS profiles, icons and existing tests were preserved. No facts, registrations, accounts, roles, skills, approvals, contributions or outcomes were invented.

## Actual validation

| Check | Result |
|---|---|
| TypeScript (`npm run typecheck`) | Passed, exit 0 |
| Mobile (`npm test`) | 25 passed, 0 failed |
| Included Android configuration checks | 4 generated-manifest scenarios passed |
| Included encoding/roster regressions | 2 passed |
| Included network/state regressions | 13 passed |
| Existing domain tests | 6 passed |
| Expo Doctor | 20/20 passed, exit 0 |
| Backend pytest safety check | 54 passed; one existing Starlette/httpx deprecation warning |
| Sync-tool unittest suite | 4 passed |
| Workstation HTTP /health | 200; expected G13 response |
| Local Android JavaScript export | Passed; 645 modules, 1.6 MB Hermes bundle |

Transport tests use controlled fetch fixtures. They do not claim phone-to-API connectivity. The local Android JavaScript export is a compilation check, not an APK build.

## Safe sync and rebuild — manual steps, not executed

1. Keep MAIN authoritative. Run the following to generate a plan only:

   ```powershell
   python F:\COMBO_A3_G13\scripts\sync_build_copy.py
   ```

   Review `docs/BUILD_SYNC_PLAN.json`: roots, paths, hashes and any REVIEW NEWER entries. Do not overwrite MAIN with older build-copy files.

2. After review, apply that plan:

   ```powershell
   python F:\COMBO_A3_G13\scripts\sync_build_copy.py --apply F:\COMBO_A3_G13\docs\BUILD_SYNC_PLAN.json
   ```

   Stale hashes and newer differing destination files cause refusal. Reconcile genuine build-copy work in MAIN, rerun checks, then regenerate/review the plan. Replaced files are backed up under `F:\G13_EAS_CLEAN\.g13-sync-backups`. The allowlist excludes Python environments, pytest/locked test folders, node_modules, native/generated outputs, .env secrets and backend folders. Destination-only files are never deleted.

3. In `F:\G13_EAS_CLEAN\mobile`, rerun TypeScript, mobile tests and Expo Doctor. Dependencies did not change; use npm ci only if installation is missing/incompatible. The inspected build copy has no native android/ tree, so EAS can generate it using the retained plugin.

4. On the phone, open `http://172.30.114.74:8000/health` using Wi-Fi or a VPN that can reach the computer. Expect G13 status ok. If unavailable, verify server binding (`--host 0.0.0.0`), computer address, port 8000, firewall, router/client isolation and routing. A workstation HTTP 200 is insufficient. If the IP changes, update the preview URL and exact-URL security gate in MAIN before syncing.

5. When the owner chooses to submit a build:

   ```powershell
   Set-Location F:\G13_EAS_CLEAN\mobile
   npx eas-cli@latest build --platform android --profile preview
   ```

   This is a remote build and may consume allowance/charges. It was not run. Keep production on HTTPS. Metro reload/OTA JavaScript cannot change an installed APK's bundled URL or native policy.

6. Download and reinstall the new preview APK. On the physical phone verify About's URL and API health; test search, timeout/cancel/retry/no-match, airplane-mode cold start, cache persistence and Wi-Fi recovery. Inspect all six screens, text, rotation, large fonts and TalkBack. Record actual device/build/results before claiming working API connectivity.

## Remaining limits

The original phone cancellation cause, phone network route and installed manifest remain unverified. The revised UI and connectivity behavior require physical-device acceptance testing. All member approvals, missing technical facts and genuine GitHub evidence remain pending. Earlier PDFs/ZIP remain historical draft snapshots; this scoped follow-up does not regenerate them.
