---
id: ARCH-043-BACKGROUND-001
architecture_id: ARCH-043
title: Build reusable Background platform configuration service
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 30
executor: null
claimed_at: null
attempt: 2
depends_on:
- ARCH-043-DATABASE-001
- ARCH-043-ADMIN-002
enables:
- ARCH-043-BACKGROUND-002
created: 2026-10-18
updated: 2026-10-18
---

# Background: provide one typed Platform Configuration service

## Architecture

- Parent: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- **Authoritative 18-key registry (including `omini.moderation`):** `moda-interact-admin/src/lib/admin/platform-configuration/contracts.ts` plus `secrets-contracts.ts`, and `docs/architecture/ARCH-043-configuration-environment-variable-mapping.md`, as supplied 18 October 2026. These are inspected contract sources, NOT a runtime dependency on the Admin repository.
- Owner: `moda_background`; implementation repository: `moda-interact-background`.
- Definition based on `moda-interact-workspace(20261018-105713).zip`; now materialized on parent task branch `task/ARCH-043-BACKGROUND-001`.

### Developer Ownership Amendment

On 2026-10-18, `/moda_developer_create ARCH-043-BACKGROUND-001` was invoked to take over this ready task. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_background`, repository ownership, dependencies, scope and acceptance criteria are unchanged. The canonical launcher will record the developer attempt claim separately.

## Objective

Create ONE reusable, strongly typed, read-only Background platform configuration service that supports the approved registry keys and provides validated, environment-scoped operation snapshots for all keys **authorised for Background**, before any existing Background consumer is changed.

## Context

The user approved exactly two ARCH-043 Background tasks: service/contracts (`BACKGROUND-001`) followed by source-level migration (`BACKGROUND-002`). Earlier `BACKGROUND-001` through `BACKGROUND-009` drafts are replaced by these two unique definitions. PostgreSQL `PlatformConfiguration` / `PlatformConfigurationAudit` already exist under `ARCH-043-DATABASE-001`; Admin's contract-driven writer and sealed secret editor already exist under `ADMIN-001/002`. No new Prisma schema, Shared package, duplicate encryption primitives or caching system is needed.

## Scope

1. Implement a Background-owned registry-aware typed read service and a minimal injectable repository port for `PlatformConfiguration`, obtaining `(environment, key, value, version)` from PostgreSQL.
2. Define and test the complete **18 registered key identities**, preserving exact case, names and fields from Admin and the explicit ARCH-043 PostgreSQL registry. Define service-side read contracts only for the **ten Background-authorised keys** below. Do not expose a permissive `getAnySecret(string)` interface to arbitrary callers.
3. For sealed records, use the existing published `@modainteract/moda-interact-shared/security/credentials/node` primitives, the persisted envelope and frozen AAD bytes. Construct AAD from the trusted row's environment, exact key and version. Never reimplement AES/keyring parsing or invent an alternate envelope.
4. Validate decrypted values or policy JSON strictly, with bounded typed errors, and return fresh per-operation, complete purpose-specific values and their configuration revision.
5. Supply an operation-scoped `readBundle(...)` when multiple keys must be resolved coherently (for example `speech.transcription` plus `ai.providers`). Use one bounded DB read/snapshot, with no external/provider call inside a transaction.
6. Add focused unit tests and a PostgreSQL-backed reader/envelope compatibility test using the existing Background testing infrastructure; do not modify business consumers in this task.

## Out of Scope

- No replacements of env accesses, provider calls, worker creation, route composition, retry policies or Background translation execution in `BACKGROUND-001`.
- No new database models/migrations, Admin changes, Shared release, system-test implementation, `_index.md`, application-wide configuration cache, TTL, Redis key cache, secret fallback to environment, or global provider factory refactor.
- Not a replacement for `BackgroundRuntimeConfig` (existing independent domain configuration). Do not extend its five-second snapshot mechanism to ARCH-043.
- No Background access to Admin/Commerce authentication credentials, `messaging.meta` webhook verification or unrelated Commerce Studio/Grafana/billing keys.

## Requirements

### Authoritative key registry and background access boundary

The service's **key catalog** must reflect exactly these 18 Admin-approved PostgreSQL keys (no historical `merchantKnowledge.upload`, `support.translation`, or `ai.providers.openAiTranslationApiKey`):

| Canonical key | Background read contract |
|---|---|
| `auth.admin` | Registry-known only; denied to Background |
| `auth.commerce` | Registry-known only; denied to Background |
| `commerce.bootstrap` | Registry-known only; denied to Background |
| `commerce.connectionKeys` | `{connectionKeysJson,activeKeyId,commandHmacKey?}`; decrypt/validate as one envelope |
| `shopify.oauth` | `{apiKey,apiSecret}` |
| `shopify.partner` | `{accessToken,organizationId,appId,apiVersion?}` |
| `shopify.appEvents` | `{clientId,clientSecret}` |
| `merchant.knowledge.r2` | `{endpoint,bucket,accessKeyId,secretAccessKey,maxUploadBytes,maxXlsxUncompressedBytes}` (ONE sealed revision) |
| `woocommerce.auth` | Registry-known only; no Background platform-owned consumer evidenced |
| `woocommerce.billing` | Registry-known only; API-004 owns billing consumer |
| `messaging.meta` | Registry-known only; Messaging integration expressly excluded |
| `messaging.sender` | `{accessToken,phoneNumberId,businessAccountId}` |
| `ai.providers` | `{groqApiKey?,openAiApiKey?}`; used as the key for the different providers, selected provider must exist |
| `speech.transcription` | `{provider,groqModelId,openaiModelId}`; provider is `groq` or `openai` |
| `woo.couponSync` | All 10 Admin fields (nine timing/batch limits plus `workerConcurrency`) |
| `admin.grafana` | Registry-known only; denied to Background |
| `commerce.preview` | Registry-known only; denied to Background |
| `omini.moderation` | `{baseUrl: string | null, modelId: string}`; non-secret, read-only policy for `ARCH-040-BACKGROUND-006` |

The contract must not invent older separate Merchant Knowledge policy/storage keys, or move support-translation model/provider ownership out of `CommerceTranslationProviderCredential` and `CommerceTranslationModelConfiguration`.

**Moderation and generic AI credentials:** The exact key is `omini.moderation` (retain this spelling; do not silently alias it to `omni.moderation`). It is a non-secret policy with `baseUrl` (nullable safe HTTPS URL) and `modelId` (bounded, validated model identifier). Current defaults are `https://api.openai.com/v1/moderations` and `omni-moderation-latest`. The moderation policy contains **no OpenAI API credential**. `ai.providers` is a separate sealed credential purpose with optional `openAiApiKey` and `groqApiKey`; these generic provider credentials may be reused by authorised Background consumers, including speech, translation where applicable, and future moderation. The old speech-only field names `openAiSpeechApiKey`/`groqSpeechApiKey` are not part of this contract. A moderation operation requiring OpenAI must fail closed if `openAiApiKey` is absent; it must not fall back to `OPENAI_API_KEY` or introduce another secret key in BACKGROUND-001.

