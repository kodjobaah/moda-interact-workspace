---
id: ARCH-052-ADMIN-003
architecture_id: ARCH-052
title: Author approved multi-discount checkout template bindings
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 40
executor: codex
claimed_at: 2026-10-31T06:30:35Z
attempt: 2
depends_on:
- ARCH-052-SHARED-012
- ARCH-052-ADMIN-002
enables:
- ARCH-052-BACKGROUND-008
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
- ARCH-052-SYSTEM-TEST-003
created: 2026-10-30
updated: 2026-10-31
---

# ARCH-052-ADMIN-003 — Author approved multi-discount checkout template bindings

## Architecture

Architecture: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Implemented in the dedicated `moda-interact-admin` task worktree for review. No provider upload was performed.

## Objective

Support independently approved checkout-target CODE and AUTOMATIC template revisions capable of describing up to three source-backed compatible offers, without changing the six existing template purposes or the alternative-product IMAGE path.

## Context

The existing `INITIAL_CODE_OFFER` authoring permits only `offer.code`. Rendering multiple coupon codes into that singular semantic slot or sending multiple automatic discounts under singular wording is misleading and may conflict with approved copy. SHARED-011 adds a new explicit `offer.codes` text semantic. Meta accepts only approved immutable template revisions; the send worker must not improvise a new copy against an old approval.

## Scope

- Extend existing Admin authored template variable registry/validator/preview/compiler in `moda-interact-admin/src/lib/admin/whatsapp-templates/authoring/` and relevant tests to support `offer.codes` for `promotionTarget:CHECKOUT` CODE_OFFER; add plural multi-discount wording for checkout-target AUTOMATIC_OFFER without introducing a code variable for automatic-only offers.
- Require literal checkout-specific copy communicating a set of possible code offers (subject to checkout eligibility). Use the current existing Admin translation mechanism and 20 locales; no extra `INITIAL_*` enum.
- Keep existing `offer.code` single-code and all alternative-product template semantics intact. Freeze distinct revision and Meta review/approval identity; Background may select only actually approved revision.

### Shared-sender Reply instruction — normative 31 October 2026

For **every new initial recovery template revision** that ARCH-052 can select, including NO_OFFER, CODE_OFFER and AUTOMATIC_OFFER, both `promotionTarget: CHECKOUT` and `ALTERNATIVE_PRODUCT` where present, and approved TEXT/IMAGE header variants:

- The **visible BODY** must identify the exact merchant using trusted `shop.name` (`RecoveryTemplateSemanticKeySchema` already supports this variable). Do not rely on the shared WhatsApp sender profile or an optional image/logo for merchant identity. The displayed merchant name must be a bound AST variable supplied from the current authenticated recovery shop, not model-written copy or a client-supplied free-text value.
- Include the following **English semantic reference** (not literal text to paste across 20 locales): for CHECKOUT, `From {{shop.name}}. Need help with this basket? Use WhatsApp's Reply option on this message, then type your question or send a voice note (up to 2 minutes).` For ALTERNATIVE_PRODUCT, replace `this basket` with `this offer or your basket`. The `{{shop.name}}` notation denotes a real existing semantic binding, not a raw escaped template string.
- The instruction MUST say to use WhatsApp's **Reply option on this specific message**, not merely to type in the chat. The locale translation must preserve that operation, the two permitted input types (text or voice note), the existing two-minute voice limit, and the distinction between the recovery basket and an optional *different* promotional product.
- Author/freeze a **new, independently approved immutable Meta revision** for each affected combination of shop/WABA, purpose, target, header kind and locale. Never mutate an already approved frozen revision or reuse its approval for different body copy. Do not add a new Meta purpose enum, footer parameter, URL button, placeholder, Shared schema or data model solely for this instruction.
- Only published, provider-approved revisions carrying the shop-name and contextual-Reply semantics are eligible for ARCH-052 initial sends. Old approved revisions remain historical/usable by otherwise unaffected workflows, but **cannot be selected as the compliant initial-outreach revision**. When the required approved revision is not yet available, Background-008 must fail closed with a typed no-send (not silently send copy lacking the instruction).
- Update the established i18n catalogues for all 20 supported locales, protecting variables/placeholder counts and Meta body lengths; do not make translation-specific assumptions about merchant names. The Admin preview and submitted provider template must show identical semantics.

## Out of Scope

- No provider upload; ARCH-052-BACKGROUND-012 owns the Meta IMAGE sample handle. No dynamic checkout URL validation or generation, product search, policy ranking, Woo restore application or direct Meta send.
- Do not edit `ARCH-052-SHOPIFY-001`, `ARCH-052-MCP-005` or `ARCH-049-BACKGROUND-003`.

## Requirements

