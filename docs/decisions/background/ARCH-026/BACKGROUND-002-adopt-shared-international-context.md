---
id: ARCH-026-BACKGROUND-002
architecture_id: ARCH-026
title: Adopt the shared merchant international context in Background
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-026-DATABASE-002
  - ARCH-026-SHOPIFY-002
  - ARCH-026-BACKGROUND-001
enables: []
created: 2026-10-02
updated: 2026-10-02
---

# Adopt the shared merchant international context in Background

## Architecture

Architecture ID: `ARCH-026`

Architecture document: `docs/architecture/ARCH-026-woocommerce-application-foundation.md`

Coordinator: `moda_architect`

## Objective

Migrate Background runtime reads of merchant language, time zone and country from Shopify-specific `ShopSettings` to provider-neutral `commerce.Shop` international context, preserving existing conversation/recovery/template semantics.

## Context

Current Background services read `ShopSettings.defaultLanguageTag`, `defaultTimeZone` and `defaultCountryCode` for conversation language defaults, WhatsApp template selection and recovery/merchant context. DATABASE-002 establishes these values on shared Shop; SHOPIFY-002 ensures current Shopify provisioning maintains them.

Woo Background workflows must not require a Shopify settings row merely to resolve merchant international context.

## Scope

Modify only `moda-interact-background` code/tests required to change the source of merchant/store international context.

Current inspected production areas include:

```text
src/services/conversation.service.ts
src/services/whatsapp-template-selector.service.ts
src/services/checkout-recovery.service.ts
```

Migrate related query projections and tests as required.

### Authoritative reads

Use:

```text
Shop.storeLocale
Shop.defaultLanguageTag
Shop.defaultTimeZone
Shop.defaultCountryCode
```

for shared international context.

Do not read ShopSettings as a fallback for those values after this task. The accepted DATABASE-002 migration/backfill and SHOPIFY-002 writer migration are the compatibility mechanism.

### Locale policy

Do not add a fixed locale allowlist. Existing business helpers may normalize `defaultLanguageTag` for provider/tool requirements, but an unknown provider-native `storeLocale` must not cause job failure by itself.

Preserve the existing distinction between merchant/store default language and customer/conversation language. CommerceAgent should continue replying in the conversation/customer language where the existing architecture says so.

## Out of Scope

- Writing shared international context.
- Woo plugin locale synchronization.
- Shopify app migration; owned by SHOPIFY-002.
- Admin migration; owned by ADMIN-002.
- Translation-provider/catalogue redesign.
- Queue/event contract changes.
- Billing/recovery lifecycle redesign.

## Requirements

### R1 — Shared context is authoritative

Background international-context reads come from Shop, not ShopSettings.

### R2 — No Shopify row requirement

A Woo Shop with no ShopSettings row can supply shared language/time-zone/country context to Background.

### R3 — No locale allowlist

Provider-native locale identity is not rejected because it lacks a Moda-authored translation.

### R4 — Existing language semantics remain intact

Store default language and conversation/customer response language remain separate concepts.

## Work Items

- [ ] Update nested database gitlink to accepted DATABASE-002 and regenerate Prisma.
- [ ] Migrate conversation-context language reads to shared Shop fields.
- [ ] Migrate WhatsApp template-selector merchant language reads to shared Shop fields.
- [ ] Migrate checkout-recovery merchant language/time-zone/country reads to shared Shop fields.
- [ ] Update focused tests, including Woo-like Shop fixtures with no ShopSettings row.
- [ ] Update documentation that names ShopSettings as the international-context source.
- [ ] Add a static audit of production ShopSettings international-context references.

## Interfaces / Contracts

Database owner: `ARCH-026-DATABASE-002`.

No queue/shared-package contract changes.

## Dependencies

- `ARCH-026-DATABASE-002`
- `ARCH-026-SHOPIFY-002`
- `ARCH-026-BACKGROUND-001`

SHOPIFY-002 ensures the current provider writer maintains shared fields; BACKGROUND-001 serializes ARCH-026 changes in the Background repository.

## Enables

None.

## Acceptance Criteria

- [ ] Background production code no longer requires ShopSettings solely for language/time-zone/country context.
- [ ] Woo-like Shop fixtures without ShopSettings can resolve shared international context.
- [ ] Existing conversation language and WhatsApp template-selection semantics remain unchanged.
- [ ] Existing recovery country/time-zone normalization behavior remains unchanged apart from source.
- [ ] Unknown provider-native store locale does not fail jobs solely due to translation coverage.
- [ ] No queue/event contract or business lifecycle changes are introduced.

## Validation

- [ ] Prisma generation from accepted DATABASE-002;
- [ ] typecheck;
- [ ] targeted lint;
- [ ] focused conversation service tests;
- [ ] WhatsApp template-selector tests;
- [ ] checkout-recovery international-context tests;
- [ ] Woo-like no-ShopSettings fixture test;
- [ ] production build;
- [ ] static audit;
- [ ] `git diff --check`;
- [ ] clean task-worktree evidence.

## Stop Condition

After required work and validation, set status to `review`, complete the Completion Report, return to `moda_architect`, and STOP.

## Implementation Notes

This is a source migration, not an opportunity to redesign language selection or translation fallbacks.

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

- SHOPIFY-002 is complete before this task so current Shopify writers maintain shared context.

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
