---
id: ARCH-045-BACKGROUND-003
architecture_id: ARCH-045
title: Synchronise Shopify consent webhook into CustomerPhone
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 40
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-045-DATABASE-002
  - ARCH-045-BACKGROUND-001
  - ARCH-045-SHARED-002
  - ARCH-045-SHOPIFY-001
enables:
  - ARCH-045-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-23
---
# Synchronise Shopify consent webhook into CustomerPhone

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** architect-promoted to `ready` on 2026-10-23 after all four declared dependencies became complete, including architect-accepted `ARCH-045-SHOPIFY-001`. The task was claimed as Attempt 1 by the canonical launcher on 2026-10-23 and explicitly taken over for developer execution. The assigned agent remains `moda_background`; execution and completion are now developer-controlled.

### 2026-10-23 Dependency Frontier Update

Promoted `pending -> ready` because `ARCH-045-DATABASE-002`, `ARCH-045-BACKGROUND-001`, `ARCH-045-SHARED-002`, and architect-accepted `ARCH-045-SHOPIFY-001` are all `complete`. The accepted SHOPIFY-001 parent task branch was incorporated into this parent task branch so the dependency decision is available without merging either task branch to `main`. This is eligibility only; no claim or implementation work has begun.

## Objective

Consume the published Shopify WhatsApp consent-change signal and **only synchronise current `commerce.CustomerPhone`** from Shopify's present authority; never trigger checkout reconciliation or recovery.

## Context

`SHOPIFY-001` emits a minimal validated consent-sync event. `BACKGROUND-001` owns the current Shopify GraphQL reader and safe monotonic CustomerPhone update. This task only routes events through the existing Background queue/worker infrastructure.

## Scope

- Add a distinct validated `ShopifyWhatsAppConsentSyncJobV1Schema` dispatch branch to the existing worker/queue, separate from checkout-v2 parsing, using the published Shared package. No new BullMQ queue or event format.
- Resolve `shopId` and Shopify customer ID from trusted event identity through Shared numeric/GID conversion; invoke BACKGROUND-001 to read current Shopify phone/consent and update the existing CustomerPhone. Do not treat the webhook payload itself as an opt-in.
- If the shop-linked Customer is unavailable or ambiguous, record bounded non-PII diagnostics and do not invent a new Customer from a phone. Existing customer/phone lifecycle constraints remain in force; privacy erasure implementation is **not** added by this consent task.
- Handle replay, ordering, outdated provider observations, schema mismatch and provider failure using existing bounded job retry/failure handling. Always project Shopify's **current observed native consent decision** onto the correct CustomerPhone when observation ordering permits; never clear or modify independent local STOP or merchant restriction for **any** Shopify response, even `SUBSCRIBED` with a `updatedAt` later than STOP. A separate explicit customer-requested Moda clearance process would be required and is outside this task.
- Explicitly prohibit checkout lookup, pending-candidate scheduling, `RecoveryInitiationService`, merchant Support notices, credit or provider-send effects in this event consumer.

## Out of Scope

- No consent-driven checkout scan/sweeper, candidate retention, direct recovery resumption, additional evidence polling, 72-hour timeout, customer-erasure work or new durable consent table.

## Requirements

- [x] All valid consent-change signals cause a **fresh provider-state check**, not acceptance of a stale event's asserted grant.
- [x] This handler may update current CustomerPhone and bounded diagnostics only; it cannot create, reschedule or send a recovery.
- [x] A delayed/missed webhook does not define consent chronology: on an eventual sync signal, read Shopify's live `state`/`updatedAt`. Do not use the webhook as proof of opt-in or trigger a recovery.
- [x] Wrong-shop, absent-customer and reordered events remain tenant-safe and fail closed without inventing a customer or opt-in; a delayed or fresh native grant never changes `whatsappNoContact`.

## Work Items

