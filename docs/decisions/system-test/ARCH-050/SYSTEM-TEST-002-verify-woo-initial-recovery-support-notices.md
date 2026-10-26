---
id: ARCH-050-SYSTEM-TEST-002
architecture_id: ARCH-050
title: Verify WooCommerce test-mode initial outreach Support notification end to end
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-050-BACKGROUND-003
  - ARCH-050-API-001
  - ARCH-050-API-002
  - ARCH-050-WOOCOMMERCE-001
  - ARCH-050-WOOCOMMERCE-002
  - ARCH-048-WOOCOMMERCE-002
  - ARCH-048-WOOCOMMERCE-003
enables: []
created: 2026-10-26
updated: 2026-10-26
---

# Verify WooCommerce test-mode initial outreach Support notification end to end

## Architecture

Architecture ID: `ARCH-050`. Architecture document: `docs/architecture/ARCH-050-merchant-recovery-initial-outreach-support-notifications.md`. Coordinator: `moda_architect`.

## Objective

Black-box verify a connected Woo merchant saves opt-in and receives exactly one navigable Support message for a guarded confirmed automated first recovery send using the explicitly controlled test-only outbound path.

## Context

Live Woo outbound is disabled outside test mode in the supplied Background snapshot and must remain so. ARCH-048 Woo checkout/order producer corrections (`WOOCOMMERCE-002/003`) are ready but not complete in the uploaded task metadata and gate integrated end-to-end verification.

## Scope

**Modify/create in `moda-interact-system-test/`:**

- `catalogue/scenarios.json` — register `RECOVERY-SUPPORT-051`, domain `RECOVERY`, provider `woocommerce`, source requirement `ARCH-050-SYSTEM-TEST-002`.
- `src/harness/recovery/woo-initial-support-notice-scenario.js` — isolated black-box Woo flow/assertions, no service implementation.
- `src/harness/recovery/woo-initial-support-notice-fixtures.js` — connected local WP/Woo installation, hosted API/Background, disposable Postgres/Redis, controlled test-only sender fixtures.
- `src/harness/recovery/index.js` — register executor without rewriting existing Shopify recovery scenarios.
- `test/harness/woo-initial-support-notice.test.js` — catalogue/guard/pipeline assertions.

Add only supporting harness modules needed for the scenario; keep fixtures/assertions/orchestration split.

## Out of Scope

- Enabling Woo production outbound, bypassing Meta safety admission, modifying Woo plugin source, or claiming live merchant delivery from a test sender.

## Requirements

- Confirm canonical metadata of `ARCH-048-WOOCOMMERCE-002` and `ARCH-048-WOOCOMMERCE-003` is `complete` before starting the **full** checkout/order ingress scenario; they are still `ready` in the uploaded snapshot.
- Use existing test-mode Woo guarded sender only (`NODE_ENV === "test"` and explicitly injected `enableTestOutbound`); verify production gate remains OFF. Do NOT claim live production deliverability from test-only evidence.
- Exercise WordPress merchant saves OFF→ON, browser→PHP→hosted API strict **recovery-policy v2**, real test-mode initial send and billing/attempt transition, hosted **Support history v2** with nullable recovery reference, WordPress Support `View conversation`, WP `admin.php?...#recovery-conversation` and tenant-scoped recovered transcript.
- Assert STOP/consent, order completion/cancel, failed provider, duplicate jobs, disabled preference, human and follow-up negative paths; no extra charge/notice. Verify capability/nonce and installation-scoped host credentials throughout.
- Separate provider-accepted-SENT evidence from WhatsApp delivery. Record production-outbound gate as known unrelated rollout dependency, not a feature defect.

## Work Items

- [ ] Register Woo scenario and split fixtures/assertions/executor modules.
- [ ] Test v2 policy and Support strict validators end-to-end, ON/OFF and exact local WP conversation link/anchor.
- [ ] Test duplicate/replay/STOP/order/unauthorised paths and absence of second charges, with guarded test-only sender.
- [ ] Record dependencies, release gate status, evidence and limitations.

## Interfaces / Contracts

- New scenario ID `RECOVERY-SUPPORT-051`, source requirement `ARCH-050-SYSTEM-TEST-002`, provider `woocommerce`.
- Validates API Policy v2, API Support history v2, Woo PHP/JS strict validators, initial Background finalisation, local WP navigation and protected hosted recovery reads.
- The Woo event producer tasks `ARCH-048-WOOCOMMERCE-002`/`-003` are explicit prerequisites of full integrated validation (not of ARCH-050 implementation tasks).

## Dependencies

- `ARCH-050-BACKGROUND-003` must be `complete` in canonical task metadata before claim.
- `ARCH-050-API-001` must be `complete` in canonical task metadata before claim.
- `ARCH-050-API-002` must be `complete` in canonical task metadata before claim.
- `ARCH-050-WOOCOMMERCE-001` must be `complete` in canonical task metadata before claim.
- `ARCH-050-WOOCOMMERCE-002` must be `complete` in canonical task metadata before claim.
- `ARCH-048-WOOCOMMERCE-002` must be `complete` in canonical task metadata before claim.
- `ARCH-048-WOOCOMMERCE-003` must be `complete` in canonical task metadata before claim.

## Enables

None. This task has no directly dependent ARCH-050 implementation task.

## Acceptance Criteria

- [ ] Enabled test-mode Woo initial send produces one Support notice and working WordPress recovery conversation link; disabled produces none.
- [ ] v2 PHP/browser/hosted contracts agree, and existing v1 compose/read receipts remain functional.
- [ ] Wrong-tenant, missing IDs, invalid nonce/capability, STOP/order suppression, duplicate jobs and human cases fail closed.
- [ ] Test harness does not open the Woo production sender gate or claim live outbound success.

## Validation

- [ ] `npm run validate:catalogue`, focused `node --test test/harness/woo-initial-support-notice.test.js`, `npm run lint`.
- [ ] `node scripts/run-system-tests.js --scenario RECOVERY-SUPPORT-051 --environment DISPOSABLE_LOCAL --list`, then `--execute` against explicitly wired local WordPress/Woo/Postgres/Redis fixtures.
- [ ] `git diff --check`, record source/test limitations and guarded outbound flag.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, update this task to `review`, provide the Completion Report, return control to `moda_architect`, and **STOP**. Do not start dependent work. A system-test task is terminal and cannot be used as a prerequisite for implementation.

## Implementation Notes

The supplied snapshot retains Woo's test-only outbound gate, while ARCH-048 Woo events WOOCOMMERCE-002/003 are not yet Complete. This test is **terminal** and must not be used to gate any implementation task. If local WordPress/Woo harness support is missing, document the precise harness gap instead of simulating a production merchant send or bypassing security.

## Completion Report

### Status

Not Started.

### Files Changed

None (definition only).

### Work Completed

None.

### Validation Results

Not executed; no implementation claimed.

### Deviations

None.

### Assumptions

The task is based on the 2026-10-26 uploaded snapshot and must recheck current canonical code during execution.

### Unresolved Issues

None recorded at definition time.

### Architectural Concerns

Return newly discovered cross-repository/schema/security/contract issues to `moda_architect`.

### Task Branch / Worktree Evidence

Not materialised. Launcher-resolved parent/implementation task worktree, synchronization and branch evidence are required at execution.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not yet reviewed.

### Follow-up

None.
