---
id: ARCH-026-WOOCOMMERCE-015
architecture_id: ARCH-026
title: Add WooCommerce read-only consent to merchant connection setup
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-026-API-007
  - ARCH-026-WOOCOMMERCE-003
  - ARCH-026-WOOCOMMERCE-006
enables:
  - ARCH-026-SYSTEM-TEST-001
created: 2026-10-10
updated: 2026-10-10
---

# Add WooCommerce read-only consent to merchant connection setup

## Architecture

Architecture ID: `ARCH-026`.

Architecture document: `docs/architecture/ARCH-026-woocommerce-application-foundation.md`.

Coordinator: `moda_architect`.

## Objective

Present an explicit WooCommerce `read` authorisation step within the existing Moda Connect experience, using native WooCommerce approval and a separate, trustworthy provider-access status.

## Context

The plugin already implements `ConnectionCoordinator`, `InstallationStore`, `ModaApiClient`, the privileged WordPress `ConnectionController`, native WordPress navigation and modular React page/controller composition. Connect automatically establishes Moda's Free plan and one-time credits; it must not be repurposed to transport Woo REST keys. `ARCH-026-API-007` will provide an HTTPS Woo authorisation URL, callback and server-side grant status. The new UI should feel consistent with Shopify's onboarding status/actions without copying Shopify's OAuth, router or billing workflow.

## Scope

`moda-interact-woocommerce` only:

- Add a small PHP facade/client for the API-007 read-authorisation start, status and local revoke endpoints using the existing stored installation credential; expose only an administrator-authorised WordPress REST facade to React.
- Show a merchant-friendly read-only permissions explanation and approval action after successful Connect, including for shops connected before this feature ships.
- Return to the existing Moda Woo admin page after WooCommerce's native approval/denial flow and re-read authoritative server-side status; keep the installation connection and billing states separate from provider grant status.
- Add modular React controller/state and focused presentational components, with 20-language WordPress gettext coverage and production ZIP validation.

## Out of Scope

- Acquiring or storing Woo consumer keys in WordPress, React, JavaScript local storage or a shortcode.
- Direct browser-to-Moda API calls, browser-supplied API origins, Shop IDs, callback targets or Woo permission scopes.
- Adding `write`/`read_write` consent; generating keys secretly during plugin activation; blocking automatic Free-plan activation on consent.
- Changing the underlying Connect/HMAC proof, billing or Recovery Settings, implementing MCP tool execution or global shop language mutation.
- Recreating the WordPress native sidebar or a monolithic new onboarding page.

## Requirements

1. **Merchant intent:** Use the existing Connect flow first. Present a clear next step such as "Allow Moda Interact to read store data", identifying that WooCommerce—not Moda—will request approval for `read` permission. The user must explicitly initiate Woo's authorisation screen; plugin activation alone never creates API credentials. A merchant declining/skipping consent remains connected and Free-onboarded, but Woo-backed read features are unavailable.
2. **Server authority:** PHP calls API-007 with the existing installation credential and derives the canonical site from `SiteIdentity`/saved installation state. Only `manage_woocommerce` users with a valid WordPress REST nonce may initiate, inspect or revoke grant status. Public challenge route remains narrowly scoped; do not add an unauthenticated local route for status or key handling.
3. **Browser safety:** The browser may receive the bounded Woo authorisation URL and safe grant-status fields only; it must never receive the consumer key/secret, stored Moda installation credential, encrypted envelope, callback token separately or provider payload. Prevent arbitrary redirect URLs, cross-origin credential dispatch, duplicate-button actions and stale async UI results.
4. **Status states:** Distinguish at least Connected-to-Moda vs read-access Pending / Approved / Declined-or-expired / Revoked-or-invalid / Provider temporarily unavailable. Do not treat Woo's browser `success=1` parameter as a grant; re-fetch API-007's committed status after return, including a bounded pending/refresh presentation when the callback arrives later. Re-authorisation is supported independently of reconnect/credit restoration.
5. **Revocation explanation:** A merchant can disconnect Moda's use of its stored outgoing read grant. Show clear instructions that they may also need to remove the original consumer key inside WooCommerce's REST API key settings; the plugin cannot claim to revoke the Woo-hosted key using a read-only grant.
6. **Shopify UX parity and modularity:** Reuse native Moda Woo navigation and the established connected workspace rather than adding Shopify's UI router. Match Shopify's design language for headings, explanatory cards, status and primary/secondary actions. Keep PHP transport, controller/state and visual components in focused separate modules rather than extending `src/page.js` or creating another monolith.
7. **20-language packaging:** All new PHP and React strings use `moda-interact` WordPress gettext and administrator UI locale (site fallback), independently of the persisted store locale and CommerceAgent language. Update the POT, 19 translated PO files, source-count/placeholder assertions and `.mo`/hashed JS assets as appropriate. `npm run plugin-zip` must ship complete translations; no English-only shortcut and no untranslated new UI visible in LocalWP.
8. **Failure independence:** Provider outage, declined access, callback delay and key invalidation must not rotate the Moda installation credential, repeat first-connect Free grants, change Shop international context, or block normal read-only Overview/Billing/Recovery Settings.

