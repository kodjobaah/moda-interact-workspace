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
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 1
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
- [ ] Bind a production server-only service through existing Prisma and logging while keeping all current Background consumer call sites unchanged.
- [ ] Test all ten supported readers, excluded-key denial, wrong environment/key/version, unsupported key, missing and revoked record, malformed policy/envelope, tampering, root mismatch, DB outage, non-secret validation, and no token leakage.
- [x] Test updated revisions are observed between operations with no caching; the same operation maintains a complete single-version R2/Partner/WhatsApp/Commerce bundle. Test generic `ai.providers` provider-specific missing keys and the two-key speech bundle.
- [x] Test `omini.moderation` defaults, nullable/safe HTTPS URL, model-ID validation, disabled/missing/malformed and cross-environment rows, and fresh revisions; test `requireModerationOperation()` reads both policy and generic sealed OpenAI credential coherently, including rotation, absent `openAiApiKey`, legacy speech-only field rejection and secret-free errors/logs. Do not add moderation SDK requests or worker integration.
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
- [ ] Encryption/decryption/AAD version and purpose compatibility with Admin is proven without new Shared crypto or schema.
- [ ] Unit and disposable PostgreSQL tests demonstrate validity, rotation, bundle consistency, auth boundary and secret non-disclosure, including `omini.moderation` plus `ai.providers` and old speech-only field rejection.
- [x] No provider, queue job or worker integration has been changed in this first task; moderation execution remains with `ARCH-040-BACKGROUND-006`.

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

Changes Requested — Attempt 1 reviewed. Attempt remains 1; a subsequent developer claim creates Attempt 2. Attempt 0 review history is preserved below.

### Files Changed

- `package.json`
- `src/services/platform-configuration/contracts.ts`
- `src/services/platform-configuration/errors.ts`
- `src/services/platform-configuration/production.ts`
- `src/services/platform-configuration/repository.ts`
- `src/services/platform-configuration/service.ts`
- `tests/integration/platform-configuration-reader.integration.test.ts`
- `tests/unit/services/platform-configuration/service.test.ts`

### Work Completed

- Added the exact 18-key registry mirror and ten-key Background read allowlist with strict typed decoders, including generic `groqApiKey` / `openAiApiKey` fields and the non-secret `omini.moderation` policy.
- Added injectable single-query repository and per-operation read/readBundle service, canonical ARCH-043 AAD and ARCH-039 shared envelope decryption, trusted deployment environment binding, redacted typed failures, selected speech credential checks, and coherent moderation/OpenAI credential resolution.
- Added server-side Prisma composition and unit plus disposable PostgreSQL coverage. Existing consumer call sites remain unchanged in the committed BACKGROUND-001 implementation.

### Validation Results

- `npx vitest run tests/unit/services/platform-configuration/service.test.ts` — passed, 9 tests.
- `npm run test:arch043-platform-configuration:postgres` — passed, 2 disposable PostgreSQL integration tests.
- Targeted `npx eslint` over the five service modules and two focused test files — passed.
- `npx tsc --noEmit` — passed.
- `npm run build` (Prisma client generation and TypeScript compilation) — passed.
- `git diff --cached --check && git diff --check` — passed.
- Launcher-resolved implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-043-BACKGROUND-001`; branch `task/ARCH-043-BACKGROUND-001`, commit `fe55c1cdfdc564733d72dd5bb6bf6f0642e6012b`, published and up to date with origin.
- Launcher-resolved parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-043-BACKGROUND-001`; branch `task/ARCH-043-BACKGROUND-001`, clean and up to date before this report update.

### Deviations

- The implementation worktree also contains a separate staged `PlatformOperationalPolicyReader` change set that edits speech, translation and Woo coupon consumers, plus a modified `database` submodule pointer. Those changes are outside BACKGROUND-001's explicit no-consumer-change scope; they were left untouched and are not included in the published BACKGROUND-001 commit or this review's task-owned file list.

### Assumptions

None

### Unresolved Issues

- The staged out-of-scope implementation changes and modified `database` submodule pointer remain in the implementation worktree and require separate task ownership/reconciliation. No changes were made to them.

### Architectural Concerns

- None identified in the committed BACKGROUND-001 implementation.

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

- The published BACKGROUND-001 commit changes only the service, its package test command, and focused tests; no provider, queue or worker consumer integration is part of that commit.
- The separate staged consumer/policy changes and `database` submodule pointer remain untouched and are explicitly excluded from this attempt.
- Implementation branch commit `fe55c1cdfdc564733d72dd5bb6bf6f0642e6012b` is published to `origin/task/ARCH-043-BACKGROUND-001`.

### Required Corrections

- Add bounded structured failure logging through the existing Background logging path for production service operations. Log only an approved reason code, exact configuration key, revision when available, and operation correlation ID; never log decrypted values, sealed envelopes, unseal material or provider request data. Add focused tests proving secret values and database/crypto exception text are absent from emitted logs.
- Add a fixed sealed `ai.providers` compatibility fixture produced by the Admin `sealSecret` writer and prove the Background reader decrypts it with the exact environment/key/revision AAD. Add negative assertions for changed key and revision, so compatibility is demonstrated across the writer/reader boundary rather than by a test-local envelope assembled with the same reader-side assumptions.
- Assert failure objects/log output for malformed, tampered, wrong-root and database-unavailable cases cannot contain supplied secret values or sensitive underlying exception text.

After the corrections are implemented and validated, invoke `/moda_developer_update ARCH-043-BACKGROUND-001` to reconcile Attempt 2. Do not complete Attempt 1. No merge to `main` is required or performed.

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
