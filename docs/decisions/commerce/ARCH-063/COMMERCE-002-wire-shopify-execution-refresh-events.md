---
id: ARCH-063-COMMERCE-002
architecture_id: ARCH-063
title: wire shopify execution refresh events
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: review
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on: ["ARCH-063-SHARED-002"]
enables: ["ARCH-063-SYSTEM-TEST-001"]
created: 2026-11-06
updated: 2026-11-06
---
# Wire shopify execution refresh events

## Architecture
ARCH-063; docs/architecture/ARCH-063-refreshable-shopify-status-and-safe-refresh-events.md. Coordinator moda_architect.

## Objective
Wire shopify execution refresh events using existing automatic coordinated refresh.

## Context
Metadata EXPIRED blocks authoring despite usable refresh; no safe refresh lifecycle events. Parent includes cross-service source audit and selected solution.

## Scope
moda-interact-commerce implementation/tests at exact touchpoints below; stale shared checkout is not a deployed observation.

| Existing file | Exact surface | Required change |
|---|---|---|
| moda-interact-commerce/src/commerce/preview/local-provider-composition.ts | factory composition | Pass safe event adapter using existing Shared logger. |
| moda-interact-commerce/src/commerce/preview/local-policy-providers.ts | fallback provider factory | Pass same adapter; one factory execution path logs once, no status events. |


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
- [x] Pass safe event adapter using existing Shared logger.
- [x] Pass same adapter; one factory execution path logs once, no status events.

## Interfaces / Contracts
Commerce-local REFRESHABLE DTO/predicate and selector metadata, plus published optional Shared onEvent hook and exact frozen event schema above. Each consumer owns safe logger forwarding; provider/runtime credentials stay server-only. Exact version recorded by SHARED-002 before consumer pins.

## Dependencies
- ARCH-063-SHARED-002

## Enables
- ARCH-063-SYSTEM-TEST-001

## Acceptance Criteria
- [x] Actual expired execution logs started/committed with selected shop ID and refreshed expiry; metadata render logs no refresh.
- [x] Injected commit/network failure emits failed only; secret canaries absent.

## Validation
- [x] Run focused command `npx vitest run tests/shopify-session-coordination.test.ts`; explicitly create additional focused fixture files where required. Shared also runs disposable PostgreSQL offline-token-provider.postgres.test.ts postcommit/concurrency fixtures.
- [x] Run owning declared typecheck/build appropriate to deployable change (Background build; System Test typecheck only); record exact commands. Capture event payloads with secret canaries and test hook failure isolation.

## Stop Condition
Complete defined work/criteria/validation, submit report for authorized review and STOP. Explicit developer completion required. System Test terminal/manually invoked; no enabled work auto-start.

## Implementation Notes
Execution ownership amendment (2026-11-06): developer explicitly requested `/moda-task ARCH-063-COMMERCE-002` implementation and authorized synchronization plus task claim/source/review publication. Delegate to moda_commerce via canonical agent preparation; retain completion_mode developer. Scope remains execution event wiring only; COMMERCE-001 metadata/UI changes excluded. No attempt or dependency change.

Dependency reconciliation (2026-11-06): ARCH-063-SHARED-002 is Accepted and explicitly developer-completed; published package @modainteract/moda-interact-shared@5.3.0 has verified downloadable immutable archive and Node hook exports. Task is Ready at unchanged Attempt 0, unclaimed. No automatic execution.

Use launcher-resolved isolated/synchronized task worktrees when execution requested. No implementation from definition. Preserve accepted locking/domain/SDK identities. Task-specific assertions are binding; no architecture selection delegated. Service logger uses published Shared logging, never raw provider/Prisma Error.

