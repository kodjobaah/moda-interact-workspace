---
id: ARCH-035-WOOCOMMERCE-009
architecture_id: ARCH-035
title: Build native Woo Recoveries list and detail
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 52
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-API-009
enables:
  - ARCH-035-SYSTEM-TEST-002
  - ARCH-035-WOOCOMMERCE-010
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-WOOCOMMERCE-009: Build native Woo Recoveries list and detail

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: uploaded `moda-interact-workspace(20261011-185536).zip`; task is a portable definition, not a claimed/materialised worktree.

## Objective

Replace the Woo Recoveries placeholder with Shopify-aligned filtering, list, detail, message history and related recoveries.

## Context

The previous Shopify/Woo merchant-screen parity assessment showed this specific gap. Reuse the already accepted
ARCH-026 WordPress connection, locale and Shop security foundations and ARCH-027 billing components; do not duplicate
provider-neutral Moda domain state. The current capability is not established by this task definition.

## Deterministic implementation specification — mandatory

**Architect contract.** The exact model/column names, paths, API shapes, authentication boundary, state machine and
negative cases below are the implementation target. This section supersedes less-specific high-level text elsewhere
in this task. Agents may split production code into smaller modules, but must not change a public contract, migration
field, ownership rule, or dependency without returning to the architect. If a named existing dependency is absent or
incompatible, **STOP** and report the precise finding; do not silently invent a substitute.

**Files:** change `register_planned('moda-interact-recoveries',...)` to `register_application` in
`includes/Admin/NativeNavigation.php`; `includes/Rest/RecoveriesController.php`, `ModaApiClient` read
methods/class-map;
`src/recoveries/{client,controller,list-screen,filters,recovery-row,detail-screen,timeline,conversation,related}.js`,
`_recoveries.scss` and tests. Native route remains WordPress `admin.php?page=moda-interact-recoveries`; detail is an
internal view selected by opaque recovery ID, not a new top-level WordPress page/router.

**UI:** authenticated GET-only WordPress REST proxy to API-009 list/detail. List status/date filters, 10/20/50
pagination, detectedAt, status, credited outcome and proven order flag; detail timeline, outreach statuses, language,
bounded transcript and related recoveries. Respect message redaction; don't show raw phone/email, checkoutToken,
provider message IDs or Shopify GID. Show exact detected/expired/completed source states, not fabricated recovery
success. Loading, 403/404, null conversation, page-not-found and stale-response views are explicit. Back-to-list
preserves safe filters and page only within live controller memory.

**Safety/tests:** authenticated Shop scoping enforced again in PHP, nonce/capability, no direct hosted API in
browser, abort/discard stale details on session/Shop switch, responsive long localised content, keyboard transcript
navigation, all 20 translation packs, Classic/Blocks test fixture data on API side and production plugin ZIP smoke.

## High-level scope (non-authoritative summary)

- Reuse existing NativeNavigation submenu; create modular list filters, result table/cards, detail header, timeline/transcript and related recovery components.
- Use authenticated GET-only PHP proxy plus controller/session revision with robust empty/error/permissions and stale response handling.
- Use WordPress administrator locale and all 20 languages; format dates and money without assuming Shopify currency or identifiers.
- Respect accessibility, responsive narrow screens and safe redaction of personal message/provider data.

## Out of Scope

- Unrelated Shopify or Woo Billing feature changes; changing another repository in this task.
- Other services' implementation code, `docs/decisions/**/_index.md`, and architecture index reconciliation.

## Implementation work items — mandatory

- [ ] Implement **exactly** the named files, routes/models and public DTO fields in the Deterministic implementation specification; do not widen cross-repository ownership.
- [ ] Enforce every declared shop/platform binding, validation boundary, state transition, CAS/idempotency invariant, denial path and privacy restriction.
- [ ] Implement the **specific negative and concurrency test matrix** named in the specification; record actual commands and real results.
- [ ] Prove that affected Shopify behaviour and current ARCH-026/027 Woo onboarding/billing contracts are preserved.
- [ ] Provide a bounded diff, changed-file list, applied migration/Shared package version where applicable, task Completion Report, and clean synchronised implementation/task worktree evidence.

## Cross-repository boundary (common requirements)

- Owning repository: `moda-interact-woocommerce`; consume only versioned, accepted cross-repository contracts.
- Hosted Woo identity is the authenticated Shop/installation; no client-controlled `shopId` or Shopify-session authentication. Where browser UI is in scope, transport runs through privileged WordPress REST/PHP with nonce and `manage_woocommerce` capability.
- For merchant display, all 20 supported WordPress UI locales use administrator language with site fallback; this must not change Shop or customer conversation language.
- New or changed externally visible API fields require strict bounded runtime schema validation and a matching OpenAPI/Shared contract owned by the producer.
- No additional external interface is authorised beyond the bounded scope above.

## Dependencies

- `ARCH-035-API-009` must be architect-accepted Complete before this task is claimed.

## Enables

- `ARCH-035-SYSTEM-TEST-002`
- `ARCH-035-WOOCOMMERCE-010`

## Acceptance Criteria

- [ ] LocalWP review against Shopify list/detail screenshots.
- [ ] Filter/detail/paging/foreign record and cross-navigation tests.
- [ ] Complete 20-locale compiled assets, strict ZIP and PHP/JS checks.
- [ ] Scope stays within `moda-interact-woocommerce` and preserves approved cross-provider and 20-locale contracts.
- [ ] Baseline, task launcher isolation, implementation commit, parent task report and regression evidence are recorded without false claims for unavailable provider services.
- [ ] `git diff --check` and repository-required build/test/lint commands pass or precise blockers are reported.

## Validation

- [ ] Run repository-declared focused test suites plus full typecheck/lint/build where applicable.
- [ ] Run real integration/black-box provider or disposable database evidence when this task's scope includes that dependency; do not substitute a mocked success.
- [ ] Check tenant isolation, disconnected/revoked credential handling, idempotency and requested negative cases.
- [ ] For Woo UI tasks, run `npm run test:i18n`, `npm run i18n:verify:20`, PHP/JS tests, admin-locale test, `npm run plugin-zip` and manual LocalWP workflow.
- [ ] Verify `git diff --check` and submit the canonical Completion Report; leave all `_index.md` files untouched until explicit reconciliation.

## Stop Condition

When requirements/acceptance and required validation are fulfilled, set the task to `review`, populate the Completion
Report and return to `moda_architect`. Do not begin dependent tasks or change other repositories on this task branch.

## Implementation Notes

Keep production responsibilities in small testable modules; prefer provider-neutral existing ownership to Shopify/Woo
service duplication. Return unexpected cross-repository schema or provider-contract gaps to the architect before
widening scope.

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

Dependencies will be rechecked at task claim time; no generated task document itself creates a branch, provider credential, tested artifact or release.

### Unresolved Issues

None identified beyond documented dependencies/provider gating.

### Architectural Concerns

None reported at definition time.

## Architect Review

### Review Status

Pending implementation.

### Review Notes

No implementation reviewed.

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending.

### Follow-up

Return to architect on implementation submission.
