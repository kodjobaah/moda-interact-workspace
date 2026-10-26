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
status: ready
priority: 35
executor: null
claimed_at: null
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
- [ ] Capture and record canonical launcher preparation and start-of-attempt synchronization evidence for both task worktrees, including recursive implementation-submodule synchronization/status, before running the Attempt 2 validation suite. Do not reconstruct this evidence for Attempt 1.

## Interfaces / Contracts

Hosted GET wire contract v1 exactly: `{ schemaVersion: 1, templates: Array<{ name: string, language: string }> }` (maximum 30; ordered locale/name; no customer data). Hosted POST preserves existing `HumanSendInput` fields and status response shape, with the template request's `templateParameters` restricted to `[]`/`{}`. Error/response codes remain bounded by the current merchant conversation contract. WooCommerce-001 owns the WordPress proxy and browser client. BG007 owns actual provider parameter binding and final send eligibility.

## Dependencies

- `ARCH-047-DATABASE-001` (Complete in supplied snapshot).

## Enables

- `ARCH-047-WOOCOMMERCE-001`.

## Acceptance Criteria

- [x] Only authenticated Woo installation for the correct shop/conversation can read eligible, published, approved Moda Follow-up choices; wrong shop, unapproved, legacy, expired provider state, wrong WABA and ambiguous variants do not leak. Verified by focused unit tests and the 4/4 disposable PostgreSQL integration suite.
- [x] Template admission rejects nonempty caller parameter arrays and old-purpose-only templates while preserving command idempotency and single sequence-two claim. Verified by focused unit tests and the 4/4 disposable PostgreSQL integration suite.
- [x] All other human-text, payment, window, consent and STOP guards are unchanged; BG007 still owns final admission.
- [x] No remaining production `purpose: "checkout-recovery"` allowlist in API merchant follow-up code; stale tests replaced.

## Validation

- [x] API route/contract/authentication and PostgreSQL integration tests in repository's declared harness, including GET-only and hostile-parameter negative cases. `npm test`: 611/611; `npm run test:arch047-schema:unit`: 7/7; `npm run test:arch047-follow-up:postgres`: 4/4.
- [x] Lint, typecheck/build where declared and `git diff --check`.
- [ ] Record the Attempt 2 canonical resolver route, exact parent/implementation worktree and branch identities, fetch/ancestry checks, clean status, and recursive submodule sync/update/status before validation. Attempt 1's original packet is unavailable and remains historical.

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

Changes Requested — developer self-review of Attempt 1. Implementation is committed and pushed on `task/ARCH-047-API-001` (`ef4578b` followed by `c75710e`). Functional and repository validation results are recorded below. The canonical launcher preparation, start-of-attempt synchronization, and recursive submodule evidence are unavailable. Attempt 1 is returned to `ready` without incrementing the attempt or changing implementation. Capture fresh canonical evidence before validation in Attempt 2, rerun the task-focused validation, and resubmit for review. This is not architect acceptance or explicit developer completion.

Patch iterations 1–5 are implementation corrections within the one durable developer execution attempt; `attempt: 1` remains unchanged.

### Files Changed

The implementation commit `ef4578b` covered 22 API files:

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

The final correction commit `c75710e` also added:

- `scripts/arch047-canonical-schema.mjs` (new)
- `tests/scripts/arch047-canonical-schema.test.mjs` (new)

It updated `package.json`, `scripts/test-arch040-woo-human-send-postgres.mjs`, `tests/integration/merchant/conversations/messages.follow-up-policy.postgres.test.ts`, and `tests/integration/merchant/conversations/messages.service.postgres.test.ts` (already in the list above). No other application repository or schema was changed for this task.

This review-submission patch changes only the parent task file. Domain `_index.md`, the parent architecture, and the `## Architect Review` section are untouched.

### Work Completed

- Implemented authenticated, tenant-scoped, no-store `GET /v1/merchant/conversations/{conversationId}/follow-up-templates`, returning schema v1 with at most 30 `{name, language}` choices.
- Resolved choices against current shop assignments, immutable Moda-authored template definitions, reviewed locales, linked Meta registrations, published state, provider approval/freshness and drift fences. The sender WABA is read from sealed platform configuration on the server.
- Replaced the legacy `purpose: "checkout-recovery"` POST allowlist with registration-backed `FOLLOW_UP_*` admission. Rejected nonempty client template parameters; the durable command records an empty parameter intent.
- Preserved Woo authentication, HUMAN control, service-window/due-time checks, idempotency, sequence-two uniqueness and Background BG007 ownership of final consent, STOP, offer, moderation and delivery checks.
- Added route/OpenAPI/unit and disposable PostgreSQL regression tests, including tenant separation, stale/ambiguous/wrong-WABA registrations, caller parameter injection, replay and sequence-two enforcement.
- Corrected disposable PostgreSQL schema discovery for linked task worktrees, verified the canonical migration lineage, handled macOS canonical paths, and removed test registration uniqueness collisions. The final one-line `node:process` import resolves the lint error.
- Because Woo has no verified customer-specific positive-offer evidence reader in this task, the catalogue intentionally returns only `FOLLOW_UP_NO_OFFER` choices.

