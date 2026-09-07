---
id: ARCH-006-ADMIN-004
architecture_id: ARCH-006
title: Build the Admin merchant-support inbox UI
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 80
executor: copilot
claimed_at: 2026-09-06T23:37:00Z
attempt: 6
depends_on:
  - ARCH-006-ADMIN-003
  - ARCH-006-BACKGROUND-007
enables:
  - ARCH-006-SYSTEM-TEST-001
created: 2026-09-05
updated: 2026-09-07T08:35:00Z
---

# ARCH-006-ADMIN-004: Build the Admin merchant-support inbox UI

## Architecture

`docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

## Objective

Build the protected Admin support experience strictly on top of accepted server capabilities, without reimplementing translation, ownership or recovery logic in the UI.

## Context

Backend behavior is deliberately complete before UI work so a Luna UI task is mostly deterministic presentation/integration.

### Attempt 2 Architect Correction Contract

Attempt 1 is retained as the starting point. Do **not** rewrite the Merchant Messages UI. Independent architect review plus manual UI validation found four bounded acceptance gaps. Attempt 2 must correct only these gaps and then return this same task to `review`.

#### Correction 1 — Use the Shared grapheme counter exactly

Current code validates with Shared `AuthoredSupportBodySchema` but calculates the visible counter with a repository-local `countGraphemes()` implementation using `Intl.Segmenter`. This duplicates a Shared contract that already exports `countUnicodeGraphemes`.

Required correction:

```ts
import {
  AuthoredSupportBodySchema,
  countUnicodeGraphemes,
} from '@modainteract/moda-interact-shared/merchant-communications';
```

and:

```ts
const count = countUnicodeGraphemes(body);
```

Delete the local `countGraphemes()` helper entirely. Do not create another local grapheme helper or fallback. The client counter and the validation schema must consume the same published Shared contract.

#### Correction 2 — Make persisted read state visible and first-render accurate

Attempt 1 marks unread `MERCHANT` messages as read in `getMerchantSupportThread()`, but the message rows are selected **before** that update and the UI does not render `readAt` at all. The task acceptance criterion that read state is distinct is therefore not satisfied.

Required server/read correction:

1. Keep the existing first-read rule: only `MERCHANT` messages in the selected thread with `readAt IS NULL` are marked read.
2. Preserve first-read stability: repeated reads must not change an existing `readAt`.
3. Reading must not change `needsAdminResponse`.
4. Perform the read-mark update before loading the message rows returned to this page, so the first rendered result contains the persisted post-read state.
5. Do not add a new database field, schema change, queue event or background action.

Required UI presentation:

- `MERCHANT` message: show `Read by support` when `readAt` is non-null, otherwise `Unread by support`.
- `ADMINISTRATIVE` or `SYSTEM` message: show `Read by merchant` when `readAt` is non-null, otherwise `Unread by merchant`.
- Keep message kind and PROCESSING/AVAILABLE/FAILED state visually separate from read state.

#### Correction 3 — Expose all bounded translation views, not only the newest translation row

Attempt 1 uses one `LEFT JOIN LATERAL ... ORDER BY createdAt DESC LIMIT 1` translation row per message. That means requesting an additional translation makes older AVAILABLE/FAILED translations inaccessible even though the task explicitly requires original content **and available translations** to be accessible.

Required read shape:

- keep the existing bounded message history (`MAX_THREAD_MESSAGES`);
- for each returned message, expose a `translations` array containing translation-safe Admin view data only:
  - `id`;
  - `targetLanguageTag`;
  - `status`;
  - `translatedBody`;
  - `createdAt`;
- do not expose provider credentials, provider request payloads, Batch internals or queue metadata;
- bound translation presentation to at most **50 translation rows per message**. This is a UI/read bound only and must not alter the database uniqueness or persistence model.

Required UI behavior:

1. Original text remains available at all times.
2. Default displayed body is the original text. Do not add client-side language-routing business rules.
3. Render one translation control/status item per returned translation, identified by its canonical `targetLanguageTag`.
4. An `AVAILABLE` translation may be selected to display its `translatedBody`.
5. A `PROCESSING`/`PENDING` translation shows status only and must not display a fallback body as if translated.
6. A `FAILED` translation exposes `Retry / Reconcile` using that exact translation row ID.
7. `View original` returns to the immutable original body.
8. The existing request-additional-translation control remains server-authoritative.

Do not collapse the translations back to a single `latestTranslation`/`translationId` field in the UI contract.

#### Correction 4 — Make the development-bypass principal durably FK-safe

Manual validation of the Attempt 1 UI exposed a real server integration defect when **Take** is used under the accepted local-development authentication bypass.

Observed database failure:

```text
SQLSTATE 23503
MerchantSupportThread_assignedPlatformAdminId_fkey
```

The exact existing state is:

```text
requirePlatformAdminMutation()
  -> development bypass principal
  -> id = "development-platform-admin"
  -> developmentBypass = true

takeMerchantSupportThreadOwnership()
  -> writes principal.id into MerchantSupportThread.assignedPlatformAdminId

MerchantSupportThread.assignedPlatformAdminId
  -> foreign key to public.PlatformAdmin.id
```

The accepted ARCH-002 development bypass is intentionally a synthetic local `SUPER_ADMIN` principal. Do **not** remove the bypass, require Google login in local development, rename the principal, weaken the foreign key, write `NULL`, or change the Prisma schema.

The defect is that ARCH-006 now persists Admin identity into FK-backed durable records, while the synthetic development principal does not yet have a corresponding local `public.PlatformAdmin` backing row.

This is not limited to **Take**. The same `principal.id` is also persisted by the current ARCH-006 server capability in:

- `MerchantSupportThread.assignedPlatformAdminId` when taking ownership;
- `MerchantSupportMessage.platformAdminId` when composing an administrative message;
- `MerchantTranslationReconciliationRequest.requestedByPlatformAdminId` for targeted reconciliation;
- `MerchantTranslationReconciliationRequest.requestedByPlatformAdminId` for global failed-translation reconciliation.

A fix that special-cases only the Take button is therefore **not accepted**.

##### Required implementation boundary

Implement one small server-side helper in `src/lib/admin/merchant-support.ts` that makes the accepted synthetic development principal durably representable **only when `principal.developmentBypass === true`**.

Use the existing fixed principal identity:

```text
id = development-platform-admin
role = SUPER_ADMIN
developmentBypass = true
```

For development bypass only, before an ARCH-006 transaction writes `principal.id` into an FK-backed column, ensure that `public.PlatformAdmin` contains a stable backing row for that exact ID. Use deterministic non-secret local identity values, for example:

```text
id              = development-platform-admin
provider        = development
providerSubject = development-platform-admin
email           = development-platform-admin@local.invalid
displayName     = Development Platform Admin
role            = SUPER_ADMIN
active          = true
```

The helper must be idempotent. It must not create a new ID on each request. It must not overwrite an unrelated existing PlatformAdmin row. A safe shape is:

```text
INSERT fixed development row
ON CONFLICT (id) DO NOTHING
        ↓
read the row with id = development-platform-admin
        ↓
verify it is the reserved development identity
        ↓
continue, or throw a clear conflict error
```

Do not use `ON CONFLICT ... DO UPDATE` to rewrite an unexpected existing identity.

For a real authenticated principal (`developmentBypass === false`), the helper must do **no insert/update**. The existing pre-provisioned `PlatformAdmin` identity remains authoritative.

##### Exact mutation coverage

Call the helper inside the same database transaction, before the first FK-backed write, in these flows:

1. `takeMerchantSupportThreadOwnership`;
2. `composeAdministrativeMessage`;
3. `requestFailedTranslationReconciliation`;
4. `requestFailedTranslationsReconciliation`.

`requestFailedTranslationsReconciliation` currently performs its insert directly. Convert only that operation to the existing callback-style `$transaction` so development-principal materialisation and reconciliation-request insertion are atomic.

Do **not** add the helper to ordinary reads. Do not add it to `requestAdditionalTranslation`, because that flow does not persist `principal.id`. Do not change `releaseMerchantSupportThreadOwnership` or SUPER_ADMIN reassignment semantics.

##### Required result

Under local development bypass:

```text
Take
  -> backing PlatformAdmin identity exists
  -> atomic assignedPlatformAdminId CAS succeeds
  -> no 23503 FK failure
  -> current admin becomes durable owner

