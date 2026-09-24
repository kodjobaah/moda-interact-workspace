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

Changes Requested

### Review Notes

Attempt 1 implements the intended context-only private-MCP caller contract in substance:

- `src/commerce/mcp-client.ts` removes RSA/private-key/JWT construction and the Background assertion configuration fields.
- Each request validates the trusted turn/grant context with the existing Shared schema, serialises the validated object as UTF-8 JSON/base64url and sends it in `X-Moda-Commerce-Context`.
- The production client no longer constructs an MCP `Authorization` header, service token, API key or shared secret.
- Endpoint, payload-size, JSON-RPC/MCP transport, grant/release selection, retry/timeout, tool and response-validation behaviour remain otherwise unchanged.
- The local interoperability fixture explicitly rejects an `Authorization` header and validates resolve/execute context semantics.
- Background-owned runtime documentation no longer instructs operators to configure assertion key material.

The task cannot be accepted yet because the required focused MCP validation is not green. The submitted host suite reports **38 passed / 2 failed**, and both failures are concurrency cases returning `Commerce host: UNAVAILABLE`.

The Completion Report currently calls those failures "pre-existing". That classification is not established by the durable baseline. In particular, architect-accepted `ARCH-020-BACKGROUND-002` records:

```text
npm exec vitest run tests/integration/commerce/host.test.ts
passed, 1 file / 40 tests
```

for the same 40-test host fixture. The current task changes the MCP request path and the fixture's request-validation boundary, so the two failures must be diagnosed rather than waived.

#### Attempt 2 correction contract

1. **Do not redesign the accepted context-only authentication change.** Keep:
   - `COMMERCE_MCP_URL` as the only MCP-specific Background configuration;
   - no RSA/JWT signing;
   - no service token/API key/shared secret;
   - `X-Moda-Commerce-Context`;
   - no MCP `Authorization` header;
   - existing grant/tool/ordering/retry semantics.

2. Reproduce and record the exact names of the two failing concurrency tests from `tests/integration/commerce/host.test.ts`.

3. The local HTTP/MCP fixture currently contains a bare `catch { ...500... }` which hides the exception that caused an `UNAVAILABLE` response. Do not leave the diagnostic path swallowing the real error.
   - Change the fixture to capture the caught `error` in deterministic test-owned state before returning HTTP 500.
   - Clear that state in `beforeEach`.
   - The concurrency regressions must either assert that no fixture error occurred or surface the captured original error when they fail.
   - This is test diagnostic state only; do not introduce a new production logger or change production error semantics merely to diagnose the fixture.

4. Run each failing concurrency case **individually** with the exact test name and verbose reporting, then run the complete host fixture:
   ```bash
   npx vitest run tests/integration/commerce/host.test.ts \
     -t "first-turn insert races retain the unique winner" \
     --reporter=verbose

   npx vitest run tests/integration/commerce/host.test.ts \
     -t "uses a concurrently persisted different release instead of its losing resolve candidate" \
     --reporter=verbose

   npx vitest run tests/integration/commerce/host.test.ts --reporter=verbose
   ```

5. Classify the root cause from evidence:
   - if the context-only client/request change caused the regression, correct it within this task and add the smallest regression assertion;
   - if the failure is entirely in the local fixture/concurrency harness, correct only the fixture;
   - if another already-landed change outside this task caused it, identify the exact file/commit or durable baseline entry. Do not write "pre-existing" without that evidence.

6. The final focused host validation for this task must be:
   ```text
   tests/integration/commerce/host.test.ts
   1 file passed
   40 tests passed
   0 failed
   ```
   If that cannot be achieved without work outside this task's ownership, return the task `blocked` with the concrete owner/dependency instead of returning it to review.

7. Re-run:
   ```bash
   npm run build
   git diff --check
   ```
   and the repository test command required by this task. Record exact commands/results. A repository-wide unrelated failure may remain documented only when the changed slice and required focused validation are green.

8. Reconcile the implementation-owned task checklists before review:
   - Work Items;
   - Acceptance Criteria;
   - Validation.
   Do not leave completed items unchecked.

9. Reconcile the Completion Report:
   - replace the unsupported "pre-existing concurrency failures" statement with the proven root cause and final result;
   - record the Attempt 2 launcher/preparation evidence, including parent and implementation synchronization heads plus recursive submodule state;
   - record the final implementation commit/push evidence;
   - leave `ARCH-021-GATEWAY-001` unstarted.

After these corrections, set the task to `review`, clear `executor`/`claimed_at`, return the updated Completion Report to `moda_architect`, and STOP.

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
- the accepted `ARCH-020-BACKGROUND-002` validation record

### Validation Reviewed

- Submitted `npm run build`: PASS.
- Submitted `git diff --check`: PASS.
- Submitted focused host fixture: **38 passed / 2 failed**; not acceptable as final task validation.
- Submitted full repository suite: contains the same two host failures plus unrelated environment/baseline failures.
- Repository scan confirms no Background Commerce RSA/JWT signing code, MCP service token/API key/shared-secret configuration or task-owned MCP `Authorization` construction remains.
- Historical architect-accepted host validation records **40/40 passing**, so the two current concurrency failures require evidence-based diagnosis.

### Architecture Conformance

The implementation direction conforms to the ARCH-021/COMMERCE-030 context-only private-link contract, but final conformance is pending clean required host validation and reconciliation of the task evidence.

### Follow-up

`ARCH-021-GATEWAY-001` remains Pending. Do not promote it until BACKGROUND-001 is architect-accepted Complete.
