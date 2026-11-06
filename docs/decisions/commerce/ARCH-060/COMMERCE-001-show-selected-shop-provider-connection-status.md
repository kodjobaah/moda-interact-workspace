---
id: ARCH-060-COMMERCE-001
architecture_id: ARCH-060
title: Show and reuse selected-shop provider integrations without credential configuration
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables: []
created: 2026-11-05
updated: 2026-11-05
---
# Show selected-shop provider integration status

## Architecture
ARCH-060; docs/architecture/ARCH-060-studio-provider-connection-visibility.md. Coordinator moda_architect.

## Objective
Display the selected shop’s existing Shopify or WooCommerce integration availability and reuse it to author additional supported tools, with credentials fetched through existing integrations.

## Context
Connections currently reads external connection records only, although Commerce already fetches canonical provider credentials for runtime tools.

## Scope
Commerce Connections list/detail composition, read-only selected-shop metadata projection, authorized server read, navigation, provider-specific Create tool entry points, existing tool-authoring handoff and focused tests described below.

## Out of Scope
Provider credential entry/edit/rotation/copying, new external provider connection rows, live probes, provider runtime rewrites, new MCP/API/schema/Shared/infrastructure changes.

## Requirements
The following architecture detail is binding for this task.

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

## Work Items
- [x] Add authorized selected-shop provider metadata reader and explicit safe DTO using the specified guard/status mapping.
- [x] Compose Store integration independently from external API list/detail data, including selected-shop switching and navigation.
- [x] Keep provider cards read-only and preserve existing external connection management.
- [x] Cover all deterministic matrix rows with focused server/UI/route tests and secret/write/network assertions.

## Interfaces / Contracts
Commerce-local provider-status DTO only, specified above. No cross-service contract. Existing integration runtime remains sole credential consumer; external ConnectionView/mutation contracts stay external-only.

## Dependencies
None

## Enables
None

## Acceptance Criteria
- [x] Every deterministic matrix row above passes.
- [x] Shopify and Woo credentials are fetched via existing integrations for actual runtime execution, never configured or duplicated by this change.
- [x] Provider metadata status remains distinguishable from live connectivity and external API connections.
- [x] No tenant/auth widening, credential/decryption/provider calls on render, or persisted writes.

## Validation
- [x] Run declared focused test command for connections-production, connections-ui, connections-route-composition and selected-shop-navigation tests after inspecting package.json.
- [x] Run repository declared typecheck and production build appropriate to changed deployable TypeScript; record exact commands/results.
- [x] Inspect serialized props/HTML/action results and captured logs using credential canaries; assert zero provider credential writes, decrypt operations and outbound provider requests for status reads.

## Stop Condition
After defined work, criteria and validation pass, submit Completion Report for review and STOP. Developer completion remains explicit via /moda_developer_update. Do not auto-claim or implement from this definition.

## Implementation Notes
Prepare through normal launcher-resolved isolated task worktrees and synchronized branches when execution is requested. No implementation has started. New metadata reader/action names are implementation-owned; existing paths/symbols above are touchpoints, not claims that status APIs already exist. Return any discovered cross-repository requirement to architect rather than adding one silently.

## Completion Report

### Status

Complete — explicit developer decision via `/moda_developer_update ARCH-060-COMMERCE-001 complete`, 5 November 2026. Attempt 1 has durable passing review `ff42613a90feadee277e9b7b5c62c2d1588813ae`; reviewed implementation `a152092a3d95639ccf588be31e3bce8f11ed90f8` is clean, committed and pushed. Completion applies the controlling architect clarification and does not claim live provider testing. Execution/completion modes remain developer; executor/claimed_at stay null and attempt remains 1.

### Files Changed

Implementation repository (commit `a152092`, published on `task/ARCH-060-COMMERCE-001`):

