---
id: ARCH-021-COMMERCE-071
architecture_id: ARCH-021
title: Add correlated structured logging for Commerce Studio Tool authoring
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 75
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-039
  - ARCH-021-COMMERCE-054
  - ARCH-021-COMMERCE-056
  - ARCH-021-COMMERCE-060
  - ARCH-021-COMMERCE-061
  - ARCH-021-COMMERCE-062
  - ARCH-021-COMMERCE-064
  - ARCH-021-COMMERCE-065
  - ARCH-021-COMMERCE-067
enables: []
created: 2026-09-27
updated: 2026-09-27
---

# Add correlated structured logging for Commerce Studio Tool authoring

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Add safe, correlated, server-side structured diagnostic logging for the Commerce Studio Tool-authoring workflow using the architecture-approved `@modainteract/moda-interact-shared/logging` API, so Request/Response validation, Shopify Admin GraphQL exploration/schema browsing and result-contract derivation, live testing, Agent/Admin contract validation, Tool mutations and reconciliation can be traced without logging authored payloads, credentials or provider/customer data.

## Context

ARCH-021 now has substantial Tool-authoring and execution behaviour across:

```text
External HTTP Request validation / preview
External HTTP Response validation
non-durable live provider Test
Agent call-side validation
Shopify Admin schema exploration / query validation / result-contract derivation
Shopify Admin Request/definition validation
atomic Tool creation
DRAFT Save / Publish
unknown-outcome reconciliation
```

The Commerce process already consumes the shared structured logger, and production Tool execution already emits architecture-approved semantic telemetry through `src/commerce/observability.ts`.

Studio authoring is less observable. Most current Studio logging is limited to unexpected exceptions such as:

```text
commerce.studio.action_failed
commerce.studio.tool_mutation_failed
commerce.tool_authoring.action_failed
commerce.studio.tool_operation_reconciliation_failed
```

Successful actions, bounded expected failures, elapsed time and live-Test stage outcomes are therefore difficult to correlate when debugging authoring behaviour. This task fills that semantic diagnostic gap. It must reuse the shared logger and must not duplicate generic framework HTTP telemetry already provided by Next.js/OpenTelemetry.

## Scope

Primary implementation surfaces:

```text
src/studio/tools/authoring-logging.ts                 # preferred bounded semantic adapter
src/studio/tools/external-validation-server-actions.ts
src/studio/tools/agent-contract-validation-server-actions.ts
src/studio/tools/admin-validation-server-actions.ts
app/api/studio/discovery/route.ts                       # Admin schema Explore request boundary where semantic logs belong
lib/discovery/service.ts                                # only where needed for schema-browse semantic outcome/duration
src/studio/tools/reconciliation-server-actions.ts
src/studio/server-actions.ts
src/commerce/tool-authoring/external-live-test.ts      # only for live-Test stage diagnostics/timing where needed
```

Directly affected focused tests may be added/updated under the existing Commerce/Studio test structure.

A differently named Commerce-owned semantic logging adapter is acceptable if it remains small, Tool-authoring-specific and implemented entirely on top of `@modainteract/moda-interact-shared/logging`.

## Out of Scope

- Creating another generic JSON logger, redaction layer, log serializer or sink.
- Replacing `@modainteract/moda-interact-shared/logging`.
- Browser `console.*` debugging or persistent client-side logs.
- Logging every keystroke or React state transition.
- Duplicating generic HTTP request count/duration/status telemetry already available from framework/OpenTelemetry instrumentation.
- Adding new metrics, traces, Grafana dashboards or alerts.
- Changing Tool-authoring business behaviour, validation semantics, persistence, tab gating or UI presentation.
- Logging full Tool definitions, GraphQL documents, selected Admin field names, GraphQL literal/variable values, JavaScript source, schema JSON, templates, request arguments, provider bodies or credentials.
- Re-instrumenting production `CommerceExecutor` lifecycle telemetry already emitted through `src/commerce/observability.ts`.
- Introducing database schema changes or durable diagnostic records.

