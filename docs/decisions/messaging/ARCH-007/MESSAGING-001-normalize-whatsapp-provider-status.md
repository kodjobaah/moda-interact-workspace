---
id: ARCH-007-MESSAGING-001
architecture_id: ARCH-007
title: Publish canonical WhatsApp provider-status events for billing/accounting consumers
task_kind: implementation
domain: messaging
repository: moda-interact-messaging
assigned_agent: moda_messaging
coordinator: moda_architect
status: complete
priority: 60
executor: null
claimed_at: null
attempt: 3
depends_on: 
  - ARCH-007-SHARED-002
  - ARCH-007-SHARED-004
enables: 
  - ARCH-007-BACKGROUND-005
  - ARCH-007-SYSTEM-TEST-003
created: 2026-09-07
updated: 2026-09-08
---

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

# ARCH-007-MESSAGING-001: Publish canonical WhatsApp provider-status events for billing/accounting consumers

## Architecture

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Extend Meta status webhook handling so verified status notifications are normalized and durably published using the accepted Shared provider-status contract.

## Context

Billing/safety accounting needs provider message lifecycle without making Messaging own billing entitlement. Existing messaging ingress already validates/normalizes inbound Meta events; this task adds only the provider-status branch needed by Background.

## Scope

Meta webhook status parsing/normalization/publication and focused tests in `moda-interact-messaging`. Consume exact Shared release.

## Out of Scope

- Updating ConversationMessage/UsageEvent in the database directly from Messaging.
- Computing merchant charges or Meta cost.
- Background status application.

## Requirements

- Accept only webhook status notifications that pass existing Meta verification/security.
- Extract providerMessageId, normalized supported status, authoritative occurredAt and shop/provider-account routing identity already available to the ingress.
- Capture optional bounded Meta pricing/category metadata only if actually present in the verified payload. Do not fabricate monetary cost or retain full webhook payload.
- Validate the normalized event with the Shared schema before publication.
- Publish to the existing architecture-approved messaging/BullMQ contract/queue path; do not create a new ad-hoc Redis channel if an accepted inbound messaging event route already exists.
- Use deterministic event/job identity so duplicate Meta status delivery is harmless downstream.
- Do not log access tokens/full customer payloads.

## Work Items

- [x] Adopt exact Shared version.
- [x] Inspect current Meta status webhook branch and queue publication.
- [x] Implement normalization/schema validation/publication.
- [x] Add tests for sent/delivered/read/failed, duplicate delivery, missing provider ID and optional metadata bounds.

## Interfaces / Contracts

Producer: `moda_messaging`
Consumer: `moda_background`
Schema: exact versioned provider-status schema from SHARED-001/002.

## Dependencies

Explicit task dependencies are authoritative in YAML frontmatter. Do not begin unless every listed dependency is architect-accepted `complete` and any accepted Shared/database artifact required by this repository is available to consume.

## Enables

- ARCH-007-BACKGROUND-005
- ARCH-007-SYSTEM-TEST-003

## Acceptance Criteria

- [x] Background can receive provider status without parsing raw Meta webhook structure.
- [x] Malformed/missing provider-message identity is rejected safely.
- [x] Duplicate provider statuses preserve deterministic identity.
- [x] No billing decision or provider cost invention occurs in Messaging.
- [x] Tests/build/validation pass.

## Validation

Inspect the repository `package.json` first. Run the focused tests required by this task plus the repository-declared typecheck/lint/build/Prisma validation that actually exists, and `git diff --check`. Do not invent missing npm scripts.

## Implementation Notes

Exact Shared dependency: `@modainteract/moda-interact-shared@0.7.4`. Import the accepted provider-status contract from that exact release; do not duplicate the schema locally.


Luna deterministic-execution guardrails:

- Treat this task file as the complete implementation contract. Do not infer additional product policy from old billing code.
- Inspect the named current implementation before editing, but if old code conflicts with ARCH-007, implement ARCH-007.
- Do not start an enabled/dependent task. Return only this task to `review` and STOP.
- Do not modify another repository except an explicitly permitted database submodule/package dependency pointer in this task.
- Do not add new billing raw SQL (`$queryRaw`, `$executeRaw`, `Prisma.sql`, raw driver SQL) to compensate for an unavailable Prisma delegate. Adopt/regenerate the accepted Prisma schema instead.
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-MESSAGING-001` branch and the mirrored parent-workspace `task/ARCH-007-MESSAGING-001` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.


## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-messaging/package.json`
- `moda-interact-messaging/package-lock.json`
- `moda-interact-messaging/app/routes/whatsapp.tsx`
- `moda-interact-messaging/tests/startup-contract.test.mjs`
- `moda-interact-messaging/tests/whatsapp-provider-status.test.mjs`

