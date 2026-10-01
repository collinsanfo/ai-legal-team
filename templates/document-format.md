# Document format

Every document is Markdown, pasted later into a page or a product screen that already shows its title.

## Top of every draft
1. No `#` title.
2. The banner, as one bold paragraph:
   `**DRAFT: not legal advice. Prepared by an AI system for review by {{OWNER}} and a qualified {{JURISDICTION}} lawyer. Do not publish until both have approved it.**`
3. The version line: `Version N (draft) · Effective [OWNER: date] · Last updated [OWNER: date] · Prepared {{DATE}}`
4. Public documents: an `## In short` section with 5 to 8 plain bullets.
5. Sections as `## 1. Heading`, subsections `###`. Category terms as `## Schedule A: Appointments` and so on.

## Markers (inline, exactly as written)
| Marker | Meaning |
|---|---|
| `[OWNER: ...]` | A fact or business choice only the owner can give |
| `[COUNSEL: ...]` | A legal point a lawyer must confirm |
| `[DECISION n]` | Text that follows owner decision n |
| `[APP CHANGE: ...]` | The product must change before this sentence is true |

## End of every draft
`## Notes for review (remove before publishing)`, containing:
- a table of every marker: marker, section, what is needed;
- the facts (N-numbers) and law (memo sections) relied on;
- `### Code changes needed for this document to be true`: a numbered list;
- one line per applied owner answer under a dated heading.

## After approval (finaliser)
- Banner: `**Approved by {{OPERATOR}} on {{DATE}}. Effective {{DATE}}.**` (internal documents:
  `**Internal. Approved {{DATE}}.**`)
- Version line: `Version N (final, approved {{DATE}}) · Effective {{DATE}} · Last updated {{DATE}}`
- Notes heading: `## Notes (remove before publishing)`
- No `[COUNSEL]` or `[DECISION]` markers left; `[APP CHANGE]` only where the product still has to change.

## Writing rules
- Short sentences, common words, one idea per sentence. No "hereinafter", no Latin.
- Lead each section with its point.
- Define each term once, then use it the same way everywhere.
- Never state as current anything the product does not do.
