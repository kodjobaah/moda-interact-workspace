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
status: in_progress
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

- [ ] Audit all owning provider comparison paths.
- [ ] Apply minimal text-only NBSP equivalence consistently.
- [ ] Add negative trust/drift and persisted-path parity tests.
- [ ] Record exact isolated source/check evidence.

## Interfaces / Contracts

Existing exact canonical component digest remains mechanism; app projection defines Meta content equivalence only. Coordinate identical vectors with sibling task ARCH-075-ADMIN-012. No new wire fields.

## Dependencies

None; current deployed6.0.1/source baseline accepted.

## Enables

Root normal reconciliation and immutable activation after both apps deployed.

## Acceptance Criteria

- [ ] Generic French NBSP/ASCII observed text compares equal without modifying inputs/snapshots/submitted hashes.
- [ ] All owning expected/observed/status/activation/finalpermit paths agree.
- [ ] Substantive text/URL/binding/category and other whitespace changes still failclosed.
- [ ] Required tests/checks/remote and report complete; no live operation.

## Validation

- [ ] Focused actual provider-hash/status/admission tests and matching cross-app golden vectors.
- [ ] Meaningful disposable PG owning reconciliation/publication/activation/current-authority proof.
- [ ] Types/scopedlint/build/exact remote checks, diff/privacy. No unrelated broad repeats; inspect declared scripts.

## Stop Condition

After work/checks publish matching source+parent report, set review and STOP; root owns all merges/liveops.

## Implementation Notes

Normal moda-task dedicated canonical sibling worktree/claim. You are not alone; do not revert others. Preserve all local/staged work. Read applicable policy/role/AGENTS; report ambiguous boundary rather than broaden normalization.

## Authoritative raw-hash-domain correction

Root accepted concrete Sharedselector boundary finding: persisted lastObservedContentHash MUST remain existing raw expected-component projection domain. Do NOT change Admin/Shared observation hash algorithm. Background reconciliation alone may prove expected-vs-observed provider component equivalence with bounded text U+00A0→ASCIIspace, strict identity/category/status and URL/binding guards. If equivalent, persist expectedRAW projection hash as canonical representative; true drift retains actualrawhash. No preexisting row/flag rewriting or manual clear. Normal root reconciliation establishes proof after deployment.

When representative differs from actualrawobservedhash, durable MetaEvent.evidence MUST retain rawobservedhash, expectedhash and explicit normalizationkind U+00A0_TO_U+0020_TEXT_ONLY, with no raw text/URLs/secrets. Existing unrelated flags/status/identity/category checks stay exact. Admin task is now PARITY/REGRESSION VERIFICATION ONLY unless actual necessary application gap proven; do not add needless normalizer. Tests exercise real representative observation through existing Admin status/publication/activation/frozen identity with negative drift/category/bindings/URLs. Background tests must prove immutable snapshot/source/submitted hashes untouched, durable evidence complete and current selector/finalpermit accepts only actual proven equivalent observation. No Shared release.

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

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual code

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

Root deployment and normal reconciliation
