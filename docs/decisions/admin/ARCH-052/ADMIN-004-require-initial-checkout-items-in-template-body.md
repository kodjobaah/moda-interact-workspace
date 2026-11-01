---
id: ARCH-052-ADMIN-004
architecture_id: ARCH-052
title: Require a frozen checkout-items BODY binding in every initial Meta recovery template
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 25
executor: copilot
claimed_at: 2026-11-01T15:43:05Z
attempt: 1
depends_on:
  - ARCH-052-ADMIN-003
  - ARCH-052-BACKGROUND-005
enables:
  - ARCH-052-BACKGROUND-017
  - ARCH-052-SYSTEM-TEST-004
created: 2026-10-31
updated: 2026-11-01
---

# ARCH-052-ADMIN-004: Require checkout items in initial Meta recovery template bodies

## Architecture

- Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.
- Owner: `moda_admin`, repository `moda-interact-admin/`.
- This is a portable task definition **defined but not materialised**. Implement through the launcher-resolved dedicated `task/ARCH-052-ADMIN-004` parent and implementation worktrees. Do not implement in BG008's active worktree.

## Objective

Ensure **every** newly authored, frozen, reviewed and published `META_RECOVERY` template with `stage: INITIAL` visibly includes the **actual abandoned checkout items** in its **BODY** through exactly one `checkout.itemsSummary` semantic binding, independent of offer type, promotion target, locale and header kind.

## Context

- `authoring/registry.ts` currently excludes `checkout.itemsSummary` for `offerType: NO_OFFER` and for `promotionTarget: ALTERNATIVE_PRODUCT`; the CHECKOUT-offer branch allows it. `authoring/validation.ts` requires `shop.name` and Reply instructions for initial copies but does not require the basket binding for all initial variants.
- ARCH-052-BACKGROUND-005 is already Complete and implements the existing Shared `checkout.itemsSummary` semantic key using trusted `CheckoutRecovery.lineItems`, with a bounded, locale-aware first-three-lines + `+N` summary. No new Shared schema, variable, formatter or database column is needed.
- ARCH-052-ADMIN-003 is Complete, already preserving merchant-identity/Reply text, singular/plural offer copy, alternative-product separation and immutable Meta registration/approval.
- Historical frozen Meta template registrations cannot be rewritten to add another positional BODY variable: this is a **new immutable revision** requiring independent Meta approval. Authoring enforcement must not pretend historical registrations are compliant.

## Scope

Implement the basket-binding **authoring and publication** invariant within `moda-interact-admin/`; include all existing INITIAL purpose/offer/target/header and 20-locale variants. Extend existing tests, previews and provider submission validations, and preserve the immutable publication lifecycle.

## Out of Scope

- Do not modify `ARCH-052-BACKGROUND-008`, `ARCH-052-ADMIN-003`, existing accepted task Completion Reports or any `_index.md`.
- No Background sender change, production provider call, Meta approval bypass, additional templating system, new semantic key, Prisma migration, checkout item reader, new checkout URL generation or order-confirmation template.
- Do not change `FOLLOW_UP` or `MODA_CONVERSATION_WRAPPER` semantics. Do not impose IMAGE availability on TEXT templates.

## Requirements

### A. Mandatory variable, eligibility and BODY placement

Modify **these exact existing Admin source files** (additional directly related tests permitted):

