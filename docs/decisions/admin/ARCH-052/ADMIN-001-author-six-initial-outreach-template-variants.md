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
status: complete
priority: 35
executor: null
claimed_at: null
attempt: 3
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

- [x] Add basket summary to registry, AST and compiler validation.
- [x] Create target-specific examples and binding eligibility rules while retaining all six existing purpose identities.
- [x] Test translation/fingerprint and Admin publication compatibility.
- [x] Support two independently indexed dynamic URL buttons when Meta approves both CTAs, and preserve both bindings through translation and publication.

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

- [x] Different promotion targets under the same existing purpose/language are carried in immutable registration metadata for deterministic downstream selection.
- [x] Where a Meta-approved alternative template has two URL CTA components, both semantic bindings and component indexes are immutable, correctly compiled, translated and preserved in registration snapshots.
- [x] Checkout and alternative promotions have distinct approved presentations using existing purpose names.
- [x] Admin authoring, compilation, translation and immutable registration snapshots distinguish CHECKOUT from ALTERNATIVE_PRODUCT and freeze `promotion.productUrl` only as an approved semantic binding; Admin never supplies a live product URL. **BG008 owns runtime source, shop scope and URL safety, with supporting BG010/MCP-003 contracts.**
- [x] Locale/Meta approval immutability and translation protections unchanged.

## Validation

- [x] Focused Admin authoring, compilation, publication, translation and Meta snapshot checks passed for the supported cases.
- [x] Add focused coverage for two URL CTA component indexes and both frozen semantic bindings; current authoring tests explicitly restrict Meta dynamic buttons to one checkout URL.
- [x] Admin typecheck, production build and `git diff --check`.
- [ ] Repository-wide lint and broad unit/security suites remain non-clean; see Completion Report for reported unrelated failures.

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

Attempt 1 history: Changes Requested; implementation commit `a871a47` remains pushed. Attempt 2 completion and review submission are recorded below.

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

Repository-wide lint and broad unit/security checks have pre-existing failures; the focused task suites and production build passed. Review found the two-CTA authoring gap recorded below. Product URL runtime safety remains dependent on the owning resolver contract.

### Architectural Concerns

Report discovered cross-repository/credential/provider-proof issues to `moda_architect`.

No additional cross-repository changes were required; the released Shared contract was consumed as specified.

### Attempt 2 Completion Report

#### Status

Ready for Review. Attempt 2 addresses every correction in the latest Architect Review. Implementation commit `14faa94a7096aef3ef9222c687cb663dd5834459` is committed and pushed on `task/ARCH-052-ADMIN-001`.

#### Architect Review Correction Mapping

- Extended the Admin AST/compiler and validation to represent two distinct dynamic URL bindings only for `ALTERNATIVE_PRODUCT`: component index 0 binds `checkout.url` and index 1 binds `promotion.productUrl`. Duplicate semantic bindings, `promotion.productUrl` on other targets, and two-button templates without this exact approved pair are rejected.
- Added alternative-template editor controls for a second CTA and the product URL binding; non-alternative templates remain limited to one button. Meta submission remains operator-controlled and no approval behavior or cross-repository contract was changed.
- Confirmed immutable translation behavior and publication snapshot preservation with focused tests. Translation retains both labels and indexes; Meta registration snapshots retain the same frozen binding pair; publication parsing retains each index/variable mapping.
- Preserved deterministic promotion-target and header-kind selection and all prior invariants. No database or shared-contract changes were needed; Shared 2.6.0 already defines both supported URL binding variables.

#### Files Changed

- `src/components/admin/whatsapp-templates/authoring/template-buttons-editor.tsx`
- `src/components/admin/whatsapp-templates/authoring/template-content-editor.tsx`
- `src/lib/admin/whatsapp-templates/authoring/compiler.ts`
- `src/lib/admin/whatsapp-templates/authoring/types.ts`
- `src/lib/admin/whatsapp-templates/authoring/validation.ts`
- `src/lib/admin/whatsapp-templates/translations/source-snapshot.ts`
- `tests/unit/arch047-template-authoring-ast.test.ts`
- `tests/unit/arch047-template-authoring-components.test.tsx`
- `tests/unit/arch047-template-compilation.test.ts`
- `tests/unit/arch047-template-meta-snapshots.test.ts`
- `tests/unit/arch047-template-publication-pure.test.ts`
- `tests/unit/arch047-template-translations.test.ts`

#### Validation

- `npm run test:arch047-admin-authoring:unit`: passed, 33/33.
- `npm run test:arch047-admin-compilation:unit`: passed, 14/14.
- `npm run test:arch047-admin-translations:unit`: passed, 16/16.
- `npm run test:arch047-admin-meta:unit`: passed, 15/15 across snapshot/service and component checks; includes dual CTA registration snapshots for all 20 locale payloads.
- `npm run test:arch047-admin-publication:unit`: passed, 22/22.
- `npx tsc --noEmit`: passed.
- Targeted ESLint on all changed production source files: passed.
- `npm run build`: passed. Existing BullMQ dynamic-dependency and optional `@valkey/valkey-glide` resolution warnings remain.
- `git diff --check`: passed.
- No PostgreSQL integration harness was run.

