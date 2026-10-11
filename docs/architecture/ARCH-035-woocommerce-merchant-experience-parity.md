---
id: ARCH-035
title: WooCommerce merchant experience parity and recovery lifecycle
status: proposed
coordinator: moda_architect
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035: WooCommerce merchant experience parity and recovery lifecycle

## Problem and inspected starting state

The 11 October 2026 parent workspace snapshot already has a real native WooCommerce plugin, Woo Shop/install identity, connected Overview, Billing (including purchases and history), category selection, effective recovery-policy summary and 20-language WordPress admin localisation. `includes/Admin/NativeNavigation.php` still marks Recoveries, Promotions and Support as planned placeholders. The Shopify app additionally has recovery list/detail, merchant Support, Promotions, Usage History, editable recovery policy, feature preferences, Merchant Knowledge and recovery-performance Overview. Neither inspected Woo plugin nor its existing API ingress implements the cart/checkout/order activity -> durable recovery pipeline. `moda-interact-database` currently has Shop-owned CheckoutRecovery/UsageEvent/Support/Promotion/Knowledge records, but includes Shopify-specific coupon references. Existing ARCH-026 read authorisation is a separate consented Woo REST grant; it is not a write grant or billing-provider credential.

The task plan is source-derived from `moda-interact-workspace(20261011-185536).zip`. The **implementation specifications in each task are architect-locked proposals** (not implemented). Their names/fields/negative tests are deliberately concrete; any mismatch discovered during execution requires an Architect decision, not agent improvisation. No `_index.md` files are to be written until explicitly authorised at architecture/session reconciliation.

## Desired parity, not literal code duplication

- WordPress admin remains the merchant shell; Woo plugin PHP is the untrusted merchant-host boundary, browser React only calls privileged WordPress REST with nonce/capability.
- Moda API owns authenticated Woo merchant reads, commands and ingress; Shared owns cross-repository event contracts; Database owns durable constraints; Background owns recovery activity, reconciliation and WhatsApp emission. Do not import Shopify-authenticated Next.js route handlers into the hosted API.
- Reuse global Shop/Subscription/BillingPeriod/CheckoutRecovery/Support/Promotion/Knowledge entitlements. Avoid second domain ledgers and Shopify-only provider IDs for Woo.
- Keep 20 merchant UI locales: administrator UI locale first, site fallback. Never overwrite persistent Shop/store language or conversation language with the administrator's display locale.
- Shop-level auth/tenant isolation, narrowly scoped GET/POST contracts, idempotent writes and exact versioning across all endpoints. Private credentials stay in PHP/server-side API and never in browser payloads, logs or WordPress options beyond accepted encrypted/controlled installation storage.
- Preserve ARCH-027 WooCommerce.com Orders as the **external** provider-owned refund-request workflow. Do not copy Shopify merchant refund POST/undo into Woo.

## Workstreams and delivery gates

### A. Independent surfaces — implement first

- **Support:** API-001 -> WOOCOMMERCE-001.
- **Recovery delay/follow-up policy:** API-002 -> WOOCOMMERCE-002. Existing Store Category selector/effective summary remain.
- **Conversation feature preferences:** API-003 -> WOOCOMMERCE-003.
- **Merchant Knowledge:** API-004 (read) -> API-005 (safe URL/upload mutations) -> WOOCOMMERCE-004, reusing existing R2/worker/domain.
- **Promotional recovery credits:** API-006 -> WOOCOMMERCE-005. This is not Woo coupon/discount support.
- **Usage history:** API-007 -> WOOCOMMERCE-006. Financial Woo billing month and Moda entitlement 30-day cadence remain distinct.
- SYSTEM-TEST-001 certifies this tranche, including 20-locale, WP permission and Shopify regression.

### B. Woo checkout/order lifecycle and meaningful recoveries

```text
SHARED-001 activity v1
    -> DATABASE-001 durable receipt/provider correlation
    -> API-008 authenticated ingress and handoff
         -> WOOCOMMERCE-007 cart/checkout producer
         -> WOOCOMMERCE-008 order outcome producer
              -> BACKGROUND-001 materialise/reschedule
              -> BACKGROUND-002 authoritative order reconciliation
                   -> API-009 recovery list/detail -> WOOCOMMERCE-009
                   -> API-010 performance/pending overview -> WOOCOMMERCE-010
                   -> SYSTEM-TEST-002 independent black-box certification
```

