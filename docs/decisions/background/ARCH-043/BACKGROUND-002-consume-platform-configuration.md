---
id: ARCH-043-BACKGROUND-002
architecture_id: ARCH-043
title: Integrate Background platform configuration consumers
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 40
executor: developer
claimed_at: 2026-10-18T15:08:26Z
attempt: 1
depends_on:
- ARCH-043-BACKGROUND-001
- ARCH-043-ADMIN-002
enables:
- ARCH-043-GATEWAY-001
- ARCH-043-SYSTEM-TEST-001
created: 2026-10-18
updated: 2026-10-18
---

# Background: replace environment readers with Platform Configuration consumption

## Architecture

- Parent: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Authoritative registry: `moda-interact-admin/src/lib/admin/platform-configuration/{contracts,secrets-contracts}.ts` and `docs/architecture/ARCH-043-configuration-environment-variable-mapping.md`.
- Owner: `moda_background`, implementation repository `moda-interact-background`.
- Snapshot: `moda-interact-workspace(20261018-105713).zip`. Materialised on parent task branch `task/ARCH-043-BACKGROUND-002`; promoted to `ready` after both declared dependencies became complete. Attempt remains 0 and no executor claim has been made.

### Developer Ownership Amendment

On 2026-10-18, `/moda_developer_create ARCH-043-BACKGROUND-002` was invoked while this task was ready and agent-owned. This is an explicit developer takeover. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_background`, repository ownership, dependencies, scope and acceptance criteria are unchanged. The next canonical launcher preparation will claim Attempt 1 as `developer`.

## Objective

Migrate **all Background-owned consumers of ARCH-043's approved configuration keys** from environment-based lookups to the accepted, typed, fresh PostgreSQL readers delivered by `BACKGROUND-001`, without changing unrelated infrastructure configuration or provider business semantics.

## Context

`BACKGROUND-001` owns one reusable typed read service. This task alone changes the existing providers, worker/composition sites, helpers and corresponding tests. It supersedes the older one-purpose Background migration tasks (`BACKGROUND-001` through `BACKGROUND-009` draft variants); do not reopen those or create a third Background task to finish a reader overlooked here.

## Scope

Systematically inspect source and test reads, including transitive helpers/constructor captures. Replace environment lookups for keys that belong to Background with typed `BACKGROUND-001` methods. Add dependency injection at job/operation boundaries, pass one validated operation snapshot into the provider call, and adjust retry/error classification without changing idempotency, persisted references or queue ordering.

### Required consumer inventory and replacement matrix

| Canonical key / DB authority | Existing source to inspect | Required consumption |
|---|---|---|
| `woo.couponSync` | `src/services/woo-coupon-sync-config.ts`, `src/workers/woo-coupon-sync.worker.ts`, dispatcher/recovery entrypoint and scheduling call sites | Replace nine `WOO_COUPON_SYNC_*` tuning env reads; read `workerConcurrency` for worker construction. A running BullMQ worker needs a controlled restart/recreation when its concurrency changes; do not promise live mutation without proof. |
| `merchant.knowledge.r2` | `src/services/merchant-knowledge-r2-config.ts` and every Merchant Knowledge asset/source upload/reconciliation reader | Consume **one sealed six-field bundle** `{endpoint,bucket,accessKeyId,secretAccessKey,maxUploadBytes,maxXlsxUncompressedBytes}`; use for storage and hard-limit decisions. R2 endpoint/bucket stay editable. Storage relocation/in-flight asset handling remains owned by other tasks; preserve persisted object identity. |
| `speech.transcription` + `ai.providers` | `src/services/speech-transcription.service.ts` and speech job orchestration | Read current provider/model and selected speech key together per transcription operation; no speech provider fallback to `GROQ_API_KEY` / `WHATSAPP_OPENAI_API_KEY` / `OPENAI_API_KEY`, or to different provider when selected key absent. |
| `commerce.connectionKeys` | `src/commerce/credential-keyring.ts`, `src/services/woo-coupon-grant.service.ts`, other Background execution and Woo REST grant/decrypt consumers | Read sealed keyring including active ID and optional command HMAC value at correct operation boundary; preserve ARCH-039 ciphertext/AAD compatibility and existing entitlement/tenant checks. Do not capture the keyring at module startup. |
| `shopify.oauth` | `src/services/shopify-session.service.ts`, background Shopify refresh/composition call sites | Read atomic Shopify API key and secret for each relevant OAuth/session refresh operation; preserve existing shop/session and provider verification behaviour. |
| `shopify.partner` | `src/providers/shopify-partner-billing.provider.ts` and all Partner billing call sites | Read complete `{accessToken,organizationId,appId,apiVersion?}` from one revision, including supported environment aliases; preserve receipt and idempotency boundaries. |
| `shopify.appEvents` | `src/providers/shopify-app-events.provider.ts` and its worker/creation sites | Read atomic client ID/secret at the point App Events provider calls need it. Inspect `ShopifyAppEventsClient.cachedToken` (including non-expiring tokens when `expires_in` is absent): an old token must not survive a credential revision change or revocation. Preserve token negotiation, retries and concurrency without any cross-operation *configuration* cache. |
| `messaging.sender` | `src/services/whatsapp.service.ts`, `src/services/whatsapp-media.service.ts` and sending/media orchestration | Read token plus two sender IDs together for each outbound/media operation; ensure no token is captured in long-lived provider instances. Keep WhatsApp event ordering, Meta response handling and attachment semantics. |

### Separate translation authority (do not add a new ARCH-043 key)

`src/providers/translation.provider.ts` currently supports `OPENAI_API_KEY`, `TRANSLATION_MODEL`, `TRANSLATION_PROVIDER` fallback. For **support-message translation**, inspect actual queue creation, submit, poll, results and reconciliation callers; use the existing `CommerceTranslationProviderCredential` plus enabled `CommerceTranslationModelConfiguration` automatic default, via their existing owning resolver, NOT `ai.providers` or a new `support.translation` policy. Preserve model identity of existing jobs, batching and reprocessing. Do not break independent Merchant Pricing/Store Category translation flows by globally replacing their provider contracts without caller-level proof.

### Explicitly excluded environment sources

Do not replace bootstrap/deployment reads unrelated to the 17-key contract: `DATABASE_URL`, `REDIS_URL`, `NODE_ENV`, trusted deployment environment, `OTEL_*`, `MODA_CONFIG_UNSEAL_KEY`/KMS identity, `WHATSAPP_API_BASE_URL`, `MODA_WOOCOMMERCE_CONNECTION_MODE`, Shopify session shop tokens, or `WOO_BILLING_ENVIRONMENT`. No Background consumers are authorised for `auth.admin`, `auth.commerce`, `commerce.bootstrap`, `woocommerce.auth`, `woocommerce.billing`, `messaging.meta`, `admin.grafana`, or `commerce.preview`; these are not work items. In particular **no Messaging webhook ingress integration** is authorised.

## Out of Scope

- No duplicate configuration service/credential resolver, changes to `BACKGROUND-001` contract, Shared crypto or Admin registry, schema/migrations, R2 object relocation work, new Messaging ingress DB client or bulk refactor of unrelated providers.
- No cross-operation cache, stale fallback, environment fallback for configured invalid/revoked rows, per-token/per-message-byte DB lookup, new queue payload contract without approved architecture or `_index.md` changes.
- No removal of environment declarations from Render; Gateway owns that after acceptance and controlled cutover.

## Requirements

1. **Callsite-by-callsite replacement:** Search direct and indirect env reads (`process.env`, injected `NodeJS.ProcessEnv`, config helpers and startup factories) in all relevant Background files. Record each replacement in a review matrix mapping original reader → key/typed getter → operation boundary → tests. A missing provider reader is an incomplete task.
2. **Per-operation fresh config:** Each relevant job/operation makes a fresh PostgreSQL read for required keys, with single same-operation snapshot reuse. No application cache/timer/last-good; a subsequent job observes changes, rotations and revocations. Database queries occur outside long-lived transactions and external network operations. Keep the existing separate `BackgroundRuntimeConfig` runtime mechanism untouched except if needed to prevent duplicated policy reads.
3. **Safe operation identity:** For credential tuples (R2, sender, Partner, App Events, Shopify OAuth, Commerce keyring), do not mix revisions, tenants, environments or env/database sources within a single operation. Use the `BACKGROUND-001` bundle API for speech provider selection and sealed API key. Enforce correct AAD for persistent encrypted Commerce grants.
4. **Failure policy:** Missing/disabled/invalid/wrong-root/wrong-purpose credentials fail closed, with redacted reason code. Distinguish transient database unavailability and apply existing retry/backoff policies; no blind permanent retry storms, skipped billing idempotency or sent-without-credentials messages.
5. **No inadvertent contract drift:** Keep R2 endpoint/bucket editable; preserve object keys and storage migration's separate ownership. Woo concurrency is process construction state (document restart requirement). Support-message translation keeps domain-model authority and no new `support.translation`/OpenAI translation key in `ai.providers`.
6. **Security:** All secrets remain server-only; provider adapters never log credentials or encrypted envelopes. Use shared structured logger where new generic logging is required and preserve existing trace/correlation fields.

## Work Items

- [ ] Audit all relevant Background environment reader entrypoints and dependency-injected environment ports; record complete migration matrix in the Completion Report.
- [ ] Replace Woo coupon sync policy and worker construction reads, with explicit worker concurrency/recreation contract and tests.
- [ ] Replace Merchant Knowledge R2 lookup with the canonical sealed six-field record, including readers used by reconciliation and source upload finalisation.
- [ ] Replace transcription policy/speech key selection, Commerce keyring/grant decrypt, and Shopify OAuth reads with accepted typed methods.
- [ ] Replace Partner billing, App Events and WhatsApp outbound/media sender credentials; ensure no long-lived env credential capture, including App Events cached-token invalidation on version change, or loss of existing provider behaviours.
- [ ] Reconcile support-message translation to its already-owned DB model/provider credential, preserving other translation flows.
- [ ] Add focused tests for each changed callsite, rotation/revocation between operations, no cross-operation cache, no credential mix, invalid/missing/DB failures and expected provider retry behaviour.
- [ ] Run targeted tests and full repository validation defined by scripts; update Completion Report and hand back at Review.

## Interfaces / Contracts

- **Only configuration service:** `ARCH-043-BACKGROUND-001` typed `BackgroundPlatformConfigurationService` and `KeyValues`/operation snapshot API; no second resolver implementation.
- Canonical registry: Admin's exact 17-key definitions and `docs/architecture/ARCH-043-configuration-environment-variable-mapping.md`; no legacy `merchantKnowledge.upload`, `support.translation` or translation key under `ai.providers`.
- Existing translation authority: `CommerceTranslationProviderCredential` + `CommerceTranslationModelConfiguration`; no new ARCH-043 record.
- Other boundaries: Shopify/WhatsApp and Commerce existing event, grant, billing and provider contracts remain unchanged. Database read errors must not be exposed to merchant browser or provider payloads.

## Dependencies

- `ARCH-043-BACKGROUND-001`
- `ARCH-043-ADMIN-002`

## Enables

- `ARCH-043-GATEWAY-001`
- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Source review matrix covers all live Background consumers of the nine authorised keys; no remaining ARCH-043 env lookup on accepted operational paths.
- [ ] Fresh per-operation snapshots, rotation and no cross-operation cache are proven, including two-key speech and six-field R2 bundle.
- [ ] Background provider behaviour, queue ordering, billing idempotency, Woo grants, translation provenance and security invariants remain unchanged.
- [ ] Editable R2 location and current-record reads work; no Gateway environment cleanup or other repository's behaviour is changed.
- [ ] Local tests and integration evidence demonstrate correct failures, redacted diagnostics and no stale/env fallback.

## Validation

- [ ] Unit tests across affected `tests/unit/services/`, `tests/unit/providers/`, worker/commerce/config paths.
- [ ] Relevant disposable PostgreSQL/integration proof for rotation, R2 record, Woo policy and provider-selection behaviour.
- [ ] Existing typecheck, lint, build and full test suite required by the repository/task, plus `git diff --check`.
- [ ] Completion Report includes callsite-to-test matrix and baseline failures distinguished from introduced regressions.

## Stop Condition

When integrations and validation are complete, record real evidence, set task to `review`, return to `moda_architect`, and **STOP**. No Gateway, System Test or neighbouring repository work is authorised implicitly.

## Implementation Notes

Prefer small service adapters or dependency injection rather than a monolithic `platform-configuration.ts`; task 1 provides the shared reader, task 2 owns integration adapters. Do not edit `docs/decisions/**/_index.md`. Confirm physical task worktree isolation/synchronisation before starting. If legacy support translation caller contracts cannot be reconciled without changing cross-repository behaviour, report the architectural gap before broad refactoring.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-18T15:08:26Z. Attempt 0 review history is preserved below.

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

Not reviewed.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Not evaluated.

### Follow-up

None
