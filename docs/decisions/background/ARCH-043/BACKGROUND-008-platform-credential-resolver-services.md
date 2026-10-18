---
id: ARCH-043-BACKGROUND-008
architecture_id: ARCH-043
title: Build Background platform credential resolver services
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
- ARCH-043-BACKGROUND-002
enables:
- ARCH-043-BACKGROUND-009
created: '2026-10-18'
updated: '2026-10-18'
---

# Build Background platform credential resolver services

## Architecture

- Architecture ID: `ARCH-043`
- Canonical document: `docs/architecture/ARCH-043-database-managed-platform-configuration.md` (17 October source-backed reconciliation).
- Owner: `moda_background` / `moda-interact-background`.
- Source inspection: `moda-interact-workspace(20261017-165350).zip`; re-check paths against the implementation worktree before changes.
- **Defined but not materialised:** no branch, worktree, claim, test run or commit is asserted.

## Objective

Expose reusable, testable, DB-backed typed credential resolver services for four sealed Background purposes, **without changing any provider call site**.

## Context

This is a bounded Background-owned unit under the five sealed purpose groups approved in ARCH-043. It must reuse the current published `@modainteract/moda-interact-shared/security/credentials/node` implementation (ARCH-039) and the existing database model; do not create new ciphertext formats, independent cryptographic libraries, database migrations, or Shared package publication work. Separate `BACKGROUND-001` owns nonsecret runtime policies and `BACKGROUND-002` owns the original sealed Commerce keyring/Shopify OAuth consumers; neither is replaced.

## Scope

- Add Background-owned resolver implementation, typed interfaces/errors, production composition and dependency-injection seams.
- Resolve `messaging.sender`, `shopify.appEvents`, `shopify.partner`, and the **two independently selected speech API keys** in speech-only `ai.providers`; support translation uses the existing Commerce translation credential resolver outside this contract.
- Provide environment-scoped lookup, v1 sealed envelope decryption, shape validation, immutable versioned snapshots and bounded diagnostic codes.
- Keep application service operation boundaries and current environment readers unchanged in this first task.
- Place focused unit tests under `tests/unit/services/platform-configuration/` and a bounded disposable PostgreSQL integration test under `tests/integration/` if repository infrastructure supports it.

## Out of Scope

- No provider runtime integration in this task (BACKGROUND-008) / no new generic resolver service API in this task (BACKGROUND-009), as applicable.
- No new Schema/Shared/gateway implementation, global caches, secrets in logs, browser exposure or unrelated refactor.
- No modification of excluded repositories or any `_index.md`.

## Requirements

- **Contract first:** match the `Interfaces / Contracts` signatures below. Test consumers can obtain resolver via composition, without importing unrelated provider classes.
- Do not create another cross-service crypto codec or a new generic logger. If a required Shared crypto export is missing, report to architect rather than copying crypto.
- Strictly distinguish no-row, disabled row, invalid/malformed envelope, wrong key/AAD and DB outage. Missing or invalid service credentials never resolve to blank strings or another purpose.
- Query at most once per resolver invocation, independent of message bytes/LLM tokens; no lookup at worker bootstrap or unrelated queue ingress.
- No networking inside database transactions; no plaintext in logs, audit history, errors or thrown causes.

## Work Items

- [ ] Author contract/types and redacted typed error codes exactly as described.
- [ ] Build injectable PostgreSQL snapshot reader and purpose-scoped decrypt/validation services.
- [ ] Bind production resolver through existing Background Prisma/ARCH-039/structured-logging infrastructure without altering consumers.
- [ ] Add tests for the four resolver methods (speech provider both variants), four purpose mappings, version changes between invocations, and complete-bundle consistency; no support translation key.
- [ ] Add negatives: missing, revoked, bad JSON, tampered envelope/AAD, wrong environment, invalid/missing selected AI key, DB failure, no secret leakage.
- [ ] Run declared focused commands/typecheck/build where applicable, record worktree and validation evidence; stop before BACKGROUND-009.

## Interfaces / Contracts

### Proposed repository-local contract (first task's owned output)

The service exports the following **typed, asynchronous, injectable API** from the Background-owned configuration area (proposed paths `src/services/platform-configuration/credential-resolver.ts` and `credential-contracts.ts`; adapt filenames to the existing code layout but preserve exported semantics):

```ts
export type BackgroundCredentialSnapshot<T> = Readonly<{
  version: number;                // PlatformConfiguration.version for this operation
  credentials: Readonly<T>;       // decrypted, validated, complete purpose bundle
}>;

export type WhatsAppSenderCredentials = Readonly<{
  accessToken: string;
  phoneNumberId: string;
  businessAccountId: string;
}>;
export type ShopifyAppEventsCredentials = Readonly<{
  clientId: string;
  clientSecret: string;
}>;
export type ShopifyPartnerCredentials = Readonly<{
  accessToken: string;
  organizationId: string;
  appId: string;
  apiVersion?: string;
}>;
export type ProviderApiCredential = Readonly<{ apiKey: string }>;

export interface BackgroundPlatformCredentialResolver {
  resolveWhatsAppSender(): Promise<BackgroundCredentialSnapshot<WhatsAppSenderCredentials>>;
  resolveShopifyAppEvents(): Promise<BackgroundCredentialSnapshot<ShopifyAppEventsCredentials>>;
  resolveShopifyPartner(): Promise<BackgroundCredentialSnapshot<ShopifyPartnerCredentials>>;
  resolveSpeechProvider(provider: "groq" | "openai"):
    Promise<BackgroundCredentialSnapshot<ProviderApiCredential>>;
}

export type BackgroundCredentialResolverDependencies = Readonly<{
  getTrustedEnvironment: () => string;
  readRow: (environment: string, key: string) => Promise<null | Readonly<{
    version: number;
    value: unknown;               // sealed envelope or explicit revoked tombstone
  }>>;
  decrypt: (input: Readonly<{
    environment: string;
    key: string;
    version: number;                // persisted row revision used by canonical AAD
    sealedValue: unknown;
  }>) => unknown;                 // production adapter MUST use published ARCH-039 crypto + canonical AAD
}>;

export function createBackgroundPlatformCredentialResolver(
  dependencies: BackgroundCredentialResolverDependencies
): BackgroundPlatformCredentialResolver;

export type CredentialResolutionFailureCode =
  | "NOT_CONFIGURED"
  | "REVOKED"
  | "INVALID_CONFIGURATION"
  | "DECRYPT_FAILED"
  | "DATABASE_UNAVAILABLE";
export class BackgroundCredentialResolutionError extends Error {
  readonly code: CredentialResolutionFailureCode;
  // Bounded, redacted error; never include plaintext/envelope, token or key.
}
```