## Work Items

- [ ] Add narrowly scoped PHP API-007 transport and privileged WordPress REST routes for read-grant start/status/revoke.
- [ ] Add modular React read-consent step, authoritative status refresh and explicit revoke/retry actions to the connected workspace.
- [ ] Add Woo-native return route/handling without accepting browser return as authoritative grant success.
- [ ] Translate every new UI/error/status message across all 20 supported catalogues, with placeholder/plural and generated asset checks.
- [ ] Add PHP/JS tests, a WordPress permission/nonce matrix and package/install/upgrade checks.

## Interfaces / Contracts

- **Remote:** API-007-owned `openapi/woocommerce-read-authorization-v1.yaml`; PHP is the only authenticated API consumer and never receives Woo's raw callback payload.
- **Local:** New admin-only WordPress REST endpoints under `/wp-json/moda-interact/v1/connection/read-access/...` (the exact routes must be documented and covered by tests). No new public challenge/callback route is required in WordPress.
- **Provider:** Browser navigation to Woo's `/wc-auth/v1/authorize?scope=read&...` using the canonical URL returned by the authenticated API. The Woo callback sends secrets directly to hosted Moda API, not to PHP/React.
- **Readback:** Server-side grant status from API-007 and the existing Moda installation connection/bootstrap remain independent.

## Dependencies

- `ARCH-026-API-007` — accepted read-grant initiation/status/callback/revocation API.
- `ARCH-026-WOOCOMMERCE-003` — accepted plugin installation credential and PHP API facade.
- `ARCH-026-WOOCOMMERCE-006` — accepted packaging and upgrade lifecycle.

## Enables

- `ARCH-026-SYSTEM-TEST-001`.

## Acceptance Criteria

- [ ] A Woo admin can approve read-only access through native Woo authorisation from the existing Connect experience; an already-connected shop can approve later without reconnecting.
- [ ] Non-admin or nonce-less requests cannot initiate/status/revoke a grant; no Woo REST key appears in PHP browser responses, translated JS data or build artefacts.
- [ ] Rejected, expired, pending and invalid grants leave the Moda connection and Free subscription/credits intact and produce truthful, recoverable UI states.
- [ ] Approval is shown only after API-007 confirms an active stored grant; callback and return ordering cannot create a false success.
- [ ] Existing native navigation, responsive parity, accessible actions and the production ZIP behave correctly on clean install and upgrade.
- [ ] All new strings are covered by 20 languages in the installed plugin, with administrator-vs-store locale separation preserved.

## Validation

- [ ] `composer lint` and `composer test`.
- [ ] `npm run test:js`, `npm run test:i18n`, `npm run i18n:verify:20`.
- [ ] `npm run plugin-zip`, with ZIP translation-asset inspection.
- [ ] Disposable WordPress/LocalWP administrator permission, consent-return/status, denied, delayed callback, revoke and upgrade checks (a real Woo callback requires reachable HTTPS test ingress).
- [ ] `git diff --check` and task-isolation/Completion Report evidence.

## Stop Condition

After Work Items, Acceptance Criteria and Validation pass, set task to `review`, return the Completion Report to `moda_architect` and STOP. Do not implement a Commerce connector or follow-on billing work.

## Implementation Notes

Do not place a callback secret or any long-lived credential into localized script data, React state or persistent WordPress options. The URL returned by the API for the Woo-hosted consent screen is a short-lived authorisation URL and must not be reassembled from user inputs. A completed `npm run plugin-zip` alone is not proof that WordPress actually loaded the generated locale assets.

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

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending.

### Review Notes

Pending implementation review.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Await repository implementation and Completion Report.