The API authenticates and durably records events before acknowledging, using existing asynchronous mechanisms. Background reuses current recovery, capacity, WhatsApp and multilingual policies. Order evidence is authoritative; late checkout events cannot reopen completed/paid recoveries. No customer PII correlation by guesswork; require stable Shop-scoped provider lineage. Unknown customer phone is not recoverable recipient evidence. Shopify webhook, checkout, order and recovery regressions are mandatory.

### C. Woo-specific recovery offers — gated provider capability

Existing `ShopSettings.fixedShopifyDiscountId` and `ShopRecoveryPolicyOverride.fixedShopifyDiscountId` point to ShopifyDiscount. These references cannot be reused for Woo coupons. Read-only `ARCH-026-API-008` capability must be verified first, then API-011 validates supported Woo coupon restrictions and fail-closed semantics, DATABASE-002 adds the single Shop-scoped Woo selection model, **API-012** performs revision-guarded merchant selection and exposes private authenticated send-time proof, WOOCOMMERCE-011 renders validated selection, BACKGROUND-003 applies only provable offers, and SYSTEM-TEST-003 certifies provider safety.

Until this gate is complete, Woo Settings may support NONE and delay/follow-up, but must explicitly disable fixed/AI coupon offers. No unproven cross-provider coupon object is sent to a customer. If the consented Woo read grant is absent, revoked or insufficient, this stream remains pending without blocking Support or basic recovery.

## Frozen cross-repository implementation contracts (11 October refinement)

The following decisions resolve ambiguity in the original generic handoff. Each named task contains the exact file/field/API/test specification; the summary below is not a licence to invent extra fields.

1. **Woo activity:** Shared `woo.activity.v1` (single strictly bounded envelope and four event kinds: CHECKOUT_UPSERT, ORDER_PLACED, ORDER_PAID, ORDER_CANCELLED). WordPress owns a stable server-created `checkoutKey` and UUID eventId; installation bearer proves Shop. DATABASE-001 adds exactly one receipt inbox and one Shop-scoped checkout lineage/tombstone; existing CheckoutRecovery remains the only recovery record. Order evidence cannot be reversed by a later checkout update. API-008 commits receipt and terminal fence before 202. Background consumes the durable inbox and existing recovery/WhatsApp scheduling, without two-phase Redis/database acknowledgement.
2. **Merchant APIs:** Support, policy, feature preferences, knowledge, promotions and usage have individually versioned strict DTOs and explicit mutation conflict/replay semantics in API-001..007. Woo plugin routes are PHP privileged proxies with WordPress nonce and administrator display locale, not direct hosted browser calls. No new copies of existing support, knowledge, billing or promotion domain tables.
3. **Woo offers:** `ShopSettings.recoveryOfferMode` remains the desired mode; DATABASE-002 adds one Woo provider-specific coupon **selection** table and freezes `RecoveryOutreachAttempt.offerSnapshot` via Woo-only immutability guard. API-011 is provider-read/eligibility proof and **does not write selection**. API-012 is the mandatory selection-CAS and internal send-time verification owner. WOOCOMMERCE-011 cannot be implemented before API-012; BACKGROUND-003 must obtain same-Shop proof before making any coupon claim. Woo's SaaS billing credentials are unrelated to the REST coupon read grant.
4. **Provider capability gates:** Real Woo Checkout Blocks/HPOS and coupon read-grant support must be verified by the owner task's explicit tests. A missing documented hook/provider response is an implementation STOP requiring an Architect amendment; it must not be silently labelled PASS. Missing Woo SaaS Billing credentials block ARCH-027 provider financial certification, not these merchant read-only tasks.
5. **Schema bounds:** No prior migration edits; additive Prisma definitions, exact `woocommerce` namespace, tenant-safe FK/index/trigger tests, fresh/upgrade/re-run disposable Postgres proof and no storefront PII dumps. No `_index.md` files until final architecture reconciliation.

## Existing dependencies and deliberate exclusions

