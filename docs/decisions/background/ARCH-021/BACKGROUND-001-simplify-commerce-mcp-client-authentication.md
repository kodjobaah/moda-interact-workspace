---
id: ARCH-021-BACKGROUND-001
architecture_id: ARCH-021
title: Remove Commerce MCP assertion signing from Background
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-030
enables:
  - ARCH-021-GATEWAY-001
created: 2026-09-24
updated: 2026-09-24
---

# Remove Commerce MCP assertion signing from Background

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Remove RS256/JWT signing and every MCP authentication credential from Background. Continue calling the private Commerce MCP URL with the same bounded conversation/grant context encoded in `X-Moda-Commerce-Context` and no `Authorization` header.

## Context

Commerce MCP caller trust is provided by the private service link. Background currently signs `CommerceAssertionSchema` data with an RSA private key solely to call that private endpoint. COMMERCE-030 removes verification and defines the new context-only request shape.

## Scope

Primary files:

```text
src/commerce/mcp-client.ts
src/commerce/index.ts                       # only if MCP config is assembled here
package.json                                # remove jose only if no other use remains
tests/*mcp*.test.ts
.env.example                                # if present
README/docs that name assertion keys
```

## Out of Scope

- Commerce server implementation.
- Gateway/private-link topology.
- Changing grants/manifests/tool authorization.
- Adding a token, shared secret, API key or replacement credential.

## Requirements

### R1. Exact environment contract

Background retains only the MCP endpoint configuration already required by deployment:

```text
COMMERCE_MCP_URL
```

Remove runtime use of:

```text
COMMERCE_ASSERTION_KEY_ID
COMMERCE_ASSERTION_PRIVATE_KEY
COMMERCE_MCP_SERVICE_TOKEN
```

Do not add replacement authentication env vars.

### R2. Exact request construction

For every MCP request, construct the existing bounded context object from trusted worker state:

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

Validate it with the existing Shared schema before encoding.

Encode UTF-8 JSON as base64url and send:

```http
Content-Type: application/json
X-Moda-Commerce-Context: <encoded context>
```

Do not send an `Authorization` header for MCP.

### R3. Remove signing machinery

Delete/stop using:

```text
SignJWT
signCommerceAssertion
RSA private-key import/parsing
kid
iss/aud/sub
jti/iat/exp
```

Remove `jose` only when repository search proves it has no other use.

### R4. Preserve request semantics

Do not change JSON-RPC method/body semantics, grant selection, retry policy, conversation ordering or Tool call behavior as part of this task.

### R5. Explicit failures

If context construction/validation fails, surface the existing bounded Commerce client failure; do not send an empty context and do not silently continue.

If the private endpoint is unavailable, preserve the real unavailable/network error path; do not label it an authentication error.

## Work Items

- [ ] Remove assertion key config/signing from `src/commerce/mcp-client.ts`.
- [ ] Add context-only header construction.
- [ ] Remove obsolete env/docs/tests.
- [ ] Preserve current MCP call semantics and error propagation.

## Interfaces / Contracts

Consumes COMMERCE-030 context-only private request contract.

## Dependencies

- ARCH-021-COMMERCE-030

## Enables

- ARCH-021-GATEWAY-001

## Acceptance Criteria

- [ ] Background has no MCP RSA/JWT signing path.
- [ ] Background has no MCP service token/API key/shared secret.
- [ ] MCP requests carry the bounded context header and no Authorization header.
- [ ] Existing grant/tool call semantics are unchanged.
- [ ] Network/context failures remain explicit.

## Validation

- [ ] focused MCP client tests
- [ ] repository test command covering CommerceAgent MCP calls
- [ ] targeted lint/typecheck/build as declared by repository
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.

## Implementation Notes

This task removes caller authentication because the private link is the agreed trust boundary. It does not remove Commerce's database authorization of the supplied business context.

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
