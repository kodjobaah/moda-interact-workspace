---
id: ARCH-035-API-002
architecture_id: ARCH-035
title: Expose safe Woo recovery policy reads and updates
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 92
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-11
updated: 2026-10-16
---

# ARCH-035-API-002: Expose safe Woo recovery policy reads and updates

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: uploaded `moda-interact-workspace(20261012-082756).zip`; portable developer-reviewed definition, not a claimed/materialised worktree.

## Objective

Allow Woo merchants to edit recovery start delay and follow-up policy using the existing Shop-owned recovery settings and effective policy precedence.

## Context

The previous Shopify/Woo merchant-screen parity assessment showed this specific gap. Reuse the already accepted
ARCH-026 WordPress connection, locale and Shop security foundations and ARCH-027 billing components; do not duplicate
provider-neutral Moda domain state. This task is explicitly authorised as an API write exception to the UI-only ARCH-035 boundary, solely to enable the already approved Recovery Behaviour controls.

## Deterministic implementation specification — mandatory

**Architect contract.** The exact model/column names, paths, API shapes, authentication boundary, state machine and
negative cases below are the implementation target. This section supersedes less-specific high-level text elsewhere
in this task. Agents may split production code into smaller modules, but must not change a public contract, migration
field, ownership rule, or dependency without returning to the architect. If a named existing dependency is absent or
incompatible, **STOP** and report the precise finding; do not silently invent a substitute.

**Files:** new `src/merchant/recovery-policy/{contract,request,service,routes}.ts`, focused unit/route/OpenAPI tests, an opt-in disposable-PostgreSQL transaction test, and
`openapi/woocommerce-merchant-recovery-policy-v1.yaml`; thin `src/index.ts`/installation route wiring. Reuse the fallback defaults from
`src/merchant/recovery-summary/recovery-summary.service.ts` and its effective-precedence semantics,
validated using Shared `parseEffectiveRecoveryPolicy`. Do not change schema: `shopify.ShopSettings` is the existing, shared Shop-keyed
policy row despite its historical schema name; `ShopRecoveryPolicyOverride` remains Platform-Admin-owned.

**Endpoints:** `GET /v1/merchant/recovery-policy` returns exactly
`{schemaVersion:1,revision:string,merchant:{recoveryDelayMinutes,recoveryOfferMode,followUpEnabled,followUpDelayMinutes},effective:{same fields},source:"MERCHANT"|"ADMIN_OVERRIDE",overrideActive:boolean,offerSelectionAvailable:false}`. Both observed `recoveryOfferMode` fields can include historical `FIXED` or `AI_BEST_APPLICABLE`; the API must never falsely report these as `NONE` or expose a Shopify discount identifier. Offer selection remains unavailable. An absent
ShopSettings row returns the Background's actual defaults (30, NONE, false, null), `revision:"UNCONFIGURED"`. `PUT
/v1/merchant/recovery-policy` exact `{expectedRevision,recoveryDelayMinutes,followUpEnabled,followUpDelayMinutes}`,
returning the same GET projection. No client-supplied shopId/source/admin reason, no Shopify discount selector.

**Validation/transaction:** `recoveryDelayMinutes` integer 0..10080; `followUpDelayMinutes` must be null when
disabled, integer 1..10080 when enabled; preserve merchant offer mode `NONE` on initial creation and leave any
existing stored selection untouched only if it is NONE. Under Shop row lock, compare
`ShopSettings.updatedAt.toISOString()` or `UNCONFIGURED` before upsert, return `409 recovery_policy_conflict` for
stale changes. Advance the timestamp monotonically by at least 1 ms for each actual update to avoid identical revisions on back-to-back saves; an identical idempotent replay is read-only. Never write `ShopRecoveryPolicyOverride` or impersonate
`PlatformAdmin`. Read/refresh effective values after every save, including active time-limited admin override. When
Woo has an unsafe historical FIXED/AI setting, report the real observed mode on GET, but reject PUT with `409 recovery_offer_unsupported` rather than overwrite a ShopifyDiscount;
Future Woo offers require separate architectural approval.

**Tests:** missing settings/default, 0/10080/10081, enabled-with-null, disabled-with-positive, stale CAS race, monotonic revision, idempotent replay, admin
override precedence and expiry, wrong Shop/installation, preserved `fixedShopifyDiscountId=null` for Woo, Shopify
policy update unchanged, no uncontrolled creation of a PlatformAdmin row. A disposable PostgreSQL check runs only when `WOO_INSTALLATION_TEST_DATABASE_URL` is set and must never target production.

## High-level scope (non-authoritative summary)

- Read current merchant-configured and effective values, platform-admin override indicators and allowed update ranges; never misrepresent effective settings as editable overrides.
- Add authenticated bounded mutation with compare-and-swap/revision protection for delay and follow-up enabled/delay only, retaining default/category/override precedence and audit.
- Provider-specific recovery-offer controls remain unavailable until separately authorised Woo coupon support; existing historical FIXED/AI_BEST_APPLICABLE settings must be reported accurately on GET and rejected for PUT.
- Do not copy Shopify-only fixedShopifyDiscountId or assign ShopifyDiscount rows to Woo shops.

## Out of Scope

- Coupon ingestion or provider discount application, direct platform-admin override edits, new merchant Settings table unless a precise schema blocker is found.
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

- The Stage 3 integration of the existing `ARCH-035-WOOCOMMERCE-002` shell (not a new dependency blocking its already-built shell).

## Acceptance Criteria

- [ ] Boundary, stale-revision and override precedence tests.
- [ ] Woo shop scope, non-Woo denial and no Shopify discount linkage tests.
- [ ] Read-after-write and Shopify recovery-policy regression tests.
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
widening scope. Shopify's existing merchant form sets a 60-minute *UI* minimum for follow-up, while the Shared
policy validator accepts integer values from 1 minute. Preserve the existing 1..10080 service contract here;
Stage 3 WooCommerce UI should continue matching Shopify's 60-minute form minimum. Therefore, the developer's
50-minute unsaved preview correctly shows an error without indicating a defect in this API.

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

Accepted — retrospective code-based review, 16 October 2026.

### Review Notes

Read/save policy and revision-based update with tenant/override protections.

This is a **retrospective, source-code-based architectural reconciliation** against the developer-provided 2026-10-16 10:58:55 workspace ZIP. The source snapshot is not the historical paired task worktrees or Git branches; an original launcher packet, accepted task commit, Completion Report validation and LocalWP run cannot be reconstructed from it. Retain `attempt: 0` and the original developer/agent Completion Report; no historical execution claim or test pass is manufactured.

### Reviewed Files

- `moda-interact-api/src/merchant/recovery-policy/{service.ts,routes.ts,request.ts,contract.ts}`
- `moda-interact-api/src/merchant/recovery-policy/{service.test.ts,routes.test.ts,service.postgres.test.ts,openapi-contract.test.ts}`
- `moda-interact-api/openapi/woocommerce-merchant-recovery-policy-v1.yaml`

### Validation Reviewed

Test files for route, tenant, pagination, query/contract and (where applicable) PostgreSQL paths inspected but **not executed**: this snapshot has no Node dependencies or database services. OpenAPI path is present. No live/disposable PostgreSQL, lint/typecheck/build or launcher/worktree evidence was available.

### Architecture Conformance

The inspected implementation provides the task's bounded capability and uses the approved architecture/repository boundary. The source-based reconciliation is not a claim of unobserved runtime validation, task worktree isolation or release certification.

### Follow-up

Continue normal work only for other, incomplete ARCH-035 tasks. The terminal SYSTEM-TEST-001 remains blocked until every required UI implementation is Complete.
