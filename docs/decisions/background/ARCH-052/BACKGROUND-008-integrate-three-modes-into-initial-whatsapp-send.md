---
id: ARCH-052-BACKGROUND-008
architecture_id: ARCH-052
title: Send approved checkout or alternative-product promotion via existing initial outreach
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 65
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-BACKGROUND-010
- ARCH-052-BACKGROUND-005
- ARCH-052-BACKGROUND-007
- ARCH-052-ADMIN-001
- ARCH-052-ADMIN-002
- ARCH-052-API-004
- ARCH-052-GATEWAY-001
enables:
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-BACKGROUND-008: Send approved checkout or alternative-product promotion via existing initial outreach

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Compose the existing initial outreach with a verified checkout discount, separately verified alternative-product promotion or approved no-offer fallback, without replacing existing Meta/consent/billing send gates.

## Context

ARCH-047 BG006 already integrates `AutomatedRecoveryTemplateService` with initial send and final Meta/credit admission; ARCH-048 Woo outreach and ARCH-050 Support notices are complete. This task extends those, not creates a new send pipeline.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Initial sequence one reads **current** merchant discount settings from Background and consumes the Background-010 trusted `CHECKOUT_DISCOUNT` / `ALTERNATIVE_PRODUCT_PROMOTION` / `NO_VERIFIED_OFFER` decision. NONE never calls discount MCP/AI. Stage-2 alternative promo is permitted only for merchant-authorised discount mode and provider-proofed product+discount pairing; a product merely sharing a taxonomy category is insufficient.
- Use existing six Meta **purposes** (`INITIAL_NO_OFFER`, `INITIAL_CODE_OFFER`, `INITIAL_AUTOMATIC_OFFER` and follow-ups) without a DB enum change. For checkout discount use approved `promotionTarget:CHECKOUT` CODE/AUTOMATIC variant; for other product use independently Meta-approved `promotionTarget:ALTERNATIVE_PRODUCT` CODE/AUTOMATIC variant. Never render alternative offer using an approved checkout-only copy. Bind distinct `promotion.productName`, `promotion.productUrl`, `promotion.offerDescription` and verified code when provided; keep abandoned-cart checkout return button separately. No claim alternate discount applies to existing cart.
- For alternate promotion, use only verified canonical storefront product URL and independently approved CTA/link text; do not change approved button URL prefix after Meta approval. Require marketing consent/category/merchant permission for cross-sell content; if required permission or approved variant absent, use approved NO_OFFER or typed no-send. No unapproved on-the-fly message body.
- Optional BG007 image may show checkout item or promoted product only with matching approved IMAGE variant, otherwise approved text-only. Resume checkout uses existing trusted Shopify URL or a **fresh Woo signed restore URL resolved in this task**, as specified next.
- **Integrate formerly BACKGROUND-006 here:** implement `src/services/woocommerce-recovery/woo-recovery-checkout-url.service.ts` as a narrow caller of API-004 private-only `POST /internal/v1/recovery/restore-link` via Gateway-001 `MODA_RECOVERY_PRIVATE_READ_API_HOSTPORT`. Its strict request body is `{shopId,checkoutRecoveryId,checkoutFingerprint}` loaded from a same-shop persisted recovery; no SHARED-004 HMAC, Redis nonce, direct Woo REST credentials or WordPress call. Validate bounded `{url,expiresAt}`: HTTPS canonical merchant host, exact `/moda-recovery/restore/<opaque-token>` path, no userinfo/fragment/redirect, future expiration <=30 min. Do not store the bearer URL on `CheckoutRecovery`, in `offerSnapshot`, or in any new table, and never log it. The existing `ConversationMessage.content` template-input snapshot may retain the dynamic URL button parameter needed to reconstruct what was actually sent; it is the **only permitted durable copy**, access-controlled under the existing message retention path, and the link must expire within 30 minutes. Resolve it during INITIAL preparation outside SQL permit/billing transactions. If unavailable/unsafe/expired, use an independently approved no-button variant or typed no-send—never substitute a generic `/checkout` URL. Shopify checkout-link behaviour remains unchanged.
- The actual prepared template parameters and existing `recoveryPromise` must remain the **single durable source of customer-facing claims** in the confirmed outbound `ConversationMessage.content`, linked through `RecoveryOutreachAttempt.outboundMessageId`. Extend the existing `RecoveryOfferPromise` only to distinguish `ALTERNATIVE_PRODUCT_PROMOTION` and its exact verified discount/product/variant identifiers, title and URL reference as necessary. Do not write or read a second `offerSnapshot.sentOffer` or duplicate policy/offer history. On follow-up, read the confirmed initial outbound message and its persisted parameters/promise; do not infer a promise from merchant settings or merely prepared/unconfirmed messages. Preserve ARCH-046 consent/STOP, moderation, credit/idempotency, human handover and ARCH-050 merchant Support notification.
- Integration tests for all three merchant modes × two platforms × checkout/alternative/no-offer, changed product/coupon, missing image/category/CTA, approved/non-approved promotion target, marketing refusal, Meta timeout, duplicate queues and credit confirmation.

