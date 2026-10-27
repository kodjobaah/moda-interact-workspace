---
id: ARCH-049-API-001
architecture_id: ARCH-049
title: Accept authenticated WooCommerce ShopBrand snapshots
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 30
executor: developer
claimed_at: 2026-10-27T12:46:54Z
attempt: 1
depends_on: ["ARCH-049-DATABASE-001"]
enables: ["ARCH-049-SYSTEM-TEST-001"]
created: 2026-10-25
updated: 2026-10-27
---

# Accept authenticated WooCommerce ShopBrand snapshots

## Architecture

`ARCH-049` — `docs/architecture/ARCH-049-shopbrand-public-media-configuration.md`; coordinator `moda_architect`. This task is materialised on its canonical parent task branch and prepared for developer Attempt 1.

## Objective

Add a tenant-authenticated hosted Moda API command to accept WooCommerce's WordPress-native site identity, save the current ShopBrand sources in `commerce.ShopBrand`, and trigger recoverable Background processing without exposing WordPress endpoints.

## Context

WooCommerce runs on merchant-owned infrastructure. The current Moda API has an installation authenticator, bounded request-body utilities and tenant-scoped transaction helpers. Reuse them; do not create a new token protocol.

## Scope

- Add `src/woocommerce/shop-brand/contract.ts`, `request.ts`, `service.ts`, `routes.ts` and focused tests.
- Register an authenticated `POST /v1/woocommerce/shop-brand` route using the canonical Woo installation authenticator.
- Validate bounded body, canonical source fields, timestamps and shop ownership, then persist original ShopBrand data and per-role media source generations using row-level locking.
- Return deterministic idempotent success only after PostgreSQL commit; leave media processing to Background.

## Out of Scope

- Calling merchant WordPress endpoints, fetching/decoding images, R2 uploads, JWT/installation auth redesign, queued events as sole durability, or any new Prisma media table.

## Requirements

### R1. Exact HTTP contract

`POST /v1/woocommerce/shop-brand`, `application/json`, maximum decoded body 16 KiB; installation credentials must authenticate **before** reading the body. Request does not contain and may not override `shopId`; resolve it from authenticated installation principal. Accept exact keys (nullable media fields explicitly null when absent):

```json
{
  "schemaVersion": "woo.shop-brand.v1",
  "eventId": "stable-event-identifier",
  "observedAt": "2026-10-25T12:00:00Z",
  "brandName": "Example Store",
  "logo": {"url":"https://store.example/wp-content/uploads/logo.png", "attachmentId":123, "altText":"Store logo", "width":1200, "height":400},
  "siteIcon": {"url":"https://store.example/wp-content/uploads/icon.png", "attachmentId":456, "altText":null, "width":512, "height":512},
  "coverImage": null
}
```

`brandName` is trimmed Unicode text (max 160 characters), nullable; attachment IDs are positive integers, `url` must be a bounded HTTPS URL (max 2048 chars) or null; pixel dimensions if supplied must be positive integers, metadata names bounded; invalid/missing field set is 400, oversized request 413, unauthorised 401, upstream/DB temporary failure 503. Reject arbitrary extra keys, duplicate headers, malformed encoding and untrusted caller shopId. `observedAt` is UTC ISO-8601; events more than 5 minutes in the future or older than last stored provider observation cannot overwrite current media fields. `eventId` is an opaque stable identifier for retry diagnostics; idempotency is based on canonical source snapshot and observedAt, not an additional events table.

### R2. Canonical mapping

`logo` -> `logoUrl`/alt/dimensions and LOGO role; `siteIcon` -> `squareLogoUrl`/alt and SQUARE_LOGO role; absent cover -> `coverImageUrl=null` and COVER_IMAGE MISSING. `shopId` is the authenticated principal. A successfully authenticated complete snapshot can clear old source roles; transient or malformed requests never do. Preserve `Shop.brand` identity across platform instances, and only allow active matched Woo installations.

### R3. Transaction/idempotency

In a short PostgreSQL transaction, upsert/lock `ShopBrand` by unique shopId, skip duplicate/older canonical snapshots, atomically update brand text/source URLs and affected role JSON generations without losing other roles. Return `200 {"status":"updated"|"unchanged"}` after commit. Do not perform network/R2/BullMQ calls in the transaction. Optional wake is non-authoritative; BG002 due scanner guarantees processing.

### R4. Failure/security

Authenticate using the existing Woo installation boundary, enforce tenant/platform/is-active status, redact image URLs and tokens in structured logs, use the existing no-store JSON response helper, and avoid leaking DB/provider errors to Woo clients.

## Work Items

- [x] Define exact request/response decoder and authenticated route.
- [x] Implement PostgreSQL transaction with per-role generations and stale ordering.
- [x] Register route and add integration tests with current auth harness.
- [x] Verify no image fetch, WordPress inbound auth change or R2 code.

## Interfaces / Contracts

