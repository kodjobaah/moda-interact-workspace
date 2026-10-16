---
id: ARCH-041-API-014
architecture_id: ARCH-041
title: Relocate Woo installation authentication into an API auth boundary
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 63
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-041-API-003
  - ARCH-041-API-005
  - ARCH-041-API-007
  - ARCH-041-API-011
enables:
  - ARCH-041-API-012
  - ARCH-041-SYSTEM-TEST-001
created: 2026-10-16
updated: 2026-10-16
---

# ARCH-041-API-014 — Relocate Woo installation authentication into an API auth boundary

## Architecture

- Architecture ID: `ARCH-041`
- Parent document: `docs/architecture/ARCH-041-hosted-api-modular-refactor.md`
- Coordinator: `moda_architect`
- **Definition state:** materialised on parent branch `task/ARCH-041-API-014` in the canonical parent task worktree.
- **Task state:** `ready`; all explicit dependencies are `complete`. The canonical launcher must re-gate them before claiming.

### Developer Takeover

The developer invoked `/moda_developer_create ARCH-041-API-014` for this ready task. Execution and completion ownership are taken over from the assigned agent and set to `developer`/`developer`; logical ownership remains `assigned_agent: moda_api`. Scope, dependency, acceptance criteria and validation requirements are unchanged. The canonical launcher will claim Attempt 1 after worktree synchronization and dependency verification.

## Objective

Make `src/auth/woo-installation/` the single API-local home for existing WooCommerce installation identity and bearer authentication, with **zero authentication-policy or HTTP behaviour change**.

## Context

`WooInstallationAuthenticator`, `WooUnauthenticatedError` and `WooInstallationPrincipal` currently live in `src/woocommerce/installation/authenticator.ts`, but merchant and billing features depend on them widely. `woocommerce/installation/credential.ts` holds the existing Woo installation credential codec used by both the authenticator and the connection service. The runtime API should own authentication as a cross-feature boundary, while Woo installation **connection establishment**, rotation lifecycle and site verification remain Woo-specific. This is a mechanical ownership refactor, **not** a new identity provider or a change to WordPress permissions.

Because imports span billing, merchant and Woo route code, this task is gated behind accepted billing extractions API-003/005/007 and merchant route extraction API-011. Unfinished ARCH-026/035/040 feature tasks do not gate it. This avoids carrying two competing authentication import paths into parallel refactoring tasks.

## Scope

- Establish `src/auth/woo-installation/principal.ts` containing the current principal type and unchanged fields: `installationId`, `shopId`, `canonicalSiteUrl`, `credentialVersion`.
- Relocate existing bearer validation, strict raw-header cardinality check, shop/installation status checks, credential comparison and denial error to `src/auth/woo-installation/authenticator.ts` without changing behavior, database query cardinality, constant-time digest comparison, error mapping or returned principal.
- Move the existing generic Woo installation bearer-credential functions (`randomSecret`, `encodeSecret`, `decodeSecret`, `digestSecret`, `constantTimeDigestMatches`) from `woocommerce/installation/credential.ts` into `auth/woo-installation/credential.ts`, preserving byte-level format and constant-time comparison. The same source file currently also implements `createSiteProof` and `verifySiteProof`: move these **Woo connection-specific** HMAC proof functions into `woocommerce/installation/site-proof.ts`, consumed by `site-verifier.ts` and its tests. The site-proof module may import the canonical auth-owned codec primitives, but `src/auth/` must never import Woo installation feature modules. Do not duplicate either implementation or change the proof message, HMAC algorithm, nonce/site binding or rejection semantics. Keep issuance/reconnection policy in `woocommerce/installation/connection-service.ts`.
- Update references in existing merchant, billing, Woo installation and application composition modules to the new canonical auth imports. Do not keep two independently maintained authenticator implementations or hidden runtime compatibility copies.
- Update the directly affected legacy unit tests and add/focus `tests/unit/auth/woo-installation/` negative/security parity tests; no bulk test migration. Introduce `installation-state.ts` **only** if an existing pure status predicate is genuinely extracted, not as an empty placeholder.

