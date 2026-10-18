---
id: ARCH-043-BACKGROUND-009
architecture_id: ARCH-043
title: Integrate Background credential resolvers into provider operations
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 55
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-043-ADMIN-002
- ARCH-043-BACKGROUND-008
- ARCH-043-BACKGROUND-001
enables:
- ARCH-043-GATEWAY-001
- ARCH-043-SYSTEM-TEST-001
created: '2026-10-18'
updated: '2026-10-18'
---

# Integrate Background credential resolvers into provider operations

## Architecture

- Architecture ID: `ARCH-043`
- Canonical document: `docs/architecture/ARCH-043-database-managed-platform-configuration.md` (17 October source-backed reconciliation).
- Owner: `moda_background` / `moda-interact-background`.
- Source inspection: `moda-interact-workspace(20261017-165350).zip`; re-check paths against the implementation worktree before changes.
- **Defined but not materialised:** no branch, worktree, claim, test run or commit is asserted.

## Objective

Replace the five previously proposed Background consumer integrations with one bounded, reviewable adoption of the accepted `BACKGROUND-008` resolver contract across actual WhatsApp, Shopify, speech and support translation operations.

## Context

This is a bounded Background-owned unit under the five sealed purpose groups approved in ARCH-043. It must reuse the current published `@modainteract/moda-interact-shared/security/credentials/node` implementation (ARCH-039) and the existing database model; do not create new ciphertext formats, independent cryptographic libraries, database migrations, or Shared package publication work. Separate `BACKGROUND-001` owns nonsecret runtime policies and `BACKGROUND-002` owns the original sealed Commerce keyring/Shopify OAuth consumers; neither is replaced.

## Scope

- Update only the concrete Background provider/service call sites listed under `Interfaces / Contracts`.
- Preserve provider method interfaces, existing retry/ordering/charging semantics and service-specific error classification.
- Add dependency injection/composition for resolver snapshots; old environment variables are retired by Gateway only after provider operations prove database parity.
- Add focused regression tests in the existing test hierarchy, including rotated/revoked configuration and cross-provider noninterference.

## Out of Scope

- No provider runtime integration in this task (BACKGROUND-008) / no new generic resolver service API in this task (BACKGROUND-009), as applicable.
- No new Schema/Shared/gateway implementation, global caches, secrets in logs, browser exposure or unrelated refactor.
- No modification of excluded repositories or any `_index.md`.

## Requirements

- Consume `BACKGROUND-008` exports unchanged, never recreate its decrypt/parse logic in each provider.
- Every provider operation resolves one snapshot before the external call; no startup fetch, hot-path query explosion or access to secrets from browser/plugin code.
- Reuse the accepted Background runtime policy readers from BACKGROUND-001 for speech/translation selection, without conflating provider keys.
- Protect token caches against revisions, allow deterministic tests to inject both the resolver and HTTP provider fakes.
- Do not broaden the generic translation provider into unrelated translation/merchant-pricing flows; return any missing support-message caller to architect.
- Keep all previously approved platform/runtime routes, feature admission, WhatsApp provider handling, and billing event idempotency semantics.

## Work Items

- [ ] WhatsApp text/template/sender identity + media download use `resolveWhatsAppSender()` per operation.
- [ ] App Events publish wiring uses `resolveShopifyAppEvents()` and version-scoped token cache; no env credential reader on migrated call path.
- [ ] Partner billing API queries use `resolveShopifyPartner()` for complete tuple, retaining existing interface and behaviour.
- [ ] Speech provider uses `resolveSpeechProvider()` with existing BACKGROUND-001 provider/model selection.
- [ ] Support translation consumes the existing `createTranslationProviderCredentialResolver`/`CommerceTranslationProviderCredential` OpenAI credential in the **correct bounded support path**, and the automatic model selected under BACKGROUND-001; record call-site audit and excluded category/pricing paths. Never use a new `ai.providers` translation key.
- [ ] Add/adjust the listed provider/service regressions including stale revision, revoked, missing, database unavailable, token non-disclosure and failure classification.
- [ ] Verify no old env credential reads remain in the migrated operations and no unrelated call paths changed; document paths changed and evidence.

## Interfaces / Contracts

### Mandatory input contract (do not redefine)

Import `BackgroundPlatformCredentialResolver`, `BackgroundCredentialSnapshot<T>` and `BackgroundCredentialResolutionError` **from the Background-owned module delivered and architect-accepted by `ARCH-043-BACKGROUND-008`**. Do not maintain independent local types or another database/crypto reader in any provider.

Resolver interface:

