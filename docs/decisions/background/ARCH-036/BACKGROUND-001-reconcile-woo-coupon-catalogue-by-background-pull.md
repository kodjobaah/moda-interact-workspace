---
id: ARCH-036-BACKGROUND-001
architecture_id: ARCH-036
title: "Synchronise Woo coupons directly from Background into the existing catalogue"
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-036-BACKGROUND-004", "ARCH-026-API-007"]
enables: ["ARCH-036-API-002", "ARCH-036-COMMERCE-001", "ARCH-036-ADMIN-001", "ARCH-036-BACKGROUND-003", "ARCH-036-SYSTEM-TEST-001"]
created: 2026-10-12
updated: 2026-10-12
---
# ARCH-036-BACKGROUND-001 — Reconcile Woo coupon catalogue by Background-pulled pages

## Architecture

- Architecture: `ARCH-036` — `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`; owner: `moda_background` / `moda-interact-background`.
- **Defined but not materialised.** No task branch, dedicated worktree, implementation commit or push has been created.

## Objective


Fetch bounded WooCommerce coupon pages **directly from Background** using the verified encrypted Woo REST read grant, then reconcile the existing `ShopifyDiscountCatalogue` and `ShopifyDiscount` rows without changing merchant selections or database schema.

## Context


The Woo installation and encrypted `WooCommerceRestReadGrant` already reside in the database. `ARCH-026-API-007` owns merchant consent/verification and secure grant persistence. Background has database access and an AES-256-GCM decryption helper; it does **not** need an API-001 coupon proxy or Shared coupon-page contract. `BACKGROUND-004` first corrects Shopify's existing `isAvailable` writer semantics. The API's read grant currently has a shop/installation/attempt-bound AEAD envelope: use its actual format/AAD, not a guessed one.

## Scope


In `moda-interact-background` only: implement a narrowly scoped Woo REST read-grant resolver, safe paginated `wc/v3/coupons` GET client, scheduled full-catalogue synchronisation and provider-aware row normalisation/generation reconciliation using existing PostgreSQL tables. Maintain existing Shopify sync behaviour and ownership. Do not add an API route, a new generic credential framework or WooCommerce plugin uploads.

## Out of Scope

No new database table/column/migration, Woo plugin uploader/hooks, API coupon-page proxy, Shared contract, queue platform or selection write; no outbound offer sending (BACKGROUND-003 owns that). Direct, narrowly authorised Background provider reads **are in scope**, but exposing credentials to queue payloads, logs, browser code or other services is not.

## Requirements


1. **Grant authorization:** accept only a valid ACTIVE Woo Shop/installation and ACTIVE grant for that exact Shop/installation, authorized scope exactly `read`, matching current credential version/authorization attempt, non-revoked and canonical-site bound. Prerequisite `ARCH-026-API-007` must be Complete; having grant-shaped Prisma rows alone is insufficient.
2. **Decryption:** use the approved Background AES-256-GCM helper and the **actual** API Woo read-envelope encoding, AAD and key ID rules. Add cross-service encrypted fixture parity (API-sealed → Background-opened; wrong Shop/installation/attempt/rotation/key fails). Inject keyring via approved Background secrets, not source files, logs, queues or browser. Reject missing/rotated/corrupt grant; recheck grant/installation after network I/O. If safe parity/config is unavailable, block and report to architect, never invent an API proxy or bypass encryption.
3. **HTTP security:** target only canonical authorised Woo store `GET /wp-json/wc/v3/coupons` with allowlisted page/per_page/order query; enforce DNS resolution/pinned address, TLS/peer/hostname, no redirects, SSRF-safe public origin in production, size/time/response bounds, exact provider auth and no raw credential in URL/log. LocalWP's non-public host must use an approved reachable test topology; don't relax production settings.
4. **Pagination:** fetch all bounded pages and verify numeric coupon IDs, total-page evidence, stable page identity and duplicate-free completed scan; retries/backoff are bounded. Missing/unstable page, malformed totals, timeout or grant revoked => no CURRENT generation, no missing-row deletion/false REMOVED status. Use the existing catalogue lease/fencing/generation mechanisms; a valid complete empty catalogue is distinct from network failure.
5. **Existing-row mapping:** `shopifyDiscountNodeId='woo:coupon:<positive id>'`; real bounded coupon code/title/type/amount/restrictions stored in existing required fields, dates and `providerSnapshot` JSONB. Normalize `providerStatus` and `fixedSelectable`. New row `isAvailable=false`; preserve selection on active resync, never set it true merely because the provider reported the coupon. Verified expiry/deactivation/deletion may clear selection. Existing referenced rows remain stored for FK/outreach history.
6. **Isolation and recovery:** tenant isolation for two Woo shops plus Shopify, idempotent retries, revoked/rotated credentials, provider outages, removed/expired/usage-exhausted coupons, oversized payloads, code changes and current/fresh catalogue constraints. Only CURRENT, ACTIVE, unexpired, supported fixedSelectable discounts are candidates for UI; their checked state is independent of provider status. Recheck dates and grant at use time.

