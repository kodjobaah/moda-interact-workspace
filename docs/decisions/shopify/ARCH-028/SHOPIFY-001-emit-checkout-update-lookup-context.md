---
id: ARCH-028-SHOPIFY-001
architecture_id: ARCH-028
title: Emit compatible checkout.updated lookup context from Shopify
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 55
executor: developer
claimed_at: 2026-10-22T13:12:29Z
attempt: 1
depends_on:
  - ARCH-028-SHARED-004
  - ARCH-028-BACKGROUND-012
enables:
  - ARCH-028-SYSTEM-TEST-001
created: 2026-10-08
updated: 2026-10-22
---
# Emit compatible checkout.updated lookup context from Shopify

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

### Developer Takeover

The developer explicitly invoked `/moda_developer_create ARCH-028-SHOPIFY-001`, taking over execution and completion authority from the prior `execution_mode: agent`, `completion_mode: automatic` definition. Execution/completion modes are now `developer`/`developer`; logical ownership remains `assigned_agent: moda_app`, and task scope, dependencies, acceptance criteria and validation requirements are unchanged. The canonical launcher will prepare the implementation task worktree and claim Attempt 1 after this amendment is published.

### Developer Takeover

The developer explicitly invoked `/moda_developer_create ARCH-028-SHOPIFY-001`, taking over execution and completion authority from the prior `execution_mode: agent`, `completion_mode: automatic` definition. Execution/completion modes are now `developer`/`developer`; logical ownership remains `assigned_agent: moda_app`, and task scope, dependencies, acceptance criteria and validation requirements are unchanged. The canonical launcher will prepare the implementation task worktree and claim Attempt 1 after this amendment is published.

## Objective

Produce validated versioned checkout.updated events containing the canonical checkoutToken and only optional, trustworthy Shopify lookup context, after the Background consumer can accept the new version.

## Context

The current Shopify `normalizeCheckoutUpdatedPayload` returns only `{checkoutToken}` even if the verified Shopify webhook contains `cart_token`, `created_at` or `abandoned_checkout_url`. The current strict v2 event must remain unchanged for queued/older consumers. SHOPIFY-001 is a producer-only implementation after SHARED-004 and consumer-first BACKGROUND-012 acceptance.

## Scope

- Use the exact published Shared Shopify event contract from SHARED-004 and emit v3 only for `checkout.updated`; retain v2 for all other existing Shopify recovery-event variants.
- Preserve checkoutToken from the verified Shopify webhook as the sole checkout identity alongside tenant Shop ID; normalize only actually present optional `cart_token`, `created_at`, `abandoned_checkout_url` using existing validators/bounds.
- Keep webhook authentication, receipt/delivery IDs, tenant-scoped ordering key, queue acceptance/acknowledgement latency and deterministic deduplication unchanged.
- If context is absent in a legitimate update, emit a valid token-only v3 event and do not invent a URL/date or drop an authenticated business event solely on that basis.
- Use fixtures proving normalisation and at-least-once delivery, including missing and malformed optional context handling consistent with the published schema.

## Out of Scope

- Changing Background candidate scheduling or abandoned checkout lookup (BACKGROUND-012).
- Changing Shared event schemas or publishing Shared package.
- Using abandonedCheckoutUrl for deduplication, identity or primary ordering.
- New synchronous Shopify Admin API calls within webhook ingress.

## Requirements

- [x] Shopify events remain keyed by `(shopId, checkoutToken)` and keep deterministic ordering keys.
- [x] Producer begins emitting v3 only after consumer-first BACKGROUND-012 is Complete/architect-accepted.
- [x] Optional lookup hints are validated and never fabricated.
- [x] Other webhook topics and existing v2 contracts remain unchanged.
- [x] Authenticated webhook durable-acceptance and fast-acknowledgement semantics do not regress.

## Work Items

- [x] Verify the Shopify dependency already pins the exact published Shared revision (`@modainteract/moda-interact-shared@2.4.3`); no dependency change required.
- [x] Extend checkout-update normalizer and event builder for versioned optional lookup hints.
- [x] Add regression tests covering absent/bad context, checkout identity, ordering and existing v2 events.
- [x] Run task-relevant Shopify tests/typecheck/build.

## Interfaces / Contracts

Producer `moda-interact`; consumer `moda-interact-background`; owner `moda-interact-shared`; runtime validator from exact SHARED-004 `@modainteract/moda-interact-shared/shopify` publication. v3 checkout.updated preserves required `checkoutToken` and adds optional nullable `cartToken`, `checkoutCreatedAt`, `abandonedCheckoutUrl` as Shopify lookup hints.

## Dependencies

- `ARCH-028-SHARED-004`
- `ARCH-028-BACKGROUND-012`

## Enables

