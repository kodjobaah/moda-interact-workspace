---
id: ARCH-021-COMMERCE-030
architecture_id: ARCH-021
title: Remove application-layer authentication from private Commerce MCP
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 10
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-020-COMMERCE-024
enables:
  - ARCH-021-BACKGROUND-001
created: 2026-09-24
updated: 2026-09-24
---

# Remove application-layer authentication from private Commerce MCP

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Remove RSA/JWT verification and every application-layer caller credential from the private Commerce MCP endpoint. Accept only the bounded `X-Moda-Commerce-Context` request context from the existing private service link while preserving authoritative PostgreSQL shop/turn/grant/release/tool authorization and bounded failure semantics.

## Context

The Commerce MCP endpoint is not a public API. Gateway/Render topology exposes it only over the private service path used by Background. ARCH-020 added RS256 signing, key distribution, `kid` rotation and JWT claim validation on top of that private link. That machinery is not required for the agreed development architecture and must not be replaced with a bearer token, API key, shared secret or another key exchange.

The private service link is the caller trust boundary. The context header remains untrusted lookup/authorization context: Commerce must continue to derive environment locally and verify authoritative shop, conversation, turn, lease, grant, release, manifest and tool state from PostgreSQL before exposing or executing capabilities.

## Scope

Primary repository-owned files include:

```text
.env.example
docs/commerce-backend-integration.md
docs/runtime-compatibility.md
lib/server/config.ts
package.json / package-lock.json
scripts/clean-clone.sh
scripts/readiness-local-smoke.mjs
src/commerce/integration/backend.ts
src/commerce/integration/backend/authorization.ts
src/commerce/mcp/authentication.ts
src/commerce/mcp/authorization.ts
src/commerce/mcp/ports.ts
src/commerce/mcp/service.ts
tests/*mcp*.test.ts
tests/local-external-mcp-diagnostic.test.ts
relevant health/backend/external-wiring tests
```

Modify equivalent existing files only when repository naming differs. Do not create a second MCP authentication module.

## Out of Scope

- Public/private routing changes (GATEWAY-001).
- Background client changes (BACKGROUND-001).
- Removing `CommerceConversationGrant` or DB-backed authorization.
- Weakening tenant/shop/turn/tool checks.
- Adding any replacement token/secret/key/API credential.
- Making MCP browser/public accessible.

## Requirements

### R1. Exact private request context contract

The normal MCP request contains **no Authorization header and no service-auth token**.

It carries exactly one bounded context header:

```http
X-Moda-Commerce-Context: <base64url(JSON UTF-8)>
```

Decoded JSON is exactly the existing bounded context fields:

```text
contractVersion
shopId
checkoutRecoveryId
conversationId
inboundVersion
purpose
optional grantId
optional releaseId
```

`environment` comes only from Commerce server configuration. Do not add `iss`, `aud`, `sub`, `kid`, `jti`, `iat`, `exp`, signature, token or secret fields.

Encoded header maximum length: 8192 characters. Reject missing header, oversized header, invalid base64url, invalid JSON or schema mismatch with explicit bounded MCP errors.

### R2. Private link is the caller trust boundary

Do not inspect `Authorization` as a service-authentication mechanism and do not require any of:

```text
COMMERCE_MCP_SERVICE_TOKEN
COMMERCE_MCP_API_KEY
COMMERCE_ASSERTION_PUBLIC_KEYS
COMMERCE_ASSERTION_PRIVATE_KEY
COMMERCE_ASSERTION_KEY_ID
```

Do not invent a replacement credential.

### R3. Preserve authoritative DB authorization exactly

After parsing request context, preserve checks equivalent to:

```text
context environment == server environment
shopId == authoritative turn.shopId
checkoutRecoveryId == authoritative turn.checkoutRecoveryId
conversationId == authoritative turn.conversationId
inboundVersion == authoritative turn.inboundVersion
shop domain is valid *.myshopify.com
for execute purpose: grant exists and context grantId/releaseId match
 grant not expired
 manifest matches grant
 requested tool is still granted/enabled
```

A well-formed context header is never sufficient by itself. It is a lookup/authorization context only.

### R4. Remove asymmetric/JWT machinery completely

Delete/stop using:

```text
jose MCP JWT verification
createAssertionVerifier
importAssertionKey
MCP_ASSERTION_ISSUER
MCP_ASSERTION_AUDIENCE
MCP_ASSERTION_SUBJECT
RSA public-key parsing
generate-commerce-assertion-keys.sh
COMMERCE_ASSERTION_PUBLIC_KEYS
```

Rename local runtime types from `McpAssertion` to `McpRequestContext` where they no longer represent a signed assertion. Reuse the already-published bounded Shared context schema if practical; no Shared release is authorised by this task.

### R5. Remove JWT-expiry-derived deadline logic

The current tool deadline uses signed assertion `exp`. After this task, deadline is derived only from the existing local tool budget:

```ts
deadlineAt = now() + 10_000;
```

or the repository's existing equivalent constant. Do not introduce a caller-supplied deadline/expiry field.

