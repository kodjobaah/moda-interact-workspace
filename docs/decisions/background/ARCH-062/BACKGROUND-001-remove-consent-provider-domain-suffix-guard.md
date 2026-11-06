---
id: ARCH-062-BACKGROUND-001
architecture_id: ARCH-062
title: remove consent provider domain suffix guard
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on: ["ARCH-061-BACKGROUND-001"]
enables: ["ARCH-062-SYSTEM-TEST-001"]
created: 2026-11-05
updated: 2026-11-06
---
# Remove consent provider domain suffix guard

## Architecture
ARCH-062; docs/architecture/ARCH-062-remove-duplicated-shopify-domain-guards.md. Coordinator moda_architect.

## Objective
Remove consent provider domain suffix guard while binding credentials to existing verified installation endpoint.

## Context
Repeated suffix gates reject trusted shop flows and conflate storefront display with Admin identity. ARCH-061 provides selected Shop ID credential snapshot.

## Scope
moda-interact-background code and focused tests at verified touchpoints below.

| Existing file | Exact surface | Required change |
|---|---|---|
| moda-interact-background/src/providers/shopify-whatsapp-consent.provider.ts | SHOP_DOMAIN; consent provider admission near68 | Remove duplicated suffix guard; use authorized shop ID and coordinated snapshot endpoint; preserve exact origin binding, customer identity and consent semantics. |


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
- [x] Remove duplicated suffix guard; use authorized shop ID and coordinated snapshot endpoint; preserve exact origin binding, customer identity and consent semantics.
- [x] Create focused test file tests/unit/providers/shopify-whatsapp-consent-domain.test.ts and cover task-specific/common acceptance matrix.

## Interfaces / Contracts
Reuse published ARCH-061 Node-only provider getSession(selectedShopId), server-only snapshot.shop/accessToken/scope and existing selected-shop auth. Update owning local ports to thread trusted endpoint, no new Shared wire contract. SDK auth remains install authority; primaryDomain is never credential destination.

## Dependencies
- ARCH-061-BACKGROUND-001

## Enables
- ARCH-062-SYSTEM-TEST-001

## Acceptance Criteria
- [x] Custom storefront label with trusted installed session still executes consent read/update only on stored integration endpoint.
- [x] Foreign shop/session or overridden origin causes no consent provider call; permissions and customer scopes unchanged.

## Validation
- [x] Run `npx vitest run tests/unit/providers/shopify-whatsapp-consent-domain.test.ts` from owning repository; test file above is explicitly new if absent.
- [x] Run declared production build for application changes; App/Commerce/MCP also declared typecheck; Background uses its declared build; System Test uses npm run typecheck instead of build.
- [x] Verify no credentials reach override/custom/redirect origin, no provider secrets in errors/DTO/HTML/logs, and no unrelated domain checks removed.

## Stop Condition
Finish defined work/acceptance/validation, submit Completion Report and STOP. Explicit developer completion required; no automatic execution of enabled tasks.

## Implementation Notes
No implementation/claim from this definition. Use normal launcher isolated worktrees when requested. Existing paths verified; new test file explicitly named. Actual install integration domain remains SDK-established and selected-shop bound, not inferred by a new parser. Return demonstrated contract/schema incompatibility instead of widening scope.

## Completion Report

### Status

Complete — Developer explicitly completed Attempt 1 on 2026-11-06 after the durable accepted review.

### Files Changed

