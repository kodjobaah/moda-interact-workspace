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
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 0
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
- [ ] Inspect actual published CommerceToolOutputs descriptors and existing bounded schema compiler. Extend a purpose-specific canonical bounded output subset/validator supporting the required existing union/nullable-object forms and safe fixed format/pattern semantics; retain finite schema depth/bytes/property/array/result limits and fail closed on unsupported keywords. Preserve existing DetailsSchemaSchema users unless demonstrably compatible. Update CommercePurposeProfileSchema and canonical manifest/grant binding to the same validator. Export consumer runtime validation once; no Commerce-local schema copy or lossy invented projection. Do not permit arbitrary eval, unrestricted regex/JSON Schema, unlimited arrays or weaker output validation. Existing maxItems=128 fields require an explicit bounded supported decision, with total 32KiB runtime result limit unchanged.

## Interfaces / Contracts
Published @modainteract/moda-interact-shared/commerce purpose profile and canonical manifest/grant contracts. Shared owns reusable bounded schema mechanics; service owners retain policy/runtime authorization. Keep immutable release identity and current overall budgets.

## Dependencies
- ARCH-064-SHARED-002

## Enables
- ARCH-064-SHARED-004

## Acceptance Criteria
- [ ] All four real default outputs (discount options/details, product search/get) accepted by profile schema and validated results; malformed/oversized/unsupported schemas and invalid outputs fail closed. Fifth bounded read operation remains supported. Manifest/grant compatibility tests bind exact purpose schemas/identities; no changed tool result semantics.

## Validation
- [ ] Focused deterministic default descriptor/result vectors, union branches/nulls, invalid outputs, excessive depth/bytes/items, unsupported keywords; declared Shared typecheck/build. No service integration or publication.

## Stop Condition
Publish implementation/report task branches and submit for architect review, then STOP. Explicit developer completion required; no enabled task auto-start.

## Implementation Notes
Exact reproduced default schema evidence is recorded in blocked ARCH-064-COMMERCE-001 report. Inspect existing bounded validator before selecting narrow representation changes; return an incompatible safety requirement to architect. No weakening through unknown schema acceptance.

## Completion Report
### Status
Not Started
### Files Changed
None
### Work Completed
None
### Validation Results
Not run; definition only.
### Deviations
None
### Assumptions
Existing canonical default result contracts remain unchanged.
### Unresolved Issues
None beyond scoped correction.
### Architectural Concerns
Preserve finite validation/evidence boundaries.

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
