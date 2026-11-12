---
id: ARCH-070-BACKGROUND-001
architecture_id: ARCH-070
title: Verify refreshed recommendation product evidence
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 10
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-070-SHARED-002
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Verify refreshed recommendation product evidence

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; coordinator moda_architect.

## Objective

Verify refreshed recommendation product evidence without relaxing existing production security or lifecycle guarantees.

## Context

Recommendation candidates were refreshed but all three were rejected as PRODUCT_REFRESH_NOT_VERIFIED, ending MISSING_VERIFIED_PRODUCT_SELECTION / INVALID_FINAL. Establish the exact provider response evidence shape before fixing its consumption.

## Scope

src/commerce/host.ts recommendation refresh and product/domain evidence composition; directly related host tests.

## Out of Scope

Other task's owned modules, Shared/MCP implementation, schema changes, provider/model switching, credentials, infrastructure, old-message replay, unrelated refactors and unsolicited customer sends.

## Requirements

A legitimate refreshed product from the connected store is accepted and produces a verified recommendation; mismatched shop/domain/product/variant, missing or malformed evidence stays rejected. Preserve current price, stock and product identity validation. Do not weaken tenant/domain verification or invent a provider contract. If the valid fix requires MCP/Shared changes, stop and return that dependency to the architect.

## Work Items

- [x] Establish exact source/fixture cause and preserve a failing regression.
- [x] Implement only the owned correction.
- [x] Validate positive and failure/recovery behavior and report evidence.

## Interfaces / Contracts

Consume published Shared contracts and existing MCP product evidence / durable conversation lifecycle. No new wire or schema contract is authorized. Cross-repository gaps return to architect.

## Dependencies

ARCH-070-SHARED-002. Retry-policy task BACKGROUND-002 remains independently executable; recommendation adoption waits for the accepted published nullable PRODUCT_ONLY URL contract.

## Enables

Developer integration and production verification after architect acceptance of both tasks.

## Acceptance Criteria

- [x] Requirements demonstrated with deterministic positive and negative regression tests.
- [x] Existing tenant, domain, message identity and lifecycle guarantees preserved.
- [x] No duplicate delivery, live test send, secret logging or unrelated changes.
- [x] Completion Report records canonical launcher packet, physical isolation, synchronization and recursive submodule evidence.

## Validation

- [x] Regression reproducing legitimate provider-shaped refresh and negative cross-store/malformed/stale evidence; existing host/composition tests, typecheck, lint and required repository CI. No Meta send in tests.
- [x] Diff hygiene and exact changed-file scope review.

## Stop Condition

Complete owned work and required validation, set review, return report and STOP. Do not merge, deploy or begin another task.

## Implementation Notes

You are not alone in the codebase. Preserve others' changes. Use the prepared dedicated mirrored worktrees and task branch. Verify actual package scripts before running checks. Existing structured semantic logs suffice; do not introduce competing logging or repeated provider work as a diagnostic mechanism.

## Completion Report

### Status

Ready for Review. Implementation and final combined-head validation committed/pushed; awaiting moda_architect review.

### Files Changed

- `package.json`, `package-lock.json`: exact published Shared 5.13.3 and canonical registry integrity.
- `src/commerce/host.ts`: retain verified URL-less catalogue products only for PRODUCT_ONLY; scope-specific mutation guard and published discriminated rendering type.
- `tests/integration/commerce/host-suites/recommendations.ts`, `host.fixture.ts`: real MCP/host/Shared composition regressions, fresh provider evidence, scope/cache negatives.
- Three existing pinned-version consumer assertions: observability startup and recovery support/finalization notices.

### Work Completed

Read-only provider evidence showed all three rejected ACTIVE/available products had null onlineStoreUrl, including the working basket product. No provider writes or Meta sends occurred. The red regression against installed public Shared 5.13.3 reproduced PRODUCT_REFRESH_NOT_VERIFIED then INVALID_FINAL (7 passed, 1 failed). Host now accepts null links only for catalogue discovery, keeps all non-null domain checks and product/variant/availability/title validation, and rejects null-link basket actions even when the same product was already cached for PRODUCT_ONLY. No fabricated links or provider publication changes.

Architect review correction/dependency items implemented: consume exact published 5.13.3; preserve mutation URL requirements and all non-null URL/domain checks. Shared contract implementation remains owned by Shared; no cross-repository source edits.

### Validation Results

