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
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 1
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
- [ ] Preserve `shopId` through sidebar links, detail links, Connections return navigation and Tool/Preview handoffs touched by this task.
- [x] Integrate shop changes with the existing navigation blocker/unknown-operation lock.
- [x] Add focused tests for no selection, valid selection, invalid selection, preservation across navigation and guarded shop changes.
- [x] Add narrow-layout/keyboard coverage consistent with current Studio navigation conventions.
- [ ] Ensure an exactly resolved selected shop remains represented by the selector when it is outside the bounded list result.

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

- [ ] Platform admin can select a real shop and the selected shop survives refresh/back/forward through `shopId` URL state.
- [x] Primary Studio navigation preserves the selected shop.
- [x] No shop is selected implicitly when `shopId` is absent or invalid.
- [x] Displayed shop/domain metadata always comes from the validated server context.
- [x] Changing shops while an editor is dirty/locked triggers the existing navigation protection rather than discarding state.
- [x] No Shopify token/session secret enters browser state.
- [ ] A valid exact selected shop remains represented in the selector even when it is absent from the bounded list result.

## Validation

- [ ] focused selected-shop context/navigation tests
- [ ] focused `/connections/[id]` direct-entry/refresh regression with `shopId`
- [ ] focused exact-selected-shop-outside-bounded-list regression
- [ ] existing Studio shell/composer navigation tests affected by the change
- [ ] targeted lint/typecheck for changed files
- [ ] `git diff --check`

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
- `app/preview/page.tsx`
- `app/styles.css`
- `tests/selected-shop-context.test.ts`
- `tests/selected-shop-navigation.test.tsx`

### Work Completed

- Added a typed `StudioShopSelection` provider and global keyboard-usable native selector. The selector uses only server-validated `ShopExecutionContext` metadata and has an explicit no-selection state.
- Added server-side `shopId` resolution for primary/detail Studio routes, Connections and Preview. Invalid ids remain unselected and show an explicit error; no first-shop fallback exists.
- Centralized `shopId` preservation in guarded composer navigation, including nested `returnTo`/`return` handoffs. Shop changes opt out only after constructing their explicit URL, so dirty and unknown-operation blockers remain authoritative.
- Added focused resolver and browser navigation tests covering absent, valid and invalid ids, query preservation, keyboard selection, dirty protection and locked-operation protection.

Acceptance mapping:
- real selection and refresh/navigation state: `components/studio-selected-shop-context.tsx`, `components/studio-composer-context.tsx`, `tests/selected-shop-navigation.test.tsx`
- primary/detail/Connections/Preview preservation: `components/studio-composer-context.tsx`, route entry points, `tests/selected-shop-navigation.test.tsx`
- no implicit selection and invalid-id handling: `src/studio/selected-shop.ts`, `tests/selected-shop-context.test.ts`
- server-derived metadata and session availability: `src/studio/contracts.ts`, ARCH-021-COMMERCE-003 services consumed by `resolveStudioShopSelection`
- dirty/locked navigation protection: existing `StudioComposerContext` blocker path plus `tests/selected-shop-navigation.test.tsx`
- browser secret boundary: only bounded `ShopExecutionContext` metadata is passed to the provider; no session token/session payload is read by this task

### Validation Results

- `npm ci` — completed; npm reported the existing Node engine mismatch (required 24.19.0, current 24.21.0), peer-dependency warnings and audit warnings.
- `npm test -- --run tests/selected-shop-context.test.ts tests/selected-shop-navigation.test.tsx` — passed, 2 files / 7 tests.
- `npm test -- --run tests/studio-workspace.test.tsx tests/connections-ui.test.tsx tests/studio-integration.test.ts` — passed, 3 files / 47 tests.
- targeted `npx eslint` over all changed TypeScript/TSX files — passed with no errors or warnings. CSS was excluded because the repository ESLint configuration has no CSS matcher.
- `npm run typecheck` — non-zero on the existing generated-Prisma/publication typing baseline across pre-existing files; no selected-shop or route-file diagnostic remained after the local shell fix.
- `git diff --check` — passed.
- No Shopify, live provider or other third-party network call was made.

### Deviations

Repository typecheck remains blocked by the pre-existing Prisma/publication typing baseline; this task introduced no diagnostic in its changed TypeScript files.

### Assumptions

The accepted ARCH-021-COMMERCE-003 service contract is the authoritative source for shop metadata and offline-session availability. Native select type-ahead satisfies the Studio selector's keyboard/search usability requirement without adding client-side shop state.

### Unresolved Issues

No task-scoped unresolved issue.

### Architectural Concerns

None.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 (`654141e`; parent report `5e12ea8`) establishes most of the intended selected-shop navigation model, but two task-scoped correctness gaps prevent acceptance.