- `app/connections/[id]/page.tsx`
- `app/connections/page.tsx`
- `app/tools/page.tsx`
- `components/production-studio-page.tsx`
- `components/studio-workspace.tsx`
- `src/commerce/integration/studio/services.ts`
- `src/studio/connections/connections-route-client.tsx`
- `src/studio/connections/connections-ui.tsx`
- `src/studio/connections/contracts.ts`
- `src/studio/connections/navigation.ts`
- `src/studio/connections/production.ts`
- `src/studio/connections/provider-status.ts`
- `src/studio/connections/provider-tool-handoff.ts`
- `src/studio/connections/server-actions.ts`
- `src/studio/connections/store-integration.tsx`
- `src/studio/contracts.ts`
- `src/studio/selected-shop.ts`
- `src/studio/tools/new-tool-editor.tsx`
- `src/studio/tools/tool-authoring-screen.tsx`
- `tests/commerce-lifecycle.test.ts`
- `tests/connections-production.test.ts`
- `tests/connections-route-composition.test.tsx`
- `tests/provider-tool-handoff.test.ts`
- `tests/selected-shop-context.test.ts`
- `tests/selected-shop-route.test.tsx`
- `tests/store-integration.test.tsx`
- `tests/tool-authoring-screen.test.tsx`
- `tests/woocommerce-rest-review-save.test.ts`

Parent repository: this task's progress report only. Claim/report formatting repair was committed during preparation as `6d778070f`; the implementation and this progress report/architect clarification are published under the developer’s explicit commit/push instruction. No gitlink, index, architecture definition, other task or main branch edits.

### Work Completed

- Added a Commerce-local server-only metadata reader and independent authenticated `getStoreIntegrationStatus` action. Each request authenticates and invokes existing Studio shop inspection before metadata access. Client domain/platform are never accepted. No selection returns no-selection without provider metadata reads.
- Shopify uses bounded offline-session existence queries with nonempty-token/expiry predicates and `select: { id: true }`, never token retrieval. Active valid sessions map to AVAILABLE; expired-only to EXPIRED; absent/online-only to MISSING. Inactive shops do not trigger provider reads.
- Woo selects only installation/grant guard metadata and checks current shop platform/status, canonical site/domain, null Shopify identity, active/unrevoked installation, read-scoped ACTIVE grant and exact shop/installation/version correspondence. No decryption, secret envelopes or provider probes are used for status. Errors return bounded results and reuse existing fixed-code logging.
- Projected a closed DTO containing only shop identity, platform, safe display host and status. Internal session/installation/grant identities and credentials are not serialized. Status text explicitly says “Integration credentials available” and “Live connection not checked”.
- Composed Store integration independently of external list/detail results on both Connections routes. Provider metadata never becomes an external connection row or enters CredentialPanel. Existing external mutations and authorization remain unchanged. ADMIN can author tools under the existing ADMIN tool-authoring policy while external credentials remain SUPER_ADMIN-managed.
- Retained selected shop across list/detail/back links, filters and return context. Selection-keyed provider components discard late prior-shop results; same-shop server refreshes replace status immediately and withdraw stale Create tool shortcuts.
- Added an optional metadata-only shop-list projection used only by Connections, preventing unselected shop lists from reading sessions for every listed shop. Other callers retain existing defaults; selected-shop context still uses existing authorized inspection.
- Added native Create tool links carrying only shopId and supported provider kind. Server preselection validates current authorized metadata, selected shop identity and matching Shopify/Woo adapter. Missing, forged, mismatched and unavailable preselection is rejected. Existing normal tool validation, Woo current-test proof, credential resolution, publication, entitlements, scopes and production allowlists are unchanged.
- Shop/provider authoring identity changes remount the local authoring screen, clearing prior-shop state/proofs. Provider preselection enters the existing NewToolEditor flow, not a new tool persistence path. Status is never execution authorization.
- Added/extended status, UI, route, navigation and authoring-entry tests, including stale async results, server refresh, auth-before-read, secret canaries, safe selects, bounded logs and existing Woo revocation/proof regression coverage.

### Architect Clarification and Follow-up Evidence

At the developer's explicit request, moda_architect recorded the controlling clarification below: preserve Shopify's inert deferred-Test checkpoint; prove existing authoritative authoring validation and normal guarded draft Save instead of introducing live provider tests. New metadata/provider/business projection remains strictly read-only; unchanged approved development-only PlatformAdmin bootstrap is a narrow inherited exception. No runtime/MCP restoration dependency was introduced and no implementation acceptance was made.

