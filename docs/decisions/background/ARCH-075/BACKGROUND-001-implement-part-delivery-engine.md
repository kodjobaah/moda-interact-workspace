---
id: ARCH-075-BACKGROUND-001
architecture_id: ARCH-075
title: Implement durable ordered physical delivery lifecycle
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-11-13T01:07:59Z
attempt: 1
depends_on:
  - ARCH-075-DATABASE-001
  - ARCH-075-SHARED-002
  - ARCH-075-SHARED-004
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Implement durable ordered physical delivery lifecycle

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect. Read all frozen contract constants and lifecycle decisions before implementation.

## Objective

Implement durable ordered physical delivery lifecycle.

## Context

User requests logo/shop details before a distinct product image and checkout footer. Existing single-provider-id response cannot safely loop multiple sends. This task owns one bounded prerequisite capability; preserve completed prior behavior.

## Scope

Adopt accepted database submodule and exact published Shared package; owning part freeze/permit/dispatch/ACK/status/reply lookup/reconciliation engine with deterministic tests, no live producer activation.

## Out of Scope

Other repositories/tasks, source main merges/deployment, production sends/replays/resets, billing/usage/cap changes, provider credentials/permissions, unsupported exactly-once assumptions, unbounded fanout/retries, unrelated refactors. Return actual cross-owner gaps.

## Requirements

Implement canonical root logical/perpart physical lifecycle. Atomic immutable manifest/part creation, unique stable identities, perpart same-tenant original control/consent/media/policy checks and no HTTP TX. Admit later part only after durable predecessor DELIVERED/READ; HTTP ACK waits for callback, never synchronously holds a worker/transaction. Immutable deadlineAt from bounded validated policy cancels unadmitted tail via asynchronous queue/repair continuation without resend; one automatic HTTP attempt after ADMITTED, UNKNOWN halts tail and never resends accepted prefix. Recover only PREPARED unattempted tail under original still-valid authority. Persist each MetaID, reconcile status-beforeACK receipt, monotonic duplicate/read-before-delivered aggregation, bounded7day receipt cleanup. Any quoted part resolves exact logical root/recovery safely. RootSENT onlyallACK, DELIVERED onlyall appropriate, READ onlyallREAD; definitive tail fail rootFAILED/partial reason, unknown conservativePENDING. HUMAN command notSENT afterheader. One logical usage/cap admission; retain original usage if prefixaccepted/unknown, no blanket compensation. Preserve old single-plan paths and current sender rate fence. Return any actual App/API projection gap rather than silently changing readers.

### Sender-bound provider correlation

Freeze actual server-selected providerAccountId/providerPhoneNumberId on every physical part. Normalized callback and quote must match both before attaching status/provider IDs or mapping root/recovery. Unknown sender events are not authority to claim a part with the same MetaID. Unmatched receipt dedupe/retention uses these IDs; existing single-message compatibility is preserved.

Runtime policy: server-owned default 120-second deadline from freeze, validated bounds 30–300 seconds; indexed repair batches at most 100 on 5-second cadence, plus immediate status/ACK continuation where supported. No new external configuration. Sender validation must use the same credential snapshot as the HTTP endpoint/token; optional server-only expected sender input leaves legacy callers unchanged. Frozen-sender child quote lookup occurs before current-global checks; old-sender root resolution cannot silently authorize a reply through a rotated sender. Continuation checks original AI inbound/control against current state without retaining the original processing lease; HUMAN admission remains original command/control based. Multipart commands must not fall into legacy single-send expired-permit reconciliation.

### Reader-first common layout compatibility

Scope now includes additive receiptv2/commonRef/custom-boundary READER and final verification support before engine rollout. Producers remain disabled here. Existing v1 frozen parser uses fixed header/footer helpers and cannot interpret future v2, so accepting a v1-only engine would permit producer-rollout overlap to cancel/drop legitimate new tails. Consume actual published Shared0045.13.9 parser, never sibling source or unpublished tarball. Until that dependency completes preserve ongoing legacy engine work/tests and design v2 read-only; do not claim final checks/rollout readiness.

