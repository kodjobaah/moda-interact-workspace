---
id: ARCH-052-BACKGROUND-018
architecture_id: ARCH-052
title: Guarantee approved no-offer TEXT outreach after optional enrichment failures
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 70
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-052-BACKGROUND-008
  - ARCH-052-ADMIN-004
  - ARCH-052-BACKGROUND-005
enables:
  - ARCH-052-SYSTEM-TEST-001
  - ARCH-052-SYSTEM-TEST-002
created: 2026-10-31
updated: 2026-11-01
---

# ARCH-052-BACKGROUND-018: Guarantee approved no-offer TEXT outreach after optional enrichment failures

## Architecture

- Initiative: `ARCH-052`; parent document `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.
- Owner: `moda_background`; implementation repository `moda-interact-background/`.
- Defined but not materialised. Do not claim, implement, commit or alter BACKGROUND-008's active worktree until this task's dependencies are architect-accepted Complete and this task is independently prepared.

## Objective

For **sequence-one INITIAL recovery outreach on Shopify and WooCommerce**, guarantee a best-effort **Meta-approved, price-neutral `INITIAL_NO_OFFER` TEXT message containing the original saved checkout items** when AI, MCP, discounts, pricing, alternative products or optional images cannot be verified. This is a fallback from **optional enrichment**, not a bypass of required consent, STOP, recovery/order, moderation, template-approval, credit, final-provider-admission or idempotency gates.

## Context

- BG008 currently calls `AutomatedRecoveryTemplateService.prepare()` before billing/provider admission. In `src/services/recovery-template-integration/automated-recovery-template.service.ts`, `result.kind === "FAILURE"`, `NO_VERIFIED_OFFER.discoveryIncomplete` and certain failed discount/product checks return `kind:"unavailable"`; `src/services/checkout-recovery/recovery-initiation.service.ts` then returns without sending, while the Woo initial template adapter returns `unavailable`. A transient optional tool/model failure may therefore silently lose an otherwise eligible initial message.
- BG005 already owns source-backed `checkout.itemsSummary` formatting from the same shop's durable `CheckoutRecovery.lineItems` (up to three lines plus a remainder). ADMIN-004 owns the approved initial template BODY requirement. BG017 separately guards mandatory checkout-items binding across all initial send paths; do **not** implement another independently maintained BODY-binding validator in this task.
- The canonical source for an actual send is the provider-confirmed `ConversationMessage` and its `recoveryPromise`. BG007 product IMAGE/R2 is optional. ARCH-053 owns checkout URL generation/restoration. ARCH-054's 0–30 minute AI **customer-reply** delay never applies to an initial recovery template or this deterministic fallback.
- A neutral `NO_OFFER` reminder **does not assert that the merchant has no offers**. Incomplete or unavailable discount discovery is neither proof of absence nor permission to advertise a discount.

## Scope

- One Background-local, deterministic `INITIAL_NO_OFFER` TEXT preparation entrypoint shared by the Shopify and Woo initial send orchestrators, with explicit failure disposition and no Agent/MCP/product-media call.
- Route optional enrichment failure to that entrypoint **before** irreversible Meta provider admission; preserve existing guarded send, billing, STOP, consent, recovery and idempotency machinery.
- Retain the original, genuinely originating provider/SDK/MCP error in shared structured logs (with bounded sensitive-data redaction), separate from the internal fallback reason; failures cannot be silently swallowed.
- Focused, injectable unit and two-provider database/dispatch integration tests; no new Schema/Shared/published package, Redis queue, table, message variant or unconditional free-form WhatsApp text.

## Out of Scope

- No changes to active BG008, completed BG005, accepted ARCH-040/ARCH-046/ARCH-047/ARCH-048, ARCH-053 checkout-link generation, ARCH-054 delay, or another domain's task file.
- No new Meta template or unapproved BODY, no generated coupon, no fabricated product/price, no bypass of approved template assignments or locale selection, no new provider/network call from Background to Shopify/WooCommerce.
- No fallback for FOLLOW_UP messages; preserve the confirmed initial promise and existing follow-up semantics.
- No new billing, consent, moderation, provider-send or eligibility engine. No `_index.md` change by the implementing agent.

## Requirements

### A. Exact local types and owning code

Create `src/services/recovery-template-integration/initial-no-offer-fallback.service.ts`. Export **these Background-local interfaces** (names and enum members are normative, not suggestions):

```typescript
import type { PreparedRecoveryTemplate } from "../recovery-template-preparation/recovery-template.types.js";
import type { templateSendFields } from "./prepared-template-send.js";

export type InitialFallbackTrigger =
  | "MERCHANT_MODE_NONE"
  | "NO_VERIFIED_PROMOTION"
  | "AI_UNAVAILABLE"
  | "MCP_UNAVAILABLE"
  | "DISCOUNT_REVALIDATION_UNAVAILABLE"
  | "DISCOUNT_INVALID_OR_INCOMPATIBLE"
  | "PRICE_UNVERIFIABLE"
  | "ALTERNATIVE_PRODUCT_UNVERIFIABLE"
  | "IMAGE_UNAVAILABLE";

