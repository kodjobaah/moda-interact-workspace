---
id: ARCH-001-BACKGROUND-003
architecture_id: ARCH-001
title: Implement Shopify abandoned checkout lookup
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-001-BACKGROUND-001"]
enables: ["ARCH-001-BACKGROUND-004", "ARCH-001-BACKGROUND-006"]
created: 2026-08-28
updated: 2026-08-28
---

# Implement Shopify Abandoned Checkout Lookup

## Architecture

Architecture ID:

ARCH-001

Architecture document:

docs/architecture/ARCH-001-shopify-checkout-recovery-webhook-processing.md

Coordinator:

moda_architect

## Objective

Implement the Shopify API/GraphQL lookup used to retrieve the authoritative current checkout state when recovery data is required.

## Context

ARCH-001 deliberately does not retain basket/customer state in the pending candidate. The background service must retrieve current Shopify data when a candidate matures and when an existing recovery needs to be refreshed.

## Scope

- Verify the exact supported Shopify API/GraphQL query for locating the abandoned checkout.
- Use the existing Shopify offline-session/access-token service.
- Accept the ARCH-001 lookup identifiers:
  - shop identity/domain;
  - checkout token;
  - cart token;
  - abandoned checkout URL;
  - checkout creation timestamp.
- Return a normalized internal result containing the current data needed by `CheckoutRecovery`.
- Distinguish:
  - found and recoverable/current;
  - not found/no longer recoverable;
  - transient Shopify failure;
  - invalid/ambiguous lookup.
- Add unit/integration tests with representative Shopify responses.
- Do not log access tokens or unnecessary customer data.

## Out of Scope

- Creating/updating `CheckoutRecovery`.
- Candidate scheduling/cancellation.
- WhatsApp sending.
- Order processing.
- Changing candidate fields or database schema without architect review.

## Requirements

Do not assume Shopify supports filtering by `checkoutToken` unless verified.

The lookup must avoid unbounded listing/scanning of a merchant's abandoned checkouts.

The normalized result should provide, where available and required by the current recovery model:
- customer identity/contact fields;
- line items;
- totals/currency;
- abandoned/recovery URL;
- completion/recoverability state.

Transient Shopify failures must throw/retry rather than be treated as 'not recoverable'.

If no deterministic/bounded lookup can be implemented from the approved identifiers, set this task to `blocked` and report the missing identifier/schema requirement to `moda_architect`.

## Work Items

- [ ] Verify the Shopify API/GraphQL lookup mechanism against the configured API version.
- [ ] Add a typed abandoned-checkout lookup input/output.
- [ ] Implement authenticated GraphQL/API request.
- [ ] Normalize current checkout data for recovery use.
- [ ] Separate not-found/not-recoverable from provider failure.
- [ ] Add tests for success, not found, completed/non-recoverable, GraphQL error and HTTP error.
- [ ] Ensure logs do not expose Shopify credentials or unnecessary customer payload.

## Interfaces / Contracts

Consumes:

- Shopify offline session/access token.
- Candidate/recovery identifiers defined by ARCH-001.

Produces:

Repository-local normalized abandoned-checkout result.

No new cross-repository contract is introduced.

## Dependencies

- ARCH-001-BACKGROUND-001

## Enables

- ARCH-001-BACKGROUND-004
- ARCH-001-BACKGROUND-006

## Acceptance Criteria

- [ ] Lookup is deterministic or bounded; it does not enumerate an unbounded abandoned-checkout history.
- [ ] Current Shopify data, not webhook basket data, is returned.
- [ ] Completed/not-recoverable checkout is distinguishable from provider failure.
- [ ] Transient Shopify failures are retryable.
- [ ] Access tokens are not logged.
- [ ] Tests cover the verified Shopify response shape.
- [ ] If deterministic lookup is impossible, task is returned Blocked rather than implementing a heuristic.

## Validation

- [ ] `npm test`
- [ ] `npm run test:shopify` where environment permits
- [ ] `npm run build`

## Implementation Notes

Reuse the existing Shopify access-token/session service.

Do not use customer identity alone to locate a checkout.

A real-provider integration test may be conditional on credentials; record that clearly in the Completion Report.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending review.

### Follow-up

None
