---
id: ARCH-052-ADMIN-001
architecture_id: ARCH-052
title: Author approved checkout/alternative promo variants under existing recovery purposes
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 35
executor: copilot
claimed_at: 2026-10-30T08:46:21Z
attempt: 1
depends_on:
- ARCH-052-SHARED-003
enables:
- ARCH-052-BACKGROUND-008
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: 2026-10-30
---

# ARCH-052-ADMIN-001: Author approved checkout/alternative promo variants under existing recovery purposes

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Author Meta-approved initial WhatsApp variants for original checkout discounts AND separate alternative-product promotions without adding a new purpose enum or database table.

## Context

ARCH-047 already owns English AST authoring/translation/Meta submission/publication and six INITIAL/FOLLOW_UP × offer-purpose slots. Do not create a second merchant template editor.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Extend `src/lib/admin/whatsapp-templates/authoring/registry.ts`, `types.ts`, `validation.ts`, compiler and template publishing snapshot JSON to support approved immutable `promotionTarget:"CHECKOUT"|"ALTERNATIVE_PRODUCT"` for CODE_OFFER and AUTOMATIC_OFFER; NO_OFFER remains category-safe and offer-free. Keep existing three INITIAL + three FOLLOW_UP purpose identities and all ARCH-047 immutable approval/digest/locale rules.
- For CHECKOUT provide basket-aware copy with verified discount that truly applies to checkout. For ALTERNATIVE_PRODUCT require `promotion.productName`, `promotion.offerDescription` and `promotion.productUrl`; author copy explicitly identifying a *different product* and never suggesting original abandoned basket receives that code. Use approved product CTA or safe separately approved link; checkout resume CTA remains trusted and not replaced silently.
- Provide own preview examples and exact proof-dependent bindings for CODE (must have provider-backed code) and AUTOMATIC (no coupon code); multiple approved immutable template entries may share a purpose/locale only when `promotionTarget`, header kind and active revision identify an unambiguous selected entry. Reject ambiguous same-purpose promotion target selection.
- Meta promotional template category/consent requirements apply to cross-sell; publishing/review remains operator-controlled, not automatic on save. Tests for immutable header, translation placeholders, missing product, approval mismatch, wrong locale and fallback.

## Out of Scope

- No new merchant template authoring, provider discount lookup, Admin media processing, changes to follow-up wording unless necessary for compatibility.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Meta template preview must be illustrative, but live variables must have proven Background resolver sources; no unbound placeholders.
- Translation tokens remain protected; require approval/publishing per shop/WABA/language.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider cart, coupon and order mutation is prohibited in ARCH-052. Checkout-link creation and customer-click cart restoration are upstream/out of scope.

## Work Items

- [x] Add basket summary to registry, AST and compiler validation.
- [x] Create target-specific examples and binding eligibility rules while retaining all six existing purpose identities.
- [x] Test translation/fingerprint and Admin publication compatibility.

## Interfaces / Contracts

Existing immutable ARCH-047 WhatsApp template authoring/publishing pipeline + Shared-002 `promotionTarget` and `promotion.*` bindings. No Prisma purpose enum change.

## Dependencies

- `ARCH-052-SHARED-003` — must be Complete and architect-accepted before this task starts.

Dependencies are authoritative in YAML; system tests are terminal validation and must never block implementation.

## Enables

- `ARCH-052-BACKGROUND-008`
- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [x] Checkout and alternative promotions have distinct approved presentations using existing purpose names.
- [x] Alternative promo cannot render with a checkout-discount-only template or unsafe product URL.
- [x] Locale/Meta approval immutability and translation protections unchanged.

## Validation