export type InitialFallbackResult =
  | Readonly<{
      kind: "PREPARED";
      trigger: InitialFallbackTrigger;
      prepared: PreparedRecoveryTemplate;
      send: ReturnType<typeof templateSendFields>;
    }>
  | Readonly<{
      kind: "BLOCKED";
      reason: "INELIGIBLE_RECOVERY" | "INVALID_ATTEMPT" |
        "CHECKOUT_ITEMS_UNAVAILABLE" | "TEMPLATE_UNAPPROVED" |
        "APPROVED_BINDING_UNAVAILABLE" | "MERCHANT_OR_SENDER_MISMATCH";
    }>
  | Readonly<{
      kind: "RETRY";
      reason: "REQUIRED_STATE_UNAVAILABLE" | "PROVIDER_OUTCOME_UNCERTAIN";
    }>;

export interface InitialNoOfferFallbackPort {
  prepare(input: Readonly<{
    shopId: string;
    recoveryId: string;
    outreachAttemptId: string;
    trigger: InitialFallbackTrigger;
  }>): Promise<InitialFallbackResult>;
}
```

Implement `InitialNoOfferFallbackService` behind this port. Use injectable DB reader, `RecoveryTemplatePreparer`, configured WABA resolver and clock; the production singleton may adapt existing services but MUST NOT call `initialOutreachOfferSelectionService`, `CommerceModelInvoker`, MCP, discount catalogue, BG016 price/product reads or BG007/R2. Do not accept merchant-provided `shopName`, `checkoutItems`, `checkoutUrl`, `verifiedOffer`, provider template name or WABA in input; resolve trusted current values from existing shop/recovery/attempt persistence.

In `prepare()`: verify the attempt belongs to the exact shop/recovery, is sequence 1 and has no provider-confirmed initial message. Read the current recovery generation, shop identity, status, stored lineItems, persisted checkout URL, default language and current configured sender using the existing sources. Invoke `RecoveryTemplatePreparer.prepare()` with `stage:"INITIAL"`, `promotionTarget:"CHECKOUT"`, `offerPresentation:"NO_OFFER"`, **TEXT-only** approval selection, `verifiedOffer` absent and `promotionalProduct` absent; reuse existing `checkout.itemsSummary`, `shop.name`, and `checkout.url` bindings and `templateSendFields(prepared, {kind:"NO_OFFER"})`. Retain the exact approved checkout CTA parameter; do not add ARCH-052 URL validation or construct a new URL. If the original basket summary cannot be bound as nonempty approved BODY text, return `BLOCKED` without any send. Do not create an independent BODY-position rule: BG017 owns that final policy. Resolve any optional customer greeting/name from the same trusted database context, never from the model or fallback caller.

Existing `RecoveryTemplatePreparer` selects only approved registrations and verifies content hashes and locale bindings. If the right TEXT `INITIAL_NO_OFFER` assignment is missing, unapproved, drifting, disabled, incorrectly bound, or cannot include the original basket, return `BLOCKED` with an exact local diagnostic rather than selecting an unapproved variant or a different merchant's registration. Missing required storage/configuration reads are `RETRY`, not fabricated proof of eligibility. The fallback never advertises a coupon, savings, prices, an alternative product or a claim that discounts were exhaustively checked.

### B. Deterministic selection and failure taxonomy

Add `src/services/recovery-template-integration/initial-outreach-fallback-selection.ts` with **this exact pure interface**:

```typescript
import type { InitialFallbackTrigger } from "./initial-no-offer-fallback.service.js";

export type InitialOutreachFailureInput =
  | Readonly<{ kind: "OPTIONAL_ENRICHMENT_FAILURE"; trigger: InitialFallbackTrigger; beforeProviderAdmission: true }>
  | Readonly<{ kind: "MANDATORY_SEND_BLOCK"; reason:
      "STOP" | "CONSENT" | "TERMINAL_RECOVERY_OR_ORDER" |
      "WRONG_SHOP_OR_RECIPIENT" | "MODERATION" | "BILLING_OR_CAPACITY" |
      "TEMPLATE_NOT_APPROVED" | "CHECKOUT_ITEMS_UNAVAILABLE" }>
  | Readonly<{ kind: "TRANSIENT_REQUIRED_STATE"; reason:
      "DB_OR_CONFIG_UNAVAILABLE" | "CURRENT_RECOVERY_UNVERIFIABLE" }>
  | Readonly<{ kind: "PROVIDER_OUTCOME_UNCERTAIN" }>;