- Max 3 codes are rendered by Background into one bounded text parameter in selected, source-confirmed order. Code list is not an arbitrary merchant/model text input.
- The checkout-target code template can display one or more codes; a singular CODE or AUTOMATIC template is never chosen for a multi-offer set. Mixed CODE+AUTOMATIC groups are permitted only if a separately approved revision truthfully mentions both components; otherwise fallback to a supported singleton.
- No claim that codes have been redeemed, cannot expire or will necessarily stack; preserve independently approved fallback when multi template unavailable.
- As immutable Meta review is asynchronous, do not mark new variant approved without actual Meta provider approval evidence.

### Source and registration boundaries

- Reuse `moda-interact-admin/src/lib/admin/whatsapp-templates/authoring/` (`registry.ts`, `draft-operations.ts`, validation/compiler/preview and translation tests), existing `shop.name` binding and existing immutable publication/Meta approval identity. Inspect the current actual file layout before editing; do not duplicate an authoring pipeline.
- No order-confirmation/transactional template is created by this task. The photographed `Order confirmed` example is a separate provider/template lifecycle, **not** a recovery purpose. Do not invite order support in ARCH-052 copy until a distinct verified order-to-conversation route exists.

## Work Items

- [x] Add `offer.codes` to authoring variable registry/allowed checkout variables, compile and preview.
- [x] Test freeze, submission-plan identity, wrong target/locale, immutable approval fingerprint, and preservation of the alternative-product path. Provider submission/approval remains an explicit external step.
- [x] Add canonical initial Reply copy for all 20 supported locales and integrate it with translation segmentation, preview, compilation, and provider submission snapshots.

- [x] Implement new initial-recovery TEXT/IMAGE template BODY revisions with the shop-name semantic and exact Reply/text/voice meaning for CHECKOUT and ALTERNATIVE_PRODUCT, for all existing initial purposes and 20 supported locales.
- [x] Add Admin freeze/translation/preview/provider-payload tests for all purpose/target/header/locale identities, preservation of the existing `shop.name` AST token and immutable approval/fingerprint changes.
- [x] Test that old approved copy is not treated as the new compliant version and that missing/unreviewed Meta approval cannot be promoted to approved.

## Interfaces / Contracts

Published Shared `RecoveryTemplateSemanticKeySchema` supports `offer.codes`; existing `RecoveryTemplateFrozenBindingsSchema` binds its position in approved TEXT/IMAGE checkout CODE_OFFER template. Example prepared text: `Use SAVE10 and SHIPFREE, subject to checkout eligibility` (from source-grounded codes only). No new Meta API component type or checkout URL slot is introduced.

## Dependencies

- ARCH-052-SHARED-012
- ARCH-052-ADMIN-002

## Enables

- ARCH-052-BACKGROUND-008
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
- `ARCH-052-SYSTEM-TEST-003` — shared sender contextual reply certification.

## Acceptance Criteria

- [x] Multi-code template can be reviewed/approved independently of BACKGROUND-008 and other currently active task branches. Actual provider approval remains asynchronous and was not performed in this task.
- [x] Original single-code, single-automatic and no-offer registrations stay usable, with immutable purpose/target/header/locale guarantees.
- [x] No product/media provider call from Admin or second grant model was added.

- [x] New ARCH-052 initial templates require merchant identity and the specific-message WhatsApp Reply instruction, followed by text or voice note (at most two minutes); saved source cannot substitute generic chat instructions.
- [x] The English source and each of the 20 locale revisions preserve the required action and audio limit, use trusted `shop.name`, and distinguish basket versus alternative-product content. Body positions/variables are validated against Meta constraints.
- [x] Changing the body creates a distinct approval identity; unavailable/unreviewed revisions cannot be promoted as compliant initial outreach. Existing no-offer, single-code, automatic-offer and follow-up behaviors remain covered.

## Validation

- [x] Existing Admin authoring/translation/Meta registration suites and focused multi-code variable tests.
- [x] Production build (includes TypeScript checking) and `git diff --check`. Changed Admin source lint passes. Repository-wide lint still reports the unrelated existing `react-hooks/set-state-in-effect` error in `src/components/admin/whatsapp-templates/media/use-shop-brand-media-role.ts:26`.

- [x] Focused tests exercise NO_OFFER, CODE_OFFER, AUTOMATIC_OFFER and ALTERNATIVE_PRODUCT, TEXT and IMAGE where supported, missing merchant-name binding, frozen AST, translation token preservation, provider submission plan and exact copy-fingerprint mismatch. No real provider submission or approval was performed.

## Stop Condition

After the specified work, validation and acceptance criteria pass, update this task's Work Items and Completion Report, set status to `review`, hand back the implementation branch and evidence, and STOP. Do not self-accept, implement enabled tasks, modify other task/index files or push main.

## Implementation Notes

Use the launcher-resolved dedicated mirrored parent/implementation worktrees and shared structured logger. All unexpected errors must be logged with bounded identifiers and propagated to the owning failure/retry boundary. Never log coupon codes, customer information, bearer tokens or raw checkout URLs. Use relative workspace edit paths; do not touch `_index.md`.

