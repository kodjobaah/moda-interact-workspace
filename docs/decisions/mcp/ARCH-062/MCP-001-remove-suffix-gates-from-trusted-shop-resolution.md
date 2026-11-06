---
id: ARCH-062-MCP-001
architecture_id: ARCH-062
title: remove suffix gates from trusted shop resolution
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on: ["ARCH-061-MCP-001"]
enables: ["ARCH-062-SYSTEM-TEST-001"]
created: 2026-11-05
updated: 2026-11-06
---
# Remove suffix gates from trusted shop resolution

## Architecture
ARCH-062; docs/architecture/ARCH-062-remove-duplicated-shopify-domain-guards.md. Coordinator moda_architect.

## Objective
Remove suffix gates from trusted shop resolution while binding credentials to existing verified installation endpoint.

## Context
Repeated suffix gates reject trusted shop flows and conflate storefront display with Admin identity. ARCH-061 provides selected Shop ID credential snapshot.

## Scope
moda-interact-mcp code and focused tests at verified touchpoints below.

| Existing file | Exact surface | Required change |
|---|---|---|
| moda-interact-mcp/src/capabilities/resolve.ts | requireActiveShop Shopify branch | Remove Shopify suffix admission; preserve selected ID/platform/status and existing Woo installation checks. |
| moda-interact-mcp/src/connections/resolver.ts | SHOPIFY_DOMAIN; verifiedShop | Resolve trusted selected-shop connection without suffix gate; require installed snapshot binding before provider execution. |
| moda-interact-mcp/src/connections/shopify/provider.ts | DOMAIN; provider request admission near297 | Use actual coordinated Session.shop endpoint from selected Shop identity; preserve exact origin/https/fixed operation path and all authorization checks. |
| moda-interact-mcp/src/connections/shopify/session-reader.ts | ShopifyOfflineSessionReader.read | Carry trusted shopId and snapshot endpoint through local reader result, no caller URL/domain as authority. |


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
- [x] Remove Shopify suffix admission; preserve selected ID/platform/status and existing Woo installation checks.
- [x] Resolve trusted selected-shop connection without suffix gate; require installed snapshot binding before provider execution.
- [x] Use actual coordinated Session.shop endpoint from selected Shop identity; preserve exact origin/https/fixed operation path and all authorization checks.
- [x] Carry trusted shopId and snapshot endpoint through local reader result, no caller URL/domain as authority.
- [x] Create focused test file tests/unit/connections/shopify-domain-boundary.test.ts and cover task-specific/common acceptance matrix.

## Interfaces / Contracts
Reuse published ARCH-061 Node-only provider getSession(selectedShopId), server-only snapshot.shop/accessToken/scope and existing selected-shop auth. Update owning local ports to thread trusted endpoint, no new Shared wire contract. SDK auth remains install authority; primaryDomain is never credential destination.

## Dependencies
- ARCH-061-MCP-001

## Enables
- ARCH-062-SYSTEM-TEST-001

## Acceptance Criteria
- [x] Selected owned custom-storefront shop reaches published tools with legitimate installed snapshot.
- [x] Missing/foreign integration, request endpoint mismatch or inactive shop still fails before provider call.
- [x] No arbitrary custom domain gets token and no cross-shop snapshot can authorize a tool.

## Validation
- [x] Run `npx tsx --test tests/unit/connections/shopify-domain-boundary.test.ts` from owning repository; test file above is explicitly new if absent.
- [x] Run declared production build for application changes; App/Commerce/MCP also declared typecheck; Background uses its declared build; System Test uses npm run typecheck instead of build.
- [x] Verify no credentials reach override/custom/redirect origin, no provider secrets in errors/DTO/HTML/logs, and no unrelated domain checks removed.

## Stop Condition
Finish defined work/acceptance/validation, submit Completion Report and STOP. Explicit developer completion required; no automatic execution of enabled tasks.

## Implementation Notes
Attempt 1 implements the selected-shop snapshot boundary in the launcher-resolved MCP worktree. Actual installation identity remains established by the credential owner/SDK; no alias discovery, schema change or new suffix validator was introduced.

