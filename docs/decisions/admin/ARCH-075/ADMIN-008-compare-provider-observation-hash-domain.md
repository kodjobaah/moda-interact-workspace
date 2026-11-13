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
status: complete
priority: 5
executor: codex
claimed_at: 2026-11-13T19:08:40Z
attempt: 1
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

- [x] Capture current domain mismatch regression and inspect all status DTO/predicate callsites.
- [x] Reuse existing server fingerprint with browser-safe DTO/predicate and fail-closed negatives.
- [x] Validate focused status/UI/source-boundary checks and publish exact mirrored report/source.

## Interfaces / Contracts

Admin-internal MetaRegistrationView safe DTO only. Existing persisted schema and observedMetaContentHash mechanism unchanged; no Shared package contract/publication.

## Dependencies

ARCH-075-ADMIN-007 architect-accepted Complete and integrated parent9aa7e7c70.

## Enables

Root-owned deployed canary UI readback and later approval/activation operations; no implicit runtime task.

## Acceptance Criteria

- [x] Correct matching provider observation does not falsely show drift merely because prepared hash differs.
- [x] Content/category/explicit/malformed drift remains fail closed; pending/unobserved and independent lifecycle gates preserved.
- [x] Safe DTO includes only required fingerprint; canonical Node hashing remains server-only.
- [x] Required tests/checks and isolation/synchronization evidence pass with no live mutations.

## Validation

- [x] Focused RED/GREEN status/projection/UI tests with actual distinct hash domains, example exclusion, content/category/timestamp/malformed negatives and pending semantics.
- [x] Relevant declared Admin unit/security/type/lint/build checks; actual client/server build graph excludes Node hashing from client. No repeat unaffected15PG suites.
- [x] Diff/privacy and exact-head remote checks, canonical launcher worktree/synchronization/recursive evidence.

## Stop Condition

Publish exact source and mirrored completion report, set review, return to architect and stop. No self-accept, main merge, provider action or rollout.

## Implementation Notes

Normal launcher-prepared dedicated mirrored task worktrees required. You are not alone; preserve current main/primary originals. No competing hash codec or scope expansion. Return cross-owner gap before implementation.

## Completion Report

### Status

Ready for Review. Exact source `049a7534f657494c4ad38e8fe755fc1c854004b6`, pushed on mirrored `task/ARCH-075-ADMIN-008`; Admin PR97 https://github.com/kodjobaah/moda-interact-admin/pull/97 . Exact-head Vercel deployment and Preview Comments checks succeeded. Source worktree is clean; root owns merges and live UI verification.

### Files Changed

- `src/lib/admin/whatsapp-templates/meta/contracts.ts`: safe expected-provider fingerprint field and pure same-domain drift predicate.
- `src/lib/admin/whatsapp-templates/meta/status.ts`: server-only validated expected fingerprint using existing `parseComponents` and `observedMetaContentHash`.
- `tests/unit/arch075-meta-provider-drift.test.tsx`: actual distinct-domain status/DTO/summary/table, drift/malformed/example/pending/retry regressions.
- `tests/unit/arch047-template-meta-components.test.mjs`: browser/server dependency-boundary assertion.

### Work Completed

Captured RED: matching normalized provider components were incorrectly reported drifted because the prepared-plus-bindings identity was different. Server projection now computes `expectedProviderContentHash` from trusted persisted components with the existing codec. Invalid/empty snapshots return null without raw JSON/errors or permissive fallback. The browser compares observed to this safe fingerprint; `submittedContentHash` retains its separate immutable identity unchanged.

Real body/header/button/category drift, explicit drift timestamp and malformed observed/expected hashes remain fail closed. Before observation, pending/unobserved behavior remains unchanged. Approval status, reconciliation/freshness, provider-absence retry, submission, publication and activation authorization remain independent and unchanged. All three UI callsites consume the same safe DTO/predicate. No provider call, persisted update, new hash implementation, schema, dependency or cross-service change.

### Validation Results

No source changes after the exact committed head. Canonical bootstrap Node24.19.0/npm11.17.0:

- Focused status/Meta-service/publication tests:48 passed; prior single-domain-mismatch regression failed as expected before the fix.
- Declared full `npm run test:unit`:837 passed,0 failed/skipped. Includes matching approved UI, genuine header/body/button changes, category/timestamp/malformed negatives, example exclusion, safe DTO privacy/bounded reads and pending/retry lifecycle behavior.
- Declared `npm test`:331 passed,0 failed; three build-dependent tests initially skipped. After production build the real server bootstrap/export/failure-isolation suite passed3/3,0 skipped.
- `npx tsc --noEmit`, declared ESLint and production build: passed. Lint retains the unchanged nested Database anonymous-default-export warning; build retains optional BullMQ Valkey warnings. No dependency changes.
- Exact final production graph: existing provider-parser/observation-codec marker in2 server outputs and0 static/client JavaScript outputs. Browser contract has no Node hashing/publishing import; no raw components were added to its safe registration DTO.
- Exact-head remote Vercel and Preview Comments: SUCCESS. No GitHub Actions workflow is declared in this repository.
- Diff/privacy/explicit four-file staging whitelist and clean source worktree: passed. No live provider/shop identities, credentials or operational exports published. Unaffected fifteen PostgreSQL suites were not repeated, as scoped.

### Preparation / Isolation Evidence

Normal `/moda-task` preparation: Attempt1/codex, dependency gate passed, durable parent claim `acfb8b6f9e97b09bd6e35c2ec4a039c540303359`. Launcher fetched/synchronized both task branches with current main and initialized/verified recursive submodules. Implementation base `8d5acec9813dbd11d610dd4121d1353a21dacd26`; unchanged nested Database `2e14f8668346dfc135aa12f8d1fbc94e05c12ce7`.

Canonical primary workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-ADMIN-008`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-ADMIN-008`. Matching mirrored branch; no primary/shared checkout switching, main push/merge or unrelated task edits.

### Deviations

None. Existing canonical server hashing and parser reused; no new framework or codec.

### Assumptions

Root's canary observations establish the visible false positive. Provider status remains provider-owned; this read-only presentation correction does not promote approval or clear persisted drift.

### Unresolved Issues

Root must verify the deployed canary UI before expansion/activation. Local/remote source checks do not establish platform-wide live approval or message delivery.

### Architectural Concerns

None newly discovered; no cross-owner gap or broader scope change.

## Architect Review

### Review Status

Accepted

### Review Notes

Independently reviewed exact source `049a7534f657494c4ad38e8fe755fc1c854004b6` and immutable report `f7e695cd207f022e18020943b2ce93de6e293e99`. Expected provider component fingerprint is server-derived using existing canonical parser/hash; submitted prepared identity remains untouched. Browser predicate compares same-domain fingerprints and retains fail-closed true content/category/timestamp/malformed drift and unobserved pending behavior. No findings.

### Reviewed Files

Both production files meta/contracts.ts and meta/status.ts plus focused service/component regressions and all predicate callsites. Reviewed safe DTO privacy, existing codec reuse, launcher physical isolation/synchronization/recursive evidence and unchanged nested Database.

### Validation Reviewed

Focused48 and full837 unit passed, security331 plus all3 postbuild real-server runtime checks passed; exact typecheck/lint/build and Vercel/Preview checks green. Build graph confirms0client/2server codec markers. Diff/privacy and clean four-file source whitelist passed. Unaffected15PG suites deliberately not repeated. No redundant heavy rerun.

### Architecture Conformance

Conforms to Admin-internal read-only status ownership. Safe expected hash only crosses browser boundary; canonical Node hashing stays server-side. No new codec, schema, dependency, provider mutation or BG/Shared change. Approval, freshness, absence/retry, publication and activation authorizations remain independent. Source presentation correction does not alter persisted drift or manufacture provider approval.

### Follow-up

Root integrates source then accepted parent/gitlink and verifies deployed canary UI against actual observations before expansion/activation. Real provider approvals, coordinated activation and genuine ordered Meta/AI/human/logo/product/checkout delivery proof remain separate. ARCH075 remains In Progress.