## Completion Report

### Status

Attempt 1 implementation was returned for a narrow wording-validation correction. The task was implemented in `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-ADMIN-003`; no Meta provider upload or approval was performed.

### Files Changed

- Admin authoring registry, draft defaults, validation, immutable-save behavior, Meta snapshot validation and publication source validation.
- Translation source snapshot and locale compilation/reconstruction, including the protected Reply-instruction segment and reviewed 20-locale copy catalogue.
- Focused authoring, translation, compilation, Meta submission and publication tests/fixtures.
- Admin dependency pin and lockfile updated to `@modainteract/moda-interact-shared` 3.0.0, which exports `offer.codes`.

### Work Completed

- Added the typed `offer.codes` variable for checkout-target CODE_OFFER templates and retained the existing single-code binding. Checkout CODE and AUTOMATIC initial copy must truthfully describe possible eligible offers; automatic offers cannot bind a coupon code.
- Kept the existing purpose enum and alternative-product semantics. `offer.codes` changes the immutable authoring/prepared identity and frozen Meta body binding.
- Added the `shop.name`-bound contextual Reply instruction to new INITIAL revisions, with distinct checkout and alternative-product wording. Admin preview/compiler and all 20 locale paths preserve the Reply-on-this-message action, text or voice note, and two-minute limit for TEXT and IMAGE templates.
- Added publication eligibility checks so historical initial revisions without the new semantics are rejected as compliant ARCH-052 initial outreach. Meta submission snapshots require every locale to retain the appropriate localized initial semantics and continue to rely on existing provider approval evidence.
- No provider upload, production configuration change, new Shared schema or data model was made.

### Validation Results

All five final focused Admin suites passed (111 checks total):

- Authoring: 39 passed.
- Meta registration/submission: 19 passed.
- Publication: 22 passed.
- Compilation: 15 passed.
- Translation: 16 passed.

`npm run build` passed, including TypeScript checking and production route generation. Build output included existing BullMQ dynamic-dependency and optional `@valkey/valkey-glide` warnings.

Changed Admin source lint passed. Repository-wide `npm run lint` remains blocked by the existing `react-hooks/set-state-in-effect` error at `src/components/admin/whatsapp-templates/media/use-shop-brand-media-role.ts:26`, outside this task. `git diff --check` passed.

### Deviations

No provider upload or Meta approval was attempted because provider submission is explicitly out of scope. Unit tests verify the immutable submission plan and approval identity; they do not claim provider approval evidence.

### Assumptions

The provider-published Shared 3.0.0 contract is the required Admin dependency version for the `offer.codes` semantic.

### Unresolved Issues

The dependent Background implementation must fail closed with a typed no-send when it cannot find an actually provider-approved compliant initial revision. This cross-service runtime behavior belongs to `ARCH-052-BACKGROUND-008` and was not implemented here.

### Architectural Concerns

None identified within Admin ownership. Repository-wide lint has the unrelated existing error recorded above.

## Architect Review

### Attempt 1 Architect Review — Changes Requested

The implementation covers the requested authoring, locale, immutable approval,
and publication boundaries, and the reported focused checks/build passed. One
required wording guarantee is not enforced: the English AUTOMATIC_OFFER check
accepts `possible` or `available` alone as its multi-offer indicator. For
example, “Your basket may qualify for a possible automatic offer, subject to
checkout eligibility” passes the current regular expressions even though it
says there is one offer. This does not satisfy the task's plural/multi-discount
wording requirement.

Required correction:

- Tighten the AUTOMATIC_OFFER checkout-copy validation so a singular sentence
  cannot pass on `possible`/`available` alone. Require a clear plural/set
  formulation such as “multiple automatic offers”, “several eligible
  discounts”, or “choose from available offers”, while retaining the explicit
  checkout-eligibility condition.
- Add a regression test proving a singular “possible automatic offer” sentence
  is rejected and the supported plural forms still pass.

Attempt 1 is returned to Ready. No implementation acceptance is recorded.

### Reviewed Files

- `src/lib/admin/whatsapp-templates/authoring/validation.ts`
- `tests/unit/arch047-template-authoring-ast.test.ts`
- The task definition and Completion Report
- Admin translation, Meta snapshot and publication validation paths

### Validation Reviewed

The submitted report records 111 focused checks, successful production build,
changed-file lint and `git diff --check`. Repository-wide lint has the unrelated
reported error in `src/components/admin/whatsapp-templates/media/use-shop-brand-media-role.ts:26`.
No validation was rerun during this review.

### Architecture Conformance

The implementation remains within Admin ownership and correctly guards
merchant-bound contextual Reply copy, locale revisions, provider approval
identity and historical initial-template exclusion. The automatic-offer wording
guard needs the correction above before acceptance.

### Follow-up

After the wording guard and regression case pass, resubmit the same task attempt
for architect review. Do not start dependent tasks before acceptance.
