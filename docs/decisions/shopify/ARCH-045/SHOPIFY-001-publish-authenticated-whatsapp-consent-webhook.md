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

Current authenticated ingress normalises checkout/cart/order/discount topics only. Extend the Shopify app's **version-controlled** subscription and queue routing using the published Shared sync-event contract, without GraphQL calls or checkout state lookups inside the webhook request. **Deployed app configuration, installed consent-read access, protected-customer-data approval, and live non-production GraphQL/webhook smoke are release/system-test evidence owned by `ARCH-045-SYSTEM-TEST-001`, not acceptance gates for this Shopify implementation task.**

## Scope

- Declare the `customers_whats_app_marketing_consent/update` subscription, appropriate API version and `read_customers` scope in the intended **version-controlled Shopify app TOML**, and statically test those declarations. Do not assert that this source file is currently deployed, the existing installation has granted the scope, or Shopify has approved protected-customer-data access. ARCH-045 does **not** use `write_customers` or Shopify mutations: WhatsApp STOP is a local Moda restriction and merchant Support notice, not a Shopify consent write. Preserve HMAC-authenticated ingress and inactive-shop boundaries.
- Normalise strict `(shopId,shopifyCustomerId,deliveryId,triggeredAt)` metadata and enqueue the Shared **sync event** under its distinct job name on an existing Shopify queue. Acknowledge only after durable enqueue.
- Keep webhook contents free of permission assertion, phone/email and checkout IDs; no `CheckoutRecovery`, pending candidate, merchant notice or GraphQL lookup in HTTP handler.
- Test the checked-in subscription config, representative numeric-ID/GID fixtures, duplicate retries, HMAC rejection, queue failure and route isolation deterministically.

## Out of Scope

- No consent-authority query or DB projection in this repository; Background owns that.
- No CMP tracking implementation, recovery scheduling/rediscovery or separate BullMQ queue.
- No live Shopify deployment inspection, installed-token permission/approval verification, read-only Shopify GraphQL field-access smoke or live signed-webhook/Background-consumer smoke in this task. These are mandatory **`ARCH-045-SYSTEM-TEST-001`** release checks and are not waived.

## Requirements

- [x] Webhook publication is authenticated, tenant-safe, idempotent and uses published Shared v1 schema (verified in focused tests; real-provider delivery is not yet verified).
- [x] Consent-change **ingress** does not trigger checkout reconciliation, recovery or outbound effects (verified in focused tests); the asynchronous `CustomerPhone` refresh belongs to `ARCH-045-BACKGROUND-003` and system testing.
- [x] Existing checkout/order/discount queue semantics remain intact in the focused regression suite.

- **H1:** Validate Shopify webhook numeric `customer_id` and canonical `gid://shopify/Customer/...` through the published Shared identity helper; reject malformed, wrong-resource, ambiguous or cross-shop identifiers. Use one canonical conversion for the consent-sync boundary, not locally duplicated ID parsing.
- **H2 (system-test release gate, not SHOPIFY-001 acceptance):** `ARCH-045-SYSTEM-TEST-001` must identify the deployed app/TOML and verify the consent topic, API version, installed `read_customers` grant and protected-customer-data approval. A TOML declaration or HTTP 200 GraphQL response with errors is not proof of field access. Keep this check mandatory **before production consent-webhook rollout**, but do not block completion of the producer code task.
- Preserve webhook HMAC, low-latency durable acceptance and bounded payload. Neither webhook delivery nor its retry schedules checkout reconcilation, recipient messaging or a recovery job.

## Work Items

- [x] Add the consent webhook topic to the intended checked-in Shopify app TOML; statically assert topic, API version and declared `read_customers` scope without claiming deployment or installed permission.
- [x] Add sync-event classification/publication on existing queue.
- [x] Add focused ingress/queue failure/security tests.
- [x] Test representative numeric-ID/GID identity, malformed/wrong-shop identities, duplicate delivery and topic/API-version handling with deterministic fixtures.
- [x] Hand off live deployed-app, installed-permission, GraphQL field-access and signed-webhook verification to `ARCH-045-SYSTEM-TEST-001`; no live result is asserted by this checkbox.

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

