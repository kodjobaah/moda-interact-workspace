---
id: ARCH-047-SHOPIFY-001
architecture_id: ARCH-047
title: Restrict Shopify merchant follow-up choices and admission to Moda-authored templates
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-047-DATABASE-001
enables:
  - ARCH-047-SYSTEM-TEST-001
created: 2026-10-26
updated: 2026-10-26
---

# Restrict Shopify merchant follow-up choices and admission to Moda-authored templates

## Architecture

Architecture: `ARCH-047` — `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`; coordinator `moda_architect`. Defined against the 26 October 2026, 06:28 workspace snapshot. The task definition was published on `origin/main` in `5c329bbc`; this developer takeover is being materialised on its canonical parent task branch. No implementation is claimed before the canonical launcher claim.

## Objective

Replace the Shopify recovery human follow-up's legacy template list/admission allowlist with a tenant-scoped catalogue of eligible **Moda-authored, explicitly published** Follow-up template choices, leaving Background BG007 authoritative for verified offer resolution and final sending.

## Context

`moda-interact/app/services/recoveries/recovery-human-commands.server.ts` still filters `purpose: "checkout-recovery"` in `readApprovedRecoveryTemplates` and in `RECOVERY_FOLLOW_UP_TEMPLATE` admission. The new six-purpose catalogue instead uses `FOLLOW_UP_NO_OFFER`, `FOLLOW_UP_CODE_OFFER` and `FOLLOW_UP_AUTOMATIC_OFFER` with a non-null Meta registration; eligibility cannot be inferred solely from an `APPROVED` variant. Merchant intent remains subject to Background BG007's final read-only checkout/offer and provider-safety recheck.

## Scope

- Own only `moda-interact/` Shopify authenticated recovery-list/detail/server-action/UI files and focused tests; start from the actual existing `readApprovedRecoveryTemplates`, merchant command submission and reply-composer paths.
- Use the current conversation/recovery/shop identity and validated sender WABA to list **only** live, enabled, non-retired, locally published, Meta-approved and current provider-approved `FOLLOW_UP_*` variants linked to a Moda-authored registration. Reject ambiguous shop/WABA/name/language records.
- Preserve existing `templateVariantId` merchant intent for an exact candidate and derive provider template name/language from DB; do not let the browser supply Meta names, prices, checkout URLs, discount codes or template parameters as trusted values.
- Extend Shopify preview/selection UI only as required to display the appropriate source language and purpose and report a safe unavailable state without inventing an offer.

## Out of Scope

- No changes to `moda-interact-background`, hosted Woo API, WordPress plugin or DB schema; no creation/editing of Meta templates; no offer-eligibility evaluation or billing admission in Shopify; no cart/checkout mutations.

## Requirements

**R1 — Authoritative selection.** For merchant-initiated sequence-two only, query `WhatsAppTemplateVariant` joined to `WhatsAppTemplateMetaRegistration` and definition/locale, using the current authenticated shop, configured sender and exact target language. Accept only `purpose` in `FOLLOW_UP_NO_OFFER`, `FOLLOW_UP_CODE_OFFER`, `FOLLOW_UP_AUTOMATIC_OFFER`; reject null registration, expired/stale status, retired/unpublished definition, disabled variant and wrong WABA. Do not return templates merely because a legacy row says `APPROVED`.

**R2 — Checkout/offer semantics.** Only offer a choice when the existing human-control, due-time, rolling-window and sequence-two restrictions allow it. If there is no verified checkout-specific positive-offer evidence, the UI must not promise eligibility for CODE/AUTOMATIC. It may show safe No Offer candidates while Background BG007 still re-evaluates the exact chosen variant. No Shopify GraphQL/Meta metadata GET in the merchant command transaction.

**R3 — Admission and replay.** Validate `templateVariantId` in the server action against the same current catalogue; reject stale/forged variants. Persist the existing idempotent sequence-two claim and provider name/language snapshot only after the existing successful admission conditions; the Background process will re-resolve all parameters and perform the final fence. Do not add staff roles or a second outbound queue.

