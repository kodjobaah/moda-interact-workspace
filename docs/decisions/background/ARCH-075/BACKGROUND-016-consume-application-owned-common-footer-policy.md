---
id: ARCH-075-BACKGROUND-016
architecture_id: ARCH-075
title: Consume application-owned common footer policy
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
claimed_at: 2026-11-14T14:19:39Z
attempt: 1
depends_on: []
enables: []
created: 2026-11-14
updated: 2026-11-14
---

# Consume application-owned common footer policy

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; moda_architect.

## Objective

Consume application-owned common footer policy.

## Context

User requests compact one-bubble AI product lists and website in clickable caption footer instead of image header. Published6 reader currently hardcodes website/header and checkout placement business policy; correct ownership once, saved template remains source of truth. No live source/activation changes by agents.

## Scope

Adopt exact published reader and implement Background application policy at every common reference selection/read/frozen/finalpermit/native preparation path. Allow saved website in checkout.available conditional before trusted checkout URL final line, unique trusted name/site/checkout bindings, allowed-variable authority. Remove website-in-header assumptions without dropping rendered boundary/hash/receipt proof. No URL counting/strip heuristics over authored answer; no invented URLs. Existing immutable common refs remain frozen and current-source locks authoritative. Final checkout and STOP/body preservation remain app-owned. No Shared business rules/release or live writes.

## Out of Scope

Unrelated refactors, arbitrary user-programmable layouts, new database/infrastructure, main merges/live operations. Preserve all others work.

## Requirements

Adopt exact published reader and implement Background application policy at every common reference selection/read/frozen/finalpermit/native preparation path. Allow saved website in checkout.available conditional before trusted checkout URL final line, unique trusted name/site/checkout bindings, allowed-variable authority. Remove website-in-header assumptions without dropping rendered boundary/hash/receipt proof. No URL counting/strip heuristics over authored answer; no invented URLs. Existing immutable common refs remain frozen and current-source locks authoritative. Final checkout and STOP/body preservation remain app-owned. No Shared business rules/release or live writes.

## Work Items

- [ ] Implement only defined owning capability.
- [ ] Add meaningful affected behavior regressions.
- [ ] Record exact source and required checks.

## Interfaces / Contracts

Shared owns technical structure/hash/render safety; applications own trusted bindings/placement/operational authority. Existing Shared6 published source immutable. No duplicated shared codec.

## Dependencies

ARCH-075-SHARED-015

## Enables

None; dependent promotions architect-owned.

## Acceptance Criteria

- [ ] Defined capability and owning-policy boundaries satisfied.
- [ ] Hash/identity/tenant/receipt/permit and mandatory content integrity retained.
- [ ] Required checks and exact immutable reports complete; no live/merge actions.

## Validation

Exact reader/app rejection tests including Shared technically accepts alternate frames while host rejects noncanonical application source; website absent from bitmap and once clickable caption, checkout last; tamper/stale/current-source/finalpermit/AI/HUMAN/native checks, types/build/scopedlint/exact CI. Local exact accepted pack tests may precede release; final registry lock/npmci required after actual approved publication.

## Stop Condition

After required work/checks publish matching source and parent report, set review and STOP. Do not continue dependent work.

## Implementation Notes

Normal moda-task canonical sibling isolation/claim required. You are not alone; do not revert others. Pending consumer tasks may perform preparatory source work only after explicit architect Ready amendment; final acceptance requires accepted published dependency. No unpublished sibling imports or fabricated registry lock.

## Preparatory execution authority

Root explicitly authorizes independent concurrent Background specialist for common-layout policy/admission and dependency adoption only. Do not modify BG015 compact helpers/presentation proof/receipts. Start normal canonical currentmain sibling; sync accepted BG015 main before final coherence checks if it merges first. API unchanged. Verify exact accepted Shared014 local6618d7 artifact no-save/no-lock for candidate tests; no fabricated registry lock. Final acceptance requires actual approved Shared015 publication, real registry lock/npmci and remote CI. Publication must await concrete consumer policy tests, so Ready permits preparatory source and pack validation independently of final release. No live operations.

## Completion Report

### Status

In Progress — concrete candidate source/tests pushed; final publication/registry checks held.

