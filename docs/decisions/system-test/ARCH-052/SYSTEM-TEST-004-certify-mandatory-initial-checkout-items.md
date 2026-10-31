---
id: ARCH-052-SYSTEM-TEST-004
architecture_id: ARCH-052
title: Certify basket item content in approved initial recovery templates across platforms
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 96
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-052-ADMIN-004
  - ARCH-052-BACKGROUND-017
  - ARCH-052-BACKGROUND-008
  - ARCH-052-BACKGROUND-007
  - ARCH-052-BACKGROUND-005
enables: []
created: 2026-10-31
updated: 2026-10-31
---

# ARCH-052-SYSTEM-TEST-004: Certify original checkout items in all INITIAL template variants

## Architecture

Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Owner: `moda_system_test` / `moda-interact-system-test`. Portable terminal validation task, **defined but not materialised**. Must remain Pending until every implementation/publication dependency is architect-accepted Complete; the developer may manually test before invoking this task.

## Objective

Independently verify that the **actual abandoned checkout items** appear in the BODY of each approved Meta INITIAL outreach template for Shopify and WooCommerce, including NO_OFFER, single/multi-discount, alternative-product and optional IMAGE variants, and cannot be bypassed by fallback, locale selection, retries or cross-tenant data.

## Context

ADMIN-004 requires one frozen `checkout.itemsSummary` BODY binding per initial variant and new immutable provider-approved revisions. BACKGROUND-017 enforces the same obligation at selection, preparation and provider-send admission, using BG005's trusted first-three-lines + `+N` formatter. No new Shared schema, Meta purpose or checkout URL is created.

## Scope

Build disposable integrated Shopify + WooCommerce merchant fixtures, real frozen published template registrations and recorded simulated Meta approval/transport at external boundaries; run both platform's existing recovery-to-WhatsApp pipeline and inspect the actual prepared `BODY` parameters and outbound durable receipts.

## Out of Scope

No changes to Background, Admin, Shared, Meta provider definitions, production fixtures or order-confirmation templates. Do not modify other tasks or `_index.md`. This task does not grant permission to bypass actual Meta approval in production.

## Requirements

### Deterministic fixture and assertion matrix

Construct two shops with a shared sender WABA/phone and independent recoveries for the same customer phone. Use exact stored items:

- Shopify A: `(productId=shoes, variantId=size-10, quantity=2, title=Blue Trainers, variantTitle=Size 10)` and `(productId=shirt, quantity=1, title=White T-shirt)`.
- WooCommerce B: `(productId=bag, quantity=1, title=Canvas Bag)` and `(productId=bottle, quantity=3, title=Water Bottle)`.
- One long basket with five well-formed distinct lines, proving first three entries and exact `+2` remainder; one empty basket; one malicious/invalid title; one wrong-shop items projection.

Use the actual accepted recovery fixture builders and their line-item JSON shape; the above labels are logical test facts, not a substitute for valid repository fixture fields. Include frozen approved 20-language template fixtures with explicit approved content hashes, real `parameterBindingsSnapshot` and Meta `BODY` placeholder sequence; mock only the external Meta API/approval and R2 edges. Do not fabricate approval states inside production code.

| Test | Expected result |
|---|---|
| Both platforms, INITIAL NO_OFFER TEXT | Actual saved basket in BODY exactly once; merchant name and Reply guidance retained |
| Both platforms, INITIAL checkout single CODE | Original items and approved singleton offer at distinct frozen BODY positions |
| Both platforms, INITIAL checkout 2–3 CODE and AUTOMATIC | Original items and truthful approved plural/automatic offer copy; no duplicate basket variable |
| Both platforms, INITIAL ALTERNATIVE_PRODUCT | Original basket distinct from recommended different product, approved checkout CTA remains |
| Approved INITIAL IMAGE header | Standardised product image header plus unchanged original basket in BODY |
| IMAGE unavailable with approved TEXT fallback | TEXT still contains the saved basket; cannot choose missing-summary fallback |
| Missing/duplicate BODY semantic, HEADER-only imitation, wrong position, altered frozen fingerprint | Fail closed before Meta send; no recovery credit committed |
| Missing/empty/malformed/wrong-shop items | Typed `BINDING_VALUE_UNAVAILABLE`/no-send; no other merchant's products substituted |
| Locale and translation matrix (20 supported locales) | Frozen parameter position and meaning preserved, localized item formatting and `+N` marker for long basket |
| Checkout generation change between preparation and dispatch | Existing BG008 stale admission prevents sending old basket content |
| Retry, duplicate event, concurrent worker delivery | At most one provider-confirmed message/charge, original frozen basket binding preserved |
| FOLLOW_UP historical template without basket | Existing behaviour unchanged; human replies unaffected |

