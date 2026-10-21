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

Conditionally display one optional native Woo WhatsApp checkout-recovery consent field on Classic and Blocks when the merchant has selected the Moda collector.

## Context

The merchant may use another plugin's legitimate WhatsApp consent collector; Moda must not silently render a duplicate. The choice is hosted on WooCommerceInstallation via API-003; the plugin should default to no Moda field until `MODA_CHECKBOX` is acknowledged.

## Scope

- Register supported Classic and Checkout Blocks checkbox integrations only for the active acknowledged `MODA_CHECKBOX` source; initial unchecked/default does not infer consent. Hide when NOT_CONFIGURED or SUPPORTED_EXTERNAL. Avoid scraping another plugin's DOM, unapproved generic adapters or theme modification.
- Display purpose-specific, clearly worded 20-locale disclosure describing **WhatsApp reminders for checkouts the customer leaves unfinished at this store and exact phone**. Offer withdrawal / explicit current-preference display when previously authenticated customer already has recorded permission; never create a new affirmative grant from UI hydration.
- Keep field optional, accessible and compatible with guests, logged-in customers, HPOS and both checkout types. Placement near billing phone preferred when supported; verify reliable checkout hooks rather than fragile JS insertion. No consent write claimed in this UI-only task.

## Out of Scope

- No standalone plugin detector, API consent write, Woo recovery engine or cookie CMP. No third-party adapter automatically registered.

## Requirements

- [ ] One Moda checkbox at most on standard supported checkout, and none when inactive source.
- [ ] Wording is broad enough only for the **agreed store-specific unfinished-checkout reminder purpose**; no prechecked new grant.

## Work Items

- [ ] Register conditional Classic and Blocks integrations without modifying merchant theme.
- [ ] Test optional/unselected state, mode switches, existing customer preference, 20 locales and checkout rendering.

## Interfaces / Contracts

Reads source setting via owning Woo integration (WOOCOMMERCE-005/API-003 where present); produces browser UI decision only, no hosted consent. Later capture owned by WOOCOMMERCE-002.

## Dependencies

None

## Enables

- `ARCH-046-WOOCOMMERCE-002`
- `ARCH-046-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Both checkout types show consent correctly for MODA source; checkout remains possible without opt-in.
- [ ] No duplicate Moda checkbox in external/off mode; no grant without deliberate customer action.

## Validation

- [ ] Focused WP JS/PHP tests and LocalWP Classic/Blocks/HPOS smoke; declared lint/build and `git diff --check`.

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

Source is the supplied 2026-10-20 snapshot, not necessarily latest developer worktree. Versioned APIs/schema and future Woo recovery capability must be verified when eligible. Consent has no Moda-imposed waiting/expiry period. Recheck the current customer-phone permission and independently applicable checkout validity; do not invent a retention deadline.

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