## Out of Scope

- No change to endpoint routes, HTTP header names, accepted credential formats, principal fields, database schema, durable state, installation rotation or revocation timing, in-flight billing command authorization or response envelope/status.
- No generic JWT, global authorization middleware, OAuth, Shopify staff authentication or new REST-read callback/webhook authentication.
- No replacement crypto implementation when approved Shared security primitives already own the mechanism; any incompatible Shared dependency gap must return to the architect.
- No WooCommerce WordPress plugin changes, new roles, nonce/capability policy changes, provider authorization, Gateway or database migrations.
- No `docs/decisions/**/_index.md` changes. No implementing API-012 or HTTP utilities within this task.

## Requirements

- The same authenticated request returns the same `WooInstallationPrincipal`, and the same rejected request remains rejected. Read `rawHeaders` for duplicate-header rejection; do not weaken case, cardinality, bearer syntax or canonical site/tenant checks.
- Preserve `wooCommerceInstallation.findUnique` lookup and all observed shop/installation checks without adding extra per-request round trips or relaxing revocation/status enforcement.
- Preserve the existing error types/codes, route-level handling and Shared logging/crypto contracts. Credentials, authorization headers, digests and sensitive shop data must never be newly logged.
- Keep the trust mechanisms **separate**: Woo connect uses site-control verification; billing webhooks use their signature; REST-read callbacks use their existing one-time capability. Moving the installation authenticator must not apply bearer middleware to those routes.
- Imports flow `merchant/billing/woocommerce -> auth/woo-installation` for identity verification; `auth/` must not depend on business services, route composition or `index.ts`.

## Work Items

- [x] Inventory existing authenticator/credential imports, tests and actual current security invariants against the accepted API-001 baseline.
- [x] Extract canonical principal, bearer authenticator and generic credential primitives into `src/auth/woo-installation/`; split `createSiteProof`/`verifySiteProof` into Woo-owned `src/woocommerce/installation/site-proof.ts` with unchanged HMAC inputs and compare semantics.
- [x] Update only the affected imports, injection types and focused tests; remove redundant old implementation instead of duplicating code.
- [x] Prove negative cases: missing/duplicate raw header, malformed/bad digest bearer, inactive/revoked installation, inactive/wrong-platform shop and rotated credentials; prove site-proof acceptance and wrong-site/nonce/tampered-proof rejection, as well as separate callback/webhook/connect trust paths.
- [x] Record touched files, exact test commands, affected security paths and baseline comparison in the Completion Report.

## Interfaces / Contracts

Canonical API-local exports: `WooInstallationPrincipal`, `WooInstallationAuthenticator`, `WooUnauthenticatedError`, `WooAuthenticationDatabase` under `src/auth/woo-installation/`; the generic credential codec helpers remain semantically identical and the Woo-only site proof functions remain in `woocommerce/installation/site-proof.ts`. The four-field principal shape, current database model and public HTTP/OpenAPI v1 security contracts do not change. No Shared publication is required.

## Dependencies

- `ARCH-041-API-003` — complete and accepted; final billing presentation imports settled.
- `ARCH-041-API-005` — complete and accepted; final recurring command imports settled.
- `ARCH-041-API-007` — complete and accepted; final recovery-credit command imports settled.
- `ARCH-041-API-011` — complete and accepted; merchant/billing route extraction settled. No external feature prerequisite.

## Enables

- `ARCH-041-API-012`
- `ARCH-041-SYSTEM-TEST-001` — direct terminal dependency, still blocked until every prerequisite is Complete.

## Acceptance Criteria

