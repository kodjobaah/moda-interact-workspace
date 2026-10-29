---
id: ARCH-052-BACKGROUND-007
architecture_id: ARCH-052
title: Resolve one verified checkout product image at runtime, with no media persistence
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-SHARED-003
- ARCH-052-COMMERCE-003
- ARCH-052-API-002
- ARCH-052-GATEWAY-001
- ARCH-049-BACKGROUND-001
- ARCH-049-BACKGROUND-004
enables:
- ARCH-052-BACKGROUND-008
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-BACKGROUND-007: Resolve one verified checkout product image at runtime, with no media persistence

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Choose one checkout line-item image via Shopify or Woo provider read APIs, verify it safely at template preparation, and return optional IMAGE header input without any database row or R2 object.

## Context

Shopify Commerce product facts can be extended to return variant/product image; Woo hosted API can extend API-process-only read port behind private authentication. The user explicitly wants runtime resolution, not CheckoutRecoveryProductMedia or persisted media metadata.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Create `src/services/recovery-product-media/recovery-product-image-resolver.ts` and tests. Input is trusted persisted `{shopId,checkoutRecoveryId,platform,checkoutGeneration,lineItems}`, not caller submitted URLs; reject empty/malformed/more than 50 entries or wrong-shop checkout.
- For at most first 3 valid lines in persisted order, first request exact variant/variation image then parent product featured-image fallback. Shopify queries Commerce-003 private `POST /internal/v1/recovery/product-image`, Woo queries API-002 same private route on its own host. Send `{shopId,checkoutRecoveryId,productId,variantId}` with Shared-004 HMAC, validate Shared-002 result and provider ID equality. At most three 2-second lookups, <=6sec total.
- Validate candidate image public HTTPS URL with no credentials, private IP, localhost, fragments, mixed-scheme redirects or unsafe host. Reuse ARCH-049 pinned DNS/SSRF safe-fetch; no redirect, <=5MB JPEG/PNG with MIME and magic-byte match, at least 200x200 and <=40MP dimensions. Signed ephemeral provider URLs require proved >=10min expiry; otherwise skip.
- Add tests for variant precedence, product fallback, first-three cap, wrong shop/line, public DNS rebinding, redirect, large/invalid images, provider rejection and approved text variant fallback.

## Out of Scope

- No database schema/migration, media provenance row, Cloudflare R2 object, new generic image proxy, checkout item persistence or ad hoc unapproved Meta header.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Do not conflate ShopBrand hero/cover image with checkout product photo. Existing SHOP_BRAND role processing remains unchanged.
- Image is optional; failure cannot permit an unsafe send or block otherwise eligible approved text-only initial outreach.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Implement one deterministic item-to-image resolver and exact provider adapters.
- [ ] Reuse existing safe fetch validation without copying generic SSRF/fetch implementations.
- [ ] Add provider simulation/media validation/fallback tests.

## Interfaces / Contracts

- Shared-002 `CHECKOUT_PRODUCT` verified provider image role and strict payload; Commerce-002 Shopify read and API-002 Woo private read with Shared-004 auth.

## Dependencies

- `ARCH-052-SHARED-003` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-COMMERCE-003` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-API-002` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-GATEWAY-001` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-049-BACKGROUND-001` — Complete in 29 October snapshot.
- `ARCH-049-BACKGROUND-004` — not Complete in 29 October snapshot.

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-BACKGROUND-008`

## Acceptance Criteria

- [ ] No new media database table, column, object store write or implicit legacy image cache.
- [ ] Only verified current product image can populate IMAGE header; missing/unsafe images use approved text fallback.

## Validation

- [ ] Background safe-fetch/media and product reader unit/integration tests, simulated Meta payload.
- [ ] Background declared typecheck/lint and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-background/src/services/recovery-product-media/recovery-product-image-resolver.ts (new)`
- `moda-interact-background/src/services/recovery-template-preparation/recovery-template-brand.ts`
- `moda-interact-background/src/services/recovery-template-preparation/recovery-template.types.ts`
- `moda-interact-background/tests/`

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
