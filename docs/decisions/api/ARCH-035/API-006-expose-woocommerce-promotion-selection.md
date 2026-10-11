---
id: ARCH-035-API-006
architecture_id: ARCH-035
title: Expose Woo promotional-credit offers and history
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 75
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-035-WOOCOMMERCE-005
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-API-006: Expose Woo promotional-credit offers and history

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: uploaded `moda-interact-workspace(20261011-185536).zip`; task is a portable definition, not a claimed/materialised worktree.

## Objective

Make existing Moda promotional recovery-credit offers, current selection and history accessible to Woo Shops.

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

**Files:** new `src/merchant/promotions/{contract,read.service,selection.service,routes}.ts`, focused tests and
OpenAPI; thin Woo installation route wiring. Reuse Shopify `app/services/promotions/promotion.service.ts` business
constraints but use the existing `PromotionCampaign`, `PromotionCampaignTranslation`, `PromotionalCreditGrant`,
`MerchantPromotionSelection`, `Subscription` records. No new model or Woo coupon mechanic.

**GET `/v1/merchant/promotions?view=OFFERS|HISTORY&page=1&pageSize=6`:** response
`{schemaVersion:1,revision,offers:[{campaignId,title,description,quantity,startsAt,expiresAt,eligible,reason}],selection:{campaignId,selectedAt,remaining,reserved,committed}|null,history:{page,pageSize,total,totalPages,items:[{campaignId,title,status,selectedAt,quantity,remaining}]}}`
with pageSize 6 or 12 and stable `(createdAt DESC,id DESC)` ordering. Display locale may select a
`PromotionCampaignTranslation`, but stored campaign language/eligibility remains unchanged. Shop and plan scope must
match `PromotionTargetScope` and current Subscription; grants are not available after expiry or exhaustedAt.

**PUT `/v1/merchant/promotions/selection`:** exact `{expectedRevision:string,campaignId:string}`; lock Shop and
selected grant, verify campaign ACTIVE/window/current billing plan/shop and unused allowance, then create/select
`PromotionalCreditGrant` once and upsert `MerchantPromotionSelection` through its existing unique Shop FK. Repeated
identical selection is a read-only success (no second grant/quantity); stale differing selection returns `409` using
expectedRevision, and expired or wrong-Shop campaign is denied. Respect reservation and consumption counts (no credit
regrant/reselection reset). The API never mints a campaign or changes ShopifyDiscount.

**Tests:** future/expired campaign, shop-only vs plan-scoped, Free shop on correct plan, concurrent selections, no
double grant, consumed campaign, admin cancelled, translation fallback, bad shop ID/credential, Shopify promotion
regression.

## High-level scope (non-authoritative summary)

- Reuse PromotionCampaign, PromotionalCreditGrant and MerchantPromotionSelection ownership and period/eligibility/lock rules; distinguish credit promotions from Woo coupons.
- Add merchant-safe current offers, available balances, selection state, paginated history and guarded selection command for authenticated Woo Shop.
- Enforce active validity window, plan/shop scope, one-selection/locking, version conflicts and no duplicate grants on retries.
- Do not implement Shopify-specific discount/APP_EVENTS mechanics in this API.

## Out of Scope

- Unrelated Shopify or Woo Billing feature changes; changing another repository in this task.
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

No blocking task dependency beyond the accepted ARCH-026/027 foundations in the stated snapshot. Confirm current compatible package/DB pins before claiming.

## Enables

- `ARCH-035-WOOCOMMERCE-005`

## Acceptance Criteria

- [ ] Active/expired/consumed/locked and concurrent selection tests.
- [ ] Tenant separation, platform eligibility and Woo/Shopify promotion regression.
- [ ] Contract validation and bounded error/no-PII logs.
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