- [x] Wire published Shared sync-job validation and distinct dispatch into the existing Shopify Background worker.
- [x] Invoke the BACKGROUND-001 injected native synchroniser and record bounded success/no-op/failure outcomes.
- [x] Test duplicate/reordered events, numeric/GID identity, provider outage and assertion of **zero** recovery/candidate/notice/billing effects.

## Interfaces / Contracts

**Producer:** ARCH-045-SHOPIFY-001. **Contract:** published ARCH-045-SHARED-001/002 consent-sync event. **Consumer:** this handler invokes ARCH-045-BACKGROUND-001 and writes existing ARCH-045-DATABASE-002 CustomerPhone fields only. No consent-wakeup or Woo contract.

## Dependencies

- `ARCH-045-DATABASE-002`
- `ARCH-045-BACKGROUND-001`
- `ARCH-045-SHARED-002`
- `ARCH-045-SHOPIFY-001`

## Enables

- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] A real native grant/revoke change eventually updates only the correct native consent state on CustomerPhone; a `SUBSCRIBED` observation may set `GRANTED` but never clears or regresses local STOP or its revision, regardless of provider `updatedAt`.
- [x] A consent-sync job alone produces **zero** checkout candidates, CheckoutRecovery rows, merchant notices, WhatsApp sends, usage charges or new recovery queue activity.
- [x] Unresolvable customer/shop, GraphQL errors and unexpected schema versions are handled deterministically using existing bounded failure mechanisms.

**Evidence scope:** The checked criteria indicate completed implementation and deterministic
unit/worker tests. A real signed Shopify webhook, a live read-only GraphQL call and
an actual provider-backed `CustomerPhone` projection are **not** claimed here;
they remain terminal integration checks owned by `ARCH-045-SYSTEM-TEST-001`.

## Validation

- [x] Typed worker dispatch tests, native provider refresh and monotonic CustomerPhone update tests, duplicate/reordered job, wrong-tenant, missing customer, provider unavailable and no-side-effect assertions.
- [x] Repository-declared checks and `git diff --check`.

## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. For publication task, do not rerun implementation validation.

## Implementation Notes

Do not treat `ShopifyWhatsAppConsentSyncJobV1` as proof of subscription. Verify provider state and the exact shop-owned customer/phone; update only the current CustomerPhone projection. Never query a checkout or call recovery materialisation in the sync handler. Keep typed event dispatch and consent projection modular instead of introducing a monolithic file.

Before claiming, use the deterministic `/moda-task` launcher and its **actual** prepared packet, read the task's complete current Architect Review, and verify task/dependency status in the developer's canonical workspace. Preserve `docs/decisions/**/_index.md` untouched until the developer explicitly closes the architecture documentation session. New runtime structured logging uses `@modainteract/moda-interact-shared/logging` where applicable. No source outside this task's owner repository may be changed unless explicitly authorised by the architecture.

## Completion Report

### Status

Ready for architectural review — **developer-owned Attempt 1**. The implementation
is committed and pushed as `4dcb00193c379901c9652db8b105447f7ba8eaa0`
(`feat(background)`) on `moda-interact-background` branch
`task/ARCH-045-BACKGROUND-003`. The final developer command showed this branch
up to date with `origin/task/ARCH-045-BACKGROUND-003` and a clean worktree.
The claim timestamp was `2026-10-23T12:31:29Z` (see **Developer Takeover**).
This is a **submission**, not an Accepted architect review or an explicit developer
completion decision. `completion_mode: developer` remains in effect.

### Files Changed

Implementation repository (`moda-interact-background`), commit `4dcb001`:

- `src/events/checkout-worker-dispatch.ts` — new named-job dispatch boundary.
- `src/services/shopify-whatsapp-consent-sync-job.service.ts` — new validated
  consent-sync job consumer and bounded outcomes.
