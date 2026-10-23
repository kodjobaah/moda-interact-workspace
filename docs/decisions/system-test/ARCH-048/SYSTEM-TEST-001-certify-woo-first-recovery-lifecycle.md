---
id: ARCH-048-SYSTEM-TEST-001
architecture_id: ARCH-048
title: Certify outbound-only Woo checkout recovery, state reconciliation and billing
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 75
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-048-WOOCOMMERCE-002
- ARCH-048-WOOCOMMERCE-003
- ARCH-048-BACKGROUND-001
- ARCH-048-BACKGROUND-002
- ARCH-048-BACKGROUND-003
- ARCH-048-BACKGROUND-004
- ARCH-048-BACKGROUND-005
- ARCH-046-BACKGROUND-002
- ARCH-046-BACKGROUND-004
- ARCH-046-WOOCOMMERCE-003
- ARCH-045-BACKGROUND-005
enables: []
created: '2026-10-23'
updated: '2026-10-23'
---

# ARCH-048-SYSTEM-TEST-001 — Certify outbound-only Woo checkout recovery, state reconciliation and billing

## Architecture

Architecture ID: `ARCH-048`

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`

Coordinator: `moda_architect`

Portable **proposed** definition based on the uploaded 2026-10-23 18:50 snapshot; no branch, task worktree, implementation commit, accepted review or release is claimed. Check actual canonical task state before materialisation.

## Objective

Independently validate that Woo checkout/order hooks produce one idempotent eligible initial recovery and billed WhatsApp send, while late activity and terminal outcomes reconcile against existing durable recovery records.

## Context

This is terminal architecture validation, not implementation. The accepted v2 proposal intentionally uses no WordPress checkout-reading endpoint, no Background-to-API lookups and no guest-session validation. Verify real current consent/STOP/billing behaviour and explicitly report residual risk of never-delivered Woo events.

## Scope

- Execute real Woo Classic/Blocks/HPOS checkout→API→BullMQ→Background→PostgreSQL→billing/Meta-controlled test scenarios, proving BG005 actually wires BG001/BG002/BG003/BG004 services.
- Verify capture-worker callbacks contain only parse/delegate/acknowledge work, Woo candidate routing uses the explicit source marker, and legacy/unmarked Shopify candidate jobs retain their original materialisation path.
- Test DB row committed then initial-send enqueue interrupted: recovery from retry/outreach adapter must not miss the send permanently or generate another message/charge.
- Check no candidate + existing `CheckoutRecovery` after initial send; later checkout update does not create a second initial recovery, even though its BullMQ job is gone.
- Verify paid/cancelled/placed order after queue removal updates existing recovery and prevents follow-up/retry.
- Cover empty/refill, duplicate delivery, same-time conflicting checkout updates, out-of-order order-first events, lost/delayed job, recovery lock expiry, TTL/replay edges, 51+ items, wrong-shop key and customer identity change.
- Cover missing/revoked/ambiguous consent, STOP and Support notice dedupe, later consent alone not waking checkout, disabled/enabled rollout, Meta template rejection and each credit bucket.
- Prove no new WordPress session read route and no Background direct or proxied Woo checkout HTTP request.
- Inject an exhausted/lost paid or checkout update and explicitly record the event-only limitation; do **not** falsely assert the pipeline detected an event never delivered.
- Use separate executors, fixtures, assertions and orchestration, with reproducible evidence/Completion Report.

## Out of Scope

- No source changes to other repositories; no infrastructure/Gateway task or database schema changes; no fake green result from mocked event-only completeness.

## Requirements

- System-test terminal dependency: only execute after all implementation and ARCH-046 consent prerequisites are complete and developer manual testing is available.
- No test claims authoritative live-cart/payment verification without a provider read.
- Billing correctness must hold for actual delivered sends; an undelivered paid event is an acknowledged safety limitation pending separate approval.

## Work Items

- [ ] Create and run independently reviewable LocalWP/Woo/Redis/Postgres/Meta-controlled scenarios with HPOS and Blocks.
- [ ] Capture no-BullMQ-job existing recovery proof and later terminal reconciliation evidence.
- [ ] Record redacted results, known limitations and stop for architect review.

## Interfaces / Contracts

- Uses existing authenticated Woo event intake, Background queues, existing recovery/consent/billing tables and test fixtures.
- No new provider state query contract.

## Dependencies

- `ARCH-048-WOOCOMMERCE-002`
- `ARCH-048-WOOCOMMERCE-003`
- `ARCH-048-BACKGROUND-001`
- `ARCH-048-BACKGROUND-002`
- `ARCH-048-BACKGROUND-003`
- `ARCH-048-BACKGROUND-004`
- `ARCH-048-BACKGROUND-005`
- `ARCH-046-BACKGROUND-002`
- `ARCH-046-BACKGROUND-004`
- `ARCH-046-WOOCOMMERCE-003`
- `ARCH-045-BACKGROUND-005`

## Enables

None

## Acceptance Criteria

- [ ] BG005 provider-aware dispatch is exercised end-to-end; unmarked Shopify jobs never reach Woo admission and Woo source jobs never reach Shopify lookup.
- [ ] Crashed row-insert→enqueue retry path results in zero duplicate attempts/charges and no lost eligible first-send scheduling.
- [ ] No duplicate initial recovery or credit when checkout activity arrives after first send and delayed job deletion.
- [ ] Known terminal events correctly suppress in-flight/future outreach and update existing durable recovery even with no pending candidate.
- [ ] No external checkout session reader, API checkout-state endpoint or guest session validation is required.
- [ ] Explicit report distinguishes undelivered Woo event limitation from tests of delivered, duplicated and reordered events.

## Validation

- [ ] System-test repository suite against isolated multi-service environment; documented Woo versions and honest simulated failure boundaries.
- [ ] Repo-specific runner, scenario evidence and `git diff --check`.

## Stop Condition

After only this task's work, criteria and required validation, complete the Completion Report with the launcher-resolved dedicated parent and implementation worktree paths, isolation, start-of-attempt synchronisation and repository revision evidence. Change to `review`, return to `moda_architect` and **STOP**. Do not start dependent work. Superseded tasks must not be claimed.

## Implementation Notes

- Manual developer validation may precede Ready terminal system test, but must not be encoded as a dependency for implementation tasks.

- Use `/moda-task` preparation with the real developer workspace before code execution. Do not treat the snapshot as a Git branch; do not edit any `docs/decisions/**/_index.md` during this architecture session. Validate actual repository scripts rather than guessing commands. Respect assigned repository and task-document ownership.

## Completion Report

### Status

Not Started — proposed portable definition only.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run by repository implementer; no task worktree or Git remote is accessible in this review package.

### Deviations

None.

### Assumptions

The latest uploaded workspace ZIP is a source snapshot, not necessarily the developer's latest task branches. The developer reports `ARCH-046-BACKGROUND-004` complete after the ZIP; verify its accepted implementation for consumer integration, without reopening it.

### Unresolved Issues

None at definition time. Raise concrete cross-repository contract gaps with the architect before implementation.

### Architectural Concerns

See the parent architecture for the explicitly acknowledged event-only missed-event limitation.

## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
