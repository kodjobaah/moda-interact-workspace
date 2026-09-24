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
status: complete
priority: 20
executor: null
claimed_at: null
attempt: 2
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

- [x] Remove assertion key config/signing from `src/commerce/mcp-client.ts`.
- [x] Add context-only header construction.
- [x] Remove obsolete env/docs/tests.
- [x] Preserve current MCP call semantics and error propagation.

## Interfaces / Contracts

Consumes COMMERCE-030 context-only private request contract.

## Dependencies

- ARCH-021-COMMERCE-030

## Enables

- ARCH-021-GATEWAY-001

## Acceptance Criteria

- [x] Background has no MCP RSA/JWT signing path.
- [x] Background has no MCP service token/API key/shared secret.
- [x] MCP requests carry the bounded context header and no Authorization header.
- [x] Existing grant/tool call semantics are unchanged.
- [x] Network/context failures remain explicit.

## Validation

- [x] focused MCP client tests
- [x] repository test command covering CommerceAgent MCP calls (repository suite run; unrelated baseline failures recorded)
- [x] targeted lint/typecheck/build as declared by repository
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.

## Implementation Notes

This task removes caller authentication because the private link is the agreed trust boundary. It does not remove Commerce's database authorization of the supplied business context.

## Completion Report

### Status

Ready for Review

### Files Changed

- `src/commerce/mcp-client.ts`
- `tests/integration/commerce/host.test.ts` (Attempt 1 implementation plus Attempt 2 fixture diagnostics)
- `docs/commerce-host.md`

### Work Completed

- Removed RSA private-key parsing, JWT assertion construction, assertion credentials and the `Authorization` header from the Background Commerce MCP client.
- Reused `CommerceAssertionSchema` to validate the bounded resolve/execute context, encoded it as UTF-8 base64url and sent it through `X-Moda-Commerce-Context` with `Content-Type: application/json`.
- Preserved endpoint validation, JSON-RPC/MCP transport behavior, grant/release selection, retry and timeout behavior, response validation, tool behavior and explicit Commerce host failures.
- Updated the focused host interoperability fixture to validate context-only requests and reject an auth header; removed obsolete assertion credential documentation.

### Validation Results

