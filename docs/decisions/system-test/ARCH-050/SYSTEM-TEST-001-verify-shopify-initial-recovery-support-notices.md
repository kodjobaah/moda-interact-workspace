---
id: ARCH-050-SYSTEM-TEST-001
architecture_id: ARCH-050
title: Verify Shopify opt-in initial outreach Support notification end to end
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
  - ARCH-050-BACKGROUND-002
  - ARCH-050-SHOPIFY-001
  - ARCH-050-SHOPIFY-002
enables: []
created: 2026-10-26
updated: 2026-10-26
---

# Verify Shopify opt-in initial outreach Support notification end to end

## Architecture

Architecture ID: `ARCH-050`. Architecture document: `docs/architecture/ARCH-050-merchant-recovery-initial-outreach-support-notifications.md`. Coordinator: `moda_architect`.

## Objective

Black-box verify a Shopify merchant can opt in, receive one notice after a real confirmed automated initial send and follow a tenant-safe link to the correct conversation.

## Context

The system-test repository owns cross-service scenarios, fixtures and evidence; do not alter implementation repositories in a testing task. Await architect acceptance of all implementation prerequisites and allow developer manual validation first.

## Scope

**Modify/create in `moda-interact-system-test/`:**

- `catalogue/scenarios.json` — register `RECOVERY-SUPPORT-050` with `sourceRequirements:["ARCH-050-SYSTEM-TEST-001"]`, provider `shopify`, domain `RECOVERY` and the required catalogue fields.
- `src/harness/recovery/initial-outreach-support-notice-scenario.js` — black-box orchestration assertions using existing fixtures/readers, without direct UI/database implementation changes.
- `src/harness/recovery/initial-outreach-support-notice-fixtures.js` — tenant fixtures, setting toggles and controlled first-send setup.
- `src/harness/recovery/index.js` — register new executor in the existing recovery-executor map.
- `test/harness/recovery-initial-outreach-support-notice.test.js` — test registration and scenario assertions; place artifacts under the existing `.validation/system-test/` convention.

Separate fixtures/assertions/orchestration rather than adding a 300-line catch-all. Reuse existing recovery/Support/WhatsApp test components where available.

## Out of Scope

- Implementing code fixes in other repositories, live Meta messaging, an unrelated system-test runner rewrite or production deployment.

## Requirements

- Use the standard `scripts/run-system-tests.js` catalogue and black-box harness; no mock of the production Background finaliser or bypass of Support loader/recovery-detail authorization.
- For an enabled Shopify merchant, drive approved checkout/recovery to durable provider-confirmed initial automated `sequence=1` send, verify persisted first attempt state, exactly one SYSTEM Support message with `RECOVERY_INITIAL_OUTREACH_SENT`, version string `"1"`, matching recovery FK and view-conversation navigation to correct transcript.
- Assert disabled/default OFF produces no notice; OFF→ON after first successful send cannot backfill; ON→OFF after send does not delete prior alert; provider failure/suppression, human/manual and sequence 2 do not create notice.
- Inject duplicate and concurrent job/replay cases; assert one Support thread, one notification, no duplicate credit. Verify different tenant cannot read target or detail, missing/deleted recovery has no action, `SUPPORT_ONLY` route restrictions remain.
- Capture HTTP/UI action evidence and DB assertions, clearly separating provider fixture accepted-SENT from live Meta delivery. Do not require production WhatsApp for repeatable local test.

## Work Items

- [ ] Add catalogued black-box scenario and separate fixtures/expectations/executor wiring.
- [ ] Run ON/OFF/replay/concurrency/failed-send and unauthorized/missing target cases against integrated local services.
- [ ] Record durable database evidence, verified link/anchor UI observation, credit count and provider status provenance.

## Interfaces / Contracts

- New recovery system-test scenario ID `RECOVERY-SUPPORT-050` (valid domain-prefixed catalogue ID); source requirement `ARCH-050-SYSTEM-TEST-001`.
- Validates ARCH-050 DATABASE/BACKGROUND-001/002/SHOPIFY-001/002 semantics using the existing official black-box runner.
- New scenario code and evidence only; never change app/database/background implementations from this system-test worktree.

## Dependencies

- `ARCH-050-BACKGROUND-002` must be `complete` in canonical task metadata before claim.
- `ARCH-050-SHOPIFY-001` must be `complete` in canonical task metadata before claim.
- `ARCH-050-SHOPIFY-002` must be `complete` in canonical task metadata before claim.

## Enables

None. This task has no directly dependent ARCH-050 implementation task.

## Acceptance Criteria

- [ ] ON initial sends exactly one linked Support notice and opens correct tenant transcript.
- [ ] OFF, late enablement, retry, provider failure, human and sequence 2 cannot create erroneous notifications/credits.
- [ ] Cross-shop URL and forged Support target are denied, no regressions in existing billing Support actions.
- [ ] Catalogue/executor/evidence all validate with unique scenario ID and replayable test fixture.

## Validation

- [ ] `npm run validate:catalogue`, `npm run test:harness` (or focused test), `npm run lint`.
- [ ] `node scripts/run-system-tests.js --scenario RECOVERY-SUPPORT-050 --environment DISPOSABLE_LOCAL --list` then repeat with `--execute` when integration environment is ready. Verify actual supported flags with `--help`.
- [ ] `git diff --check` and evidence/branch/worktree records.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, update this task to `review`, provide the Completion Report, return control to `moda_architect`, and **STOP**. Do not start dependent work. A system-test task is terminal and cannot be used as a prerequisite for implementation.

## Implementation Notes

This is terminal integrated validation, gated on accepted database, Background Shopify integration and both Shopify UI tasks. Developer manual validation may precede execution but is not a dependency task. System testing must not run without all listed implementation tasks Complete or modify their source code to force a PASS.

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