## Completion Report

### Status

Complete — Attempt 1, explicitly completed by the developer on 6 November 2026 following accepted review `a7e085a23`. Executor/claimed_at remain null and attempt is unchanged. Implementation commit `d0a8de3` is pushed to MCP `task/ARCH-062-MCP-001`; this report is published on the matching parent task branch under explicit developer authorization. The scoped passing review and explicit completion decision are recorded below.

### Files Changed

- `src/capabilities/resolve.ts`: remove Shopify suffix admission; preserve selected ID, active status, platform and bounded nonempty metadata; Woo checks unchanged.
- `src/connections/resolver.ts`, `ports.ts`: remove the Shopify suffix constant and remove domain from the private provider input. Provider execution receives the trusted selected Shop ID.
- `src/connections/shopify/session-reader.ts`: selected-ID-only read; return the server-only `Pick<OfflineCredentialSnapshot, "shopId" | "shop" | "accessToken" | "scope">` from one committed Shared result. Keep identity, token, scope, error-privacy and signal checks.
- `src/connections/shopify/provider.ts`: remove suffix admission and bind the fixed versioned GraphQL POST URL to that same snapshot's endpoint/Shop ID. Validate exact HTTPS host/origin, no credentials/port, fixed path, no query/hash, no redirect; retain read-only query checks, scope-positive preflight, version/response bounds and cancellation.
- NEW `tests/unit/connections/shopify-domain-boundary.test.ts`: actual handler/registry/resolver/reader/provider boundary tests.
- Updated resolver, reader, provider, coordination and product-search composition fixtures to carry the snapshot endpoint/identity rather than a caller domain.
- `README.md`: document endpoint authority and retained mapping/rollout boundary.

### Work Completed

1. Removed only the three task-identified suffix gates. Metadata discovery does not acquire or refresh credentials. Existing tenant/platform/status, plan/Feature and Woo installation/origin checks remain.
2. Removed caller/display domain from the local credential-reader and Shopify provider ports. The transport uses the endpoint, token, permission scope and selected Shop identity from the same Shared snapshot. There is no browser Host, URL, opaque context or tool-argument authority over credential destination.
3. Added transport destination binding using URL structural equality, not a replacement suffix admission policy. Malformed endpoint components, alternate response origins and redirects fail closed; the fixed Admin API version/path/method and read-only operation constraints remain.
4. Kept the published Shared 5.2.0 provider, existing integration mapping, lock identity, refresh recovery and configuration unchanged. A Shared mapping probe proves that a stored Shop.domain/Session.shop mismatch cannot cause alias guessing, OAuth/config reads or provider IO.
5. New tests execute an eligible published tool through the real MCP HTTP handler and registry with custom storefront metadata and an injected legitimate installation snapshot. They cover request overrides, missing/foreign/inactive/wrong-provider shops, missing/conflicting credentials, foreign snapshots, malformed endpoints, redirects, response-origin mismatch, secret canaries and Feature revocation.
6. Codex acting as moda_mcp provided the explicitly requested source, test, documentation and validation assistance. Developer execution/completion ownership remains unchanged.

### Validation Results

All repository commands ran in `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-062-MCP-001` with Node 24.19.0 / npm 11.17.0 recovered through the canonical workspace bootstrap.

| Command | Result |
|---|---|
| `npm ci --ignore-scripts` | Locked dependencies installed; no package/lockfile changes. |
| `npx tsx --test tests/unit/connections/shopify-domain-boundary.test.ts` | 26 passed, 0 failed/skipped, exit 0. |
| `npm run test:unit` | 400 passed, 0 failed/skipped, exit 0; includes all new boundary and affected connection/policy/Woo tests. |
| `npm run typecheck` | Passed, exit 0. |
| `npm run build` | Passed, exit 0. |
| `npm run lint` | Passed, exit 0. |
| `git -c core.fsmonitor=false diff --check` | Passed. |
| Scoped source inspection | No Shopify suffix regex/DOMAIN gate remains in capabilities/connections. Woo implementation validation branches and unrelated domain checks were not removed. |

