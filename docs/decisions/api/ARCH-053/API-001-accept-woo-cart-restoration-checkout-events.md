---
id: ARCH-053-API-001
architecture_id: ARCH-053
title: Extend canonical Woo activity v1 with restoration and verified phone
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-053-SHARED-002
enables:
- ARCH-053-WOOCOMMERCE-001
created: 2026-10-29
updated: 2026-10-30
---

# ARCH-053-API-001 — Extend canonical Woo activity v1 with restoration and verified phone

## Architecture

Architecture ID: `ARCH-053`. Document: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Coordinator: `moda_architect`. Materialised and accepted Complete at Attempt 1. Parent and API implementation task branches are published; no API-only deployment is authorized.

## Objective

Extend the **existing** authenticated WooCommerce `CHECKOUT_UPDATED` activity contract to carry the full restore snapshot and canonical phone proof under one `woo.activity.v1` HTTP version, while publishing the existing `woo.activity.v1` BullMQ job. Do not create `woo.activity.v3` or preserve an unnecessary HTTP v2/v3 compatibility layer.

## Context

The inspected snapshot is dated 2026-10-30 07:59. ARCH-052 owns dynamic discount discovery and is not a checkout-URL implementation domain. ARCH-048-BACKGROUND-007..011 task files are present, but none has been accepted Complete in this snapshot (007 Ready, 008–011 Pending). This task is **Pending** from the snapshot/dependency inventory, subject to fresh launcher re-gating.

## Scope

Repository: **`moda-interact-api` only**. Inspect the actual files before editing; the following paths are the explicit source ownership boundary:

- `src/woocommerce/activity/contract.ts`: extend `WooCheckoutSnapshot` with `restoration?: WooCartRestoreSnapshotV1` imported from the **published** `@modainteract/moda-interact-shared/woocommerce` entrypoint; validate it at runtime using `WooCartRestoreSnapshotV1Schema`. Remove `WOO_ACTIVITY_PHONE_VERSION` and the HTTP v2-only `parseWooCheckoutPhoneEvent()` branch. Preserve `WOO_ACTIVITY_VERSION = 'woo.activity.v1'` for both checkout and order events, and keep the v1 queue job shape with the additive optional `checkout.restoration`.
- `src/woocommerce/activity/request.ts`: continue strict JSON/body/header validation using `parseWooActivityEvent`; reject unknown versions (including v2 and v3) and retain the 65,536-byte body cap. No new endpoint or content type.
- `src/woocommerce/activity/producer.ts` and `redis-producer.ts`: change only if needed to preserve validated restoration in the existing deterministic job, digest and replay path. Keep queue names, IDs, retry/backoff, retention and durable acceptance point exactly as currently implemented.
- `tests/unit/woocommerce/activity/*.test.ts` and, only if necessary, `scripts/test-arch035-woo-activity-redis.mjs`: update the existing phone-version tests to target v1, add restore/queue/replay tests, and assert strict v2/v3 rejection. Do not leave tests asserting v2 HTTP acceptance in the new canonical contract.
- Existing route/authentication files only if the current implementation actually requires a bounded change; report any broader ownership/design problem to `moda_architect`.

No changes to API-002 link resolution, API-003 outbound-offer evidence, WordPress source, Background source, Prisma schema or another task definition.

## Out of Scope

No new event version, parallel parser, compatibility adapter, alternate queue, activity endpoint, eventType, REST resolver, coupon validity calculation, live Woo provider call, consent creation, checkout URL generation or database admission. No existing order event contract changes. Do not touch ARCH-052 discount discovery or ARCH-048 recovery-generation ownership.

## Requirements

