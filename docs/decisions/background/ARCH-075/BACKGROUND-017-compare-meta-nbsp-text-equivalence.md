---
id: ARCH-075-BACKGROUND-017
architecture_id: ARCH-075
title: Compare observed Meta text with bounded NBSP equivalence
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 10
executor: codex
claimed_at: 2026-11-14T15:45:30Z
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

Background provider observed+expected reconciliation, selection/preparation and final registration fence; meaningful persisted status/current-source authority regression.

## Out of Scope

Shared releases, whitespace generalization, source/hash rewriting, guard bypass, provider registration/activation/live DB writes, unrelated refactor.

## Requirements

Root actual read-only Graph.find proves French expected BODY and observed BODY differ only U+00A0 NBSP replaced with ASCIIspace before two colons; HEADER IMAGE exact. Application-owned provider-comparison projection may normalize this specific codepoint in rendered provider text only. Do not normalize arbitrary strings/URLs/button URLs/identities/bindings, immutable prepared/source/submitted hashes or persisted snapshots. No trim/collapse/newline/NFKC/narrowNBSP normalization. Preserve exclusion of submission examples, exact category/parameters/status/current-source/timestamp checks. If embedded raw URL NBSP ambiguity arises, refuse rather than invent broad URL heuristics. Corresponding Admin/Background generic French vectors must agree; this is provider semantic equivalence, not a new shared serialization/crypto primitive. Reuse existing Shared technical digest/parser machinery where already available; no Shared release. Root normal reconciliation will replace observed comparison hashes after deployment; no migration/manual live data rewrite. Historical exact snapshot/hash reads remain exact. Real text/URL/button/binding/category changes must remain drift/failclosed. No provider calls/live operations or new logging payloads.

## Work Items

- [x] Audit all owning provider comparison paths.
- [x] Apply minimal text-only NBSP equivalence consistently.
- [x] Add negative trust/drift and persisted-path parity tests.
- [x] Record exact isolated source/check evidence.

## Interfaces / Contracts

Existing exact canonical component digest remains mechanism; app projection defines Meta content equivalence only. Coordinate identical vectors with sibling task ARCH-075-ADMIN-012. No new wire fields.

## Dependencies

None; current deployed6.0.1/source baseline accepted.

## Enables

Root normal reconciliation and immutable activation after both apps deployed.

## Acceptance Criteria

- [x] Generic French NBSP/ASCII observed text compares equal without modifying inputs/snapshots/submitted hashes.
- [x] All owning expected/observed/status/activation/finalpermit paths agree.
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

Ready for Review — exact source/checks published; no merge or live operations.

### Files Changed

- `provider-text-equivalence.ts`: bounded Meta display-text equivalence only.
- `contracts.ts`: hash-only audit evidence type; existing observedContentHash unchanged.
- `service.ts`: exact category/provider identity gates and frozenRAW representative on proven equivalence.
- `status-repository.ts`: validates hash-evidence consistency and atomically persists existing RECONCILE event evidence with status projection.
- Helper/service unit tests plus new disposable reconciliation→selector→SQL final-permit test.

### Work Completed

Exact source `eb732bac14aaee02b1db496377cb25ae3c1d3660` pushed on matching task branch, source PR229. No Shared/dependency/hash algorithm change. Only HEADER(TEXT), BODY, FOOTER and known button display-text leaves may map U+00A0 to ASCIIspace for comparison; URL/phone/identity/unsupported paths remain exact. Raw URL/placeholder NBSP ambiguity refuses equivalence; no trim/collapse/newline/NFKC/narrowNBSP normalization. Projection uses existing canonical component hash and existing example exclusion. Frozen source/compiled components/bindings/submitted hashes are never rewritten.

If expected and observed raw hashes differ but bounded display equivalence and exact category/provider identity hold, service persists original expectedRAW hash as existing-domain representative. Existing Admin/Shared selector/finalpermit hash consumers remain unchanged. Existing category/status/identity/POST_INTENT/CAS/time/current-source gates remain decisive. Repository requires proof to match the actual frozen raw expected hash and chosen representative, different lowercase64hex raw observed hash and exact normalization kind. Same transaction stores existing RECONCILE/CURRENT event evidence `{normalizationKind,rawObservedContentHash,expectedContentHash}` without raw content. True drift persists actual raw hash. No old status/event row rewrite; root normal reconciliation after deploy is the operational path.

Shared Admin golden fixture expected BODY `Boutique NBSP: Exemple / Panier NBSP: {{1}}` versus ASCIIspaces pins E `e17121a73dfea9c4202119663c50d123ff20f30f0b9d0d8158464c18d5741c77` and O `f6ee4fc0dc11c3ce77ca934eeb477841aa498dd00858a85d371e64219c8841cd`, normalizationkind `U+00A0_TO_U+0020_TEXT_ONLY`. Exact pair/field names relayed to Admin012 for independent raw-consumer parity tests.

