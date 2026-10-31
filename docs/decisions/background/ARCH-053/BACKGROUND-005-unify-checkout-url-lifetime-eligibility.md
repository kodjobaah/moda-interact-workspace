---
id: ARCH-053-BACKGROUND-005
architecture_id: ARCH-053
title: Enforce one configured recovery lifetime across Background checkout URL paths
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-016-BACKGROUND-005
  - ARCH-053-BACKGROUND-003
  - ARCH-048-BACKGROUND-011
enables:
  - ARCH-053-SYSTEM-TEST-001
created: 2026-10-31
updated: 2026-10-31
---

# ARCH-053-BACKGROUND-005 — Unify checkout URL lifetime eligibility in Background

## Architecture

- Initiative: `ARCH-053`.
- Canonical architecture: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`.
- Coordinator: `moda_architect`.
- Portable definition, **defined but not materialised**: this review environment has no authority to claim a developer worktree, Git branch, commit or push.

## Objective

Use the persisted `public."BackgroundRuntimeConfig"."checkoutRecoveryLifetimeDays"` policy for **all Background checkout URL eligibility decisions**: AI/human conversation wrappers, automated WhatsApp template `checkout.url` binding, and the locked final Woo initial-send permit. Eliminate independent five-minute and seven-day checkout age limits without modifying any other lifecycle or outbound safety rule.

## Context

The 2026-10-31 09:57 snapshot contains three inconsistent Background paths:

1. `src/services/conversation-wrappers/repository.ts` constructor defaults `maxCheckoutAgeMs` to seven days, measured from `CheckoutRecovery.lastExternalActivityAt`.
2. `src/services/recovery-template-preparation/recovery-template-brand.ts` constructor defaults `maxCheckoutAgeMs` to five minutes. `src/services/recovery-template-integration/automated-recovery-template.service.ts` supplies `recovery.updatedAt` as `checkout.observedAt`, even though that timestamp does not prove checkout activity.
3. `src/services/woocommerce-recovery/woo-initial-send-fence.service.ts` locks a recovery and checks its status and `expiredAt`, but does not independently test the current configured inactivity cutoff before issuing the provider-send permit.

`src/services/checkout-recovery-expiry.service.ts` already expires records at `lastExternalActivityAt <= now - configuredLifetimeDays`. Do **not** modify that worker. ARCH-016-DATABASE-002 and ARCH-016-BACKGROUND-005 remove the old 1–90 limit and allow every non-negative whole day value, default 21; this task depends on the accepted ARCH-016 Background policy task.

## Scope

Changes are strictly within `moda-interact-background` and this assigned task file. Required production files (relative to the repository root):

1. **Create** `src/services/recovery-lifetime/checkout-recovery-lifetime.ts`: one pure, injectable-clock-compatible eligibility function and one canonical persisted-policy reader/validator reusable by the wrapper and template paths; do not introduce a service-local general logger.
2. **Modify** `src/services/conversation-wrappers/repository.ts`: eliminate `maxCheckoutAgeMs`, read the canonical policy through the defined port, and use the shared Background helper on `recovery.lastExternalActivityAt`.
3. **Modify** `src/services/recovery-template-preparation/recovery-template-brand.ts`: remove the five-minute constructor option and evaluate `checkout.url` using the same helper and trusted policy provided by the owning integration service. Keep URL, host, tenant and explicit `expiresAt` checks.
4. **Modify** `src/services/recovery-template-preparation/recovery-template.types.ts`: carry the actual `lastExternalActivityAt` evidence and the validated `checkoutRecoveryLifetimeDays` in `TrustedCheckout` (or minimally equivalent, explicitly typed fields); do not carry a caller-supplied or shop-controlled lifetime.
5. **Modify** `src/services/recovery-template-integration/automated-recovery-template.service.ts`: select `lastExternalActivityAt` and `expiredAt` instead of using `updatedAt` as freshness evidence; read policy from the persisted global config; bind the trusted timestamp and policy to template preparation and reject an expired/invalid recovery before building the CTA.
6. **Modify** `src/services/woocommerce-recovery/woo-initial-send-fence.service.ts`: add `lastExternalActivityAt` to the locked recovery `SELECT`; read and validate the canonical `BackgroundRuntimeConfig` row **inside the existing PostgreSQL transaction**, and apply the same strict cutoff before allowing provider dispatch. Do not call Redis/HTTP or fetch another service inside this transaction.
7. **Update** focused tests under `tests/unit/services/conversation-wrappers/`, `tests/unit/services/recovery-template-preparation/`, `tests/unit/services/recovery-template-integration/`, `tests/unit/services/woocommerce-recovery/`, and `tests/integration/woo-initial-send-fence.integration.test.ts` (plus the existing fence-race test if necessary). Only directly affected fixtures are in scope.

Implementation support files needed by the listed paths may be adjusted only to maintain compilation and preserve existing contracts. No API, Admin, Database, Shopify, Shared package, Gateway or WordPress source changes.

## Out of Scope

- No edits to `src/services/checkout-recovery-expiry.service.ts`, the ARCH-016 global setting/validator, database schema/migrations, Admin UI or the ARCH-052 discount verification/freshness policy.
- No additional `checkoutUrlExpiryDays`, token lifetime, message-send-relative expiration, Redis cache, extra outbound message, webhook or queue contract.
- No change to Shopify's provider-generated URL or WooCommerce's `wc_get_checkout_url()` semantics.
- No change to the Woo initial-send permit's existing lock order, consent, STOP, credit, order, template approval, tenant or idempotency guards; no production Woo sending enablement.

## Requirements

### Canonical policy and exact boundary

The sole policy source is the `id = 'default'` row of `public."BackgroundRuntimeConfig"`. Treat `checkoutRecoveryLifetimeDays` as a **non-negative whole number** (0, 1, 21, 91, 180, 365 and larger values representable by the existing PostgreSQL `INTEGER` column), with no application-imposed upper bound. Do not substitute 21 or seven days when the row is absent/invalid. A value of **0 makes every recovery immediately age-ineligible**, even at the observation instant; it does not imply an unlimited lifetime.

For valid `Date` values `activityAt` and `now`, the *only* age predicate is:

```ts
activityAt <= now && now - activityAt < lifetimeDays * 86_400_000
```

Treat the expression as mathematical integer milliseconds, **not** an instruction to use unsafe Number arithmetic or construct an out-of-range `Date`. With large PostgreSQL `INTEGER` values use exact, safe arithmetic (e.g. compare `BigInt(now.getTime()) - BigInt(activityAt.getTime())` against `BigInt(lifetimeDays) * 86_400_000n`) so the allowable configuration range is not accidentally narrowed. Validate both timestamps and the policy; do not round fractional days or clamp high values. At the **exact** cutoff (`now - activityAt === lifetimeMs`), eligibility is false, matching the expiry worker's `lte` cutoff. Any future or invalid activity timestamp is ineligible.

### Required internal interfaces

The single Background-owned helper must expose an explicit, testable signature with semantics equivalent to:

```ts
export function isCheckoutRecoveryWithinLifetime(input: Readonly<{
  lastExternalActivityAt: Date;
  now: Date;
  checkoutRecoveryLifetimeDays: number;
}>): boolean;

