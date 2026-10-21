---
id: ARCH-035-SYSTEM-TEST-001
architecture_id: ARCH-035
title: Certify Woo merchant Admin UI parity with Shopify
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-WOOCOMMERCE-001
  - ARCH-035-WOOCOMMERCE-002
  - ARCH-035-WOOCOMMERCE-003
  - ARCH-035-WOOCOMMERCE-004
  - ARCH-035-WOOCOMMERCE-005
  - ARCH-035-WOOCOMMERCE-006
  - ARCH-035-WOOCOMMERCE-009
  - ARCH-035-WOOCOMMERCE-012
  - ARCH-035-WOOCOMMERCE-013
enables: []
created: 2026-10-11
updated: 2026-10-21
---

# ARCH-035-SYSTEM-TEST-001: Certify Woo merchant Admin UI parity with Shopify

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: `moda-interact-workspace(20261011-192347).zip`; portable definition, not materialised.

## Objective

Certify the UI-only WooCommerce merchant Admin surfaces against the existing Shopify page structure and interaction expectations without asserting missing backend operations work.

## Context

The parent ARCH-035 architecture was narrowed by user direction to UI only. Its former checkout/order, offers, database and API implementations are superseded. The nine required Woo UI tasks listed under Dependencies are recorded Complete. WOOCOMMERCE-010 was superseded on 21 October 2026 because no authoritative Woo recovery-analytics aggregate API exists; it is not a certification prerequisite.

## Scope

- Inspect both source page hierarchies and collect reproducible automated component/DOM-layout comparison evidence for the existing account/store Overview (not Shopify recovery analytics), Recoveries list/detail, Billing, Promotions, Support, Recovery Settings with features and knowledge, and Usage History. Developer-supplied LocalWP screenshots may be reviewed separately; the system-test agent must not launch, run or manually inspect LocalWP.
- Test connected, disconnected, permission denied, loading, empty, error and external-API-unavailable states, and correct WordPress provider/navigation shell.
- Confirm all 20 merchant UI locales, appropriate WordPress administrator language with site fallback and unaffected store/conversation language.
- Verify accessible controls, focus, keyboard, responsive/mobile and double-submit prevention.
- Verify that no fixture-only data is displayed as real revenue, orders, messages, promotions, credits or backend success.

## Out of Scope

- Authentic Woo checkout event ingestion, order reconciliation, WhatsApp recovery delivery, Woo coupon fulfilment or provider revenue certification.
- New hosted API, Shared, Background or Database implementation.
- Changes to `_index.md` before explicit architect reconciliation.

## Requirements

- Work from the architecture-approved Shopify source references and the ASCII designs of each Woo UI task, not generic design assumptions.
- Record each surface as matched, partially matched, or blocked by an existing missing data/action contract; distinguish **UI parity** from **functional/backend parity**.
- Test WordPress nonce/capability denial and disconnect identity fencing for real available admin actions.
- Keep system tests black-box, with modular executors/fixtures/assertions/orchestration and evidence paths.

## Work Items

- [ ] Record source comparison for all merchant surfaces and main UI interactions.
- [ ] Exercise routes, breadcrumbs, filters, pagination, forms and unavailable states.
- [ ] Exercise 20 UI locales and WordPress admin permission handling.
- [ ] Record per-page screenshots/test evidence and explicit uncovered backend functionality.
- [ ] Verify existing Billing/onboarding and Shopify reference flows were not modified.

## Interfaces / Contracts

- UI navigation, local WordPress browser/plugin boundaries and approved existing API responses only. No new event or command contract is certified by this task.

## Dependencies

- `ARCH-035-WOOCOMMERCE-001` Complete
- `ARCH-035-WOOCOMMERCE-002` Complete
- `ARCH-035-WOOCOMMERCE-003` Complete
- `ARCH-035-WOOCOMMERCE-004` Complete
- `ARCH-035-WOOCOMMERCE-005` Complete
- `ARCH-035-WOOCOMMERCE-006` Complete
- `ARCH-035-WOOCOMMERCE-009` Complete
- `ARCH-035-WOOCOMMERCE-012` Complete
- `ARCH-035-WOOCOMMERCE-013` Complete

## Enables

None. Terminal ARCH-035 UI-validation task.

## Acceptance Criteria

- [ ] Every required implemented UI surface is structurally and interactively compared with the applicable Shopify reference; the Woo Overview is certified for its existing account/store context only, not Shopify recovery-performance/aggregate parity.
- [ ] Disabled/unavailable functionality is documented clearly and not passed as production capability.
- [ ] All 20 locales, responsive/keyboard tests and WP privilege/nonce checks have evidence.
- [ ] No backend/domain lifecycle assertion is made based on fixture UI success.
- [ ] Independent evidence is preserved for architect review.

## Validation

- [ ] Repository-supported automated system/browser/DOM tests and repeatable WordPress fixture matrix; no LocalWP execution by the system-test agent.
- [ ] 20-locale and accessibility/responsive validation.
- [ ] Reproduce negative unavailable/disconnected/denied cases.
- [ ] git diff --check and task/worktree report evidence.

## Stop Condition

Submit evidence and Completion Report with task at `review`, then STOP. Do not move to a checkout/order lifecycle test or claim backend certification.

## Implementation Notes

The test is terminal. The nine remaining listed UI prerequisites are recorded Complete; it may be invoked after the developer’s separate manual-validation checkpoint. Superseded WOOCOMMERCE-010 is intentionally excluded. The developer alone runs/checks LocalWP and may supply screenshots or a manual validation report before choosing to invoke this Ready test. The system-test agent validates automated architecture/UI evidence independently, distinguishing any supplied manual artifacts from tests it actually ran. Absence of developer LocalWP screenshots must be reported as `developer validation pending`, never silently invented as a passed system-test check.

## ASCII Page Design

```text
+----------------------------------------------------------+
| UI parity evidence                                      |
| Shopify reference | Woo admin page | Comparison          |
| Overview          | Overview       | [status/evidence]   |
| Recoveries        | List + Detail | [status/evidence]   |
| Settings          | Sections      | [status/evidence]   |
| Promotions        | Promotions    | [status/evidence]   |
| Support           | Support       | [status/evidence]   |
| Usage             | Usage History | [status/evidence]   |
| Billing           | Billing       | [regression]        |
+----------------------------------------------------------+
| Separate UI parity from backend feature availability.   |
+----------------------------------------------------------+
```

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

No task branch/claim has been materialised in this review environment.

### Unresolved Issues

Backend gaps are reported, not modified by this system test.

### Architectural Concerns

None reported.

## Architect Review

### Review Status

Pending implementation.

### Review Notes

**Dependency/frontier reconciliation — 2026-10-21:** WOOCOMMERCE-010 was superseded without code; remove its prerequisite. The other nine UI prerequisites are recorded Complete in this snapshot, so promote this terminal task `pending -> ready`, without claiming execution. Test the existing Overview account/store UI, not unsupported recovery analytics. This is UI-only certification and does not establish real Support messaging, checkout/order capture, Merchant Knowledge processing, or recovery delivery; those have separate terminal tests (SYSTEM-TEST-005, -002 and -004 respectively). No system-test implementation or acceptance is claimed.

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending.

### Follow-up

Architect validates UI comparison and records known unavailable backend functionality.
