# Software, IP and open-source review

Use for websites, apps, APIs, SaaS and software deliverables. This is an evidence workflow, not an
automatic license clearance tool. Read `roles/09-software-ip.md` and the relevant product materials.

## Inventory before interpretation

Record software version/commit and whether the worktree is dirty. For each material record:
ID, component or asset, exact version/hash, origin, copyright holder if known, actual license or
service terms and source, modifications, usage, distribution and evidence status. Include direct
and transitive packages, browser bundles, Capacitor/native plugins, vendored code, containers,
fonts/icons/media, datasets, models and generated code. Distinguish code from hosted service terms.
Track missing/ambiguous terms; absence of a license is not permission.

Review the shipped web assets and mobile binary as well as server code. Separate internal use,
SaaS/network access, redistributed SDK, customer-hosted deployment and mobile distribution.
Never say all copyleft licenses prohibit commercial use or all permissive licenses impose no duties.
For disputed compatibility, source offers or license exceptions, state facts and ask counsel.

## Development and ownership

Map first-party authorship to employment/contractor/contributor agreements actually supplied.
Check assignment scope, background IP, third-party exclusions, subcontractors, moral-rights treatment
where applicable, confidentiality and any authority to license or sublicense. Repository access or
payment does not establish ownership. Git authorship metadata alone is not a chain of title.

Keep brand/trademark permission separate from a software license. Record generated code/assets and
the relevant provider terms/date and input provenance; do not promise exclusivity or non-infringement.
Review scraping/data collection permissions, API/cloud terms, training/evaluation data and model
licenses when triggered. No unsupported assumption about an AI provider's training rights.

## Engineering hand-off

Give each gap an ID, affected artifact, verified evidence, proposed fix, owner/counsel decision,
distribution scope and acceptance criterion. Examples: retain a notice in web/mobile releases;
replace an asset whose provenance cannot be established; produce an SBOM from the release lockfile;
verify signed release artifacts include required notices. A scanner finding is a lead with coverage
limits, not a legal determination. Keep private contracts and security details outside public repos.

Useful official references (open current texts before applying them):

- [SPDX license expressions](https://spdx.dev/learn/handling-license-info/): represent licenses and
  exceptions; an identifier does not establish compatibility or obligations.
- [REUSE specification](https://reuse.software/spec-3.3/): file-level copyright/license metadata.
- [OpenChain ISO/IEC 5230](https://openchainproject.org/license-compliance): a process reference;
  do not claim certification without evidence.

These standards are not statutes. Check the actual upstream license texts and counsel's interpretation
for the applicable jurisdiction and delivery model.
