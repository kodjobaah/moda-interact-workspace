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
status: in_progress
priority: 63
executor: developer
claimed_at: 2026-10-16T19:52:22Z
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

- [ ] Inventory existing authenticator/credential imports, tests and actual current security invariants against the accepted API-001 baseline.
- [ ] Extract canonical principal, bearer authenticator and generic credential primitives into `src/auth/woo-installation/`; split `createSiteProof`/`verifySiteProof` into Woo-owned `src/woocommerce/installation/site-proof.ts` with unchanged HMAC inputs and compare semantics.
- [ ] Update only the affected imports, injection types and focused tests; remove redundant old implementation instead of duplicating code.
- [ ] Prove negative cases: missing/duplicate raw header, malformed/bad digest bearer, inactive/revoked installation, inactive/wrong-platform shop and rotated credentials; prove site-proof acceptance and wrong-site/nonce/tampered-proof rejection, as well as separate callback/webhook/connect trust paths.
- [ ] Record touched files, exact test commands, affected security paths and baseline comparison in the Completion Report.

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

- [ ] `src/auth/woo-installation/principal.ts` and `authenticator.ts` own the canonical existing principal/validator; the existing credential codec has one tested home, without duplicated service-owned implementations.
- [ ] All API runtime imports use the canonical auth boundary; no unresolved old authenticator paths remain. `createSiteProof` and `verifySiteProof` are owned once by `src/woocommerce/installation/site-proof.ts`, while `src/auth/` has no Woo feature import; site challenge bytes, proof comparison, and issuance/callback/webhook responsibilities remain unchanged.
- [ ] Same accepted/denied credentials, exact error/header response behaviour, tenant scope and current credential-rotation/revocation semantics before and after relocation.
- [ ] Existing auth test coverage is maintained and `tests/unit/auth/woo-installation/` adds meaningful negative parity proof; the new tests are discovered by the existing npm script.
- [ ] No additional auth DB query, altered provider/transaction operation, public contract change, WordPress permission change, blanket middleware or leaked secret.
- [ ] No `_index.md` touched and no unrelated refactor files changed.

## Validation

- [ ] Existing `src/woocommerce/installation/authenticator.test.ts` assertions (either retained with imports adjusted or specifically relocated), credential/site-proof and `site-verifier.test.ts` HMAC/wrong-site/nonce/tampering cases, and related Woo connection and route suites.
- [ ] Focused `tests/unit/auth/woo-installation/*.test.ts` and API-001 cross-router/security characterization suites.
- [ ] Existing billing/merchant tests that consume the principal and any relevant conditional PostgreSQL auth/merchant suites when disposable database prerequisites are available.
- [ ] `npm test`, `npm run typecheck`, `npm run lint`, `npm run build` according to the current `package.json` scripts.
- [ ] `git diff --check` plus launcher-prepared isolated parent/implementation worktree, sync and recursive submodule evidence.

## Stop Condition

When the bounded work and validation are complete, finish the Completion Report, set the task to `review`, return to `moda_architect` and **STOP**. Do not begin API-012 without architect acceptance and dependency promotion.

## Implementation Notes

This is **one mechanical ownership migration** of a security-sensitive feature already verified by API-001. Treat the existing mixed `credential.ts` as two responsibilities: shared bearer-credential primitives in `auth/woo-installation/credential.ts`, and site-control HMAC proof in `woocommerce/installation/site-proof.ts` (no new cryptographic implementation or proof format). Keep the current auth query and credential codec as the behavioral authority; do not redesign authorization while reorganizing files. An optional `installation-state.ts` must only hold extracted existing checks without changed semantics. New tests follow the accepted `tests/unit/` path; there is no bulk migration of legacy tests and no changes to the system-test repository here.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and the canonical task immediately before claiming. The startup launcher packet is valid evidence of isolation and synchronization. The uploaded snapshot is not the developer's live Git worktree. Any new cross-service contract, required Shared crypto change or unexpected source drift is returned to the architect, not implemented opportunistically.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-16T19:52:22Z. Attempt 0 review history is preserved below.

### Files Changed

None. To be recorded by the implementing agent.

### Work Completed

None.

### Validation Results

Not run. Record actual commands and outcomes; do not infer a pass from documentation.

### Deviations

None.

### Assumptions

The ARCH-041 billing and route extraction streams have been accepted before this high-fan-out import relocation. Future unrelated API feature tasks may remain unfinished.

### Unresolved Issues

None at definition time; implementation drift is an architect handoff.

### Architectural Concerns

Return any authentication/contract/schema cross-boundary issue to `moda_architect`.

## Architect Review

### Review Status

Pending.

### Review Notes

Not reviewed or accepted; task defined but not materialised.

### Reviewed Files

None — review will inspect actual code, task report and task branch evidence.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending implementation and review against ARCH-041 security and routing invariants.

### Follow-up

Acceptance or Changes Requested to be recorded by `moda_architect`; only accepted Complete unblocks API-012.