BACKGROUND-001 **exposes typed reads only**, including a purpose-specific `requireModerationOperation()` helper that reads both `omini.moderation` and `ai.providers` as one operation snapshot and returns the moderation revision, credential revision, and credential only to trusted server-side code. `ARCH-040-BACKGROUND-006` owns the OpenAI moderation call, its delivery/charging implications and any conversation-worker integration. BACKGROUND-001 must not make provider calls, change existing translation/speech consumers or expose provider secrets through an HTTP response or log.

### Proposed repository-local API

Use the following semantics; filenames may follow repository conventions:

```ts
type BackgroundReadableKey =
  | "woo.couponSync" | "speech.transcription" | "merchant.knowledge.r2"
  | "commerce.connectionKeys" | "shopify.oauth" | "shopify.partner"
  | "shopify.appEvents" | "messaging.sender" | "ai.providers" | "omini.moderation";

type ConfigSnapshot<T> = Readonly<{ key: BackgroundReadableKey; version: number; value: Readonly<T> }>;
type KeyValues = {
  "woo.couponSync": WooCouponSyncPolicy; // exact Admin contract fields/ranges
  "speech.transcription": SpeechPolicy;
  "merchant.knowledge.r2": MerchantKnowledgeR2Settings;
  "commerce.connectionKeys": CommerceConnectionSecurity;
  "shopify.oauth": ShopifyOAuthCredentials;
  "shopify.partner": ShopifyPartnerCredentials;
  "shopify.appEvents": ShopifyAppEventsCredentials;
  "messaging.sender": WhatsAppSenderCredentials;
  "ai.providers": ProviderApiKeys; // {openAiApiKey?, groqApiKey?}; generic provider credentials
  "omini.moderation": ModerationPolicy; // {baseUrl: string | null, modelId: string}
};
interface BackgroundPlatformConfigurationService {
  read<K extends BackgroundReadableKey>(key: K): Promise<ConfigSnapshot<KeyValues[K]>>;
  readBundle<K extends BackgroundReadableKey>(keys: readonly K[]): Promise<Readonly<{[P in K]: ConfigSnapshot<KeyValues[P]>}>>;
  requireModerationOperation(): Promise<Readonly<{
    moderation: ConfigSnapshot<KeyValues["omini.moderation"]>;
    providerVersion: number;
    openAiApiKey: string; // trusted server-only; never log or expose through HTTP
  }>>;
}
```

