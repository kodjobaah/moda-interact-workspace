---
id: ARCH-035-WOOCOMMERCE-001
architecture_id: ARCH-035
title: Build native Woo merchant Support screen
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 95
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-API-001
enables:
  - ARCH-035-SYSTEM-TEST-001
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-WOOCOMMERCE-001: Build native Woo merchant Support screen

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: uploaded `moda-interact-workspace(20261011-185536).zip`; task is a portable definition, not a claimed/materialised worktree.

## Objective

Replace the Support placeholder with a functional WordPress administrator support inbox consistent with the Shopify merchant experience.

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

**Files:** change `includes/Admin/NativeNavigation.php` from `register_planned('moda-interact-support',...)` to
`register_application(...)`; add `includes/Rest/SupportController.php`, PHP `ModaApiClient` methods and class-map
entry, `src/support/{client,controller,screen,message-list,message-card,composer,pagination}.js`,
`src/styles/_support.scss`; thin addition to
`src/page/{connected-workspace,controller-factory,controller-session,page-actions}.js` and
`src/native-admin/mount.js` as required, PHP+JS tests, POT/19 PO and compiled language files. Do not append a new
400-line `page.js`/`billing-screen.js`.

**Behavior:** authenticated native Support submenu loads GET
`/wp-json/moda-interact/v1/support/messages?page=1&pageSize=25`, composed with API-001. Add POST `/support/messages`
and `/support/messages/:id/read` privileged WordPress routes; all require `manage_woocommerce`, WP REST cookie/nonce,
site identity and connected installation. PHP must append bearer server-side; React never contacts hosted API
directly. Show paginated messages, unread Administrative/System badges, original/translated toggle, sending state,
accessible 0/500 Unicode-grapheme counter and composer; generate one cryptographically secure `actionId` per submit,
hold it on retry, prevent double-submit. Read acknowledgements are idempotent and only for unread authorized
messages; Woo system messages must never open Shopify merchant refund-POST actions.

**Session safety:** stale GET/POST/translated responses ignored after disconnect/credential rotation, no message/body
in browser localStorage/WordPress options. All 20 administrator languages use static gettext, PO/POT/MO/JS build;
admin UI locale doesn't change source/Shop conversation language. Tests: nonce denial, contributor denial, 501
graphemes, translated vs failed, duplicate submit, reconnect, zero/50 messages, long text mobile/focus, full ZIP.

## High-level scope (non-authoritative summary)

- Activate the existing Moda Interact Support submenu; implement history/pagination, unread indicators, translated/original message details, composer and read acknowledgements. Surface only provider-appropriate system actions; Woo refunds remain external WooCommerce.com Orders navigation.
- Use the same connected workspace, controller/session invalidation, authenticated PHP REST proxy and WordPress nonce/capability protections as Billing.
- Keep transport, state/controller, read markers, message display and composer in focused modules; prevent double-send and stale responses after disconnect.
- Translate all new UI strings in the 20 supported locales using native WordPress gettext and administrator UI language with site fallback.

## Out of Scope

- New top-level menu, direct API calls from React, merchant WhatsApp conversations.
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

- `ARCH-035-API-001` must be architect-accepted Complete before this task is claimed.

## Enables

- `ARCH-035-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] LocalWP manual navigation and send/read-state demonstration.
- [ ] PHP privilege/nonce tests; JS pagination, accessibility, stale-response and duplicate-send tests.
- [ ] POT+19 PO/compiled language assets, plugin ZIP and Shopify regression checks.
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