1. `src/lib/admin/whatsapp-templates/authoring/registry.ts`: for `family === "META_RECOVERY" && stage === "INITIAL"`, allow `checkout.itemsSummary` in BODY for each `NO_OFFER`, checkout-target CODE/AUTOMATIC (single or plural), and alternative-product CODE/AUTOMATIC variant. Preserve other offer-specific variables exactly. Do not add it to the IMAGE/TEXT HEADER, FOOTER or URL button palettes, and do not extend wrapper allowances. Preserve existing FOLLOW_UP eligibility.
2. `src/lib/admin/whatsapp-templates/authoring/validation.ts`: for **initial, publication-compliant** Meta ASTs, reject unless `raw.body` contains **exactly one** `{ type: "variable", name: "checkout.itemsSummary" }`. Reject missing, duplicated, text-only simulation, a header-only occurrence, or an invalid variable position. Preserve all existing `shop.name`, contextual Reply, multi-code, alternative-product, image-header, Meta 1,024-character BODY, and at-most-ten BODY variable requirements. Make the rule reachable at each existing production freeze/review/publish/registration boundary that uses `requireInitialReply: true`; incomplete editor drafts may retain the existing non-publishable editing behaviour.
3. `src/lib/admin/whatsapp-templates/authoring/draft-operations.ts`: ensure newly constructed INITIAL BODY defaults/variant changes include exactly one semantic node in a clearly labelled original-basket section. Preserve the complete reviewed Reply tail and the existing offer-specific copy. In ALTERNATIVE_PRODUCT, visibly separate **original abandoned items** from the different recommended product and do not imply its discount applies to the original basket.
4. `src/lib/admin/whatsapp-templates/authoring/compiler.ts`, `src/lib/admin/whatsapp-templates/publishing/source.ts`, `src/lib/admin/whatsapp-templates/meta/snapshot.ts`, and `src/lib/admin/whatsapp-templates/compilation/reconstruction.ts`: reuse their established frozen AST, provider BODY example, translation and registration mechanisms. Only adjust these files if needed to ensure the updated invariant is checked in every publishable path. Do **not** build a second compiler or change positional binding schema. The compiled `parameterBindings.body` position must correspond to exactly one `{{N}}` token in the submitted immutable Meta BODY; its example value must be the existing safe registry sample, not merchant/customer data.
5. `src/lib/admin/whatsapp-templates/translations/source-snapshot.ts` and existing locale/translation operations: retain the new semantic node and its position through all **20 supported locale** review/compile flows, together with the existing merchant name and Reply instructions. Each locale requires reviewed, meaningful original-basket wording; preserve each locale's translation-review gate, not machine-inferred English copy.

Do not insert raw `{{...}}` strings into AST literal text. The merchant/product/cart identities are resolved at runtime; Admin examples must never contain actual customer data.

### B. Exact template matrix (all must be independently validated)

| Stage | Offer type | Target | Header | Mandatory BODY semantic |
|---|---|---|---|---|
| INITIAL | NO_OFFER | none | TEXT | `checkout.itemsSummary` exactly once |
| INITIAL | CODE_OFFER | CHECKOUT | TEXT / approved IMAGE where supported | Exactly once, plus existing singular/plural code binding |
| INITIAL | AUTOMATIC_OFFER | CHECKOUT | TEXT / approved IMAGE where supported | Exactly once, plus existing honest automatic wording |
| INITIAL | CODE_OFFER | ALTERNATIVE_PRODUCT | TEXT / approved IMAGE where supported | Exactly once, explicitly described as **original basket** |
| INITIAL | AUTOMATIC_OFFER | ALTERNATIVE_PRODUCT | TEXT / approved IMAGE where supported | Exactly once, explicitly described as **original basket** |
| FOLLOW_UP | Any existing valid variant | Existing rules | Existing rules | **No new mandatory condition** |
| MODA_CONVERSATION_WRAPPER | Any | Existing rules | Existing rules | **No change** |

IMAGE headers are optional and separate; `checkout.itemsSummary` remains a textual BODY parameter even when the header is IMAGE. The BODY displays the existing bounded first-three-line summary and `+N` remainder, not a fabricated entire-basket transcription. No price/savings is inferred from the summary.

### C. Immutable registration and live readiness

- Changed source BODY or locale means a new immutable content hash, binding fingerprint and provider-review revision. Preserve historical source, approval and Meta provider IDs without rewriting them.
- Draft save, locale review, source publication, frozen provider submission and preview must agree on the exact BODY parameter sequence. A newly compliant definition is **not provider-approved** until Meta actually approves it; do not mark it APPROVED in tests or runtime config without provider evidence.
- If a legacy initial registration lacks the binding, Admin must not treat it as compliant for new initial outreach. Background-017 owns the separate final runtime gate and will exclude it. This task does not change BG008's active implementation.
- Visible merchant name, basket label, dynamic basket summary, Reply-on-this-message instructions, text/voice note guidance, and CTA remain independently present; ALTERNATIVE_PRODUCT's promotion is not part of the original basket.

## Work Items

- [ ] Update eligible-variable registry for all INITIAL variants without broadening FOLLOW_UP/wrapper variables.
- [ ] Enforce exactly-one BODY semantic at all publishable validation paths; reject missing/duplicate/header-only/static imitations.
- [ ] Update INITIAL defaults and alternative-product copy; preserve locale-aware Reply tail and source translation structure.
- [ ] Update compiled/translated Meta examples, immutable revision and snapshot conformance tests across 20 locales.
- [ ] Document Meta reapproval requirement for revised immutable template versions; do not claim provider approval was executed.

