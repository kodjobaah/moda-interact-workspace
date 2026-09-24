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
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 1
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

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

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

Changes Requested

### Review Notes

Attempt 1 implements the core private-link simplification correctly: runtime RSA/JWT verification and MCP caller credentials are removed; `X-Moda-Commerce-Context` is bounded/canonical; environment is server-derived; the tool deadline is local (`now + 10_000`); and the existing PostgreSQL authorization path remains in front of tool execution. The declared local external MCP diagnostic also exercises the persisted grant -> tools/list -> tools/call lifecycle without JWT/key configuration.

The task returns to Ready for one bounded correction pass:

1. **Remove secret-bearing configuration logging.** `lib/server/config.ts` currently logs the raw endpoint value and parsed `URL` while reading `DATABASE_URL` and `REDIS_URL`. Those values may contain usernames/passwords and must never be emitted to application logs. Remove the diagnostic `console.log` output from the configuration parser; do not replace it with partially redacted secret logging.
2. **Preserve typed MCP authorization failures at the production adapter boundary.** The production Prisma resolver can throw coded `LifecycleError` values such as `FORBIDDEN`/`UNAVAILABLE` before `resolveAuthorizedSnapshot()` runs. `createCommerceAuthorization()` currently lets those escape as generic errors, so `createMcpService()` converts them to HTTP 503/`UNAVAILABLE`. Map only known authorization-domain codes to the corresponding bounded `McpError` (`FORBIDDEN`, `STALE_TURN`, `INCOMPATIBLE_VERSION`, `UNAVAILABLE`, etc.) while leaving unexpected database/runtime failures fail-closed as `UNAVAILABLE`. Add focused end-to-end adapter/service coverage proving a shop/conversation ownership mismatch is not collapsed to generic 503 and that an unexpected storage failure still is.
3. **Reconcile operational documentation/config examples.** Remove the orphan RSA-public-key comment from `.env.example`; update changed runtime/deployment guidance so it no longer says consumers retain a "signed-context" check; and remove stale Commerce README/readiness wording that claims RSA public-key validation. Do not change Studio's unrelated Auth.js/JWT session documentation.
4. **Completion Report/workflow reconciliation.** Attempt 1 executor material was written into architect-owned Objective/Context/Scope while the formal Completion Report remained `Not Started`. This architect patch restores the canonical task definition. Attempt 2 must populate the standard Completion Report with actual changed files, validation, prepared worktree/synchronization evidence, final implementation commit and pushed-branch evidence, then return the task to `review`.

No redesign of the private-link trust decision, context schema, DB grant/tool authorization, provider budget, or local diagnostic lifecycle is requested.

### Reviewed Files

- `src/commerce/mcp/authentication.ts`
- `src/commerce/mcp/ports.ts`
- `src/commerce/mcp/authorization.ts`
- `src/commerce/mcp/service.ts`
- `src/commerce/integration/backend.ts`
- `src/commerce/integration/backend/authorization.ts`
- `lib/server/config.ts`
- `.env.example`
- `docs/runtime-compatibility.md`
- `docs/commerce-backend-integration.md`
- `README.md`
- `scripts/readiness-local-smoke.mjs`
- `scripts/clean-clone.sh`
- focused MCP/authorization/local-diagnostic tests

### Validation Reviewed

- Submitted focused MCP suite: 5 files / 26 tests passed.
- Submitted `npm run diagnose:arch020-external-mcp:local`: passed end to end with zero owned Docker resources remaining.
- Submitted lint: 0 errors (6 pre-existing warnings).
- Submitted `git diff --check`: passed.
- Repository-wide typecheck baseline remains non-blocking for unrelated files; Attempt 2 must keep task-owned diagnostics clean.

### Architecture Conformance

Conforms in substance to the private-link/context-only architecture, but cannot be accepted while task-owned configuration may log credentials and production authorization-domain failures can be collapsed to generic `UNAVAILABLE` contrary to R6.

### Follow-up

Return the same task through `/moda-task ARCH-021-COMMERCE-030`. Preserve `attempt: 1`; the next authorized claim becomes Attempt 2. `ARCH-021-BACKGROUND-001` remains Pending until COMMERCE-030 is Complete.
