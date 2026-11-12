---
id: ARCH-069-BACKGROUND-001
architecture_id: ARCH-069
title: Adopt chronological model serialization
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 10
executor: codex
claimed_at: 2026-11-12T11:22:30Z
attempt: 1
depends_on:
  - ARCH-069-SHARED-002
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Adopt chronological model serialization

## Architecture

ARCH-069 — `docs/architecture/ARCH-069-chronological-commerce-model-inputs.md`; coordinator moda_architect.

## Objective

Consume the published chronological Shared model adapter in Background without changing delivery or turn lifecycle contracts.

## Context

Production's snowboard turn returned an internal-looking indicator. The model serializer independently places current context before prior history. This task addresses only its bounded owning outcome; the exact indicator cause requires evidence and must not be asserted merely from a passing structural test.

## Scope

Repository: `moda-interact-background`.

- Pin the approved published Shared 5.13.2 package and matching lockfile integrity.
- Add or adjust a focused consumer regression proving older history precedes the current snowboard question at the actual model boundary.
- Preserve admission, STOP/consent, tenant ownership, existing message/usage idempotency and delivery behavior.
- Support coordinator-owned read-only/no-send reproduction and record how production verification will be performed; do not send or replay production messages as an implementation test.

## Out of Scope

Moderation/STOP changes, sentinel blocklists, provider/model switching, schema or queue changes, credential edits, production message replay, unrelated dependency changes and another repository's implementation.

## Requirements

- Verify actual public-registry download/install of5.13.2 and matching SHA512 lock integrity before merge/deployment; local accepted-tarball or cache-only installation does not prove registry availability.

- Pin the approved published Shared 5.13.2 package and matching lockfile integrity.
- Add or adjust a focused consumer regression proving older history precedes the current snowboard question at the actual model boundary.
- Preserve admission, STOP/consent, tenant ownership, existing message/usage idempotency and delivery behavior.
- Support coordinator-owned read-only/no-send reproduction and record how production verification will be performed; do not send or replay production messages as an implementation test.

## Work Items

- [x] Verify actual public-registry download/install of5.13.2 and matching SHA512 lock integrity before merge/deployment; local accepted-tarball or cache-only installation does not prove registry availability.

- [x] Pin the approved published Shared 5.13.2 package and matching lockfile integrity.
- [x] Add or adjust a focused consumer regression proving older history precedes the current snowboard question at the actual model boundary.
- [x] Preserve admission, STOP/consent, tenant ownership, existing message/usage idempotency and delivery behavior.
- [x] Support coordinator-owned read-only/no-send reproduction and record how production verification will be performed; do not send or replay production messages as an implementation test.

## Interfaces / Contracts

Existing Shared ModelRequest/ModelStep and `@modainteract/moda-interact-shared/commerce/model/node`; no wire schema changes. Background remains host/lifecycle owner. Shared implementation owner: ARCH-069-SHARED-001.

## Dependencies

- ARCH-069-SHARED-002

## Enables

None

## Acceptance Criteria

- [x] Verify actual public-registry download/install of5.13.2 and matching SHA512 lock integrity before merge/deployment; local accepted-tarball or cache-only installation does not prove registry availability.

- [x] Pin the approved published Shared 5.13.2 package and matching lockfile integrity.
- [x] Add or adjust a focused consumer regression proving older history precedes the current snowboard question at the actual model boundary.
- [x] Preserve admission, STOP/consent, tenant ownership, existing message/usage idempotency and delivery behavior.
- [x] Support coordinator-owned read-only/no-send reproduction and record how production verification will be performed; do not send or replay production messages as an implementation test.

## Validation

- [x] Verify actual public-registry download/install of5.13.2 and matching SHA512 lock integrity before merge/deployment; local accepted-tarball or cache-only installation does not prove registry availability.

- [x] Inspect package scripts and run the relevant model/host/turn integration unit checks.
- [x] Run Background typecheck, changed-file lint and required full CI suite.
- [x] Use disposable PostgreSQL/Redis only if the scoped regression requires persistence; never inherited live DATABASE_URL/REDIS_URL.
- [x] Confirm dependency resolves from the published registry artifact and no sibling source imports are introduced.

## Stop Condition

After the scoped work, acceptance criteria and required validation pass, complete this task's report, set review, publish both mirrored task branches, return to moda_architect and STOP. Do not begin dependent work, merge main or send a production message.

## Implementation Notes

Use launcher-resolved physical parent and implementation task worktrees for the entire attempt. Preserve unrelated changes. All no-send/live diagnostic artifacts must be protected and excluded from Git; no credentials or private customer prompt payloads in reports. Publication task validation is release mechanics only.

## Completion Report

### Status

Ready for Review. Implementation and task report are published on matching `task/ARCH-069-BACKGROUND-001` branches. No merge or architect acceptance is claimed by this agent.

### Files Changed

