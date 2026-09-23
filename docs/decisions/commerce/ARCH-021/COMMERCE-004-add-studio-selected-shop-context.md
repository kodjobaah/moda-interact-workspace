---
id: ARCH-021-COMMERCE-004
architecture_id: ARCH-021
title: Add Studio-wide selected-shop navigation context
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-021-COMMERCE-003
enables:
  - ARCH-021-COMMERCE-005
created: 2026-09-23
updated: 2026-09-23
---

# Add Studio-wide selected-shop navigation context

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Add an explicit, refresh-stable selected-shop context to Commerce Studio so later authoring, live tool testing and conversation preview can operate against one server-validated shop without hidden global client state.

## Context

ARCH-021-COMMERCE-003 provides the server-validated shop context. The Studio currently has a Merchants page but no single shop selection that follows the user across Tools, Connections, Preview and other authoring surfaces.

For Phase 1 the canonical administrator selection is URL/navigation state using `shopId`. This makes the context explicit, shareable, compatible with refresh/back/forward navigation and easy for the server to validate. It is not durable business state.

A later merchant-facing Studio can derive/fix the shop from merchant authentication rather than exposing an admin selector; the downstream authoring APIs still consume the same validated shop context.

## Scope

- Introduce a Studio selected-shop provider/model sourced from a `shopId` query parameter.
- Resolve the selected id through ARCH-021-COMMERCE-003 before presenting it as valid context.
- Add a Studio shop selector suitable for platform admins.
- Preserve the selected `shopId` across primary Studio navigation, detail navigation and `returnTo` handoffs unless the destination deliberately changes/clears shop context.
- Use the existing Studio navigation blocker so changing shop cannot silently discard unsaved authoring state.
- Make selected shop identity/Shopify-offline-session availability accessible to later Tool/Preview components through a typed context.
- Do not silently auto-select the first shop.

## Out of Scope

- Persisting selection in PostgreSQL, Redis, cookies or localStorage.
- Live Shopify/external provider calls.
- Model/prompt configuration.
- Merchant authentication/authorization.
- Changing shop data itself.

## Requirements

- Canonical query parameter: `shopId=<Commerce Shop.id>`.
- The URL value is an identifier only; the displayed domain/label/plan comes from the server-validated context.
- Missing `shopId` means **no selected shop**, not an arbitrary default.
- Invalid/not-found `shopId` must be surfaced explicitly and must not fall back to a different shop.
- Navigation links preserve current `shopId` while retaining their own existing route/query state.
- Changing shop uses `StudioComposerContext.requestNavigation(...)` or equivalent guarded navigation so dirty/locked editors retain the accepted unsaved-operation protections.
- The context exposes offline Shopify session availability but never the session token.

## Work Items

- [x] Add typed selected-shop context/provider consuming the server contract from ARCH-021-COMMERCE-003.
- [x] Add a searchable/usable shop selector to the Studio shell or equivalent global authoring chrome.
- [x] Preserve `shopId` through sidebar links, detail links, Connections return navigation and Tool/Preview handoffs touched by this task.
- [x] Integrate shop changes with the existing navigation blocker/unknown-operation lock.
- [x] Add focused tests for no selection, valid selection, invalid selection, preservation across navigation and guarded shop changes.
- [x] Add narrow-layout/keyboard coverage consistent with current Studio navigation conventions.
- [x] Ensure an exactly resolved selected shop remains represented by the selector when it is outside the bounded list result.

## Interfaces / Contracts

Consumes:

- ARCH-021-COMMERCE-003 shop execution context
- existing `StudioComposerContext` navigation guard
- existing `StudioShell` navigation

Produces:

- one typed Studio selected-shop context for later ARCH-021 tasks.

No server/business-state persistence is introduced.

## Dependencies

- ARCH-021-COMMERCE-003

## Enables

- ARCH-021-COMMERCE-005

## Acceptance Criteria

- [x] Platform admin can select a real shop and the selected shop survives refresh/back/forward through `shopId` URL state.
- [x] Primary Studio navigation preserves the selected shop.
- [x] No shop is selected implicitly when `shopId` is absent or invalid.
- [x] Displayed shop/domain metadata always comes from the validated server context.
- [x] Changing shops while an editor is dirty/locked triggers the existing navigation protection rather than discarding state.
- [x] No Shopify token/session secret enters browser state.
- [x] A valid exact selected shop remains represented in the selector even when it is absent from the bounded list result.

## Validation

- [x] focused selected-shop context/navigation tests
- [x] focused `/connections/[id]` direct-entry/refresh regression with `shopId`
- [x] focused exact-selected-shop-outside-bounded-list regression
- [x] existing Studio shell/composer navigation tests affected by the change (44 passed; one unrelated auth-entrypoint baseline assertion failed)
- [x] targeted lint/typecheck for changed files (lint passed; repository typecheck remains on the documented baseline)
- [x] `git diff --check`

