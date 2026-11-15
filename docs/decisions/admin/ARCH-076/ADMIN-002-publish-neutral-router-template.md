---
id: ARCH-076-ADMIN-002
architecture_id: ARCH-076
title: Publish a dedicated tenant-neutral routing template
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 25
executor: codex
claimed_at: 2026-11-15T12:57:28Z
attempt: 1
depends_on: []
enables: [ARCH-076-BACKGROUND-004]
created: 2026-11-15
updated: 2026-11-15
---

# Publish a dedicated tenant-neutral routing template

## Architecture

[ARCH-076](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md), coordinated by `moda_architect`. This task owns the Admin authoring/publication boundary; BACKGROUND-004 owns runtime selection and neutral sending.

## Objective

Allow a platform administrator to author, review and activate an independent neutral ROUTER template for questions whose merchant is not yet proved.

## Context

The live ambiguity message is hard-coded, while ordinary AI/HUMAN/SHARED layouts can require a merchant identity, customer or checkout. Borrowing such a layout before merchant attribution either leaks a tenant or refuses the send. The product owner requires a separate Admin-editable neutral template and the normal shop layout only after a shop is established.

The current database stores `WhatsAppConversationWrapperActiveSlot.audience` as String varchar(24). Admin owns its authoring audience union and publication controls. Shared 6.1.0's prepared projection reader and renderer do not select an audience. Its ordinary `chooseSlot` and `validDefinition` deliberately accept only SHARED/AI/HUMAN: preserve that boundary. This task needs no database migration or Shared release.

## Scope

- Extend Admin-owned authoring audience types, family/audience selector, draft operations, variable palette, examples and read-only/detail/coverage labels with `ROUTER`, displayed as “Router — before a shop is selected”.
- Extend `src/lib/admin/whatsapp-templates/wrappers/{contracts,eligibility,reads,service,repository,preview}.ts` and existing authoring/compilation/publication actions only as needed to persist and activate that exact audience.
- Keep `MODA_CONVERSATION_WRAPPER`, prepared schema version 1, immutable source/locale hashes, review records, active-slot edit-version CAS, authorization and audit mechanisms.
- Reuse the existing translation/review workflow and normal supported locales. No live translation, publication, activation or Meta call occurs during implementation validation.
- Update relevant unit/component and disposable PostgreSQL authoring/publication tests, operator documentation and declared scripts where required.

## Out of Scope

Sender inventory, billing/allowance renewal, merchant identity matching, routing-model decisions, provider dispatch, changes to Shared ordinary audience policy, schema migration, live credentials/settings or Meta registration. No second template engine or hand-built runtime projection format.

## Requirements

1. ROUTER is an Admin application-owned persisted audience. The browser may select it only through authenticated existing template actions. Super-admin mutation/read rules, current environment isolation, review and source immutability stay unchanged.
2. A ROUTER definition uses exactly one `response.body` slot in body. Static neutral header/footer text is allowed. Reject all `variable` nodes in every section, checkout conditionals, `productImage`, `compositeProfile` and composite hashes, and any required customer/shop/checkout binding. Never silently strip unsafe nodes on save, compile, review or activation. No logo or shop masthead is implied by selecting ROUTER.
3. Reuse the existing prepared compiler/hash format: audience remains on the definition, not a new Shared prepared JSON field. Read/preview checks inspect the actual compiled projection as well as authoring input so a tampered persisted payload cannot bypass the neutral rule.
4. Ordinary SHARED/AI/HUMAN authoring, common-layout projection, renderer and publication retain their behavior. ROUTER does not require the SHARED composite profile. Do not label ROUTER as AI or pass it into Shared's ordinary audience selection to obtain acceptance.
5. Fix the Admin publication/reads fallback explicitly: ROUTER selects only its own active slot. No ROUTER→SHARED/AI/HUMAN fallback; ordinary source precedence stays unchanged. Missing ROUTER is visibly “Not configured”. A configured invalid/retired/unreviewed/hash-mismatched ROUTER definition is visibly refused, never shown as absence or replaced with another audience.
6. Use existing locale review/publication eligibility, source hash/content hash, actor identity and edit-version checks. Concurrent activations CAS the same ROUTER slot. Activating ROUTER cannot mutate or deactivate SHARED, AI or HUMAN. Record normal bounded audit provenance.
7. The preview shows platform-neutral static outer copy plus an illustrative routing question. It loads no shop, customer, basket, media or checkout. Explain that merchant-specific text/media appear only after verified shop selection, through that shop's normal AI/SHARED path. The editor must not suggest inserting raw placeholders as a way around restricted variables.
8. Runtime safety remains Background-owned: ADMIN-002 validates allowed structure and publication; BACKGROUND-004 also rechecks the neutral projection and outer static copy against its proved candidate identity scope. This task must not claim arbitrary administrator text can be automatically proven tenant-neutral without runtime checks.

