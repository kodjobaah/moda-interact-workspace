---
id: ARCH-040-SYSTEM-TEST-001
architecture_id: ARCH-040
title: Certify one conversation and shared follow-up credit
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-040-DATABASE-001
  - ARCH-040-BACKGROUND-002
  - ARCH-040-ADMIN-001
enables: []
created: 2026-10-14
updated: 2026-10-17
---

# ARCH-040-SYSTEM-TEST-001 — Certify one conversation and shared follow-up credit

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Independently certify the **shared PostgreSQL/Background runtime**: atomic handover, WhatsApp message history, one post-window follow-up and billing under adversarial concurrency, without depending on Shopify or WooCommerce API implementation.

## Context

The approved direction is one existing `Conversation` for one `CheckoutRecovery` generation, with author-distinguished messages and one recovery-wide post-24-hour follow-up shared between human and AI. This is the platform-neutral **Database -> Background** certification; the Shopify and WooCommerce browser/API boundaries are certified independently in SYSTEM-TEST-002 and SYSTEM-TEST-003.

## Scope

- Implement the bounded system-test capability described by the objective.
- Add focused tests and evidence for that capability.

## Out of Scope

- No creation of a second Conversation for human chat or a recovery follow-up.
- No independent human-only follow-up allowance or duplicate usage counter.
- No updates to docs/decisions/**/_index.md pending explicit user confirmation.
- No opportunistic cross-repository work or additional task execution.

## Requirements

- Include negative cases for standalone/PRODUCT_SUPPORT human-command admission, recovery shop mismatch, AI ownership revision race, and one existing sequence-2 follow-up. Demonstrate scheduled NO_RESPONSE follow-up suppression after customer reply while an eligible deliberate merchant follow-up uses the same single claim; never treat follow-up as a second Conversation.
- Confirm the shared runtime uses existing provider delivery, receipts and credit identity; no alternate sender/ledger. No platform UI implementation is required for this producer-neutral test.

- Use black-box disposable PostgreSQL/Redis harness with real service boundaries; no all-in-one test file.
- Test customer inbound resets window, queued text crossing 24-hour expiry, takeover vs in-flight AI, human/AI follow-up race, retries, already used and failed provider sends.
- Seed authenticated-shop-equivalent, tenant-scoped persisted control state and commands directly through the test harness; do not launch Shopify app, WooCommerce plugin or Woo-only API as a prerequisite.
- Assert same Conversation ID before/after every operation and one sequence-2 attempt/credit.

### Abuse-protection certification

- Seed ACTIVE/SUSPENDED restriction state and audit transitions through the same PostgreSQL schema. Verify command already queued, leased, or retried before Admin suspension is blocked when suspension wins the final provider-admission race; verify provider request already irreversibly submitted first is not claimed retractable.
- Prove AI and automation still work, human-only blocked commands do not charge recovery credits, same Conversation is retained, repeated rate/spam does not multiply provider sends, restore does not revive old rejected commands, and tenant isolation is intact. Use no Shopify/Woo producer as prerequisite.


### Platform-neutral scheduling, provider races and content-memory certification

Validate with neutral persisted producer fixtures, not Shopify/WooCommerce implementation dependencies: one accepted HUMAN command is picked up by one PostgreSQL poller across competing messaging worker replicas; no command-specific BullMQ queue exists. Existing inbound WhatsApp and delayed recovery no-response jobs still execute via their original BullMQ workers and converge on shared BG001 policy. Test `AI -> HUMAN -> AI` with a HUMAN-authored historical message: the resumed model receives it as labelled untrusted merchant context, not its own prior assistant utterance. Deliver verified out-of-order inbound WhatsApp timestamps (including audio), assert monotonic `lastInboundAt`/window eligibility. Exercise prior unclaimed scheduled sequence-2 claimed by HUMAN, claimed/UNKNOWN rejection, one attempt/credit. Force permit-first/takeover-first and suspension-first/permit-first races, crashed admitted/UNKNOWN commands and no blind provider re-submission. Assert default command/dedupe records are not purged. All final provider transport tests use mocked Meta and real database claim/admission transactions; no claim of provable exactly-once delivery under an unknown provider outcome.


## Work Items

- [ ] Use black-box disposable PostgreSQL/Redis harness with real service boundaries; no all-in-one test file.
- [ ] Test customer inbound resets window, queued text crossing 24-hour expiry, takeover vs in-flight AI, human/AI follow-up race, retries, already used and failed provider sends.
- [ ] Use producer-neutral persisted fixtures; do not require Shopify, WooCommerce or Woo API processes.
- [ ] Assert same Conversation ID before/after every operation and one sequence-2 attempt/credit.

## Interfaces / Contracts

Test canonical persisted Prisma state, control transitions, worker dispatch and provider receipts through the **shared Database/Background runtime**. Use producer-neutral, tenant-scoped fixture commands and attempts to prove that dispatch and recovery credit treatment do not depend on their source. Shopify authentication/routes belong to SYSTEM-TEST-002; Woo installation authentication and hosted API belong to SYSTEM-TEST-003. No new Conversation for any follow-up.

## Dependencies

- ARCH-040-DATABASE-001
- ARCH-040-BACKGROUND-002
- ARCH-040-ADMIN-001

## Enables

None.

## Acceptance Criteria

- [ ] Single-conversation invariant passes through all branches.
- [ ] Human and AI concurrency produce at most one follow-up credit and provider action.
- [ ] Cross-tenant persisted commands are rejected by the database/worker; platform authentication and HTTP bypass cases are tested in each platform’s independent E2E task.

## Validation

- [ ] Black-box database/queue/provider matrix
- [ ] Evidence bundle and deterministic repro scripts
- [ ] git diff --check; review canonical task-worktree and dependency-sync evidence

## Stop Condition

After only this task’s Work Items, Acceptance Criteria and Validation are complete, record implementation evidence, set status to review and return control to moda_architect. Do not begin dependent tasks.

## Implementation Notes

Use `scripts/start-agent-task.py --prepare` in the actual developer workspace when this definition is materialised; keep matching parent and implementation task branches in separate launcher-resolved worktrees, as documented in workspace policy. Check actual repository scripts before validation. Structured logging must use the published shared logger; no credentials or full customer content in logs. Preserve current production compatibility unless architect specifically establishes a safe pre-production breaking rollout.

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
The architecture is proposed; implementation starts only after agreed/materialised task definition.

### Unresolved Issues
None recorded at definition time.

### Architectural Concerns
Return newly discovered contract or ownership gaps to moda_architect.

## Architect Review

### Review Status
Pending

### Review Notes
Not reviewed.

### Reviewed Files
None.

### Validation Reviewed
None.

### Architecture Conformance
Pending.

### Follow-up
None.
