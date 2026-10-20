---
id: ARCH-046-BACKGROUND-004
architecture_id: ARCH-046
title: Gate Woo proactive follow-ups on current WhatsApp consent
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: blocked
priority: 38
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-046-BACKGROUND-001
  - ARCH-046-BACKGROUND-002
enables:
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-20
---

# Gate Woo proactive follow-ups on current WhatsApp consent

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

**Execution gate:** This task is intentionally `blocked` pending a separately approved Woo recovery lifecycle/live checkout-state contract, and must **not** be claimed merely because its enumerated task dependencies become Complete.

## Objective

Apply one current Woo consent policy to every approved proactive Woo recovery follow-up or merchant post-window template without prematurely charging or burning the follow-up slot.

## Context

The existing proactive follow-up processors are attached to Shopify recovery. A real Woo follow-up path does not yet have an approved implementation/checkout-state reader, so this task is BLOCKED.

## Scope

- Locate every future approved Woo business-initiated sequence-two and merchant post-window recovery template path, inject BACKGROUND-001 exact-checkout/recipient consent policy immediately before attempt/billing and again near irreversible provider handoff.
- Fail closed after revocation, **merchant source-mode/provider/epoch switch**, recipient or checkout changes; preserve existing recipient suppression, Meta window constraints, human moderation and `ARCH-040` handover.
- Release/correct a provisional credit reservation when later consent check fails before provider send, without a false SENT state or consumption of the one allowed sequence-two slot.

## Out of Scope

- No changes to ordinary legitimate customer-initiated 24h service-window replies.
- No Woo follow-up engine or chat UI implementation; no Shopify consent queries in Woo.
- No duplicate shared policy/reader implementation.

## Requirements

- **Execution gate:** wait for approved Woo recovery and follow-up template lifecycle, not just capture-only activities.
- Consent must match currently selected recipient/checkout/purpose; no merchant override.
- No credit or follow-up slot burned on denied/unavailable pre-send check.

## Work Items

- [ ] Record approved Woo follow-up source/contract and implement one injected consent policy at every proactive send entry.
- [ ] Test revoked-after-scheduling, merchant source-switch after scheduling, and after-provisional-credit-before-provider races.
- [ ] Prove human/customer-service replies are not incorrectly blocked by marketing check.

## Interfaces / Contracts

Uses BACKGROUND-001 reader and approved Woo proactive send boundary; no Shared contract or new database model.

## Dependencies

- `ARCH-046-BACKGROUND-001`
- `ARCH-046-BACKGROUND-002`

## Enables

- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Revoked/unknown consent prevents proactive follow-up and post-window merchant template and consumes no credit.
- [ ] Previously valid consent revalidated immediately before provider handoff; no duplicate sequence-two slot.
- [ ] Customer-service reply workflow retains existing authorised rules.

## Validation

- [ ] Focused Woo follow-up credit/provider and concurrency tests on approved source; `git diff --check`.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

This is a separate task because first outreach and scheduled/manual proactive follow-ups have distinct send/admission paths and failure modes.

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

External approved Woo recovery lifecycle/live checkout-state reader and independently accepted send/billing admission are currently missing; task remains Blocked.

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
