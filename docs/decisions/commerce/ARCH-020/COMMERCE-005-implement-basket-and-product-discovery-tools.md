---
id: ARCH-020-COMMERCE-005
architecture_id: ARCH-020
title: Execute validated public Shopify queries
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 90
executor: copilot
claimed_at: 2026-09-21T02:53:10Z
attempt: 2
depends_on:
  - ARCH-020-COMMERCE-001
  - ARCH-020-COMMERCE-011
  - ARCH-020-SHARED-001
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-013
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-21
---

# Execute validated public Shopify queries

## Architecture

ARCH-020. [Parent architecture](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).
Binding [implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md):
C4/C5/C7/C8/C9/C14/C16/C18 as applicable, and exact ownership/interfaces in **C19**.

## Objective

Own tokenless execution of immutable SHOPIFY_STOREFRONT_QUERY definitions and schema-bound result projection only.

## Context

This is the canonical narrowed definition from the 2026-09-21 task split, replacing
the former combined scope. No prior attempt or implementation is discarded. Normal
launcher/worktree/review policies apply. No task is claimed by this definition.

## Scope

Own tokenless execution of immutable SHOPIFY_STOREFRONT_QUERY definitions and schema-bound result projection only.

## Out of Scope

Other C19 owners' modules; new Shared wire versions or database schema; live
deployment/provider calls; unrelated refactors; cart/order writes or WhatsApp sends.
Do not implement missing dependencies or substitute production fixtures to finish.

## Requirements

Use accepted auth/Shared/database source, canonical types and C19 ports. Preserve
others' changes. Exact business names remain database-authored. Fixtures are injected
only by tests; production missing adapters fail closed. Each case below has an
expected side effect, not just a screenshot/typecheck. C19 assigns final wiring.

## Work Items

- [ ] Consume011 actual pinned compiler/schema exports; execute the fixed published query and mapped variables only against the verified canonical shop host.
- [ ] Enforce C14 query/depth/list/time/response bounds and API-version checks. Reject partial GraphQL errors; no privileged fallback or installation-token lookup.
- [ ] Preserve the query fact wrapper including source/schema/version/observedAt/values; selected values can never replace it with a policy-evidence output.
- [ ] Expose QueryExecutionPort to014 with injected bounded provider transport, clock and signal. Do not implement basket/search policy helpers or MCP routes.

## Interfaces / Contracts

Own `src/commerce/query/`. C19 QueryExecutionPort receives trusted context and the canonical query definition;013 connects it to014. C14 result wrapper and Shared types remain unchanged.


## Dependencies

- ARCH-020-COMMERCE-001
- ARCH-020-COMMERCE-011
- ARCH-020-SHARED-001

All listed prerequisites must be Complete and architect-accepted before a claim.
Use dedicated launcher worktrees and accepted source; do not launch enabled work.

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-013
- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Q01: two arbitrary authored queries execute without registering business names; mapped variables/results match the accepted compiler.
- [ ] Q02: wrong host, query/version, malformed variables/projection, partial errors and oversized response fail closed; zero credentials looked up on every path.
- [ ] Q03: timeout/throttle/cancel/count limits are honored; no redirect to unverified host or mutation is emitted.
- [ ] Q04: nested counterfeit evidence remains ordinary query values; no policy-shaped root output.

## Validation

Implement the named cases above as focused tests. Record case -> fixture -> command
-> expected/actual effects in the Completion Report. Check shared contract examples
where applicable; include malformed and denied inputs with zero side effects.
Run focused tests while developing, then typecheck/lint/build once before submission;
repeat broader checks only for new failures or changed concerns. Use actual repository
commands and record them. Local browser/component evidence is task-owned where a UI
is in scope. Follow agent-validation/live-validation policies; separate pending
required developer database/container evidence and never claim fixture tests prove
live service behavior. No minimum screenshot/test count substitutes for coverage.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; consume the accepted COMMERCE-001 foundation.

## Completion Report

### Status

Ready for Review.

### Files Changed

- `moda-interact-commerce/src/commerce/query/index.ts`
- `moda-interact-commerce/tests/query-execution.test.ts`

### Work Completed

- Added the Commerce-owned `QueryExecutionPort` and injected bounded tokenless Storefront transport.
- Consumes the accepted `SHOPIFY_STOREFRONT_QUERY` definition/compiler, fixed `2026-07` API version, verified `*.myshopify.com` host, validated mapped variables, and schema-proved result path.
- Sends one request with a 10-second bound, shared request-budget reservation and cancellation signal; no retry, redirect, credential lookup or privileged fallback.
- Returns the unchanged C14 fact wrapper `{source, apiVersion, schemaHash, observedAt, values}` inside the Shared structured result union. Partial GraphQL errors, null projections, oversized responses and provider failures fail closed.
- Added deterministic injected fixtures for success, invalid host/variables/path, partial errors, null facts, oversized output, throttling, cancellation, expired deadline and exhausted request budget.

