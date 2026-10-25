---
id: ARCH-047-BACKGROUND-001
architecture_id: ARCH-047
title: Implement recovery WhatsApp template preparation module
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 30
executor: developer
claimed_at: 2026-10-25T17:01:45Z
attempt: 1
depends_on:
  - ARCH-047-DATABASE-001
enables:
  - ARCH-047-BACKGROUND-006
  - ARCH-047-BACKGROUND-007
created: 2026-10-23
updated: 2026-10-25
---

# Implement recovery WhatsApp template preparation module

## Architecture

Architecture ID: `ARCH-047`.

Architecture document: `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`.

Coordinator: `moda_architect`.

This is the **first module-first Background task**, replacing the original broad `BACKGROUND-001` specification. Source snapshot: 23 October 2026 with the consolidated DB001 Attempt 7 authoring/publishing model reviewed 24 October 2026. This task is `pending` until its real prerequisites are Complete; No new ARCH-047 Shared template package is required; Admin persists compiled payload and binding data for this module to consume.

## Objective

Provide **one reusable, independently testable `RecoveryTemplatePreparer` module** that selects an approved, enabled and explicitly shop-assigned **Moda-authored** recovery Meta template from PostgreSQL, resolves deterministic language fallback and **populates** already-compiled, frozen per-language parameter bindings with trusted runtime values to produce a prepared provider payload. Return the prepared payload or a typed unavailable reason **without sending a message**, evaluating discounts, calling Meta metadata APIs or altering any caller's existing recovery/admission logic.

## Context

The existing `src/services/whatsapp-template-selector.service.ts` performs shop/WABA/purpose/language selection from `WhatsAppTemplateVariant`, exposing historical provider metadata-category verification semantics. Existing initiation, automated follow-up, human command and final outbound paths contain logic that the original ARCH-047 task attempted to change together. Under the agreed modular plan those caller changes are explicitly deferred to `BACKGROUND-006` and `BACKGROUND-007`.

DB001 adds `WhatsAppTemplateDefinition`, multilingual locales, Meta registrations with immutable `componentsSnapshot`/`parameterBindingsSnapshot` and a nullable `WhatsAppTemplateVariant.metaRegistrationId` provenance relation. Template content is Moda-authored only; a missing relation means a legacy/unproven assignment and must not become selectable through this new module.

## Scope

Work only in `moda-interact-background/`; implement a cohesive folder such as:

```text
src/services/recovery-template-preparation/
  recovery-template-preparer.service.ts     # public facade
  recovery-template-selection.ts            # purpose/locale/assignment selection
  recovery-template-bindings.ts             # ordered parameter resolution
  recovery-template-brand.ts                # tenant-scoped ShopBrand text/media references
  recovery-template-repository.ts           # focused Prisma reads
  recovery-template.types.ts                # module-private ports/results
```

This is **suggested modular structure**, not permission to implement unrelated shared machinery. Reuse/adapt the existing `whatsapp-template-selector.service.ts` internals where appropriate; leave it callable by legacy consumers until integration tasks migrate callers. Keep pure helpers separate from DB access and external boundary ports; inject dependencies for focused tests. Avoid large catch-all files.

## Out of Scope

- No changes to initial recovery, scheduled follow-up, AI, merchant command or human handover call sites. These belong to `BACKGROUND-006`–`009`.
- Do not edit `outbound-message-delivery.service.ts`, either send fence, credit reservation/compensation or `outbound-whatsapp-admission.service.ts` in this module task. `BACKGROUND-006` later integrates a shared final-send adapter; `BACKGROUND-007` consumes it.
- Do not implement the offer resolver (`BACKGROUND-004`), Meta template creation/status reconciliation (`BACKGROUND-003`), translation (`BACKGROUND-002`), wrapper rendering (`BACKGROUND-005`), merchant UI or Admin publication.
- Do not parse or compile Admin authoring AST, duplicate runtime parameter-binding data definitions, add Prisma tables, perform Graph API metadata preflight, or implement billing/consent logic, webhook handling or Meta delivery calls.
- Do not delete the legacy category-preflight service or break existing callers merely to make this new preparer available before migration. Remove old plumbing only in the later integration task after all callers have migrated and tests prove it is unreachable.

## Requirements

### R1. Narrow facade and input contract