### Validation Results

- Normal prepared launcher: primary `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; dedicated parent `moda-interact-workspace-task-ARCH-075-BACKGROUND-017` and implementation `moda-interact-workspace.worktrees/ARCH-075-BACKGROUND-017`, mirrored task branches. Initial parentdf5666d628bd4f237b8336b43e8e2ae7c14581ca/sourcec041c88757ec6d1ddc583dd2cde6e0cf92755796; remote task sync not-needed/originmain already-current both. Recursive database6f42b71112efe7ac63654d55f41cd74ca569b1ae ready with sync/update PASS. Attempt1/codex15:45:30Z claim14bebc9efb8a730b487b5717a4636856d6de9927 pushed. No primary/other-task writes.
- `npm ci --no-audit --no-fund`: PASS. Declared package scripts inspected; no package/lock change.
- Initial helper/service focused68/2files PASS; production `npm run build` PASS (Prisma generation and TypeScript). Final affected unit suite232/12files PASS, including existing reconciliation/admission/finalpermit and actual shared selection tests. Scoped ESLint all7 changed files PASS; diff/privacy PASS.
- Actual disposable PostgreSQL runner with new NBSP case plus existing arch047 lifecycle suite:2/2PASS,14.13s. Real claim/POST_INTENT/submission then reconciliation writes expectedRAW representative and exact hash-only event evidence. Real delegated Shared selector and actual locked SQL finalpermit accept it; substantive text, URL, category, provider ID, PAUSED status, stale timestamp, wrong binding fingerprint and disabled current assignment remain refused. Invalid evidence rejected before mutation. Source/locale/submitted/compiled/bindings unchanged; normal fresh equivalent re-observation is the only flag-clearing path. No actual Meta network calls.
- Exact source GitHub CI43612826090 and43612805748 bothSUCCESS at15:58:17Z/15:58:43Z, including actual typecheck and unit execution. Inspected43612826090 logs396files/4429testsPASS,81.36s. No broad duplicate local run.
- Logs `/tmp/bg017-focused-initial.log`, `/tmp/bg017-build.log`, `/tmp/bg017-postgres.log`, `/tmp/bg017-focused-final.log`, `/tmp/bg017-lint.log`; no raw production payload/credential fixtures committed. Full repository lint was not repeated; unchanged unrelated baseline errors are outside this task and no full-lint-green claim is made.

### Deviations

None. Authoritative raw-domain/evidence amendment followed; no normalized persisted hash domain or Shared selector adapter introduced.

### Assumptions

Root owns integration/deployment and normal production provider reconciliation; all provider calls in validation use injected fixtures/disposable infrastructure.

### Unresolved Issues

None within task. Production French normal reconciliation/rollout remains root-owned and unclaimed by this agent.

### Architectural Concerns

None; policy is Meta-specific application semantics, existing raw hashing/serialization mechanics remain unchanged.

## Architect Review

### Review Status

Accepted

### Review Notes

Independently inspected exacteb732bac14aaee02b1db496377cb25ae3c1d3660 and finalreportcab01ee15c7e54f9f71a46ca45feaf59b0a20e11. Bounded component display-text NBSP equivalence preserves existing RAW expected hash domain, category/provider identity exactness and immutable snapshots. Rawobservedhash/expectedhash/normalizationkind retained durably in existing reconciliation event transaction; true drift keeps actualrawhash. URL/placeholder ambiguity and all other whitespace changes refuse. No findings.

### Reviewed Files

Provider-text comparator, contracts evidence type, service reconciliation, status repository proof/event persistence and unit/disposable lifecycle tests. Existing hash mechanism/Shared selector unchanged.

### Validation Reviewed

Canonical sibling launcher/claim/sync/database evidence;68initial/232affected/build-types/scopedlint; actualPG2 including durable event→delegatedSharedselector→SQLfinalpermit and substantive/identity/status/binding/current-source negatives. ExactCI43612826090/43612805748 success,4429tests396files. No real provider/customer payload committed, no extra broad repeats.

### Architecture Conformance

Conforms owning Meta equivalence policy, hash/receipt/tenant/current-authority guards and immutable audit preservation. No Shared/dependency/schema/newwire or live writes. Normal root reconciliation establishes new evidence, no manual flag clear or historical rewrite. Separate BG018 UI request consumer does not block acceptance.

### Follow-up

Root source/main merge then actual parent pin, deployment/drain and audited normal service reconciliation. Admin012 tests-only parity acceptance independent. Pending provider approvals remain external, no rollout completion claim.