Compose
  -> platformAdminId FK succeeds

Targeted/global reconciliation
  -> requestedByPlatformAdminId FK succeeds
```

Real authenticated test/production behavior must remain unchanged.

### Attempt 2 File Boundary

Production/test changes are permitted only in:

- `src/components/admin/merchant-support-inbox.tsx`;
- `src/lib/admin/merchant-support.ts`;
- `tests/security/admin-merchant-support-ui.test.mjs`;
- `tests/security/admin-merchant-support.test.mjs` where needed to prove the corrected read/translation behavior and development-principal FK safety using the existing test style.

Do not modify navigation, auth, actions, Prisma schema/migrations, Shared, Background, Shopify, queue-monitor, observability, package dependencies, lockfiles or locale catalogues for Attempt 2. If one of those changes appears necessary, set this task `blocked` and return the exact gap to `moda_architect`.

## Scope

Admin navigation/pages/components for pending queue, shop support history, ownership controls, compose, translation state/original view and recovery actions.

## Out of Scope

- New DB/queue/provider logic.
- Direct Redis/OpenAI access.
- Client-derived admin/shop/message kind/language routing.
- Editing/deleting sent source messages.

## Requirements

Implement:
- `Merchant Messages` navigation/landing;
- all-pending default plus ownership filters;
- bounded shop thread/history;
- SYSTEM / ADMINISTRATIVE / MERCHANT badges;
- owner/unassigned display and Take/Release; SUPER_ADMIN reassignment using accepted commands;
- compose enabled only when UI sees current admin as owner (server remains authority);
- shared 500-grapheme client counter/validation mirroring server, no silent truncation;
- PROCESSING/AVAILABLE/FAILED status;
- `View original` and available translations;
- request additional canonical translation through server capability;
- failed translation `Retry/Reconcile` action that calls durable targeted reconciliation capability;
- SUPER_ADMIN-only `Reconcile failed translations` operational action using the accepted global durable request capability;
- merchant-message first-read invocation on thread view per accepted server semantics.

Do not show English fallback to a non-English merchant outbound message; Admin may always see original administrative text and status.

## Work Items

- [x] Inspect existing Admin layout/design-system/navigation patterns.
- [x] Build pending-support landing/filter/pagination UI.
- [x] Build thread/history/status/original/translation UI.
- [x] Add owner controls and owner-gated compose UI.
- [x] Add 500-grapheme compose UX using shared contract.
- [x] Add targeted translation reconciliation action and SUPER_ADMIN-only global failed-translation reconciliation action.
- [x] Add focused component/route integration and accessibility/security rendering tests.

Attempt 2 correction:

- [x] Replace the local grapheme counter with Shared `countUnicodeGraphemes`.
- [x] Return post-first-read persisted `readAt` state and render read state distinctly.
- [x] Replace the single-latest translation read shape with bounded per-message translation views.
- [x] Render translation target/status controls and per-FAILED-translation reconciliation without client-side language-routing rules.
- [x] Materialise the synthetic development principal safely before every ARCH-006 FK-backed Admin-attribution write.
- [x] Strengthen focused tests for all four correction areas.
- [x] Run the complete task Validation and return this same task to `review`.
- [x] Cast the development principal role to the schema-qualified PostgreSQL enum and verify the bound SQL parameter.

## Interfaces / Contracts

Calls only architect-accepted ADMIN-001/ADMIN-003 server capabilities and shared presentation-safe schemas. No queue/job/provider code in components.

## Dependencies

Explicit task dependencies are listed in YAML frontmatter.

## Enables

`ARCH-006-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] All pending shops and owner state are clear and bounded.
- [x] Non-owner can read but cannot successfully send.
- [x] Ownership controls reflect server outcomes/races and Take succeeds under the accepted local development bypass without FK failure.
- [x] Compose uses the published Shared grapheme counter and schema client-side; server errors remain handled.
- [x] Message kinds, message state and persisted read state are distinct.
- [x] Original text and all bounded returned translations are accessible.
- [x] Failed translation can create an Admin reconciliation request.
- [x] No message body is treated as trusted HTML/Markdown execution.
- [x] No business translation/recovery/grapheme rules are duplicated client-side.

## Validation

Attempt 2 must run at minimum:

```bash
node --test tests/security/admin-merchant-support-ui.test.mjs
node --test tests/security/admin-merchant-support.test.mjs
npm test
npx tsc --noEmit --pretty false
npm run lint
npm run build
npm run prisma:validate
git diff --check
```

Focused regression proof must establish:

- `merchant-support-inbox.tsx` imports and uses Shared `countUnicodeGraphemes`; no local `countGraphemes` or `Intl.Segmenter` implementation remains there;
- first-read marking remains `MERCHANT`-only, `readAt IS NULL`-only and does not clear `needsAdminResponse`; returned message data reflects the persisted mark;
- read-state labels are rendered separately from kind and PROCESSING/AVAILABLE/FAILED state;
- more than one translation row for one message is represented in the returned `translations` collection;
- original body remains selectable; AVAILABLE translation bodies can be selected; FAILED translation reconciliation uses the exact failed translation ID;
- no HTML/Markdown execution path is introduced;
- the development-bypass principal is materialised with one stable reserved `PlatformAdmin` ID before FK-backed ARCH-006 Admin-attribution writes;
- repeated development requests reuse the same backing identity rather than creating duplicates;
- real authenticated principals never trigger synthetic development-row creation;
- Take, administrative compose, targeted reconciliation and global reconciliation all cover the FK-safe path;
- the regression test must fail if only Take is fixed while compose/reconciliation still persist an unbacked development principal ID.

The known pre-existing Admin internationalisation assertion expecting historical Shared `0.7.0` may remain the only full-suite failure if it is unchanged. Any new failure is task-owned.

## Implementation Notes

If server capability appears missing, return the gap to `moda_architect`; do not repair architecture inside the UI task.

## Completion Report

### Status

Ready for Review (Attempt 4).

Attempt 4 corrected the raw development `PlatformAdmin` INSERT to supply the required `"updatedAt"` value from `CURRENT_TIMESTAMP`. The existing schema-qualified enum cast and bound `SUPER_ADMIN` parameter remain unchanged.

### Files Changed

- `moda-interact-admin/src/app/(protected)/merchant-support/page.tsx`
- `moda-interact-admin/src/components/admin/merchant-support-inbox.tsx`
- `moda-interact-admin/src/components/admin/admin-shell.tsx`
- `moda-interact-admin/src/components/admin/sidebar.tsx`
- `moda-interact-admin/src/lib/admin/merchant-support.ts`
- `moda-interact-admin/src/i18n/locales/en.json`
- `moda-interact-admin/src/i18n/required-keys.ts`
- `moda-interact-admin/tests/security/admin-merchant-support-ui.test.mjs`
- `moda-interact-admin/tests/security/admin-merchant-support.test.mjs`

### Work Completed

- Added protected Merchant Messages navigation and `/merchant-support` landing route.
- Added bounded pending-thread search, ownership filters, pagination, selection, first-read detail loading, and plain-text bounded history rendering.
- Added SYSTEM/ADMINISTRATIVE/MERCHANT badges, PROCESSING/AVAILABLE/FAILED states, original/translation switching, additional translation requests, and targeted/global reconciliation controls.
- Added Take/Release/SUPER_ADMIN reassignment controls and owner-only compose with shared grapheme validation and server error handling.
- Exposed latest translation identity and target language in the accepted detail read shape.
- Added focused route and UI boundary tests.
- Corrected the development-principal INSERT to use `CAST(<bound role> AS "public"."PlatformAdminRole")`; `SUPER_ADMIN` remains a bound parameter.
- Added the required `"updatedAt"` column with database-side `CURRENT_TIMESTAMP`.

