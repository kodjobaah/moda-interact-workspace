---
id: ARCH-054-SYSTEM-TEST-001
architecture_id: ARCH-054
title: Certify delayed AI replies and immediate human response end to end
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-054-DATABASE-001
  - ARCH-054-SHARED-001
  - ARCH-054-SHARED-002
  - ARCH-054-API-001
  - ARCH-054-API-002
  - ARCH-054-SHOPIFY-001
  - ARCH-054-SHOPIFY-002
  - ARCH-054-WOOCOMMERCE-001
  - ARCH-054-BACKGROUND-001
  - ARCH-054-BACKGROUND-002
  - ARCH-054-BACKGROUND-003
enables: []
created: 2026-10-31
updated: 2026-10-31
---


# ARCH-054-SYSTEM-TEST-001: Certify delayed AI replies and immediate human response end to end


## Architecture

Architecture: `ARCH-054`

Document: `docs/architecture/ARCH-054-merchant-configurable-ai-response-delay.md`

Coordinator: `moda_architect`. Task **defined but not materialised**; no local Git/worktree/branch activity is claimed.


## Objective

Black-box certify the merchant delay control, AI scheduling, tenancy, text/voice, human control and final Meta admission across Shopify and WooCommerce.


## Context

ARCH-054 adds a **merchant-selectable integer 0–30 minute AI reply delay** to the existing ARCH-040 recovery-conversation processor and handover controls, leaving merchant-authored HUMAN replies without configured delay. See the parent architecture and current snapshot for specific boundaries.


## Scope

Add `ARCH054-AI-DELAY-001` and `ARCH054-HUMAN-BYPASS-001` to `catalogue/scenarios.json` using existing scenario schema; implement modular fixture/executor/assertion helpers under `test/harness/arch054/` rather than one 300-line script; add harness tests and evidence output through existing `scripts/run-system-tests.js`. Test disposable PostgreSQL/Redis and Meta emulator, not production credentials.


## Out of Scope

No unrelated architecture changes, new standalone chat service, per-user timer jobs, invented provider error explanations, or updates to `docs/decisions/**/_index.md`. No implementation outside the assigned repository.


## Requirements

- Exercise merchant 0,1,7,30 writes/reads, invalid -1/31/fraction/string, correct optimistic revision, concurrent Shopify/Woo settings updates (different merchants), and future-turn-only changes.
- Assert actual provider send count/time relative to persisted deadline in a controllable clock: text at t0 and t0+2m with delay5 => earliest t0+5m plus quiet; no second agent call. Audio starts delay at transcription completion; failed/stale transcription no AI.
- Test Shopify and Woo user Take Over before due, during LLM await, after final Meta dispatch; HUMAN text sends through normal moderated path without AI timer; Resume AI does not revive stale scheduled work. Tests must distinguish request already dispatched from one not yet admitted.
- Shared sender, same phone across two shops: quoted inbound context resolves independently, two deadlines are independent; no cross-shop message/credit leakage. STOP remains immediate regardless of delay. No false "exactly once provider delivery" assertions.
- Test 0 preserves quiet/settle behaviour and initial recovery outreach/follow-up schedule unchanged. Verify original provider error logging, redaction, correlation and no swallowed exceptions.


## Work Items

- [ ] Implement two catalogue scenarios and modular fixtures/executors/assertions; ensure preflight readiness before running.
- [ ] Record commands, test environment, container cleanup and pass/fail evidence for both platforms.


## Interfaces / Contracts

Existing WhatsApp ingress, recovery and human send contracts; published v1 merchant delay contract. This terminal system-test task creates no app API or database schema.


## Dependencies

- ARCH-054-DATABASE-001
- ARCH-054-SHARED-001
- ARCH-054-SHARED-002
- ARCH-054-API-001
- ARCH-054-API-002
- ARCH-054-SHOPIFY-001
- ARCH-054-SHOPIFY-002
- ARCH-054-WOOCOMMERCE-001
- ARCH-054-BACKGROUND-001
- ARCH-054-BACKGROUND-002
- ARCH-054-BACKGROUND-003


## Enables

None


## Acceptance Criteria

- [ ] Every required scenario passes or is explicitly blocked with reproducible evidence; customer never sees early AI or stale human-owned AI response.
- [ ] Merchant-authored HUMAN command is not artificially delayed; multi-merchant tenant isolation maintained.


## Validation

- [ ] `npm run validate:catalogue`; `npm run system:messaging:plan`, then `node scripts/run-system-tests.js --scenario ARCH054-AI-DELAY-001,ARCH054-HUMAN-BYPASS-001 --execute`; `git diff --check`.


## Stop Condition

After all required Work Items, Acceptance Criteria and Validation are complete, update Completion Report, set status to `review`, return control to `moda_architect` and **STOP**. Do not implement dependent tasks. Publication tasks do not rerun accepted implementation validation.


## Implementation Notes

Implement only the identified repository-owned changes; preserve original provider/SDK errors in shared structured logs and rethrow failures to the owning retry/admission boundary.


## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not Run

### Deviation / Assumptions / Unresolved Issues / Architectural Concerns

None

### Worktree and Git Evidence

Not materialised; implementing agent must record launcher-prepared dedicated parent/implementation worktree paths, start-of-attempt sync, branch SHAs, submodule pins and cleanup.


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
