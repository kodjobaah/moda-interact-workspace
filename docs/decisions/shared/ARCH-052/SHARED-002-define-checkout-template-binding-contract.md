---
id: ARCH-052-SHARED-002
architecture_id: ARCH-052
title: Define checkout and alternative-promotion WhatsApp bindings
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
- ARCH-052-SHARED-003
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-SHARED-002: Define checkout and alternative-promotion WhatsApp bindings

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Own the new semantic WhatsApp initial-outreach binding names and product-media role once, as the shared contract consumed by Admin and Background.

## Context

ARCH-047 Admin and Background currently hold parallel semantic-variable allowlists. `shop.categoryName` already exists. ARCH-049 defines three ShopBrand IMAGE header roles with immutable compiled hashes; checkout product media is a fourth distinct role, not a ShopBrand role.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- **Introduce** `checkout.itemsSummary` as a new bounded semantic binding computed by Background from existing persisted lineItems; retain already-implemented `shop.categoryName` translation binding and add `CHECKOUT_PRODUCT` optional verified image role. The image is resolved via MCP `commerce_get_product`, not a Commerce/API private image route and never stored in a new table.
- Add `promotion.scope: "CHECKOUT"|"ALTERNATIVE_PRODUCT"`, `promotion.productName` (<=120), `promotion.productUrl` (HTTPS storefront host proof, <=2048), `promotion.offerDescription` (<=160), `promotion.code` (code only if proof-backed) bindings to existing `/recovery-template-bindings` so alternative product text cannot assert it discounts existing checkout. No model-supplied freeform message text.
- Declare a strict `promotionTarget` value on immutable JSON authoring/compiled template metadata, `CHECKOUT` or `ALTERNATIVE_PRODUCT`, without changing Prisma enum or adding a template table/column. Background selects only separately approved locale/provider template variant matching this value, or falls back to approved NO_OFFER; absence of promotion link means no alt promotion send.
- Extend the existing dynamic URL button binding (today only `checkout.url`) with a second explicit semantic source `promotion.productUrl`. The existing checkout CTA consumes the upstream `CheckoutRecovery.checkoutUrl` unchanged via `checkout.url`, **without new checkout URL validation**. The separately approved `ALTERNATIVE_PRODUCT` promotional CTA consumes `promotion.productUrl` with the existing product-proof requirements and approved template bindings. Do not swap a promotional URL into the resume-checkout button. Missing required approved template variants still follow the existing no-offer/no-send handling; do not add URL-specific checkout fallback handling.
- Add schema tests for **alternative-product** host mismatch, unsafe promotional link, newline/placeholder abuse, absent image, wrong binding per promotion target and immutable compilation hash compatibility. For `checkout.url`, test only that the stored value is passed unchanged; do not add checkout URL format, host, prefix or reachability validation.

## Out of Scope

- No new R2 storage, database media rows, generic image fetcher, HTTP auth scheme or runtime provider connection.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Product images are optional and must never be substituted into a ShopBrand role; IMAGE header role is frozen in the immutable provider-approved projection.
- No arbitrary text/URL injection into Meta template, no dynamic footer and no new unapproved variable names.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider cart, coupon and order mutation is prohibited in ARCH-052. Checkout-link creation and customer-click cart restoration are upstream/out of scope.

## Work Items

- [ ] Define shared schemas/exports and fixtures.
- [ ] Document compatible Admin/Background compiler/runtime semantic constraints.
- [ ] Run contract fixtures and cross-runtime-safe import tests.

## Interfaces / Contracts

Published `@modainteract/moda-interact-shared/recovery-template-bindings` for both Admin and Background; existing purpose slots remain `INITIAL_NO_OFFER`, `INITIAL_CODE_OFFER`, `INITIAL_AUTOMATIC_OFFER` (no database enum change). `promotionTarget` distinguishes the separately approved alternative variant under existing CODE/AUTOMATIC purposes.

## Dependencies

None.

Dependencies are authoritative in YAML; system tests are terminal validation and must never block implementation.

## Enables

- `ARCH-052-SHARED-003`

## Acceptance Criteria

- [ ] Admin and Background can validate exactly the same key/role fixtures.
- [ ] Existing ARCH-047/049 frozen bindings remain valid; unknown dynamic keys and ambiguous image roles fail closed.

## Validation

- [ ] Shared unit/contract tests, package build/typecheck, browser-safe entrypoint test.
- [ ] `git diff --check` and API export shape checks.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-shared/src/recovery-template-bindings.ts`
- `moda-interact-shared/src/recovery-template-bindings.test.ts`

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