### Validation Results

Evidence from the supplied developer logs and implementation snapshot:

- `npm test`: **611 passed, 0 failed** (earlier full-suite run).
- `npm run test:arch047-schema:unit`: **7/7 passed** (Attempt 4 resolver validation).
- `npm run test:arch047-follow-up:postgres`: **4/4 passed**, using the approved canonical schema and migration chain in a disposable PostgreSQL environment (Attempt 4 validation).
- `npm run typecheck`: **passed** (Attempt 4 validation).
- `npm run build`: **passed** (Attempt 4 validation).
- `npm run lint`: **passed** with `--max-warnings=0` in `typescript(20261026-130430)` after the Attempt 5 `node:process` import fix.
- `git apply --check --whitespace=error-all`, `git apply --whitespace=error-all`, and `git diff --check`: **completed without reported errors** for the Attempt 5 correction in the latest log.
- `git commit`: **`c75710e`** (`feat(arch-047-api-001)`), 6 changed files, on `task/ARCH-047-API-001`.
- `git push -u origin task/ARCH-047-API-001`: **succeeded**; log shows remote branch advanced `ef4578b..c75710e`.
- The comprehensive suites were run before the final import-only correction. The final log reran lint, not every suite; the correction adds an explicit Node built-in import and does not change business logic.

Physical-worktree evidence recorded by the archive helper and Git output:

- Dedicated parent: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-047-API-001`.
- Dedicated API implementation: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-047-API-001`, on `task/ARCH-047-API-001`.
- **Outstanding review evidence**: the provided logs/ZIP do not independently establish the launcher-resolved primary workspace root, start-of-attempt parent/implementation synchronisation, or recursive implementation submodule preparation. The launcher's prepared execution packet, or equivalent canonical evidence, should be included with the review; the physical paths alone do not prove these policy requirements.

### Deviations

The API's pinned Prisma-generated schema predates accepted ARCH-047. The catalogue therefore uses a bounded read-only SQL query over canonical ARCH-047 tables without changing the database submodule or introducing a migration. Its disposable PostgreSQL runner uses the accepted canonical schema/migration chain and checks lineage rather than pretending the older API schema contains the new models.

### Assumptions

- The accepted `ARCH-047-DATABASE-001` migration is deployed before the API needs these catalogue tables in a shared runtime.
- The verified current sender WABA is available through sealed server-side platform configuration.
- Without a verified Woo customer-specific positive-offer source, no `FOLLOW_UP_CODE_OFFER` or `FOLLOW_UP_AUTOMATIC_OFFER` choice is advertised.

### Unresolved Issues

- **Workflow evidence:** Attempt 1's original launcher preparation packet and start-of-attempt synchronization/recursive-submodule evidence are unavailable. This historical gap is not reconstructed. Before validation in Attempt 2, capture and record the canonical resolver route; exact parent and implementation paths and branch identities; fetch and task/main ancestry checks for both repositories; clean task-owned working-tree state; and `submodule sync --recursive`, `submodule update --init --recursive`, and recursive status in the implementation worktree. Clearly distinguish the new packet from Attempt 1 history.
- A local file named `typescript` appeared untracked in an earlier implementation-worktree status capture, but the current canonical implementation worktree is clean and the artifact is not part of the pushed implementation commit.
- No known outstanding implementation test failure from the supplied validation logs. The task is **not** architect-accepted or explicitly developer-completed.

### Architectural Concerns

No new cross-repository runtime contract or schema ownership is requested. The API only exposes advisory template choices and durable human-send admission; Background BG007 independently validates actual sends. `ARCH-047-WOOCOMMERCE-001` remains dependent on this task attaining `status: complete`, not merely `review`.

## Developer Self-Review - Changes Requested (Attempt 1)

- Review result: Changes Requested for missing required workflow evidence; this review found no source-code defect.
- Evidence discrepancy: the Completion Report states that Attempt 1's launcher preparation, synchronization, and recursive-submodule packet was not established. Physical paths and current branch cleanliness do not prove start-of-attempt preparation. Do not reconstruct or relabel later evidence as Attempt 1 evidence.
- Required correction for Attempt 2: before validation, capture the canonical resolver route; exact parent and implementation worktree/branch identities; fetch and task/main ancestry checks in both repositories; clean worktree status; and recursive submodule sync/update/status in the implementation worktree.
- Revalidation: rerun `npm run test:arch047-schema:unit`, `npm run test:arch047-follow-up:postgres`, `npm run typecheck`, `npm run build`, `npm run lint`, and `git diff --check` from the canonical implementation worktree. Preserve the recorded Attempt 1 `npm test` result as historical evidence and clearly label any newly run suite results by attempt.
- State: `status: ready`, `executor: null`, `claimed_at: null`, `attempt: 1`. Do not create Attempt 2 here; the next developer claim increments once.
- Scope/frontier: implementation files and branch remain unchanged. `ARCH-047-WOOCOMMERCE-001` remains pending until API-001 is Complete.

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
