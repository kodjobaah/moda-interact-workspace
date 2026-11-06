---
id: ARCH-062-COMMERCE-001
architecture_id: ARCH-062
title: bind admin destinations to installed shop
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 50
executor: developer
claimed_at: 2026-11-06T13:22:57Z
attempt: 1
depends_on: ["ARCH-061-COMMERCE-001"]
enables: ["ARCH-062-SYSTEM-TEST-001"]
created: 2026-11-05
updated: 2026-11-06
---
# Bind admin destinations to installed shop

## Architecture
ARCH-062; docs/architecture/ARCH-062-remove-duplicated-shopify-domain-guards.md. Coordinator moda_architect.

## Objective
Bind admin destinations to installed shop while binding credentials to existing verified installation endpoint.

## Context
Repeated suffix gates reject trusted shop flows and conflate storefront display with Admin identity. ARCH-061 provides selected Shop ID credential snapshot.

## Scope
moda-interact-commerce code and focused tests at verified touchpoints below.

| Existing file | Exact surface | Required change |
|---|---|---|
| moda-interact-commerce/src/commerce/query/admin.ts | validShopDomain; createAdminQueryExecutionPort guard near194; AdminOfflineSessionPort | Replace suffix validation with selected-shop/snapshot binding; port accepts selected shop identity, supplies endpoint+token same snapshot. |
| moda-interact-commerce/src/commerce/preview/local-policy-providers.ts | createProductionAdminTransport guard near27 | Replace endsWith suffix guard with exact resolved trusted integration origin and fixed API path binding; retain https/method/redirect/deadline limits. |
| moda-interact-commerce/src/commerce/preview/local-provider-composition.ts | createStudioLocalProviderExecution | Thread authorized call.turn.shopId and current coordinated snapshot endpoint into query transport; display domain not credential host. |


## Out of Scope
Arbitrary custom-domain OAuth/Admin endpoints, DNS/alias discovery, schema, SDK internals, new credentials/configuration UI, billing Shopify-admin handle conversion and unrelated display-only formatting.

## Requirements
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

## Work Items
- [ ] Replace suffix validation with selected-shop/snapshot binding; port accepts selected shop identity, supplies endpoint+token same snapshot.
- [ ] Replace endsWith suffix guard with exact resolved trusted integration origin and fixed API path binding; retain https/method/redirect/deadline limits.
- [ ] Thread authorized call.turn.shopId and current coordinated snapshot endpoint into query transport; display domain not credential host.
- [ ] Create focused test file tests/shopify-admin-domain-boundary.test.ts and cover task-specific/common acceptance matrix.

## Interfaces / Contracts
Reuse published ARCH-061 Node-only provider getSession(selectedShopId), server-only snapshot.shop/accessToken/scope and existing selected-shop auth. Update owning local ports to thread trusted endpoint, no new Shared wire contract. SDK auth remains install authority; primaryDomain is never credential destination.

## Dependencies
- ARCH-061-COMMERCE-001

## Enables
- ARCH-062-SYSTEM-TEST-001

## Acceptance Criteria
- [ ] All existing Admin query AST/variable/body limits still apply after suffix check removal.
- [ ] Custom storefront display never becomes fetch host; exact trusted endpoint succeeds and mismatch rejects before network.
- [ ] External/Woo transports and metadata-only Connections remain unchanged.

## Validation
- [ ] Run `npx vitest run tests/shopify-admin-domain-boundary.test.ts` from owning repository; test file above is explicitly new if absent.
- [ ] Run declared production build for application changes; App/Commerce/MCP also declared typecheck; Background uses its declared build; System Test uses npm run typecheck instead of build.
- [ ] Verify no credentials reach override/custom/redirect origin, no provider secrets in errors/DTO/HTML/logs, and no unrelated domain checks removed.

## Stop Condition
Finish defined work/acceptance/validation, submit Completion Report and STOP. Explicit developer completion required; no automatic execution of enabled tasks.

## Implementation Notes
No implementation/claim from this definition. Use normal launcher isolated worktrees when requested. Existing paths verified; new test file explicitly named. Actual install integration domain remains SDK-established and selected-shop bound, not inferred by a new parser. Return demonstrated contract/schema incompatibility instead of widening scope.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-11-06T13:22:57Z. Attempt 0 review history is preserved below.

### Files Changed
None
### Work Completed
None
### Validation Results
Definition only; runtime tests not run.
### Deviations
None
### Assumptions
ARCH-061 prerequisite provides selected-shop snapshot with trusted endpoint.
### Unresolved Issues
None blocking definition.
### Architectural Concerns
No new endpoint discovery, schema or permission widening authorized.

## Architect Review
### Review Status
Pending
### Review Notes
Definition reviewed against existing suffix checks and official storefront/Admin identity distinction; no implementation reviewed.
### Reviewed Files
Touchpoint table above.
### Validation Reviewed
Definition metadata/path validation only.
### Architecture Conformance
Task is repository-owned and gated by its ARCH-061 adoption prerequisite.
### Follow-up
None

## Dependency frontier reconciliation — 2026-11-06
Architect coordination only: the explicit ARCH-061 prerequisite is Complete with a durable developer completion decision in its canonical task record. Promoted Pending -> Ready; executor/claimed_at remain null and attempt remains 0. No execution, acceptance or completion decision occurred.