export type InitialFallbackDecision =
  | Readonly<{ action: "PREPARE_NO_OFFER_TEXT"; trigger: InitialFallbackTrigger }>
  | Readonly<{ action: "DO_NOT_SEND"; reason: Extract<InitialOutreachFailureInput,
      {kind:"MANDATORY_SEND_BLOCK"}>["reason"] }>
  | Readonly<{ action: "RETRY_EXISTING_ATTEMPT"; reason: Extract<InitialOutreachFailureInput,
      {kind:"TRANSIENT_REQUIRED_STATE"}>["reason"] }>
  | Readonly<{ action: "RECONCILE_EXISTING_SEND" }>;

export function classifyInitialOutreachFallback(
  input: InitialOutreachFailureInput,
): InitialFallbackDecision;
```

Map each discriminant to the identically ordered action above. A `beforeProviderAdmission:false` optional failure is **not representable** and cannot enter the fallback branch. Callers must first map their existing BG008 typed outcomes to one of the four discriminants, based on the actual operation boundary: model/MCP/discount/product/price/R2 results are optional; consent, STOP, recipient, terminal order/recovery, moderation, WABA, billing and immutable-template approval are mandatory. A trusted basket generation or ownership mismatch MUST cause a fresh current-state read; an inconclusive read maps to `TRANSIENT_REQUIRED_STATE`, not to optional failure. Classification MUST NEVER use a provider error string or guess whether Meta accepted an already issued request. Preserve the provider's actual exception and `cause` separately in the shared log.

- `NONE` mode: directly prepare approved `INITIAL_NO_OFFER` TEXT without calling MCP/AI.
- `FIXED` or AI mode: if the optional decision is unavailable, incomplete, times out, throws inside an explicitly optional boundary, or proposed offers fail source/pair/price verification, prepare `INITIAL_NO_OFFER` TEXT immediately. Do not wait for a repeated optional MCP/AI retry before attempting a valid neutral reminder.
- If a subset remains conclusively supported and approved, BG008 may send that subset; otherwise use TEXT fallback. `NO_VERIFIED_OFFER` with `discoveryIncomplete:true` is **not a send prohibition**: it may result in neutral TEXT but never in the assertion that the catalogue contains no offers.
- If the basket generation/checkout ownership changes, re-read current durable recovery/attempt state before fallback; never send the old basket's text. If the required current state cannot be established, return `RETRY`, not `PREPARED`.
- An F1/F2/F3 discount-only source failure before provider admission may trigger independently prepared neutral TEXT after fresh mandatory checks; F3 failure of required consent/STOP/recovery/order/billing/identity or an unknown DB state may **not** be downgraded to an optional failure.
- A failure after potentially irreversible provider admission (Meta timeout/unknown acknowledgment, admission receipt `PENDING`, or unknown provider outcome) MUST NOT trigger another template send. Reconcile the existing message/idempotency record first. A definitely rejected Meta request follows the existing provider-retry/compensation policy, not an immediate duplicate fallback attempt.

### C. Both existing delivery paths, one send and one credit

Modify **only** the existing initial paths:

- `src/services/checkout-recovery/recovery-initiation.service.ts`: when BG008's prepared optional template is unavailable, invoke the fallback service before billing admission instead of returning without an attempt; keep the **same** `RecoveryOutreachAttempt` and `recovery-outreach:${attempt.id}` idempotency key. The existing consent, STOP, recovery lifetime, recipient, capacity, final admission, moderation and credit checks remain authoritative both before and immediately before dispatch.
- `src/services/woocommerce-recovery/woo-recovery-outreach.adapters.ts`: adapt `templates.select` so an optional preparer failure selects the independently approved fallback. `src/services/woocommerce-recovery/woo-recovery-outreach.service.ts` retains its existing `WooGuardedInitialSender` final SQL consent/STOP + terminal-order fence and exactly-once attempt lifecycle. A temporary optional failure must not become an irreversible `suppressed`/`FAILED` attempt without trying the safe fallback.
- `src/services/recovery-template-integration/automated-recovery-template.service.ts`: do not disguise optional result failures as mandatory configuration failures. Reuse the new, typed fallback decision or make its optional failure explicit for both callers. Do not change the FOLLOW_UP path. Do not call the offer agent a second time on fallback, and do not open another conversation.

If an optional enhancement fails *after credit reservation but before provider admission*, reuse or safely release/re-admit the same reservation according to the existing billing contract; never reserve two billable initial conversations. If a mandatory pre-send check fails, release according to the existing compensation path. Only a provider-confirmed outbound message may finalize the attempt and its `ConversationMessage.content.recoveryPromise:{kind:"NO_OFFER"}`. No confirmed send means no promised coupon, no false `sentAt`, and no extra follow-up scheduling.

### D. Required send prohibitions and retries

A customer STOP (including the existing quoted-merchant vs standalone/all-registered-merchants policy) always blocks relevant outreach. Missing/withdrawn consent, terminal or superseded recovery/order, wrong recipient/tenant, moderation failure, credit/capacity denial, invalid WABA/Meta registration and missing approved TEXT template also prohibit sending or require the existing retry/reconciliation path. The business objective is **attempt an eligible approved reminder regardless of optional enrichment failures**, not violate WhatsApp permission, Meta approval or durable admission rules.

- **Optional failure**: immediate price-neutral fallback; no extra message or credit and no endless AI/MCP retry loop.
- **Transient mandatory state failure**: preserve original error; schedule only the existing bounded BullMQ retry under the original attempt identity. Do not convert it to `NO_OFFER` eligibility or mark an unconfirmed attempt sent.
- **Missing approved fallback template**: durable `CONFIGURATION_BLOCKED` diagnostic and merchant/internal support visibility through existing notification facilities where permitted; no unapproved free-form text.
- **Unknown Meta send**: preserve pending provider outcome and reconcile using existing idempotency/admission; never launch a second fallback send merely because the response timed out.
- **Permanent prohibition**: no fallback, no Meta call; preserve the correct billing and attempt state.

### E. Logging and latency budget

Use `@modainteract/moda-interact-shared/logging`, with bounded shop/recovery/attempt IDs, offer mode, trigger, local disposition, original provider/SDK `Error` and `cause`, provider status/request ID where known, and a **separate** internal reason. Preserve original error text after required redaction; never invent a provider explanation or silently swallow unexpected exceptions. Do not log raw customer names/numbers, item descriptions, coupon codes, checkout or product URLs, tokens, prompts or entire unfiltered provider payloads. Preserve existing observability failure isolation. Never hold a database transaction or BullMQ worker open to wait for AI/MCP retry; fallback should use the existing send path promptly when optional processing is unsuccessful.

## Work Items

- [ ] Create the typed, injectable fallback service and pure, stage-aware failure classifier in the exact files above.
- [ ] Verify current recovery/attempt/shop and prepare independently Meta-approved `INITIAL_NO_OFFER` TEXT using persisted basket, shop and checkout CTA only.
- [ ] Integrate the same fallback service into Shopify and Woo **initial** paths before irreversible provider admission; preserve all final guards and the existing receipt/credit identity.
- [ ] Make optional failure types observable without converting uncertain Meta sends or mandatory check failures into fallback.
- [ ] Add named unit, integration and failure-injection tests and record exact validation evidence.

## Interfaces / Contracts

- Producer: `AutomatedRecoveryTemplateService.prepare()` and BG008's optional offer result; consumer: the new `InitialNoOfferFallbackService` and the existing Shopify/Woo initial-send adapters.
- Reused: `RecoveryTemplatePreparer`, `RecoveryTemplatePreparationInput`, `PreparedRecoveryTemplate`, `templateSendFields`, BG005 `checkout.itemsSummary`, accepted Admin `INITIAL_NO_OFFER` TEXT registration, existing merchant policy and guarded provider-admission/credit contracts.
- No Shared/Zod/public HTTP/MCP/queue or new Prisma contract. All new types are local to `moda-interact-background` and the source code paths above.

## Dependencies

- `ARCH-052-BACKGROUND-008`: completed, accepted, with its existing initial-send integration.
- `ARCH-052-ADMIN-004`: completed, accepted, with independent approved `INITIAL_NO_OFFER` TEXT authoring contract. **Meta registration approval must additionally be verified at runtime; task acceptance is not provider approval.**
- `ARCH-052-BACKGROUND-005`: completed, accepted, for canonical saved basket summaries.
- BG017 is independently responsible for the final all-variant mandatory checkout-items binding gate; this task does not duplicate its guard. Terminal system tests depend on both BG017 and BG018. BG007 IMAGE is an optional runtime enhancement and is **not** a direct dependency for implementing TEXT fallback.

## Enables

- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] NONE, FIXED and AI modes send exactly one approved `INITIAL_NO_OFFER` TEXT reminder with actual merchant identity, nonempty saved checkout summary, Reply text/voice guidance and original stored checkout CTA when no supported promotion can be prepared due to optional services.
- [ ] For one and three proposed discounts, invalid coupons, unsupported stacking, partial/incomplete catalogue, MCP timeout, AI refusal/exception, BG016 incomparable pricing, wrong alternative-product proof and BG007/R2 failures lead to a safe source-supported subset or prompt neutral TEXT fallback, never unsupported coupon/price/image claims.
- [ ] F1/F2/F3 optional source drift cannot send stale promotional terms; mandatory state drift fails closed or retries. Follow-up remains unchanged.
- [ ] STOP, no consent, completed/cancelled/superseded recovery/order, bad recipient/shop, moderation or billing denial, missing approved Meta template and unknown provider admission NEVER bypass normal send controls.
- [ ] The same attempt, idempotency key, provider-confirmed `recoveryPromise`, single credit and durable recipient/merchant association are used. No second send after a provider-uncertain outcome, no double reservation and no extra proactive follow-up.
- [ ] Exact originating MCP/AI/Meta/Prisma error (when available) is retained in structured logs subject to redaction; internal fallback reason is separate; the customer does not receive raw diagnostics.
- [ ] No new provider product API, checkout URL validator, Redis queue, database schema, generic logger, uncontrolled retry or cross-tenant data access is introduced.

## Validation

- [ ] `tests/unit/services/recovery-template-integration/initial-no-offer-fallback.service.test.ts`: all triggers, trusted basket/attempt/merchant, no MCP/AI/R2 calls, approved frozen TEXT, unavailable template/empty basket, wrong shop and stable CTA.
- [ ] `tests/unit/services/recovery-template-integration/initial-outreach-fallback-selection.test.ts`: operation/stage-based classification, F1/F2/F3, consent/STOP, DB failure, provider accepted/unknown, one-shot fallback.
- [ ] `tests/unit/services/recovery-template-integration/automated-recovery-template.service.test.ts`: optional `FAILURE`, discoveryIncomplete and null/invalid alternative -> typed fallback, and unchanged FOLLOW_UP.
- [ ] `tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts`: Shopify initial fallback through actual billing and idempotent send composition, changed basket, revived STOP, post-reservation failure, duplicate callback and no confirmed send.
- [ ] `tests/unit/services/woocommerce-recovery/woo-recovery-outreach.service.test.ts` and `tests/integration/arch048-woo-initial-outreach.integration.test.ts`: Woo guarded sender, terminal-order fence, consent/STOP, optional model/MCP failure, provider unknown/retry and one confirmed attempt.
- [ ] PostgreSQL-backed final admission tests for both platforms; inject at least one distinct real provider-origin error and redacted secret, validate one send/credit and no stale promises. Execute task-required actual repository unit, lint, typecheck, build and whitespace scripts; record any unrun integration prerequisites in the Completion Report.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, update the Completion Report, set status to `review`, return control to `moda_architect` and **STOP**. Do not begin an enabled task, modify domain `_index.md`, merge branches or push main.

## Implementation Notes

Treat the approved no-offer template as a **neutral basket reminder**; do not assert that discount discovery was exhaustive. `stage:"INITIAL"` only. The canonical Meta-approved template is mandatory even when AI/MCP is down; plain WhatsApp free text is not an allowed substitute for an outbound business-initiated template. Use existing per-shop sender and merchant policy sources, not caller-provided tenant text. Existing follow-up message-count and human reply handling must remain unchanged. Respect task-worktree isolation and shared structured logging conventions.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-background/src/services/recovery-template-integration/initial-no-offer-fallback.service.ts` (new)
- `moda-interact-background/src/services/recovery-template-integration/initial-outreach-fallback-selection.ts` (new)
- `moda-interact-background/src/services/recovery-template-integration/automated-recovery-template.service.ts`
- `moda-interact-background/src/services/recovery-offers/initial-outreach-offer-selection.service.ts`
- `moda-interact-background/src/agents/initial-outreach-offer.agent.ts`
- `moda-interact-background/src/services/checkout-recovery/recovery-initiation.service.ts`
- `moda-interact-background/src/services/woocommerce-recovery/woo-recovery-outreach.adapters.ts`
- `moda-interact-background/src/services/woocommerce-recovery/woo-recovery-outreach.service.ts`
- `moda-interact-background/tests/unit/services/recovery-template-integration/initial-no-offer-fallback.service.test.ts` (new)
- `moda-interact-background/tests/unit/services/recovery-template-integration/initial-outreach-fallback-selection.test.ts` (new)
- `moda-interact-background/tests/unit/services/recovery-template-integration/automated-recovery-template.service.test.ts`
- `moda-interact-background/tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts`
- `moda-interact-background/tests/unit/services/woocommerce-recovery/woo-recovery-outreach.service.test.ts`
- `moda-interact-background/tests/integration/arch048-woo-initial-outreach.integration.test.ts`
- `moda-interact-background/tests/integration/fixtures/arch048-woo-outreach.fixture.ts`
- `moda-interact-background/tests/integration/fixtures/woo-approved-initial-template.fixture.ts`

