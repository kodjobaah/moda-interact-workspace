---
id: ARCH-060
title: Studio selected-shop provider connection visibility
status: agreed
coordinator: moda_architect
created: 2026-11-05
updated: 2026-11-05
---
# ARCH-060: Studio selected-shop provider connection visibility

## Decision
Connections shows a read-only **Store integration** section for the selected shop, alongside existing **External API connections** management. Shopify and WooCommerce credentials are fetched by the existing integration runtime. They are NEVER entered, edited, rotated, copied or duplicated in Studio. Do not create CommerceExternalConnection rows/revisions/credentials for Shopify or WooCommerce. Preserve external connection forms and their existing authorization unchanged.

## Current implementation evidence
app/connections/page.tsx resolves Studio shop selection but calls listConnections without passing selection into a provider read. src/studio/connections/production.ts createProductionConnectionPort delegates list/get to ExternalIntegration.lifecycle, which covers external connection rows only. Commerce already has direct integration data access: src/commerce/preview/local-provider-composition.ts createStudioLocalProviderExecution fetches Shopify offline sessions server-side, and src/commerce/woocommerce/authoring-credential.ts resolveWooReadGrant fetches the canonical Woo installation/grant and decrypts through Shared credentials. No new credential source, MCP request or provider connection storage is needed.

## Read contract and privacy
Add a Commerce-local server-only provider-status reader and a separate authenticated server action; these are new symbols, not existing APIs. Input is selected shop ID only. Resolve authorization and current shop/platform using existing Studio shop-context inspection before reading provider metadata. Never trust a client domain/platform. Return a bounded discriminated DTO: kind no-selection, forbidden/not-found, unavailable, or ok; ok contains selected shop ID, platform, safe display domain and status AVAILABLE, MISSING, INACTIVE, EXPIRED, NO_READ_ACCESS or UNKNOWN. No raw rows, tokens, encrypted envelopes, key IDs, grant/authorization IDs, consumer keys/secrets, raw provider responses or stack traces cross the client boundary.

Shopify AVAILABLE means current active selected Shopify shop has a matching non-online Session with nonempty token present and expires null or future. Do not return/read the token value for rendering: use a bounded existence query with nonempty-token predicate and explicit safe selects. Expired-only session yields EXPIRED, no offline session yields MISSING. The term offline session is Shopify's server credential type; it does NOT mean the shop is disconnected. Scope metadata may support a safe missing-read-scope state where an existing required scope is known; do not invent new required scopes. A valid local record does not prove live provider connectivity or token validity; label AVAILABLE as "Integration credentials available" and state "Live connection not checked". Do not claim Connected/Healthy from metadata alone.

WooCommerce metadata checks mirror resolveWooReadGrant guards: selected active WOOCOMMERCE shop; active unrevoked installation; canonicalSiteUrl/domain match; null shopifyShopId; ACTIVE read-scoped grant tied to same shop/installation with credentialVersionSnapshot matching installation credentialVersion. Missing grant -> NO_READ_ACCESS; inactive/revoked installation -> INACTIVE; absent installation -> MISSING; version mismatch -> NO_READ_ACCESS. No decrypt or new provider/network probe on page render. Runtime tools continue resolving/decrypting credentials only through the existing credential runtime. Local metadata cannot establish encryption configuration or live provider health; unknown/read failure -> UNKNOWN/unavailable, never AVAILABLE by fallback.

## State and navigation behavior
No selected shop: prompt "Select a shop to view its store integration"; do not choose the first shop or query provider status. Invalid/unauthorized selection: deny without leaking whether another tenant has credentials. Switching shops replaces status immediately and prevents stale prior-shop async results from showing under the new selection; cache keys must include authorized selected shop identity and do not use shared cross-shop status caches. Retain shopId across list/detail/back links where supported. Provider status remains visible when external integration configuration/list is unavailable; it must not depend on getCommerceExternalIntegration. External list filters/pagination continue to apply to external rows only; provider section is not a fake paginated connection row. Read-only viewers may see status only if existing Studio page/shop-read auth permits; no widened access.