export function parseCheckoutRecoveryLifetimeDays(value: unknown): number;

export interface CheckoutRecoveryLifetimeReader {
  read(): Promise<number>; // reads persisted default config and validates it
}
```

The `read()` path is injected for deterministic tests and reads **the canonical persisted global policy**, not a caller-provided day count. Prefer a bounded field-only Prisma read (`backgroundRuntimeConfig.findUnique({where:{id:'default'},select:{checkoutRecoveryLifetimeDays:true}})`) without local hardcoded fallback. A missing or invalid config prevents URL binding/provider-send; an unexpected DB error is logged through `@modainteract/moda-interact-shared/logging` and propagated to the retry-owning boundary. A business ineligibility result is not a silent exception.

In `WooInitialSendFenceService.admitFinalSend`, the policy query is a SQL read against `public."BackgroundRuntimeConfig"` **inside the already-open transaction**, after the existing ordered locks; use an appropriate row lock/read consistency so a concurrent Admin update cannot make a final permit pass against a fabricated policy. Absence/invalidity suppresses provider admission (and logs a bounded reason); unexpected PostgreSQL errors propagate, retaining the current attempt/credit settlement ownership. Do not add external I/O inside the transaction.

### Per-path required behaviour

- **AI and human wrappers:** Keep `shop.status`, `recovery.status`, `expiredAt`, tenant/customer relation and `trustedHttpsUrl(..., shop.domain)` checks. Only expose `checkout.url` when the canonical lifetime predicate succeeds. A valid URL after five minutes or seven days remains eligible if the configured lifetime has not elapsed.
- **Automated template:** Preserve existing frozen template, approved-host, tenant, HTTPS, sender, coupon verification and `checkout.expiresAt` constraints. `observedAt` must be the recovery's **`lastExternalActivityAt`**, not `updatedAt` or message-send time. The configured days must come from the persisted policy and be checked at preparation time, not from merchant inputs. Do not refresh old evidence by changing `updatedAt`.
- **Final Woo send fence:** Read `lastExternalActivityAt` under the recovery row lock and reject at/after the cutoff even if the row is still `DETECTED` because the periodic expiry worker has not run. Keep ALL existing STOP/consent/order/template/credit/provider-permit protections; suppression does not itself issue refunds or change confirmed sends.
- **Observability:** Use the existing Shared Node logger; record bounded reason, recovery/shop identifiers and original dependency error in redacted form. Never emit the bearer checkout URL, token, customer phone, coupon code or raw customer payload. Do not create a competing generic logger.

## Work Items

- [ ] Inspect the canonical ARCH-016 policy implementation, the three existing Background paths and their existing tests before editing.
- [ ] Implement and test the shared Background-only pure lifetime predicate and injected persisted-policy reader.
- [ ] Remove the seven-day wrapper cap and apply the configured cutoff while retaining all existing wrapper security guards.
- [ ] Remove the five-minute template cap and bind `lastExternalActivityAt` plus validated canonical policy instead of `updatedAt`.
- [ ] Add the locked-policy and locked-activity cutoff to the Woo final-send permit without disturbing its transaction and settlement semantics.
- [ ] Add deterministic boundary/security tests and record exact validation commands and worktree/branch evidence.

## Interfaces / Contracts

- **Source:** `public."BackgroundRuntimeConfig"(id='default', checkoutRecoveryLifetimeDays)`; schema and value domain owned by `ARCH-016-DATABASE-002`/`ARCH-016-BACKGROUND-005`. Default 21 days; 0 allowed; no 90-day maximum. This task must consume those accepted changes rather than reimplement them.
- **Timestamp:** `commerce."CheckoutRecovery"."lastExternalActivityAt"` (real checkout activity). `updatedAt` is **not** evidence of validity.
- **Internal helper:** `isCheckoutRecoveryWithinLifetime`, `parseCheckoutRecoveryLifetimeDays` and the `CheckoutRecoveryLifetimeReader` described above; do not publish a new Shared package contract.
- **Template input:** `TrustedCheckout` remains shop-scoped with actual checkout timestamp, validated lifetime, existing `url`, `expiresAt`, `approvedHosts`. Change its local type/tests consistently; it does not alter the Meta wire contract.
- **Provider-send permit:** No change to `WooInitialFinalPermitInput` or external message contract; only an additional locked DB guard.

## Dependencies

- `ARCH-016-BACKGROUND-005` — accepted unrestricted non-negative integer runtime policy (after ARCH-016-DATABASE-002).
- `ARCH-053-BACKGROUND-003` — accepted generation URL issuance.
- `ARCH-048-BACKGROUND-011` — accepted multi-generation Woo send orchestration.

## Enables

- `ARCH-053-SYSTEM-TEST-001` — after all its own dependencies are accepted.

## Acceptance Criteria

- [ ] No checkout URL path retains a five-minute/seven-day literal or a second URL-age setting; other unrelated short-lived evidence rules remain intact.
- [ ] One policy reader and one pure evaluator are reused by wrappers and templates; the Woo SQL permit applies the same evaluator to SQL-locked evidence.
- [ ] Tests for `0`, `1`, `21`, `91`, `180`, `365` and PostgreSQL maximum representable integer; negative/fractional/null/missing policy fails closed.
- [ ] Tests confirm `now < activityAt` is denied, one millisecond before cutoff is eligible, and the **exact** cutoff is denied for wrapper, template and final Woo send.
- [ ] A recovery aged six minutes or eight days (with lifetime 21) can bind a trusted checkout URL, whereas elapsed >=21 days cannot; moving only `recovery.updatedAt` does not refresh eligibility.
- [ ] A shortened Admin lifetime takes effect on subsequent checks, with no dependence on the periodic expiry worker; the default 21 is read from persisted policy, not hardcoded into the binding.
- [ ] Missing/invalid/unavailable policy never authorizes a URL or a final send; unexpected dependency errors are visible and retryable, not swallowed.
- [ ] Existing tenant/domain/HTTPS, generation/lifecycle, template approval, consent, STOP, order, credit, idempotency and concurrency protections pass regression tests.
- [ ] No external network access inside final-send SQL transaction; provider delivery and settlement remain unchanged.
- [ ] No non-Background implementation source, `_index.md` or parent architecture edits by the repository agent.

## Validation

- [ ] `npx vitest run tests/unit/services/conversation-wrappers/woo-checkout-link.test.ts tests/unit/services/recovery-template-preparation/recovery-template-preparer.test.ts tests/unit/services/recovery-template-integration/automated-recovery-template.service.test.ts tests/unit/services/woocommerce-recovery/woo-initial-send-fence.service.test.ts` (plus new pure-helper tests).
- [ ] `node scripts/test-integration.mjs tests/integration/woo-initial-send-fence.integration.test.ts` using disposable test services, including the exact cutoff without an expiry sweep.
- [ ] `npm run lint` and `npm run build` using repository declared scripts and prepared toolchain.
- [ ] `git diff --check`; no `_index.md` changes or cross-repository implementation edits.
- [ ] Completion Report with test counts, actual errors, prepared physical worktree evidence, parent/implementation branch SHAs, DB submodule pin and test-container cleanup.

## Stop Condition

After the Work Items, Acceptance Criteria and Validation are satisfied, update only permitted task execution metadata/Completion Report, set `status: review`, return evidence to `moda_architect` and **STOP**. Do not start another task, modify indexes, update the architecture document or publish/merge branches as a side effect.

## Implementation Notes

This is deliberately **one Background task**: all three call sites must be composed in a single independently reviewable change. The module path names and tests above match the 2026-10-31 09:57 snapshot. The helper is Background-owned because no additional cross-repository runtime mechanism has been approved. This task does not remove or change ARCH-016's runtime bounds itself; ARCH-016 must be complete first.

## Completion Report

### Status

Not Started — defined but not materialised.

### Files Changed

None.

### Work Completed

Not Started.

### Validation Results

Not Run.

### Deviations

None.

### Assumptions

Implementation must re-check the task worktree and accepted ARCH-016 baseline before claim.

### Unresolved Issues

None asserted; return a concrete incompatibility to `moda_architect` rather than inventing an alternate limit.

### Architectural Concerns

None asserted before implementation.

## Architect Review

### Review Status

Pending

### Review Notes

Not reviewed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

To be reviewed.

### Follow-up

None.