## Requirements

### R1 — use the shared structured logger only

All new diagnostic events MUST use:

```ts
import {
  createLogger,
  type StructuredLogger,
} from "@modainteract/moda-interact-shared/logging";
```

or an existing Commerce semantic adapter that itself uses that export.

Do not add service-local replacements for:

```text
JSON serialization
levels
redaction
Error serialization
size bounds
sink failure isolation
```

The canonical service identity remains:

```text
service.namespace = moda-interact
service.name = moda-interact-commerce
deployment.environment.name = resolved deployment environment
```

### R2 — one bounded Tool-authoring semantic event model

Prefer a small Commerce-owned semantic adapter rather than scattering unrelated event shapes across Server Actions.

At minimum emit stable events equivalent to:

```text
commerce.studio.tool_authoring.started
commerce.studio.tool_authoring.outcome
```

with a bounded `action` field rather than inventing a different event name for every button.

The supported action vocabulary must cover the server-side authoring boundaries that currently exist, including as applicable:

```text
external.request.preview
external.request.validate
external.response.validate
external.definition.validate
external.observe
external.live_test
agent_call.validate
admin.schema.browse
admin.request.validate
admin.definition.validate
admin.result_contract.derive
admin.metadata.read
tool.create_initial_draft
tool.update_draft
tool.publish
tool.reconcile
```

If the current integrated source contains an authenticated Result Template validation Server Action when this task executes, include it in the same vocabulary; do not create a new Server Action solely for logging.

### R3 — log start and outcome so hangs are diagnosable

For bounded Server Actions that can perform validation, compilation, database work or provider I/O, emit a start event before substantive work and exactly one outcome event when the action settles.

The outcome record must include, where applicable:

```text
action
outcome
durationMs
diagnosticId
operationId          # mutations only, bounded
requestId            # only when a bounded trusted request/correlation header is already available
executionKind        # EXTERNAL_HTTP / SHOPIFY_ADMIN_GRAPHQL when safely known
issueCount           # validation only
errorCode            # bounded normalized application error code
retryable            # when part of the action result
```

Do not log a false success if the caller receives a validation error, conflict, denial or unavailable result.

Logging failure must never change the returned Tool-authoring result.

### R4 — live Test logging must expose stages without payloads

The non-durable External HTTP live Test is a key debugging boundary.

Emit safe stage outcome information for:

```text
requestConstruction
connectionResolution
providerRequest
responseProcessing
resultValidation
```

The final live-Test diagnostic may include:

```text
stage status: passed / failed / not-run
normalized failure code
provider HTTP status or status class
provider content type when bounded and safe
total durationMs
```

It MUST NOT include:

```text
request URL/query values
header values
authorization material
provider bodyText/provider json
processed result values
Tool arguments
JavaScript source
```

A provider timeout/hang must be distinguishable from request-construction or response-processing failure through the stage diagnostics.

### R5 — Tool mutation and reconciliation outcomes must be visible

The existing Tool mutation wrapper currently emphasizes unexpected failures. Add semantic outcome logging around the real mutation boundary so these cases can be distinguished without reading UI state:

```text
SUCCEEDED
INVALID_INPUT
FORBIDDEN
NOT_FOUND
CONFLICT
CAS_CONFLICT
LIVE_TEST_REQUIRED
DATABASE_UNAVAILABLE
UNKNOWN
INTERNAL_ERROR
```

Preserve the existing `operationId` reconciliation semantics.

For unknown-outcome reconciliation, log whether the operation was:

```text
committed
not-committed
unavailable/error
```

Do not log free-form publication reasons or complete mutation payloads.

### R6 — validation outcomes must be visible without authored content

For Request, Response, Agent and Admin validation/derivation actions, log semantic outcome and safe counts/metadata only.

Examples of safe fields include:

```text
valid
issueCount
schemaHash prefix/hash when already non-secret and bounded
processingKind
requestMode
```

Do not log issue messages when they may reproduce authored content. Prefer bounded issue codes/paths only if the existing validation model proves them safe; otherwise log counts only.


For Shopify Admin Explore/schema derivation specifically, safe metadata may include:

```text
apiVersion
schemaHash or bounded schema-hash prefix
browse kind / object kind where it is an enum
returned field/type count where bounded
issueCount
derived result kind
derived top-level property count / collection flag where already computed
```

Do not log selected GraphQL field names, operation/document text, argument names/values, literal buffers or the derived schema JSON.

### R6a — Admin Explore and result-schema construction are first-class diagnostic boundaries

The Shopify Admin Explore workflow must be traceable through its existing server boundaries without adding a logging-only Server Action or moving browser-local query-builder state to the server.

At minimum, emit start/outcome/duration diagnostics for:

```text
Admin schema browse / metadata read
Admin query/request validation
Admin result-contract/schema derivation
```

The intended debugging sequence is reconstructable as:

```text
Explore schema browse
    -> validate generated/manual Admin query
    -> derive the canonical Admin result contract/schema
```

Where `createDiscoveryService(...).adminSchema(...)` already emits `CommerceTelemetry.discovery(...)`, do not mechanically duplicate that metric as a log. Structured logging is justified only for correlation/timing and bounded schema/compiler metadata needed to diagnose authoring failures. Prefer one semantic structured-log emission boundary (route or service), not duplicate route+service records for the same browse operation.

Client-only `buildAdminQuery(...)` editing/build failures that never cross an existing server boundary remain UI diagnostics; do not create a new network call solely to log them. Once the candidate reaches the existing Admin validation/derivation actions, those actions must provide the server-side diagnostic trail.

### R7 — correlation identifiers are diagnostic, not durable business state

Generate a bounded per-action `diagnosticId` on the server for authoring actions that do not already have an `operationId`.

Where an existing bounded `operationId`, trusted request ID or trace context is available, include it rather than creating a competing durable identifier.

Do not add a database column/table or durable Tool-definition field for logging correlation.

A client-wide authoring-session correlation protocol is not required by this task and must not be introduced merely for logging.

### R8 — sensitive-data exclusion is explicit

Tests must prove that new events do not intentionally contain:

```text
Shopify or provider credentials
Authorization/API-key header values
cookies/tokens
request query/header values
Tool invocation argument values
provider response bodies or JSON
processed result values
GraphQL document text
selected Shopify Admin field names
GraphQL argument/literal/variable values
Admin schema/result-schema JSON
JavaScript source
input/result schema JSON
Agent/Result Template text
connection secret material
```

Identifiers that materially help diagnostics should use existing bounded/hash conventions where appropriate rather than exposing unnecessary raw tenant/resource identifiers.

### R9 — do not duplicate existing production execution telemetry

`src/commerce/execution/executor.ts` already emits semantic `commerce.definition.outcome` telemetry for production definition resolution/execution/render.

Do not add another parallel production-execution event stream representing the same lifecycle merely because Studio logging is being improved.

This task instruments Studio authoring, Shopify Admin Explore/schema derivation, validation, non-durable live testing, mutations and reconciliation where an equivalent semantic signal is currently absent. Existing `CommerceTelemetry.discovery(...)` signals remain authoritative for their metric/telemetry purpose; structured logs must complement rather than mirror them.

## Work Items