### Work Completed

- Adopted and installed exact `@modainteract/moda-interact-shared@0.7.4` provider-status v2.
- Removed the unsupported `metadata.shop_id` tenant assumption and normalized only verified `entry.id`, `metadata.phone_number_id`, and `status.id` identities.
- Added verified Meta status normalization for SENT, DELIVERED, READ, and FAILED using schema version 2.
- Validated normalized events with Shared `safeParseNormalizedWhatsAppStatus`.
- Published validated `message-status` jobs to the existing `whatsapp-events` BullMQ queue.
- Added deterministic, bounded job identity derived only from provider account, provider phone number, provider message, and status.
- Preserved only bounded optional pricing/category/model metadata; no monetary cost was fabricated.
- Removed raw webhook-body logging.
- Added realistic Meta-shaped no-`shop_id` fixtures and v2 contract assertions.
- Added `normalizeProviderStatusFromWebhook`, used by the route and focused tests, to cover extraction from realistic Meta `entry.id` and `change.value.metadata.phone_number_id` fields.

### Validation Results

- `npm test` — passed: 21 tests, 1 Redis-dependent integration test skipped because `TEST_REDIS_URL` is unset.
- `npm test -- tests/whatsapp-provider-status.test.mjs` — passed: 8 focused tests, including the realistic Meta webhook extraction regression.
- `npm run typecheck` — passed.
- `npm run build` — passed.
- `npm ls @modainteract/moda-interact-shared --depth=0` — confirmed `0.7.4`.
- `git diff --check` — passed.
- No lint or Prisma validation scripts are declared in `package.json`.

### Deviations

- Tenant/shop resolution is intentionally absent from Messaging per the v2 architecture contract; Background resolves durable tenant context from provider message identity.

### Assumptions

- Meta `entry.id` is the provider-account identity and `value.metadata.phone_number_id` is the provider phone-number identity.

### Unresolved Issues

The Redis-backed queue integration test remains skipped without `TEST_REDIS_URL`; the existing repository test suite owns that environment provision.

### Architectural Concerns

None

## Architect Review

### Review Status

Blocked

### Review Notes

Attempt 1 is not architect-acceptable because the accepted Shared
`NormalizedWhatsAppStatus` v1 contract requires `shopId`, but the verified raw
Meta webhook does not provide a tenant/shop identifier.

Direct inspection of the submitted implementation shows:

```ts
const shopId =
  typeof metadata?.shop_id === "string"
    ? metadata.shop_id.trim()
    : "";

if (!providerAccountId || !shopId || ...) {
  return null;
}
```

and the Completion Report explicitly assumes:

> Meta `entry.id` is the provider-account identity and the verified deployment
> payload supplies `metadata.shop_id` for tenant routing.

That assumption is not supported by the real Meta Cloud API status payload.
Meta status webhooks provide:

```text
entry.id                     = WhatsApp Business Account identity
value.metadata.phone_number_id
value.metadata.display_phone_number
status.id                    = provider message identity
status.status
status.timestamp
status.pricing?              = optional provider pricing/category metadata
```

They do not provide `metadata.shop_id`.

Messaging verifies the HMAC over the exact raw request body, so a gateway/body
transform cannot safely add a tenant field before this verification boundary.

The defect therefore originates in the architect-accepted Shared v1 contract,
not in a repository-local implementation choice. The task is blocked until
SHARED-003/SHARED-004 replace/publish the provider-status routing contract.

### Accepted Attempt-1 Work That May Be Reused

The following Attempt-1 implementation is directionally correct and should be
retained when this task is later unblocked:

- exact Shared dependency adoption mechanism;
- verified-webhook-only status branch;
- SENT/DELIVERED/READ/FAILED normalization;
- authoritative provider timestamp conversion;
- bounded optional pricing/category/model metadata;
- Shared safe-parse validation before publication;
- existing `whatsapp-events` / `message-status` BullMQ route;
- deterministic bounded status job identity;
- removal of raw webhook-body logging;
- focused status/duplicate/malformed tests.

### Required Architectural Dependency

New tasks:

```text
ARCH-007-SHARED-003
  Correct provider-status routing contract to schema v2
        ↓
ARCH-007-SHARED-004
  Publish @modainteract/moda-interact-shared@0.7.4
        ↓
ARCH-007-MESSAGING-001
  Re-enter as Attempt 2
```

Until SHARED-004 is architect-accepted Complete, this task MUST remain Blocked.

### When Unblocked: Attempt 2 Contract