### Work Completed

- Added the task-normative local fallback result/port and pure classifier for optional enrichment failure, mandatory block, transient required state, and provider uncertainty.
- Added injectable fallback preparation that re-reads current shop, recovery and sequence-one attempt state; checks durable provider dispatch identity; formats only saved basket data; uses persisted checkout URL and current WABA; and prepares the approved `INITIAL_NO_OFFER` TEXT through the existing preparer. Missing approval/binding fails closed and missing approved registration records a durable configuration diagnostic.
- Routed merchant `NONE` mode directly to the shared fallback and routed eligible optional enrichment failures to that same fallback without another offer-agent call. Shopify and Woo keep their existing attempt, billing/credit, idempotency, final consent/STOP, recovery/order and provider-admission/reconciliation guards. FOLLOW_UP is unchanged.
- Preserved originating AI/MCP errors and causes through shared structured logging with existing redaction conventions.
- Added focused classifier, fallback, coordinator and both-provider send-composition unit tests. Updated the disposable Woo integration registration to exercise the required saved-basket BODY and persisted checkout CTA bindings.
- Implementation commit `a0a1a55` (`feat(background): add initial no-offer fallback`) was pushed to `task/ARCH-052-BACKGROUND-018` in `moda-interact-background`.

### Validation Results

- Focused five-suite Vitest run: passed, 5 files / 136 tests.
- `npm run test:unit`: passed, 333 files / 3,592 tests.
- `npm run lint`: passed.
- `node node_modules/.pnpm/typescript@6.0.3/node_modules/typescript/bin/tsc --noEmit`: passed.
- `node scripts/test-integration.mjs tests/integration/arch048-woo-initial-outreach.integration.test.ts`: passed, 1 file / 18 tests using disposable PostgreSQL and Redis.
- `git diff --check`: passed.
- `npm run build`: Prisma generation completed, but the script could not find the repository-local `tsc` executable shim. Direct invocation of the installed TypeScript compiler passed as noted above.
- No dedicated Shopify PostgreSQL initial-dispatch integration test exists in this repository; Shopify fallback composition and billing/idempotency/finalization were validated by the focused unit suite, but the task's requested Shopify PostgreSQL-backed validation remains outstanding.