- `resolveWhatsAppSender()` -> `version` + `{ accessToken, phoneNumberId, businessAccountId }`.
- `resolveShopifyAppEvents()` -> `version` + `{ clientId, clientSecret }`.
- `resolveShopifyPartner()` -> `version` + `{ accessToken, organizationId, appId, apiVersion? }`.
- `resolveSpeechProvider("groq"|"openai")` -> `version` + `{ apiKey }` selected from corresponding `ai.providers` field.
- **No `resolveSupportTranslation()` method.** Support translation uses the existing Background `src/commerce/translation-provider-credential.ts` resolver for OpenAI and BACKGROUND-001's enabled automatic translation-model choice; keep its distinct `CommerceEnvironment` mapping/AAD.

All methods are `Promise`-returning and may raise the redacted typed `BackgroundCredentialResolutionError`; callers must not assume synchronous constructor-time credentials. Do not modify `BACKGROUND-008` contracts or generic resolver code in this task without architect re-review.

### Required runtime integration map (inspection checklist)

| Flow | Inspected 17 October source file(s) | Required change | Preserve / required test |
|---|---|---|---|
| WhatsApp outbound sender | `src/services/whatsapp.service.ts` (`resolveSender`, `getProviderAccountId`, `sendWhatsAppText`, `sendWhatsAppTemplate`) | Replace direct `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_BUSINESS_ACCOUNT_ID` reads with **one** `resolveWhatsAppSender()` snapshot per outbound operation; pass it through sender identity and HTTP transport | Provider sender IDs, template/text payload, idempotency and error semantics; `tests/unit/services/whatsapp.service.test.ts` |
| WhatsApp media download | `src/services/whatsapp-media.service.ts` (`downloadAudio`) | Resolve once before metadata/download pair; keep same token for both HTTP calls | Media size, MIME, timeout, retries; `tests/unit/services/whatsapp-media.service.test.ts`. `WHATSAPP_API_BASE_URL` remains deployment-owned |
| Shopify App Events | `src/services/shopify-usage-event-publisher.service.ts` (`createDefaultClient`, `getProvider`, `publishDue`); `src/providers/shopify-app-events.provider.ts` (`readShopifyAppEventsConfig`, `ShopifyAppEventsClient`) | Hydrate an immutable `resolveShopifyAppEvents()` snapshot for a bounded billing-event publish operation; refactor *cached* client so revision changes invalidate its authentication/token state. Preserve token refresh only within a consistent credential revision; no static indefinitely cached provider constructed from env | App Events retries/claiming/HTTP error classification/pagination; `tests/unit/providers/shopify-app-events.provider.test.ts`, `tests/unit/services/shopify-usage-event-publisher.service.test.ts`, `tests/integration/shopify-usage-event-publisher.concurrency.integration.test.ts` |
| Shopify Partner billing | `src/providers/shopify-partner-billing.provider.ts` (`ShopifyPartnerBillingApi`, `readConfig`, `getActiveSubscription`, `getSubscriptionReconciliationSnapshot`) | Replace token/org/app reads with `resolveShopifyPartner()` per Partner billing API operation; preserve `shopifyPartnerBillingApi` call contract through injection/asynchronous resolution | Subscription/reconciliation correctness and API version handling; `tests/unit/providers/shopify-partner-billing.provider.test.ts`. Do not use shop OAuth/App Events identities |
| Speech transcription | `src/services/speech-transcription.service.ts` (`ProviderSpeechTranscriptionService.transcribe`, `speechTranscriptionService`) | Read `speech.transcription` provider/model policy from prior BACKGROUND-001; call `resolveSpeechProvider(selectedProvider)` once per transcription request and pass API key into selected provider operation | Voice-note MIME/size, model mapping, network errors; `tests/unit/services/speech-transcription.service.test.ts` |
| Support-message translation | `src/commerce/translation-provider-credential.ts` (existing resolver), `src/providers/translation.provider.ts` (`createOpenAITranslationProvider`), plus `translation-batch-submit.service.ts`, `translation-batch-poll.service.ts`, `translation-batch-results.service.ts`, `translation-reconciliation.service.ts` as applicable to the actual support flow | Use the **existing** Commerce translation provider credential (OpenAI) and the verified enabled automatic model chosen by BACKGROUND-001 for *new* support jobs. Pass the decrypted credential explicitly at the call boundary; never resolve it from `ai.providers` or a new `support.translation` row. Preserve old queued job model snapshots. | Focused support job submit/poll/results/reconciliation tests plus `tests/unit/providers/translation.provider.test.ts`. Verify Merchant Pricing and Store Category flows remain on their established credential/model paths, not unintentionally redirected. |