`resolveSpeechProvider("groq")` selects `groqSpeechApiKey`; `resolveSpeechProvider("openai")` selects `openAiSpeechApiKey`. They are the **two speech fields** of the single `ai.providers` row; missing the selected field fails rather than borrowing another provider's key. Require the approved specific field at the point of use. The version belongs to the **whole** sealed record; selecting one credential does not create a distinct key-version table.

**Purpose / row mapping** (single authoritative PostgreSQL read per resolver call; the environment is derived from trusted deployment configuration, not accepted as an arbitrary caller parameter):

| Resolver | `PlatformConfiguration.key` | Decrypted typed JSON |
|---|---|---|
| `resolveWhatsAppSender` | `messaging.sender` | `{accessToken,phoneNumberId,businessAccountId}` |
| `resolveShopifyAppEvents` | `shopify.appEvents` | `{clientId,clientSecret}` |
| `resolveShopifyPartner` | `shopify.partner` | `{accessToken,organizationId,appId,apiVersion?}` |
| `resolveSpeechProvider` | `ai.providers` | selected speech API key |


**Resolution semantics:** Determine the deployment environment server-side, read `(environment,key)` once, distinguish absent row, explicit disabled/revoked tombstone, invalid JSON/envelope, cryptographic failure and database outage. Decrypt the canonical v1 envelope with the published ARCH-039 Node-only helper, preserving the existing AAD byte contract, then validate the **complete purpose shape** with bounded exact fields. Return an immutable *operation snapshot* with its current `version`. Do not mix fields from environment sources, substitute another purpose, retry by falling back on database failures or reuse cached decrypted credentials across operations. The new credential resolver itself is DB-only; any explicit rollout coexistence belongs to BACKGROUND-009 and must not bypass a present invalid/revoked record. No DB read or external provider request inside a transaction.

**Injection/testability:** Provide a factory that accepts a narrow Prisma configuration-reader port, an environment-identity supplier (trusted), and decryptor/test seam. Production factory binds to canonical Prisma/client and published crypto. Tests inject fakes; no module-global process-env lookups in domain methods, no constructor-triggered DB calls, no unbounded cache or credential logging.

The exported error codes are stable for Background callers; error messages/log fields are redacted. Handle retries according to owning operation: DB unavailable may be transient; invalid/revoked/missing secrets must not cause blind retry storms. No part of this first task invokes WhatsApp, Shopify or AI provider endpoints.

## Dependencies

- `ARCH-043-ADMIN-002`
- `ARCH-043-BACKGROUND-002`

## Enables

- `ARCH-043-BACKGROUND-009`

### 18 October contract narrowing (controlling)

`BackgroundPlatformCredentialResolver` exposes **only** `resolveWhatsAppSender()`, `resolveShopifyAppEvents()`, `resolveShopifyPartner()` and `resolveSpeechProvider("groq"|"openai")`. No `resolveSupportTranslation()` export, `openAiTranslationApiKey` parsing or translation provider credential duplication is permitted. The approved support workflow already has a separate Background-owned resolver at `src/commerce/translation-provider-credential.ts` using `CommerceTranslationProviderCredential`. Explicitly test that legacy `ai.providers` JSON with a translation field cannot silently make that field authoritative. Preserve published ARCH-039 crypto and existing typed redacted failures.


## Acceptance Criteria

- [ ] All four resolver methods have stable types, tested with realistic decoded payloads (both speech choices separately).
- [ ] Every returned snapshot carries one version and complete immutable typed credentials.
- [ ] Each operation fetches only its purpose, with no cross-operation stale values or environment fallback; no provider call sites changed.
- [ ] Failure classification and sensitive-information redaction are verified.
- [ ] Tests live in existing test hierarchy and recorded runtime typecheck/build passes.

## Validation

- [ ] Focused new unit tests (normal repository test runner; test files in `tests/unit/`).
- [ ] Disposable PostgreSQL reader/migration-compatible integration where available.
- [ ] Prisma typecheck, lint/build per repository scripts, `git diff --check`.
- [ ] Start-of-attempt isolated-worktree, branch, submodule and sync evidence.

## Stop Condition

After completing the required Work Items, Acceptance Criteria, and Validation, update the task's Completion Report, move to `review` and STOP. Do not implement the dependent task automatically; architect acceptance gates it.

## Implementation Notes

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