Expose a typed `RecoveryTemplatePreparer.prepare(input)` entrypoint with shop ID, resolved configured sender WABA, recovery stage (`INITIAL` or `FOLLOW_UP`), **verified offer presentation** (`NO_OFFER`, `CODE_OFFER` or `AUTOMATIC_OFFER`), canonical conversation/merchant language inputs, and trusted read-only checkout/customer runtime values. The caller is responsible for obtaining the verified offer; this module never chooses or evaluates discounts.

The module maps stage + verified offer presentation to one of the **six agreed recovery purpose identifiers**, using the agreed six-purpose mapping documented in the ARCH-047 parent architecture and Admin-prepared definition metadata. It returns a `PreparedRecoveryTemplate` or a discriminated unavailable result; include the exact assigned variant ID, registration ID, definition ID, shop/WABA/purpose, provider template name/language, selected canonical language, ordered Meta header/body/button parameters and binding fingerprint or equivalent verification evidence. Omit PII from diagnostics.

### R2. Database-authoritative selection

Query only local Prisma records and current approved/enabled assignments. Require all of: matching shop, configured sender WABA, recovery purpose, available canonical language, non-null Moda `metaRegistrationId`, connected registration with `APPROVED` provider status, no blocking drift/revocation/disable, and exact template/provider identity. Refuse ambiguous active assignments in a slot; never select arbitrarily. Preserve deterministic exact → base → merchant default → explicitly configured platform fallback precedence consistent with the existing selector. No HTTP `message_templates` lookup, cached Meta category preflight or trust in user-supplied WABA values.

The new module does not automatically accept historical variants lacking registration provenance. Until explicit publication of Moda-authored versions, an unavailable result is valid; do not silently use an external template.

### R3. Frozen language-specific bindings

Read only the **Admin-compiled** frozen `WhatsAppTemplateMetaRegistration.parameterBindingsSnapshot` and `componentsSnapshot` for the exact selected language. Never parse/compile the Admin AST. Resolve parameters from trusted values only, including customer name when safe, shop name, valid current checkout URL and independently verified offer details. Preserve the approved component index, button index and variable order for that language; translations may reorder variables. Do not substitute a guessed checkout link, coupon, amount or expiry. Validate the stored component/binding snapshot compatibility and fail closed on missing required variables, unsupported component types, corrupt fingerprints, provider/locale mismatch or malformed values.

### R3a. ShopBrand text variables and typed URL references from the Admin editor

The ADMIN-003 English composer currently offers these **exact semantic keys** in its text-token pickers: `shopBrand.brandName`, `shopBrand.logoUrl`, `shopBrand.logoAltText`, `shopBrand.logoWidth`, `shopBrand.logoHeight`, `shopBrand.squareLogoUrl`, `shopBrand.squareLogoAltText`, `shopBrand.coverImageUrl`. It also offers `customer.firstName`, `shop.name`, `checkout.url` and an optional checkout link button. This module resolves only keys actually referenced by the **frozen, Admin-compiled** binding snapshot; it must not parse the AST, discover placeholders from displayed text, or inject extra text into the approved components.

| Frozen semantic source | Runtime resolution | Missing/unusable treatment |
|---|---|---|
| `shopBrand.brandName` | Optional `shopify.ShopBrand.brandName` for **the selected shop** | Typed missing-binding result; use `shop.name` only when the Admin-authored binding contract explicitly selects that source; no silent substitution |
| `shopBrand.logoAltText`, `shopBrand.squareLogoAltText` | Optional, bounded ShopBrand text metadata | Typed missing-binding result; these are text fields, **not** a WhatsApp image alt-text feature |
| `shopBrand.logoWidth`, `shopBrand.logoHeight` | Optional integer ShopBrand metadata, stringified only for an explicitly compiled **text** placeholder | Missing/invalid => typed unavailable; integers do **not** resize or configure WhatsApp header images |
| `shopBrand.logoUrl`, `shopBrand.squareLogoUrl`, `shopBrand.coverImageUrl` | **TEXT URL binding only** when a verified HTTPS, WhatsApp-ready, R2-hosted derivative is available through the approved brand-media metadata/port | Until the separate ShopBrand media architecture exists and reports `READY`, refuse the binding. Never substitute an unprocessed merchant-controlled source URL or treat its string as an attached image |

Use a bounded **shopId-scoped** Prisma brand-read adapter; `ShopBrand` is optional and currently lives in the `shopify` schema, so do **not** assume WooCommerce shops have a populated brand record. Batch only the required column reads once per preparation; do not perform cross-tenant lookups. Treat empty strings, unexpected types, overlong values and unsupported characters as unavailable according to the approved component/binding limits; do not invent missing brand values or leak raw URLs/checkout URLs in logs.

