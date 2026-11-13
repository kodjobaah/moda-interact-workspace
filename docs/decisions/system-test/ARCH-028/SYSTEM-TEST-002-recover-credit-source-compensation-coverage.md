---
id: ARCH-028-SYSTEM-TEST-002
architecture_id: ARCH-028
title: Recover source-specific compensation acceptance coverage
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-11-13T15:10:32Z
attempt: 1
depends_on:
  - ARCH-028-ADMIN-001
  - ARCH-028-BACKGROUND-007
  - ARCH-028-BACKGROUND-009
  - ARCH-028-SHOPIFY-001
  - ARCH-047-ADMIN-007
  - ARCH-047-BACKGROUND-006
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Recover source-specific compensation acceptance coverage

## Architecture

ARCH-028; docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md; coordinator moda_architect.

## Objective

Incorporate the backed-up missing source-specific131026 compensation coverage onto current main without losing newer acceptance behavior.

## Context

Primary checkout has27 tracked edits and30 untracked additions behind current main. The delta adds three PAID/PROMO/PURCHASED scenarios plus supporting fixtures/diagnostics/terminal-recipient checks. Root verified full external Git bundles, staged/unstaged binary patches and nonignored untracked archives before reconciliation. This bounded incremental acceptance slice does not complete the original broad ARCH028SYSTEM001 certification.

## Scope

Selective missing compensation scenarios, approved Admin/Meta template fixtures, settled durable capacity gate, terminal-recipient suppression/merchant-notice UI/order/idempotency observation, directly supporting bounded diagnostics/tests/catalogue/docs from the protected backup.

## Out of Scope

Application source fixes, full18-scenario ARCH028 certification, non131026/uncertain settlement policy expansion, live provider/customer calls, raw historical evidence publication, framework changes and main integration.

## Requirements

- Base execution on fresh current system-test main, preserving all ARCH075/coupon/merchant-followup scenarios and existing encryption/messaging.meta/Meta-ingress contracts. Current catalogue plus exactly three genuinely missing rows replaces neither current main nor its newer entries.
- Selectively port27 tracked/30 untracked local candidates from verified moda-local-reconciliation-backup-20261113T145749Z. Do not copy historical attempt25 transcript. Correct ported fixtures to actual current strict contracts (including required schemaVersion1); do not weaken validators/assertions.
- Exercise PAID included-current-period, active promotional and valid purchased-lot credit correction with exact source-owned balances, linked negative reporting usage and original lineage. No test may pre-create recovery reservations/usages/messages/compensation; actual accepted workers create those. Synthetic purchase issuance is explicit fixture, not a real charge.
- Signed131026 receipt must settle durable correction/suppression before the once-only merchant SYSTEM notice. Replay/stale receipts cannot double-correct, transfer credit, change suppression identity or send again. Subsequent same-shop suppressed checkout admits no extra billing/provider work. Strong MESSAGE_SENT plus exact settled ledger readiness prevents premature passes.
- Run actual synthetic tenant-isolated disposable PostgreSQL/Redis/current accepted worker images and local HTTP Meta/Shopify emulators for the three source cases and modified Free/status/settlement paths. Record exact source/image/migration identities and actual outcome. Route product defects to owners rather than patching other repositories.
- Failure-stage diagnostics must remain bounded/redacted, respect actual authenticated merchant UI/tenant boundaries and preserve truthful failures. Existing main readiness/encryption modules are reused rather than replaced with stale local versions.
- All explicit implementation prerequisites are Complete. Root's new explicit recover/test request supplies the current developer manual launch checkpoint. This is a terminal task; no implementation depends on it. Preserve original SYSTEM001 broad scope/status and accepted ARCH075 evidence. No production/full architecture certification claim.

## Work Items

- [ ] Reconcile backup/current-main overlap and port missing behavior only.
- [ ] Validate fixtures, bounded diagnostics and meaningful integrated compensation paths.
- [ ] Publish mirrored report/source, set review and stop.

