---
id: ARCH-006-ADMIN-002
architecture_id: ARCH-006
title: Add merchant-communications to the existing Admin queue monitor
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 85
executor: copilot
claimed_at: 2026-09-06T19:55:47Z
attempt: 1
depends_on:
  - ARCH-006-BACKGROUND-007
enables: []
created: 2026-09-05
updated: 2026-09-06T19:30:00Z
---

# ARCH-006-ADMIN-002: Add merchant-communications to the existing Admin queue monitor

## Architecture

`docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

## Objective

Expose the accepted `merchant-communications` BullMQ queue in the existing protected read-only queue monitor using existing redaction/pagination patterns.

## Context

This remains a separate small but useful operational capability because it modifies an existing monitor with its own security/redaction tests; it must not become a second translation-control surface.

## Scope

Existing Admin queue-monitor reader/route/UI configuration and tests needed to include the new queue safely.

## Out of Scope

- Translation reconciliation controls.
- Message body display.
- Queue mutation/retry/remove actions.
- New generic telemetry.

## Requirements

Use the canonical shared queue name. Preserve existing platform-admin protection and bounded job inspection. Queue job payloads are ID-only, but still apply existing safe-redaction conventions. Do not add queue mutation actions.

## Work Items

- [x] Inspect current queue monitor registry/reader/tests.
- [x] Register `merchant-communications` using accepted shared queue contract.
- [x] Verify waiting/active/delayed/failed views use existing bounded/redacted behavior.
- [x] Add focused tests proving auth and no message content/secrets exposure.

## Interfaces / Contracts

Consumes SHARED-001 queue name; does not own BullMQ work semantics.

## Dependencies

Explicit task dependencies are listed in YAML frontmatter.

## Enables

None

## Acceptance Criteria

- [x] Queue appears in existing monitor.
- [x] Monitor remains read-only and protected.
- [x] Job inspection is bounded/redacted.
- [x] No translation recovery/business mutation is added.

## Validation

Focused monitor tests plus declared Admin validation and `git diff --check`.

## Implementation Notes

Do not fold the Admin manual translation-reconciliation action into this operational queue monitor; that action belongs to the support UI/server capability.

## Completion Report

### Status

Ready for architect review.

### Files Changed

- `moda-interact-admin/src/lib/admin/queue-monitor.ts`
- `moda-interact-admin/src/i18n/index.ts`
- `moda-interact-admin/src/i18n/locales/en.json`
- `moda-interact-admin/src/i18n/required-keys.ts`
- `moda-interact-admin/tests/security/admin-internationalization.test.mjs`
- `moda-interact-admin/tests/security/admin-queue-monitor.test.mjs`

### Work Completed

- Registered the canonical shared merchant-communications queue and all five accepted translation job names in detailed and overview monitor registries.
- Added catalogue-owned queue and job labels without adding queue mutation or reconciliation controls.
- Extended focused tests for five-queue snapshots, bounded overview readers, shared job registration, redaction, authorization, and read-only behavior.

### Validation Results

- Focused queue monitor test: passed, 14/14.
- Affected internationalization and queue monitor tests: 20/21 passed; the remaining failure is the existing Shared runtime version assertion expecting `0.7.0` while the installed package is `0.7.1`.
- Full Admin test suite: 91/92 passed; the remaining failure is the same existing Shared runtime version assertion.
- `npm run lint`: passed with two existing React Hook dependency warnings in `src/components/admin/queue-monitor.tsx`.
- `npm run prisma:validate`: passed.
- `npm run build`: passed with existing workspace-root and optional BullMQ Valkey dependency warnings.
- `git diff --check`: passed.

### Deviations

The repository's internationalization security test still expects Shared package version `0.7.0`; this task uses the already-installed and declared `0.7.1` package and does not change that unrelated baseline.

### Assumptions

The shared merchant-communications contract exports remain the source of truth for the queue name and accepted job names.

### Unresolved Issues

No task-scoped issues remain. The unrelated Shared version assertion should be reconciled separately.

### Architectural Concerns

None. The monitor remains a bounded, protected, read-only operational view and does not expose translation recovery controls.

## Architect Review

### Review Status

Accepted — Complete.

### Independent Review

`moda_architect` independently reviewed Attempt 1 against the bounded queue-monitor contract and compared the implementation snapshot with the previously accepted Admin baseline. The application changes are confined to the existing queue registry, Admin i18n catalogue/required-key list, and focused queue/i18n tests. The monitor now consumes `MERCHANT_COMMUNICATIONS_QUEUE_NAME` and `MERCHANT_COMMUNICATIONS_JOB_NAMES` from the accepted Shared contract rather than duplicating the queue/job identifiers.

The merchant-communications queue participates in the existing bounded waiting/active/delayed/failed readers and five-queue overview without adding retry, remove, pause, resume, reconciliation, or other mutation capability. Platform-admin authorization and the existing no-store/read-only API boundary are unchanged. List/snapshot responses remain payload-redacted; selected-job detail retains the previously accepted protected diagnostic contract. The newly registered merchant-communications payloads are ID-only and therefore do not introduce merchant message body content into Redis job data.

Focused test changes cover the canonical queue/job registry, five-queue snapshot/overview behavior, bounded readers, read-only UI behavior, catalogue-owned labels, and authorization. The agent reports 14/14 queue-monitor tests passing, build/Prisma/lint/`git diff --check` passing, and the only full-suite failure remains the already-known stale ARCH-005 Shared `0.7.0` assertion. The supplied snapshot excludes `node_modules`, so the architect could not independently re-run dependency-backed tests inside the extracted archive; static comparison found no task-scoped contradiction with the reported evidence.

### Coordination Decision

`ARCH-006-ADMIN-002` is Complete. It enables no downstream task, so no additional task is promoted by this acceptance. `ARCH-006-ADMIN-004` remains independently Ready from the earlier `BACKGROUND-007` release. System-test tasks remain manual-gated.