- Public npm install from fresh `/tmp/moda-arch070-bg001-public-cache`: 609 packages installed; actual canonical Shared 5.13.3 downloaded. Lock integrity `sha512-x2vu8tD4Vs9fzIGNLPc/4McxXsz96xiZjLUzaXUEvK2ShuU6RZcWP8N3nxmdc3rP3Qg/5PH+dyhp/9iw82WBWA==`.
- Full real host suite: 90 passed on final combined head, including missing product, malformed price, unsafe title/URL, cross-store URL, stale product/variant, unavailable, null-link ADD/REPLACE and cross-scope cache cases.
- Focused recommendation, installed model boundary and pinned-version consumers: 57 passed in 15 files serially. Parallel run hit existing subprocess 5-second contention timeouts; unchanged timeout policy, serial rerun passed.
- TypeScript `tsc6 --noEmit`: passed.
- Changed-file ESLint: passed. Full ESLint reports four existing unused declarations in untouched `candidate-index.store.ts` and `recovery-offer-resolver.service.ts`; identical main source, outside task scope, reported to coordinator.
- `git diff --check`: passed.
- No live PostgreSQL/Redis used. Host integration uses fixture database and local MCP/model servers; unit env explicitly points to loopback port 1.
- PR: https://github.com/kodjobaah/moda-interact-background/pull/202; initial implementation bfaf6f3. Final combined head 91f880e490aa80d4df49c1e697534ee3d0a457a5 includes footer04317ce74b79192d0ce909de5edc0d1265e47b5c and retry1afff14201c3f55a7f6745686e16abf3090499da. Both required full CI runs passed (368 unit files), including clean dependency installation, Prisma generation and typecheck: https://github.com/kodjobaah/moda-interact-background/actions/runs/43227000270 and https://github.com/kodjobaah/moda-interact-background/actions/runs/43226985311. Combined-head local90 host tests, typecheck and changed-file lint also passed.

### Physical Worktree and Launcher Evidence

Prepared packet `/tmp/moda-arch070-bg001-attempt2-prepare.json`, task ARCH-070-BACKGROUND-001, attempt 2, executor codex; claim 38352357268fd80d922f7c2b7627ba3f427f3502 committed/pushed by launcher. Canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-070-BACKGROUND-001`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-070-BACKGROUND-001`; both branches `task/ARCH-070-BACKGROUND-001`. Shared/default checkouts switched or mutated: no. Another task worktree reused: no.

Parent remote task fast-forward not needed; origin/main already current. Implementation remote task fast-forward not needed; origin/main incorporated by launcher at 1afff14201c3f55a7f6745686e16abf3090499da. Recursive submodule sync/update passed, database 5329d5390d346042895219663f3a040ea54ae168 initialized at recorded commit. No parent submodule gitlink staged.

### Deviations / Assumptions

No scope deviation. No database migration or queue contract changed. PostgreSQL is not part of the modified host evidence boundary; existing local MCP/model host integration exercises the actual published rendering contract.

### Unresolved Issues / Architectural Concerns

Production deployment and genuine customer-question verification remain with root after architect review. Final combined head includes independently owned retry and footer changes and passes both full CI runs. No merge or deployment performed by this agent.

## Architect Review

### Review Status

Accepted — Attempt 2.

### Review Notes

Reviewed actual final combined91f880e490aa80d4df49c1e697534ee3d0a457a5 and durable reportbf903d8c8. Exact public Shared5.13.3 is pinned with approved integrity. Verified trusted catalogue null URL is accepted only for PRODUCT_ONLY; ADD/REPLACE retain required URL even when refresh cache was populated by a catalogue selection. Product/variant identity, available/title/price and nonnull shop-domain/URL checks remain fail-closed. No fabricated link. Verified merged footer04317ce and retry1afff14 are ancestors. Canonical attempt2 isolation, dependency gating, synchronization and recursive database evidence reviewed.

### Reviewed Files

commerce/host.ts, recommendation host cases and fixture, package/lock, three exact pinned-version assertions. No unrelated runtime files changed.

### Validation Reviewed

Red regression; final combined host90 passes and57 focused/published-consumer passes, clean public-cache install of609 packages, typecheck, scoped lint and diff hygiene. Independently verified both final-head CI jobs success (2m28s/2m26s). Full lint's four unused declarations are unchanged at origin/main04317ce in candidate-index.store.ts and recovery-offer-resolver.service.ts; independently confirmed zero source diff, recorded as pre-existing diagnostic rather than invented baseline ID. No unrelated cleanup required. Serial subprocess rerun passed without changing timeout policy.

### Architecture Conformance

Conforms to accepted/published Shared contract and tenant-scoped evidence ownership. Production-compatible broadening only for linkless catalogue presentation, no mutation weakening, schema, infrastructure, credential or queue changes. Combined retry/footer behavior remains intact. Architecture remains In Progress pending deployment and genuine recommendation/footer evidence.

### Follow-up

Developer may merge PR202 exact91f880e and deploy. Verify a genuinely new production recommendation question, accepted product evidence, footer, Meta response and durable delivery without resetting/replaying old inbound. Then reconcile final parent gitlinks and architecture completion.
