# Go-live gate

The documents go into the product only when every box is ticked. Publishing earlier makes the operator's
own statements untrue, and those cannot be disclaimed.

## Product
- [ ] Every `[APP CHANGE]` item marked "before the documents go live" is shipped and verified.
- [ ] The product records each acceptance: user, document, version, time and method.
- [ ] New versions trigger an accept screen; people who have not accepted keep their existing bookings,
      refunds and data rights.
- [ ] Sign-up shows the terms (or a "by continuing you agree" line with links) before any account exists,
      for every sign-in method.
- [ ] A legal screen lists every public document with its version, effective date and last-updated date.
- [ ] Copy elsewhere in the product (help pages, checkout, receipts, AI screens) matches the documents.
- [ ] Every item in `checklists/product-implementation.md` that applies is done.
- [ ] The approved documents and the product changes list are in the product repository (for example
      `docs/legal/`) and referenced from `AGENTS.md`, `CLAUDE.md` or the README.

## Operator and regulators
- [ ] The operator's legal name, registration number, address, phone and email are filled in.
- [ ] Registration with the data protection regulator is done (number filled in) where required.
- [ ] The payments position is confirmed in writing (lawyer, and the processor where relevant) before any
      live payment.
- [ ] Platform settings match the documents (fees, retention periods, backups).

## Lawyer
- [ ] A qualified lawyer has checked the high-penalty items the team listed (payments licensing, sensitive
      data, regulated services, company set-up, anything criminal).
- [ ] Their answers are recorded in the pack.

## Publishing
- [ ] `python scripts/build_pack.py PACK --check-publish` passes: no draft banner and no marker left in
      any public document.
- [ ] Published copies drop the notes sections and all markers; the annotated pack stays internal.
- [ ] The effective date is the day the documents are published in the product.
- [ ] Users are told about the change; earlier versions are archived.
