---
id: ARCH-007-SHARED-002
architecture_id: ARCH-007
title: Publish the accepted ARCH-007 billing contract release
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: complete
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on: 
  - ARCH-007-SHARED-001
enables: 
  - ARCH-007-SHOPIFY-001
  - ARCH-007-MESSAGING-001
  - ARCH-007-BACKGROUND-001
  - ARCH-007-BACKGROUND-006
  - ARCH-007-ADMIN-001
created: 2026-09-07
updated: 2026-09-07T21:28:00+01:00
---

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

# ARCH-007-SHARED-002: Publish the accepted ARCH-007 billing contract release

## Architecture

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Publish exactly the architect-accepted SHARED-001 billing contract package version and prove a clean consumer can import the new public exports.

## Context

This is a publication gate. Consumer agents should not implement local substitutes while waiting for Shared publication.

## Scope

Package version/lock metadata, npm publication, registry verification and isolated exact-version consumer import/schema/helper verification only.

## Out of Scope

- Changing SHARED-001 implementation.
- Updating any consumer repository dependency.
- Starting SHOPIFY/MESSAGING/BACKGROUND/ADMIN work.

## Requirements

- Confirm SHARED-001 is architect-accepted Complete before publication.
- Publish the next repository-approved package version without changing accepted runtime source.
- Verify registry metadata and install the exact published version into an isolated clean consumer.
- Import the billing/provider-status exports and execute one valid/invalid schema parse plus deterministic key check.
- Record exact published version in Completion Report.

## Work Items

- [ ] Claim publication task.
- [ ] Bump only publication metadata as required.
- [ ] Publish using repository convention.
- [ ] Run clean-consumer exact-version verification.
- [ ] Return task to review and STOP.

## Interfaces / Contracts

Published contract is the only authorized consumer source:

`@modainteract/moda-interact-shared@<published-version>`

## Dependencies

Explicit task dependencies are authoritative in YAML frontmatter. Do not begin unless every listed dependency is architect-accepted `complete` and any accepted Shared/database artifact required by this repository is available to consume.

## Enables

- ARCH-007-SHOPIFY-001
- ARCH-007-MESSAGING-001
- ARCH-007-BACKGROUND-001
- ARCH-007-BACKGROUND-006
- ARCH-007-ADMIN-001

## Acceptance Criteria

- [ ] Published package contains exactly the accepted SHARED-001 behavior.
- [ ] Clean consumer can import all new public billing/provider-status exports.
- [ ] No consumer repository was modified.
- [ ] No implementation validation already accepted in SHARED-001 is needlessly rerun beyond publication verification.

## Validation

Run only publication/release validation required by this task: package/registry metadata, exact-version clean install/import/runtime smoke and `git diff --check`. Do not rerun the full SHARED-001 implementation suite.

## Implementation Notes

Publication-only hard stop. Do not commit/push unless the developer explicitly authorizes VCS publication for this specific task; if registry publication itself is not authorized/possible in the execution environment, report the exact blocker rather than altering consumer repositories.
Luna deterministic-execution guardrails:

