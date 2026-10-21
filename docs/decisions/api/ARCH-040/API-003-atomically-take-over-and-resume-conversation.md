---
id: ARCH-040-API-003
architecture_id: ARCH-040
title: Implement WooCommerce Take Over and Resume AI endpoint
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 40
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-040-DATABASE-001
enables:
  - ARCH-040-API-004
  - ARCH-040-WOOCOMMERCE-001
created: 2026-10-14
updated: 2026-10-19
---

# ARCH-040-API-003 — Implement WooCommerce Take Over and Resume AI endpoint

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. The task definition is materialized on the canonical parent task branch.

## Developer Ownership Amendment

On 2026-10-19, `/moda_developer_create ARCH-040-API-003` was invoked to take over this ready task. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_api`, repository ownership, scope, dependencies, requirements, and acceptance criteria are unchanged. The canonical developer launcher records the execution attempt separately.

## Objective

Expose an authenticated **WooCommerce-only** control command that atomically takes over or resumes the *existing* customer conversation via compare-and-set and immutable transition history.

## Context

`DATABASE-001` adds `Conversation.controlMode`, `controlRevision`, and `ConversationControlEvent`. Woo installation authentication and shop ownership checks already exist in the API; Shopify implements its own session-authenticated Prisma transition, not an API call. The worker (`BACKGROUND-001`) separately fences in-flight AI replies.

## Scope

- Implement only the WooCommerce-hosted API boundary described here, using the existing authenticated installation and generated Prisma models.
- Follow the existing API HTTP route, validation, logging, error and OpenAPI patterns, and add focused tests.
- Keep API controller/validation, tenant-scoped service, persistence and API contract tests modular. Do not introduce a catch-all file.

## Out of Scope

- Shopify authentication, Shopify app routes or direct Shopify merchant calls to this hosted API.
- New Moda merchant accounts, per-staff permissions/assignments or staff attribution identifiers.
- A second conversation, another message table, a second follow-up allowance or a new recovery credit ledger.
- Provider WhatsApp delivery, background worker business logic, webhook processing or queue workers.
- WordPress admin/UI implementation, which belongs to `moda_woocommerce`.
- Recreating Shared conversation DTOs; Prisma is canonical for persisted data, while HTTP DTOs are local to API.
- No `docs/decisions/**/_index.md` changes before explicit user confirmation.

## Requirements

- An ARCH-040 control action requires `Conversation.checkoutRecoveryId IS NOT NULL` and ownership through `CheckoutRecovery.shopId`; deny standalone/product-support conversations even if `Conversation.shopId` matches. Preserve the existing Woo installation authentication and non-enumerating cross-shop 404.

### Exact endpoint

`POST /v1/merchant/conversations/{conversationId}/control`

```json
{ "targetMode": "HUMAN", "expectedControlRevision": 4 }
```

- `targetMode` is exactly `HUMAN` or `AI`; `expectedControlRevision` is a nonnegative integer. Strictly reject unknown/duplicated/invalid fields, oversized body, unsupported media type and malformed ID. No staff IDs, shopId, actorPlatform or actorSubject.
- Reuse `WooInstallationAuthenticator` and current connected installation verification; derive `shopId` only from trusted installation credentials. ARCH-040 is recovery-only: require `Conversation.checkoutRecoveryId` and resolve conversation ownership through **`CheckoutRecovery.shopId`**; do not fall back to nullable `Conversation.shopId`. Any shop conflict/inactive installation fails closed.
- Success `200` returns `{schemaVersion:1,conversationId,controlMode,controlRevision,controlChangedAt}`. A **same-mode request at the current expected revision** is a `200` no-op with unchanged revision and **no new event**. Any wrong/stale expected revision is `409 {error:"stale_control_revision"}` even if the requested mode now matches; include current mode/revision only after ownership is established.
- Missing or foreign conversation: `404 {error:"not_found"}`; unauthenticated installation: `401 {error:"unauthorized"}`; malformed: `400 {error:"invalid_request"}`; domain/integrity conflicts: explicit 409 code; unexpected failure: 500 without detail leaks.

### Atomicity and ordering

- Inside **one PostgreSQL transaction**, revalidate shop/install/conversation relationship, read current mode and revision, CAS update `(id, controlMode, controlRevision)` to target mode with `controlRevision+1`, update `controlChangedAt`, and insert exactly one `ConversationControlEvent` with matching revision/timestamp. Zero-row CAS is a 409; never silently overwrite or replay another writer's update.
- `AI -> HUMAN` must be allowed at any time for an authenticated merchant, independently of whether the customer-service window is open; takeover does **not** permit an otherwise forbidden send.
- `HUMAN -> AI` must not resurrect old agent work; `BACKGROUND-001` consumes the monotonic revision at its dispatch fence. An already irreversibly dispatched provider call is not recalled; do not claim otherwise.
- This HTTP command changes control only. It must not create a `Conversation`, enqueue a message, send WhatsApp, claim a recovery follow-up or debit a credit. No Redis/provider calls in the transaction.
- No extra per-employee roles/claims or separate merchant login: existing Woo installation credential is authoritative on hosted API; WordPress permission/nonce checks belong to consolidated `WOOCOMMERCE-001`.

### Human-messaging suspension behaviour

- A suspended shop cannot Take Over into `HUMAN`; return stable `403 human_messaging_suspended`. It may still explicitly Resume AI for a previously HUMAN-controlled conversation. Reading the same conversation remains allowed.
- Read the persisted DATABASE-001 restriction using the installation-authenticated shop and coordinate the takeover decision with restriction state changes; an optimistic browser badge does not authorize a transition.


### Platform-specific transport, shared durable authority

This hosted endpoint is **WooCommerce-only** because the existing Woo installation credential is the HTTP authentication boundary; it does not implement a Woo-only conversation policy. Resolve tenant via `CheckoutRecovery.shopId` and apply exactly the same transaction/CAS, shop-restriction and `ConversationControlEvent` semantics that SHOPIFY-001 applies under a Shopify session. Do not enqueue BullMQ or schedule a follow-up on control change; Background's shared revision and provider fence protect all existing recovery-linked sends. The response contains `controlChangedAt` only (no obsolete `humanTakenOverAt`). When a provider permit has already committed, a mode change does not claim that the Meta request can be recalled.


## Work Items

- [x] Implement the strict Woo-authenticated control POST route and local request/response schema.
- [x] Implement shop-scoped transaction that performs CAS, timestamp changes and `ConversationControlEvent` insertion atomically.
- [x] Implement current-revision same-mode no-op and stale-revision conflict semantics.
- [x] Register route/docs and add failure handling without provider, queue or credit side effects.
- [x] Cover concurrency, double clicks, AI→HUMAN→AI→HUMAN, shop isolation and revoked/rotated Woo installations.

## Interfaces / Contracts

`POST /v1/merchant/conversations/{conversationId}/control` is a Woo installation HTTP boundary. Persistence is canonical `Conversation`, `ConversationControlMode`, `ConversationControlEvent` generated by Prisma under `DATABASE-001`. `BACKGROUND-001` owns final outbound AI fencing; Shopify independently uses the same persisted CAS/event semantics in its authenticated server routes. No Shared schema or Shopify assertion.

## Dependencies

- ARCH-040-DATABASE-001

## Enables

- ARCH-040-API-004
- ARCH-040-WOOCOMMERCE-001

## Acceptance Criteria

- [x] Takeover success is returned only after the mode/revision and one matching transition event are committed.
- [x] Two simultaneous commands with the same expected revision produce one transition and one stale conflict; later no-op does not alter revision/history.
- [x] AI→HUMAN→AI→HUMAN produces revisions N+1, N+2, N+3, with monotonic immutable audit rows.
- [x] Foreign shop, malformed data, invalid installation and corrupted ownership never change a conversation.
- [x] Neither a takeover nor a resume creates a new message, outreach attempt, credit, or second `Conversation`.

## Validation

- [x] HTTP request/response, authorization, invalid input and status-code tests.
- [x] Disposable PostgreSQL transactional CAS/race tests, no-op and audit consistency tests with retries.
- [x] Cross-shop (including recovery conversation with null `Conversation.shopId`), rotated/revoked installation and read isolation regressions.
- [x] `git diff --check`, repository's applicable typecheck/build/lint, and isolated task-worktree evidence.

## Stop Condition

After only this task’s Work Items, Acceptance Criteria and Validation are complete, record implementation evidence and complete the developer-owned task. Do not begin dependent tasks.

## Implementation Notes

- Follow the canonical `scripts/start-agent-task.py --prepare` preparation packet and the parent/implementation worktree policy. Only claim the task in the real development workspace, not this portable definition.
- Do not assume a particular validation command: inspect `moda-interact-api/package.json` and the task's requirements. Use disposable PostgreSQL integration fixtures from this repository.
- Use `@modainteract/moda-interact-shared/logging` for structured logging; log bounded identifiers/outcomes rather than customer content, bearer tokens, WordPress credentials or private recipient numbers.
- Fresh development schema only. No historical-data migration/backfill/old-contract adapters are required for ARCH-040. Keep existing WooCommerce credential rotation/disconnection and API response header security protections.

## Completion Report

### Status

Complete — Attempt 1 accepted and explicitly completed by developer on 2026-10-19.

### Files Changed

- `src/merchant/conversations/control/contract.ts`
- `src/merchant/conversations/control/request.ts`
- `src/merchant/conversations/control/routes.ts`
- `src/merchant/conversations/control/service.ts`
- `src/composition/merchant.ts`
- `openapi/merchant-conversation-control-v1.yaml`
- focused unit, contract, route and disposable PostgreSQL tests
- `package.json` and the ARCH-040 PostgreSQL test runner

### Work Completed

- Added the authenticated WooCommerce-only `POST /v1/merchant/conversations/{conversationId}/control` boundary with strict request/response validation and bounded errors.
- Added transaction-scoped shop and installation revalidation, recovery ownership through `CheckoutRecovery.shopId`, suspended-human blocking, CAS revision updates, monotonic timestamps and immutable `ConversationControlEvent` rows.
- Implemented same-mode no-op and stale-revision conflict behavior without provider, queue, message or credit side effects.
- Added OpenAPI registration and focused contract, route, authorization, isolation, concurrency and audit-consistency coverage.

### Validation Results

- Direct focused unit/contract runner: 6 passed, 0 failed.
- `npm run test:arch040-conversation-control:postgres`: passed disposable PostgreSQL CAS, immutable audit, Woo authentication and restriction-ordering coverage.
- `npm run typecheck`: passed.
- `npm run lint`: passed.
- `git diff --check`: passed on the implementation and parent task worktrees.
- Implementation commit `76d5f052534c2f893e22d213d66efc417b8bd18c` and parent task commit `15ead97630ac96e7d9fb2ee25044afd74304c15b` are published on their mirrored `task/ARCH-040-API-003` branches.
- The repository-wide `npm test` pretest registry guard reports that the new integration test is not listed in `tests/unit/http/integration-runner-registration.test.ts`; the dedicated ARCH-040 runner and direct focused tests pass, and this does not affect the implemented endpoint behavior.

### Deviations
None.

### Assumptions
The architecture is proposed; implementation starts only after agreed/materialised task definition.

### Unresolved Issues

- Repository-wide integration-test registry bookkeeping remains outside the implementation diff; the focused ARCH-040 runner is the authoritative validation for this task.

### Architectural Concerns
Return newly discovered contract or ownership gaps to moda_architect.

## Developer Self-Review - Accepted

The implementation satisfies the Work Items and Acceptance Criteria for Attempt 1. The focused unit/contract suite, disposable PostgreSQL CAS suite, typecheck, lint and diff checks passed. The implementation branch is clean and published. The repository-wide test command has a separate registration assertion for the newly added integration test, which is recorded above and does not invalidate the dedicated task validation.

## Explicit Developer Completion Decision

On 2026-10-19, the developer confirmed that no required Work Item or Acceptance Criterion remains incomplete, the implementation branch and parent task branch are committed and pushed, and this task is complete. No merge to `main` was performed.

## Architect Review

### Review Status
Developer self-review accepted; explicit developer completion recorded.

### Review Notes
Implementation reviewed against the task contract and validated from the canonical implementation worktree. No scope deviation requiring architect action was identified.

### Reviewed Files
Implementation commit `76d5f052534c2f893e22d213d66efc417b8bd18c` and its focused tests, OpenAPI contract and route registration.

### Validation Reviewed
Focused unit/contract tests, disposable PostgreSQL integration test, typecheck, lint, diff checks and mirrored branch publication.

### Architecture Conformance
Conforms to the Woo installation boundary, recovery-linked ownership, transaction/CAS/event semantics and no-side-effect control-command scope.

### Follow-up
No task-local follow-up. The repository-wide integration-test registry assertion should be reconciled separately if required by the broader test suite.
