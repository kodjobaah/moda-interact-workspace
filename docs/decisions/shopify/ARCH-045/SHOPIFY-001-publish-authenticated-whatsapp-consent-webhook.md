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
status: review
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-045-SHARED-002
enables:
  - ARCH-045-BACKGROUND-003
  - ARCH-045-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-23
---
# Enqueue authenticated Shopify WhatsApp consent-state sync

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** Developer-owned Attempt 1, submitted for architectural review on 2026-10-23. The task was already materialised and claimed as `executor: developer` at `2026-10-23T10:43:38Z` (recorded in the original task YAML); its implementation commit `56d96bd` was pushed on the Shopify `task/ARCH-045-SHOPIFY-001` branch. This handoff clears the active claim in the review state without changing `execution_mode: developer` or `completion_mode: developer`. The parent task/report commit is separate, and architect acceptance plus explicit developer completion remain outstanding.

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

- [x] Webhook publication is authenticated, tenant-safe, idempotent and uses published Shared v1 schema (verified in focused tests; real-provider delivery is not yet verified).
- [ ] Consent change does not trigger checkout reconciliation; it only updates current CustomerPhone asynchronously.
- [x] Existing checkout/order/discount queue semantics remain intact in the focused regression suite.

- **H1:** Validate Shopify webhook numeric `customer_id` and canonical `gid://shopify/Customer/...` through the published Shared identity helper; reject malformed, wrong-resource, ambiguous or cross-shop identifiers. Use one canonical conversion for the consent-sync boundary, not locally duplicated ID parsing.
- **H2:** Identify which Shopify app TOML is actually deployed and verify the `customers_whats_app_marketing_consent/update` subscription, selected API version, active installed scopes, and protected customer data approval. A TOML declaration or HTTP 200 GraphQL response with errors is not proof of field access.
- Preserve webhook HMAC, low-latency durable acceptance and bounded payload. Neither webhook delivery nor its retry schedules checkout reconcilation, recipient messaging or a recovery job.

## Work Items

- [ ] Validate live Shopify app config/scope/topic.
- [x] Add sync-event classification/publication on existing queue.
- [x] Add focused ingress/queue failure/security tests.

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

- [x] Authenticated consent webhook publishes one validated sync hint before a 2xx in focused tests; live webhook delivery remains unverified.
- [x] Duplicate delivery, unknown/inactive shop and malformed ID do not publish cross-tenant or recovery work in focused tests; end-to-end ordering is reserved for integration/system validation.
- [x] No new queue, phone/PII payload or checkout re-evaluation at ingress.

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

**Submitted for architect review — developer Attempt 1 (2026-10-23).** Source implementation committed and pushed to the Shopify task branch as `56d96bd`. The developer takeover and original claim are evidenced in this task's existing metadata and appended history. This is **not** architect acceptance, a passing developer self-review or a `complete` task. Required live Shopify permission and deployment checks are **not evidenced**, so acceptance must remain subject to explicit review.

### Files Changed

Shopify implementation commit `56d96bd`: 13 files, 648 insertions, 43 deletions.

- `app/routes/webhooks/root/route.jsx`
- `app/services/webhooks/shopify-webhook-ingress.service.ts`
- `app/services/webhooks/shopify-webhook-queue.server.ts`
- `app/services/webhooks/shopify-whatsapp-consent-normalization.ts` (new)
- `docs/arch-045/SHOPIFY-001-consent-ingress-verification.md` (new)
- `package.json`; `package-lock.json`
- `shopify.app.moda-interact.toml`
- `tests/unit/webhooks/shopify-webhook-ingress.service.test.js`
- `tests/unit/webhooks/shopify-webhook-queue.server.test.js`
- `tests/unit/webhooks/shopify-whatsapp-consent-config.test.js` (new)
- `tests/unit/webhooks/shopify-whatsapp-consent-normalization.test.ts` (new)
- `tests/unit/webhooks/webhooks-route.test.js`

This review-submission patch changes **only the current parent task file**; it does not alter implementation source, parent architecture or any `_index.md`.

### Work Completed

- Added `customers_whats_app_marketing_consent/update` to the named `shopify.app.moda-interact.toml` (`2026-07`) existing webhook subscription, without introducing Shopify customer-write scope or STOP-to-Shopify mutation. **Deployment of this named TOML remains unconfirmed.**
- Kept authenticated Shopify webhook handling. Extracted strict, lossless raw numeric `customer_id` / canonical Customer GID identity and validated it with the published Shared identity helper; rejects malformed, contradictory and wrong-resource IDs.
- Published a minimal Shared `ShopifyWhatsAppConsentSyncJobV1Schema` hint containing `schemaVersion`, `shopId`, `shopifyCustomerId`, `deliveryId`, `triggeredAt` to the existing `checkout-events` queue under the distinct `shopify-whatsapp-consent-sync` name; no phone, provider consent decision, checkout ID, recovery creation or outbound send at ingress.
- Preserved unknown/inactive-shop quarantine and retryable queue-publish failures; pinned the consumed Shared package to `@modainteract/moda-interact-shared@2.5.0`.
- Added focused routing, HMAC, customer-ID precision, tenant, queue, duplicate, malformed-ID, API-version and configuration tests.
- Applied a separate incremental TypeScript correction for the BullMQ job-name typing error **within the same claimed developer Attempt 1**. The final implementation was published as one commit (`56d96bd`).

