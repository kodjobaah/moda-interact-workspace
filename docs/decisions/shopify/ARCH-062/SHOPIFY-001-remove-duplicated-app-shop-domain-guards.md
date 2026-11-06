---
id: ARCH-062-SHOPIFY-001
architecture_id: ARCH-062
title: remove duplicated app shop domain guards
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on: ["ARCH-061-SHOPIFY-001"]
enables: ["ARCH-062-SYSTEM-TEST-001"]
created: 2026-11-05
updated: 2026-11-06
---
# Remove duplicated app shop domain guards

## Architecture
ARCH-062; docs/architecture/ARCH-062-remove-duplicated-shopify-domain-guards.md. Coordinator moda_architect.

## Objective
Remove duplicated app shop domain guards while binding credentials to existing verified installation endpoint.

## Context
Repeated suffix gates reject trusted shop flows and conflate storefront display with Admin identity. ARCH-061 provides selected Shop ID credential snapshot.

## Scope
moda-interact code and focused tests at verified touchpoints below.

| Existing file | Exact surface | Required change |
|---|---|---|
| moda-interact/app/services/shop/shop.service.ts | profileSchema.myshopifyDomain; authenticated profile equality near203 | Drop suffix regex; retain bounded provider string shape and compare provider identity to SDK session.shop, never storefront input. Preserve Shop GID checks. |
| moda-interact/app/routes/public/home/route.jsx | MYSHOPIFY_DOMAIN parser and installation form/copy | Remove duplicate suffix admission; delegate to existing SDK auth, preserve safe return URL; unknown custom domain gets Shopify launch guidance, no discovery. |
| moda-interact/app/services/merchant-knowledge/upload.server.ts | domain guard near119 | Remove regex as tenant admission; derive trusted selected shop/session identity through existing authenticated context, preserve signed upload/ownership constraints. |


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
- [x] Drop suffix regex; retain bounded provider string shape and compare provider identity to SDK session.shop, never storefront input. Preserve Shop GID checks.
- [x] Remove duplicate suffix admission; delegate to existing SDK auth, preserve safe return URL; unknown custom domain gets Shopify launch guidance, no discovery.
- [x] Remove regex as tenant admission; derive trusted selected shop/session identity through existing authenticated context, preserve signed upload/ownership constraints.
- [x] Create focused test file tests/unit/shopify-domain-boundary.test.ts and cover task-specific/common acceptance matrix.

## Interfaces / Contracts
Reuse published ARCH-061 Node-only provider getSession(selectedShopId), server-only snapshot.shop/accessToken/scope and existing selected-shop auth. Update owning local ports to thread trusted endpoint, no new Shared wire contract. SDK auth remains install authority; primaryDomain is never credential destination.

## Dependencies
- ARCH-061-SHOPIFY-001

## Enables
- ARCH-062-SYSTEM-TEST-001

## Acceptance Criteria
- [x] Provider profile custom primaryDomain with authentic integration identity passes; mismatched SDK identity rejects.
- [x] Public custom-storefront input performs no credentialed network or DNS alias resolution and shows SDK installation guidance on rejection.
- [x] Authorized upload passes with trusted association; foreign selected-shop input denied independent of domain shape.

## Validation
- [x] Run `npx vitest run tests/unit/shopify-domain-boundary.test.ts` from owning repository; test file above is explicitly new if absent.
- [x] Run declared production build for application changes; App/Commerce/MCP also declared typecheck; Background uses its declared build; System Test uses npm run typecheck instead of build.
- [x] Verify no credentials reach override/custom/redirect origin, no provider secrets in errors/DTO/HTML/logs, and no unrelated domain checks removed.

## Stop Condition
Finish defined work/acceptance/validation, submit Completion Report and STOP. Explicit developer completion required; no automatic execution of enabled tasks.

## Implementation Notes
No implementation/claim from this definition. Use normal launcher isolated worktrees when requested. Existing paths verified; new test file explicitly named. Actual install integration domain remains SDK-established and selected-shop bound, not inferred by a new parser. Return demonstrated contract/schema incompatibility instead of widening scope.

## Completion Report

### Status

Ready for Architect Review — Attempt 1. Developer self-review passed; developer completion remains pending architect acceptance and an explicit developer completion decision. Attempt 0 review history is preserved below.

### Files Changed

