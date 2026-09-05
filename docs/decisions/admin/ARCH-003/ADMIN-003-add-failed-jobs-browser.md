---
id: ARCH-003-ADMIN-003
architecture_id: ARCH-003
title: Present the four queues in a compact summary table
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 30
executor: copilot
claimed_at: 2026-09-04T19:56:19Z
attempt: 1
depends_on:
  - ARCH-003-ADMIN-008
enables:
  - ARCH-003-ADMIN-004
created: 2026-09-04
updated: 2026-09-04
---

# Present the four queues in a compact summary table

## Architecture

Architecture ID: `ARCH-003`

Architecture document:
`docs/architecture/ARCH-003-admin-operational-ui.md`

Coordinator: `moda_architect`

## Objective

Replace the interim large queue-card presentation on `Observability > Shopify
Queues` with a compact summary table covering all four observed queues.

## Context

ADMIN-002 establishes the correct page boundary. This task changes only the
queue summary presentation and queue coverage.

## Scope

- present exactly these four queue rows:
  - `checkout-events`
  - `order-events`
  - `pending-recovery-candidates`
  - `whatsapp-events`;
- show compact operational columns for each row:
  - queue name
  - job label/description
  - waiting
  - active
  - delayed
  - failed
  - workers
  - last Redis activity;
- preserve refresh interval selection and manual refresh on this detailed page;
- provide a read-only `View details` or equivalent queue-selection affordance;
- reuse the current queue data access where practical;
- add only the Admin-local queue configuration required for the two additional
  observed queues.

## Out of Scope

- retrieving failed-job rows;
- sorting failures;
- selected job details;
- mutations;
- database changes.

## Requirements

- all four queues appear in one compact operational presentation;
- layout remains usable on typical laptop widths;
- failed counts are shown here because this is the detailed Observability page;
- refresh controls remain on this page only;
- `View details` selects a queue but does not yet need to render failure rows;
- Redis unavailability degrades safely.

## Work Items

- [x] Extend the Admin queue summary model to all four observed queues.
- [x] Replace large per-queue cards with a compact summary table.
- [x] Preserve existing refresh controls.
- [x] Add the read-only queue selection/details affordance.
- [x] Add focused four-queue table tests.

## Interfaces / Contracts

Consumes the protected queue reader and Observability page created by prior
tasks.

No cross-service payload contract is changed.

## Dependencies

- `ARCH-003-ADMIN-008`

## Enables

- `ARCH-003-ADMIN-004`

## Acceptance Criteria

- [x] Exactly four observed queues are shown.
- [x] Queue metrics are presented as compact rows rather than oversized cards.
- [x] Waiting, active, delayed, failed, workers and last activity are visible.
- [x] Refresh controls remain functional.
- [x] Queue selection/details action is present and read-only.
- [x] No failed-job retrieval is implemented in this task.

## Validation

- [x] focused four-queue summary tests
- [x] affected Admin test suite
- [x] repository typecheck
- [x] repository lint
- [x] production build
- [x] `git diff --check`

## Implementation Notes

The existing filename is retained because this task ID already existed as a
pending ARCH-003 task before refinement. The task body is authoritative.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `moda-interact-admin/src/lib/admin/queue-monitor.ts`
- `moda-interact-admin/src/components/admin/queue-monitor.tsx`
- `moda-interact-admin/tests/security/admin-queue-monitor.test.mjs`

### Work Completed
- Extended the Admin-local detailed queue definitions to cover all four observed
  queues while retaining canonical Shopify job names for checkout and order
  events.
- Replaced the large queue cards with a compact horizontally contained table
  showing queue, job label, waiting, active, delayed, failed, workers and last
  Redis activity.
- Added a read-only `View details` queue selection state without failed-job
  retrieval or queue mutations.
- Added focused assertions for four detailed rows and the table affordance.

### Validation Results
- `npm exec -- node --test tests/security/admin-queue-monitor.test.mjs` passed
  (10 tests).
- `npm test` passed (39 tests).
- `npm exec tsc -- --noEmit` passed.
- `npm run lint` passed.
- `npm run build` passed.
- `git diff --check` passed.

### Deviations
The production build retains existing warnings for Next.js multiple-lockfile
workspace-root inference and BullMQ's optional `@valkey/valkey-glide` module.

### Assumptions
The two non-Shopify queue labels remain Admin-local descriptive labels because
no shared job-name contracts were changed.

### Unresolved Issues
None.

### Architectural Concerns
None.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 is architect-accepted Complete.

The reviewed implementation conforms to the bounded ADMIN-003 scope:

- exactly four observed queues are represented;
- the detailed queue presentation is a compact table rather than oversized
  per-queue cards;
- waiting, active, delayed, failed, worker count and latest Redis activity are
  visible;
- existing refresh interval selection and manual refresh behavior are
  preserved;
- `View details` performs read-only queue selection only;
- failed-job retrieval, sorting and job-detail data are not implemented early;
- Redis access remains behind the existing protected Admin API/server boundary.

The two non-Shopify queue labels are Admin-local descriptive labels only and do
not change producer/consumer runtime contracts.

### Reviewed Files

- `moda-interact-admin/src/lib/admin/queue-monitor.ts`
- `moda-interact-admin/src/components/admin/queue-monitor.tsx`
- `moda-interact-admin/src/app/(protected)/observability/queues/page.tsx`
- `moda-interact-admin/tests/security/admin-queue-monitor.test.mjs`
- `docs/decisions/admin/ARCH-003/ADMIN-003-add-failed-jobs-browser.md`

### Validation Reviewed

Implementing-agent evidence records:

- focused queue-monitor tests: pass;
- full Admin tests: 39 passed;
- TypeScript: pass;
- lint: pass;
- production build: pass;
- `git diff --check`: pass.

The supplied review archive does not include `node_modules`, so the architect
inspected the current source and recorded validation rather than reinstalling
dependencies solely to rerun the suite.

### Architecture Conformance

Accepted.

The implementation remains confined to `moda-interact-admin`, preserves the
read-only architecture boundary, and does not begin ADMIN-004 work.

### Follow-up

`ARCH-003-ADMIN-004` is now Ready.

It must implement only the bounded failed-job server reader/API and must not
begin the failed-job browser UI.
