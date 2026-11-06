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
attempt: 2
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

Developer Self-Review Passed / Accepted — Attempt 2, 2026-11-06. Both prior findings are resolved. Status remains Review pending explicit developer completion.

### Files Changed

- `app/services/shop/shop.service.ts`: bounded nonempty provider identity, compared with the SDK-authenticated `session.shop`; Shop GID validation is unchanged.
- `app/services/shop/merchant-request-context.server.ts` and `app/routes/auth/catchall/route.jsx`: name and pass the authenticated SDK shop identity explicitly.
- `app/routes/public/home/route.jsx` and `app/routes/auth/login/error.server.jsx`: remove the app-owned suffix parser, preserve the platform launch query handoff, delegate installation validation to Shopify SDK login/auth, and provide Shopify installation guidance on rejection.
- `app/services/merchant-knowledge/upload.server.ts` and `app/routes/app/merchant-knowledge/upload-intent/route.ts`: remove domain admission and domain-derived object-key namespace; use the already-authorized selected Shop ID for the server-generated signed-upload key.
- `tests/unit/shopify-domain-boundary.test.ts`, `tests/unit/services/shop.service.test.ts`, `tests/unit/routes/public-home-route.test.ts`, `tests/unit/merchant-knowledge-upload.test.ts`, `tests/integration/merchant-knowledge-upload.integration.test.ts`, `tests/integration/merchant-knowledge-finalization.postgres.test.ts`, and `tests/integration/merchant-shop-bootstrap.postgres.test.ts`: add/update identity, no-discovery, selected-Shop ownership, key and caller coverage.
- `tests/unit/routes/auth-catchall.test.ts` and `tests/unit/merchant-knowledge-actions.test.ts`: Attempt 2 updates the two stale assertions to the `sessionShop` and selected-Shop-ID-only caller contracts.

### Work Completed

- Authenticated profile provider identity now accepts a bounded provider-owned value and must equal the SDK-authenticated session shop before any local tenant read/write. Shop GID checks remain intact.
- Public installation no longer classifies shop input with an app-owned suffix regex. Shopify launch parameters are preserved through the existing app handoff; direct custom storefront input receives Shopify installation guidance without lookup, DNS discovery, or profile probes. SDK `InvalidShop` rejection uses the same guidance.
- Upload-intent authorization still resolves the selected owned Shop through `settingsMutationAccess`; request bodies cannot supply `shopId` or `shopDomain`. The service uses that trusted ID to namespace the server-generated object key, then preserves the existing ownership, file, expiry, and signed PUT checks.
- Focused acceptance coverage verifies a custom storefront with matching SDK integration identity, mismatch rejection before local access, no public custom-domain discovery, Shopify SDK guidance, selected-Shop-bound upload, and rejection of a foreign Shop ID/domain override.
- Attempt 2 addressed both P2 review findings: the auth catchall test now asserts that `session.shop` is passed as `sessionShop`; the merchant knowledge action test now expects only the authenticated selected Shop ID and allowed upload fields. Its existing malicious `shopId`/`shopDomain` request rejection coverage remains in place.

### Validation Results

- `npx vitest run tests/unit/shopify-domain-boundary.test.ts` — 1 test file passed; 4 tests passed.
- `npx vitest run tests/unit/shopify-domain-boundary.test.ts tests/unit/services/shop.service.test.ts tests/unit/merchant-knowledge-upload.test.ts tests/unit/routes/public-home-route.test.ts` — 4 test files passed; 65 tests passed.
- `npm run build` — passed (Prisma client generation, client build, and server build). Existing upstream Rollup comment/chunk-size and Prisma browser-import warnings remain non-fatal.
- `npm run typecheck` — passed.
- `git diff --check` — passed. Touchpoint review confirms suffix guards were removed only from the three task-owned boundaries; unrelated display/provider-domain handling was not changed. Upload DTOs and diagnostics contain neither user-supplied domain nor Shopify credential values.
- Attempt 2 focused selection `npx vitest run tests/unit/shopify-domain-boundary.test.ts tests/unit/services/shop.service.test.ts tests/unit/merchant-knowledge-upload.test.ts tests/unit/routes/public-home-route.test.ts` — 4 files passed; 65 tests passed.
- Attempt 2 caller selection `npx vitest run tests/unit/merchant-request-context.test.ts tests/unit/routes/auth-catchall.test.ts tests/unit/merchant-knowledge-actions.test.ts` — 3 files passed; 31 tests passed. This includes the two caller tests that failed review.
- Attempt 2 `npm run typecheck` — passed. The production source is unchanged in Attempt 2, so the successful Attempt 1 `npm run build` remains the applicable build evidence; no PostgreSQL run was required by declared validation or requested by the review.
- Attempt 2 `git diff --check` — passed.

### Deviations

