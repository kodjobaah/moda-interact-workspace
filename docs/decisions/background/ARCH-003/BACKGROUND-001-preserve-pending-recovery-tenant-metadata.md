---
id: ARCH-003-BACKGROUND-001
architecture_id: ARCH-003
title: Preserve tenant metadata on pending-recovery candidate jobs
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 10
executor: copilot
claimed_at: 2026-09-05T06:02:15Z
attempt: 1
depends_on:
  - ARCH-003-ADMIN-013
enables:
  - ARCH-003-ADMIN-017
created: 2026-09-05
updated: 2026-09-05
---

# Preserve tenant metadata on pending-recovery candidate jobs

## Architecture

`docs/architecture/ARCH-003-admin-operational-ui.md`

## Objective

Make newly produced `pending-recovery-candidates` jobs operationally
tenant-identifiable so the ARCH-003 queue UI can show their real shop.

## Scope

For newly enqueued pending-recovery candidate jobs, preserve explicit:

```text
data.shopId
data.shopDomain
```

from tenant identity already known by the producing background workflow.

Do not perform an additional database/API lookup solely for observability.

Use a tenant-readable BullMQ ID:

```text
<shopId>--<existingDeterministicJobId>
```

Preserve the complete existing deterministic ID as the suffix.

## Requirements

- preserve current candidate delay/scheduling semantics;
- preserve retry/removal behavior;
- preserve existing candidate payload fields;
- keep current shopId;
- add normalized shopDomain without fabricating it;
- preserve idempotency across the job-ID transition;
- check/handle legacy and new job IDs where necessary so rollout cannot create
  duplicate candidate work;
- do not rewrite historical Redis jobs;
- do not modify Shopify ingress;
- do not modify WhatsApp ingress;
- no new per-shop queues.

## Acceptance Criteria

- [x] New candidate data contains explicit shopId.
- [x] New candidate data contains explicit normalized shopDomain.
- [x] Both values come from already-known tenant context.
- [x] New candidate job ID starts with `<shopId>--`.
- [x] Existing deterministic ID remains the full suffix.
- [x] Legacy/new transition cannot create duplicate candidate work.
- [x] Candidate delay semantics are unchanged.
- [x] Recovery business behavior is unchanged.
- [ ] Focused tests and repository validation pass.

## Validation

- [x] focused pending-recovery producer tests
- [x] candidate consumer regression tests
- [ ] repository test/build checks (build passes; full suite has an unrelated existing `recovery-routing.service.test.ts` mock failure)
- [x] typecheck (via `npm run build`)
- [ ] lint (no lint script is defined for this repository)
- [x] `git diff --check`

## Completion Report

### Status

Ready for Review.

### Implemented Files

- `moda-interact-background/src/domain/pending-recovery-candidate.ts`
- `moda-interact-background/src/services/pending-recovery-candidate.service.ts`
- `moda-interact-background/tests/unit/services/pending-recovery-candidate.service.test.ts`
- `moda-interact-background/tests/unit/services/matured-candidate.materialization.test.ts`

### Validation Results

- Focused pending-recovery and materialization tests: 20 passed.
- `npm run build`: passed.
- Full `npm test`: 96 passed, 4 skipped, 1 unrelated failure in
  `tests/unit/services/recovery-routing.service.test.ts`; its Prisma mock does
  not define `customerPhone.findMany`.
- `git diff --check`: passed.

### Deviations, Assumptions, and Unresolved Issues

- Legacy jobs remain the active correlation target when only the legacy ID
  exists; when both IDs exist, the new-format job wins and the legacy duplicate
  is removed.
- Historical Redis jobs are not rewritten.
- Lint was not run because no lint script is defined in the background package.
- The unrelated recovery-routing test failure remains unresolved.

### Git / VCS Note

Changes are ready for developer review and commit. No commit or push was made.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 is architect-accepted Complete based on the corrected
`moda-interact-background` submission.

The reviewed implementation adds explicit tenant attribution to newly produced
`pending-recovery-candidates` jobs:

```text
data.shopId
data.shopDomain
```

`shopDomain` is normalized from the already-known checkout event domain before
the existing Shop lookup and is carried into the candidate payload.

New BullMQ candidate IDs use:

```text
<shopId>--<existingDeterministicJobId>
```

while retaining the existing deterministic pending-recovery ID as the complete
suffix.

### Rolling idempotency behavior

The producer checks both:

```text
new tenant-readable ID
legacy deterministic ID
```

before creating a job.

Accepted transition behavior:

- new-format job exists -> refresh it;
- legacy-format job exists -> refresh/reuse it without creating a duplicate;
- both exist -> retain the new-format job and remove the redundant legacy copy;
- neither exists -> enqueue the new-format ID.

Existing checkout/cart Redis indexes continue to point to the active candidate
ID, preserving O(1) correlation.

### Architecture boundaries preserved

The implementation does not change:

- candidate delay configuration;
- retry/backoff/remove policy;
- checkout-recovery materialization semantics;
- Shopify webhook ingress;
- WhatsApp ingress;
- queue topology;
- historical Redis job IDs.

Historical legacy jobs are not rewritten.

### Reviewed Files

- `moda-interact-background/src/domain/pending-recovery-candidate.ts`
- `moda-interact-background/src/services/pending-recovery-candidate.service.ts`
- `moda-interact-background/tests/unit/services/pending-recovery-candidate.service.test.ts`
- `moda-interact-background/tests/unit/services/matured-candidate.materialization.test.ts`
- `docs/decisions/background/ARCH-003/BACKGROUND-001-preserve-pending-recovery-tenant-metadata.md`

### Validation Reviewed

Implementing-agent evidence:

- focused pending-recovery/materialization tests: 20 passed;
- build/typecheck: passed;
- `git diff --check`: passed;
- full suite: 96 passed, 4 skipped, 1 unrelated existing routing-test mock
  failure.

The full-suite failure is not caused by this task. The failing
`recovery-routing.service.test.ts` Prisma mock does not define
`customerPhone.findMany`, while the unrelated routing service invokes it.

No lint script exists in the Background package, so lint is not an executable
repository validation for this task.

### Result

`ARCH-003-BACKGROUND-001` is Complete.

`ARCH-003-ADMIN-017` is promoted to Ready.
