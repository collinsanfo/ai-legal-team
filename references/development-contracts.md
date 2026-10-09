# Software development and vendor contracts

Use for issue spotting and proposed wording in NDAs, development agreements, SOWs, SaaS/vendor
contracts, maintenance terms and contributor IP documents. The original document stays unchanged;
the team does not negotiate, sign or send proposals. Read `roles/10-development-contracts.md`.

## Intake and playbook

Record parties, client/vendor side, contract family, governing law, territory, document version,
annexes and precedence. Ask for missing schedules that change scope. Create an owner-approved
playbook with desired position, fallback, escalation and negotiable/non-negotiable status.
Without it, flag issues and choices rather than inventing a liability cap or business tolerance.
Use `templates/development-contract-review.md` for the review table.

## Check actual deliverables

| Area | Questions for the review |
|---|---|
| Scope and acceptance | Deliverables, measurable acceptance tests, dependencies, milestones, review/rejection/cure process, silence-as-acceptance, change requests and cost impact |
| IP and reuse | Assignment timing/scope, background IP license, contractor/subcontractor authority, OSS and assets, generated code, patent/trademark rights and retained portfolio rights |
| Security and data | Roles/purposes, access restrictions, approved subprocessors, actual hosting, breach handling, deletion/return, audit scope, secrets and test-data controls |
| Operations | Supported versions, hosting/maintenance ownership, support and service levels, patching, third-party service outages, documentation and reproducible builds |
| Control and exit | Source/repository/domain/store/cloud-account ownership, credentials delivered securely, export format, transition help, continuity, termination and source escrow when needed |
| Commercial risk | Fees/taxes/payment triggers, warranties, infringement remedies, indemnities, liability carve-outs, insurance, disputes and survival |

Tie performance/security promises to implementation evidence. Owner approval cannot turn a future
feature into a present fact. Monetary/commercial terms in a development contract do not authorize
adding payments to the user's product.

For each proposed clause record its goal, source clause, trade-off and approval still required.
Use a separate Markdown redline or unified diff. Real Word tracked changes require a document tool
that preserves original content, authorship and revisions; verify the result before describing it
as tracked changes. No DOCX automation is bundled in this kit.

The legal researcher must verify governing-law rules and mandatory rights using current primary
sources. Templates are issue lists, not assertions that any wording is enforceable worldwide.