Producer: Woo plugin `ModaApiClient`. Consumer: Moda API-owned HTTP contract; both implement the same documented `woo.shop-brand.v1` payload. The corresponding Woo plugin implementation can be developed in parallel using fixed HTTP fixtures; production activation and integrated validation require this API task to be accepted. Durable result: `commerce.ShopBrand` source fields and `whatsAppMedia` generation/work statuses. BG002 later processes the PENDING media without a direct API→Background call.

## Dependencies

- ARCH-049-DATABASE-001

## Enables

- ARCH-049-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Unauthenticated and cross-installation requests cannot mutate ShopBrand.
- [x] Valid complete snapshot writes source generations atomically and responds only after PostgreSQL commit.
- [x] Duplicate/older observations do not create new generations or overwrite newer source.
- [x] Missing/removed source is distinguished from failed request.
- [x] No new table/queue contract or WordPress server endpoint.

## Validation

- [x] API contract and body-size/headers/security tests.
- [x] Database-backed tenant/idempotent/ordering/multi-role update integration tests.
- [x] Register route in existing composition and verify startup/typecheck/lint/test commands.
- [x] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and Validation are complete, record the Completion Report and change task status to `review`; hand off to `moda_architect` and STOP. Do not continue into a dependent task or change an `_index.md`.

## Implementation Notes

All task work must use the canonical launcher-provided **dedicated parent and implementation worktrees**, synced task/<TASK_ID> branches and start-of-attempt evidence. Inspect the actual pinned package scripts, source and existing conventions before editing. Do not merge branches, push main, edit another repository, start an enabled task or change any `docs/decisions/**/_index.md`. Use structured logging via `@modainteract/moda-interact-shared/logging`; secrets and full untrusted URLs must not enter diagnostics. Document changed files, relevant test commands, results, security/tenant checks, commits and worktree evidence in the Completion Report.

Ensure the plugin uses the existing installation credential scheme; no source data or shop IDs are accepted from the untrusted caller as authority for tenant selection.

## Completion Report

### Status

Ready for Review — developer Attempt 1 (claim `2026-10-27T12:46:54Z`). Four incremental delivery patches were applied within this **one** developer workflow attempt; the canonical task `attempt` remains 1. Implementation was committed and pushed. The post-validation upstream merge and remaining publication/verification caveat are recorded below for the reviewer.

### Files Changed

Task-owned implementation changes in `moda-interact-api` (14 entries including database gitlink):

- `database` (nested database submodule gitlink; advanced to the accepted ARCH-049 ShopBrand schema during implementation; verify the final gitlink after the upstream merge).
- `package.json` (focused unit and disposable-PostgreSQL integration test scripts).
- `scripts/test-arch049-shop-brand-postgres.mjs`.
- `src/composition/routes.ts`.
- `src/composition/woocommerce.ts`.
- `src/index.ts`.
- `src/woocommerce/shop-brand/contract.ts`.
- `src/woocommerce/shop-brand/request.ts`.
- `src/woocommerce/shop-brand/routes.ts`.
- `src/woocommerce/shop-brand/service.ts`.
- `tests/integration/woocommerce/shop-brand/service.postgres.test.ts`.
- `tests/unit/woocommerce/shop-brand/contract.test.ts`.
- `tests/unit/woocommerce/shop-brand/routes.test.ts`.
- `tests/unit/woocommerce/shop-brand/service.test.ts`.

An **additional** merge from API `origin/main` occurred after the successful validation. Its log shows incoming changes to the *merchant recovery-policy* OpenAPI/source/tests and a database-submodule merge conflict, resolved by staging the database gitlink. These incoming upstream files are not claimed as features implemented under this task.

### Work Completed

- Implemented tenant-authenticated `POST /v1/woocommerce/shop-brand` using the existing Woo installation authenticator, rejecting untrusted `shopId` and authenticating before body parsing.
- Added the strict `woo.shop-brand.v1` contract: canonical observedAt, 16 KiB maximum body, exact JSON fields, duplicate-header/key rejection, UTF-8 and HTTPS source validation, and no-store `200` (`updated`/`unchanged`), `400`, `401`, `413` and `503` responses.
- Used a short PostgreSQL transaction with Shop/ShopBrand row locks and in-transaction installation revalidation. Persisted the original brand fields and JSON role source generations for `LOGO`, `SQUARE_LOGO`, and `COVER_IMAGE`; protected newer observations and READY assets, preserved other roles and handled explicit source removal as `MISSING`.
- Retained Background ownership of media processing: no WordPress server calls, image decoding, R2 activity or BullMQ publication in the API transaction. Shared structured logging emits bounded, redacted diagnostics rather than source URLs or credentials.
- Added unit/contract/HTTP tests and executable PostgreSQL integration coverage for tenant isolation, revoked/suspended installations, malformed payloads, duplicate/stale observations, role generation transitions, metadata-only updates and concurrent worker writes.
- Corrected three test-fixture defects in incremental patches: optional PostgreSQL URL typing, global count isolation, and valid `(status, revokedAt)` transitions. No production-code changes were required for those three corrections.