### Deviations

- The task's two-provider PostgreSQL integration validation is incomplete because the repository provides a disposable PostgreSQL/Redis integration harness only for Woo initial outreach. No new Shopify integration harness was added within this task.
- The full broader matrix of every named optional source failure, adversarial mandatory-policy race and downstream system certification was not executed. The existing named acceptance/validation checkboxes remain unchanged for architect review.

### Assumptions

- Runtime availability and approval of the per-shop `INITIAL_NO_OFFER` Meta registration remain external operational prerequisites; the implementation checks current assignment/registration and fails closed when unavailable.

### Unresolved Issues

- Add or run a Shopify PostgreSQL-backed initial-dispatch integration covering fallback, billing identity, durable idempotency and confirmed finalization.
- Review typed reason-code routing in `AutomatedRecoveryTemplateService` against all BG008 optional and mandatory failure boundaries; unrecognized outcomes currently fail closed.

### Architectural Concerns

Architect Review remains Pending. No schema, Shared/public contract, queue, provider API, checkout URL issuance/validation or other repository was changed. The launcher prepared Attempt 1 for `copilot`, passed the dependency gate, and initialized the implementation database submodule at `7c377282aa5819b3008b7d7f3018f44f4161523e`. Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-BACKGROUND-018`; implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-BACKGROUND-018`. Both task branches are `task/ARCH-052-BACKGROUND-018`. The shared/default workspace checkout was not used for task implementation. Parent claim commit: `993aff77062e3c9def8650ca74e464b4a6189191`.

