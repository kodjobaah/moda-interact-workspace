---
id: ARCH-003-ADMIN-018
architecture_id: ARCH-003
title: Distinguish unresolved WhatsApp jobs from orphan tenant metadata
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 30
executor: copilot
claimed_at: 2026-09-05T06:19:38Z
attempt: 1
depends_on:
  - ARCH-003-ADMIN-017
enables:
  - ARCH-003-ADMIN-019
created: 2026-09-05
updated: 2026-09-05
---

# Distinguish unresolved WhatsApp jobs from orphan tenant metadata

## Architecture

`docs/architecture/ARCH-003-admin-operational-ui.md`

## Objective

Represent legitimate tenant uncertainty at WhatsApp ingress truthfully in the
ARCH-003 queue UI.

## Classification

```text
Known
Unresolved
Orphan / No shop
```

### Known

An approved explicit field supplies a normalized shop domain.

### Unresolved

The queue boundary legitimately permits tenant identity to be unknown.

For the current architecture this includes `whatsapp-events` jobs that have no
approved explicit tenant/shop attribution at ingress.

### Orphan / No shop

The job belongs to a queue/job type expected to contain tenant attribution but
the approved field is absent or invalid.

## Scope

- introduce explicit `Unresolved` UI treatment;
- make Unresolved filterable independently from Orphan;
- preserve All shops behavior;
- preserve known-shop filtering;
- preserve all four BullMQ states;
- preserve pagination and detail;
- do not change `moda-interact-messaging`;
- do not add synchronous tenant lookup to WhatsApp ingress;
- do not guess tenant from phone/email/message text/context IDs.

## Acceptance Criteria

- [x] WhatsApp ingress job with no approved shop attribution renders Unresolved.
- [x] Unresolved is filterable independently.
- [x] Orphan remains distinct and filterable.
- [x] Known shops still filter correctly.
- [x] All shops includes Known + Unresolved + Orphan.
- [x] No fuzzy inference is introduced.
- [x] Four-state/pagination/detail workflow does not regress.
- [x] Validation passes.

## Completion Report

### Status

Ready for Review.

Implementation completed in `moda-interact-admin`:

- Added explicit `known`, `unresolved`, and `orphan` attribution to queue
  summaries and details while keeping `shop` nullable for compatibility.
- Classified `whatsapp-events` without approved tenant metadata as unresolved;
  no tenant lookup or fuzzy inference is performed.
- Added the independent `__unresolved__` filter and ensured orphan facets and
  filters exclude unresolved WhatsApp jobs.
- Added regression coverage for WhatsApp snapshots, detail attribution,
  facets, filtering, existing known-shop projection, orphan handling, and the
  four queue states.

Validation completed:

- `npm test` passed: 74 tests.
- `npm run lint` passed with two existing React hook dependency warnings.
- `npm run build` passed; Next.js reported existing workspace-root and optional
  BullMQ `@valkey/valkey-glide` warnings.
- `git diff --check` passed.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 is architect-accepted Complete.

The reviewed implementation establishes explicit queue-job attribution:

```text
known
unresolved
orphan
```

Accepted behavior:

- an approved explicit normalized shop domain is `known`;
- `whatsapp-events` without approved tenant attribution are `unresolved`;
- queue boundaries that expect tenant attribution but lack it remain `orphan`;
- `__unresolved__` is independently filterable from `__orphan__`;
- All shops includes known, unresolved, and orphan jobs;
- selected-job detail carries the same attribution classification;
- Failed / Active / Waiting / Delayed behavior remains intact.

The WhatsApp regression coverage also proves that an unapproved `shopDomain`
field inside the WhatsApp payload is not treated as tenant attribution.

No synchronous tenant lookup or fuzzy inference from phone, email, message text,
context ID, URL, job ID, or arbitrary payload strings was introduced.

Validation evidence:

- Admin suite: 74 tests passed;
- build: passed;
- TypeScript diagnostics: clean;
- `git diff --check`: passed;
- lint: passed with the two existing React hook warnings.

### Result

`ARCH-003-ADMIN-018` is Complete.

The separate live navigation issue identified after implementation is owned by
`ARCH-003-ADMIN-019`, which is promoted to Ready.
