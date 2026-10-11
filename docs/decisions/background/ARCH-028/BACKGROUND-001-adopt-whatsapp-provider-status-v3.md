---
id: ARCH-028-BACKGROUND-001
architecture_id: ARCH-028
title: Adopt WhatsApp provider-status v3 and explicit status transitions
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-028-DATABASE-001
  - ARCH-028-SHARED-002
enables:
  - ARCH-028-MESSAGING-001
created: 2026-10-03
updated: 2026-10-11
---

# Adopt WhatsApp provider-status v3 and explicit status transitions

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Adopt the exact published dual-version WhatsApp provider-status contract, persist bounded provider failure evidence, and replace the unsafe numeric status rank with explicit delivery-state transitions while preserving delivered-usage and retry semantics.

## Context

Current `STATUS_RANK` orders `FAILED < SENT`, so a late SENT can resurrect a failed message. ARCH-028 requires a partial transition lattice instead.

This remains a consumer/evidence task. It does not classify provider codes or compensate/reachability/notify.

## Scope

Update the exact published Shared dependency, accepted database submodule, `whatsapp-provider-status.service.ts`, and focused tests.

Explicit transitions:

```text
PENDING -> SENT | DELIVERED | READ | FAILED
SENT -> DELIVERED | READ | FAILED
FAILED -> DELIVERED | READ
DELIVERED -> READ
READ -> no later state
```

A late SENT from FAILED/DELIVERED/READ is ignored. DELIVERED/READ may supersede FAILED as stronger positive evidence. Historical failure evidence is retained.

For v3 FAILED persist bounded `providerFailureCode` and `failedAt`; v2 FAILED may persist `failedAt` without inventing a code. Replayed v3 FAILED may enrich a null failure code on an already-FAILED message.

## Out of Scope

- Meta webhook parsing/production.
- Provider-code classification.
- RecoveryOutreachAttempt/follow-up mutation.
- Reachability/suppression.
- Compensation/hard-limit correction.
- Synchronous send rejection.
- Merchant notification.

## Requirements

- [x] Consume exact SHARED-002 package and accepted DATABASE-001 fields.
- [x] Accept v2 and v3 through canonical Shared parser.
- [x] Replace numeric total rank with explicit allowed transitions.
- [x] FAILED -> SENT is impossible.
- [x] FAILED -> DELIVERED/READ is permitted.
- [x] DELIVERED/READ never regress to FAILED/SENT.
- [x] Persist bounded failure evidence and allow idempotent evidence enrichment.
- [x] Preserve one idempotent `DELIVERED_WHATSAPP_MESSAGE` usage event and Serializable/CAS retry behaviour.
- [x] New ARCH-028 production source files SHOULD target <=200 physical lines and MUST NOT exceed 300 physical lines.
- [x] Existing production source files already above 300 physical lines may receive only minimal integration/composition edits; substantive new ARCH-028 policy, orchestration, persistence/accounting or provider-specific behaviour MUST be extracted into focused modules.
- [x] Keep independently testable orchestration, policy/classification, persistence/accounting and provider-adapter responsibilities separated; do not introduce a new catch-all service merely because they belong to the same architecture task.

## Work Items

- [x] Verify exact published Shared package and accepted database gitlink; both were already pinned to the required revisions.
- [x] Implement explicit status transition helper/lattice.
- [x] Persist v3 failure evidence and v2 failedAt semantics.
- [x] Add replay/enrichment and out-of-order tests, including FAILED then SENT.
- [x] Preserve delivered usage/accounting tests.
- [x] Review touched production-file sizes/responsibilities and keep policy in a focused module.

## Interfaces / Contracts

Consumes `NormalizedWhatsAppStatus` v2/v3 from `@modainteract/moda-interact-shared/billing` and DATABASE-001 message fields.

## Dependencies

- `ARCH-028-DATABASE-001`
- `ARCH-028-SHARED-002`

## Enables

- `ARCH-028-MESSAGING-001`

## Acceptance Criteria

