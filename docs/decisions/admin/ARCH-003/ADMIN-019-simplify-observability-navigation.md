---
id: ARCH-003-ADMIN-019
architecture_id: ARCH-003
title: Simplify Observability navigation and remove queue CTA from Grafana page
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: review
priority: 40
executor: copilot
claimed_at: 2026-09-05T06:29:59Z
attempt: 1
depends_on:
  - ARCH-003-ADMIN-018
enables:
  - ARCH-003-SYSTEM-TEST-001
created: 2026-09-05
updated: 2026-09-05T06:31:38Z
---

# Simplify Observability navigation and remove queue CTA from Grafana page

## Architecture

`docs/architecture/ARCH-003-admin-operational-ui.md`

## Runtime issue

The current left navigation is:

```text
Observability
  Overview
  Shopify Queues
  Grafana
```

and the parent Observability link opens `/observability`.

The `/observability` Grafana/status page also contains another Shopify Queues
card with an `Open Shopify Queues` button.

This is redundant and makes the default Observability destination unclear.

## Required navigation

The left navigation must become:

```text
Tenant Directory

Observability
  Shopify Queues
  Grafana
```

There is no `Overview` child.

Clicking the parent:

```text
Observability
```

must navigate directly to:

```text
/observability/queues
```

so Shopify Queues is the default Observability workspace.

## Grafana navigation

Keep the existing Grafana child behavior:

- when a validated Grafana destination exists, use the existing safe external
  destination/new-tab behavior;
- when Grafana is not configured and the existing safe fallback is
  `/observability`, that protected route may continue to show its
  Grafana configuration/unavailable state.

Do not weaken URL validation, authentication, or private telemetry boundaries.

## Grafana/status page cleanup

On:

```text
/observability
```

remove the internal Shopify Queues promotional card/CTA, including the content:

```text
Shopify Queues
Inspect read-only queue activity and refresh diagnostics.
Open Shopify Queues
```

Keep:

- environment label;
- Grafana configuration warning;
- validated Grafana dashboard/log/trace/metric links;
- private telemetry/authentication explanation.

## Queue page

`/observability/queues` remains the protected Shopify Queues route.

Do not change:

- queue snapshots;
- filters;
- Failed / Active / Waiting / Delayed;
- drawer behavior;
- pagination;
- job detail;
- tenant attribution.

If the queue page still renders a breadcrumb/control labelled `Observability`
that navigates to `/observability`, remove that redundant breadcrumb. Do not
leave a visible Observability navigation control that contradicts the new
default destination.

## Tests

Update navigation/security regression coverage to prove:

- [x] sidebar contains Tenant Directory;
- [x] Observability parent href is `/observability/queues`;
- [x] expanded Observability children contain Shopify Queues and Grafana;
- [x] expanded Observability children do not contain Overview;
- [x] Shopify Queues child points to `/observability/queues`;
- [x] existing safe Grafana href handling remains;
- [x] `/observability` retains the platform-admin guard;
- [x] ObservabilityPanel no longer contains the Shopify Queues CTA/card;
- [x] `/observability/queues` remains platform-admin protected;
- [x] queue-monitor functionality is untouched;
- [x] no fabricated Dashboard/Billing/Settings destinations are added.

## Acceptance Criteria

- [x] Clicking Observability lands on Shopify Queues.
- [x] Overview is removed from the left submenu.
- [x] Shopify Queues remains visible as the queue child.
- [x] Grafana remains accessible from the left submenu.
- [x] Grafana/status page contains no link/card back to Shopify Queues.
- [x] Existing Grafana security/configuration behavior is preserved.
- [x] Existing queue diagnostics do not regress.
- [x] tests pass.
- [x] TypeScript passes.
- [x] lint passes apart from previously accepted warnings.
- [x] build passes.
- [x] `git diff --check` passes.

## Completion Report

### Status

Ready for Review.

### Files Changed

- `src/components/admin/sidebar.tsx`
- `src/components/admin/observability-panel.tsx`
- `src/app/(protected)/observability/queues/page.tsx`
- `tests/security/admin-sidebar-navigation.test.mjs`
- `tests/security/grafana-observability.test.mjs`

### Work Completed

- Observability parent navigation now opens `/observability/queues`.
- Removed the Overview submenu entry and the redundant queue-page breadcrumb.
- Removed the Shopify Queues promotional card and CTA from the Grafana/status
  page while retaining Grafana links, configuration state, and private
  telemetry messaging.
- Preserved protected route guards, validated Grafana destination behavior, and
  all queue-monitor functionality.
- Added precise navigation and CTA regression assertions.

### Validation Results

- `npm test`: 74 tests passed.
- `npm run lint`: passed with two previously accepted React hook dependency
  warnings in `src/components/admin/queue-monitor.tsx`.
- `npm run build`: passed with existing Next.js workspace-root and optional
  BullMQ `@valkey/valkey-glide` warnings.
- TypeScript diagnostics: no errors in changed source files.
- `git diff --check`: passed.

### Deviations

None.

### Assumptions

The unconfigured Grafana fallback remains `/observability` as explicitly
allowed by the task.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending architect review
