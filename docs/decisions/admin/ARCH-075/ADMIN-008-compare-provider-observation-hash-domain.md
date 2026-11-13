---
id: ARCH-075-ADMIN-008
architecture_id: ARCH-075
title: Compare provider drift within the observed component hash domain
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 5
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-075-ADMIN-007
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Compare provider drift within the observed component hash domain

## Architecture

ARCH075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Show genuine Meta component/category drift without comparing provider observation fingerprints to unrelated prepared-content hashes.

## Context

After ADMIN007, root's canary created20/20 templates; approved observed rows have driftDetectedAt null but UI reports provider drift. Actual source meta/contracts.ts hasMetaProviderDrift compares lastObservedContentHash (normalized components excluding examples) with submittedContentHash (prepared plus bindings). Existing publishing/validation.ts observedMetaContentHash(componentsSnapshot) is the correct existing canonical provider fingerprint and common-activation/preview.ts already uses it. This task corrects that narrow safe status projection/UI predicate; no provider or approval mutation is needed.

## Scope

Admin meta safe status DTO/server projection, browser-safe drift predicate and directly affected status/table tests. Reuse existing canonical provider fingerprint server-side; preserve all existing moderation/approval/freshness/technical-retry/publish/activation guards.

## Out of Scope

Background/Shared/Database or schema changes; new hashing implementation; provider calls/retries/activation; raw component/credential exposure; false approval promotion; unrelated authoring/translation changes; repeated unaffected fifteen PostgreSQL suites.

## Requirements

- Compute expected provider observation hash from trusted persisted componentsSnapshot using existing observedMetaContentHash on the server. Carry only the bounded safe hash (for example expectedProviderContentHash) in the status DTO; do not move Node crypto or server publishing dependencies into client contracts/components.
- Compare observed to expected within this same hash domain. submittedContentHash remains its existing immutable prepared-content identity and must not be relabeled/recomputed/overwritten.
- Preserve true content drift, observed category mismatch and explicit driftDetectedAt. Missing/malformed unverifiable expected fingerprint must fail closed when an observation exists; it must never clear genuine drift or manufacture approval. Before observation, preserve existing unobserved/pending behavior and keep approval/freshness/absence/retry gates independent.
- Hash only trusted validated component data server-side. Unexpected malformed snapshots must produce safe unavailable/fail-closed status, not secrets/raw JSON or an unhandled permissive fallback. Reuse existing parser where required; do not add competing canonicalization.
- All hasMetaProviderDrift callsites and safe DTO construction must align. No caller-controlled expected hash is an authority; action/submission/activation authorization remains server-owned.
- Test an actual-domain approved fixture where submitted hash legitimately differs from provider fingerprint yet observed equals canonical components; UI must not label drift. Changing body/button/header component content, category or timestamp must still report drift. Excluded example-only differences must not create provider drift; prepared identity checks remain distinct.
- Root alone verifies deployed UI against canary observations before expansion/activation. Local source acceptance does not establish provider-wide/live success.

## Work Items

- [ ] Capture current domain mismatch regression and inspect all status DTO/predicate callsites.
- [ ] Reuse existing server fingerprint with browser-safe DTO/predicate and fail-closed negatives.
- [ ] Validate focused status/UI/source-boundary checks and publish exact mirrored report/source.

## Interfaces / Contracts

Admin-internal MetaRegistrationView safe DTO only. Existing persisted schema and observedMetaContentHash mechanism unchanged; no Shared package contract/publication.

## Dependencies

ARCH-075-ADMIN-007 architect-accepted Complete and integrated parent9aa7e7c70.

## Enables

Root-owned deployed canary UI readback and later approval/activation operations; no implicit runtime task.

## Acceptance Criteria

- [ ] Correct matching provider observation does not falsely show drift merely because prepared hash differs.
- [ ] Content/category/explicit/malformed drift remains fail closed; pending/unobserved and independent lifecycle gates preserved.
- [ ] Safe DTO includes only required fingerprint; canonical Node hashing remains server-only.
- [ ] Required tests/checks and isolation/synchronization evidence pass with no live mutations.

## Validation

- [ ] Focused RED/GREEN status/projection/UI tests with actual distinct hash domains, example exclusion, content/category/timestamp/malformed negatives and pending semantics.
- [ ] Relevant declared Admin unit/security/type/lint/build checks; actual client/server build graph excludes Node hashing from client. No repeat unaffected15PG suites.
- [ ] Diff/privacy and exact-head remote checks, canonical launcher worktree/synchronization/recursive evidence.

## Stop Condition

Publish exact source and mirrored completion report, set review, return to architect and stop. No self-accept, main merge, provider action or rollout.

## Implementation Notes

Normal launcher-prepared dedicated mirrored task worktrees required. You are not alone; preserve current main/primary originals. No competing hash codec or scope expansion. Return cross-owner gap before implementation.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

### Deviations

None

### Assumptions

Root canary evidence establishes visible false positive; no live approval/activation changes authorized by this task.

### Unresolved Issues

Real rollout and live message proof remain root-owned.

### Architectural Concerns

Return any new contract/dependency gap.

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

ARCH075 remains In Progress pending actual approvals/activation/delivery verification.
