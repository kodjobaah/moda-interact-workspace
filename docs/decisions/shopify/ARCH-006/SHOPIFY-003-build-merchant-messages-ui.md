---
id: ARCH-006-SHOPIFY-003
architecture_id: ARCH-006
title: Build the merchant Messages UI
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: complete
priority: 80
executor: null
claimed_at: null
attempt: 4
depends_on:
  - ARCH-006-SHOPIFY-001
  - ARCH-006-BACKGROUND-007
  - ARCH-005-SHOPIFY-002
enables:
  - ARCH-006-SYSTEM-TEST-001
created: 2026-09-05
updated: 2026-09-06
---
# ARCH-006-SHOPIFY-003: Build the merchant Messages UI

## Architecture

`docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

## Objective

Build the Shopify merchant Messages experience on top of accepted server behavior, with no translation or tenant-routing business logic invented in the client.

## Context

Backend compose/read/translation decisions are already accepted before this UI task. This makes the Luna implementation primarily deterministic UI integration.

## Scope

Shopify app navigation, unread badge, support thread/history/components, compose UX and original/translated display.

## Out of Scope

- DB/queue/provider changes.
- Client-supplied shop/language/message-kind state.
- Direct OpenAI/Redis access.
- Editing/deleting sent messages.

## Requirements

Add protected `Messages` navigation with tenant-safe unread badge from server capability. Show bounded chronological thread with distinct `System`, `Moda Support`, `Merchant/You` presentation.

ADMINISTRATIVE/SYSTEM are visible to merchant only when server returns AVAILABLE. For non-English outbound, render the exact translation for snapshotted `displayLanguageTag`; provide `View original`. Never silently display an English fallback for a required non-English translation.

Merchant compose uses shared 1..500 grapheme client validation/counter, rejects rather than truncates, and calls accepted compose service. Pending/processing feedback must not imply translation is lost.

Opening AVAILABLE ADMINISTRATIVE/SYSTEM calls accepted first-read behavior.

## Work Items

- [x] Inspect current Shopify design/navigation/i18n component conventions.
- [x] Add Messages navigation + unread badge.
- [x] Build bounded support-thread UI and kind/status presentation.
- [x] Add exact display translation + View original behavior.
- [x] Add 500-grapheme compose UX and server error handling.
- [x] Integrate first-read behavior.
- [x] Add focused UI/security/accessibility tests.
- [x] Correct empty-unread revalidation and server read eligibility semantics.

## Interfaces / Contracts

Consumes SHOPIFY-001 server capability and shared browser-safe body validation only. No queue/provider code.

## Dependencies

Explicit task dependencies are listed in YAML frontmatter.

## Enables

`ARCH-006-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Shared shop thread visible only to authenticated shop.
- [x] Message kinds are visually distinct.
- [x] Required non-English outbound never falls back silently to English.
- [x] View original is available when translation shown.
- [x] Compose enforces 500 graphemes and no truncation.
- [x] First-read integration is tenant-safe.
- [x] Client does not manufacture shop/language/kind/translation decisions.

## Validation

Focused UI/route tests plus declared Shopify tests/typecheck/lint/build and `git diff --check`.

## Implementation Notes

If backend capability is missing, stop and return to architect rather than implementing it inside a route/component.

## Completion Report

### Status

Ready for Review.

Attempt 4 was a test/validation-only correction. The accepted Attempt 3 production implementation was not changed.

### Files Changed

`app/routes/app.merchant-support.jsx`, `app/services/merchant-support/merchant-support.service.ts`, `tests/unit/merchant-support-route.test.ts`, and `tests/unit/merchant-support-service.test.ts`.

Attempt 4 touched only `tests/unit/merchant-support-service.test.ts` and this task metadata. The duplicate service import was merged, and the first-read test now asserts the actual `COALESCE("readAt", NOW())` SQL expression.

### Work Completed

