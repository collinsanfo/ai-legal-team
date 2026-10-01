# Putting the documents into the product

The documents protect the operator only if the product shows them at the right moments and keeps the
records. The team lists what is missing as product changes; engineering ships them before go-live.

## Where each document must be reachable
| Place | What to link or show |
|---|---|
| Website footer, app settings, app-store listing | Terms, Privacy Policy, Cookie Policy (web), Community Guidelines, Legal Notice where required, contact |
| Sign-up, for every method (email, phone, Google, Apple) | The acceptance line with links before the account exists; age confirmation; a separate, unticked marketing opt-in |
| Checkout and booking | Seller identity and contact; total price with fees and taxes; cancellation, refund and withdrawal terms; order-button wording where required; link to Payments and Refunds |
| Seller onboarding and listing | Business Terms acceptance; prohibited-listings rules; licence declarations |
| Posting, messaging, live content | Community Guidelines link; a report button |
| AI features | A point-of-use notice naming the provider and the limits |
| Permission prompts | Purpose strings that match the Privacy Policy |
| Account settings | Account deletion; data download; cookie and consent choices; marketing opt-out |
| Receipts and confirmation emails | Seller details; price breakdown; cancellation terms; links to the documents |
| App-store listings | Privacy Policy URL; App Privacy and Data safety answers; support URL; account-deletion URL (Google Play) |

## Records to keep
- **Acceptance log:** user, document, version, time, method (tick, button or sign-in line), app version or
  page.
- **Consent log:** cookies (choice, time, banner version); marketing (channel, time, source); consents for
  regulated services.
- **Data requests and breaches:** a log of each, with deadlines.
- **Moderation:** decisions, the reasons given, appeals and outcomes.
- **Sellers:** verification records where the law requires them.

## Versions and changes
- Each document has a version number, an effective date and an archive of earlier versions.
- A change triggers notice to users and, where the owner decided so, acceptance before carrying on.
- People who have not accepted keep their existing bookings, refunds and data rights.

## Hand-off to engineering
- Put the approved documents, the product changes list and this checklist in the product repository
  (for example `docs/legal/`), and point to them from `AGENTS.md`, `CLAUDE.md` or the README. Developers,
  coding agents and automated code reviewers can only work from what is in the repository; they cannot
  open private review pages or documents.
- Say which text is the source of truth (the approved Markdown), where the product shows it, and that
  the product must not publish a document until the changes it depends on are live.
- Keep internal lawyer material (questions for counsel, red-team findings, research) out of any public
  repository.

## Before go-live
- `python scripts/build_pack.py PACK --check-publish` passes.
- Every link works on the web, iOS and Android, signed in and signed out.
- The app-store answers match the Privacy Policy and the code.
