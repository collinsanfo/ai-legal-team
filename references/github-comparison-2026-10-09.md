# GitHub legal-agent comparison — 9 October 2026

This comparison informs the design of this kit for software, apps and websites. It is a source inspection, not a legal opinion, procurement certification or performance benchmark. No measured cross-kit legal efficacy evaluation has been run. The inspected material does not establish a universal best legal team. Repository popularity, agent counts, passing software tests and recent commits do not establish legal correctness.

The upgrades in this kit are original implementation. This review borrows workflow ideas; it does not import third-party code, prompts or document templates.

## Scope and reproducible snapshot

Primary repository documentation, selected skill instructions, validators, license text and benchmark documentation were inspected. GitHub's repository and commit APIs supplied the following default-branch snapshot. All six repositories were non-archived when checked on 9 October 2026. Activity establishes a maintenance signal, not quality, support or legal currency. A repository's `pushed_at` may reflect another branch; the dates below belong to the inspected default-branch commits.

| Project | Default branch | Commit | Commit date (UTC) |
| --- | --- | --- | --- |
| Anthropic Claude for Legal | `main` | [4a6c6518](https://github.com/anthropics/claude-for-legal/commit/4a6c651889c97cc9140580363c73e0eb17379c2b) | 2026-07-23 |
| LegalQuants LQ Skills | `main` | [884cf402](https://github.com/LegalQuants/lq-skills/commit/884cf402949981ca2a4afb8ff88f19337005eecf) | 2026-06-28 |
| LegalQuants LQ.AI | `main` | [224044cc](https://github.com/LegalQuants/lq-ai/commit/224044cc9c43913e1606919cef47fa77794f3aef) | 2026-10-09 |
| doc.haus | `dochaus` | [f3cdfd15](https://github.com/sure-scale/doc-haus/commit/f3cdfd15f7b675e651773b3f6a8ef9468f56ed14) | 2026-06-13 |
| Rohas Nagpal Legal AI Skills / vCLO | `main` | [949d2488](https://github.com/rohasnagpal/legal-ai-skills/commit/949d2488815f8ace752b022e8b75374782af4ba8) | 2026-10-09 |
| Harvey Legal Agent Benchmark | `main` | [a15650fe](https://github.com/harveyai/harvey-labs/commit/a15650fe74bb20b86f160aaabdad75b87a91b6e8) | 2026-10-08 |

## Agent frameworks and workflow libraries

| Candidate and inspected sources | Useful design lessons | Limits and reuse caveats |
| --- | --- | --- |
| [Claude for Legal](https://github.com/anthropics/claude-for-legal), [OSS review](https://github.com/anthropics/claude-for-legal/blob/4a6c651889c97cc9140580363c73e0eb17379c2b/ip-legal/skills/oss-review/SKILL.md), [launch review](https://github.com/anthropics/claude-for-legal/blob/4a6c651889c97cc9140580363c73e0eb17379c2b/product-legal/skills/launch-review/SKILL.md) | Product, privacy, commercial, AI-governance and IP workflows; practice profiles and approval routing. OSS review considers deployment model, version-specific license text, transitives and outbound notices. | Apache-2.0 repository. Primarily Claude configuration; some connectors require customer subscriptions. Its structural [validator](https://github.com/anthropics/claude-for-legal/blob/4a6c651889c97cc9140580363c73e0eb17379c2b/scripts/validate.py) does not measure legal accuracy. Treat its legal characterizations as review prompts, not authorities. |
| [LQ Skills](https://github.com/LegalQuants/lq-skills), [eval guidance](https://github.com/LegalQuants/lq-skills/blob/884cf402949981ca2a4afb8ff88f19337005eecf/evals/README.md), [license-comply](https://github.com/LegalQuants/lq-skills/blob/884cf402949981ca2a4afb8ff88f19337005eecf/skills/license-comply/SKILL.md) | Harness-independent skills, proposition checking, adversarial review, source-status discipline, EU privacy-notice and DPA workflows. Baseline comparisons and retained evidence are encouraged. | Apache-2.0 generally, with individual MIT exceptions; inspect each selected skill's license. Legacy evals are explicitly manual behavioral checks. The license skill covers Python and per-dependency policy classification, not npm/native dependencies or overall license compatibility. |
| [LQ.AI](https://github.com/LegalQuants/lq-ai), [honest-state catalog](https://github.com/LegalQuants/lq-ai/blob/224044cc9c43913e1606919cef47fa77794f3aef/docs/HONEST-STATE.md) | Matter-scoped work, citation ledger, quote verification, explicit failure states, governed tool calls and cost/halt brakes. A capability-to-code/test catalog makes claims inspectable. | Apache-2.0 core; OpenWebUI and PyMuPDF introduce separate license conditions. Do not assume an HTTP boundary resolves AGPL obligations. Its catalog discloses unfinished instruction-channel isolation, unmeasured legal-corpus anonymization accuracy, deferred DOCX ingestion and scaffold-only substantive Word features. |
| [doc.haus](https://github.com/sure-scale/doc-haus), [license](https://github.com/sure-scale/doc-haus/blob/f3cdfd15f7b675e651773b3f6a8ef9468f56ed14/LICENSE) | OpenCode-derived agent harness; reviewer, adversarial challenger and summarizer; matter-local document index; source quotations and Word tracked changes. | Actual LICENSE is MIT with retained OpenCode attribution, despite GitHub metadata reporting `NOASSERTION`. Local storage does not make cloud-model prompts local. Source and demos do not establish independently measured legal efficacy. |
| [Legal AI Skills / vCLO](https://github.com/rohasnagpal/legal-ai-skills), [validator](https://github.com/rohasnagpal/legal-ai-skills/blob/949d2488815f8ace752b022e8b75374782af4ba8/scripts/validate.rb) | A coordinating chief agent, practice specialists, jurisdiction modules, official-source routing and coordinated legal workflows; Codex and Claude support. | MIT. India/US/UK modules do not establish EU or German coverage. Structural safeguards and behavioral fixtures are useful, but skill counts and validation success are not proof of correct legal outcomes. |

Design recommendation: use Claude for Legal as the most relevant workflow reference for software launch and OSS/IP coverage; use LQ's evidence discipline and doc.haus's independent challenge pattern. This is a fit judgment, not a performance ranking.

## Evaluation infrastructure

[Harvey LAB](https://github.com/harveyai/harvey-labs) is an MIT-licensed benchmark and execution/grading harness, not an installable legal department. Its [tutorial](https://github.com/harveyai/harvey-labs/blob/a15650fe74bb20b86f160aaabdad75b87a91b6e8/docs/tutorial.md) describes task instructions, synthetic lawyer-reviewed documents, explicit deliverables, rubric criteria, traces and LLM judging. Synthetic documents have acknowledged imperfections. Scores belong to the tested model, tools, task set and budget; they do not automatically transfer to this kit or prove jurisdiction-specific launch readiness.

## Gap-to-upgrade mapping

| Gap to address in this kit | Upgrade requirement |
| --- | --- |
| General IP review lacks a software inventory | Record pinned dependencies, actual license text, transitives, vendored code, assets, fonts, models and native plugins; distinguish hosted service, browser distribution and mobile binaries. Keep unknown/conflicting licenses unresolved. |
| General contracts miss delivery mechanics | Add SOW scope, acceptance evidence, change control, IP chain, background IP, confidentiality, maintenance, vendor/API terms, handover and exit questions. |
| Privacy text can outrun implementation | Map processing purposes, data categories, vendors, permissions, retention, deletion and security claims to inspected implementation and tests. Confirm markets and operator facts rather than infer jurisdiction from location. |
| Launch review can become a generic checklist | Bind findings to code paths, versions, screenshots, platform requirements and actual proof; identify missing acceptance evidence. |
| Citation presence can masquerade as support | Separate quotation matching from current authority, applicability and proposition support; retain source, date, jurisdiction, pinpoint, status and disagreements. |
| Marker/banner gates can accept unsupported output | Require structured evidence, issue resolution and independent challenge; distinguish missing facts, owner decisions and human legal review. |
| Added coverage can be mistaken for proven efficacy | Compare old and upgraded workflows on the same unseen fixtures, model, tools and budgets. Measure issue recall, unsupported claims, citation support, coverage, time and cost; retain outputs and grading evidence. |

Until that evaluation exists, describe these changes as broader coverage and stronger verification controls. Keep deterministic gate tests, model-output evaluation and human legal review as separate evidence.
