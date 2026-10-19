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
status: complete
priority: 40
executor: null
claimed_at: null
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
- Authoritative registry: the user-approved ARCH-043 PostgreSQL key registry (18 keys, including `omini.moderation`), reflected by `moda-interact-admin/src/lib/admin/platform-configuration/{contracts,secrets-contracts}.ts` and `docs/architecture/ARCH-043-configuration-environment-variable-mapping.md`. The user-approved registry prevails over stale 17-key text; do not introduce aliases.
- Owner: `moda_background`, implementation repository `moda-interact-background`.
- Initial definition snapshot: `moda-interact-workspace(20261018-105713).zip`. That statement was historical preparation evidence only. The current task was subsequently claimed as developer Attempt 1 on `task/ARCH-043-BACKGROUND-002`; preserve the live frontmatter claim and do not reset it.

### Developer Ownership Amendment

On 2026-10-18, `/moda_developer_create ARCH-043-BACKGROUND-002` was invoked while this task was ready and agent-owned. This is an explicit developer takeover. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_background`, repository ownership, dependencies, scope and acceptance criteria are unchanged. The canonical launcher subsequently claimed developer Attempt 1. The existing task claim, attempt, completion authority and Architect Review remain unchanged by this documentation amendment.

### Authoritative registry and consumer boundary (2026-10-18)

- The approved registry contains **18 PostgreSQL keys**; the `BACKGROUND-001` service authorises **10 Background-readable purposes**. This task integrates **nine existing consumer purposes**, counting `speech.transcription` and `ai.providers` separately. `omini.moderation` is the tenth readable purpose but **not** a consumer migration in this task.
- `ai.providers` contains the generic sealed provider credentials `openAiApiKey?` and `groqApiKey?`, reusable by *authorised* speech/AI operations; the obsolete `openAiSpeechApiKey` and `groqSpeechApiKey` names are not accepted. This does **not** change the separate support-message translation credential authority.
- `omini.moderation` contains only `baseUrl` and `modelId`. `ARCH-040-BACKGROUND-006` owns the future moderation client/consumer and may use `ai.providers.openAiApiKey` via its approved purpose-specific reader. Do not execute moderation or introduce a new `support.translation` configuration key here.

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
| `speech.transcription` + `ai.providers` | `src/services/speech-transcription.service.ts` and speech job orchestration | Read the provider/model plus generic `groqApiKey` or `openAiApiKey` together in one operation snapshot; no speech fallback to `GROQ_API_KEY` / `WHATSAPP_OPENAI_API_KEY` / `OPENAI_API_KEY` or a different provider when its selected key is absent. |
| `commerce.connectionKeys` | `src/commerce/credential-keyring.ts`, `src/services/woo-coupon-grant.service.ts`, other Background execution and Woo REST grant/decrypt consumers | Read sealed keyring including active ID and optional command HMAC value at correct operation boundary; preserve ARCH-039 ciphertext/AAD compatibility and existing entitlement/tenant checks. Do not capture the keyring at module startup. |
| `shopify.oauth` | `src/services/shopify-session.service.ts`, background Shopify refresh/composition call sites | Read atomic Shopify API key and secret for each relevant OAuth/session refresh operation; preserve existing shop/session and provider verification behaviour. |
| `shopify.partner` | `src/providers/shopify-partner-billing.provider.ts` and all Partner billing call sites | Read complete `{accessToken,organizationId,appId,apiVersion?}` from one revision, including supported environment aliases; preserve receipt and idempotency boundaries. |
| `shopify.appEvents` | `src/providers/shopify-app-events.provider.ts` and its worker/creation sites | Read atomic client ID/secret at the point App Events provider calls need it. Inspect `ShopifyAppEventsClient.cachedToken` (including non-expiring tokens when `expires_in` is absent): an old token must not survive a credential revision change or revocation. Preserve token negotiation, retries and concurrency without any cross-operation *configuration* cache. |
| `messaging.sender` | `src/services/whatsapp.service.ts`, `src/services/whatsapp-media.service.ts` and sending/media orchestration | Read token plus two sender IDs together for each outbound/media operation; ensure no token is captured in long-lived provider instances. Keep WhatsApp event ordering, Meta response handling and attachment semantics. |

### Separate translation authority (do not add a new ARCH-043 key)

For **support-message translation**, inspect queue creation, submit, poll, results, **`SUBMISSION_UNKNOWN` reconciliation** and their transitive provider factories. Use the existing `CommerceTranslationProviderCredential` plus enabled `CommerceTranslationModelConfiguration` automatic default, via their existing owning resolver, **not** `ai.providers` or a new `support.translation` policy. For existing batches, preserve the *persisted* provider/model and credential ownership; do not recompute the model during reconciliation.

The production provider/factory must receive the resolved credential explicitly: no implicit `OPENAI_API_KEY`, `TRANSLATION_MODEL` or `TRANSLATION_PROVIDER` fallback. If a Commerce credential is missing or revoked, reconciliation **fails closed even when a valid-looking legacy `OPENAI_API_KEY` is present**. Prove that no external provider call occurs and that safe Shared-logger diagnostics do not contain the credential or exception details. Preserve the independent Merchant Pricing / Store Category translation flows through explicit injected credentials and focused regressions rather than switching their credential authority.

### Explicitly excluded environment sources

Do not replace bootstrap/deployment reads unrelated to the **18-key registry**: `DATABASE_URL`, `REDIS_URL`, `NODE_ENV`, trusted deployment environment, `OTEL_*`, `MODA_CONFIG_UNSEAL_KEY`/KMS identity, `WHATSAPP_API_BASE_URL`, `MODA_WOOCOMMERCE_CONNECTION_MODE`, Shopify session shop tokens, or `WOO_BILLING_ENVIRONMENT`. No Background consumers are authorised for `auth.admin`, `auth.commerce`, `commerce.bootstrap`, `woocommerce.auth`, `woocommerce.billing`, `messaging.meta`, `admin.grafana`, or `commerce.preview`; these are not work items. In particular **no Messaging webhook ingress integration** is authorised. `omini.moderation` is readable via `BACKGROUND-001` but has **no consumer in BACKGROUND-002**; `ARCH-040-BACKGROUND-006` owns its use.

## Out of Scope

- No duplicate configuration service/credential resolver, changes to `BACKGROUND-001` contract, Shared crypto or Admin registry, schema/migrations, R2 object relocation work, new Messaging ingress DB client, `omini.moderation` consumer or bulk refactor of unrelated providers.
- No cross-operation cache, stale fallback, environment fallback for configured invalid/revoked rows, per-token/per-message-byte DB lookup, new queue payload contract without approved architecture or `_index.md` changes.
- No removal of environment declarations from Render; Gateway owns that after acceptance and controlled cutover.

## Requirements

1. **Callsite-by-callsite replacement:** Search direct and indirect env reads (`process.env`, injected `NodeJS.ProcessEnv`, config helpers and startup factories) in all relevant Background files. Record each replacement in a review matrix mapping original reader → key/typed getter → operation boundary → tests. A missing provider reader is an incomplete task.
2. **Per-operation fresh config:** Each relevant job/operation makes a fresh PostgreSQL read for required keys, with single same-operation snapshot reuse. No application cache/timer/last-good; a subsequent job observes changes, rotations and revocations. Database queries occur outside long-lived transactions and external network operations. Keep the existing separate `BackgroundRuntimeConfig` runtime mechanism untouched except if needed to prevent duplicated policy reads.
3. **Safe operation identity:** For credential tuples (R2, sender, Partner, App Events, Shopify OAuth, Commerce keyring), do not mix revisions, tenants, environments or env/database sources within a single operation. Use the `BACKGROUND-001` bundle API for speech provider selection and sealed API key. Enforce correct AAD for persistent encrypted Commerce grants.
4. **Failure policy:** Missing/disabled/invalid/wrong-root/wrong-purpose credentials fail closed, with redacted reason code. Distinguish transient database unavailability and apply existing retry/backoff policies; no blind permanent retry storms, skipped billing idempotency or sent-without-credentials messages.
5. **No inadvertent contract drift:** Keep R2 endpoint/bucket editable; preserve object keys and storage migration's separate ownership. Woo concurrency is process construction state (document restart requirement). Support-message translation keeps domain-model authority and no new `support.translation`/OpenAI translation key in `ai.providers`.
6. **Security and logging:** All secrets remain server-only; provider adapters must never log credentials, encrypted envelopes or raw exception details. Use `createLogger` from `@modainteract/moda-interact-shared/logging` (no second generic logger); emit bounded semantic reason codes and preserve existing trace/correlation fields. Logger/sink failure must not convert a fail-closed credential decision into a provider call.
7. **Legacy-reader hardening:** No production path may implicitly obtain migrated credentials or policy from `process.env`, including through default parameters/constructors, Woo worker-concurrency defaults, or long-lived App Events tokens. Explicitly injected synthetic test input is allowed only as an intentional test boundary and must not become a production fallback.
8. **Translation revocation proof:** With `OPENAI_API_KEY` populated in the process environment and the previously valid Commerce translation credential revoked/deleted in PostgreSQL, `SUBMISSION_UNKNOWN` reconciliation must reject provider construction and sending. Verify the selected persisted model is retained for a valid credential and secrets/errors are redacted in Shared logs.
9. **Repository-contained tests:** All unit tests and frozen fixtures must resolve within `moda-interact-background` itself (relative to the test module or repository), without requiring `MODA_WORKSPACE_ROOT` or reading a sibling checkout. Disposable integration tests may provision PostgreSQL/Redis but may not assume another repository's worktree.

## Work Items

- [x] Audit all relevant Background environment reader entrypoints and dependency-injected environment ports; record complete migration matrix in the Completion Report.
- [x] Replace Woo coupon sync policy and worker construction reads, with explicit worker concurrency/recreation contract and tests.
- [x] Replace Merchant Knowledge R2 lookup with the canonical sealed six-field record, including readers used by reconciliation and source upload finalisation.
- [x] Replace transcription policy/speech key selection, Commerce keyring/grant decrypt, and Shopify OAuth reads with accepted typed methods.
- [x] Replace Partner billing, App Events and WhatsApp outbound/media sender credentials; ensure no long-lived env credential capture, including App Events cached-token invalidation on version change, or loss of existing provider behaviours.
- [x] Reconcile support-message translation, including `SUBMISSION_UNKNOWN`, to its already-owned DB model/provider credential, preserving existing persisted provider/model and other translation flows.
- [x] Eliminate runtime `OPENAI_API_KEY` translation fallback; add a real PostgreSQL credential-revocation test with the legacy environment key still populated.
- [x] Use the existing Shared structured logger for credential-resolution failures, with bounded reason codes and no secret-bearing diagnostics.
- [x] Keep frozen ARCH-020 evidence fixture inside Background tests, and update affected test doubles and stale dependency assertion for repository-local validation.
- [x] Add focused tests for each changed callsite, rotation/revocation between operations, no cross-operation cache, no credential mix, invalid/missing/DB failures and expected provider retry behaviour.
- [x] Finish the final committed-worktree source/acceptance review, capture exact changed-file and Git commit/branch evidence, record integrated validation, and hand back at Review.

## Interfaces / Contracts

- **Only configuration service:** `ARCH-043-BACKGROUND-001` typed `BackgroundPlatformConfigurationService` and `KeyValues`/operation snapshot API; no second resolver implementation.
- Canonical registry: the user-approved **18-key** PostgreSQL registry and matching Admin definitions; **10** Background-readable purposes, **nine** existing consumer-purpose migrations here. Do not use legacy `merchantKnowledge.upload`, `support.translation` or an `ai.providers` key for support-message translation. The generic sealed provider fields are `openAiApiKey?` and `groqApiKey?`.
- `omini.moderation` is a reader-only purpose at this stage; its actual consumer is `ARCH-040-BACKGROUND-006`. `commerce.connectionKeys.commandHmacKey` remains available in the canonical reader but is not to be wired to a fabricated Background consumer.
- Existing translation authority: `CommerceTranslationProviderCredential` + `CommerceTranslationModelConfiguration`; no new ARCH-043 record.
- Other boundaries: Shopify/WhatsApp and Commerce existing event, grant, billing and provider contracts remain unchanged. Database read errors must not be exposed to merchant browser or provider payloads.

## Dependencies

- `ARCH-043-BACKGROUND-001`
- `ARCH-043-ADMIN-002`

## Enables

- `ARCH-043-GATEWAY-001`
- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Source review matrix covers all live Background consumers of the **nine integrated purposes** (out of 10 Background-readable purposes); no direct migrated-purpose environment reads remain in production source. `omini.moderation` consumption remains explicitly deferred to ARCH-040.
- [x] Fresh per-operation snapshots, rotation and no cross-operation cache are covered, including two-key speech and six-field R2 bundle.
- [x] Background provider behaviour, queue ordering, billing idempotency, Woo grants, translation provenance and security invariants are covered by the passing unit and integration suites.
- [x] Editable R2 location and current-record reads remain supported; no Gateway environment cleanup or other repository's behaviour was changed.
- [x] Local tests and disposable integration evidence demonstrate correct failures, redacted **Shared structured logs**, no stale/environment fallback, and rejected revoked Commerce translation credentials despite `OPENAI_API_KEY` being set.
- [x] ARCH-020 frozen evidence fixtures and Background tests resolve within this repository without parent-workspace environment overrides.

## Validation

- [x] Unit tests across affected service/provider/worker/commerce/config paths: **2,251/2,251** passed across **219/219** files.
- [x] Disposable PostgreSQL/integration proof: full `npm run test:integration` **13/13** passed; platform configuration **3/3**, support-translation revocation **1/1**, Woo dispatch **5/5**, translation assembly and enum bindings **5/5** passed. Translation fixtures now seed/inject the configured database model/credential contracts; the separate revocation test continues to exercise production credential resolution.
- [x] Build (`prisma generate` + `tsc`), lint, and `git diff --check` passed. The final assembly fixture adjustment was revalidated with its PostgreSQL integration test.
- [x] Completion Report records the callsite matrix, exact committed file inventory, commit/branch evidence, validation and the earlier parallel-load-only scheduling timeout (which passed 2/2 in isolation).

## Stop Condition

When integrations and validation are complete, record real evidence, set task to `review`, return to `moda_architect`, and **STOP**. No Gateway, System Test or neighbouring repository work is authorised implicitly.

## Implementation Notes

Prefer small service adapters or dependency injection rather than a monolithic `platform-configuration.ts`; task 1 provides the shared reader, task 2 owns integration adapters. Do not edit `docs/decisions/**/_index.md`. Confirm physical task worktree isolation/synchronisation before starting. If legacy support translation caller contracts cannot be reconciled without changing cross-repository behaviour, report the architectural gap before broad refactoring.

## Completion Report

### Status

Complete — developer Attempt 1. The Accepted self-review and explicit developer completion decision are recorded below.

### Files Changed

The final implementation is **69 paths**, exactly the output of `git diff --name-only origin/main...HEAD` in the canonical Background implementation worktree. Commit `22ff4ffd2b947a6bfee487be309cae807a0464bf` is pushed to `origin/task/ARCH-043-BACKGROUND-002`; the implementation worktree is clean except for the unstaged `database` submodule pointer. That pointer references database commit `69c0c8bfce283145e4e02f1d524bf420be6773ed` (`Task/arch 040 database 005 (#56)`), reachable from `database/origin/main`; it is excluded from the task commit per VCS policy.

Exact committed path inventory:

```text
docs/arch043-background-002-consumer-review.md
package-lock.json
package.json
src/agents/commerce.agent.ts
src/commerce/credential-keyring.ts
src/entrypoints/merchant-knowledge.ts
src/entrypoints/recovery.ts
src/providers/shopify-app-events.provider.ts
src/providers/shopify-partner-billing.provider.ts
src/providers/translation.provider.ts
src/providers/woo-coupon-pages.ts
src/providers/woo-coupon-transport.ts
src/services/checkout-recovery/recovery-initiation.service.ts
src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts
src/services/merchant-knowledge-r2-config.ts
src/services/merchant-pricing-translation-batch-poll.service.ts
src/services/merchant-pricing-translation-batch-results.service.ts
src/services/merchant-pricing-translation-batch-submit.service.ts
src/services/merchant-pricing-translation-reconciliation.service.ts
src/services/outbound-whatsapp-admission.service.ts
src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts
src/services/platform-configuration/consumers.ts
src/services/platform-configuration/support-translation.ts
src/services/recovery-routing.service.ts
src/services/routing-guidance.service.ts
src/services/shopify-session.service.ts
src/services/shopify-usage-event-publisher.service.ts
src/services/speech-transcription.service.ts
src/services/store-category-translation-batch-poll.service.ts
src/services/store-category-translation-batch-results.service.ts
src/services/store-category-translation-batch-submit.service.ts
src/services/store-category-translation-reconciliation.service.ts
src/services/translation-batch-assembly.service.ts
src/services/translation-batch-poll.service.ts
src/services/translation-batch-results.service.ts
src/services/translation-batch-submit.service.ts
src/services/translation-reconciliation.service.ts
src/services/whatsapp-conversation-routing.service.ts
src/services/whatsapp-media.service.ts
src/services/whatsapp.service.ts
src/services/woo-coupon-catalogue.service.ts
src/services/woo-coupon-dispatcher.service.ts
src/services/woo-coupon-grant.service.ts
src/services/woo-coupon-reader.service.ts
src/services/woo-coupon-sync-config.ts
src/workers/woo-coupon-sync.worker.ts
tests/fixtures/commerce/arch020-evidence-contract-fixtures.v1.json
tests/integration/arch043-support-translation-revocation.integration.test.ts
tests/integration/translation-batch-assembly.concurrency.integration.test.ts
tests/integration/translation-enum-bindings.integration.test.ts
tests/unit/commerce/credential-keyring.test.ts
tests/unit/commerce/evidence.test.ts
tests/unit/entrypoints/merchant-knowledge.test.ts
tests/unit/providers/translation.provider.test.ts
tests/unit/runtime/observability-startup.test.ts
tests/unit/runtime/recovery-entrypoint.woo-coupons.test.ts
tests/unit/services/checkout-recovery/recovery-outreach-follow-up-processor.service.test.ts
tests/unit/services/outbound-whatsapp-admission/outbound-message-delivery.service.test.ts
tests/unit/services/platform-configuration/consumers.test.ts
tests/unit/services/speech-transcription.service.test.ts
tests/unit/services/translation-batch-lifecycle.test.ts
tests/unit/services/translation-batch-poll.service.test.ts
tests/unit/services/translation-batch-results.service.test.ts
tests/unit/services/translation-batch-submit.service.test.ts
tests/unit/services/translation-reconciliation.service.test.ts
tests/unit/services/whatsapp-media.service.test.ts
tests/unit/services/whatsapp.service.test.ts
tests/unit/services/woo-coupon-delivery-boundary.test.ts
tests/unit/workers/woo-coupon-sync.worker.test.ts
```

### Work Completed

- Implemented PostgreSQL-backed operation-boundary consumption for Woo coupon policy, sealed R2, transcription plus generic provider credentials, Commerce grant keyring, Shopify OAuth/Partner/App Events, and WhatsApp sender/media paths. Existing provider and queue semantics remain review requirements, not presumed architect-accepted.
- Routed support-message translation submit/poll/results/reconciliation through existing Commerce translation model/credential authority; removed implicit OpenAI translation environment fallback, preserving persisted batch model identity.
- Added revoked-credential regression with legacy `OPENAI_API_KEY` populated, requiring fail-closed behaviour with no provider request; used `@modainteract/moda-interact-shared/logging` for bounded, secret-free diagnostic events.
- Updated affected test-only fixtures for asynchronous readers and durable-claim boundaries; froze the ARCH-020 evidence fixture inside Background for repository-local tests; reconciled the observability test assertion with the manifest-pinned Shared version without upgrading it.
- Maintained `omini.moderation` as future ARCH-040 consumer scope; no moderation consumer, Gateway cleanup or database migration is part of this task.

### Validation Results

- Final canonical route: developer/developer Attempt 1; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-043-BACKGROUND-002`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-043-BACKGROUND-002`; both on `task/ARCH-043-BACKGROUND-002`.
- `npm run test:unit`: **2,251/2,251** passed across **219/219** files.
- `npm run test:integration`: **13/13** passed across **5/5** files. Translation assembly and enum binding focused rerun passed **5/5**; after the final assembly-fixture cleanup adjustment its PostgreSQL concurrency test passed **1/1**. Conversation-turn scheduling passed **2/2** in isolation after a parallel full-suite timeout; the complete suite subsequently passed.
- `npm run test:arch043-platform-configuration:postgres`: **3/3** passed.
- `npm run test:arch043-translation-revocation:postgres`: **1/1** passed with legacy `OPENAI_API_KEY` present and no provider call after credential revocation.
- `npm run test:arch036-woo-coupon-dispatch:postgres`: **5/5** passed.
- `npm run build` (Prisma generation and `tsc`) passed; `npm run lint` passed; `git diff --check` and staged `git diff --cached --check` passed.
- Direct production-source scan found no reads matching the migrated `OPENAI_API_KEY`, `TRANSLATION_MODEL`, `TRANSLATION_PROVIDER`, `GROQ_API_KEY`, `WHATSAPP_OPENAI_API_KEY` or `WOO_COUPON_SYNC_*` patterns.
- Implementation branch publication verified: commit `22ff4ffd2b947a6bfee487be309cae807a0464bf` on `origin/task/ARCH-043-BACKGROUND-002`; 69 committed paths; no uncommitted task-owned source changes.

### Deviations

The migration required test-only compatibility updates to old asynchronous/synchronous mocks, a repository-local frozen ARCH-020 fixture and a version expectation matching the already pinned Shared `2.4.1` package. Translation integration fixtures were updated to seed the Commerce automatic model contract and inject a test credential only where fake providers are used; production credential reads remain fail-closed. These changes do not constitute runtime fallbacks or a dependency upgrade.

### Assumptions

The route was re-resolved from the canonical primary workspace immediately before review. Parent and implementation worktrees use the canonical launcher paths and mirrored task branch. Implementation commit is pushed; the changed database pointer is intentionally unstaged and points to a published mainline database commit.

### Unresolved Issues

No task-local blockers remain. Render environment cleanup remains outside scope and must wait for the Gateway task and controlled rollout.

### Architectural Concerns

- Registry now has 18 keys; the tenth Background-readable key `omini.moderation` is **not** integrated here. `ARCH-040-BACKGROUND-006` retains consumer ownership.
- Shared generic provider keys (`openAiApiKey`, `groqApiKey`) are not interchangeable with the separate Commerce support-translation credential authority.
- Gateway environment cleanup is gated on actual implementation acceptance and deployment/rollback review. PostgreSQL readers must not be treated as proof of production cutover.

## Developer Self-Review

### Review Status

Accepted — developer-as-architect review, Attempt 1, 2026-10-18.

### Review Notes

Reviewed the committed implementation against the nine-purpose migration scope, operation-boundary/fresh-read requirements, translation credential authority and revocation condition, exclusion of `omini.moderation` and Gateway work, final 69-path diff, and validation results above. No task-scoped blocking findings remain. The database gitlink is excluded from the implementation commit because the referenced commit is already on database `origin/main` and VCS policy reserves gitlink integration for after implementation acceptance/merge.

### Reviewed Files

All 69 paths in the committed implementation inventory above, plus the canonical task file and consumer review matrix.

### Validation Reviewed

Unit 2,251/2,251; full integration 13/13; platform configuration PostgreSQL 3/3; support translation revocation PostgreSQL 1/1; Woo dispatch PostgreSQL 5/5; build, lint and diff checks passed.

### Review Decision

Passing/Accepted. Task transitioned to `review`; Attempt 1 is unchanged. This is the durable review prerequisite for the developer's explicit completion decision.

## Architect Review

### Review Status

Not separately performed; this task uses developer completion authority.

### Review Notes

No assigned-agent architect review is claimed. See the accepted Developer Self-Review above.

### Reviewed Files

All committed implementation paths listed above.

### Validation Reviewed

Validation evidence listed above.

### Architecture Conformance

Conforms to the stated task scope and exclusions as assessed in the Developer Self-Review.

### Follow-up

No task-scoped follow-up. Gateway cutover remains downstream and out of scope.

## Developer Completion Decision

The developer explicitly authorized completion after the durable Accepted review was pushed. All required Work Items, Acceptance Criteria and Validation checkboxes are complete; implementation commit `22ff4ffd2b947a6bfee487be309cae807a0464bf` and parent review commit `6faff4f04193237b6e889a9941f777446dfd4ebc` are published on their mirrored `task/ARCH-043-BACKGROUND-002` branches. Attempt remains 1. No merge to either `main` branch was performed.
