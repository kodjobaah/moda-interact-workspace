---
id: ARCH-075-ADMIN-012
architecture_id: ARCH-075
title: Compare observed Meta text with bounded NBSP equivalence
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 10
executor: codex
claimed_at: 2026-11-14T15:45:18Z
attempt: 1
depends_on: []
enables: []
created: 2026-11-14
updated: 2026-11-14
---

# Compare observed Meta text with bounded NBSP equivalence

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; moda_architect.

## Objective

Align provider observation equivalence with evidenced NBSP transport normalization while retaining exact immutable source identity.

## Context

Production French initial/follow-up registrations currently PROVIDER_DRIFT; private evidence root-owned, use generic fictional French fixtures only. Scope necessary current rollout fix, no provider/source mutation.

## Scope

Admin provider-content hash used by status DTO/publication equivalence/common activation; meaningful persisted activation/publication regression.

## Out of Scope

Shared releases, whitespace generalization, source/hash rewriting, guard bypass, provider registration/activation/live DB writes, unrelated refactor.

## Requirements

Root actual read-only Graph.find proves French expected BODY and observed BODY differ only U+00A0 NBSP replaced with ASCIIspace before two colons; HEADER IMAGE exact. Application-owned provider-comparison projection may normalize this specific codepoint in rendered provider text only. Do not normalize arbitrary strings/URLs/button URLs/identities/bindings, immutable prepared/source/submitted hashes or persisted snapshots. No trim/collapse/newline/NFKC/narrowNBSP normalization. Preserve exclusion of submission examples, exact category/parameters/status/current-source/timestamp checks. If embedded raw URL NBSP ambiguity arises, refuse rather than invent broad URL heuristics. Corresponding Admin/Background generic French vectors must agree; this is provider semantic equivalence, not a new shared serialization/crypto primitive. Reuse existing Shared technical digest/parser machinery where already available; no Shared release. Root normal reconciliation will replace observed comparison hashes after deployment; no migration/manual live data rewrite. Historical exact snapshot/hash reads remain exact. Real text/URL/button/binding/category changes must remain drift/failclosed. No provider calls/live operations or new logging payloads.

## Work Items

- [x] Audit all owning provider comparison paths.
- [x] Verify Background-proven expected-RAW representative parity through unchanged Admin comparisons.
- [x] Add negative trust/drift and persisted-path parity tests.
- [x] Record exact isolated source/check evidence.

## Interfaces / Contracts

Existing exact canonical component digest remains mechanism; app projection defines Meta content equivalence only. Coordinate identical vectors with sibling task ARCH-075-BACKGROUND-017. No new wire fields.

## Dependencies

None; current deployed6.0.1/source baseline accepted.

## Enables

Root normal reconciliation and immutable activation after both apps deployed.

## Acceptance Criteria

- [x] Background-proven French representative passes Admin gates while actual expected/observed RAW hashes stay distinct and inputs/snapshots/submitted hashes remain unchanged.
- [x] Admin expected/status/publication/common-activation paths agree on the raw expected representative; corresponding selector/finalpermit proof remains Background017-owned.
- [x] Substantive text/URL/binding/category and other whitespace changes still failclosed.
- [x] Required tests/checks/remote and report complete; no live operation.

## Validation

- [x] Focused actual provider-hash/status/admission tests and matching cross-app golden vectors.
- [x] Meaningful disposable PG owning reconciliation/publication/activation/current-authority proof.
- [x] Types/scopedlint/build/exact remote checks, diff/privacy. No unrelated broad repeats; inspect declared scripts.

## Stop Condition

After work/checks publish matching source+parent report, set review and STOP; root owns all merges/liveops.

## Implementation Notes

Normal moda-task dedicated canonical sibling worktree/claim. You are not alone; do not revert others. Preserve all local/staged work. Read applicable policy/role/AGENTS; report ambiguous boundary rather than broaden normalization.

## Authoritative raw-hash-domain correction