No live provider call is required.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin ARCH-021-COMMERCE-005.

## Implementation Notes

Do not add a hidden global “current shop” singleton. The URL identifier plus server resolution is the authoritative platform-admin Studio context for Phase 1.

## Completion Report

### Status

Ready for Review

### Files Changed

- `src/studio/contracts.ts`
- `src/studio/selected-shop.ts`
- `components/studio-selected-shop-context.tsx`
- `components/studio-composer-context.tsx`
- `components/studio-shell.tsx`
- `components/production-studio-page.tsx`
- `components/studio-screen.tsx`
- `app/features/page.tsx`
- `app/features/[id]/page.tsx`
- `app/tools/page.tsx`
- `app/tools/[id]/page.tsx`
- `app/capabilities/page.tsx`
- `app/capabilities/[id]/page.tsx`
- `app/releases/page.tsx`
- `app/releases/[id]/page.tsx`
- `app/explore/page.tsx`
- `app/shops/page.tsx`
- `app/shops/[id]/page.tsx`
- `app/connections/page.tsx`
- `app/connections/[id]/page.tsx`
- `app/preview/page.tsx`
- `app/styles.css`
- `tests/selected-shop-context.test.ts`
- `tests/selected-shop-navigation.test.tsx`
- `tests/selected-shop-route.test.tsx`

### Work Completed

- Added a typed `StudioShopSelection` provider and global keyboard-usable native selector. The selector uses only server-validated `ShopExecutionContext` metadata and has an explicit no-selection state.
- Added server-side `shopId` resolution for primary/detail Studio routes, Connections and Preview. Invalid ids remain unselected and show an explicit error; no first-shop fallback exists.
- Centralized `shopId` preservation in guarded composer navigation, including nested `returnTo`/`return` handoffs. Shop changes opt out only after constructing their explicit URL, so dirty and unknown-operation blockers remain authoritative.
- Added focused resolver and browser navigation tests covering absent, valid and invalid ids, query preservation, keyboard selection, dirty protection and locked-operation protection.
- Attempt 2 correction: `/connections/[id]` now accepts `shopId`, resolves the server-validated context through `getStudioServices()`, and passes `shopSelection` to `StudioShell` while preserving connection search, cursor and enabled state.
- Attempt 2 correction: exact selected shop context is merged into the bounded selector options by durable id, replacing any duplicate listed record with the exact server result; the accepted list bound is unchanged.
- Added direct-entry/refresh route coverage and an outside-bounded-list resolver regression.

Acceptance mapping:
- real selection and refresh/navigation state: `components/studio-selected-shop-context.tsx`, `components/studio-composer-context.tsx`, `tests/selected-shop-navigation.test.tsx`
- primary/detail/Connections/Preview preservation: `components/studio-composer-context.tsx`, route entry points, `tests/selected-shop-navigation.test.tsx`
- no implicit selection and invalid-id handling: `src/studio/selected-shop.ts`, `tests/selected-shop-context.test.ts`
- server-derived metadata and session availability: `src/studio/contracts.ts`, ARCH-021-COMMERCE-003 services consumed by `resolveStudioShopSelection`
- dirty/locked navigation protection: existing `StudioComposerContext` blocker path plus `tests/selected-shop-navigation.test.tsx`
- browser secret boundary: only bounded `ShopExecutionContext` metadata is passed to the provider; no session token/session payload is read by this task
- Attempt 2 review correction 1: `app/connections/[id]/page.tsx`, `tests/selected-shop-route.test.tsx`; focused route test passed and confirmed server resolution plus preserved connection list state.
- Attempt 2 review correction 2: `src/studio/selected-shop.ts`, `tests/selected-shop-context.test.ts`; focused resolver test passed and confirmed exact selected-shop representation and durable-id deduplication.

Prepared execution evidence:
- `prepared_execution=true`, `dependency_gate=passed`, `execution_state=claimed`, `attempt=2`, `executor=copilot` at handoff.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-004`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-004`.
- Branch: `task/ARCH-021-COMMERCE-004`.
- The deterministic launcher completed the required task-branch synchronization and recursive submodule initialization before this handoff; no startup resynchronization or submodule mutation was performed during Attempt 2.

### Validation Results

- `npm ci` — completed; npm reported the existing Node engine mismatch (required 24.19.0, current 24.21.0), peer-dependency warnings and audit warnings.
- `npm test -- --run tests/selected-shop-context.test.ts tests/selected-shop-navigation.test.tsx tests/selected-shop-route.test.tsx` — passed, 3 files / 9 tests.
- `npm test -- --run tests/studio-shell.test.tsx tests/studio-workspace.test.tsx tests/connections-ui.test.tsx tests/auth-entrypoints.test.ts` — 44 passed / 1 failed across 4 files; the unrelated existing auth-entrypoint assertion expects `createMcpService` while the current route contains `getCommerceBackend`.
- targeted `npx eslint app/connections/'[id]'/page.tsx src/studio/selected-shop.ts tests/selected-shop-context.test.ts tests/selected-shop-navigation.test.tsx tests/selected-shop-route.test.tsx` — passed with no errors or warnings.
- `npm run typecheck` — non-zero with 226 errors in 11 pre-existing Prisma/publication typing files; no selected-shop, Connections detail route, or focused test diagnostic was reported.
- `git diff --check` — passed.
- No Shopify, live provider or other third-party network call was made.

