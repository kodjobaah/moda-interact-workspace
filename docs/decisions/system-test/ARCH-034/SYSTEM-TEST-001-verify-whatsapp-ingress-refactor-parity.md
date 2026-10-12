---
id: ARCH-034-SYSTEM-TEST-001
architecture_id: ARCH-034
title: Verify WhatsApp ingress refactor and rejection hardening
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 80
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-034-MESSAGING-005"]
enables: []
created: 2026-10-11
updated: 2026-10-12
---

# Verify WhatsApp ingress refactor and rejection hardening

## Architecture

Architecture ID: `ARCH-034`.

Architecture document: `docs/architecture/ARCH-034-whatsapp-webhook-ingress-maintainability.md`.

Coordinator: `moda_architect`.

## Objective

Independently validate the refactored Messaging webhook ingress and the explicit post-refactor invalid-request preflight hardening using the established system-test harness, without inventing new release certification.

## Context

The consolidated `moda-interact-system-test` suite contains an existing Messaging runtime, disposable Redis/PostgreSQL, the canonical WhatsApp emulator fixture and implemented BLACK_BOX inbound-message scenarios. The October 2026 source snapshot shows `MESSAGING-STATUS-001` still planned because its external outcome boundary is not yet certifiable. This task validates refactor parity; it does not convert an internal queue assertion into release-grade BLACK_BOX evidence.

## Scope

- Reuse the established Messaging harness and signed Meta fixture support; do not add a second provider emulator or disposable data-plane implementation.
- Run current black-box inbound/reply/duplicate/coalescing/abuse scenarios against the post-refactor built Messaging service when the environment supports them.
- Add or reuse narrowly scoped INTEGRATION evidence proving signed v3 FAILED with bounded code and valid inbound payloads reach the unchanged queue boundary with expected event/identity and HMAC rejection precedes publication.
- Prove that structurally malformed but correctly signed envelopes return `400 invalid_payload` without publication (not `500`), and a valid inbound event followed by a malformed inbound event anywhere later in the same request returns `400` with **zero** published jobs.
- Verify signed valid mixed inbound/status requests still publish unchanged payloads/job IDs in order; malformed individual statuses remain ignored. Test accepted partial-publication/retry/idempotency explicitly as a *distinct* queue-failure boundary, not as preflight atomicity.
- Store redacted deterministic evidence and update the existing scenario catalogue/traceability only if a genuinely new scenario is introduced.

## Out of Scope

- Changing Messaging runtime code or Background delivery policy.
- Claiming Redis/BullMQ acceptance across a failing queue as all-or-nothing; only rejection during **preflight** guarantees zero jobs.
- Marking planned `MESSAGING-STATUS-001` BLACK_BOX or release-ready based only on internal Redis/DB evidence.
- Adding another WhatsApp stub, a new queue, new service topology or production credentials.

## Requirements

- Use current `moda-interact-system-test` scripts/harness and own `moda_system_test` repo; source snapshot command names must be checked at execution.
- Explicitly distinguish malformed signed webhook structure (`400 invalid_payload`), invalid JSON (`400 invalid_json`), bad/missing HMAC (`401`), valid no-op/non-messages changes (`200`), and queue failures (retry/`500`).
- Use synthetic credentials and isolated/disposable resources; do not access production or shared Render test state inadvertently.
- Distinguish CONTRACT/INTEGRATION/BLACK_BOX evidence honestly and retain source SHA, runtime and scenario identifiers.
- No new catch-all fixtures/executors; modularity policy maximum 300 source/test lines and separate fixtures/assertions/executors.
- A blocked runtime prerequisite is BLOCKED, not a falsely passing/failing product journey.

## Work Items

- [ ] Select and run relevant existing Messaging scenarios using current catalogue and harness.
- [ ] Add/extend only necessary bounded integration assertions for signed v3 and queue identity parity.
- [ ] Verify the hardening matrix: malformed signed top-level/nested shapes => controlled 400 and no jobs; early valid then late invalid inbound => 400 and zero jobs; valid mixed messages/statuses => ordered unchanged jobs; malformed individual statuses remain ignored.
- [ ] Record complete evidence provenance, actual classifications, skipped/blocked conditions and redaction check.
- [ ] Run relevant harness/structure/catalogue validation and return for architect review.

## Interfaces / Contracts

- Canonical system-test source of truth: `moda-interact-system-test/catalogue/scenarios.json` and existing Messaging executors/fixtures.
- Expected runtime: actual refactored/hardened `moda-interact-messaging` (after MESSAGING-005) and existing approved Background/WhatsApp emulator as needed.
- Published queue contracts remain the unchanged Shared inbound v1/provider-status v3 payloads.

## Dependencies

- `ARCH-034-MESSAGING-005`

## Enables

None.

## Acceptance Criteria

- [ ] Existing applicable Messaging BLACK_BOX scenarios show no externally observable regression.
- [ ] Signed v3/provider-code/duplicate ingress parity has evidence at the appropriate INTEGRATION boundary.
- [ ] Invalid/missing Meta signature does not enqueue business events.
- [ ] Signed malformed envelope and later-invalid inbound cases return 400 without any queue publication; accepted valid events retain existing identities and order.
- [ ] Evidence does not claim queue publication is transactional once publication begins; retry idempotency remains verifiable.
- [ ] Evidence never mislabels internal queue assertions as BLACK_BOX or claims planned status lifecycle certification.
- [ ] No system-test file exceeds the maintainability structure limit; no raw credentials/customer-sensitive payloads in evidence.

## Validation

Inspect the current repository `package.json` and use its actual scripts. The following existed in the inspected baseline; if they have changed, record the difference without inventing scripts.

- [ ] `npm run test:messaging-harness` (if still declared)
- [ ] `npm run system:messaging:plan` (if still declared)
- [ ] `npm run system:messaging` (when disposable runtime prerequisites are available)
- [ ] `npm run validate:catalogue` (if relevant source changes)
- [ ] `npm run validate:structure` / declared lint and `git diff --check`

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are satisfied, record the Completion Report, set status to `review`, and STOP for `moda_architect`. Never start the enabled task automatically. Use the canonical mirrored task branches and launcher-resolved physical worktrees; do not implement in a shared/default checkout.

## Implementation Notes

System-test tasks are terminal: do not make any implementation task depend on this task. Reuse existing black-box scenarios; do not change their meaning. If Redis/Docker/emulator cannot be started, record a BLOCKED validation item rather than claim success. The developer controls when to run this after manual application review.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending.

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
