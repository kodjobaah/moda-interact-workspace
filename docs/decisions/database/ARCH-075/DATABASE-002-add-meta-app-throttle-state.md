---
id: ARCH-075-DATABASE-002
architecture_id: ARCH-075
title: Add durable Meta app sample throttle state
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 5
executor: codex
claimed_at: 2026-11-13T11:03:20Z
attempt: 1
depends_on:
  - ARCH-075-DATABASE-001
enables:
  - ARCH-075-BACKGROUND-007
created: 2026-11-13
updated: 2026-11-13
---

# Add durable Meta app sample throttle state

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Add durable Meta app sample throttle state.

## Context

Actual Meta sample_session HTTP403/code4 app request limit was classified as permanent blocked. One upload perlocale plus60second local polling and replica overlap can amplify calls; changing classification alone does not give durable cooldown. Existing scheduler leases/config/audit rows are not proper app-scoped lifecycle state. Generic historical rejection events do not carry code4 evidence.

## Scope

Additive Prisma model/migration/constraints and focused ERD/documentation for one app-scoped sample-operation cooldown/lease row. No application behavior, provider calls or existing state rewrite.

## Out of Scope

Other repositories except explicit accepted submodule adoption, provider credentials/grants, live sends/repair/deployment, Shared publication, blind create retry, unsupported caching, generic refactors or implementation-source merges.

## Requirements

Dedicated whatsapp.MetaTemplateAppOperationState keyed by existing CommerceEnvironment plus appId (numeric1..32), not tenant/WABA: app quota spans those scopes. Fields: cooldownUntil nullable timestamp, consecutiveThrottleCount nonnegative bounded saturating integer, lastThrottleAt nullable, lease owner token/generation/acquiredAt/leaseUntil with coherent nullable tuple, updatedAt. Use owner/generation fencing and monotonic generation; no secret/token payload. Exact field names may follow repository conventions but publish the final shape before consumer execution. One lease covers ONE bounded sample operation,120seconds; app backoff first15minutes, doubles to6hour cap. Database supplies invariant storage; Background owns timing/policy. A cooldown cannot be removed/shortened by stale owner completion; expired ownership can be reclaimed only with new generation. PK supports point lookup; add only indexes needed by actual queries, not speculative scans. Preserve existing tables/records and reversible compatible rollout. No reuse of scheduler enum/config/audit JSON.

## Work Items

- [x] Implement only the owning bounded outcome and final contract.
- [x] Prove meaningful failure/concurrency/compatibility behavior.
- [x] Complete mirrored report/checks, return review and stop.

## Interfaces / Contracts

Database002 owns durable Prisma/SQL state. Background007 consumes exact accepted schema and owns provider policy/leases/recovery; no new Shared contract. SystemTest002 is terminal validation. Root owns migration/deployment/operational evidence; no network inside transaction.

## Dependencies

ARCH-075-DATABASE-001

## Enables

ARCH-075-BACKGROUND-007

## Acceptance Criteria

- [x] Assigned bounded capability/invariants and explicit negative behavior satisfied.
- [x] Existing provider-intent, tenant/environment, immutable source and legacy lifecycle guards remain intact.
- [x] Canonical matching physical isolation/sync and exact validation evidence reported; no live mutation.

## Validation

- [x] Real PostgreSQL fresh+populated-upgrade migration, duplicate app identity, environment separation, lease tuple/nonnegative/generation and stale-owner invariants; generated Prisma/types/static checks and focused ERD. No unrelated baseline diagram/history repair.
- [x] Diff/privacy hygiene; no secrets/private production identifiers or unsupported capability claim.

## Stop Condition

When scope/checks complete, submit Completion Report/status review and STOP. No enabled task, source merge, hosted migration or live recovery/provider action.

## Implementation Notes

You are not alone; preserve other work. Canonical launcher packet owns start/claim. Root owns all final merges, test/prod migration, worker rollout/drain and protected live evidence. New domain logs reuse published Shared logging; do not duplicate generic telemetry. Return genuine contract gaps before widening scope.

## Completion Report

### Status

Ready for Review. Implementation `f805897e78b41e21f0e959249909bddf3054c6c1`
is committed and pushed on `task/ARCH-075-DATABASE-002`. No hosted migration,
provider request, registration repair or application change was performed.

### Files Changed

Prisma model and additive migration
`20261113111320_arch075_meta_app_operation_state`; two focused validation scripts
and package script entries; owning contract documentation, focused PlantUML/PNG
and the corresponding model block in the existing full ERD source. No previous
migration or unrelated diagram block was changed.

### Work Completed

Dedicated `whatsapp.MetaTemplateAppOperationState`, composite primary key
`environment` / `appId`, numeric app identity, bounded 0–31 throttle count,
nullable cooldown/last-throttle timestamps, coherent nullable owner/acquisition/
expiry tuple and monotonic nonnegative bigint generation. SQL guards prohibit
identity changes, generation regression, active acquisition replacement, a new
acquisition without a new generation, shortening/clearing future cooldown,
erasing/backdating throttle time and row deletion that would reset fencing.