### Validation Results

- Focused support security test: passed, 13 tests; focused UI test: passed, 5 tests.
- Full `npm test`: 99 passed, 1 known pre-existing failure; `admin-internationalization.test.mjs` still expects Shared `0.7.0` while the accepted dependency is `0.7.1`.
- `npx tsc --noEmit --pretty false`: passed.
- `npm run lint`: passed with two pre-existing `queue-monitor.tsx` hook warnings.
- `npm run build`: passed; `/merchant-support` compiled as a dynamic route.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.

### Deviations

- No Attempt 4 scope deviation. No schema/migration/auth/UI change was made. The stale Shared `0.7.0` internationalization assertion remains outside the permitted file boundary and is unchanged.

### Assumptions

- Existing server capabilities remain authoritative for ownership, language routing, message kind, durable translation requests, and reconciliation.
- `getMerchantSupportThread` remains the accepted first-read invocation for merchant messages.

### Unresolved Issues

- The stale shared-package version assertion in the existing full Admin test suite remains for `moda_architect`/repository owners to reconcile separately.

### Architectural Concerns

- No new architectural concern. The development identity INSERT retains the required enum cast and now supplies `"updatedAt"` with `CURRENT_TIMESTAMP`; all four FK-backed ARCH-006 mutation paths still call the same helper. The focused regression would fail against the Attempt 3 INSERT. No commit or push was performed; architect acceptance remains pending.

### Attempt 4 Completion Report

#### Files Changed

- `moda-interact-admin/src/lib/admin/merchant-support.ts`
- `moda-interact-admin/tests/security/admin-merchant-support.test.mjs`
- this task metadata and the Admin ARCH-006 index

#### Validation Results

- Focused Admin support security test: 13 passed.
- Focused Admin support UI test: 5 passed.
- Full Admin tests: 99 passed, 1 known pre-existing failure out of 100. `admin-internationalization.test.mjs` still expects Shared `0.7.0`, while the accepted dependency is `0.7.1`.
- TypeScript check: passed.
- Lint: passed with two unchanged `queue-monitor.tsx` hook warnings.
- Production build: passed with existing Next.js workspace-root and BullMQ optional-dependency warnings.
- Prisma validation: passed.
- `git diff --check`: passed.

#### Scope Confirmation

No schema/migration, authentication, UI, Shared, Shopify, Background, Gateway, or system-test changes were made. The task is returned to `review`; architect acceptance remains pending.

### Attempt 5 Completion Report

#### Files Changed

- `moda-interact-admin/src/lib/admin/merchant-support.ts`
- `moda-interact-admin/tests/security/admin-merchant-support.test.mjs`
- this task metadata and the Admin ARCH-006 index

#### Work Completed

- Changed only the compose transaction lock from bare `FOR UPDATE` to `FOR UPDATE OF t`.
- Preserved the optional `LEFT JOIN "shopify"."ShopSettings"`, owner recheck, and stable `merchantMessageVersion` semantics.
- Extended the executed `Prisma.Sql` regression to assert the optional join, relation-qualified lock, and rejection of the bare lock form.
- Preserved the enum cast, bound `SUPER_ADMIN`, `updatedAt = CURRENT_TIMESTAMP`, and shared helper across all four FK-backed mutation paths.

#### Validation Results

- Focused Admin support security test: 13 passed.
- Focused Admin support UI test: 5 passed.
- Full Admin tests: 99 passed, 1 known pre-existing failure out of 100. `admin-internationalization.test.mjs` still expects Shared `0.7.0`, while the accepted dependency is `0.7.1`.
- TypeScript check: passed.
- Lint: passed with two unchanged `queue-monitor.tsx` hook warnings.
- Production build: passed with existing Next.js workspace-root and BullMQ optional-dependency warnings.
- Prisma validation: passed.
- `git diff --check`: passed.

#### Scope Confirmation

No schema/migration, authentication, UI, Shared, Shopify, Background, Gateway, or system-test changes were made. No commit or push was performed. The task is returned to `review`; architect acceptance remains pending.

### Attempt 6 Completion Report

#### Work Completed

- Cast the bound compose `state` value to `"support"."MerchantSupportMessageState"` for both English `AVAILABLE` and non-English `PROCESSING` messages.
- Cast the bound additional-translation `direction` value to `"support"."MerchantTranslationDirection"` while preserving the existing deterministic mapping and queue behavior.
- Added generated-`Prisma.Sql` regressions for both INSERT statements, including target table, schema-qualified enum cast, and preserved bound values.
- Inspected the service's dynamic enum-bound raw writes. The existing `PlatformAdminRole` cast remains intact; SQL enum literals were not mechanically rewritten, and no additional dynamic enum binding was found.

#### Validation Results

- Focused Admin support security test: 13 passed.
- Focused Admin support UI test: 5 passed.
- Full Admin tests: 99 passed, 1 known unchanged failure out of 100. `admin-internationalization.test.mjs` still expects Shared `0.7.0`, while the accepted dependency is `0.7.1`.
- TypeScript check: passed.
- Lint: passed with the two unchanged `queue-monitor.tsx` hook warnings.
- Production build: passed with existing Next.js workspace-root and BullMQ optional-dependency warnings.
- Prisma validation: passed.
- `git diff --check`: passed.

#### Scope Confirmation

`FOR UPDATE OF t`, the `PlatformAdminRole` cast, and development `updatedAt = CURRENT_TIMESTAMP` remain intact. No schema, migration, authentication or UI changes were made. The new generated-SQL regressions fail against the prior uncast Attempt 5 forms. No commit or push was performed; architect acceptance remains pending.

### Attempt 2 Completion Report

#### Work Completed

- Replaced the local UI grapheme counter with Shared `countUnicodeGraphemes`.
- Made merchant first-read marking `MERCHANT`/unread-only, idempotent, `needsAdminResponse`-preserving, and transactional with the returned message read.
- Replaced the latest-only translation projection with up to 50 translation-safe rows per message and exposed original/AVAILABLE/PENDING/PROCESSING/FAILED controls in the UI.
- Added distinct persisted read-state labels and exact failed translation-row reconciliation actions.
- Added idempotent development-bypass `PlatformAdmin` materialisation with reserved-identity conflict verification before Take, compose, targeted reconciliation, and global reconciliation writes.
- Converted global reconciliation insertion to the callback transaction boundary.
- Added focused regression assertions for all correction areas and updated transaction fixtures.

#### Files Changed in Attempt 2

- `moda-interact-admin/src/components/admin/merchant-support-inbox.tsx`
- `moda-interact-admin/src/lib/admin/merchant-support.ts`
- `moda-interact-admin/tests/security/admin-merchant-support-ui.test.mjs`
- `moda-interact-admin/tests/security/admin-merchant-support.test.mjs`

#### Validation Results

- Focused UI/server tests: 17 passed.
- `npm test`: 98 passed, 1 pre-existing failure; `admin-internationalization.test.mjs` still expects Shared `0.7.0` while the accepted dependency is `0.7.1`.
- `npx tsc --noEmit --pretty false`: passed.
- `npm run lint`: passed with two pre-existing `queue-monitor.tsx` hook warnings.
- `npm run build`: passed with existing Next.js workspace-root and BullMQ optional-dependency warnings.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.

#### Deviations and Unresolved Issues

- No Attempt 2 scope deviation. The stale Shared `0.7.0` internationalization assertion remains outside the permitted file boundary and is unchanged.

## Architect Review

### Attempt 1 — 2026-09-06

### Review Status

Not accepted — returned to Ready for bounded Attempt 2 correction.

### Independent Findings