### Validation Results

Developer terminal evidence from 2026-10-23:

- `npm run prisma:generate` — **PASS** (Prisma Client v6.19.3 generated).
- `npm run typecheck` — **PASS** after Prisma generation and the BullMQ typing correction.
- `npm run lint` — **PASS**; no errors reported.
- Focused `npx vitest run` (webhook ingress, webhook queue, route, consent normalization, consent configuration) — **PASS: 5/5 suites, 76/76 tests** (37 + 15 + 5 + 17 + 2).
- `git diff --check` and `git diff --cached --check` — **PASS**, no whitespace errors reported.
- `git diff --cached --stat` — 13 files, 648 insertions, 43 deletions.
- `git commit -m "feat(ARCH-045-SHOPIFY-001): enqueue authenticated consent sync"` — **PASS**, short commit `56d96bd`.
- `git push origin task/ARCH-045-SHOPIFY-001` — **PASS** to `https://github.com/kodjobaah/moda-interact.git`.
- **NOT RUN / NOT EVIDENCED:** complete repository build, deployed app TOML / webhook subscription verification, active installed token's `read_customers` grant and protected-customer-data approval, non-production GraphQL field-access smoke, and a real signed webhook-to-queue/Background-consumer smoke. These remain unchecked in Work Items, Acceptance Criteria and Validation above.

### Deviations

- Explicit developer takeover is already recorded in the task: `execution_mode: developer`, `completion_mode: developer`, Attempt 1 claimed at `2026-10-23T10:43:38Z`. Preserve this ownership; do not revert to agent/automatic mode. The earlier handoff patch assumed the stale Ready/Attempt 0 state, which caused its application failure.
- Attempt 1 was delivered via two incremental source patches before the final single Shopify implementation commit. The first generated a BullMQ typing error, corrected and revalidated before commit.
- A launcher-generated preparation packet and corresponding start-of-attempt **parent/implementation worktree synchronization evidence** were not included in the material reviewed here. The claimed timestamp is evidenced in the task YAML; physical-isolation and synchronization evidence are **not independently verified** by this ZIP.
- Outstanding live-provider requirements are not treated as passed or waived merely because source-only validation passed.

### Assumptions

- `shopify.app.moda-interact.toml` is the intended source candidate; it is not confirmed as the Shopify CLI-deployed configuration. TOML `read_customers` is not proof of the currently installed app's protected data access.
- `ARCH-045-BACKGROUND-003` is the separate consumer of the Shared consent-sync hint. Until the consumer and rollout are verified, successful ingress tests do not demonstrate durable `CustomerPhone` update or end-to-end consent convergence.

### Unresolved Issues

- Confirm selected Shopify app, deployed TOML and webhook topic, installed `read_customers` grant, protected-customer-data approval, and a read-only customer-consent GraphQL field-access smoke on a non-production shop; check GraphQL `errors` and precise customer GID equality.
- Verify a real, HMAC-valid consent webhook is durably enqueued; validate consumer compatibility and the required release order before enabling webhook traffic.
- Provide the launcher-resolved canonical parent/implementation worktree and start-of-attempt sync evidence for final governance review. Do not invent worktree paths or preparation output.
- The unchecked requirements, Work Items, Acceptance Criteria and Validation must be completed or explicitly dispositioned by the responsible reviewer. No completed review or developer completion is asserted.

### Architectural Concerns

- A Shopify consent-change event is a **refresh hint**, not consent authority. The Background consumer must fetch current Shopify consent and respect independent Moda-local STOP restrictions; ingress must never create `CheckoutRecovery`.
- Enabling a distinct queue job without the compatible Background consumer risks unprocessed events; enforce rollout sequencing.

### Git / VCS

- **Implementation repository:** `moda-interact`, branch `task/ARCH-045-SHOPIFY-001`; committed and pushed short SHA `56d96bd` (full SHA not provided by developer output). No merge to `main` is evidenced.
- **Parent workspace branch:** `task/ARCH-045-SHOPIFY-001` in the dedicated parent worktree. This handoff is a proposed documentation edit; its parent commit/push are not yet evidenced.
- **Developer claim:** `claimed_at: 2026-10-23T10:43:38Z` in the uploaded task; transitioned from the existing claimed Attempt 1 to review without fabricating another claim or Attempt 2.
- **Physical worktree and synchronization:** the uploaded ZIP identifies the parent task worktree, but does not by itself verify Git common-dir mapping, launcher preparation, recursive submodules or start-of-attempt sync. Evidence remains for review.

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