1. **One v1 request contract.** Authentication through existing `WooInstallationAuthenticator` occurs before parsing. HTTP `POST /v1/woocommerce/activity` `CHECKOUT_UPDATED` has `schemaVersion: 'woo.activity.v1'`, unchanged top-level eventId, checkoutKey and ISO `occurredAt`, and `checkout: {currency, total, items?, contact?, restoration?}`. The `restoration` field is optional for missing/unknown cart evidence but, when present, must match the published Shared discriminated supported/unsupported schema. Never infer `appliedCouponCodes: []` from absence. Reject unrecognised keys and any v2/v3 version.
2. **Preserve v2 phone proof without its version.** For HTTP checkout `contact` with `phone`, `canonicalPhone` (digits-only E.164 without `+`) is mandatory; `verifiedCountryCode` remains optional but, if supplied, must match the existing two-letter validation. Verify `normalizeRecipientPhone(phone, {verifiedCountryCode?})` succeeds and `.e164.slice(1) === canonicalPhone`. Neither proof field may exist when `phone` is absent. Reject mismatches, unverified international/national context or malformed proof; never silently accept a raw unverified phone. An HTTP checkout without phone is allowed. Phone evidence never grants marketing consent.
3. **Existing v1 queue projection.** Use `parseWooCheckoutEvent`/`parseWooActivityEvent` to create the normalized `WooCheckoutEvent`/`WooCheckoutJob`. The queue contains verified `contact.phone` as E.164 with leading `+`, and MUST NOT include `canonicalPhone` or `verifiedCountryCode`; copy the validated `checkout.restoration` structurally unchanged, including full originally applied coupon codes. Queue `schemaVersion` is still `'woo.activity.v1'` and the queue remains `woo-checkout-capture-v1`, job `checkout-updated`. Do not change `woo-order-capture-v1` or order event semantics.
4. **Existing identity and replay.** Preserve authenticated tenant scope (never accept caller-supplied `shopId`), eventId, occurredAt, deterministic BullMQ job ID and content digest derived from the entire validated normalized event. Identical replay is idempotent; same eventId with different restoration data triggers the existing replay conflict. Failure of the queue's durable acceptance must return the existing retryable failure status; do not acknowledge before acceptance.
5. **Invalid input and safety.** Enforce body cap 65,536 bytes before JSON parse; Shared validator enforces line/coupon shape, types, cardinalities and unknown-field rejection, never Woo business eligibility. Keep existing 4xx/503 mapping and bounded shared structured logs without raw cart, codes, tokens or PII. Never do WordPress network calls inside API ingest.
6. **Pre-production cutover.** No consumer is known to need HTTP v2 compatibility in production; do not manufacture adapters. API-001 and WooCommerce-001 **must be integrated as one pre-production release**: existing test installations emitting HTTP v2 must not be pointed to the strict v1-only API until their plugin is updated. Do not deploy an intermediate API-only change. A retained test queue is explicitly drained or safely retained after a conscious developer decision, never silently deleted.


### Mandatory workflow/security invariants

- Before claiming the task, inspect the parent ARCH-053 architecture, `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/developer-task-workflow.md`, `docs/task-definition-materialization.md`, accepted dependencies and launcher-prepared dedicated parent/implementation worktree evidence. Use only the assigned task worktree/branch, update only this task's execution fields and Completion Report, and do not claim any commit/push without Git evidence.
- Never invent a local substitute for the published Shared restore schema or change cross-repository contracts independently. Return missing contracts, incompatible task dependencies and provider-boundary issues to `moda_architect` before implementing a workaround. Do not change task status to Complete yourself.
- Application runtime errors must not be swallowed. Reuse `@modainteract/moda-interact-shared/logging` for structured Node logs, with bounded event codes and non-sensitive identities. Never log phone values, customer contact details, coupon codes, full cart payloads, restoration URL tokens, authorization headers or secrets; logging/telemetry failure must not change business correctness.
- Preserve installation authentication, tenant isolation, consent/STOP, order and final-send fences. The plugin cannot directly access hosted PostgreSQL/Redis, the API cannot modify Woo sessions, and this task must not activate Woo production WhatsApp sends or introduce cross-generation outreach limits.
- When the defined acceptance and validation evidence is complete, set task to review with full Completion Report and STOP. No follow-on tasks, main merges or changes outside the authorized repository and task metadata.

## Work Items

