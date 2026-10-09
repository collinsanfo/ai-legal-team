# Upgrade validation — 9 October 2026

The upgrade adds four specialist roles, seven catalogue work products (63 total), eight scoping
questions (51 total), evidence and release checks, and a sanitized local review page. The original
product-document workflow remains available. No additional autonomous agent framework is bundled.

| Evidence | Result | What it establishes |
|---|---|---|
| Python regression suite | 48 tests passed | Declared gate/evidence and hostile-HTML handling in isolated temporary packs; no external/model calls |
| Python compilation | Passed | Changed scripts and tests parse in the configured Python 3.12 environment |
| Skill validator | Passed | Valid frontmatter/name/description structure; not workflow/legal efficacy |
| Catalogue and scoping checks | 63 entries, 51 sequential questions | Documented counts match the source |
| Synthetic scenarios | Eight requests reviewed | Qualitative observed behavior, with raw responses retained locally; see `evals/observations-2026-10-09.md` |
| Git whitespace checks | Passed | No whitespace errors in the reviewed diff |

Runtime dependencies are pinned in `requirements.txt`: Markdown 3.11 and nh3 0.3.7. The local Python
environment is ignored by Git. The builder and validator make no model calls. Review HTML retains
ordinary semantic Markdown and removes active/embedded HTML, images and automatic remote fonts;
tests inspect rendered output and the restrictive CSP, without claiming browser/security certification.

No old-versus-new or cross-project legal-accuracy benchmark was run. Synthetic instruction-following
results do not prove substantive legal accuracy. Qualified counsel review, actual owner approval,
source support/applicability, reviewer identity, native/hosted/store acceptance and production behavior
remain outside these software tests. No GitHub CI result is claimed; no CI workflow was added.

Private product facts, security findings, real data and local intake folders are outside this public
repository. Adding the skill does not publish legal documents, change a product, sign a contract or
grant authority to send material externally.