Root accepted concrete Sharedselector boundary finding: persisted lastObservedContentHash MUST remain existing raw expected-component projection domain. Do NOT change Admin/Shared observation hash algorithm. Background reconciliation alone may prove expected-vs-observed provider component equivalence with bounded text U+00A0→ASCIIspace, strict identity/category/status and URL/binding guards. If equivalent, persist expectedRAW projection hash as canonical representative; true drift retains actualrawhash. No preexisting row/flag rewriting or manual clear. Normal root reconciliation establishes proof after deployment.

When representative differs from actualrawobservedhash, durable MetaEvent.evidence MUST retain rawobservedhash, expectedhash and explicit normalizationkind U+00A0_TO_U+0020_TEXT_ONLY, with no raw text/URLs/secrets. Existing unrelated flags/status/identity/category checks stay exact. Admin task is now PARITY/REGRESSION VERIFICATION ONLY unless actual necessary application gap proven; do not add needless normalizer. Tests exercise real representative observation through existing Admin status/publication/activation/frozen identity with negative drift/category/bindings/URLs. Background tests must prove immutable snapshot/source/submitted hashes untouched, durable evidence complete and current selector/finalpermit accepts only actual proven equivalent observation. No Shared release.

## Completion Report

### Status

Ready for Review — tests-only parity verification complete on exact pushed source; no Admin runtime/hash/dependency changes.

### Files Changed

- `tests/fixtures/arch075-meta-nbsp.ts`: generic French cross-app expected/observed golden pair and hash-only evidence kind.
- `tests/unit/arch075-meta-provider-drift.test.tsx`: raw hash-domain/status DTO/UI parity and substantive text, URL, category, explicit-flag and other-whitespace negatives.
- `tests/unit/arch047-template-publication-pure.test.ts`: real frozen registration/publication representative, exact source/prepared/submitted identity and binding/status/URL negatives.
- `tests/integration/arch075-common-activation.postgres.test.ts`: current-profile persisted French receipt, durable evidence privacy, timestamp/content/category/flag gates, full cohort activation and unchanged snapshots.

### Work Completed