Preserved the accepted merchant visibility, exact translation provenance, Shared grapheme counter, Pending Recoveries ICU-key correction, and server-derived tenant behavior. Attempt 3 now short-circuits empty unread state, requires HTTP success plus `{ marked: true }` for each read, performs at most one bounded revalidation after durable progress, and restricts server read success to tenant-owned AVAILABLE ADMINISTRATIVE/SYSTEM messages. Added deterministic route lifecycle and service eligibility regressions.

### Validation Results

Focused merchant-support service test: 7 passed. Touched-file ESLint: passed with no file-specific diagnostics. Full Shopify tests: 147 passed, 1 skipped across 23 files. Production build: passed. Prisma validation: passed. `git diff --check`: passed. Repository-wide lint/typecheck baseline issues remain outside this bounded task; they were not rerun for Attempt 4. npm reported the existing `shamefully-hoist` configuration warning, ESLint reported the existing TypeScript-version compatibility warning, and the build reported existing React Router future-flag and dependency annotation warnings.

### Deviations

The UI continues to use the accepted SHOPIFY-001 route/service and does not add backend, queue, provider, or tenant-routing logic. First-read uses authenticated same-origin POST requests, requires the accepted action's semantic success response, and follows durable progress with one React Router revalidation at most.

### Assumptions

The app root loader performs the bounded support unread query to render the navigation count. Shared `countUnicodeGraphemes` and `AuthoredSupportBodySchema` remain the client/server body contract.

### Unresolved Issues

No unresolved implementation issue. Long-running Docker/system/live-environment validation remains developer-owned by repository policy. Repository-wide lint/typecheck baseline failures remain outside this task's bounded files.

### Architectural Concerns

No new architectural concern. The task is ready for independent `moda_architect` review.

### Attempt 4 Handoff

The duplicate-import warning in the touched service test is removed, and the idempotent first-read SQL contract is explicitly covered. No production Shopify files, Shared files, schema/migrations, downstream tasks, or other repositories were modified during Attempt 4. The task is returned to `review`; architect acceptance is pending.

## Architect Review

### Review Status

Accepted / Complete

### Architect Review — Attempt 1 — 2026-09-06

**Review Status: Corrections required.**

Independent architect review finds the overall UI direction sound: authenticated tenant derivation is preserved, the Messages navigation/unread count is server-derived, the thread is bounded/paginated, translated AVAILABLE messages expose an explicit View original control, merchant compose calls the accepted server capability, and the agent returned this task to `review` without promoting downstream work.

Four blocking contract gaps remain:

1. **Outbound PROCESSING/FAILED messages are still exposed to the merchant browser before AVAILABLE.**
   `readMerchantSupportMessages()` selects every message for the Shop, including ADMINISTRATIVE/SYSTEM rows whose state is PROCESSING or FAILED, and serializes their immutable English `originalBody` into loader JSON. The React component hides that body visually, but the data has already crossed the browser boundary. SHOPIFY-003 explicitly requires ADMINISTRATIVE/SYSTEM to be merchant-visible only when AVAILABLE, with no silent English fallback for required non-English output. Pagination/total must also describe the merchant-visible set rather than hidden outbound rows.

2. **First-read mutation bypasses React Router revalidation, leaving the navigation unread badge stale.**
   The component calls global `fetch()` directly for each read mark. Those successful actions do not cause the root `/app` loader to re-run, so `Messages (N)` can remain stale after the merchant opens and reads the messages. First-read must use a router-managed action/revalidation path or explicitly revalidate once the read marks complete.

3. **The displayed grapheme counter duplicates the Shared contract instead of using it.**
   The route imports `AuthoredSupportBodySchema` but defines a local `countGraphemes()` implementation. Shared already publishes `countUnicodeGraphemes`; SHOPIFY-003 requires the compose validation/counter to use the Shared 1..500 grapheme contract, not a second implementation with different fallback semantics.

