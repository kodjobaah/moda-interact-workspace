---
id: ARCH-034-MESSAGING-004
architecture_id: ARCH-034
title: Extract webhook dispatcher and compose thin route
task_kind: implementation
domain: messaging
repository: moda-interact-messaging
assigned_agent: moda_messaging
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-034-MESSAGING-003"]
enables: ["ARCH-034-SYSTEM-TEST-001"]
created: 2026-10-11
updated: 2026-10-11
---

# Extract webhook dispatcher and compose thin route

## Architecture

Architecture ID: `ARCH-034`.

Architecture document: `docs/architecture/ARCH-034-whatsapp-webhook-ingress-maintainability.md`.

Coordinator: `moda_architect`.

## Objective

Move authenticated entry/change traversal and normalization-to-publication orchestration to a focused dispatcher, leaving `app/routes/whatsapp.tsx` as a small HTTP response/telemetry composition module.

## Context

After MESSAGING-001/002/003, the route still owns loops over `entry`, `changes`, `messages` and `statuses` and short-circuit/ignore behaviour. The route currently responds 400 to invalid inbound messages, ignores invalid statuses, and can enqueue earlier entries before a later invalid event; this task must not silently change those behaviours.

## Scope

- Introduce `app/lib/whatsapp/webhook-dispatch.server.ts` to orchestrate only verified, parsed payload dispatch to existing extracted normalizers and publishers.
- Keep exported React Router `loader` and `action` in `app/routes/whatsapp.tsx`, preserving method, raw-body signature, JSON parse, response/telemetry and exception handling.
- Add route-level HTTP and mixed signed-payload tests, including inbound/status ordering, unsupported event filtering, signatures and error paths; update old test imports to the extracted owners.
- Confirm and record final source module sizes and minimal residual route responsibilities.

## Out of Scope

- Changing top-level JSON shape validation or existing partial-publication/400 semantics.
- Changing Meta/provider status policy or introducing a new queue, DB operation, tracing framework or merchant side effect.
- Rewriting independent extracted modules or moving HTTP response telemetry into dispatch.

## Requirements

- Exact `GET/POST /webhook/whatsapp` URL, exported loader/action responses/statuses/headers and accepted payload behaviour remain unchanged.
- For each `messages` change, preserve messages-first/statuses-second traversal and nested ordering.
- Malformed inbound event still triggers existing 400 handling; malformed individual provider status still silently skips. Do not label existing partial publication as fixed.
- Preserve raw-body signature verification before JSON and dispatch; errors after publication keep existing failure/telemetry handling.
- Keep `app/routes/whatsapp.tsx` at or below 150 physical lines without relocating all previous contents into another >300-line catch-all.
- New dispatcher remains focused (target <=200, hard <=300 physical lines); no duplicate observability emitter.

## Work Items

- [ ] Extract verified event traversal into dispatcher without changing observable behaviour.
- [ ] Add focused route-level verification and mixed-event orchestration tests, preserving existing tests.
- [ ] Run full repo validation, inspect sensitive-data boundary and line-count target.
- [ ] Report known malformed-payload/partial-enqueue risks as out-of-scope follow-up; do not fix within refactor.

## Interfaces / Contracts

- Route configuration `app/routes.ts` and URL unchanged.
- Uses narrow collaborators created in `ARCH-034-MESSAGING-001` through `-003`.
- Retains `recordWhatsAppIngressTelemetry`, `whatsapp-events` queue and canonical Shared v1/v3 payloads.

## Dependencies

- `ARCH-034-MESSAGING-003`

## Enables

- `ARCH-034-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Route contains only minimal HTTP ingress/response/telemetry composition and <=150 physical lines.
- [ ] No new production source file exceeds 300 physical lines, and new dispatcher remains independently testable.
- [ ] GET verification, rejected POSTs, valid signed inbound/status and mixed payloads retain response/publish behaviour.
- [ ] Existing unit/regression suites and production build pass; no raw body/secret/customer text is newly logged.
- [ ] Known hardening questions are documented, not silently changed.

## Validation

Inspect the current repository `package.json` and use its actual scripts. The following existed in the inspected baseline; if they have changed, record the difference without inventing scripts.

- [ ] `node --import tsx --test tests/whatsapp-provider-status.test.mjs tests/whatsapp-inbound-normalization.test.mjs`
- [ ] HTTP route/dispatcher-focused Node tests (test filenames defined by implementer)
- [ ] `node --import tsx --test tests/whatsapp-ingress-telemetry.test.mjs`
- [ ] `npm test`
- [ ] `npm run typecheck`
- [ ] `npm run build`
- [ ] `git diff --check`
- [ ] Record focused changed-file sizes; no new source file above 300 physical lines

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are satisfied, record the Completion Report, set status to `review`, and STOP for `moda_architect`. Never start the enabled task automatically. Use the canonical mirrored task branches and launcher-resolved physical worktrees; do not implement in a shared/default checkout.

## Implementation Notes

Preserve the route as the framework boundary rather than exporting a second HTTP handler from the dispatcher. Do not classify internal queue observations as BLACK_BOX product evidence. Successful manual validation may precede the terminal system-test task.

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
