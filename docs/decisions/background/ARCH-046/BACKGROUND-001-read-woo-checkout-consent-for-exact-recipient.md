---
id: ARCH-046-BACKGROUND-001
architecture_id: ARCH-046
title: Read durable Woo checkout consent for exact proactive recipient
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

# Read durable Woo checkout consent for exact proactive recipient

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

## Objective

Provide a small injectable Background policy that returns consent allowed/not-authorised/unavailable based on current **hosted source configuration** plus matching Woo checkout/recipient evidence.

## Context

Shopify ARCH-045 reads Shopify Admin GraphQL. Woo uses an unrelated source and requires a distinct adapter. This pure read can be built without enabling recovery sends.

## Scope

- Implement typed `WooCheckoutRecoveryConsentReader` with `{shopId,checkoutKey,recipient,purpose}` and three-way outcome `allowed|not-authorised|verification-unavailable` over **shop source configuration plus** canonical Prisma consent projection.
- Permit only current decision GRANTED for exact key **and current hosted mode/provider/configurationEpoch**. Unconfigured/disabled, unsupported external adapter, revoked, former epoch or mismatched recipient are not authorised. DB failures are unavailable and fail closed.
- Use the same existing canonical outbound-recipient normalization as recovery where possible; test format equivalence to API-001.
- Keep dependency injectable/testable and logging through shared Node logger, bounded semantic fields only.

## Out of Scope

- No Shopify GraphQL dependency, Woo WordPress REST calls, new checkout engine, webhook consumer or sends.
- No duplicate opt-in evidence table, Shared queue contract or generic logger.
- No inference of consent from phone, order metadata, email checkbox or CMP.

## Requirements

- No `shopId` or checkout identity fallback to phone-only.
- A DB exception never becomes allowed or a revocation guess.
- Do not cache positive grants or source configuration across send boundaries; both current config and consent must be re-read when actual provider admission is approved.

## Work Items

- [ ] Implement injected current-state reader and explicit typed outcomes.
- [ ] Test exact shop/checkout/recipient/purpose, active source+epoch, NOT_CONFIGURED, Moda→external/off→Moda switches, unknown provider, revoked/none, DB error, canonical phone mismatch.
- [ ] Provide usage contract to blocked BACKGROUND-002/003/004.

## Interfaces / Contracts

Consumes Database-001 Prisma source configuration and exact-recipient projection directly. Background-local adapter, not a cross-service Shared transport schema.

## Dependencies

- `ARCH-046-DATABASE-001`

## Enables

- `ARCH-046-BACKGROUND-002`
- `ARCH-046-BACKGROUND-004`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Only same authenticated shop + Woo checkoutKey + exact recipient + purpose + current GRANTED **stamped with active mode/provider/epoch** returns allowed.
- [ ] All other cases fail closed and no Shopify source is consulted.
- [ ] No recovery/credit/provider send side effects introduced.

## Validation

- [ ] Focused Background unit tests and disposable PostgreSQL reader integration; typecheck/repository declared build and `git diff --check`.

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

Source is the supplied 2026-10-20 snapshot, not necessarily latest developer worktree. Versioned APIs/schema and future Woo recovery capability must be verified when eligible. Fixed provisional 72-hour consent wait from `detectedAt`, always shortened by actual earlier Woo checkout expiration/paid-order state.

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
