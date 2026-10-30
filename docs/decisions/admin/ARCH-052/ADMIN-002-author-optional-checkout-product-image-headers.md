---
id: ARCH-052-ADMIN-002
architecture_id: ARCH-052
title: Author approved optional checkout and alternative-product IMAGE headers
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: blocked
priority: 35
executor: copilot
claimed_at: 2026-10-30T11:23:51Z
attempt: 1
depends_on:
- ARCH-052-SHARED-003
- ARCH-049-ADMIN-002
enables:
- ARCH-052-BACKGROUND-008
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: 2026-10-30
---

# ARCH-052-ADMIN-002: Author approved optional checkout and alternative-product IMAGE headers

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Allow one optional Meta-approved IMAGE header representing the checkout item or verified alternative promotional product, without new product-image tables or new ShopBrand roles.

## Context

ARCH-049 ADMIN002 already adds frozen ShopBrand media roles to Meta template authoring. A checkout product IMAGE role is distinct and optional; Meta approval applies to the exact header family.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Use Shared-002 `CHECKOUT_PRODUCT` media role and Shared-008 exact MCP product images; author separate immutable IMAGE and text-only fallback variants for `promotionTarget:CHECKOUT` and `promotionTarget:ALTERNATIVE_PRODUCT` where approved, under existing INITIAL purposes.
- Bind an alternate image only to the same verified product/variant ID chosen by Background-010; no arbitrary AI-selected URL. Preserve ARCH-049 media origin validation and frozen Meta header digests; reject header type/role changes after approval.
- Tests for missing/unsafe image, product mismatch, variant fallback, revoked source, translation and correct text-only variant choice.

## Out of Scope

- No actual Shopify/Woo photo download, R2 processing, Meta sample-media sourcing workaround or live send.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- A product image can be used only after Background returned a typed `VERIFIED_PROVIDER_IMAGE` in the current 5-minute preparation window, and the exact Meta IMAGE template was approved.
- If the image is absent/expired or source changed use a different approved TEXT template identity; never alter an approved template component at send.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider cart, coupon and order mutation is prohibited in ARCH-052. Checkout-link creation and customer-click cart restoration are upstream/out of scope.

## Work Items

- [x] Implement new header role UI/validation and preview.
- [x] Reuse and regression-test the existing paired variant fallback publication/eligibility contract.
- [ ] Run immutable digest and Meta approval flow regression tests; Meta submission remains blocked without a trusted sample handle producer.

## Interfaces / Contracts

Existing ARCH-049 media conventions, Shared-002 image role and promotionTarget metadata. Background-007 owns actual MCP product reads.

## Dependencies

- `ARCH-052-SHARED-003` — must be Complete and architect-accepted before this task starts.
- `ARCH-049-ADMIN-002` — must be Complete and architect-accepted before this task starts.

Dependencies are authoritative in YAML; system tests are terminal validation and must never block implementation.

## Enables

- `ARCH-052-BACKGROUND-008`
- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] IMAGE header with product role compiles/reviews/publishes only through Admin.
- [ ] A missing READY product media selects an approved fallback or typed no-send; it never swaps media into an unrelated role.

## Validation