Upload storage namespace now uses the trusted selected Shop ID instead of a domain. This removes storefront-domain shape from tenant admission and key selection while preserving each persisted asset's explicit object key and existing signed-upload semantics. No schema or external contract changed.

### Assumptions

ARCH-061 prerequisite provides selected-shop snapshot with trusted endpoint.

### Unresolved Issues

None known for architect review. Both Attempt 1 caller-test findings are corrected and the requested affected-caller selection passes. No PostgreSQL container scenario was required by this task's declared validation.

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
  Attempt 1: parent remote task branch fast-forwarded: yes; architect readiness reconciliation and report-format fix were present before the claim
  Attempt 1: parent origin/main incorporated: already-current
  Attempt 1: implementation remote task branch fast-forwarded: not-needed; launcher started from current origin/main
  Attempt 1: implementation origin/main incorporated: already-current
  Attempt 2: parent remote task branch fast-forwarded: not-needed; origin/main incorporated: already-current
  Attempt 2: implementation remote task branch fast-forwarded: not-needed; origin/main incorporated: already-current
  Attempt 2 recursive submodules: sync --recursive passed; update --init --recursive passed; `database` at `bd2d09066a8eb178a56f48fbbf88df637c411059`

Implementation repository:
  repository: `moda-interact`
  Attempt 1 commit: `3a5c920b4217f09dd8a958dacb6cae13971237bc`
  Attempt 2 commit: `249de4e130117d85a86763de3abc4c71b36e9996`
  remote branch: `origin/task/ARCH-062-SHOPIFY-001`
  pushed: yes

Parent workspace:
  task file: `docs/decisions/shopify/ARCH-062/SHOPIFY-001-remove-duplicated-app-shop-domain-guards.md`
  Attempt 1 report commit: `4168d87f1` (report and review transition; evidence amendment in `be3833f0a`)
  Attempt 2 claim commit: `0597d8ea717293bfe03893f0400be69dd0446543`
  Attempt 2 review report commit: `2eea08576` (publication evidence finalized in the following parent report commit)
  remote branch: `origin/task/ARCH-062-SHOPIFY-001`
  pushed: yes; Attempt 2 report and VCS evidence are published on `origin/task/ARCH-062-SHOPIFY-001`
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

### Developer Self-Review - Passed — Attempt 1 (superseded by architect review)

Attempt: 1
Scope: reviewed all task Work Items, Acceptance Criteria, and declared validation against the implementation diff and test results above.
Decision: implementation passes developer self-review and is submitted for `moda_architect` review. No architect acceptance decision has been made. Because `completion_mode` is `developer`, explicit developer completion remains pending.

### Developer Self-Review - Passed — Attempt 2

Attempt: 2
Finding: both stale caller assertions identified in the Attempt 1 Architect Review now match the implementation's authenticated session and selected-Shop-ID-only contracts.
Validation: all 65 focused tests and all 31 tests in the affected caller selection pass; `npm run typecheck` and `git diff --check` pass. Attempt 1 production build remains applicable because Attempt 2 changes tests only.
Decision: the required corrections pass developer self-review and are resubmitted for `moda_architect` review. No architect acceptance decision has been made. Because `completion_mode` is `developer`, explicit developer completion remains pending.

## Architect Review
### Review Status
Passed / Accepted — Attempt 2 (2026-11-06); explicit developer completion pending.
### Review Notes
Both Attempt 1 caller-test findings are resolved by exact argument assertions: SDK-authenticated `sessionShop` is passed to the Shop service, and upload intent uses the authenticated selected Shop ID without the removed domain field. No production behavior changed in this correction.
### Reviewed Files
Attempt 2 diff `3a5c920..249de4e`: `tests/unit/routes/auth-catchall.test.ts` and `tests/unit/merchant-knowledge-actions.test.ts`, plus updated task/report evidence. The prior implementation review remains applicable to unchanged production source.
### Validation Reviewed
Independent combined focused/caller selection: 96 tests in 7 files passed, exit 0. Implementation diff whitespace check passed. Attempt 2 typecheck success is developer-reported; independently passing Attempt 1 typecheck and developer-reported production build remain applicable to unchanged application source. No container/integration run was required or performed in this review.
### Architecture Conformance
Previous review found no production identity/destination defect. The corrections retain precise authenticated identity assertions and do not restore suffix guards or permit request-supplied credential destinations. All requested corrections are resolved; no known required task-owned item remains incomplete.
### Follow-up
Explicit `/moda_developer_update ARCH-062-SHOPIFY-001 complete` is required. No downstream promotion occurs before that decision.

## Dependency frontier reconciliation — 2026-11-06
Architect coordination only: the explicit ARCH-061 prerequisite is Complete with a durable developer completion decision in its canonical task record. Promoted Pending -> Ready; executor/claimed_at remain null and attempt remains 0. No execution, acceptance or completion decision occurred.


## Developer Self-Review - Changes Requested — Attempt 1 (2026-11-06)