- ARCH-026 installation, category, locale and REST-read foundations are reused; `ARCH-026-API-008` is referenced only where approved provider REST reads are required. Its task record was still pending in the inspected snapshot, so this dependency is not assumed complete merely because related source exists.
- ARCH-027 accepted Billing/Top-ups/Purchase History remain unchanged. Missing WooCommerce.com SaaS sandbox credentials and LocalWP HTTPS return URLs block real money certification only; they must not be misrepresented as blockers to read-only Support/Settings/Knowledge/Promotions or local cart/order recovery development.
- No new Woo SaaS subscription/charge/refund API, no WordPress-local Postgres access, no direct browser calls to Moda-hosted APIs, no duplicate background worker, no fabricated promotions, discounts or recovered revenue, no new account/router framework.
- No Gateway deployment task is justified from the current snapshot: existing hosted API and privileged plugin proxy routes can be extended. If deployment evidence later proves route/auth/traffic configuration changes are required, return with that precise blocker before creating a Gateway task.
- Merchant Knowledge and Support may reuse current cross-shop domain workers only after tests prove Woo Shop eligibility. Missing worker support requires a narrowly scoped architect follow-up, not a silent rewrite.

## Implementation quality and acceptance

- Every task is one repository owner, defined file and non-overlapping boundary, no 300+ line catch-all new production file (target <=200 physical lines, hard ceiling 300 for new source).
- Each Woo UI task includes PHP privilege/nonce checks, session/disconnect stale-response fencing, responsive/keyboard/a11y validation, WordPress gettext POT + 19 reviewed PO files + compiled JS/MO assets and `plugin-zip`.
- Each cross-service producer/consumer records exact Shared versions and applied Prisma migrations. Disposable Postgres/Redis + WordPress tests must distinguish unit/contract/integration/black-box evidence.
- Preserve Shopify merchant routes and recovery/discount/billing behaviour; no parity pass relies only on mocked UI data.
- A task is not Complete until its own Completion Report and architect/developer acceptance are recorded. System test certification and genuine Woo SaaS billing/payment/provider refund certification remain separate from UI implementation acceptance.

## Task planning state

All task files in this handoff are portable **definitions only**. `ready` means zero unmet declared implementation prerequisites in this parent plan, not that a launcher/branch/worktree was created or a capability shipped. This environment did not create/push task branches or claims; the developer must materialise each task through the canonical launcher in the real workspace.

## Complete task dependency map