4. **The existing Pending Recoveries unavailable state performs one exact ICU lookup that does not exist and therefore crashes SSR.**
   This is an exact-key mismatch, not an absence of the existing Pending Recoveries explanatory translation. The current source contains two different lookups:

   ```jsx
   <span>{i18n.t("pending.unavailable")}</span>
   ...
   <p className="pending-recoveries-message" dir={i18n.direction}>
     {i18n.t("pending.unavailableMessage")}
   </p>
   ```

   Treat these keys as distinct:

   - `pending.unavailable` — **does not exist** as an exact catalogue key and is the lookup causing `Missing ICU catalogue key: pending.unavailable`.
   - `pending.unavailableMessage` — **does exist in all 20 merchant locale catalogues** and is the longer Pending Recoveries explanatory sentence. It is valid and must remain unchanged.
   - `common.unavailable` — **does exist in all 20 merchant locale catalogues** and is the existing reusable short label (`Unavailable` in English). It is the correct key for the `<span>` above.

   A command such as `grep pending.unavailable *` also matches the longer string `pending.unavailableMessage`; that substring match does **not** mean the exact key `pending.unavailable` exists. ICU lookup is exact.

   The required production change is exactly:

   ```diff
   - <span>{i18n.t("pending.unavailable")}</span>
   + <span>{i18n.t("common.unavailable")}</span>
   ```

   Preserve the existing `i18n.t("pending.unavailableMessage")` call directly below it. Do not rename it, remove it, or replace it with `common.unavailable`. Do not add `pending.unavailable` to any locale catalogue. Do not modify any of the 20 locale JSON files for this correction.

The current focused tests do not prove the actual merchant presentation boundary: they test loader/action tenant derivation and grapheme counting, but do not prove hidden outbound rows never reach the merchant response, `View original` is available only after the required translation is AVAILABLE, that first-read refreshes the unread navigation state, or that the dashboard unavailable state resolves only canonical catalogue keys.

### Attempt 2 — Bounded Correction Contract

The repository agent may change only:

- `moda-interact/app/routes/app.jsx`
- `moda-interact/app/routes/app.merchant-support.jsx`
- `moda-interact/app/services/merchant-support/merchant-support.service.ts`
- `moda-interact/tests/unit/merchant-support-route.test.ts`
- `moda-interact/tests/unit/merchant-support-service.test.ts`
- `moda-interact/app/components/dashboard/PendingRecoveries.jsx`
- `moda-interact/tests/unit/merchant-i18n.test.ts`

`app/tailwind.css` is read-only for Attempt 2 unless a focused accessibility/presentation regression proves a styling change is required. Do not modify billing, queue/provider/background code, database schema/migrations, Shared, ARCH-005 behavior, or any downstream/system-test task.

Required correction:

- Make the server history contract expose:
  - all MERCHANT messages; and
  - ADMINISTRATIVE/SYSTEM messages only when `state = 'AVAILABLE'`.
  Hidden PROCESSING/FAILED outbound messages must not serialize `originalBody` or any other message payload to the browser. The paginated `total`/`totalPages` must use the same merchant-visible predicate. Unread remains AVAILABLE ADMINISTRATIVE/SYSTEM with `readAt IS NULL`.
- Preserve exact required-language selection: for an AVAILABLE non-English outbound message, return only the AVAILABLE translation whose target matches the snapshotted `displayLanguageTag`; never fall back to English or another translation. `View original` may expose immutable English source only after that merchant-visible translated message is AVAILABLE.
- Make first-read update the app-shell unread badge. Use React Router mutation/revalidation semantics or explicitly call router revalidation after the bounded read-mark sequence completes. Do not continuously revalidate or create an effect loop. Failed read requests must not be treated as successfully read.
- Import and use Shared `countUnicodeGraphemes` for the counter. Remove the independent local grapheme algorithm. `AuthoredSupportBodySchema` remains the authoritative client/server rejection contract and bodies are never truncated.
- Fix the live Pending Recoveries SSR failure with the following exact, bounded edit in `app/components/dashboard/PendingRecoveries.jsx`:

  ```diff
  - <span>{i18n.t("pending.unavailable")}</span>
  + <span>{i18n.t("common.unavailable")}</span>
  ```

  The following existing explanatory-message lookup is a separate valid key and **must remain present and unchanged**:

  ```jsx
  i18n.t("pending.unavailableMessage")
  ```

  Do not add an exact `pending.unavailable` key. Do not rename or remove `pending.unavailableMessage`. Do not modify any locale JSON file. The intended unavailable-state semantics are: short generic label = `common.unavailable`; longer recovery-specific explanation = `pending.unavailableMessage`.
