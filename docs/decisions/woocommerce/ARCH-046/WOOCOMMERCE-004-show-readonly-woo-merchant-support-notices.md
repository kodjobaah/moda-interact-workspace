---
id: ARCH-046-WOOCOMMERCE-004
architecture_id: ARCH-046
title: Display authenticated consent-related merchant Support system notices
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 33
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-046-API-002
enables:
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-20
---

# Display authenticated consent-related merchant Support system notices

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

## Objective

Connect the existing Woo Support screen to an authorised read-only system-notice API through a privileged WordPress REST proxy.

## Context

Woo `src/support/support-client.js` explicitly returns unavailable capabilities; the visual page exists but has no hosted read implementation.

## Scope

- Add a narrow WordPress REST handler and server-side ModaApiClient method that proxies API-002 using existing installation credentials; require a valid WordPress REST nonce and merchant/admin capability.
- Enable only supported `read` capability in `src/support/support-client.js` and render paginated system notices in existing Support thread components; keep send and mark-read capabilities unavailable.
- Preserve two-stage WooCommerce → Moda Interact admin menu, modular controller/UI split, locale translations, no cross-merchant exposure and safe empty/error states.

## Out of Scope

- Do not implement arbitrary support messages, customer WhatsApp notifications or platform-admin inbox.
- Do not expose installation secret to browser or make new WordPress top-level menus.
- Do not change `MerchantSupportMessage` schema or bypass API auth.

## Requirements

- Server derives installation principal and tenant, browser only calls same-origin privileged WP REST route.
- Read-only notice DTO has bounded text/metadata; no raw phone/customer PII leakage.
- Proper unauthorised/empty/loading/error states; do not claim send/markRead works.

## Work Items

- [ ] Implement WP REST proxy and PHP client for approved API-002 read route.
- [ ] Wire existing Support controller/client/page to read-only safe projection.
- [ ] Test WordPress capability/nonce, API denial, Shop isolation, pagination and translation.

## Interfaces / Contracts

Consumes API-002's authenticated read-only Support notices projection; no new Shared contract or application write capability.

## Dependencies

- `ARCH-046-API-002`

## Enables

- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Connected Woo merchant sees only its Support system notices through original navigation.
- [ ] Non-admin, invalid WP nonce and stale installation cannot read.
- [ ] Support send/mark-read remain disabled until independently approved; 20 locale support maintained.

## Validation

- [ ] PHPUnit REST auth/proxy tests, JS Support UI tests, PHP lint/build/ZIP and LocalWP merchant/admin negative checks.
- [ ] 20-language catalogues and `git diff --check`.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

The notice is a merchant **in-app** message, not WhatsApp to the merchant. It must not be dropped into generic WordPress notices with unbounded PII.

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
