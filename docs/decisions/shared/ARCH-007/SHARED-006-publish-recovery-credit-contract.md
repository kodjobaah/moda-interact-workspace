---
id: ARCH-007-SHARED-006
architecture_id: ARCH-007
title: Publish Shared recovery-credit billing contract
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: complete
priority: 38
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-007-SHARED-005
enables:
  - ARCH-007-ADMIN-005
  - ARCH-007-SHOPIFY-004
  - ARCH-007-BACKGROUND-009
created: 2026-09-08
updated: 2026-09-08
---

# ARCH-007-SHARED-006: Publish Shared recovery-credit billing contract

## Exact release

Publish the architect-accepted SHARED-005 implementation as:

```text
@modainteract/moda-interact-shared@0.8.0
```

This is a publication-only task.

Allowed:
- apply/select exact version `0.8.0`;
- publication-specific lock/package metadata;
- publish;
- verify registry version and exported `RECOVERY_CREDIT_PACK_PURCHASE`.

Forbidden:
- implementation changes;
- new billing behavior;
- rerunning implementation unit/integration suites merely to revalidate accepted SHARED-005;
- consumer repository edits.

Validation is publication mechanics only.

## Luna execution rules

- Treat this file as the complete execution contract. Do not redesign the feature.
- Do not broaden scope into adjacent billing/conversation work.
- Before editing, inspect the exact named current files and repository `package.json`.
- Use only repository scripts that actually exist.
- Do not modify another repository unless this task explicitly authorises a dependency pointer/version update.
- Do not start a task listed under `enables`.
- Return only this task to `review` and STOP.
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-SHARED-006` branch and the mirrored parent-workspace `task/ARCH-007-SHARED-006` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.

## Completion Report

### Status
Ready for Review (Attempt 1)

### Files Changed
- `moda-interact-shared/package.json`
- `moda-interact-shared/package-lock.json`
- Published package artifact `@modainteract/moda-interact-shared@0.8.0`

### Work Completed
- Set the Shared package version from `0.7.4` to the exact required publication version `0.8.0`.
- Published the architect-accepted SHARED-005 contract to the public npm registry with the `latest` tag.
- After architect review identified stale root package version metadata in `package-lock.json`, the developer reconciled both lockfile root version declarations to `0.8.0`. No republish was performed.

### Validation Results
- `npm publish --access public --registry=https://registry.npmjs.org`: passed; published `@modainteract/moda-interact-shared@0.8.0`.
- `npm view @modainteract/moda-interact-shared version`: passed; registry reports `0.8.0`.
- `npm view @modainteract/moda-interact-shared dist-tags`: passed; `latest` reports `0.8.0`.
- Published tarball inspection: passed; `dist/billing.d.ts` contains and exports `RECOVERY_CREDIT_PACK_PURCHASE`.
- Published runtime export check: passed; extracted `dist/billing.js` exports the complete canonical metric list including `RECOVERY_CREDIT_PACK_PURCHASE`.
- `git diff --check`: passed.
- Initial tarball fetch briefly returned npm `ETARGET` before registry propagation; retry succeeded.
- The first isolated runtime import lacked package dependencies; retry with the repository's installed dependencies succeeded. No implementation test suites were rerun, per task scope.

### Deviations
None.

### Assumptions
- The already architect-accepted SHARED-005 source and generated package artifact were the publication input; no implementation changes were introduced for SHARED-006.

### Unresolved Issues
None. The local package/lock publication-version mismatch identified during architect review was corrected by the developer without creating a new task attempt or republishing the package.

### Architectural Concerns
None.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 is architect-accepted Complete.

The npm publication itself was already successful and valid:

- `@modainteract/moda-interact-shared@0.8.0` was published successfully;
- registry `version` is `0.8.0`;
- registry `latest` points to `0.8.0`;
- the published declaration contains `RECOVERY_CREDIT_PACK_PURCHASE`;
- the published runtime billing export contains the accepted canonical metric tuple;
- no SHARED-005 implementation behavior was changed by the publication task.

The only issue identified in the first architect review was local repository publication metadata:

```text
package.json                 = 0.8.0
package-lock.json root       = 0.7.4
package-lock packages[""]    = 0.7.4
```

The developer subsequently corrected the two `package-lock.json` root package-version declarations to `0.8.0`.

This is accepted as a developer-side metadata correction within the existing Attempt 1 handoff. A separate Attempt 2 was not necessary because:

1. the package had already been correctly published as `0.8.0`;
2. the defect was local root-package version metadata only;
3. no dependency graph or Shared implementation redesign was required;
4. republishing `0.8.0` would have been incorrect and unnecessary.

No additional npm publication is required.

### Reviewed Evidence

- `moda-interact-shared/package.json` publication version from the submitted review bundle;
- `moda-interact-shared/package-lock.json` mismatch identified during the first architect review;
- npm publication confirmation showing successful publication of `@modainteract/moda-interact-shared@0.8.0`;
- repository-agent registry/declaration/runtime publication checks;
- developer confirmation that the lockfile root package versions were reconciled to `0.8.0`.

A fresh post-correction Shared archive was not supplied for this acceptance overlay, so the final local lockfile correction is recorded on developer confirmation rather than a second independent archive inspection. This does not affect the already independently evidenced npm publication.

### Architecture Conformance

Accepted.

### Current Shared Release

The current architect-accepted and published Shared release is now:

```text
@modainteract/moda-interact-shared@0.8.0
```

This release contains the accepted `RECOVERY_CREDIT_PACK_PURCHASE` billing metric.

### Follow-up

`ARCH-007-SHARED-006` is Complete.

Immediate downstream consequence:

`ARCH-007-BACKGROUND-009` is now Ready because all of its dependencies are Complete:

```text
ARCH-007-DATABASE-005 Complete
ARCH-007-SHARED-006 Complete
ARCH-007-BACKGROUND-007 Complete
```

`ARCH-007-ADMIN-005` remains Pending because `ARCH-007-ADMIN-001` is not yet Complete.

`ARCH-007-SHOPIFY-004` remains Pending because `ARCH-007-ADMIN-005` is not yet Complete.

No system-test task is automatically started.
