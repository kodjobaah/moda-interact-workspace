---
id: ARCH-026-ADMIN-002
architecture_id: ARCH-026
title: Read merchant international context from shared Shop state
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-026-DATABASE-002
  - ARCH-026-SHOPIFY-002
  - ARCH-026-ADMIN-001
enables: []
created: 2026-10-02
updated: 2026-10-02
---

# Read merchant international context from shared Shop state

## Architecture

Architecture ID: `ARCH-026`

Architecture document: `docs/architecture/ARCH-026-woocommerce-application-foundation.md`

Coordinator: `moda_architect`

## Objective

Migrate Admin cross-merchant/support reads of merchant international context from `shopify.ShopSettings` to provider-neutral `commerce.Shop` state so Woo merchants do not require a fabricated Shopify settings row.

## Context

Current Admin support/translation logic reads `ShopSettings.defaultLanguageTag` for merchant-target language selection. DATABASE-002 establishes shared Shop language/time-zone/country context and SHOPIFY-002 ensures the current Shopify writer maintains it.

ADMIN-001 separately migrates the shared onboarding milestone and serializes ARCH-026 Admin changes.

## Scope

Modify only `moda-interact-admin` production/tests required to source international context from Shop.

Current inspected area includes `src/lib/admin/merchant-support.ts` and its focused security/tests.

Do not redesign support translation policy; replace the provider-specific persistence source only.

## Out of Scope

- Removing legacy ShopSettings fields.
- Woo merchant UI.
- Translation catalogue/provider redesign.
- Admin UI locale configuration.
- Billing/recovery logic.

## Requirements

### R1 — Shared Shop context is authoritative

Admin support/merchant international-context reads use shared Shop fields rather than requiring ShopSettings.

### R2 — Cross-platform tenants work without ShopSettings

A Woo Shop with no Shopify settings row can participate in the affected Admin support/read flows.

### R3 — Translation behavior is preserved

Existing target-language normalization/fallback behavior remains unchanged except for the source field.

## Work Items

- [ ] Update nested database gitlink to accepted DATABASE-002 and regenerate Prisma.
- [ ] Change Admin support international-context query/projection to shared Shop fields.
- [ ] Remove the affected runtime requirement for a ShopSettings join.
- [ ] Update focused security/unit tests with Shopify and Woo-like Shop fixtures.
- [ ] Audit changed Admin code for remaining ShopSettings international-context dependencies.

## Interfaces / Contracts

Database owner: `ARCH-026-DATABASE-002`.

## Dependencies

- `ARCH-026-DATABASE-002`
- `ARCH-026-SHOPIFY-002`
- `ARCH-026-ADMIN-001`

## Enables

None.

## Acceptance Criteria

- [ ] Affected Admin support logic reads shared Shop international context.
- [ ] Woo-like Shops require no ShopSettings row for the affected flow.
- [ ] Existing language normalization/fallback behavior remains unchanged.
- [ ] No legacy fields are removed.
- [ ] No unrelated Admin/business behavior changes.

## Validation

- [ ] Prisma generation from accepted DATABASE-002;
- [ ] typecheck;
- [ ] targeted lint;
- [ ] focused merchant-support/security tests;
- [ ] Woo-like no-ShopSettings fixture test;
- [ ] production build;
- [ ] static audit;
- [ ] `git diff --check`;
- [ ] clean task-worktree evidence.

## Stop Condition

After required work and validation, set status to `review`, complete the Completion Report, return to `moda_architect`, and STOP.

## Implementation Notes

Keep this task a bounded persistence-source migration.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

- SHOPIFY-002 is complete so current Shopify state is maintained on Shop.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