## Verified touchpoints
| Existing file/symbol | Required change |
|---|---|
| moda-interact-commerce/app/connections/page.tsx / Page | Pass resolved selected-shop status separately from external initialList |
| moda-interact-commerce/app/connections/[id]/page.tsx / Page | Preserve selected-shop integration context while retaining external detail auth |
| moda-interact-commerce/src/studio/selected-shop.ts / resolveStudioShopSelection | Reuse selection resolution; do not silently select another shop |
| moda-interact-commerce/src/studio/server-actions.ts / shop-context actions | Reuse server-side authorized shop inspection, not client platform/domain |
| moda-interact-commerce/src/studio/connections/contracts.ts / local connection contracts | Add bounded read-only provider-status DTO/port, distinct from mutable external ConnectionView |
| moda-interact-commerce/src/studio/connections/production.ts / createProductionConnectionPort | Compose independent authenticated provider metadata read; no dependency on ExternalIntegration availability |
| moda-interact-commerce/src/studio/connections/server-actions.ts / listConnections action module | Add read-only provider action, authenticate every request; keep external mutations unchanged |
| moda-interact-commerce/src/studio/connections/connections-route-client.tsx / ConnectionsRouteClient | Carry selection-keyed provider status separately from external rows |
| moda-interact-commerce/src/studio/connections/connections-ui.tsx / ConnectionsPage, CredentialPanel | Add Store integration read-only section; never pass provider into CredentialPanel or external edit actions |
| moda-interact-commerce/src/studio/connections/navigation.ts / navigation helpers | Preserve authorized selected-shop context on routes/back navigation |
| moda-interact-commerce/src/commerce/preview/local-provider-composition.ts / createStudioLocalProviderExecution | Evidence/reuse boundary only: actual Shopify execution retains fetched offline session flow |
| moda-interact-commerce/src/commerce/woocommerce/authoring-credential.ts / resolveWooReadGrant | Reuse canonical guard semantics; actual tools keep existing fetched/decrypted credentials; no UI copy |
| moda-interact-commerce/tests/connections-production.test.ts | Authenticated metadata read and secret-free DTO tests |
| moda-interact-commerce/tests/connections-ui.test.tsx | Read-only section/state tests and absence of provider credential controls |
| moda-interact-commerce/tests/connections-route-composition.test.tsx | List/detail selected-shop propagation and external/provider independence |
| moda-interact-commerce/tests/selected-shop-navigation.test.tsx | Shop switching/back links without stale tenant status |

## Deterministic acceptance matrix
| Fixture/trigger | Expected behavior |
|---|---|
| No selection | Selection prompt; zero provider/session/grant reads |
| Active Shopify + valid offline session | AVAILABLE, Shopify label, live-check disclaimer; no credential controls |
| Shopify online-only / expired-only sessions | MISSING / EXPIRED respectively; never available by online session |
| Woo active matching read grant | AVAILABLE, WooCommerce label; no credential controls |
| Woo revoked/inactive / missing grant / version mismatch | INACTIVE / NO_READ_ACCESS / NO_READ_ACCESS |
| Missing installation or session | MISSING; direct merchant to existing installation flow without credential entry form |
| Authorized shop A switched to B during fetch | Only B result rendered; A result discarded |
| Forged other-shop ID or unauthenticated action | Denial before provider metadata read; no existence/credential leak |
| Database failure / external integration unavailable | Safe unavailable provider state on DB failure; external integration failure alone does not hide provider status |
| External rows empty while provider available | Provider section visible; external empty-state accurate |
| External create/edit/set/remove credential | Existing authorized external behavior retained, no provider rows written |
| Page render/refresh/provider status action | Zero writes, zero decrypt calls, zero outbound provider calls; secrets absent from DTO/HTML/serialized props/logs |

## Ownership and rollout
One bounded Commerce task suffices: all metadata and existing credentials are accessible in Commerce today. No MCP, Shared, Database or Gateway change; no provider API/schema/permission or secret wiring change. This is a compatible UI/read projection rollout with existing tenant and staff boundaries preserved. No data migration. Reuse existing bounded logging with fixed failure codes; do not log raw database/provider errors. No new generic telemetry. Roll back UI/read code without state conversion. Do not claim provider live health or runtime decryption verification from metadata.

