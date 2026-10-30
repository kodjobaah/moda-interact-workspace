---
id: ARCH-052-ADMIN-003
architecture_id: ARCH-052
title: Author approved multi-discount checkout template bindings
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-SHARED-012
- ARCH-052-ADMIN-002
enables:
- ARCH-052-BACKGROUND-008
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: 2026-10-30
updated: 2026-10-30
---

# ARCH-052-ADMIN-003 — Author approved multi-discount checkout template bindings

## Architecture

Architecture: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Architect coordination task; **portable definition, not materialised**. No branch or runtime implementation has been created by this artifact.

## Objective

Support independently approved checkout-target CODE and AUTOMATIC template revisions capable of describing up to three source-backed compatible offers, without changing the six existing template purposes or the alternative-product IMAGE path.

## Context

The existing `INITIAL_CODE_OFFER` authoring permits only `offer.code`. Rendering multiple coupon codes into that singular semantic slot or sending multiple automatic discounts under singular wording is misleading and may conflict with approved copy. SHARED-011 adds a new explicit `offer.codes` text semantic. Meta accepts only approved immutable template revisions; the send worker must not improvise a new copy against an old approval.

## Scope

- Extend existing Admin authored template variable registry/validator/preview/compiler in `moda-interact-admin/src/lib/admin/whatsapp-templates/authoring/` and relevant tests to support `offer.codes` for `promotionTarget:CHECKOUT` CODE_OFFER; add plural multi-discount wording for checkout-target AUTOMATIC_OFFER without introducing a code variable for automatic-only offers.
- Require literal checkout-specific copy communicating a set of possible code offers (subject to checkout eligibility). Use the current existing Admin translation mechanism and 20 locales; no extra `INITIAL_*` enum.
- Keep existing `offer.code` single-code and all alternative-product template semantics intact. Freeze distinct revision and Meta review/approval identity; Background may select only actually approved revision.

## Out of Scope

- No provider upload; ARCH-052-BACKGROUND-012 owns the Meta IMAGE sample handle. No dynamic checkout URL validation or generation, product search, policy ranking, Woo restore application or direct Meta send.
- Do not edit `ARCH-052-SHOPIFY-001`, `ARCH-052-MCP-005` or `ARCH-049-BACKGROUND-003`.

## Requirements

- Max 3 codes are rendered by Background into one bounded text parameter in selected, source-confirmed order. Code list is not an arbitrary merchant/model text input.
- The checkout-target code template can display one or more codes; a singular CODE or AUTOMATIC template is never chosen for a multi-offer set. Mixed CODE+AUTOMATIC groups are permitted only if a separately approved revision truthfully mentions both components; otherwise fallback to a supported singleton.
- No claim that codes have been redeemed, cannot expire or will necessarily stack; preserve independently approved fallback when multi template unavailable.
- As immutable Meta review is asynchronous, do not mark new variant approved without actual Meta provider approval evidence.

## Work Items

- [ ] Add `offer.codes` to authoring variable registry/allowed checkout variables, compile and preview.
- [ ] Test freeze, submit, actual approval identity, wrong target/locale, unapproved multi fallback and no change to alternative product path.
- [ ] Update declared 20-locale catalogue strings where required; run focused Admin tests and builds.

## Interfaces / Contracts

Published Shared `RecoveryTemplateSemanticKeySchema` supports `offer.codes`; existing `RecoveryTemplateFrozenBindingsSchema` binds its position in approved TEXT/IMAGE checkout CODE_OFFER template. Example prepared text: `Use SAVE10 and SHIPFREE, subject to checkout eligibility` (from source-grounded codes only). No new Meta API component type or checkout URL slot is introduced.

## Dependencies

- ARCH-052-SHARED-012
- ARCH-052-ADMIN-002

## Enables

- ARCH-052-BACKGROUND-008
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] Multi-code template can be reviewed/approved independently of BACKGROUND-008 and other currently active task branches.
- [ ] Original single-code, single-automatic and no-offer registrations stay usable, with immutable purpose/target/header/locale guarantees.
- [ ] No product/media provider call from Admin or second grant model.

## Validation

- [ ] Existing Admin authoring/translation/Meta registration suite and focused multi-code variable tests.
- [ ] Admin declared typecheck/lint/build and `git diff --check`.

## Stop Condition

After the specified work, validation and acceptance criteria pass, update this task's Work Items and Completion Report, set status to `review`, hand back the implementation branch and evidence, and STOP. Do not self-accept, implement enabled tasks, modify other task/index files or push main.

## Implementation Notes

Use the launcher-resolved dedicated mirrored parent/implementation worktrees and shared structured logger. All unexpected errors must be logged with bounded identifiers and propagated to the owning failure/retry boundary. Never log coupon codes, customer information, bearer tokens or raw checkout URLs. Use relative workspace edit paths; do not touch `_index.md`.

## Completion Report

### Status

Not started — defined but not materialised.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

No production compatibility is required; all required source provenance remains available for implementing agents to verify.

### Unresolved Issues

None at definition time.

### Architectural Concerns

Any source contract/deployment gap must be escalated rather than patched locally.

## Architect Review

### Review Status

Pending.

### Review Notes

New multi-discount feature task; no implementation reviewed.

### Reviewed Files

None.

### Validation Reviewed

No implementation validation yet.

### Architecture Conformance

Pending implementation and review.

### Follow-up

None.