1. **Shared grapheme contract is duplicated in the UI.** `merchant-support-inbox.tsx` imports Shared `AuthoredSupportBodySchema` but implements its own `countGraphemes()` using `Intl.Segmenter`. Shared `merchant-communications` already exports `countUnicodeGraphemes`; the task explicitly requires the shared 500-grapheme client counter/validation contract.

2. **Read state is not actually presented.** `readAt` is returned by the server shape but is never rendered, so the checked acceptance criterion that message kind/status/read state are distinct is not satisfied. In addition, the first-read update currently occurs after the message SELECT, so the first render receives the pre-mark value.

3. **Translation presentation is lossy.** `getMerchantSupportThread()` exposes only the newest translation row through a LATERAL `LIMIT 1`. Once multiple canonical translations exist, older AVAILABLE or FAILED translations cannot be viewed or reconciled from the UI. That does not satisfy `View original and available translations`.

4. **Focused UI proof does not cover the presentation gaps above.** The current source-boundary test confirms imports/actions/plain-text rendering/SUPER_ADMIN gating but does not assert Shared counter reuse, read-state presentation or multi-translation accessibility.

5. **Manual Take fails under the accepted development-auth bypass because the synthetic principal is not FK-backed.** `requirePlatformAdminMutation()` returns the fixed local principal `development-platform-admin`, while `MerchantSupportThread.assignedPlatformAdminId` references `public.PlatformAdmin(id)`. The Take command writes that synthetic ID directly and PostgreSQL correctly rejects it with SQLSTATE `23503`. The same latent mismatch exists in administrative-message and reconciliation-request attribution writes, so Attempt 2 must correct the shared ARCH-006 mutation boundary rather than patching only Take.

The remaining Attempt 1 implementation is retained. Navigation, ownership controls, server-authoritative compose, plain-text rendering, reconciliation commands and the reported repository validation do not require rewrite. The known full-suite historical Shared `0.7.0` assertion remains out of scope.

Attempt remains `1` until the Admin repository agent claims this returned Ready task. The claim must set `status: in_progress`, set the executor/claim timestamp and increment `attempt` to `2`. The agent must implement only the correction contract above, return `ARCH-006-ADMIN-004` to `review`, and STOP. Do not claim or implement `ADMIN-005` in the same invocation.


### Architect Review — Attempt 2 — 2026-09-06

**Review Status: Not accepted — return to Ready for one bounded Attempt 3 correction.**

Attempt 2 correctly implemented the Shared grapheme counter, post-read state, bounded translation presentation, and the development-bypass backing-identity concept. Manual validation nevertheless exposed one concrete PostgreSQL type error in the backing-identity INSERT.

#### Blocking defect — development `PlatformAdmin.role` is bound as PostgreSQL `text`

Observed runtime failure when clicking **Take** under the accepted development authentication bypass:

```text
SQLSTATE 42804
column "role" is of type "PlatformAdminRole" but expression is of type text
HINT: You will need to rewrite or cast the expression.
```

The current helper contains this shape:

```ts
INSERT INTO "public"."PlatformAdmin" (..., "role", ...)
VALUES (..., ${DEVELOPMENT_PLATFORM_ADMIN.role}, ...)
```

`DEVELOPMENT_PLATFORM_ADMIN.role` is the JavaScript string `SUPER_ADMIN`. Prisma parameterises it as a text bind parameter. PostgreSQL does not implicitly coerce that text parameter to the schema-qualified enum column type `"public"."PlatformAdminRole"` in this raw INSERT, so the helper fails before the backing development administrator can be materialised. The subsequent ownership UPDATE is therefore never reached.

This is why the source/mocked tests passed while live PostgreSQL failed: the current test doubles count `$executeRaw` calls but do not execute the generated SQL against PostgreSQL or assert the enum cast in the generated SQL.

All other Attempt 2 corrections are retained. Do not rewrite the Merchant Messages UI.

### Attempt 3 — Exact Correction Contract

Attempt 3 is intentionally tiny for GPT-5.6 Luna. Modify only the development-principal enum binding and its focused regression proof.

#### Permitted files

Production/test changes are permitted only in:

- `moda-interact-admin/src/lib/admin/merchant-support.ts`
- `moda-interact-admin/tests/security/admin-merchant-support.test.mjs`
- this task file and `docs/decisions/admin/ARCH-006/_index.md` as required by the normal task protocol.

Do **not** modify:

- `merchant-support-inbox.tsx`;
- Admin navigation/routes/actions;
- authentication helpers or the accepted development-bypass principal;
- Prisma schema or migrations;
- Shared, Shopify, Background, Gateway or system-test code;
- package versions or lockfiles;
- translation/read-state/grapheme behavior already accepted from Attempt 2.

If a change outside the permitted files appears necessary, stop and return the task `blocked` to `moda_architect` with the exact reason.

#### Required production edit

In `ensureDevelopmentPlatformAdmin()`, preserve the fixed development identity exactly as it is now. Change only how the `role` value is inserted into PostgreSQL.

The `role` bind parameter **must be explicitly cast to the actual schema-qualified PostgreSQL enum type**:

```ts
CAST(${DEVELOPMENT_PLATFORM_ADMIN.role} AS "public"."PlatformAdminRole")
```

The resulting INSERT must have this semantic shape:

```sql
INSERT INTO "public"."PlatformAdmin" (
  "id", "provider", "providerSubject", "email", "displayName", "role", "active"
) VALUES (
  <fixed id>,
  <development provider>,
  <fixed provider subject>,
  <fixed local email>,
  <fixed display name>,
  CAST(<bound SUPER_ADMIN value> AS "public"."PlatformAdminRole"),
  true
)
ON CONFLICT ("id") DO NOTHING
```

Do not use `Prisma.raw()` or string concatenation to inject the role. Keep the role as a normal bound value and cast that bound value.

Do not hardcode or change the database enum definition. Do not change `PlatformAdminRole`, do not weaken the foreign key, and do not replace the backing identity with `NULL`.

#### Required behavior after correction

Under local development bypass:

```text
Take
  -> ensureDevelopmentPlatformAdmin()
  -> INSERT fixed development admin with enum-safe role cast
  -> verify reserved backing identity
  -> UPDATE MerchantSupportThread.assignedPlatformAdminId
  -> success; no SQLSTATE 42804 and no SQLSTATE 23503
```

Because the same helper is already called by all four accepted FK-backed mutation paths, the corrected helper must also leave these paths valid without additional special cases:

- administrative compose;
- targeted failed-translation reconciliation;
- global failed-translation reconciliation.

Real authenticated principals (`developmentBypass === false`) must still perform no synthetic identity write.

#### Deterministic regression requirement

The current mocked tests are insufficient because `$executeRaw` always returns success without examining PostgreSQL typing. Add a focused test that captures the **actual `Prisma.Sql` object passed to the helper's development-identity INSERT** and proves both:

1. the SQL template contains an explicit cast to the exact type:

   ```text
   CAST(... AS "public"."PlatformAdminRole")
   ```

2. the bound values still contain `SUPER_ADMIN` as a parameter rather than interpolating it with unsafe raw SQL/string concatenation.

The regression must fail against the current Attempt 2 implementation where the role is just an uncast text parameter.

Keep the existing regression that proves the helper is invoked in exactly the four accepted FK-backed mutation paths. Do not replace behavioral coverage with only a source substring assertion if the intercepted `Prisma.Sql` query can be inspected using the existing test style.

If the repository test environment has an explicitly configured disposable PostgreSQL test database, an additional focused live execution is welcome, but **do not invent or require a new database harness in this bounded task**. The generated-SQL regression is mandatory regardless.

#### Validation

Run at minimum:

```bash
node --test tests/security/admin-merchant-support.test.mjs
node --test tests/security/admin-merchant-support-ui.test.mjs
npm test
npx tsc --noEmit --pretty false
npm run lint
npm run build
npm run prisma:validate
git diff --check
```