## Completion Report
### Status
Ready for Review
### Files Changed
- package.json and package-lock.json: exact published Shared 5.3.0 pin.
- src/commerce/preview/shopify-refresh-events.ts: domain semantic logger adapter.
- src/commerce/preview/local-provider-composition.ts and local-policy-providers.ts: hook wiring.
- tests/shopify-refresh-events.test.ts: real published-provider composition fixtures.
### Work Completed
Primary and fallback factories pass one safe observer to the published Shared provider. Adapter uses existing Shared logging implementation with canonical Commerce identity and factory environment. Explicit field allowlist excludes domain, session ID, credentials, scopes and errors. Started/committed use info; failed uses warn. Primary passes its provider into fallback registrations, so no duplicate observer/provider is created. Metadata/status paths unchanged; no COMMERCE-001 work. Existing refresh coordination, authorization, provider calls and caller errors preserved.
### Validation Results
- `npx vitest run tests/shopify-session-coordination.test.ts tests/shopify-refresh-events.test.ts`: PASS 2 files, 10 tests, no skips. Real published provider through both factory paths verifies actual expired refresh, persisted expiry, one safe pair, metadata/reuse silence, commit/network UNKNOWN failure without committed, secret canary absence.
- `npm run prisma:generate`: PASS using recorded nested database schema; generated local client only. Initial fresh-install focused collection needed this generation, then passed.
- `npm run typecheck:build`: PASS (schema sync, Next route typegen, production TypeScript).
- Focused strengthened logging-envelope assertions: PASS 1 file, 6 tests; canonical service/environment and exact safe field keys. Used exact previously bootstrap-resolved Node executable with architect approval after redundant bootstrap delay; no runtime selection/PATH change.
- `git diff --check`: PASS.
- Published package install via `npm install @modainteract/moda-interact-shared@5.3.0 --save-exact --ignore-scripts` succeeded. npm reported 35 audit issues (18 moderate,16 high,1 critical); no unrelated dependency remediation attempted. Peer/deprecation warnings recorded; lock diff limited to Shared version/registry integrity.
### Deviations
Added a separate focused real-provider fixture because existing coordination test mocks Shared factory. No duplicate Shared mechanism. Consumer test uses mocked local persistence/network and production composition/policy adapter/Shared provider/logger; no live provider calls. Shared postcommit/PostgreSQL behavior already validated by accepted SHARED-001; no cross-repository rerun.
### Assumptions
Refresh logs are best effort process-local diagnostics; no deployment state inferred from local checks. Definition dispatch layer is mocked solely to reach registered policy execution in primary factory fixture.
### Unresolved Issues
None.
### Architectural Concerns
None. No cross-repository code, database schema, UI/metadata or deployment changes.
### Git / VCS
Task branch: task/ARCH-063-COMMERCE-002
Physical worktree isolation:
- canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
- parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-063-COMMERCE-002
- implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-063-COMMERCE-002
- parent and implementation branches: task/ARCH-063-COMMERCE-002
- shared workspace/source checkout switched or mutated: no
- another task worktree reused: no
Start-of-attempt synchronization (launcher packet):
- parent/implementation remote task fast-forward: not-needed
- parent/implementation origin/main incorporated: already-current
- recursive submodule sync/update: passed; database bd2d09066a8eb178a56f48fbbf88df637c411059; status ready
- Attempt 1 claim f9e4a608b92fd6012db3c9dbb082521d869fa2ff pushed
Implementation commit: 4b2abdd (full hash in task history); pushed to origin/task/ARCH-063-COMMERCE-002.
Parent report commit follows this edit on matching task branch. Submodule gitlink staged: no. Main merges: none.

## Architect Review
### Review Status
Accepted — explicit developer completion pending.
### Review Notes
2026-11-06 moda_architect inspected actual implementation 4b2abdde15c6612b96f95fd3ec23dcf3a4c3dc2a and report 8c667804512d4c4af1e40e233273abd1a062ed7a. Both factory paths wire published Shared 5.3.0 hook through one small semantic adapter using Shared logging. Explicit field projection preserves safe correlation/outcome metadata without error, body, domain, session or credentials. Started/committed log info and failed logs warn. Primary provider injection prevents duplicate fallback construction; no metadata refresh/event path introduced. No implementation corrections required.
### Reviewed Files
- src/commerce/preview/shopify-refresh-events.ts
- src/commerce/preview/local-provider-composition.ts
- src/commerce/preview/local-policy-providers.ts
- tests/shopify-refresh-events.test.ts
- package.json/package-lock.json and task Completion Report.
### Validation Reviewed
Focused 10/10 and strengthened envelope fixture 6/6 passed, production typecheck:build passed, Prisma generation and whitespace validation passed. Inspected real published-provider fixtures through both composition paths for metadata/reuse silence, committed expiry and selected Shop correlation, network/commit UNKNOWN failures with no committed event and secret-canary exclusion. Accepted Shared PostgreSQL fixtures already cover actual database postcommit/concurrency mechanics; consumer did not duplicate cross-repository validation.
### Architecture Conformance
Conforms to ARCH-063 bounded Commerce consumer wiring; consumes exact published package and canonical Shared logger. No generic logger fork, lock changes, UI/status scope crossover into COMMERCE-001, schema, deployment or gitlink changes. Canonical launcher worktrees/start synchronization/database submodule evidence verified. Local results make no deployed-state claim.
### Follow-up
Task remains review under completion_mode developer. Explicit completion: `/moda_developer_update ARCH-063-COMMERCE-002 complete`. System Test remains Pending on incomplete dependencies/manual-gated; no follow-on work starts automatically.
