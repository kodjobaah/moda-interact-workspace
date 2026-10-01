---
id: ARCH-021-COMMERCE-108
architecture_id: ARCH-021
title: Superseded - selected-shop Preview Tool execution
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 102
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-09-29
updated: 2026-10-01
superseded_by: ARCH-024-COMMERCE-006
---

# Execute Feature Preview Tools against the selected shop

> **Superseded 2026-10-01. Do not execute.** ARCH-024-COMMERCE-006 replaces this unstarted Tool-execution task.
> The remaining content is retained as historical design context only.

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Make Feature-composed Test Conversations execute the exact frozen Tool revisions through the existing production `DefinitionExecutor` against the validated selected shop, instead of the synthetic fixture executor and `preview.myshopify.com` context.

## Context

The current multi-turn Preview constructs Tool calls with:

```text
shopDomain = preview.myshopify.com
checkoutRecoveryId = preview-<fixture>
backend.createFixtureExecution(...)
synthetic Shopify Admin result generation
```

That is suitable for deterministic automated fixture Preview, but it does not test the CommerceAgent against the selected merchant shop.

The production Commerce backend already exposes:

```text
CommerceBackend.execution
```

which is the accepted `DefinitionExecutionPort`/`DefinitionExecutor` with server-owned provider integrations. COMMERCE-105 freezes the exact Tool revision definitions selected by Features and COMMERCE-106 freezes the validated shop identity. This task connects those two facts without adding a second Tool execution implementation.

## Scope

Primary implementation areas:

```text
src/commerce/integration/preview/adapters.ts
src/commerce/preview/service.ts
existing execution port/types needed to construct an AuthorizedToolCall
focused Preview/DefinitionExecutor integration tests
```

Provider implementations themselves are out of scope; reuse the existing production execution port.

## Out of Scope

- Feature selection/composition resolution (C105).
- Effective model/prompt selection (C106).
- Human Feature picker UI (C107).
- Deleting fixture/test support (C109).
- New Shopify access-token handling.
- New External HTTP connection storage.
- New Policy Operation implementation.
- Fabricating CheckoutRecovery/customer/order state for Preview.
- Allowing arbitrary mutations solely to make Preview pass.

## Requirements

### R1 — Feature Preview uses `CommerceBackend.execution`

For the supported `FEATURES` multi-turn path, execute Tools through the existing production:

```text
CommerceBackend.execution
```

Do not call:

```text
backend.createFixtureExecution(...)
fixtureQuery(...)
```

for a Feature-composed conversation turn.

Legacy fixture/tool-test code may remain for deterministic automated/test-only paths until C109.

### R2 — exact frozen definition/revision is authoritative

For every runner Tool call, use only the descriptor and definition frozen at conversation creation by C105/C106.

Required invariants:

```text
requested descriptor.toolRevisionId exists in frozen snapshot
frozen definition Tool identity/revision matches manifest/grant
call name matches frozen definition
arguments are runner-produced and validated by DefinitionExecutor
```

If the frozen definition is missing/mismatched, return the canonical unavailable/not-found Tool result; do not re-read the latest Tool revision and do not silently upgrade.

### R3 — construct selected-shop AuthorizedToolCall

Construct the execution call from server/frozen state only:

```text
turn.shopId            = frozen selected shop.id
shopDomain             = frozen selected shop.domain
grant/release/tool IDs = frozen Preview bundle/manifest exact values
definition             = frozen Tool definition
environment            = Preview environment
purpose                = preview
deadline/signal         = existing Preview bounded deadline/cancellation
```

Do not accept shop domain, Tool revision or definition from the browser.

Preview-specific conversation/grant IDs may remain ephemeral.

### R4 — Shopify Admin runs against selected shop's offline session

For `SHOPIFY_ADMIN_GRAPHQL`, allow the existing production Admin query execution port to resolve the selected shop domain to its server-side offline Shopify session/access token.

Expected behaviour:

```text
selected shop + offline session available -> real Shopify Admin request
selected shop offline session unavailable -> canonical UNAVAILABLE/error Tool result
```

No access token is returned to the browser or frozen Preview state.

### R5 — External HTTP uses existing production connection boundary

For `EXTERNAL_HTTP`, use existing `DefinitionExecutor`/External integration connection resolution and server-held credentials.

Do not substitute the old external response fixture in normal Feature conversation execution.

Provider errors/deadlines remain canonical Tool results and must not crash the Preview service process.

### R6 — Policy Operations use existing registry; do not fabricate business state

For `POLICY_OPERATION`, use the existing production registry/DefinitionExecutor.

A Test Conversation does not automatically correspond to a durable `CheckoutRecovery`. Therefore:

```text
operation can execute from the bounded selected-shop/Preview context -> use real result
operation requires missing recovery/customer/order durable state -> canonical NOT_FOUND/UNAVAILABLE result is valid
```

Do not create fake database rows or mutate production business state just to make a Policy Operation Preview succeed.

Any Policy Operation that is inherently mutating and not approved for Preview must remain denied/unavailable under the existing safety boundary.

### R7 — preserve exact authorization to selected Feature Tool set

The runner may invoke only Tool revisions present in the frozen Feature-composed manifest/grant.

`isAuthorized` must continue to prove exact `toolId + toolRevisionId`; it must not authorize by Tool name alone or by current database state.

Unselected Feature Tools must not become callable because they exist in the repository or active production Release.

### R8 — preserve cancellation/deadline/budgets

Carry the existing Preview `AbortSignal`, deadline and remote-call budgets into `DefinitionExecutor`.

A cancelled Preview run must stop/abort outstanding provider execution where supported and settle according to current cancellation/unknown-outcome semantics.

Do not introduce unbounded retries.

### R9 — Preview remains isolated from outbound messaging

This task enables real Tool data access for selected-shop testing; it does **not** turn Preview into production conversation delivery.

Preview must not:

```text
send WhatsApp/customer messages
create a production conversation grant
schedule Background jobs
create checkout recovery state
record billable production usage solely because Preview ran
```

Keep the existing Preview purpose/safety instruction and service isolation.

### R10 — deterministic fixture support remains for automated tests until cleanup

Do not delete `createFixtureExecution`, fixture query helpers or `/api/studio/preview/tool-tests` merely because the supported human Conversation flow no longer uses them. Existing External Code Response/testing seams still depend on fixture Tool tests. C109 owns selective cleanup and explicitly preserves test/code-response dependencies.

## Work Items

- [ ] Add a real selected-shop execution path to the Preview Tool executor using `CommerceBackend.execution`.
- [ ] Build `AuthorizedToolCall` only from frozen server state + runner arguments.
- [ ] Remove synthetic `preview.myshopify.com` from the supported Feature path.
- [ ] Route Shopify Admin through the selected shop's real offline-session query port.
- [ ] Route External HTTP through the existing production connection/executor boundary.
- [ ] Route Policy Operations through the existing registry without fabricating durable business state.
- [ ] Preserve exact manifest/grant Tool authorization.
- [ ] Preserve cancellation/deadline/budget semantics.
- [ ] Add negative regression proving an unselected Feature Tool cannot be invoked.
- [ ] Add regressions proving a post-start newer Tool revision is not used.
- [ ] Preserve fixture Tool-test/code-response seams for automated/internal use.

## Interfaces / Contracts

Consumes:

```text
COMMERCE-105 frozen Feature Tool manifest/definitions
COMMERCE-106 frozen selected shop
CommerceBackend.execution
```

No new cross-service contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-105
- ARCH-021-COMMERCE-106

## Enables

- ARCH-021-COMMERCE-109

## Acceptance Criteria

- [ ] Feature conversation Tool execution calls `CommerceBackend.execution`, not fixture execution.
- [ ] Exact frozen Tool revision/definition is used; later publication cannot change a running conversation.
- [ ] Shopify Admin calls target the validated selected shop and use its server-side offline session.
- [ ] External HTTP calls use existing server-owned connection/credential handling.
- [ ] Policy Operations use the existing registry and return canonical missing-context errors rather than fabricated state.
- [ ] Unselected Feature Tools are not authorized/callable.
- [ ] Selected-shop domain/Tool definition/revision cannot be overridden by the browser.
- [ ] Cancellation/deadline/remote-call budgets remain enforced.
- [ ] Preview does not send customer messages, create production grants/jobs/recovery state, or weaken the Preview safety boundary.
- [ ] Deterministic fixture/code-response Tool-test support required outside the human Conversation UI remains working.

## Validation

- [ ] focused Preview -> DefinitionExecutor tests
- [ ] Shopify Admin selected-shop/offline-session integration regression
- [ ] External HTTP selected-shop/connection integration regression
- [ ] Policy Operation missing-durable-context regression
- [ ] exact frozen revision/no-latest-reread regression
- [ ] unselected Tool authorization negative regression
- [ ] cancel/deadline regression
- [ ] no-customer-delivery/no-production-grant assertions
- [ ] existing external code-response/fixture Tool-test regressions
- [ ] targeted ESLint
- [ ] repository typecheck or changed-file diagnostics per baseline policy
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin COMMERCE-109.

## Implementation Notes

Do not create a special "Preview executor" that reimplements provider semantics. The architecture goal is parity: same frozen Tool definition + same production DefinitionExecutor, with Preview-specific authorization/context and no customer-delivery side effects.

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
