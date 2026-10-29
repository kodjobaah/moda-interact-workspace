---
id: ARCH-043-MESSAGING-001
architecture_id: ARCH-043
title: Resolve Meta webhook authentication credentials from sealed platform configuration
task_kind: implementation
domain: messaging
repository: moda-interact-messaging
assigned_agent: moda_messaging
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 30
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-043-DATABASE-001
  - ARCH-043-ADMIN-002
enables: []
created: 2026-10-28
updated: 2026-10-28
---

# ARCH-043-MESSAGING-001 — Database-backed Meta webhook credentials

## Architecture

- Parent: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`, **28 October 2026 Messaging cutover addendum**. The addendum specifically supersedes the earlier ARCH-043 ban on a Messaging `messaging.meta` runtime consumer.
- Admin plaintext contract authority: `moda-interact-admin/src/lib/admin/platform-configuration/secrets-contracts.ts` and `secret-validation.ts`; accepted writer `ARCH-043-ADMIN-002`.
- Database authority: existing `public."PlatformConfiguration"` model and unique `(environment,key)` constraint; accepted `ARCH-043-DATABASE-001`.
- Reference pattern only: `moda-interact-background/src/services/platform-configuration/{repository,service,production}.ts`. Do **not** import, modify, move or copy Background modules.
- Execution is **only** in `moda-interact-messaging`; use the existing published Shared package for cryptography and logging. No new Shared, Admin, Background, API, Gateway, Database or System Test implementation task is authorised by this definition.
- **Materialisation history:** this definition was initially supplied portably and was later materialised and executed through the canonical launcher-resolved parent and Messaging implementation worktrees. Attempt 1 worktree and synchronization evidence is recorded in the Completion Report.

## Objective

Replace the Messaging app's environment-variable Meta webhook **GET verification token and POST signature secret** with an operation-fresh, environment-scoped read of the already existing, Admin-sealed `messaging.meta` record in PostgreSQL, without changing webhook dispatch/queue business behaviour.

## Context

- Current `app/lib/whatsapp/webhook-auth.server.ts` reads `process.env.WHATSAPP_VERIFY_TOKEN` and `process.env.META_APP_SECRET`. `app/routes/whatsapp.tsx` uses these for `loader()` (GET) and `action()` (POST).
- Admin already persists `messaging.meta` as a sealed v1 envelope and validates a two-field plaintext payload `{appSecret, verifyToken}`. The developer confirmed an existing `test` record at version `1` and `kind='sealed'`; that fact does **not** establish that the stored plaintext matches live Meta credentials.
- Messaging has **no Prisma client/schema submodule or database connection**. Use a small Messaging-owned, parameterised PostgreSQL `pg` repository and an injectable typed reader; do not introduce a Prisma schema checkout or clone Background's generic all-purpose configuration registry.
- Existing `@modainteract/moda-interact-shared@2.5.1` already publishes the ARCH-039 Node-only crypto functions. **Developer direction: no new shared primitive, export, task or package release.** Implement strict ARCH-043 envelope parsing/AAD and purpose-specific validation locally in Messaging, byte-compatible with Admin.
- The authenticated event dispatcher, normalization, BullMQ publication and existing Meta template-status handling are **unchanged**.

## Scope

**Only these Messaging repository source, dependency and test touchpoints are authorised:**

| Existing/new path relative to `moda-interact-messaging/` | Required operation and ownership |
|---|---|
| `package.json`, `package-lock.json` | Add `pg` runtime dependency and `@types/pg` development types using the repository's npm lockfile; do not upgrade Shared or unrelated dependencies. |
| `app/lib/platform-configuration/meta-contract.server.ts` **NEW** | Local, server-only `messaging.meta` purpose types, exact closed-field validator, typed safe failure codes and row/snapshot interfaces. |
| `app/lib/platform-configuration/meta-repository.server.ts` **NEW** | Single-key `pg`-backed read-only PostgreSQL adapter; parameterised SQL, injectable query dependency, at most one row. |
| `app/lib/platform-configuration/meta-reader.server.ts` **NEW** | Injectable read/decrypt/validate service using only existing Shared Node crypto, frozen ARCH-043 AAD, independent keyring provider and redacted structured outcomes. |
| `app/lib/platform-configuration/meta-production.server.ts` **NEW** | Server-only production composition of bounded `pg.Pool`, trusted environment identity, external unseal material, reader and Shared logger. |
| `app/lib/whatsapp/webhook-auth.server.ts` | Make HMAC checking credential-argument-driven; remove both environment-backed Meta-secret getters. Preserve exact raw-body HMAC and constant-time signature comparison. |
| `app/routes/whatsapp.tsx` | Await one credentials snapshot per eligible GET or signed POST; preserve GET/POST separation, response bodies and dispatcher injection; add fail-closed redacted configuration-unavailable response. |
| `app/lib/observability/whatsapp-ingress-telemetry.ts` | Extend **existing** bounded semantic telemetry to cover configuration-unavailable POST as reason `configuration_unavailable` / HTTP `503`, without introducing a duplicate request metric or new telemetry framework. |
| `tests/platform-configuration-meta-reader.test.mjs` **NEW** | Strict envelope/contract/AAD/rotation/malformed/secret-redaction unit tests using injected row repository and keyring. |
| `tests/platform-configuration-meta-postgres.test.mjs` **NEW** | Disposable PostgreSQL integration checks for the parameterised `pg` repository and committed row revisions; explicit opt-in test database guard. |
| `tests/whatsapp-webhook-auth.test.mjs` | Adapt HMAC tests to explicit secret parameter and GET tests to injectable configuration reader; remove env-secret fixture reliance. |
| `tests/whatsapp-webhook-route.test.mjs` | Adapt signed, unsigned, malformed, mixed-event, publisher-failure and authentication tests to reader injection. |
| `tests/whatsapp-template-status-route.test.mjs` | Preserve all template-status acceptance and queue-failure tests using injected credentials. |
| `tests/whatsapp-webhook-preflight-telemetry.test.mjs` | Preserve preflight/telemetry assertions with DB-backed reader test seam. |
| `tests/whatsapp-queue-telemetry.test.mjs` | Preserve optional Redis/trace test, replacing `META_APP_SECRET` test env mutation with injected credentials. |
| `tests/whatsapp-ingress-telemetry.test.mjs` | Assert bounded `configuration_unavailable`/503 observation and failure isolation. |
| `README.md` | Document database-backed webhook credential source, required external runtime inputs, readiness/failure semantics and removal of old runtime token requirements. |

Test helpers may be placed under `tests/helpers/` **only** if necessary for deterministic fixture reuse across the listed tests; do not add a second configuration service or unrelated production modules.

## Out of Scope

- **NO changes or tasks** in `moda-interact-shared`, Admin, Background, API, Database, Gateway, System Test or any other repository; no new Shared primitive, schema, codec, AAD export or package publication. Do not import Admin/Background application code at runtime.
- Do not modify `PlatformConfiguration`, migrations, audit models, Admin editor contracts, `messaging.sender`, outbound sender credentials, Meta template models, BullMQ contracts, normalization, queue names, retry policy, worker processing or CommerceAgent.
- No private credential-returning HTTP API, service-to-service secret proxy, Redis/HTTP cache, fallback to old `WHATSAPP_VERIFY_TOKEN`/`META_APP_SECRET`, or adoption of credentials from an unrelated environment.
- Do not change `GET /health`, `GET /ready`, Render Blueprint or environment groups in this Messaging implementation task. **Operational deployment wiring is a separate prerequisite** and cannot be achieved by edits within Messaging. Do not claim the deployed test service works until the required variables/access have been provisioned.
- No generic cross-purpose configuration reader; accept **only** `messaging.meta` as a read key.
- No new Meta webhook event types or changes to business handling of `message_echoes`, template-quality/category updates or `messaging_handovers`.

## Requirements

### R1 — Fixed database and plaintext contract

- Key literal: `messaging.meta`; environment: trusted deployment `DEPLOYMENT_ENVIRONMENT_NAME` (the test deployment is `test`). Never accept environment/key from HTTP query, webhook body, tenant, WABA or Meta payload. Enforce allowlist `local|test|development|staging|production`; hosted deployments must explicitly supply `DEPLOYMENT_ENVIRONMENT_NAME` (do not silently use `NODE_ENV=production` to select a database record).
- Read **one** fresh snapshot per eligible webhook HTTP request; no across-request cache, timer, last-known-good or environment secret fallback. Reuse only the *connection pool*, never the plaintext credential snapshot.
- Existing table/fields: `public."PlatformConfiguration"` with `environment: string`, `key: string`, `version: positive integer`, `value: JSON object`. Unique `(environment,key)` already exists; do not add schema/migration.
- Decrypted plaintext must be an object with **exactly two own fields** named `appSecret` and `verifyToken`; both nonempty trimmed strings, UTF-8 length ≤4096 each, no control characters, no additional properties; bound whole plaintext JSON to ≤8192 UTF-8 bytes. Match Admin `secret-validation.ts` rules for `messaging.meta`, not the API's older uppercase-name interpretation.
- Expose neither plaintext credentials nor the sealed row outside the server reader or into request/response/log/error objects. The caller gets a readonly `{ key, version, value: {appSecret, verifyToken} }` snapshot; never expose the raw stored envelope.

### R2 — Fixed sealed-envelope and cryptographic contract

- Stored `value` is **exactly** one of: `{kind:'disabled',schemaVersion:1}` (reject with `DISABLED`), or `{kind:'sealed',schemaVersion:1,algorithm:'AES-256-GCM',wrappingKeyId,nonce,ciphertext,authTag}` (no extra/missing fields). Reject plaintext, unknown kind, algorithm/version and malformed values.
- Validate key ID against `/^[A-Za-z0-9_-]{1,64}$/` and disallow `__proto__`, `prototype`, `constructor`. Parse `nonce`, `ciphertext`, `authTag` as strict **canonical standard base64** (not base64url), with `nonce` = 12 decoded bytes, `authTag` = 16 decoded bytes, ciphertext nonempty and bounded ≤8192 decoded bytes; round-trip base64 must match input.
- AAD bytes **must** be `JSON.stringify(["moda-platform-config-v1", environment, "messaging.meta", version, 1])` after validating trusted environment, fixed purpose and positive safe-integer version. No different spacing, additional fields, JSON object representation or fallback AAD. Authentication must fail if environment, purpose, version, ciphertext, nonce or auth tag is changed.
- Import **only existing** published `decryptCredential`, `parseCredentialKeyring`, `resolveActiveCredentialKey` and types from `@modainteract/moda-interact-shared/security/credentials/node`. Do not implement AES-GCM or keyring parsing locally or modify Shared.
- The *independent* external `MODA_CONFIG_UNSEAL_KEY` and `MODA_CONFIG_UNSEAL_ACTIVE_KEY_ID` supply the wrapping keyring and active key selection; parse/validate on each read (not module import), allowing old-row key IDs during rotation. Never use `messaging.sender` token, Commerce credential keyring, Meta app secret or a generated default as an unseal key.
- An absent/wrong keyring, tampered envelope, wrong AAD or malformed plaintext fails closed. Do not expose raw driver, crypto, PostgreSQL or decryption exceptions; log bounded reason codes only.

### R3 — Exact service and repository interfaces

Provide the following purpose-local interfaces (names/signatures are binding, except import paths may use normal project-relative aliases):

```typescript
export type MetaWebhookCredentials = Readonly<{
  appSecret: string;
  verifyToken: string;
}>;
export type MetaConfigRow = Readonly<{
  environment: string;
  key: string;
  version: number;
  value: unknown;
}>;
export type MetaCredentialsSnapshot = Readonly<{
  key: "messaging.meta";
  version: number;
  value: MetaWebhookCredentials;
}>;
export type MetaConfigurationFailureCode =
  | "MISSING" | "DISABLED" | "INVALID" | "UNSEAL_FAILED" | "DB_UNAVAILABLE";