### Attempt 2 Completion Report

#### Status

Ready for architect review. Attempt 1's review and evidence above are preserved; the four requested implementation and validation corrections are addressed below. This report does not make an architect acceptance decision.

#### Files Changed in Attempt 2

- `moda-interact-background/src/agents/initial-outreach-offer.graph.ts`
- `moda-interact-background/src/services/recovery-offers/initial-outreach-offer-selection.service.ts`
- `moda-interact-background/src/services/recovery-template-integration/automated-recovery-template.service.ts`
- `moda-interact-background/tests/unit/agents/initial-outreach-offer.graph.test.ts`
- `moda-interact-background/tests/unit/services/recovery-offers/initial-outreach-offer-selection.service.test.ts`
- `moda-interact-background/tests/unit/services/recovery-template-integration/automated-recovery-template.service.test.ts`
- `moda-interact-background/tests/unit/services/recovery-template-integration/initial-no-offer-fallback.service.test.ts`
- `moda-interact-background/tests/integration/arch052-shopify-initial-no-offer-dispatch.integration.test.ts` (new)

#### Work Completed

- Confirmed the implementation task branch includes BG017 via merge `e1933b7` (including `42f1f88`) and retained its mandatory checkout-items BODY binding guard. Updated the fallback unit fixture to supply the required saved-items BODY position; no competing BODY-position policy was introduced.
- Restricted thrown-error fallback to retryable `CommerceHostError("UNAVAILABLE")` and typed `CommerceModelInvocationFailure` at `model.invoke`. In the graph, that model failure is represented by the exact typed `UNAVAILABLE / AI_UNAVAILABLE / retryable` result. Coordinator failure-result handling now uses exact typed code/reason/retryable combinations; denied, configuration, invalid-result, generic graph-operation and non-retryable failures remain unavailable and do not prepare fallback.
- Added graph, selection and coordinator regressions for typed optional failures and unknown/mandatory failure propagation.
- Added a disposable PostgreSQL Shopify dispatch integration. It exercises persisted consent, approved `INITIAL_NO_OFFER` template registration and checkout bindings, recovery attempt, billing reservation, final outbound permit, provider-confirmed message and finalization. Moderation is stubbed only at its assessment boundary because the disposable environment has no platform moderation credentials; the PostgreSQL send fence and provider-delivery path remain active. A required-consent denial case proves no recovery, attempt, reservation or provider call is created.
- Implementation commit `6858b12` (`fix(background): tighten initial fallback failure routing`) was pushed to `task/ARCH-052-BACKGROUND-018`.