### R6. Failure behavior is explicit

Malformed/missing context -> explicit `INVALID_INPUT`/`UNAUTHENTICATED`-equivalent bounded error appropriate to the MCP contract.

DB unavailable -> explicit `UNAVAILABLE`.

DB mismatch/stale turn/grant -> existing `STALE_TURN`/`FORBIDDEN`/`INCOMPATIBLE_VERSION` behavior.

Do not catch and convert these to success/empty results.

### R7. Local diagnostic migration

`tests/local-external-mcp-diagnostic.test.ts` must stop generating an RSA key pair and signing a JWT. It sends only:

```text
Content-Type: application/json
X-Moda-Commerce-Context: <encoded context>
```

The existing persisted lifecycle must continue to prove:

```text
connection -> credential -> Tool -> preview -> publish -> capability -> release -> grant -> tools/list -> tools/call
```

with zero JWT/key/token configuration.

## Work Items

- [x] Replace assertion verification with bounded context parsing.
- [x] Rename local assertion-only types to request-context terminology.
- [x] Remove RSA/JWT imports/config/scripts/env requirements.
- [x] Remove assertion-expiry deadline dependency.
- [x] Preserve DB authorization checks unchanged in substance.
- [x] Update health/readiness/MCP tests and local diagnostic.

## Interfaces / Contracts

Private runtime request:

```text
private service link
+ X-Moda-Commerce-Context
+ JSON-RPC body
```

There is deliberately no application-layer caller credential.

## Dependencies

- ARCH-020-COMMERCE-024

## Enables

- ARCH-021-BACKGROUND-001

## Acceptance Criteria

- [x] Commerce MCP has no runtime RSA/JWT verification.
- [x] Commerce MCP requires no token/API key/shared secret.
- [x] Missing/malformed/oversized context is rejected explicitly.
- [x] DB-backed turn/grant/shop/tool authorization remains intact.
- [x] Local end-to-end MCP diagnostic passes without keys or tokens.
- [x] No new public MCP route is introduced.

## Validation

- [x] MCP context parsing tests
- [x] MCP authorization tests
- [x] health/config tests (health origin assertion remains a documented baseline mismatch)
- [x] local external MCP diagnostic
- [x] targeted ESLint/typecheck (lint passed; repository typecheck is blocked by unrelated existing errors)
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.

## Implementation Notes

The private service link authenticates network placement. Commerce still authorizes every business operation from durable PostgreSQL state. Do not reintroduce a second caller-authentication protocol in application code.

## Completion Report

### Status

Ready for Review

### Files Changed

- `lib/server/config.ts`
- `src/commerce/integration/backend/authorization.ts`
- `tests/mcp-service.test.ts`
- `.env.example`
- `README.md`
- `docs/commerce-backend-integration.md`
- `docs/runtime-compatibility.md`

### Work Completed

- Removed raw `DATABASE_URL`/`REDIS_URL` endpoint and parsed-URL logging from configuration parsing; no replacement secret logging was added.
- Added production authorization-boundary translation for known `LifecycleError` codes to bounded `McpError` responses, preserving `FORBIDDEN`, `STALE_TURN`, `INCOMPATIBLE_VERSION`, `UNAVAILABLE`, and related known outcomes.
- Preserved fail-closed `UNAVAILABLE` behavior for unexpected resolver/storage failures.
- Added adapter-to-service coverage proving a shop/conversation ownership denial remains `FORBIDDEN` rather than becoming generic 503, while an unexpected storage error remains `UNAVAILABLE`.
- Removed the orphan RSA key example and stale signed-context/RSA readiness guidance from Commerce-owned documentation.
- Preserved the accepted context-only private MCP flow, DB-backed authorization, local ten-second deadline, and diagnostic lifecycle.

### Validation Results

- Launcher evidence: prepared execution was claimed for Attempt 2 with `execution_state=claimed`, dependency gate passed, parent head `30949d2671b2b3f85f0a740508191a44884efc87`, implementation head `fd281e0e92914378cb911d4539ab5f9c4b9ec629`, canonical worktrees supplied by launcher, and recursive submodules ready with database at `98fdf715e54fe6df92ac6951facd104e410068f2`.
- Final implementation commit `e9c7c85009552463f9447475072e9bbc6f2ff433` was pushed to `origin/task/ARCH-021-COMMERCE-030`; final parent report commit is recorded below and was pushed to the same mirrored branch in the parent workspace repository.
- `npm run test -- tests/mcp-service.test.ts tests/mcp-authorization.test.ts`: passed, 2 files / 19 tests.
- `npm run test -- tests/mcp-service.test.ts tests/mcp-authorization.test.ts tests/mcp-compatibility.test.ts tests/auth-entrypoints.test.ts`: MCP/authorization/compatibility files passed, 3 files / 26 tests; `tests/auth-entrypoints.test.ts` has one pre-existing assertion mismatch expecting route source text `createMcpService` although the current route delegates through `getCommerceBackend().mcp`.
- `npm run diagnose:arch020-external-mcp:local`: passed end to end; persisted connection -> credential -> tool -> preview -> publish -> capability -> release -> grant -> tools/list -> tools/call lifecycle passed, and cleanup reported zero owned Docker resources.
- `npm run lint`: passed with 0 errors and 6 pre-existing warnings; no new task-owned diagnostics.
- `npm run typecheck`: blocked by existing unrelated diagnostics in preview route imports, Studio components, agent-configuration effective configuration, and one agent-configuration test; no changed-file diagnostics were reported.
- `npm run build`: blocked by the same pre-existing missing preview modules in `app/api/studio/code-response/validate/route.ts`; code-runtime packaging/smoke and Prisma generation passed before Next compilation.
- `git diff --check`: passed.
- Commerce-owned stale-authentication scan for `COMMERCE_ASSERTION`, `MCP_ASSERTION`, RSA public-key, signed-context, assertion verifier/importer, and key-generation references: no matches.

