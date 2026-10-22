---
id: ARCH-046-API-005
architecture_id: ARCH-046
title: Manage merchant recovery suppression for Woo customers
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 33
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-045-DATABASE-002
enables:
  - ARCH-046-WOOCOMMERCE-007
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
created: '2026-10-21'
updated: 2026-10-22
---
# Manage merchant recovery suppression for Woo customers

## Architecture

### Developer Takeover

The developer explicitly invoked `/moda_developer_create ARCH-046-API-005`, taking execution and completion authority from the prior agent-owned definition. The task scope, dependencies, acceptance criteria and validation expectations are unchanged; `assigned_agent: moda_api` remains the logical repository owner. Attempt 1 was claimed at 2026-10-22T18:08:50Z; worktree isolation and start-of-attempt synchronisation evidence still needs to be confirmed from the prepared launcher packet.

Architecture ID: `ARCH-046`
Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** Developer Attempt 1 implemented and published for architectural review. Developer completion remains separate and pending; this task is not architect-accepted or Complete.

## Objective

Provide an installation-authenticated merchant command to **disable or re-enable recovery for an existing CustomerPhone**, and record a customer-reported off-channel opt-out, without turning merchant selection into WhatsApp consent.

## Context

A merchant may choose not to recover a customer or receive a customer opt-out by phone/email. Both suppress recovery; neither permits the merchant to grant opt-in. Only an existing GRANTED customer preference can be eligible when merchant suppression is cleared.

## Scope

- Accept only authenticated active installation and privileged WP admin-proxied request for the one unambiguous existing Woo Customer/active canonical phone within the authenticated merchant and explicit opt-out evidence reference; shop is always inferred from installation.
- Atomically set/increment the durable CustomerPhone local no-contact override, idempotently handling request replay and installation/phone changes; allow clearing only a merchant-owned recovery suppression after checking current GRANTED consent; never grant consent or clear CUSTOMER_STOP.
- Provide bounded read-only opt-out status to the admin caller with minimal PII. No checkout reconciliation or recovery job on either command.

## Out of Scope

- No new WP user role, generic consent-provider adapter or background recovery search.

## Requirements

- [x] Merchant suppression/recorded opt-out is immediately authoritative for matching CustomerPhone; re-enabling requires current GRANTED consent, must not clear CUSTOMER_STOP, and cannot be overwritten by stale grant.
- [x] Another merchant or browser without WP admin authorization cannot forge opt-out or grant.

## Work Items

- [x] Accept only authenticated active installation and privileged WP admin-proxied request for the one unambiguous existing Woo Customer/active canonical phone within the authenticated merchant and explicit opt-out evidence reference; shop is always inferred from installation.
- [x] Atomically set/increment the durable CustomerPhone local no-contact override, idempotently handling request replay and installation/phone changes; allow clearing only a merchant-owned recovery suppression after checking current GRANTED consent; never grant consent or clear CUSTOMER_STOP.
- [x] Provide bounded read-only opt-out status to the admin caller with minimal PII. No checkout reconciliation or recovery job on either command.

## Interfaces / Contracts

Owner: `moda-interact-api` (`moda_api`). Use the canonical Database/Shared contracts named in this architecture; authorise only this repository's implementation. No consent-triggered checkout recovery job, new merchant role, or raw personally identifiable logging.

## Dependencies

- `ARCH-045-DATABASE-002`

## Enables

- `ARCH-046-WOOCOMMERCE-007`
- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [x] Merchant suppression/recorded opt-out is immediately authoritative for matching CustomerPhone; re-enabling requires current GRANTED consent, must not clear CUSTOMER_STOP, and cannot be overwritten by stale grant.
- [x] Another merchant or browser without WP admin authorization cannot forge opt-out or grant.

## Validation

- [x] Installation auth, shop-scoped canonical-phone lookup, duplicate/ambiguous customers, disable/re-enable, no-consent re-enable, customer STOP precedence, replay and cross-shop tests.

## Stop Condition

After defined Work Items, Acceptance Criteria and required Validation, record dedicated parent/implementation task worktree and start-of-attempt synchronisation evidence, set `status: review`, submit Completion Report to `moda_architect`, and STOP. No dependent task may start before architect acceptance.

## Implementation Notes

Use the architect-approved consent model: no initial CheckoutRecovery without verified current permission, no arbitrary consent timeout, and consent changes do not trigger checkout reconciliation. Follow the current `/moda-task` launcher and exact published Shared/Database contracts. Preserve `docs/decisions/**/_index.md` until architecture session completion is confirmed. Use Shared structured logging on Node; bounded WordPress-safe diagnostics in PHP. Any missing cross-repository capability returns to architect rather than being implemented outside repository ownership.

## Completion Report

### Status

Ready for Review — developer Attempt 1. Implementation published to
`kodjobaah/moda-interact-api` branch `task/ARCH-046-API-005` at
`71fa299d1191c43ca85fc981f69d31d3d12eb469`
(`feat(ARCH-046-API-005): implement Woo customer recovery suppression`).
The parent task was claimed on 2026-10-22T18:08:50Z. This submission does not
assert architect acceptance or developer completion.

### Files Changed

Implementation repository `moda-interact-api` (published commit above):