### Evidence and limits

- Assert the exact Meta request component order and template registration identity from the immutable frozen snapshot; do **not** infer success merely from a rendered preview or an Admin AST.
- Assert `BODY` parameter count matches approved registration and `checkout.itemsSummary` occupies the expected 1-based frozen binding index. Assert the value corresponds to the authentic recovery's saved line items, not the alternative product, and that no raw customer PII, coupon codes or checkout URLs appear in logs.
- Simulate Meta provider errors with real originating message/code and verify shared-logger diagnostics preserve them safely. Provider approval is an external gate; test approval/denial snapshots without claiming live Meta approvals.
- Use disposable PostgreSQL and Redis/BullMQ with worker retries and close all resources. Observe both Shopify and WooCommerce, not mock-only unit tests. The system test must run **after** all dependencies are accepted.

## Work Items

- [ ] Add deterministic cross-platform fixed checkout fixtures and approved initial TEXT/IMAGE registration fixtures.
- [ ] Execute the full offer/header/locale/target matrix and compare approved BODY positions with actual Meta requests.
- [ ] Exercise negative/cross-shop/old revision/retry cases and assert no Meta send or credit on invalid content.
- [ ] Record PostgreSQL, Redis, Meta fake and all service cleanup/evidence in system-test Completion Report.

## Interfaces / Contracts

Existing `checkout.itemsSummary` semantic in `@modainteract/moda-interact-shared/recovery-template-bindings`, `CheckoutRecovery.lineItems`, frozen Meta `parameterBindingsSnapshot.body` / `componentsSnapshot`, BG017 local verified position witness and the existing confirmed `ConversationMessage` / `RecoveryOutreachAttempt` association. No new wire API. Input fixtures use current provider-neutral source IDs and shop-scoped `CheckoutRecovery` records.

## Dependencies

- `ARCH-052-ADMIN-004`
- `ARCH-052-BACKGROUND-017`
- `ARCH-052-BACKGROUND-008`
- `ARCH-052-BACKGROUND-007`
- `ARCH-052-BACKGROUND-005`

## Enables

None. This is terminal system validation; no implementation or publication task depends on it.

## Acceptance Criteria

- [ ] Every tested INITIAL provider-approved variant from both platforms sends the correct original checkout-item summary once, while preserving checkout CTA, merchant identity, Reply instruction and offer provenance.
- [ ] IMAGE/locale/no-offer/alternative-product fallback cannot bypass checkout items. All invalid/legacy states fail closed with no unsafe send or credit.
- [ ] Same-phone two-merchant isolation, retries, concurrency fencing and final checkout-generation admission remain correct.
- [ ] All 20 supported locales preserve correct frozen semantic and reviewed localized body labels; historical FOLLOW_UP behaviour is unchanged.
- [ ] System environment and container cleanup plus original-provider error fidelity are documented.

## Validation

- [ ] Run repository-defined `ARCH-052` system-test CLI/scenarios in disposable local PostgreSQL and Redis with both platform fixtures; record exact commands and versions.
- [ ] Verify both positive and negative variant matrix, independent Meta request assertions, durable receipt/billing and dead-letter/retry handling.
- [ ] Run changed-file lint/typecheck and `git diff --check`; record any unavailable integration prerequisite as blocked rather than marking tests passed.

## Stop Condition

After the required integrated validation is complete, update this task's Work Items, Completion Report and `status: review`, return to architect and **STOP**. Do not edit parent architecture or other task statuses as system-test owner.

## Implementation Notes

Reuse `moda-interact-system-test` modular executor/fixture/assertion/helper structure; no monolithic 300+ line files. No real external Meta send or checkout mutation. Honour canonical worktrees, tenant isolation and exact provider diagnostics. Do not create a second release/queue/commerce agent.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

Approved registration fixtures model immutable provider-reviewed initial revisions without claiming live provider approval.

### Unresolved Issues

None known at definition time.

### Architectural Concerns

None at definition time.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting integrated test implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not yet assessed.

### Follow-up

None.
