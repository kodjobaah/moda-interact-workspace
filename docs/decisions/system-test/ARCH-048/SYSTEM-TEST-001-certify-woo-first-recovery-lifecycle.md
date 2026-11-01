---
id: ARCH-048-SYSTEM-TEST-001
architecture_id: ARCH-048
title: Certify Woo multi-generation checkout recovery, consent, routing and billing
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
  - ARCH-048-BACKGROUND-006
  - ARCH-048-BACKGROUND-007
  - ARCH-048-BACKGROUND-008
  - ARCH-048-BACKGROUND-009
  - ARCH-048-BACKGROUND-010
  - ARCH-048-BACKGROUND-011
  - ARCH-046-BACKGROUND-002
  - ARCH-046-BACKGROUND-004
  - ARCH-046-WOOCOMMERCE-003
  - ARCH-045-BACKGROUND-005
enables: []
created: 2026-10-23
updated: 2026-10-29
---

# ARCH-048-SYSTEM-TEST-001 — Certify Woo multi-generation checkout recovery

## Architecture

Architecture ID: `ARCH-048`.

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md` (2026-10-29 amendment).

Coordinator: `moda_architect`. This is a **terminal** system-test task, not an implementation prerequisite or a live provider activation task. It remains Pending while BG007–BG011 and returning-consent prerequisites are incomplete. The portable definition is not a branch or deployment claim.

## Objective

Independently prove a complete Woo checkout can be abandoned, resumed, have its old recovery cancelled, and then be abandoned again as a **new generation with its own eligible initial outreach**, without duplicating sends, billing, violating consent or allowing older jobs/replies to revive the old recovery.

## Context

The original 2026-10-23 acceptance task prohibited a second recovery after any prior row; this is **superseded**. The new lifecycle permits sequential generations per `(shopId, checkoutKey)`. The underlying Woo event-only capture, ARCH-046 consent/STOP gates, Woo outbound test-only flag and Shopify source-isolation checks remain. `moda_system_test` owns the test harness; it does not implement or correct Background or Woo business code.

## Scope

- Create/extend reproducible end-to-end scenarios and fixtures in `moda-interact-system-test/` using the repository's actual catalogue/harness conventions, including Classic Checkout, Checkout Blocks, HPOS, authenticated Moda API, real Redis/BullMQ and PostgreSQL, and controlled/emulated Meta provider responses.
- Capture actual checkout line items, order event, `CheckoutRecovery.generation`, status history, candidate job/index, attempt, reservation/usage, conversation and provider-message evidence using redacted tenant fixtures.
- Exercise the accepted BG007–BG011 services **through actual queue workers**, not just mocked methods; preserve existing Shopify/unmarked-candidate coverage.
- Cover supported failures: out-of-order events, same-second conflict, duplicate event ID, SQL close→Redis scheduling crash, INSERT→initial enqueue crash, index ownership loss, lease expiry, provider permit→closure, credit release failure, order-first/paid event, STOP and returning-consent change.
- Record the limitations of Woo events that never arrive and the bounded order-first Redis terminal-evidence retention.

## Out of Scope

No production WhatsApp send, live merchant checkout-state HTTP read, unapproved WordPress extension endpoint, global outreach policy refactor, other repository source changes, schema migration or simulated green results unsupported by measured observations.

## Requirements

### Required scenarios (all must be independently evidenced)

1. **G1 initial:** create cart A, wait configured inactivity delay, verify one `CheckoutRecovery` generation 1 with snapshot A, one DETECTED history row; with explicit *test-only* Woo outbound opt-in and qualified consent/template/credit, prove at most one confirmed initial/provider permit/charge.
2. **New checkout update closes G1:** after gen-1 admission (both before and after its first send), change quantity/add/remove item; verify only gen 1 becomes `CANCELLED` with one `CHECKOUT_RESUMED` history row, its original `lineItems`, `currency`, `totalPrice`, message and confirmed usage remain unchanged. No new G1 send occurs after closure.
3. **G2 candidate:** inspect pending generation 2 (not immediate recovery row), whose basket is the **new** full cart; a second edit updates only that candidate and restarts inactivity delay. Explicit empty cart cancels candidate; refill starts a valid G2 candidate. Unknown/oversized basket never borrows old items.
4. **G2 admitted:** once last activity delay expires, exactly one gen-2 `CheckoutRecovery` is inserted with new items/total and distinct recovery ID. When eligible, its **own initial** can be admitted/sent/charged **even if G1 already sent**; no cross-generation cooldown or lifetime initial cap. Within each recovery initial is still idempotent. Woo follow-ups remain disabled.
5. **G3:** resume gen 2 and re-abandon; same rules yield generation 3 rather than duplicate gen 2 or an unbounded number of initial sends **within one generation**.
6. **Replay and crash:** duplicate original checkout event cannot spuriously cancel G1; exact admitted-origin event can repair a missed initial enqueue without opening G2; crash after SQL close but before Redis schedule repairs **same G2**; stale old maturity job/index cannot delete G2; duplicate G2 maturity creates only one row; failed jobs remain visible and retryable.
7. **Order:** `ORDER_PLACED` suppresses recovery but is not `ORDER_PAID`; paid/cancelled events after candidate removal or after G1 cancellation suppress future candidate/initial while observed. Assert what can and cannot be proven for an **order-first event whose Redis evidence eventually expires**; do not claim permanent protection without a durable order-first record.
8. **Consent and STOP:** missing/revoked/ambiguous consent, changed phone/installation/customer identity, local STOP, merchant eligibility, template-category/registration failure and insufficient capacity deny sends for **each** generation. Later consent alone must not fabricate a checkout resumption/candidate. Returning-customer consent task ARCH-046-WOO003 must be implemented first.
9. **Provider settlement:** G1 pre-permit RESERVED free, paid-included, purchased or promotional credit is released once on closure; delivered or provider-admitted/uncertain G1 work is not falsely cancelled/refunded or sent again. Provider permit committing on either side of SQL closure has the correct one-way outcome. G2 has a separate source key/attempt/charge.
10. **WhatsApp routing:** explicit G1 provider-context reply persists in historical conversation without old AI/recovery automation; unreferenced reply goes to the single eligible active G2 conversation; same phone across two eligible shops remains guidance/ambiguous; STOP still acts before routing; duplicate inbound does not add turns.
11. **Source isolation:** Woo candidate includes generation; no Woo job goes through Shopify materialisation. Old unmarked Shopify job continues in Shopify path; unknown marker fails closed. No Woo API checkout-reading endpoint, Background→Woo live HTTP or unapproved provider call is introduced.
12. **Never-delivered events:** deliberately exhaust/drop an authenticated checkout update and a paid order event; verify system cannot claim to know them and that this limitation is explicitly recorded as an outbound launch blocker. Do not silently invent a provider read.
13. **Production mode:** prove normal non-test Woo composition refuses initial provider sending; any test-only opt-in cannot enable live/staging sending accidentally. No Woo automatic follow-up is sent.

## Work Items

- [ ] Build catalogue scenarios and fixture/setup/teardown through real approved system-test harness.
- [ ] Execute and record G1→G2→G3, basket history, inactivity timing and initial independent eligibility.
- [ ] Execute event ordering/crash/replay/index/lease and order-reconciliation failures.
- [ ] Execute billing bucket, provider uncertainty, consent/STOP, multi-generation routing and Shopify regression checks.
- [ ] Run default-off and never-delivered-event negative scenarios; document risks and environment assumptions.
- [ ] Return redacted evidence paths and repeatable commands in Completion Report; stop for architect review.

## Interfaces / Contracts

- Uses unchanged `woo.activity.v1` authenticated API and shared queue contracts, v2 **internal Background** `WooPendingCandidate.generation`, existing PostgreSQL `CheckoutRecovery` and history, Woo final SQL send permit and provider emulator.
- Separate per-test shop, checkout key, source event IDs, item snapshots, consent/phone identity and credit buckets; no use of real merchant PII.
- Test results use system-test repository's existing scenario catalogue and evidence format. No new runtime API contract.

## Dependencies

All YAML `depends_on` task IDs above must be accepted **Complete**. This includes BG007–BG011, `ARCH-046-WOOCOMMERCE-003` and the prior ARCH-048/046/045 foundation tasks. Developer may perform manual acceptance before choosing when to run this Ready terminal task; that checkpoint is not an implementation dependency.

## Enables

None; final architect verification may mark ARCH-048 Implemented only after this task is accepted and remaining rollout gates are explicitly dispositioned.

## Acceptance Criteria

- [ ] At least one end-to-end Classic and one Blocks/HPOS G1→G2 scenario prove new items and different immutable recovery IDs.
- [ ] Both G1 and G2 can each receive an independently qualified initial in test mode, but retries/duplicate deliveries never create a second initial/charge **inside** either generation; no cross-generation cooldown/cap exists.
- [ ] G1 closes once, G2 pending updates do not create G3 prematurely, and G1 confirmed sends/billing remain immutable.
- [ ] Provider-before/after-closure races, all four credit buckets, uncertain permit, same-second ambiguity and Redis/Postgres crash repair are covered by reproducible evidence.
- [ ] Terminal order, STOP/current consent, provider MARKETING registration, prior-generation routing, cross-shop ambiguity and Shopify source isolation behave as specified.
- [ ] Production Woo sending remains disabled; no follow-up or remote Woo checkout read was introduced.
- [ ] Explicitly separate **delivered event guarantees** from **never delivered** checkout/payment event and expired order-first fence limitations; do not claim complete safety without evidence.

## Validation

- [ ] `npm run validate:catalogue` and `npm run test:harness` against newly registered scenarios.
- [ ] `npm run system:plan` or `npm run system:recovery:plan` to show selected scenarios (check actual CLI args/catalogue).
- [ ] `node scripts/run-system-tests.js --scenario <actual registered scenario IDs> --execute` against an isolated LocalWP/Woo/API/Background/Redis/PostgreSQL/test Meta environment. Document exact scenario IDs, versions, commands and any blocked cases; do not mark unrun scenarios passing.
- [ ] `npm run lint`, `npm run typecheck` and `git diff --check` as applicable to test harness source.

## Stop Condition

When all required scenarios have run or genuine blockers are recorded, complete the task's Completion Report, set status `review` only for satisfied acceptance criteria, return to `moda_architect` and **STOP**. If a required test cannot pass because implementation is defective, report the failing evidence and block rather than patch application code or claim success.

## Implementation Notes

This is a system-test **terminal task**. Use the launcher-resolved dedicated parent and implementation worktrees and record isolation, start synchronization, Git revisions and recursive submodules; never run in a shared checkout. Read exact package scripts, scenario catalogue and available emulators before choosing commands. Historical first-recovery-only scenario expectations must be updated to the **new** lifecycle; preserve existing independent consent/Shopify regressions. The current source snapshot contains no proof that the new implementation has been integrated/deployed. No live Meta API credentials or real customer data are authorised for these tests.

## Completion Report

### Status

Not Started — revised portable definition, not materialised for this amendment.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run by system-test agent.

### Deviations

None.

### Assumptions

Inspected 2026-10-29 snapshot only; actual LocalWP/HPOS, queue and Meta emulator versions must be recorded.

### Unresolved Issues

None at definition time; previously documented event-only and TTL limitations remain explicit.

### Architectural Concerns

No claim that undelivered activity can be detected or that production outreach is safe/approved.

## Architect Review

### Review Status

Pending.

### Review Notes

No implementation/evidence reviewed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