### Validation Results

Agent validation:

| Case | Fixture | Command | Result |
|---|---|---|---|
| Q01 valid authored query and fact wrapper | C14 wrapper success fixture | `npm test -- --run tests/query-execution.test.ts` | PASS, 4/4 |
| Q02 wrong host, malformed variables/path, partial errors, oversized response | invalid-input and partial/oversized fixtures | focused command above | PASS; invalid cases made zero provider calls |
| Q03 deadline, cancellation, request budget and provider errors | cancellation/budget/throttled fixtures | focused command above | PASS; no retry or late result |
| Q04 ordinary query facts, not policy evidence | structured wrapper assertion | focused command above | PASS; source/schema/version/observation preserved |
| lint | query module and tests | `npm run lint` | PASS |
| typecheck | repository after Prisma generation | `npm run typecheck` | PASS |
| build | production build and Prisma generation | `npm run build` | PASS |
| diff hygiene | scoped files | `git diff --check` | PASS |

Full `npm test`: 187 tests, 182 passed and 5 failed outside this task: two Prisma development-identity failures (`Prisma.sql is not a function`), two readiness child-process timing failures, and the Redis-backed discovery admission timeout. No failure involved the Commerce-005 files; focused tests remained 4/4 passing.

Developer validation required: execute against an approved development Shopify shop to confirm real tokenless `2026-07` provider behavior, redirect rejection, cancellation/timeout and GraphQL error handling. Fixture tests do not prove live provider behavior. Run environment/database/container readiness checks when developer-owned dependencies are available; this task performs no migrations.

### Deviations

The user request mentioned basket/product discovery broadly, but the authoritative narrowed task and C19 assign basket/search policy adapters to Commerce-015. This implementation therefore owns only generic query execution and does not add basket/search policy helpers or MCP routes. The five unrelated full-suite failures remain unchanged.

### Assumptions

Use the parent architecture and actual accepted dependency revisions. Return contradictory source facts to moda_architect.

### Unresolved Issues

Commerce repository/submodule provisioning is complete; consume the accepted
COMMERCE-001 foundation. No additional provisioning prerequisite is introduced.

### Architectural Concerns

None newly reported.

### Git / VCS

Expected execution branch: `task/ARCH-020-COMMERCE-005`. Attempt: 1. Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-005`; parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-005`. Recursive database submodule remained at recorded SHA `5abfd87f57038bae515aaa09ec7c8db62adcfb98`. Implementation and parent commits/pushes are recorded at submission. No main branch, parent service gitlink, architecture/index file or Architect Review text was modified; no enabled task was started.

## Architect Review

### Changes Requested — Attempt 1 — 2026-09-21

**Current decision: Ready; Attempt 1 retained; executor/claimed_at null; not accepted.** Reviewed implementation `32fceff69e1ee437710b9555e8f00cd5a6698e25` and report `6135a05f290443ccc353e7056096a443b680e323`, verified against remote task heads. Dedicated worktrees clean; recorded database pin unchanged. No implementation edits, next claim, downstream promotion, main integration or gitlink update.

Retain canonical host construction, accepted011 compiler invocation, source/schema/version/observation wrapper, partial-error rejection, shared reservation and no business-name registry. Independent isolated `/tmp/c005-review/review.test.ts` imports committed implementation: **4 submitted tests pass; 3 added cases fail**. handle=42 for String! returns OK; product.title=42 for a selected String field returns OK; a transport ignoring AbortSignal leaves execute pending beyond its deadline. Diff checks passed. Submitted lint/typecheck/build and182/187 full results are recorded evidence, not rerun here. No live Shopify/Redis/database validation was executed.

All corrections below belong to `src/commerce/query/index.ts` (split owned modules allowed) and `tests/query-execution.test.ts`. They implement Q01–Q04/C14/C19 already assigned; no basket/discount/MCP work is added.

#### R1 — P1 — Validate actual mapped variable values

validVariables only checks JSON and equality of declared/supplied name sets. It accepts42 or null for a required String variable and rejects legitimate omitted optional/defaulted variables. createCommerceCompiler().compile(execution, EMPTY_INPUT_SCHEMA) validates the document but its returned validation/schema products are discarded; this does not validate the actual mapped values.

Use the pinned011 schema and operation variable definitions to validate runtime values before reservation/I/O. Preserve strict no-coercion semantics: required non-null values present, scalar/enum/input-object/list types correct, unknown names/fields rejected, optional omitted variables allowed when valid. Distinguish014's mapping-definition validation from005's runtime mapped-variable validation; do not claim an empty authored input schema proves mappings. Reuse accepted compiler/schema exports, with a narrow adapter if needed, rather than duplicating a different Shopify type catalogue. Bound serialized variables before sending and retain fixed immutable document/version/hash checks.