- Keep tenant/shop/language/kind/provenance decisions server-derived. Do not add client Redis/OpenAI access or translation orchestration.

Required focused regressions:

1. Merchant history query/count use the same visibility predicate and exclude PROCESSING/FAILED ADMINISTRATIVE/SYSTEM rows while retaining MERCHANT rows.
2. A required-language AVAILABLE outbound message returns the exact matching translated body and exposes the original only through the explicit translated-message presentation path; no wrong-language/English fallback is produced.
3. First-read marks only tenant-verified AVAILABLE ADMINISTRATIVE/SYSTEM messages and causes exactly one bounded app-loader revalidation after the read sequence, so the unread badge can refresh without an effect loop.
4. The compose counter uses Shared grapheme semantics for complex Unicode at 500/501 and the client still rejects rather than truncates.
5. Add a focused regression for the Pending Recoveries exact-key correction. It must prove all of the following without changing locale files:
   - `common.unavailable` resolves successfully through merchant i18n;
   - `pending.unavailableMessage` remains a valid, separate catalogue key;
   - `PendingRecoveries.jsx` no longer contains the exact lookup `i18n.t("pending.unavailable")`;
   - `PendingRecoveries.jsx` still contains `i18n.t("pending.unavailableMessage")`.

   A deterministic source-level assertion in `tests/unit/merchant-i18n.test.ts` is acceptable for the last two checks. If using a source assertion, match the full lookup string including the closing quote/parenthesis so `pending.unavailableMessage` cannot be mistaken for `pending.unavailable`. Do not use substring-only catalogue-key detection.
6. Existing auth/tenant provenance, pagination, compose server error, merchant-i18n catalogue validation, build, Prisma validation, touched-file lint/diagnostics and `git diff --check` remain passing. Existing unrelated repository-wide baseline lint/typecheck diagnostics remain out of scope.

Return this same task to `review` and STOP. Do not promote any system-test task.



### Architect Review — Attempt 2 — 2026-09-06

**Review Status: Corrections required.**

Attempt 2 correctly fixes the other four architect-review findings:

- merchant history/count now use one server-side visibility predicate so PROCESSING/FAILED ADMINISTRATIVE/SYSTEM rows do not cross the merchant browser boundary;
- required non-English display selection remains pinned to the snapshotted `displayLanguageTag`, with no English/wrong-language fallback;
- the compose counter now delegates to Shared `countUnicodeGraphemes`;
- Pending Recoveries now uses `common.unavailable` for the short label while retaining `pending.unavailableMessage` unchanged.

One blocking first-read/revalidation defect remains.

#### Blocking defect: the effect revalidates again when there are no unread IDs

Current Attempt 2 code always executes `revalidator.revalidate()` after the `for` loop, even when the unread-ID list is empty:

```jsx
async function markUnreadMessages() {
  for (const messageId of unreadMessageIds.split(",").filter(Boolean)) {
    ...
  }
  if (!cancelled) revalidator.revalidate();
}
```

This violates the Attempt 2 requirement for **exactly one bounded app-shell revalidation after successful first-read marking**.

Deterministic sequence with one unread message:

```text
loader returns unread message m1
        ↓
effect posts read(m1)
        ↓
revalidate #1
        ↓
loader returns m1 with readAt set
        ↓
unreadMessageIds changes from "m1" to ""
        ↓
effect runs again
        ↓
for-loop has zero entries
        ↓
current code still calls revalidate #2   <-- defect
```

On a page that starts with no unread messages, the same code also performs an unnecessary revalidation immediately on mount. Depending on `useRevalidator()` object identity across router state changes, using the whole `revalidator` object as an effect dependency can also create avoidable effect re-entry risk.

