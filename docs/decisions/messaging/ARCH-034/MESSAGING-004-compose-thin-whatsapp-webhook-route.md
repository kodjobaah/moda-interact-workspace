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
status: complete
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on: ["ARCH-034-MESSAGING-003"]
enables: ["ARCH-034-MESSAGING-005"]
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

- Changing top-level JSON shape validation or existing partial-publication/400 semantics. This is owned by downstream `ARCH-034-MESSAGING-005` after the refactor is architect-accepted.
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

- [x] Extract verified event traversal into dispatcher without changing observable behaviour.
- [x] Add focused route-level verification and mixed-event orchestration tests, preserving existing tests.
- [x] Run full repo validation, inspect sensitive-data boundary and line-count target.
- [x] Report known malformed-payload/partial-enqueue risks as out-of-scope follow-up; do not fix within refactor.

## Interfaces / Contracts

- Route configuration `app/routes.ts` and URL unchanged.
- Uses narrow collaborators created in `ARCH-034-MESSAGING-001` through `-003`.
- Retains `recordWhatsAppIngressTelemetry`, `whatsapp-events` queue and canonical Shared v1/v3 payloads.

## Dependencies

- `ARCH-034-MESSAGING-003`

## Enables

- `ARCH-034-MESSAGING-005` — starts only after this pure-refactor task is Complete; the terminal system test now depends on MESSAGING-005.

## Acceptance Criteria

- [x] Route contains only minimal HTTP ingress/response/telemetry composition and <=150 physical lines.
- [x] No new production source file exceeds 300 physical lines, and new dispatcher remains independently testable.
- [x] GET verification, rejected POSTs, valid signed inbound/status and mixed payloads retain response/publish behaviour.
- [x] Existing unit/regression suites and production build pass; no raw body/secret/customer text is newly logged.
- [x] Known hardening questions are documented, not silently changed.

## Validation

Inspect the current repository `package.json` and use its actual scripts. The following existed in the inspected baseline; if they have changed, record the difference without inventing scripts.

- [x] `node --import tsx --test tests/whatsapp-provider-status.test.mjs tests/whatsapp-inbound-normalization.test.mjs`
- [x] HTTP route/dispatcher-focused Node tests (test filenames defined by implementer)
- [x] `node --import tsx --test tests/whatsapp-ingress-telemetry.test.mjs`
- [x] `npm test`
- [x] `npm run typecheck`
- [x] `npm run build`
- [x] `git diff --check`
- [x] Record focused changed-file sizes; no new source file above 300 physical lines

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are satisfied, record the Completion Report, set status to `review`, and STOP for `moda_architect`. Never start the enabled task automatically. Use the canonical mirrored task branches and launcher-resolved physical worktrees; do not implement in a shared/default checkout.

## Implementation Notes

Preserve the route as the framework boundary rather than exporting a second HTTP handler from the dispatcher. Do not classify internal queue observations as BLACK_BOX product evidence. Successful manual validation may precede the terminal system-test task.

## Completion Report

### Status

Ready for Review — retrospective developer-applied Attempt 1, accepted by architect after validation confirmation.

### Files Changed

- `app/routes/whatsapp.tsx`
- `app/lib/whatsapp/webhook-dispatch.server.ts` (new)
- `tests/whatsapp-webhook-dispatch.test.mjs` (new)
- `tests/whatsapp-webhook-route.test.mjs` (new)

### Work Completed

Moved existing authenticated `entry`/`changes` traversal to a focused 60-line dispatcher, leaving a 138-line route responsible for HTTP entrypoints, raw-body signature verification delegation, response mapping and ingress telemetry. Preserved messages-first/statuses-second ordering, ignored individual invalid provider statuses, and retained the known malformed-envelope and partial-publication behaviours for MESSAGING-005. Added dispatcher and signed HTTP tests using the existing narrow injected-publisher/test-dispatch seam. No changes to Shared contracts, queue identity or policy.

### Validation Results

Developer confirms all instructed MESSAGING-004 tests, full test suite, typecheck, production build and whitespace check **passed**; exact local command transcripts/counts were not attached. Earlier isolated behavioural-equivalence checks of the delivered implementation reported 12/12 comparable scenarios and 11/11 added tests (substitute Shared validators, not an independent full-repository test run). The inspected implementation is 138 route lines / 60 dispatcher lines. Redis telemetry had already been validated for MESSAGING-003 using disposable Redis and was left unchanged by this task.

### Deviations

Developer intentionally applied architect-supplied patches in the shared/main checkout rather than through mirrored launcher worktrees. No task branch/launcher/claim metadata is fabricated. This is a retrospective documentation correction, not a newly executed task.

### Assumptions

The developer's "all green" confirmation covers the validation commands in this task after application of the MESSAGING-004 patch to the accepted MESSAGING-003 baseline.

### Unresolved Issues

No blocking issue in the bounded refactor. The pre-existing malformed-envelope and partial-publication concerns remain explicitly allocated to MESSAGING-005.

### Architectural Concerns

None within the pure extraction. Publication is intentionally not made transactional in this task.

## Architect Review

### Review Status

Accepted — Attempt 1 (2026-10-11).

### Review Notes

The extraction conforms to the accepted ARCH-034 division of responsibilities. The route remains <=150 lines, the focused dispatcher remains <=200 lines, and no event interpretation or queue semantics changed. Existing known rejection and partial-publication behaviour was intentionally retained for MESSAGING-005. Developer-reported validation was accepted under the established manual-patch workflow with that execution deviation recorded.

### Reviewed Files

`app/routes/whatsapp.tsx`, `app/lib/whatsapp/webhook-dispatch.server.ts`, `tests/whatsapp-webhook-dispatch.test.mjs`, `tests/whatsapp-webhook-route.test.mjs`, plus the accepted normalization/authentication/publisher modules consumed unchanged.

### Validation Reviewed

Developer: all tests/typecheck/build/diff checks green (counts/logs not supplied). Isolated behavioural comparison 12/12 and new tests 11/11 were reported with substitute Shared validators. Reconstructed post-M004 source and its four-file change scope were inspected; no developer machine test process or dedicated task-worktree use is claimed.

### Architecture Conformance

Conforms. MESSAGING-005 is now the sole owner of the intentional hardening change and may proceed after this acceptance is applied.

### Follow-up

Promote `ARCH-034-MESSAGING-005` to Ready. Keep `ARCH-034-SYSTEM-TEST-001` Pending until MESSAGING-005 is accepted Complete. No domain `_index.md` updates in this session.
