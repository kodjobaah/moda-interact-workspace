---
id: ARCH-064-SHARED-003
architecture_id: ARCH-064
title: support canonical purpose output schemas
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: review
priority: 40
executor: codex
claimed_at: 2026-11-06T20:07:25Z
attempt: 1
depends_on: ['ARCH-064-SHARED-002']
enables: ['ARCH-064-SHARED-004']
created: 2026-11-06
updated: 2026-11-06
---
# Support canonical purpose output schemas

## Architecture
ARCH-064; docs/architecture/ARCH-064-published-initial-outreach-profile.md. Coordinator moda_architect.

## Objective
Provide one bounded Shared purpose output-schema contract/validator that represents the existing registered default policy outputs without changing their data semantics.

## Context
Commerce Attempt 1 proved Shared 5.4.0 purpose outputSchema:DetailsSchemaSchema rejects all four actual default policy outputs. Discount descriptors use root anyOf; products use nullable objects, format/pattern and category/collection arrays up to128. No canonical compatible projector exists. Commerce remains fail-closed; no local schema fork permitted.

## Scope
Inspect actual published CommerceToolOutputs descriptors and existing bounded schema compiler. Extend a purpose-specific canonical bounded output subset/validator supporting the required existing union/nullable-object forms and safe fixed format/pattern semantics; retain finite schema depth/bytes/property/array/result limits and fail closed on unsupported keywords. Preserve existing DetailsSchemaSchema users unless demonstrably compatible. Update CommercePurposeProfileSchema and canonical manifest/grant binding to the same validator. Export consumer runtime validation once; no Commerce-local schema copy or lossy invented projection. Do not permit arbitrary eval, unrestricted regex/JSON Schema, unlimited arrays or weaker output validation. Existing maxItems=128 fields require an explicit bounded supported decision, with total 32KiB runtime result limit unchanged.

## Out of Scope
Changing canonical tool outputs, host offer evidence authority, permissions/entitlements, Commerce/MCP/Background implementation, main integration or automatic follow-on work.

## Requirements
All four real default outputs (discount options/details, product search/get) accepted by profile schema and validated results; malformed/oversized/unsupported schemas and invalid outputs fail closed. Fifth bounded read operation remains supported. Manifest/grant compatibility tests bind exact purpose schemas/identities; no changed tool result semantics.

## Work Items
- [x] Inspect actual published CommerceToolOutputs descriptors and existing bounded schema compiler. Extend a purpose-specific canonical bounded output subset/validator supporting the required existing union/nullable-object forms and safe fixed format/pattern semantics; retain finite schema depth/bytes/property/array/result limits and fail closed on unsupported keywords. Preserve existing DetailsSchemaSchema users unless demonstrably compatible. Update CommercePurposeProfileSchema and canonical manifest/grant binding to the same validator. Export consumer runtime validation once; no Commerce-local schema copy or lossy invented projection. Do not permit arbitrary eval, unrestricted regex/JSON Schema, unlimited arrays or weaker output validation. Existing maxItems=128 fields require an explicit bounded supported decision, with total 32KiB runtime result limit unchanged.

## Interfaces / Contracts
Published @modainteract/moda-interact-shared/commerce purpose profile and canonical manifest/grant contracts. Shared owns reusable bounded schema mechanics; service owners retain policy/runtime authorization. Keep immutable release identity and current overall budgets.

## Dependencies
- ARCH-064-SHARED-002

## Enables
- ARCH-064-SHARED-004

## Acceptance Criteria
- [x] All four real default outputs (discount options/details, product search/get) accepted by profile schema and validated results; malformed/oversized/unsupported schemas and invalid outputs fail closed. Fifth bounded read operation remains supported. Manifest/grant compatibility tests bind exact purpose schemas/identities; no changed tool result semantics.

## Validation
- [x] Focused deterministic default descriptor/result vectors, union branches/nulls, invalid outputs, excessive depth/bytes/items, unsupported keywords; declared Shared typecheck/build. No service integration or publication.

## Stop Condition
Publish implementation/report task branches and submit for architect review, then STOP. Explicit developer completion required; no enabled task auto-start.

## Implementation Notes
Exact reproduced default schema evidence is recorded in blocked ARCH-064-COMMERCE-001 report. Inspect existing bounded validator before selecting narrow representation changes; return an incompatible safety requirement to architect. No weakening through unknown schema acceptance.

## Completion Report
### Status
Ready for Review — bounded canonical purpose-output correction implemented, validated and published.
### Files Changed
- src/commerce/purpose-output.ts
- src/commerce/purpose-output.fixtures.json
- src/commerce/purpose-output.test.ts
- src/commerce/definitions.ts
- src/commerce/index.ts
- src/commerce/runner/tool-execution.ts
### Work Completed
Added one purpose-specific canonical schema/consumer compiler exported through ./commerce: CommercePurposeOutputSchema, CommercePurposeOutputSchemaSchema, validateCommercePurposeOutputSchema and compileCommercePurposeOutputSchema. Profile validation and runner successful-result validation consume it; canonical manifest/grant binding continues to bind complete exact output schema and identities. Existing Input/Details subsets and tool result data are unchanged.

