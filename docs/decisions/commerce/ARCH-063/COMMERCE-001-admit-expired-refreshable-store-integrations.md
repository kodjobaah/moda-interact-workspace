---
id: ARCH-063-COMMERCE-001
architecture_id: ARCH-063
title: admit expired refreshable store integrations
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables: ["ARCH-063-SYSTEM-TEST-001"]
created: 2026-11-06
updated: 2026-11-06
---
# Admit expired refreshable store integrations

## Architecture
ARCH-063; docs/architecture/ARCH-063-refreshable-shopify-status-and-safe-refresh-events.md. Coordinator moda_architect.

## Objective
Admit expired refreshable store integrations using existing automatic coordinated refresh.

## Context
Metadata EXPIRED blocks authoring despite usable refresh; no safe refresh lifecycle events. Parent includes cross-service source audit and selected solution.

## Scope
moda-interact-commerce implementation/tests at exact touchpoints below; stale shared checkout is not a deployed observation.

| Existing file | Exact surface | Required change |
|---|---|---|
| moda-interact-commerce/src/studio/connections/provider-status.ts | readProviderMetadata | Add REFRESHABLE safe metadata query and explicit unusable/ambiguous states without token selects. |
| moda-interact-commerce/src/studio/connections/contracts.ts | StoreIntegrationStatus | Add REFRESHABLE; keep secret-free local DTO. |
| moda-interact-commerce/src/studio/connections/provider-tool-handoff.ts | resolveNativeToolPreselection | Export/reuse isStoreIntegrationUsableForAuthoring; accept AVAILABLE/REFRESHABLE Shopify only. |
| moda-interact-commerce/src/studio/connections/store-integration.tsx | StoreIntegration | Render automatic-refresh guidance and permit usable link; retain stale shop result exclusion. |
| moda-interact-commerce/components/studio-selected-shop-context.tsx | selected-shop header | Replace hardcoded Shopify boolean label with provider-specific metadata status. |
| moda-interact-commerce/src/studio/contracts.ts | ShopExecutionContext | Replace existence boolean with safe storeIntegration metadata field. |
| moda-interact-commerce/src/commerce/integration/studio/services.ts | shop context projection | Reuse metadata classifier, no OAuth status probe. |
| moda-interact-commerce/src/studio/testing/in-memory-studio-services.ts | shop context fixtures | Return new explicit provider metadata fixture shape. |


## Out of Scope
Page-render refresh, manual credential entry, lock/recovery redesign, schema, topology, generic logger/metric framework and automatic task execution.

## Requirements
## Problem and audited behavior
Commerce src/studio/connections/provider-status.ts readProviderMetadata checks valid access then expired access and emits EXPIRED without checking usable refresh credentials. store-integration.tsx and provider-tool-handoff.ts permit AVAILABLE only, so users cannot reach the already automatic execution refresh. Selector components/studio-selected-shop-context.tsx renders an existence-only shopifyOfflineSessionAvailable boolean even for Woo. Existing expired-status tests encode this dead end. App shop.service.ts readiness near128–136 accepts refreshToken presence without refreshTokenExpires, giving the opposite false-positive. Shared offline-token-provider has coordinated refresh mechanics but no refresh events. These are local implementation observations, not deployed-state claims.

Canonical ARCH-061-MCP-001 implementation worktree session-reader.ts calls provider.getSession(shopId) without a premature expiry gate; shared submodule checkout may show old direct reads and is not proof of deployed behavior. Background shopify-session.service.ts delegates Shared getAccessToken; no access-expiry admission gate found. Commerce execution composition/local-policy-providers already call Shared; App SDK wrapper handles token refresh inside transaction scope. Audit fixes below preserve existing accepted locking/identity/recovery rather than reimplementing it.

