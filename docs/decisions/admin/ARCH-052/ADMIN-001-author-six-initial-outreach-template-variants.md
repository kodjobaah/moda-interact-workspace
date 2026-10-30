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
status: ready
priority: 35
executor: null
claimed_at: null
attempt: 0
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

**Attempt 14 immutable presentation contract:** for new initial CODE/AUTOMATIC variants, choose the exact approved registration by `(shopId, senderWabaId, purpose, canonicalLanguageTag, promotionTarget, headerKind)` and an enabled approved published revision. The currently implemented `selectRecoveryAssignment()` rejects multiple candidates for the same purpose/locale before checking `promotionTarget`; the Admin publisher must store the approved discriminator and make it available to Background-008 for deterministic filtering **before** ambiguity detection. Do not select arbitrarily by first record or publish the same identity twice. Alternative-product templates may have **two independently Meta-approved dynamic URL CTA slots**, one bound to `checkout.url` (Resume checkout) and one to `promotion.productUrl` (View offer), using existing Shared-002 `buttons[]` and approved component indexes. Only create such a variant if Meta accepts it; no unapproved button or arbitrary model-written text. No ARCH-052 checkout URL validity checks.


- Meta template preview must be illustrative, but live variables must have proven Background resolver sources; no unbound placeholders.
- Translation tokens remain protected; require approval/publishing per shop/WABA/language.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider cart, coupon and order mutation is prohibited in ARCH-052. Checkout-link creation and customer-click cart restoration are upstream/out of scope.

## Work Items

- [ ] Add basket summary to registry, AST and compiler validation.
- [ ] Create safe six-purpose/three INITIAL starter examples and variant eligibility rules.
- [ ] Test translation/fingerprint and Admin publication compatibility.

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

- [ ] Different promotion targets under the same existing purpose/language remain separately selectable by immutable registration metadata; selecting one does not create `AMBIGUOUS_ASSIGNMENT` for the other.
- [ ] Where the Meta-approved alternative template has two URL CTA components, both semantic bindings and their indexes are immutable, correctly compiled, translated and preserved in registration snapshots.


- [ ] Checkout and alternative promotions have distinct approved presentations using existing purpose names.
- [ ] Alternative promo cannot render with a checkout-discount-only template or unsafe product URL.
- [ ] Locale/Meta approval immutability and translation protections unchanged.

## Validation

- [ ] Admin tests: same purpose and language with two target variants, wrong header role, duplicate approved same-target variant, two CTA component indexes and Meta rejection of unsupported button configuration.


- [ ] Admin authoring/compiler/publishing/translation unit tests and approved template snapshots.
- [ ] Admin typecheck/lint/tests and `git diff --check`.

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
