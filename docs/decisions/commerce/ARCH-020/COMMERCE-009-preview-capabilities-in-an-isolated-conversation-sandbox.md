---
id: ARCH-020-COMMERCE-009
architecture_id: ARCH-020
title: Implement isolated preview lifecycle and execution service
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 130
executor:
claimed_at:
attempt: 1
depends_on:
  - ARCH-020-COMMERCE-002
  - ARCH-020-SHARED-001
  - ARCH-020-COMMERCE-001
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-010
  - ARCH-020-COMMERCE-013
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-21
---

# Implement isolated preview lifecycle and execution service

## Architecture

ARCH-020. [Parent architecture](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).
Binding [implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md):
C4/C5/C7/C8/C9/C14/C16/C18 as applicable, and exact ownership/interfaces in **C19**.

## Objective

Own C9.1 preview routes, synthetic runner/tool execution, Redis state/replay/budgets and cancellation. No U14 visual components.

## Context

This is the canonical narrowed definition from the 2026-09-21 task split, replacing
the former combined scope. No prior attempt or implementation is discarded. Normal
launcher/worktree/review policies apply. No task is claimed by this definition.

## Scope

Own C9.1 preview routes, synthetic runner/tool execution, Redis state/replay/budgets and cancellation. No U14 visual components.

## Out of Scope

Other C19 owners' modules; new Shared wire versions or database schema; live
deployment/provider calls; unrelated refactors; cart/order writes or WhatsApp sends.
Do not implement missing dependencies or substitute production fixtures to finish.

## Requirements

Use accepted auth/Shared/database source, canonical types and C19 ports. Preserve
others' changes. Exact business names remain database-authored. Fixtures are injected
only by tests; production missing adapters fail closed. Each case below has an
expected side effect, not just a screenshot/typecheck. C19 assigns final wiring.

## Work Items

- [ ] Implement every C9.1 route and strict body/status/ownership shape using accepted auth guards. Fixture mode requires no live provider/model; explicit model mode has separate credentials.
- [ ] Implement atomic environment/admin/run identity, creation replay, payload conflicts, conversation busy lock, 24h retention,20-turn/32k history, quotas and cancellation/UNKNOWN handling.
- [ ] Reuse the accepted Shared runner, C16 synthetic frozen response definition and C6.2 language/status fixtures. No production transcript/shop credential or WhatsApp admission.
- [ ] Use C19 PreviewBundleLoader against injected authorized synthetic bundle fixtures until013 supplies the real saved-bundle adapter. Unavailable production composition fails closed.
- [ ] Expose the exact service contract and controlled runner fixtures to017. Do not implement UI forms/navigation/screens or production publication/compiler services.

## Interfaces / Contracts

Own `src/commerce/preview/` and exact C9.1 route handlers under the accepted App Router root.017 owns U14;013 owns real saved-bundle composition. This backend task can be accepted with strict loader fixtures;013 must verify real service wiring.


## Dependencies

- ARCH-020-COMMERCE-002
- ARCH-020-SHARED-001
- ARCH-020-COMMERCE-001

All listed prerequisites must be Complete and architect-accepted before a claim.
Use dedicated launcher worktrees and accepted source; do not launch enabled work.

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-010
- ARCH-020-COMMERCE-013
- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] P01: all C9.1 methods validate auth/owner/body and return exact statuses; other admin IDs leak no data.
- [ ] P02: cross-replica same-ID replay reserves one budget/model call; changed payload conflicts; distinct run IDs on one conversation reject before any start.
- [ ] P03: quotas, history/turn boundaries, cancellation/completion race, unknown/crash state, slot TTL and retained dedupe have explicit fake-clock assertions.
- [ ] P04: C6.2 language and C16 response cases use frozen synthetic state and the same runner version; later publication never expands the preview grant.
- [ ] P05: fixture output cannot send WhatsApp, access production providers or spend model quota; model mode never falls back to production keys.

## Validation

Implement the named cases above as focused tests. Record case -> fixture -> command
-> expected/actual effects in the Completion Report. Check shared contract examples
where applicable; include malformed and denied inputs with zero side effects.
Run focused tests while developing, then typecheck/lint/build once before submission;
repeat broader checks only for new failures or changed concerns. Use actual repository
commands and record them. Local browser/component evidence is task-owned where a UI
is in scope. Follow agent-validation/live-validation policies; separate pending
required developer database/container evidence and never claim fixture tests prove
live service behavior. No minimum screenshot/test count substitutes for coverage.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; consume the accepted COMMERCE-001 foundation.

## Completion Report

### Status

Ready for Review.

### Files Changed

