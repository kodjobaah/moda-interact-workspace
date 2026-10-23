---
id: ARCH-045-SHOPIFY-001
architecture_id: ARCH-045
title: Enqueue authenticated Shopify WhatsApp consent-state sync
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-045-SHARED-002
enables:
  - ARCH-045-BACKGROUND-003
  - ARCH-045-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-22
---
# Enqueue authenticated Shopify WhatsApp consent-state sync

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** portable definition, **not** materialised in a developer task worktree or committed/pushed; no execution claim exists.

## Objective

Subscribe to Shopify WhatsApp consent-change webhooks and enqueue only a **current-state refresh signal** on the existing Shopify webhook pipeline; never schedule or materialise a checkout recovery.

## Context

Current authenticated ingress normalises checkout/cart/order/discount topics only. Extend the live authoritative app subscription and queue routing using the published Shared sync-event contract, without GraphQL calls or checkout state lookups inside the webhook request.

## Scope

- Verify the actual deployed Shopify app TOML/config, selected API version, `customers_whats_app_marketing_consent/update` topic, `read_customers` scope/installed grant and protected customer-data approval. ARCH-045 does **not** use `write_customers` or Shopify mutations: WhatsApp STOP is a local Moda restriction and merchant Support notice, not a Shopify consent write. Preserve HMAC-authenticated ingress and inactive-shop boundaries.
- Normalise strict `(shopId,shopifyCustomerId,deliveryId,triggeredAt)` metadata and enqueue the Shared **sync event** under its distinct job name on an existing Shopify queue. Acknowledge only after durable enqueue.
- Keep webhook contents free of permission assertion, phone/email and checkout IDs; no `CheckoutRecovery`, pending candidate, merchant notice or GraphQL lookup in HTTP handler.
- Test real subscription config, duplicate retries, HMAC reject, queue failure and route isolation.

## Out of Scope

- No consent-authority query or DB projection in this repository; Background owns that.
- No CMP tracking implementation, recovery scheduling/rediscovery or separate BullMQ queue.

## Requirements

- [ ] Webhook publication is authenticated, tenant-safe, idempotent and uses published Shared v1 schema.
- [ ] Consent change does not trigger checkout reconciliation; it only updates current CustomerPhone asynchronously.
- [ ] Existing checkout/order/discount queue semantics remain intact.

- **H1:** Validate Shopify webhook numeric `customer_id` and canonical `gid://shopify/Customer/...` through the published Shared identity helper; reject malformed, wrong-resource, ambiguous or cross-shop identifiers. Use one canonical conversion for the consent-sync boundary, not locally duplicated ID parsing.
- **H2:** Identify which Shopify app TOML is actually deployed and verify the `customers_whats_app_marketing_consent/update` subscription, selected API version, active installed scopes, and protected customer data approval. A TOML declaration or HTTP 200 GraphQL response with errors is not proof of field access.
- Preserve webhook HMAC, low-latency durable acceptance and bounded payload. Neither webhook delivery nor its retry schedules checkout reconcilation, recipient messaging or a recovery job.

## Work Items

- [ ] Validate live Shopify app config/scope/topic.
- [ ] Add sync-event classification/publication on existing queue.
- [ ] Add focused ingress/queue failure/security tests.

- [ ] Test real numeric-ID webhook fixture, GID normalisation, GraphQL customer ID equality, wrong shop and invalid topic/API version.
- [ ] Record the selected deployed TOML/app scopes and a non-production GraphQL field-access smoke or an explicit access blocker; do not assume token access.
- [ ] Validate that an authorised installed-shop token can read the current customer WhatsApp consent (including protected data approval), not just receive the webhook. Record any required read-scope re-authorisation, and do **not** add `write_customers` merely for STOP handling.

## Interfaces / Contracts

Produces ARCH-045-SHARED-001/002 published `ShopifyWhatsAppConsentSyncJobV1Schema` job. Consumed by ARCH-045-BACKGROUND-003 to refresh `CustomerPhone` only, not to create recovery.

## Dependencies

- `ARCH-045-SHARED-002`

## Enables

- `ARCH-045-BACKGROUND-003`
- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Authenticated consent webhook reliably publishes one validated sync hint before 2xx.
- [ ] Duplicate/reordered webhook, unknown shop and malformed ID cannot change another tenant or trigger recovery.
- [ ] No new queue, phone/PII payload or checkout re-evaluation at ingress.

- [ ] Authenticated webhook works with published Shared identity helper; a malformed ID does not create a job, and the deployed app configuration is verified rather than inferred.
- [ ] The selected installed app has confirmed **read** access to the required consent field; no Shopify write scope or STOP-to-Shopify mutation is a release prerequisite.

## Validation

- [ ] Targeted Shopify webhook HMAC/publish/queue-failure tests, actual app config subscription verification, repository-declared checks and `git diff --check`.

- [ ] HMAC/duplicate/tenant/API field-denied tests; actual non-production Shopify token permission smoke if available (report pending if not).

## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. For publication task, do not rerun implementation validation.

## Implementation Notes

Do not infer runtime config from filename. Shopify 2026-07 documented webhook payload uses `customer_id` and `phone_number`; never use webhook phone as identity/permission for admission. Existing `recordShopifyWebhookOutcome` is reusable.

Before claiming, use the deterministic `/moda-task` launcher and its **actual** prepared packet, read the task's complete current Architect Review, and verify task/dependency status in the developer's canonical workspace. Preserve `docs/decisions/**/_index.md` untouched until the developer explicitly closes the architecture documentation session. New runtime structured logging uses `@modainteract/moda-interact-shared/logging` where applicable. No source outside this task's owner repository may be changed unless explicitly authorised by the architecture.

## Completion Report

### Status

Not Started — external portable definition, not materialised.

### Files Changed

None — not implemented.

### Work Completed

None.

### Validation Results

Not run; the supplied snapshot is not the developer's task worktree.

### Deviations

None.

### Assumptions

Use the 2026-10-20 snapshot for orientation; revalidate active code/configuration when the task is materially claimed. ARCH-045 does not impose a consent-expiry window; current Shopify consent and actual checkout eligibility are separate.

### Unresolved Issues

None recorded at definition time; report any discovered cross-repository dependency rather than implementing outside ownership.

### Architectural Concerns

None recorded at definition time.

## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

None.

### Reviewed Files

None — portable definition only.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.

## Developer Takeover

On 2026-10-23, `/moda_developer_create ARCH-045-SHOPIFY-001` was invoked while this task was ready and agent-owned. This is an explicit developer takeover. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_app`, repository ownership, dependencies, scope and acceptance criteria are unchanged. The canonical launcher will claim Attempt 1 after worktree preparation.

**2026-10-22 architect coordination:** Promoted `pending -> ready` because all declared dependencies in the supplied snapshot are `complete`. Task remains unclaimed (`executor: null`, `claimed_at: null`, `attempt: 0`). This eligibility change does not materialise a branch/worktree or start implementation.