The prior adapter's scope-only expected shape was updated to include the newly threaded shop identity/endpoint; the final 400-test pass includes that correction. The required new 26-test command passed independently.

Pinned schema setup used `npm run schema:install:shopify -- /Users/kwadwoadomafriyie/project/moda-interact-workspace/moda-interact-commerce/lib/discovery/artifacts/admin-2026-07.json`; the installer verified the existing canonical SHA-256. No schema download/substitution or sibling source edit.

Evidence: `/tmp/arch062-mcp-domain.log`, `/tmp/arch062-mcp-unit.log`, `/tmp/arch062-mcp-typecheck-final.log`, `/tmp/arch062-mcp-build.log`, `/tmp/arch062-mcp-lint.log`, `/tmp/arch062-mcp-schema.log`. These are local temporary receipts; the exact commands and outcomes are preserved here.

### Worktree and Preparation Evidence

- Canonical primary workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-062-MCP-001`, reused.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-062-MCP-001`, newly created, base `bdd69ca353fac6d84b86060c4715b4d187581e58` already contains the accepted ARCH-061 adoption.
- Both branches: `task/ARCH-062-MCP-001`. Neither shared checkout was switched/mutated for source work; no other task worktree reused.
- Both remote task branch fast-forwards: not-needed; both origin/main incorporation results: already-current.
- Recursive submodule sync/update/verification: passed; `database` at `bd2d09066a8eb178a56f48fbbf88df637c411059`.
- Launcher dependency gate passed: ARCH-061-MCP-001 Complete.
- Readiness correction `1f192a7b5` reconciled that completed canonical prerequisite and normalized report heading spacing before preparation. It changed no requirements, execution/completion mode or attempt.
- Durable developer claim `e801cc057ff4f63dd401956f8cadca6eda82d831`, pushed; Attempt 1 at `2026-11-06T13:14:21Z`.

### Deviations

None. Reused the published Shared snapshot type in a private local port; no new Shared wire contract, schema, validator, alias mapping or service was introduced.

### Assumptions / Evidence Boundary

The positive custom-storefront test supplies an already trusted SDK-established snapshot through the credential-owner seam. It does not invent or prove a persisted alias between a custom Shop.domain and a different Session.shop. The separate negative test uses the actual published Shared provider with an injected database to prove that missing association fails closed without network. No new PostgreSQL, Docker, live Shopify, App SDK/install or integrated cross-service run was performed for this task; those are not claimed by these unit proofs.

Official Shopify [Shop 2026-07 reference](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/Shop) retains separate myshopifyDomain and primaryDomain fields. Runtime authority remains the accepted installation snapshot, not recognition of a domain string.

### Unresolved Issues

No task-owned implementation issue remains. Scoped review and explicit developer completion are recorded. ARCH-062-SYSTEM-TEST-001 remains Pending on Shopify completion; it was not started/promoted.

### Architectural Concerns

No arbitrary custom storefront host becomes an Admin/OAuth destination by user input. Missing/mismatched installation association continues to fail without guessing. No lock/recovery, SDK, Woo/external credential, DNS, deployment, main merge or gitlink change was made.

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

## Dependency Reconciliation — 6 November 2026

The synchronized canonical ARCH-061-MCP-001 record is Complete, Attempt 1,
following accepted review `7f61bde93` and explicit developer completion
`38b94f3cb` (source `c9ca303`). Its completion is present in this task's
synchronized parent branch. All explicit prerequisites are therefore Complete.
Correct the stale Pending flag to Ready, leaving attempt 0, executor/claimed_at
null and developer execution/completion modes unchanged. No requirements are
waived and no claim is created by this readiness correction. Normal developer
preparation and source/validation gates still apply.

## Publication — 6 November 2026

The developer explicitly authorized committing and pushing both task branches. Implementation `d0a8de3` contains the source, tests and documentation described above. The matching parent branch publishes this report. At that publication, task remained `in_progress`, Attempt 1, pending authorized review; no acceptance/completion, downstream promotion, main merge, deployment or gitlink update was implied.

## Developer Self-Review Passed / Accepted — Attempt 1 (6 November 2026)