- `npm run build`: passed, including Prisma generation and TypeScript compilation.
- `git diff --check`: passed.
- Exact reviewed concurrency cases reproduced individually with `--reporter=verbose`: `first-turn insert races retain the unique winner` passed; `uses a concurrently persisted different release instead of its losing resolve candidate` passed.
- Added deterministic fixture error capture, cleared in `beforeEach`, and surfaced the original caught error from both concurrency cases. The captured fixture error remained null in both individual runs and the complete focused run.
- Final focused `npx vitest run tests/integration/commerce/host.test.ts --reporter=verbose`: 1 file passed, 40 tests passed, 0 failed.
- Full `npm test`: 10 failures remain outside this task: missing ARCH-020 evidence fixture checkout, absent `moda_interact_test` database (4 translation integration failures), stale shared-runtime version expectation, and 4 unrelated maturation/billing failures. The focused host fixture and changed slice are green.
- No Background `jose` dependency or MCP service-token/API-key/shared-secret use remains. Remaining `Authorization` matches are unrelated WhatsApp/Shopify provider credentials.
- Attempt 2 launcher evidence: parent synchronization head `143da32a30c451bc625ccacaeac85d9f1a234a5a`; implementation head `49e8596b2acc0d778430e9d4a26af495a845f8ce`; parent claim commit `9597650a71109383cbad73462fc3b7d08f6f662e`; parent `origin/main` incorporated and implementation `origin/main` already current; recursive submodule sync/update passed with database at `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
- Implementation commits `49e8596` and `a8dfda0` were pushed to `origin/task/ARCH-021-BACKGROUND-001`; final correction commit is `a8dfda0`.

### Deviations

- The repository has no declared lint script; `npm run build` and `git diff --check` were run as the available targeted static validation.

### Assumptions

- `CommerceAssertionSchema` is the authoritative published bounded context schema and its resolve/execute fields remain unchanged by COMMERCE-030.

### Unresolved Issues

- The two concurrency failures reported in Attempt 1 were not reproducible in Attempt 2. After fixture exception capture was added, both exact tests passed individually and the full 40-test fixture passed with no captured fixture error. No production client change was needed, and no unsupported baseline waiver is being claimed.

### Architectural Concerns

- None.

### Attempt 2 Correction Mapping

1. **Diagnose the two concurrency failures:** Reproduced both exact test names individually with verbose reporting; both passed. The complete host fixture passed 40/40.
2. **Expose swallowed fixture errors:** `tests/integration/commerce/host.test.ts` now stores the caught error, clears it per test, and rethrows it from each reviewed concurrency case when present. No fixture error was captured in the required runs.
3. **Preserve the accepted context-only design:** No production MCP client redesign or credential reintroduction; `COMMERCE_MCP_URL`, bounded context header, no MCP `Authorization`, and existing grant/tool semantics remain unchanged.
4. **Reconcile evidence and status:** Attempt 2 preparation heads, submodule state, final implementation push, exact validation commands/results, and repository residual failures are recorded above. `ARCH-021-GATEWAY-001` remains unstarted.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 is accepted. The production Background MCP caller now conforms to the ARCH-021 / COMMERCE-030 context-only private-service contract without reintroducing an application-layer caller credential.

- `src/commerce/mcp-client.ts` has no RSA/private-key/JWT signing path and no MCP service-token/API-key/shared-secret configuration.
- `COMMERCE_MCP_URL` remains the only MCP-specific Background configuration.
- Resolve/execute context is validated with the existing published Shared schema, encoded as UTF-8 JSON/base64url and sent in `X-Moda-Commerce-Context`.
- The task-owned Commerce MCP client does not construct an `Authorization` header.
- Endpoint validation, request/response size bounds, ten-second request deadline, JSON-RPC/MCP transport, grant/release selection and Tool behavior remain unchanged in substance.
- Remaining `jose` package-lock presence is transitive through `@modelcontextprotocol/sdk`; Background has no direct `jose` dependency or task-owned signing usage.

The Attempt 1 concurrency validation concern is also resolved. Attempt 2 added deterministic fixture error capture without changing production failure semantics, reran both reviewed concurrency cases individually, and restored the complete host fixture to 40/40. No fixture exception was captured and no production MCP-client correction was required.

Implementation reviewed: `a8dfda0` (following initial implementation `49e8596`). Submitted parent report: `ea5a3a7b`.

### Reviewed Files

- `moda-interact-background/src/commerce/mcp-client.ts`
- `moda-interact-background/src/commerce/host.ts`
- `moda-interact-background/src/commerce/grants.ts`
- `moda-interact-background/tests/integration/commerce/host.test.ts`
- `moda-interact-background/docs/commerce-host.md`
- `moda-interact-background/package.json`
- `moda-interact-background/package-lock.json`
- `docs/decisions/commerce/ARCH-021/COMMERCE-030-simplify-private-mcp-authentication.md`
- this task's Completion Report
- the accepted `ARCH-020-BACKGROUND-002` host-validation record

### Validation Reviewed

- Submitted focused host fixture: **1 file / 40 tests passed / 0 failed**.
- Both previously failing concurrency cases passed individually with verbose reporting.
- Fixture diagnostic state remained clear in the reviewed individual and complete focused runs.
- Submitted `npm run build`: PASS, including Prisma generation and TypeScript compilation.
- Submitted `git diff --check`: PASS.
- Repository scan confirms no task-owned MCP RSA/JWT signing, assertion-key configuration, service token/API key/shared secret, or MCP `Authorization` construction remains.
- The submitted full repository suite retains documented failures outside this task; the changed Commerce host slice is green.
- The supplied review archive does not contain `node_modules`, so the architect inspected the implementation/test source and submitted results rather than rerunning Node validation locally.

### Architecture Conformance

Conforms. Background now treats the private service link as the MCP caller trust boundary while continuing to send only bounded request context for Commerce's authoritative PostgreSQL shop/turn/grant/release/tool authorization. No replacement application-layer credential was introduced.

### Follow-up

`ARCH-021-GATEWAY-001` is now **Ready** because both `ARCH-021-COMMERCE-030` and `ARCH-021-BACKGROUND-001` are Complete. Gateway must preserve private-only `/api/mcp` routing while removing obsolete assertion-key wiring and must not introduce a replacement secret.
