---
id: ARCH-010-SHARED-006
architecture_id: ARCH-010
title: Publish top-up refund Shared message contracts
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 23
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-SHARED-005
enables:
  - ARCH-010-ADMIN-002
  - ARCH-010-ADMIN-003
  - ARCH-010-SHOPIFY-017
created: 2026-09-11
updated: 2026-09-11T17:44:41Z
---

# ARCH-010-SHARED-006: Publish top-up refund Shared message contracts

## Objective

Publish the architect-accepted additive Shared billing-message change from ARCH-010-SHARED-005 for Admin/Shopify consumers.

## Publication rule

Before changing version metadata, inspect:

```text
package.json
package-lock.json
npm registry current version/dist-tag
```

Choose the next valid additive pre-1.0 release from the actual accepted/published state.

Do not assume a version number from this task document. If repository/registry state has advanced or another accepted unpublished Shared change must be co-released, STOP and return the observed state to `moda_architect` rather than overwriting/guessing.

Publication-only: do not alter contract implementation except version/package metadata required by the accepted source.

Verify the published tarball/runtime/declarations expose the three refund codes through the canonical billing export.

Run established Shared publication validation and `git diff --check`.

## Validation

Use only the repository's established publication workflow. Verify the published tarball/runtime/declarations expose the three accepted refund message codes through the canonical billing export, confirm registry version/dist-tag, and run `git diff --check`.

## Non-goals

Do not alter the accepted SHARED-005 contract implementation, edit consumer repositories, create provider refund APIs, or publish unrelated unreviewed Shared changes.

## Stop conditions

STOP if the registry/repository version has advanced unexpectedly, SHARED-005 is not the source being published, or another accepted-but-unpublished Shared change must be co-released without architect reconciliation.

## Completion Report

### Status
Complete — publication satisfied by coordinated Shared `0.10.0` co-release.

### Files Changed
No separate implementation or package-version change was required for this task.

### Work Completed
The architect-accepted `ARCH-010-SHARED-005` refund message contracts were already
present in the Shared source tree physically published by
`ARCH-010-SHARED-002` as:

`@modainteract/moda-interact-shared@0.10.0`

The coordinated release therefore satisfied this task's publication objective
without a second npm publication.

The published Shared contract contains the accepted canonical refund message codes:

- `BILLING_REFUND_REQUEST_RECEIVED`;
- `BILLING_REFUND_COMPLETED`;
- `BILLING_REFUND_REJECTED`.

### Validation Results
Publication evidence inherited from the coordinated `0.10.0` release:

- package tests: `110 passed, 1 skipped`;
- typecheck: passed;
- build: passed;
- public billing-entrypoint validation: passed;
- pack dry-run / published artifact validation: passed;
- npm `latest`: `0.10.0`;
- shasum: `219601ddc1689f5cbeb6a8b4ab82326445b16654`.

No additional `npm publish` was required or permitted because it would have
republished functionality already present in `0.10.0`.

### Git / VCS
Publication evidence is the coordinated SHARED-002 release handoff:

- implementation/publication commit: `583a7d6`;
- parent Completion Report commit: `d658adc`.

No separate SHARED-006 implementation commit is required because this task was
satisfied by the already-published coordinated artifact.

### Architect Review

#### Review Status
Accepted

#### Coordinated publication acceptance

Architect review accepts `@modainteract/moda-interact-shared@0.10.0` as satisfying
the publication objective of this task.

`ARCH-010-SHARED-005` had already been architect-accepted before publication, and
its three refund billing-message contracts were included in the source tree
published as `0.10.0`.

Publishing a second semantically identical package release solely for this task
would be redundant and would violate the intent of the publication/version
coordination rules.

**Architect decision: Accepted — Complete via coordinated `0.10.0` co-release.**

`attempt: 0` is intentionally preserved because no separate task execution or
second publication was required.

