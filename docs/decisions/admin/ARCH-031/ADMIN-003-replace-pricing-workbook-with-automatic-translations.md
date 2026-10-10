---
id: ARCH-031-ADMIN-003
architecture_id: ARCH-031
title: Replace Merchant Pricing workbook with automatic translations
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-031-ADMIN-001
  - ARCH-031-ADMIN-002
  - ARCH-031-BACKGROUND-001
enables:
  - ARCH-031-SYSTEM-TEST-001
created: 2026-10-10
updated: 2026-10-10
---

# Replace Merchant Pricing workbook with automatic translations

## Architecture

Architecture ID: `ARCH-031`.

Architecture document: `docs/architecture/ARCH-031-automatic-merchant-pricing-translations.md`.

Coordinator: `moda_architect`.

## Objective

Replace the normal Merchant Pricing XLSX translation workflow with automatic durable translation progress/retry UX and atomically consume a validated ready translation run when the administrator creates or saves the pricing plan.

## Context

ARCH-031-ADMIN-002 creates/reuses durable translation work and can reconstruct a strict canonical Merchant Pricing translation package from a ready run. ARCH-031-BACKGROUND-001 executes that work. This task is the final Admin integration point: it removes translation labor from the plan author while retaining the existing seven-step builder and the explicit final Create/Save action.

The current `MerchantPricingTranslationWorkbook` / `translationJson` workflow must remain intact until this task because it is the only complete authoring path in intermediate states. This task replaces that normal builder path only after all required runtime dependencies are accepted.

## Scope

Within `moda-interact-admin` only:

- Step 7 automatic translation status/retry/review UI;
- builder/controller state for `translationRunId` and bounded polling;
- automatic request/reuse when Step 7 is entered and translation is required;
- stale-run invalidation in client state when translatable English source changes;
- final `mutateMerchantPricingPlanAction` integration that consumes a ready run server-side;
- atomic run recheck/application in the final Merchant Pricing serializable transaction;
- removal of workbook download/upload/import from the normal Merchant Pricing builder;
- tests covering create/edit/reorder/failure/double-submit semantics;
- retention of any workbook helpers only where still used by tests/maintenance or other non-builder flows.

Keep API calls/state/controller logic separated from presentational components. Do not turn `merchant-pricing-plan-builder.tsx` into a large orchestration component.

## Out of Scope

- changing the 20 supported languages;
- changing Store Category automatic translation;
- changing Promotion XLSX translation;
- database schema/migrations;
- Background provider execution;
- adding browser/provider credential/model selection;
- a new public API/Gateway route;
- deleting generic workbook/parser helpers that remain used elsewhere without a separate demonstrated cleanup need;
- changing Merchant Pricing economics/feature/Shopify-plan-handle rules;
- any `_index.md` update.

## Requirements

### R1 — seven-step workflow remains

Preserve the existing seven-step Merchant Pricing builder and final explicit administrator confirmation.

Step 7 remains `Translations & review`, but normal copy/controls become automatic, for example:

```text
Translations
Moda Interact translates the English merchant content automatically.

Model: <configured automatic-default model>
Status: Translating / 20 of 20 ready / Failed

[Retry translations]  # terminal failure only
```

Do not expose provider credential ids, provider file ids or model selection to the plan author.

### R2 — automatic request/reuse

When Step 7 is entered:

```text
edit + translatable English source unchanged
    -> retain persisted 20/20 translations; no run

otherwise
    -> request/reuse durable translation work through ADMIN-002
```

The request is server-authoritative. The browser does not construct durable run/items or choose the translation model.

A repeated render/navigation to Step 7 for unchanged current source must reuse the current/eligible run rather than create duplicate provider work.

### R3 — bounded polling lifecycle

Poll only the current run through the bounded ADMIN-002 status endpoint/action while status is nonterminal.

Polling must stop when:

- `READY_TO_APPLY`;
- `FAILED`;
- the component unmounts/drawer closes;
- the current English source identity changes;
- the builder changes to a different plan/handle.

Do not refresh/reload the entire Billing page merely to observe translation progress.

Use a bounded interval/backoff appropriate to the existing Batch runtime; do not busy-loop.

