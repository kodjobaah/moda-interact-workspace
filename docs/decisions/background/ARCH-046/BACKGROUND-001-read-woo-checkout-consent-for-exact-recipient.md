---
id: ARCH-046-BACKGROUND-001
architecture_id: ARCH-046
title: Read current Woo customer-phone consent for exact recipient
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 27
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-046-DATABASE-001
enables:
  - ARCH-046-BACKGROUND-002
  - ARCH-046-BACKGROUND-004
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-20
---

# Read current Woo customer-phone consent for exact recipient

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

## Objective

Provide one injectable, fail-closed Woo recovery-consent reader for **verified customer + exact phone + purpose**, combining existing `CustomerPhone` state with the current Woo installation source/epoch.

## Context

Shopify ARCH-045 uses Shopify native consent. Woo's consent authority is hosted CustomerPhone for an authenticated Woo customer/guest identity, not a checkout-scoped consent projection. This reader can be implemented while ARCH-035 remains capture-only.

## Scope

- Implement injectable typed `WooCheckoutRecoveryConsentReader` (name may be retained for compatibility) accepting `{shopId,verifiedCustomerId,recipient,purpose}` plus checkout identity only for safe ownership/context assertions; return `allowed|not-authorised|verification-unavailable`.
- Read current `WooCommerceInstallation` mode/provider/epoch and matching active `CustomerPhone` decision for that **shop-owned customer** and exact canonical recipient. Permit only explicit current GRANTED for `WHATSAPP_CHECKOUT_RECOVERY` with current source/provider/epoch and valid disclosure scope. Unknown, revoked, changed phone, mode disabled, unapproved external source or identity mismatch fail closed; DB errors are unavailable.
- Do not accept or look up consent by phone alone, nor require the consent evidence collection checkout to equal the current checkout if the accepted disclosure authorises future checkout reminders for the same verified customer/phone. Re-read near provider dispatch; no stale allowed cache.

## Out of Scope

- No duplicate Woo consent projection, Shopify GraphQL, Woo recovery engine, customer identity invention, send/billing effect or Shared queue contract.

## Requirements

- [ ] Verified customer/shop and exact canonical phone are mandatory; no guest phone-only correlation.
- [ ] Current mode/provider/epoch and revocation are checked before any authorised outbound message.

## Work Items

- [ ] Implement small injected current CustomerPhone/source reader.
- [ ] Test reused consent for another verified checkout, guest mismatch, phone change, revoke, epoch change, unavailable DB and no side effects.

## Interfaces / Contracts

Consumes DATABASE-001 CustomerPhone current consent and WooCommerceInstallation source fields; Background-local typed policy, no new cross-repository contract.

## Dependencies

- `ARCH-046-DATABASE-001`

## Enables

- `ARCH-046-BACKGROUND-002`
- `ARCH-046-BACKGROUND-004`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Correct customer and phone grant (current source/epoch) passes; another customer/number or revoked/unknown/source mismatch does not.
- [ ] No recovery/credit/provider side effects or unsafe cached permission.

## Validation

- [ ] Focused Background unit + disposable PostgreSQL consent reader tests; repository-declared build/typecheck and `git diff --check`.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

This task is safe to implement before a Woo recovery engine exists; do not include admission integration here.

Before any implementation, use `/moda-task` deterministic preparation against the **developer's actual** primary workspace, read the latest task/Architect Review, the parent architecture, relevant agent instructions, and the repository's real `package.json` scripts. Do not invent environment variables or claim a completed checkout/recovery source from the snapshot. Do not modify another repository, architecture-wide docs or `docs/decisions/**/_index.md` in a repository task. Use `@modainteract/moda-interact-shared/logging` for Node server diagnostics; PHP uses WordPress-specific safe diagnostics. Preserve official user/merchant i18n and tenant boundaries.

## Completion Report

### Status

Not Started — portable, not materialised.

### Files Changed

None — no runtime implementation in this documentation patch.

### Work Completed

None.

### Validation Results

Not run by a repository agent; no developer worktree/remote access is available from this snapshot.

### Deviations

None.

### Assumptions

Source is the supplied 2026-10-20 snapshot, not necessarily latest developer worktree. Versioned APIs/schema and future Woo recovery capability must be verified when eligible. Consent has no Moda-imposed waiting/expiry period. Recheck the current customer-phone permission and independently applicable checkout validity; do not invent a retention deadline.

### Unresolved Issues

None recorded at definition time; raise actual missing cross-repository contract/rollout dependencies to moda_architect before scope drift.

### Architectural Concerns

None recorded beyond explicit context and gates.

## Architect Review

### Review Status

Pending — no implementation reviewed or accepted.

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
