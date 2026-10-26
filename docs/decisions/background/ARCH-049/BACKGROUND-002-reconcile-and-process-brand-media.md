---
id: ARCH-049-BACKGROUND-002
architecture_id: ARCH-049
title: Own durable ShopBrand media generations, retries and reconciliation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-049-DATABASE-001", "ARCH-049-BACKGROUND-001"]
enables: ["ARCH-049-BACKGROUND-003", "ARCH-049-SYSTEM-TEST-001"]
created: 2026-10-25
updated: 2026-10-25
---

# Own durable ShopBrand media generations, retries and reconciliation

## Architecture

`ARCH-049` — `docs/architecture/ARCH-049-shopbrand-public-media-configuration.md`; coordinator `moda_architect`. **Portable task definition, not materialised in a developer Git worktree.**

## Objective

Implement the one-owner image-processing state machine over ShopBrand JSONB: claim due fixed roles, invoke BG001, persist verified READY atomically, reclaim abandoned work and periodically revalidate mutable source images.

## Context

ShopBrand persists role-specific source/work/ready fields; there is no media job table. PostgreSQL commit of PENDING is the durable acceptance point; BullMQ is an optional wake-up, not a second durable requirement.

## Scope

- Build `src/services/shop-brand-media-orchestration/` with source-slot persistence helper, lease/claim/CAS repository, due scanner and thin worker entrypoint.
- Use BG001 processor as an injected dependency and record structured outcomes via Shared logging.
- Schedule a bounded due scan every 5 minutes; allow optional BullMQ wake, with reconciliation required if wake is lost.
- Implement seven-day READY rechecks for same-URL changed bytes with safe last-known-good retention, and bounded retry/lease recovery.

## Out of Scope

- Implementing image fetching/transcoding, Shopify GraphQL, WordPress API, Woo plugin endpoint, ARCH-047 send-time resolution or metadata database triggers.

## Requirements

### R1. Common source update algorithm

Export an application-level source updater usable in Background and reproducible by the API service (the persistence JSON format is the architecture contract, not a Shared AST package):

```typescript
type BrandRole = 'LOGO'|'SQUARE_LOGO'|'COVER_IMAGE';
interface SourceObservation {
  shopId: string; role: BrandRole; sourceUrl: string|null;
  sourceReference: string|null; sourceFingerprint: string|null;
  observedAt: string;
}
```

With a short PostgreSQL row lock, check observed ordering and previous source values, increase source generation only on change, set PENDING or MISSING, clear lease/retry/failure, and preserve other roles atomically. Do not hold a DB transaction while downloading/uploading. Source timestamps are producer metadata; a replayed older observation must not overwrite a newer one. With no `ShopBrand` row, upsert by unique `shopId` before locking.

### R2. Work claim and completion

Claim one `(shopId,role,generation,fingerprint)` with expiring lease; write work.status PROCESSING and lease fields atomically. Run BG001 outside transactions. Publish READY only on matching current generation/fingerprint and claim. Store object key/contentType/output dimensions/bytes/digest/verifiedAt. Stale results do not update current READY, but immutable R2 objects need not be immediately deleted. On permanent failure set FAILED without retryAt; on transient failure increment attempts and schedule 1m, 5m, 30m, 2h, 24h with a max five attempts per generation. Reclaim expired leases.

### R3. Durable due scanner

Every five minutes examine a **bounded** number of ShopBrand JSON roles with work.status PENDING or retryable FAILED or expired PROCESSING. Do not use an unbounded full-table lock, do not starve a hot shop, and never require the best-effort BullMQ wake for correctness. The source change commit is sufficient for recovery after process restart. When the next process is launched, it must find due rows deterministically.

### R4. Revalidation of same-URL bytes

At least once per seven days, schedule a bounded content refresh of READY source URLs without immediately suppressing their last verified **current-generation** asset. If bytes unchanged, retain existing key. If bytes changed and the effective source reference/generation is still current at commit, atomically replace the ready object key/digest. Transient refresh failures keep the previously verified same-generation READY asset eligible and record a separate failure/retry marker; a source URL/reference change increments generation and makes old READY ineligible. Do not allow an old worker to overwrite a changed role.

### R5. Initial limits/telemetry

Expose per-role retry and failureCode metadata, bound memory/worker concurrency to R2 and external hosts, and use the existing shared logger. No new generic service logger or duplicated framework metrics.

## Work Items

- [ ] Implement row-locked source updater and lease/CAS repository.
- [ ] Implement bounded due scanner and optional wake handling.
- [ ] Implement retry, crash recovery and seven-day content refresh.
- [ ] Test two workers, multi-role writes, stale completion, source removal, duplicate source event and status reconstruction.

## Interfaces / Contracts

Consumes `commerce.ShopBrand` `whatsAppMedia` JSON schema version 1 and BG001 `process()` output. Produces updated per-role work/ready JSON. For lookup, only `READY` with matching `sourceGeneration` and `sourceFingerprint` is eligible; consumers must also check validated media properties and trusted public origin.

## Dependencies

- ARCH-049-DATABASE-001
- ARCH-049-BACKGROUND-001

## Enables

- ARCH-049-BACKGROUND-003
- ARCH-049-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Duplicate or concurrent source updates do not lose another role or duplicate current generation.
- [ ] Lost queue wakes and worker crashes are recovered by due-row scan.
- [ ] Old generation or old lease holder cannot publish READY.
- [ ] Failed fetch/R2 calls are retried within bounded policy; permanent errors visible without endless retry.
- [ ] A same-URL updated image is eventually detected and atomically replaces READY without forcing a send-time download.

## Validation

- [ ] PostgreSQL integration tests for per-role row-lock/CAS/unique shop and multi-worker contention.
- [ ] Unit tests for retry backoff, due-scan bounds and lease expiry.
- [ ] Deterministic output-stale and revalidation fixture tests.
- [ ] Relevant Background lint/typecheck/tests and `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and Validation are complete, record the Completion Report and change task status to `review`; hand off to `moda_architect` and STOP. Do not continue into a dependent task or change an `_index.md`.

## Implementation Notes

All task work must use the canonical launcher-provided **dedicated parent and implementation worktrees**, synced task/<TASK_ID> branches and start-of-attempt evidence. Inspect the actual pinned package scripts, source and existing conventions before editing. Do not merge branches, push main, edit another repository, start an enabled task or change any `docs/decisions/**/_index.md`. Use structured logging via `@modainteract/moda-interact-shared/logging`; secrets and full untrusted URLs must not enter diagnostics. Document changed files, relevant test commands, results, security/tenant checks, commits and worktree evidence in the Completion Report.

No additional assumptions are authorised.

## Completion Report

### Status

Not Started — defined but not materialised.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None beyond the explicit architecture/task contract.

### Unresolved Issues

None; live environment availability is a validation prerequisite and must be reported if missing.

### Architectural Concerns

None reported.

## Architect Review

### Review Status

Pending.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not reviewed.

### Follow-up

None.
