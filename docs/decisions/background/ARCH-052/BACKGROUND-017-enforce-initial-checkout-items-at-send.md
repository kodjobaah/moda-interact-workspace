---
id: ARCH-052-BACKGROUND-017
architecture_id: ARCH-052
title: Enforce mandatory checkout-summary BODY binding in every initial Meta send
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 65
executor: codex
claimed_at: 2026-11-01T18:17:44Z
attempt: 1
depends_on:
  - ARCH-052-ADMIN-004
  - ARCH-052-BACKGROUND-008
  - ARCH-052-BACKGROUND-007
  - ARCH-052-BACKGROUND-005
enables:
  - ARCH-052-SYSTEM-TEST-004
created: 2026-10-31
updated: 2026-11-01
---

# ARCH-052-BACKGROUND-017: Reject initial sends without the checkout-items BODY binding

## Architecture

- Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.
- Owner: `moda_background`, repository `moda-interact-background/`.
- This task is **defined but not materialised**. It MUST NOT begin before the four listed dependencies are architect-accepted Complete, and MUST NOT be implemented in the active BACKGROUND-008 worktree.

## Objective

At the shared recovery template selection, preparation and send boundary, require that every INITIAL `NO_OFFER`, checkout CODE/AUTOMATIC, alternative-product, TEXT or IMAGE message **actually resolves and sends** a nonempty, source-backed abandoned-basket summary in the provider-approved BODY at the originally approved position. If any prerequisite fails, return a typed unavailable/no-send rather than sending a template without checkout items.

## Context

- BG008 is implementing the two-provider initial outreach sender and must remain unmodified while in progress. Its current `AutomatedRecoveryTemplateService` already supplies `{shopId, lineItems: recovery.lineItems}` as `checkoutItems` and freezes semantic preparation through `RecoveryTemplatePreparer`.
- BG005 accepted `formatCheckoutItemsSummary()` and `RecoveryVariableResolver.resolve("checkout.itemsSummary")`; the formatter uses saved tenant-scoped `CheckoutRecovery.lineItems`, at most three displayed lines and a neutral `+N` remainder, with no invented price.
- The current `recovery-template-selection.ts` checks `shop.name` and offer-specific bindings but does not require `checkout.itemsSummary`. `recovery-template-bindings.ts` already validates parameter positions, Meta BODY `{{N}}` placeholders, and immutable content fingerprints.
- ADMIN-004 supplies independently reviewed, translated and approved registration candidates with the exact BODY binding. BG007 adds optional IMAGE-header delivery after BG008, so BG017 runs **after both** to avoid overlapping changes in the same selection/preparation code.

## Scope

Add one Background-local initial BODY binding policy to the existing shared template preparer/send path, with deterministic negative handling for both platforms and all approved header kinds. Do not introduce a new Meta template, database record, Shared contract or alternate sender.

## Out of Scope

- Do not modify active BACKGROUND-008, accepted BG005/ADMIN-003 or existing `_index.md` tasks.
- No new product search, LLM, discount eligibility, provider price verification, image transform, R2 upload, checkout URL generation, Meta template registration or approval.
- Do not alter FOLLOW_UP semantics, WhatsApp contextual inbound routing or HUMAN-mode responses.

## Requirements

### A. Exact owning files and local guard API

Create `src/services/recovery-template-preparation/initial-checkout-items-policy.ts` with this pure, exported, Background-local contract:

```typescript
export type InitialCheckoutItemsBindingDecision =
  | Readonly<{ ok: true; bodyPosition: number | null }>
  | Readonly<{ ok: false; reason: "BINDINGS_INVALID" | "DEFINITION_UNAVAILABLE" }>;

export function decideInitialCheckoutItemsBinding(input: Readonly<{
  stage: "INITIAL" | "FOLLOW_UP";
  parameterBindingsSnapshot: unknown;
}>): InitialCheckoutItemsBindingDecision;
```

Deterministic rules:

1. `FOLLOW_UP`: return `{ ok: true, bodyPosition: null }` without adding new restrictions.
2. `INITIAL`: require a JSON-object frozen snapshot with an array `body`; every element must be a JSON object with an integer 1-based `position`, and the array positions must be contiguous and equal to their indices + 1. Reject malformed/untrusted entries as `BINDINGS_INVALID`.
3. Count entries with `variable === "checkout.itemsSummary"`. Exactly one is required; zero or more than one returns `DEFINITION_UNAVAILABLE`. Return its verified 1-based `bodyPosition`.
4. This helper **does not** reimplement JSON canonicalisation, digest verification, approved Meta component token validation or source-binding semantics. The existing `prepareFrozenComponents()` remains the sole complete frozen-snapshot verifier and checks matching `{{N}}` markers, binding fingerprint and BODY length.

