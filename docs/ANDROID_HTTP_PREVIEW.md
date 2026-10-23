# Controlled Android HTTP preview ? 2026-10-23

The existing managed Expo app had no cleartext exception. A standalone release build targeting modern Android normally rejects HTTP under the platform default. The client already permits HTTP URLs in JavaScript, but that does not override Android's native policy. No native android/ tree existed or was edited.

## Changes

- mobile/eas.json: preview.env.EXPO_PUBLIC_API_URL is now http://172.30.114.74:8000. Production profile is unchanged.
- mobile/app.config.js: preserves all app.json values and any existing plugins. Enables the local plugin's exception only for EAS_BUILD_PROFILE=preview AND the supplied exact API URL (ignoring trailing slashes).
- mobile/plugins/withPreviewCleartext.js: uses Expo's existing config-plugin support to set android:usesCleartextTraffic to true for that controlled preview configuration and explicitly false otherwise. No new dependency. The exception is app-wide within an eligible preview APK, not a per-host Android firewall rule. It does not affect HTTPS evidence-link validation.
- mobile/tests/android-config.test.ts: adds four integration checks against Expo's generated Android manifests, including production configured with the HTTP URL, unset profile and unrelated preview host. Checks preserve package identity and INTERNET permission and confirm no networkSecurityConfig overrides the flag.
- README.md: documents preview URL, scope, production HTTPS requirement and mandatory rebuild.

The pre-existing EAS project ID, app name/package/version/icon, navigation, caches, request timeout, offline behavior, API client and production build profile were preserved. No remote project/build operations occurred, no dependencies changed, and no APK was built or installed.

## Actual results

- npm run typecheck: exit 0, no TypeScript errors.
- npm test: 10 passed, 0 failed (six existing domain tests plus four generated-manifest checks).
- npx expo-doctor@latest: exit 0; 20/20 checks passed.

| Generated configuration | android:usesCleartextTraffic |
|---|---|
| preview + http://172.30.114.74:8000 | true |
| production + http://172.30.114.74:8000 | false |
| no profile + http://172.30.114.74:8000 | false |
| preview + http://example.com:8000 | false |

These are executed Expo manifest-introspection checks, not an inspection of a compiled APK or a real-device network test. The API host's reachability from a phone was not tested. A rebuilt eligible preview APK has a native policy permitting HTTP; actual connectivity still requires the phone to reach that address/port and the server to listen on a reachable interface with firewall access.

Rebuild/reinstall the preview APK to apply the native manifest change. Metro reload/OTA JavaScript alone cannot change Android security policy. For local Expo introspection/prebuild, explicitly set EAS_BUILD_PROFILE=preview and EXPO_PUBLIC_API_URL=http://172.30.114.74:8000; EAS supplies the preview profile's environment during its build. Configure an actual HTTPS endpoint for production.

Sources: Android network security defaults https://developer.android.com/privacy-and-security/security-config and application usesCleartextTraffic https://developer.android.com/guide/topics/manifest/application-element .