The known pre-existing Admin internationalisation assertion expecting Shared `0.7.0` may remain the only full-suite failure if unchanged. Any new failure is task-owned.

Before returning to review, inspect the final diff and explicitly state that:

- the development identity INSERT contains the enum cast;
- no schema/migration/auth/UI change was made;
- all four FK-backed paths still call the same helper;
- the focused regression would fail on the uncast Attempt 2 SQL.

Return this same task to `review` and STOP. Do not claim `ADMIN-005` or any system-test task in the same invocation.


### Architect Review — Attempt 3 — 2026-09-06

**Review Status: Not accepted — return to Ready for one bounded Attempt 4 correction.**

Attempt 3 correctly fixed the PostgreSQL enum typing defect by keeping `SUPER_ADMIN` as a bound parameter and explicitly casting it to `"public"."PlatformAdminRole"`. Manual PostgreSQL validation nevertheless exposed one further schema-level defect in the same development-principal materialisation INSERT.

#### Blocking defect — raw INSERT omits required `PlatformAdmin.updatedAt`

Observed runtime failure when clicking **Take** under the accepted development authentication bypass:

```text
SQLSTATE 23502
not-null violation while inserting public.PlatformAdmin
```

The failing row shown by PostgreSQL has the final values:

```text
..., active=true, lastLoginAt=null, createdAt=<timestamp>, updatedAt=null
```

The database schema is authoritative:

```prisma
model PlatformAdmin {
  id              String            @id @default(cuid())
  provider        String            @default("google")
  providerSubject String?
  email           String            @unique
  displayName     String?
  role            PlatformAdminRole @default(ADMIN)
  active          Boolean           @default(true)
  lastLoginAt     DateTime?
  createdAt       DateTime          @default(now())
  updatedAt       DateTime          @updatedAt
}
```

and the migration creates:

```sql
"lastLoginAt" TIMESTAMP(3),
"createdAt"   TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
"updatedAt"   TIMESTAMP(3) NOT NULL
```

`@updatedAt` is Prisma Client behavior. It does **not** create a PostgreSQL default for raw SQL. Therefore a raw `INSERT` that omits `"updatedAt"` attempts to store `NULL` and PostgreSQL correctly rejects it with SQLSTATE `23502`.

This is why the mocked `$executeRaw()` tests passed while the live PostgreSQL operation failed.

All previously accepted Attempt 2 behavior and the Attempt 3 enum cast must remain unchanged.

### Attempt 4 — Exact Correction Contract

Attempt 4 is intentionally tiny for GPT-5.6 Luna. Correct only the schema-invalid development identity INSERT and add a regression that proves the raw SQL supplies the required timestamp.

#### Permitted files

Production/test changes are permitted only in:

- `moda-interact-admin/src/lib/admin/merchant-support.ts`
- `moda-interact-admin/tests/security/admin-merchant-support.test.mjs`
- this task file and `docs/decisions/admin/ARCH-006/_index.md` for normal task bookkeeping.

Do **not** modify:

- `src/components/admin/merchant-support-inbox.tsx`;
- Admin routes/actions/navigation;
- authentication or the development-bypass principal;
- Prisma schema or migrations;
- Shared, Shopify, Background, Gateway or system-test code;
- package versions or lockfiles;
- read-state, translation, grapheme, ownership, compose or reconciliation semantics;
- the explicit `"public"."PlatformAdminRole"` cast added in Attempt 3.

If a change outside the permitted files appears necessary, stop and return the task `blocked` to `moda_architect` with the exact reason.

#### Required production edit

Inspect the authoritative `PlatformAdmin` schema before changing the query.

The existing raw INSERT currently supplies:

```text
id
provider
providerSubject
email
displayName
role
active
```

Schema reconciliation must recognize:

```text
lastLoginAt -> nullable, may be omitted
createdAt   -> NOT NULL but has PostgreSQL DEFAULT CURRENT_TIMESTAMP, may be omitted
updatedAt   -> NOT NULL and has NO PostgreSQL default, MUST be supplied by raw SQL
```

Modify only the development backing-row INSERT so `"updatedAt"` is explicitly inserted using the database clock.

Required semantic shape:

```sql
INSERT INTO "public"."PlatformAdmin" (
  "id",
  "provider",
  "providerSubject",
  "email",
  "displayName",
  "role",
  "active",
  "updatedAt"
) VALUES (
  <fixed development id>,
  <development provider>,
  <fixed provider subject>,
  <fixed local email>,
  <fixed display name>,
  CAST(<bound SUPER_ADMIN> AS "public"."PlatformAdminRole"),
  true,
  CURRENT_TIMESTAMP
)
ON CONFLICT ("id") DO NOTHING
```

The expected source-level correction is equivalent to:

```ts
await transaction.$executeRaw(Prisma.sql`
  INSERT INTO "public"."PlatformAdmin" (
    "id", "provider", "providerSubject", "email", "displayName", "role", "active", "updatedAt"
  ) VALUES (
    ${DEVELOPMENT_PLATFORM_ADMIN.id},
    ${DEVELOPMENT_PLATFORM_ADMIN.provider},
    ${DEVELOPMENT_PLATFORM_ADMIN.providerSubject},
    ${DEVELOPMENT_PLATFORM_ADMIN.email},
    ${DEVELOPMENT_PLATFORM_ADMIN.displayName},
    CAST(${DEVELOPMENT_PLATFORM_ADMIN.role} AS "public"."PlatformAdminRole"),
    ${DEVELOPMENT_PLATFORM_ADMIN.active},
    CURRENT_TIMESTAMP
  )
  ON CONFLICT ("id") DO NOTHING
`);
```

Minor formatting differences are allowed. The semantics are not.

Do **not**:

- add a schema default or migration;
- use JavaScript `new Date()` when `CURRENT_TIMESTAMP` can provide the database timestamp;
- change `createdAt`;
- update an existing reserved row on conflict;
- replace `ON CONFLICT ("id") DO NOTHING`;
- remove the post-insert reserved-identity verification;
- remove or change the enum cast;
- use unsafe string concatenation or `Prisma.raw()` for values.

#### Required runtime result

For the first local-development ownership mutation:

```text
Take
  -> ensureDevelopmentPlatformAdmin()
  -> raw INSERT satisfies every PlatformAdmin NOT NULL/no-default requirement
  -> fixed development backing row is created
  -> reserved identity is verified
  -> MerchantSupportThread.assignedPlatformAdminId CAS executes
  -> ownership succeeds
```

The same helper remains shared by the four existing FK-backed paths:

1. Take ownership;
2. administrative compose;
3. targeted failed-translation reconciliation;
4. global failed-translation reconciliation.

Do not add four separate fixes.

#### Deterministic regression requirement

The existing Attempt 3 regression already proves:

```text
SUPER_ADMIN remains a bound parameter
+
CAST(... AS "public"."PlatformAdminRole") exists
```

Preserve that regression.

Extend the captured `Prisma.Sql` regression so it additionally proves the development identity INSERT contains both:

```text
"updatedAt"
```

and:

```text
CURRENT_TIMESTAMP
```

The test must fail against Attempt 3, where the INSERT omits `"updatedAt"`.

Do not satisfy this by checking an unrelated query or merely checking the Prisma schema. The assertion must inspect the actual `Prisma.Sql` object passed to `$executeRaw()` for the development identity INSERT.

Also keep the existing test proving the helper is used by all four FK-backed mutation paths.

#### Validation

Run at minimum:

```bash
node --test tests/security/admin-merchant-support.test.mjs
node --test tests/security/admin-merchant-support-ui.test.mjs
npm test
npx tsc --noEmit --pretty false
npm run lint
npm run build
npm run prisma:validate
git diff --check
```

The known historical Shared `0.7.0` assertion may remain the only unchanged full-suite failure. Any new failure is task-owned.

Before returning to review, inspect the final diff and explicitly report:

- the enum cast is still present;
- `"updatedAt"` is explicitly supplied with `CURRENT_TIMESTAMP`;
- no schema/migration/auth/UI change was made;
- all four FK-backed mutation paths still use the same helper;
- the focused SQL regression would fail on the Attempt 3 INSERT.

Return this same task to `review` and STOP. Do not claim `ADMIN-005` or any system-test task in the same invocation.


### Architect Review — Attempt 4 — 2026-09-06

**Review Status: Not accepted — return to Ready for one bounded Attempt 5 correction.**

Attempt 4 correctly repaired development `PlatformAdmin` materialisation by supplying
the required raw-SQL `"updatedAt"` value with `CURRENT_TIMESTAMP`. Manual integrated
validation now confirms that **Take succeeds and durable ownership is established**.

The next acceptance path, **Compose administrative reply**, fails before the message
insert with PostgreSQL SQLSTATE `0A000`:

```text
ERROR: FOR UPDATE cannot be applied to the nullable side of an outer join
```

This is a separate SQL correctness defect in the existing compose transaction.

#### Exact root cause

`composeAdministrativeMessage()` currently loads and locks the selected support thread
with this semantic query:

```sql
SELECT
  t."shopId",
  t."assignedPlatformAdminId",
  t."merchantMessageVersion",
  ss."defaultLanguageTag"
FROM "support"."MerchantSupportThread" t
LEFT JOIN "shopify"."ShopSettings" ss
  ON ss."shopId" = t."shopId"
WHERE t."id" = <thread id>
FOR UPDATE
```

The `LEFT JOIN` is required because a shop may have no `ShopSettings` row and
`defaultLanguageTag` is therefore nullable.

In PostgreSQL, an unqualified/bare:

```sql
FOR UPDATE
```

applies the row-lock request to all lockable relations participating in the query.
Here `ss` is the nullable side of a `LEFT JOIN`. PostgreSQL cannot row-lock a row that
may represent the synthetic NULL side of that outer join, so the statement is rejected
with SQLSTATE `0A000`.

The concurrency requirement is **not** to lock `ShopSettings`. The transaction must
serialize the authoritative `MerchantSupportThread` row so that, immediately before
the administrative message is persisted, the transaction rechecks:

- current owner (`assignedPlatformAdminId`);
- current merchant version (`merchantMessageVersion`).

Therefore the smallest correct PostgreSQL statement is:

```sql
FOR UPDATE OF t
```

which locks only the `MerchantSupportThread` row while retaining the optional
`ShopSettings` lookup in the same statement.

Do not remove the thread lock.

All previously accepted Attempt 2, Attempt 3 and Attempt 4 corrections must remain
unchanged.

### Attempt 5 — Exact Correction Contract

Attempt 5 is intentionally tiny for GPT-5.6 Luna. Correct only the invalid compose
row-lock clause and add a deterministic regression for the generated SQL.

#### Permitted files

Production/test changes are permitted only in:

- `moda-interact-admin/src/lib/admin/merchant-support.ts`
- `moda-interact-admin/tests/security/admin-merchant-support.test.mjs`
- this task file and `docs/decisions/admin/ARCH-006/_index.md` for normal task bookkeeping.

Do **not** modify:

- `src/components/admin/merchant-support-inbox.tsx`;
- Admin routes/actions/navigation;
- authentication or development-principal materialisation;
- Prisma schema or migrations;
- package files or lockfiles;
- Shared, Shopify, Background, Gateway or system-test code;
- read-state behavior;
- translation presentation or reconciliation behavior;
- ownership semantics;
- grapheme counting;
- the Attempt 3 `PlatformAdminRole` cast;
- the Attempt 4 `PlatformAdmin.updatedAt = CURRENT_TIMESTAMP` raw INSERT correction.

If a change outside the permitted files appears necessary, stop and return the task
`blocked` to `moda_architect` with the exact reason.

#### Required production edit

In `composeAdministrativeMessage()`, change only the locking clause of the existing
thread/settings query.

Current invalid form:

```sql
WHERE t."id" = ${input.threadId}
FOR UPDATE
```

Required form:

```sql
WHERE t."id" = ${input.threadId}
FOR UPDATE OF t
```

Equivalent TypeScript target:

```ts
const rows = await transaction.$queryRaw<...>(Prisma.sql`
  SELECT t."shopId", t."assignedPlatformAdminId", t."merchantMessageVersion",
    ss."defaultLanguageTag"
  FROM "support"."MerchantSupportThread" t
  LEFT JOIN "shopify"."ShopSettings" ss ON ss."shopId" = t."shopId"
  WHERE t."id" = ${input.threadId}
  FOR UPDATE OF t
`);
```

Minor formatting differences are allowed. The SQL semantics are not.

#### Required locking semantics

The corrected query must preserve all of these properties:

```text
MerchantSupportThread t
        ↓
selected by exact thread id
        ↓
FOR UPDATE OF t
        ↓
thread row is locked for the compose transaction
        ↓
current owner is rechecked
        ↓
merchantMessageVersion used by this administrative response is stable
        ↓
message / optional translation / thread state commit atomically
```

`ShopSettings ss` remains a normal optional read. It is **not** row-locked.

Do **not** solve this by:

- deleting `FOR UPDATE`;
- changing the `LEFT JOIN` to `INNER JOIN`;
- adding a mandatory `ShopSettings` row;
- using bare `FOR UPDATE` again;
- using `FOR UPDATE OF ss`;
- using `FOR UPDATE OF t, ss`;
- splitting or moving message writes outside the existing transaction;
- weakening or deleting the owner recheck;
- changing translation-language selection;
- changing the database schema.

The absence of `ShopSettings` must continue to be legal.

#### Deterministic regression requirement

Extend the existing focused security test using its current generated-`Prisma.Sql`
inspection style.

The test must inspect the **actual `Prisma.Sql` object passed to `$queryRaw()` by
`composeAdministrativeMessage()` for the thread/settings read** and prove:

```text
LEFT JOIN "shopify"."ShopSettings" ss
```

is still present, and:

```text
FOR UPDATE OF t
```

is present.

It must also prove the invalid form does not regress. Do not use a weak substring
assertion where `FOR UPDATE` would also match `FOR UPDATE OF t`.

A deterministic assertion may normalize whitespace and then assert, for example:

```text
contains:  FOR UPDATE OF t
not match: /FOR UPDATE(?!\s+OF\s+t)/
```

or an equivalently precise assertion.

The regression must fail against Attempt 4, whose compose query ends in bare
`FOR UPDATE`.

Do not satisfy this requirement by testing only source text unrelated to the executed
query. Capture/inspect the generated `Prisma.Sql` supplied to the mocked `$queryRaw()`
during the compose flow.

Preserve the existing focused regressions for:

- Shared authored-body/grapheme behavior;
- owner recheck;
- English/non-English compose transaction behavior;
- development identity materialisation;
- enum cast;
- required `updatedAt` timestamp;
- all four FK-backed development-principal mutation paths.

#### Validation

Run at minimum:

```bash
node --test tests/security/admin-merchant-support.test.mjs
node --test tests/security/admin-merchant-support-ui.test.mjs
npm test
npx tsc --noEmit --pretty false
npm run lint
npm run build
npm run prisma:validate
git diff --check
```

The known historical Shared `0.7.0` assertion may remain the only unchanged full-suite
failure. The two known unchanged `queue-monitor.tsx` lint warnings may remain if they
are still exactly the documented baseline. Any new failure or warning in a touched
file is task-owned.

Before returning to review, inspect the final diff and explicitly report:

- compose uses `FOR UPDATE OF t`;
- the `LEFT JOIN ShopSettings` remains intact;
- the owner recheck and `merchantMessageVersion` semantics remain intact;
- Attempt 3 enum-cast correction remains intact;
- Attempt 4 `updatedAt/CURRENT_TIMESTAMP` correction remains intact;
- no schema, migration, auth or UI change was made;
- the new SQL regression would fail against Attempt 4.

Return this same task to `review` and STOP. Do not claim `ADMIN-005` or any system-test
task in the same invocation.


