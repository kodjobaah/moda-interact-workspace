---
id: ARCH-047-API-001
architecture_id: ARCH-047
title: Provide WooCommerce merchant follow-up template choices and safe command admission
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 35
executor: developer
claimed_at: 2026-10-26T08:26:05Z
attempt: 1
depends_on:
  - ARCH-047-DATABASE-001
enables:
  - ARCH-047-WOOCOMMERCE-001
created: 2026-10-26
updated: 2026-10-26
---

# Provide WooCommerce merchant follow-up template choices and safe command admission

## Architecture

Architecture: `ARCH-047` — `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`; coordinator `moda_architect`. Based on 26 October 2026, 06:28 snapshot. Materialised on the canonical parent task branch from the published definition; developer takeover is recorded below.

## Objective

Replace the hosted Woo merchant command's legacy template allowlist and add one authenticated, bounded read endpoint for eligible Moda-authored Follow-up choices without granting the Woo plugin provider credentials or direct database access.

## Context

`src/merchant/conversations/messages/admission.service.ts` currently uses `purpose: "checkout-recovery"`, names/language supplied by the caller and accepts a nonempty `templateParameters` array. The WordPress UI currently hard-disables post-window template selection (`canTemplate: false`) because it has no authoritative list. BG007 must remain the final provider, offer, consent and recipient validator.

## Scope

- Add the exact **GET** route `GET /v1/merchant/conversations/{conversationId}/follow-up-templates` within the installed merchant-authenticated conversations boundary. The hosted response is `{"schemaVersion":1,"templates":[{"name":"...","language":"..."}]}`; include only bounded safe strings, with at most 30 entries and no provider IDs, customer data, parameters or secrets. Return the existing no-store and error style; an ineligible conversation returns an empty list, never invented choices.
- Amend the existing `POST /v1/merchant/conversations/{conversationId}/messages` command admission to resolve `RECOVERY_FOLLOW_UP_TEMPLATE` candidates against active `FOLLOW_UP_*` assignments linked to Moda-authored Meta registrations and their current WABA/language; reject ambiguous/unlinked/disabled/not-approved registrations.
- For a template command, accept only **empty** caller `templateParameters` (`[]` or `{}` for legacy wire shape) and persist an empty parameter intent; BG007 computes actual provider body/header/button parameters from trusted data. Reject nonempty client parameters and no-op on refused commands.

## Out of Scope

- No WooCommerce WordPress UI/PHP code, Meta API calls, new provider client, checkout mutation, eligibility recommendation or DB migration. No new generic merchant auth or second human inbox.

## Requirements

**R1 — Tenant and scope.** Reuse `WooInstallationAuthenticator` and the existing `ownedRecoveryConversation` check; ensure the conversation belongs to the requesting installation/shop and is HUMAN-controlled, outside the 24-hour service window, with follow-up still due and unused. Never return another tenant's assignments.

**R2 — Catalogue.** Only return `FOLLOW_UP_NO_OFFER`, `FOLLOW_UP_CODE_OFFER`, `FOLLOW_UP_AUTOMATIC_OFFER` variants tied to the current shop and sender/WABA and their non-retired published definition; require currently approved registration with no unresolved provider fence/drift. Deduplicate or reject collisions, do not guess provider account. If a verified customer-specific positive offer is unavailable, do not advertise CODE/AUTOMATIC as known eligible; safe No Offer is allowed. No provider calls on GET.

**R3 — Command admission.** Keep existing anti-replay/idempotency, latest customer inbound check, sequence-two transaction and send-command format. Use the exact validated `name + language` that was available from the tenant's current assignment, and prevent nonempty merchant-supplied parameters from being stored as trusted send content. BG007 re-resolves every choice and may reject it later. Do not use Shopify-authored source IDs as if they were Woo checkout evidence.

**R4 — Legacy removal.** Delete the legacy `purpose: "checkout-recovery"` approval lookup and associated outdated API tests/fixtures once the new path passes; preserve all unrelated send-command status, user authentication and compensation logic.

## Work Items

- [x] Implement bounded authenticated GET in the existing merchant conversations route/service directories, without large combined route/service files.
- [x] Replace the legacy follow-up allowlist and client-parameter acceptance with the current registration-backed catalogue in the existing admission service.
- [x] Add status/no-store, tenant, WABA, language, provider-state, window, due-time, idempotency, empty-parameters and replay tests.
- [x] Remove obsolete filters/mocks and record exact file/test changes in Completion Report.

## Interfaces / Contracts