#### Existing Suite Limitations

The repository-wide lint/unit/security limitations recorded under Attempt 1 were not rerun because this attempt changes only the authoring, translation, and publication projection slice. The previously reported broad unit/security harness failures are not claimed as resolved; all focused suites for this correction pass. The content-editor JSX apostrophe lint issue touched during this attempt was escaped, and the changed production-source lint command passes. No new unrelated failures were observed.

#### Launcher and Branch Evidence

- Prepared Attempt 2 was launcher-claimed by `copilot`; claim commit `0884b7228c6ab427c1809ff981509343b363eca3` was already pushed. Launcher startup/discovery/sync/claim steps were not repeated.
- Dependency gate `ARCH-052-SHARED-003` was complete. Recursive implementation submodule state was ready at recorded database commit `f16d5fc955b1fa1215177cc89fb6fd326bfa65c`.
- Parent task branch: `task/ARCH-052-ADMIN-001`; prepared parent head was `c966bb9a629626ea89d7829b3954844ab16cdabe`.
- Implementation branch: `task/ARCH-052-ADMIN-001`; prepared implementation head was `a871a4700f24fc6aa8a4939fe9fbb438b1912cef`.
- Implementation commit: `14faa94a7096aef3ef9222c687cb663dd5834459`; pushed. Implementation worktree was clean after publication.

#### Deviations and Unresolved Issues

No deviations or unresolved cross-repository requirements. Meta approval remains a provider/operator gate; this change adds no claim that Meta has approved any particular two-button template.

### Attempt 3 Completion Report

#### Status

Blocked pending an architect-owned update to `ARCH-052-BACKGROUND-008`. Architect Review Attempt 2 confirms the dual-CTA correction is complete and requests no further Admin source changes. Acceptance remains pending runtime proof of product URL provenance and safety.

#### Required Background Contract and Tests

`ARCH-052-BACKGROUND-008` must require `promotion.productUrl` to come from the authenticated current-shop MCP product result, and require an unsafe URL to be rejected or routed to the approved no-offer/no-send path. Add focused Background runtime tests covering the authenticated current-shop source and unsafe-URL fail-closed behavior. After that gate is satisfied, `moda_architect` must either record BG008 as satisfying the runtime half of this Admin criterion or amend the Admin criterion to the Admin authoring boundary while preserving the BG008 gate.

#### Admin Changes and Branch State

No Admin source correction was requested or made. This attempt changes only this task report and lifecycle status. No runtime tests were rerun because there were no source changes. The implementation branch remains `task/ARCH-052-ADMIN-001` at `14faa94a7096aef3ef9222c687cb663dd5834459`; the parent task branch contains this blocked report update. Return the cross-repository contract and acceptance disposition to `moda_architect`.


## Architect Review — Attempt 1 (Changes Requested)

### Review Status

Changes Requested — Attempt 1. The implementation is not accepted against the current task acceptance criteria.

### Review Notes

Reviewed implementation commit `a871a47` in the dedicated Admin worktree. The authoring contract does not support the conditional two-button alternative-product template required by the task: `UrlButton.variable` permits only `checkout.url`, AST validation permits at most one URL button, and validation rejects any other dynamic URL variable. Therefore an approved alternative template with both Resume checkout and View offer buttons cannot be authored and compiled into frozen bindings.

### Reviewed Files

- `src/lib/admin/whatsapp-templates/authoring/types.ts` — `UrlButton` supports only `checkout.url`.
- `src/lib/admin/whatsapp-templates/authoring/validation.ts` — limits authoring to one URL button and only permits the checkout URL binding.
- `src/lib/admin/whatsapp-templates/authoring/compiler.ts` — compiles only the current authorable button bindings.
- Related publication parsing and snapshot code was inspected for compatibility.

### Validation Reviewed

Reviewed the implementation diff and the task completion report. The report records passing focused Admin authoring, compilation, publication, translation, Meta, typecheck, UI lint, production build, and diff checks, alongside unrelated repository-wide validation failures. No additional tests were run during this review.

### Architecture Conformance

Promotion-target metadata and header-kind selection are carried through authoring and publication. However, the required two-CTA case is not representable end-to-end, so acceptance criterion 2 remains unmet.

### Follow-up

Extend the Admin AST, validation, compiler, immutable snapshots, and translation/publication checks to support both independently indexed URL bindings (`checkout.url` and `promotion.productUrl`) when the approved Meta template contains both buttons. Add focused tests proving both indexes and semantic bindings survive compilation, translation, and registration snapshotting. Resubmit for review after the focused checks pass.


## Architect Review — Attempt 2 (Changes Requested)

### Review Status

Changes Requested. The Attempt 1 dual-CTA correction is implemented and the submitted focused validation passes. No further Admin source correction is requested.

### Review Notes