### Architect Review — Attempt 5 — 2026-09-06

**Review Status: Not accepted — return to Ready for one bounded Attempt 6 correction.**

Attempt 5 correctly changed the compose thread/settings query from bare
`FOR UPDATE` to `FOR UPDATE OF t`. Manual PostgreSQL validation confirms that
the compose transaction now passes the outer-join locking boundary.

The next statement fails when inserting the administrative message with
PostgreSQL SQLSTATE `42804`:

```text
ERROR: column "state" is of type support."MerchantSupportMessageState"
but expression is of type text
HINT: You will need to rewrite or cast the expression.
```

This is a raw-SQL/PostgreSQL-enum typing defect.

#### Exact root cause

`composeAdministrativeMessage()` computes:

```ts
const state = needsTranslation ? 'PROCESSING' : 'AVAILABLE';
```

and then binds that JavaScript string directly into the enum-backed column:

```sql
INSERT INTO "support"."MerchantSupportMessage" (..., "state", ...)
VALUES (..., ${state}, ...)
```

`Prisma.sql` parameterises `${state}` as PostgreSQL `text`. The authoritative
ARCH-006 database schema defines:

```prisma
enum MerchantSupportMessageState {
  PROCESSING
  AVAILABLE
  FAILED

  @@schema("support")
}

model MerchantSupportMessage {
  ...
  state MerchantSupportMessageState
  ...
}
```

Therefore the bound value must be explicitly cast to:

```sql
"support"."MerchantSupportMessageState"
```

#### Same demonstrated defect class — second remaining dynamic enum binding

`moda_architect` audited every `$executeRaw(Prisma.sql\`...\`)` statement in
`src/lib/admin/merchant-support.ts` against the ARCH-006 database schema so
Attempt 6 does not repair only the button path that happened to be manually
exercised.

There is exactly one other remaining dynamic JavaScript value in this service
that is bound directly into a PostgreSQL enum column:

```ts
const direction = directionByKind[message.kind ...];

...

INSERT INTO "support"."MerchantMessageTranslation" (..., "direction", ...)
VALUES (..., ${direction}, ...)
```

The authoritative database schema defines:

```prisma
enum MerchantTranslationDirection {
  MERCHANT_TO_ADMIN
  ADMIN_TO_MERCHANT
  SYSTEM_TO_MERCHANT

  @@schema("support")
}

model MerchantMessageTranslation {
  ...
  direction MerchantTranslationDirection
  ...
}
```

Therefore `${direction}` has the same demonstrated `text -> enum` defect and
must be explicitly cast to:

```sql
"support"."MerchantTranslationDirection"
```

This second correction is not speculative feature work. It is the same
confirmed raw-SQL enum-binding defect class, in the same service, identified by
a complete inspection of the remaining dynamic enum-bound parameters.

Do not broaden this into a general rewrite of raw SQL.

### Attempt 6 — Exact Correction Contract

Attempt 6 is intentionally narrow and explicit for GPT-5.6 Luna.

Correct exactly these two dynamic enum bindings and add deterministic
generated-SQL regressions. Preserve all accepted Attempt 2–5 behavior.

#### Permitted files

Production/test changes are permitted only in:

- `moda-interact-admin/src/lib/admin/merchant-support.ts`
- `moda-interact-admin/tests/security/admin-merchant-support.test.mjs`
- this task file and `docs/decisions/admin/ARCH-006/_index.md` for normal task bookkeeping.

Do **not** modify:

- `src/components/admin/merchant-support-inbox.tsx`;
- Admin routes/actions/navigation;
- authentication or development-principal materialisation;
- Prisma schema or migrations;
- package files or lockfiles;
- Shared, Shopify, Background, Gateway or system-test code;
- read-state behavior;
- translation presentation/reconciliation semantics;
- ownership semantics;
- grapheme counting;
- Attempt 3 `PlatformAdminRole` cast;
- Attempt 4 `PlatformAdmin.updatedAt = CURRENT_TIMESTAMP`;
- Attempt 5 `FOR UPDATE OF t`.

If a change outside the permitted files appears necessary, stop and return the
task `blocked` to `moda_architect` with the exact reason.

---

## Correction A — compose message state enum

In `composeAdministrativeMessage()`, preserve:

```ts
const state = needsTranslation ? 'PROCESSING' : 'AVAILABLE';
```

Do not create separate SQL branches for English and translated messages.

Current invalid semantic form:

```ts
${messageId}, ${input.threadId}, 'ADMINISTRATIVE', ${state}, ${body},
```

Required semantic form:

```ts
${messageId},
${input.threadId},
'ADMINISTRATIVE',
CAST(${state} AS "support"."MerchantSupportMessageState"),
${body},
```

Equivalent SQL requirement:

```sql
CAST(<bound state> AS "support"."MerchantSupportMessageState")
```

The value must remain a bound parameter. Do not use `Prisma.raw(state)`, string
concatenation, interpolation into SQL text, or an allowlisted raw SQL fragment.

Required runtime behavior:

```text
default merchant language English
  -> state = AVAILABLE
  -> bound parameter
  -> cast to support.MerchantSupportMessageState
  -> INSERT succeeds

non-English merchant language
  -> state = PROCESSING
  -> bound parameter
  -> same enum cast
  -> INSERT succeeds
  -> existing translation workflow continues unchanged
```

Do not cast the message `kind` literal merely for consistency. The existing SQL
literal `'ADMINISTRATIVE'` is not the demonstrated failing bound-parameter
case and should remain unchanged.

---

## Correction B — additional-translation direction enum

In `requestAdditionalTranslation()`, preserve the existing deterministic
direction mapping:

```ts
const directionByKind = {
  MERCHANT: 'MERCHANT_TO_ADMIN',
  ADMINISTRATIVE: 'ADMIN_TO_MERCHANT',
  SYSTEM: 'SYSTEM_TO_MERCHANT',
} as const;
```

Current invalid semantic form:

```ts
${randomUUID()}, ${input.messageId}, ${direction},
```

Required semantic form:

```ts
${randomUUID()},
${input.messageId},
CAST(${direction} AS "support"."MerchantTranslationDirection"),
```

Equivalent SQL requirement:

```sql
CAST(<bound direction> AS "support"."MerchantTranslationDirection")
```

The value must remain parameterised.

Do not:

- change the direction mapping;
- infer direction in the browser;
- change translation uniqueness;
- alter `ON CONFLICT ("messageId", "targetLanguageTag") DO NOTHING`;
- change queue publication behavior;
- cast the existing literal `'PENDING'` merely for consistency;
- create a new enum abstraction or shared helper.

---

## Complete enum-bound-parameter audit result for this service

Attempt 6 must record in its Completion Report that the agent inspected the
current `merchant-support.ts` raw writes and preserved the following boundary:

Already corrected / valid dynamic enum binding:

```text
PlatformAdmin.role
  -> bound SUPER_ADMIN
  -> CAST(... AS "public"."PlatformAdminRole")
```

Correct in Attempt 6:

```text
MerchantSupportMessage.state
  -> bound AVAILABLE/PROCESSING
  -> CAST(... AS "support"."MerchantSupportMessageState")

MerchantMessageTranslation.direction
  -> bound direction value
  -> CAST(... AS "support"."MerchantTranslationDirection")
```

Existing enum values expressed as SQL string literals, for example:

```text
'ADMINISTRATIVE'
'ADMIN_TO_MERCHANT'
'PENDING'
'TRANSLATION'
'FAILED_TRANSLATIONS'
```

must not be mechanically rewritten merely because they target enum columns.
The demonstrated defect is specifically bound JavaScript `text` parameters
written into PostgreSQL enum columns.

If the agent discovers another **dynamic bound parameter** in this service that
targets an enum column and is not listed above, it must stop and report the
exact query/schema evidence to `moda_architect` rather than silently broaden
scope.

---

## Deterministic regression requirements