## Work Items

- [ ] Add isolated ROUTER authoring, labels, restricted palettes and neutral preview.
- [ ] Apply restrictive compiled-projection validation and independent publication/read selection.
- [ ] Preserve immutable review/hash/CAS/audit behavior and all ordinary audience regressions.
- [ ] Run focused component/unit and disposable PostgreSQL checks plus repository-required lint/type/build checks; publish both task branches and report.

## Interfaces / Contracts

Persist existing `WhatsAppTemplateDefinition.kind='MODA_CONVERSATION_WRAPPER'`, `audience='ROUTER'`; active slot key is exactly `ROUTER`. Reuse existing prepared schema version 1, `readPreparedWrapper` and `renderPreparedWrapper` structural machinery from the published Shared package. The normal Shared `WrapperAudience`, `WrapperSource`, `chooseSlot` and `validDefinition` are not widened.

Background's application-owned selector will read only ROUTER for neutral scope and revalidate the published definition/locale/hash/slot provenance. It will render with no tenant/customer variables, no media and checkout unavailable. No new queue or public API payload is introduced.

## Dependencies

- ARCH-076-DATABASE-001, accepted and available at the intended consumer database pin. Existing wrapper tables themselves need no change.

## Enables

- ARCH-076-BACKGROUND-004 consumes the independent published ROUTER slot.
- ARCH-076-SYSTEM-TEST-001 remains manual-gated and is not executed in this user-authorized cycle.

## Acceptance Criteria

- [ ] A real Admin component/action round trip saves, reviews and activates a valid neutral ROUTER source with immutable prepared hash and independent slot.
- [ ] Every variable category, conditional, product/composite media option, raw placeholder and tampered compiled projection is rejected with actionable UI feedback, without silently rewriting source.
- [ ] Missing and refused ROUTER are distinct; neither falls back to normal audiences. Normal SHARED/AI/HUMAN selection still works with a ROUTER row present.
- [ ] Lower roles, stale source/locale review, retired definition, incorrect hashes, stale edit version and concurrent activations cannot mutate the wrong slot.
- [ ] Preview uses no merchant/customer/media query and no remote provider call; labels/documentation accurately describe neutral scope.

## Validation

Inspect the implementation worktree's actual package scripts before running them. Extend the existing template authoring/compilation/wrapper publication unit and component suites. Extend the existing disposable PostgreSQL wrapper-publication harness for ROUTER isolation, actual source→projection→review→slot CAS, concurrent activation and tampering. Run declared relevant lint, typecheck and production build; `git diff --check`. Record exact commands/results, baseline warnings and invocation-owned database cleanup. Do not call production or run the deferred SYSTEM-TEST task.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation pass, set the task to review, commit/push implementation and parent task-report branches, return to `moda_architect` and stop. No main merge, live activation or follow-on task.

## Implementation Notes

Defined in the reconciliation parent branch, not claimed. Use `/moda-task ARCH-076-ADMIN-002` only after architect promotion to Ready and launcher preparation. No implementation worktree is required merely for definition. Keep application policy out of Shared and avoid any duplicate hashing/rendering implementation.

## Completion Report

### Status

Not Started.

### Files Changed

Pending implementation.

### Work Completed

Pending. Record exact launcher-resolved parent/implementation worktrees, mirrored branch, preparation/synchronization packet and consumer database pin.

### Validation Results

Pending. Record actual checks, warnings/failures and cleanup.

### Deviations

None recorded.

### Assumptions

None recorded.

### Unresolved Issues

None recorded.

### Architectural Concerns

None recorded.

## Architect Review

### Review Status

Pending.

### Review Notes

Pending.

### Reviewed Files

Pending.

### Validation Reviewed

Pending.

### Architecture Conformance

Pending.

### Follow-up

Pending.