1. `app/connections/[id]/page.tsx` is not wired to the selected-shop resolver. The list route accepts `shopId`, resolves it through `resolveStudioShopSelection(...)` and passes `shopSelection` into `StudioShell`; the detail route still accepts only `search`/`cursor`/`enabled` and renders `StudioShell` without `shopSelection`. Existing `StudioNavigationLink` handling correctly preserves `shopId` into the detail URL, but refreshing/directly entering that preserved URL causes the shell/provider to fall back to an empty selection. This breaks the refresh-stable Studio-wide context and the explicit Connections/detail-navigation requirement.
2. Production shop discovery is bounded (`backend.inspection.listShops` takes at most 100 rows), while exact `shopId` resolution is independent. `resolveStudioShopSelection(...)` currently returns the exact `selectedShop` separately but does not ensure it is present in the selector's `shops` collection. A valid selected shop outside the bounded list can therefore resolve server-side while the controlled selector has no matching option. Merge the exact selected context into the option set by id when necessary. Do not widen/remove the accepted server list bound and do not redesign the selector for this correction.

The earlier apparent concern about raw detail links is not a defect: `components/studio-workspace.tsx` aliases `StudioNavigationLink` as `Link`, so those links already traverse the shop-preserving navigation path. Dirty/locked shop changes also reuse the accepted navigation blocker, and the selected-shop browser contract contains bounded metadata only.

The Completion Report again omits the launcher's exact prepared parent/implementation worktree, synchronization and recursive-submodule packet fields. Because source correction is already required, Attempt 2 should add those evidence fields rather than leaving them for architect reconciliation. Do not create code churn solely for the evidence update.

### Reviewed Files

- `moda-interact-commerce/src/studio/selected-shop.ts`
- `moda-interact-commerce/src/studio/contracts.ts`
- `moda-interact-commerce/components/studio-selected-shop-context.tsx`
- `moda-interact-commerce/components/studio-composer-context.tsx`
- `moda-interact-commerce/components/studio-shell.tsx`
- `moda-interact-commerce/components/production-studio-page.tsx`
- `moda-interact-commerce/components/studio-screen.tsx`
- `moda-interact-commerce/components/studio-workspace.tsx`
- `moda-interact-commerce/app/connections/page.tsx`
- `moda-interact-commerce/app/connections/[id]/page.tsx`
- `moda-interact-commerce/app/preview/page.tsx`
- primary/detail Studio route entry points under `app/features`, `app/tools`, `app/capabilities`, `app/releases`, `app/explore` and `app/shops`
- `moda-interact-commerce/src/commerce/integration/backend.ts` (bounded shop-list behaviour)
- `moda-interact-commerce/tests/selected-shop-context.test.ts`
- `moda-interact-commerce/tests/selected-shop-navigation.test.tsx`

### Validation Reviewed

- Reported focused selected-shop validation: 2 files / 7 tests passed.
- Reported affected Studio regression validation: 3 files / 47 tests passed.
- Reported changed-file ESLint: passed.
- Reported `git diff --check`: passed.
- Reported repository typecheck remains non-zero only on the documented pre-existing Prisma/publication typing baseline; no selected-shop diagnostic was reported.
- Review archive contains no `node_modules`, so the architect did not independently rerun the Node/Vitest commands from this snapshot.
- Static review confirms normal `StudioWorkspace` detail links already use `StudioNavigationLink` through its local `Link` alias; the blocking defect is specifically the missing server resolution/composition on `/connections/[id]`.

### Architecture Conformance

Partial. The URL-owned `shopId` model, server-derived metadata, primary navigation preservation, nested return-parameter preservation, dirty/locked transition protection and token/session non-disclosure conform to ARCH-021. Acceptance is withheld because the Connections detail route does not restore the validated context on refresh/direct entry and because an exact valid selection can fall outside the bounded selector option list.

### Follow-up

Return the same task to Attempt 2. Required correction contract:

- update `app/connections/[id]/page.tsx` to accept `shopId`, resolve it with the accepted ARCH-021-COMMERCE-003 service, and pass the resulting `shopSelection` to `StudioShell` while preserving existing connection list-state semantics;
- ensure `resolveStudioShopSelection(...)` (or the equivalent bounded presentation layer) includes the exact selected context in the selector option set when the selected id is valid but absent from the bounded list result; deduplicate by durable shop id;
- add a focused regression proving `/connections/[id]?shopId=<id>` restores the selected server context on refresh/direct entry;
- add a focused regression where list results omit the exact selected shop but exact resolution succeeds, proving the selector model still represents that selected shop;
- rerun the task-scoped selected-shop/Studio validation, lint/typecheck/diff checks and reconcile the Validation checklist;
- record the launcher-prepared parent/implementation worktree, synchronization and recursive-submodule evidence in the Completion Report.

Keep `attempt: 1` until the authorized executor reclaims the task; the next claim increments it to Attempt 2. COMMERCE-005 remains dependency-gated until this task and its other prerequisites are Complete.