The Admin AST/compiler, authoring UI, translation snapshot and Meta publication snapshot now preserve two distinct approved URL bindings at their exact indexes: `checkout.url` and `promotion.productUrl`. Validation limits the two-button arrangement to `ALTERNATIVE_PRODUCT`, rejects duplicate/missing semantic bindings, and preserves the trusted checkout CTA. The Attempt 2 report records passing focused authoring, compilation, translation, Meta and publication suites, typecheck, changed-source lint, production build and diff check. The implementation commit `14faa94a7096aef3ef9222c687cb663dd5834459` and parent task report are published on their task branches.

Acceptance remains withheld because this task still has an unchecked criterion: an alternative promotion must not render with an unsafe product URL, with runtime safety owned by the resolver contract. Admin publishes a dynamic `promotion.productUrl` binding and approved component metadata, but it cannot prove the runtime value's source, shop ownership or URL safety. The pending `ARCH-052-BACKGROUND-008` task currently requires an MCP-returned canonical storefront product URL but does not define the concrete validation/fail-closed contract or its tests.

### Required Follow-up

Before accepting ADMIN-001, establish the ownership split durably: update the owning Background resolver task contract to require that `promotion.productUrl` comes from the authenticated, current-shop MCP product result and is rejected or handled by the approved no-offer/no-send path when its URL is unsafe; add focused runtime coverage there. Then either record that BG008 gate as the satisfaction of the runtime half of this criterion or amend this Admin criterion to its own authoring boundary and preserve the BG008 gate. No additional Admin implementation change is requested.

### Reviewed Files

- `src/lib/admin/whatsapp-templates/authoring/types.ts`
- `src/lib/admin/whatsapp-templates/authoring/validation.ts`
- `src/lib/admin/whatsapp-templates/authoring/compiler.ts`
- `src/components/admin/whatsapp-templates/authoring/template-buttons-editor.tsx`
- `src/lib/admin/whatsapp-templates/translations/source-snapshot.ts`
- Meta registration and publication snapshot/validation code
- Focused authoring, compilation, translation, Meta snapshot and publication tests

### Validation Reviewed

Attempt 2 reports 33 authoring tests, 14 compilation tests, 16 translation tests, 15 Meta checks, and 22 publication tests passing; `npx tsc --noEmit`, changed-production-source ESLint, `npm run build`, and `git diff --check` also passed. The broader repository lint/unit/security failures remain recorded as existing unrelated suite limitations. No tests were rerun during this review.

### Architecture Conformance

The dual CTA implementation conforms to the Admin ownership boundary and retains approval immutability. Runtime product URL provenance/safety is a downstream send-time responsibility and is not yet specified strongly enough in the owning Background-008 task contract to accept this cross-service criterion.

## Architect Review — Attempt 3 (Accepted: Admin boundary)

### Review Status

Accepted. `status: complete` under `completion_mode: automatic`. The historical Attempt 3 blocked report is retained; it is superseded by this architect-owned boundary reconciliation, not a new Admin source attempt.

### Review Notes

Attempt 2 accepted the dual-CTA implementation and its focused authoring, compilation, translation, Meta snapshot, publication, typecheck and production-build evidence. The attached Admin source also shows that its AST/validation supports two approved dynamic URL variables with distinct indexes and immutable publication bindings. No additional Admin source change or Admin runtime test is required. Admin has no access to the send-time MCP product result and therefore cannot establish a live product URL's origin, tenant ownership or suitability.

The prior unchecked acceptance item combined Admin authoring with Background runtime safety and created a dependency cycle: BACKGROUND-008 depends on ADMIN-001, while ADMIN-001's acceptance awaited BACKGROUND-008. The item is now scoped to the Admin-owned frozen binding contract. **BACKGROUND-008 has an independent, mandatory runtime URL-provenance and fail-closed acceptance gate; BACKGROUND-010 supplies the source-bound product result and MCP-003 owns shop-scoped provider projection.** Accepting Admin does not assert that this runtime gate or Meta approval of a live two-button template has passed.

### Reviewed Files

`src/lib/admin/whatsapp-templates/authoring/{types,validation,compiler,registry}.ts`, `src/lib/admin/whatsapp-templates/meta/{contracts,snapshot}.ts`, the matching Admin tests and the Attempt 2 review/report evidence. Runtime consumer contracts were reviewed in BACKGROUND-008/BACKGROUND-010 and MCP-003 task definitions; those implementations remain pending.

### Validation Reviewed

The Attempt 2 report records passing focused suites (33 authoring, 14 compilation, 16 translations, 15 Meta and 22 publication), typecheck, touched-source lint, production build and diff check. These validations were **reviewed, not rerun** in this architectural correction. The previous repository-wide baseline failures remain recorded.

### Architecture Conformance

Accepted for Admin's immutable template authoring and publication scope. Product URL provenance, host safety and approved template send admission remain downstream requirements. No change to the developer's implementation branch or release is claimed.

### Follow-up

BACKGROUND-008 must prove source-bound `promotion.productUrl` and unsafe-URL fail-closed behaviour before *its own* acceptance. Its blocked runtime requirement must not be used to reopen or gate this completed Admin task. System-test terminal tasks independently certify both providers.