- [x] Authenticated webhook routing uses the published Shared identity helper and rejects malformed IDs without queue publication (focused tests); no deployed-app verification is asserted.
- [x] The **checked-in** named Shopify app TOML declares the consent topic, API version and `read_customers` without adding `write_customers` or a STOP-to-Shopify mutation. Whether the deployed installation has effective access is a required `ARCH-045-SYSTEM-TEST-001` assertion, **not** a SHOPIFY-001 completion criterion.

## Validation

- [x] Focused Shopify webhook HMAC/publish/queue-failure, duplicate, tenant and customer-identity tests; version-controlled app config assertions and `git diff --check` — 76/76 focused tests passed in developer evidence.
- [x] Repository-declared `prisma:generate`, typecheck, lint and build checks — passed in developer evidence, including a successful `npm run build`.
- [ ] Start-of-attempt parent and implementation worktree synchronization/launcher evidence — **workflow requirement remains outstanding; it cannot be replaced by a system-test run**.

Live permission/approval/GraphQL/signed-webhook checks are explicitly assigned to `ARCH-045-SYSTEM-TEST-001`; they are **not** unchecked validation items for this implementation task.

## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. For publication task, do not rerun implementation validation.

## Implementation Notes

Do not infer **deployed** runtime configuration or installed-token access from a source filename. Shopify 2026-07 documented webhook payload uses `customer_id` and `phone_number`; never use webhook phone as identity/permission for admission. Existing `recordShopifyWebhookOutcome` is reusable. Source-level subscription checks belong here; the live access and webhook smoke evidence belongs in the terminal `ARCH-045-SYSTEM-TEST-001` task, after its implementation dependencies are complete.

Before claiming, use the deterministic `/moda-task` launcher and its **actual** prepared packet, read the task's complete current Architect Review, and verify task/dependency status in the developer's canonical workspace. Preserve `docs/decisions/**/_index.md` untouched until the developer explicitly closes the architecture documentation session. New runtime structured logging uses `@modainteract/moda-interact-shared/logging` where applicable. No source outside this task's owner repository may be changed unless explicitly authorised by the architecture.

## Completion Report

### Status

**Returned for changes — original developer self-review of Attempt 1 (2026-10-23); scope amended 2026-10-23.** Source implementation remains committed and pushed to the Shopify task branch as `56d96bd`. The focused tests and full application build passed in the canonical implementation worktree. The formerly required live Shopify deployment/permission/GraphQL/webhook verification is now owned by `ARCH-045-SYSTEM-TEST-001` and does **not** prevent completion of this implementation task. The start-of-attempt synchronization packet remains unevidenced and is a **separate workflow review issue**. Status remains `ready` (not accepted or complete); Attempt remains 1, with no active claim.

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
- **DEFERRED TO ARCH-045-SYSTEM-TEST-001 (NOT RUN / NOT EVIDENCED):** deployed app TOML / webhook subscription verification, active installed token's `read_customers` grant and protected-customer-data approval, non-production GraphQL field-access smoke, and a real signed webhook-to-queue/Background-consumer smoke. These are mandatory terminal system-test/release checks, **not** SHOPIFY-001 Work Items, Acceptance Criteria or Validation blockers. Start-of-attempt worktree preparation evidence remains unevidenced separately.

Independent developer review reruns on 2026-10-23 in the canonical implementation worktree:

- Focused consent ingress, queue, route, normalization and configuration suites — **PASS 76/76**.
- `npm run build` — **PASS**, including Prisma generation and React Router client/server builds. Vite emitted bundle-size and dependency annotation warnings; no build error occurred.
- `git diff --check origin/main...HEAD` — **PASS**.
- Implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-045-SHOPIFY-001` is clean at `56d96bdc1cbe81949c6f02188008c71142a993f6`, equal to `origin/task/ARCH-045-SHOPIFY-001`; `origin/main` is an ancestor. Parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-045-SHOPIFY-001` is clean at `24d5c461d0dfcb5cef4de1ad06f983d55db48279`, equal to its task remote.
- These current branch checks do not supply the missing start-of-attempt launcher synchronization packet and do not establish Shopify deployment or installed-token access.

### Deviations

- Explicit developer takeover is already recorded in the task: `execution_mode: developer`, `completion_mode: developer`, Attempt 1 claimed at `2026-10-23T10:43:38Z`. Preserve this ownership; do not revert to agent/automatic mode. The earlier handoff patch assumed the stale Ready/Attempt 0 state, which caused its application failure.
- Attempt 1 was delivered via two incremental source patches before the final single Shopify implementation commit. The first generated a BullMQ typing error, corrected and revalidated before commit.
- A launcher-generated preparation packet and corresponding start-of-attempt **parent/implementation worktree synchronization evidence** were not included in the material reviewed here. The claimed timestamp is evidenced in the task YAML; physical-isolation and synchronization evidence are **not independently verified** by this ZIP.
- Outstanding live-provider requirements are not treated as passed or waived: under the 2026-10-23 scope amendment, they are deferred to `ARCH-045-SYSTEM-TEST-001` and must pass before release, but no longer block SHOPIFY-001 code-task completion.

### Assumptions

- `shopify.app.moda-interact.toml` is the intended source candidate; it is not confirmed as the Shopify CLI-deployed configuration. TOML `read_customers` is not proof of the currently installed app's protected data access.
- `ARCH-045-BACKGROUND-003` is the separate consumer of the Shared consent-sync hint. Until the consumer and rollout are verified, successful ingress tests do not demonstrate durable `CustomerPhone` update or end-to-end consent convergence.

### Unresolved Issues

- **Transferred to terminal `ARCH-045-SYSTEM-TEST-001`:** identify the deployed Shopify app/TOML and actual webhook subscription, verify installed `read_customers` and protected-customer-data access, run a read-only non-production customer-consent GraphQL field query with no `errors` and exact GID equality, and exercise a real authenticated webhook through durable enqueue and the compatible Background consumer. Those release gates remain open, but are **not** SHOPIFY-001 acceptance criteria.
- **Still required for SHOPIFY-001 governance:** provide actual launcher-resolved canonical parent/implementation worktree and start-of-attempt sync evidence, or record the workflow non-conformance and obtain the required next-attempt validation under the approved task process. Do not invent historical preparation output.
- No architect acceptance or explicit developer completion is asserted; remain `ready` until the remaining workflow review issue is resolved.

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

Pending — no architect acceptance. Developer self-review returned Attempt 1 for changes; see the appended review record.

### Review Notes

None.

### Reviewed Files

No files reviewed by `moda_architect`; the developer's implementation review and validation evidence are recorded below.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.

## Developer Takeover