- `src/workers/checkout.worker.ts` — existing BullMQ worker integration.
- `tests/unit/events/checkout-worker-dispatch.test.ts` — new routing tests.
- `tests/unit/services/shopify-whatsapp-consent-sync-job.service.test.ts` — new
  payload, identity, retry, replay and safety tests.
- `tests/unit/services/shopify-whatsapp-consent.service.test.ts` — extended
  CustomerPhone projection/STOP invariants.
- `tests/unit/workers/checkout.worker.test.ts` — new live worker-wiring tests.

No schema, Shared, Shopify producer, billing, checkout/recovery lifecycle, parent
architecture or domain `_index.md` changes are part of this implementation.

### Work Completed

- Routed the Shared `shopify-whatsapp-consent-sync` job by **name** before
  existing checkout event parsing in the `checkout-events` worker. Existing
  checkout-created, checkout-updated and cart-activity jobs retain their handlers.
- Validated the published Shared v1 payload and canonical Shopify customer ID;
  invoked `BACKGROUND-001`'s `syncCustomer()` to read **current** provider state.
  Webhook content is never treated as an opt-in grant.
- Applied bounded non-PII outcome logging, safe skip for wrong/inactive/ambiguous
  customer identity, stale-observation no-op, and retryable provider/read/write
  failure handling through the existing BullMQ retry policy. No new queue.
- Preserved local WhatsApp STOP and tenant fences; the consent-only path does not
  call recovery, candidate scheduling, notifications, provider sends or credits.
- Added focused unit/worker regression coverage. The incremental one-line
  TypeScript discriminant correction from the patch labelled **Attempt 2** was
  included before commit; it is a correction within **task Attempt 1**, not a
  separately claimed architecture-task attempt.

### Validation Results

- `npm run prisma:generate` — passed; generated Prisma Client v6.19.3.
- Focused `npx vitest run` for six suites — **64/64 passed** (first local run):
  checkout-worker dispatch (5), sync-job service (21), checkout-worker wiring
  (4), consent projection (18), Shopify contract adapter (10), BullMQ telemetry
  (6).
- First `npm run build` — one TS2339 discriminant-narrowing error. Corrected by
  the subsequent one-line incremental patch.
- Final `npm run build` (includes `prisma:generate` and `tsc`) — passed after
  that correction. Final `npm run lint` (`eslint .`) — passed.
- `git apply --check --whitespace=error-all` and `git diff --check` — passed
  during patch application; final implementation Git status clean after push.
- Focused Vitest suites were **not shown rerun after** the one-line TypeScript
  correction; the passing 64/64 result precedes it. No live Shopify/provider
  system test is claimed by this task.
- Commit/push: `4dcb00193c379901c9652db8b105447f7ba8eaa0`; origin branch
  `task/ARCH-045-BACKGROUND-003` (developer-supplied Git output, also visible
  in the implementation repository).

### Physical Worktree and Start-of-Attempt Evidence

- Canonical implementation worktree recorded at takeover:
  `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-045-BACKGROUND-003`;
  branch `task/ARCH-045-BACKGROUND-003`.
- Parent claim commit: `94934ad88a3ecfe929c047bd312a7c3b02d5da4a`;
  launcher-recorded claim timestamp: `2026-10-23T12:31:29Z`.
- Recursive implementation submodules were prepared at takeover; `database`
  recorded at `2e009298612133aace095db5d57245a5b01e773a`.
- The takeover text states the canonical worktree was synchronized, but the
  evidence supplied for this submission **does not enumerate** the parent and
  implementation `origin/task` fast-forward and `origin/main` incorporation
  outcomes (`yes` / `not-needed` / `already-current`). The canonical primary
  workspace root and parent worktree absolute path are not independently
  available in the supplied terminal record. Architect/developer reviewer should
  verify the prepared launcher packet/claim evidence; neither shared-checkout
  isolation nor the four synchronization statuses is certified here by inference.

### Deviations