### R4 — stale-source client handling

Changing any translatable source after a run is associated invalidates that run association in client state:

- plan English description;
- highlight English title;
- highlight English description;
- adding/removing a highlight.

Highlight reorder alone MUST NOT invalidate translation because source identity is contentKey-canonicalized by ADMIN-002.

Changing non-translatable pricing, economics, model, features or usage-event fields does not invalidate a ready run.

Client invalidation is UX only. Server-side source-hash/handle validation remains the correctness boundary.

### R5 — retry UX

For a terminal failed run:

- show bounded failure copy suitable for an administrator;
- offer `Retry translations`;
- retry creates/reuses a valid new run using the current automatic default through ADMIN-002;
- no raw provider response/error or source text is exposed.

Missing automatic-default model/provider credential must render a clear configuration action message pointing to System Controls / Translations; it must not silently fall back to English/manual XLSX.

### R6 — ready review

A ready run displays at least:

```text
20 / 20 languages ready
translation model display name
```

An edit whose source is unchanged displays retained translation completeness without starting provider work.

The administrator may inspect the final plan review, but normal creation does not require downloading/uploading a workbook or manually filling translations.

### R7 — final server mutation consumes durable work

For changed/new translatable content, submit only a `translationRunId` as translation-work identity. Do not trust browser-supplied translated JSON/XLSX content.

Before writing final plan state, `mutateMerchantPricingPlanAction` (or a focused service it delegates to) must:

1. rebuild the authoritative canonical source from the submitted current plan data;
2. load the run and require `READY_TO_APPLY`;
3. require exact `shopifyPlanHandle` and source-hash match;
4. reconstruct/validate the canonical schema-v2 translation package through ADMIN-002;
5. enter the existing serializable final plan transaction;
6. lock/re-read or otherwise concurrency-protect the translation run;
7. re-require `READY_TO_APPLY`, exact handle and exact source identity;
8. write/update the Merchant Pricing plan, exact 20 plan translations, exact highlight translations and normal related state;
9. mark the consumed run `APPLIED`, set application timestamps/provenance, and associate the resulting plan id if DATABASE-001 permits;
10. commit the plan write and run application atomically.

If any recheck fails, neither the plan write nor `APPLIED` transition commits.

No external provider/Redis operation occurs in this transaction.

### R8 — unchanged-edit retention

Preserve current ARCH-014 edit semantics:

- if all translatable English source is unchanged, retain existing persisted translations without a new translation run;
- reorder-only highlight edits retain translations;
- changed/new fields require a ready run;
- removal of a highlight removes its final translation rows through the normal final mutation.

Do not force translation merely because non-translatable plan fields changed.

### R9 — double-click / concurrency safety

Preserve the existing critical-submit double-click protection in the UI and add server correctness independently of it.

A ready translation run may be consumed at most once. Two concurrent final submissions must not both apply the same run or create conflicting duplicate plans. One wins under existing serializable/uniqueness rules; the other returns a bounded stale/already-applied/concurrency response.

### R10 — workbook retirement boundary

Remove these controls from the normal Step 7 Merchant Pricing experience:

```text
Download pre-populated translation spreadsheet
Drop your completed .xlsx spreadsheet here
Choose spreadsheet
```

Remove `translationJson` from normal changed-content submission/state once the automatic path is authoritative.

Do not delete the strict canonical schema-v2 parser: automatic results are reconstructed into that same package and validated server-side as defence in depth.

Any workbook endpoint/component/helper that becomes dead after this task may be removed **only if** repository reference inspection proves it is Merchant-Pricing-only and tests are updated in the same task. Promotion workbook behavior is untouched.

### R11 — observability

Use Shared logging for any new/changed semantic application events, including bounded outcomes such as:

```text
admin.merchant_pricing.translation_applied
admin.merchant_pricing.translation_apply_failed
```

Do not log translation text, workbook content or provider secrets.

## Work Items