- `ARCH-028-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Valid SHOP-scoped checkout.updated v3 always carries non-empty checkoutToken; URL is never used as identity.
- [x] v2 producer paths for other Shopify topics continue to pass.
- [x] Missing context does not cause fabricated values, webhook rejection or premature business filtering.
- [x] Exact Shared publication revision is installed and upgraded Background consumer is accepted.
- [x] Focused ingress contract/authentication/queue regression tests pass.

## Validation

- [x] Focused checkout normalization + ingress + queue tests: 3 suites, 57/57 tests passed (developer-provided terminal log, 2026-10-22).
- [x] `npm run prisma:generate`: Prisma Client v6.19.3 successfully generated (developer-provided terminal log, 2026-10-22).
- [x] `npm run typecheck`: passed following Prisma generation (developer-provided terminal log, 2026-10-22).
- [x] `npm run build`: Shopify client and SSR builds passed; non-fatal chunk-size warning (developer-provided terminal log, 2026-10-22).
- [x] `git diff --check` of the Attempt 1 implementation patch in an isolated snapshot passed; live dedicated-worktree Git evidence remains to be verified by architect review.

## Stop Condition

Complete defined work/acceptance/validation, fill the Completion Report, set status `review`, return to `moda_architect`, and STOP. Do not begin a dependent task.

## Implementation Notes

Preserve the existing minimal ingress boundary: receive/authenticate/normalize/durably enqueue/acknowledge. The URL, when present, is a retrieval hint and customer recovery link, not a business identifier. Do not synchronously query abandonedCheckouts in the webhook handler.

## Completion Report

### Status

Ready for Review — Attempt 1, claimed by developer at 2026-10-22T13:12:29Z. The implementation and task validation evidence have been supplied; branch publication and prepared-worktree evidence still require verification.

### Files Changed

Shopify implementation repository `moda-interact` (Attempt 1 implementation patch):

- `app/services/webhooks/checkout-normalization.ts`
- `app/services/webhooks/shopify-webhook-ingress.service.ts`
- `app/services/webhooks/shopify-webhook-queue.server.ts`
- `tests/unit/webhooks/shopify-normalization.test.js`
- `tests/unit/webhooks/shopify-webhook-ingress.service.test.js`
- `tests/unit/webhooks/shopify-webhook-queue.server.test.js`

Parent task definition (this submission):

- `docs/decisions/shopify/ARCH-028/SHOPIFY-001-emit-checkout-update-lookup-context.md`

### Work Completed

- Extended only `checkout.updated` to the published v3 Shopify recovery-event contract; other producer event variants continue to emit v2.
- Retained validated non-empty `checkoutToken` with Shop ID as the canonical checkout identity and preserved the existing ordering key, delivery-ID deduplication, and queue publication path.
- Added independently validated optional `cartToken`, `checkoutCreatedAt` and `abandonedCheckoutUrl` lookup hints from verified webhook fields. Absent/malformed hints do not fabricate values or prevent token-only updates.
- Added normalization, webhook ingress and queue tests for valid, absent, malformed and oversized optional context, version compatibility, ordering and duplicate delivery.
- Verified against the provided workspace snapshot that Shopify pins `@modainteract/moda-interact-shared@2.4.3`, and `ARCH-028-SHARED-004` and `ARCH-028-BACKGROUND-012` are marked Complete.

### Validation Results

- `typescript(20261022-132038)`: focused `npm test -- tests/unit/webhooks/shopify-normalization.test.js tests/unit/webhooks/shopify-webhook-ingress.service.test.js tests/unit/webhooks/shopify-webhook-queue.server.test.js` — **PASS**, 3/3 suites, 57/57 tests (21 normalization, 24 ingress, 12 queue).
- Same log: `npm run build` — **PASS**, client and SSR builds; Rollup reported a non-fatal chunk-size warning.
- An initial `npm run typecheck` failed with missing generated Prisma types (426 errors across 60 files, no reported errors in the six modified files) before regeneration.
- `typescript(20261022-132513)`: `npm run prisma:generate` — **PASS**, generated Prisma Client v6.19.3; `npm run typecheck` (`react-router typegen && tsc --noEmit`) — **PASS**.
- Portable Attempt 1 implementation patch was checked with `git apply --check --whitespace=error-all` and `git diff --check` against an isolated supplied-code snapshot. This does not establish the state of the developer's local implementation worktree.

### Deviations

- The initially failing typecheck passed after Prisma Client regeneration; no additional task-specific source correction was required.
- Attempt 1 was claimed by the developer as shown in the updated parent task snapshot; the original task metadata has been preserved (`execution_mode: developer`, `completion_mode: developer`, `executor: developer`, and `claimed_at`).
- Implementation was distributed through a portable patch. No verified implementation commit SHA, push confirmation, or launcher worktree/synchronization packet was supplied with the logs; these remain review-evidence gaps.

### Assumptions

- The published Shared `2.4.3` contract contains the expected v3 checkout-update validator, and the already-accepted Background consumer will be deployed before the v3 Shopify producer.
- The optional URL and timestamp remain lookup hints, never checkout identity or ordering keys.

### Unresolved Issues

- Confirm the pushed implementation commit SHA on `task/ARCH-028-SHOPIFY-001`, plus `git status` and `git diff --check` from the dedicated implementation worktree.
- Provide launcher-resolved parent/implementation worktree paths, Git branch state, start-of-attempt synchronization and recursive submodule preparation evidence required by `docs/agent-worktree-isolation-policy.md`.
- Commit and push this Completion Report on the parent `task/ARCH-028-SHOPIFY-001` branch; ensure no unmerged implementation submodule gitlink is staged.
- Developer completion authority remains `developer`: an architect Accepted review must not automatically mark the task `complete`. Explicit developer completion remains required.

### Architectural Concerns

No design change is proposed. The architect should verify implementation source and missing workflow evidence before acceptance. `ARCH-028-SYSTEM-TEST-001` remains gated until the task is both accepted and completed.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