The remaining two-tool reuse evidence is now explicit:

- Shopify: real authorized `CommerceLifecycle` + `FixturePublicationStore` create two separately named `SHOPIFY_ADMIN_GRAPHQL` draft revisions and CREATE_TOOL audits. Assertions retain draft-only state and exclude credential/external linkage, capability/release/pointer changes. Existing authoring-screen/Shopify UI regressions independently enforce current authoring validation and inert deferred Test.
- Woo: actual `saveWooCommerceToolDraft` authorizes the same shop and validates two independently signed current proofs, then uses real lifecycle/store to create two separately named Woo drafts. Assertions retain same-shop DRAFT_ONLY state, edit authorization, zero Save-time provider calls and no credential/external linkage or release/admission changes.
- The architect's bounded read-only follow-up confirmed these new cases, together with existing handoff/authoring regressions, are sufficient focused two-draft boundary evidence. This is deterministic compositional evidence, not a live test or full implementation acceptance.

### Validation Results

Final local checks:

- `npm test -- tests/connections-production.test.ts tests/connections-ui.test.tsx tests/connections-route-composition.test.tsx tests/selected-shop-navigation.test.tsx tests/selected-shop-context.test.ts tests/selected-shop-route.test.tsx tests/store-integration.test.tsx tests/provider-tool-handoff.test.ts tests/tool-authoring-screen.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/woocommerce-rest-review-workflow.test.tsx tests/woocommerce-rest-live-test-service.test.ts tests/woocommerce-rest-review-save.test.ts tests/tool-authoring-no-provider-io.test.ts tests/studio-integration.test.ts` — **15 files, 223 tests passed**, exit 0. Final log `/tmp/arch060-tests.log`.
- `npm run typecheck` — exit 0. Log `/tmp/arch060-typecheck.log`.
- `npm run build` — exit 0, including declared schema/manual/code-runtime packaging/smoke, Prisma generation and Next production build. Log `/tmp/arch060-build.log`. Existing Nunjucks webpack import warnings remain; no dependency changes.
- Installed repository-declared dependencies with `npm ci --include=dev`; used workspace Node bootstrap, Node 24.19.0. Generated Prisma from the existing recorded Database submodule; no schema/pin edits or migrations.
- `npm exec -- eslint <all changed/new TypeScript files>` — exit 0, zero errors; one pre-existing unused `selectedShop` parameter warning in NewToolWorkspace (present before task). Log `/tmp/arch060-lint.log`.
- `git diff --check` — exit 0.

An intermediate expanded test run found two old selected-shop route mocks missing the new status action. Updated those fixtures and assertions; focused rerun passed, followed by the final all-green 223-test run. No failing test was removed or weakened.

Credential canary tests inspect returned DTO, rendered native HTML/serialized route props and captured bounded logs. Safe-select assertions exclude credential envelopes/token retrieval; projection only performs find queries and no decrypt/provider operations. Existing external mutation tests and Woo revocation/current-proof tests remain passing. These are deterministic local tests, not real store/provider connectivity evidence. No live provider probe or merchant mutation was performed.

Additional validation after architect clarification:

- `npm test -- tests/commerce-lifecycle.test.ts tests/woocommerce-rest-review-save.test.ts` — 39 tests passed, including the two new reuse cases. Log `/tmp/arch060-reuse-tests.log`.
- Final `npm run typecheck` — exit 0 after replacing untyped snapshot member access with runtime structural assertions. The corrected 39-test lifecycle/Save run also exits 0. No application code changed during this follow-up.
- Lint of the two added-to test files: zero errors, one existing unused `_input` fixture-parameter warning in Woo review-save. Together with the earlier NewToolWorkspace warning, no new lint errors were introduced. Application source is unchanged since the successful production build.

### Deviations

