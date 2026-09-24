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
status: review
priority: 20
executor: null
claimed_at: null
attempt: 1
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

Ready for Review

### Files Changed

- `src/commerce/mcp-client.ts`
- `tests/integration/commerce/host.test.ts`
- `docs/commerce-host.md`

### Work Completed

- Removed RSA private-key parsing, JWT assertion construction, assertion credentials and the `Authorization` header from the Background Commerce MCP client.
- Reused `CommerceAssertionSchema` to validate the bounded resolve/execute context, encoded it as UTF-8 base64url and sent it through `X-Moda-Commerce-Context` with `Content-Type: application/json`.
- Preserved endpoint validation, JSON-RPC/MCP transport behavior, grant/release selection, retry and timeout behavior, response validation, tool behavior and explicit Commerce host failures.
- Updated the focused host interoperability fixture to validate context-only requests and reject an auth header; removed obsolete assertion credential documentation.

### Validation Results

- `npm run build`: passed, including Prisma generation and TypeScript compilation.
- `git diff --check`: passed.
- Focused `tests/integration/commerce/host.test.ts`: 38 passed, 2 existing concurrency cases failed with `Commerce host: UNAVAILABLE`; both fail in isolation and do not produce context/header or HTTP-response diagnostics.
- Full `npm test`: 10 failures, including the same two host concurrency failures and unrelated existing failures for the missing ARCH-020 evidence fixture checkout, absent `moda_interact_test` database, stale shared-runtime version expectation, and unrelated maturation/billing/observability tests. No failure identified in the context-only request cases.
- No Background `jose` dependency or MCP service-token/API-key/shared-secret use remains. Remaining `Authorization` matches are unrelated WhatsApp/Shopify provider credentials.
- Prepared launcher evidence: implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-BACKGROUND-001`, parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-BACKGROUND-001`; recursive submodule sync/update passed and the database submodule was at `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
- Implementation commit `49e8596` was pushed to `origin/task/ARCH-021-BACKGROUND-001`.

### Deviations

- The repository has no declared lint script; build and `git diff --check` were run as the available targeted static validation.

### Assumptions

- `CommerceAssertionSchema` is the authoritative published bounded context schema and its resolve/execute fields remain unchanged by COMMERCE-030.

### Unresolved Issues

- The two pre-existing Commerce host concurrency fixture failures remain for architect review; they are outside the context-authentication change and reproduce independently by test name.

### Architectural Concerns

- None.

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
