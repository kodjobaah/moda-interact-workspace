---
id: ARCH-063-MCP-001
architecture_id: ARCH-063
title: wire safe shopify refresh event adapter
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
depends_on: ["ARCH-063-SHARED-002"]
enables: ["ARCH-063-SYSTEM-TEST-001"]
created: 2026-11-06
updated: 2026-11-06
---
# Wire safe shopify refresh event adapter

## Architecture
ARCH-063; docs/architecture/ARCH-063-refreshable-shopify-status-and-safe-refresh-events.md. Coordinator moda_architect.

## Objective
Wire safe shopify refresh event adapter using existing automatic coordinated refresh.

## Context
Metadata EXPIRED blocks authoring despite usable refresh; no safe refresh lifecycle events. Parent includes cross-service source audit and selected solution.

## Scope
moda-interact-mcp implementation/tests at exact touchpoints below; stale shared checkout is not a deployed observation.

| Existing file | Exact surface | Required change |
|---|---|---|
| moda-interact-mcp/src/runtime/prisma.ts | canonical provider composition from accepted ARCH-061 | Wire published hook at actual local-client factory, preserve selected shop context and typed errors. |


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
- [x] Wire published hook at actual local-client factory, preserve selected shop context and typed errors.

## Interfaces / Contracts
Commerce-local REFRESHABLE DTO/predicate and selector metadata, plus published optional Shared onEvent hook and exact frozen event schema above. Each consumer owns safe logger forwarding; provider/runtime credentials stay server-only. Exact version recorded by SHARED-002 before consumer pins.

## Dependencies
- ARCH-063-SHARED-002

## Enables
- ARCH-063-SYSTEM-TEST-001

## Acceptance Criteria
- [x] Canonical reader calls Shared getSession without expiry pre-rejection; event adapter receives one refresh lifecycle; scope/tenant/cancellation behavior retained.

## Validation
- [x] Run focused command `npx tsx --test tests/unit/connections/shopify-session-coordination.test.ts`; explicitly create additional focused fixture files where required. Shared also runs disposable PostgreSQL offline-token-provider.postgres.test.ts postcommit/concurrency fixtures.
- [x] Run owning declared typecheck/build appropriate to deployable change (Background build; System Test typecheck only); record exact commands. Capture event payloads with secret canaries and test hook failure isolation.

## Stop Condition
Complete defined work/criteria/validation, submit report for authorized review and STOP. Explicit developer completion required. System Test terminal/manually invoked; no enabled work auto-start.

## Implementation Notes
Dependency reconciliation (2026-11-06): ARCH-063-SHARED-002 is Accepted and explicitly developer-completed; published package @modainteract/moda-interact-shared@5.3.0 has verified downloadable immutable archive and Node hook exports. Task is Ready at unchanged Attempt 0, unclaimed. No automatic execution.

Use launcher-resolved isolated/synchronized task worktrees when execution requested. No implementation from definition. Preserve accepted locking/domain/SDK identities. Task-specific assertions are binding; no architecture selection delegated. Service logger uses published Shared logging, never raw provider/Prisma Error.

## Completion Report

### Status

Complete — Attempt 1 accepted and explicitly developer-completed on 2026-11-06.

### Files Changed
package.json, package-lock.json, src/runtime/prisma.ts, tests/unit/connections/shopify-session-coordination.test.ts.

### Work Completed
Pinned published Shared 5.3.0. The actual local-client factory installs an environment-scoped Shared logger hook forwarding exactly event, operationId, shopId, source, durationMs, outcome and reasonCode. Failed events use warn; started/committed use info. No raw errors or credentials are attached. Existing selected-shop reader, typed errors, tenant checks and automatic refresh coordination are retained.

### Validation Results
- `npx tsx --test tests/unit/connections/shopify-session-coordination.test.ts`: 16 passed.
- `npm run build`: passed, including Prisma generation.
- `npm run typecheck`: initially found optional test-hook typing; corrected. Final `./node_modules/.bin/tsc --noEmit -p tsconfig.json`: passed.
- Final `./node_modules/.bin/tsx --test tests/unit/connections/shopify-session-coordination.test.ts`: 16 passed, including frozen bounded lifecycle payload, secret canaries and throwing hook isolation.
- `git diff --check`: passed.
- Shared PostgreSQL fixtures belong to the accepted Shared dependency; not rerun in MCP.

### Deviations
Normalized task report blank lines required by launcher. Initial validation attempted before installation finished could not locate tsx/Prisma; successful reruns above supersede it.

### Assistance
Implementation assistance explicitly authorized by developer in this chat; execution ownership remains developer. No subagents used.

### Unresolved Issues
None. Local validation does not assert deployed observability.

### Git / VCS
Task branch: task/ARCH-063-MCP-001.
Canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace.
Parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-063-MCP-001.
Implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-063-MCP-001.
Both physical worktrees use task/ARCH-063-MCP-001. Shared checkouts were not switched or used for implementation; no other task worktree reused.
Launcher prepared/synchronized worktrees in initial attempt; implementation origin/main is an ancestor of HEAD. Parent task branch was published and contains the durable developer Attempt 1 claim. No new claim or attempt increment on resume.
Implementation commit: 7ab689b; remote origin/task/ARCH-063-MCP-001.
Parent report is committed/pushed separately on matching task branch; its exact commit is available in Git history.
No submodule gitlink staged. Neither branch merged to main.

## Developer Self-Review - Passed
Attempt 1 accepted for developer review: defined MCP work and acceptance criteria satisfied by factory wiring, published dependency pin and focused validation. Exactly one lifecycle is observed in the refresh fixture; original scope, tenant and cancellation cases pass. Explicit `/moda_developer_update ARCH-063-MCP-001 complete` is pending under completion_mode: developer.

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

## Developer Completion Decision
2026-11-06: Developer explicitly invoked `/moda_developer_update ARCH-063-MCP-001 complete`. Accepted Attempt 1 remains unchanged. Passing self-review is durable in parent commit 5f5ea8338; implementation 7ab689b3c3a907efb54dbcc99c36042a7cf5db48 matches origin/task/ARCH-063-MCP-001 and worktree is clean. Required work and validation are satisfied. Status complete; executor and claimed_at remain null. Neither main branch merged or pushed.

### Dependency-frontier reconciliation
ARCH-063-SYSTEM-TEST-001 remains Pending and manually gated: COMMERCE-001 Ready, SHOPIFY-001 In Progress and COMMERCE-002 Review are not Complete. BACKGROUND-001 and SHARED-002 are Complete. No downstream task promoted or started.