- `app/services/shop/shop.service.ts`: bounded nonempty provider identity, compared with the SDK-authenticated `session.shop`; Shop GID validation is unchanged.
- `app/services/shop/merchant-request-context.server.ts` and `app/routes/auth/catchall/route.jsx`: name and pass the authenticated SDK shop identity explicitly.
- `app/routes/public/home/route.jsx` and `app/routes/auth/login/error.server.jsx`: remove the app-owned suffix parser, preserve the platform launch query handoff, delegate installation validation to Shopify SDK login/auth, and provide Shopify installation guidance on rejection.
- `app/services/merchant-knowledge/upload.server.ts` and `app/routes/app/merchant-knowledge/upload-intent/route.ts`: remove domain admission and domain-derived object-key namespace; use the already-authorized selected Shop ID for the server-generated signed-upload key.
- `tests/unit/shopify-domain-boundary.test.ts`, `tests/unit/services/shop.service.test.ts`, `tests/unit/routes/public-home-route.test.ts`, `tests/unit/merchant-knowledge-upload.test.ts`, `tests/integration/merchant-knowledge-upload.integration.test.ts`, `tests/integration/merchant-knowledge-finalization.postgres.test.ts`, and `tests/integration/merchant-shop-bootstrap.postgres.test.ts`: add/update identity, no-discovery, selected-Shop ownership, key and caller coverage.

### Work Completed

- Authenticated profile provider identity now accepts a bounded provider-owned value and must equal the SDK-authenticated session shop before any local tenant read/write. Shop GID checks remain intact.
- Public installation no longer classifies shop input with an app-owned suffix regex. Shopify launch parameters are preserved through the existing app handoff; direct custom storefront input receives Shopify installation guidance without lookup, DNS discovery, or profile probes. SDK `InvalidShop` rejection uses the same guidance.
- Upload-intent authorization still resolves the selected owned Shop through `settingsMutationAccess`; request bodies cannot supply `shopId` or `shopDomain`. The service uses that trusted ID to namespace the server-generated object key, then preserves the existing ownership, file, expiry, and signed PUT checks.
- Focused acceptance coverage verifies a custom storefront with matching SDK integration identity, mismatch rejection before local access, no public custom-domain discovery, Shopify SDK guidance, selected-Shop-bound upload, and rejection of a foreign Shop ID/domain override.

### Validation Results

- `npx vitest run tests/unit/shopify-domain-boundary.test.ts` — 1 test file passed; 4 tests passed.
- `npx vitest run tests/unit/shopify-domain-boundary.test.ts tests/unit/services/shop.service.test.ts tests/unit/merchant-knowledge-upload.test.ts tests/unit/routes/public-home-route.test.ts` — 4 test files passed; 65 tests passed.
- `npm run build` — passed (Prisma client generation, client build, and server build). Existing upstream Rollup comment/chunk-size and Prisma browser-import warnings remain non-fatal.
- `npm run typecheck` — passed.
- `git diff --check` — passed. Touchpoint review confirms suffix guards were removed only from the three task-owned boundaries; unrelated display/provider-domain handling was not changed. Upload DTOs and diagnostics contain neither user-supplied domain nor Shopify credential values.

### Deviations

Upload storage namespace now uses the trusted selected Shop ID instead of a domain. This removes storefront-domain shape from tenant admission and key selection while preserving each persisted asset's explicit object key and existing signed-upload semantics. No schema or external contract changed.

### Assumptions

ARCH-061 prerequisite provides selected-shop snapshot with trusted endpoint.

### Unresolved Issues

None known for developer review. No PostgreSQL container scenario was required by this task's declared validation.

### Architectural Concerns

No new endpoint discovery, schema, credential destination, or permission widening was introduced. Existing Shopify SDK install/auth validation remains authoritative; custom storefront hosts are never used as Admin credential destinations.

### Git / VCS

Task branch: `task/ARCH-062-SHOPIFY-001`

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-062-SHOPIFY-001`
  parent branch: `task/ARCH-062-SHOPIFY-001`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-062-SHOPIFY-001`
  implementation branch: `task/ARCH-062-SHOPIFY-001`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes; architect readiness reconciliation and report-format fix were present before the claim
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed; launcher started from current origin/main
  implementation origin/main incorporated: already-current

Implementation repository:
  repository: `moda-interact`
  commit: `3a5c920b4217f09dd8a958dacb6cae13971237bc`
  remote branch: `origin/task/ARCH-062-SHOPIFY-001`
  pushed: yes

Parent workspace:
  task file: `docs/decisions/shopify/ARCH-062/SHOPIFY-001-remove-duplicated-app-shop-domain-guards.md`
  commit: pending report commit
  remote branch: `origin/task/ARCH-062-SHOPIFY-001`
  pushed: pending
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

### Developer Self-Review - Passed

Attempt: 1
Scope: reviewed all task Work Items, Acceptance Criteria, and declared validation against the implementation diff and test results above.
Decision: implementation passes developer self-review and is submitted for `moda_architect` review. No architect acceptance decision has been made. Because `completion_mode` is `developer`, explicit developer completion remains pending.

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