Approved finite bounds: schema 32768 UTF-8 bytes, depth 8, 256 nodes, 128 total object properties, 2–4 anyOf branches, 128 array members, 4096 string characters and complete result 32768 UTF-8 bytes. Array/string maxima omitted by actual descriptors receive implicit runtime caps 128/4096; explicit above-cap maxima reject. Closed objects, supported keywords/types, numeric bounds and enums validated; nullable objects/arrays and root object unions supported. Schema is snapshotted by compiler, so later caller mutation cannot change enforcement. No arbitrary JSON Schema/eval or caller regex execution.

Only exact code-owned pattern spellings recognized: canonical money and known UTC datetime encodings. Fixed semantic functions enforce money syntax, calendar validity, timestamp precision and URI semantics matching existing CommerceProductSchema (HTTPS, no credentials/nondefault port). Unsupported format/pattern fails closed. Canonical JSON rejects cycles, nonfinite values, foreign prototypes and sparse/extended arrays. No output projection or tool output change; budget enforcement rejects oversized results.

Preserved exact audited descriptors for all four defaults and compared current real CommerceToolOutputs serializers explicitly. Tested complete unchanged discount options/details/unavailable/null branches, full products with sale evidence and 128 category/collection IDs. Fifth bounded read-operation shape remains supported. Manifest/grant output-schema tampering rejects.
### Validation Results
- `npx tsx --test src/commerce/purpose-output.test.ts src/commerce/purpose-profile.test.ts src/commerce/selection.test.ts src/commerce/runner/runner.test.ts`: PASS 69/69, zero skips/failures.
- Final `npm run typecheck`: PASS.
- Final `npm run build`: PASS ESM and declaration build for latest runtime source.
- `git diff --check`: PASS.
- Tests cover exact default descriptors/results, union branches/nulls, actual canonical output validation, malformed outputs, amounts, UTC calendar/precision, HTTPS semantics, unsupported keywords/patterns/formats, schema bytes/depth/nodes/properties/branches, implicit/explicit array/string bounds, total32KiB, prototypes/cycles/nonfinite/sparse data, compiler mutation isolation and exact profile/manifest/grant binding.
- Initial run exposed only test serialization mismatch (raw Zod versus existing authoring nullable/enum projection) and current locked Zod datetime spelling drift; corrected explicit test representation and compatibility coverage. A test-helper annotation was corrected after initial typecheck. No task-introduced unresolved failures.
### Deviations
Architect approved purpose-only caps above rather than widening existing DetailsSchemaSchema. Actual locked Zod emits optional-seconds UTC datetime spelling whereas audited descriptor receipt requires seconds; both exact fixed patterns supported with distinct precision semantics. Tests assert this single known difference rather than falsely normalizing it away, and prove minute precision succeeds only current encoding. Existing safe HTTPS refinement was confirmed directly from canonical CommerceProductSchema. Test-only descriptor serialization preserves existing nullable/enum form; no runtime schema/result weakening.
### Assumptions
Producer descriptors remain authoritative for tool-specific semantics; generic purpose compiler enforces the bounded supported schema plus existing execution validators/authorization. Consumer wiring and separate SHARED-004 publication remain gated; no package release or consumer implementation performed.
### Unresolved Issues
None scoped.
### Architectural Concerns
No permission/evidence authority expansion, tool-output semantic change or unrestricted compiler introduced.
### Git / VCS
Task branch: task/ARCH-064-SHARED-003.

Physical worktree isolation (launcher packet):
- canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
- parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-064-SHARED-003
- parent branch: task/ARCH-064-SHARED-003
- implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-064-SHARED-003
- implementation branch: task/ARCH-064-SHARED-003
- shared/default checkouts switched or mutated for task implementation: no
- another task worktree reused: no

Start-of-attempt synchronization (launcher packet):
- parent remote task branch fast-forwarded: not-needed
- parent origin/main incorporated: already-current
- implementation remote task branch fast-forwarded: not-needed
- implementation origin/main incorporated: already-current
- recursive submodule sync/update: passed; recorded submodules none; status ready
- Attempt 1 claim: d4563a717c6e56cb25f83e1f70efbeb7fb7ad045; pushed yes

Implementation commit e42a8a38044cdb1b9b909bf790bbb35e37332d6b pushed to origin/task/ARCH-064-SHARED-003; implementation tree clean. Parent report is committed/pushed on matching task branch after this edit; exact report commit available in Git history. Submodule gitlink staged: no. Merged to implementation main: no. Merged to workspace main: no. Package version changed/published: no.

## Architect Review
### Review Status
Pending
### Review Notes
Correction definition only, no execution.
### Reviewed Files
Blocked Commerce evidence and published profile contract.
### Validation Reviewed
No execution claimed.
### Architecture Conformance
Shared-first correction with separate publication gate.
### Follow-up
None
