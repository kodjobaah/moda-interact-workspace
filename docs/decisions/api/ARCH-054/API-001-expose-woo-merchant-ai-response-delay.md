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
status: in_progress
priority: 30
executor: copilot
claimed_at: 2026-10-31T22:03:08Z
attempt: 2
depends_on:
  - ARCH-054-DATABASE-001
  - ARCH-054-SHARED-002
enables:
  - ARCH-054-WOOCOMMERCE-001
created: 2026-10-31
updated: 2026-10-31
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

- [ ] Implement read/update service, strict request/response and route composition.
- [ ] Add tests for 0,7,30, bad -1/31/float/string/extra fields, conflict/retry, same-value no-op, revocation while updating, cross-tenant tampering, concurrent writes and recovery-policy unaffected.


## Interfaces / Contracts

Canonical Shared v1 examples (request) `{ "schemaVersion":1, "expectedRevision":"UNCONFIGURED", "aiResponseDelayMinutes":7 }`; (response) `{ "schemaVersion":1, "revision":"2026-10-31T16:28:55.123Z", "aiResponseDelayMinutes":7 }`. Owner Shared-001/002; consumers API and Woo PHP.


## Dependencies

- ARCH-054-DATABASE-001
- ARCH-054-SHARED-002


## Enables

- ARCH-054-WOOCOMMERCE-001


## Acceptance Criteria

- [ ] Only authenticated same-tenant Woo read/write succeeds; no Shop ID from browser; revision and changed value consistent. Hosted API consumes exactly the published Shared package version and records it in the lockfile.
- [ ] No modification to recovery-delay values, follow-up or human-send path; all failures return deterministic statuses and do not mutate settings.


## Validation

- [ ] `npx tsx --test tests/unit/merchant/ai-response-delay/settings.test.ts`; `node scripts/test-arch054-ai-response-delay-postgres.mjs`; `npm run lint`; `npm run typecheck`; `npm run build`; `git diff --check`.


## Stop Condition

After all required Work Items, Acceptance Criteria and Validation are complete, update Completion Report, set status to `review`, return control to `moda_architect` and **STOP**. Do not implement dependent tasks. Publication tasks do not rerun accepted implementation validation.


## Implementation Notes

Implement only the identified repository-owned changes; preserve original provider/SDK errors in shared structured logs and rethrow failures to the owning retry/admission boundary.


## Completion Report

### Status

Attempt 1 implementation and focused unit tests are complete. The database dependency blocker is resolved; the task is Ready for attempt 2 so the API owner can rerun PostgreSQL integration, typecheck, and build validation against the updated database submodule.

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

### Deviation / Assumptions / Unresolved Issues / Architectural Concerns

Attempt 1 was blocked because its initial `database` submodule pin was `b87e460e86de2044477f8c96b5c1c42e722de8f0`, which lacked the ARCH-054 field and migration. Architect verification on 2026-10-31 confirms that the API task worktree now pins and checks out database commit `7c377282aa5819b3008b7d7f3018f44f4161523e`; that commit contains `ShopSettings.aiResponseDelayMinutes Int @default(0)` and migration `20261031170000_arch054_merchant_ai_response_delay/migration.sql`, which adds the column and range check. The gitlink matches the clean database checkout. The previous dependency blocker is resolved. The API owner must claim attempt 2 through the launcher and rerun the PostgreSQL integration test, typecheck, build, and remaining task validation; this status transition does not accept the implementation.

### Worktree and Git Evidence

Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-054-API-001`, branch `task/ARCH-054-API-001`, prepared claim commit `f19b8a81a127af94afdc13cd4b4f6b09033b78a6`.
Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-054-API-001`, branch `task/ARCH-054-API-001`, prepared base commit `e59aba1939531e250b7cefc3c1c3e21b13cda3af`.
Launcher start synchronization: remote task-branch fast-forward `not-needed`; `origin/main` incorporation `already-current` in both worktrees. Recursive submodule sync/update passed; database submodule pinned at `b87e460e86de2044477f8c96b5c1c42e722de8f0`.
Shared workspace and source checkouts were not switched or mutated; no other task worktree was reused. No implementation submodule gitlink was staged.


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
