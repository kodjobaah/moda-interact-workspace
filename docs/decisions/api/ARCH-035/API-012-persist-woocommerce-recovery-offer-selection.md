---
id: ARCH-035-API-012
architecture_id: ARCH-035
title: Persist validated Woo coupon selection and expose internal send-time proof
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 36
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-API-011
  - ARCH-035-DATABASE-002
enables:
  - ARCH-035-WOOCOMMERCE-011
  - ARCH-035-BACKGROUND-003
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-API-012: Validated coupon selection and internal runtime proof

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: uploaded `moda-interact-workspace(20261011-185536).zip`

## Objective

Close the explicit API-011 -> DATABASE-002 -> Woo merchant UI/Background selection-and-proof dependency. No user-supplied coupon code becomes authority.

## Deterministic implementation specification — mandatory

**Architect contract.** All fields, endpoints, invariants and tests below are mandatory; incompatible provider
evidence must return to the architect rather than silently changing DATABASE-002.

**Why this task exists:** The original task graph had a consumer/producer hole: WOOCOMMERCE-011 was expected to
persist a Woo coupon selection, but API-011 is a read/validation-only API and DATABASE-002 must land first. This
separate task owns the missing transaction and the bounded Background proof boundary. Depends on accepted API-011 and
DATABASE-002; enables WOOCOMMERCE-011 and BACKGROUND-003.

**Files:** `src/woocommerce/recovery-offers/{selection.service,selection.routes,internal-verification.routes}.ts`,
tests, OpenAPI for merchant selection and a private service contract, config in `src/runtime-config.ts` and binding
in `src/index.ts`. No schema modifications. Use DATABASE-002 `WooCommerceRecoveryCouponSelection` with `ShopSettings`
lock/transaction; derive Shop from authenticated installation, never supplied by merchant.

**Merchant endpoint:** `PUT /v1/merchant/recovery-offers/selection` exact
`{actionId:UUIDv4,expectedRevision:int,mode:"NONE"|"FIXED"|"AI_BEST_APPLICABLE",providerCouponId:string|null}` →
`{schemaVersion:1,revision,mode,selectedCoupon:{providerCouponId,code,verifiedAt}|null}`. Initial mode NONE is always
allowed; FIXED is allowed only if API-011 has a fresh eligible provider read for this Shop and verified coupon ID;
`AI_BEST_APPLICABLE` is disabled with `422 unsupported_offer_strategy` unless API-011 explicitly certifies the
strategy. In one transaction lock Shop, check expected revision, update `ShopSettings.recoveryOfferMode` and set
`fixedShopifyDiscountId=null` on Woo, upsert selection with exactly one monotonically incremented revision. For NONE,
null the coupon fields but retain row/revision. Same actionId+digest returns the saved result using persisted
selection `lastActionId`/`lastActionSha256` (cannot double-select); changed payload with same actionId returns 409.
Selection revision remains monotonic. Use 409 for stale revision/identity, 422 for not eligible, 503 for provider
read unavailable. Do not accept couponCode/value from browser.

**Background-only verification:** `POST /v1/internal/woocommerce/recovery-offers/verify` exact
`{shopId,checkoutKey,attemptId,issuedAt,nonce}` and HMAC-SHA256 of exact method/path/timestamp/nonce/body, keyed with
server-only `MODA_WOO_INTERNAL_API_HMAC_KEY` (>=32 random bytes, same secret in API and Background, never in WP).
Require ±60s clock bound, constant-time MAC and Shop.platform=WOOCOMMERCE, exact Shop-owned CheckoutRecovery/outreach
attempt, and active REST read grant. No browser/installation credential alone can invoke it. Return only
`{schemaVersion:1,decision:"NONE"|"FIXED",providerCouponId,code,evidenceSha256,verifiedAt}` using API-011 coupon
verification re-check for the exact checkout; it does **not** persist a snapshot or mutate credit/discount state. On
service absence/missing key or inaccessible Woo grant, fail closed to NONE (not a claimed approved coupon); log safe
reason only. The HMAC integration is in-scope, not delegated to an unspecified future agent.

**Proofs:** two administrators concurrent select, nonexistent/out-of-plan providerCouponId, revoked read grant, NONE
clears selection/keeps revision, forged shop ID ignored, no ShopifyDiscount rows created, HMAC wrong/expired/replay
(idempotent read), background exact attempt ownership, provider unavailable, and no secret or coupon PII in logs.

## Out of Scope

- Changes to DATABASE-002, Shared activity event, Shopify coupon schema or ARCH-027 SaaS payment/refund APIs.
- Merchant browser invocation of the internal HMAC endpoint, or direct WordPress access to Woo SaaS vendor billing keys.
- Any `docs/decisions/**/_index.md` edits.

## Implementation work items

- [ ] Implement exact read/merchant selection and internal proof boundary.
- [ ] Enforce Shop lock, revision CAS, HMAC/tenant validation and fail-closed provider evidence.
- [ ] Execute all named contract, security, concurrency and revocation tests.
- [ ] Update API OpenAPI/contract tests, record actual Shared/DB dependency versions.
- [ ] Submit clean bounded code and Completion Report for Architect review.

## Dependencies

- `ARCH-035-API-011` accepted Complete.
- `ARCH-035-DATABASE-002` accepted Complete.

## Enables

- `ARCH-035-WOOCOMMERCE-011`
- `ARCH-035-BACKGROUND-003`

## Acceptance Criteria

- [ ] Exact strict public selection DTO and internal HMAC proof contract.
- [ ] No Woo coupon selection can be saved without live ownership/eligibility proof.
- [ ] Revoked/expired proof always returns NONE and cannot be used to promise discount.
- [ ] Shopify discount and Woo SaaS billing paths are untouched.
- [ ] Build, typecheck, lint, focused Postgres/HMAC tests and `git diff --check` actually pass.

## Stop Condition

On success, set status `review`, populate Completion Report and STOP until Architect acceptance.

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

Only accepted API-011 and DATABASE-002 contracts are inputs.

### Unresolved Issues

None identified in task planning.

## Architect Review

### Review Status

Pending implementation.

### Review Notes

No implementation reviewed.