`read` must be restricted to the Background allowlist and source a trusted deployment environment. Do not allow caller-supplied environment names, arbitrary key strings, optional generic browser getters, or access to secret records outside the Background allowlist. Underlying injected `readRow`/`readRows` Prisma ports can be mocked; compose real Prisma and crypto only in server-only runtime modules. A service can additionally expose purpose-named helpers (`requireR2`, `requireShopifyPartner`, `requireWhatsAppSender`, `requireSpeechOperation`, `requireCommerceConnectionSecurity`) to reduce consumer interpretation. All operations remain read-only.

### Verification, failure and performance semantics

- Perform a **fresh PostgreSQL lookup per relevant service operation**; within one operation reuse its immutable typed result. No cross-operation in-memory/Redis cache, last-known-good fallback, refresh timer, or boot-time singleton secret capture. For multiple-row operation bundles, require consistent row values from one bounded read statement/transaction, releasing DB resources before provider networking.
- The row's `environment` is a trusted deployment identity, never supplied by a merchant/job payload; no cross-environment or cross-purpose fallback. Missing, revoked, malformed, wrong-environment, AAD mismatch, decryption failure and unavailable DB have distinguishable redacted errors. No environment fallback for a configured invalid/revoked record.
- Keep the canonical AAD bytes `JSON.stringify(["moda-platform-config-v1", environment, key, version, 1])` and ARCH-039 ciphertext format; include deterministic cross-writer vectors compatible with the existing Admin writer.
- Match actual Admin field shapes and hard caps, especially safe R2 endpoint URL/bucket constraints, upload integers, Woo bounds, speech model IDs, Shopify Partner tuple, WhatsApp sender IDs, and optional provider-key selection. `merchant.knowledge.r2` has one version for all six fields; do not split its stored bundle.
- Errors and shared structured logs may contain a bounded reason code, configuration key, row revision and operation correlation ID; never log plaintext, cipher envelope, key material, private tokens or provider request bodies.
- Keep existing deployment/bootstrap environment settings (DB/Redis/OTEL, unseal root, `WHATSAPP_API_BASE_URL`, `MODA_WOOCOMMERCE_CONNECTION_MODE`, etc.) outside this service.

## Work Items

