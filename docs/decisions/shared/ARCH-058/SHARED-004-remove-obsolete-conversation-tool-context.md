---
id: ARCH-058-SHARED-004
architecture_id: ARCH-058
title: Remove the obsolete MCP conversation tool-context contract
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 36
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-058-SHARED-003
enables:
  - ARCH-058-SHARED-005
  - ARCH-058-SHARED-006
  - ARCH-058-SYSTEM-TEST-001
created: 2026-11-04
updated: 2026-11-04
---

# ARCH-058-SHARED-004: Remove the obsolete MCP conversation tool-context contract

## Architecture

Architecture ID: `ARCH-058`.

Parent: `docs/architecture/ARCH-058-commerce-agent-product-discovery.md`.

Boundary decision: MCP is a shop-scoped tool provider/executor. Background owns conversation identity, inbound version, retained grants, leases and human-control state. `docs/architecture/ARCH-058/contracts.md`, section 4.1, is authoritative.

Coordinator: `moda_architect`.

This task replaces the unexecuted revision-9 SHARED-004 publication task. Publication is now SHARED-006 because the final package must contain SHARED-003, SHARED-004 and SHARED-005 together.

## Objective

Remove the unused `CommerceConversationToolContextSchema` and `CommerceConversationToolContext` public exports that imply MCP understands conversation state, while preserving the legitimate Background/runner conversation contracts and the separately accepted outreach tool context.

## Context

The current source exports `CommerceConversationToolContextSchema` with `conversationId`, `inboundVersion` and `grantId`, but the corrected ARCH-058 runtime explicitly does not send or interpret that structure in MCP. Keeping the export invites future agents to restore the incorrect ownership boundary.

Background may continue to use `CommerceTurnIdentitySchema`, `CommerceAssertionSchema` and `CommerceConversationGrantSchema` locally. Existing initial-outreach adapters may continue to use `CommerceOutreachToolContextSchema` through the opaque trusted MCP `toolContext`; this task must not remove or change that separate contract.

## Scope

Modify only:

- `src/commerce/schemas.ts`
- `src/commerce/product-discovery-contracts.test.ts`
- `scripts/validate-commerce-entrypoints.mjs`
- `README.md`

If generated declarations are produced by the ordinary build, validate them but do not commit generated output unless that is already repository policy.

## Out of Scope

- Removing `CommerceTurnIdentitySchema`, `CommerceResolveAssertionSchema`, `CommerceExecuteAssertionSchema`, `CommerceAssertionSchema` or `CommerceConversationGrantSchema`.
- Removing or changing `CommerceOutreachToolContextSchema` or outreach execution behavior.
- Changing MCP request parsing, opaque `toolContext`, Background transport code or application behavior.
- Any hash work; SHARED-003 owns built-in identity.
- Date/time validation; SHARED-005 owns it.
- Package version/publication; SHARED-006 owns it.

## Requirements

1. Remove `CommerceConversationToolContextSchema` and `CommerceConversationToolContext` from the `/commerce` public surface.
2. Delete focused tests and entrypoint assertions whose only purpose is to validate/export that obsolete contract.
3. Update README export documentation to state the ownership boundary explicitly: Background owns conversation/grant/turn state; MCP receives authenticated shop identity and may forward only already accepted opaque adapter context such as outreach context.
4. Preserve the existing public conversation/runner schemas listed under Out of Scope without shape changes.
5. Preserve `CommerceOutreachToolContextSchema` unchanged.
6. Do not introduce a replacement conversation-to-MCP schema under another name.

## Work Items

- [x] Remove the obsolete schema/type exports.
- [x] Remove their focused tests and clean-process export check.
- [x] Correct README contract ownership text.
- [x] Prove legitimate conversation/grant and outreach exports remain available.
- [x] Run the required validation.

## Interfaces / Contracts

Removed public API in the later SHARED-006 major release:

```text
CommerceConversationToolContextSchema
CommerceConversationToolContext
```

Preserved examples include:

```text
CommerceTurnIdentitySchema
CommerceAssertionSchema
CommerceConversationGrantSchema
CommerceOutreachToolContextSchema
```

## Dependencies

- `ARCH-058-SHARED-003`

## Enables

