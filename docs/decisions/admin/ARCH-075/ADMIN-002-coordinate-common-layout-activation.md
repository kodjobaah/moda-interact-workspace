---
id: ARCH-075-ADMIN-002
architecture_id: ARCH-075
title: Coordinate approved common-layout activation
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-11-13T04:17:42Z
attempt: 1
depends_on:
  - ARCH-075-ADMIN-001
  - ARCH-075-BACKGROUND-002
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Coordinate approved common-layout activation

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Coordinate approved common-layout activation.

## Context

The user explicitly requires all Meta templates, AI replies and HUMAN messages to share one shop header and checkout footer, with product images separate. Existing Admin-owned SHARED wrapper definition/slot is the common immutable content authority; family-specific body/offer/opt-out content stays intact. No duplicate hardcoded frame builders.

## Scope

Existing Admin approved-source/publication preview, SHARED wrapper activation/CAS/audit and registered replacement readiness. Source capability only; no live provider publication or activation.

## Out of Scope

Other repositories, new database tables/settings, provider permissions, live registrations/activation, source merges, unapproved publication, changing billing/cap semantics, arbitrary source refactors, automatic mutation of approved templates. Background engine001 uses accepted published5.13.9 compatible readers and remains producer-disabled.

## Requirements

Use existing publication operation/target snapshots, SHARED slot version CAS and audit in bounded serializable transactions; no new setting/table. Preview exact affected active Meta stage/offer/locale/shop slots and selected common revision. Every required replacement must have provider APPROVED/content-equivalent registration and matching canonical commonRef; stale/missing locale, approval, source, active-pointer or current slot mismatch refuses activation. Do not claim cross-shop atomicity from existing per-shop operations/global SHARED slot. Before implementing, return any actual inability to coordinate global common pointer with target assignments safely. Required behavior is one reviewed common revision across newly sent Meta/AI/HUMAN, not silent mixed versions.

Source/approval workflows must keep existing Meta snapshots immutable, clone/register/review replacements; live provider submission/activation remains root-owned after concrete review. Background consumer must be deployed before selecting new projections. Existing approved outreach outside customer window remains a template send only, no new product freeform tail. Runtime mismatches fail closed before provider. Preserve compatible legacy frozen messages. Test concurrent Admin/slot/provider drift, all-or-no-switch per intended transaction boundary, idempotent replay and audit. Stop with explicit architectural gap if broader schema/contract change is necessary.

### Bounded global activation contract

Inspection found existing operations publish one definition in per-shop transactions while the SHARED pointer is global. Sequential reuse is insufficient. Use one strict Admin-local versioned coordinator snapshot in existing publication operation JSON, discriminated as `schemaVersion: 2`, `kind: COMMON_RECOVERY_ACTIVATION`. It binds the exact common reference, expected SHARED pointer/version, complete cohort fingerprint, per-definition immutable source/registration identities and reviewed shop/assignment digests, actor/reason and override acknowledgement. The coordinator may reference the common definition through the existing definition FK if schema-compatible. Existing per-definition operation/target audit records may be committed COMPLETE in the same transaction with coordinator linkage; do not duplicate the complete manifest per child or misrepresent existing counters. Ordinary v1 progress/advance must never process the v2 coordinator. Exact operation-key replay is idempotent; changed actor/fingerprint/intent refuses.

Conservative implementation bounds: at most six reviewed scenario definitions, 50 shops, 1,000 replacement locale targets and independently 1,000 currently selectable affected variants; canonical snapshot at most 1 MiB. Enumerate with limit-plus-one and refuse overflow before mutation. These are safety bounds, not measured throughput. Cover the complete globally affected selectable cohort, including exact unchanged assignments where applicable; no arbitrary subset under a global pointer. Larger cohorts require a returned architecture gap rather than partial activation.

Commit all assignments, operation/target outcomes, SHARED CAS/lifecycle and audits in one serializable transaction, with existing 30-second timeout and 10-second maximum lock wait. No network, page commits or silent automatic reconfirmation. On conflict/timeout roll back everything and require appropriate reviewed retry. Acquire one shared activation/publication advisory fence before protected reads, use consistent lock order and actual row/version checks, and include every relevant ordinary writer or equivalent proven database conflict. An advisory lock alone does not protect an uncooperative writer; root's writer audit and concurrent real-PostgreSQL tests must demonstrate coverage.

Preserve historical AI/HUMAN slots. Accepted Background common mode selects a valid active common SHARED source before legacy audience overrides; show that precedence rather than deleting the older slots. Activation still requires both-environment producer rollout and drain evidence. No live action is authorized by this task.

### Existing source catalogue gate

When common-layout mode is activated, new publication/submission of unstamped legacy saved/queued definitions must refuse with a clone-with-common-layout action. Do not retrofit current common content during an HTTP send, mutate old snapshots or silently publish duplicate versions. Active replacement cohort is reviewed from real supported scenario inventory, not merely two existing NO_OFFER definitions. Root reviews copy and coverage before external registration. Existing legacy records stay readable/cloneable and historical sends unchanged.

### Explicit live registration environment constraint

User authorizes recovery template registration in PRODUCTION Meta account only. Root then copies the approved immutable catalogue/registration metadata and referenced common source coherently to test for the same provider assets. Never initiate duplicate external registration from test. Keep local source/reference/locale identities and provider WABA/content/approval proof consistent; no fabricated approval or source-hash rewrite. Actual callback/status environment routing must be verified before claiming live ordered test processing: copied provider metadata alone does not prove delivery callbacks reach the test database. Root owns every live registration/copy/activation action after concrete review.

## Work Items

- [ ] Complete assigned bounded capability only.
- [ ] Prove compatibility and meaningful negative/failure behavior.
- [ ] Submit mirrored branch/report and stop.

## Interfaces / Contracts

Common content authority: selected immutable Admin SHARED wrapper revision and locale projection. Shared owns canonical semantic key/wrapper validation; Admin owns authoring/compiler/reference/activation; Background owns tenant-derived values, frozen rendering, sending and current fences. Existing template registration hashes remain authority for provider components.

## Dependencies

ARCH-075-ADMIN-001, ARCH-075-BACKGROUND-002

## Enables

Only explicitly promoted dependent tasks after acceptance.

## Acceptance Criteria

- [ ] One common content source is used without duplicated formatting or unauthorized semantic widening.
- [ ] Old stored projections/registrations remain readable and immutable; new fields do not grant tenant/provider authority.
- [ ] Assigned validation and isolated mirrored synchronization evidence are complete.

## Validation

- [ ] Actual PostgreSQL coordinated activation, stale source/slot/approval/locale and concurrent conflict/replay tests.
- [ ] Declared relevant tests/types/lint/build and exact-head CI; no live registration mutation.

## Stop Condition

After required work and validation, submit review and STOP. No enabled-task execution, merge, live mutation or unapproved public release.

## Implementation Notes

You are not alone; preserve other changes. Canonical prepared packet is startup/isolation authority. Report actual cross-owner gaps rather than inventing a setting/schema or weakening strict validation.

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

None beyond approved contracts.

### Unresolved Issues

None currently; return concrete gaps.

### Architectural Concerns

Preserve one common content authority and immutable prior registrations.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual source review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
