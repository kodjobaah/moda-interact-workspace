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
status: complete
priority: 40
executor: null
claimed_at: null
attempt: 2
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

- [x] Extract pure deterministic IDs and publishing helpers with narrow interfaces.
- [x] Move/update focused job-ID assertions and add queue publication equivalence tests.
- [x] Run relevant tests and note exact module sizes and no queue changes.

## Interfaces / Contracts

- Queue owner: `app/lib/queues/whatsapp.queue.ts` using existing Redis and BullMQ telemetry.
- Input contracts: published Shared inbound v1 and provider-status v3 objects.
- Existing queue consumers remain in `moda-interact-background`; no contract change.

## Dependencies

- `ARCH-034-MESSAGING-002`

## Enables

- `ARCH-034-MESSAGING-004`

## Acceptance Criteria

- [x] Duplicate inbound/provider status produce identical IDs to pre-refactor code.
- [x] Evidence-bearing FAILED v3 remains distinguishable from no-evidence FAILED, while duplicate evidence deduplicates.
- [x] Queue jobs, options, payloads, publish sequencing and failure propagation remain unchanged.
- [x] Existing telemetry/Redis adapter untouched; new files <=300 physical lines.

## Validation

Inspect the current repository `package.json` and use its actual scripts. The following existed in the inspected baseline; if they have changed, record the difference without inventing scripts.

- [x] `node --import tsx --test tests/whatsapp-provider-status.test.mjs tests/whatsapp-inbound-normalization.test.mjs`
- [x] `node --import tsx --test tests/whatsapp-queue-telemetry.test.mjs` (existing Redis-backed assertion may skip without TEST_REDIS_URL)
- [x] New focused publisher equivalence tests (test-file name chosen by implementer)
- [x] `npm test`
- [x] `npm run typecheck`
- [x] `npm run build`
- [x] `git diff --check`
- [x] Record focused changed-file sizes; no new source file above 300 physical lines

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are satisfied, record the Completion Report, set status to `review`, and STOP for `moda_architect`. Never start the enabled task automatically. Use the canonical mirrored task branches and launcher-resolved physical worktrees; do not implement in a shared/default checkout.

## Implementation Notes

Keep the pure identity helper isolated from `getWhatsAppQueue()` so it can be tested without Redis. If a test-facing queue injection seam is necessary, make it narrow and avoid creating a new generic provider abstraction.

## Completion Report

### Status

Ready for Review — developer-managed extraction plus disposable-Redis validation, subsequently architect-reviewed and accepted on 2026-10-11. Two incremental patch deliveries were used (Attempt 1 source extraction, Attempt 2 Redis runner); no launcher claim was made.

### Files Changed

Implementation repository (`moda-interact-messaging`), first patch:

- `app/routes/whatsapp.tsx` — delegate queue writes and job identities; 243 -> 185 physical lines.
- `app/lib/whatsapp/job-identity.server.ts` — new, 24 physical lines.
- `app/lib/whatsapp/whatsapp-job-publisher.server.ts` — new, 47 physical lines.
- `tests/whatsapp-inbound-normalization.test.mjs` — import the identity helper from its owning module.
- `tests/whatsapp-provider-status.test.mjs` — import the status identity helper from its owning module.
- `tests/whatsapp-job-publisher.test.mjs` — new, 136 physical lines; six declared publisher tests.

Second incremental patch:

- `scripts/run-whatsapp-queue-redis-test.sh` — new, 69 physical lines; isolated disposable Docker Redis test launcher.

**This acceptance patch changes parent-workspace task/architecture documentation only, not those seven implementation files.** The existing `app/lib/queues/whatsapp.queue.ts` Redis/BullMQ adapter and shared telemetry are untouched.

### Work Completed

- Extracted deterministic inbound `wa-` and status `ws-` hash identity into a pure server-only helper without introducing timestamps or altering v3 FAILED provider-code evidence identity.
- Extracted `message-received` and `message-status` publication through the already-existing `getWhatsAppQueue()` adapter. The optional injected queue is a narrow test seam only; queue names, normalized event payloads, job IDs, attempts=3 and exponential 1000 ms backoff remain unchanged.
- Kept production publication order, error propagation, HMAC-before-publication and telemetry behaviour unchanged. No new queue, Redis connection, provider classification, tenant lookup or Shared contract was introduced.
- Updated owner-import tests and added isolated publisher equivalence tests for job options/payloads, v3 failure-evidence identity and propagated queue errors.
- Added a disposable Redis 7.4 Alpine test runner: Docker chooses an ephemeral localhost-only port, `TEST_REDIS_URL` and `REDIS_URL` apply to the test process only, disk persistence is disabled, and an exit trap removes the container. No production Redis connection is reconfigured.

### Validation Results

**Developer-reported following Attempt 1:** all requested focused tests, full `npm test`, `npm run typecheck`, `npm run build`, and `git diff --check` passed. Original command-by-command transcripts and exact overall suite counts were not attached, so no invented counts or independent execution claim is made.