- [x] Add a bounded Tool-authoring semantic logging adapter using the shared logger.
- [x] Add started/outcome diagnostics to External HTTP Request/Response/definition authoring Server Actions.
- [x] Add safe stage/outcome diagnostics to non-durable External HTTP live Test.
- [x] Add Agent call-side validation diagnostics.
- [x] Add Shopify Admin schema-browse/Explore diagnostics with safe metadata and no GraphQL/schema payloads.
- [x] Add Shopify Admin Request/definition validation and result-contract/schema-derivation diagnostics.
- [x] Add Tool create/save/publish mutation outcome diagnostics without logging payloads/reasons.
- [x] Add unknown-operation reconciliation diagnostics.
- [x] Consolidate unexpected-error diagnostics into bounded semantic outcomes without logging raw exceptions.
- [x] Add sensitive-data exclusion and logger-failure-isolation regressions.
- [x] Add focused success/expected-failure/unexpected-failure logging tests.

## Interfaces / Contracts

Consumes the architecture-approved shared logging contract:

```text
@modainteract/moda-interact-shared/logging
createLogger
StructuredLogger
```

Consumes existing ARCH-021 authoring/runtime boundaries from:

```text
ARCH-021-COMMERCE-039   local-only initial Tool authoring
ARCH-021-COMMERCE-054   non-durable External HTTP live Test
ARCH-021-COMMERCE-056   Agent-contract validation
ARCH-021-COMMERCE-060   Shopify Admin Tool execution/domain
ARCH-021-COMMERCE-061   Admin schema exploration/query-building domain
ARCH-021-COMMERCE-062   canonical Admin result-contract derivation
ARCH-021-COMMERCE-064   Explore Shopify Admin authoring/session handoff
ARCH-021-COMMERCE-065   split Admin Request/Response authoring
ARCH-021-COMMERCE-067   separated Agent/Result Template validation ownership
```

No cross-repository runtime contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-039
- ARCH-021-COMMERCE-054
- ARCH-021-COMMERCE-056
- ARCH-021-COMMERCE-060
- ARCH-021-COMMERCE-061
- ARCH-021-COMMERCE-062
- ARCH-021-COMMERCE-064
- ARCH-021-COMMERCE-065
- ARCH-021-COMMERCE-067

## Enables

None.

## Acceptance Criteria

- [x] All new generic logging uses `@modainteract/moda-interact-shared/logging`; no competing generic logger is created.
- [x] Tool-authoring Server Actions emit bounded semantic started/outcome diagnostics for the scoped actions.
- [x] Successful actions, expected bounded failures and unexpected failures are distinguishable in logs.
- [x] Duration is available for scoped server-side actions so slow/hanging boundaries can be identified.
- [x] External HTTP live Test diagnostics identify request construction, connection resolution, provider request, response processing and result validation outcomes.
- [x] Live-Test logs contain no request/provider/processed payload values or credentials.
- [x] Tool create/save/publish outcomes are traceable by bounded operation identity without logging mutation payloads or publication reasons.
- [x] Unknown-operation reconciliation outcome is traceable.
- [x] Request/Response/Agent/Admin validation outcomes expose safe issue counts/status without authored content.
- [x] Shopify Admin Explore schema browsing emits traceable start/outcome/duration diagnostics with safe bounded schema metadata only.
- [x] Shopify Admin result-contract/schema derivation emits traceable outcome diagnostics without GraphQL documents, selected field names or schema JSON.
- [x] Existing `CommerceTelemetry.discovery(...)` is not mechanically duplicated; structured logs add only correlation/timing/debug metadata absent from the existing telemetry.
- [x] Logging/sink failure cannot change validation, live-Test, mutation or reconciliation results.
- [x] No duplicate production `CommerceExecutor` lifecycle telemetry is introduced.
- [x] No database migration, durable diagnostic record, UI behaviour change, metric, trace, dashboard or alert is introduced.

## Validation

- [x] focused Tool-authoring logging adapter tests
- [x] focused External HTTP authoring Server Action logging tests
- [x] focused live-Test stage logging tests
- [x] focused Tool mutation/reconciliation logging tests
- [x] focused Agent/Admin validation logging tests
- [x] focused Admin Explore schema-browse and result-contract/schema-derivation logging tests
- [x] explicit sensitive-data canary test proving prohibited payload/source/credential values are absent from emitted records
- [x] logger/sink failure-isolation regression
- [x] targeted ESLint for changed files
- [x] changed-file TypeScript diagnostics or repository typecheck with baseline reconciliation
- [x] `git diff --check`