### Files Changed

- New common-layout-policy.ts: application-owned trusted binding/placement admission wrapper over canonical Shared reader.
- common-layout.ts: receipt/rendered-boundary/current-source readers use owning policy.
- composition.ts: selectedCommonLayout only substitutes policy reader import/call; no compact product edits.
- recovery-template-common.ts: native source/reference identity paths use same app policy.
- New focused policy tests and separate disposable PostgreSQL current-source authority test.

### Work Completed

Initial source be0128b593323b87297b111327fbf10cc741d419 pushed on matching task branch. Shared remains technical snapshot parser; Background requires exactly one trusted name in header, one website in old header OR checkout-aware conditional, empty static footer, exactly one checkout conditional, allowed bindings only, and exact trusted checkout token on final separate line. All direct exported reader callsites audited and routed through this app policy. Original valid header-site sources are preserved byte-for-byte. No source rehash/rewrite, arbitrary authored text surgery, model/compact/permit/billing change.

### Validation Results

- Exact accepted Shared014 archive6618d7c97e99c1e75ab67240ba940a5a5eade2a37a5661de000f25c5ade3a97a SHA verified; clean npmci then no-save/no-lock install; all161 installed archive files byte-identical.
- Focused candidate tests24/24PASS2files: new app policy/native identities/website caption plus existing immutable/frozen common receipt tests. Structurally valid forbidden/duplicate/missing/trailing content rejected by host before SQL; exact website caption/native parameters and old hashes retained.
- Candidate build/types/scopedlint PASS. Expanded affected suite276/19files PASS. Separate actual disposable PostgreSQL locked-source test1/1 PASS: reviewed website-caption source accepted, stale editVersion/sourceHash/contentHash refused, replacement with structurally intact forbidden customer binding refused, old selected reference refused after switch. No fixture/timeout/guard weakening. Logs /tmp/bg016-build-candidate.log, /tmp/bg016-types-candidate.log, /tmp/bg016-scopedlint.log, /tmp/bg016-expanded-focused.log and /tmp/bg016-postgres-candidate.log. Draft source PR228. Preliminary remoteCI43605019489 failed under still-declared public6.0.0: Shared technical-acceptance assertion returns invalid at new policy test41; exact failed log inspected. This is the deliberately held new-publication gate, not passing CI. Final actual published6.0.1 adoption/real registry lock/npmci/remote CI held until root approval+publication. No fabricated registry metadata.
- Prepared launcher: canonical primary /Users/kwadwoadomafriyie/project/moda-interact-workspace; parent /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-BACKGROUND-016 and implementation /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-BACKGROUND-016, both task/ARCH-075-BACKGROUND-016. Initial parent8ffc7049778d4d400f7629dd6a4d7a056ee4eb1f; source d0c968e68d38031a9b3e884301573adbcbb08652. Both remote task sync not-needed/originmain already-current. Recursive database6f42b71112efe7ac63654d55f41cd74ca569b1ae ready, sync/update passed. Attempt1/codex claimed14:19:39Z commit6a3f94440529919986cea98282914f23a716674f pushed. No primary/other-task edits.

- Root requested integration of accepted BG015 main9d82f403272c7832b8abcbdf672676028551b061. Merged INTO task implementation branch90c5775; sole composition.ts conflict was two new imports, both preserved. No compact runtime edits. New test-only b8453d3cd5ef696288088a1afeed314c004f6e0e verifies actual AI/HUMAN service composite generation with saved website caption, exact header image-provenance input without URL and successful frozen-plan reread. Combined affected63/3files PASS; combined types/scopedlint PASS. Prior expanded276/19 and PG1 proofs retained (policy runtime unchanged). Final public registry checks remain held.

### Deviations

None. Preparatory execution authorized despite publication final gate.

### Assumptions

Root owns all merges/live/provider operations and exact public approval. Final sync with accepted BG015 main before coherent acceptance if it integrates first.

### Unresolved Issues

Actual approved6.0.1 publication and final registry checks pending; task remains In Progress.

### Architectural Concerns

None; semantic reader policy is deliberately application-owned rather than a duplicated Shared structural codec.

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

None
