---
id: ARCH-026-ADMIN-002
architecture_id: ARCH-026
title: Read merchant international context from shared Shop state
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 45
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-026-DATABASE-002
  - ARCH-026-SHOPIFY-002
  - ARCH-026-ADMIN-001
enables: []
created: 2026-10-02
updated: 2026-10-03
---

# Read merchant international context from shared Shop state

## Architecture

Architecture ID: `ARCH-026`

Architecture document: `docs/architecture/ARCH-026-woocommerce-application-foundation.md`

Coordinator: `moda_architect`

## Objective

Migrate Admin cross-merchant/support reads of merchant international context from `shopify.ShopSettings` to provider-neutral `commerce.Shop` state so Woo merchants do not require a fabricated Shopify settings row.

## Context

Current Admin support/translation logic reads `ShopSettings.defaultLanguageTag` for merchant-target language selection. DATABASE-002 establishes shared Shop language/time-zone/country context and SHOPIFY-002 ensures the current Shopify writer maintains it.

ADMIN-001 separately migrates the shared onboarding milestone and serializes ARCH-026 Admin changes.

## Scope

Modify only `moda-interact-admin` production/tests required to source international context from Shop.

Current inspected area includes `src/lib/admin/merchant-support.ts` and its focused security/tests.

Do not redesign support translation policy; replace the provider-specific persistence source only.

## Out of Scope

- Removing legacy ShopSettings fields.
- Woo merchant UI.
- Translation catalogue/provider redesign.
- Admin UI locale configuration.
- Billing/recovery logic.

## Requirements

### R1 — Shared Shop context is authoritative

Admin support/merchant international-context reads use shared Shop fields rather than requiring ShopSettings.

### R2 — Cross-platform tenants work without ShopSettings

A Woo Shop with no Shopify settings row can participate in the affected Admin support/read flows.

### R3 — Translation behavior is preserved

Existing target-language normalization/fallback behavior remains unchanged except for the source field.

## Work Items

- [x] Confirm nested database gitlink is at accepted DATABASE-002 and regenerate Prisma.
- [x] Change Admin support international-context query/projection to shared Shop fields.
- [x] Remove the affected runtime requirement for a ShopSettings join.
- [x] Update focused security/unit tests with Shopify and Woo-like Shop fixtures.
- [x] Audit changed Admin code for remaining ShopSettings international-context dependencies.

## Interfaces / Contracts

Database owner: `ARCH-026-DATABASE-002`.

## Dependencies

- `ARCH-026-DATABASE-002`
- `ARCH-026-SHOPIFY-002`
- `ARCH-026-ADMIN-001`

## Enables

None.

## Acceptance Criteria

- [x] Affected Admin support logic reads shared Shop international context.
- [x] Woo-like Shops require no ShopSettings row for the affected flow.
- [x] Existing language normalization/fallback behavior remains unchanged.
- [x] No legacy fields are removed.
- [x] No unrelated Admin/business behavior changes.

## Validation

- [x] Prisma generation from accepted DATABASE-002;
- [x] typecheck;
- [x] targeted lint;
- [x] focused merchant-support/security tests;
- [x] Woo-like no-ShopSettings fixture test;
- [x] production build;
- [x] static audit;
- [x] `git diff --check`;
- [x] clean task-worktree evidence after publication.

## Stop Condition

After required work and validation, set status to `review`, complete the Completion Report, return to `moda_architect`, and STOP.

## Implementation Notes

Keep this task a bounded persistence-source migration.

## Completion Report

### Status

Ready for Review

### Files Changed

- `src/lib/admin/merchant-support.ts`
- `tests/security/admin-merchant-support.test.mjs`

### Work Completed

- `composeAdministrativeMessage` now reads `commerce.Shop.defaultLanguageTag` by joining the support thread directly to `commerce.Shop`; the query retains `FOR UPDATE OF t` and no longer depends on a Shopify `ShopSettings` row.
- Existing target-language normalization and the `en-GB` fallback are unchanged. Focused tests cover English, a Woo-like French Shop with no settings row, and null-language fallback.
- The nested `database` submodule was already at accepted DATABASE-002 commit `16dba1a7c88f432f2f7d2cf718ae8297977cdcc3`; no submodule gitlink change was needed. Prisma Client was regenerated from that schema.
- Launcher evidence: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-026-ADMIN-002` on `task/ARCH-026-ADMIN-002`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-026-ADMIN-002` on `task/ARCH-026-ADMIN-002`. Both worktrees were created for this attempt; no shared/default checkout or other task worktree was reused or switched.
- Start synchronization: parent and implementation task branches were already current with their task refs; current `origin/main` was already incorporated in both. Recursive submodule sync and initialization passed; the database commit was `16dba1a7c88f432f2f7d2cf718ae8297977cdcc3`.

