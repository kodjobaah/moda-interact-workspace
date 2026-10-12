---
id: ARCH-035-API-011
architecture_id: ARCH-035
title: Establish safe Woo coupon/offer integration contract
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 42
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-026-API-008
enables:
  - ARCH-035-DATABASE-002
  - ARCH-035-API-012
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-API-011: Establish safe Woo coupon/offer integration contract

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: uploaded `moda-interact-workspace(20261011-185536).zip`; task is a portable definition, not a claimed/materialised worktree.

## Objective

Prove the supported Woo coupon-read/applicability contract before enabling Shopify-style fixed or AI-selected discounts for Woo recovery messages.

## Context

The previous Shopify/Woo merchant-screen parity assessment showed this specific gap. Reuse the already accepted
ARCH-026 WordPress connection, locale and Shop security foundations and ARCH-027 billing components; do not duplicate
provider-neutral Moda domain state. The current capability is not established by this task definition.

## Deterministic implementation specification — mandatory

**Architect contract.** The exact model/column names, paths, API shapes, authentication boundary, state machine and
negative cases below are the implementation target. This section supersedes less-specific high-level text elsewhere
in this task. Agents may split production code into smaller modules, but must not change a public contract, migration
field, ownership rule, or dependency without returning to the architect. If a named existing dependency is absent or
incompatible, **STOP** and report the precise finding; do not silently invent a substitute.

**Files:** `src/woocommerce/recovery-offers/{contract,provider-read.service,eligibility.service,routes}.ts`,
dedicated tests and OpenAPI, thin installation route wiring. Consume the existing
`src/woocommerce/rest-read/{provider-connection.service,product-operation}.ts` trust/credential boundary and
ARCH-026-API-008 **only once architect-accepted**; never use Woo SaaS Billing credentials. No writes or new DB model
in this task (DATABASE-002 owns persistence).

**Read contract:** `GET /v1/merchant/recovery-offers/coupons` returns
`{schemaVersion:1,capability:"AVAILABLE"|"NOT_AUTHORISED"|"UNSUPPORTED",coupons:[{providerCouponId,code,description,type,expiresAt,eligible,unavailableReason}],revision}`.
Require current Woo read grant, current credential version and Shop ownership. Only code coupons of explicitly
supported Woo fixed-cart or percent types; reject/omit automatic/manual ambiguous, user/customer-restricted,
product/category-restricted, single-use/expired/usage-exhausted and other restrictions that cannot be validated for a
future checkout. Include bounded reason
`UNSUPPORTED_RESTRICTION|EXPIRED|READ_GRANT_REQUIRED|PROVIDER_UNAVAILABLE|NOT_SELECTABLE` rather than an unsafe
fallback label.

**Proof contract:** `POST /v1/merchant/recovery-offers/verify` exact `{providerCouponId,checkoutKey}` for an
already-Shop-owned lineage returns
`{schemaVersion:1,decision:"ELIGIBLE"|"NONE",providerCouponId|null,code|null,evidenceSha256|null,verifiedAt|null,expiresAt|null}`.
The server reloads coupon via accepted scoped Woo provider read, validates current cart/product restrictions against
exact checkout lineage and current server time; no browser-supplied discount value, percent, code or customer
identity is trusted. The short-lived proof is not proof of final order redemption. If read grant is revoked/expired,
provider times out, HPOS/Blocks capability differs or coupon details are ambiguous, decision is NONE and outward
promises are disabled. Coupon selection save will be added by WOOCOMMERCE-011/API-011 follow-on as an authenticated
**CAS mutation after DATABASE-002**, not silently to this read-only task; record the exact route and owner in the
task handoff.

**Tests:** valid public coupon, expired/over-limit, fixed/percent, individual-use, product/category/customer
restrictions, revoked grant, two Shops with same providerCouponId, proof expiration, unexpected provider API fields,
stale checkout, unsupported Blocks capability, auth failure, no ShopifyDiscount lookup or SaaS billing access. If the
provider read grant doesn't expose proven coupon metadata, STOP and return capability gap instead of inventing coupon
equivalence.

## High-level scope (non-authoritative summary)

- Use the existing ARCH-026 merchant-consented Woo REST read grant, never an unauthorised Store API connection or vendor SaaS Billing credentials.
- Validate coupon code/type/expiry/usage limits/product/category/customer restrictions and safe eligibility under Classic/Blocks/HPOS supported stores.
- Provide bounded shop-scoped available-coupon/eligibility read semantics and precise diagnostics; fail closed to NONE where provider proof is incomplete.
- Document what evidence must be frozen into a recovery offer and why ShopifyDiscount foreign keys cannot be reused.

