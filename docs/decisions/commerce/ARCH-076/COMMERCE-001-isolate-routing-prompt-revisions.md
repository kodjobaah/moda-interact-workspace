---
id: ARCH-076-COMMERCE-001
architecture_id: ARCH-076
title: Exclude routing-only prompt revisions from normal Commerce configuration
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables: [ARCH-076-BACKGROUND-004, ARCH-076-SYSTEM-TEST-001]
created: 2026-11-15
updated: 2026-11-15
---

# Isolate routing-only prompt revisions

## Architecture

ARCH-076; [parent architecture](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md), coordinator moda_architect.

## Objective

Prevent normal Commerce Studio configuration from reading, seeding or activating routing-only prompt revisions.

## Context

ADMIN003 publishes immutable PLATFORM revisions in the existing prompt lineage, tagged `sourceContext.purpose = RECOVERY_ROUTING` and schemaVersion 1, without changing the normal agent pointer. Existing Commerce `prompt-service.ts#setPointer` checks PUBLISHED/exact scope but not purpose, so Studio can otherwise activate such a revision. Admin's normal-agent guard does not protect this separate repository. This bounded correction is required before live routing prompt activation; ADMIN003's own source acceptance is independent.

## Scope

Commerce-owned prompt configuration services/read models, normal draft seed/read selection and applicable Studio selectors/server actions. Start at `src/commerce/agent-configuration/prompt-service.ts`, effective configuration and prompt revision reads. Inspect actual current repository tests/package commands before implementation.

## Out of Scope

Admin implementation, new prompt lineage/table/schema, Shared changes/publication, model configuration refactor, routing execution, provider calls, live settings and deferred SYSTEM-TEST execution.

## Requirements

- [x] Application-owned purpose guard rejects a revision tagged RECOVERY_ROUTING from every ordinary normal Commerce activation path, even when PUBLISHED, exact PLATFORM scope and explicitly supplied by ID.
- [x] Normal revision listings, effective read models and draft seeds exclude routing-only revisions. Do not simply remove sourceContext from projections and lose evidence. An already-invalid active pointer fails closed with a bounded actionable error; never silently choose another active prompt or repair configuration by writing during a read.
- [x] A normal draft created without an active pointer uses the latest eligible normal revision, not a newer routing revision. Preserve existing scope/shop, PUBLISHED/DRAFT, edit-version/CAS, immutable content hash, role and audit behavior.
- [x] Normal revision numbering shares the existing lineage with routing publication. Allocate against actual latest revision under existing concurrency controls, so excluding routing revisions from candidates does not reuse their revision numbers.
- [x] Same protection applies to explicit platform/shop activation entry points as appropriate; wrong owner/scope remains rejected. Ordinary untagged revisions retain current behavior. Treat purpose as application policy, not a new Shared business enum.
- [x] No new schema or Shared release. No normal pointer/model/prompt editVersion changes caused merely by reading, listing or rejecting routing revisions.

## Work Items

- [x] Inspect all normal Studio prompt activation/read/seed entry points in the current accepted main.
- [x] Implement the bounded application-owned purpose exclusion consistently.
- [x] Add focused tests for explicit activation, no-active seed, effective read and shared-lineage revision allocation.
- [x] Run declared focused validation and complete the report in canonical launcher-prepared worktrees.

## Interfaces / Contracts

Existing CommerceAgentPromptRevision.sourceContext JSON carries purpose RECOVERY_ROUTING; published prompt schema and existing normal agent pointers are unchanged. Admin owns routing publication and recovery.routingAgent pointer. Commerce owns ordinary Studio activation/reads. Background revalidates routing prompt references at use. The purpose discriminator does not authorize tenant access or substitute for exact scope validation.

## Dependencies

None. The tag contract is defined here and in the accepted parent architecture; fixtures can seed tagged rows without waiting for Admin deployment. ADMIN003 acceptance is not blocked by this task, but live routing activation and BG004 acceptance require it Complete.

## Enables

ARCH-076-BACKGROUND-004 and final deferred integrated routing validation.

## Acceptance Criteria

- [x] Tagged PLATFORM PUBLISHED revision cannot become an ordinary active Commerce prompt via explicit Studio API/action.
- [x] Newest tagged revision is absent from normal candidate/seed paths; normal revision numbers remain collision-free.
- [x] Tagged current pointer produces a visible refusal without fallback or mutation; normal exact-owner CAS behavior remains intact.
- [x] Focused tests, required checks and mirrored worktree evidence are recorded; no live calls or unrelated source changes.