## Stop Condition

After the scoped Studio Tool-authoring and live-Test diagnostic events are implemented with shared logging, sensitive-data protections and focused validation, set the task to `review`, complete the Completion Report and STOP.

Do not add dashboards, metrics/traces, tab behaviour changes, broader production execution instrumentation or unrelated observability cleanup.

## Implementation Notes

Read and obey:

```text
docs/observability/shared-logging.md
```

The shared logger already owns serialization, levels, redaction, Error handling, size bounds and sink isolation. The Commerce adapter should add only Tool-authoring semantic meaning and safe correlation metadata.

Prefer one consistent event shape that can be queried by `action`, `outcome`, `operationId`/`diagnosticId` and duration rather than many one-off event names.

Do not introduce permanent application metrics merely to mirror these logs. Framework/OpenTelemetry HTTP telemetry remains the source for generic request count/status/duration; this task adds domain semantics that generic HTTP instrumentation does not know.

## Completion Report

### Status
Ready for Architect Review

### Files Changed
- `src/studio/tools/authoring-logging.ts` and the External HTTP, Agent, Admin, mutation, reconciliation, and discovery service boundaries.
- Focused logging, privacy, discovery, mutation, reconciliation, live-Test, and authoring action tests.

### Work Completed
- Added correlated `started`/`outcome` events with bounded action names, outcomes, durations, diagnostic IDs, operation IDs, allowlisted error codes, and safe validation/schema summaries.
- Added safe live-Test stage summaries and a single Admin schema-browse logging boundary while preserving existing discovery telemetry.
- Consolidated legacy raw-error mutation/reconciliation records into the semantic outcome stream; exception messages and payload-bearing error objects are not logged.
- Implementation commits `b8adc5f` and `d3f6a0d` are pushed to `origin/task/ARCH-021-COMMERCE-071`.
- Physical worktree isolation: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-071` on `task/ARCH-021-COMMERCE-071`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-071` on the same task branch. The shared workspace and shared implementation checkout were not switched or mutated for task work; no other task worktree was reused.
- Start synchronization: parent task fast-forward `not-needed`, parent `origin/main` incorporation `already-current`; implementation task fast-forward `not-needed`, implementation `origin/main` incorporation `already-current`.
- Recursive implementation submodules: `git submodule sync --recursive` passed; `git submodule update --init --recursive` passed; database submodule commit `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.

### Validation Results
- Focused C071 Vitest set: 11 files passed, 100 tests passed. Covered adapter, external actions, live-Test stages, Agent/Admin validation, Admin discovery, mutation, and reconciliation.
- Mutation/reconciliation failure-isolation slice: 2 files passed, 20 tests passed, including sensitive exception-message canaries and throwing logger methods.
- Targeted ESLint across all changed source/test files passed.
- Editor TypeScript diagnostics: no errors in the 12 changed TypeScript files.
- `npm run typecheck` reports 264 existing diagnostics across 30 files; none are in C071-changed files. Repository-wide typecheck therefore remains blocked by unrelated baseline errors.
- `git diff --check` passed; implementation worktree is clean and up to date with its task-branch remote.

### Deviations
The previous mutation and reconciliation error events serialized raw `Error` objects. They were consolidated into the semantic outcome events to avoid leaking arbitrary exception messages; safe outcome codes, durations, correlation IDs, and result semantics remain available.

### Assumptions
No new authenticated Result Template validation Server Action existed at implementation time; Agent/Result Template validation already uses the scoped Agent validation boundary.

### Unresolved Issues
The repository-wide typecheck has 264 pre-existing diagnostics across 30 files. Changed-file diagnostics and targeted lint/tests pass.
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