| Task | Owner | Capability | Depends on | Initial state |
|---|---|---|---|---|
| `ARCH-035-API-001` | moda-interact-api | Expose Woo merchant support history and actions | — | Ready |
| `ARCH-035-WOOCOMMERCE-001` | moda-interact-woocommerce | Build native Woo merchant Support screen | `ARCH-035-API-001` | Pending |
| `ARCH-035-API-002` | moda-interact-api | Expose safe Woo recovery policy reads and updates | — | Ready |
| `ARCH-035-WOOCOMMERCE-002` | moda-interact-woocommerce | Add editable Woo recovery policy controls | `ARCH-035-API-002` | Pending |
| `ARCH-035-API-003` | moda-interact-api | Expose plan-gated Woo conversation feature preferences | — | Ready |
| `ARCH-035-WOOCOMMERCE-003` | moda-interact-woocommerce | Add Conversation Features controls to Woo Recovery Settings | `ARCH-035-API-003` | Pending |
| `ARCH-035-API-004` | moda-interact-api | Expose Woo Merchant Knowledge source catalogue | — | Ready |
| `ARCH-035-API-005` | moda-interact-api | Add authenticated Woo Merchant Knowledge source mutations | `ARCH-035-API-004` | Pending |
| `ARCH-035-WOOCOMMERCE-004` | moda-interact-woocommerce | Add Merchant Knowledge management to Woo Recovery Settings | `ARCH-035-API-005`, `ARCH-035-WOOCOMMERCE-003` | Pending |
| `ARCH-035-API-006` | moda-interact-api | Expose Woo promotional-credit offers and history | — | Ready |
| `ARCH-035-WOOCOMMERCE-005` | moda-interact-woocommerce | Replace Woo Promotions placeholder with promotion-credit management | `ARCH-035-API-006` | Pending |
| `ARCH-035-API-007` | moda-interact-api | Expose Woo provider-correct usage and entitlement history | — | Ready |
| `ARCH-035-WOOCOMMERCE-006` | moda-interact-woocommerce | Add Woo usage-history reporting screen | `ARCH-035-API-007` | Pending |
| `ARCH-035-SHARED-001` | moda-interact-shared | Define Woo checkout and order activity contract v1 | — | Ready |
| `ARCH-035-DATABASE-001` | moda-interact-database | Persist Woo activity receipts and checkout/order correlation | `ARCH-035-SHARED-001` | Pending |
| `ARCH-035-API-008` | moda-interact-api | Accept durable Woo checkout and order events | `ARCH-035-SHARED-001`, `ARCH-035-DATABASE-001` | Pending |
| `ARCH-035-WOOCOMMERCE-007` | moda-interact-woocommerce | Capture supported Woo cart and checkout activity | `ARCH-035-API-008` | Pending |
| `ARCH-035-WOOCOMMERCE-008` | moda-interact-woocommerce | Capture authoritative Woo order lifecycle evidence | `ARCH-035-API-008` | Pending |
| `ARCH-035-BACKGROUND-001` | moda-interact-background | Materialise and reschedule Woo abandoned checkout candidates | `ARCH-035-API-008`, `ARCH-035-WOOCOMMERCE-007` | Pending |
| `ARCH-035-BACKGROUND-002` | moda-interact-background | Reconcile authoritative Woo order outcomes | `ARCH-035-BACKGROUND-001`, `ARCH-035-WOOCOMMERCE-008` | Pending |
| `ARCH-035-API-009` | moda-interact-api | Expose Woo recovery history and detail read models | `ARCH-035-BACKGROUND-002` | Pending |
| `ARCH-035-WOOCOMMERCE-009` | moda-interact-woocommerce | Build native Woo Recoveries list and detail | `ARCH-035-API-009` | Pending |
| `ARCH-035-API-010` | moda-interact-api | Expose Woo overview performance and pending work | `ARCH-035-BACKGROUND-002`, `ARCH-035-API-009` | Pending |
| `ARCH-035-WOOCOMMERCE-010` | moda-interact-woocommerce | Extend Woo Overview with recovery performance | `ARCH-035-API-010`, `ARCH-035-WOOCOMMERCE-009`, `ARCH-035-WOOCOMMERCE-006` | Pending |
| `ARCH-035-API-011` | moda-interact-api | Establish safe Woo coupon/offer integration contract | `ARCH-026-API-008` | Pending |
| `ARCH-035-API-012` | moda-interact-api | Persist validated coupon selection and internal runtime proof | `ARCH-035-API-011`, `ARCH-035-DATABASE-002` | Pending |
| `ARCH-035-DATABASE-002` | moda-interact-database | Store Woo recovery-offer selection and immutable evidence | `ARCH-035-API-011` | Pending |
| `ARCH-035-WOOCOMMERCE-011` | moda-interact-woocommerce | Add approved Woo recovery-offer selection UI | `ARCH-035-API-012`, `ARCH-035-DATABASE-002`, `ARCH-035-WOOCOMMERCE-002` | Pending |
| `ARCH-035-BACKGROUND-003` | moda-interact-background | Resolve Woo recovery offers from verified provider context | `ARCH-035-BACKGROUND-002`, `ARCH-035-API-012`, `ARCH-035-DATABASE-002` | Pending |
| `ARCH-035-SYSTEM-TEST-001` | moda-interact-system-test | Certify Woo merchant surfaces and Shopify parity | `ARCH-035-WOOCOMMERCE-001`, `ARCH-035-WOOCOMMERCE-002`, `ARCH-035-WOOCOMMERCE-003`, `ARCH-035-WOOCOMMERCE-004`, `ARCH-035-WOOCOMMERCE-005`, `ARCH-035-WOOCOMMERCE-006` | Pending |
| `ARCH-035-SYSTEM-TEST-002` | moda-interact-system-test | Certify Woo checkout-to-recovery and order outcomes | `ARCH-035-WOOCOMMERCE-007`, `ARCH-035-WOOCOMMERCE-008`, `ARCH-035-BACKGROUND-002`, `ARCH-035-WOOCOMMERCE-009`, `ARCH-035-WOOCOMMERCE-010` | Pending |
| `ARCH-035-SYSTEM-TEST-003` | moda-interact-system-test | Certify Woo coupons and recovery-offer safety | `ARCH-035-BACKGROUND-003`, `ARCH-035-WOOCOMMERCE-011`, `ARCH-035-SYSTEM-TEST-002` | Pending |

Task totals: 32 definitions (7 Ready, 25 Pending); none materialised or claimed.
