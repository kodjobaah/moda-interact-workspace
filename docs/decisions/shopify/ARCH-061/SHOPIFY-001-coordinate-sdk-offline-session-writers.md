---
id: ARCH-061-SHOPIFY-001
architecture_id: ARCH-061
title: coordinate sdk offline session writers
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-061-SHARED-002"]
enables: ["ARCH-061-BACKGROUND-001", "ARCH-061-COMMERCE-001", "ARCH-061-MCP-001", "ARCH-061-SYSTEM-TEST-001"]
created: 2026-11-05
updated: 2026-11-05
---
# Coordinate sdk offline session writers

## Architecture
ARCH-061; docs/architecture/ARCH-061-shopify-offline-token-refresh-coordination.md. Coordinator moda_architect.

## Objective
Coordinate sdk offline session writers using the published injected-client Shared runtime.

## Context
Background bespoke refresh currently reads/refreshes/writes unlocked; App SDK refreshes before storage write. Consumers use the same persisted rotating offline credential.

## Scope
Task-owned moda-interact changes and focused validation only. Cross-repository paths below are read-only baseline evidence unless owned by this task.

| Existing file | Symbol/surface | Required change |
|---|---|---|
| moda-interact/app/shopify.server.js | shopifyApp configuration and sessionStorage | Compose factory with App Prisma and existing OAuth configuration; establish supported pre-read SDK boundary. |
| moda-interact/app/routes/webhooks/app/uninstalled/route.jsx | uninstall route | Enforce same lifecycle lock order/current-install checks and no stale resurrection. |
| moda-interact/tests/helpers/shopify-lifecycle-postgres.ts | independent Prisma/session storage fixtures | Add SDK-vs-shared concurrency and install/uninstall race tests. |


## Out of Scope
Central token service, agent tools, sibling imports, credential UI, schema changes, node_modules patches, automatic execution, claims or main merges.

## Requirements
The entire parent architecture runtime/bounds/SDK/lifecycle/ambiguity matrix is normative. Factory accepts each service's local Prisma client at composition. Lock before read/decision/remote refresh; write-only locking is insufficient. No exactly-once remote guarantee across crash. Stop for unsupported SDK/lifecycle/recovery gaps instead of weakening coordination.

## Work Items
- [ ] Inventory every SDK/custom offline writer and prove supported coordinated read-through-refresh scope. Storage-write-only adapter is forbidden.
- [ ] Implement App lifecycle ordering with Shared primitives and canonical identity checks; stop on unsupported SDK/absent-row boundary.
- [ ] Prove SDK/Background-style client simultaneous refresh yields one normal remote call; stale store cannot overwrite new pair.

## Interfaces / Contracts
Shared Node-only factory and structural transaction interface/error categories defined by SHARED-001 and published by SHARED-002. Consumers inject local client/config/fetch and translate errors. No sibling source imports; no browser exports or raw token DTOs. App owns all SDK/lifecycle mutation entrypoints.

## Dependencies
- ARCH-061-SHARED-002

## Enables
- ARCH-061-BACKGROUND-001
- ARCH-061-COMMERCE-001
- ARCH-061-MCP-001
- ARCH-061-SYSTEM-TEST-001

## Acceptance Criteria
- [ ] Inventory every SDK/custom offline writer and prove supported coordinated read-through-refresh scope. Storage-write-only adapter is forbidden.
- [ ] Implement App lifecycle ordering with Shared primitives and canonical identity checks; stop on unsupported SDK/absent-row boundary.
- [ ] Prove SDK/Background-style client simultaneous refresh yields one normal remote call; stale store cannot overwrite new pair.
- [ ] Relevant parent matrix rows pass; no uncoordinated bypass, stale pair overwrite or secret emission.

## Validation
- [ ] Inspect package.json and run declared focused unit/integration tests for task-owned matrix rows, including disposable PostgreSQL separate-client races; record exact commands. Run declared typecheck/build appropriate to deployable changes.
- [ ] Record boundary/gap evidence honestly; never infer SDK coordination from helper-only tests.

## Stop Condition
Submit completed report for authorized review and STOP after scoped criteria/validation. Explicit developer completion required. Do not start enabled tasks; system validation is terminal/manually invoked.

## Implementation Notes
No execution started. Use launcher isolated/synchronized task worktrees when requested. Read installed SDK and official Shopify recovery guidance before implementing. Node recovery uses workspace bootstrap. Return new schema, lock primitive or unsupported SDK requirements to architect. Publication is release mechanics only.

## Completion Report
### Status
Not Started
### Files Changed
None
### Work Completed
None
### Validation Results
Definition only.
### Deviations
None
### Assumptions
Same canonical PostgreSQL credential row and supported provider recovery rules; implementation must verify lifecycle/SDK gates.
### Unresolved Issues
See parent open implementation gates; no false implementation claim.
### Architectural Concerns
Stop for absent-row lifecycle, unsupported SDK boundary or recovery persistence needs.

## Architect Review
### Review Status
Pending
### Review Notes
Definition only.
### Reviewed Files
None
### Validation Reviewed
None
### Architecture Conformance
Pending implementation.
### Follow-up
None