Extend the existing focused security tests using the current generated
`Prisma.Sql` capture/inspection style.

### Regression A — compose state

Capture the actual `Prisma.Sql` passed to `$executeRaw()` for the
`MerchantSupportMessage` INSERT.

Normalize whitespace if needed.

Prove all of the following:

1. the INSERT targets `"support"."MerchantSupportMessage"`;
2. the generated SQL contains the exact enum type name:

```text
"support"."MerchantSupportMessageState"
```

3. the generated SQL contains a `CAST(... AS
   "support"."MerchantSupportMessageState")` around the parameter slot used for
   state;
4. `AVAILABLE` remains in the query's bound `values` for the English path;
5. `PROCESSING` remains in the query's bound `values` for the non-English path.

The regression must fail against Attempt 5, where `${state}` is an uncast text
parameter.

Do not satisfy this with a source-text-only assertion. Inspect the actual
`Prisma.Sql` object supplied to the mocked `$executeRaw()`.

### Regression B — additional translation direction

Exercise `requestAdditionalTranslation()` far enough to capture the actual
`Prisma.Sql` passed to `$executeRaw()` for the
`MerchantMessageTranslation` INSERT.

Prove:

1. the INSERT targets `"support"."MerchantMessageTranslation"`;
2. the generated SQL contains:

```text
"support"."MerchantTranslationDirection"
```

3. the direction parameter slot is wrapped in:

```text
CAST(... AS "support"."MerchantTranslationDirection")
```

4. the mapped direction remains a bound `values` entry rather than becoming raw
   SQL text.

At minimum exercise one deterministic mapping, e.g.:

```text
MERCHANT -> MERCHANT_TO_ADMIN
```

If the existing focused test structure already cheaply covers all three message
kinds, preserve/use that coverage; do not build a new parameterized framework
solely for this task.

The regression must fail against Attempt 5, where `${direction}` is an uncast
text parameter.

### Preserve existing focused regressions

Do not delete or weaken regression coverage for:

- Shared authored-body/grapheme validation;
- owner recheck;
- English/non-English compose transaction behavior;
- development identity materialisation;
- `PlatformAdminRole` cast and bound `SUPER_ADMIN`;
- required development `updatedAt/CURRENT_TIMESTAMP`;
- all four FK-backed development-principal mutation paths;
- `LEFT JOIN ShopSettings`;
- exact `FOR UPDATE OF t` locking.

---

## Validation

Run at minimum:

```bash
node --test tests/security/admin-merchant-support.test.mjs
node --test tests/security/admin-merchant-support-ui.test.mjs
npm test
npx tsc --noEmit --pretty false
npm run lint
npm run build
npm run prisma:validate
git diff --check
```

The known historical Shared `0.7.0` assertion may remain the only unchanged
full-suite failure. The two known unchanged `queue-monitor.tsx` lint warnings
may remain only if they are still exactly the documented baseline.

Any new failure or warning in a touched file is task-owned.

Before returning to review, inspect the final diff and explicitly report:

- `FOR UPDATE OF t` remains intact;
- `PlatformAdminRole` cast remains intact;
- development `updatedAt/CURRENT_TIMESTAMP` remains intact;
- compose `state` is still a bound parameter and is cast to
  `"support"."MerchantSupportMessageState"`;
- additional-translation `direction` is still a bound parameter and is cast to
  `"support"."MerchantTranslationDirection"`;
- English AVAILABLE and non-English PROCESSING compose semantics remain intact;
- no schema, migration, auth or UI change was made;
- both new generated-SQL regressions would fail against Attempt 5.

Return this same task to `review` and STOP.

Do not claim `ADMIN-005` or any system-test task in the same invocation.


### Architect Acceptance — Attempt 6 — 2026-09-07

**Review Status: Accepted / Complete.**

Independent `moda_architect` review accepts Attempt 6 and closes
`ARCH-006-ADMIN-004`.

#### Independent source review

The Attempt 5 -> Attempt 6 production diff is limited to the two
architect-authorised dynamic PostgreSQL enum bindings in
`src/lib/admin/merchant-support.ts`:

```text
composeAdministrativeMessage()
  bound AVAILABLE / PROCESSING
  -> CAST(... AS "support"."MerchantSupportMessageState")

requestAdditionalTranslation()
  bound MERCHANT_TO_ADMIN / ADMIN_TO_MERCHANT / SYSTEM_TO_MERCHANT
  -> CAST(... AS "support"."MerchantTranslationDirection")
```

Both values remain Prisma-bound parameters. No `Prisma.raw()`, SQL string
concatenation or browser-side enum routing was introduced.

The generated-SQL regressions inspect the actual `Prisma.Sql` objects supplied
to the mocked database boundary:

- English compose proves bound `AVAILABLE` plus the
  `"support"."MerchantSupportMessageState"` cast.
- Non-English compose proves bound `PROCESSING` through the same cast.
- Additional translation proves the generated
  `"support"."MerchantTranslationDirection"` cast and retains the mapped
  direction as a bound value.

The existing all-three-kind mapping assertions remain intact.

#### Database-schema cross-check

Architect review cross-checked the current raw-write shapes against the
ARCH-006 database schema/migration.

The dynamic enum bindings in this service are now:

```text
PlatformAdmin.role
  -> CAST(bound SUPER_ADMIN AS "public"."PlatformAdminRole")

MerchantSupportMessage.state
  -> CAST(bound state AS "support"."MerchantSupportMessageState")

MerchantMessageTranslation.direction
  -> CAST(bound direction AS "support"."MerchantTranslationDirection")
```

The remaining enum-valued writes in this service use SQL literals in a
destination-column context and do not reproduce the demonstrated bound-text
parameter defect.

The previously corrected runtime boundaries remain intact:

```text
development PlatformAdmin
  -> explicit PlatformAdminRole cast
  -> updatedAt = CURRENT_TIMESTAMP

compose thread read
  -> LEFT JOIN optional ShopSettings
  -> FOR UPDATE OF t
```

The message/translation inserts also continue to provide every required
NOT-NULL/no-default timestamp column that is written through raw SQL.

#### Scope review

Direct archive comparison against Attempt 5 shows expected changes only in:

- `moda-interact-admin/src/lib/admin/merchant-support.ts`;
- `moda-interact-admin/tests/security/admin-merchant-support.test.mjs`;
- this task record;
- `docs/decisions/admin/ARCH-006/_index.md`.

An ignored `tsconfig.tsbuildinfo` validation artifact also changed in the
archive; `.gitignore` excludes `*.tsbuildinfo`, so it is not a repository task
change.

No UI, auth, schema, migration, package, Shared, Shopify, Background, Gateway
or system-test implementation was changed.

#### Validation evidence

The repository agent reports:

- focused Admin support security tests: passed;
- focused Admin support UI tests: passed;
- TypeScript: passed;
- build: passed;
- Prisma validation: passed;
- `git diff --check`: passed;
- full suite: 99 passed, 1 unchanged historical Shared `0.7.0` assertion
  failure;
- lint: only the two unchanged `queue-monitor.tsx` warnings.

The supplied review archive contains no `node_modules`, so dependency-requiring
commands were not independently rerun by the architect. The inspected
production/test diff and reported validation are internally consistent.

#### Final decision

`ARCH-006-ADMIN-004` is **Complete**.

This acceptance does not invoke ARCH-006 system tests. Per the developer's
manual-validation strategy, integrated manual smoke testing remains the next
checkpoint before terminal system-test execution.

Recommended manual smoke sequence:

```text
Take / existing ownership
  -> Send English administrative message
  -> verify Admin history
  -> verify merchant Messages history
  -> reload both applications
  -> verify persistence
  -> request an additional translation
  -> exercise targeted reconciliation on a FAILED translation when available
```

If live PostgreSQL validation exposes a new task-owned defect, reopen this task
with the concrete runtime evidence rather than broadening another task.

No commit or push is authorised or performed by this acceptance.
