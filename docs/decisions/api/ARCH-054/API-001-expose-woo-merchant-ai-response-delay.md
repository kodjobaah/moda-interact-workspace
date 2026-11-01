---
id: ARCH-054-API-001
architecture_id: ARCH-054
title: Expose merchant AI reply delay via authenticated Woo API
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 30
executor: copilot
claimed_at: 2026-10-31T22:40:01Z
attempt: 3
depends_on:
  - ARCH-054-DATABASE-001
  - ARCH-054-SHARED-002
enables:
  - ARCH-054-WOOCOMMERCE-001
created: 2026-10-31
updated: 2026-11-01
---


# ARCH-054-API-001: Expose merchant AI reply delay via authenticated Woo API


## Architecture

Architecture: `ARCH-054`

Document: `docs/architecture/ARCH-054-merchant-configurable-ai-response-delay.md`

Coordinator: `moda_architect`. Attempt 1 was blocked by the database schema dependency; the updated database submodule now resolves that blocker. The task is Ready for attempt 2.


## Objective

Add standalone v1 Woo installation-authenticated GET/PUT for the shared shop AI-delay configuration, without changing recovery-delay policy or conversation commands.


## Context

ARCH-054 adds a **merchant-selectable integer 0–30 minute AI reply delay** to the existing ARCH-040 recovery-conversation processor and handover controls, leaving merchant-authored HUMAN replies without configured delay. See the parent architecture and current snapshot for specific boundaries.


## Scope

Create `src/merchant/ai-response-delay/contract.ts`, `service.ts`, `routes.ts`, `request.ts`; register in `src/composition/merchant.ts`. Update `moda-interact-api/package.json` and `package-lock.json` to the exact architect-accepted version published by ARCH-054-SHARED-002; do not import sibling Shared source. Add `tests/unit/merchant/ai-response-delay/settings.test.ts` and `scripts/test-arch054-ai-response-delay-postgres.mjs`. Reuse current WooInstallationAuthenticator and no-store JSON response helpers. Do not modify `src/merchant/recovery-policy/*` behavior.


## Out of Scope

No unrelated architecture changes, new standalone chat service, per-user timer jobs, invented provider error explanations, or updates to `docs/decisions/**/_index.md`. No implementation outside the assigned repository.


## Requirements

- Route exactly `GET/PUT /v1/merchant/ai-response-delay`, request/response JSON use published `MerchantAiResponseDelayWriteV1Schema`/`ReadV1Schema` from `@modainteract/moda-interact-shared/ai-response-delay`; no local structurally copied Zod. GET has no request body; PUT body <= 2048 bytes, `application/json`, strict keys. Both require authenticated ACTIVE verified Woo installation bound to current canonical site URL and active Shop; no browser-provided shop ID, no query override.
- GET returns `{schemaVersion:1,revision,aiResponseDelayMinutes}` from `ShopSettings`, with default 0/revision `UNCONFIGURED` only if authenticated shop has no settings row; `Cache-Control: no-store`.
- PUT requires `expectedRevision` equality and 0..30 integer, locks shop row, confirms installation state inside transaction and updates ONLY `aiResponseDelayMinutes` and monotonically `updatedAt` in existing ShopSettings; on first row create set safe established defaults and correct `shopId`. Return same read DTO/new revision. Idempotent identical value must not mutate or bump revision. Conflict 409 with stable `ai_response_delay_conflict` code; malformed 400; unauthorized 401/403; unauthenticated response must not disclose settings. Do not alter pending turn timestamps or admin overrides. Support original cause logging with sensitive redaction on error.


## Work Items

- [x] Implement read/update service, strict request/response and route composition.
- [x] Add tests for 0,7,30, bad -1/31/float/string/extra fields, conflict/retry, same-value no-op, revocation while updating, cross-tenant tampering, concurrent writes and recovery-policy unaffected.


## Interfaces / Contracts

Canonical Shared v1 examples (request) `{ "schemaVersion":1, "expectedRevision":"UNCONFIGURED", "aiResponseDelayMinutes":7 }`; (response) `{ "schemaVersion":1, "revision":"2026-10-31T16:28:55.123Z", "aiResponseDelayMinutes":7 }`. Owner Shared-001/002; consumers API and Woo PHP.


