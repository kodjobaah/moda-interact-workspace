---
id: ARCH-003-ADMIN-017
architecture_id: ARCH-003
title: Project pending-recovery tenant metadata in queue diagnostics
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 20
executor: copilot
claimed_at: 2026-09-05T06:10:37Z
attempt: 1
depends_on:
  - ARCH-003-BACKGROUND-001
enables:
  - ARCH-003-ADMIN-018
created: 2026-09-05
updated: 2026-09-05
---

# Project pending-recovery tenant metadata in queue diagnostics

## Architecture

`docs/architecture/ARCH-003-admin-operational-ui.md`

## Objective

Make new `pending-recovery-candidates` jobs appear under their real shop in the
ARCH-003 queue filters instead of `Orphan / No shop`.

## Scope

Extend the explicit shop projection used by the generic queue-job readers.

Canonical paths:

```text
checkout-events / order-events
  -> data.tenant.shopDomain

pending-recovery-candidates
  -> data.shopDomain
```

Use only explicit allowlisted paths.

## Requirements

- normalize the projected shop domain using existing Admin normalization rules;
- new pending-recovery jobs with `data.shopDomain` appear under that shop;
- historical pending-recovery jobs without it remain `Orphan / No shop`;
- `shop=*` includes attributed and historical orphan jobs;
- `shop=__orphan__` continues to work;
- Failed/Active/Waiting/Delayed support remains unchanged;
- pagination/detail behavior remains unchanged;
- do not infer shop from shopId, jobId, email, phone, URL, or arbitrary strings;
- no queue mutation.

## Acceptance Criteria

- [x] Pending-recovery shopDomain is projected.
- [x] Shop facets include normalized pending-recovery shops.
- [x] Delayed pending-recovery rows show the real shop when metadata exists.
- [x] Historical missing-metadata jobs remain Orphan / No shop.
- [x] Existing checkout/order projection is unchanged.
- [x] Four-state filtering does not regress.
- [x] Pagination/detail workflow does not regress.
- [x] Validation passes.

## Completion Report

### Status

Ready for Review.

### Work Items

- [x] Extend the allowlisted generic shop projection for pending-recovery
  payloads.
- [x] Preserve normalized projection and orphan behavior across all queue
  states and detail reads.
- [x] Add regression coverage for metadata, facets, and historical orphans.

### Files Changed

- `moda-interact-admin/src/lib/admin/queue-monitor.ts`
- `moda-interact-admin/tests/security/admin-queue-jobs.test.mjs`

### Work Completed

Pending-recovery jobs now project `data.shopDomain` through the generic queue
reader using the existing normalization rules. The projection is restricted to
the allowlisted `evaluate-pending-recovery` job name and does not infer a shop
from `shopId`, job IDs, or arbitrary payload fields. Historical jobs without
`shopDomain` remain orphaned, while facets and `__orphan__` filtering continue
to reflect attributed and unattributed jobs across all four states.

### Validation Results

- Focused queue list/detail tests: 11 passed.
- `npm test`: 73 passed.
- `npm run build`: passed; Next.js emitted existing workspace-root and optional
  BullMQ `@valkey/valkey-glide` warnings.
- `npm run lint`: passed with two existing React hook warnings in
  `src/components/admin/queue-monitor.tsx`; no errors.
- `git diff --check`: passed.

### Deviations

None.

### Assumptions

- The producer-owned BullMQ job name is `evaluate-pending-recovery`; the
  existing human-readable queue label remains unchanged for the UI.

### Unresolved Issues

None.

### Architectural Concerns

None. The change remains confined to the Admin repository and performs no queue
mutation.

### Git / VCS Note

Implementation is ready for developer commit/push. No commit or push was made.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 is architect-accepted Complete.

The reviewed implementation extends the existing explicit queue-job shop
projection without introducing fuzzy tenant inference.

Accepted projection:

```text
checkout-events / order-events
  -> data.tenant.shopDomain

pending-recovery-candidates
  -> data.shopDomain
```

For `pending-recovery-candidates`, the projection is restricted to the real
producer-owned BullMQ job name:

```text
evaluate-pending-recovery
```

The existing normalization rules are reused.

### Historical compatibility

Historical pending-recovery jobs without `data.shopDomain` continue to produce:

```text
shop = null
```

and therefore remain visible as:

```text
Orphan / No shop
```

New attributed jobs contribute their normalized domain to the Shop facets and
can be filtered by that domain.

### Architecture boundaries preserved

The implementation does not infer a shop from:

- shopId;
- BullMQ jobId;
- email;
- phone number;
- URLs;
- arbitrary nested payload strings.

It does not change:

- queue state handling;
- Failed / Active / Waiting / Delayed support;
- pagination;
- job detail behavior;
- queue mutation policy.

### Reviewed Files

- `moda-interact-admin/src/lib/admin/queue-monitor.ts`
- `moda-interact-admin/tests/security/admin-queue-jobs.test.mjs`
- `docs/decisions/admin/ARCH-003/ADMIN-017-project-pending-recovery-shop.md`

### Validation Reviewed

Implementing-agent evidence records:

- focused queue tests: 11 passed;
- full Admin suite: 73 passed;
- production build: passed;
- TypeScript diagnostics: none;
- lint: passed with the two pre-existing React hook warnings;
- `git diff --check`: passed.

### Result

`ARCH-003-ADMIN-017` is Complete.

`ARCH-003-ADMIN-018` is promoted to Ready.
