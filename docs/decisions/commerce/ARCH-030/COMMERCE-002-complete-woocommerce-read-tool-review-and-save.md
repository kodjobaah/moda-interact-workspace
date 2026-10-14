---
id: ARCH-030-COMMERCE-002
architecture_id: ARCH-030
title: Complete WooCommerce Tool Review and Save after successful Test
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 36
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-030-COMMERCE-001
enables: []
created: 2026-10-14
updated: 2026-10-14
---

# Complete WooCommerce Tool Review and Save after successful Test

## Architecture

Architecture ID: `ARCH-030`.

Architecture document: `docs/architecture/ARCH-030-woocommerce-commerce-tool-authoring.md`.

Coordinator: `moda_architect`.

## Objective

Make the WooCommerce new-tool wizard reviewable and persistable only after a current successful Woo Test.

## Context

The Woo-specific Review component is a placeholder. The existing `PersistedNewToolKind` excludes WooCommerce, so enabling Next from Test alone would strand users at a nonfunctional review/save checkpoint.

## Scope

- Implement Woo provider-specific Review summary (shop, resource/GET method, configured inputs, response projection, template and test proof).
- Extend the canonical persisted Commerce Tool definition and validation path for a *bounded Woo read-tool type* using the accepted Shared descriptor; persist no Woo credentials or arbitrary HTTP fields.
- Enforce server-side Save guard for a current successful Shop/context-bound Test and preserve local authoring until Review Save.

## Out of Scope

- No live Background/MCP/WhatsApp execution activation; saving a Woo tool must not imply production execution support.
- No database migration without prior architect review; return any required schema change as a dependency gap.
- No merchant Studio exposure or read-write Woo operations.

## Requirements

- Unsaved draft remains local; Save goes through the approved Commerce tool lifecycle.
- Persisted definition stores only versioned operation ID, parameter mappings, bounded result schema/template and authorized metadata, not keys or URLs.
- Stale/failed/forbidden tests or Shop switches cannot be used as successful Save proof.
- If production Woo executor is not yet approved, clearly mark saved tools unavailable for live binding/publication instead of falsely advertising them as executable.
- Existing Shopify and External HTTP tool save flows stay unaffected.

## Work Items

- [ ] Implement Review summary and provider-specific schema/persistence adapter.
- [ ] Implement server save test-evidence revalidation and supported lifecycle/eligibility.
- [ ] Add round-trip, invalid/forbidden/stale-save, duplicate-click and other-provider regression tests.

## Interfaces / Contracts

Consumes Commerce-001 passed Shop-bound test state and published Shared descriptor. Existing Commerce tools remain on current storage/authorization boundaries. A later MCP/Background runtime project must supply separate approved execution ownership.

## Dependencies

- `ARCH-030-COMMERCE-001`

## Enables

None.

## Acceptance Criteria

- [ ] Woo Tool can reach Review and Save only after a current successful permitted test.
- [ ] Saved tool round trips the same canonical GET operation, mapping, response contract and template with no secrets.
- [ ] Denied/stale cases cannot bypass Save guards; live activation remains blocked absent a supported production executor.
- [ ] No regressions in other tool providers.

## Validation

- [ ] Focused Review/Save, persistence, role isolation and stale-test regression suites.
- [ ] Commerce typecheck/lint/build and appropriate persistence integration, where available.
- [ ] git diff --check and no secret/runtime exposure verification.

## Stop Condition

After all required Work Items, Acceptance Criteria and Validation pass, record a truthful Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not start dependent tasks or mark this task Complete.

## Implementation Notes

Do not introduce or backfill production Woo executor. The user asked to complete creation-time testing; production use of the tool remains an explicit future architecture decision.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None recorded yet.

### Architectural Concerns

None recorded yet.

## Architect Review

### Review Status

Pending.

### Review Notes

Not reviewed: portable task definition only.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending implementation.

### Follow-up

Await dependency-gated, launcher-materialised execution and independent review.