Consume this guard in existing, exact Background files:

- `src/services/recovery-template-preparation/recovery-template-selection.ts`: exclude noncompliant INITIAL registration candidates before locale/purpose approval selection. A matching but noncompliant registration must not be silently replaced with an unapproved or weaker template; respect the current immutable locale/assignment fallback rules and return a typed unavailable result if none qualify.
- `src/services/recovery-template-preparation/recovery-template-preparer.service.ts`: recheck the **selected** frozen registration, then run existing `prepareFrozenComponents()` and `RecoveryVariableResolver` to obtain the actual summary. A missing, empty, malformed, cross-shop or unsafe `CheckoutRecovery.lineItems` value must result in existing `BINDING_VALUE_UNAVAILABLE`/no-send, not a substituted free-text or model-generated basket.
- `src/services/recovery-template-preparation/recovery-template.types.ts`: extend only the **Background-local** prepared-result type with `initialCheckoutItemsBodyPosition: number | null`, set by the verified preparer. A null value is permitted only for FOLLOW_UP. Do not persist this transient witness or add it to Shared.
- `src/services/recovery-template-integration/prepared-template-send.ts`: on any INITIAL `purpose`, require a positive verified body position, exactly one prepared BODY component, and a nonempty TEXT parameter at the corresponding 0-based array index; fail with a typed local admission rejection before constructing a send request. For FOLLOW_UP, retain current transport behaviour. Reuse the existing `FinalTemplateIdentity`/`bindingFingerprint` to prevent substituting a different provider registration after preparation.
- `src/services/recovery-template-integration/automated-recovery-template.service.ts`: reuse the single existing shop-scoped checkout-items input for both Shopify and WooCommerce. Do not re-read products, translate checkout titles with AI, modify source line items, or bypass the current BG008 offer/price/consent/STOP gates.

If a new helper is necessary in `recovery-template-bindings.ts`, limit it to exposing the already-validated position for the prepared registration. Do not copy the existing fingerprint/`{{N}}` validator.

### B. Required variant behaviour

| INPUT | REQUIRED outcome |
|---|---|
| INITIAL NO_OFFER approved TEXT with exactly one BODY basket binding | PREPARED and nonempty basket parameter |
| INITIAL single/multi CODE or AUTOMATIC checkout TEXT | PREPARED with original basket plus approved offer presentation |
| INITIAL ALTERNATIVE_PRODUCT TEXT | PREPARED with **original checkout basket** summary and separate alternative-product parameters |
| INITIAL approved IMAGE variant | Same BODY basket requirement; header media preparation remains independently controlled by BG007 |
| INITIAL with no BODY basket binding, duplicate binding, invalid position, missing BODY token or wrong fingerprint | Typed unavailable/no-send, **never** fallback to any missing-summary template |
| INITIAL with malformed/empty/unsafe/cross-merchant saved line items | `BINDING_VALUE_UNAVAILABLE`/no-send; no Meta send or additional billing commit |
| FOLLOW_UP valid historical template without basket binding | Unchanged behaviour |

The basket summary comes exclusively from the **actual saved checkout lines** of the authenticated shop and recovery generation. Do not infer items from product recommendations or a merchant's generic catalogue. Formatter truncation to first three lines and `+N` remainder is allowed; silently omitting the entire summary is not.

### C. Ordering, races, failure handling and dispatch

- Apply the guard before selecting an IMAGE/TEXT fallback and again to the exact prepared immutable registration used by the final transport. TEXT fallback, language fallback, a NO_OFFER downgrade and IMAGE fallback **may not** remove checkout items; if no compliant provider-approved variant exists, no-send.
- Keep BG008's transactional attempt/receipt and final admission semantics. On checkout generation or items fingerprint change during preparation, existing stale recovery admission wins: do not send previously composed basket content for an obsolete recovery.
- Reuse the existing submission-state, Meta approval, exact WABA/shop/locale, approved-content hash and prepared-send identity checks. No second registration or provider approval simulation.
- Use `@modainteract/moda-interact-shared/logging`. Unexpected database/provider exceptions retain the **actual originating exception** and provider details with necessary redaction and are propagated; never silently catch and continue. Record safe shop/recovery/attempt IDs and typed reason only; do not log product descriptions, customer details, coupon codes or URLs.
- No new queue, per-send AI invocation, price recalculation, external merchant read or billing event. Human responses and the customer voice Reply path are unaffected.