- [ ] Consume accepted ADMIN-001, ADMIN-002 and BACKGROUND-001 implementations/gitlinks.
- [ ] Replace Step 7 workbook UI with automatic translation status/review components.
- [ ] Add focused controller/hook state for request/reuse, polling, invalidation and retry.
- [ ] Preserve no-run retained-translation path for unchanged edits.
- [ ] Replace normal `translationJson` changed-content submission with `translationRunId`.
- [ ] Integrate ready-package reconstruction into the final server mutation.
- [ ] Make translation-run `APPLIED` transition atomic with final plan persistence.
- [ ] Add server and client double-submit/stale-run protections.
- [ ] Remove now-dead Merchant-Pricing-only workbook UI/actions/helpers only after reference proof.
- [ ] Add bounded shared structured logging.
- [ ] Add focused unit/security/integration tests for create, edit retention, reorder, source invalidation, retry, stale source, already-applied run and concurrent submit.
- [ ] Run full focused Admin validation and record results.

## Interfaces / Contracts

Consumes:

- `ARCH-031-ADMIN-001` automatic-default System Controls behavior;
- `ARCH-031-ADMIN-002` request/status/source/package service boundary;
- durable completed work produced by `ARCH-031-BACKGROUND-001` through DATABASE-001 state;
- existing Merchant Pricing canonical translation parser/schema-v2 package.

Produces the completed Admin Merchant Pricing authoring path consumed by terminal system validation in `ARCH-031-SYSTEM-TEST-001`.

No new browser-to-provider or cross-repository queue contract is introduced.

## Dependencies

- `ARCH-031-ADMIN-001`.
- `ARCH-031-ADMIN-002`.
- `ARCH-031-BACKGROUND-001`.

## Enables

- `ARCH-031-SYSTEM-TEST-001`.

## Acceptance Criteria

- [ ] A new plan can be authored with English merchant content only; no XLSX download/upload is required.
- [ ] Step 7 automatically requests/reuses translation and displays durable progress.
- [ ] The plan author cannot select provider/model credentials per plan.
- [ ] Entering Step 7 repeatedly with unchanged source does not duplicate active provider work.
- [ ] Polling terminates correctly and does not refresh the whole Billing page.
- [ ] Changing translatable source invalidates the current run association; highlight reorder alone does not.
- [ ] Failed translation exposes bounded retry/configuration UX and never falls back to English/manual workbook.
- [ ] `Create plan` / `Save plan` remains unavailable for changed/new content until a matching run is `READY_TO_APPLY`.
- [ ] Final mutation rejects a ready run from another handle or stale source.
- [ ] Final mutation reconstructs and strictly validates the exact 20-locale translation package server-side.
- [ ] Run application and final plan persistence are atomic; an `APPLIED` run cannot be consumed twice.
- [ ] Existing edit-with-unchanged-source and reorder-only translation retention still works.
- [ ] Normal Merchant Pricing UI no longer contains XLSX translation download/upload controls.
- [ ] Existing Merchant Pricing plan completeness/database integrity remains intact.
- [ ] Promotion translation workflow is unchanged.

## Validation

- [ ] focused builder draft/controller unit tests for automatic request/poll/invalidation/retry behavior.
- [ ] focused component/source tests proving workbook controls are absent from normal Merchant Pricing Step 7.
- [ ] security/action tests for SUPER_ADMIN request/final mutation and untrusted run ids.
- [ ] focused database-backed integration test for atomic run consumption + plan write, including concurrent/double-submit behavior where repository fixtures support it.
- [ ] regression tests for unchanged-edit/reorder translation retention and existing Merchant Pricing builder economics/feature flow.
- [ ] `npm run test` or focused repository-declared security suite for affected paths.
- [ ] `npm run test:unit` or focused unit subset for affected paths.
- [ ] `npm run lint`.
- [ ] `npm run build`.
- [ ] `git diff --check`.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, set status to `review`, return the Completion Report to `moda_architect` and STOP. Do not execute the system-test task. The developer may manually validate the completed implementation before invoking system testing.

## Implementation Notes

Keep the builder modular. Translation request/poll lifecycle belongs in a focused controller/hook; database/provider details stay in server services/actions; presentational Step 7 components receive bounded state/handlers.

The strict Merchant Pricing parser is intentionally retained as a final validator even though the browser no longer supplies an XLSX-generated package.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

None.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending implementation review.

### Follow-up

None.
