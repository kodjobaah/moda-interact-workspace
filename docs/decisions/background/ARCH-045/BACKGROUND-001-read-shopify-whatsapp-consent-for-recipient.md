---
id: ARCH-045-BACKGROUND-001
architecture_id: ARCH-045
title: Synchronise and evaluate current Shopify phone consent
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-045-DATABASE-002
enables:
  - ARCH-045-BACKGROUND-002
  - ARCH-045-BACKGROUND-003
  - ARCH-045-BACKGROUND-004
  - ARCH-045-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-21
---
# Synchronise and evaluate current Shopify phone consent

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** portable definition, **not** materialised in a developer task worktree or committed/pushed; no execution claim exists.

## Objective

Provide a small injected Shopify authority reader plus `CustomerPhone` current-state synchroniser for a verified shop customer and **exact active recipient phone**, consumed by normal reconciliation and consent-sync events.

## Context

Shopify remains source of truth; the newly shared `CustomerPhone` fields (ARCH-045-DATABASE-002) are the local current-state projection that normal checkout reconciliation reads. The snapshot has no such fields today. A local grant must never bypass an unavailable or negative fresh provider check at the irreversible send boundary.

## Scope

- Implement an injectable Shopify GraphQL current-consent reader accepting `{shopId,shopifyCustomerId,recipient?}` with bounded timeout and typed allowed/not-authorised/unavailable outcomes; verify actual API-version path and exact default phone/recipient.
- Resolve a verified existing shop-owned `Customer` and its exact active `CustomerPhone` using canonical phone, never by phone-only identity. For such a verified Customer, safely create/rotate the active phone row if Shopify reports a newly verified default number; do not create a Customer from phone alone. Refresh current phone state from Shopify `whatsAppMarketingConsent` with monotonic source timestamps; unknown/non-subscribed/revoked is not a grant.
- Support **normal candidate/reconciliation** reads from current CustomerPhone and initial provider refresh when local state is missing/uncertain; sync-event consumer BACKGROUND-003 can call the same sync operation without creating a checkout.
- Ensure a final fresh Shopify authority check before irreversible proactive provider dispatch so webhook latency/out-of-order updates cannot permit a revoked number. If shop/customer/phone linkage is not safe, fail closed and do not create a guest/customer via phone alone.
- Test grant/revoke, unknown, missing customer, changed number, duplicate/older provider observation, source error, tenant match and injectability; use Shared structured logging with no PII.

## Out of Scope

- No checkout materialisation/merchant notice logic (BACKGROUND-002), no webhook transport/queue worker (BACKGROUND-003), no evidence table or consent-triggered checkout scan.

## Requirements

- [ ] Current local consent is scoped to exact customer and phone and cannot be overwritten by an older provider observation.
- [ ] Missing/unknown/non-SUBSCRIBED, mismatched or unavailable consent fails closed; source-of-truth remains Shopify.
- [ ] First authoritative read can seed current phone state when a new customer is encountered in normal reconciliation; no Shopify customer is invented from phone alone.

## Work Items

- [ ] Define typed injected read/sync interface and Shopify provider adapter.
- [ ] Write checked current phone state via new Database-002 fields, with safe provider ordering.
- [ ] Test local selection/provider refresh, provider failure, recipient change, and pre-send validation.

## Interfaces / Contracts

Depends on `ARCH-045-DATABASE-002` `CustomerPhone` schema. Background-local `readCurrent({shopId,shopifyCustomerId,recipient})` / `syncCustomer({shopId,shopifyCustomerId})` or equivalent injected port; `ARCH-045-BACKGROUND-003` consumes sync without recovery lookup; `BACKGROUND-002/004` use current state with live provider safety fence. No new cross-service API.

## Dependencies

- `ARCH-045-DATABASE-002`

## Enables

- `ARCH-045-BACKGROUND-002`
- `ARCH-045-BACKGROUND-003`
- `ARCH-045-BACKGROUND-004`
- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Exact customer/active phone native `SUBSCRIBED` state is projected to CustomerPhone with correct source time; negative state clears eligibility.
- [ ] Unknown, mismatched and API unavailable cannot grant outreach; changed phone never inherits old grant.
- [ ] Provider revalidation at outbound boundary is possible through the injected reader; Shopify state remains authoritative.

## Validation

- [ ] Focused Shopify GraphQL provider, CurrentPhone synchronization, stale/duplicate, tenant/recipient and failure unit/integration tests, repository-declared build and `git diff --check`.

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