- Preserved Shopify's existing deliberate deferred-live-test contract. `NewToolWorkspace` displays “Live Shopify Admin tests are deferred until standalone MCP integration is restored”; `tests/shopify-admin-tools-ui.test.tsx` and tool-authoring-screen tests explicitly enforce no embedded live-test invocation. The new shortcut opens this existing authoring flow. The controlling architect clarification supersedes the earlier live-tested Shopify criterion with authoritative validation and guarded draft Save plus an inert-Test negative assertion. No runtime restoration or bypass was invented.
- Extended the local shop-list read with an optional session-availability flag to satisfy Connections' no-selection/no-provider-query boundary; defaults elsewhere are unchanged.
- Preparation initially failed because the task's Completion Report lacked the blank lines required by the launcher's status parser, after writing Attempt 1 locally. Repaired only report formatting and durably completed that same developer claim, without a second attempt or ownership-mode change.

### Assumptions

Existing authenticated Studio shop inspection is the authority for shop visibility; provider metadata remains a point-in-time hint. Runtime test/run/save operations continue enforcing current integration validity independently. Metadata availability does not establish valid decryption configuration, live health, additional scopes or production admission.

### Unresolved Issues

None blocking task completion under the controlling architect clarification. Both acceptance conflicts were resolved, required implementation/validation passed, the developer self-review is durably accepted, and the developer has now explicitly completed Attempt 1. Source publication was verified at `a152092`; this completion record is published on the matching parent task branch. No live provider/deployment success is asserted. Initiative-wide wording reconciliation remains a separate architect documentation responsibility before marking the initiative Implemented.

### Architectural Concerns

Do not equate AVAILABLE metadata with provider health or execution authorization. Preserve Shopify deferred Test under the controlling architect clarification; do not restore runtime functionality or fabricate a passing live test. Provider connection/credential records, crypto/runtime APIs, scopes, entitlements and release/outreach admission remain under their existing owners and unchanged.

### Worktree and Assistance Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-060-COMMERCE-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-060-COMMERCE-001`.
- Both branches: `task/ARCH-060-COMMERCE-001`. Implementation base `7f50848ee783479ec4d259c10000effd3d2e1bd6`; feature commit `a152092` is pushed to the implementation task branch.
- Existing Database submodule verified at recorded `bd2d09066a8eb178a56f48fbbf88df637c411059` with no changed pin.
- Developer Attempt 1, claim time `2026-11-05T18:39:43Z`, durable preparation claim `6d778070f`. Initial Codex executor preparation correctly refused developer mode; preparation continued under the canonical developer workflow. During implementation, assistance preserved `execution_mode: developer`, `completion_mode: developer`, `executor: developer` and `status: in_progress`; the later review cleared the claim and explicit developer decision now completes the task.
- Material assistance: Commerce-local source/test implementation, focused validation and progress reporting, explicitly authorized in the current request. No other worktree/shared checkout used for implementation. The developer explicitly authorized a moda_architect subagent consultation, limited to task-owned architect clarification and read-only follow-up; no parallel implementation agents, main merge, downstream execution or lifecycle self-review.

### Publication Authorization

The developer explicitly requested “commit and push the changes”. Published the task-owned implementation and parent report/architect clarification on their matching `task/ARCH-060-COMMERCE-001` branches. No gitlink/index changes, main merge, self-review or lifecycle/completion transition is included. That publication step did not change lifecycle state. Subsequent passing developer review and the explicit completion decision are recorded below.

## Architect Review

### Review Status

Pending — architect scope clarification recorded on 2026-11-05 at the developer's explicit request. This consultation is not implementation acceptance or developer self-review; lifecycle metadata and completion authority are unchanged.

### Review Notes

The existing Shopify authoring UI deliberately defers embedded live testing following the standalone MCP extraction. Source and regression tests confirm that its normal draft Save path uses authoritative definition/request/result-contract/template validation while no deferred provider test is invoked or marked PASSED. Requiring live Shopify testing here would contradict the task's explicit no-runtime-rewrite/no-new-MCP boundary. The controlling amendment below resolves that contradiction without restoring or bypassing runtime functionality.

The provider metadata projection is read-only. Existing Studio development-bypass authorization may invoke the pre-existing idempotent PlatformAdmin bootstrap. Requiring this bounded feature to remove that shared authentication behavior would expand scope and risk changing staff authorization. The controlling amendment defines the narrow exception; no provider or business-state write is permitted.