- Treat this task file as the complete implementation contract. Do not infer additional product policy from old billing code.
- Inspect the named current implementation before editing, but if old code conflicts with ARCH-007, implement ARCH-007.
- Do not start an enabled/dependent task. Return only this task to `review` and STOP.
- Do not modify another repository except an explicitly permitted database submodule/package dependency pointer in this task.
- Do not add new billing raw SQL (`$queryRaw`, `$executeRaw`, `Prisma.sql`, raw driver SQL) to compensate for an unavailable Prisma delegate. Adopt/regenerate the accepted Prisma schema instead.
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-SHARED-002` branch and the mirrored parent-workspace `task/ARCH-007-SHARED-002` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.


## Completion Report

### Status

Ready for Review

### Files Changed

`package.json` (version `0.7.2` -> `0.7.3`) and this task record.

### Work Completed

- Published `@modainteract/moda-interact-shared@0.7.3` to the public npm registry.
- Preserved the architect-accepted SHARED-001 runtime source; no consumer repository was modified.
- Published package includes the billing entrypoint and accepted provider-status/key behavior.

### Validation Results

- Registry metadata confirmed version `0.7.3`, tarball URL, and integrity `sha512-g02RIvud6d4gQd++paXR+KvKpcWsc1t4dao3ggTGiEpXO8DaDOtz56Es/73Z58PKU5AoblXd75ADbuHSD9zZxA==`.
- Clean temporary consumer installed exact `@modainteract/moda-interact-shared@0.7.3`.
- Consumer imported `@modainteract/moda-interact-shared/billing` successfully.
- Valid normalized provider status parsed successfully; invalid `QUEUED` status was rejected.
- Lifecycle billing source key was deterministic and bounded to the required limit.
- `git diff --check` passed.

### Deviations

None

### Assumptions

The next repository-approved patch release after registry version `0.7.2` is `0.7.3`.

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None

### Attempt 1 Architect Review

**Changes Requested — publication succeeded, but repository publication metadata is inconsistent.**

The submitted workspace and the merchant-supplied npm publication confirmation
were reviewed directly.

Accepted evidence from Attempt 1:

- `@modainteract/moda-interact-shared@0.7.3` was successfully published;
- `package.json` is version `0.7.3`;
- the submitted `src/billing.ts`, `src/billing.test.ts`, `src/index.ts`, and
  `tsup.config.ts` are byte-for-byte identical to the architect-accepted
  SHARED-001 source;
- the Completion Report records successful exact-version clean-consumer import
  and runtime smoke validation.

One original-scope publication defect remains:

- `package-lock.json` still declares version `0.7.2` at both:
  - top-level `version`;
  - `packages[""].version`.

SHARED-002 Scope explicitly owns **package version/lock metadata**, so the
repository must not finish the publication task with `package.json` and
`package-lock.json` describing different package versions.

### Attempt 2 Required Changes

Reclaim this same task as Attempt 2 and perform ONLY this metadata correction.

1. Synchronize `package-lock.json` to the already-published package version
   `0.7.3`. A repository-local command such as:

   `npm version 0.7.3 --no-git-tag-version --allow-same-version`

   is acceptable if it changes only the expected package/lock publication
   metadata. Do not manually rewrite unrelated lockfile dependency metadata.

2. Verify all of the following:
   - `package.json.version === "0.7.3"`;
   - `package-lock.json.version === "0.7.3"`;
   - `package-lock.json.packages[""].version === "0.7.3"`;
   - no architect-accepted SHARED-001 runtime source changed;
   - `git diff --check` passes.

3. **Do NOT run `npm publish` again.**
   Version `0.7.3` is already published and immutable.

4. **Do NOT bump to `0.7.4`.**
   This correction is repository metadata alignment for the already-published
   `0.7.3` release, not a new release.

5. Do not modify consumer repositories and do not start any enabled task.

6. Update the Completion Report with an explicit Architect Review checklist
   showing the lockfile correction and validation, return ONLY SHARED-002 to
   `review`, and STOP.

### Final Architect Review

**Accepted.**

The publication gate is architect-complete.

Accepted evidence:

1. The npm publication confirmation supplied by the developer confirms
   `@modainteract/moda-interact-shared@0.7.3` was successfully published.
2. Attempt 1 direct source review confirmed the published runtime source matched
   the architect-accepted SHARED-001 implementation and the clean exact-version
   consumer validation succeeded.
3. The only Changes Requested item was repository publication metadata:
   `package-lock.json` still identified the root package as `0.7.2`.
4. The developer applied the bounded metadata correction directly and supplied
   verification output confirming all three canonical version fields now agree:

   - `package.json.version === "0.7.3"`
   - `package-lock.json.version === "0.7.3"`
   - `package-lock.json.packages[""].version === "0.7.3"`

5. No republish and no `0.7.4` release is required. The immutable public artifact
   remains `@modainteract/moda-interact-shared@0.7.3`.

### Architecture Conformance — Final

Accepted. SHARED-002 is Complete and `0.7.3` is the exact ARCH-007 Shared release
that consumer tasks must adopt.

### Follow-up — Final

The following tasks now have all dependencies Complete and are Ready with
`attempt: 0`:

- `ARCH-007-SHOPIFY-001`
- `ARCH-007-MESSAGING-001`
- `ARCH-007-BACKGROUND-001`
- `ARCH-007-BACKGROUND-006`
- `ARCH-007-ADMIN-001`

All other ARCH-007 tasks remain dependency-gated. System-test tasks remain
terminal/manual-gated and do not block implementation work.
