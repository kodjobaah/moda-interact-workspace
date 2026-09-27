---
id: ARCH-023-SHOPIFY-004
architecture_id: ARCH-023
title: Build Merchant Knowledge settings UI
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-SHOPIFY-003
enables:
  - ARCH-023-SYSTEM-TEST-002
created: 2026-09-27
updated: 2026-09-27
---

# Build Merchant Knowledge settings UI

## Architecture

Architecture ID:

`ARCH-023`

Architecture document:

`docs/architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md`

Coordinator:

`moda_architect`

## Objective

Build the Shopify merchant UI for configuring logical Merchant Knowledge entries, locale URLs, purposes, ordering, status and manual refresh.

## Context

The UI reflects authoritative server state from SHOPIFY-003. It must describe entries rather than Commerce capabilities and must not imply that page content grants actions.

## Scope

- Display feature availability and current `maxKnowledgeEntries`.
- Add/edit/remove/reorder logical entries with merchant-facing name and allow-listed purpose.
- Manage locale sources using supported Moda locales and show active/pending/failed revision status.
- Expose manual Refresh and last successful fetch metadata.
- Show truncation/content-unit usage and plan-ineligible stored entries where applicable.

## Out of Scope

- URL fetching/previewing page bodies in browser.
- Prompt authoring.
- Automatic translation of merchant web content.

## Requirements

- Hidden/disabled feature cannot be configured.
- UI never treats a pending/failed revision as active.
- Downgrade state explains which deterministic first-N entries remain entitled without deleting excess entries.
- Refresh is explicit merchant action.

## Work Items

- [ ] Build settings components and navigation integration.
- [ ] Wire SHOPIFY-003 actions/status loaders.
- [ ] Add accessibility, validation and state-transition tests.

## Interfaces / Contracts

Consumes SHOPIFY-003 server contract only; no direct Redis/Commerce provider calls.

## Dependencies

- ARCH-023-SHOPIFY-003

## Enables

- ARCH-023-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] Merchant can configure entry/purpose/locale URL and see processing result.
- [ ] Refresh preserves displayed current active source until successful replacement.
- [ ] Plan counts are displayed as knowledge entries, not capabilities/URLs.

## Validation

- [ ] Focused component/route tests.
- [ ] Accessibility/validation regressions.
- [ ] Lint/typecheck/build as declared.
- [ ] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.

## Implementation Notes

None

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

Pending.

### Follow-up

None
