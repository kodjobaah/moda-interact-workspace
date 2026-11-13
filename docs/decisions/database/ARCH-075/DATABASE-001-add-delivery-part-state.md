---
id: ARCH-075-DATABASE-001
architecture_id: ARCH-075
title: Persist bounded physical delivery parts and early status receipts
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 10
executor: codex
claimed_at: 2026-11-13T00:38:32Z
attempt: 1
depends_on: []
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Persist bounded physical delivery parts and early status receipts

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect. Read all frozen contract constants and lifecycle decisions before implementation.

## Objective

Persist bounded physical delivery parts and early status receipts.

## Context

User requests logo/shop details before a distinct product image and checkout footer. Existing single-provider-id response cannot safely loop multiple sends. This task owns one bounded prerequisite capability; preserve completed prior behavior.

## Scope

Prisma schema/additive PostgreSQL migration, necessary constraints/indexes/relations/immutable fields and owning migration tests/ERD. Existing ConversationMessage stays logical root; no new root status enum.

## Out of Scope

Other repositories/tasks, source main merges/deployment, production sends/replays/resets, billing/usage/cap changes, provider credentials/permissions, unsupported exactly-once assumptions, unbounded fanout/retries, unrelated refactors. Return actual cross-owner gaps.

## Requirements

Implement ConversationDeliveryPart and minimal ConversationDeliveryStatusReceipt per canonical architecture. Max3 via ordinal0..2 CHECK + unique(root,ordinal). Root FK/cascade, unique perpart dispatch/provider IDs, immutable frozen payload/digest/ordinal/root identity. Persist immutable delivery deadlineAt and a state/deadline scan index for bounded asynchronous tail cancellation. Persist PREPARED/ADMITTED/ACKNOWLEDGED/DELIVERED/READ/FAILED/UNKNOWN/CANCELLED child states, ACK/status/failure timestamps and bounded codes. Do not invent provider state transitions in source service. Status receipts dedupe providerID/status/provider timestamp, attach optional part, indexed unmatched receivedAt for7day bounded cleanup; no raw webhook/customer JSON. Existing root/command provider columns remain compatible and untouched. Protect known provider evidence and immutable preparation against updates; migration safe for populated tables. No application/provider logic or network in migration. Coordinate exact generated field/enum names to architect before consumers.

### Sender identity columns

Part and status receipt require nonempty bounded providerAccountId and providerPhoneNumberId, frozen from server-owned sender authority. Receipt dedupe/correlation includes both plus providerMessageId/status/providerTimestamp; linking may not rely on MetaID alone. Index sender-bound correlation and unmatched retention. Exact role names HEADER/PRODUCT/ANSWER; payloadDigest64 lowercase hex. Immutable sourceIdentity is a bounded object JSON decoded only by Background, not a duplicate DB wire validator. Preserve valid read-before-ACK persistence; do not impose invalid cross-provider timestamp ordering.

## Work Items

- [x] Implement only assigned capability and document compatibility.
- [x] Complete meaningful required checks and regression/negative evidence.
- [x] Publish mirrored branch/report and return review, then stop.

## Interfaces / Contracts

Use canonical ARCH075 frozen decisions. Shared owns ordered schema/digest and existing perpart media exports; Database owns durable child/status identity; Background owns provider/current authorization and logical aggregation. Never duplicate validators or fabricate product/provider identity.

## Dependencies

None

## Enables

Only dependent tasks after architect acceptance; never begin them implicitly.

## Acceptance Criteria

- [x] Assigned bounded capability and frozen contract behavior satisfied.
- [x] Legacy reads/records remain compatible; no unauthorized cross-owner/billing/security change.
- [x] Durable/contract identity and fault cases satisfy required checks without silent fallback.
- [x] Canonical dedicated mirrored worktree, synchronization and recursive evidence recorded; no private proof committed.

## Validation

