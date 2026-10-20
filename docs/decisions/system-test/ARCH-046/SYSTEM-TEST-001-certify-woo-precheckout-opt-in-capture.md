---
id: ARCH-046-SYSTEM-TEST-001
architecture_id: ARCH-046
title: Certify Woo pre-submission WhatsApp consent capture on LocalWP
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-046-DATABASE-001
  - ARCH-046-API-001
  - ARCH-046-WOOCOMMERCE-001
  - ARCH-046-WOOCOMMERCE-002
  - ARCH-046-WOOCOMMERCE-003
enables: []
created: 2026-10-20
updated: 2026-10-20
---

# Certify Woo pre-submission WhatsApp consent capture on LocalWP

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

**System test is terminal:** No implementation task depends on this task. Execute only after its own implementation dependencies are accepted and the developer has an opportunity for manual LocalWP validation.

## Objective

Black-box certify the independently complete Woo opt-in phase using real LocalWP Classic/Blocks before any Woo recovery engine is enabled.

## Context

The opt-in collection path can be tested before the blocked recovery phase and must prove **abandoned** checkout consent persists; a clicked checkbox or completed order alone is not sufficient.

## Scope

- Launch real disposable LocalWP/Woo Classic and Blocks checkouts (guest and logged in), connected to isolated hosted API/PostgreSQL; manually abandon before placing order and verify durable grant/evidence.
- Verify required optional unchecked field, exact phone/checkoutKey, phone change, revoke, re-enter same checkout and explicit later grant, queue/retry identity, API outage/recovery, checkout non-blocking and HPOS/order regression.
- Prove zero CheckoutRecovery materialisation, WhatsApp sends or credit debits in this phase; document consent acceptance events and source revisions with redacted evidence.

## Out of Scope

- No requirement to send a WhatsApp recovery or complete ARCH-046-BACKGROUND-002/003/004.
- No enabling of the ARCH-035 recovery flow or coupling this system test as a dependency of implementation tasks.

## Requirements

- Only run after dependencies are Complete and architect-accepted; developer may first manually validate LocalWP.
- Use disposable credentials/database and isolate production; no real customer phone/WhatsApp template.
- Test actual persisted pre-submission evidence, not only form snapshots or fixture acceptance.

## Work Items

- [ ] Build isolated LocalWP Classic/Blocks/HPOS fixture with connected test API.
- [ ] Execute positive, negative, retry, revoke, phone-change, return and cross-shop scenarios.
- [ ] Record machine-readable redacted evidence and release decision without modifying production.

## Interfaces / Contracts

End-to-end PHP→API `woo.whatsapp-consent.v1`→PostgreSQL current/event records; captures truth of phase 1 only.

## Dependencies

- `ARCH-046-DATABASE-001`
- `ARCH-046-API-001`
- `ARCH-046-WOOCOMMERCE-001`
- `ARCH-046-WOOCOMMERCE-002`
- `ARCH-046-WOOCOMMERCE-003`

## Enables

None

## Acceptance Criteria

- [ ] Consent stored before order placement for guest and account in Classic/Blocks.
- [ ] Revocation/late retry/phone change never allow stale or mismatched grant.
- [ ] API outage cannot block checkout or produce fake consent.
- [ ] No Woo recovery/send/billing side effects occur in capture-only phase.

## Validation

- [ ] Repeatable LocalWP real browser/WP, hosted API and disposable PostgreSQL black-box evidence.
- [ ] Verify plugin ZIP/locale/HPOS regression and negative scenarios.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

Terminal **stage-one** system test. It is not a dependency of BG002/003/004; further implementation proceeds only by architect-approved external recovery-lifecycle prerequisites, not by test completion.

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
