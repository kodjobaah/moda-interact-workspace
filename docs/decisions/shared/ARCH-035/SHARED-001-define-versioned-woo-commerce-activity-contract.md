---
id: ARCH-035-SHARED-001
architecture_id: ARCH-035
title: Define Woo checkout and order activity contract v1
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 70
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-035-API-008
  - ARCH-035-DATABASE-001
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-SHARED-001: Define Woo checkout and order activity contract v1

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: uploaded `moda-interact-workspace(20261011-185536).zip`; task is a portable definition, not a claimed/materialised worktree.

## Objective

Publish one strict bounded versioned Woo-origin checkout/order event envelope consumed by plugin, API and Background.

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

**Owning files (exact):** `moda-interact-shared/src/woocommerce/activity/v1.ts` (new strict runtime schema and
inferred type), `src/woocommerce/activity/index.ts` (new export barrel), `package.json` exports and `tsup.config.ts`
build entry, plus `src/woocommerce/activity/v1.test.ts`. Follow the existing package export/build convention, publish
a new immutable Shared version, and record its exact package version in API-008 and both plugin producers. No Prisma
implementation here.

**Freeze `woo.activity.v1` before downstream work.** One versioned JSON body, top-level keys only: `contractVersion:
"woo.activity.v1"`, `eventId: UUIDv4`, `kind: CHECKOUT_UPSERT | ORDER_PLACED | ORDER_PAID | ORDER_CANCELLED`,
`checkoutKey: string(1..128)` (server-generated, stable for one Woo checkout lineage), `revision:
integer(1..2147483647)`, `occurredAt: ISO-8601 UTC instant`, `cartKey: string(1..128)|null`, `orderId: decimal
numeric string(1..20)|null`, and `snapshot: CheckoutSnapshot|null`. No browser/provider-supplied `shopId`,
installation credential, or session token in the body; the hosted API derives the shop from the Authorization
principal. Strictly reject unknown keys and excessive JSON/body size (maximum 16 KiB encoded UTF-8).

`CHECKOUT_UPSERT` requires `orderId=null` and a bounded `snapshot` with exactly `currency: /^[A-Z]{3}$/`,
`totalMinor: nonnegative safe integer`, `checkoutUrl: same-origin absolute URL or null`, `lineItems: [0..20]` of
`{productId: numeric Woo ID string, variationId: numeric string|null, quantity: positive integer, title:
string(1..160)}`, `recipientE164: E.164|null`, `whatsappConsentVerified: boolean`, `consentCapturedAt: ISO UTC|null`.
Reject `recipientE164` without verified explicit WhatsApp opt-in and a captured timestamp. There are **no** customer
names, email/address fields, arbitrary metadata, raw Woo objects or free-form nested JSON. A partial checkout with no
phone/url is valid and must never result in invented values. ORDER_* require `snapshot=null`, non-null `orderId` and
exact `checkoutKey` from original order metadata.

**Identity/ordering:** The WordPress producer generates `eventId` once upon durable local enqueue, not once per
transport retry. It increments `revision` per checkout lineage and stores the stable `checkoutKey` on the Woo order
as protected order meta. Event replay uses identical canonical bytes; reuse of eventId with different bytes is
conflict. ORDER_* events are authoritative over late CHECKOUT_UPSERT for that checkoutKey; ORDER_PAID can never be
reverted; order placed/cancelled suppresses outreach for that same lineage. There is no PII-based fuzzy order
matching. The contract does not authenticate the sender; API-008 must enforce installation bearer authentication.

**Tests:** exact-key acceptance and rejection; missing/empty/null/wrong ID; over-16-KiB; invalid ISO dates and
future-skew policy; invalid E.164/consent; malformed URL/foreign-origin; 21 line items; order without matching stable
key; stable byte-for-byte idempotency fingerprint/fixture; all event kinds; no Shopify/WhatsApp contract changes.
Include golden JSON fixtures with both valid partial and terminal examples. **Gate:** downstream task cannot invent a
new field/kind without an architect update to this task and publication.

## High-level scope (non-authoritative summary)

- Define canonical Woo event identity and kinds for cart/checkout upsert, paid/placed order, cancellation or supersession; distinguish event occurrence from repeated delivery.
- Include installation/shop binding, consent-approved customer reachability, provider checkout/cart/order identity, timestamps, currency and minimal line-item snapshots with explicit optionality.
- Normalize or reject malformed/oversized input, forbid fabricated checkout URLs/phone numbers and provide deterministic idempotency/correlation guidance.
- Do not alter Shopify webhook schemas or existing WhatsApp v1/v3 contracts; publish canonical Shared package version before consuming.

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

- Owning repository: `moda-interact-shared`; consume only versioned, accepted cross-repository contracts.
- Hosted Woo identity is the authenticated Shop/installation; no client-controlled `shopId` or Shopify-session authentication. Where browser UI is in scope, transport runs through privileged WordPress REST/PHP with nonce and `manage_woocommerce` capability.
- For merchant display, all 20 supported WordPress UI locales use administrator language with site fallback; this must not change Shop or customer conversation language.
- New or changed externally visible API fields require strict bounded runtime schema validation and a matching OpenAPI/Shared contract owned by the producer.
- No additional external interface is authorised beyond the bounded scope above.

## Dependencies

No blocking task dependency beyond the accepted ARCH-026/027 foundations in the stated snapshot. Confirm current compatible package/DB pins before claiming.

## Enables

- `ARCH-035-API-008`
- `ARCH-035-DATABASE-001`

## Acceptance Criteria

- [ ] Runtime parser/schema, exact negative/boundary and replay identity tests.
- [ ] Version compatibility and package-export/typecheck validation.
- [ ] Published version/consumer pin evidence without hidden local dependency.
- [ ] Scope stays within `moda-interact-shared` and preserves approved cross-provider and 20-locale contracts.
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

Return to architect on implementation submission.