Hosted GET wire contract v1 exactly: `{ schemaVersion: 1, templates: Array<{ name: string, language: string }> }` (maximum 30; ordered locale/name; no customer data). Hosted POST preserves existing `HumanSendInput` fields and status response shape, with the template request's `templateParameters` restricted to `[]`/`{}`. Error/response codes remain bounded by the current merchant conversation contract. WooCommerce-001 owns the WordPress proxy and browser client. BG007 owns actual provider parameter binding and final send eligibility.

## Dependencies

- `ARCH-047-DATABASE-001` (Complete in supplied snapshot).

## Enables

- `ARCH-047-WOOCOMMERCE-001`.

## Acceptance Criteria

- [ ] Only authenticated Woo installation for the correct shop/conversation can read eligible, published, approved Moda Follow-up choices; wrong shop, unapproved, legacy, expired provider state, wrong WABA and ambiguous variants do not leak. **Implementation and unit coverage inspected; disposable PostgreSQL verification pending.**
- [ ] Template admission rejects nonempty caller parameter arrays and old-purpose-only templates while preserving command idempotency and single sequence-two claim. **Implementation and unit coverage inspected; disposable PostgreSQL verification pending.**
- [x] All other human-text, payment, window, consent and STOP guards are unchanged; BG007 still owns final admission.
- [x] No remaining production `purpose: "checkout-recovery"` allowlist in API merchant follow-up code; stale tests replaced.

## Validation

- [ ] API route/contract/authentication and PostgreSQL integration tests in repository's declared harness, including GET-only and hostile-parameter negative cases. **Route/contract unit tests passed as part of 611/611; `npm run test:arch047-follow-up:postgres` was not executed in supplied log.**
- [x] Lint, typecheck/build where declared and `git diff --check`.

## Stop Condition

Return current task to `review` with tests and Completion Report, then STOP. Do not modify Background, Shopify, Woo plugin or `_index.md` files.

## Implementation Notes

Use isolated worktrees with exact mirrored task branches. Keep GET/POST tenant scoping in the owning API service, never trust browser role or supplied WABA. Consumers remain free to show fewer template candidates but may never manufacture new ones.

## Execution Ownership Amendment

- Date: 2026-10-26.
- Materialisation: The supplied canonical task definition was already published in the workspace history. Its dedicated parent worktree and `task/ARCH-047-API-001` branch were created from the current published `origin/main`; implementation preparation has not yet been claimed.
- Change: The developer explicitly invoked `/moda_developer_create ARCH-047-API-001` for this Ready agent-owned task. Execution ownership transfers to the developer and completion mode is set to developer review.
- Preserved: `assigned_agent: moda_api`, coordinator, repository, task scope, acceptance criteria and validation requirements.
- Dependency check: `ARCH-047-DATABASE-001` routes as `complete` in its canonical task record.
- State before claim: `ready`, Attempt 0, `executor: null`, `claimed_at: null`. The canonical developer workflow will claim Attempt 1 after synchronizing both task worktrees.

## Completion Report

### Status

In Progress — developer Attempt 1 implementation finished and committed as `ef4578b` (`feat(api)`) on `task/ARCH-047-API-001`; terminal log shows a successful push to `origin/task/ARCH-047-API-001`. Awaiting mandatory disposable PostgreSQL integration validation before changing task status to `review`. Patch iteration Attempt 2 does not alter the durable developer task attempt number (`attempt: 1`).

### Files Changed

API implementation (from the `ef4578b` commit output; 22 files in total):

- `src/composition/merchant.ts`
- `src/merchant/conversations/messages/admission.service.ts`
- `src/merchant/conversations/messages/contract.ts`
- `src/merchant/conversations/messages/follow-up-catalogue.ts` (new)
- `src/merchant/conversations/messages/follow-up.service.ts` (new)
- `src/merchant/conversations/messages/routes.ts`
- `src/platform-configuration/composition.ts`
- `src/platform-configuration/errors.ts`
- `src/platform-configuration/service.ts`
- `openapi/merchant-conversation-human-send-v1.yaml`
- `package.json`
- `scripts/test-arch040-woo-human-send-postgres.mjs`
- `tests/integration/merchant/conversations/arch047-template-fixture.ts` (new)
- `tests/integration/merchant/conversations/messages.follow-up-catalogue.postgres.test.ts` (new)
- `tests/integration/merchant/conversations/messages.follow-up-policy.postgres.test.ts`
- `tests/integration/merchant/conversations/messages.service.postgres.test.ts`
- `tests/unit/http/integration-runner-registration.test.ts`
- `tests/unit/merchant/conversations/messages/contract.test.ts`
- `tests/unit/merchant/conversations/messages/follow-up-catalogue.test.ts` (new)
- `tests/unit/merchant/conversations/messages/openapi-contract.test.ts`
- `tests/unit/merchant/conversations/messages/routes.test.ts`
- `tests/unit/platform-configuration/service.test.ts`