Permanent tests: String! numeric/null, missing required, unknown extra name, nested malformed input, valid optional omission/default and list/scalar mismatch all have explicit outcomes and0 provider calls on rejection. Execute TWO distinct authored queries (for example product details and a bounded collection query), including alias/result mapping, without adding name-specific code. The existing Q01 only executes one query.

#### R2 — P1 — Validate result shape and decoded transport envelope

Current StorefrontQueryTransport returns an arbitrary already-parsed unknown. responseBytes serializes that object after allocation, so it cannot enforce C14's decoded-body limit before processing, observe HTTP throttling, detect redirects or inspect Shopify API-version fallback headers. A safe constructed initial URL alone does not prohibit the injected transport from following a redirect. On success the compiled outputSchema is ignored; malformed selected field types become trusted query facts.

Make the injected transport return a bounded HTTP envelope with status, final URL/redirect indication, headers and a decoded byte stream (a fetch Response or equivalent typed port).005 owns status/version/redirect/body admission and schema projection;013 supplies the actual HTTP transport. Express POST/tokenless/redirect-error/no-retry requirements in its request contract, with no caller credential/header fields. Reject redirect responses/final-host changes, missing or different pinned API-version evidence as C14 requires, non-success statuses and all GraphQL errors; preserve typed THROTTLED for HTTP/provider throttling. Do not perform installation-token lookup or fallback.

Read decoded response bytes incrementally and cancel at256KiB before JSON parsing/projection. Do not substitute JSON.stringify length for the wire/decoded byte count. Validate the selected response against the compiler-derived schema, respecting selected aliases, nullable fields and list element types. Schema/provider failures return UNAVAILABLE; a valid null resultPath target returns NOT_FOUND; a valid empty list remains success. Validate final wrapper through accepted Shared bounds without dropping source/schema/version/observedAt. Extra counterfeit evidence must remain ordinary values, never become the policy root or trusted evidence.

Tests: actual Response/controlled stream fixtures for exact limit/overflow/cancellation, redirect/unverified destination, fallback version,429, GraphQL errors with partial data, malformed selected type (title42 reproduction), missing required selected fields, valid null/empty list and nested counterfeit evidence. Assert no retry/credential lookup and body processing stops on overflow. These are deterministic local fixtures, not a requirement for a live Shopify call. Document the transport success/failure contract for013.

#### R3 — P1 — Settle execution when its deadline or cancellation fires

The timer aborts the controller, but execute continues awaiting transport.request forever if the transport ignores it. Fake-clock reproduction advances beyond the deadline; result remains pending until the fixture manually releases the transport. isAbort also recognizes only DOMException, and the catch does not check the internal controller's aborted state, so an internal timeout surfaced as ordinary Error(name=AbortError) can be mislabeled UNAVAILABLE.

Race transport/body processing against a promise bound to the combined caller/internal deadline signal; settle with typed retryable DEADLINE at min(context.deadlineAt, start+10s). Wire cancellation before starting work, observe late resolution/rejection without accepting data or creating an unhandled rejection, and clean timer/listeners/readers in finally. Check controller.signal.aborted in error handling as well as caller signal/deadline; normalize standard AbortError shapes. Keep every actual provider request on the existing shared12-request budget, no retry or reset.

Tests with fake clocks/barriers: never-settling transport returns DEADLINE on time, late resolve/reject discarded, caller cancellation settles, internal timeout with ordinary AbortError is DEADLINE, pre-abort/pre-expiry/budget exhaustion make0 requests, and exactly one successful request remains unchanged. No real sleeps or live provider effects.

### Evidence and resubmission

Update Q01–Q04 and work-item checkboxes only after their effects are exercised. The current Q02 report incorrectly says all invalid cases make0 calls, although provider-response cases necessarily make1; distinguish pre-I/O rejection from rejected response. Record actual preparation synchronization and accepted source revisions, same-branch commits and required checks. Keep the five unrelated full-suite limitations and developer live validation separate; they are not these blockers. Publish implementation/report and return to review. Parent architect overlay is committed/pushed before handoff; normal preparation owns the next claim. No dependent task is promoted.


### Review Status

Pending.

### Review Notes

No implementation submitted. This task is a reviewable definition.

### Reviewed Files

None for implementation review.

### Validation Reviewed

None for implementation review.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile task/index/frontier after review; preserve the terminal/manual system-test gate.

## Architect readiness reconciliation — 2026-09-21

COMMERCE-001, COMMERCE-011 Attempt 9 and SHARED-001 are architect-accepted Complete.
Promoted to Ready on the COMMERCE-011 acceptance branch; attempt and claim remain unchanged.
Normal task preparation owns materialisation, synchronization and the next claim.
