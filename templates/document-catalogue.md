# Document catalogue

Every legal document a software product may need: websites, web apps, mobile apps, SaaS, marketplaces
and online stores. **Pick only what the product needs**, with `checklists/document-scoping.md`. Drafters
use the entry for each of their documents together with `templates/document-format.md`.

How to read an entry. The heading gives the title, the standard file name and the audience (public:
published to users or customers; internal: for the operator, the lawyer and engineering). The build
script uses the file name to title, order and group each document. **Needed when** says what triggers
it. **Must cover** lists the contents. **Watch** names rules that often apply.

The laws under **Watch** are common examples from the EU, the UK and the US, current to late 2026. They
are not complete, and they may not apply where the product operates. The researchers confirm what
applies, with sources.

## 1. Core

### Terms of Service · `terms-of-service.md` · public
**Needed when:** always. Also called Terms of Use or Terms and Conditions.
**Must cover:** who the operator is (legal name, registration number, address, email, phone); how people
accept, and how changes and versions work; what the product is and is not (not the seller, employer,
bank or insurer, where true); defined terms; eligibility and minimum age; accounts; the rules for each
feature (buying, booking, posting, messaging, AI), with category sections where risks differ; payments in
short; user content and the licence granted; acceptable use; reporting and the take-down contact;
suspension and closure (truthful); the operator's role and a reasonable liability cap with lawful
carve-outs; rights the law does not let you remove; governing law, complaints and disputes (no forced
arbitration where consumer law forbids it); general clauses; contact.
**Watch:** consumer rules on unfair terms (for example EU Directive 93/13/EEC); supplier-information duties
in e-commerce laws; EU Digital Services Act (DSA) Art. 14 on clear terms and content restrictions; UK
Online Safety Act 2023 for services where users share content.

### Privacy Policy · `privacy-policy.md` · public
**Needed when:** the product handles any personal data, which is almost always. Both app stores require
one.
**Must cover:** the mandatory notice items of each jurisdiction; the controller (and its registration
number where the regulator requires one); each category of data, its source, purpose and legal basis;
sensitive data, or that none is collected; who sees what (other users, sellers, staff); every outside
service by name or type, what it receives and where it is; transfers abroad and their safeguards;
retention per record type, and backups; rights, how to use them and the deadlines; marketing consent and
opt-out; minimum age; AI in short; location, push and email; cookies in short; security without
overclaiming; breach notification; changes and versions; contact, the data protection officer or local
representative where required, and how to complain to the regulator.
**Watch:** GDPR and UK GDPR Arts 13, 14 and 27; California's CCPA/CPRA (notice at collection, and a "Do Not
Sell or Share" link where it applies) and CalOPPA; other US state privacy laws; national data protection
acts, many of which require registration with the regulator.

### Cookie Policy · `cookie-policy.md` · public
**Needed when:** a website or web app uses cookies or similar technology (local storage, pixels, SDKs,
embedded content) beyond what is strictly necessary.
**Must cover:** each cookie or tracker, who sets it, why, how long it lasts and whether it is essential;
how to accept, refuse and change choices; links to the third parties' policies.
**Watch:** EU ePrivacy Directive Art. 5(3) and UK PECR reg. 6 (consent before non-essential cookies);
regulators expect refusing to be as easy as accepting. The banner text belongs in In-product Legal Texts.

### Acceptable Use Policy · `acceptable-use-policy.md` · public
**Needed when:** people can upload, post, send, host, run code or use an API. Simple products can fold it
into the Terms.
**Must cover:** forbidden content and conduct; security abuse (scraping, probing, spam, evading limits);
fair-use limits; reporting; enforcement steps.

### In-product Legal Texts · `in-product-texts.md` · public
**Needed when:** always. These short texts carry most of the legal weight, because people read them at the
moment they act.
**Must cover, as the product needs:** the sign-up acceptance line for every sign-in method; age
confirmation; cookie banner and preferences; marketing opt-in (unticked); permission prompts (location,
camera, contacts, notifications) with their purpose strings; the AI disclosure at the point of use;
checkout and booking disclosures (seller identity, total price with fees and taxes, cancellation and
withdrawal rights); order-button wording; receipts and confirmation emails; account deletion
confirmation; consent ticks for regulated services; footer links.
**Watch:** EU Consumer Rights Directive Art. 8(2) (the order button must say "order with obligation to pay"
or something equally clear); app-store rules on purpose strings and prominent disclosure.

## 2. Accounts, age and safety