- [x] FAILED cannot be resurrected by SENT.
- [x] DELIVERED/READ may supersede FAILED and clear no historical failure fields.
- [x] v2/v3 compatibility and failure enrichment are idempotent.
- [x] Unknown/non-outbound/unowned handling remains bounded.
- [x] Delivered usage identity/accounting is unchanged.
- [x] No ARCH-028 recovery/reachability/compensation policy is introduced.
- [x] No new ARCH-028 production source file exceeds 300 physical lines; new files target <=200 lines where the responsibility remains coherent.
- [x] Existing >300-line production files contain only thin ARCH-028 wiring/composition changes, with substantive new behaviour implemented in focused modules.
- [x] No touched production module combines independently testable orchestration, policy/classification, persistence/accounting and provider-specific mechanics into one catch-all implementation.

## Validation

Run repository-declared Prisma generation/validation, focused provider-status tests, unit/full tests, build and `git diff --check` as declared by the current repository.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

Do not encode the lattice as another arbitrary numeric rank. Make allowed transitions explicit and test every contested edge.

Keep the provider-status consumer thin. Prefer a dedicated status-transition helper/lattice and bounded failure-evidence merge helper rather than growing `whatsapp-provider-status.service.ts` with transition policy.

Maintainability is part of acceptance, not a post-task cleanup. Prefer a thin task-facing/orchestrator service that delegates to focused domain modules. Tests may remain larger when a cohesive behavioural matrix is clearer; the production-source line ceiling does not require microscopic file splitting.

## Completion Report

### Status

Ready for Review

### Files Changed

Implementation repository:
- `src/domain/whatsapp-provider-status-transition.ts`
- `src/services/whatsapp-provider-status.service.ts`
- `tests/unit/domain/whatsapp-provider-status-transition.test.ts`
- `tests/unit/services/whatsapp-provider-status.service.test.ts`

### Work Completed

Replaced numeric status ranking with an explicit transition lattice and made forbidden stale transitions no-ops. The service consumes the published v2/v3 Shared parser, persists first `failedAt` evidence and bounded v3 `providerFailureCode`, permits replay enrichment only when the stored code is null, and retains failure evidence when positive delivery/read evidence advances the status. Existing Serializable transaction, CAS conflict retry, deterministic delivered-usage idempotency, ownership checks and delivered accounting remain in place. The exact dependency is `@modainteract/moda-interact-shared@1.4.0` (registry integrity and tarball verified); the initialized database gitlink is the accepted `b9cb77a74c5fffa250dc65ed34de23113738d8e8` snapshot containing `providerFailureCode` and `failedAt`, so no dependency or gitlink churn was needed.

### Validation Results

Passed focused provider-status and transition-matrix tests: 43 tests. Passed `npm run prisma:validate`, `npm run prisma:generate`, `npm run build`, and `git diff --check`. Passed the complete unit suite (`npm run test:unit -- --maxWorkers=2`) and full repository suite (`npm test -- --maxWorkers=2`): 202 files, 2043 tests. An initial unbounded `npm test` run had three 5-second timeouts in unrelated observability/worker-startup tests; the bounded-concurrency full rerun passed with no failures.

### Deviations

No package or submodule update was required because the implementation worktree already pinned the exact published Shared release and accepted DATABASE-001 gitlink. The initial unbounded full-suite timeouts are recorded above; the same complete suite passed with bounded concurrency.

### Assumptions

The installed `1.4.0` Shared package is the canonical published v2/v3 parser; public registry metadata matched the lockfile. The supplied database submodule commit is the accepted DATABASE-001 schema baseline.

### Unresolved Issues

None.

### Architectural Concerns

None.

### Attempt 1 Worktree and Launcher Evidence

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; resolved by Git common-dir, not from a previous task worktree.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-028-BACKGROUND-001`, branch `task/ARCH-028-BACKGROUND-001`; reused and synchronized, with `origin/main` already incorporated.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-028-BACKGROUND-001`, branch `task/ARCH-028-BACKGROUND-001`; created for Attempt 1, with `origin/main` already current.
- Remote task-branch fast-forwards: `not-needed` for both worktrees.
- Recursive submodule sync and update/init: both passed. The initialized `database` submodule is at `b9cb77a74c5fffa250dc65ed34de23113738d8e8`.
- Shared/default workspace and implementation checkouts were not switched or used for task edits; no other task worktree was reused.
- Durable parent claim commit: `cb715fd7a174e9ff264195ad01fb7fecec2f0e87`. Implementation commit: `fb16853` (`feat(background): adopt WhatsApp provider status v3`).

