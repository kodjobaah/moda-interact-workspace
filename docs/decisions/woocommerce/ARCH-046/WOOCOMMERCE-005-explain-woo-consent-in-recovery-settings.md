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
status: superseded
priority: 24
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-20
updated: 2026-10-21
---

# Configure Woo consent source and explain recovery eligibility in Recovery Settings

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

## Objective

**Superseded — do not implement or claim.** The merchant-selectable `NOT_CONFIGURED` / `MODA_CHECKBOX` / `SUPPORTED_EXTERNAL` source selector, provider adapters and source-epoch persistence were removed from the agreed Woo v1 design on 2026-10-21. `ARCH-045-DATABASE-002` now uses existing WooInstallation identity and current CustomerPhone plus Moda-checkbox evidence only. No hosted consent-source settings API is required; WooCommerce Recovery Settings guidance and checkbox registration are consolidated under `ARCH-046-WOOCOMMERCE-001`. Everything below is retained solely as superseded historical specification; it is **not executable scope**.


Let merchants select exactly one authoritative WhatsApp consent collector and understand that **no consent means no CheckoutRecovery**, while retaining native WooCommerce UI/navigation.

## Context

The merchant may have another plugin checkbox. API-003 stores the source/epoch on existing WooCommerceInstallation; no generic third-party provider is yet certified. Customer permission is on CustomerPhone, separate from merchant source choice and checkout lifespan.

## Scope

- Provide privileged Recovery Settings read/write for API-003, with NOT_CONFIGURED default, MODA_CHECKBOX and SUPPORTED_EXTERNAL only after a certified adapter. The host-confirmed mode controls the optional Classic/Blocks Moda checkbox.
- Explain WhatsApp unfinished-checkout scope, explicit phone-specific opt-in, withdrawal, source switching, external-plugin evidence requirements and risk of duplicate WhatsApp abandoned-cart sender plugins; never automatically trust a cookie/CMP.
- Explain **no consent -> no CheckoutRecovery, send or recovery credit**, with a checkout-keyed merchant Support notice where appropriate. Later consent merely updates the customer-phone preference; only a subsequent **ordinary** checkout reconciliation, if it runs and the checkout remains eligible, can create recovery. No arbitrary consent expiry.
- Preserve the existing WooCommerce → Moda Interact navigation, WP capability/nonce security, 20 locales and HPOS support.

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

- [ ] Only one approved collector configured, no duplicate Moda checkbox or unsupported adapter auto-acceptance.
- [ ] Merchant guidance correctly describes current CustomerPhone, no immediate recovery on opt-in alone, and ordinary reconciliation-only re-evaluation.

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