## Out of Scope

- No new Meta template creation on send path, no independent billing/consent engine, no cart mutations, no reopening ARCH-050 notices or paid follow-up business changes.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- No new offerSnapshot policy or sent-offer contract, no backfill or legacy adapters. The existing message receipt remains authoritative; preserve the existing one-send/idempotency rules.
- Before final send, re-read current merchant mode and selected IDs for FIXED; if the chosen offer is no longer authorised or the checkout is no longer recoverable, replace with approved NO_OFFER or skip send, never advertise revoked offer. When FIXED or AI has no verifiable offer, use NO_OFFER only if its own approved variant exists, otherwise typed no-send. If a verification budget was exhausted or the catalogue was incomplete, do not claim that no merchant discount exists. If the model fails and an MCP proof-positive offer exists, use BACKGROUND-010's deterministic verified fallback.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Bind the three trusted offer outcomes into the existing approved template/send flow without a new messaging pipeline.
- [ ] Implement Woo recovery URL adapter formerly BACKGROUND-006, with precise expiry/host validation and fallback/no-send.
- [ ] Extend existing `RecoveryOfferPromise` and persisted `ConversationMessage.content` only as necessary for alternative products, and make follow-up consume the confirmed initial outbound message; never duplicate the same offer into offerSnapshot.
- [ ] Run two-provider end-to-end initial-send, current-policy-change, unsafe Woo URL, duplicate/idempotency and follow-up integration suites.

## Interfaces / Contracts

Shared-002 template `promotionTarget`, binding and URL-button contracts; Background-local `InitialOutreachAgentResult`; existing persisted `recoveryPromise`/`ConversationMessage.content` receipt and `RecoveryOutreachAttempt.outboundMessageId`; API-004 strict private restore-link response `{url,expiresAt}`; existing Meta approval, consent, credit and send pipeline unchanged.

## Dependencies

- `ARCH-052-BACKGROUND-010` — must be Complete and architect-accepted before this task starts.
- `ARCH-052-BACKGROUND-005` — must be Complete and architect-accepted before this task starts.
- `ARCH-052-BACKGROUND-007` — must be Complete and architect-accepted before this task starts.
- `ARCH-052-ADMIN-001` — must be Complete and architect-accepted before this task starts.
- `ARCH-052-ADMIN-002` — must be Complete and architect-accepted before this task starts.
- `ARCH-052-API-004` — must be Complete and architect-accepted before this task starts.
- `ARCH-052-GATEWAY-001` — must be Complete and architect-accepted before this task starts.

Dependencies are authoritative in YAML; system tests are terminal validation and must never block implementation.

## Enables

- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Correct approved text distinguishes discount on abandoned checkout from a separate product offer.
- [ ] All added promotions have current provider proof, required marketing permissions and valid approved template.
- [ ] No duplicate send/billing, no unsafe Woo restore links or additional bearer-token persistence and no change to final outbound consent/moderation/admission gates.

## Validation

- [ ] Background initial-send unit and PostgreSQL tests (Shopify + Woo, duplicate/retry/provider race, change of merchant settings, initial/follow-up persisted promise, malformed/expired/wrong-shop restore link).
- [ ] Existing ARCH-047/048/050 admission, moderation, STOP, credit and notification suites.
- [ ] Background build/lint and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-background/src/services/recovery-template-integration/automated-recovery-template.service.ts`
- `moda-interact-background/src/services/recovery-template-preparation/`
- `moda-interact-background/src/services/checkout-recovery/recovery-initiation.service.ts`
- `moda-interact-background/src/services/woocommerce-recovery/woo-recovery-checkout-url.service.ts`
- `moda-interact-background/src/services/recovery-template-integration/prepared-template-send.ts`
- `moda-interact-background/src/services/conversation-moderation/automated-template-input.ts`
- `moda-interact-background/tests/integration/`

Source ownership is restricted to the assigned repository plus this task file. `moda_architect` owns architectural/dependency/index reconciliation. The implementing agent should stop for an architectural connector/schema gap rather than inventing a cross-repository workaround.

## Completion Report

### Status

Not Started — portable definition, no task claim.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run.

### Deviations

None reported.

### Assumptions

Execution will verify its current workspace, source state, dependency versions and test harness.

### Unresolved Issues

None established by implementation.

### Architectural Concerns

Report discovered cross-repository/credential/provider-proof issues to `moda_architect`.


## Architect Review

### Review Status

Pending.

### Review Notes

Planning only; no source implementation accepted.

### Reviewed Files

The task definition was authored from the 29 October 2026 snapshot; a code implementation has not been reviewed.

### Validation Reviewed

None for implementation.

### Architecture Conformance

To be determined after implementation review.

### Follow-up

Materialise with the canonical task launcher after the planning patch is integrated and dependencies become Complete.
