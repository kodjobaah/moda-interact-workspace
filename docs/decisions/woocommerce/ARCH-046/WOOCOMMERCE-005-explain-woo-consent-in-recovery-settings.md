---
id: ARCH-046-WOOCOMMERCE-005
architecture_id: ARCH-046
title: Explain Woo opt-in and consent-blocked recovery in Recovery Settings
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 36
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-046-WOOCOMMERCE-002
  - ARCH-046-WOOCOMMERCE-004
enables:
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-20
---

# Explain Woo opt-in and consent-blocked recovery in Recovery Settings

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

## Objective

Explain to connected Woo merchants how optional checkout opt-in works and why some recoveries pause, linking them to visible in-app notices.

## Context

Merchants need to understand consent collection, temporary blocking and later-grant expiration; the Woo UI already has Recovery Settings and Support navigation.

## Scope

- Add a concise localized Recovery Settings section identifying Classic/Blocks consent field behaviour, purpose and non-WhatsApp alternatives; explain absent consent blocks proactive outreach and does not consume recovery credits.
- Show guidance that only a **new affirmative customer action on the same valid checkout** can wake a blocked recovery in v1; opt-in after expiry or paid order does not revive it.
- Link/view actual relevant Support notices through WOOCOMMERCE-004; do not promise active Woo recovery until the separately approved engine is deployed.
- Preserve `WooCommerce > Moda Interact` entry point and nested `Overview`, `Recoveries`, `Billing`, `Promotions`, `Support`, `Recovery settings`, with native gettext and 20 locales.

## Out of Scope

- No merchant override/force-send/manual grant and no new CMP banner.
- No new WP staff roles/accounts, no campaign creation and no backend Woo recovery activation.

## Requirements

- Merchant text cannot state a checkbox itself is irrevocable grant or guarantee sending.
- Translation parity covers all 20 supported Woo admin locales; WordPress user admin locale with existing fallback and distinct store/customer language.
- Show actual readiness when consent capture is unavailable due to installation disconnection.

## Work Items

- [ ] Add bounded merchant help panel to existing Recovery Settings layout.
- [ ] Provide correct link/explanation to read-only Support and states.
- [ ] Verify all twenty translations, responsive page, no new top-level menu.

## Interfaces / Contracts

No new API schema; consumes WOOCOMMERCE-002 opt-in capability and WOOCOMMERCE-004 notice read state.

## Dependencies

- `ARCH-046-WOOCOMMERCE-002`
- `ARCH-046-WOOCOMMERCE-004`

## Enables

- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Merchant sees true consent setup, missing-consent reason and no-charge explanation.
- [ ] No bypass control or misleading promise of enabled Woo recovery.
- [ ] 20-language UI and established navigation preserved.

## Validation

- [ ] UI tests/translation build/WordPress ZIP and LocalWP merchant settings checks.
- [ ] `git diff --check`.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

Privacy/tracking cookies and WhatsApp recovery opt-in must be presented separately.

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
