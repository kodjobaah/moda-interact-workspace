---
id: ARCH-020-COMMERCE-006
architecture_id: ARCH-020
title: Read merchant discount policy and normalise Shopify rules
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 100
executor: copilot
claimed_at: 2026-09-21T00:50:49Z
attempt: 1
depends_on:
  - ARCH-020-COMMERCE-001
  - ARCH-020-DATABASE-001
  - ARCH-020-SHARED-001
  - ARCH-016-BACKGROUND-001
  - ARCH-016-DATABASE-001
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-013
  - ARCH-020-COMMERCE-016
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-21
---

# Read merchant discount policy and normalise Shopify rules

## Architecture

ARCH-020. [Parent architecture](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).
Binding [implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md):
C4/C5/C7/C8/C9/C14/C16/C18 as applicable, and exact ownership/interfaces in **C19**.

## Objective

Own current discount-policy resolution, permission-aware offer listing and provider rule normalization. Do not calculate qualification or savings.

## Context

This is the canonical narrowed definition from the 2026-09-21 task split, replacing
the former combined scope. No prior attempt or implementation is discarded. Normal
launcher/worktree/review policies apply. No task is claimed by this definition.

## Scope

Own current discount-policy resolution, permission-aware offer listing and provider rule normalization. Do not calculate qualification or savings.

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

- [x] Reuse the accepted policy shape through an injected policy port: NONE/FIXED/AI_BEST_APPLICABLE, with fixed-offer authorization and stale-catalogue/scope fail-closed checks. No catalogue or synchronizer was added.
- [x] Implemented `getDiscountOptions` and `DiscountRuleReader` under C19. Shop ownership, policy mode and fixed-offer identity are checked before provider requests; denied cases produce zero provider calls.
- [x] Inspected the pinned 2026-07 Admin GraphQL surface and documented the static query-to-normalized-field mapping in `docs/discount-support-matrix.md`. Missing `read_discounts` scope returns `UNAVAILABLE`; no OAuth expansion or privileged fallback exists.
- [x] Normalized native basic percentage/fixed values, all/product/variant/collection targets, minimums, dates and semantics. Incomplete, customer/usage, combination and unsupported families remain explicit `UNKNOWN`/`UNSUPPORTED` conditions.
- [x] Shared the injected request budget across bounded pagination (20 per page, 3 pages, 50 offers); no eligibility calculation, Evidence generation or recommendation ranking was added.

## Interfaces / Contracts

Own `src/commerce/discounts/reader/`. C19 DiscountRuleSnapshot is the sole input contract for016.016 owns calculation;013 connects discounts.getOptions to014. Provider schema evidence is an implementation deliverable, not permission to invent Shopify semantics.


## Dependencies

- ARCH-020-COMMERCE-001
- ARCH-020-DATABASE-001
- ARCH-020-SHARED-001
- ARCH-016-BACKGROUND-001
- ARCH-016-DATABASE-001

All listed prerequisites must be Complete and architect-accepted before a claim.
Use dedicated launcher worktrees and accepted source; do not launch enabled work.

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-013
- ARCH-020-COMMERCE-016
- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] D01: NONE lists none; FIXED permits only its offer; AI listing is bounded and discloses truncation; wrong tenant/offer yields zero provider calls.
- [ ] D02: provider fixtures map percentage/fixed/all/product/variant/collection/minimum/date fields to the exact C19 DTO; incomplete fields never become defaults claiming support.
- [ ] D03: unsupported app/Function/BXGY/shipping/combination restrictions remain UNSUPPORTED; unverified customer/usage facts remain UNKNOWN.
- [ ] D04: missing scopes, provider outage, stale catalogue and pagination/retry ceilings return bounded errors; semantic fingerprint excludes observation timestamps.
- [ ] D05: every supported normalization profile has cited pinned provider-schema evidence; unproven allocation/rounding becomes UNSUPPORTED, not a guessed formula.

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

Ready for Review. Attempt 1 implementation and agent-owned validation are complete.

### Files Changed

- `src/commerce/discounts/reader/types.ts`: C19 local ports, policy/result types, normalized snapshot and injected provider contracts.
- `src/commerce/discounts/reader/reader.ts`: bounded policy-aware option listing, fixed-offer reader, normalization and semantic fingerprinting.
- `src/commerce/discounts/reader/index.ts`: reader exports.
- `tests/discount-reader.test.ts`: deterministic policy, authorization, normalization, bounds and fail-closed fixtures.
- `docs/discount-support-matrix.md`: pinned 2026-07 Admin schema evidence and static query-to-DTO mapping.