- [x] Inspect the live Admin registry and verify 18 exact keys and Background's ten-key allowlist, including `omini.moderation`; document exact values and field schemas used.
- [x] Implement injectable DB repository, typed contracts/validators, sealed reader with ARCH-039 decryption and AAD, and operation-level snapshot/bundle API.
- [x] Bind the production server-only service through existing Prisma and the shared structured logger.
- [x] Preserve all current Background consumer call sites unchanged in the final BACKGROUND-001 tree. Commit `792a782` restores the consumer files to their state at scoped reader commit `fe55c1c`; no consumer files differ in the net task implementation.
- [x] Test all ten supported reader decoders, denied registered keys, missing rows, wrong environment, wrong key/version AAD, malformed policy, tampering, root mismatch, database outage and selected-provider validation.
- [x] Complete the failure-redaction matrix for malformed/disabled records and prove supplied secret values and underlying exception text are absent from errors/logs; unknown-key denial is covered without disclosing the key.
- [x] Test per-operation fresh reads/revisions, generic `ai.providers` selection, the two-key speech bundle, and the coherent moderation/OpenAI operation bundle.
- [x] Test a complete single-snapshot R2, Commerce connection-keyring, Shopify Partner and WhatsApp sender bundle with full versioned values.
- [x] Test moderation defaults, nullable/safe HTTPS URL, model-ID validation, disabled/missing/malformed and cross-environment rows, fresh revisions, provider-key absence/legacy field rejection, and OpenAI key rotation.
- [x] Include an operation correlation ID and available row revision in bounded failure logs, with assertions that log fields contain no credentials, envelope data or underlying exception details. Do not add moderation SDK requests or worker integration.
- [x] Run focused unit/integration suite, typecheck/lint/build where declared, and `git diff --check`; record launcher-prepared worktree, test and commit evidence.

## Interfaces / Contracts

- Admin registry: `moda-interact-admin/src/lib/admin/platform-configuration/contracts.ts` and `secrets-contracts.ts` (design-time authority, not imported across a source checkout at runtime).
- Key mapping: `docs/architecture/ARCH-043-configuration-environment-variable-mapping.md` (registry now has 18 keys, including `omini.moderation`; update any stale 17-key architecture references separately).
- DB: `PlatformConfiguration` / existing `PlatformConfigurationAudit`; owner `ARCH-043-DATABASE-001`.
- Secret writer: existing accepted `ARCH-043-ADMIN-002`; ciphertext/AAD match its persisted contract.
- Crypto: already published `@modainteract/moda-interact-shared/security/credentials/node`; do not create ARCH-043 Shared tasks.
- Consumers: `ARCH-043-BACKGROUND-002` owns ARCH-043 provider/worker migrations; `ARCH-040-BACKGROUND-006` owns the future moderation integration using this typed reader and the generic OpenAI credential.

## Dependencies

- `ARCH-043-DATABASE-001`
- `ARCH-043-ADMIN-002` (for verified sealed envelope/field contract; completed in this snapshot)

## Enables

- `ARCH-043-BACKGROUND-002`

## Acceptance Criteria

- [x] Exactly the 18 canonical keys are recognised; Background can resolve only its ten authorised keys, with correct fields and shapes.
- [x] A production server-only typed DB reader exists and can be injected/tested without starting a provider/worker.
- [x] Every reader fetches per operation without caching or env fallback; failures are distinguishable and fail closed.
- [x] Encryption/decryption/AAD version and purpose compatibility with Admin is proven using a fixed Admin-produced fixture and changed-purpose/revision negatives, without new Shared crypto or schema.
- [x] Unit and disposable PostgreSQL tests demonstrate validity, rotation, bundle consistency, auth boundary and secret non-disclosure, including `omini.moderation` plus `ai.providers` and old speech-only field rejection.
- [x] No provider, queue job or worker integration remains changed in the final task implementation tree; moderation execution remains with `ARCH-040-BACKGROUND-006`.

## Validation

- [x] Focused `tests/unit/services/platform-configuration/` tests, including moderation policy + generic provider credential reuse (commands derived from actual package scripts).
- [x] PostgreSQL-backed reader/crypto compatibility scenario including moderation revision and generic OpenAI credential rotation using the existing disposable test infrastructure; record Docker/dependency blockers accurately.
- [x] Repository TypeScript typecheck, changed-file lint, applicable build and `git diff --check`.

## Stop Condition

When the single service/contract outcome, its validation and Completion Report are complete, set this task to `review`, return it to `moda_architect` and **STOP**. Do not start `BACKGROUND-002` or update its task state.

## Implementation Notes