The present handoff patch updates only this canonical task definition; it does not alter implementation files, domain `_index.md`, parent architecture, or the `## Architect Review` section.

### Work Completed

- Added authenticated, tenant-scoped, no-store `GET /v1/merchant/conversations/{conversationId}/follow-up-templates`, returning schema v1 with at most 30 bounded `{name, language}` choices.
- Added a read-only, bounded catalogue query against canonical ARCH-047 template variants, Meta registrations, reviewed locales, and published definition state. Provider sender WABA is read from sealed platform configuration on the server; stale reconciliation, drift, mismatched WABA, unlinked/ambiguous or unapproved registrations fail closed.
- Replaced merchant POST's `purpose: "checkout-recovery"` allowlist with registration-backed `FOLLOW_UP_*` admission; nonempty client template parameters are rejected and the durable command's parameter intent is empty. Existing idempotent replay, HUMAN control, service-window and sequence-two claim remain.
- Preserved Background BG007 ownership of final consent/STOP, offer and provider delivery validation. No Shopify provider identity or Woo checkout mutation was introduced.
- Added/updated unit, route/OpenAPI and disposable PostgreSQL test fixtures. Because a customer-specific positive-offer evidence reader is not available for Woo, catalogue choices intentionally remain `FOLLOW_UP_NO_OFFER` only.

### Validation Results

Observed in supplied `typescript(20261026-115208)` terminal log:

- Attempt 2 correction: `git apply --check --whitespace=error-all`, `git apply --whitespace=error-all`, and `git diff --check` returned without reported errors.
- `npm test`: **611 passed / 0 failed / 0 skipped**, including the new catalogue and route unit tests.
- `npm run typecheck`: **passed**, using generated Prisma Client v6.19.3.
- `npm run lint`: **passed** with `--max-warnings=0`.
- `npm run build`: **passed**.
- `git commit -m "feat(api)"`: created implementation commit `ef4578b`, reporting 22 changed files and five new files.
- `git push -u origin task/ARCH-047-API-001`: **succeeded** according to terminal output.
- `npm run test:arch047-follow-up:postgres`: **NOT RUN / no result shown**. The new PostgreSQL integration test exists, but `npm test` runs `tests/unit/**/*.test.ts` only; it is not equivalent to the PostgreSQL test. This acceptance gate remains open.

Physical worktree isolation evidenced by the archive helper's terminal output:

- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-047-API-001` on `task/ARCH-047-API-001` (task-file metadata).
- API implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-047-API-001` on `task/ARCH-047-API-001` (Git output).
- Canonical primary workspace root, start-of-attempt fast-forward/mainline synchronization, recursive submodule preparation, and confirmation that no shared checkout was mutated: **not independently demonstrated by the attached terminal log**. Supply the launcher preparation packet or equivalent evidence for architect review; do not infer compliance from the ZIP alone.

### Deviations

The API's pinned Prisma schema predates canonical ARCH-047. The catalogue therefore uses a bounded SQL read of the accepted canonical ARCH-047 tables without modifying the API database submodule or creating new migrations. This approach requires the accepted migration to be deployed and must be exercised by the disposable PostgreSQL suite.

### Assumptions

- The accepted `ARCH-047-DATABASE-001` migration is available to the disposable test harness and the deployment environment.
- Positive offer choices are excluded until a customer-specific, provider-verified Woo offer eligibility source exists; no eligibility is inferred from the merchant's chosen template.

### Unresolved Issues

- **Review blocker:** run `npm run test:arch047-follow-up:postgres` using the approved disposable PostgreSQL harness; attach the full result, then mark the remaining acceptance and validation checkboxes and transition the task to `review`.
- **Workflow evidence gap:** attach or transcribe the start-of-attempt launcher synchronization/submodule/isolation evidence before acceptance. The supplied log establishes the task-worktree paths but does not establish every required policy check.
- A local untracked file named `typescript` appears in `git status` after the implementation commit; it was not part of the 22-file implementation commit. Do not stage it as task source.

### Architectural Concerns

No new cross-repository contract or schema ownership requested. The API provides advisory template choices and durable human-send admission only; Background BG007 remains the final eligibility, provider, moderation and delivery boundary. The task is not architect-accepted, and enabling `ARCH-047-WOOCOMMERCE-001` must await developer completion.

## Architect Review

### Review Status
Pending.

### Review Notes
No implementation reviewed.

### Reviewed Files
None.

### Validation Reviewed
None.

### Architecture Conformance
Not assessed.

### Follow-up
WooCommerce UI consumes this endpoint; Background BG007 performs final admission.