- [x] Admin authoring/compiler/publishing/translation and Meta snapshot unit/component checks.
- [x] Admin typecheck, production build and `git diff --check`.
- [ ] Repository-wide lint and the broad unit/security suites are not clean; see Completion Report for unrelated existing failures.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-admin/src/lib/admin/whatsapp-templates/authoring/registry.ts`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/authoring/types.ts`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/authoring/validation.ts`
- `moda-interact-admin/tests/unit/`

Source ownership is restricted to the assigned repository plus this task file. `moda_architect` owns architectural/dependency/index reconciliation. The implementing agent should stop for an architectural connector/schema gap rather than inventing a cross-repository workaround.

## Completion Report

### Status

Ready for Review — implementation committed and pushed on the mirrored task branches.

### Files Changed

Implementation repository commit `a871a47` (`feat(admin): add checkout and alternative promotion variants`) changes:

- `package.json`, `package-lock.json`
- `src/app/(protected)/system-controls/whatsapp-templates/[definitionId]/publish/page.tsx`
- `src/components/admin/whatsapp-templates/authoring/template-family-purpose-selector.tsx`
- `src/components/admin/whatsapp-templates/authoring/template-review-summary.tsx`
- `src/components/admin/whatsapp-templates/authoring/template-saved-detail.tsx`
- `src/lib/admin/whatsapp-templates/authoring/compiler.ts`
- `src/lib/admin/whatsapp-templates/authoring/registry.ts`
- `src/lib/admin/whatsapp-templates/authoring/types.ts`
- `src/lib/admin/whatsapp-templates/authoring/validation.ts`
- `src/lib/admin/whatsapp-templates/meta/contracts.ts`
- `src/lib/admin/whatsapp-templates/meta/snapshot.ts`
- `src/lib/admin/whatsapp-templates/publishing/impact.ts`
- `src/lib/admin/whatsapp-templates/publishing/source.ts`
- `src/lib/admin/whatsapp-templates/publishing/types.ts`
- `src/lib/admin/whatsapp-templates/publishing/validation.ts`
- `tests/unit/arch047-template-authoring-ast.test.ts`
- `tests/unit/arch047-template-meta-snapshots.test.ts`
- `tests/unit/arch047-template-publication-pure.test.ts`

### Work Completed

Added the Shared 2.6.0 promotion target and frozen binding contract to Admin authoring, validation, compilation, translation consistency and Meta snapshots. CHECKOUT and ALTERNATIVE_PRODUCT retain the six existing purpose identities while using distinct proof-dependent variable eligibility and previews. Alternative-product variants require product name, description and URL, product-specific copy, and a trusted checkout-resume button; AUTOMATIC offers cannot bind coupon codes. Publication fingerprints and selection now include promotion target and header kind and reject duplicate exact matches. The authoring review, saved immutable detail and publication page identify the selected target; publication also displays header format and immutable source revision before impact confirmation.

### Validation Results

Passed:

- `npm run test:arch047-admin-authoring:unit`: 31 passed.
- `npm run test:arch047-admin-compilation:unit`: 13 passed.
- `npm run test:arch047-admin-publication:unit`: 21 passed.
- `npm run test:arch047-admin-translations:unit`: 15 passed.
- `npm run test:arch047-admin-meta:unit`: Meta snapshot/service checks passed, including target drift rejection; Meta component check passed.
- `npx tsc --noEmit`: passed.
- `npx eslint` on the three changed UI files: passed.
- `npm run build`: passed; Next.js reported existing BullMQ dynamic-dependency and optional `@valkey/valkey-glide` resolution warnings.
- `git diff --check`: passed.

Repository-wide validation limitations:

- `npm run lint` fails on existing violations in `template-content-editor.tsx`, `media/shop-brand-media-header-section.tsx` and `media/use-shop-brand-media-role.ts`; these files are not changed by this task.
- `npm run test:unit` reports 537 passing and 25 failing tests. Failures include direct-runner module/alias resolution for ARCH-047 tests, older ARCH-043/ARCH-049 suites, and existing commerce-policy test harness dependency mismatches. The focused ARCH-047 scripts above pass.
- `npm test` security suite has existing static-contract failures in Store Category translation, tenant KPI assertions and shared logging expectation; none are in files changed by this task.
- Prisma generation completed as part of Meta tests and production build. No PostgreSQL integration harness was run.

### Deviations

Admin was pinned to Shared 2.5.1 while the architect-accepted `ARCH-052-SHARED-003` contract is released in Shared 2.6.0; the dependency and lockfile were updated to consume that contract. Repository-wide lint/unit/security checks remain non-clean for unrelated existing issues listed above; focused task checks, typecheck and production build pass.

### Assumptions

The prepared launcher packet authoritatively claimed this task and supplied the canonical mirrored task worktrees; the portable-definition text above was not treated as the current lifecycle state. Existing purpose identities and ARCH-047 immutable approval/digest rules remain authoritative.

### Unresolved Issues

Repository-wide lint and broad unit/security checks have pre-existing failures; the focused task suites and production build passed. No source-level blocker remains within this task's Admin ownership.

### Architectural Concerns

Report discovered cross-repository/credential/provider-proof issues to `moda_architect`.

No additional cross-repository changes were required; the released Shared contract was consumed as specified.


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