On 2026-10-23, `/moda_developer_create ARCH-045-SHOPIFY-001` was invoked while this task was ready and agent-owned. This is an explicit developer takeover. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_app`, repository ownership, dependencies, scope and acceptance criteria are unchanged. The canonical launcher will claim Attempt 1 after worktree preparation.

**2026-10-22 architect coordination:** Promoted `pending -> ready` because all declared dependencies in the supplied snapshot are `complete`. Task remains unclaimed (`executor: null`, `claimed_at: null`, `attempt: 0`). This eligibility change does not materialise a branch/worktree or start implementation.

## Developer Self-Review - Changes Requested

### Review Decision

Attempt 1 is returned for changes on 2026-10-23. Frontmatter is `status: ready`, `executor: null`, `claimed_at: null`, `attempt: 1`. The implementation is reviewable and its focused tests/build pass, but required release evidence and start-of-attempt workflow evidence are not established. This is not architect acceptance or developer completion.

### Findings and Required Corrections

1. **Verify the actual Shopify release configuration and access.** Record the selected app/client and confirm in the Shopify CLI/Partner configuration that the deployed app uses the intended `shopify.app.moda-interact.toml`, API version `2026-07`, and consent topic subscription. Using an authorized non-production installation, verify the installed `read_customers` grant and protected customer-data approval, then run the read-only consent GraphQL query from `docs/arch-045/SHOPIFY-001-consent-ingress-verification.md`. Record HTTP success, no GraphQL errors/field denial, and equality between returned customer GID and the Shared-normalized webhook identity. Do not include tokens or other secrets in the report, and do not add `write_customers`.
2. **Verify the producer rollout boundary.** Exercise an HMAC-valid consent webhook against the actual non-production ingress and verify it receives success only after the distinct `shopify-whatsapp-consent-sync` job is durably enqueued. Confirm the compatible `ARCH-045-BACKGROUND-003` consumer is deployed before enabling the subscription. If provider/runtime access is unavailable, retain this as an explicit blocked release gate; do not mark the related acceptance criteria complete.
3. **Supply truthful start-of-attempt synchronization evidence.** The canonical parent and implementation worktrees currently exist, are clean and their task branches are published, but the task report says the Attempt 1 launcher preparation/synchronization packet was not included. Recover the actual launcher evidence if available; otherwise, on the next claimed attempt, record the launcher-generated parent/implementation synchronization and recursive-submodule results. Do not reconstruct or claim a historical sync result from current branch ancestry.
4. **Complete and reconcile the remaining task checklist (historical instruction).** Run any remaining repository-declared validation required for this task and update only those Work Items, Acceptance Criteria and Validation items supported by evidence. The current independent review reran the focused suite and `npm run build`; it did not verify the external Shopify release gates above. The live-provider portion of this instruction is superseded by the scope amendment below.

### Review Evidence

- Focused consent ingress, queue, route, normalization and config tests: **76/76 passed** on 2026-10-23.
- `npm run build`: **passed** on 2026-10-23; Prisma generation and client/server builds succeeded. Vite emitted non-fatal bundle-size and dependency annotation warnings.
- `git diff --check origin/main...HEAD`: **passed**. Implementation branch `task/ARCH-045-SHOPIFY-001` is clean at `56d96bdc1cbe81949c6f02188008c71142a993f6`, published to its task remote; `origin/main` is an ancestor. Parent branch is clean at `24d5c461d0dfcb5cef4de1ad06f983d55db48279`, published to its task remote.
- Canonical worktree paths were verified. The available evidence does not contain the start-of-attempt synchronization packet or any live Shopify deployment, permission, GraphQL, or webhook result.
- `ARCH-045-BACKGROUND-003` remains `pending`; `ARCH-045-SYSTEM-TEST-001` remains `pending` and manual-gated. No downstream task was promoted or started.

### 2026-10-23 Scope Amendment — Live Verification Assigned to System Test

At the developer's request, the **current** SHOPIFY-001 task contract now ends at checked-in webhook configuration, authenticated queue publication and deterministic repository validation. The prior self-review's corrections **1 and 2** (deployed app/installed access/GraphQL and real signed-webhook smoke), and the live-provider portion of correction **4**, are **transferred to `ARCH-045-SYSTEM-TEST-001`**. The earlier review remains above as historical evidence; it does not continue to impose live-provider acceptance gates on SHOPIFY-001. Neither those checks nor their results are waived or asserted complete. They remain required **before production rollout**.

Correction **3** (start-of-attempt synchronization/worktree preparation evidence) remains a separate **SHOPIFY-001 workflow compliance requirement**. It is not an integration test, cannot be shifted to system testing, and has not been evidenced. The already-committed implementation remains `56d96bd`; no source changes are requested by this scope amendment. Task metadata remains developer-owned, `status: ready`, `attempt: 1`; this amendment does not claim architect acceptance or explicit developer completion.
