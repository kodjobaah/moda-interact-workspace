---
id: ARCH-052-BACKGROUND-007
architecture_id: ARCH-052
title: Resolve optional checkout or promoted-product image via MCP at runtime
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
- ARCH-052-MCP-003
- ARCH-052-COMMERCE-007
- ARCH-049-BACKGROUND-001
- ARCH-049-BACKGROUND-004
enables:
- ARCH-052-BACKGROUND-008
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-BACKGROUND-007: Resolve optional checkout or promoted-product image via MCP at runtime

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Provide an optional validated IMAGE header for the chosen checkout product or recommended alternative product, using MCP `commerce_get_product` and no API/Commerce image proxy or new media persistence.

## Context

Both Shopify and WooCommerce product information is resolved **at runtime by MCP-003**, using authenticated direct provider connections. There is no hosted API or Commerce private product-image endpoint, no product catalogue replication and no image database persistence. Background consumes the exact published `commerce_get_product` result.

## Scope

- Use existing `src/services/recovery-template-preparation/` and MCP `commerce_get_product` (published and entitled) to fetch the exact product/variant in current shop for a checkout item or selected alternative product. Variant image wins; product image fallback only if same shop/id. Never use fuzzy search as proof of identity.
- Validate returned HTTPS image source/media type, allowed host and accessible header within bounded download/preparation time; if source is unsafe/unavailable, use separately approved text/no-image variant. Reuse existing ARCH-049 media processing only when necessary and already approved; do not invent new R2 tables or persistent image catalogue.
- The image source and selected promotion product must match immutable attempt scope; no signed URL/secret or raw image source in logs. Validate retries and fallback when the image disappears.

## Out of Scope

- No database schema/migration, media provenance row, Cloudflare R2 object, new generic image proxy, checkout item persistence or ad hoc unapproved Meta header.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Do not conflate ShopBrand hero/cover image with checkout product photo. Existing SHOP_BRAND role processing remains unchanged.
- Image is optional; failure cannot permit an unsafe send or block otherwise eligible approved text-only initial outreach.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider cart, coupon and order mutation is prohibited in ARCH-052. Checkout-link creation and customer-click cart restoration are upstream/out of scope.

## Work Items

- [ ] Implement `recovery-product-image-resolver.ts` using the existing Background MCP transport and the published `commerce_get_product` tool; prefer checkout exact variant or recommended alternative exact product/variant.
- [ ] Validate public HTTPS, safe resolved address and final peer, no unsafe redirects, supported image MIME + magic bytes, <=5 MB and verified target product origin/identity; use existing security/media primitives.
- [ ] On image missing/unsafe/expired/offline return a typed no-media outcome and select an independently approved text-only Meta template; no side-effect on eligibility or checkout send.
- [ ] Test Shopify and WooCommerce variant vs product image, mismatched tenant, invalid/expired media, retry and no MCP-to-API path.

## Interfaces / Contracts

Shared-002 `CHECKOUT_PRODUCT` IMAGE role and `RecoveryProductImageResultSchema`, Shared-008 `commerce_get_product` output; existing ARCH-049 media processing. No COMMERCE-002/API-002/private product-image endpoints.

## Dependencies

- `ARCH-052-SHARED-003` — must be Complete and architect-accepted before this task starts.
- `ARCH-052-MCP-003` — must be Complete and architect-accepted before this task starts.
- `ARCH-052-COMMERCE-007` — must be Complete and architect-accepted before this task starts.
- `ARCH-049-BACKGROUND-001` — must be Complete and architect-accepted before this task starts.
- `ARCH-049-BACKGROUND-004` — must be Complete and architect-accepted before this task starts.

Dependencies are authoritative in YAML; system tests are terminal validation and must never block implementation.

## Enables

- `ARCH-052-BACKGROUND-008`

## Acceptance Criteria

- [ ] Checkout image and alternative promo product image resolve via exact MCP lookup.
- [ ] Failed or unsafe media yields approved text-only template or no-send, not broken IMAGE header.
- [ ] No new Prisma image table or MCP-to-API product call.

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