- [x] Replace the v2-specific HTTP parser/version branch with one strict v1 checkout input parser retaining all existing verified-phone checks; leave order v1 parser unchanged.
- [x] Import the published `WooCartRestoreSnapshotV1Schema`/type and support `checkout.restoration` in `WooCheckoutSnapshot` and v1 queue projection without service-local copied Zod schemas.
- [x] Update request/producer only as required so the validated restoration is included in job content digest and retained replay semantics.
- [x] Rewrite existing v2 phone tests as v1 acceptance/rejection tests and cover v2/v3 rejection, original coupon fidelity, supported/unsupported snapshots, missing snapshot, no-phone checkout, and unchanged order events.
- [x] Record that API and Woo plugin changes require a coordinated pre-production cutover, not an independent API deployment.

## Interfaces / Contracts

**Contract owner:** API for the complete activity envelope and verified phone projection; Shared for `WooCartRestoreSnapshotV1Schema` and `WooCartRestoreSnapshotV1` as published by `ARCH-053-SHARED-002`. Producer: WooCommerce-001; queue consumer: Background-001. No new Shared phone schema.

**HTTP checkout event (complete illustrative valid v1 payload):**

```json
{
  "schemaVersion": "woo.activity.v1",
  "eventId": "woo-0123456789abcdef0123456789abcdef",
  "eventType": "CHECKOUT_UPDATED",
  "checkoutKey": "woo-original-checkout-001",
  "occurredAt": "2026-10-30T07:00:00.000Z",
  "checkout": {
    "currency": "GBP",
    "total": "90.00",
    "items": [{"productId": "101", "title": "T-shirt", "quantity": 2}],
    "contact": {
      "phone": "+447700900123",
      "canonicalPhone": "447700900123",
      "verifiedCountryCode": "GB"
    },
    "restoration": {
      "schemaVersion": "woo.cart-restore.v1",
      "kind": "supported",
      "appliedCouponCodes": ["SAVE10"],
      "lines": [{"productId": "101", "quantity": 2}]
    }
  }
}
```

**Normalized BullMQ checkout job** has the same `eventId`, `checkoutKey`, `occurredAt`, currency, total, items and restoration plus an **authenticated** `shopId` and existing `contentDigest`, but `contact` is exactly `{ "phone": "+447700900123" }` (no `canonicalPhone` or `verifiedCountryCode`). The job's `schemaVersion` remains `woo.activity.v1`. The projection must preserve any other allowed, validated contact fields such as email and name.

**Normative signatures (existing names, extended, no new v3):**

```typescript
import type { WooCartRestoreSnapshotV1 } from "@modainteract/moda-interact-shared/woocommerce";

interface WooCheckoutSnapshot {
  currency: string;
  total: string;
  items?: WooCheckoutItem[];
  contact?: WooCheckoutContact;
  restoration?: WooCartRestoreSnapshotV1;
}

// HTTP-only proof fields may occur in input, but never in WooCheckoutJob.
// HTTP version constant: WOO_ACTIVITY_VERSION = "woo.activity.v1";
// Queue: WOO_CHECKOUT_QUEUE = "woo-checkout-capture-v1".
```

For HTTP checkout with no phone, omit `phone`, `canonicalPhone` and `verifiedCountryCode` together; do not reject the restorable basket merely because a phone could not be verified by Woo. For orders retain the existing `'woo.activity.v1'` order envelope and separate order queue. Invalid restoration is 400, never silently dropped or converted into `kind:'unsupported'` by the API.

## Dependencies

- `ARCH-053-SHARED-002` (must be architect-accepted Complete)

## Enables

- `ARCH-053-WOOCOMMERCE-001`

## Acceptance Criteria

- [x] The valid HTTP example parses on `woo.activity.v1` and produces a v1 queue job containing identical restorable lines and original coupon codes; HTTP-only phone proof is removed and phone is E.164.
- [x] v1 checkout with no phone (and no proof fields) still enqueues valid product/restoration data; v1 with phone but missing/mismatched proof fails closed; proof fields without a phone fail.
- [x] `woo.activity.v2`, `woo.activity.v3`, malformed input, unknown fields, bad coupon/line shape or over-65,536-byte body cannot enqueue; no dual-version compatibility code remains.
- [x] Absent restoration stays absent; `kind:'unsupported'` stays unsupported; neither is treated as empty coupon list or restorable supported basket.
- [x] Duplicate eventId with same normalized validated event is idempotent; different coupon/line/attributes for same eventId causes replay conflict, not overwrite.
- [x] Existing `ORDER_PLACED`, `ORDER_PAID`, `ORDER_CANCELLED` v1 parsing and queues remain unchanged, as do tenant authentication, publisher durability/retries and consent separation.
- [x] The developer's integration handoff explicitly says API-001 cannot be deployed independently ahead of a compatible WooCommerce-001 producer.
- [x] No unrelated repository/source changes or ARCH-052 contract changes.