After SHARED-004 is accepted, `moda_architect` will return this same task to
`ready` with `attempt: 1`. Attempt 2 must:

1. adopt exact `@modainteract/moda-interact-shared@0.7.4`;
2. consume provider-status schema v2;
3. derive only provider identities actually present in the verified webhook:
   - `providerAccountId = entry.id`;
   - `providerPhoneNumberId = metadata.phone_number_id`;
   - `providerMessageId = status.id`;
4. remove all `metadata.shop_id` assumptions and test fixtures;
5. publish no tenant/shop ID from Messaging;
6. let Background resolve the durable shop from its local outbound
   message/usage state using `providerMessageId`;
7. keep deterministic job identity based only on durable provider identities and
   normalized status;
8. add focused tests using a realistic Meta status payload shape with
   `metadata.phone_number_id` and no `shop_id`.

Do not introduce a database lookup into Messaging merely to manufacture
`shopId`. Tenant resolution belongs to Background's durable-state boundary.

### Reviewed Files

- `moda-interact-messaging/package.json`
- `moda-interact-messaging/package-lock.json`
- `moda-interact-messaging/app/routes/whatsapp.tsx`
- `moda-interact-messaging/app/lib/queues/whatsapp.queue.ts`
- `moda-interact-messaging/tests/whatsapp-provider-status.test.mjs`
- `moda-interact-messaging/tests/startup-contract.test.mjs`
- task Completion Report

### Validation Reviewed

Attempt 1 reported and the submitted repository supports:

- exact Shared `0.7.3` dependency;
- 20 tests passed with one Redis opt-in skip;
- typecheck passed;
- build passed;
- `git diff --check` passed.

Those validations do not remove the architectural routing defect because the
tests currently fabricate `metadata.shop_id`.

### Architecture Conformance

Blocked by cross-repository contract defect. No billing/tenant decision should
be moved into Messaging as a workaround.

### Follow-up

Complete and architect-review SHARED-003, then SHARED-004. After the corrected
Shared release is published, `moda_architect` will unblock this same task for
Attempt 2. BACKGROUND-005 remains pending.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 3 satisfies the bounded correction contract from Attempt 2. The production implementation remains architecture-conformant and the required realistic Meta webhook extraction regression is now present.

`action()` iterates `value.statuses` from the verified webhook and passes the actual `entry`, `change`, and `status` objects to the exported pure `normalizeProviderStatusFromWebhook()` helper. That helper derives `providerAccountId` from `entry.id` and `providerPhoneNumberId` from `change.value.metadata.phone_number_id`; the nested status object supplies `providerMessageId`, status, timestamp, and bounded pricing metadata. The resulting candidate is validated through Shared `safeParseNormalizedWhatsAppStatus` schema v2 before queue publication.

The focused regression uses a Meta-shaped status fixture with `entry.id`, `changes[].value.metadata.phone_number_id`, `statuses[]`, and no `shop_id`/`shopId`, and proves the expected Shared-valid v2 event. Existing SENT/DELIVERED/READ/FAILED, malformed identity, bounded pricing, and deterministic duplicate/job-ID tests remain in place.

No tenant lookup, fabricated tenant identity, new queue, duplicate provider-status schema, or billing decision was introduced. Manifest and lockfile both resolve exact `@modainteract/moda-interact-shared@0.7.4`.

### Reviewed Files

- `moda-interact-messaging/package.json`
- `moda-interact-messaging/package-lock.json`
- `moda-interact-messaging/app/routes/whatsapp.tsx`
- `moda-interact-messaging/tests/whatsapp-provider-status.test.mjs`
- `moda-interact-messaging/tests/startup-contract.test.mjs`
- task Completion Report

### Validation Reviewed

- Focused provider-status tests: 8 passed per Completion Report.
- Full repository tests: 21 passed, 1 Redis-dependent integration test skipped because `TEST_REDIS_URL` is unset.
- Typecheck: passed.
- Build: passed.
- Exact Shared dependency: `0.7.4` confirmed in manifest and lockfile.
- `git diff --check`: passed.
- Architect source inspection confirmed the Attempt-3 helper is used by `action()`, realistic payload extraction is covered, no runtime `shop_id`/`shopId` assumption remains, and deterministic status identity still excludes tenant state.

### Architecture Conformance

Accepted. `ARCH-007-MESSAGING-001` is Complete.

### Follow-up

`ARCH-007-BACKGROUND-005` is NOT Ready yet because it also depends on `ARCH-007-BACKGROUND-004`. Keep BACKGROUND-005 Pending until BACKGROUND-004 is architect-accepted Complete. `ARCH-007-SYSTEM-TEST-003` remains terminal/manual-gated and must not block unfinished implementation.
