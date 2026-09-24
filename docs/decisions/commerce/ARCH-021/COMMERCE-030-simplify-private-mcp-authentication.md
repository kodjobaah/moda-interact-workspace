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
attempt: 0
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

Remove RSA/JWT assertion authentication from the Commerce MCP endpoint and replace it with **no application-layer caller credential at all**. The existing private service link is the caller trust boundary. Preserve a bounded request-context header and every PostgreSQL-backed shop/turn/grant/release/tool authorization check.

## Context

The Commerce MCP endpoint is not a public API. Gateway/Render topology exposes it only over the private service path used by Background. ARCH-020 added RS256 signing, key distribution, `kid` rotation and JWT claim validation on top of that private link. That machinery is not required for the agreed development architecture and must not be replaced with a bearer token, API key, shared secret or another key exchange.

This task removes **caller authentication**, not business authorization. Commerce must continue to reject stale/mismatched conversation, shop, recovery, inbound-version, grant, release and tool context using PostgreSQL state.

## Scope

Primary files:

```text
src/commerce/mcp/authentication.ts
src/commerce/mcp/ports.ts
src/commerce/mcp/service.ts
src/commerce/integration/backend.ts
lib/server/config.ts
.env.example
docs/runtime-compatibility.md
generate-commerce-assertion-keys.sh          # delete
tests/*mcp*.test.ts
tests/health.test.ts
tests/local-external-mcp-diagnostic.test.ts
scripts/readiness-local-smoke.mjs
scripts/clean-clone.sh
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

- [ ] Replace assertion verification with bounded context parsing.
- [ ] Rename local assertion-only types to request-context terminology.
- [ ] Remove RSA/JWT imports/config/scripts/env requirements.
- [ ] Remove assertion-expiry deadline dependency.
- [ ] Preserve DB authorization checks unchanged in substance.
- [ ] Update health/readiness/MCP tests and local diagnostic.

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

- [ ] Commerce MCP has no runtime RSA/JWT verification.
- [ ] Commerce MCP requires no token/API key/shared secret.
- [ ] Missing/malformed/oversized context is rejected explicitly.
- [ ] DB-backed turn/grant/shop/tool authorization remains intact.
- [ ] Local end-to-end MCP diagnostic passes without keys or tokens.
- [ ] No new public MCP route is introduced.

## Validation

- [ ] MCP context parsing tests
- [ ] MCP authorization tests
- [ ] health/config tests
- [ ] local external MCP diagnostic
- [ ] targeted ESLint/typecheck
- [ ] `git diff --check`

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

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