The focused regression added in Attempt 2 is source-text-only and does not prove the required lifecycle. It asserts that a `revalidate()` call exists, but it does not prove that zero unread IDs produce zero revalidations or that a successful read sequence produces exactly one.

There is one related semantic gap in the accepted action/service path: `markMerchantSupportMessageRead()` returns `true` after tenant existence verification even when the message is not an AVAILABLE ADMINISTRATIVE/SYSTEM message and the UPDATE affects no eligible row. The browser therefore cannot distinguish `marked: false` from an actual successful first-read mark. Attempt 3 must tighten this return contract without changing the database schema or tenant boundary.

### Attempt 3 — Bounded Correction Contract

This is a narrow correction. Preserve every accepted Attempt 2 change. Do not redesign the Messages page.

The repository agent may modify only:

- `moda-interact/app/routes/app.merchant-support.jsx`
- `moda-interact/app/services/merchant-support/merchant-support.service.ts`
- `moda-interact/tests/unit/merchant-support-route.test.ts`
- `moda-interact/tests/unit/merchant-support-service.test.ts`
- this task file and its Shopify ARCH-006 index as required by the normal task protocol.

Do **not** modify:

- `app/routes/app.jsx`;
- `app/components/dashboard/PendingRecoveries.jsx`;
- any merchant locale JSON file;
- Shared/package versions;
- database schema/migrations;
- Background/Gateway/Admin code;
- any ARCH-005 behavior;
- any system-test/downstream task.

#### Required production behavior

1. **Zero unread IDs must be a no-op.**

   Before issuing any POST or calling router revalidation, derive the concrete unread ID array and return immediately when it is empty.

   Required lifecycle:

   ```text
   unread IDs = []
       -> 0 read POSTs
       -> 0 router revalidations
   ```

2. **A successful bounded read sequence must cause exactly one router revalidation.**

   For one or more unread IDs:

   ```text
   unread IDs = [m1, m2, ...]
       -> POST each ID serially using the existing authenticated same-origin action
       -> require HTTP success
       -> require response JSON `marked === true`
       -> after the successful sequence, call router `revalidate()` exactly once
   ```

   After that revalidation, the loader should return those messages with `readAt` populated. The resulting empty unread-ID list must hit requirement 1 and must **not** trigger a second revalidation.

3. **Do not depend on the entire mutable revalidator object inside the effect.**

   Prefer the narrow callable dependency:

   ```jsx
   const { revalidate } = useRevalidator();
   ```

   and make the effect depend on the unread-ID value plus the stable revalidation function, not on the whole `revalidator` state object.

   Do not suppress React hook dependency rules to hide an effect-loop problem.

4. **Treat semantic read failure as failure, not success.**

   A `200` response containing `{ marked: false }` is not a successful first-read mark. The client must inspect the JSON result and must not treat it as success.

   If a sequence has no successful mark, do not revalidate merely because the effect ran. If an earlier ID was successfully marked before a later ID fails, at most one revalidation may be used to refresh the shell to the durable state already changed; do not create a retry/revalidation loop.

5. **Tighten `markMerchantSupportMessageRead()` return semantics.**

   It may return `true` only when the requested message:

   - belongs to the authenticated `shopId`;
   - is `ADMINISTRATIVE` or `SYSTEM`;
   - is `AVAILABLE`;
   - is therefore eligible for the first-read operation.

   A MERCHANT message, PROCESSING/FAILED outbound message, wrong-tenant ID, or missing ID must return `false` and must not be reported as successfully marked.

   Preserve idempotency: an already-read eligible AVAILABLE ADMINISTRATIVE/SYSTEM message may safely return `true`; `readAt` must remain first-read (`COALESCE`) semantics.

6. **Preserve all Attempt 2 behavior unchanged.**

   In particular, do not regress:

   - server-side merchant-visible history predicate and matching pagination count;
   - hidden PROCESSING/FAILED outbound payload boundary;
   - exact `displayLanguageTag` translation selection;
   - explicit View original behavior only for translated AVAILABLE output;
   - Shared `countUnicodeGraphemes` usage and 500/501 rejection semantics;
   - `common.unavailable` / `pending.unavailableMessage` ICU correction;
   - server-derived tenant/shop/language/kind/provenance decisions.