- [x] `src/auth/woo-installation/principal.ts` and `authenticator.ts` own the canonical existing principal/validator; the existing credential codec has one tested home, without duplicated service-owned implementations.
- [x] All API runtime imports use the canonical auth boundary; no unresolved old authenticator paths remain. `createSiteProof` and `verifySiteProof` are owned once by `src/woocommerce/installation/site-proof.ts`, while `src/auth/` has no Woo feature import; site challenge bytes, proof comparison, and issuance/callback/webhook responsibilities remain unchanged.
- [x] Same accepted/denied credentials, exact error/header response behaviour, tenant scope and current credential-rotation/revocation semantics before and after relocation.
- [x] Existing auth test coverage is maintained and `tests/unit/auth/woo-installation/` adds meaningful negative parity proof; the new tests are discovered by the existing npm script.
- [x] No additional auth DB query, altered provider/transaction operation, public contract change, WordPress permission change, blanket middleware or leaked secret.
- [x] No `_index.md` touched and no unrelated refactor files changed.

## Validation

- [x] Existing auth assertions, credential/site-proof and `site-verifier.test.ts` HMAC/wrong-site/nonce/tampering cases, and related Woo connection and route suites.
- [x] Focused `tests/unit/auth/woo-installation/*.test.ts` and API-001 cross-router/security characterization suites.
- [x] Existing billing/merchant tests that consume the principal and conditional PostgreSQL auth/merchant suites with disposable database prerequisites available.
- [x] `npm test`, `npm run typecheck`, `npm run lint`, `npm run build` according to the current `package.json` scripts.
- [x] `git diff --check` plus launcher-prepared isolated parent/implementation worktree, synchronization and recursive submodule evidence.

## Stop Condition

When the bounded work and validation are complete, finish the Completion Report, set the task to `review`, return to `moda_architect` and **STOP**. Do not begin API-012 without architect acceptance and dependency promotion.

## Implementation Notes

This is **one mechanical ownership migration** of a security-sensitive feature already verified by API-001. Treat the existing mixed `credential.ts` as two responsibilities: shared bearer-credential primitives in `auth/woo-installation/credential.ts`, and site-control HMAC proof in `woocommerce/installation/site-proof.ts` (no new cryptographic implementation or proof format). Keep the current auth query and credential codec as the behavioral authority; do not redesign authorization while reorganizing files. An optional `installation-state.ts` must only hold extracted existing checks without changed semantics. New tests follow the accepted `tests/unit/` path; there is no bulk migration of legacy tests and no changes to the system-test repository here.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and the canonical task immediately before claiming. The startup launcher packet is valid evidence of isolation and synchronization. The uploaded snapshot is not the developer's live Git worktree. Any new cross-service contract, required Shared crypto change or unexpected source drift is returned to the architect, not implemented opportunistically.

## Completion Report

### Status

Complete — Attempt 1 passed developer self-review, Architect Review was accepted as supplied with the explicit completion request, and the developer recorded the completion decision on 2026-10-16. Attempt 0 review history is preserved below.

### Files Changed

92 files changed in implementation commit `15f048ee5f1e8a13edbc3996e6e2196024428823`: canonical authenticator, principal and credential codec moved to `src/auth/woo-installation/`; site-proof HMAC functions moved to `src/woocommerce/installation/site-proof.ts`; affected API imports and focused tests updated; API-001 security baseline references updated. No `_index.md`, database schema, endpoint contract or WordPress plugin changes.

### Work Completed

Moved Woo installation bearer identity/authentication into the API auth boundary and relocated the Woo-only connect site-proof functions to the Woo installation feature. Preserved the raw-header cardinality check, bearer format, one-row `findUnique` lookup, installation/shop status checks, constant-time digest comparison, error behavior and four-field principal. Added focused parity tests for malformed/missing/duplicate headers, bad credentials, revoked/inactive/incompatible rows, canonical credential encoding and site-proof acceptance/tampering. Existing callback, webhook and connect trust paths remain separate. Reviewed the implementation against the API-001 security baseline; confirmed no runtime references to old auth module paths and no Woo feature imports from `src/auth/`.