#### Validation Results

- `npx vitest run tests/unit/agents/initial-outreach-offer.graph.test.ts tests/unit/services/recovery-template-integration/automated-recovery-template.service.test.ts`: passed, 2 files / 46 tests.
- `npx vitest run tests/unit/services/recovery-template-integration/initial-no-offer-fallback.service.test.ts`: passed, 1 file / 16 tests.
- The focused offer-selection, coordinator, Shopify recovery-initiation and Woo initial-outreach unit suites passed, 4 files / 81 tests. The complete final unit run passed 3,611 of 3,612 tests across 334 files; its sole failure is the existing unrelated `tests/unit/services/recovery-template-preparation/arch049-frozen-image-binding.test.ts` expectation for `NO_APPROVED_ASSIGNMENT`, where the current preparer returns `DEFINITION_UNAVAILABLE`.
- `node scripts/test-integration.mjs tests/integration/arch052-shopify-initial-no-offer-dispatch.integration.test.ts tests/integration/arch048-woo-initial-outreach.integration.test.ts`: passed, 2 files / 21 tests (2 Shopify PostgreSQL and 19 Woo PostgreSQL/Redis).
- `npm run lint`: passed.
- The unmodified `npm run build` initially found the pnpm-store compiler but no `node_modules/.bin/tsc` shim (`sh: tsc: command not found`). The complete declared build then passed with the installed TypeScript 6.0.3 compiler temporarily exposed on PATH: `PATH="$PWD/node_modules/.pnpm/typescript@6.0.3/node_modules/typescript/bin:$PATH" npm run build`. Prisma generation and `tsc` both completed; no package or lockfile change was required.
- `git diff --check`: passed.

#### Attempt 2 Handoff

Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-BACKGROUND-018`; implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-BACKGROUND-018`. Both task branches are `task/ARCH-052-BACKGROUND-018`. The Attempt 2 parent claim commit `3756ac7c41effef37558584903e1a82299aa9feb` was pushed before implementation; this report follows implementation commit `6858b12`. Attempt 2 does not merge either task branch to `main`, modify another repository, or alter the Attempt 1 Architect Review.

## Architect Review — Attempt 1

### Review Status

Changes Requested — Attempt 1. The task returns to `ready`; `executor` and
`claimed_at` are cleared. Attempt 1 and its validation evidence remain
preserved.

### Review Notes

The design and implementation cover the intended neutral fallback, retain the
existing send and billing identity, and provide strong unit and Woo integration
evidence. Acceptance is blocked by the following issues:

1. **[P1] Reconcile with the merged BG017 implementation.** The implementation
   branch is three commits behind current `origin/main`. BG017 has since merged
   changes to the same preparation, selection, prepared-send and orchestration
   files; the current `origin/main` diff removes the fallback implementation
   and replaces portions of those shared paths with the mandatory basket guard.
   Rebase/merge onto the current main and preserve both the fallback and BG017
   guard, then rerun affected validation. The current submitted tree is not the
   integrated source that would result from acceptance.
2. **[P1] Add the required Shopify disposable PostgreSQL dispatch proof.** The
   task explicitly requires PostgreSQL-backed final-admission coverage for
   both platforms. Attempt 1 has Woo PostgreSQL/Redis integration coverage and
   Shopify unit coverage only. Add or use a disposable Shopify integration
   path that proves fallback, the same attempt/idempotency identity, one credit
   and provider-confirmed finalization, plus mandatory no-send behavior.
3. **[P1] Do not classify every thrown agent error as optional.**
   `InitialOutreachOfferSelectionService.resolve()` maps every thrown error
   from `this.agent()` to `AI_UNAVAILABLE`, except `CommerceHostError`, which
   maps to `MCP_UNAVAILABLE`. Unknown/programming or required-state errors can
   therefore enter the fallback path without evidence that they are optional.
   Classify only recognized model/MCP optional failures; propagate or return a
   retry disposition for unrecognized errors, and add a regression test proving
   they do not send a fallback template.
4. **[P2] Complete the declared build validation.** `npm run build` did not
   complete because the local `tsc` shim was missing. Direct `tsc --noEmit`
   passed, but it does not verify the repository build script. Restore the
   prepared local build tooling and rerun `npm run build`, or record a
   reproducible environment cause and a supported equivalent for the complete
   build command.

The reported full unit run, lint, direct TypeScript compilation, Woo
PostgreSQL/Redis integration and emulator tests are useful evidence. No
architect acceptance decision is made until the source is reconciled with
BG017, the Shopify database path is covered, and failure classification is
safe for unknown errors.

### Reviewed Files