### Reviewed Files

- This task definition, additional authoring criteria and current implementation-assistance report.
- `src/studio/tools/new-tool-editor.tsx` — explicit deferred Shopify Test step and existing validation/Save controls.
- `tests/shopify-admin-tools-ui.test.tsx`, `tests/tool-authoring-screen.test.tsx` — deferred Test remains inert; no PASSED provider-test state is fabricated; current validation gates remain required.
- `src/commerce/integration/backend.ts:authorizeStaff`, `lib/auth/development-platform-admin.ts:ensureDevelopmentStudioAdmin` — existing development-only identity bootstrap; ordinary persisted-staff authorization reads current active role.
- `src/studio/connections/provider-status.ts`, `src/studio/connections/provider-tool-handoff.ts` — safe metadata selects and navigation-only preselection, without provider credential retrieval/decryption or persistence.

### Validation Reviewed

Inspected the relevant source and existing test assertions to establish the two conflicting contracts. The reported 223 passing focused tests, typecheck and production build remain implementer-provided evidence; they were not independently rerun in this scope-only consultation. No live provider operation, credential mutation, deployment or implementation publication was performed.

### Architecture Conformance

Preserving Shopify's deferred Test guard and the existing development identity bootstrap conforms to the bounded read-projection/navigation purpose under the amendment below. This does not assess every implementation criterion, establish live connectivity, accept the implementation, complete the task or waive normal developer reconciliation/publication.

### Follow-up

The implementing developer may reconcile the Work Items, Validation and Completion Report against the amended criteria, then use `/moda_developer_update ARCH-060-COMMERCE-001` for the normal developer review. Retain existing Woo current-test proof and runtime revocation guards. Publish task-owned changes only through the authorized developer publication workflow; no completion or merge is authorized by this consultation. Align the duplicated ARCH-060 architecture wording during normal architect documentation reconciliation before the initiative is marked Implemented; this decision does not create a runtime-restoration dependency for this task.

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
- [x] Authorized Shopify shop -> Create tool opens Shopify Admin GraphQL authoring with that shop selected; an additional supported tool can be validated/tested/saved through the existing lifecycle using fetched credentials.
- [x] Authorized WooCommerce shop -> Create tool opens WooCommerce REST API authoring with that shop selected; additional supported read tools retain the existing current-test proof before save.
- [x] Missing selection, denied authoring role or missing/inactive provider metadata never exposes an enabled native Create tool shortcut; deep-link attempts still obey existing server authorization. Do not disable independently authorized external API creation.
- [x] Changing shop/provider invalidates stale authoring tests and previous-shop preselection; a forged provider kind cannot select another tenant or mismatched adapter.
- [x] Credentials revoked after metadata load cause the subsequent test/run to fail through existing guards; status display never supplies authority.
- [x] Two separately created tools reuse the same native integration without creating provider external-connection/credential records; no secret values in routes, drafts, browser props or logs.
- [x] Creating a tool leaves existing integration scopes, feature entitlements and outreach allowlists unchanged; normal publication is required for production capability use.

No new provider operation is implemented by this task. Unsupported operations require separately reviewed runtime work before they can be offered in authoring. Extend focused Connections and tool-authoring UI/server tests to prove every row above. Definition amendment only; implementation remains unclaimed.


## Controlling architect clarification — 2026-11-05

This architect-authored clarification resolves the developer-reported acceptance conflicts for `ARCH-060-COMMERCE-001`. It controls over contrary wording in the earlier copied authoring acceptance detail for this bounded task. It narrows proof to the capabilities that currently exist; it does not represent a successful live test or authorize new runtime/MCP work.

### Shopify authoring acceptance replacement

Replace the earlier additional Shopify criterion requiring a tool to be “validated/tested/saved ... using fetched credentials” with the following observable contract:

- An authorized selected Shopify shop with AVAILABLE metadata opens the existing `SHOPIFY_ADMIN_GRAPHQL` authoring flow with that shop selected. An additional supported definition can pass the existing authoritative definition, Request, current result-contract and Result Template validations and be saved through the normal guarded draft lifecycle. No validation, role, draft, publication or capability gate is weakened.
- Shopify's existing deferred Test checkpoint remains explicit and inert: it does not retrieve credentials, call a provider/test endpoint, or fabricate a PASSED provider-test state. Preserving the current deferral is a passing requirement for this task, not an unresolved live-test requirement. Acceptance evidence must call this authoritative authoring validation/draft Save, never live provider testing.
- The new status display and Create tool entry do not supply credentials or authority. Any actually available runtime execution path continues fetching credentials and enforcing current shop/provider/permission/revocation guards through its existing resolver. Restoring Shopify live authoring tests or standalone MCP integration requires separately reviewed runtime scope when that capability is requested; it is not a dependency or implementation requirement of this task.

The earlier revocation criterion is provider-capability-specific: Woo's available authoring Test/run path must continue failing through its existing guards after grant revocation/rotation; Shopify's deferred authoring Test must remain non-executing and must not claim success. Existing available execution paths must retain their current revocation guards. No new Shopify provider call is required to prove this projection/navigation change.

The two-tool reuse criterion remains mandatory at the supported lifecycle boundary: two separately created native tool drafts may reuse the same authorized store integration through the existing guarded authoring/Save lifecycle, without creating native-provider external connection/credential records. For Shopify, proof uses the existing authoring validation and draft Save path plus the deferred-Test negative assertion; for Woo, it retains current-test proof before Save. Two links or two metadata reads alone are not proof of two guarded draft creations. Live store/provider testing is not introduced by this clarification.

### Zero-write boundary clarification

“Zero writes on render/refresh/status read” means the new provider-status projection and navigation must not create or mutate provider/installation/grant/session credentials, external connection rows/revisions/credentials, tool drafts, merchant/business state, scopes, entitlements or release/admission state. The projection itself must use read queries only, perform no decryption and make no outbound provider request. Normal authenticated persisted-staff reads must remain read-only, with existing authorization checked before provider metadata access.

There is one narrow inherited exception: when existing server-side authentication has already selected the approved development-bypass principal, the unchanged `authorizeStaff` -> `ensureDevelopmentStudioAdmin` identity-backing bootstrap may perform its existing idempotent PlatformAdmin INSERT ... ON CONFLICT DO NOTHING invocation(s). It is not provider setup or a metadata-side effect introduced for this feature. This exception does not allow client-selected bypass flags, new identities, broader roles, altered auth policy, extra bootstrap writes or any provider/business-state writes. Do not move the bootstrap into the metadata reader or remove existing authorization merely to produce a zero-write counter.

Deterministic evidence must distinguish (a) the provider projection after authorized inspection, asserting no writes/decrypt/provider I/O and no secret serialization, from (b) the pre-existing development identity bootstrap behavior where that mode is exercised. Report the latter accurately; do not claim every development-bypass page request executes zero SQL write statements. No authentication rewrite or additional implementation task is required solely to remove this inherited bootstrap.

### Decision limits and remaining requirements

All other original task criteria remain in force, including tenant/auth boundaries, safe selected-shop projection, external/provider independence, stale-result rejection, provider-kind validation, credential canaries, Woo proof/revocation guards and reuse of native integrations without duplicated credentials. This clarification does not check completion boxes or assert that the current local changes prove every row. Normal source/test reconciliation, authorized publication and developer review/completion remain required. No repository source, task lifecycle/claim metadata, dependency, index/frontier, main branch or runtime credential is changed by this decision.


## Developer Self-Review Passed / Accepted — Attempt 1 (2026-11-05)

Reconciled source, task scope/amendment, worktree/publication state, validation and authorized assistance using `/moda_developer_update ARCH-060-COMMERCE-001`. **Review passed; no actionable findings.** This is passing review, not task completion: `completion_mode: developer` requires an explicit `/moda_developer_update ARCH-060-COMMERCE-001 complete` decision. Status Review; claim cleared; attempt remains 1.

### Implementation and conformance