- `database` (submodule points to accepted `ARCH-045-DATABASE-002` revision `508a89463ccb24dcc31e5f38e04be8cfd10ad690`)
- `package.json`
- `scripts/test-arch046-woo-consent-postgres.mjs`
- `src/composition/routes.ts`
- `src/composition/woocommerce.ts`
- `src/index.ts`
- `src/woocommerce/recovery-selection/contract.ts`
- `src/woocommerce/recovery-selection/request.ts`
- `src/woocommerce/recovery-selection/routes.ts`
- `src/woocommerce/recovery-selection/service.ts`
- `tests/unit/composition/real-route-registration.test.ts`
- `tests/unit/woocommerce/recovery-selection/contract.test.ts`
- `tests/unit/woocommerce/recovery-selection/routes.test.ts`
- `tests/integration/woocommerce/recovery-selection/service.postgres.test.ts`
- `docs/arch046-woo-merchant-recovery-selection.md`
- `docs/openapi/arch046-woo-recovery-selection-v1.yaml`

Parent coordination update: this task definition only. No `_index.md` changes.

### Work Completed

- Added installation-authenticated, WP admin-proxied `GET` and `POST`
  `/v1/woocommerce/customer-recovery-selection` endpoints. Shop scope comes
  only from the authenticated active installation; no caller-specified shop or
  customer selector is accepted.
- Added strict versioned command and status contracts, exact canonical-phone
  lookup, 2 KiB POST size bound, revision preconditions and no-store responses
  without disclosing customer identifiers.
- Applied `SUPPRESS` (`MERCHANT_OPT_OUT`), `REENABLE` (only for an already
  GRANTED and otherwise eligible recipient), and `RECORD_CUSTOMER_STOP`
  (terminal `CUSTOMER_STOP`) to durable CustomerPhone no-contact state.
  Per-recipient transaction locking, stale-write checks, replay idempotency,
  installation validity and tenant isolation are enforced.
- Reused the approved Database/Shared model; no new table, merchant role,
  recovery reconciliation, queue publication, billing event or recovery job.
- Added contract/OpenAPI guidance and API unit and disposable-PostgreSQL tests,
  including concurrent operations, changed-number and STOP precedence cases.

### Validation Results

Observed in the 2026-10-22 local terminal log:

- `npm run test:arch046-woo-selection:unit` — **PASS 3/3**.
- `npm run test:arch046-woo-selection:postgres` — **PASS 8/8**;
  59/59 migrations applied to a disposable PostgreSQL database. The eight
  cases include the existing five consent scenarios and three selection
  scenarios for suppression, STOP, scope and concurrency.
- `npm run test:arch046-woo-consent:unit` — **PASS 7/7**.
- `npm run lint` — **PASS** (ESLint, zero reported errors).
- `npm run build` — **PASS** (Prisma generation and production TypeScript build).
- `git diff --check` — **PASS** (no output in terminal log).
- `npm run typecheck` — **FAIL** with three `TS2345` diagnostics in the
  unchanged `tests/unit/merchant/merchant-knowledge/upload-timing.test.ts`
  at lines 71, 80 and 92 (`dataFormatKey: string` versus `UploadFormat`).
  No errors are reported in API-005's changed files. This is not recorded as
  a named API baseline in `docs/development-baseline.md`; the repository-wide
  typecheck must **not** be represented as passing.
- GitHub API branch inspection — published implementation commit
  `71fa299d1191c43ca85fc981f69d31d3d12eb469` contains the API-005
  implementation and test changes listed above.
- Dedicated parent/implementation worktree and start-of-attempt
  synchronisation packet: **not supplied in the provided terminal logs**;
  reviewer must inspect the original launcher preparation evidence before
  treating physical task isolation as verified. A branch name or passing
  tests alone do not establish it.

### Deviations

- The hosted API accepts `X-Moda-WP-Admin-Verified: 1` only with authenticated
  installation credentials. Independent WordPress nonce, logged-in admin and
  management-capability enforcement is **WooCommerce plugin owned**, not proven
  by these API integration tests; `ARCH-046-WOOCOMMERCE-007` must validate it.
- The API requires an opaque external evidence reference for a reported STOP,
  but the accepted CustomerPhone schema has no column for retaining that
  reference. The API applies the authoritative STOP to CustomerPhone and
  leaves external evidence retention with the originating merchant system;
  see Architectural Concerns.

### Assumptions

- The installation token remains server-side in the Woo PHP proxy and is never
  available to browser code. The proxy asserts WordPress admin verification
  only after validating the actual session, capability and nonce.
- `ARCH-045-DATABASE-002` revision
  `508a89463ccb24dcc31e5f38e04be8cfd10ad690` is the approved dependency.
  All test results above reflect the locally synchronised API database
  submodule; they are not a production deployment certification.

### Unresolved Issues

- Full repository typecheck has three unrelated Merchant Knowledge test typing
  errors. Request architect classification and a separate owning correction
  rather than changing that test within API-005.
- Provide launcher-resolved physical worktree paths and start-of-attempt
  synchronisation evidence for architectural review if not already available
  to the reviewer.
- Real WordPress admin proxy/nonce/session behaviour and evidence retention in
  the calling Woo merchant environment require Woo-owned verification.

### Architectural Concerns

- `CUSTOMER_STOP` remains non-clearable by a merchant, but the opaque
  off-channel evidence reference is **not durably stored in Moda**; if Moda
  must centrally retain evidence provenance, a database-owned contract/change
  is required. Do not repurpose checkbox consent evidence to store it.
- The privileged WordPress proxy assertion is a cross-repository trust
  boundary. Hosted API enforces active installation authentication and rejects
  missing/untrusted admin proxy context; WooCommerce owns the real session,
  nonce and capability checks. No circular API dependency on Woo test completion
  is introduced by this report.

## Architect Review

### Review Status
Pending — no implementation reviewed.

### Review Notes
None.

### Reviewed Files
None.

### Validation Reviewed
None.

### Architecture Conformance
Not assessed.

### Follow-up
None.