**R4 — Retire obsolete behaviour.** Remove all `purpose: "checkout-recovery"` filters and obsolete imported-template choices in this Shopify interface; remove dead helpers/tests only after checking real imports, while preserving human text, tenant scope, STOP/consent, late response and billing behaviour.

## Work Items

- [ ] Replace both legacy selectors in `recovery-human-commands.server.ts` with the DB-backed current `FOLLOW_UP_*` catalogue and exact variant validation.
- [ ] Update dedicated merchant template selector/preview React components and state hook as necessary without bundling the whole Recovery Detail UI into one file.
- [ ] Replace legacy mocks and add post-window, selection, replay, stale/foreign WABA and no-offer tests.
- [ ] Document actual task worktree/commit/test evidence and source-level obsolete-code cleanup.

## Interfaces / Contracts

Consumes `Shop`, `WhatsAppTemplateVariant`, `WhatsAppTemplateMetaRegistration`, the published template definition and existing `MerchantConversationSendCommand` (name/language command snapshot). Browser sends only the stable `templateVariantId` already supported by Shopify. BG007 owns offer verification, fresh template resolution, parameter binding and provider final admission; this task does not change that ownership.

## Dependencies

- `ARCH-047-DATABASE-001` (Complete in the supplied snapshot).

## Enables

- `ARCH-047-SYSTEM-TEST-001` after acceptance and integration.

## Acceptance Criteria

- [ ] Shopify only exposes Moda-authored, published, provider-eligible `FOLLOW_UP_*` assignments for the correct shop/WABA/language, and denies legacy/null-registration/stale/ambiguous variants.
- [ ] Positive-discount candidates cannot be presented as a verified customer-specific saving without read-only provider evidence. BG007 independently rejects an invalid offer/template at dispatch.
- [ ] Existing human-control, service-window, one-follow-up, idempotency, consent, STOP and billing semantics remain unchanged.
- [ ] No production `purpose: "checkout-recovery"` filter or obsolete imported-template action remains in this Shopify merchant command/list path; no duplicate template picker or monolithic component is introduced.

## Validation

- [ ] Focused Shopify server-action and UI tests, lint/typecheck per actual package scripts; test stale consent/offer/assignment and denied-user boundaries.
- [ ] `git diff --check` and source-reference check for legacy `checkout-recovery` purpose in touched Shopify paths; preserve unrelated code.

## Stop Condition

Complete only this Shopify task, update Completion Report and set task to `review`, then STOP. Do not change system-test, parent architecture, other repositories or `_index.md` files.

## Implementation Notes

Use launcher-prepared dedicated mirrored `task/ARCH-047-SHOPIFY-001` worktrees and the current task branch as required by the repository policies. The source snapshot is not proof of current main; reconcile exact installed dependency versions at implementation start. Do not weaken Background's final admission by relying on early UI eligibility.

## Completion Report

### Status
Not Started — defined but not materialised.

### Files Changed
None.

### Work Completed
None.

### Validation Results
Not run.

### Deviations
None.

### Assumptions
No new DB schema or merchant auth model.

### Unresolved Issues
Checkout-specific discount verification is incomplete in the reviewed BG004 defaults; positive-offer UI and tests cannot claim provider-backed eligibility until that separate capability exists.

### Architectural Concerns
None additional.

## Architect Review

### Review Status
Pending.

### Review Notes
No implementation reviewed.

### Reviewed Files
None.

### Validation Reviewed
None.

### Architecture Conformance
Not assessed.

### Follow-up
Review the final integration with BG007; do not use system testing as an implementation dependency.

## Developer Ownership Amendment

- Date: 2026-10-26.
- Change: The developer explicitly invoked `/moda_developer_create ARCH-047-SHOPIFY-001` for this Ready agent-owned task. Execution ownership is transferred to the developer, and completion is set to developer review.
- Preserved: `assigned_agent: moda_app`, coordinator, repository, task scope, acceptance criteria, validation requirements, dependency gate, Ready eligibility, and attempt 0. The explicit dependency `ARCH-047-DATABASE-001` was verified complete. This amendment does not itself claim an implementation attempt.
