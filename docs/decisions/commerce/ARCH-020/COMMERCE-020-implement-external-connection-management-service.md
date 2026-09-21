---
id: ARCH-020-COMMERCE-020
architecture_id: ARCH-020
title: Implement external connection lifecycle and command kernel
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 150
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-020-DATABASE-003
  - ARCH-020-SHARED-002
  - ARCH-020-COMMERCE-002
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-024
  - ARCH-020-GATEWAY-003
  - ARCH-020-COMMERCE-028
created: 2026-09-21
updated: 2026-09-21
---

# Implement external connection lifecycle and command kernel

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Own src/commerce/connections/lifecycle/** and src/commerce/connections/command-kernel.ts only. Implement metadata/revision/enabled lifecycle and reusable transaction/auth/replay kernel. No credential encryption/storage commands/resolver, network, UI or final factories.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Own src/commerce/connections/lifecycle/** and src/commerce/connections/command-kernel.ts only. Implement metadata/revision/enabled lifecycle and reusable transaction/auth/replay kernel. No credential encryption/storage commands/resolver, network, UI or final factories.

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

- [ ] Implement createConnectionLifecycle with list/get/create/updateMetadata/createRevision/setEnabled, strict section4 DTOs, immutable revision allocation and locked metadata CAS.
- [ ] Implement section9 command kernel with authorization-before-replay, canonical keyed digest, transaction mutation/audit atomicity and unique-race reconciliation.028 imports it; no generic application framework.
- [ ] Provide metadata-only U15/U16 read models; do not claim credential status is implemented. Return exact new revision IDs without migrating published tool references.
- [ ] Produce actual lifecycle create/revise/disable success and contentious update/replay/rollback scenarios early.

## Interfaces / Contracts

C21 sections1–8 retain data/behavior requirements. [Section9](../../../architecture/ARCH-020-external-api-tools.md#9-tightened-implementation-boundaries-and-evidence) is authoritative for the narrowed ownership, factory signatures, scenario IDs and handoff rules. Consume accepted exports; no consumer may repair a missing producer by weakening the contract. Record actual dependency commits and published package versions.

## Dependencies

- ARCH-020-DATABASE-003
- ARCH-020-SHARED-002
- ARCH-020-COMMERCE-002

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-024
- ARCH-020-GATEWAY-003
- ARCH-020-COMMERCE-028

## Acceptance Criteria

- [ ] CL01: valid create->metadata update->new immutable revision->disable/enable path through actual service preserves prior revision and returns exact IDs.
- [ ] CL02: two clients contend on same CAS or operation: one effect/audit; same replay returns original; altered replay/stale CAS produce no write; failure after actual write rolls back.
- [ ] CL03: ADMIN/revoked staff mutation denied before replay; connection origin/auth schema errors rejected; no credentials or HTTP in owned implementation.

## Validation

Provide `test:arch020-external-connection-lifecycle` and scenario IDs from C21 section9. Start with the named positive path through the actual owned implementation. Add the specified rejection/race cases. Each report maps criterion -> test file/test name -> command -> observable result, not just a suite count. No claimed success based only on safe rejection or missing-config tests. Preserve each review reproduction as a committed regression alongside adjacent allowed/denied cases.

Use focused checks while implementing, then existing typecheck/build/lint where defined. Record unrun developer-owned PostgreSQL/container checks accurately; executable scenarios must still exist. No repeated unrelated full suites or screenshot quotas. No live credentials/WhatsApp delivery.

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

Implementation complete; submitted for Architect Review.

### Files Changed

- `src/commerce/connections/command-kernel.ts`
- `src/commerce/connections/lifecycle/index.ts`
- `src/commerce/connections/lifecycle/types.ts`
- `tests/connection-lifecycle.test.ts`
- `package.json` (`test:arch020-external-connection-lifecycle`)

### Work Completed

- Implemented the C21 command transaction kernel with active-staff/SUPER_ADMIN authorization before replay lookup, canonical keyed request digests, same-operation replay, conflicting replay rejection, atomic mutation/audit handling, and unique-race reconciliation.
- Implemented metadata-only connection list/get/create/updateMetadata/createRevision/setEnabled lifecycle operations with strict bounded DTOs, HTTPS origin and auth-header validation, immutable revision numbering, and atomic edit-version CAS.
- Added CL01/CL02/CL03 focused acceptance coverage for the positive lifecycle, replay/conflict/stale-CAS/rollback behavior, and origin/auth rejection.

### Validation Results

- `npm run test:arch020-external-connection-lifecycle`: passed, 1 file and 5 tests.
- `npx eslint src/commerce/connections/command-kernel.ts src/commerce/connections/lifecycle/index.ts src/commerce/connections/lifecycle/types.ts tests/connection-lifecycle.test.ts`: passed.
- `npm run typecheck`: task-owned connection files have no diagnostics; the repository command remains red on pre-existing unrelated baseline errors in `lib/auth/development-platform-admin.ts`, `lib/server/connections.ts`, and `src/commerce/integration/**`.
- `git diff --check`: passed.
- Full build and PostgreSQL/container checks were not run; no live credentials or external HTTP calls were used.

### Deviations

No design deviations. Implementation remains within the task-owned connection lifecycle/kernel paths, with the required focused test script and test file added for acceptance evidence.

### Assumptions

C21 read-only scope; credential encryption/storage, OAuth, network execution, UI, publication, preview, and final factories remain out of scope.

### Unresolved Issues

Repository-wide typecheck/build debt remains outside the task-owned files. PostgreSQL/container validation remains developer-owned and unrun.

### Architectural Concerns

No architectural concern identified in the implemented scope. Architect review should confirm the accepted C21 field/error contracts and the baseline typecheck debt noted above.

### Git / VCS

Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-020`.
Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-020`.
Logical agent: `moda_commerce`; canonical executor: `copilot`; attempt: 1.
Dependencies were accepted before execution: DATABASE-003, SHARED-002, COMMERCE-002.
Database submodule evidence: `7f920e8f2ad523e78e566f4dbdfbb1f68118b082`.
Implementation branch: `task/ARCH-020-COMMERCE-020`; commit/push: `5229b033a7dbef73b35571784996b539707cf03a`.

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
