---
id: ARCH-035
title: WooCommerce merchant Admin UI parity with Shopify
status: proposed
coordinator: moda_architect
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035: WooCommerce merchant Admin UI parity with Shopify

## Status and revision context

**Proposed UI-led revision, 11 October 2026.** The developer narrowed ARCH-035 to the WooCommerce merchant interface and requested ASCII page designs. After approving the Recoveries shell, the developer explicitly authorised a **bounded read-only API for page data with pagination**, without reopening recovery processing. This replaces the earlier UI-plus-checkout/order-recovery lifecycle architecture. No implementation task is accepted; no parent or implementation task branch was created/pushed by this portable-document handoff. Do not update any `docs/decisions/**/_index.md` files until the developer explicitly confirms final reconciliation.

## Problem and inspected starting state

The inspected `moda-interact-workspace(20261011-192347).zip` has a native WordPress plugin with working connected Overview, Billing and Recovery Settings/Store Category surfaces. `moda-interact-woocommerce/includes/Admin/NativeNavigation.php` still uses `register_planned` for Recoveries, Promotions and Support; its `src/native-admin/page-surface.js` and `src/page/connected-workspace.js` handle only Overview/Billing/Recovery Settings. Woo Usage History and Recoveries detail are not current UI surfaces. Shopify has merchant Support, Promotions, Recoveries list/detail, Usage History, a richer Overview, and Recovery Settings with policy, feature preferences and Merchant Knowledge sections.

## Goal

Make WooCommerce **page structure, navigation, information hierarchy, validation/feedback and merchant interactions** match the current Shopify merchant-facing experience as closely as WordPress Admin permits. Keep WordPress-native navigation and presentation rather than shipping Shopify-specific authentication or Polaris server components. All UI plans must be grounded in the actual Shopify source, not invented features, copy, backend data or status labels.

## Explicit non-goals and boundary

- No PostgreSQL schema or table additions, migrations, Database/Shared contract implementations or new queue events.
- No Woo checkout/order capture, lineage, recovery materialisation, provider-status reconciliation, new Background jobs, WhatsApp changes or new checkout recovery engine.
- No Woo coupon validation/selection/provenance, discount issuance, new billing/refund business behaviour or price/plan changes.
- No new hosted API **writes**, checkout capture, new private gateway/Render configuration or externally published contracts. Narrow read-only merchant APIs explicitly approved to populate an accepted Woo UI surface are permitted; `ARCH-035-API-009` and `ARCH-035-API-013` are specifically approved read-only UI data dependencies.
- No attempt to change the actual Shopify page behaviour. Shopify is read-only reference.
- No production fake data, fake success, made-up recovery revenue, credentials in browser storage or direct browser-to-hosted-API calls.

## Architecture and ownership

- **`moda-interact-woocommerce` (`moda_woocommerce`):** sole implementation repository for this UI initiative. Existing WordPress navigation, React components/hooks/controllers, CSS, native gettext and approved plugin REST client/proxy integration are in scope. No new hosted service routes or provider domain algorithms.
- **`moda-interact` (`moda_app`):** read-only Shopify UX reference.
- **`moda-interact-api` (`moda_api`):** bounded authenticated, read-only UI data endpoints when individually authorised, starting with paginated Recoveries list API-009 and Recovery Detail API-013. No billing, ingress or recovery-processing changes.
- **`moda-interact-database`, `moda-interact-background`, `moda-interact-shared`, `moda-interact-gateway`:** no ARCH-035 implementation tasks.
- **`moda-interact-system-test` (`moda_system_test`):** one terminal UI parity/certification task, after all implementation tasks are accepted.
- **`moda_architect`:** cross-page design, task scope/dependencies, review, UI parity and documentation reconciliation.

### Existing service functionality versus UI parity

A page can be drawn and tested without creating backend operations. A missing approved data/action API **does not authorise a Woo repository agent to implement or invent that API**. The UI may use a test-only fixture and a strictly local presentation adapter for design and component tests, but merchant-facing production must show an honest unavailable/disabled state for unsupported operations. No missing real data is represented as zero, a successful send, a successful save, a selected promotion, recovered revenue or an active AI capability.

If the developer later wants full real-end-to-end merchant feature parity, the missing hosted API/checkout/order/offer capabilities require separately scoped architecture and implementation, not hidden scope expansion in ARCH-035.

## Shopify-to-Woo source map

