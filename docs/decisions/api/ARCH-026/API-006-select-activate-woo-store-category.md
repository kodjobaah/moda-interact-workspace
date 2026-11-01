---
id: ARCH-026-API-006
architecture_id: ARCH-026
title: Select and activate Woo Store Category against existing Free subscription
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 36
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-026-API-005
enables:
  - ARCH-026-WOOCOMMERCE-008
created: 2026-10-09
updated: 2026-10-16
---

# Select and activate Woo Store Category against existing Free subscription

## Architecture

Architecture ID: `ARCH-026`.

Architecture document: `docs/architecture/ARCH-026-woocommerce-application-foundation.md`.

Coordinator: `moda_architect`.

## Objective

Allow a connected WooCommerce merchant to select or change its canonical Store Category and optional taxonomy mappings, publishing the matching CommerceAgent prompt immediately when its automatically assigned Free subscription is active.

## Context

Shopify currently stages its first category before plan activation, then publishes the pending prompt upon eligible subscription activation; later settings changes publish replacements. WooCommerce Connect has already activated Free. A Woo merchant must not be asked to choose a plan and must not be left indefinitely pending after a successful initial category selection. Reuse canonical Commerce profile/prompt state and match Shopify's generation/templating rules.

## Scope

`moda-interact-api` only:

- Define strict versioned, bounded `POST /v1/merchant/store-category` OpenAPI request/response contract, authenticated via existing active Woo installation principal.
- Validate enabled category/default template, selected mapping IDs and prompt template conditions using the published Shared Commerce template rendering/provenance helpers.
- Implement generation-checked category selection and prompt publication under the Shop-scoped transaction/locking and runtime Commerce environment policy; initial activation requires an existing ACTIVE/TRIALING subscription with non-null plan.
- For an already active profile, preserve Shopify-equivalent atomic category change, prompt revision/provenance, selected mappings and current configuration switching.
- Return the new authoritative profile/generation or a bounded error, and add focused tests including PostgreSQL concurrency, rollback, template drift, revocation and billing invariants.

## Out of Scope

- Installation handshake, Free-plan activation, credential rotation, billing/entitlement grants or plan chooser.
- Creating a separate Woo category catalogue, Woo product-category inference, WordPress route or UI.
- Changing Shopify selection routes, Background, schema, Gateway or merchant bootstrap v1 response.

## Requirements

- Resolve Shop solely from installation authentication, recheck principal/Shop continuity before mutation and never allow caller-selected `shopId`/Commerce environment.
- Accept only `schemaVersion: 1`, `categoryId`, bounded unique `selectedMappingIds`, and nonnegative safe-integer `expectedPendingSelectionGeneration`; reject unknown fields and mapping IDs not belonging to the selected category.
- Follow Shopify `store-category-selection.server.ts` preparation/recheck strategy: enabled/default template and mapping version validation, deterministic shared prompt rendering, preserved source provenance, published revision, and CAS generation protection. No duplicate prompt lineage/configuration.
- For a Shop with no active category and an eligible active Free subscription, a **successful POST returns with activeCategory set and prompt published/configuration active**; there must be no stranded pending initial selection awaiting another plan event.
- When an active category already exists, changing category or mappings publishes a new revision and updates the active configuration atomically, maintaining monotonic edit/generation semantics. On failure, preserve the previous active profile and prompt.
- Invalid/disabled template or mapping => bounded unavailable error; stale generation, concurrent selection or catalog edits => conflict; missing/ineligible subscription => no category publication and an explicit bounded failure, not hidden billing writes.
- Failed/retried requests cannot alter Shop connection, installation credential/version, subscription, Free credit counter, reserved or committed usage. Only explicit POST mutates category state; no GET or Connect side effects.
- Reuse `@modainteract/moda-interact-shared/logging`; log redacted semantic result and correlation identifiers, not prompt text or credentials. Do not re-create standard HTTP metrics.

## Work Items

- [ ] Define strict OpenAPI mutation schema and classification of errors.
- [ ] Implement authenticated, shop-scoped prevalidation + atomic selection/prompt publication, with correct environment selection.
- [ ] Cover initial Free activation, later category replacement, selected mappings and published prompt/provenance.
- [ ] Add concurrent/CAS, disabled/template-drift, revoked principal, rollback and unchanged Free-credit tests.

## Interfaces / Contracts

- Source category/profile read contract: `ARCH-026-API-005`.
- Mutation endpoint: `POST /v1/merchant/store-category`, versioned OpenAPI owned by `moda_api` and consumed by `ARCH-026-WOOCOMMERCE-008`.
- Authentication: existing `WooInstallationAuthenticator` from `ARCH-026-API-002`.
- Durable models: existing `CommerceShopProfile`, `CommerceAgentPrompt`, `CommerceAgentPromptRevision`, `CommerceAgentConfiguration`, Category/template/mapping records and `Subscription` (eligibility read only).
- Shared package: `@modainteract/moda-interact-shared/commerce` for canonical prompt context rendering/provenance compatibility. Shopify store-category selection/activation implementations are behavioural parity references, not permitted imports across repository boundaries.