### Account Deletion and Data Requests · `account-deletion.md` · public
**Needed when:** people can create accounts.
**Must cover:** how to delete an account in the product and from the web; what is deleted, what is kept,
for how long and why; how to download data or make other requests; response times.
**Watch:** Apple App Store guideline 5.1.1(v) (in-app deletion when the app lets people create accounts);
Google Play's account deletion policy (in the app and through a web link); privacy-law deadlines.

### Children's Privacy Notice · `childrens-privacy.md` · public
**Needed when:** the product is aimed at children, or is likely to attract them.
**Must cover:** what is collected from children; parental consent and controls; no behavioural
advertising; how parents can review and delete data.
**Watch:** US COPPA (under 13); GDPR Art. 8 (digital consent age between 13 and 16 by country); the UK Age
Appropriate Design Code; app-store rules for apps in kids categories.

### Safety Guidelines · `safety-guidelines.md` · public
**Needed when:** people meet in person, enter homes, travel together or trade valuable items.
**Must cover:** practical safety advice; what the operator checks and does not check (truthfully);
emergency contacts; how to report.

## 3. Money

### Payments and Refunds Policy · `payments-and-refunds.md` · public
**Needed when:** money moves through the product.
**Must cover:** how paying works under the real payment model; the payment methods that really exist;
every fee and who pays it; when money is taken and released; cancellations and statutory withdrawal
rights; refunds, where they go and how long they take; tips; declined or expired requests; no-shows
(without the platform deciding who is right, unless it really does); chargebacks; currency and taxes.
**Watch:** withdrawal rights for distance contracts (for example 14 days in the EU and the UK, with
exceptions); card-scheme rules on showing the refund policy at checkout; payment-services licensing if
the operator holds or moves other people's money.

### Subscription Terms · `subscription-terms.md` · public
**Needed when:** anything renews automatically: plans, memberships, trials that turn into paid plans.
**Must cover:** price, billing period and renewal; trial conversion and reminders; how to cancel (as easy
as signing up); price changes with notice; refunds on cancelling; what happens to data afterwards.
**Watch:** US state automatic-renewal laws (for example California Business and Professions Code § 17600
and following); EU and UK consumer rules; Apple and Google subscription rules when they bill.

### Fee Schedule · `fee-schedule.md` · public
**Needed when:** sellers, hosts or business users pay fees, or buyers pay service fees.
**Must cover:** every fee, when it applies, how it is worked out, taxes on fees, worked examples.

## 4. Selling goods and services

### Shipping and Delivery Policy · `shipping-policy.md` · public
**Needed when:** physical goods are delivered.
**Must cover:** where you deliver; costs and times; when risk and ownership pass; failed deliveries;
customs duties; damaged or lost parcels.