Source `e2ffe1f2147146963aa6d42603bf610e0629a7df` pushed on `task/ARCH-075-ADMIN-012`, Admin PR [101](https://github.com/kodjobaah/moda-interact-admin/pull/101). Exactly four test/fixture files changed; `src/`, package/lock, database and existing hash functions are unchanged.

Audited the actual expected-provider hash DTO (`meta/status.ts`), registration/publication equivalence (`publishing/validation.ts`) and fresh observed-content/current-profile activation gate (`common-activation/preview.ts`). Existing exact Admin comparisons already accept Background's proven expected-RAW representative. No normalizer or runtime change is needed or added.

Pinned the BG017-coordinated generic golden pair: expected raw hash `e17121a73dfea9c4202119663c50d123ff20f30f0b9d0d8158464c18d5741c77` and actual observed raw hash `f6ee4fc0dc11c3ce77ca934eeb477841aa498dd00858a85d371e64219c8841cd`. They deliberately remain different. Only the simulated proven receipt uses expected RAW as its observation representative. Durable evidence retains actual raw observed hash, expected hash and `U+00A0_TO_U+0020_TEXT_ONLY`; the status DTO does not expose that evidence or raw content.

The persisted test explicitly simulates BG017's separately tested reconciliation result, not a worker invocation or an Admin equivalence proof. It verifies the unchanged Admin gate contract across all 20 reviewed locales and a 40-target conservative cohort. Background017 owns bounded equivalence, provider identity/category validation and selector/final SQL permit proof. Root owns deployment and normal reconciliation; no manual row/flag rewrite is performed here.

### Validation Results

- Declared unit runner over provider-drift/status, publication-pure and common-activation suites: **43 passed, 0 failed, 0 skipped**. Final narrow status rerun after refining its corresponding prepared-identity fixture: **10 passed**; counts overlap, not an aggregate unique total.
- Declared `npm run test:arch075-admin-common-activation:postgres`: **2 passed**. Real current-profile saved/read/reviewed cohort accepts expected-RAW representative, rejects unproven actual raw hash, category/explicit drift/substantive content changes and stale reconciliation, then preserves source/prepared/submitted/locale snapshots and normal activation/audit/replay/rollback behavior. Durable hash-only evidence remains server-side. Disposable container removed; no hosted database used.
- Publication fixture uses the actual `frozenLocaleSnapshot` canonical TEXT registration bindings, retaining sourceHash/localeContentHash and exact expected snapshot checks rather than relaxing any guard.
- `npx tsc --noEmit`: passed. Configured scoped ESLint invocation returned zero errors with four repository ignore warnings: tests are intentionally excluded by the existing lint configuration; actual runner/typecheck validate these changed files. No lint override or runtime change introduced.
- Declared `npm run build`: passed, terminal exit 0; existing optional BullMQ Valkey resolution warnings unchanged. Production browser graph across **71 JS files** contains no Node renderer/font-loader/frozen-verifier markers.
- Exact source `e2ffe1f2147146963aa6d42603bf610e0629a7df`: **Vercel SUCCESS** at 2026-11-14T16:01:08Z; Preview Comments SUCCESS at 16:01:09Z.
- Diff/privacy/isolation checks passed; source branch clean. Generic fictional fixtures only, no production IDs, raw provider/customer content or credentials. No unrelated broad checks or Shared release.

### Deviations

The authoritative raw-hash-domain amendment supersedes the initial normalizer wording. This task verifies parity only; changing Admin normalization would break the existing raw selector/permit domain and was deliberately not implemented.

### Assumptions

Background017 proves bounded text equivalence before recording the expected-RAW representative and preserves actual raw evidence. Admin retains all independent source/approval/freshness guards. Root coordinates source integration, deployment and normal live reconciliation; no main merge or live operations by this agent.

### Unresolved Issues

None within Admin parity verification. Background017 runtime proof and root deployment/reconciliation remain separately owned and are not claimed by these Admin tests.

### Architectural Concerns

No necessary application gap found: one unchanged raw domain is retained through status/publication/common activation and the delegated selector/permit boundary. No new hashing primitive, schema, compatibility branch or Shared business policy.

Isolation: primary root `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-ADMIN-012`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-ADMIN-012`; both `task/ARCH-075-ADMIN-012`. Launcher verified remote/main synchronization and recursive Database `2e14f8668346dfc135aa12f8d1fbc94e05c12ce7`; implementation base `3f316edb00499abd0040ccf95fd6d06ad1f319bc`. Attempt1 claim `563a4784d7efebc9d8da0041cac646efa10fba49` pushed. No primary/default or other task source changed.

## Architect Review

### Review Status

Accepted

### Review Notes

Independently inspected exacte2ffe1f2147146963aa6d42603bf610e0629a7df all four test files and reportedffb75bfceb0a74617e1591f389a578fc2d27d9. Tests prove unchanged Admin raw component hashes accept only Background-proven expectedRAW representative, not actual differing raw hash alone. Current-profile forty-target activation/status/publication remains strict with source/binding/category/freshness/drift negatives. No runtime normalizer or hash rewrite added. No findings.

### Reviewed Files

Fictional cross-app golden vectors, status/drift UI tests, publication equivalence tests and actual common activation PostgreSQL workflow. Evidence is hash-only and immutable snapshots retained.

### Validation Reviewed

Dedicated launcher/claim/synchronization evidence;43focused plus10narrow status, disposablePG2 currentprofile/cohort/audit/privacy, types/build exit0/browser71graph, exact Vercel16:01:08 success. ScopedESLint0errors/four configured ignored-test warnings transparently disclosed. No unnecessary runtime/build-contract changes.

### Architecture Conformance

Conforms narrowed tests-only app parity scope, unchanged Shared/dependencies/rawhash/runtime and independent BG017 implementation. No provider/live/database production operations or inferred rollout completion.

### Follow-up

Root source merge, actual parent gitlink integration and optional automatic deploy verification. Production French reconciliation/activation remains root-owned; pending provider statuses not bypassed.
