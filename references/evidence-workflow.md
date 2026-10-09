# Evidence, review and change control

Read `roles/12-evidence-verifier.md`. Use the machine contract in `references/evidence-schema.md`.
Store raw source snapshots and their hashes in the private pack, with enough context to check the
proposition. Source material may be confidential or copyrighted: save only appropriate extracts or
permitted copies. Do not reproduce large external texts in public comparison reports.

## Distinct checks

1. **Identity:** canonical official URL, publisher, title, document/section and retrieval time.
2. **Support:** does the source actually support this specific claim, including exceptions and context?
3. **Current status:** enactment/commencement dates, amendments, territorial versions, withdrawn policy,
   subsequent case treatment. A pending bill is not current law.
4. **Applicability:** actual operator/market, controller/processor/platform role, product facts, thresholds
   and exemptions. Interpretation needing counsel stays qualified, not mechanically verified law.
5. **Implementation:** local file and exact hash, commit/worktree state, relevant line range and observed
   behavior. Record local tests, native checks and hosted evidence separately.

Maintain stable source/claim IDs. Give each material product or legal claim an accepted/held/rejected
decision and verified/qualified/unverified/contradicted status. Held gaps stay visible in drafts/review;
an uncertain claim cannot be accepted just to clear a gate. Explicitly track which evidence supports
each selected public document, including how conflicts were resolved.

Researcher confidence is a separate judgment: high confidence in reading a statute is not high
confidence in territorial applicability. A source hash proves bytes, not authorship, source authority
or legal truth. Machine validators do not open URLs, evaluate entailment or perform a citator search.

## Independent pass and hand-off

Assign a verifier who reads raw evidence rather than only a summary. Preserve disagreement; neither
majority voting nor repeated model agreement resolves uncertain law. Make focused counsel questions
and engineering tasks with evidence IDs, severity, acceptance criteria and affected release surfaces.
Record observed scope/coverage, runtime/model configuration and limits, not a invented certainty score.

Re-review when document bytes, code facts, launch jurisdiction, provider terms or source policy change.
For publication use `references/publish-gate.md`. Owner/counsel/product records must come from actual
reviews with dated supporting artifacts; AI roles cannot manufacture them. Passing validates the
recorded local prerequisites and hashes, not legal compliance, reviewer credentials or deployment.