- `src/services/recovery-template-integration/initial-no-offer-fallback.service.ts`
- `src/services/recovery-template-integration/initial-outreach-fallback-selection.ts`
- `src/services/recovery-template-integration/automated-recovery-template.service.ts`
- `src/services/recovery-offers/initial-outreach-offer-selection.service.ts`
- `src/services/checkout-recovery/recovery-initiation.service.ts`
- `src/services/woocommerce-recovery/woo-recovery-outreach.adapters.ts`
- `src/services/woocommerce-recovery/woo-recovery-outreach.service.ts`
- Related unit and Woo integration tests.
- The Attempt 1 Completion Report and validation evidence.

### Validation Reviewed

- Focused unit suites: 136 tests passed; full unit suite: 3,592 tests passed.
- Lint and direct TypeScript compilation passed.
- Woo disposable PostgreSQL/Redis integration: 18 tests passed.
- `npm run build` failed because the repository-local `tsc` shim was missing.
- Shopify PostgreSQL initial-dispatch validation was not run or available.
- Implementation worktree is clean, but its task branch is three commits behind
  current `origin/main`; BG017 changed the same shared implementation paths.
- Parent report and implementation branches were pushed before this review.

### Architecture Conformance

The fallback uses the existing approved template path and retains the existing
attempt, billing and provider guards. However, the broad error conversion can
turn an unclassified failure into an optional fallback, and the implementation
has not yet been reconciled with the merged BG017 basket guard. The submitted
state therefore does not yet demonstrate conformance across the final shared
send boundary.

### Follow-up

Reconcile this branch with current `origin/main` and preserve both BG017 and
BG018 behavior. Restrict fallback to positively classified optional AI/MCP or
enrichment failures, with unrecognized failures remaining retryable or
propagated. Add and run the Shopify disposable PostgreSQL path required by the
task, rerun affected unit/Woo integration suites after reconciliation, and
complete the declared build. Keep SYSTEM-TEST-001/002 blocked on their other
prerequisites; no downstream status changed in this review.


## Architect Review — Attempt 2

### Review Status

Changes Requested — Attempt 2. The task returns to `ready`; Attempt 2 and its validation evidence remain preserved.

### Review Notes

The Attempt 2 changes resolve the prior findings: the implementation includes the merged BG017 checkout-items guard, optionality is no longer inferred from arbitrary thrown agent errors, the Shopify PostgreSQL dispatch path is covered, and the declared build completed using the installed TypeScript compiler on `PATH`.

One blocking optional-failure routing gap remains. In `AutomatedRecoveryTemplateService`, `failureTrigger()` only recognizes AI/MCP availability, model deadline, and model budget failures. The current offer revalidator also returns typed retryable outcomes such as `OFFER_DISCOVERY_INCOMPLETE`, `SOURCE_FENCE_F1_*`, `CURRENT_SOURCE_READ_DEADLINE`, and `SOURCE_FENCE_F2_CHANGED`. Those are returned through `result.kind === "FAILURE"`, but currently fall through to `unavailable(result.reasonCode)` instead of preparing the approved no-offer TEXT fallback. This can still drop an otherwise eligible initial outreach when optional discount discovery/revalidation is incomplete or temporarily unavailable, contrary to the task objective.

Classify the exact revalidation outcomes that represent optional enrichment failure and route those to fallback after the fallback service's fresh mandatory-state checks. Keep identity mismatch, stale/unauthorized proposal, required database/configuration state failures, mandatory policy failures, and unknown failure codes blocked or retryable; do not broadly treat every retryable failure as optional. Add regressions for the selected source-fence/deadline/incomplete cases and for mandatory or unknown reason codes remaining non-fallback.

### Reviewed Files

- `src/services/recovery-template-integration/automated-recovery-template.service.ts`
- `src/services/recovery-offers/current-outreach-offer-revalidation.service.ts`
- `src/services/recovery-offers/initial-outreach-offer-selection.service.ts`
- `src/services/recovery-template-integration/initial-no-offer-fallback.service.ts`
- Attempt 2 graph, coordinator and Shopify PostgreSQL integration tests.
- The Attempt 2 Completion Report and preserved Attempt 1 Architect Review.

### Validation Reviewed

Reviewed the reported 21 Shopify/Woo PostgreSQL integration tests, focused graph/coordinator/fallback suites, lint, build, and complete unit run (3,611/3,612; the sole failure is reported as the unrelated ARCH-049 preparer expectation). No tests were rerun during this review.

### Architecture Conformance

The integration and guard corrections conform. Acceptance remains blocked because some explicitly optional discount-source failures still take the unavailable/no-send path rather than the approved no-offer fallback.

### Follow-up

At Attempt 3, classify the whitelisted retryable optional revalidation outcomes and route them to the fallback with fresh mandatory-state checks. Preserve fail-closed/retry behavior for mandatory, stale-identity, and unrecognized failures. Add the focused regressions, rerun affected validation, and resubmit. Keep SYSTEM-TEST-001 and SYSTEM-TEST-002 pending; no downstream task is promoted by this review.