- `package.json`, `package-lock.json`: exact published Shared `5.13.2` pin, canonical public registry URL and accepted integrity; no other dependency changes.
- `tests/unit/commerce/published-model-chronology.test.ts`: installed-public-export regression at the actual SDK message boundary. Covers both supported history shapes, the current snowboard question after older assistant history, and current-turn tool observations afterward. SDK constructor interception and a network hard-block prevent provider calls.
- `tests/unit/runtime/observability-startup.test.ts`, `tests/unit/services/checkout-recovery/recovery-initial-outreach-support-notice.service.test.ts`, `tests/unit/services/checkout-recovery/recovery-outreach-finalization-notice.test.ts`: existing exact installed-release assertions updated.
- `scripts/run-arch024-production-model-disposable.mjs`: stale disposable raw-keyring fixture now uses the existing published `parseCredentialKeyring` API. Production code is unchanged.

### Work Completed

- Verified an actual HTTP 200 download from the canonical public tarball URL, not only registry metadata or a local publication artifact.
- Verified the downloaded bytes match SHA1 `fb876e81e539a6fe8a3521072b7c8d870c52a389` and integrity `sha512-PhKt+u0nhptXAVwcx6j7Lf0Sx7/pMbVQ8gxZMo0xCKA/DGTwJjGChTzHupkJcni4Qm9y0qFBhGgFsKQOUnEDNA==`.
- Performed `npm ci --ignore-scripts --legacy-peer-deps --no-audit --no-fund --prefer-online` using a new task-specific npm cache: 609 packages installed successfully. Installed package version and lock integrity were checked again afterward.
- Preserved delivery, moderation/STOP, consent, tenant ownership, usage/message idempotency, grants, queue contracts and database schema. No production runtime source changes were needed.
- Supported coordinator-owned protected no-send reconstruction of the 10:38 turn. The capture exercised the actual host/history/runner with a read-only SQL transaction, rejected writes, intercepted the first model request and blocked model/MCP/Meta calls. Protected prompt artifacts remain outside Git. The exact indicator was absent from that captured request.
- Coordinator reports the paired anonymized provider probe improved current-turn intent with chronological ordering. This does not establish deterministic causality for the exact earlier indicator.

### Validation Results

- Public registry artifact download, accepted SHA1/SHA512 verification, clean-cache install and installed package/lock checks: passed.
- Ten focused model/model-resolution/host/MCP/turn/worker/export files: 179 unique tests passed. The existing observability subprocess test exceeded its five-second timeout during parallel contention; its isolated single-worker rerun passed all ten tests without changing its timeout or behavior.
- New installed-package SDK boundary regressions: all three passed; provider networking remained blocked and tools, output-token limits and active cancellation signal were preserved.
- Prisma client generation: passed with the recorded database submodule; no database access or schema changes.
- `tsc --noEmit`, changed-file ESLint and `git diff --check`: passed.
- `scripts/run-arch024-production-model-disposable.mjs`: passed against its own disposable local PostgreSQL instance after the test-only keyring fixture repair. All migrations applied; model selection, pending-plan behavior, Shop isolation, encrypted credential rotation and model identity stability were verified. Its container/network were cleaned up. Inherited live database/Redis endpoints were never used.
- Final-head full GitHub CI: both runs passed. Run `43210152386` completed in 2m23s; run `43210195098` completed in 2m36s. Final totals: 367 files and 3,941 tests passed.
- CI: https://github.com/kodjobaah/moda-interact-background/actions/runs/43210152386 and https://github.com/kodjobaah/moda-interact-background/actions/runs/43210195098.
- Implementation commit: `6ccad024eb69aceb20406d0d0f40eb05f0c29a7f`; PR: https://github.com/kodjobaah/moda-interact-background/pull/199.

### Physical Worktree Isolation and Launcher Evidence

- Canonical primary workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-069-BACKGROUND-001`, branch `task/ARCH-069-BACKGROUND-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-069-BACKGROUND-001`, branch `task/ARCH-069-BACKGROUND-001`.
- Shared workspace or implementation checkout switched/mutated for task work: no. Another task worktree reused: no.
- Launcher start-of-attempt synchronization: parent remote task branch fast-forward not needed; parent origin/main already current; implementation remote task branch fast-forward not needed; implementation origin/main already current.
- Recursive submodule sync/update: launcher passed both; recorded `database` commit `5329d5390d346042895219663f3a040ea54ae168` initialized correctly.
- Durable launcher claim: `aafa37366e0b33b8f0b7a4c5c26adba102df4656`, attempt 1, executor codex. Prepared claim/preparation was not duplicated.

### Deviations

The existing disposable production-model proof used a pre-keyring-API raw map and initially failed with `hasKey is not a function`. Its test fixture was repaired using the published parser so the requested validation could run. No credential resolver or other runtime implementation was changed.

### Assumptions

The existing request schemas, pinned release and turn/delivery contracts remain authoritative. Registry-installed Shared 5.13.2 is the sole model serialization implementation; no sibling source imports were introduced.

### Unresolved Issues

Actual customer-facing production answer verification remains coordinator-owned after review, integration and deployment. Verify a fresh genuine customer question through production ingress/moderation/model tool use and delivered answer; do not replay or reopen an already-processed inbound turn. Exact causality for the earlier indicator is not claimed by this task.

### Architectural Concerns

None beyond the bounded ordering defect. No schema, queue, infrastructure, provider/model selection or credential changes were introduced.

## Architect Review

### Review Status

Pending

### Review Notes

Not reviewed

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