### Work Completed

- Added injected `DiscountPolicyPort` and `DiscountProvider` boundaries; production construction with no approved provider fails `UNAVAILABLE` rather than using fixtures or live fallback.
- Implemented `NONE` empty listing, `FIXED` configured-offer-only access and bounded `AI_BEST_APPLICABLE` listing with truncation disclosure.
- Enforced shop/policy/offer authorization before provider I/O and shared the request budget across pages.
- Normalized native basic percentage/fixed rules with explicit targets, minimums, dates, support states, unresolved/unsupported conditions and timestamp-independent SHA-256 semantic fingerprints.
- Preserved the boundary to COMMERCE-016: this task does not calculate eligibility, savings or Evidence.

### Validation Results

Agent-executed validation:

- `npm run prisma:generate`: passed; canonical nested Prisma client generated at pinned `6.19.3`.
- `npm exec vitest run tests/discount-reader.test.ts tests/auth-permissions.test.ts`: passed, 2 files / 13 tests.
- `npm test`: passed, 14 files / 80 tests.
- `npm run lint`: passed.
- `npm run typecheck`: passed; Next route types and `tsc --noEmit` completed successfully.
- `npm run build`: passed; Prisma generation, webpack compilation, TypeScript, page data and static generation completed.
- `git diff --check`: passed.

Requirement-to-fixture matrix:

| Requirement | Fixture/test | Expected side effects | Result |
| --- | --- | --- | --- |
| D01 NONE/FIXED | `returns no options...`; `permits only the configured FIXED offer...` | NONE makes zero provider requests; wrong fixed offer is `DENIED` before I/O | Passed |
| D01 AI bound | `bounds AI listing at 50 offers...` | maximum 50 normalized offers and `truncated: true` | Passed |
| D02 supported mapping | `normalizes percentage, all-target...` | percentage, target, minimum, dates and proven semantics map to C19 DTO | Passed |
| D02 incomplete fields | `preserves incomplete targets...`; malformed native value fixture | no default target/value; explicit null and `UNKNOWN`/`UNSUPPORTED` condition | Passed |
| D03 unsupported/unknown | `keeps unsupported discount families explicit`; incomplete target fixture | app/Function family and unknown target semantics remain explicit | Passed |
| D04 scope/outage | `returns UNAVAILABLE for missing scope...`; `fails closed when provider adapter is unavailable` | zero provider requests for missing scope; bounded retryable unavailable result | Passed |
| D04 stale catalogue | policy fixture uses `catalogueFresh: false` through the same guard | `UNAVAILABLE` before provider I/O | Covered by guard; no live provider claim |
| D04 fingerprint | `does not include observation timestamps...` | same semantic fingerprint for different observation timestamps | Passed |
| D05 pinned semantics | support matrix plus proven-semantics fixture | unsupported/unproven allocation and rounding cannot become supported | Passed |
| Tenant/auth isolation | `rejects a wrong tenant...` plus wrong-offer fixture | `DENIED` and zero provider calls | Passed |

Tests use injected deterministic policy/provider fixtures only. They do not claim
live Shopify/provider behavior.

### Deviations

The accepted Shared package is not present as an installed source export in this
fresh Commerce checkout, so the C19 reader port is declared structurally local as
specified by C19; no new wire version or competing shared package was created.
The production assembly owner (COMMERCE-013) and live provider adapter remain
outside this task.

### Assumptions

Use the parent architecture and actual accepted dependency revisions. Return contradictory source facts to moda_architect.

### Unresolved Issues

Developer-owned validation remains: pair the reader with the accepted production
Shopify adapter/installation-token lookup and run the approved live/pre-production
Shopify Admin API check against a test shop using the pinned 2026-07 schema and
actual granted scopes. No live credentials were inspected or used here.

### Architectural Concerns

None newly reported.

### Git / VCS

Expected mirrored branch: `task/ARCH-020-COMMERCE-006`. Implementation worktree:
`/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-006`.
Parent task worktree:
`/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-006`.
Both were prepared by the launcher and remained isolated from `main`.
Implementation commit: `4b968c1` (`feat(commerce): add bounded discount rule
reader`), pushed explicitly as `HEAD:refs/heads/task/ARCH-020-COMMERCE-006` to
the Commerce remote after the Git helper reported the prepared local upstream
was `origin/main`. Parent report commit: `536484d0`, pushed to
`origin/task/ARCH-020-COMMERCE-006`. No parent service gitlink,
architecture/index file, or `main` branch was updated.

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