### Validation Results

- Passed: `npm run prisma:generate` against accepted DATABASE-002.
- Passed: `npx tsc --noEmit`.
- Passed: `npx eslint src/lib/admin/merchant-support.ts`; the `.mjs` test file is ignored by the repository ESLint configuration.
- Passed: all 13 task-relevant merchant-support behavior/security tests, including the new shared-Shop and null-fallback coverage; all 7 `admin-merchant-support-ui` security tests passed.
- Passed: `npm run build` and `git diff --check`. The build emitted BullMQ warnings for a dynamic dependency and optional `@valkey/valkey-glide`, but completed successfully.
- Passed: static audit found no `ShopSettings` reference in `src/lib/admin/merchant-support.ts`.
- `npm test` is not fully green because unrelated existing assertions fail: the merchant-support suite pins the shared package version to `1.0.1` while `package.json` declares `1.1.0`; the billing pack status suite expects a legacy `RECOVERY` status marker not present in its current source. These expectations are outside this task and were not changed.
- Passed: `git diff --check`; implementation and parent task worktrees were clean after their task commits and pushes.

### Deviations

- No schema gitlink update was required because launcher preparation had already materialized the accepted DATABASE-002 commit.
- The broad Admin suite retains unrelated baseline assertion failures listed above; task-relevant behavior and UI security tests pass.

### Assumptions

- SHOPIFY-002 is complete so current Shopify state is maintained on Shop.

### Unresolved Issues

- The unrelated `npm test` assertions should be reconciled by their owning Admin task; they do not exercise this persistence-source migration.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted — Attempt 1

### Review Notes

Accepted. Implementation `84a8329d16844f289a4cfce43724b3b2de3819e0` is a bounded persistence-source migration: `composeAdministrativeMessage` now reads `defaultLanguageTag` from the authoritative shared `commerce.Shop` row joined through the support thread's `shopId`, without requiring a Shopify `ShopSettings` row. The existing ownership recheck, `FOR UPDATE OF t` thread lock, target-language normalization, `en-GB` fallback, message/translation state transitions, thread-update semantics and post-commit best-effort queue dispatch are unchanged. The Woo-like no-ShopSettings and null-language fixtures cover the required cross-platform behavior.

The repository-wide `npm test` residuals do not block this task. Both are present in the exact pre-task base `3745d6ccebfe470c57ac00e33905a1a78c8f072e`: `tests/security/admin-merchant-support.test.mjs` still expects Shared `1.0.1` while `package.json` already declares `1.1.0`, and the billing-pack status assertion conflicts with the already-existing legacy hard-coded status list in `billing-recovery-packs.tsx`. ADMIN-002 changes neither area.

### Reviewed Files

- `src/lib/admin/merchant-support.ts`
- `tests/security/admin-merchant-support.test.mjs`
- `docs/decisions/admin/ARCH-026/ADMIN-002-read-shared-international-context.md`

### Validation Reviewed

- `npm run prisma:generate`: passed against accepted DATABASE-002 (`database@16dba1a7c88f432f2f7d2cf718ae8297977cdcc3`).
- `npx tsc --noEmit`: passed.
- Targeted source lint: passed.
- Task-relevant merchant-support behavior/security tests: 13/13 passed.
- Admin merchant-support UI security tests: 7/7 passed.
- Static audit: no `ShopSettings` reference remains in `src/lib/admin/merchant-support.ts`.
- `npm run build`: passed; reported BullMQ optional/dynamic dependency warnings are non-blocking.
- `git diff --check`: passed.
- Implementation/report task worktrees were reported clean and remote-aligned after publication.

### Architecture Conformance

Conformant. DATABASE-002 shared Shop international context is now the Admin support language source; Woo-like Shops no longer require a fabricated Shopify settings row; no legacy schema field is removed; and the established support translation/locking/queue contract is preserved.

### Follow-up

None for ADMIN-002. The materialised ARCH-026 Admin migration stream is complete. The inherited Shared-version and billing-pack test assertions remain with their owning Admin maintenance work and are not expanded into this task.