## Interfaces / Contracts

Current accepted ARCH028/ARCH027 credit and provider contracts, ARCH047 approved template lifecycle and published Shared contracts remain authoritative. No new release or application source edit. Root owns full verified external backup and final integration; preserve all originals.

## Dependencies

ARCH-028-ADMIN-001, ARCH-028-BACKGROUND-007, ARCH-028-BACKGROUND-009, ARCH-028-SHOPIFY-001, ARCH-047-ADMIN-007, ARCH-047-BACKGROUND-006.

## Enables

None

## Acceptance Criteria

- [ ] Three missing source scenarios and supporting coverage are incorporated without removing newer main functionality.
- [ ] Actual durable source-specific accounting, suppression/notice ordering/idempotency and strict fixture contracts pass meaningful disposable tests.
- [ ] Exact source/image/backup/isolation/synchronization/validation evidence is truthful; no live mutation or full certification claim.

## Validation

- [ ] Actual declared full harness/unit/static/catalogue/syntax checks and privacy/diff hygiene.
- [ ] Three source compensation disposable integrated runs plus modified Free/provider-status/durable-settlement paths with real PostgreSQL/Redis/worker/emulator evidence. Missing prerequisites or product failures are reported, not fabricated green.

## Stop Condition

Publish task-owned source and parent report on matching branches, set review and return to moda_architect. Do not self-accept, merge, deploy, mutate live systems or start follow-on tasks.

## Implementation Notes

You are not alone; preserve others' edits. Normal launcher owns dedicated matching parent/implementation worktrees, synchronization, recursive submodules and claim. Never reuse primary or another task worktree. Root owns final integration. No broad new architecture or credential export publication.

## Completion Report

### Status

In Progress — selective source recovery and local checks complete; disposable integration pending resource slot.

### Files Changed

System Test catalogue, recovery/status fixtures and scenarios, bounded diagnostics, unit tests and recovery documentation. Primary source checkout remains untouched.

### Work Completed

Recovered the three missing source-specific scenarios from the verified backup while retaining all 181 current-main scenarios. Added strict schemaVersion 1 template bindings and modern encryption configuration; retained newer coupon, follow-up, ordered-message and readiness coverage. Fixed worktree-aware Gateway fixture lookup through MODA_WORKSPACE_ROOT.

### Validation Results

Node v24.19.0. Catalogue regeneration validates 184 scenarios (81 implemented, 103 planned); syntax validates 317 JavaScript files; source structure passes. Final full serial suite passed: 562 tests, 560 passed, two intentional skips, zero failures. Corrected stale catalogue assertions and scenario implementation provenance; focused rerun passed all 23 tests. Additional Messaging provenance coverage for all three source scenarios passed three script tests; implementation source is pushed at 5395ecb (full SHA recorded by repository Git). Actual disposable PostgreSQL/Redis/worker compensation runs remain in progress; no integration success is claimed.

External backup: moda-local-reconciliation-backup-20261113T145749Z, verified by coordinator before recovery. Prepared claim 82be96ffb523780ab52bb09be1c459942724c5fd; implementation baseline f3914582f31c3dc261852ed10cd98537809776ad. Both canonical task branches were synchronized by the launcher. No primary checkout, live provider or customer mutation.

### Deviations

None

### Assumptions

Verified external backup remains intact.

### Unresolved Issues

Host load exceeded 250 during concurrent validation; coordinator sequenced heavy work. Final unit/static checks pass. Isolated accepted App653677f and Messaging3b3d6b5 tracked-source snapshots installed successfully. First PAID disposable run migrated PostgreSQL successfully and built accepted App in74 seconds; pinned Background8add92e Docker build is currently running. Required integrated business proof remains outstanding.

### Architectural Concerns

Route newly discovered source defects to owning tasks.

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

Original broad SYSTEM001 certification and live production acceptance remain separate.