## Work Items


- [ ] Implement shop/grant resolver with secure AEAD parity and environment keyring validation.
- [ ] Implement bounded SSRF/TLS-safe paginated Woo coupon read client and stable full-scan contract.
- [ ] Reconcile coupon rows and catalogue generations without overwriting selected flags; preserve Shopify paths.
- [ ] Add focused security, idempotency, complete/incomplete pages, zero-coupon, tombstone, expired and cross-Shop tests.
- [ ] Document Background runtime secret provision/rotation and deployment test evidence; report any unsupported transport capability.

## Interfaces / Contracts


Existing Prisma `WooCommerceInstallation`, `WooCommerceRestReadGrant`, `Shop`, `ShopifyDiscountCatalogue`, `ShopifyDiscount` and API-007 encryption envelope. External provider REST `wc/v3/coupons` with bounded `page`/`per_page`. **No new Shared npm contract or API coupon-proxy endpoint.**

## Dependencies


- `ARCH-036-BACKGROUND-004` — Shopify selection semantics no longer overwritten by sync.
- `ARCH-026-API-007` — accepted encrypted read-only grant lifecycle and credential envelope.

## Enables


- `ARCH-036-API-002`
- `ARCH-036-COMMERCE-001`
- `ARCH-036-ADMIN-001`
- `ARCH-036-BACKGROUND-003`
- `ARCH-036-SYSTEM-TEST-001`

## Acceptance Criteria


- [ ] Background itself securely enumerates Woo coupons with the verified read grant; no API-001 endpoint or shared schema required.
- [ ] API-owned sealed grant decrypts only with exact, current Shop/installation/attempt/AAD/keyring; no plaintext secret is persisted or logged.
- [ ] SSRF/TLS/redirect protections, grant rotation/revocation and post-request checks fail closed.
- [ ] Stable complete scans reconcile provider lifecycle without reselecting unchecked coupons; failed scans never tombstone unseen rows or erase merchant selections.
- [ ] Existing table schema/constraints/migrations unchanged and Shopify sync regressions pass.

## Validation


- [ ] Focused direct Woo REST transport and grant/AEAD cross-service parity tests, including invalid key/AAD, SSRF/redirect/rebind and revoked grant.
- [ ] Disposable PostgreSQL full generation, zero/partial/unstable pages, two Woo Shops + Shopify, concurrent scan and state transitions.
- [ ] Declared Background typecheck, lint, tests/build and `git diff --check` (based on repository `package.json`).

## Stop Condition

After bounded work, acceptance checks and required validation: document the Completion Report, set the task to `review` and STOP. Do not begin dependent tasks. For `superseded` tasks, do not execute or claim.

## Implementation Notes


Keep the Background provider client domain-specific and reuse existing approved transport/crypto primitives; do not create a competing generic logger or cryptography implementation. A dedicated Gateway/deployment task is needed only if real keyring/egress configuration cannot be satisfied by existing infrastructure. Do not implement send-time validation in this task; `BACKGROUND-003` owns it. Preserve the physical dedicated task-worktree and prepared-launcher evidence.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run; task not claimed.

### Deviations

None.

### Assumptions

The executor will verify checkout, actual dependencies, task worktrees and available toolchain at claim time.

### Unresolved Issues

None recorded.

### Architectural Concerns

Stop and return cross-repository, credential, provider compatibility or schema deviations to `moda_architect`.

## Architect Review

### Review Status

Pending.

### Review Notes

Portable revised definition; no implementation submitted or accepted.

### Reviewed Files

Source snapshot and task contract only. No execution files reviewed.

### Validation Reviewed

No implementation tests have run as part of this definition.

### Architecture Conformance

To be determined after implementation review.

### Follow-up

Await real task materialisation, execution, Completion Report and Architect review.