- `src/providers/shopify-whatsapp-consent.provider.ts`: remove the `.myshopify.com` admission regex; obtain the selected Shop's Shared session snapshot and construct the fixed Admin endpoint from `snapshot.shop`, enforcing exact HTTPS host/origin, no credentials or explicit port, fixed path, bounded request/response, and `redirect: "error"`.
- `src/services/shopify-session.service.ts`: expose Shared `getSession(shopId)` through a server-only local helper while retaining the existing token helper for other callers.
- `src/services/shopify-whatsapp-consent.service.ts`: call the consent reader with the already authorized Shop ID and customer GID; do not pass a display/storefront domain as a credential destination.
- `tests/unit/providers/shopify-whatsapp-consent-domain.test.ts`: add custom-storefront override, missing/foreign session, malformed stored endpoint, and redirect/error canary cases.
- Updated `tests/unit/providers/shopify-whatsapp-consent.provider.test.ts`, `tests/unit/services/shopify-whatsapp-consent.service.test.ts`, and `tests/unit/services/shopify-session.service.test.ts` for snapshot threading and unchanged consent/session behavior.

### Work Completed

- Removed the duplicate provider-owned `.myshopify.com` suffix regex from consent execution. The provider now uses the selected Shop ID to retrieve the ARCH-061 coordinated server-side snapshot and sends the access token only to the trusted endpoint from that same snapshot.
- Removed `shopDomain` from the consent-reader input and service call, preventing a storefront/display host or caller override from selecting the credential recipient.
- Preserved customer GID validation, consent query/state decoding, local authorization/write semantics, timeout/cancellation, and response-size bounds. The request remains a fixed POST to the fixed Admin GraphQL path with `redirect: "error"`.
- Added endpoint checks for exact HTTPS host/origin, no embedded credentials, no explicit port, and no path/query/fragment override. Malformed stored endpoint data fails closed before fetch.
- Retained the existing selected-shop/session association as the source of authorization; missing/foreign associations yield no Shopify request. No unrelated suffix/domain checks were removed.

### Validation Results

- `npx vitest run tests/unit/providers/shopify-whatsapp-consent-domain.test.ts` — 7 tests passed.
- `npx vitest run tests/unit/providers/shopify-whatsapp-consent-domain.test.ts tests/unit/providers/shopify-whatsapp-consent.provider.test.ts tests/unit/services/shopify-whatsapp-consent.service.test.ts tests/unit/services/shopify-session.service.test.ts` — 53 tests passed across 4 files.
- `npm run build` — passed, including Prisma Client generation and TypeScript compilation (exit 0).
- `git diff --check` — passed.
- Endpoint/credential evidence: tests assert the custom storefront override is absent from the request URL, only the stored snapshot host receives the selected Shop token, malformed hosts do not reach fetch, redirect handling is `error`, and returned failure results do not expose the token canary.
- Preparation evidence: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-062-BACKGROUND-001`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-062-BACKGROUND-001`; both branches `task/ARCH-062-BACKGROUND-001`. Dependency gate passed (`ARCH-061-BACKGROUND-001` Complete). Both worktrees reused; task remote fast-forward was not needed and `origin/main` was already incorporated. Recursive submodule preparation passed; `database` was initialized at `bd2d09066a8eb178a56f48fbbf88df637c411059`. The parent report-format correction is `eec74c0c4a3cba4953a376135252e02849b209c7`; durable Attempt 1 claim is `7271eafe6bdad14309ad8185c1017d2436862867`.

### Deviations

- The initial launcher run found the definition's Completion Report headings missing required blank-line spacing. Corrected and pushed the task-owned report formatting before the durable claim; no task scope or acceptance criterion changed.

### Assumptions

- ARCH-061 `getSession(selectedShopId)` returns the server-only snapshot from the same selected Shop/session association and includes the SDK-established integration endpoint and access token.

### Unresolved Issues

None identified within the bounded Background task.

### Architectural Concerns

None. No endpoint discovery, schema change, permission widening, custom-domain OAuth/Admin support, or sibling-repository changes were introduced.

### Developer Self-Review — Passed

Attempt 1 was checked against the full task definition and acceptance matrix. Required focused tests, related consent/session regressions, Background build, endpoint-origin controls and credential-redaction evidence passed. Completion mode is developer; the explicit completion decision is recorded below.

## Developer Completion Decision — 2026-11-06