## Tasks
| Task | Owner | Status | Dependencies |
|---|---|---|---|
| ARCH-060-COMMERCE-001 | moda_commerce | Ready | None |

## Open Questions
None blocking. This definition intentionally displays persisted integration availability, not live connectivity. No implementation or execution claim has occurred.

## Reuse store integrations when creating other tools

The Store integration section must provide an authorized **Create tool** entry point for the selected provider, not just a status display. Shopify opens the existing Shopify Admin GraphQL authoring flow (`SHOPIFY_ADMIN_GRAPHQL`); WooCommerce opens the existing WooCommerce REST API authoring flow (`WOOCOMMERCE_REST_API`). Carry only selected shop identity and the supported tool kind into the existing authoring route. Derive and validate shop platform server-side. These connections are reusable by any additional tool supported by those existing authoring/runtime adapters; they are not limited to the canonical product, shipping or discount capabilities.

Credentials are fetched server-side through the existing Shopify session/WooCommerce grant resolver when testing or executing a tool. Neither navigation nor tool definitions may carry tokens, credential envelopes or a copied connection credential. Do not create external connection rows for native providers. Metadata AVAILABLE is not execution authorization: each test/run rechecks current shop, provider, scopes and credential validity through existing runtime guards. Preserve existing draft validation, read-only operation restrictions, test proof requirements, publication and capability/release admission. Adding a tool never expands integration scopes or outreach's tool allowlist automatically.

### Additional verified authoring touchpoints
| File | Required change |
|---|---|
| `moda-interact-commerce/src/studio/connections/connections-ui.tsx` | Add Create tool action to native provider section, gated by existing authoring role and selected-shop state; no credential controls. |
| `moda-interact-commerce/src/studio/tools/new-tool-editor.tsx` / `NewToolEditor` | Reuse provider kind selection and selectedShop/shopId handling; validate incoming preselection and preserve normal authoring controls. |
| `moda-interact-commerce/src/studio/tools/tool-authoring-screen.tsx` | Preserve role checks, selected shop and current WooCommerce test proof on creation; do not bypass draft/test validation. |
| `moda-interact-commerce/src/commerce/preview/local-provider-composition.ts` / `createStudioLocalProviderExecution` | Reuse credential resolution for authoring tests; no duplicate credential source or weakened runtime guard. |
| `moda-interact-commerce/src/commerce/woocommerce/authoring-credential.ts` / `resolveWooReadGrant` | Retain current shop/installation/grant checks for every WooCommerce test. |

### Additional mandatory acceptance criteria
- [ ] Authorized Shopify shop -> Create tool opens Shopify Admin GraphQL authoring with that shop selected; an additional supported tool can be validated/tested/saved through the existing lifecycle using fetched credentials.
- [ ] Authorized WooCommerce shop -> Create tool opens WooCommerce REST API authoring with that shop selected; additional supported read tools retain the existing current-test proof before save.
- [ ] Missing selection, denied authoring role or missing/inactive provider metadata never exposes an enabled native Create tool shortcut; deep-link attempts still obey existing server authorization. Do not disable independently authorized external API creation.
- [ ] Changing shop/provider invalidates stale authoring tests and previous-shop preselection; a forged provider kind cannot select another tenant or mismatched adapter.
- [ ] Credentials revoked after metadata load cause the subsequent test/run to fail through existing guards; status display never supplies authority.
- [ ] Two separately created tools reuse the same native integration without creating provider external-connection/credential records; no secret values in routes, drafts, browser props or logs.
- [ ] Creating a tool leaves existing integration scopes, feature entitlements and outreach allowlists unchanged; normal publication is required for production capability use.

No new provider operation is implemented by this task. Unsupported operations require separately reviewed runtime work before they can be offered in authoring. Extend focused Connections and tool-authoring UI/server tests to prove every row above. Definition amendment only; implementation remains unclaimed.
