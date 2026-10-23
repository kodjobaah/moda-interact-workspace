---
id: ARCH-046-WOOCOMMERCE-001
architecture_id: ARCH-046
title: Register Moda Woo consent checkbox and Recovery Settings guidance
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
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
updated: 2026-10-22
---

# Register Moda Woo consent checkbox and Recovery Settings guidance

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

## Objective

Register and conditionally display Moda’s own optional WhatsApp checkout-recovery checkbox in Classic and Blocks, and explain the opt-in to merchants in the existing Recovery Settings. No consent-source selector or third-party adapter.

## Context

Moda alone owns its checkout checkbox; any other plugin's checkout UI is outside Moda's scope. `ARCH-046-API-003` and `ARCH-046-WOOCOMMERCE-005` are Superseded. The checkbox is a runtime registration when the Moda plugin is connected/authorised and the existing recovery feature is enabled; no merchant consent-source configuration exists.

## Scope

- Register supported Classic and Checkout Blocks checkbox integrations on eligible requests for an active connected installation with the existing Checkout Recovery feature enabled. Initial checkbox state is unchecked and optional. When the feature is disabled, installation disconnected/revoked or plugin deactivated, omit the field on subsequent page loads. Do not modify themes or interact with third-party plugins.
- Display purpose-specific, clearly worded 20-locale disclosure describing **WhatsApp reminders for checkouts the customer leaves unfinished at this store and exact phone**. Offer withdrawal / explicit current-preference display when previously authenticated customer already has recorded permission; never create a new affirmative grant from UI hydration.
- Keep the field optional, accessible and compatible with guests, logged-in customers, HPOS and both checkout types. Placement near billing phone preferred when officially supported; avoid fragile JS insertion. Registration must be idempotent across plugin upgrades/reactivation. An already-open checkout may display stale UI but cannot grant consent without server-side revalidation of current installation, recovery-feature eligibility and customer/phone identity.
- In the existing merchant Recovery Settings, explain exactly what the optional WhatsApp reminder covers, how current grants/withdrawals affect recovery, and that no consent means no recovery. Retain existing 20-locale localisation. Do **not** add a consent-source dropdown or controls for other plugins. The actual hosted consent write belongs to WOOCOMMERCE-002/API-001.

## Out of Scope

- No standalone plugin detector, API consent write, Woo recovery engine or cookie CMP. No third-party adapter automatically registered.

## Requirements

- [ ] The optional Moda checkbox must expressly describe **WhatsApp abandoned-basket/checkout-recovery marketing reminders**, identify the merchant, and remain unchecked. It must not be described merely as transactional order updates or consent to provide a phone number; preserve the displayed wording/version/locale for the existing evidence contract.

- [ ] One Moda checkbox at most on eligible Classic/Blocks checkout; none when the connection or recovery feature is inactive.
- [ ] Wording is broad enough only for the **agreed store-specific unfinished-checkout reminder purpose**; no prechecked new grant.

- The checkbox is entirely Moda-owned. Do not detect, hide, disable or warn about other plugins’ consent checkboxes; there is no supported-external mode in v1. Consent eligibility requires an independently verified customer grant through API-001.
- Use official Classic/Blocks extension locations, with accessible text and 20 locale handling, but do not assume Woo Blocks order-only field persistence is evidence of abandonment-stage grant.

## Work Items

- [ ] Register one conditional Classic and Blocks checkbox and add customer-consent guidance to existing Woo Recovery Settings without modifying the merchant theme.
- [ ] Test optional/unselected state, enabled/disabled recovery feature, connect/disconnect, deactivate/reactivate/upgrade/uninstall, already-open checkout, existing customer preference, 20 locales and checkout rendering.

## Interfaces / Contracts

Consumes existing plugin/installation state and recovery feature eligibility. Produces Moda checkout UI and merchant Recovery Settings guidance only; consent capture remains WOOCOMMERCE-002 and persistence remains API-001. No API-003 or WOOCOMMERCE-005.

## Dependencies

None

## Enables

- `ARCH-046-WOOCOMMERCE-002`
- `ARCH-046-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Both checkout types show the optional checkbox only for a connected, authorised, recovery-enabled installation; checkout remains possible without opt-in.
- [ ] No duplicate Moda registration on refresh/upgrade; disabled/deactivated/disconnected installations omit the field and no grant occurs without deliberate action plus hosted API acknowledgement.

- [ ] Merchant Recovery Settings contains accurate 20-locale consent guidance with no consent-source selector, and the plugin does not interfere with third-party checkout plugins.

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

## Developer Takeover

On 2026-10-23, `/moda_developer_create ARCH-046-WOOCOMMERCE-001` was invoked while this task was ready and agent-owned. This is an explicit developer takeover. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_woocommerce`, repository ownership, dependencies, scope and acceptance criteria are unchanged. The canonical launcher will claim Attempt 1 after worktree preparation.