## Dependencies

- ARCH-054-DATABASE-001
- ARCH-054-SHARED-002


## Enables

- ARCH-054-WOOCOMMERCE-001


## Acceptance Criteria

- [x] Only authenticated same-tenant Woo read/write succeeds; no Shop ID from browser; revision and changed value consistent. Hosted API consumes exactly the published Shared package version and records it in the lockfile.
- [x] No modification to recovery-delay values, follow-up or human-send path; all failures return deterministic statuses and do not mutate settings.


## Validation

- [x] `npx tsx --test tests/unit/merchant/ai-response-delay/settings.test.ts`; `node scripts/test-arch054-ai-response-delay-postgres.mjs`; `npm run lint` (coordinator-approved exception for one unrelated pre-existing `no-empty` at `src/merchant/support/routes.ts:75`); `npm run typecheck`; `npm run build`; `git diff --check`.


## Stop Condition

After all required Work Items, Acceptance Criteria and Validation are complete, update Completion Report, set status to `review`, return control to `moda_architect` and **STOP**. Do not implement dependent tasks. Publication tasks do not rerun accepted implementation validation.


## Implementation Notes

Implement only the identified repository-owned changes; preserve original provider/SDK errors in shared structured logs and rethrow failures to the owning retry/admission boundary.


## Completion Report

### Status

Ready for Architect review. Attempt 3 implementation criteria and all task-specific validations are complete. Full `npm run lint` still fails on the unrelated existing empty catch in `src/merchant/support/routes.ts:75`; that out-of-scope file is unchanged. The coordinator authorized a task-scoped exception to this lint gate so API-001 can proceed to review. This exception is not implementation acceptance.

### Files Changed

Added `src/merchant/ai-response-delay/contract.ts`, `request.ts`, `service.ts`, and `routes.ts`; registered the routes in `src/composition/merchant.ts`; pinned `@modainteract/moda-interact-shared` to `3.1.0` in `package.json` and `package-lock.json`; added `tests/unit/merchant/ai-response-delay/settings.test.ts`, `tests/integration/merchant/ai-response-delay/service.postgres.test.ts`, and `scripts/test-arch054-ai-response-delay-postgres.mjs`.

### Work Completed

Implemented the standalone authenticated GET/PUT route using the published Shared v1 schemas, strict 2048-byte JSON request parsing, no-store responses, transaction-time active Shop/installation validation, Shop-row locking, optimistic revision conflict handling, monotonic timestamps, idempotent same-value updates, and settings-row defaults. Added mock-backed route/service tests and disposable PostgreSQL concurrency/tenant/revocation/recovery-policy coverage. No recovery-policy implementation files or conversation timestamps were changed.

### Validation Results

`npx tsx --test tests/unit/merchant/ai-response-delay/settings.test.ts`: PASS, 5 tests.
`npx eslint` on changed TypeScript source and tests: PASS.
`git diff --check`: PASS.
Shared package metadata and installed dependency: PASS, exact `3.1.0`; npm package export `./ai-response-delay` is present.
`node scripts/test-arch054-ai-response-delay-postgres.mjs`: BLOCKED. The runner successfully started disposable PostgreSQL and deployed the API submodule's migrations, then Prisma rejected `aiResponseDelayMinutes` because the pinned database schema/client does not define the field.
`npm run typecheck` and `npm run build`: BLOCKED by the same missing Prisma field (`TS2339`/`TS2353`).
`npm run lint`: FAILS on existing unrelated `src/merchant/support/routes.ts:75` empty catch block; changed TypeScript files pass targeted ESLint.

### Attempt 2 Validation Results