### Validation Results

Passed focused command `npx tsx --test tests/unit/auth/woo-installation/authenticator.test.ts tests/unit/auth/woo-installation/credential.test.ts tests/unit/auth/woo-installation/authentication-contract.test.ts tests/unit/woocommerce/installation/site-proof.test.ts src/woocommerce/installation/site-verifier.test.ts src/woocommerce/installation/routes.test.ts src/woocommerce/installation/connection-service.test.ts` (47/47).

Passed `npm test` (402 passed, 0 failed, 42 skipped; skips are conditional PostgreSQL cases), `npm run typecheck`, `npm run lint`, `npm run build`, and `git diff --check origin/main...HEAD`.

Passed `npm run test:integration` using disposable PostgreSQL: Woo installation (13), bootstrap (2), store context (1), category reads (1), category writes (3), REST-read authorization (4), and ARCH-041 billing (17); 41 database integration tests passed, 0 failed. The harness cleaned up its disposable containers.

Implementation commit `15f048ee5f1e8a13edbc3996e6e2196024428823` is published to `origin/task/ARCH-041-API-014`. Parent and implementation worktrees were launcher-resolved canonical task worktrees, clean at review, and on the mirrored task branch. The parent task branch was synchronized with its remote; implementation task branch is published and based on its current `origin/main`. The task attempt's launcher preparation supplied synchronization and recursive-submodule evidence.

### Deviations

None. Scope remained limited to the defined API ownership refactor.

### Assumptions

The ARCH-041 billing and route extraction streams were complete and launcher-gated before this high-fan-out import relocation. Future unrelated API feature tasks may remain unfinished.

### Unresolved Issues

None.

### Architectural Concerns

None identified. Architect Review acceptance was explicitly supplied with the developer's completion request.

## Architect Review

### Review Status

Accepted.

### Review Notes

The developer explicitly supplied “Architect Review Accepted” with the completion request. Acceptance is recorded against implementation commit `15f048ee5f1e8a13edbc3996e6e2196024428823` and the validation evidence in the Completion Report; no additional architect review notes were supplied.

### Reviewed Files

`src/auth/woo-installation/authenticator.ts`, `principal.ts`, `credential.ts`, `src/woocommerce/installation/site-proof.ts`, affected consumers/tests, and `tests/contracts/http-billing-security-baseline.md`.

### Validation Reviewed

Reviewed the focused 47-test auth/site-proof/route suite, full `npm test`, `npm run typecheck`, `npm run lint`, `npm run build`, `git diff --check origin/main...HEAD`, and `npm run test:integration` (41 disposable-PostgreSQL tests passed).

### Architecture Conformance

Accepted for the bounded ownership refactor; recorded behavior and security invariants are preserved, with no public contract or schema change.

### Follow-up

Accepted. API-014 is complete; API-012 is promoted to `ready`. API-013 remains pending and continues to gate ARCH-041-SYSTEM-TEST-001.

### Developer Self-Review - Passed

- Attempt: 1.
- Reviewed implementation commit: `15f048ee5f1e8a13edbc3996e6e2196024428823`.
- Result: scope, security invariants and validation passed; task moved to `review`.
- At review submission, `completion_mode: developer` left explicit completion pending.

### Developer Completion Decision

- Decision: Complete.
- Authorized action: `/moda_developer_update ARCH-041-API-014 complete`.
- Date: 2026-10-16.
- Accepted review: Architect Review Accepted, as explicitly supplied by the developer with this completion request.
- Attempt: 1, unchanged.
- Implementation commit: `15f048ee5f1e8a13edbc3996e6e2196024428823`, published to `origin/task/ARCH-041-API-014`.
- Parent task/report branch: `task/ARCH-041-API-014`.
- Dependency frontier: API-012 promoted to `ready`; ARCH-041-SYSTEM-TEST-001 remains `pending` because API-013 is pending.
- No task branch was merged to `main`.