export class MetaConfigurationFailure extends Error {
  readonly code: MetaConfigurationFailureCode;
}
export interface MetaConfigRepository {
  readMeta(environment: string): Promise<MetaConfigRow | null>;
}
export interface MetaWebhookCredentialsReader {
  read(): Promise<MetaCredentialsSnapshot>;
}
export type MetaUnsealKeyringProvider = () => CredentialKeyring;
export function createPgMetaConfigRepository(
  db: Pick<Pool, "query">,
): MetaConfigRepository;
export function createMetaWebhookCredentialsReader(input: {
  repository: MetaConfigRepository;
  environment: string;
  unsealKeyring: MetaUnsealKeyringProvider;
  logger?: Pick<StructuredLogger, "info" | "warn">;
}): MetaWebhookCredentialsReader;
export function getProductionMetaWebhookCredentialsReader(): MetaWebhookCredentialsReader;
```

- `CredentialKeyring` is the existing Shared Node crypto type; `StructuredLogger` is the existing Shared logging type; `Pool` is from `pg`. Keep typings/imports in `.server.ts` modules.
- **SQL contract** in the `pg` repository (one parameterised, read-only statement per request):

```sql
SELECT "environment", "key", "version", "value"
FROM public."PlatformConfiguration"
WHERE "environment" = $1 AND "key" = $2
LIMIT 2
```

Bind `$1` to the validated trusted environment and `$2` to the literal `messaging.meta`. Reject >1 result; validate returned `environment`, `key` and `version` again in the reader. Return `null` for zero rows. Map DB/connection timeouts to `DB_UNAVAILABLE`, never include SQL text, URL or driver error in public failure messages. Do **not** read audit table or other secret purposes.
- Production composition owns a lazily connected process-local `pg.Pool` with a small bounded pool (default max 2), explicit finite connect/query timeouts and safe idle-client error reporting; close connections in test teardown. Do not open a PostgreSQL connection at module-import time or create one pool per HTTP request.
- Shared `createLogger({serviceName:'moda-interact-messaging', environment})` for structured success/failure events, e.g. `messaging.platform_configuration.read_succeeded` / `read_failed`. Only `{key:'messaging.meta',reasonCode,version?,correlationId}` and already-validated deployment identity may appear; never include token, secret, ciphertext, wrapping keys, AAD, DB URL, raw row or error message/stack. Logging-sink errors must not alter webhook correctness; application failures must **not** be silently swallowed.
- The reader must be injectable in tests and used by both GET and POST. All calls to `.read()` represent an **operation-time** database read, so rotation/revocation is visible without redeploy.

### R4 — Route and signature touchpoints / HTTP contract

- Preserve `loader({request})` for **GET `/webhook/whatsapp`**, `action({request}, dispatch=dispatchWhatsAppWebhook)` for **POST `/webhook/whatsapp`**, and the existing dispatcher-only test seam. Add a separate optional injected `MetaWebhookCredentialsReader` parameter (GET second argument; POST **third** argument) defaulting to the same production reader. React Router production will still supply only the first framework argument. Do not change route path or `app/routes.ts`.
- GET: malformed/missing mode/token/challenge can return `403 Forbidden` without a database read; for an eligible verification GET, perform **exactly one** `reader.read()` and compare the supplied token with `snapshot.value.verifyToken`, preserving `200` with exact challenge and `Content-Type: text/plain` on match, `403 Forbidden` on mismatch. Do not echo token or ciphertext.
- POST: check `POST` method, read **raw original bytes/string**, and reject missing/obviously malformed `x-hub-signature-256` (`401 Unauthorized`) before querying DB; for a syntactically signed candidate, read **exactly one** credentials snapshot and call `verifyMetaSignature(request, rawBody, snapshot.value.appSecret)`. Keep signature validation **before** JSON parse, preflight and queue operations, and preserve timing-safe comparison. Reject wrong signatures `401`; malformed signed JSON/payload `400`; successfully dispatched payload `200 EVENT_RECEIVED`; downstream publisher failures remain non-acknowledged.
- Auth module public HMAC signature becomes `verifyMetaSignature(request: Request, rawBody: string, appSecret: string): boolean` (pure w.r.t. environment). Remove `getWhatsAppVerifyToken()` and the `getMetaAppSecret()` env read entirely; GET compares the injected snapshot's token. No plaintext Meta secret reads anywhere else in Messaging.
- If DB unavailable, row missing/disabled/invalid, decryption fails or unseal keyring absent, **no verification success and no dispatch/queue publication**: return bounded `503 Service Unavailable` for eligible GET/POST, with a safe log reason; never mistake a configuration outage for `401 Invalid signature`, return `200`, or use old env secrets. Add the single bounded `configuration_unavailable`/503 semantic observation to the existing POST ingress telemetry. Unknown/programmer errors still propagate through the existing route exception/telemetry path; never turn queue errors into 503 configuration errors.
- Preserve existing signed template-status, messages/status, preflight, queue publication and timing behaviour. This task does **not** expand supported Meta webhook field types.

### R5 — Deployment boundary (documentation only in this task)

- Existing Render test service `moda-interact-gateway/render.test.yaml` declares `moda-interact-messaging-test` with `moda-interact-test-config`, Redis and **legacy** `moda-interact-test-meta-webhook-config`. It does **not** supply DB or unseal material. The deployed cutover therefore **cannot** work until deployment owner/operator supplies `DATABASE_URL` (test database), `MODA_CONFIG_UNSEAL_KEY`, `MODA_CONFIG_UNSEAL_ACTIVE_KEY_ID` and explicit `DEPLOYMENT_ENVIRONMENT_NAME=test` with secure Render environment handling. Database access should be least-privilege read-only for the required configuration row/table where operationally feasible.
- **Do not modify Gateway in this task** or pretend those values are already provisioned. `README.md` and Completion Report must clearly flag the environment provisioning and eventual removal of old `META_APP_SECRET`/`WHATSAPP_VERIFY_TOKEN` as external rollout steps. The implementation must never rely on the legacy group, even if it remains provisioned during transition.
- Keep existing `GET /health` liveness and `GET /ready` Redis readiness unchanged; configuration outage is expressed on protected webhook requests, not by requiring a DB round trip on every health check.

## Work Items

- [x] Verify exact Admin `messaging.meta` sealed/plaintext writer contract, existing ARCH-043 AAD and already published Shared imports in the pinned Messaging dependency; no Shared changes requested.
- [x] Add `pg` and `@types/pg` to Messaging package/lockfile; `npm ci` and production build passed.
- [x] Implement the **four** specified server-only Messaging configuration modules, with closed-purpose SQL, injectable repository, strict parser/validator, Shared decryption and trusted-env production composition.
- [x] Replace environment Meta-secret reads in `webhook-auth.server.ts` and wire GET/POST `whatsapp.tsx` using the specified injection seams, one snapshot/request and redacted 503 failure contract.
- [x] Extend existing ingress telemetry only with `configuration_unavailable` and status 503; use Shared structured logger and safe error/sink behaviour.
- [x] Update the existing webhook/queue test suites and ingress telemetry suite; preserve original regression coverage. The task's named `tests/whatsapp-webhook-preflight-telemetry.test.mjs` does not exist; updated and ran the actual `tests/whatsapp-webhook-preflight.test.mjs` suite instead.
- [x] Add purpose-contract, sealed-envelope/crypto, rotation and guarded PostgreSQL read-integration tests with deterministic Admin-compatible ciphertext fixtures; no live Meta credentials used.
- [x] Update Messaging README for required database/unseal environment variables and rollout prerequisite; no other repository changed.
- [x] Record isolated parent/implementation worktree packet, sync evidence, files, tests and blockers in Completion Report; set task to `review`.

## Interfaces / Contracts

- **Writer (read-only reference):** `moda-interact-admin/src/lib/admin/platform-configuration/{secrets-contracts,secret-validation,seal}.ts` — plaintext `{appSecret,verifyToken}`, sealed envelope and canonical AAD. This writer is **not** a runtime import.
- **Table (read-only):** `public."PlatformConfiguration"`, existing `@@unique([environment,key])`; approved `ARCH-043-DATABASE-001`.
- **Shared published, unchanged:** `@modainteract/moda-interact-shared/security/credentials/node` (`decryptCredential`, `parseCredentialKeyring`, `resolveActiveCredentialKey`, `CredentialKeyring`) and `@modainteract/moda-interact-shared/logging` (`createLogger`, `StructuredLogger`). Do not add any new shared entrypoint.
- **Messaging local reader API:** `MetaWebhookCredentialsReader.read()` returns `MetaCredentialsSnapshot` as specified in R3. Only `messaging.meta` may be read.
- **Messaging local HMAC API:** `verifyMetaSignature(request,rawBody,appSecret)`; no token secret env getters.
- **Messaging route API:** original React Router GET/POST exports, original `dispatchWhatsAppWebhook` event handoff and original queue contracts. Add dependency-injected reader parameters solely for testability.
- **External configuration:** `DATABASE_URL`, `DEPLOYMENT_ENVIRONMENT_NAME`, `MODA_CONFIG_UNSEAL_KEY`, `MODA_CONFIG_UNSEAL_ACTIVE_KEY_ID`, provided by deployment; not secret data in source. Old Meta runtime env values are ignored by Messaging code after change.
- **No publication dependency:** Shared already at 2.5.1 in this repository; do not create a Shared task or version upgrade.

## Dependencies

- `ARCH-043-DATABASE-001` — **Complete in supplied 28 October snapshot**; contains table and constraints.
- `ARCH-043-ADMIN-002` — **Complete in supplied 28 October snapshot**; owns the sealed writer and closed plaintext contract.

Neither Background nor a newly invented Shared task is a dependency. Launcher must revalidate these statuses on the developer's **canonical task branch** before claim.

## Enables

None within this standalone implementation definition. Live deployment requires separately provisioned credentials/database connectivity and later integrated verification; do not silently create or start a Gateway/System Test task.

## Acceptance Criteria

- [x] Both GET verification and POST HMAC use the explicit trusted deployment environment and `messaging.meta` DB sealed row, never the two old Meta env vars, with **one** fresh row read per eligible request and no cross-request credential cache.
- [x] Purpose, environment, version, seven sealed fields, base64 encoding/length, ciphertext/AAD/auth-tag and decrypted `{appSecret,verifyToken}` exact schema are validated, using **only existing Shared crypto**.
- [x] Missing, disabled, malformed, wrong-purpose, wrong-environment, old revision, wrong key, tampered nonce/tag/ciphertext, absent keyring, database unavailable and query timeout fail closed with bounded failures. The guarded real PostgreSQL integration passed; the timeout-specific test verifies PostgreSQL SQLSTATE `57014` becomes `DB_UNAVAILABLE` and the signed webhook returns 503 without dispatch.
- [x] Each read fetches a fresh row; credential and wrapping-key rotation behavior is covered by tests, with current values used on the next operation without a process restart.
- [x] GET/POST response, signature ordering, configuration 503, dispatch, payload and queue-failure behavior are covered by the passing route/authentication tests.
- [x] Existing `message_template_status_update`, inbound `messages`, delivery statuses, queue payloads and dispatch ordering remain unchanged; existing route/queue regression tests pass with injected readers.
- [x] The pool is bounded and the integration fixture closes its pool; query is parameterised and fixed-purpose, with no schema copy, new shared code, cache or changes outside Messaging implementation.
- [x] Shared structured logs and existing telemetry report bounded reason codes/503 without exposing credentials, envelope, AAD, query/error details or sensitive Meta payload; sink-failure behavior is isolated.
- [x] README and Completion Report make external Render DB/unseal provisioning, legacy variable removal and pre-deploy configuration verification explicit; no live test deployment is claimed.

## Validation

- [x] `npm ci` with checked-in lockfile and `npm run typecheck` passed.
- [x] Focused command passed using actual source suite `tests/whatsapp-webhook-preflight.test.mjs` in place of the task's nonexistent `tests/whatsapp-webhook-preflight-telemetry.test.mjs`.
- [x] `npm test` passed (98 passed, 0 failed, 3 skipped); `npm run build` passed. Build printed existing Vite browser-externalization warnings for Node modules imported by ioredis; build completed successfully.
- [x] Disposable PostgreSQL integration passed against a fresh loopback-only PostgreSQL cluster and dedicated `moda_messaging_disposable_arch043_messaging001` database. The accepted ARCH-043 PlatformConfiguration migration was applied; the test's empty-table guard passed and it read, revised, revoked and cleaned up its own disabled fixture row. No live test database or `test/messaging.meta` row was used.
- [x] Deterministic SQL timeout regression passed: PostgreSQL statement-timeout SQLSTATE `57014` is mapped to the generic `DB_UNAVAILABLE` failure, and an eligible signed POST returns 503 with zero dispatcher calls.
- [x] Fixed Admin-compatible encrypted fixtures and deterministic malformed-envelope, AAD, wrong-environment/version, ciphertext/tag, wrong-keyring, disabled/plaintext, redaction, sink-failure and rotation tests passed.
- [x] Optional Redis-backed queue/trace cases were skipped because `TEST_REDIS_URL` is unset. `git diff --check` passed.
- [x] Attempt 2 launcher evidence: parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-043-MESSAGING-001` at pre-claim HEAD `292359677b286d1f552d9f89850abdb159849b12`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-043-MESSAGING-001` at HEAD `69413cb862a575836d28def7c7d713e2f2b51918`. Both branches were `task/ARCH-043-MESSAGING-001`, task-branch fast-forward was not needed, `origin/main` was already current, recursive submodule sync/update passed with no entries. The launcher claim commit was `30be558aa219c19e12955ded0c7c6e5727c9fb19`.

## Stop Condition

After scoped implementation, Acceptance Criteria, required Validation and Completion Report are complete, set this task to `review`, return to `moda_architect`, and **STOP**. Do not implement deployment changes, unrelated event fields, a Shared primitive or any follow-on task. Repository agent must not mark its own task Complete.

## Implementation Notes

- This explicitly chooses direct **`pg`** for a single fixed read in Messaging: it keeps runtime implementation self-contained without Prisma schema copy/generator, and mirrors Background's **behavioural** contract (one database read → strict envelope → Shared unseal → purpose decode), not its source imports or generic registry.
- Four new modules are the maximum authorised production addition for this capability. If a reusable parser would otherwise be factored to Shared, keep the small purpose-specific parser inside `meta-reader.server.ts`; do not initiate a Shared subtask. Use Shared only for **existing** cryptography/logger APIs.
- Keep `.server.ts` boundaries; do not import `pg`/Shared Node crypto in browser-accessible modules. The production reader should be lazy, constructed once and injectable; it must not open new pools per request or store plaintext across calls.
- The route already injects `dispatch` as the **second** `action` parameter. Preserve that seam exactly and add credentials reader as **third**. Tests must not silently call real PostgreSQL by omitting the injected reader.
- `NODE_ENV=production` occurs on Render test deployments. Use explicit `DEPLOYMENT_ENVIRONMENT_NAME=test` rather than selecting `production` based on `NODE_ENV`.
- Contract sample for the Meta verify endpoint: `GET /webhook/whatsapp?hub.mode=subscribe&hub.verify_token=...&hub.challenge=...`; the GET **does not** publish any queue message. Meta later sends independent POST webhooks. The task changes only credential source, not HTTP flow.
- Secure deployment environment provision and infrastructure changes are **not** part of this Messaging code task. Do not claim acceptance of a live cutover based on unit tests alone; separate end-to-end deployment verification is required.

## Completion Report

### Status

Ready for Architect Review — Attempt 2 corrections are committed and pushed on the existing Messaging task branch. The task branch is intentionally not merged to `main`.

### Files Changed

`README.md`; `package.json`; `package-lock.json`; `app/lib/platform-configuration/meta-contract.server.ts`; `app/lib/platform-configuration/meta-repository.server.ts`; `app/lib/platform-configuration/meta-reader.server.ts`; `app/lib/platform-configuration/meta-production.server.ts`; `app/lib/whatsapp/webhook-auth.server.ts`; `app/routes/whatsapp.tsx`; `app/lib/observability/whatsapp-ingress-telemetry.ts`; `tests/platform-configuration-meta-reader.test.mjs`; `tests/platform-configuration-meta-postgres.test.mjs`; `tests/helpers/meta-credentials.mjs`; `tests/whatsapp-webhook-auth.test.mjs`; `tests/whatsapp-webhook-route.test.mjs`; `tests/whatsapp-template-status-route.test.mjs`; `tests/whatsapp-webhook-preflight.test.mjs`; `tests/whatsapp-queue-telemetry.test.mjs`; `tests/whatsapp-ingress-telemetry.test.mjs`.

### Work Completed

Added a Messaging-only, read-only `pg` repository for the fixed `messaging.meta` row and an injectable reader that validates the trusted environment, row, sealed envelope, canonical base64, AAD, and exact two-field plaintext using the existing Shared crypto APIs. The production composition creates a lazy bounded pool and parses the independent unseal keyring on each read. No credential snapshot is cached.

GET verification and POST HMAC now use one fresh database-backed snapshot per eligible request; malformed modes and absent/malformed signatures still stop before database access. Configuration failures fail closed with bounded 503 responses and POST semantic telemetry. Old Meta environment variables are no longer read. Structured outcomes use the Shared logger with bounded fields and sink-failure isolation.

Updated documentation and regression tests. Attempt 1 implementation commit: `69413cb` (`Add database-backed Meta webhook credentials`). Attempt 2 added the deterministic timeout regression test and ran the guarded PostgreSQL integration. Latest implementation commit: `24dd41f4ccc8660ab38192c66a281c3d5c0a5976`; both implementation commits are pushed to `origin/task/ARCH-043-MESSAGING-001`.

### Validation Results

Attempt 1 validation remains recorded: `npm ci`, `npm run typecheck`, focused suites, `npm test` (98 passed, 0 failed, 3 skipped), `npm run build`, and `git diff --check` passed. For Attempt 2, the dedicated PostgreSQL integration passed (1 passed, 0 skipped), the focused route suite passed (7 passed, 0 skipped), and the full suite ran with PostgreSQL enabled (100 passed, 0 failed, 2 skipped). The remaining two skips are optional Redis-backed tests because `TEST_REDIS_URL` is unset. `git diff --check` passed. Build warnings from Attempt 1 concerned existing ioredis Node-module browser externalization; the build completed successfully.

### Deviations

The task names `tests/whatsapp-webhook-preflight-telemetry.test.mjs`, which is absent from the repository. Source inspection identified `tests/whatsapp-webhook-preflight.test.mjs` as the actual preflight suite; it was updated and included in focused and full validation. Attempt 2 resolved the prior PostgreSQL and timeout evidence gaps using the dedicated disposable database and deterministic SQLSTATE test described above. No production implementation change was needed.

### Assumptions

The accepted Admin writer contract and Shared crypto API are authoritative. No claim was made about the live plaintext or Meta subscription. The deployment owner will provide and verify database/unseal configuration before hosted cutover.

### Unresolved Issues

Before hosted cutover, provision and verify Render `DATABASE_URL`, `MODA_CONFIG_UNSEAL_KEY`, `MODA_CONFIG_UNSEAL_ACTIVE_KEY_ID`, and `DEPLOYMENT_ENVIRONMENT_NAME=test` with least-privilege database access. Remove legacy `META_APP_SECRET` and `WHATSAPP_VERIFY_TOKEN` only as a coordinated external rollout step. The local disposable PostgreSQL integration does not establish hosted configuration or live Meta credential correctness.

### Architectural Concerns

A PostgreSQL lookup before verifying a syntactically valid signed POST adds database read load and dependency to webhook ingress. Query/pool timeouts and upstream request-rate protection should be assessed during hosted validation; no cache or new gateway implementation is authorised by this task.

### Publication and Review

- Implementation branch: `task/ARCH-043-MESSAGING-001`, latest Attempt 2 commit `24dd41f4ccc8660ab38192c66a281c3d5c0a5976`, pushed to `origin`.
- Parent task/report branch: `task/ARCH-043-MESSAGING-001`; the Attempt 2 review report is being committed and pushed separately.
- Parent submodule pointer was not changed. No merge to `main` was performed.
- Architect follow-up: external Render provisioning and hosted configuration verification remain rollout prerequisites; no dependency task was advanced.

## Architect Review

### Review Status

Changes Requested — validation and record reconciliation only

### Review Notes

The implementation diff at `69413cb862a575836d28def7c7d713e2f2b51918` is within the narrowly authorised Messaging repository scope. The fixed-purpose `pg` query, row/envelope/plaintext checks, use of the existing Shared Node crypto and logger APIs, fresh read per eligible GET/POST, bounded configuration failure handling, and unchanged queue/event contracts are consistent with the ARCH-043 Messaging addendum. The recorded start-of-attempt evidence identifies dedicated parent and implementation worktrees, synchronized task branches and `origin/main`, and successful recursive submodule preparation. Both declared dependencies, `ARCH-043-DATABASE-001` and `ARCH-043-ADMIN-002`, are Complete.

Acceptance is withheld because the task's PostgreSQL integration validation and one part of its explicit failure criterion remain unverified. The Completion Report says the guarded PostgreSQL test was skipped because no disposable database was available, the corresponding acceptance criterion is unchecked, and the report itself says this run is required before acceptance. The repository test does exercise the parameterised repository with injected stubs, but it is not evidence against a real schema-migrated PostgreSQL database. The criterion also explicitly includes query-timeout failure handling; the report does not show a timeout-specific test or live timeout result.

The task's Architecture section still describes this task as a portable, unmaterialised definition, contradicting the prepared worktree and Completion Report. That statement has been corrected to record materialisation history for the next attempt.

No code defect is established by the current evidence. Do not change implementation code unless the requested validation exposes a failure.

### Reviewed Files

- `moda-interact-messaging` implementation branch `task/ARCH-043-MESSAGING-001` at `69413cb862a575836d28def7c7d713e2f2b51918` (18-file task diff from `origin/main`).
- `app/lib/platform-configuration/meta-contract.server.ts`
- `app/lib/platform-configuration/meta-repository.server.ts`
- `app/lib/platform-configuration/meta-reader.server.ts`
- `app/lib/platform-configuration/meta-production.server.ts`
- `app/lib/whatsapp/webhook-auth.server.ts`
- `app/routes/whatsapp.tsx`
- `app/lib/observability/whatsapp-ingress-telemetry.ts`
- `tests/platform-configuration-meta-reader.test.mjs`
- `tests/platform-configuration-meta-postgres.test.mjs`
- Relevant route/authentication/telemetry tests and README.
- `ARCH-043` Messaging cutover addendum and both completed dependency records.

### Validation Reviewed

Reviewed the Completion Report for `npm ci`, `npm run typecheck`, focused suites, `npm test` (98 passed, 0 failed, 3 skipped), `npm run build`, and `git diff --check`. The report explains that the guarded PostgreSQL integration and optional Redis tests were skipped. No tests were rerun. The implementation branch is clean at the reported pushed commit. Passing unit/stub tests do not satisfy the explicitly unchecked real PostgreSQL integration criterion.

### Architecture Conformance

Implementation scope and repository ownership conform. Completion cannot be accepted until database-boundary behavior is validated against a dedicated disposable PostgreSQL database and query-timeout behavior is demonstrated. No external Render provisioning or production cutover is required to accept this bounded code task; those remain rollout prerequisites.

### Follow-up

Return this same task to `ready`, clear `executor` and `claimed_at`, and preserve `attempt: 1` so the next claim increments it exactly once. The next attempt must:

1. Provision a **dedicated disposable, loopback PostgreSQL database** with the required `PlatformConfiguration` schema/migrations and set only the documented opt-in test variables. Run `tests/platform-configuration-meta-postgres.test.mjs` through the repository's declared test command and record a passing result. The fixture's empty-database guard must pass; do not use or mutate the live `test/messaging.meta` row.
2. Add or run a deterministic test for a PostgreSQL query timeout showing it is normalized to `DB_UNAVAILABLE` and the webhook request fails closed with HTTP 503 and no dispatch. Record the command and result. Keep the failure bounded and redact driver details.
3. Update the Completion Report with both results and clear the corresponding unchecked Acceptance Criteria/Validation items. No implementation changes are required if those checks pass.

Keep all other task scope and the external deployment provisioning boundary unchanged. No downstream task is enabled by this standalone definition.