## Dependencies

- `ARCH-026-API-005` — must be Complete to establish the read contract and canonical profile model.

## Enables

- `ARCH-026-WOOCOMMERCE-008`.

## Acceptance Criteria

- [ ] Choosing category on an existing connected Free Woo Shop (subscription ACTIVE) returns active category and published matching CommerceAgent prompt in the correct environment, no pending initial state.
- [ ] Selected eligible mapping IDs appear in persisted prompt source/provenance and are reflected by the next profile GET.
- [ ] An existing active category/mappings can change with correct new published prompt and preserved old state on any failed update.
- [ ] Two concurrent attempts with the same generation cannot both win; stale generation returns conflict without lost updates.
- [ ] Disabled/missing category/default template, invalid mappings and changed edit versions do not partially update prompt/profile state.
- [ ] Unauthorized/revoked/cross-tenant installation cannot mutate a Shop or another Shop's prompt.
- [ ] Free subscription, five lifetime credits, consumed/reserved amounts, credential identity/version and `Shop.onboardingCompleted` remain unchanged.
- [ ] Focused parity tests prove Shopify-equivalent selection, generation, mapping and prompt lifecycle semantics; no separate Woo taxonomy or prompt storage appears.

## Validation

- [ ] Focused unit/route/OpenAPI tests and repository-declared typecheck/lint/build.
- [ ] Disposable PostgreSQL transaction/parallel mutation tests and after-failure rollback checks.
- [ ] Compare critical outcome fixtures to the existing Shopify category selection and activation tests.
- [ ] `git diff --check` and task launcher worktree/synchronization evidence in Completion Report.

## Stop Condition

After required work and validation, set task to review, return Completion Report to `moda_architect`, STOP; do not implement Woo UI.

## Implementation Notes

Initial Woo category activation must be an atomic server-side business outcome, not a client-side `select` then `activate` sequence that can leave a merchant stranded if a second request fails. It must not grant Free credits anew. Minimize long-lived transactions: render and prepare before Shop lock; CAS-recheck all referenced versions before commit. Preserve already-active replacement semantics and compatibility with existing Shopify prompt conventions.

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

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted — retrospective implementation-evidence reconciliation, 2026-10-16.

### Review Notes

The versioned category-selection POST boundary, installation authentication, bounded input parsing, Commerce prompt/selection transaction and conflict handling are implemented and registered.

This is an explicit architecture-level retrospective closure based on the 2026-10-16 supplied code snapshot, **not** a reconstruction of an original task execution or CI run. The attached archive has no Git worktrees/commits or historical launcher packet, so mirrored-branch isolation, claim provenance, original attempts, historical test results and actual WordPress/HTTPS/provider execution cannot be independently certified here. Original `attempt: 0` and executor-owned Completion Report are preserved without manufacturing evidence. These provenance limitations do not establish process compliance. Terminal integrated Woo provider certification remains `ARCH-026-SYSTEM-TEST-001`.

### Reviewed Files

- `moda-interact-api/src/merchant/store-categories/selection-routes.ts`
- `moda-interact-api/src/merchant/store-categories/selection-schema.ts`
- `moda-interact-api/src/merchant/store-categories/store-category-selection.service.ts`
- `moda-interact-api/src/merchant/store-categories/selection-preparation.ts`
- `moda-interact-api/src/merchant/store-categories/selection-publication.ts`
- `moda-interact-api/src/index.ts`

### Validation Reviewed

- `moda-interact-api/src/merchant/store-categories/selection-routes.test.ts` (test present and inspected; not independently executed in this read-only archive)
- `moda-interact-api/src/merchant/store-categories/selection-schema.test.ts` (test present and inspected; not independently executed in this read-only archive)
- `moda-interact-api/src/merchant/store-categories/store-category-selection.service.postgres.test.ts` (test present and inspected; not independently executed in this read-only archive)
- `moda-interact-api/src/merchant/store-categories/selection-openapi-contract.test.ts` (test present and inspected; not independently executed in this read-only archive)
- Static cross-file wiring and source inspection: completed for this task's bounded implementation.
- No new API TypeScript, PHP unit, WordPress integration, PostgreSQL or live provider tests were executed as part of this reconciliation unless explicitly listed as PASS above.

### Architecture Conformance

Accepted for bounded code-level implementation reconciliation. Live/integrated runtime acceptance is reserved for terminal system-test evidence. No source-code change is authorised by this review.

### Follow-up

`ARCH-026-SYSTEM-TEST-001` — certify the integrated HTTPS callback, real Woo consent/read and credential/tenant/billing isolation. Recover missing Git/provenance records separately if full historical workflow certification is required; do not invent them.