**Translation boundary:** Source inspection found `createOpenAITranslationProvider()` also called from `translation-batch-submit`, `translation-batch-poll`, `translation-batch-results`, `merchant-pricing-translation-*`, `store-category-translation-*`, and `translation-reconciliation` services. These consumers already have distinct credential/model ownership; support-message callers must use the existing Commerce translation provider credential and approved automatic model, not a second key. If the actual support-message caller cannot be isolated in the task worktree, STOP and return the exact discovered ownership gap to `moda_architect`—do not replace all factory calls speculatively.

### Operation-level guarantees

- Retrieve a fresh snapshot at the start of each relevant provider operation, **not** on worker startup, every queued event, media byte/chunk, or shared module import. Do not retain an unbounded global credential cache. Do not load a new revision halfway through a single provider operation; a later operation observes rotation/revocation. Existing per-revision short-lived provider token caches must be tied to revision and invalidated on change.
- Convert Background resolver failure codes to existing provider/workflow error classifications. Missing/revoked/invalid credentials are non-retryable operational configuration failures; DB outages use bounded retry as appropriate. Never retry forever, emit secrets, or fall back to a possibly stale environment credential after a configured bad/revoked row.
- `speech.transcription` is the active speech provider/model policy. `support.translation` is a **retired/migration-only** policy: obtain a valid enabled automatic translation model via BACKGROUND-001 and existing Commerce translation models instead. Do not change `META_APP_SECRET`, `WHATSAPP_VERIFY_TOKEN`, `WHATSAPP_API_BASE_URL`, shop token ownership, Commerce provider credential records, billing/WhatsApp event ordering, or transactional boundaries.

## Dependencies

- `ARCH-043-ADMIN-002`
- `ARCH-043-BACKGROUND-008`
- `ARCH-043-BACKGROUND-001`

## Enables

- `ARCH-043-GATEWAY-001`
- `ARCH-043-SYSTEM-TEST-001`

### 18 October translation integration review gate

- Inspect and report the exact support-message queue creation, batch submit, poll, results, and reconciliation call sites. Preserve `MerchantMessageTranslation` lifecycle, model identity for already-created jobs, ordering and retries; no global provider factory replacement without a proved caller inventory.
- Require the existing `CommerceTranslationProviderCredential` resolver with canonical Commerce-specific AAD, fail closed for absent/revoked/wrong-environment/bad credential. No silent env fallback or new `ai.providers.openAiTranslationApiKey` usage for support translation.
- A valid enabled `CommerceTranslationModelConfiguration` automatic default must be selected for new support-message work via BACKGROUND-001; existing job snapshots do not change when defaults rotate. Record both credential and model revision behaviour in the Completion Report.
- Validate support-message cases alongside non-support translation regression tests to establish no shared-provider collateral changes.


## Acceptance Criteria

- [ ] Existing WhatsApp message sending, media retrieval, Shopify event publishing, Partner billing, speech and support translation tests pass.
- [ ] Rotation causes next operation to use new snapshot; same operation cannot mix old/new identity or cache tokens across revisions.
- [ ] Invalid/revoked provider configuration fails closed without retry storms, dropped billing idempotency or secret leaks.
- [ ] Existing Merchant Pricing/Store Category translation and other provider credential records are unchanged; support caller evidence is explicit.
- [ ] All required dependencies, launcher isolation, targeted validation and code review boundaries are recorded.

## Validation

- [ ] Run listed `tests/unit/services/*.test.ts` and `tests/unit/providers/*.test.ts` plus concurrency integration for App Events.
- [ ] Add support-translation caller-focused tests, wrong-environment and rotation/revocation integration tests.
- [ ] Existing background suite/typecheck/lint/build per package.json and `git diff --check`.
- [ ] Completion Report includes precise mapping of changed call sites to tests and any exceptions discovered.

## Stop Condition

After completing the required Work Items, Acceptance Criteria, and Validation, update the task's Completion Report, move to `review` and STOP. Do not implement the dependent task automatically; architect acceptance gates it.

## Implementation Notes

For every changed provider operation, add a Completion Report review matrix: **source function → original env access removed → resolver method used → query point → version/rotation behaviour → tests run**. An attempted change to `translation.provider.ts` must list every affected consumer to demonstrate unrelated flows remain unchanged.

Follow launcher-prepared isolated parent/implementation worktrees, start-of-attempt synchronisation and current repository conventions. Type definitions are service-local because the consumer and its callers are within one Background repository; do not publish them as a new cross-repository Shared contract. Keep test files under the established `tests/unit/` / `tests/integration/` hierarchy, not beside runtime source. Verify existing package scripts before validation rather than inventing commands. No `_index.md` changes.

## Completion Report

### Status

Not Started

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
