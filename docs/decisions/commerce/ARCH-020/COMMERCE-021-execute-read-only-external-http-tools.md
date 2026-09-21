---
id: ARCH-020-COMMERCE-021
architecture_id: ARCH-020
title: Execute read-only external HTTP tools
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 150
executor: copilot
claimed_at: 2026-09-21T21:49:12Z
attempt: 1
depends_on:
  - ARCH-020-SHARED-002
  - ARCH-020-COMMERCE-014
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-024
  - ARCH-020-GATEWAY-003
  - ARCH-020-COMMERCE-030
created: 2026-09-21
updated: 2026-09-21
---

# Execute read-only external HTTP tools

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Own src/commerce/external-http/** plus explicit014 dispatcher/renderer extension points. Implement C21 transport with injected028 resolver and025/026 processing ports. No connection persistence, UI or production factory wiring.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Own src/commerce/external-http/** plus explicit014 dispatcher/renderer extension points. Implement C21 transport with injected028 resolver and025/026 processing ports. No connection persistence, UI or production factory wiring.

## Out of Scope

Writes, OAuth, unsandboxed code, customer-specific lookups, live credentials or
WhatsApp sends, pricing/merchant feature overrides, automatic API discovery,
external-result caching and other owners' implementation files. No live deployment.

## Requirements

Use C21 named interfaces and bounded examples. All dependencies must be accepted
Complete before claim. Readiness is not execution. Component tasks may prove their
ports with fixtures; only024 and SYSTEM-TEST-002 claim real assembled flow.
Protect every UI command against double clicks, preserve same-operation retries,
and never expose secrets or raw external response data in errors/logs.

## Work Items

- [x] Implement createExternalHttpExecutionPort and explicit EXTERNAL_HTTP branch, runtime wrapper/schema validation, rendering and result/error mapping. Existing query/policy dispatch remains exhaustive.
- [x] Implement fixed-origin DNS/socket pinning, TLS hostname verification, target classification, no redirects/proxies/cookies, encoded bounded query and abort/deadline/decompression limits.
- [x] Decode declared JSON/TEXT without assuming structured content; apply injected visual/code dispatcher before final schema validation/rendering; on failure return bounded error, never raw upstream data. Exclude provider responses from logs.
- [x] Consume shared per-call budgets with no hidden retries; current connection authorization every call. Document transport fixture evidence and exact public factory in docs/external-http-executor.md.

## Interfaces / Contracts

C21 is the shared contract between these tasks. Own only the paths identified
above. Record exact accepted dependency SHA/package version and source exports
in the Completion Report. No catch-all shared integration barrel. Return genuine
contract contradictions with a source reproduction; do not weaken validation.

## Dependencies

- ARCH-020-SHARED-002
- ARCH-020-COMMERCE-014

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-024
- ARCH-020-GATEWAY-003
- ARCH-020-COMMERCE-030

## Acceptance Criteria

- [ ] HT01: first prove supported GET through actual DNS-aware transport into controlled HTTPS server, with auth from injected resolver, exact encoded query and filtered valid response reaching renderer. Missing-config-only evidence is insufficient.
- [ ] HT02: recorded socket address matches approved resolution; private/mapped-IP/rebinding/redirect attempts fail before credential-bearing dispatch; no second unvalidated DNS lookup.
- [ ] HT03: UTF-8 JSON and TEXT decoding, one-request budget, streamed/decompressed byte bound, deadline/abort, MIME/schema/status mapping use actual stream fixtures; no raw body fallback.
- [ ] HT04: synthetic404/429/5xx and malformed data produce exact errors; old Shopify/policy dispatch still works; each denial case is paired with adjacent permitted case through same entry point.

## Validation

Provide `test:arch020-external-http` with HT01–HT04. HT01 must be implemented first and retained as the positive baseline. Tests instantiate createExternalHttpExecutionPort and the actual production DNS/transport implementation. A controlled HTTPS endpoint and injected DNS mapping may replace external internet, never bypass certificate/hostname verification or target validation in production code. Use recording socket/TLS adapters at OS boundary only where CI cannot bind a public address; demonstrate production connector uses the approved address.

Publish a fixtures table naming request, expected status/data, connected address and provider-call count. Every review correction becomes a committed regression plus adjacent allowed case. Typecheck/build plus old suites cannot substitute for these scenarios. Live public provider calls are unnecessary.

## Stop Condition

Submit implementation and parent report through normal mirrored task branches,
then stop at Review for moda_architect. Never self-accept, launch downstream tasks,
merge main, publish service deployments or update workspace service gitlinks.
Shared's package publication is required only for SHARED-002 as explicitly scoped.
SYSTEM-TEST-002 requires explicit developer invocation even when Ready.

## Implementation Notes

Use /moda-task launcher-resolved dedicated worktrees and preparation packet.
Task authoring on main is the user's documentation exception, not permission for
implementation on main. Preserve unrelated work and existing task claims.

## Completion Report

### Status

Review.

### Files Changed

- `src/commerce/external-http/index.ts`
- `src/commerce/execution/executor.ts`
- `src/commerce/execution/index.ts`
- `src/commerce/execution/ports.ts`
- `src/commerce/execution/renderer.ts`
- `tests/external-http-executor.test.ts`
- `tests/fixtures/external-http-tls.ts`
- `docs/external-http-executor.md`
- `package.json`
- `package-lock.json`

### Work Completed

- Added the injected `createExternalHttpExecutionPort` and secure Node HTTPS transport with fixed-origin GET construction, current connection resolution, address classification, DNS/socket pinning, TLS SNI and hostname verification, no redirects/proxies/cookies/retries, bounded decompression, decoding, result validation and bounded error mapping.
- Added an explicit `EXTERNAL_HTTP` dispatcher and renderer branch while retaining the existing Shopify and policy branches.
- Reconciled the accepted Shared package dependency to `@modainteract/moda-interact-shared@0.14.2`.
- Added the task-owned transport fixture table and public factory documentation.

### Validation Results

- `npm run test:arch020-external-http`: passed, 4/4 HT01--HT04 tests.
- `npm exec vitest run tests/definition-execution.test.ts tests/external-http-executor.test.ts`: passed, 16/16 tests.
- `npm run lint`: passed with two pre-existing warnings outside task-owned files (`scripts/code-runtime-manifest.mjs`, `src/commerce/code-response/runtime/kernel.ts`).
- `git diff --check`: passed.
- `npm run typecheck`: blocked by existing Prisma typing errors under `src/commerce/integration/backend*`; touched external-HTTP files have no editor diagnostics.

### Deviations

- The accepted Shared result union does not include `CANCELLED`. Abort/cancellation is therefore represented as non-retryable `DEADLINE`; no unsupported wire error code was introduced.

### Assumptions

- C21 read-only scope; visual rules and generic JavaScript remain injected processor ports owned by COMMERCE-025 and COMMERCE-026.

### Unresolved Issues

- Repository-wide typecheck remains blocked by unrelated integration backend Prisma typing errors.

### Architectural Concerns

- The Shared `CommerceToolResult` union lacks the C21-specified `CANCELLED` code. This task preserved the accepted shared contract and maps cancellation to `DEADLINE`; architect review should decide whether a future shared-contract amendment is required.

### Git / VCS

Mirrored branch: `task/ARCH-020-COMMERCE-021`.

Physical worktree isolation:
- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-021`
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-021`
- Shared workspace and shared implementation checkouts were not mutated for task work; no other task worktree was reused.

Start-of-attempt synchronization was already-current for both task branches. Recursive implementation submodule synchronization and update passed; `database` was initialized at `7f920e8f2ad523e78e566f4dbdfbb1f68118b082`. Implementation commit `b19f9d7` (`feat(commerce): execute bounded external HTTP tools`) was pushed to `origin/task/ARCH-020-COMMERCE-021`.

## Architect Review

### Review Status

Pending.

### Review Notes

Definition only; no implementation acceptance.

### Reviewed Files

Not applicable.

### Validation Reviewed

Not applicable.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile readiness/indexes after prerequisite acceptance; no automatic launch.