The existing Admin editor's image-URL tokens are **text links**, not image headers. A future image-header binding requires a distinct, explicitly compiled media component and an approved READY processed asset from the separate **proposed ARCH-049 ShopBrand media-normalisation architecture**. Expose an injectable `resolveReadyShopBrandMedia(shopId, role)` boundary or equivalent typed unavailable result, but **do not implement fetching, image inspection, resizing, R2 uploads, source asset lifecycle or new Prisma columns in BG001**. Fail closed for a compiled image-header request until that media contract is available; do not change its required header type or fall back to source URLs. Any subsequent adapter implementation must stay with the agreed media owner.

### R3b. Checkout link and dynamic URL-button bindings

Resolve `checkout.url` only from the trusted, shop/recovery-associated **current** checkout context. For the editor's link button, consume the **Admin-frozen** approved HTTPS prefix and typed/encoded dynamic URL-button binding; supply the required runtime suffix/parameter in the exact component and button position without manufacturing a new URL shape, concatenating an untrusted destination, or appending checkout data twice. Reject missing or stale checkout links, malformed/unapproved redirect hosts or cross-shop destinations, unsupported button shapes and required media/bindings with no safe value. A URL printed in a body is ordinary text, **not** automatically a WhatsApp CTA button.

### R4. No side effects or admission bypass

`prepare` performs no send, provider HTTP, Meta create/edit, Redis queue write, credit reservation, bill, discount application or cart/checkout update. The returned exact variant/registration identifiers permit the **existing final outbound fence** to re-check assignment and provider status later; the preparer is not the final send permission. Error outcomes never count as an outreach attempt or permanently consume a credit.

### R5. Modular, testable implementation

Keep repository queries, language selection, variable resolution and facade coordination separable. Do not introduce a generic logger, duplicate the existing Shared internationalisation utilities, create an AST parser, or move offer resolution or final send policy into this module. Existing `WhatsAppTemplateSelectorService` may remain a legacy compatibility path until subsequent task call sites migrate; record precisely which path is new and which still needs integration.

## Work Items

- [ ] Inspect existing selector, DB001 Prisma models and Admin-persisted components/binding snapshots; identify minimal module-local ports.
- [ ] Implement focused Prisma selection with shop/WABA/purpose/language/provenance filters and explicit ambiguity outcomes.
- [ ] Implement frozen **Admin-prepared** parameter resolution, correct for language-specific reordered placeholders, without AST parsing.
- [ ] Resolve the eight screenshot-exposed ShopBrand keys by exact type/source, including missing-field and non-Shopify-brand cases; separate text links from actual image media, and never use raw original image URLs as Meta media.
- [ ] Prepare the existing Admin-compiled checkout CTA button from its trusted URL/prefix/encoded dynamic binding; provide an explicit unavailable result for missing checkout data or unsupported URL/media components.
- [ ] Expose one typed `PreparedRecoveryTemplate` facade and structured unavailable outcomes for callers.
- [ ] Add focused unit and database integration coverage, including legacy/unlinked rows, disabled/revoked/drifted providers and invalid bindings.
- [ ] Record exact source changes, worktree/synchronisation evidence and validation commands in the Completion Report; return control to architect without touching callers.

## Interfaces / Contracts

Consumes accepted `ARCH-047-DATABASE-001` schema and Admin-prepared `MetaRegistration.componentsSnapshot`/`parameterBindingsSnapshot`; reuses existing published Shared language canonicalisation utilities only where applicable. There is **no new ARCH-047 Shared authoring contract prerequisite**. For the module-private facade define a bounded `PreparedRecoveryTemplate` / `TemplateUnavailable` result. BG004 owns the verified offer decision; BG006/BG007 own integration, not duplicate selector/binding implementations.

`WhatsAppTemplateVariant.metaRegistrationId → WhatsAppTemplateMetaRegistration → WhatsAppTemplateLocale/Definition` is provenance, not permission to create a new Meta template. A successful prepared payload is not permission to send: existing consent/STOP, service-window, moderation, billing and final database fences remain authoritative at the outbound boundary.

## Dependencies

- `ARCH-047-DATABASE-001` — consolidated authoring/locale/registration/shop-variant contract, **Complete** before this task becomes Ready.

No Admin import task dependency. Approved published fixtures are sufficient to validate preparation without forcing Admin implementation to precede this module.

## Enables