`npx tsx --test tests/unit/merchant/ai-response-delay/settings.test.ts`: PASS, 5 tests.
`node scripts/test-arch054-ai-response-delay-postgres.mjs`: PASS. Prisma Client generation succeeded; all 68 migrations deployed, including `20261031170000_arch054_merchant_ai_response_delay`; PostgreSQL integration passed tenant isolation, defaults, same-value no-op, compare-and-set race, and revocation checks.
`npm run lint`: FAIL, one unrelated existing error at `src/merchant/support/routes.ts:75` (`no-empty`); no task-owned source change caused the failure, and the unrelated file was not modified. `moda_architect` authorized a task-scoped exception for API-001 review; the support route was not changed.
`npm run typecheck`: PASS; Prisma Client generation and TypeScript check succeeded.
`npm run build`: PASS; Prisma Client generation and production TypeScript build succeeded.
`git diff --check`: PASS.

### Attempt 2 Launcher and Git Evidence

Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-054-API-001`, branch `task/ARCH-054-API-001`; prepared parent head `6205d3baac470daa067150c36a18e1ade0b3e332`; Attempt 2 claim commit `07396377d2763a6012d31f5cec20c6ffb57ed9e2` was pushed by the launcher.
Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-054-API-001`, branch `task/ARCH-054-API-001`, implementation head `3cb67ea009ce00d0280d8ec7690a14a63222b2b9` (`already-current`).
Launcher synchronization evidence: parent `origin/main` incorporated `yes`; implementation `origin/main` incorporation `already-current`; recursive submodule initialization/readiness passed; database submodule pinned at `7c377282aa5819b3008b7d7f3018f44f4161523e`.
Both worktrees were clean before validation. No API source changes or implementation submodule gitlink changes were made during Attempt 2. The parent task report is the only changed file in this attempt.

### Attempt 2 Deviation / Assumptions / Unresolved Issues / Architectural Concerns

The previous missing-Prisma-field blocker is resolved: the pinned database submodule includes `ShopSettings.aiResponseDelayMinutes Int @default(0)` and migration `20261031170000_arch054_merchant_ai_response_delay`. PostgreSQL integration, typecheck, build, and diff validation pass. Full-repository lint still reports the existing unrelated `no-empty` error at `src/merchant/support/routes.ts:75`; the file remains unchanged. `moda_architect` authorized a task-scoped exception to the lint gate for review. This exception does not accept the implementation or change the lint result.

### Attempt 3 Summary

Addressed the Architect Review correction by comparing `expectedRevision` before the identical-value no-op. A same-value PUT with the current revision succeeds without writing; a stale same-value PUT returns HTTP 409 with `ai_response_delay_conflict` and does not write. The task remains scoped to the existing API implementation; no recovery-policy behavior or other repository-owned files were changed.

### Attempt 3 Files Changed

Implementation commit `50ddbb0a93e6a5650456054b2c693aa7fd3fded8` changes `src/merchant/ai-response-delay/service.ts`, `tests/unit/merchant/ai-response-delay/settings.test.ts`, and `tests/integration/merchant/ai-response-delay/service.postgres.test.ts`. The parent conflict-merge commit `dba4297a8bd5113f378c24059afce5f258dd30e7` remains in parent task-branch history.

### Attempt 3 Tests and Validation Results

`npx tsx --test tests/unit/merchant/ai-response-delay/settings.test.ts`: PASS, 6 tests. The added regression `same-value PUT succeeds only with the current revision and never writes` verifies current-revision HTTP 200/no write and stale-revision HTTP 409 `{ error: "ai_response_delay_conflict" }`/no write. The service test `current-revision same-value retries do not write; stale different values conflict` also passes.
`node scripts/test-arch054-ai-response-delay-postgres.mjs`: PASS, 1 PostgreSQL integration test; all 68 migrations applied, including ARCH-054. The integration covers tenant isolation, defaults, same-value no-op, compare-and-set race, and revocation; its current-revision no-op uses the returned revision.
`npm run typecheck`: PASS.
`npm run build`: PASS.
`npx eslint src/merchant/ai-response-delay/service.ts tests/unit/merchant/ai-response-delay/settings.test.ts tests/integration/merchant/ai-response-delay/service.postgres.test.ts`: PASS.
`git diff 50ddbb0a93e6a5650456054b2c693aa7fd3fded8^ 50ddbb0a93e6a5650456054b2c693aa7fd3fded8 --check`: PASS.
`npm run lint`: FAILS only on the existing unrelated `no-empty` at `src/merchant/support/routes.ts:75`. That file is unchanged, and the coordinator-approved task-scoped exception recorded above applies; targeted ESLint on all changed implementation/test files passes.

