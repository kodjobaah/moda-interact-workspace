---
id: ARCH-046-WOOCOMMERCE-001
architecture_id: ARCH-046
title: Render optional WhatsApp recovery opt-in in Classic and Blocks checkout
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 26
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-046-WOOCOMMERCE-002
  - ARCH-046-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-20
---

# Render optional WhatsApp recovery opt-in in Classic and Blocks checkout

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

## Objective

Introduce one explicit, unchecked-by-default and appropriately translated WhatsApp recovery opt-in field on real Woo Classic and Blocks checkouts, safely feature-gated until persistence is wired.

## Context

The shipped WP plugin has no storefront consent hook. Woo Additional Checkout Fields support checkboxes on Blocks; Classic needs its supported checkout integration. A field alone is not proof that an abandoned guest opted in.

## Scope

- Add a small modular PHP and front-end registration for an optional unchecked checkbox, separate from terms, cookies, email marketing and purchasing.
- Support both Classic shortcode checkout and Checkout Blocks using Woo 11+ extension points; ensure field remains optional and no automatic/prechecked positive state even for returning customers.
- Provide a disclosure tied to store identity, WhatsApp purpose and expected recovery reminder messages; use WordPress-native gettext and existing 20 locale compilation pipeline.
- Hide/disable or explain the option until a safe pre-submit persistence pathway is deployed; do not present a functioning guarantee of consent storage while backend absent.

## Out of Scope

- No hosted API grant before API-001 or browser→Moda direct request.
- No actual checkout recovery, marketing pixel, cookie CMP or speculative pop-up/banner.
- No rewrite of navigation, PHP bootstrap or large monolithic React page.

## Requirements

- `required:false`, unchecked by default; form submission succeeds without opt-in.
- Distinguish visible positive choice from a persisted permission; no fake grant or indication of completed storage.
- WordPress/Woo compatibility with Woo Checkout Blocks, Classic guest and logged-in experience; accessible label and 20 supported translations.

## Work Items

- [ ] Implement small per-checkout field/render adapters and feature gate.
- [ ] Add PHP/frontend tests for unchecked default and optionality in both modes.
- [ ] Update POT/PO/MO + JS locale assets per existing repository tooling, ZIP packaging.

## Interfaces / Contracts

Introduces versioned disclosure/checkbox semantic identifiers to be consumed by WOOCOMMERCE-002; does NOT introduce API payload or an asserted hosted grant.

## Dependencies

None

## Enables

- `ARCH-046-WOOCOMMERCE-002`
- `ARCH-046-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Real Classic and Blocks pages display correctly with opt-in initially unchecked and optional.
- [ ] Guest and logged-in purchase is not blocked by declining the checkbox.
- [ ] No call creates a consent grant before the explicit persistence integration is available.
- [ ] All 20 merchant locales compile; public-facing strings have proper gettext domain.

## Validation

- [ ] Plugin PHP/JS focused tests, PHP lint, production ZIP build and LocalWP Classic/Blocks smoke test.
- [ ] WordPress 20-locale asset verification and `git diff --check`.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

The field is not a licence to send any WhatsApp message; actual grant requires subsequent hosted DB acknowledgement and exact phone binding.

Before any implementation, use `/moda-task` deterministic preparation against the **developer's actual** primary workspace, read the latest task/Architect Review, the parent architecture, relevant agent instructions, and the repository's real `package.json` scripts. Do not invent environment variables or claim a completed checkout/recovery source from the snapshot. Do not modify another repository, architecture-wide docs or `docs/decisions/**/_index.md` in a repository task. Use `@modainteract/moda-interact-shared/logging` for Node server diagnostics; PHP uses WordPress-specific safe diagnostics. Preserve official user/merchant i18n and tenant boundaries.

## Completion Report

### Status

Not Started — portable, not materialised.

### Files Changed

None — no runtime implementation in this documentation patch.

### Work Completed

None.

### Validation Results

Not run by a repository agent; no developer worktree/remote access is available from this snapshot.

### Deviations

None.

### Assumptions

Source is the supplied 2026-10-20 snapshot, not necessarily latest developer worktree. Versioned APIs/schema and future Woo recovery capability must be verified when eligible. Fixed provisional 72-hour consent wait from `detectedAt`, always shortened by actual earlier Woo checkout expiration/paid-order state.

### Unresolved Issues

None recorded at definition time; raise actual missing cross-repository contract/rollout dependencies to moda_architect before scope drift.

### Architectural Concerns

None recorded beyond explicit context and gates.

## Architect Review

### Review Status

Pending — no implementation reviewed or accepted.

### Review Notes

None.

### Reviewed Files

None — portable definition only.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