Readerv2 binds canonical commonRef, actual rendered header/footer/trusted boundaries and original tenant/control/source/policy evidence; re-read active immutable SHARED source/locale hashes and existing current saved identity facts. No hardcoded prefix added over custom common content. Legacyv1 exact bytes remain readable. Status/ACK outcome persistence must retain real provider evidence even if full source becomes unavailable; invalid/unknown preparation never grants a fresh send or cancels arbitrary foreign work. HUMAN original admission/new-inbound policy unchanged. Final engine exact-head tests include mixedv1/v2 readers, custom boundaries, stale/tampered reference, callbacks/ACK race and no producer activation.

### Private v2 boundary receipt

Keep old receiptv1 exact. New Background-local recoveryShopHeader union member is strict `{schemaVersion:2,kind:RECOVERY_COMMON_LAYOUT,shopId,commonRef,variables:{shop.name,shop.websiteUrl,checkout.url},boundaries:{header,body,footer}}`; public commonRef remains Shared schemaVersion1. Original actor/control/source/policy receipt remains separate. Complete root equals header+body+footer and exact existing renderPreparedWrapper(commonRef.prepared, trusted variables, body). Derive canonical header/footer by a collision-checked internal response marker through the same existing renderer; marker never sent, exactly one split required, no arbitrary authored substring stripping or parallel formatter. Re-read current immutable SHARED definition/source/locale hashes and saved identity/checkout facts before admission.

Freeze variables from existing owning verified identity helper: valid sanitized saved name, else exact verified saved-domain hostname (explicit domain fallback, no invented brand name); normalized saved-domain website and existing trusted checkout resolver. Recompute identically on final validation. Unsafe/missing website cannot authorize v2. Strict bounds and original moderation/source identity remain; HUMAN new inbound alone does not invent a refusal gate. Final tests prove custom common header/footer, source/ref/fact tampering and v1 replay compatibility.

## Work Items

- [ ] Implement only assigned capability and document compatibility.
- [ ] Complete meaningful required checks and regression/negative evidence.
- [ ] Publish mirrored branch/report and return review, then stop.

## Interfaces / Contracts

Use canonical ARCH075 frozen decisions. Shared owns ordered schema/digest and existing perpart media exports; Database owns durable child/status identity; Background owns provider/current authorization and logical aggregation. Never duplicate validators or fabricate product/provider identity.

## Dependencies

ARCH-075-DATABASE-001
ARCH-075-SHARED-002

## Enables

Only dependent tasks after architect acceptance; never begin them implicitly.

## Acceptance Criteria

- [ ] Assigned bounded capability and frozen contract behavior satisfied.
- [ ] Legacy reads/records remain compatible; no unauthorized cross-owner/billing/security change.
- [ ] Durable/contract identity and fault cases satisfy required checks without silent fallback.
- [ ] Canonical dedicated mirrored worktree, synchronization and recursive evidence recorded; no private proof committed.

## Validation

- [ ] Real PostgreSQL concurrent root/part creation, perpart CAS, crash-before/after permit/ACK, unknown halting, tail resume/control/STOP cancellation, prefix preservation and logical usage tests.
- [ ] Status-beforeACK, duplicate/out-of-order/read-before-delivered, root aggregation and quoted anypart tenant tests.
- [ ] Legacy single-send/reconciliation, package integrity/install, types/scoped lint/build and exact-head full CI.
- [ ] Diff/privacy hygiene and report actual results, no production sends or secrets.

## Stop Condition

After required work and validation, set review, submit Completion Report and STOP. No main merge/deploy or enabled task execution.

## Implementation Notes

Accepted Database source merged at `a9b6ab852a8245dfd14447808aac288a23b113d0`; update the task-owned nested database gitlink to that exact source and generate Prisma. Preserve current5.13.8 engine work; final reader integration consumes published Shared5.13.9 from canonical public registry after Shared004 acceptance, verifying installed integrity. This task must wire active queue/repair/status/quote readers and continuation lifecycle in deployed entrypoints, not leave an unused engine. It must not enable new producer manifests; Background002 does that only after engine rollout and old-reader drain proof. Root requires engine Live/healthy evidence in both environments before producer merge.

You are not alone. Preserve others' edits and canonical prepared isolation. Root owns final merges/deployment. Architecture constants resolve inter-agent assumptions; report genuine gaps before expanding scope.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Pending

### Deviations

None

### Assumptions

None beyond canonical contracts.

### Unresolved Issues

None currently; report concrete gaps.

### Architectural Concerns

No weakening of tenant, immutable outcome or uncertain-provider safety.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual implementation review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
