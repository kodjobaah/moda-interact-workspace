---
id: ARCH-034-MESSAGING-003
architecture_id: ARCH-034
title: Extract WhatsApp queue publishing and job identity
task_kind: implementation
domain: messaging
repository: moda-interact-messaging
assigned_agent: moda_messaging
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-034-MESSAGING-002"]
enables: ["ARCH-034-MESSAGING-004"]
created: 2026-10-11
updated: 2026-10-11
---

# Extract WhatsApp queue publishing and job identity

## Architecture

Architecture ID: `ARCH-034`.

Architecture document: `docs/architecture/ARCH-034-whatsapp-webhook-ingress-maintainability.md`.

Coordinator: `moda_architect`.

## Objective

Move deterministic inbound/status job identifiers and BullMQ producer calls out of the route into focused Messaging-owned collaborators, with byte-for-byte equivalent job data/options/identities.

## Context

The current route owns `createJobId`, `createStatusJobId`, `enqueueInboundMessage` and provider-status queue creation. `app/lib/queues/whatsapp.queue.ts` already owns the canonical queue connection and shared telemetry; it must be reused, not replaced.

## Scope

- Extract pure identity functions into `app/lib/whatsapp/job-identity.server.ts` (or equivalent).
- Extract minimal inbound/status job producer functions into `app/lib/whatsapp/whatsapp-job-publisher.server.ts` (or equivalent), consuming the existing queue adapter.
- Adjust the route to call those functions, retaining current publish order, messages/status validation and error propagation.
- Move job-ID tests to direct owner imports and add focused publisher tests using test-isolated queue stubs or disposable Redis when appropriate.

## Out of Scope

- Changing Redis/BullMQ instances, queue topology, shared observability, worker code, producer retry policy or metadata.
- Adding tenant/customer lookup, alternative idempotency or changing status v3 evidence identity.
- Refactoring the event traversal or authentication flow (owned by MESSAGING-004 / -002).

## Requirements

- Keep queue name `whatsapp-events`, job names `message-received` and `message-status` and exact normalized payloads.
- Preserve inbound `wa-` hash, status `ws-` hash and evidence-bearing FAILED v3 hash input; no timestamp additions.
- Preserve per-job attempts=3 and exponential backoff delay=1000, plus use of existing queue adapter and its defaults.
- Do not enqueue before HMAC verification; failures must retain existing propagation/acknowledgement semantics.
- Avoid a new queue connection, competing logger or home-grown tracing.

## Work Items

- [ ] Extract pure deterministic IDs and publishing helpers with narrow interfaces.
- [ ] Move/update focused job-ID assertions and add queue publication equivalence tests.
- [ ] Run relevant tests and note exact module sizes and no queue changes.

## Interfaces / Contracts

- Queue owner: `app/lib/queues/whatsapp.queue.ts` using existing Redis and BullMQ telemetry.
- Input contracts: published Shared inbound v1 and provider-status v3 objects.
- Existing queue consumers remain in `moda-interact-background`; no contract change.

## Dependencies

- `ARCH-034-MESSAGING-002`

## Enables

- `ARCH-034-MESSAGING-004`

## Acceptance Criteria

- [ ] Duplicate inbound/provider status produce identical IDs to pre-refactor code.
- [ ] Evidence-bearing FAILED v3 remains distinguishable from no-evidence FAILED, while duplicate evidence deduplicates.
- [ ] Queue jobs, options, payloads, publish sequencing and failure propagation remain unchanged.
- [ ] Existing telemetry/Redis adapter untouched; new files <=300 physical lines.

## Validation

Inspect the current repository `package.json` and use its actual scripts. The following existed in the inspected baseline; if they have changed, record the difference without inventing scripts.

- [ ] `node --import tsx --test tests/whatsapp-provider-status.test.mjs tests/whatsapp-inbound-normalization.test.mjs`
- [ ] `node --import tsx --test tests/whatsapp-queue-telemetry.test.mjs` (existing Redis-backed assertion may skip without TEST_REDIS_URL)
- [ ] New focused publisher equivalence tests (test-file name chosen by implementer)
- [ ] `npm test`
- [ ] `npm run typecheck`
- [ ] `npm run build`
- [ ] `git diff --check`
- [ ] Record focused changed-file sizes; no new source file above 300 physical lines

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are satisfied, record the Completion Report, set status to `review`, and STOP for `moda_architect`. Never start the enabled task automatically. Use the canonical mirrored task branches and launcher-resolved physical worktrees; do not implement in a shared/default checkout.

## Implementation Notes

Keep the pure identity helper isolated from `getWhatsAppQueue()` so it can be tested without Redis. If a test-facing queue injection seam is necessary, make it narrow and avoid creating a new generic provider abstraction.

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