## Interfaces / Contracts

**Existing Shared contract (no modification):** `@modainteract/moda-interact-shared/recovery-template-bindings` semantic key `checkout.itemsSummary` and existing frozen `parameterBindings.body` `{ position: number, variable: string }` entries.

**Exact AST node:**

```json
{ "type": "variable", "name": "checkout.itemsSummary" }
```

**Valid illustrative English BODY AST fragment** (part of a full AST; do not use raw template tokens):

```json
[
  { "type": "text", "value": "You left these items in your basket: " },
  { "type": "variable", "name": "checkout.itemsSummary" },
  { "type": "text", "value": ". " }
]
```

Compiled position is determined by the existing `bodyText()` compiler from the order of BODY variable nodes. The verified consumer must identify `checkout.itemsSummary` through the **frozen semantic bindings**, not by searching translated text for an English phrase.

**Producers:** Admin authoring/translation/compiler. **Consumer:** existing Meta registration snapshots and subsequent Background-017 send admission. **Version:** existing `schemaVersion:1`; no new API or local clone.

## Dependencies

- `ARCH-052-ADMIN-003` — accepted template semantics and 20-locale instructions.
- `ARCH-052-BACKGROUND-005` — accepted existing summary semantic and locale-aware runtime binder.

## Enables

- `ARCH-052-BACKGROUND-017` — runtime send guard after BG008 and optional BG007.
- `ARCH-052-SYSTEM-TEST-004` — terminal cross-platform certification after implementation tasks.

## Acceptance Criteria

- [ ] For every INITIAL variant in matrix A/B, `eligibleVariables` allows the BODY semantic and `validateTemplateAst(..., { requireInitialReply:true })` rejects any absent/duplicated checkout-summary variable.
- [ ] Each of the 20 locale review/publication paths round-trips exactly one BODY semantic, its provider position, and the localized original-basket label; existing BODY parameter, language and character limits hold.
- [ ] Header-only, literal imitation, missing and duplicated body nodes fail; TEXT/IMAGE, single/multi CODE, AUTOMATIC and alternative-product remain distinct and correct.
- [ ] Translation and publication preserve the existing `shop.name` + contextual Reply, dynamic buttons and offer provenance rules.
- [ ] New BODY revisions are immutable and must obtain independent Meta approval; no previously approved hash/registration is altered or implicitly accepted.
- [ ] Existing FOLLOW_UP and wrapper validation/authoring paths remain unchanged.

## Validation

- [ ] `tests/unit/arch047-template-authoring-ast.test.ts`: matrix and negative cases.
- [ ] `tests/unit/arch047-template-translations.test.ts`: all 20 locale structural/semantic/position checks.
- [ ] `tests/unit/arch047-template-compilation.test.ts`, `tests/unit/arch047-template-meta-snapshots.test.ts` and `tests/unit/arch047-template-publication-pure.test.ts`: frozen provider BODY, identity and approval checks.
- [ ] `tests/integration/arch047-template-authoring.postgres.test.ts` and `tests/integration/arch047-template-publication.postgres.test.ts` with disposable PostgreSQL: accepted/rejected immutable revision flows.
- [ ] Repository-declared changed-file lint, typecheck/build and `git diff --check`; record exact invoked commands/results, not assumed scripts.

## Stop Condition

After the specified Work Items, Acceptance Criteria and validation are completed, update only this task's execution metadata, checklists and Completion Report, set `status: review`, return control to `moda_architect`, and **STOP**. Do not start BG017, overwrite the historical ADMIN-003 task, or edit `_index.md`.

## Implementation Notes

Use the existing `authoring/registry.ts` and `validation.ts` path; no second renderer or schema. Keep each source/test module bounded and follow the existing Admin translation/publishing patterns. Use `@modainteract/moda-interact-shared/logging`; preserve actual upstream provider/SDK errors with bounded redaction, and propagate unexpected failures. Never log customer names, checkout URLs, product descriptions or generated copy.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

Only immutable newly authored Meta INITIAL revisions are accepted as compliant; historical provider approvals remain unchanged.

### Unresolved Issues

None in task scope.

### Architectural Concerns

None at definition time.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting repository implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not yet assessed.

### Follow-up

None.