## Validation

- [x] Unit/service tests cover tagged and untagged revisions, missing/malformed context, exact scope, unauthorized owner, draft/published state and stale CAS.
- [x] Disposable PostgreSQL service tests prove rejected tagged activation leaves normal pointer/editVersion/audit unchanged; normal fallback seed skips newest tagged revision while allocating beyond actual latest; existing invalid active pointer read is refusal and read-only; concurrent ordinary/routing-like revision inserts preserve uniqueness/CAS behavior.
- [x] Existing relevant prompt/effective configuration tests, declared typecheck/lint and production build appropriate to changed code.
- [x] Git diff check; no schema/Shared/live configuration changes. Inspect package.json and existing harnesses rather than inventing scripts. These task-local checks do not execute SYSTEM-TEST.

## Stop Condition

After Work Items, Acceptance Criteria and Validation pass, set review, return Completion Report and STOP. Do not activate routing or begin another task.

## Implementation Notes

Reuse the existing authorization, prompt storage, CAS and audit mechanisms. A small repository-local purpose predicate is application policy; do not import Admin source or duplicate generic parsing/cryptography. If an inaccessible current module or existing schema prevents the guard, return the concrete gap to architect instead of widening ownership.

## Completion Report

### Status

Ready for Review. Implementation committed/pushed and all required checks passed on the exact source tree. No self-acceptance or main merge.

### Files Changed

- `src/commerce/agent-configuration/prompt-purpose.ts`: repository-owned routing-purpose predicate.
- `prompt-service.ts`: normal lineage filtering, explicit activation/mutation guards, read-only invalid-pointer refusal, eligible normal seed and actual shared-lineage revision numbering.
- `effective-configuration.ts`: retain purpose evidence through resolution and reject routing-only active instructions before returning normal configuration.
- Prompt/effective unit tests and `tests/arch076-prompt-isolation-postgres.test.ts`.
- Invocation-owned disposable PostgreSQL runner and package script; no dependency version/lock or database pin change.

### Work Completed

- Examined all Commerce normal prompt reads and mutation entry points. Current normal Studio prompt selectors consume the service/effective models; model-only state exposes no prompt content and remains unchanged.
- Routing-tagged PLATFORM or SHOP revisions are absent from normal lineage reads. They cannot be selected by explicit ID, edited or published through normal prompt commands, even when otherwise exact-scope and PUBLISHED. The purpose check occurs before projection, rather than removing its evidence first.
- Existing routing-only active pointers produce actionable refusal in pointer/effective reads; no fallback, write, model pointer or edit-version change occurs during reads. An omitted-text draft refuses an invalid active pointer too.
- An explicit draft text or template still copies that source exactly. When text is omitted, a valid normal active revision or latest eligible PUBLISHED normal revision seeds the draft. The existing lineage lock now allocates actual maximum revision + 1 across all purposes, including routing-only rows and numbering gaps.
- Existing SUPER_ADMIN authority, exact-owner/scope checks, immutable hashes, CAS, operation receipt and audit mechanisms are preserved. No Shared business enum/schema/release, new database structure or live mutation.

### Validation Results

- `npx vitest run tests/agent-configuration-prompts.test.ts tests/agent-configuration-effective.test.ts tests/agent-configuration-platform-prompt-ui.test.tsx --maxWorkers=1`: **49/49 passed** on final committed source.
- `npm run test:arch076-prompt-isolation:postgres`: **5/5 passed** using accepted recorded migrations on private loopback `pgvector/pgvector:pg17`. Proves both-scope routing refusal without pointer/version/audit change, latest normal seed while numbering beyond a tagged revision/gap, invalid active pointer read/draft refusal without mutation, authorization/owner/CAS behavior, and shared-lineage concurrent normal/routing-like allocation. Owned container removed; no deployment credentials/provider/network calls inherited into tests.
- `npm run lint`: exit 0, zero errors; 10 existing warnings in unrelated files only.
- `npm run typecheck`: exit 0, schema sync and route type generation passed.
- Prisma client generation passed from recorded database pin `5329d5390d346042895219663f3a040ea54ae168`.
- `npm run build`: exit 0, webpack compilation, packaged manuals/runtime smoke, Prisma generation, TypeScript, static page generation and final route/build traces passed. One existing Nunjucks dynamic-dependency warning only.
- `git diff --check`: passed. No schema/Shared/live settings or deferred SYSTEM-TEST execution.