### Returns and Warranty Policy · `returns-and-warranty.md` · public
**Needed when:** goods or digital content are sold. Small stores can fold it into Payments and Refunds.
**Must cover:** the legal guarantee first, then any extra guarantee; how to return; who pays for return
delivery; exceptions (made to order, perishable, sealed hygiene goods, digital content once supplied with
consent); refund timing.
**Watch:** EU Sale of Goods Directive 2019/771 (at least two years' legal guarantee); EU Digital Content
Directive 2019/770; UK Consumer Rights Act 2015.

### Product Safety and Seller Information · `product-safety.md` · public
**Needed when:** physical consumer products are sold, especially into the EU.
**Must cover:** what each listing must show (manufacturer or responsible person, product identifiers,
warnings and safety information); recalls; how to report an unsafe product.
**Watch:** EU General Product Safety Regulation 2023/988 (online sellers and marketplaces, from 13 December
2024).

### Booking and Cancellation Terms · `booking-terms.md` · public
**Needed when:** people book times, places or services: appointments, stays, rentals, classes, events.
**Must cover:** how a booking is confirmed; deposits; cancellation windows for each side; lateness and
no-shows; changes; what the provider must supply; damage and security deposits for rentals.

### Reviews Policy · `reviews-policy.md` · public
**Needed when:** the product shows ratings or reviews.
**Must cover:** who can review (verified buyers or anyone); how reviews are checked; what is removed;
incentives and paid reviews (banned, or clearly labelled); how sellers can reply.
**Watch:** EU Omnibus Directive 2019/2161 (say whether and how reviews are verified); UK DMCC Act 2024
(fake reviews banned); US FTC rule on consumer reviews and testimonials (16 CFR Part 465).

## 5. Marketplaces and platforms

### Business (Seller) Terms · `business-terms.md` · public
**Needed when:** third parties sell, list, host or provide services through the product.
**Must cover:** who can sell; accepting the terms; the seller is the seller; accurate listings, licences
and permits (self-declared is never shown as verified); the prohibited-listings policy; prices, fees and
payouts under the real payment model; refunds and chargebacks; taxes; rules for buyer data; reviews;
self-dealing; suspension, reasons and appeals; ending the agreement; liability and indemnity
(reasonable); disputes; category schedules.
**Watch:** EU Platform-to-Business Regulation 2019/1150; DSA Arts 30 and 31 (trader traceability,
compliance by design); seller-income reporting by platforms (for example the EU's DAC7).

### Prohibited and Restricted Listings · `prohibited-listings.md` · public
**Needed when:** users can list goods or services.
**Must cover:** banned and restricted goods and services, each with its basis; the conditions for
restricted ones (licences, age checks); how listings are checked (truthfully); the catch-all "other"
category; what happens on a breach.

### Buyer Protection Policy · `buyer-protection.md` · public
**Needed when:** the operator promises anything when a purchase goes wrong: holding funds, refunds,
deciding disputes.
**Must cover:** what is covered and what is not; how and by when to claim; evidence; who decides; costs.
Promise only what the operations and the payment model can deliver.

### Ranking and Recommendations Notice · `ranking-transparency.md` · public
**Needed when:** the product ranks, recommends or sponsors listings or content.
**Must cover:** the main factors behind ranking; paid placement and its label; personalisation, and how to
turn it off where required.
**Watch:** EU Platform-to-Business Regulation Art. 5; EU consumer rules on ranking (Omnibus); DSA Art. 27
(recommender systems) and Art. 38 (a non-profiling option on very large platforms).

### Content Moderation and Appeals · `moderation-and-appeals.md` · public
**Needed when:** the operator removes content, restricts accounts or demotes listings.
**Must cover:** how reports are handled; the actions the operator takes; the reasons it gives; how to
appeal and how fast; outside dispute bodies where they exist.
**Watch:** DSA Arts 16, 17, 20 and 21; UK Online Safety Act complaints duties.

## 6. User content and community

### Community Guidelines · `community-guidelines.md` · public
**Needed when:** people post, review, message, stream or comment.
**Must cover:** what may and may not be posted; reviews; messages; live content; how to report, what
happens next, who reviews and how fast (truthfully); enforcement; content about children and vulnerable
people.

### Copyright and Take-down Policy · `copyright-policy.md` · public
**Needed when:** users can upload or post content.
**Must cover:** how to send a notice and what it must contain; counter-notices; repeat infringers; the
designated contact.
**Watch:** US DMCA § 512 (register a designated agent with the US Copyright Office); DSA Art. 16; national
safe-harbour rules for hosts.

### Trademark Policy · `trademark-policy.md` · public
**Needed when:** brands are listed, or user names and pages could impersonate others.
**Must cover:** how to report misuse, the evidence needed, what the operator does.

## 7. Marketing, promotions and partners

### Marketing Communications Notice · `marketing-consent.md` · public
**Needed when:** the operator markets by email, text, push or phone.
**Must cover:** what is sent and how often; the consent asked for (separate from the Terms); how to opt
out.
**Watch:** EU and UK ePrivacy rules (UK PECR reg. 22); US CAN-SPAM Act (email) and TCPA (texts and calls).

### Advertising and Disclosure Policy · `advertising-policy.md` · public
**Needed when:** the product shows ads, sponsored listings, affiliate links or influencer content.
**Must cover:** how ads and paid placements are labelled; affiliate disclosures; rules for advertisers.
**Watch:** US FTC Endorsement Guides (16 CFR Part 255); UK CAP Code; DSA Art. 26 (ads on platforms).

### Referral and Rewards Terms · `referral-terms.md` · public
**Needed when:** people earn credit, points, cash or perks for referrals, activity or loyalty.
**Must cover:** how rewards are earned; their value and expiry; abuse rules; changing or ending the
programme; tax.

### Gift Card and Voucher Terms · `gift-card-terms.md` · public
**Needed when:** the product sells or issues gift cards, vouchers or stored credit.
**Must cover:** value, expiry, fees, where it can be used, refunds, loss and theft.
**Watch:** limits on expiry and fees (for example the US Credit CARD Act of 2009 and state laws);
electronic-money rules if the card can be used outside the product.

### Contest and Giveaway Rules · `contest-rules.md` · public
**Needed when:** the operator runs sweepstakes, contests or giveaways.
**Must cover:** who can enter, how, dates, prizes and odds, how winners are chosen and told, publicity.
**Watch:** "no purchase necessary" rules and state registration for large prizes in the US; lottery and
gaming laws elsewhere; social networks' promotion rules.

### Affiliate or Partner Agreement · `affiliate-agreement.md` · public
**Needed when:** partners earn commission for promoting the product.
**Must cover:** commission, tracking, payment, brand use, disclosure duties, termination.

## 8. AI features

### AI Features Notice · `ai-features-notice.md` · public
**Needed when:** the product offers AI features: chat, generation, recommendations, scoring, automated
decisions.
**Must cover:** each feature; what it can see; what goes to which provider, and whether it is stored or
used for training; limits (it can be wrong, gives no professional advice, cannot decide or pay unless it
really does); what not to share; human review; how to stop using it; labels on AI-generated content.
**Watch:** EU AI Act (Regulation 2024/1689) Art. 50 transparency duties (from 2 August 2026); GDPR Art. 22
on decisions made solely by automated means; consumer-protection rules on AI claims.

### AI Acceptable Use Policy · `ai-acceptable-use.md` · public
**Needed when:** users can prompt generative AI.
**Must cover:** forbidden uses; the providers' own usage rules passed on to users; consequences.

## 9. Mobile apps and app stores

### App Store Privacy Disclosures · `store-privacy-disclosures.md` · internal
**Needed when:** the product ships on the Apple App Store or Google Play.
**Must cover:** answers for Apple's App Privacy questions and Google Play's Data safety form, taken from
the data map: data types, purposes, linked to the person or not, tracking, sharing, encryption in
transit, deletion.
**Watch:** each store's current questions. The answers must match the Privacy Policy and the code.

### End-User Licence Agreement · `eula.md` · public
**Needed when:** the app needs licence terms that the Terms of Service and the store's standard licence do
not cover.
**Watch:** Apple's standard licence applies unless the app supplies its own.

## 10. Business customers, APIs and developers

### Business Customer Agreement · `customer-agreement.md` · public
**Needed when:** businesses buy the product (SaaS plans, enterprise deals).
**Must cover:** the service and orders; fees and invoices; term and renewal; who owns customer data;
confidentiality; intellectual property; warranties; liability cap; indemnities; suspension; ending the
agreement and exporting data; governing law.

### Data Processing Agreement · `data-processing-agreement.md` · public
**Needed when:** the operator processes personal data on behalf of business customers.
**Must cover:** the processor terms the law requires (instructions, confidentiality, security,
sub-processors, help with requests, deletion or return, audits); transfer clauses; a link to the
sub-processor list.
**Watch:** GDPR Art. 28; EU Standard Contractual Clauses (Decision 2021/914) and the UK addendum; CCPA
service-provider terms.

### Sub-processor List · `subprocessors.md` · public
**Needed when:** there is a data processing agreement, or the Privacy Policy points to a list of
providers.
**Must cover:** each provider, what it does, what data it handles, and where.

### Service Level Agreement · `sla.md` · public
**Needed when:** uptime or support response times are promised.
**Must cover:** what is measured, the targets, exclusions, how to claim credits, credits as the remedy.

### API and Developer Terms · `api-terms.md` · public
**Needed when:** others use an API, SDK or integration.
**Must cover:** keys and security; rate limits; allowed uses; limits on using and storing data;
attribution; changes and deprecation; suspension.

### Security Overview · `security-overview.md` · public
**Needed when:** business customers ask how their data is protected.
**Must cover:** the controls actually in place (never overclaim); certifications actually held; incident
notification.

### Vulnerability Disclosure Policy · `vulnerability-disclosure.md` · public
**Needed when:** the product is online and holds personal or financial data.
**Must cover:** how to report; scope; safe harbour for good-faith research; response times. Publish a
`/.well-known/security.txt` file (RFC 9116).
**Watch:** the EU Cyber Resilience Act (Regulation 2024/2847) for software and connected products sold in
the EU (vulnerability reporting duties from 11 September 2026).

## 11. Regulated categories

Most category rules belong inside the Terms of Service and the Business Terms, as schedules (for example
"Schedule A: Appointments"). Add a standalone document only where the law requires one, or where the
readers differ.

### Consent Forms · `consent-forms.md` · public
**Needed when:** a service needs specific informed consent: treatments, health services, recordings,
minors' activities, background checks.
**Must cover:** short, versioned texts; one tick per thing agreed; no more data than needed; who keeps the
record and for how long.

### Consumer Health Data Policy · `consumer-health-data-policy.md` · public
**Needed when:** the product handles consumer health data of people in places that require a separate
policy (for example Washington's My Health My Data Act). First ask whether the product needs health
data at all.

### Candidate Privacy Notice · `candidate-privacy.md` · public
**Needed when:** the product runs job adverts or recruitment, or the operator hires through it.
**Must cover:** what candidates' data is used for, who sees it, how long it is kept.
**Watch:** employment-agency licensing; non-discrimination rules for adverts.

Typical category issues to check: health and wellness (practitioner licensing, health data); money and
crypto (licences, risk warnings, anti-money-laundering checks); accommodation (host registration, rent
and deposit rules); food (permits, allergen information, for example EU Regulation 1169/2011);
transport and vehicles (driver and vehicle licensing, insurance); alcohol, tobacco and other
age-restricted goods (age checks at sale and delivery, online-sale bans); education and children's
services (safeguarding, background checks); events (refunds for cancelled events, ticket resale);
gambling (a licence, or a ban).

## 12. Company and public notices

### Legal Notice (Imprint) · `imprint.md` · public
**Needed when:** the law requires company details on the website, as in Germany and Austria; good
practice everywhere.
**Must cover:** name, legal form, address, representatives, register and number, VAT number, contact, and
the supervising authority if the activity is regulated.
**Watch:** Germany's Digitale-Dienste-Gesetz (DDG) § 5; EU e-Commerce Directive 2000/31/EC Art. 5; in the
UK, the Company, Limited Liability Partnership and Business (Names and Trading Disclosures) Regulations
2015.

### Accessibility Statement · `accessibility-statement.md` · public
**Needed when:** the product serves the public sector, falls under the European Accessibility Act (many
consumer e-commerce and banking services in the EU since 28 June 2025; micro-enterprises are exempt for
services), or the operator wants to show its commitment.
**Must cover:** the standard targeted (for example WCAG 2.2 level AA); known gaps; how to get help or an
alternative; how to complain.

### Law Enforcement Request Guidelines · `law-enforcement-guidelines.md` · public
**Needed when:** the product holds data that authorities may request; expected of larger platforms.
**Must cover:** what a valid request needs; emergencies; whether users are told; what data exists.

### Transparency Report · `transparency-report.md` · public
**Needed when:** the law requires regular reports on moderation (for example DSA Arts 15 and 24; small and
micro enterprises are exempt from some of these duties), or the operator chooses to publish one.
**Must cover:** notices received, actions taken, response times, appeals and their outcomes.

## 13. Internal compliance records

### Data Map and Retention Schedule · `data-map-and-retention.md` · internal
**Needed when:** always.
**Must cover:** a record of processing (data, where it is stored, purpose, legal basis, who can access it,
outside services, retention, what deletion does); a register of processors; a retention schedule with
its legal bases; the regulator registration checklist; product changes needed.
**Watch:** GDPR Art. 30.

### Data Protection Impact Assessment · `dpia.md` · internal
**Needed when:** processing is likely to be high-risk: sensitive data, children, large-scale tracking,
precise location, profiling, AI, systematic monitoring.
**Must cover:** what happens and why; necessity and proportionality; risks to people; measures; the risk
left; sign-off.
**Watch:** GDPR Art. 35, and the regulator's list of processing that always needs one.

### Legitimate Interests Assessment · `legitimate-interests.md` · internal
**Needed when:** the Privacy Policy relies on legitimate interests for any purpose.
**Must cover:** the interest; why the processing is necessary; the balance against people's rights;
safeguards.

### International Transfer Assessment · `transfer-assessment.md` · internal
**Needed when:** personal data goes to countries the law does not treat as adequate, under safeguards such
as standard contractual clauses.
**Must cover:** what goes where; the safeguard used; the risks in the destination country; extra
measures.

### Data Request Procedure · `data-request-procedure.md` · internal
**Needed when:** always.
**Must cover:** how requests arrive; identity checks; who handles them; deadlines; reply templates; the
log.

### Breach Response Plan · `breach-response-plan.md` · internal
**Needed when:** always.
**Must cover:** spotting, assessing and containing a breach; who decides; when to tell the regulator and
the people affected (for example within 72 hours to the authority under GDPR Art. 33); the breach log.

### AI Register and Risk Assessment · `ai-risk-assessment.md` · internal
**Needed when:** the product uses AI.
**Must cover:** every AI system and provider; the data used; purpose; risk level under the rules that
apply (for example the EU AI Act); human oversight; testing; incidents.

### Online Safety Risk Assessment · `online-safety-risk-assessment.md` · internal
**Needed when:** users can share content with each other and the UK Online Safety Act, or a similar law,
applies.
**Must cover:** the illegal-content risk assessment and, where children can use the service, the
children's risk assessment; measures; review dates.