#### Required focused regressions

Add/adjust tests so the regression is deterministic rather than merely checking that the source contains a `revalidate()` call.

At minimum prove:

1. **No unread IDs:** the first-read lifecycle performs zero read requests and zero revalidation calls.
2. **One or more successful IDs:** all intended read requests succeed and router revalidation occurs exactly once.
3. **Post-revalidation empty state:** the empty unread-ID state cannot cause a second revalidation.
4. **HTTP failure or `{ marked: false }`:** is not counted as successful first-read behavior and cannot create a revalidation loop.
5. **Server return contract:** wrong tenant, MERCHANT, PROCESSING and FAILED messages return `false`; eligible AVAILABLE ADMINISTRATIVE/SYSTEM returns `true`; already-read eligible rows remain idempotent.
6. Existing Attempt 2 focused regressions remain passing, including visibility/count, exact translation provenance, Shared grapheme counting and Pending Recoveries exact ICU keys.
7. Full declared Shopify validation remains as required by the task: focused tests, full `npm test`, build, Prisma validation, touched-file lint/diagnostics and `git diff --check`. Existing unrelated repository-wide lint/typecheck baseline diagnostics may remain only if unchanged and clearly reported.

Do not solve this by adding timers, arbitrary flags, global mutable state, suppressing hook lint rules, or weakening first-read semantics. Keep the correction local and deterministic.

Return this same task to `review` and STOP. Do not promote any system-test task.


### Architect Review — Attempt 3 — 2026-09-06

**Review Status: Corrections required.**

Attempt 3 production behavior is accepted in substance. Independent architect review confirms that the bounded first-read lifecycle now satisfies the required runtime contract:

- an empty unread-ID set returns without issuing a read POST or router revalidation;
- one or more successful semantic read results cause one bounded revalidation;
- HTTP failure and `{ marked: false }` are not treated as successful reads;
- the effect depends on the narrow `revalidate` callable rather than the full revalidator object;
- `markMerchantSupportMessageRead()` now verifies authenticated Shop ownership plus ADMINISTRATIVE/SYSTEM and AVAILABLE eligibility before returning `true`;
- first-read persistence retains `COALESCE("readAt", NOW())` semantics;
- all accepted Attempt 2 behavior remains unchanged.

No production correction has been identified in the Attempt 3 implementation.

The task cannot yet be architect-accepted because Attempt 3 introduced a validation regression in a touched file and did not add the explicitly requested idempotency regression:

1. `tests/unit/merchant-support-service.test.ts` now imports the same service module twice:

   ```ts
   import { composeMerchantMessage } from "../../app/services/merchant-support/merchant-support.service";
   import { markMerchantSupportMessageRead } from "../../app/services/merchant-support/merchant-support.service";
   ```

   This is the source of the two new import-lint warnings reported by the repository agent. These warnings are not part of the pre-existing repository baseline: the second import was introduced by Attempt 3. The task contract permits unrelated unchanged repository-wide baseline diagnostics, but it does not permit a new diagnostic in a touched file.

2. The Attempt 3 service regression proves eligibility SQL but does not explicitly prove the required already-read idempotency contract. Production source still uses `COALESCE("readAt", NOW())`, so the behavior is correct, but the bounded correction contract explicitly required focused regression coverage for already-read eligible rows.

### Attempt 4 — Bounded Validation/Test-Only Correction Contract

This is a **test/validation-only correction**. The production implementation from Attempt 3 is architect-approved in substance. Do not redesign or modify runtime behavior.

The repository agent may modify only:

- `moda-interact/tests/unit/merchant-support-service.test.ts`;
- this task file and the Shopify ARCH-006 index as required by normal task protocol.

Do **not** modify any production file, including:

- `moda-interact/app/routes/app.merchant-support.jsx`;
- `moda-interact/app/services/merchant-support/merchant-support.service.ts`;
- `moda-interact/app/routes/app.jsx`;
- `moda-interact/app/components/dashboard/PendingRecoveries.jsx`;
- locale catalogues;
- Shared/package versions;
- database schema/migrations;
- Background/Gateway/Admin code;
- any ARCH-005 behavior;
- any system-test/downstream task.