### Execution and VCS Evidence

Prepared execution packet `/tmp/arch076-commerce001-prepared.json` was read in full. Mechanical startup/claim/submodule preparation was not repeated.

- Canonical primary workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-076-COMMERCE-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-076-COMMERCE-001`.
- Both branches: `task/ARCH-076-COMMERCE-001`. Shared/default checkouts were not switched or mutated; no other task worktree reused.
- Launcher parent remote task fast-forward not-needed; origin/main incorporated yes (final gate already-current). Implementation fast-forward not-needed; origin/main already-current.
- Launcher recursive submodule sync/update passed and recorded database pin `5329d5390d346042895219663f3a040ea54ae168`; unchanged by this task.
- Existing attempt 1 claim `5e527fbbd6f8fc0950715623da17c759979ff10b`, claimed `2026-11-15T13:59:51Z`, preserved.
- Implementation committed/pushed `59735a4e6c248734afea37c6792594b5cb24d738`, tree `500ca32e165d9974a02cd0ff46f4e5128aca175d`; PR https://github.com/kodjobaah/moda-interact-commerce/pull/197. No main merge/push, parent gitlink or Architect Review edits by this agent.

### Post-review Merge Evidence

Root accepted the bounded source implementation and merged PR197 to actual Commerce main `608ce7e6bb1ed96171b57671ef20861b0824b792`. This repository agent fetched that commit and independently verified its tree equals the tested source `59735a4e6c248734afea37c6792594b5cb24d738`: both are `500ca32e165d9974a02cd0ff46f4e5128aca175d`, with an empty diff. Required passing checks therefore cover the exact merged tree without redundant reruns.

The parent task branch incorporated current `origin/main` before this evidence update. Root/architect retains Accepted review, automatic completion, active-claim clearing and final Commerce gitlink authority. This agent keeps status `review` and leaves Architect Review unchanged; it has not merged main, staged a gitlink or changed live settings.

### Deviations

None. The omitted-text draft seed and actual max revision allocation implement the explicit task requirement; supplied text/template behavior is unchanged.

### Assumptions

The existing application-owned `sourceContext.purpose = RECOVERY_ROUTING` marker remains the cross-application purpose discriminator. Any marker version is excluded from normal Commerce; this does not replace exact scope validation.

### Unresolved Issues

None in the bounded implementation. Test-first rollout and production deployment holds remain coordinator-owned.

### Architectural Concerns

None within this bounded task. Routing and conversation allowance renewal remain independent.

## Architect Review

### Review Status

Accepted — automatic completion, 15 November 2026.

### Review Notes

Root accepted source59735a4e6c248734afea37c6792594b5cb24d738 and merged Commerce PR197 to actual main608ce7e6bb1ed96171b57671ef20861b0824b792. Independently fetched merge and verified identical tree500ca32e165d9974a02cd0ff46f4e5128aca175d and empty source diff. Preserved prepared attempt1 history and canonical worktree/sync/recursive evidence in report; clear active executor/claimed_at on completion. No live changes or provider calls.

### Reviewed Files

Actual prompt-purpose.ts, prompt-service.ts normal lineage/seed/pointer guards, effective-configuration.ts purpose-preserving refusal, focused unit and PostgreSQL cases. Root reviewed complete bounded change.

### Validation Reviewed

Final49 unit/UI/effective checks,5 disposable PostgreSQL cases, lint, typecheck and full production build all passed. Actual accepted merged tree is identical; no redundant implementation reruns. Existing unrelated warnings are recorded. SYSTEM-TEST was not executed.

### Architecture Conformance

Normal Studio reads/seeds/mutations/activation reject routing-tagged revisions, exact owner/scope/auth/CAS/audit retained, true latest shared-lineage numbering prevents collision. Invalid active pointer fails closed without mutation/fallback; normal model settings unaffected. No Shared or schema changes.

### Follow-up

BG004 still Pending until BG003 Complete; neutral/policy Admin dependencies are already Complete. This acceptance removes the Commerce isolation activation gate only, not remaining runtime/test-first production gates. SYSTEM-TEST remains deferred. Parent gitlink records actual merged Commerce main; root handles final integration.