## Validation

- [x] `npm run test:arch035-woo-activity:unit` (existing contract/phone/replay suite revised to v1)
- [ ] `npm run test:arch035-woo-activity:redis` with the declared isolated Redis environment when available; otherwise record the blocked validation and do not mark it passed
- [x] `npm run typecheck` and `npm run lint`
- [x] Focused tests proving v1 only, exact validated Shared restore snapshots, normalized phone, no-phone, and order regression
- [x] `git diff --check`; record each exact command/result in Completion Report

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are complete, update ONLY this task's authorised execution metadata, checklists and Completion Report, set `status: review` and return to `moda_architect`; **STOP**. Do not begin Enables, merge task branches, push `main` or change Architect Review yourself.

## Implementation Notes

The existing source already has `WOO_ACTIVITY_VERSION = 'woo.activity.v1'`, a v2 phone-specific `WOO_ACTIVITY_PHONE_VERSION`, and a v1 BullMQ publisher. Remove the **HTTP version split**, not the existing safety validation: move the working v2 phone-proof rules into the sole v1 checkout parser, then enrich that same normalized v1 queue event with Shared-validated restoration. Tests must use the published Shared contract, not a repository-local clone. No schema/migration task, queue migration or consumer-version task is justified for this change.

Task dependency files record *source* readiness, not permission to deploy intermediate incompatible pieces to live test installations. Deployment/activation of strict v1 API and updated v1 Woo plugin is one coordinated, non-production change. If actual production or retained externally consumed v2 events are discovered, **stop for architect reclassification** rather than invent compatibility adapters.

## Completion Report

### Status

Accepted Complete at Attempt 1 by the architect. The Redis integration validation remains explicitly blocked because Docker is unavailable; it was not reported as passed.

### Files Changed

- `moda-interact-api/package.json` and `package-lock.json` — pin the accepted published Shared package at 2.8.0.
- `moda-interact-api/src/woocommerce/activity/contract.ts` — one strict v1 parser, verified phone normalization/proof stripping, and Shared-validated optional restoration.
- `moda-interact-api/src/woocommerce/activity/routes.ts` — bounded Shared-logger error summary for queue failures without logging provider/Redis messages.
- `moda-interact-api/openapi/woocommerce-activity-v1.yaml` — document v1 proof fields and restoration shapes.
- `moda-interact-api/tests/unit/woocommerce/activity/{contract,openapi,producer,routes}.test.ts` — v1, restore, replay, phone-free route and bounded-error coverage.

### Work Completed

- Removed the HTTP v2 phone parser/version branch. Checkout and order envelopes remain `woo.activity.v1`; v2/v3 are rejected. Phone input requires matching digits-only `canonicalPhone`, validates an optional uppercase two-letter country, normalizes through Shared `normalizeRecipientPhone`, and strips both HTTP-only proof fields from the queued event.
- Pinned `@modainteract/moda-interact-shared` to published 2.8.0 and imported its `WooCartRestoreSnapshotV1Schema` and type. Optional restoration is rejected on invalid Shared shape and projected unchanged, including supported/unsupported kind, line attributes, coupon ordering and spelling. The existing producer digest and retained replay path includes the normalized event without changing queue names or durability settings.
- Updated unit coverage for v1 and v2/v3 rejection, required phone proof, no-phone requests, supported/unsupported/absent restoration, malformed Shared snapshots, order regression, queue projection, and restoration replay conflict. OpenAPI now reflects the contract.
- Recorded the required coordinated pre-production handoff: API-001 must not deploy independently before the compatible WooCommerce-001 producer.
- Launcher preparation/claim evidence: Attempt 1 claimed at `2026-10-30T14:48:24Z`; canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-053-API-001` on `task/ARCH-053-API-001`, synchronized starting HEAD `6ae519e7147c05fc286de519055a4f8ffc47e2b2`; API implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-053-API-001` on `task/ARCH-053-API-001`, synchronized starting HEAD `5efb9f40ff4917ae5efec947b82ab19bd6559e31`. At launch both remote task branches needed no fast-forward and `origin/main` was already current. Recursive submodules were initialized at their recorded commits; the Shared dependency gate passed.
- Implementation commit: `30df9848cc2e1d9026afc94f3a120c9318162ffe` on the API task branch.

