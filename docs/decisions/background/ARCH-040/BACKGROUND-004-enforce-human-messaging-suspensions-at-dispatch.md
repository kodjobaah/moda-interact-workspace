---
id: ARCH-040-BACKGROUND-004
architecture_id: ARCH-040
title: Enforce merchant human-messaging restriction at dispatch
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-16
updated: 2026-10-17
---

# ARCH-040-BACKGROUND-004 — Enforce merchant human-messaging restriction at dispatch

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. Portable task definition; no branch, worktree, commit, push or implementation is claimed.

## Objective

**SUPERSEDED by `ARCH-040-BACKGROUND-001` (service/policy implementation) and `ARCH-040-BACKGROUND-002` (runtime integration). Do not execute this task.** Its detailed requirements are historical context; all required behaviour and tests were folded into the two active tasks.


Prevent queued or newly submitted HUMAN messages from reaching the WhatsApp provider once platform restriction is suspended, without interrupting AGENT/AUTOMATION messages.

## Context

Shopify server and Woo hosted API reject restricted submissions, but UI/API checks alone are insufficient: a command may have been accepted before an Admin suspension and still be queued or leased. Only Background controls final irreversible provider admission.

## Scope

- Check DATABASE-001 restriction while consuming `MerchantConversationSendCommand` and before the final provider handoff.
- Establish a documented cross-process serialization/fencing boundary against concurrent Admin suspension, including claim/retry/reconciliation.
- Record a durable restricted outcome on eligible commands without provider contact, debit, or generating a new Conversation.

## Out of Scope

- Do not change existing AI/automation entitlement or full-shop `Shop.status` rules; this is a platform-controlled HUMAN-only restriction.
- No merchant-facing toggle to restore a suspension, no per-employee permission system, no new Conversation or duplicated follow-up credit.
- Do not add new ARCH-040 Shared package publication, Shopify-to-Woo/API dependencies or `docs/decisions/**/_index.md` files.
- No speculative new service, queue platform or third-party AI moderation provider.

## Requirements

### Race and suspension contract

- Only `senderType=HUMAN` / merchant commands are restricted. Leave existing AI `AGENT`/`AUTOMATION` and normal customer ingress unaffected by this **human-only** gate.
- Refuse HUMAN commands when status SUSPENDED, including commands already `ACCEPTED` or leased before suspension. A command denied for suspension receives a bounded terminal failure/blocked reason `human_messaging_suspended`; do not retry endlessly and do not charge a recovery credit for a provider send that did not occur.
- Explicitly define final provider admission ordering: if the Admin suspension transaction commits **before** the send's irreversible provider-submission boundary, the HUMAN send must be suppressed. Re-read authority at that boundary and serialize/fence that decision; merely checking when the worker dequeues is insufficient. If submission genuinely preceded suspension, record it accurately: sent requests cannot be recalled.
- Do not hold a long-running PostgreSQL transaction across a Meta HTTP request. Prefer an existing durable reservation/fencing mechanism or a bounded, database-backed send-admission lease with explicit ordering semantics; if no safe fence exists, identify the architectural gap rather than claiming a read-check guarantees atomic external effects.
- Idempotency, retry, provider uncertainty and later receipts stay owned by existing Background dispatch. Suspension/restriction checks do not create a second follow-up claim/credit ledger. Resuming merchant access does not automatically requeue previously rejected commands; merchant must make a fresh deliberate send.
- Status changes must never automatically change `Conversation.controlMode` or cause CommerceAgent to send spontaneously. A merchant can explicitly Resume AI while suspended.
- Log identifiers/reason codes only using the shared logging package; never raw message content or internal admin notes.

## Work Items

- [ ] Implement durable restriction lookup and enforced HUMAN gate in the canonical dispatch path.
- [ ] Add race-safe final provider admission fencing compatible with administrative status transitions.
- [ ] Set terminal restricted outcomes and expose stable status for UI polling without revealing internal admin reason.
- [ ] Prove AI/automation continue and HUMAN commands are blocked before provider handoff, regardless of Shopify/Woo producer.

## Interfaces / Contracts

Consumes the consolidated DATABASE-001 restriction and merchant send-command models, using existing Background outbound provider/receipt/credit mechanisms. The `human_messaging_suspended` outcome is surfaced through existing command state/error fields and existing HTTP/UI boundaries without new Shared publication.

## Dependencies

None — superseded.

## Enables

None — superseded.

## Acceptance Criteria

- [ ] A restriction committed before final provider admission prevents HUMAN send, including queued/leased commands.
- [ ] No false success/credit charge for blocked sends; retries and duplicate jobs do not bypass restriction.
- [ ] AI messages, customer ingress and recovery automation are unaffected.
- [ ] Suspension and release are durable and shop-scoped with no cross-tenant effect.

## Validation

- [ ] PostgreSQL + disposable Redis worker concurrency/suspend/send race tests
- [ ] Provider mock submitted-before-vs-after suspension proof
- [ ] Queued/leased/replayed command and credit tests
- [ ] git diff --check and worktree evidence

## Stop Condition

After defined work, acceptance criteria and required validation are complete, record Completion Report, set task to review, return control to moda_architect and STOP. Do not begin another task.

## Implementation Notes

Coordinate ordering with ADMIN-001 and DATABASE-001. If precise provider-admission fencing cannot be built without broader changes, report the precise limitation for architectural decision rather than approximating correctness. Use the canonical task preparation/worktree protocol. Check actual repository scripts before running tests; use the published shared logger for structured telemetry without message contents or credentials. No `_index.md` updates until the user explicitly confirms architectural-session completion.

## Completion Report

### Status
Not Started

### Files Changed
None.

### Work Completed
None.

### Validation Results
Not run.

### Deviations
None.

### Assumptions
The initiative is proposed; work has not begun.

### Unresolved Issues
None recorded.

### Architectural Concerns
None recorded.

## Architect Review

### Review Status
Pending

### Review Notes
None.

### Reviewed Files
None.

### Validation Reviewed
None.

### Architecture Conformance
Pending.

### Follow-up
None.
