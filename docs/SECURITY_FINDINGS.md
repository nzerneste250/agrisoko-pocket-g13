# Dependency security findings — 2026-10-23

`npm audit --json` completed after an initial DNS failure. Its raw output is docs/NPM_AUDIT.json. It reports 15 high-severity affected dependency nodes, zero critical, tracing to two underlying advisories:

- braces <=3.0.3: stack-exhaustion denial of service through deeply nested patterns. https://github.com/advisories/GHSA-vfj7-8cjw-p6xm
- node-forge <=1.4.0: RSA signature verification accepts nested DigestAlgorithm elements. https://github.com/advisories/GHSA-86w9-cpqp-85rv

Installed chains: Expo 58.0.17 -> Expo Metro -> metro-file-map -> micromatch -> braces 3.0.3; Expo CLI and code-signing-certificates -> node-forge 1.4.0. `npm view braces version` returned 3.0.3; `npm view node-forge version` returned 1.4.0. No patched stable package versions were offered by the registry during this check.

The audit proposes Expo 44.0.6 as a major-version replacement. That is a large downgrade incompatible with the prepared SDK 58 application. No forced downgrade, unsupported override or false claim of a clean audit was applied. These are unresolved build-tool dependency findings, and the scope of exposure must be reviewed before a final release. Avoid untrusted build inputs and follow upstream patches; re-run npm audit when patched packages become available. Expo Doctor passing is a compatibility result, not proof that dependencies have no vulnerabilities.
