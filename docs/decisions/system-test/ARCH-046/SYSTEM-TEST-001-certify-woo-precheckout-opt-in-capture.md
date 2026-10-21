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
  - ARCH-045-DATABASE-002
  - ARCH-046-API-001
  - ARCH-046-WOOCOMMERCE-001
  - ARCH-046-WOOCOMMERCE-002
  - ARCH-046-WOOCOMMERCE-003
  - ARCH-045-SHARED-002
  - ARCH-045-BACKGROUND-005
  - ARCH-046-API-005
  - ARCH-046-WOOCOMMERCE-007
enables: []
created: 2026-10-20
updated: 2026-10-21
---

# Certify Woo pre-submission WhatsApp consent capture on LocalWP

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

**System test is terminal:** No implementation task depends on this task. Execute only after its own implementation dependencies are accepted and the developer has an opportunity for manual LocalWP validation.

## Objective

Black-box certify Woo Classic/Blocks **consent-only capture**: verified changes update common CustomerPhone plus one immutable evidence fact, without a recovery scheduler or consent-event processing backlog.

## Context

The current Woo integration is ARCH-035 capture-only. Consent is stored on CustomerPhone and authenticated installation identity on WooCommerceInstallation; the one minimal evidence record must prove explicit opt-in before order placement.

## Scope

- Run connected LocalWP Classic and Blocks for guest/account customers, pre-submit grant, revoke, later grant and abandon-before-order scenarios. Check shared CustomerPhone current decision and **one append-only evidence fact per accepted change**, accurate disclosure/version and exactly one idempotent event retry.
- Verify default unknown with one initially unchecked Moda checkbox when installed/connected and recovery-enabled; no checkbox when disabled/deactivated/disconnected, no grant from an already-open stale page after disabling recovery, and no selectable external-provider mode.
- Test guest identity, phone change, same account across verified checkouts, out-of-order replay, API outage while checkout continues, 20 locales and HPOS. No 72-hour consent expiry.
- Assert **zero CheckoutRecovery rows, provider sends, recovery credits, BullMQ consent-driven jobs or evidence processing/claim/ack fields** during capture-only rollout. Consent history is audit only, not a worklist.

- **C1/C2/C4/C5/C6:** Add merchant-scoped Customer/CustomerPhone canonical-phone matching through hosted API and normal capture envelope, UK national vs +44 numbers, one/no/multiple matches within a shop, cross-shop reuse, stale guest checkbox attempts/reinstall, replayed/stale decisions, local STOP/admin off-channel opt-out and evidence history after withdrawal.
- **H3/H4:** Prove actual Classic and Blocks pre-submit ordering: ACK→later checkout event vs checkout event before ACK, lost ACK/retry, checkbox unchecked, Action Scheduler retry and no later event (no recovery).

## Out of Scope

- No approval to create Woo recovery, send WhatsApp or run still-blocked Background-002/003/004.

## Requirements

- [ ] Real WP checkout plugins/API/PostgreSQL observed, not only checkbox DOM test; secrets/customer PII redacted.
- [ ] Missing LocalWP/Docker capability explicitly reported as incomplete, not PASS.

## Work Items

- [ ] Build separated realistic Classic/Blocks fixtures, executors, DB and consent assertions.
- [ ] Run customer/phone grant/revoke/installation lifecycle/no-recovery and regression tests.
- [ ] Record LocalWP, API, DB evidence and skipped constraints.

## Interfaces / Contracts

Consolidated ARCH-045-DATABASE-002 (CustomerPhone, active WooInstallation and `commerce.WhatsAppConsentEvidence` audit), API-001 and WOOCOMMERCE-001/002/003. No Shopify sync queue, evidence worklist or recovery wakeup.

## Dependencies

- `ARCH-045-DATABASE-002`
- `ARCH-046-API-001`
- `ARCH-046-WOOCOMMERCE-001`
- `ARCH-046-WOOCOMMERCE-002`
- `ARCH-046-WOOCOMMERCE-003`
- `ARCH-045-SHARED-002`
- `ARCH-045-BACKGROUND-005`
- `ARCH-046-API-005`
- `ARCH-046-WOOCOMMERCE-007`

## Enables

None

## Acceptance Criteria

- [ ] Current phone/source is on existing CustomerPhone/installation; exactly one `commerce.WhatsAppConsentEvidence` audit table and no worklist.
- [ ] Actual Classic/Blocks secure consent decisions before order and later withdrawal are proven on real WP/API/PostgreSQL.
- [ ] No recovery, credit, outbound provider send, consent-driven queue or scheduled checkout recheck in the capture-only phase.

- [ ] Existing Customer/CustomerPhone may be resolved by one unambiguous merchant-scoped canonical phone, while a grant still requires an authenticated deliberate checkbox action; ambiguous matches, stale sender permission and consent-driven recovery jobs are rejected.

## Validation

- [ ] LocalWP/real PostgreSQL Classic/Blocks/system-test evidence with merchant-scoped matching, guest/installation/idempotency assertions and `git diff --check`; missing runtime dependencies recorded as incomplete.

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