The developer explicitly invoked `/moda_developer_update ARCH-062-BACKGROUND-001 complete`. Attempt 1 has the durable `Developer Self-Review Accepted` record; all required Work Items and Acceptance Criteria are checked; the implementation branch is committed, pushed, clean and aligned with `origin/task/ARCH-062-BACKGROUND-001` at `f04051270b4de36530c8efe325e7defe1bb51ec4`. No merge to `main` is required or performed.

Dependency-frontier reconciliation: `ARCH-062-SYSTEM-TEST-001` remains `pending` and manual-gated because its other explicit dependencies `ARCH-062-SHOPIFY-001`, `ARCH-062-COMMERCE-001`, and `ARCH-062-MCP-001` are each still `pending`. No downstream task was promoted by this completion.

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


## Architect Dependency Reconciliation — 2026-11-06

ARCH-061-BACKGROUND-001 Attempt 1 is explicitly developer-completed after passing review `6f522798a`, implementation `3fed264`. All explicit prerequisites are now Complete. Promoted from Pending to Ready; Attempt 0, executor null and claimed_at null remain unchanged. This is dependency eligibility only; normal preparation and explicit execution authorization remain required.

## Developer Self-Review Accepted — 2026-11-06

Attempt 1 passes the authorized developer-as-architect review. Status remains `review`, executor and claimed_at remain null, and Attempt 1 is unchanged. Explicit `/moda_developer_update ARCH-062-BACKGROUND-001 complete` is required before completion or downstream promotion. This section supersedes the definition-only Pending architect review above for the implementation reviewed here.

### Implementation and architecture assessment

Reviewed all seven changed files in implementation commit `f04051270b4de36530c8efe325e7defe1bb51ec4` against its parent. The local session service delegates getSession to the existing published Shared provider; the consent service forwards its already resolved Shop ID and customer GID. The consent provider removes the duplicated suffix gate and obtains token and integration host from one selected-shop snapshot. The fixed HTTPS Admin URL rejects userinfo, ports, path/query/fragment overrides and non-exact host/origin forms; redirects are refused. Existing customer identity checks, consent decoding and persistence authorization remain intact. No blocking implementation finding. No new alias mapping, endpoint discovery or Shared contract was introduced.

### Independent validation

- PASS: `npx vitest run tests/unit/providers/shopify-whatsapp-consent-domain.test.ts tests/unit/providers/shopify-whatsapp-consent.provider.test.ts tests/unit/services/shopify-whatsapp-consent.service.test.ts tests/unit/services/shopify-session.service.test.ts`: 4 files, 53 tests. Includes the required seven focused domain tests.
- PASS: `npm run build` (Prisma generation and TypeScript compilation, exit 0).
- PASS: `git diff --check`; implementation worktree clean, remote task branch verified at `f04051270b4de36530c8efe325e7defe1bb51ec4`.
- Validation used the canonical implementation worktree. Unit tests inject the session boundary: actual Shared database mapping/refresh behavior is inherited from ARCH-061 and was not re-proven by these tests. Redirect evidence verifies fetch redirect:error configuration and bounded failure handling; no live Shopify or cross-service system test was run.

### Worktree and publication evidence

Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`. Git worktree registrations independently verified parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-062-BACKGROUND-001` and implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-062-BACKGROUND-001`, each on `task/ARCH-062-BACKGROUND-001`. Parent fetched and fast-forward checked against its remote task branch (already current at `ab58964fbaf4b0a407e9ac7f50cc37ab5546d6dc`). Start-of-attempt synchronization/submodule preparation remains the reported evidence above; this review did not repeat or manufacture it. No shared checkout was switched, no implementation edits were made, and no gitlink was staged. The existing developer report supplies implementation assistance and validation history; this review adds independent validation rather than changing execution ownership.

The current parent task/review record is published by the commit containing this section on `origin/task/ARCH-062-BACKGROUND-001`. No merge to main, deployment, downstream claim or completion transition is performed.