## Exact functional decision
Add Commerce-local StoreIntegrationStatus REFRESHABLE. Keep EXPIRED for unusable refresh-required credentials, with label "Refresh or reconnection required" so a within-skew access token is not falsely described already expired. Both status and App readiness use the current helper's fixed 320000ms skew, test boundaries at exactly now+320000 and +320001; do not revert to an assumed five-minute constant. For an authorized ACTIVE Shopify shop with exactly one matching offline session, metadata AVAILABLE means nonempty access present with null expiry with no refresh token (the helper-supported nonexpiring state) or expires>now+320000ms. Access inside the helper's actual 320000ms refresh skew, including expired access, with refreshToken present/nonempty and refreshTokenExpires>now is REFRESHABLE. Access requiring refresh without usable refresh is EXPIRED; absent offline/access is MISSING, ambiguous or invalid mapping UNKNOWN/unavailable. Query refresh presence using DB predicates and explicit safe selects; never select/return token or decrypt. No page render/status read/network mutation. Readiness means credentials can be attempted, never live provider health. Display REFRESHABLE as "Ready to refresh automatically" and "Credentials refresh when a tool runs" with existing "Live connection not checked". No user refresh button, credential edit or reinstall requirement for REFRESHABLE.

Allow both AVAILABLE and REFRESHABLE for Shopify tool-authoring link and native tool preselection; Woo retains AVAILABLE and existing grant checks. Use one local isStoreIntegrationUsableForAuthoring predicate in provider-tool-handoff.ts and reuse in StoreIntegration. Test/save/live-test actions MUST independently resolve current selected Shop and execute via Shared getSession/getAccessToken; do not authorize from stale browser status, skip scope checks or refresh on save if existing save is metadata-only. Refresh happens only at actual provider execution. A stale REFRESHABLE hint can fail safely if refresh is revoked; stale AVAILABLE can refresh at execution after expiry. Existing pending async shop-switch results must never reopen another shop's link.

Selector header must show provider-specific metadata state from the same safe classifier: remove existence-only boolean as decision source, replace ShopExecutionContext field with `storeIntegration:{platform:'SHOPIFY'|'WOOCOMMERCE';status:StoreIntegrationStatus}|null` as Commerce-local contract. The production projection reuses readProviderMetadata; injected test fixtures updated. No cross-service wire schema. Unknown/no selection stays explicit; Woo never labelled Shopify session. Header and Connections agree without live checks.

App readiness function must use same logical credential viability: nonexpiring access with no refresh token OR access valid beyond now+320000ms OR access requiring refresh with nonempty refresh and refresh expiry strictly future; missing/expired refresh expiry is false. This remains metadata-only and does not replace actual Shared execution validation. Shared helper invalid-token semantics remain unchanged. MCP/Background direct helper callers require no new optimistic expiry precheck.

## Exact safe refresh-event contract
Shared factory gains optional `onEvent?:(event:ShopifyOfflineRefreshEvent)=>void` hook, exported from ./shopify/node. Hook failure is swallowed synchronously; async return is ignored and rejection suppressed; telemetry never changes return/transaction outcome. Event is frozen plain bounded object `{event:'shopify.offline_refresh.started'|'shopify.offline_refresh.committed'|'shopify.offline_refresh.failed';operationId:string;shopId:string|null;source:'SHARED'|'SDK';durationMs:number;outcome:'STARTED'|'COMMITTED'|'REJECTED'|'UNKNOWN'|'CANCELLED'|'UNAVAILABLE';reasonCode:ShopifyOfflineTokenErrorCode|null}`. No domain, session ID, token, scope, error/cause/body, OAuth client key/secret, endpoint or customer fields. operationId is a fresh UUID per attempted refresh, not caller text; duration monotonic elapsed rounded/clamped 0..60000. shopId derives trusted context; SDK bootstrap uses null until resolved, never a guessed domain as identifier.

For Shared getSession: emit started immediately before actual refresh dispatch after all eligibility checks; emit committed ONLY after interactive transaction commits successfully; emit failed once on rejection, cancellation, timeout, malformed response or persistence/commit ambiguity after start. Unknown after remote acceptance maps UNKNOWN/REFRESH_OUTCOME_UNKNOWN, never committed. Returning existing valid/nonexpiring credential emits no refresh event. Lock waiter rereading committed token emits none. Hook is not a competing logger: each service adapter forwards schema fields to existing @modainteract/moda-interact-shared/logging logger, info started/committed, warn failed. No raw Error attached. Exactly one terminal event per started attempt within a running process; process death can leave started without terminal, do not claim durable/exactly-once telemetry.