**Developer-supplied Redis run following Attempt 2 (2026-10-11):**

```
redis:7.4-alpine image downloaded
Running Redis-backed WhatsApp tests on disposable Redis (localhost:32870)
PASS uses one shared adapter through the native Queue telemetry option
PASS continues the inbound request trace without changing the queue payload
tests 2 / pass 2 / fail 0 / skipped 0
```

This is live disposable Docker/Redis execution evidence, unlike the earlier Redis-conditional full-suite skip. It exercises a signed inbound webhook, BullMQ publication/processing, trace continuity and unchanged queue payload. The user supplied the output; the architect did not run Docker in this review environment.

**Architect independently verified:** seven-file implementation scope, deterministic identity/publisher source and focused test semantics; original-to-extracted queue/job-ID smoke parity (eight tested publish calls during patch preparation); file-size bounds; Redis-runner `bash -n`, local-only ephemeral binding, finite readiness wait, per-process environment isolation and `trap`-based cleanup. Prior source patch and incremental Redis patch individually passed isolated fresh-baseline `git apply --check --whitespace=error-all`, application, and `git diff --check` checks.

Existing Vite Node-core browser-externalization warnings are nonfatal and not a task regression. The Redis test output logs only bounded message identifiers/type/phone-number IDs, not raw bodies or customer content.

### Deviations

The developer expressly used architect-supplied patches in the main Messaging checkout, not the standard `/moda-task` prepared pair of canonical parent/implementation task worktrees and mirrored branches. This is a recorded task-execution workflow non-conformance, not claimed launcher evidence. No prepared packet, durable claim/push or implementation Git commit is invented. `attempt: 2` records the two manual patch iterations, not two verified launcher claims.

### Assumptions

The developer's earlier "all the test pass with green" statement applies to the MESSAGING-003 focused/full suite, typecheck, build and whitespace commands from the patch instructions. The subsequent quoted output is the actual disposable Redis run for this same refactor.

### Unresolved Issues

None identified in the bounded BullMQ/identity extraction. Malformed webhook envelopes and partial publication before a later invalid event remain unchanged by this task, and are explicitly assigned to `ARCH-034-MESSAGING-005` after the thin-route task.

### Architectural Concerns

No new cross-repository contract, durable-state, Redis deployment or Queue topology decision is introduced. Normal agent execution must continue to enforce the dedicated-task-worktree policy; this manual patch review is not proof of compliant agent worktree execution.

## Architect Review

### Review Status

Accepted — developer-managed patch iteration 2 (2026-10-11).

### Review Notes

The extraction preserves the `whatsapp-events` producer boundary while isolating pure deterministic job identities and a narrow publisher. Existing client-visible webhook behaviour, v1/v3 message/status payloads, v3 FAILED evidence deduplication, producer retries and errors remain unchanged. The tests and isolated original/extracted comparison cover those invariants. The subsequent disposable Docker Redis run provides the previously missing unskipped BullMQ/OpenTelemetry queue integration evidence.

Review accepts the **implementation and validation**, while explicitly recording the non-standard manual-main-checkout execution rather than asserting launcher/worktree/branch provenance.

### Reviewed Files

- `app/routes/whatsapp.tsx`
- `app/lib/whatsapp/job-identity.server.ts`
- `app/lib/whatsapp/whatsapp-job-publisher.server.ts`
- `tests/whatsapp-inbound-normalization.test.mjs`
- `tests/whatsapp-provider-status.test.mjs`
- `tests/whatsapp-job-publisher.test.mjs`
- `scripts/run-whatsapp-queue-redis-test.sh`
- Existing `app/lib/queues/whatsapp.queue.ts` (ownership/unchanged adapter check)
- User-provided complete live Redis test summary

### Validation Reviewed

- Developer-reported focused tests, full suite, typecheck, production build and whitespace validation: PASS (no exact totals supplied).
- Developer-supplied live Redis-backed queue telemetry: **2/2 PASS, 0 skipped, 0 failed**, disposable Redis 7.4 Alpine on localhost:32870.
- Architect prior isolated queue-identity/publication equivalence checks and patch/syntax checks: PASS.
- Architect inspection of disposable Redis runner, cleanup isolation and shell syntax: PASS.
- No independent full repository or Docker integration execution by the architect is claimed.

### Architecture Conformance

Conforms to `ARCH-034-MESSAGING-003`: exact existing queue adapter, two job types, payloads/identities, attempts/backoff, failure propagation, v3 evidence identity, no new backend/database coupling, and module-size targets. No change is made to MESSAGING-004 traversal or MESSAGING-005 pre-publication hardening semantics.

### Follow-up

Promote `ARCH-034-MESSAGING-004` from Pending to Ready after this task is accepted Complete. Keep `ARCH-034-MESSAGING-005` and the terminal `ARCH-034-SYSTEM-TEST-001` Pending. Do not reconcile any `docs/decisions/**/_index.md` until the developer explicitly ends this architectural session.