**Scoped review accepted; no actionable finding.** Reviewed published implementation
`d0a8de3a26244aeaa184a58f3def613891fca5d3` against parent
`bdd69ca353fac6d84b86060c4715b4d187581e58`, all twelve changed files,
the current task contract and its acceptance/validation requirements. This
developer-as-architect review supersedes the definition-only Pending review
for this implementation; its historical text is preserved.

### Source and contract review

The three identified suffix gates are removed without changing Woo validation
branches, selected tenant/platform/status or plan/Feature authorization.
Credential acquisition takes only the trusted selected Shop ID; the local port
carries endpoint, Shop ID, token and scope from the same Shared snapshot.
The provider rechecks snapshot identity, binds the fixed HTTPS Admin URL to the
exact snapshot host/origin with no credentials/port/path/query/hash override,
and keeps redirect:error, read-only query admission, scope preflight, API
version/response bounds and cancellation. No domain discovery, alias mapping,
new Shared contract, token cache, schema or refresh-lock/recovery change was
introduced.

Reviewed fixture changes for the new port shape. The positive custom-storefront
test injects a legitimate installation snapshot and proves local transport
authority; it does not prove a persisted custom-domain alias. The negative
mapping probe exercises the actual published Shared provider with injected
database state and denies missing association before OAuth/GraphQL IO. These
limits are accurately recorded rather than presented as live SDK or
cross-service proof.

### Review validation

- Reran `npx tsx --test tests/unit/connections/shopify-domain-boundary.test.ts tests/unit/connections/resolver.test.ts tests/unit/connections/shopify/session-reader.test.ts tests/unit/connections/shopify/provider.test.ts`: **60 passed, 0 failed/skipped**, exit 0. Includes the required 26-test boundary file. Receipt: `/tmp/arch062-mcp-review.log`.
- Reviewed submitted full-unit receipt: **400 passed, 0 failed/skipped**. Reviewed typecheck, build and lint receipts; no source change since their reported passing runs. These broader checks were not repeated during review.
- Verified `git diff --check`, clean implementation and parent worktrees before this record, and zero ahead/behind counts against fetched matching remote task branches.
- Verified dedicated mirrored physical worktree registrations for this task. Start-of-attempt dependency/synchronization/submodule evidence remains the launcher packet recorded above, not a repeated startup claim.

### Decision and lifecycle

Preserve developer execution/completion modes and Attempt 1. Set status Review,
executor null and claimed_at null. Material implementation assistance remains
recorded in the Completion Report; execution ownership is unchanged. The
implementation branch is already committed/pushed; this task-owned review/report
is committed/pushed on the matching parent branch.

Explicit `/moda_developer_update ARCH-062-MCP-001 complete` is still required.
No completion or downstream promotion is made by this review. No code edit,
test-infrastructure deployment, main merge, gitlink change, new attempt or
enabled system-test execution occurred.

## Developer Completion Decision — Attempt 1 (6 November 2026)

The developer explicitly invoked `/moda_developer_update ARCH-062-MCP-001 complete`.
Verified durable accepted scoped review `a7e085a23`, all required checked Work
Items/Acceptance Criteria, and the clean published implementation
`d0a8de3a26244aeaa184a58f3def613891fca5d3`. The parent review branch was also
clean and aligned with its fetched remote before this update. No implementation
change or test rerun was necessary for this documentation/lifecycle decision.

Set status Complete; keep Attempt 1, developer execution/completion modes,
executor null and claimed_at null. Preserve the scoped review and its evidence
limits: this task does not certify App SDK installation, persisted aliases,
live providers or integrated cross-service rollout.

Recalculated downstream eligibility using fetched published parent task records:
BACKGROUND-001 Complete at `6d8c9d6ee`, COMMERCE-001 Complete at
`1bcf42b25`, and SHOPIFY-001 Ready after Changes Requested at `d812181a6`.
SYSTEM-TEST-001 therefore remains Pending, unclaimed, on Shopify completion.
Its manual terminal execution/cutover gates remain in force. No sibling task
lifecycle was changed, no enabled task was executed, and no main merge,
deployment or gitlink update occurred.