| Shopify reference | Native Woo target | Task |
|---|---|---|
| `app/routes/app/merchant-support/route.jsx` | Support submenu: message thread/composer | WOOCOMMERCE-001 |
| `app/routes/app/recovery-settings/RecoverySettingsView.tsx` | Recovery Settings: effective policy + behaviour sections | WOOCOMMERCE-002 |
| `app/components/settings/FeaturePreferences.tsx` | Feature controls **within Recovery Settings** | WOOCOMMERCE-003 |
| `app/components/settings/MerchantKnowledgeSection.tsx` | Merchant Knowledge **within Recovery Settings** | WOOCOMMERCE-004 |
| `app/routes/app/promotions/route.tsx` | Promotions credits submenu | WOOCOMMERCE-005 |
| `app/components/dashboard/UsageEvents.tsx` | Usage History linked from merchant surfaces | WOOCOMMERCE-006 |
| `app/routes/app/recoveries/RecoveryList.tsx` | Recoveries list/filter/pagination submenu | WOOCOMMERCE-009 |
| `app/routes/app/recovery-detail/RecoveryDetail.tsx` | Recoveries detail with message history | WOOCOMMERCE-013 |
| `app/components/dashboard/RecoveryOverview.tsx` + `PendingRecoveries.jsx` | Richer Woo Overview | WOOCOMMERCE-010 |
| Shopify merchant navigation layout | WordPress Admin surface registry/breadcrumbs/links | WOOCOMMERCE-012 |

Existing Woo Billing and Store Category/connection screens are preserved and included in UI regression comparison; no speculative redesign task is assigned to already implemented capabilities. New gaps discovered in comparison return to the architect for bounded follow-up.

## UI structure / ASCII design contract

Every new or revised Woo UI task includes a source-derived `## ASCII Page Design` section. It specifies the **page shell, positioning, major cards, controls, actions, navigation and relevant loading/empty/error/disabled states**. Fixed-width ASCII is a reviewable layout contract, not pixel-level CSS and **not permission to invent domain data or functionality**. Keep each section with its Shopify analogue: Feature Preferences and Merchant Knowledge are sections of Recovery Settings; Promotions are recovery-credit promotions, not provider coupons.

```text
WordPress Admin
  Moda Interact
    Overview ------------------ Recovery performance / capacity / pending
    Recoveries --------------- Filtered list -> Recovery detail
    Billing ------------------ Existing Billing + link to Usage History
    Promotions --------------- Promotional recovery credits
    Support ------------------ Merchant support inbox
    Recovery settings -------- Effective policy / controls
                                   |-- Feature preferences
                                   |-- Store category
                                   +-- Merchant Knowledge
```

A Woo UI task must split presentation, controller/state, data client and integration rather than introduce monolithic page.js or oversized component files. Prefer modules near 200 lines; no new production catch-all above 300 lines.

## Security, localisation, failure handling

- Use `manage_woocommerce`, WordPress REST nonce/capability and existing connected installation/credential rotation guards for any approved network operation.
- No direct browser-to-hosted Moda API, tenant-supplied shop identity, leaked secret/token or storing sensitive support/recovery data in browser persistence.
- WordPress administrator UI locale with site-language fallback, full parity across all 20 supported merchant UI locales; preserve saved store/customer-conversation languages.
- Accessible labels, keyboard/focus order, narrow viewport, translated/original message display and no duplicate submits or stale asynchronous results after disconnect.
- Use real approved read actions only if present; all unavailable write/read capabilities have explicit merchant-facing disabled/failed states and test fixtures remain test-only.
- No new telemetry, new gateway resources or cross-service version publication is justified by UI-only scope. Existing failure/logging and security mechanisms remain in place.

## Rollout / verification

Current planned UI work is pre-production; no database migration is authorised. The new read-only API must be available before the separate WooCommerce proxy/React integration is enabled. Existing WordPress ZIP build/install/upgrade and 20-language compilation remain required. The certification task validates **UI parity**, not Woo checkout/recovery lifecycle, provider offers or end-to-end payment/refund workflows. Do not claim real feature certification from component fixtures.

For each UI implementation task run the repository-declared relevant JS/PHP tests, `npm run test:i18n`, `npm run i18n:verify:20`, `npm run build`, `npm run plugin-zip`, LocalWP UI checks and `git diff --check` as specified in that task. The developer may manually validate before choosing to execute Ready SYSTEM-TEST-001.

## Active task plan (portable definitions, not materialised)