## Architect Review

### Review Status

Accepted — Attempt 1 (2026-10-11).

### Review Notes

Accepted the bounded consumer-side adoption of WhatsApp provider-status v3. GitHub comparison confirms implementation branch `task/ARCH-028-BACKGROUND-001` is one commit ahead of `main` (none behind), with exactly four task-scoped files changed; implementation commit `fb16853c5221cc07915deac6c7eb227b793111c1` is published. Parent branch `task/ARCH-028-BACKGROUND-001` is two commits ahead of `main` (none behind); its submitted Completion Report is published as `63173e5cb863d483299ee9bb16483220b76429ce`. The archive omits `.git`, so the launcher-resolved physical parent/implementation worktree locations, clean state and recursive submodule preparation are supported by the Completion Report rather than independently observable from the archive. No physical-isolation anomaly was identified in the reported evidence.

The explicit transition lattice prevents `FAILED -> SENT` resurrection and any delivery/read regression; `FAILED -> DELIVERED/READ` remains possible. The canonical Shared v2/v3 parser validates each inbound event. The consumer records first failure time for v2/v3 FAILED, writes bounded v3 provider codes, and permits idempotent null-code enrichment on replay; positive delivery/read outcomes preserve historical failure evidence. Existing Shop ownership, Serializable/CAS retry, and deterministic one-per-message `DELIVERED_WHATSAPP_MESSAGE` accounting are preserved. No provider-code classification, compensation, suppression, outreach mutation or merchant notification was introduced.

Background was already exactly pinned to `@modainteract/moda-interact-shared@1.4.0`, a subsequent published release containing the accepted dual-version provider-status contract; no dependency modification was needed in this task. SHARED-002 originally published that contract in `1.3.1`. The accepted database model contains `providerFailureCode VARCHAR(64)` and `failedAt`, matching the consumer persistence. No source-level acceptance blocker was found.

### Reviewed Files

- `src/domain/whatsapp-provider-status-transition.ts`
- `src/services/whatsapp-provider-status.service.ts`
- `tests/unit/domain/whatsapp-provider-status-transition.test.ts`
- `tests/unit/services/whatsapp-provider-status.service.test.ts`
- `moda-interact-background/package.json` and `package-lock.json` (exact pinned dependency; unchanged)
- `moda-interact-background/database/prisma/schema.prisma` and ARCH-028 migration (consumed persistence fields; unchanged)
- Parent ARCH-028 architecture, Shared-001/002 and Database-001 task contracts.

### Validation Reviewed

- Agent-reported focused provider-status/lattice suite: **43 tests PASS**.
- Agent-reported complete unit suite and complete repository suite, each run with `--maxWorkers=2`: **202 files, 2,043 tests PASS**; initial unbounded suite had three unrelated 5-second timeouts, recorded transparently in the Completion Report.
- Agent-reported `npm run prisma:validate`, `npm run prisma:generate`, `npm run build`, and `git diff --check`: **PASS**.
- Independent review inspected four implementation/test files and confirmed GitHub branch/commit scope and ancestry. The archive contains no `node_modules` or original command logs, so the reported runtime test/build results were not independently rerun here.

### Architecture Conformance

Conforms to ARCH-028 provider-status consumer boundary and bounded task requirements. Explicit state transitions, strict dual-version validation, failure-evidence persistence/enrichment, stronger positive-delivery precedence and delivered-usage idempotency are present. New policy module is 29 physical lines; the updated consumer remains below 300 physical lines. Downstream delivery-failure classification, compensation and merchant notification remain separate responsibilities.

### Follow-up

- `ARCH-028-MESSAGING-001` becomes **Ready** now that SHARED-002 and BACKGROUND-001 are Complete. It must adopt the canonical published Shared v3 producer contract and preserve deterministic FAILED evidence identity; it must not start BACKGROUND-002 until accepted.
- Developer owns integration of the Background implementation task branch into Background `main`, followed by the parent workspace gitlink update and parent task-branch merge. The architect review patch is documentation-only and does not merge or push either branch.
- No `docs/decisions/**/_index.md` files are updated; defer domain index reconciliation until the developer explicitly ends the architecture/session.