Suggested modules: `src/services/platform-configuration/{contracts,repository,service,errors}.ts` and isolated tests under `tests/unit/services/platform-configuration/`. Keep modules modular; do not make a monolithic catch-all service or repeat the same encryption and validation helpers in multiple domain adapters. Production readers may use purpose-specific helpers but there is only ONE Platform Configuration service boundary. Do not change `docs/decisions/**/_index.md`.

## Completion Report

### Status

Developer Self-Review Passed — Attempt 2. Explicit developer completion is pending. Attempt 1 and earlier Attempt 2 review history are preserved below.

### Files Changed

- BACKGROUND-001 service commit `fe55c1c`: eight files (`package.json`, five `src/services/platform-configuration/` modules, and the focused unit/integration tests).
- Subsequent published commit `b94fe1b` on the same task branch: recovery entrypoint, Woo coupon providers/services/worker, speech and translation consumers, operational-policy reader, and their tests. This follow-up commit is outside the reviewed BACKGROUND-001 scope and is not accepted as part of its outcome.
- Attempt 2 published commit `92255e0`: production shared-logger wiring, bounded service outcome logs, fixed Admin-produced `ai.providers` envelope fixture, and focused tests for exact AAD compatibility, secret redaction, and logging-sink failure isolation.
- Attempt 2 corrective commit `792a782`: adds correlation/revision logging and expanded unit/PostgreSQL bundle and redaction coverage; removes the interim operational-policy reader and restores consumer files to their `fe55c1c` state.

### Work Completed

- Added the exact 18-key registry mirror and ten-key Background read allowlist with strict typed decoders, including generic `groqApiKey` / `openAiApiKey` fields and the non-secret `omini.moderation` policy.
- Added injectable single-query repository and per-operation read/readBundle service, canonical ARCH-043 AAD and ARCH-039 shared envelope decryption, trusted deployment environment binding, redacted typed failures, selected speech credential checks, and coherent moderation/OpenAI credential resolution.
- Added server-side Prisma composition and unit plus disposable PostgreSQL coverage. The scoped reader commit `fe55c1c` left consumer call sites unchanged; `b94fe1b` temporarily changed them, and `792a782` restores the final tree to the scoped reader state.
- Attempt 2 added structured success/failure events without logging plaintext, envelopes, or underlying DB/crypto errors; its fixed Admin-produced fixture decrypts with the frozen environment/key/version AAD, and changed key/revision cases are rejected.
- Attempt 2 now covers all ten valid decoder paths, moderation policy freshness and validation, generic provider selection, shared moderation credentials, failure/log redaction, operation correlation IDs and available revisions, plus the complete versioned R2/Commerce connection-keyring/Shopify Partner/WhatsApp sender bundle.
- Commit `792a782` restores the consumer modules to their pre-`b94fe1b` state. Comparing the final implementation tree with `fe55c1c` shows no net consumer changes; the interim operational-policy reader and its integration have been removed.

### Validation Results

