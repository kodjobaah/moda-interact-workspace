---
id: ARCH-003-ADMIN-010
architecture_id: ARCH-003
title: Align Admin sidebar shell and Observability navigation with approved UI
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 40
executor: copilot
claimed_at: 2026-09-04T20:53:22Z
attempt: 1
depends_on:
  - ARCH-003-ADMIN-007
enables:
  - ARCH-003-ADMIN-011
created: 2026-09-04
updated: 2026-09-04
---

# Align Admin sidebar shell and Observability navigation with approved UI

## Objective

Bring the current left Admin navigation shell materially into line with the
approved visual reference, while making Shopify Queues a first-class nested
Observability destination rather than only a card/button reached from the
generic Observability overview.

## Visual reference

Use:

`docs/architecture/ARCH-003-shopify-queues-approved-reference.png`

The reference is acceptance guidance for information architecture and active
navigation state.

## Scope

- preserve `/observability` as the Observability overview;
- rework the left navigation from the current flat two-link treatment into the
  approved persistent sidebar composition;
- preserve Moda Interact branding at the top;
- preserve Tenant Directory as a real destination;
- render Observability as a grouped/expanded parent with nested:
  - Overview
  - Shopify Queues
  - Grafana;
- expose Shopify Queues directly from that nested navigation;
- expose the existing Grafana destination/behavior without fabricating a route;
- show the correct nested active state for Overview vs Shopify Queues;
- add the administrator identity/profile treatment anchored at the bottom of
  the sidebar using already-available authenticated/admin identity data;
- preserve authentication and responsive behavior;
- maintain a stable sidebar width/layout compatible with the later right-hand
  Queue details drawer;
- add focused sidebar/navigation tests.

## Requirements

- the left sidebar must materially match the approved shell: brand/header,
  navigation spacing, icon+label rows, grouped Observability treatment, nested
  children, active states, and bottom administrator identity area;
- Observability must visibly expose `Overview`, `Shopify Queues`, and `Grafana`
  affordances in a coherent nested/grouped navigation treatment;
- `/observability/queues` must be directly discoverable without first reading an
  overview card;
- the active Shopify Queues child must be visually distinct while its
  Observability parent remains visibly active/expanded;
- the sidebar must remain visually stable when the later right-hand Queue
  details drawer opens;
- the current repository has no real Dashboard, Billing, or Settings routes:
  do not add dead links merely because they appear in the mockup;
- record Dashboard/Billing/Settings as explicit visual-reference deviations in
  the Completion Report unless real destinations are independently available
  by execution time;
- do not alter queue APIs, Redis readers, or failed-job logic;
- do not redesign the Shopify Queues main content in this task.

## Acceptance Criteria

- [x] Sidebar uses the approved persistent branded vertical-shell composition.
- [x] Tenant Directory remains functional as a real destination.
- [x] Observability group exposes Overview and Shopify Queues directly.
- [x] Grafana remains discoverable using the existing valid destination/overview behavior.
- [x] Active navigation state distinguishes `/observability` and `/observability/queues`.
- [x] Observability remains visibly expanded/active when Shopify Queues is selected.
- [x] Administrator identity/profile treatment is anchored at the bottom.
- [x] Sidebar remains stable at desktop/laptop widths.
- [x] No dead/fabricated Dashboard/Billing/Settings routes are added.
- [x] Any missing mockup destinations are explicitly listed as visual deviations.
- [x] Focused sidebar/navigation tests pass.
- [x] Full Admin tests pass.
- [x] Typecheck, lint, production build, and `git diff --check` pass.

## Completion Report

### Status
Ready for Review.

### Implementation

- Reworked the persistent Admin sidebar into a stable branded desktop rail with
  Tenant Directory and grouped Observability navigation.
- Added nested Overview, Shopify Queues, and Grafana destinations with parent
  expansion and distinct Overview/Shopify Queues active states.
- Preserved the existing validated Grafana destination behavior, falling back to
  the protected Observability overview when no external Grafana destination is
  configured.