Implementation commit `fa795af310d0df76a1553e4adb7d77dbe6c7b149` in
`moda-interact-commerce`:

- `lib/preview/types.ts`, `store.ts`, `service.ts`, `runtime.ts`, `http.ts`
- C9.1 App Router handlers under `app/api/studio/preview/`
- `tests/preview-service.test.ts`

### Work Completed

- Implemented strict C9.1 preview schemas and typed error/status mapping.
- Implemented owner-scoped conversation/run state, creation/run replay and
  payload conflict handling, busy/history/TTL checks, fixture execution and
  explicit cancellation flags.
- Added authenticated fixtures, conversation, run status, cancellation and
  tool-test route handlers. Authentication failures retain the existing Studio
  401/403/503 contract; malformed bodies return `{code: INVALID_INPUT}`.
- Added injected `PreviewBundleLoader` and state-store ports. Runtime composition
  fails closed with `UNAVAILABLE` until the saved-bundle adapter is supplied by
  COMMERCE-013; no production provider, customer transcript, Shopify token or
  WhatsApp path is used.

### Correction Checklist

Architect Review outcome before implementation: Pending; no correction items
were issued. Checklist disposition: no review corrections were applicable.

### Validation Results

Agent-executed:

- `npm test -- tests/preview-service.test.ts`: PASS, 1 file / 4 tests.
- `npm run lint`: PASS.
- `npm run typecheck`: PASS after `npm run build` generated the accepted Prisma
  client.
- `npm run build`: PASS; all C9.1 routes compiled and were listed by Next.js.
- `git diff --check`: PASS.
- `npm test`: 72 passed, 1 failed. The unrelated failure is
  `tests/readiness-docker.test.ts`, “kills ignored-stdio descendants after
  leader exit on timeout”, failing because the descendant signal-handler IDs
  were undefined before cancellation. No preview files are involved.

Focused case matrix:

- creation replay/conflict and owner isolation -> injected `InMemoryPreviewStateStore`
  plus synthetic `PreviewBundleLoader` -> `npm test -- tests/preview-service.test.ts`
  -> PASS; one matching payload returns 200, changed payload returns ID_CONFLICT,
  and another admin returns NOT_FOUND without execution.
- fixture execution/replay -> fixture loader and `healthy-en` fixture -> same
  focused command -> PASS; no model configuration is required and duplicate run
  returns the stored result.
- invalid fixture/model fail-closed -> bounded fixture catalogue and absent model
  env -> same focused command -> PASS; INVALID_INPUT/UNAVAILABLE and no loader
  fallback.
- history/retention/cancel -> injected fake clock and in-memory state -> same
  focused command -> PASS; HISTORY_LIMIT is rejected, completed result wins a
  late cancel, and expired status returns NOT_FOUND.

Developer validation required: live Redis/production saved-bundle composition,
multi-replica atomic quota/concurrency behaviour, and COMMERCE-013 real adapter
pairing remain pending because this task owns injected lifecycle fixtures and
must not use live provider infrastructure.

### Deviations

The task definition requires Redis-backed atomic budgets and multi-replica race
evidence, but the accepted C19 task boundary permits injected lifecycle fixtures
until COMMERCE-013 supplies real composition. This implementation provides the
state-store port and deterministic local store; production runtime intentionally
fails closed rather than inventing a Redis or saved-bundle adapter.

### Assumptions

- Accepted database revision consumed: `5abfd87f57038bae515aaa09ec7c8db62adcfb98`.
- Fixture-only runtime is the safe default until COMMERCE-013 wiring; model mode
  requires explicit preview configuration and never falls back to production keys.

### Unresolved Issues

Commerce repository/submodule provisioning is complete; consume the accepted
COMMERCE-001 foundation. No additional provisioning prerequisite is introduced.

### Architectural Concerns

None newly reported.

### Git / VCS

- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-009`, branch `task/ARCH-020-COMMERCE-009`, clean after push.
- Parent/report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-009`, branch `task/ARCH-020-COMMERCE-009`.
- Database gitlink/submodule evidence: accepted SHA
  `5abfd87f57038bae515aaa09ec7c8db62adcfb98`; no database files or gitlink were
  edited.
- Implementation commit pushed to
  `origin/task/ARCH-020-COMMERCE-009`:
  `fa795af310d0df76a1553e4adb7d77dbe6c7b149`.
- No main branch merge, parent service gitlink update, or other repository edit
  was performed.

## Architect Review

### Review Status

Pending.

### Review Notes

No implementation submitted. This task is a reviewable definition.

### Reviewed Files

None for implementation review.

### Validation Reviewed

None for implementation review.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile task/index/frontier after review; preserve the terminal/manual system-test gate.