Background must still CAS exact environment/app/owner/generation/unexpired lease:
SQL cannot infer a caller's previously observed token. Release clears the three
nullable lease fields without resetting generation; renewal preserves original
owner/generation/acquisition; expired reclaim advances generation. No timing
policy/provider cache or registration transition was installed by Database.
The contract documents Background's endorsed 120-second single-operation lease
and 15-minute exponential cooldown capped at six hours. The PK is the sole index;
point operations scale with configured apps rather than per-event hot-path rows.
No tenant relation, credential payload or cascade was added.

### Validation Results

- `npm ci`: locked install passed; no dependency/lock changes.
- Actual local PostgreSQL17 author fixture: all77 previous migrations deployed;
  `prisma migrate dev --name arch075_meta_app_operation_state --create-only`
  generated the new table; reviewed task-only SQL was applied locally.
- `npm run prisma:generate`: Prisma6.19.3 generated actual client/types.
- `npm run validate`: schema valid.
- `npm run test:arch075-meta-app-operation-state`: bounded static checks passed.
- `npm run lint`: repository ESLint passed, zero warnings.
- `npm run test:arch075-meta-app-operation-state:postgres`: **67 assertions**
  passed against invocation-owned PostgreSQL17, actual Prisma migrate deploy
  fresh and populated upgrade, both subsequent deploys no-op. Duplicate identity,
  separate environments, numeric/bounded/nullable tuple failures, two concurrent
  replica acquisitions with exactly one winner, active/expired generation guards,
  stale-owner completion with zero updates, cooldown/throttle-time anti-regression,
  deletion prevention and preserved legacy shops/writers all passed. Fixtures and
  owned containers removed. No hosted database or provider calls.
- Focused PlantUML PNG generated and visually inspected; `git diff --check` passed.

### Deviations

Actual migrate-dev generation also proposed unrelated pre-existing schema/history
index/FK renames/default changes. These were excluded from this task's new,
unapplied migration before application; existing history was never rewritten.
On local apply, migrate-dev then prompted to generate the same unrelated drift.
Queued terminal validation text accidentally became that extra migration's name;
its first unrelated DROP failed2BP01. Only this invocation's untracked extra
migration folder was removed and the entire disposable author fixture deleted.
Final source contains only the intended additive migration. The independent
noninteractive fresh/upgrade deploy proof passed afterward, without history
repair or accepting any failed/partial fixture result.

### Assumptions

No provider reset guarantee. Timing bounds are internal Background policy. A
bigint generation must remain a bigint/string in consumer code; it must not be
coerced to an unsafe JavaScript number. Count saturates at31. Rare configured-app
rows are retained; no cleanup scan is needed. The root applies hosted migrations
before deploying a consumer; old readers/writers are unaffected.

### Unresolved Issues

None in the bounded database scope. Root/Background own actual throttling evidence,
provider retry policy, exact historical recovery and live verification.

### Architectural Concerns

No cross-owner source change. Background must consume the documented point-CAS
contract and preserve all registration CREATE/POST uncertainty fences.

### Prepared execution evidence

Canonical primary workspace:
`/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
Parent task worktree:
`/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-DATABASE-002`.
Implementation task worktree:
`/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-DATABASE-002`.
Both branches `task/ARCH-075-DATABASE-002`. Existing prepared attempt1/claim
`040bd0e66a54b9698772a40e3ffbc5084b0048d2` reused unchanged; no re-claim,
shared checkout mutation or other task worktree reuse. Prepared parent remote
fast-forward not-needed/main already-current; implementation remote fast-forward
not-needed/main already-current. Recursive sync/update passed with no nested
submodules. Deterministic launcher preparation was not repeated.

## Architect Review

### Review Status

Accepted

### Review Notes

Accepted exact source `f805897e78b41e21f0e959249909bddf3054c6c1` and mirrored report `28db58064cf1c5624b6f2052ee10064329332238`. Independent SQL/schema/consumer-contract review confirms additive dedicated environment/app state, not reused scheduler/config/audit storage. Count0..31, BigInt generation and retained-row deletion guard are approved.

### Reviewed Files

Prisma app operation model; additive20261113111320 migration and lifecycle trigger; consumer contract; actual migration/CAS tests/static validator and focused ERD.

### Validation Reviewed

67 real PostgreSQL assertions passed for fresh and populated upgrade with actual Prisma deploy/no-op repeats, concurrent acquisition, expired reclaim/stale CAS, tuple/count/identity/environment and future cooldown/time guards. Prisma generation/validation, static checks, lint, focused ERD visual and diff checks passed. Canonical prepared paths/sync/claim reviewed. Unrelated generated drift was excluded; accidental extra local author migration failed and its owned fixture was disposed. Independent clean noninteractive deploy proof passed; no hosted history repair or shared source change.

### Architecture Conformance

One configured app/environment point row, no tenant/provider credential data or speculative scan index. Identity/generation and active ownership/cooldown constraints preserve durable state. Background still must compare exact environment/app/owner/generation/unexpired lease; SQL cannot infer caller evidence. Migration is additive and compatible with old workers; no provider/cache/policy implementation in Database task.

### Follow-up

Root owns source merge and migration test/prod before Background007 deploy. Exact historical missing-local migration exception may be used only with independently matching retained SQL/live checksum, all canonical history checks and unchanged ledger; no resolve/rewrite. Promote Background007 on this acceptance, pin actual merged database commit. SystemTest001 remains accepted; new terminal SystemTest002 is separately pending. Architecture In Progress.