| Task | Owner | Outcome | Depends on | Planned state |
|---|---|---|---|---|
| `ARCH-035-API-009` | moda_api | Read existing Woo Shop Recoveries with bounded filters and server-side pagination | — | Ready |
| `ARCH-035-API-013` | moda_api | Read existing Recovery Detail, conversation history and related recoveries with independent bounded cursors | API-009 | Pending |
| `ARCH-035-WOOCOMMERCE-012` | moda_woocommerce | Preserve two-stage WordPress navigation and wire native pages | — | Ready |
| `ARCH-035-WOOCOMMERCE-002` | moda_woocommerce | Match Shopify recovery-policy settings layout and controls | — | Ready |
| `ARCH-035-WOOCOMMERCE-001` | moda_woocommerce | Build native Woo merchant Support screen UI | WOOCOMMERCE-012 | Pending |
| `ARCH-035-WOOCOMMERCE-003` | moda_woocommerce | Add Shopify-parity conversation feature controls within Recovery Settings | WOOCOMMERCE-002 | Pending |
| `ARCH-035-WOOCOMMERCE-004` | moda_woocommerce | Add Shopify-parity Merchant Knowledge section within Recovery Settings | WOOCOMMERCE-003 | Pending |
| `ARCH-035-WOOCOMMERCE-005` | moda_woocommerce | Build native Woo Promotions credit-selection UI | WOOCOMMERCE-012 | Pending |
| `ARCH-035-WOOCOMMERCE-006` | moda_woocommerce | Add Shopify-parity Woo Usage History UI | WOOCOMMERCE-012 | Pending |
| `ARCH-035-WOOCOMMERCE-009` | moda_woocommerce | Build native Woo Recoveries list UI | WOOCOMMERCE-012 | Pending |
| `ARCH-035-WOOCOMMERCE-013` | moda_woocommerce | Build native Woo Recovery Detail UI | WOOCOMMERCE-009 | Pending |
| `ARCH-035-WOOCOMMERCE-010` | moda_woocommerce | Bring native Woo Overview presentation to Shopify dashboard parity | WOOCOMMERCE-006, WOOCOMMERCE-013 | Pending |
| `ARCH-035-SYSTEM-TEST-001` | moda_system_test | Independent native UI parity validation | All 10 Woo UI tasks | Pending |

This is **13 active task definitions**: **3 Ready, 10 Pending**, with no formal task acceptance recorded in the snapshot. The developer has separately visually reviewed the Woo Recoveries shell. Stage 3 WordPress REST/React integration will be materialised as an additional bounded task after API-009 approval. The system test is a terminal dependency; no implementation task depends on a system test. Task state is authoritative in each individual YAML file, not in this summary.

## Superseded definitions (not executable)

The original ARCH-035 plan also contained 23 non-UI task definitions; **API-009 is now explicitly re-scoped and reactivated**, leaving 22 superseded task definitions. These are retained for history with `status: superseded`, not silently deleted or reassigned:

- API-001..008 and API-010..012 (11): other hosted merchant APIs, Woo activity and coupon interfaces. API-009 is re-scoped as an active list-read task.
- DATABASE-001..002 (2): checkout activity / Woo offer persistence.
- BACKGROUND-001..003 (3): checkout/order/recovery processing and offers.
- SHARED-001 (1): Woo commerce activity contract.
- WOOCOMMERCE-007, -008, -011 (3): checkout/order event producers and coupon selection.
- SYSTEM-TEST-002 and -003 (2): backend checkout/order/offer certification.

Superseded task IDs must not be repurposed for unrelated UI changes. Their former dependencies are absent from all active tasks. This does **not** certify that the underlying functionality is implemented or unnecessary for eventual functional parity.

## Dependency graph

```text
WOOCOMMERCE-012 (navigation) ----+----> 001 Support
                                 +----> 005 Promotions
                                 +----> 006 Usage History -----+
                                 +----> 009 Recoveries list    |
                                             |                 |
                                             v                 |
                                         013 Detail ------------+--> 010 Overview

WOOCOMMERCE-002 (policy layout)
          |
          v
    003 Feature controls
          |
          v
    004 Merchant Knowledge

API-009 (existing-data list read) ---> Woo Recoveries list integration
    |
    v
API-013 (detail/messages/related reads) ---> future Woo Recovery Detail integration

All ten Woo UI tasks ---------------------------> SYSTEM-TEST-001
```

The ordering minimizes file conflicts while leaving independent surfaces parallel. A task becomes Ready only when its actual declared dependencies are architect-accepted `complete`.

## Open issues to report, not implement in ARCH-035

- Which requested merchant read/mutation operations are actually exposed through existing approved Woo PHP plugin / hosted API calls. The current plugin does not expose the full set of Shopify-equivalent data/actions.
- Whether the existing Woo Overview can retrieve authoritative recovery performance, pending recoveries and currency values without new hosted API support. Until verified show unavailable instead of fake zero.
- Whether server-side support message send/read and Knowledge/Promotions/feature writes exist as approved public Woo endpoints. Until verified disable actions and report integration gaps.

## Architecture change history

- **2026-10-11 original:** mixed Woo merchant UI and checkout/order/offer recovery lifecycle, 32 task definitions.
- **2026-10-11 UI-only scope decision:** user limited work to merchant UI and required ASCII page designs. Backend tasks superseded; 10 bounded Woo UI tasks (two new task IDs) and one terminal UI test; no `_index.md` changed.

- **2026-10-11 staged Recoveries agreement:** developer approved responsive UI shell, authorised API-009 as existing-data read only with server-side page/pageSize/total/totalPages and date/customer/status filters. Reopened/re-scoped API-009; no new tables, Background work or `_index.md` changes. Stage 3 remains a separate future integration task.

- **2026-10-12 detail read approval:** developer requested Stage 2 after the responsive Recovery Detail shell. Added API-013 as a bounded Woo Shop-authenticated read-only detail/messaging/related endpoint with independent cursor pagination. No database, Background, Shopify or `_index.md` work.
