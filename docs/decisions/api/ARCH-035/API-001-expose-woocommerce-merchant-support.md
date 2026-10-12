---
id: ARCH-035-API-001
architecture_id: ARCH-035
title: Expose Woo merchant support history and actions
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 95
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-035-WOOCOMMERCE-001
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-API-001: Expose Woo merchant support history and actions

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: uploaded `moda-interact-workspace(20261011-185536).zip`; task is a portable definition, not a claimed/materialised worktree.

## Objective

Expose the existing merchant support thread, translated/system-message information, send and read-state actions through Woo installation authentication.

## Context

The previous Shopify/Woo merchant-screen parity assessment showed this specific gap. Reuse the already accepted
ARCH-026 WordPress connection, locale and Shop security foundations and ARCH-027 billing components; do not duplicate
provider-neutral Moda domain state. The current capability is not established by this task definition.

## Deterministic implementation specification — mandatory

**Architect contract.** The exact model/column names, paths, API shapes, authentication boundary, state machine and
negative cases below are the implementation target. This section supersedes less-specific high-level text elsewhere
in this task. Agents may split production code into smaller modules, but must not change a public contract, migration
field, ownership rule, or dependency without returning to the architect. If a named existing dependency is absent or
incompatible, **STOP** and report the precise finding; do not silently invent a substitute.