- [x] Prisma validate/generate and real PostgreSQL migration on populated legacy baseline.
- [x] Duplicate ordinal/provider/dispatch IDs, ordinal bounds, FK/cascade, immutable payload/provider evidence and indexed status lookup/dedupe tests; no destructive rollback assumptions.
- [x] Repository-required schema/migration checks and diff/ERD validation, inspect package scripts.
- [x] Diff/privacy hygiene and report actual results, no production sends or secrets.

## Stop Condition

After required work and validation, set review, submit Completion Report and STOP. No main merge/deploy or enabled task execution.

## Implementation Notes

You are not alone. Preserve others' edits and canonical prepared isolation. Root owns final merges/deployment. Architecture constants resolve inter-agent assumptions; report genuine gaps before expanding scope.

## Completion Report

### Status

Ready for Review. Implementation committed and pushed at `53a798fe7d31e2fcecf3dfec04e74b723933ba4d`; source PR [74](https://github.com/kodjobaah/moda-interact-database/pull/74). No implementation/main merge, hosted migration or provider call was performed.

### Files Changed

- `prisma/schema.prisma`: three additive enums, bounded child delivery-part model, normalized status receipt model and logical-root child relation; existing root/provider/command/status fields remain unchanged.
- `prisma/migrations/20261113004310_arch075_ordered_delivery_parts/migration.sql`: additive tables/enums, root/ordinal and provider uniqueness, JSON/digest/sender/evidence checks, immutable preparation/once-set outcomes and anti-reset guards, sender/message-bound receipt attachment and deadline/retention indexes.
- `scripts/test-arch075-delivery-parts-postgres.mjs`: real fresh/populated-upgrade, negative constraint, concurrent CAS, early callback, sender isolation, immutable evidence and cascade coverage.
- `scripts/test-arch075-human-root-postgres.mjs`: real original HUMAN command/root/physical-part compatibility with aggregate SENT and null scalar root MetaID.
- `scripts/test-arch075-deploy-history-postgres.mjs`: real Prisma deploy with an invocation-owned synthetic applied-but-missing historical file, preservation of that historical audit, pending additive application and no-op redeploy.
- `scripts/validate-arch075-delivery-parts.mjs` and `package.json`: additive-schema checks and owning validation commands.
- `docs/arch075-delivery-parts.md`, bounded additions to `docs/generated/prisma-erd.puml`, and task-scoped generated `arch075-delivery-parts.puml/.png`: persistence, access-path, concurrency and rollout contract; focused diagram visually verified.

### Work Completed

The existing ConversationMessage remains the single logical billing/history/HUMAN-command anchor. New ConversationDeliveryPart rows have at most three unique ordinals 0..2, immutable role/payload/digest/source/sender/deadline identity and independently unique dispatch/provider IDs. SQL guards preserve assigned permits and outcome timestamps, prohibit preparation mutation and forbid terminal cancellation or read/delivered evidence from regressing into another attempt. Read may arrive before delivered or before ACK persistence without an invalid timestamp-order assumption.

Normalized status receipts have no raw webhook/customer JSON. Sender account/phone plus provider message/status/timestamp form their dedupe identity. First attachment requires both sender IDs and exact provider message identity to match the referenced part; received facts and existing attachment are immutable. Root cascade removes parts and attached receipts; unmatched rows remain eligible for bounded seven-day retention. Existing root/command triggers and all existing objects are unchanged.

Access paths correspond to exact root/ordinal freeze/read, unique part dispatch/provider lookup, state/deadline repair and sender-prefixed ACK correlation plus partial unmatched receivedAt/id retention pages. Child rows are bounded to three per logical reply; no new Shopify ingress write or billing ledger is introduced. Application-owned policy, per-part current authorization, complete plan decoding and aggregate state remain Background/Shared responsibilities. No provider/network call is made by a database transaction.

### Validation Results

- `npm ci --ignore-scripts` completed; workspace bootstrap supplied the declared Node24.19.0 runtime.
- Prisma `validate` and `generate` passed. Migration was authored with `prisma migrate dev --create-only` against an invocation-owned PostgreSQL17/pgvector container bound exclusively to loopback, then applied to that disposable database. No hosted development command was run.
- Final `npm run test:arch075-delivery-parts:postgres`: **123 assertions passed** across fresh and populated legacy upgrades, including exact unchanged legacy row, old writer compatibility, duplicate/bounded ordinals, FK/cascade, JSON/digest/sender bounds, immutable preparation/permit/Meta/timestamp/failure evidence, cancelled/unknown preservation, two real concurrent permit-CAS attempts with one winner, sender-scoped early READ receipt before ACK, read-before-delivered state and indexed lookup/retention/dedupe.
- `npm run test:arch075-human-root:postgres` passed against actual historical HUMAN triggers: original lease and atomic root/parts/admitted command linkage, header ACK does not mark logical success, claimed-lease reacquisition refused, and all-part ACK permits aggregate command/root SENT with root providerMessageId null and original logical dispatch key intact.
- `npm run test:arch075-deploy-history:postgres` passed using the real Prisma CLI: the synthetic historical applied-but-missing audit stayed unchanged, only pending ARCH075 applied and the subsequent deploy was a no-op. No hosted migration history was rewritten or resolved.
- `npm run test:arch075-delivery-parts`, `npm run test:arch068-conversation-delivery-plan`, `npm run test:first-production-baseline`, four-script scoped ESLint with max-warnings0 and diff checks passed. Repository declares no generic build/type script or GitHub workflow; Prisma generation and owning PostgreSQL checks provide the applicable validation.
- `npm run erd:puml` produced the full current schema projection; only the new five enum/entity blocks and five relations were retained in the global source as architect-directed. Focused PlantUML PNG rendered successfully at887x944 and was visually inspected complete. Existing global PNG remains byte-for-byte unchanged.
- All invocation-owned PostgreSQL containers and temporary migration fixtures were removed. No external connection string or production endpoint was supported by the executable database tests.

Physical worktree isolation from the prepared launcher packet:

- Canonical primary workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-DATABASE-001`; implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-DATABASE-001`.
- Both branches: `task/ARCH-075-DATABASE-001`; no shared/default checkout switched or mutated for implementation and no previous task worktree reused.
- Prepared parent origin/main already current at`c7938c5c110a17f0d06b0b2b98099aa60d644bbb`; implementation origin/main already current at`5329d5390d346042895219663f3a040ea54ae168`; no remote-task fast-forward needed in either repository.
- Launcher recursive submodule sync/update passed, with no implementation submodule entries. Prepared codex attempt1 claim was committed/pushed at`b61e36bc3a7728497d47cb0a5e0ddd4bd46a249e`; it was not repeated.

### Deviations

Prisma create-only output also proposed unrelated baseline index/FK renames/default changes. Those statements were excluded; the final migration contains only ARCH075 objects. After local application, a further dev prompt requested a separate unrelated drift migration; it was cancelled without creating or applying that migration. No historical migration file was edited.

Full ERD regeneration exposed pre-existing unrelated schema drift and the global raster renderer's4096px clipping limit. Architect approved bounded global PUML additions, preservation of the existing global PNG and a complete focused task-owned PUML/PNG. No unrelated ERD reconciliation was attempted.

### Assumptions

Shared validates contiguous ordered roles and trusted per-part plans. Background freezes the original complete source authority, controls sender/status attachment, enforces predecessor DELIVERED/READ and immutable deadline policy, retains one logical usage reservation and owns truthful logical-root/HUMAN aggregation. The database does not duplicate those policies.

### Unresolved Issues

Root owns accepted source merge, additive hosted migration and coordinated consumer rollout. No production verification or downstream implementation is claimed by this prerequisite task.

### Architectural Concerns

Do not reuse a single provider permit for multiple physical sends, clear UNKNOWN evidence for a retry, recapture a newer HUMAN/AI authority or attach callbacks using only a global MetaID. Per-part immutable evidence and sender correlation are explicit downstream contracts.

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