### Deviations

- The implementation push helper rejected the local upstream-name mismatch; the exact command `git push origin HEAD:refs/heads/task/ARCH-021-COMMERCE-030` published successfully.
- The repository-wide typecheck/build and one entrypoint assertion remain blocked by pre-existing baseline issues documented above; the focused changed-slice tests and lint are clean.

### Assumptions

- The launcher-provided worktree, synchronization, dependency, and submodule evidence is authoritative for Attempt 2 and was not redundantly recreated.
- The private service link remains the caller trust boundary; no replacement credential or public MCP route was introduced.

### Unresolved Issues

- Architect/developer follow-up remains for the documented repository typecheck/build baseline and the stale `auth-entrypoints` source-text assertion.

### Architectural Concerns

- None introduced. The four Architect Review corrections are implemented in the files above and covered by focused adapter/service tests plus local end-to-end diagnostic evidence.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 satisfies the bounded correction contract from Attempt 1 and the original private-MCP simplification requirements.

- `lib/server/config.ts` no longer logs raw/parsed `DATABASE_URL` or `REDIS_URL` values, so task-owned configuration does not emit credential-bearing endpoints.
- The production authorization adapter maps known `LifecycleError` authorization-domain codes to bounded `McpError` results before they reach the MCP service while unexpected resolver/storage failures fail closed as `UNAVAILABLE`.
- Focused adapter-to-service regressions prove a `FORBIDDEN` ownership denial remains HTTP 403/`FORBIDDEN` and an unexpected storage failure remains HTTP 503/`UNAVAILABLE`.
- Commerce-owned environment/runtime/readiness documentation no longer instructs operators to configure RSA assertion keys or retain a signed-context check. Unrelated Auth.js Studio JWT/session behavior is untouched.
- The accepted private-link request remains context-only: no `Authorization` header, bearer token, API key, shared secret, RSA/JWT verification or caller-supplied expiry/deadline was reintroduced.
- Existing PostgreSQL shop/turn/grant/release/tool authorization and the local ten-second execution deadline remain in the request path.
- The Completion Report now records launcher-resolved worktree isolation/synchronization/submodule evidence, final implementation commit `e9c7c85009552463f9447475072e9bbc6f2ff433`, pushed-branch evidence, focused validation and the accepted non-blocking repository baselines.

The stale `tests/auth-entrypoints.test.ts` route-source assertion remains non-blocking: it asserts literal source text `createMcpService` although the route now delegates through `getCommerceBackend().mcp`; the production MCP route behavior is covered by the focused MCP suite and local persisted external-MCP diagnostic.

### Reviewed Files

- `lib/server/config.ts`
- `src/commerce/integration/backend/authorization.ts`
- `src/commerce/mcp/authentication.ts`
- `src/commerce/mcp/authorization.ts`
- `src/commerce/mcp/ports.ts`
- `src/commerce/mcp/service.ts`
- `tests/mcp-service.test.ts`
- `.env.example`
- `README.md`
- `docs/commerce-backend-integration.md`
- `docs/runtime-compatibility.md`
- task Completion Report and launcher/worktree evidence

### Validation Reviewed

- Focused MCP/authorization/compatibility suite: 26 tests passed.
- Local persisted external-MCP diagnostic: passed end to end with clean owned-resource cleanup.
- Lint: 0 errors; submitted warnings are pre-existing.
- `git diff --check`: passed.
- Repository-wide typecheck/build blockers remain documented unrelated baseline conditions and introduce no task-owned diagnostics.
- Commerce-owned stale RSA/assertion/signed-context scan: no remaining task-owned matches.

### Architecture Conformance

Accepted. The implementation conforms to the ARCH-021 private-link/context-only caller-trust decision while retaining durable PostgreSQL authorization and bounded failure semantics. It introduces no replacement application-layer credential and no public MCP exposure.

### Follow-up

`ARCH-021-BACKGROUND-001` is now Ready because its sole dependency, COMMERCE-030, is Complete.

`ARCH-021-GATEWAY-001` remains Pending until BACKGROUND-001 is Complete.
