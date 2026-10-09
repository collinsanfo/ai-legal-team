# App and website release review

Read `roles/11-platform-privacy.md`. Scope each surface: web/PWA, Android, iOS, wrappers/native pilots,
hosted backend and store submission. Use `templates/platform-privacy-matrix.md`. Local source, tests,
native-device checks, hosted verification and actual store acceptance are separate evidence.

## Checks selected by actual behavior

- Derive personal data, permissions, SDK/API recipients, location precision, storage/cookies,
  telemetry, ads and external resource requests from source and configuration. Do not read secrets.
- Trace access control and community/tenant membership on the server. Determine who can see public
  posts, private messages, report evidence, media links and pickup details.
- Distinguish a deletion request from completed deletion. Map live records, media, caches, backups,
  retention, appeals/legal holds, and provider deletion. Check export coverage and identity verification.
- Trace sign-up acceptance, version history, marketing/analytics consent, revocation and logout.
  Never conflate consent to terms with a privacy legal basis or assume all storage needs consent.
- Map user-generated content to actual reporting, blocking, moderation, response procedures, appeals,
  copyright complaints and age/child-safety choices. A report form does not establish staffed operations.
- Reconcile each App Privacy/Data safety answer with actual SDK/client/server behavior and release
  configuration. Check permissions, account deletion, contact URLs and support workflow.
- Check accessibility statements against known gaps and the assessed surface. Automated audits do not
  certify full conformance. Verify the applicability of accessibility law before calling it mandatory.
- Review sustainability, charity/partnership, impact, encryption and security claims against evidence.
  Separate WebRTC transport encryption from stored-text E2EE; identify actual keys and trust limits.

## Source starting points

Open and record the current text, territory, effective date and exact relevant section during each
real review. A source link is discovery, not evidence it applies to the product.

| Source type | Official source | Trigger to investigate |
|---|---|---|
| Platform terms | [Apple App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/) | Apple distribution; UGC, privacy, accounts and permissions |
| Platform terms | [Google Play User Data](https://support.google.com/googleplay/android-developer/answer/10144311) | Android distribution; privacy and SDK/data declarations |
| Platform terms | [Google Play account deletion](https://support.google.com/googleplay/android-developer/answer/13327111) | Apps with account creation; in-app and external deletion paths |
| Statute | [GDPR official text](https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng) | Applicable territorial/data-processing scope; do not assume EU scope from hosting alone |
| Statute | [EU Digital Services Act](https://eur-lex.europa.eu/eli/reg/2022/2065/oj/eng) | Applicable intermediary/platform role and exemptions |
| National regulator / official text | [Ghana Data Protection Commission](https://dpc.gov.gh/) and [Act 843 hosted by the NCA](https://nca.org.gh/wp-content/uploads/2020/09/Data-Protection-Act-2012.pdf) | Ghana launch research; verify current law, territorial scope, controller facts and amendments before drawing conclusions |
| National regulator | The launch country's privacy, consumer, communications and sector regulators | Always research the actual market, including markets outside EU/UK/US |

This kit does not bundle current national-law conclusions. A Ghana-first, Indian, Brazilian or other
product needs its own official-source research; the catalogue's examples are not global coverage.
Unknown operator identity, target countries or age audience remain explicit owner questions.