- `ARCH-058-SHARED-005`
- `ARCH-058-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] `CommerceConversationToolContextSchema` and `CommerceConversationToolContext` are absent from source/declarations/entrypoint inventory.
- [x] No replacement public contract sends conversation ID, grant ID, inbound version, lease or human-control state to MCP.
- [x] `CommerceAssertionSchema`, `CommerceConversationGrantSchema` and `CommerceOutreachToolContextSchema` retain their current shapes.
- [x] Product-discovery and runner focused tests pass.
- [x] No application repository is modified by this task.

## Validation

```bash
npm ci --no-audit --no-fund
npm run test:product-discovery-contracts
npm run typecheck
npm run build
npm run validate:commerce-entrypoints
rg -n 'CommerceConversationToolContext' src/commerce --glob '!*.test.ts' || true
git diff --check
```

The grep must produce no occurrence in production Commerce source. Negative tests, the entrypoint verifier and README may name the removed export while proving/documenting its absence. `npm run validate:commerce-entrypoints` must prove the built `/commerce` package does not export either removed symbol.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, set status to `review`, complete the report, return to `moda_architect` and STOP. Do not begin SHARED-005 or publication.

## Implementation Notes

Do not confuse the removed conversation-specific contract with the existing opaque `toolContext` transport extension point. The latter remains available for already accepted adapters such as initial outreach; MCP discovery/authorization does not interpret it as conversation authority.

## Completion Report

### Status

Review

### Files Changed

 - `README.md`
 - `scripts/validate-commerce-entrypoints.mjs`
 - `src/commerce/product-discovery-contracts.test.ts`
 - `src/commerce/schemas.ts`

### Work Completed

 - Removed `CommerceConversationToolContextSchema` and its inferred type from the public Commerce schemas.
 - Removed obsolete contract assertions while retaining recommendation tests; the clean-process verifier now rejects both removed runtime exports and generated declaration names.
 - Confirmed the verifier still sees turn identity, resolve/execute assertions, assertion union, conversation grant and outreach context exports.
 - Documented Background ownership of conversation/grant/turn state and the limited opaque MCP adapter-context boundary.
 - Implementation commit: `2efd9cd` (`Remove obsolete Commerce conversation context`), pushed to `task/ARCH-058-SHARED-004`.

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-058-SHARED-004`
  parent branch: `task/ARCH-058-SHARED-004`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-058-SHARED-004`
  implementation branch: `task/ARCH-058-SHARED-004`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Recursive implementation submodules:
  git submodule sync --recursive: passed
  git submodule update --init --recursive: passed
  status: ready; no recursive submodule entries

### Validation Results

 - `npm ci --no-audit --no-fund`: passed.
 - `npm run test:product-discovery-contracts`: passed; 76 passed, 1 skipped, 0 failed.
 - `npm run typecheck`: passed.
 - `npm run build`: passed; generated the Commerce package declarations.
 - `npm run validate:commerce-entrypoints`: passed; clean-process runtime imports retain expected exports and neither removed name appears in the built `/commerce` declarations.
 - `rg -n 'CommerceConversationToolContext' src/commerce --glob '!*.test.ts' || true`: no production-source matches.
 - `git diff --check`: passed.

### Deviations

The focused test command initially could not start because the prepared worktree had no installed dependencies; the required `npm ci` resolved this. The verifier checks the bundled `dist/commerce/index.d.ts` emitted by the repository build.

### Assumptions

The launcher confirmed the sole dependency, SHARED-003, was complete at `59ea61f34197d64180e46680ac6d552b5e989a36`.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

**Accepted — Attempt 1, 2026-11-04.** Implementation `2efd9cd` satisfies the bounded removal task. No blocking findings identified. Task marked `complete` under automatic completion mode; executor and claim cleared, Attempt 1 preserved.

### Reviewed Files and Conformance

Reviewed all four changed files against implementation main: `src/commerce/schemas.ts`, `src/commerce/product-discovery-contracts.test.ts`, `scripts/validate-commerce-entrypoints.mjs` and `README.md`. Only the obsolete conversation tool-context schema/type are removed from production source. Legitimate turn/assertion/grant and outreach schemas retain their shapes. No replacement conversation-to-MCP contract is introduced. Documentation explicitly assigns conversation/grant/turn state to Background while preserving the opaque accepted adapter-context boundary.

The clean-process verifier rejects both removed runtime names and their names in generated Commerce declarations, and asserts availability of the preserved conversation/runner and outreach schema exports. Package version/publication and timestamp work remain with their designated follow-on tasks. No application repository is modified.

### Independent Validation

Executed from the dedicated implementation worktree with Node 24.19.0:

- `npm run test:product-discovery-contracts`: **76 passed, 1 skipped, 0 failed**. The skipped case is the existing actual Commerce projector/publication integration case; it is not counted as passed.
- `npm run typecheck`: passed.
- `npm run build`: passed, including generated declarations.
- `npm run validate:commerce-entrypoints`: passed; actual clean-process Commerce/runner imports and public export assertions executed.
- Production Commerce source search for `CommerceConversationToolContext`: no matches.
- Implementation comparison whitespace check: passed. Implementation checkout was clean before verification.

Local verification log: `/tmp/arch058-shared004-review.log` (not a committed artifact). Existing installed dependencies were used; this review did not rerun npm ci or publish a package.

### Isolation and Follow-up

Reviewed the Completion Report's prepared isolation/synchronization evidence. Parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-058-SHARED-004`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-058-SHARED-004`, both using `task/ARCH-058-SHARED-004`.

SHARED-005's sole prerequisite is now Complete, so it is promoted to `ready` at Attempt 0 with no claim. SHARED-006 remains pending on SHARED-005; no enabled task is executed. This acceptance does not complete ARCH-058 or authorize publication.

The developer explicitly authorized committing and pushing this acceptance review on 2026-11-04. Only parent task documentation is changed; no implementation code, dependency, gitlink or main branch is modified.

## Architect Dependency Reconciliation (2026-11-04)

SHARED-003 Attempt 2 is accepted and Complete at `59ea61f34197d64180e46680ac6d552b5e989a36`. The sole prerequisite is satisfied; this task is ready, unclaimed, at Attempt 0. Normal launcher preparation and source integration gates remain required. No implementation is started by this promotion.

## Post-Acceptance Dependency Reconciliation (2026-11-04)

SHARED-004 is accepted and Complete at `2efd9cd`. SHARED-005 is Ready, unclaimed, at Attempt 0. SHARED-006 remains Pending until SHARED-005 completes. The earlier Attempt 0 handoff above is retained as historical context.