None reported in runtime scope. A one-line typing correction was required and
incorporated in the implementation commit. The detailed start-of-attempt packet
remains a **workflow-evidence review item**, not proof of a code defect.

### Assumptions

`ARCH-045-BACKGROUND-001` remains the authoritative synchronizer; the published
Shared event is the only producer/consumer contract. Live provider ingress and
cross-service proofs are reserved for `ARCH-045-SYSTEM-TEST-001`; its manual gate
and downstream task states remain unchanged.

### Unresolved Issues

- Architectural reviewer must obtain/confirm the launcher-resolved parent/primary
  worktree paths, physical isolation and per-repository synchronization results.
- Reviewer should decide whether to require a final 64-test rerun following the
  one-line TypeScript correction; focused tests did not visibly rerun thereafter.
- Non-production signed-webhook/GraphQL proof is a terminal system-test gate,
  not demonstrated by this local implementation evidence.

### Architectural Concerns

No new cross-repository contract, database or billing mechanism was introduced.
The consumer depends on published Shared v2.5.0 and existing `BACKGROUND-001`.
The architect must verify implementation compatibility and lifecycle evidence
before an Accepted review; no dependent task is unblocked by this submission.

## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

None.

### Reviewed Files

None — portable definition only.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.

## Developer Takeover

On 2026-10-23, `/moda_developer_create ARCH-045-BACKGROUND-003` was invoked while this task was ready and agent-owned. The canonical launcher claimed Attempt 1 at `2026-10-23T12:31:29Z`, committed the parent claim as `94934ad88a3ecfe929c047bd312a7c3b02d5da4a`, and created the implementation worktree at `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-045-BACKGROUND-003` on `task/ARCH-045-BACKGROUND-003`. Recursive submodule synchronization passed; the `database` submodule is initialized at `2e009298612133aace095db5d57245a5b01e773a`.

This is an explicit developer takeover. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_background`, repository ownership, dependencies, scope and acceptance criteria are unchanged.

## Developer Self-Review - Accepted - Attempt 1 (2026-10-23)

The implementation satisfies the defined Work Items and Acceptance Criteria: the published consent-sync job is validated and routed separately from checkout events, refreshes current Shopify provider state through `BACKGROUND-001`, preserves CustomerPhone STOP state, handles tenant/identity and provider failures through existing bounded worker behavior, and has no recovery, candidate, notice, billing, or provider-send side effects. The implementation branch is clean and published at `4dcb00193c379901c9652db8b105447f7ba8eaa0`; the parent task branch is also published and clean. Live signed-webhook, provider GraphQL, and durable cross-service projection evidence remains explicitly assigned to `ARCH-045-SYSTEM-TEST-001`.

Focused validation was rerun after the final TypeScript correction: **48/48 tests passed** across the dispatch, sync-job, worker-wiring, and consent-projection suites; `npm run build` passed; `npm run lint` passed; and `git diff --check origin/main...HEAD` passed. The earlier six-suite 64/64 result preceded the correction, so this rerun closes that evidence gap for the affected suites.

This is a passing review submission, not a completion decision. Because `completion_mode: developer`, the task remains `status: review` with `executor: null`, `claimed_at: null`, and Attempt 1 preserved. Explicit completion requires `/moda_developer_update ARCH-045-BACKGROUND-003 complete`.

## Developer Completion Decision - Attempt 1 (2026-10-23)

The developer explicitly completed this task after the accepted Attempt 1 review. The implementation branch is committed and published at `4dcb00193c379901c9652db8b105447f7ba8eaa0`; the parent task record is committed and published on `task/ARCH-045-BACKGROUND-003`. No task branch was merged to `main`, and no implementation or parent worktree is required to be reopened.

Dependency-frontier reconciliation confirms all declared dependencies remain `complete`. `ARCH-045-SYSTEM-TEST-001` remains `pending` and is not started automatically; live signed webhook, provider GraphQL, and durable cross-service projection validation remain its responsibility.
