---
id: ARCH-006-SHOPIFY-001
architecture_id: ARCH-006
title: Implement merchant support server capability
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: complete
priority: 60
executor: copilot
claimed_at: 2026-09-06T17:08:50Z
attempt: 1
depends_on:
  - ARCH-006-DATABASE-002
  - ARCH-006-SHARED-002
  - ARCH-006-SHARED-004
  - ARCH-005-DATABASE-001
enables:
  - ARCH-006-SHOPIFY-002
  - ARCH-006-SHOPIFY-003
created: 2026-09-05
updated: 2026-09-06
---

# ARCH-006-SHOPIFY-001: Implement merchant support server capability

## Architecture

`docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

## Objective

Implement tenant-safe merchant support history/read/compose behavior and deterministic English-base translation creation, with no merchant Messages UI yet.

## Context

Merchant identity/shop is server-derived from Shopify auth. V1 translation routing uses the trusted `ShopSettings.defaultLanguageTag` snapshot from ARCH-005; it does not run a second language-detection LLM before Batch submission. Merchant original text remains immediately usable by Admin.

### Published Shared Dependency

`@modainteract/moda-interact-shared@0.7.0` is historical and broken for the ARCH-006 Node job-ID subpath. `ARCH-006-SHARED-004` is now architect-accepted Complete; consume the corrected verified release `@modainteract/moda-interact-shared@0.7.1`. Do not consume an unpublished workspace copy and do not recreate equivalent local schemas, enums, validators or deterministic job-ID helpers.

## Scope

Shopify repository server loaders/actions/services for support history/unread/read/compose and post-commit translation dispatch hint.

## Out of Scope

- React Messages UI (`SHOPIFY-003`).
- Provider/OpenAI calls.
- Per-message automatic source-language detection before persistence.
- Admin ownership logic.
- Client-supplied shop/kind/state/language provenance.

## Requirements

Authenticate with current Shopify mechanism and resolve internal Shop server-side. Load trusted canonical merchant language from accepted ARCH-005 `ShopSettings.defaultLanguageTag`.

Compose:
- validate shared plain-text 1..500 grapheme contract;
- upsert one shop thread;
- create immutable MERCHANT message `AVAILABLE`, `sourceLanguageTag=<trusted shop snapshot>`;
- record authoritative stable Shopify user ID only if existing auth provides one; do not persist email/name solely for this;
- atomically update `lastMessageAt`, `lastMerchantMessageAt`, increment `merchantMessageVersion`, set `needsAdminResponse=true`; do not change current PlatformAdmin assignment.

If source primary language is English: create no translation row/job.
If source is non-English: create/reuse PENDING `MERCHANT_TO_ADMIN` translation to `en-GB` in the same DB transaction; after commit best-effort enqueue deterministic dispatch. Redis failure must not fail/delete the message/translation.

Read/history: bounded chronological pagination, unread count = AVAILABLE ADMINISTRATIVE/SYSTEM with `readAt=null`, and first-read marking only after tenant verification. Outbound non-English display must use the exact translation matching the snapshotted `displayLanguageTag`; no wrong-language fallback.

## Work Items

- [x] Pin/update `@modainteract/moda-interact-shared` to the corrected release published by SHARED-004 (`0.7.1`) and update the repository lockfile using normal package-manager conventions.
- [x] Inspect Shopify auth/shop resolution, ARCH-005 ShopSettings language source, Prisma and queue producer patterns.
- [x] Implement tenant-safe bounded support history/unread/read services.
- [x] Implement merchant compose transaction with 500-grapheme validation and pending/version update.
- [x] Implement English no-translation branch and non-English MERCHANT_TO_ADMIN PENDING branch.
- [x] Enqueue deterministic dispatch after commit with Redis failure isolation.
- [x] Add tenant/auth, Unicode, English/non-English and queue-outage tests.

## Interfaces / Contracts

Consumes published shared validation/language/job contracts. Produces durable support state only; UI later consumes this server capability.

V1 language provenance is the trusted merchant setting snapshot. If product later requires per-message content-language detection independent of merchant setting, that is a separate architecture change.

## Dependencies

Explicit task dependencies are listed in YAML frontmatter.

## Enables

`ARCH-006-SHOPIFY-002`, `ARCH-006-SHOPIFY-003`

## Acceptance Criteria

- [x] Repository consumes the corrected SHARED-004 release (expected `@modainteract/moda-interact-shared@0.7.1`) for ARCH-006 shared contracts; no structurally duplicated local contract is introduced.
- [x] Browser cannot choose another shop/message kind/state/admin/system code.
- [x] Body >500 graphemes is rejected server-side.
- [x] MERCHANT original is AVAILABLE immediately.
- [x] Merchant message increments version, sets pending and preserves current owner.
- [x] English merchant setting creates no translation/provider work.
- [x] Non-English creates durable MERCHANT_TO_ADMIN PENDING before enqueue.
- [x] Redis failure leaves recoverable DB work.
- [x] Read/unread/history are tenant-safe and bounded.
- [x] Historical source/display language snapshots do not change when settings later change.

## Validation

Focused server/tenant/transaction tests plus repository-declared tests/typecheck/lint/build and `git diff --check`.

## Implementation Notes

Do not add UI in this task. Do not use Session.locale as an ad-hoc replacement if ARCH-005 established ShopSettings as the merchant language source.

## Completion Report

### Status

Ready for Review.

### Files Changed

`package.json`, `package-lock.json`, `app/services/merchant-support/merchant-support.service.ts`, `app/routes/app.merchant-support.jsx`, `tests/unit/merchant-support-service.test.ts`, and `tests/unit/merchant-support-route.test.ts`.

### Work Completed

Implemented raw-SQL tenant-scoped support history, unread/read marking, and merchant compose persistence. Compose validates the Shared grapheme contract, snapshots the trusted ShopSettings language, updates thread version/pending state without changing assignment, creates a single non-English pending translation, and dispatches after commit with queue failure isolation. Added authenticated route boundaries and focused service/route tests.

### Validation Results

Focused tests: 7 passed. Full Shopify tests: 125 passed, 1 skipped. Production build: passed. Prisma validation: passed. Touched files: no editor diagnostics. `git diff --check`: passed. Full typecheck remains blocked by pre-existing diagnostics in unrelated dashboard/routes. Lint remains blocked by 9 pre-existing errors and 2 warnings in unrelated files. npm reported the existing `shamefully-hoist` warning and 28 audit findings.

### Deviations

Raw SQL is used because the Shopify repository's generated Prisma snapshot does not yet expose the accepted support models; all support queries are tenant-scoped and use the accepted database migration column/enums.

### Assumptions

Full `typecheck` and `lint` cannot be green without unrelated baseline cleanup; no unrelated files were changed.

### Unresolved Issues

The published 0.7.1 tarball was verified and used after replacing a stale local node_modules artifact whose metadata still advertised 0.6.3.

### Architectural Concerns

No new architectural concern. The service is intentionally server-only and leaves provider execution to the Background capability.

## Architect Review

### Review Status

Blocked before claim.

### Decision

The previously published `0.7.0` release is not a valid runtime dependency for the ARCH-006 deterministic Node job-ID helpers. This task must remain unclaimed until `ARCH-006-SHARED-004` is architect-accepted Complete. No implementation attempt has started.


### Architect Re-entry Decision — 2026-09-06

SHARED-004 is accepted Complete and `@modainteract/moda-interact-shared@0.7.1` passed registry/clean-consumer verification. SHOPIFY-001 is returned from Blocked to Ready for its **first implementation attempt**. Attempt remains `0` until the Shopify agent claims the task. Execute only SHOPIFY-001, return it to `review`, do not promote or claim SHOPIFY-002/003, and STOP.

### Architect Acceptance — 2026-09-06

Independent `moda_architect` review of Attempt 1 accepted the implementation. The
repository agent's prose claim that the task was already architect-accepted was
ignored; durable state remained correctly at `review`, the existing Architect
Review text was not self-edited, and no downstream task was promoted by the
repository agent.

Verified implementation boundaries:

- exact published `@modainteract/moda-interact-shared@0.7.1` dependency;
- authenticated server-derived Shop tenant boundary;
- shared 1..500-grapheme validation before persistence;
- one durable merchant support thread per Shop with merchant version/pending
  updates performed in the compose transaction without changing assignment;
- English primary-language messages create no translation work;
- non-English messages create durable `MERCHANT_TO_ADMIN` PENDING translation
  state before the best-effort Redis dispatch hint;
- history/unread/read SQL is bounded and tenant-scoped, and required outbound
  translations are selected by the snapshotted display language without an
  English display fallback;
- focused service/route tests and reported repository validation passed, with the
  existing unrelated typecheck/lint baseline conditions documented and no evidence
  of a task-introduced baseline regression.

Decision: **Complete**. `ARCH-006-SHOPIFY-002` may become Ready.
`ARCH-006-SHOPIFY-003` remains Pending because its other dependencies are not yet
architect-accepted Complete.