### Finding and required correction

[P2] Update existing regression coverage for the changed caller contracts. `tests/unit/routes/auth-catchall.test.ts:43` still asserts `resolveShopifyShop({admin, domain})` although the route now supplies `{admin, sessionShop: session.shop}`. `tests/unit/merchant-knowledge-actions.test.ts:193` still expects `shopDomain` although the upload action now supplies only the authenticated Shop ID and permitted upload fields. Both fail on the reviewed task source. Assert the new exact arguments and retain the protections that identity comes from SDK authentication and cannot be overridden by request input; do not restore domain admission or weaken assertions to make tests pass.

Rerun the declared four-file focused selection plus `tests/unit/merchant-request-context.test.ts`, `tests/unit/routes/auth-catchall.test.ts`, and `tests/unit/merchant-knowledge-actions.test.ts`; record passing results and updated build/typecheck evidence as appropriate to the correction. Update the Completion Report to cover these caller regressions. No implementation correction was made during this review.

### Evidence and disposition

- Reviewed implementation `3a5c920b4217f09dd8a958dacb6cae13971237bc`, baseline `f14509f`; implementation and parent canonical worktrees are clean and on `task/ARCH-062-SHOPIFY-001`. Live remote source matched that implementation commit; parent pre-review HEAD matched live remote `be3833f0ad7da8ede467bb882aa1a84efb5d4a7f`.
- Launcher-resolved physical paths verified: parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-062-SHOPIFY-001`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-062-SHOPIFY-001`. Recorded preparation/synchronization evidence remains in the report. No shared/default checkout was switched or reused for implementation/review.
- Independent command `node node_modules/vitest/vitest.mjs run tests/unit/shopify-domain-boundary.test.ts tests/unit/services/shop.service.test.ts tests/unit/merchant-knowledge-upload.test.ts tests/unit/routes/public-home-route.test.ts`: 65 passed in 4 files, exit 0 (`/tmp/arch062-shopify-review-unit.log`).
- Independent command `node node_modules/vitest/vitest.mjs run tests/unit/merchant-request-context.test.ts tests/unit/routes/auth-catchall.test.ts tests/unit/merchant-knowledge-actions.test.ts`: 29 passed, 2 failed in 3 files, exit 1 (`/tmp/arch062-shopify-review-callers.log`). Both failures are the concrete contract mismatches above.
- Independent `npm run typecheck`: passed, exit 0 (`/tmp/arch062-shopify-review-typecheck.log`). `git diff --check HEAD^`: passed. Node 24.19.0 used in the canonical implementation worktree. No independent production build or container tests were run; existing report build evidence remains developer-reported.
- Decision: Ready, executor null, claimed_at null, Attempt 1 unchanged; completion remains developer-controlled. This supersedes the earlier developer self-review pass for acceptance purposes. No new attempt is created, downstream task is promoted, main is merged, gitlink is staged or deployment is performed.


## Developer Self-Review Passed / Accepted — Attempt 2 (2026-11-06)

- Decision: accept Attempt 2; retain Review, executor null, claimed_at null and attempt 2 unchanged. Explicit developer completion remains pending. This passing review supersedes the Attempt 1 Changes Requested disposition while preserving that history.
- Source: `249de4e130117d85a86763de3abc4c71b36e9996`, verified equal to the live remote implementation task branch, clean canonical worktree. The only changes since previously reviewed `3a5c920` are the two requested caller assertions and a final newline. No production source changed.
- Parent: pre-review `7554a4255f9430e03581de38d0dd6def892a7223`, verified equal to the live published task branch, with a clean canonical parent worktree. Both remain on `task/ARCH-062-SHOPIFY-001`. Physical isolation and synchronization evidence is recorded above; no shared checkout was switched and no unrelated task worktree was reused.
- Independent validation: `node node_modules/vitest/vitest.mjs run tests/unit/shopify-domain-boundary.test.ts tests/unit/services/shop.service.test.ts tests/unit/merchant-knowledge-upload.test.ts tests/unit/routes/public-home-route.test.ts tests/unit/merchant-request-context.test.ts tests/unit/routes/auth-catchall.test.ts tests/unit/merchant-knowledge-actions.test.ts` passed all 96 tests in 7 files, exit 0, using Node 24.19.0 in the canonical implementation worktree (`/tmp/arch062-shopify-attempt2-review.log`). `git diff --check 3a5c920 HEAD` passed in that implementation worktree.
- Validation scope: reviewed reported Attempt 2 typecheck pass. Production source is unchanged, so the prior independent typecheck and submitted successful build remain applicable. No independent build/typecheck rerun or PostgreSQL scenario is claimed for this review.
- Publication: this review updates only the current task record on the parent task branch. No main merge, gitlink staging, deployment, claim, attempt increment or downstream execution/promotion occurs. No material assigned-agent assistance was newly reported for this correction.