## Out of Scope

- Auto-creation of Woo coupons, privileged Woo write grants, discounts outside valid provider evidence.
- Other services' implementation code, `docs/decisions/**/_index.md`, and architecture index reconciliation.

## Implementation work items — mandatory

- [ ] Implement **exactly** the named files, routes/models and public DTO fields in the Deterministic implementation specification; do not widen cross-repository ownership.
- [ ] Enforce every declared shop/platform binding, validation boundary, state transition, CAS/idempotency invariant, denial path and privacy restriction.
- [ ] Implement the **specific negative and concurrency test matrix** named in the specification; record actual commands and real results.
- [ ] Prove that affected Shopify behaviour and current ARCH-026/027 Woo onboarding/billing contracts are preserved.
- [ ] Provide a bounded diff, changed-file list, applied migration/Shared package version where applicable, task Completion Report, and clean synchronised implementation/task worktree evidence.

## Cross-repository boundary (common requirements)

- Owning repository: `moda-interact-api`; consume only versioned, accepted cross-repository contracts.
- Hosted Woo identity is the authenticated Shop/installation; no client-controlled `shopId` or Shopify-session authentication. Where browser UI is in scope, transport runs through privileged WordPress REST/PHP with nonce and `manage_woocommerce` capability.
- For merchant display, all 20 supported WordPress UI locales use administrator language with site fallback; this must not change Shop or customer conversation language.
- New or changed externally visible API fields require strict bounded runtime schema validation and a matching OpenAPI/Shared contract owned by the producer.
- No additional external interface is authorised beyond the bounded scope above.

## Dependencies

- `ARCH-026-API-008` must be architect-accepted Complete before this task is claimed.

## Enables

- `ARCH-035-DATABASE-002`
- `ARCH-035-API-012`

## Acceptance Criteria

- [ ] Provider read-grant/revocation, HTTP/local/HTTPS and unsupported coupon capability proofs.
- [ ] Coupon expiry/restriction/ambiguous cart checks with no invalid offer.
- [ ] Source contract and evidence for DATABASE-002 and runtime owner.
- [ ] Scope stays within `moda-interact-api` and preserves approved cross-provider and 20-locale contracts.
- [ ] Baseline, task launcher isolation, implementation commit, parent task report and regression evidence are recorded without false claims for unavailable provider services.
- [ ] `git diff --check` and repository-required build/test/lint commands pass or precise blockers are reported.

## Validation

- [ ] Run repository-declared focused test suites plus full typecheck/lint/build where applicable.
- [ ] Run real integration/black-box provider or disposable database evidence when this task's scope includes that dependency; do not substitute a mocked success.
- [ ] Check tenant isolation, disconnected/revoked credential handling, idempotency and requested negative cases.
- [ ] For Woo UI tasks, run `npm run test:i18n`, `npm run i18n:verify:20`, PHP/JS tests, admin-locale test, `npm run plugin-zip` and manual LocalWP workflow.
- [ ] Verify `git diff --check` and submit the canonical Completion Report; leave all `_index.md` files untouched until explicit reconciliation.

## Stop Condition

When requirements/acceptance and required validation are fulfilled, set the task to `review`, populate the Completion
Report and return to `moda_architect`. Do not begin dependent tasks or change other repositories on this task branch.

## Implementation Notes

Keep production responsibilities in small testable modules; prefer provider-neutral existing ownership to Shopify/Woo
service duplication. Return unexpected cross-repository schema or provider-contract gaps to the architect before
widening scope.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

Dependencies will be rechecked at task claim time; no generated task document itself creates a branch, provider credential, tested artifact or release.

### Unresolved Issues

None identified beyond documented dependencies/provider gating.

### Architectural Concerns

None reported at definition time.

## Architect Review

### Review Status

Pending implementation.

### Review Notes

No implementation reviewed.

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending.

### Follow-up

**Superseded by ARCH-035 UI-only scope revision (11 October 2026).** This definition is historical and MUST NOT be claimed or executed under ARCH-035. Backend/data/event/coupon capabilities require a separately agreed architecture if ever authorised. No implementation was reviewed or accepted.

Return to architect on implementation submission.