- `ARCH-047-BACKGROUND-006` — Automated Recovery Integration.
- `ARCH-047-BACKGROUND-007` — Merchant Post-Window Integration (also requires the common adapter provided by BG006).

The enabled tasks are **planned**, not yet materialised. Do not start either from this task.

## Acceptance Criteria

- [ ] For each of six purpose combinations the preparer selects only a valid local shop/WABA/locale-assigned **Moda-authored** registration and yields a fully parameterised provider payload.
- [ ] English and a translated language with reordered placeholders produce different but semantically correct positional parameter arrays from one trusted variable set.
- [ ] Wrong shop/WABA, no approval, disabled row, registration absent, drift/revocation, ambiguous slot and missing required variables yield explicit unavailable results and no provider call/charge.
- [ ] `brandName` and text alt fields bind from the same shop; optional/null or wrong-shop ShopBrand data does not produce invented output. Width/height bind only as optional numeric **text**; they never alter a WhatsApp media header.
- [ ] The three image-URL text bindings never use raw ShopBrand source URLs; a READY processed, approved R2 derivative is required. Actual image-header payloads use a separately typed media binding or return `TEMPLATE_UNAVAILABLE_MEDIA_NOT_READY` (or equivalent) until the separate asset-processing architecture is available.
- [ ] The approved checkout dynamic CTA URL suffix is safely bound/encoded once; missing, stale or untrusted destination fails closed. Tests distinguish body URL text from an actual button parameter.
- [ ] The implementation has a cohesive new module facade with isolated repository, matching, bindings and unit-test responsibilities; it has no direct dependants in the existing orchestration paths at handoff time.
- [ ] Legacy recovery, merchant command, consent/STOP, final admission and existing outbound contracts are unchanged; no current send path is broken or migrated by this task.

## Validation

- [ ] Focused selector/binding unit tests with malformed/duplicate/stale assignment and translation binding fixtures.
- [ ] ShopBrand text/URL/media readiness matrix (all eight keys, missing/empty/wrong-shop/no-Woo brand, oversized values, remote-original URL refused, optional READY R2 fixture) and trusted HTTPS checkout CTA encoding/reordered language binding tests.
- [ ] Task-owned PostgreSQL integration test of variant→registration→locale/definition provenance, language fallback and real Prisma queries, using disposable database targets and declared DB001 schema.
- [ ] Source/static assertions that the new module contains no Graph template read/create or WhatsApp send calls, and that pre-existing call sites were not changed.
- [ ] Repository-declared TypeScript/lint/test/build checks appropriate to changed code; `git diff --check`.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation are met, update this task's execution evidence and Completion Report, return it to `review` through the normal task workflow, then **STOP**. No BG006–009 integration, Admin modifications, legacy category-service removal, System Test or `_index.md` updates.

## Implementation Notes

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/developer-task-workflow.md` and the logical `moda_background` instructions. The task launcher owns dedicated parent and implementation worktrees, branch synchronisation, recursive submodules and attempt claiming. Preserve the accepted ARCH-045/046 consent/STOP work. Route any missing prepared-payload contract or DB relation to `moda_architect` rather than making a cross-repository workaround. Structured logging uses `@modainteract/moda-interact-shared/logging`; observability failures never alter send eligibility.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-25T17:01:45Z. Attempt 0 review history is preserved below.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

The DB001 Attempt 7 schema and Admin-prepared compiled-payload contract must be available at execution. Recheck the actual accepted DB schema and Admin-frozen compiled data when the task worktree is prepared. No new Shared AST publication prerequisite is assumed.

### Unresolved Issues

Prerequisite DB001 developer completion remains outstanding; no new Shared publication gate is required. Existing consumer task scopes must be reconciled before integration.

### Architectural Concerns

No business lifecycle constraint should be pushed into PostgreSQL. No AI-initiated checkout mutation is authorised.

## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed; module-only implementation has not started.

### Follow-up

Reconcile the now-defined module-first Background task set and cross-repository Admin/Messaging transport handoffs before making dependencies Ready. Do not update `_index.md` until explicitly authorised by the user.

## Execution Ownership Amendment

- Date: 2026-10-25
- Change: The developer explicitly invoked `/moda_developer_create` for this Ready agent-owned task. Execution ownership is transferred to the developer, and completion is set to developer review.
- Preserved: `assigned_agent: moda_background`, coordinator, repository, dependency, task scope, acceptance criteria and validation requirements.
- Claim state: This amendment does not claim an implementation attempt; the canonical launcher records the claim after dependency and worktree preparation.