### Deviations

Repository typecheck remains blocked by the pre-existing Prisma/publication typing baseline; this task introduced no diagnostic in its changed TypeScript files. The affected Studio regression command retains one unrelated auth-entrypoint baseline failure described above.

### Assumptions

The accepted ARCH-021-COMMERCE-003 service contract is the authoritative source for shop metadata and offline-session availability. Native select type-ahead satisfies the Studio selector's keyboard/search usability requirement without adding client-side shop state.

### Unresolved Issues

No task-scoped unresolved issue.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 (`b67177d`; parent report `ce5461f`) satisfies the complete Attempt 1 correction contract and the original COMMERCE-004 acceptance contract.

The Connections detail route now accepts `shopId`, resolves it through the accepted ARCH-021-COMMERCE-003 server service, and passes the resulting `shopSelection` to `StudioShell`. Existing connection `search`, `cursor` and `enabled` state continue to be forwarded unchanged to `ConnectionsRouteClient`, so direct entry/refresh restores the selected-shop shell context without disturbing Connections list state.

`resolveStudioShopSelection(...)` now merges the exact server-resolved selected shop into the bounded selector option set by durable shop id. This preserves the accepted 100-shop discovery bound while ensuring a valid exact selection outside that page remains representable by the controlled selector. Existing duplicate listed records are replaced by the exact server-derived context rather than producing duplicate option ids.

The focused regressions prove direct-entry restoration and the outside-bounded-list case. The submitted Completion Report also records the launcher-prepared parent/implementation worktrees, task branch, synchronization and recursive-submodule preparation evidence requested after Attempt 1.

The Attempt 2 snapshot contains the already architect-accepted COMMERCE-001 production Connections boundary work after launcher synchronization; those inherited changes are not treated as new COMMERCE-004 implementation scope. No live provider execution, durable selected-shop persistence, model/prompt configuration, or credential/session secret exposure was introduced.

### Reviewed Files

- `moda-interact-commerce/app/connections/[id]/page.tsx`
- `moda-interact-commerce/src/studio/selected-shop.ts`
- `moda-interact-commerce/components/studio-selected-shop-context.tsx`
- `moda-interact-commerce/components/studio-composer-context.tsx`
- `moda-interact-commerce/components/studio-shell.tsx`
- `moda-interact-commerce/src/studio/contracts.ts`
- `moda-interact-commerce/src/commerce/integration/studio/services.ts`
- `moda-interact-commerce/src/commerce/integration/backend.ts`
- `moda-interact-commerce/tests/selected-shop-context.test.ts`
- `moda-interact-commerce/tests/selected-shop-navigation.test.tsx`
- `moda-interact-commerce/tests/selected-shop-route.test.tsx`

### Validation Reviewed

- Reported focused selected-shop validation: 3 files / 9 tests passed.
- Reported affected Studio/Connections regression validation: 44 passed / 1 unrelated existing auth-entrypoint baseline assertion failed.
- Reported targeted ESLint: passed.
- Reported `git diff --check`: passed.
- Reported repository typecheck remains non-zero with 226 diagnostics in 11 pre-existing Prisma/publication typing files; no selected-shop or Connections detail-route diagnostic was reported.
- Review archive contains no `node_modules`, so the architect did not independently rerun the Node/Vitest commands from this snapshot.
- Static review confirms the direct-detail route forwards `search`, `cursor` and `enabled`, resolves `shopId` server-side and passes `shopSelection` into `StudioShell`.
- Static review confirms exact selected-shop merging occurs by durable id without widening the accepted bounded discovery query.

### Architecture Conformance

Conformant. COMMERCE-004 now provides one explicit URL-owned, server-validated selected-shop context across the Studio, including Connections detail refresh/direct entry. The selector represents valid exact selections outside the bounded list, shop changes remain guarded by the existing dirty/locked navigation blocker, and only bounded shop/session-availability metadata enters browser state. No durable selected-shop state or live provider execution was introduced.

### Follow-up

ARCH-021-COMMERCE-004 is accepted Complete. Because ARCH-021-COMMERCE-001 and ARCH-020-COMMERCE-023 are already Complete, ARCH-021-COMMERCE-005 is now Ready. ARCH-021-COMMERCE-002 remains independently Ready. Do not begin COMMERCE-006 until COMMERCE-005 is architect-accepted Complete.
