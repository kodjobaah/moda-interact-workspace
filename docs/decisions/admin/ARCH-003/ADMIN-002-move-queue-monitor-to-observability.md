---
id: ARCH-003-ADMIN-002
architecture_id: ARCH-003
title: Move detailed queue diagnostics to Observability page shell
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 20
executor: copilot
claimed_at: 2026-09-04T19:16:14Z
attempt: 1
depends_on:
  - ARCH-003-ADMIN-001
enables:
  - ARCH-003-ADMIN-008
created: 2026-09-04
updated: 2026-09-04
---

# Move detailed queue diagnostics to Observability page shell

## Architecture

Architecture ID: `ARCH-003`

Architecture document:
`docs/architecture/ARCH-003-admin-operational-ui.md`

Coordinator: `moda_architect`

## Objective

Create the permanent `Observability > Shopify Queues` destination and remove the
large detailed queue-monitor block from `Tenant Directory`, without yet
redesigning the queue data into the final compact table.

## Context

ADMIN-001 provides compact queue activity cards on `Tenant Directory`.
Once those cards exist, detailed queue diagnostics should no longer occupy the
merchant-directory page.

This task is intentionally limited to navigation/page placement so Luna does not
need to perform the final queue-table redesign in the same execution.

## Scope

- remove the large detailed queue monitor from `Tenant Directory`;
- create or reuse a dedicated `Shopify Queues` route under Admin Observability;
- add/update sidebar or Observability navigation so the page is discoverable;
- move/reuse the existing detailed queue-monitor component on the new page as an
  interim presentation;
- preserve existing protected server-side queue access and refresh behavior;
- preserve existing Grafana navigation.

## Out of Scope

- final compact four-queue table redesign;
- failed-job list;
- failed-job detail;
- Redis reader redesign unless strictly required for page relocation;
- database changes;
- queue mutations.

## Requirements

- `Tenant Directory` no longer contains the large queue diagnostics block;
- the existing detailed queue monitor is reachable under Observability;
- no queue capability is lost during relocation;
- existing authorization remains enforced;
- Redis credentials remain server-side;
- Redis unavailability must not break unrelated Admin navigation/pages.

## Work Items

- [x] Identify the existing Tenant Directory queue-monitor mount point.
- [x] Remove that detailed monitor from Tenant Directory.
- [x] Add/refine the protected Shopify Queues Observability route.
- [x] Add/refine navigation to the Shopify Queues route.
- [x] Reuse the current detailed monitor on that route without broad redesign.
- [x] Add focused route/navigation placement tests.

## Interfaces / Contracts

Consumes the queue-monitor capability accepted under `ARCH-002-ADMIN-011` and
the overview separation established by `ARCH-003-ADMIN-001`.

No new cross-service contract is introduced.

## Dependencies

- `ARCH-003-ADMIN-001`

## Enables

- `ARCH-003-ADMIN-003`

## Acceptance Criteria

- [x] Tenant Directory contains no large detailed queue-monitor block.
- [x] Shopify Queues is reachable under Observability.
- [x] Existing queue data and refresh behavior remain functional on the new page.
- [x] Existing Admin authorization is preserved.
- [x] No database or non-Admin repository changes are made.

## Validation

- [x] focused navigation/page placement tests
- [x] affected Admin test suite
- [x] repository typecheck
- [x] repository lint
- [x] production build
- [x] `git diff --check`

## Implementation Notes

Do not opportunistically implement the final compact table or failed-job
experience. Return those to the following tasks.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `moda-interact-admin/src/app/(protected)/page.tsx`
- `moda-interact-admin/src/app/(protected)/observability/queues/page.tsx`
- `moda-interact-admin/src/components/admin/observability-panel.tsx`
- `moda-interact-admin/tests/security/grafana-observability.test.mjs`
- `docs/decisions/admin/ARCH-003/ADMIN-002-move-queue-monitor-to-observability.md`

### Work Completed
- Removed the detailed `QueueMonitor` mount from Tenant Directory while retaining
  the compact queue overview cards.
- Added the protected `/observability/queues` page and reused the existing
  detailed queue monitor without changing its refresh or API behavior.
- Added an Observability-panel link so platform admins can discover Shopify
  Queues alongside the existing Grafana destinations.
- Preserved the existing platform-admin page guard and server-side Redis access.

### Validation Results
- `node --test tests/security/grafana-observability.test.mjs tests/security/admin-queue-monitor.test.mjs` — 12 passed, 0 failed.
- `npm test` — 36 passed, 0 failed.
- `npm exec tsc -- --noEmit` — passed.
- `npm run lint` — passed with no warnings.
- `npm run build` — passed; `/observability/queues` is included as a dynamic route.
  Existing optional BullMQ `@valkey/valkey-glide` module warning remains.
- `git diff --check` — passed.

### Deviations
None.

### Assumptions
The existing detailed monitor is the intended interim presentation until the
later compact-table task; no queue-reader or data-contract redesign is needed.

### Unresolved Issues
None.

### Architectural Concerns
None.

## Architect Review

### Review Status
Accepted

### Review Notes

Architect reviewed the actual Attempt 1 implementation. The detailed `QueueMonitor` is no longer mounted on Tenant Directory, `/observability/queues` is protected with `requirePlatformAdminPage()`, the existing read-only monitor and refresh behavior are reused without queue-reader redesign, and the Observability landing page provides discoverable navigation to Shopify Queues while preserving existing Grafana navigation.

No database or non-Admin repository implementation was introduced.

### Reviewed Files

- `moda-interact-admin/src/app/(protected)/page.tsx`
- `moda-interact-admin/src/app/(protected)/observability/queues/page.tsx`
- `moda-interact-admin/src/app/(protected)/observability/page.tsx`
- `moda-interact-admin/src/components/admin/observability-panel.tsx`
- `moda-interact-admin/src/components/admin/queue-monitor.tsx`
- `moda-interact-admin/tests/security/grafana-observability.test.mjs`

### Validation Reviewed

Repository-agent evidence reviewed:

- focused tests: 12 passed, 0 failed;
- full Admin tests: 36 passed, 0 failed;
- TypeScript: passed;
- lint: passed;
- production build: passed;
- `git diff --check`: passed.

The supplied review archive does not include `node_modules`, so the architect did not independently rerun the Node validation suite.

### Architecture Conformance

Conforms to ARCH-003 ADMIN-002 scope. The task intentionally relocates the existing detailed monitor without implementing the later compact four-queue table or failed-job workflow.

### Follow-up

`ARCH-003-ADMIN-008` is now Ready. It owns the separately observed Tenant Directory queue-overview cold-readiness issue. `ARCH-003-ADMIN-003` remains Pending until ADMIN-008 is architect-accepted Complete.