### Attempt 3 Deviations / Assumptions / Unresolved Issues / Architectural Concerns

No implementation deviations or unresolved task requirements. The known full-lint exception remains the only validation limitation; all other required focused validations passed. The task is submitted for Architect review and is not marked Complete.

### Attempt 1 Deviation / Assumptions / Unresolved Issues / Architectural Concerns

Attempt 1 was blocked because its initial `database` submodule pin was `b87e460e86de2044477f8c96b5c1c42e722de8f0`, which lacked the ARCH-054 field and migration. Architect verification on 2026-10-31 confirmed that the API task worktree would pin and check out database commit `7c377282aa5819b3008b7d7f3018f44f4161523e`; that commit contains `ShopSettings.aiResponseDelayMinutes Int @default(0)` and migration `20261031170000_arch054_merchant_ai_response_delay/migration.sql`, which adds the column and range check. The gitlink matches the clean database checkout. At the end of Attempt 1, the dependency blocker was considered resolved and Attempt 2 was requested to rerun PostgreSQL integration, typecheck, build, and remaining validation; that historical status did not accept the implementation.

### Worktree and Git Evidence

Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-054-API-001`, branch `task/ARCH-054-API-001`, prepared claim commit `f19b8a81a127af94afdc13cd4b4f6b09033b78a6`.
Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-054-API-001`, branch `task/ARCH-054-API-001`, prepared base commit `e59aba1939531e250b7cefc3c1c3e21b13cda3af`.
Launcher start synchronization: remote task-branch fast-forward `not-needed`; `origin/main` incorporation `already-current` in both worktrees. Recursive submodule sync/update passed; database submodule pinned at `b87e460e86de2044477f8c96b5c1c42e722de8f0`.
Shared workspace and source checkouts were not switched or mutated; no other task worktree was reused. No implementation submodule gitlink was staged.


## Architect Review

### Review Status

Changes Requested

### Review Notes

The authenticated tenant checks, Shared v1 schemas, transaction-time installation recheck, shop lock, monotonic revision, safe first-row defaults, and limited update fields conform to the task. One optimistic-concurrency requirement is not met: `MerchantAiResponseDelayService.update` returns successfully for an unchanged value before comparing `expectedRevision`. The task requires revision equality; a stale same-value request must not bypass that precondition.

### Reviewed Files

- `src/merchant/ai-response-delay/contract.ts`
- `src/merchant/ai-response-delay/request.ts`
- `src/merchant/ai-response-delay/service.ts`
- `src/merchant/ai-response-delay/routes.ts`
- `src/composition/merchant.ts`
- `tests/unit/merchant/ai-response-delay/settings.test.ts`
- `tests/integration/merchant/ai-response-delay/service.postgres.test.ts`
- `scripts/test-arch054-ai-response-delay-postgres.mjs`
- `package.json`, `package-lock.json`, and the pinned database submodule

### Validation Reviewed

Reviewed the reported 5 passing focused unit tests, PostgreSQL integration, targeted ESLint, typecheck, build, and diff check. Full-repository lint still reports the unrelated pre-existing `no-empty` at `src/merchant/support/routes.ts:75`; the task-scoped exception is recorded. No validation was rerun during this review.

### Architecture Conformance

Changes requested for the stale-revision behavior. The rest of the reviewed API boundary and persistence behavior conforms to the task and published Shared contract.

### Follow-up

Keep this task at Attempt 2 and return it to Ready. Check `expectedRevision` before the same-value no-op path. Add a regression proving a same-value request with the current revision succeeds without writing, while a same-value request with a stale revision returns `409 ai_response_delay_conflict` and does not write. `ARCH-054-WOOCOMMERCE-001` remains Pending until API-001 is accepted and Complete.