SDK-managed refresh/token exchange is not observable solely from Shared getSession. App coordination wrapper tracks bounded OAuth request intent in its existing ALS context: grant_type refresh_token emits same SDK started event; successful SDK credential persistence does not yet emit committed. Emit SDK committed only after outer coordinated transaction commits (including authenticated redirect commit); rejection/rollback/deadline/commit failure emits SDK failed. Token exchange acquisition is a distinct operation and MUST NOT be mislabeled refresh: no refresh event unless grant_type refresh_token. If SDK delegates to Shared refresh, source SHARED owns events and wrapper emits no duplicate. App creates service-owned event adapter reusing same exported event shape; no generic logger fork. Tests cover SDK refresh/store-success/commit-failure and redirect handling.

## Package/dependency and rollout
Shared implementation extends existing API compatibly; publication chooses next available approved semver and records exact version before consumer pins. No forced version guess or unpublished sibling import. Commerce UI correction is independent and Ready now; it uses existing accepted ARCH-060/061/062 contracts, does not wait for log publication. Shared logging implementation is also independently Ready. Consumer event wiring depends on Shared publication. App wiring includes metadata-readiness correction. System Test is terminal on all fixes; manually invoked after optional user exercise. Compatible rollout, no schema/credential/env or Render topology change. Logging absent in old binaries is expected until owning consumer deployed; do not assert deployed observability from local code. No new metric/span framework. Metadata reads and tooling never expose provider secrets.

## Work Items
- [x] Audit components/production-studio-page.tsx native tool preselection and src/studio/tools/shopify-admin-editor.tsx plus existing authoring actions referenced by that editor: navigation/test/save must not pre-reject REFRESHABLE; metadata-only save must not invoke refresh; runtime scope/tenant authorization remains authoritative. Add route/deep-link and live-test fixtures, including stale status after refresh revocation.
- [x] Add REFRESHABLE safe metadata query and explicit unusable/ambiguous states without token selects.
- [x] Add REFRESHABLE; keep secret-free local DTO.
- [x] Export/reuse isStoreIntegrationUsableForAuthoring; accept AVAILABLE/REFRESHABLE Shopify only.
- [x] Render automatic-refresh guidance and permit usable link; retain stale shop result exclusion.
- [x] Replace hardcoded Shopify boolean label with provider-specific metadata status.
- [x] Replace existence boolean with safe storeIntegration metadata field.
- [x] Reuse metadata classifier, no OAuth status probe.
- [x] Return new explicit provider metadata fixture shape.

## Interfaces / Contracts
Commerce-local REFRESHABLE DTO/predicate and selector metadata, plus published optional Shared onEvent hook and exact frozen event schema above. Each consumer owns safe logger forwarding; provider/runtime credentials stay server-only. Exact version recorded by SHARED-002 before consumer pins.

## Dependencies
None

## Enables
- ARCH-063-SYSTEM-TEST-001

## Acceptance Criteria
- [x] Expired/within-skew access+future refresh -> REFRESHABLE; expired/within-skew access with expired/missing refresh ->EXPIRED (UI label: Refresh or reconnection required); beyond-skew valid access AVAILABLE; zero decrypt/network/write metadata calls.
- [x] Header and Connections agree for Shopify/Woo; existing custom-domain integration mapping unchanged.
- [x] AVAILABLE and REFRESHABLE links/deep-link preselection work; stale shop response excluded.
- [x] Actual live test of expired-refreshable row invokes Shared once, persists pair/expiry then provider request; revoked scope and cross-tenant selection fail.

## Validation
- [x] Run focused command `npx vitest run tests/store-integration.test.tsx tests/provider-tool-handoff.test.ts tests/connections-production.test.ts`; explicitly create additional focused fixture files where required. Shared also runs disposable PostgreSQL offline-token-provider.postgres.test.ts postcommit/concurrency fixtures.
- [x] Run owning declared typecheck/build appropriate to deployable change (Background build; System Test typecheck only); record exact commands. Capture event payloads with secret canaries and test hook failure isolation.

## Stop Condition
Complete defined work/criteria/validation, submit report for authorized review and STOP. Explicit developer completion required. System Test terminal/manually invoked; no enabled work auto-start.

## Implementation Notes
Use launcher-resolved isolated/synchronized task worktrees when execution requested. No implementation from definition. Preserve accepted locking/domain/SDK identities. Task-specific assertions are binding; no architecture selection delegated. Service logger uses published Shared logging, never raw provider/Prisma Error.

## Completion Report

### Status

Ready for Review — Attempt 1. Implementation and local validation passed; explicit developer completion pending.