### Validation Results

- PASS — `npm run test:arch035-woo-activity:unit`: 24 tests passed, 0 failed. Coverage includes the authenticated route, v1-only version checks, phone-proof projection, phone-free restoration enqueue, Shared supported/unsupported schema cases, order regressions, and retained replay conflict on changed restoration.
- BLOCKED — `npm run test:arch035-woo-activity:redis` was not run because Docker is unavailable to this environment. `docker info --format '{{.ServerVersion}}'` failed with permission denied connecting to `unix:///Users/kwadwoadomafriyie/.colima/default/docker.sock`; therefore the declared disposable Redis/BullMQ integration remains unverified.
- PASS — `npm run typecheck` (including Prisma client generation).
- PASS — `npm run lint` (`eslint . --max-warnings=0`).
- PASS — `git diff --check`.

### Deviations

The Redis integration could not run because the configured Docker daemon socket is inaccessible. It is explicitly left unchecked above and is not reported as passed.

### Assumptions

`ARCH-053-SHARED-002` is accepted Complete and its published package is 2.8.0. The architecture's pre-production cutover requirement applies: API-001 and WooCommerce-001 must be integrated together; no live production v2 consumer was identified by this task.

### Unresolved Issues

The disposable Redis/BullMQ integration remains unverified until Docker is available. Unit-level publisher replay and durability behavior passed.

### Architectural Concerns

The downstream WooCommerce producer must be released in the same coordinated pre-production cutover. Do not deploy the strict v1 API independently ahead of WooCommerce-001.

## Architect Review — Attempt 1 (Accepted)

### Review Status

Accepted. The API contract, validation and v1 queue projection meet this task's acceptance criteria. Mark Complete at Attempt 1. This does not authorize API-only deployment; the updated WooCommerce producer must be integrated in the coordinated pre-production cutover.

### Review Notes

The implementation removes the HTTP version split while retaining strict v1 checkout and order handling. Phone proof is required and normalized when a phone is present, stripped before queueing, and does not create consent. The published Shared restoration schema validates the optional snapshot; the normalized event, original coupon evidence and restoration data flow into the existing digest and retained replay conflict logic. Tenant identity remains server-derived, the request body remains bounded, and queue failures preserve the retryable 503 boundary with bounded logging. No unrelated source ownership or ARCH-052 work was changed.

The OpenAPI schema documents the restoration shape and phone proof. It is less strict than the published Shared runtime schema for control characters in coupon and variation-attribute text; the Shared validator remains authoritative and rejects those values. This documentation limitation does not change runtime acceptance behavior.

### Reviewed Files

Reviewed the implementation diff in `src/woocommerce/activity/contract.ts`, `src/woocommerce/activity/routes.ts`, `openapi/woocommerce-activity-v1.yaml`, and the contract, producer, route and OpenAPI tests, plus the Completion Report.

### Validation Reviewed

The report records 24 passing unit tests, typecheck, lint and `git diff --check`. The declared disposable Redis/BullMQ integration could not run because Docker access to the configured Colima socket was denied. That validation remains unchecked and is not represented as passing; this limitation was permitted by the task's explicit “when available” condition. Tests were not rerun during architect review.

### Architecture Conformance

The strict v1 API is not to be deployed independently ahead of WOOCOMMERCE-001. Both API-001 and BACKGROUND-001 are now accepted Complete, so WOOCOMMERCE-001 is dependency-ready. No production activation or deployment is included in this acceptance.

### Follow-up

Keep the Redis/BullMQ integration validation visible as outstanding until Docker is available. Promote WOOCOMMERCE-001 to Ready; API-002 is also Ready from its completed SHARED-002 and DATABASE-001 prerequisites. No system-test task is promoted.
