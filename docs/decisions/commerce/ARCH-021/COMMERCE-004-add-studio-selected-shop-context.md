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
status: in_progress
priority: 30
executor: copilot
claimed_at: 2026-09-23T10:41:24Z
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

- [ ] Add typed selected-shop context/provider consuming the server contract from ARCH-021-COMMERCE-003.
- [ ] Add a searchable/usable shop selector to the Studio shell or equivalent global authoring chrome.
- [ ] Preserve `shopId` through sidebar links, detail links, Connections return navigation and Tool/Preview handoffs touched by this task.
- [ ] Integrate shop changes with the existing navigation blocker/unknown-operation lock.
- [ ] Add focused tests for no selection, valid selection, invalid selection, preservation across navigation and guarded shop changes.
- [ ] Add narrow-layout/keyboard coverage consistent with current Studio navigation conventions.

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
- [ ] Primary Studio navigation preserves the selected shop.
- [ ] No shop is selected implicitly when `shopId` is absent or invalid.
- [ ] Displayed shop/domain metadata always comes from the validated server context.
- [ ] Changing shops while an editor is dirty/locked triggers the existing navigation protection rather than discarding state.
- [ ] No Shopify token/session secret enters browser state.

## Validation

- [ ] focused selected-shop context/navigation tests
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

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