### Files Changed
31 task-owned files: provider metadata/status contracts, authoring predicate and Connections UI, selected-shop header and production projection, preview/test-conversation contract consumers, injected fixtures and regression tests. Exact paths are recorded by implementation commit 97ab6ce.

### Work Completed
Added Shopify REFRESHABLE using the helper's 320000ms skew and future refresh expiry. Bounded id-only predicates detect missing/ambiguous offline rows without selecting credentials. Shared authoring predicate admits AVAILABLE/REFRESHABLE for Shopify and AVAILABLE for Woo. Header and Connections share provider-specific metadata labels and automatic-refresh guidance. Existing custom-domain mapping retained; malformed Shopify paths/ports rejected. ProductionStudioPage deep links admit usable hints; pending shop-switch results remain excluded.

Audited ShopifyAdminEditor and server actions: compiler actions retain independent role authorization; draft saves remain metadata-only and use guarded publication lifecycle; execution resolves current selected-shop credentials through Shared. Real published Shared 5.2.0 local fixture refreshes expired credentials once, persists rotated pair/expiry and resolves transaction before Admin request. Revoked refresh, revoked scope and foreign-shop cases fail safely. Native draft-save fixture asserts zero network calls.

### Validation Results
- `npm run typecheck`: passed.
- `npm run build`: passed; existing Nunjucks dynamic-import warning only.
- `npx tsc --noEmit`: passed.
- ESLint on all 11 changed production files: passed.
- `git diff --check`: passed.
- `npx vitest run tests/feature-configuration-page.test.tsx tests/store-integration.test.tsx tests/provider-tool-handoff.test.ts tests/connections-production.test.ts tests/provider-metadata-refreshable.test.ts tests/shop-execution-context.test.ts tests/selected-shop-navigation.test.tsx tests/shopify-session-coordination.test.ts tests/test-conversations-screen.test.tsx tests/tool-authoring-no-provider-io.test.ts tests/selected-shop-route.test.tsx tests/preview-page.test.tsx tests/studio-simulated-tool-tests.test.ts tests/commerce-lifecycle.test.ts`: 14 files / 153 tests passed.
- Metadata tests cover exactly now+320000 and +320001, expired/missing refresh, nonexpiring access, empty access, ambiguity and safe selects.

### Deviations / Assistance
Task is developer-owned; explicit user implementation authorization was fulfilled with material moda_commerce agent assistance. Root retained lifecycle/publication responsibility. Launcher synchronized isolated worktrees and set Attempt 1 before report-format failure; normalized report and published durable claim e26cc87b3 without incrementing attempt. Dependent preview/test-conversation consumers and fixtures required compatible local contract updates. No Shared dependency bump required for this independent UI task.

### Validation Limits / Unresolved Issues
Execution proof is local synthetic database/transport with the real published helper. No deployed Shopify or real PostgreSQL run is claimed; Shared PostgreSQL evidence belongs to the accepted Shared task, and terminal system validation remains separately manual-gated. No implementation issues remain.

### Git / VCS
Canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace.
Parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-063-COMMERCE-001.
Implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-063-COMMERCE-001.
Both branches: task/ARCH-063-COMMERCE-001. Launcher established/synchronized both worktrees before claim; recursive database submodule recorded bd2d09066a8eb178a56f48fbbf88df637c411059. Implementation baseline 76f46d2. Shared checkouts were not switched for implementation; no other task worktree reused.
Implementation: 97ab6ce; published origin/task/ARCH-063-COMMERCE-001.
Parent claim: e26cc87b3; this review report is published on the matching parent task branch, exact commit recorded by Git history.
Submodule gitlink staged: no. Merged/pushed main: no.

## Developer Self-Review - Passed
Attempt 1 local implementation meets the defined Commerce scope with required focused tests, production build and typecheck passing. Actual tool execution is exercised through published Shared using synthetic credentials and transport; deployed behavior is not asserted. Execution ownership remains developer. Explicit `/moda_developer_update ARCH-063-COMMERCE-001 complete` is pending.

## Architect Review
### Review Status
Pending
### Review Notes
Definition source audit completed; implementation not reviewed. Historical task acceptance preserved.
### Reviewed Files
Task touchpoints above; canonical MCP ARCH-061 reader inspected separately from stale shared checkout.
### Validation Reviewed
Task metadata/dependency/path checks only.
### Architecture Conformance
Single repository ownership; shared release gate explicit; independent Commerce correction not blocked on logging.
### Follow-up
None