Reviewed all 28 changed files against baseline `7f50848ee783479ec4d259c10000effd3d2e1bd6`, including authorized selected-shop metadata queries, bounded DTO, independent external/provider composition, selection-keyed rendering/navigation and server-validated native authoring preselection. Provider status selects credential-presence metadata only, with no decrypt/provider I/O or credential writes. Current tenant, platform, offline-session and Woo installation/grant/version checks retain existing authorization. Runtime credential fetching and current-proof/revocation guards remain owned by their existing adapters.

The deterministic status/navigation/privacy matrix and guarded two-draft reuse are covered by the focused evidence. Acceptance checkboxes above are reconciled **under the controlling architect clarification**: the original Shopify live-test wording is superseded by authoring validation/guarded Save and deferred-Test negative proof; zero-write assertions apply to the new projection and ordinary authenticated reads, with only the explicitly permitted inherited development identity bootstrap exception. No live Shopify authoring test, provider connectivity, decryption success or universal development-request zero-write claim is made.

### Validation and publication

- Independently ran the fifteen-file focused command listed in the report plus `tests/commerce-lifecycle.test.ts` as one aggregate: **257 tests across 16 files passed**, exit 0. Log `/tmp/arch060-developer-review.log`. This covers the amended guarded reuse and existing Shopify/Woo authoring regressions; it is not added to earlier counts as unique extra coverage.
- Independently checked `git diff --check HEAD^`: passed; inspected submitted typecheck/build logs and reported scoped lint. Typecheck/build/lint were not independently rerun in this review.
- Implementation HEAD and `origin/task/ARCH-060-COMMERCE-001` both equal `a152092a3d95639ccf588be31e3bce8f11ed90f8`. No uncommitted implementation changes. Canonical parent worktree was clean at `bf8078a8dfc49e02f02230df511dc8eb182e4fef` before this record; its task ref matched the remote.
- Dedicated parent/implementation paths, matching branches, preparation/synchronization, unchanged Database pin and material authorized Codex assistance are recorded in the Completion Report. No implementation changes were needed or published by this reconciliation; only the parent task review is committed/pushed.

### Boundaries and follow-up

No explicit dependencies/enables exist; no downstream task is promoted. No main merge, gitlink update, credential mutation, deployment or task completion is performed. The developer retains final completion/integration authority. Earlier architecture wording requiring live Shopify Test is superseded for this task by the recorded clarification; duplicated initiative wording must be reconciled before the initiative is marked Implemented, as already required by that decision.


## Developer Completion Decision — Attempt 1 (2026-11-05)

The developer explicitly invoked `/moda_developer_update ARCH-060-COMMERCE-001 complete`. Verified the durable **Developer Self-Review Passed / Accepted** record in published parent commit `ff42613a90feadee277e9b7b5c62c2d1588813ae`, all required work/criteria reconciled under the controlling architect clarification, and unchanged clean/published implementation `a152092a3d95639ccf588be31e3bce8f11ed90f8`. The passing review independently recorded 257 tests across 16 files; existing typecheck/build/lint evidence remains applicable. No redundant source validation run is needed for this documentation-only completion decision.

Transitioned Review -> Complete. Preserved developer execution/completion modes and Attempt 1; executor and claimed_at remain null. This decision is the developer's explicit completion authority, not an automatic implementation-agent acceptance. Earlier pending-completion statements in the preserved review are historical and superseded by this decision.

### Dependency frontier and publication

Recalculated eligibility from task definitions: no explicit dependencies/enables and no downstream task references exist for this task. Updated the ARCH-060 Commerce task index row to Complete; no other task is promoted or started. The architecture initiative is not marked Implemented by this task completion; the existing architect instruction to reconcile duplicated initiative wording remains separate.

Committed/pushed only the current task record and its domain-index completion reconciliation on parent `task/ARCH-060-COMMERCE-001`. Implementation is already published; no source change, gitlink update, main merge/push, credential mutation or deployment is performed.

## Scoped follow-up — ARCH-063 (2026-11-06)
See docs/architecture/ARCH-063-refreshable-shopify-status-and-safe-refresh-events.md for source-audited refreshable metadata admission and safe postcommit refresh-event corrections. Historical completion/review and attempt are preserved; this reference does not reopen or claim the task. No deployed-state inference.