## Work Items

- [ ] Add and test pure INITIAL-only `decideInitialCheckoutItemsBinding()`.
- [ ] Integrate into approved registration selection and selected-template preparation for TEXT and IMAGE, with existing immutable fingerprint verification.
- [ ] Add transient verified BODY-position witness and reject any initial prepared send lacking it.
- [ ] Exercise NO_OFFER, single/multi CODE, AUTOMATIC, ALTERNATIVE_PRODUCT, locale fallbacks, image fallback and cross-shop invalid checkout items.
- [ ] Confirm BG008's final source/price/consent/credit admission checks and follow-up remain unchanged.

## Interfaces / Contracts

**Existing Shared:** `checkout.itemsSummary` from `@modainteract/moda-interact-shared/recovery-template-bindings`; approved Meta registration `parameterBindingsSnapshot.body` and `componentsSnapshot`; existing trusted `CheckoutRecovery.lineItems`. No new cross-service contract or Shared publication.

**Producer:** Admin-004 frozen registration. **Consumer:** Background recovery template selection/preparation/send. **Additional local witness:** `initialCheckoutItemsBodyPosition: number | null`; never persisted or passed to Meta. The actual Meta BODY parameter is the value returned from BG005's trusted formatter. `schemaVersion` remains 1; the existing content/fingerprint identity is authoritative.

## Dependencies

- `ARCH-052-ADMIN-004`: reviewed template authoring invariant.
- `ARCH-052-BACKGROUND-008`: accepted, already developed initial send path; do not merge into its active attempt.
- `ARCH-052-BACKGROUND-007`: accepted optional IMAGE path; prevents a parallel edit to common selection/preparation modules.
- `ARCH-052-BACKGROUND-005`: accepted trusted checkout-items formatter/binder.

## Enables

- `ARCH-052-SYSTEM-TEST-004` — terminal certification of required basket content.

## Acceptance Criteria

- [ ] Each required approved INITIAL variant in both Shopify and Woo sends has exactly one verified `checkout.itemsSummary` BODY binding and the original saved basket displayed at the correct Meta parameter position.
- [ ] NONE of the legacy/missing/duplicate/corrupt/HEADER-only/empty/cross-tenant cases can send a WhatsApp template or commit an additional credit.
- [ ] Offer fallback, NO_OFFER, IMAGE → TEXT, and 20-locale language resolution cannot bypass the binding; lacking a compliant approved variant is typed no-send.
- [ ] No guessed items, offer products substituted as basket contents, false monetary claims or modification to checkout state.
- [ ] Existing FOLLOW_UP message and merchant HUMAN reply remain unaffected; no new Meta or Shared contract.
- [ ] Original provider/SDK errors remain observable through the shared structured logger, not rewritten as guessed causes.

## Validation

- [ ] `tests/unit/services/recovery-template-preparation/recovery-template-preparer.test.ts`: frozen position, mismatches, BODY summary missing/duplicate, missing saved lines and shop mismatch.
- [ ] `tests/unit/services/recovery-template-integration/prepared-template-send.test.ts`: positive and negative final BODY-position admission, follow-up regression.
- [ ] `tests/unit/services/recovery-template-integration/automated-recovery-template.service.test.ts`: all INITIAL offer/target branches, TEXT and IMAGE where approved, no-send and exact shop association.
- [ ] `tests/integration/arch047-recovery-template-preparation.integration.test.ts` and BG008's existing integration harness: saved source lines, locale/Meta registration and no duplicate billing under retry.
- [ ] Changed-file lint, repository-declared TypeScript build/check and `git diff --check`, plus focused tests and disposable PostgreSQL validation. Record command/evidence and environment gaps.

## Stop Condition

When all requirements, checkboxes and required validation pass, write the Completion Report, set this task to `review`, return to `moda_architect`, and **STOP**. Do not reopen BG008 or accepted Admin/Background tasks; no `_index.md` modifications.

## Implementation Notes

Start via the canonical launcher; resolve the implementation repository's dedicated worktree rather than using another task's checkout. Follow BG008/BG007's accepted final source/admission mechanisms and add only the bounded basket-binding invariant. Prefer modular helpers and table-driven fixtures. Do not change Meta template identities, checkout link generation or live provider fetching in this task.

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

BG008 and BG007 will be architect-accepted before this task begins; production send uses the same frozen registration read by the preparer.

### Unresolved Issues

None known.

### Architectural Concerns

None at definition time.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not yet assessed.

### Follow-up

None.
