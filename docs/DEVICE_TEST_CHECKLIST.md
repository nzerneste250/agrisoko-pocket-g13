# Android manual test checklist — NOT EXECUTED

Record tester, date, device, Android version, APK SHA-256 and actual result per row. No device has passed yet.

1. Install build/AgriSokoPocket_G13.apk without Expo Go; cold launch.
2. Check all six screens, Android back navigation, rotation, large font and TalkBack labels.
3. Check connected directory and profile retrieval against a reachable HTTPS API.
4. Submit full names, real aliases, declared roles, skills/features, no-match and invalid/overlong input.
5. Observe loading; stop API and verify timeout/retry with useful local fallback.
6. Start in airplane mode: bundled roster must remain usable before any network use.
7. Run live search, close/reopen app offline: cached directory/profile/last useful result must persist.
8. Submit a no-match and confirm the last useful successful result remains accessible from Home.
9. Restore connectivity and verify directory refresh/source labels. A connected network with unreachable API must still degrade safely.
10. Test approved HTTPS evidence links and rejected unsafe URLs.
11. Record real screenshots, failures and fixes. Collect genuine feedback with consent; never fabricate signatures.
12. Record the real demo covering installation, online/offline lookup, failure handling, approach and actual individual contributions.
