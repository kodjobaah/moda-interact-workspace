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

- [ ] Implement bounded authenticated GET in the existing merchant conversations route/service directories, without large combined route/service files.
- [ ] Replace the legacy follow-up allowlist and client-parameter acceptance with the current registration-backed catalogue in the existing admission service.
- [ ] Add status/no-store, tenant, WABA, language, provider-state, window, due-time, idempotency, empty-parameters and replay tests.
- [ ] Remove obsolete filters/mocks and record exact file/test changes in Completion Report.

## Interfaces / Contracts

Hosted GET wire contract v1 exactly: `{ schemaVersion: 1, templates: Array<{ name: string, language: string }> }` (maximum 30; ordered locale/name; no customer data). Hosted POST preserves existing `HumanSendInput` fields and status response shape, with the template request's `templateParameters` restricted to `[]`/`{}`. Error/response codes remain bounded by the current merchant conversation contract. WooCommerce-001 owns the WordPress proxy and browser client. BG007 owns actual provider parameter binding and final send eligibility.

## Dependencies

- `ARCH-047-DATABASE-001` (Complete in supplied snapshot).

## Enables

- `ARCH-047-WOOCOMMERCE-001`.

## Acceptance Criteria

- [ ] Only authenticated Woo installation for the correct shop/conversation can read eligible, published, approved Moda Follow-up choices; wrong shop, unapproved, legacy, expired provider state, wrong WABA and ambiguous variants do not leak.
- [ ] Template admission rejects nonempty caller parameter arrays and old-purpose-only templates while preserving command idempotency and single sequence-two claim.
- [ ] All other human-text, payment, window, consent and STOP guards are unchanged; BG007 still owns final admission.
- [ ] No remaining production `purpose: "checkout-recovery"` allowlist in API merchant follow-up code; stale tests replaced.

## Validation

- [ ] API route/contract/authentication and PostgreSQL integration tests in repository's declared harness, including GET-only and hostile-parameter negative cases.
- [ ] Lint, typecheck/build where declared and `git diff --check`.

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

In Progress — developer Attempt 1 claimed at `2026-10-26T08:26:05Z`; the canonical API implementation worktree is prepared on `task/ARCH-047-API-001` at `31382d75e11d9df53f15254b595cfcca26248005` (`origin/main`). Implementation has not started.

### Files Changed
None.

### Work Completed
None.

### Validation Results
Not run.

### Deviations
None.

### Assumptions
Existing authenticated Woo installation boundary and database Prisma client are reused.

### Unresolved Issues
Read-only provider verified coupon eligibility remains a separate gap; this task does not implement it.

### Architectural Concerns
None additional.

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