### Validation Results

Validated **before** the subsequent upstream merge; evidence: developer terminal capture `typescript(20261027-143455)`:

| Command/check | Result |
| --- | --- |
| `npm run test:arch049-shop-brand:postgres` | **PASS** — 3/3 real PostgreSQL integration tests (including actual Woo installation HTTP auth and concurrency), 65 migrations applied to disposable database. |
| `npm run test:arch049-shop-brand:unit` | **PASS** — 9/9 unit, contract and HTTP tests. |
| `npm run typecheck` | **PASS** — Prisma client generated successfully; `tsc --noEmit -p tsconfig.json` completed without errors. |
| `npm run lint` | **PASS** — `eslint . --max-warnings=0`. |
| `npm run build` | **PASS** — Prisma generation and `tsc -p tsconfig.build.json`. |
| `git diff --check` and `git diff --cached --check` | **PASS** — no whitespace errors reported. |

Git/worktree and publication evidence:

- Parent task worktree: `moda-interact-workspace-task-ARCH-049-API-001`; implementation worktree: `moda-interact-workspace.worktrees/ARCH-049-API-001`, both reported as canonical dedicated paths in the launcher-origin task claim and latest snapshot archive creation.
- Both task branches: `task/ARCH-049-API-001`. Task claim records start-of-attempt parent/API synchronisation, clean worktrees and verified dependency `ARCH-049-DATABASE-001: complete`.
- Implementation commit: **`83c801d`** (`feat(arch-049-api-001)`), successfully pushed to `origin/task/ARCH-049-API-001` in the supplied log.
- Later local merge commit: **`7a55571`** (`Merge remote-tracking branch 'origin/main' into task/ARCH-049-API-001`), created after tests; the log does **not** show a subsequent test run or push of this merge commit. The final database gitlink also needs verification after its manual submodule-conflict resolution.
- At the end of the log, Git reported no staged or unstaged tracked changes, but an untracked `typescript` log file remained. This is non-task output and should not be included in the commit.

### Deviations

- The API task branch was updated from `origin/main` **after** the tests. Git reported a database-submodule merge conflict that the developer resolved by staging the gitlink and committing a merge. The post-merge result has not been independently regression-tested or confirmed remotely by the supplied evidence.
- No intentional changes to the task's agreed API behaviour or repository ownership. Four patch delivery numbers are not four workflow attempts.

### Assumptions

- `ARCH-049-DATABASE-001` provides the accepted `commerce.ShopBrand.whatsAppMedia` schema; the nested database commit should remain aligned after the upstream merge.
- `ARCH-049-BACKGROUND-002` owns the durable due scanner for `PENDING` media; API success is based on PostgreSQL commit, not queue publication.
- Existing Woo installation credentials and principal resolution are authoritative; source payloads do not supply tenant authority.

### Unresolved Issues

- **Pre-acceptance verification:** From the current merged API task tip (`7a55571`), verify `git submodule status --recursive`, rerun the focused PostgreSQL/unit tests and repository typecheck/lint/build (or provide equivalent evidence demonstrating no post-merge regression), then push `task/ARCH-049-API-001` and record its final published commit. The supplied log proves `83c801d` was pushed, **not** that `7a55571` was pushed.
- A complete launcher-resolved execution packet is not attached to the validation log; the existing task claim records its start-of-attempt synchronisation and isolation. Architect/developer reviewer should reconcile against the actual Git worktree and branch state before acceptance.

### Architectural Concerns

No new cross-repository contract, queue, provider or schema architecture change is proposed by this task. Verify that the database gitlink retained the accepted ARCH-049 migration after the manual merge resolution. No dependent task was started by this implementation.

## Architect Review

### Review Status

Pending.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not reviewed.

### Follow-up

None.

## Dependency Frontier Reconciliation

- Promoted from `pending` to `ready` on 2026-10-27 after its only declared dependency, `ARCH-049-DATABASE-001`, was explicitly completed.
- At promotion, Attempt remained 0 with no executor or claim timestamp; no implementation attempt or implementation worktree had yet been created.

## Execution Ownership Amendment and Claim

- On 2026-10-27, `/moda_developer_create ARCH-049-API-001` explicitly took over the ready agent-owned task for developer execution. `assigned_agent: moda_api` is unchanged; `execution_mode` and `completion_mode` are now `developer`.
- Developer Attempt 1 was claimed at `2026-10-27T12:46:54Z` after verifying `ARCH-049-DATABASE-001` was complete and synchronizing both canonical task worktrees.
- Parent task branch `task/ARCH-049-API-001` merged current parent `origin/main`; implementation branch `task/ARCH-049-API-001` was created from current API `origin/main`. Both task worktrees were clean before the claim. The shared API source checkout's existing `start-dev.sh` modification and untracked `typescript` file were left untouched.
