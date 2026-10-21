---
id: ARCH-046-WOOCOMMERCE-005
architecture_id: ARCH-046
title: Configure Woo consent source and explain recovery eligibility in Recovery Settings
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 24
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-046-API-003
enables:
  - ARCH-046-WOOCOMMERCE-002
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-20
---

# Configure Woo consent source and explain recovery eligibility in Recovery Settings

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

## Objective

Let merchants select exactly one authoritative WhatsApp consent collector and understand that **no consent means no CheckoutRecovery**, while retaining native WooCommerce UI/navigation.

## Context

The merchant may have another plugin checkbox. API-003 stores the source/epoch on existing WooCommerceInstallation; no generic third-party provider is yet certified. Customer permission is on CustomerPhone, separate from merchant source choice and checkout lifespan.

## Scope

- Add privileged, 20-locale Recovery Settings read/write proxy for API-003 with modes Not configured (default), Moda checkbox, and Supported external provider **only after certification**. Host acknowledgment controls displayed saved state; source switch increments epoch and invalidates eligibility of old source grants.
- Explain optional Classic/Blocks Moda checkbox, store-specific unfinished-checkout scope, exact phone, withdrawal and verified third-party evidence requirements. Warn about overlapping checkboxes **and overlapping WhatsApp abandoned-cart sender plugins** without fake automatic detection.
- Explain that missing/unverified consent prevents any `CheckoutRecovery` creation and charges; merchant Support notice refers to the **checkout**, not a paused recovery. Later customer opt-in may permit a first recovery **only if the abandoned checkout remains identifiable and eligible**; neither consent nor checkout automatically expires after a Moda-imposed 72-hour period.
- Preserve existing two-stage `WooCommerce > Moda Interact` to top-level active nested menu navigation, 20 native gettext locales, HPOS compatibility and Support link.

## Out of Scope

- No checkbox auto-detection, CMP banner, third-party adapter implementation, admin-created grant, manual bypass or source-specific consent DB table.

## Requirements

- [ ] Mode change is durable in existing hosted installation configuration only after API acknowledgement.
- [ ] Consent mode does not equal customer consent; unsupported external integration cannot be selected as a shortcut.

## Work Items

- [ ] Implement settings proxy/UI with accepted source, epoch, safe disabled states and idempotent save.
- [ ] Add clear merchant guidance, translations and duplicate-checkbox warnings; test no-source/Moda/external-unavailable flows.

## Interfaces / Contracts

Consumes API-003 source read/write and provides current selection to Woo conditional checkout integrations; merchant Support notices from BACKGROUND-002 require future approved recovery engine.

## Dependencies

- `ARCH-046-API-003`

## Enables

- `ARCH-046-WOOCOMMERCE-002`
- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] One collector selected and persisted; no automatic extra Moda checkbox or unsafe external selection.
- [ ] Accurate no-consent/no-recovery/no-charge copy; no 72-hour consent expiry or promise of guaranteed old-checkout resumption.

## Validation

- [ ] WordPress capability/REST nonce, modes, existing 20 locales, Classic/Blocks visibility, merchant UI tests and declared build/lint; `git diff --check`.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

Privacy/tracking cookies and WhatsApp recovery opt-in must be presented separately. Do not infer external-plugin WhatsApp permission from a plugin activation, checkout DOM or cookie/CMP category.

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