- `npx vitest run tests/unit/services/platform-configuration/service.test.ts` — passed, 9 tests.
- `npm run test:arch043-platform-configuration:postgres` — passed, 2 disposable PostgreSQL integration tests.
- Targeted `npx eslint` over the five service modules and two focused test files — passed.
- `npx tsc --noEmit` — passed.
- `npm run build` (Prisma client generation and TypeScript compilation) — passed.
- `git diff --cached --check && git diff --check` — passed.
- Attempt 2: `npx vitest run tests/unit/services/platform-configuration/service.test.ts` — passed, 12 tests.
- Attempt 2: `npm run test:arch043-platform-configuration:postgres` — passed, 2 disposable PostgreSQL integration tests.
- Attempt 2: targeted `npx eslint` over the platform-configuration service modules and unit/integration tests — passed.
- Attempt 2: `npx tsc --noEmit` — passed; `npm run build` (Prisma client generation and TypeScript compilation) — passed.
- Attempt 2: `git show --check --oneline 92255e0` — passed.
- Latest validation: `npx vitest run tests/unit/services/platform-configuration/service.test.ts` — passed, 14 tests.
- Latest validation: `npm run test:arch043-platform-configuration:postgres` — passed, 3 disposable PostgreSQL integration tests.
- Latest validation: targeted ESLint, `npx tsc --noEmit`, and `npm run build` — passed.
- Latest validation: `git diff fe55c1c..HEAD --check` — passed; net diff contains only package script and platform-configuration service/contract/test files, with no Background consumer changes.
- At the Attempt 2 claim handoff, the launcher-resolved implementation worktree was `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-043-BACKGROUND-001`, branch `task/ARCH-043-BACKGROUND-001`, at `92255e09d5bae1829978bfcc5356f7dfc32fa634`.
- Launcher-resolved parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-043-BACKGROUND-001`; branch `task/ARCH-043-BACKGROUND-001`, clean and synchronized with `origin/task/ARCH-043-BACKGROUND-001` before this report update. Attempt 2 claim commit: `ad4abbd94f84d321237e478cc6f574906ca5c576`.

### Deviations

- A follow-up commit `b94fe1b` was published on the BACKGROUND-001 implementation branch after the initial review snapshot. It adds `PlatformOperationalPolicyReader` and changes speech, translation, recovery, Woo coupon and worker consumers, contrary to BACKGROUND-001's explicit no-consumer-change scope. The commit was not reverted or rewritten.
- The unrelated rollout note and newer database submodule state remain preserved outside the implementation task worktree; that worktree remains pinned to the database gitlink recorded by its task branch.

### Assumptions

None

### Unresolved Issues

- None. Historical commit `b94fe1b` introduced consumer/policy changes outside scope; corrective commit `792a782` removes that policy layer and restores the consumer modules to their scoped-reader versions. The final tree has no net consumer changes against `fe55c1c`.
- No required Work Item or Acceptance Criterion remains incomplete in the final task tree. The Architect Review section remains separate and unchanged; this passing self-review is submitted for the developer's explicit completion decision.

### Architectural Concerns

- Historical scope deviation from `b94fe1b` is corrected in the final implementation tree by `792a782`; no net Background consumer changes remain against `fe55c1c`.

## Developer Self-Review - Changes Requested

### Review Status

Changes Requested — Attempt 1.

### Reviewed Files

- The eight files listed in the Completion Report.

### Validation Reviewed

- Focused platform configuration unit suite (9/9).
- Disposable PostgreSQL reader integration suite (2/2).
- Targeted ESLint, TypeScript check, package build and diff checks.

### Scope and Worktree Review

- Commit `fe55c1c` contains the typed reader and focused tests. Later commit `b94fe1b` adds policy and consumer changes outside this task's scope.
- The implementation branch is published through `b94fe1b`; its only local worktree difference at final inspection is the `database` submodule pointer.
- The disposable PostgreSQL, unit and build checks recorded above cover the scoped reader implementation. The operational-policy tests added by `b94fe1b` were not run as BACKGROUND-001 validation.

### Required Corrections

- Add bounded structured failure logging through the existing Background logging path for production service operations. Log only an approved reason code, exact configuration key, revision when available, and operation correlation ID; never log decrypted values, sealed envelopes, unseal material or provider request data. Add focused tests proving secret values and database/crypto exception text are absent from emitted logs.
- Add a fixed sealed `ai.providers` compatibility fixture produced by the Admin `sealSecret` writer and prove the Background reader decrypts it with the exact environment/key/revision AAD. Add negative assertions for changed key and revision, so compatibility is demonstrated across the writer/reader boundary rather than by a test-local envelope assembled with the same reader-side assumptions.
- Add a focused `readBundle()` test for the complete R2, Commerce connection keyring, Shopify Partner, and WhatsApp sender tuple, proving one repository snapshot supplies each complete versioned value.
- Assert failure objects/log output for malformed, tampered, wrong-root and database-unavailable cases cannot contain supplied secret values or sensitive underlying exception text.
- Resolve the scope violation introduced by `b94fe1b`: obtain architect disposition to assign those policy/consumer changes to their owning task, then use a new corrective commit if needed to restore the BACKGROUND-001 branch outcome. Do not reset or rewrite the published branch history.

After the corrections are implemented and validated, invoke `/moda_developer_update ARCH-043-BACKGROUND-001` to reconcile Attempt 2. Do not complete Attempt 1. No merge to `main` is required or performed.

## Developer Self-Review - Changes Requested

### Review Status

Changes Requested — Attempt 2. Corrections are recorded in the later passing Attempt 2 self-review below; attempt history remains unchanged.

### Reviewed Files

- Attempt 2 changes in `src/services/platform-configuration/production.ts`, `src/services/platform-configuration/service.ts`, `tests/fixtures/platform-configuration/admin-sealed-ai-providers.v1.json`, and `tests/unit/services/platform-configuration/service.test.ts`.
- Published scope deviation in `b94fe1b`, including the operational-policy reader and modified recovery, Woo coupon, speech, translation and worker consumers.

### Validation Reviewed

- Focused unit suite: 12/12 passed.
- PostgreSQL-backed reader suite: 2/2 passed.
- Targeted ESLint, `npx tsc --noEmit`, `npm run build`, and `git show --check --oneline 92255e0`: passed.

### Corrections Completed in Attempt 2

- Production composition now injects the existing shared structured logger.
- Service logs bounded success/failure outcomes and suppresses database/crypto exception details; tests check secret/envelope redaction and a throwing log sink.
- A fixed Admin-produced sealed `ai.providers` fixture proves decryption with the persisted ARCH-043 envelope and frozen AAD; changed purpose and revision are rejected.
- Added tests exercise all ten valid reader decoders, generic provider-key selection, moderation policy validation/freshness, and moderation/OpenAI credential rotation.

### Required Corrections Remaining

- Add operation correlation ID and available row revision to bounded failure logs; test secret and exception-detail redaction for those emitted fields.
- Add one `readBundle()` test proving a complete same-snapshot R2, Commerce connection-keyring, Shopify Partner and WhatsApp sender tuple with their revisions.
- Complete explicit redaction coverage for malformed/revoked records and unknown-key denial, including error objects and emitted logs.
- Resolve the `b94fe1b` scope violation through explicit architect disposition and separate task ownership or a new corrective commit. Do not reset or rewrite published history; do not treat the consumer changes as accepted BACKGROUND-001 work without that disposition.

### Scope and Worktree Review

- At the time of the Attempt 2 Changes Requested review, the implementation branch was published through `92255e0`; this historical review record is superseded by the passing review below.
- The parent task branch was clean and synchronized before this review update. The canonical implementation worktree is `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-043-BACKGROUND-001`; the canonical parent worktree is `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-043-BACKGROUND-001`.
- The preserved rollout note and newer database submodule state remain outside the task implementation worktree; the task submodule remains at its recorded gitlink.

## Developer Self-Review Passed

### Review Status

Passed — Attempt 2. The task transitions to `review`; explicit developer completion remains pending because `completion_mode` is `developer`.

### Reviewed Files and Scope

- Reviewed the final net implementation diff from `fe55c1c` through `792a78288cbf72de574264a438af670314c5d99f`.
- The final tree contains the bounded platform-configuration service, its production Prisma/logger composition, contracts, fixture and focused tests. The interim policy module and consumer changes introduced by `b94fe1b` have been removed/restored; no consumer modules differ from the scoped reader baseline.
- The rollout note and newer database submodule state remain preserved outside the implementation task worktree. The task worktree's database submodule remains at its recorded gitlink.

### Validation Reviewed

- Focused unit suite: 14/14 passed.
- PostgreSQL-backed reader suite: 3/3 passed.
- Targeted ESLint, `npx tsc --noEmit`, `npm run build`, and net `git diff --check`: passed.
- Implementation branch is clean and published at `792a78288cbf72de574264a438af670314c5d99f`.

### Work Item and Acceptance Review

- Every Work Item and Acceptance Criterion is complete in the final task tree. In particular, the final tree has no consumer integration, includes the Admin-produced AAD fixture, correlation/revision-bearing bounded logs, redaction coverage, and a complete four-purpose versioned bundle test.
- No known required validation remains outstanding. No provider SDK request, queue integration, or worker migration was added to BACKGROUND-001.

The task is submitted in `review`. The developer must explicitly invoke `/moda_developer_update ARCH-043-BACKGROUND-001 complete` to record completion. No merge to `main` was performed.

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
