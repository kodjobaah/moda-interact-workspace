---
id: ARCH-045-BACKGROUND-001
architecture_id: ARCH-045
title: Read current Shopify WhatsApp consent for the exact recipient
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-045-BACKGROUND-002
  - ARCH-045-BACKGROUND-004
  - ARCH-045-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-20
---
# Read current Shopify WhatsApp consent for the exact recipient

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** portable definition, **not** materialised in a developer task worktree or committed/pushed; no execution claim exists.

## Objective

Provide an injectable read-only Shopify WhatsApp marketing-consent evaluator for the exact outbound recovery recipient.

## Context

Current Background Shopify offline-token and Admin GraphQL clients exist; neither recovery initiation nor follow-up currently checks `Customer.defaultPhoneNumber.whatsAppMarketingConsent`.

## Scope

- Implement a small injected `WhatsAppRecoveryConsentReader` (or repository-conformant equivalent) accepting `{shopId, shopifyCustomerId, recipient}` and returning typed `allowed`, `not-authorised`, `verification-unavailable`.
- Use the installed shop offline session and Shopify Admin GraphQL 2026-07+ `Customer.defaultPhoneNumber {phoneNumber whatsAppMarketingConsent {state updatedAt}}`; verify exact schema on selected API version.
- Normalise both current Shopify phone and proposed recipient with existing recipient canonicalisation; validate `customer(id:)` matches the intended Shopify customer and shop.
- Use bounded network timeout, retry classification and shared structured logger without phone/secret/customer payload in logs.

## Out of Scope

- No call to `customerWhatsAppMarketingConsentUpdate`, `setTrackingConsent`, Customer Privacy API or Shopify storefront code.
- No persisted local consent Boolean or phone-only fallback.
- No recovery lifecycle/messaging/billing mutation.

## Requirements

- [ ] Only **current** `SUBSCRIBED` for matching customer and exact canonical default phone is `allowed`.
- [ ] Missing Shopify ID, mismatched phone, absent customer/default phone, `UNSUBSCRIBED`, `PENDING`, `NEVER_SUBSCRIBED`, `REDACTED`, unknown state are `not-authorised`.
- [ ] API/session/permission/timeouts are `verification-unavailable`, **never** allowed.
- [ ] API credentials never enter log events; injection supports real-provider boundary tests and deterministic unit tests.

## Work Items

- [ ] Implement small read-only adapter and explicit policy interface.
- [ ] Write tests for each Shopify state, phone/customer/shop mismatch and provider failure.
- [ ] Validate logger usage and timeout bounds.

## Interfaces / Contracts

Background-local injectable `check({shopId,shopifyCustomerId,recipient})`; no cross-repository contract. Reads Shopify API requiring existing `read_customers` scope. Returns `{kind:"allowed"}|{kind:"not-authorised",reason}|{kind:"verification-unavailable",reason}` or an equivalent exhaustive discriminated union.

## Dependencies

None

## Enables

- `ARCH-045-BACKGROUND-002`
- `ARCH-045-BACKGROUND-004`
- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Subscribed exact identity/number passes; all other states/identities fail closed.
- [ ] Provider errors are distinguishable from explicit lack of consent; retry does not grant permission.
- [ ] No Shopify mutation, persisted consent cache or sensitive logging.

## Validation

- [ ] Focused mocked Shopify Admin GraphQL contract/timeout tests and repository-declared build/typecheck; `git diff --check`.

## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. For publication task, do not rerun implementation validation.

## Implementation Notes

Exact Shopify customer GID must be constructed only from a validated shop-linked customer identifier. Do not use a recovery phone number to search for another customer. Keep this shared across Background admission paths by dependency injection, not copy-pasted GraphQL calls.

Before claiming, use the deterministic `/moda-task` launcher and its **actual** prepared packet, read the task's complete current Architect Review, and verify task/dependency status in the developer's canonical workspace. Preserve `docs/decisions/**/_index.md` untouched until the developer explicitly closes the architecture documentation session. New runtime structured logging uses `@modainteract/moda-interact-shared/logging` where applicable. No source outside this task's owner repository may be changed unless explicitly authorised by the architecture.

## Completion Report

### Status

Not Started — external portable definition, not materialised.

### Files Changed

None — not implemented.

### Work Completed

None.

### Validation Results

Not run; the supplied snapshot is not the developer's task worktree.

### Deviations

None.

### Assumptions

Use the 2026-10-20 snapshot for orientation; revalidate active code/configuration when the task is materially claimed. ARCH-045 does not impose a consent-expiry window; current Shopify consent and actual checkout eligibility are separate.

### Unresolved Issues

None recorded at definition time; report any discovered cross-repository dependency rather than implementing outside ownership.

### Architectural Concerns

None recorded at definition time.

## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

None.

### Reviewed Files

None — portable definition only.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