- Moved sign-out into a bottom administrator identity/profile treatment and
  surfaced the authorized administrator role.
- Added focused source-level sidebar/navigation coverage.

### Files Changed

- `src/components/admin/admin-shell.tsx`
- `src/components/admin/sidebar.tsx`
- `src/components/admin/icons.tsx`
- `src/app/(protected)/observability/queues/page.tsx`
- `tests/security/admin-sidebar-navigation.test.mjs`

### Validation

- Focused sidebar/Grafana tests: passed.
- Full Admin test suite: 55 passed.
- `npm exec tsc -- --noEmit`: passed.
- `npm run lint`: passed with two existing `react-hooks/exhaustive-deps`
  warnings in `src/components/admin/queue-monitor.tsx`.
- `npm run build`: passed with the existing multiple-lockfile workspace-root
  warning and optional BullMQ `@valkey/valkey-glide` warning.
- `git diff --check`: passed.

### Deviations

- Dashboard, Billing, and Settings remain absent from the sidebar because the
  repository has no real destinations for them. No dead links were fabricated.

### Assumptions and Unresolved Issues

- The existing authenticated principal exposes the authorized role but not a
  display name through the current shell-facing API, so the profile treatment
  uses the generic Administrator label and role.
- No queue API, Redis reader, failed-job logic, or Shopify Queues main-content
  redesign was included.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 is architect-accepted Complete.

The reviewed implementation materially aligns the existing Admin shell with the
approved left-navigation treatment without fabricating product destinations:

- Moda Interact branding remains anchored at the top of a stable desktop rail;
- Tenant Directory remains a real top-level destination;
- Observability is rendered as a grouped parent;
- Overview, Shopify Queues, and Grafana are exposed as nested children while the
  Observability group is active;
- `/observability` and `/observability/queues` have distinct nested active states;
- Shopify Queues is directly discoverable from the sidebar;
- Grafana reuses the existing validated destination and safely falls back to the
  Observability overview when no external destination is configured;
- the sidebar uses a fixed-width/shrink-safe desktop composition compatible with
  the upcoming right-hand queue drawer;
- administrator identity/role treatment is anchored at the bottom;
- Dashboard, Billing, and Settings were not fabricated because the repository
  has no real routes for those destinations.

The current shell-facing `PlatformAdminPrincipal` exposes `id`, `role`, and
development-bypass state, but no display name. The generic Administrator label
is therefore an accepted truthful deviation from the mockup rather than an
invented identity.

### Reviewed Files

- `moda-interact-admin/src/components/admin/admin-shell.tsx`
- `moda-interact-admin/src/components/admin/sidebar.tsx`
- `moda-interact-admin/src/components/admin/icons.tsx`
- `moda-interact-admin/src/app/(protected)/observability/queues/page.tsx`
- `moda-interact-admin/src/lib/auth/platform-admin.ts`
- `moda-interact-admin/tests/security/admin-sidebar-navigation.test.mjs`
- `docs/decisions/admin/ARCH-003/ADMIN-010-align-observability-navigation.md`

### Validation Reviewed

Implementing-agent evidence records:

- full Admin tests: 55 passed;
- TypeScript: pass;
- lint: pass with the two existing exhaustive-deps warnings;
- production build: pass;
- `git diff --check`: pass.

Focused navigation coverage verifies the nested Observability destinations,
active queue state, stable desktop rail, bottom administrator treatment,
Grafana fallback behavior, and absence of fabricated Dashboard/Billing/Settings
routes.

### Architecture Conformance

Accepted.

The task is confined to the Admin shell/navigation presentation and does not
alter Redis readers, queue APIs, failed-job security boundaries, or the Shopify
Queues main-content composition reserved for ADMIN-011.

### Follow-up

`ARCH-003-ADMIN-011` is now Ready.

ADMIN-011 must change only the Shopify Queues page composition into the approved
main-table + right-hand Queue details drawer shell. Drawer metrics/recent
failures remain ADMIN-012.