**Files:** add `src/merchant/support/{contract,service,routes}.ts` plus `service.test.ts`, `routes.test.ts`, a
focused PostgreSQL test and `openapi/woocommerce-merchant-support-v1.yaml`; thin registration in `src/index.ts` /
`src/woocommerce/installation/routes.ts`. Do not import `moda-interact/app/...` (Shopify's Next runtime) into the
hosted API; its `app/services/merchant-support/merchant-support.service.ts` supplies the reference SQL/business
rules.

**Three exact installation-authenticated routes:** `GET /v1/merchant/support/messages?page=1&pageSize=25` (`page>0`,
`pageSize=10|25|50`); `POST /v1/merchant/support/messages` exact `{body:string,actionId:UUIDv4}`; `POST
/v1/merchant/support/messages/{messageId}/read` empty body. Reply with
`{schemaVersion:1,page,pageSize,total,totalPages,unread,items:[{id,kind,state,displayBody,originalBody,isTranslated,sourceLanguageTag,displayLanguageTag,systemCode,systemVersion,createdAt,readAt}]}`
on GET; new message POST returns `{schemaVersion:1,messageId}`; mark-read returns `{schemaVersion:1,marked:boolean}`.
Reject unknown fields; never expose `shopifyUserId`, internal support admin ID, raw translation job ID, credential or
other tenant's message.

**Data ownership:** use existing `support.MerchantSupportThread` (`shopId @unique`) and `MerchantSupportMessage`, and
Shared `AuthoredSupportBodySchema` (500 Unicode graphemes). Lock the Shop and thread; insert the thread once and
increment `merchantMessageVersion` only for a newly committed merchant message. `sourceKey` derives from
`woo-support:<shopId>:<actionId>` and is unique; same replay returns original message, different body with same
actionId returns `409`. Set `shopifyUserId=null`; `kind=MERCHANT`, `state=AVAILABLE`, correct default-language tag,
and `needsAdminResponse=true`. Preserve existing translation dispatch contract/queue
(`MERCHANT_COMMUNICATIONS_QUEUE_NAME`): create the durable translation record before best-effort enqueue; queue
absence must not lose message. Mark-read updates only a Shop-owned `ADMINISTRATIVE|SYSTEM` message, with monotonic
readAt; other-Shop IDs return 404.

**Auth and lifecycle:** use the existing WooInstallationAuthenticator and active-Shop/installation checks. GET may
remain viewable for a connected restricted plan if existing support policy allows; mutation denies
disconnected/revoked/shop-invalid. Explicit codes: `invalid_request`, `support_message_unavailable`,
`support_conflict`, `remote_unavailable`. All responses tenant-scoped. Tests include 500/501 graphemes, unicode,
repeat actionId/concurrency, wrong-Shop read, read-only system messages, translated/untranslated, stale credentials
and Redis unavailable, Shopify support regression.

## High-level scope (non-authoritative summary)

- Reuse support.MerchantSupportThread/Message and the published merchant-communications content/length contracts; never create a second support inbox.
- Implement versioned bounded GET history with pagination, unread counts and translated/original message variants, plus explicit compose and mark-read endpoints.
- Derive shop identity only from active Woo installation credentials, apply lifecycle restrictions, optimistic/idempotent write guards, bounded authored text and safe error codes.
- Preserve Admin support state, system-message metadata and existing translation queue semantics; never spoof Shopify user identity or expose Shopify-only merchant refund actions to Woo Shops.

## Out of Scope

- New support tables, customer WhatsApp replies, administrator queue redesign, direct WordPress-to-Postgres access.
- Other services' implementation code, `docs/decisions/**/_index.md`, and architecture index reconciliation.

## Implementation work items — mandatory

- [ ] Implement **exactly** the named files, routes/models and public DTO fields in the Deterministic implementation specification; do not widen cross-repository ownership.
- [ ] Enforce every declared shop/platform binding, validation boundary, state transition, CAS/idempotency invariant, denial path and privacy restriction.
- [ ] Implement the **specific negative and concurrency test matrix** named in the specification; record actual commands and real results.
- [ ] Prove that affected Shopify behaviour and current ARCH-026/027 Woo onboarding/billing contracts are preserved.
- [ ] Provide a bounded diff, changed-file list, applied migration/Shared package version where applicable, task Completion Report, and clean synchronised implementation/task worktree evidence.

## Cross-repository boundary (common requirements)

- Owning repository: `moda-interact-api`; consume only versioned, accepted cross-repository contracts.
- Hosted Woo identity is the authenticated Shop/installation; no client-controlled `shopId` or Shopify-session authentication. Where browser UI is in scope, transport runs through privileged WordPress REST/PHP with nonce and `manage_woocommerce` capability.
- For merchant display, all 20 supported WordPress UI locales use administrator language with site fallback; this must not change Shop or customer conversation language.
- New or changed externally visible API fields require strict bounded runtime schema validation and a matching OpenAPI/Shared contract owned by the producer.
- No additional external interface is authorised beyond the bounded scope above.

## Dependencies

No blocking task dependency beyond the accepted ARCH-026/027 foundations in the stated snapshot. Confirm current compatible package/DB pins before claiming.

## Enables

- `ARCH-035-WOOCOMMERCE-001`

## Acceptance Criteria

- [ ] Tenant-isolation tests for reads and commands including revoked/rotated credentials.
- [ ] Read/send/read-receipt and concurrency tests; Shopify merchant support unchanged.
- [ ] API schema, runtime validation, typecheck, lint and focused tests.
- [ ] Scope stays within `moda-interact-api` and preserves approved cross-provider and 20-locale contracts.
- [ ] Baseline, task launcher isolation, implementation commit, parent task report and regression evidence are recorded without false claims for unavailable provider services.
- [ ] `git diff --check` and repository-required build/test/lint commands pass or precise blockers are reported.

## Validation

- [ ] Run repository-declared focused test suites plus full typecheck/lint/build where applicable.
- [ ] Run real integration/black-box provider or disposable database evidence when this task's scope includes that dependency; do not substitute a mocked success.
- [ ] Check tenant isolation, disconnected/revoked credential handling, idempotency and requested negative cases.
- [ ] For Woo UI tasks, run `npm run test:i18n`, `npm run i18n:verify:20`, PHP/JS tests, admin-locale test, `npm run plugin-zip` and manual LocalWP workflow.
- [ ] Verify `git diff --check` and submit the canonical Completion Report; leave all `_index.md` files untouched until explicit reconciliation.

## Stop Condition

When requirements/acceptance and required validation are fulfilled, set the task to `review`, populate the Completion
Report and return to `moda_architect`. Do not begin dependent tasks or change other repositories on this task branch.

## Implementation Notes

Keep production responsibilities in small testable modules; prefer provider-neutral existing ownership to Shopify/Woo
service duplication. Return unexpected cross-repository schema or provider-contract gaps to the architect before
widening scope.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

Dependencies will be rechecked at task claim time; no generated task document itself creates a branch, provider credential, tested artifact or release.

### Unresolved Issues

None identified beyond documented dependencies/provider gating.

### Architectural Concerns

None reported at definition time.

## Architect Review

### Review Status

Pending implementation.

### Review Notes

No implementation reviewed.

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending.

### Follow-up

**Superseded by ARCH-035 UI-only scope revision (11 October 2026).** This definition is historical and MUST NOT be claimed or executed under ARCH-035. Backend/data/event/coupon capabilities require a separately agreed architecture if ever authorised. No implementation was reviewed or accepted.

Return to architect on implementation submission.