- [ ] Admin authoring/preview, frozen fingerprint and publication regression suites.
- [ ] Admin typecheck/tests/lint and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-admin/src/lib/admin/whatsapp-templates/authoring/`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/media/`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/publishing/`
- `moda-interact-admin/tests/unit/`

Source ownership is restricted to the assigned repository plus this task file. `moda_architect` owns architectural/dependency/index reconciliation. The implementing agent should stop for an architectural connector/schema gap rather than inventing a cross-repository workaround.

## Completion Report

### Status

Blocked — Admin authoring and fallback-selection changes are implemented and focused validation passes. End-to-end Meta IMAGE submission/publication and runtime proof enforcement require upstream capabilities not present in the owned repositories.

### Files Changed

- `moda-interact-admin/package.json`
- `moda-interact-admin/src/components/admin/whatsapp-templates/authoring/template-authoring-workspace.tsx`
- `moda-interact-admin/src/components/admin/whatsapp-templates/authoring/template-content-editor.tsx`
- `moda-interact-admin/src/components/admin/whatsapp-templates/media/shop-brand-media-header-section.tsx`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/authoring/types.ts`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/authoring/validation.ts`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/meta/contracts.ts`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/meta/snapshot.ts`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/publishing/source.ts`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/publishing/types.ts`
- `moda-interact-admin/tests/unit/arch047-template-meta-snapshots.test.ts`
- `moda-interact-admin/tests/unit/arch047-template-publication-pure.test.ts`
- `moda-interact-admin/tests/unit/arch049-admin-media-compiler.test.ts`
- `moda-interact-admin/tests/unit/arch049-admin-media-components.test.tsx`
- `moda-interact-admin/tests/unit/arch049-admin-media-projection-vectors.test.ts`

### Work Completed

Added the Shared `CHECKOUT_PRODUCT` role to the Admin authoring AST and validation, with explicit offer-target requirements. Added a distinct product-image authoring option that is not backed by ShopBrand sample assets or arbitrary URLs. Preserved immutable role/digest behavior and added locale role-drift checks to Meta submission planning and publication translation validation. Confirmed and tested that existing publication selection chooses the exact approved TEXT variant for the same purpose/target rather than mutating or selecting the IMAGE variant. No product-image resolver or Meta sample-media workaround was introduced.

### Validation Results

Launcher packet: prepared execution for attempt 1; claim commit `0bd17e5461d5301a608fcd096cd1f9bbfa198a95`; dependency gate passed for `ARCH-052-SHARED-003` and `ARCH-049-ADMIN-002`; database submodule initialized at `f16d5fc955b1fa1215177cc89fb6fd326bfa65c`.

- `npm run test:arch049-admin-media:unit`: passed, 26 unit tests and 1 SQL test.
- `npm run test:arch047-admin-authoring:unit`: passed, 33 tests.
- `npm run test:arch047-admin-compilation:unit`: passed, 14 tests.
- `npm run test:arch047-admin-publication:unit`: passed, 22 tests.
- `npm run test:arch047-admin-translations:unit`: passed, 16 tests.
- `npm run test:arch047-admin-meta:unit`: passed, 14 snapshot/service tests and 1 UI test.
- `npx tsc --noEmit`: passed.
- `npm run build`: passed; emitted non-fatal existing BullMQ dynamic-dependency and optional `@valkey/valkey-glide` warnings.
- `git diff --check`: passed.
- `npm run test:unit`: 555/572 passed; 17 failed. Failures include unrelated commerce-policy mock harness dependency mismatches, CJS/ESM interop and top-level-await loader errors; the focused authoring/publication/translation/media/Meta scripts above pass.
- `npm run lint`: blocked by an existing `react-hooks/set-state-in-effect` error in unchanged `src/components/admin/whatsapp-templates/media/use-shop-brand-media-role.ts:26`; focused lint on changed source had no errors.

### Deviations

The requested `VERIFIED_PROVIDER_IMAGE` five-minute proof/resolver and exact selected product/variant/source-revocation checks are not implemented in Admin or Background. Admin authoring cannot safely provide runtime enforcement without Background's typed contract. Additionally, Meta submission still fails closed with `IMAGE_SAMPLE_HANDLE_REQUIRED`; no trusted sample-handle producer exists in Admin, and the task explicitly prohibits a sample-media sourcing workaround. Consequently the task cannot meet its end-to-end IMAGE approval/publication and runtime fallback/no-send acceptance criteria within Admin ownership. No live messaging or product-media fetch was performed.

### Assumptions

Shared 2.6.0's exported `RecoveryTemplateHeaderMediaRole` is authoritative for CHECKOUT_PRODUCT. The existing publication identity selector supports distinct IMAGE/TEXT variants keyed by promotion target and header format. The prepared launcher supplied canonical worktrees and dependency evidence, which were used without repeating startup discovery or claim operations.

### Unresolved Issues

1. Background must provide the typed, current-window `VERIFIED_PROVIDER_IMAGE` contract/resolver, including exact product/variant binding, source-change/revocation handling, and safe TEXT fallback or typed no-send. Coordinate this dependency before enabling downstream runtime use.
2. The owning Meta integration path must provide a trusted IMAGE sample upload-handle producer so Admin can submit the immutable IMAGE template without inventing a media workaround.
3. Full `npm run test:unit` remains at 555/572 due to loader/mock-harness failures; repository lint remains blocked by the unrelated existing media-hook diagnostic. Focused task validation is green.

### Architectural Concerns

Return to `moda_architect` for cross-repository sequencing of the Background proof resolver and trusted Meta sample-handle producer. The Admin-owned authoring and fallback-selection portion is implemented, but acceptance remains blocked pending those dependencies and full approval-flow validation.


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