#### Required correction 1 — remove the Attempt 3 duplicate import warning

Replace the two imports from the same service module with one import declaration. The target shape is:

```ts
import {
  composeMerchantMessage,
  markMerchantSupportMessageRead,
} from "../../app/services/merchant-support/merchant-support.service";
```

Do not suppress or disable ESLint rules. Do not change repository lint configuration.

#### Required correction 2 — explicitly regress first-read idempotency

Extend the existing `markMerchantSupportMessageRead()` focused test so it proves that the UPDATE retains first-read semantics. The regression must inspect the actual `Prisma.Sql` passed to `$executeRaw` and assert that it contains:

```sql
"readAt" = COALESCE("readAt", NOW())
```

The test must continue to prove that:

- eligible tenant-owned AVAILABLE ADMINISTRATIVE/SYSTEM returns `true`;
- wrong-tenant, MERCHANT, PROCESSING and FAILED cases return `false`;
- the eligible UPDATE uses COALESCE so an already-populated `readAt` is not overwritten.

A deterministic SQL-shape assertion is sufficient here because the production behavior was already inspected and no disposable PostgreSQL integration test is required for this narrow UI task.

#### Required validation

Run at minimum:

1. focused merchant-support service test;
2. the full declared Shopify test suite;
3. touched-file ESLint for `tests/unit/merchant-support-service.test.ts`;
4. production build;
5. Prisma validation;
6. `git diff --check`.

The touched service test must have **zero new lint warnings/errors**. Existing unrelated repository-wide lint/typecheck baseline diagnostics may remain only if unchanged.

Return this same task to `review` and STOP. Do not modify or promote any system-test task.


### Architect Acceptance — Attempt 4 — 2026-09-06

**Review Status: Accepted / Complete.**

Independent `moda_architect` review accepts Attempt 4 and the underlying
`ARCH-006-SHOPIFY-003` implementation.

Attempt 4 stayed within the architect-authorised validation/test-only surface.
A direct comparison with Attempt 3 confirms that only these files changed:

- `tests/unit/merchant-support-service.test.ts`;
- this task record;
- the ARCH-006 Shopify index.

No production Shopify file changed in Attempt 4.

Verified acceptance evidence:

- the duplicate service-module import introduced in Attempt 3 is merged into one
  import declaration, removing the task-owned touched-file import diagnostic;
- the focused read regression now inspects the actual `Prisma.Sql` passed to
  `$executeRaw()` and explicitly proves
  `"readAt" = COALESCE("readAt", NOW())`, closing the required first-read
  idempotency proof;
- the previously reviewed Attempt 3 production behavior remains unchanged:
  empty unread state is a no-op; successful bounded read marking causes at most
  one shell revalidation; HTTP/semantic read failures are not treated as
  success; server read success is restricted to tenant-owned AVAILABLE
  ADMINISTRATIVE/SYSTEM messages; and already-read eligible rows preserve their
  original first-read timestamp;
- accepted Attempt 2 behavior remains present, including the merchant-visible
  history/count boundary, exact translation provenance, Shared
  `countUnicodeGraphemes`, and the Pending Recoveries
  `common.unavailable` / `pending.unavailableMessage` ICU correction;
- the repository agent reports 147 tests passing with 1 skipped, plus passing
  build, Prisma validation, focused service validation, ESLint and
  `git diff --check`;
- the supplied review archive contains no `node_modules`, so the architect could
  not independently rerun dependency-requiring commands from this archive; the
  source/test diff and reported validation are internally consistent.

`ARCH-006-SHOPIFY-003` is therefore **Complete**.

Per the developer's manual-validation strategy, this acceptance does **not**
invoke or promote a terminal ARCH-006 system-test task. System validation remains
deferred until the developer is satisfied with manual integrated behavior.

No commit or push is authorised or performed by this acceptance.
