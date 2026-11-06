---
id: ARCH-062
title: Remove duplicated Shopify domain guards on trusted integrations
status: agreed
coordinator: moda_architect
created: 2026-11-05
updated: 2026-11-06
---
# ARCH-062: Trusted integration identity and custom storefront domains

## Decision and boundary
Remove app-owned duplicated `.myshopify.com` suffix/regex admission checks from already authorized selected-shop execution and metadata paths. A shop may have a custom storefront domain. This does NOT make that storefront an Admin/OAuth credential destination. Reuse ARCH-061 selected Shop ID -> trusted existing installation/offline Session mapping; snapshot.shop is the actual SDK-established integration endpoint. No new validator, alias table, DNS discovery, primaryDomain-to-Admin rewrite or central service. Existing SDK install/auth domain acceptance, JWT/HMAC and tenant admission remain authoritative.

Official sources: [Shopify Shop object](https://shopify.dev/docs/api/admin-graphql/latest/objects/shop) distinguishes myshopifyDomain from primaryDomain; [Admin API](https://shopify.dev/docs/api/admin-graphql/latest) documents Admin requests at the shop integration endpoint; [Shopify domain guidance](https://help.shopify.com/en/manual/domains/removing-domains) retains original Shopify identity when storefront domains change. Never claim a custom storefront host is a valid OAuth/Admin endpoint solely because a merchant entered it.

## Exact data and request contract
Consumer authorization resolves selected commerce.Shop.id first. Obtain ARCH-061 getSession(shopId) server-only snapshot, using existing owned Shop/domain/session association, not user/domain pattern recognition. Transport receives snapshot.shop together with selected-shop identity and current accessToken from SAME snapshot. Endpoint is constructed from this trusted host and fixed existing Admin API path/version. Runtime still validates exact requested origin/host equals resolved snapshot.shop, https, no URL credentials, no arbitrary port, fixed path, method/query/body bounds, redirect:error and existing timeout/cancellation. These are destination-binding/SSRF controls, not a replacement suffix regex. An input URL/primaryDomain/browser Host/tool argument cannot choose credential recipient. A mismatched or missing mapping fails before credential retrieval/network. Do not fabricate mapping when existing Shop.domain differs from Session.shop without persisted installation association: explicit unavailable, no guessed fallback or schema change.

ARCH-061 snapshot already carries server-only shop and scope; reuse it rather than adding a second reusable contract/package. Where a port today returns string token and accepts domain, change owning local port to accept selected shop ID and return/use snapshot endpoint or thread trusted endpoint separately from display domain. No cross-repository sibling imports. Endpoint identity remains server-only. Metadata-only reads do not refresh credentials; external credential authoring and WooCommerce flows retain their existing behavior.

## App entry and profile decision
App authenticated profile myshopifyDomain is provider-owned integration identity, distinct from storefront primaryDomain. Replace suffix regex schema validation with existing bounded nonempty provider string shape checks and retain equality to SDK-authenticated Session.shop; do NOT compare to a user-supplied storefront domain. Selected-shop trusted uploads use the selected owned shop/session association, never a suffix regex as authorization. For public install entry remove duplicated suffix parser and restrictive explanatory copy; hand install domain to existing Shopify SDK login/auth validation. Unknown custom storefront input is not resolved by DNS or credentialed probes: show guidance to launch/install the app through Shopify's existing flow and let SDK obtain integration identity. Already connected custom-storefront shops use owned selected-shop identity, not a new auth host. Preserve anti-open-redirect and mutation origin controls. No promise that arbitrary custom storefront is accepted by Shopify OAuth.

## Deterministic common acceptance matrix
| Scenario | Required result |
|---|---|
| Existing Shopify shop with custom storefront, legitimate stored SDK integration/session | Selected-shop operations admitted; credentials sent only to actual stored integration endpoint |
| Selected owned shop + user custom URL/Host/header/tool domain override | Override cannot select endpoint; reject mismatch or ignore display-only field |
| Shop/session association missing/foreign/ambiguous | Existing safe unavailable/denied result before provider network; no alias guessing |
| New install input accepted/rejected by SDK | SDK remains authority; no duplicated suffix parser; rejection gives guidance without credential probe |
| Provider profile identity mismatches authenticated SDK session | Existing identity rejection retained; custom storefront does not weaken it |
| Redirect to arbitrary/custom/private origin | redirect:error; credentials never forwarded |
| Existing Woo/external connection | Existing validation/SSRF and authoring behavior unchanged |
| Stored integration absent/wrong provider/inactive tenant | Fail closed independent of domain string shape |
| Commerce status render | Metadata only; no OAuth refresh or probe |
| Secret canary in credentials/provider errors | Not in UI, HTML, action DTO or logs |

## Exclusions and rollout
No blanket search/replace of every myshopify string. Leave SDK internals, documentation/examples of actual Admin endpoints and Shopify-admin billing handle construction intact. Recovery summary display-only regex is not authentication: change only if necessary for correct display, with dedicated fixture; never replace provider endpoint with it. Partner API tokens are a different credential domain and outside scope. No schema/DNS/secret/infrastructure change. Compatible application rollout after each ARCH-061 owner adoption; preserve old stored identities. Do not change lock identity/refresh recovery. System test is terminal after accepted implementation and optional user manual checks. Definitions only, no deployment/claim. Existing generic logging suffices; no observability framework work.

## Tasks
| Task | Owner | Status | Dependencies |
|---|---|---|---|
| ARCH-062-SHOPIFY-001 | shopify | Ready | ARCH-061-SHOPIFY-001 |
| ARCH-062-BACKGROUND-001 | background | Complete | ARCH-061-BACKGROUND-001 |
| ARCH-062-COMMERCE-001 | commerce | Complete | ARCH-061-COMMERCE-001 |
| ARCH-062-MCP-001 | mcp | Complete | ARCH-061-MCP-001 |
| ARCH-062-SYSTEM-TEST-001 | system-test | Pending | ARCH-062-SHOPIFY-001, ARCH-062-BACKGROUND-001, ARCH-062-COMMERCE-001, ARCH-062-MCP-001 |

## Architecture definition review
Inspected existing suffix checks and trusted session flow; official sources separate storefront from Admin identity. No new domain discovery or storage needed. Existing ARCH-061 adoption provides selected-shop snapshot. No unresolved architectural decision is delegated to implementation.

Dependency frontier — 2026-11-06: ARCH-062-BACKGROUND-001 is Ready/unclaimed following explicit completion of ARCH-061-BACKGROUND-001. Other task statuses remain unchanged.

Dependency frontier — 6 November 2026: ARCH-062-MCP-001 is Ready/unclaimed after canonical ARCH-061-MCP-001 completion `38b94f3cb`. No enabled task execution or deployment is authorized by this correction.

## MCP Completion / Current Dependency Frontier — 6 November 2026

MCP-001 Attempt 1 is explicitly developer-completed following passing scoped
review `a7e085a23`, implementation `d0a8de3`. Fetched published parent
records show Background Complete (`6d8c9d6ee`), Commerce Complete
(`1bcf42b25`), and Shopify Ready after Changes Requested (`d812181a6`).
These records supersede the older readiness summaries above; no sibling
lifecycle is changed here.

SYSTEM-TEST-001 remains Pending solely on Shopify completion. Terminal/manual
execution and cutover gates remain unchanged; no system run, deployment,
main merge, gitlink update or architecture-wide completion is implied.
