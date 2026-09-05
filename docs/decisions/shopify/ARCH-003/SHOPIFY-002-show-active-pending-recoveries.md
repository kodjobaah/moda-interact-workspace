---
id: ARCH-003-SHOPIFY-002
architecture_id: ARCH-003
title: Show active pending recoveries on merchant Usage overview
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: complete
priority: 30
executor: copilot
claimed_at: 2026-09-05T09:12:07Z
attempt: 3
depends_on:
  - ARCH-003-SHOPIFY-001
  - ARCH-003-BACKGROUND-002
enables:
  - ARCH-003-SYSTEM-TEST-002
created: 2026-09-05
updated: 2026-09-05
---

# Show active pending recoveries on merchant Usage overview

## Architecture

`docs/architecture/ARCH-003-admin-operational-ui.md`

## Objective

On the authenticated Shopify merchant `Usage overview` screen, show all
currently active pending-recovery candidates for the resolved shop using
shop-scoped, read-only Redis/BullMQ access.

The view must be useful to the merchant without exposing internal recovery
tokens, Redis details or other shops' candidates.

## Placement

The existing Usage overview currently renders:

```text
Current usage
Past paid usage
```

Add a full-width section below that usage block:

```text
Pending recoveries
```

This section must visually fit the existing Moda/Shopify dashboard rather than
introducing a separate operational-console style.

## Meaning of "active pending recovery"

A candidate is displayed only while it remains in the Background-owned
shop-scoped active index and its BullMQ job state is one of:

```text
delayed
waiting
active
```

Merchant labels:

```text
delayed -> Scheduled
waiting -> Waiting
active  -> Processing
```

Do not show:

```text
failed
completed
unknown/missing jobs
```

A matured candidate is no longer a pending candidate even when downstream
materialisation fails.

## Tenant isolation

The loader already obtains the shop from:

```text
authenticate.admin(request)
    ->
shopService.resolveShopifyShop(...)
```

The pending-recovery query must use only that resolved internal:

```text
shop.id
shop.domain
```

The browser must not be allowed to supply a shopId/shopDomain that selects the
Redis index.

Read only:

```text
pending-recovery:index:shop:<authenticated shop.id>
```

For every returned BullMQ job, verify defense-in-depth:

```text
job.name == evaluate-pending-recovery
job.data.shopId == authenticated shop.id
normalize(job.data.shopDomain) == normalize(authenticated shop.domain)
```

A mismatch is omitted and must not leak candidate data.

## Data source

Background owns the index:

```text
pending-recovery:index:shop:<shopId>
```

ZSET member:

```text
pending candidate BullMQ job ID
```

ZSET score:

```text
scheduled due time in epoch milliseconds
```

BullMQ queue:

```text
pending-recovery-candidates
```

The Shopify application is a read-only merchant consumer.

No queue mutation controls are permitted.

## Redis connection

Reuse the existing environment contract:

```text
REDIS_URL
```

No new secret/environment variable is required.

Redis access is server-side only.

Use bounded connection/command behavior appropriate for a page loader. Do not
allow an unavailable Redis endpoint to hang the merchant request indefinitely.

## Failure behavior

Redis/BullMQ availability must not take down the rest of the merchant dashboard.

If pending-recovery data cannot be read within the bounded operation:

- continue rendering current/past usage;
- return a safe pending-recovery unavailable state;
- render a compact message such as:

```text
Pending recovery status is temporarily unavailable.
```

Do not return Redis URLs, raw connection errors or stack traces to browser UI.

## Pagination

The per-shop ZSET supports efficient exact pagination.

Use a bounded page size:

```text
10
```

The route may use a merchant-safe query parameter such as:

```text
pendingPage=1
```

Requirements:

- default page 1;
- clamp invalid values to page 1;
- `ZCARD` supplies the shop-scoped total;
- `ZRANGE`/equivalent reads only the requested page ordered by due time;
- Previous/Next navigation;
- changing pending page must not switch the existing Usage overview into bill
  detail mode;
- no global Redis scan.

## Browser DTO

Return only fields necessary for display, for example:

```text
id
status
checkoutCreatedAt
scheduledFor
```

The job ID may be retained as an opaque React/navigation key but should not be
presented as merchant-facing business data.

Do NOT send these candidate fields to the browser:

```text
checkoutToken
cartToken
abandonedCheckoutUrl
REDIS_URL
Redis key names
raw BullMQ opts
stack traces
```

The recovery URL contains a recovery key and must not be exposed merely to
populate this table.

## UI

Create a small reusable component rather than turning `UsageOverview.jsx` into
a large monolith.

Suggested display:

```text
Pending recoveries                                      3 active

Checkout created          Recovery scheduled        Status
05 Sep 08:04              05 Sep 08:34             Scheduled
05 Sep 08:07              Due now                   Waiting
05 Sep 08:08              Processing                Processing
```

Exact wording may be refined to fit the existing design.

Empty state:

```text
No active pending recoveries.
```

Unavailable state:

```text
Pending recovery status is temporarily unavailable.
```

The section is read-only.

No Cancel / Retry / Process-now action is part of this task.

## Expected implementation areas

Likely areas:

```text
app/routes/app._index.jsx
app/components/dashboard/UsageOverview.jsx
app/components/dashboard/<new pending-recovery component>.jsx
app/services/<server-only pending-recovery reader>
app/tailwind.css
tests/...
```

The agent should choose the smallest reusable structure consistent with the
existing repository.

## Tests

Cover at minimum:

- [x] authenticated shop ID determines the Redis index;
- [x] browser input cannot select another shop's index;
- [x] only delayed/waiting/active jobs are returned;
- [x] job name is validated;
- [x] `data.shopId` is validated;
- [x] `data.shopDomain` is normalized and validated;
- [x] failed/completed/missing jobs are omitted;
- [x] checkout/cart tokens and abandoned checkout URL are not returned in DTO;
- [x] page size is 10;
- [x] total/page metadata comes from shop-scoped ZSET;
- [x] no global Redis `SCAN` is used;
- [x] Redis unavailable state does not fail the main dashboard loader;
- [ ] populated UI renders rows;
- [ ] empty UI renders correctly;
- [ ] unavailable UI renders correctly;
- [ ] Previous/Next behavior is correct.

## Live Verification

Using the current development Redis and a fresh Shopify checkout:

1. create a checkout that produces a delayed pending candidate;
2. verify Background has indexed it under the authenticated shop;
3. open `/app`;
4. verify the candidate appears under `Pending recoveries`;
5. verify the merchant view shows safe timestamps/state only;
6. allow/cancel the candidate so it stops being pending;
7. refresh `/app`;
8. verify it disappears.

Where practical, verify a different shop cannot see the candidate.

## Acceptance Criteria

- [x] Usage overview contains a Pending recoveries section below usage charts.
- [x] Active candidates for the authenticated shop are visible.
- [x] Scheduled/Waiting/Processing states are represented truthfully.
- [x] All active candidates are browsable through shop-scoped pagination.
- [x] No global BullMQ/Redis scan is used.
- [x] No cross-tenant candidate can be displayed.
- [x] Sensitive candidate tokens/URL are not exposed.
- [x] Redis failure degrades only the pending-recovery section.
- [x] Existing usage overview/current/past bill behavior does not regress.
- [x] no queue mutations are added.
- [x] focused tests pass.
- [x] full tests pass subject only to documented baseline conditions.
- [x] typecheck/lint/build pass subject only to documented baseline conditions.
- [x] `git diff --check` passes.
- [ ] live verification succeeds where environment permits.

## Architect Amendment 001 — Manual refresh for Pending recoveries

The initial merchant Pending recoveries panel is visually accepted as the
baseline for this task, but one small interaction is required before architect
acceptance.

### Objective

Add a lightweight manual refresh control to the Pending recoveries section so a
merchant can update candidate state without reloading/re-querying the entire
Usage overview.

This is intentionally **not** the Admin queue polling model.

Do not add:

```text
5 seconds
10 seconds
30 seconds
automatic polling interval selector
```

The merchant dashboard should use explicit refresh only.

### Required header behavior

The Pending recoveries header should expose:

```text
Pending recoveries                         <N> active

Last updated HH:mm                         Refresh
```

Exact visual spacing may follow the existing component design.

The `Last updated` value represents the time the Pending recoveries dataset was
successfully obtained for display, not the checkout's creation/update time.

### Refresh behavior

Clicking `Refresh` must:

1. refresh only the Pending recoveries data;
2. avoid a full document reload;
3. avoid unnecessarily re-running current/past billing/usage queries;
4. preserve the current `pendingPage` where that page is still valid;
5. show a disabled busy state such as:

```text
Refreshing…
```

while the request is in flight;
6. prevent duplicate refresh clicks while already refreshing;
7. update the active count, rows, pagination metadata and `Last updated` time
   after the refresh completes.

Use the repository's existing React Router data APIs and the smallest
server-only authenticated endpoint/resource-loader structure appropriate to the
current implementation.

Do not move Redis access into browser code.

### Pagination edge case

Suppose the merchant is viewing:

```text
pendingPage=2
```

and refresh removes enough matured candidates that page 2 no longer exists.

The refreshed panel must fall back to the last valid page rather than displaying
a permanently empty invalid page.

Examples:

```text
page 2 -> page 2       when still valid
page 2 -> page 1       when only one page remains
page 4 -> page 3       when page 3 becomes the last valid page
```

This correction may be implemented server-side or by a bounded client follow-up
request, but it must not introduce an unbounded loop.

### Failure behavior

A failed refresh must preserve the architecture's supplementary-data failure
boundary.

Do not fail the whole merchant dashboard.

The panel may show the existing safe unavailable state:

```text
Pending recovery status is temporarily unavailable.
```

or preserve the previous successful data with a compact safe refresh-error
message, provided no raw Redis/BullMQ error details reach the browser.

### Tenant isolation

The refresh request must derive the shop from the authenticated Shopify admin
session exactly as the initial load does.

The browser must not be able to supply:

```text
shopId
shopDomain
Redis key
```

to select another tenant.

All existing job-name, job-state, `data.shopId` and normalized
`data.shopDomain` validation remains required.

### Sensitive data

Refresh must continue returning only the safe merchant DTO.

Do not expose:

```text
checkoutToken
cartToken
abandonedCheckoutUrl
REDIS_URL
Redis key names
BullMQ opts
raw job data
```

### UI scope

Keep the current visual panel as the baseline.

Do not redesign the table or usage charts.

The only intended visual addition is the compact refresh/last-updated affordance
in the Pending recoveries section.

### Regression coverage

Add focused tests for:

- [x] manual refresh requests only pending-recovery data;
- [x] refresh derives the tenant from authenticated Shopify context;
- [x] refresh does not accept a browser-selected shop identity;
- [x] busy state disables repeated refresh;
- [x] active count and rows update after refresh;
- [x] successful refresh updates `Last updated`;
- [x] current valid `pendingPage` is preserved;
- [x] invalid page after refresh falls back to the last valid page;
- [x] empty results fall back safely to page 1;
- [x] refresh failure does not fail the rest of Usage overview;
- [x] no automatic polling interval is introduced;
- [x] sensitive candidate fields remain absent from the browser DTO.

### Live verification

With an authenticated merchant session and a real delayed candidate:

1. open `/app`;
2. verify the candidate appears in Pending recoveries;
3. note `Last updated`;
4. cause or wait for a candidate-state change;
5. click `Refresh`;
6. verify only the panel refresh interaction occurs;
7. verify the row/state/count changes;
8. verify `Last updated` advances;
9. verify no full document reload occurs.

### Attempt handling

This amendment belongs to the existing `ARCH-003-SHOPIFY-002` Attempt 1.

Do not create or claim a new task.

Do not increment the attempt.

After implementation and validation:

```text
status: review
executor: copilot
attempt: 1
Completion Report: Ready for Review
```

## Resolver Coordination Remedy

The first Amendment 001 overlay incorrectly placed this task into:

```text
status: in_progress
claimed_at: null
```

The authoritative repository resolver only permits execution to begin from:

```text
status: ready
```

This coordination-only remedy therefore restores:

```yaml
status: ready
executor: null
claimed_at: null
attempt: 1
```

`attempt: 1` records the already-finished initial SHOPIFY-002 implementation.

When the repository agent claims this Ready task for Amendment 001, the normal
claim protocol will advance it to:

```yaml
status: in_progress
executor: <current executor>
claimed_at: <claim timestamp>
attempt: 2
```

This is expected and is not a new architectural task. It is the second execution
attempt of the same `ARCH-003-SHOPIFY-002` task.

The implementation scope remains only Architect Amendment 001:

- manual Pending recoveries refresh;
- `Last updated`;
- refresh only pending-recovery data;
- preserve/fallback pending pagination;
- no merchant auto-polling;
- preserve tenant isolation and sensitive-data redaction.

## Architect Correction — Amendment 002: pagination state synchronisation

The manual-refresh implementation is close to acceptance, but review of the
actual component exposed one state-synchronisation defect.

### Problem

`PendingRecoveries` currently initialises local display state from loader props:

```js
const [displayData, setDisplayData] = useState(pendingRecoveries);
const [lastUpdated, setLastUpdated] = useState(
  pendingRecoveries?.available ? pendingRecoveriesUpdatedAt : null
);
```

and later updates that state only from:

```text
fetcher.data
```

The normal Previous/Next controls navigate through:

```text
/app?pendingPage=<n>
```

which re-runs the parent `/app` loader.

React Router may keep the existing component mounted while supplying new
`pendingRecoveries` / `pendingRecoveriesUpdatedAt` props.

Without synchronising those new props into local state, the browser can reach:

```text
URL pendingPage=2
displayData.page=1
```

The next manual refresh then uses:

```js
displayData.page
```

and can request the wrong page.

### Required correction

Synchronise local Pending recoveries display state whenever the parent loader
supplies a new pending-recovery dataset.

Conceptually:

```text
new pendingRecoveries prop
        |
        v
displayData = pendingRecoveries

new pendingRecoveriesUpdatedAt prop
        |
        v
lastUpdated = successful timestamp / null
```

The implementation should avoid clobbering a completed `fetcher` refresh unless
the parent loader has actually supplied new props.

The smallest idiomatic React solution is preferred.

### Required behavior

Verify this sequence:

```text
initial page 1
    |
click Next
    v
parent loader returns page 2
    |
panel renders page 2
    |
click Refresh
    v
resource loader receives pendingPage=2
```

Also verify:

```text
page 2
    |
Refresh
    |
result shrinks to totalPages=1
    v
panel renders effective page 1
    |
subsequent Refresh uses page 1
```

### Regression coverage

Add focused coverage proving:

- [x] a new parent-loader `pendingRecoveries` prop updates the displayed page;
- [x] a new parent-loader timestamp updates `Last updated`;
- [x] navigating from page 1 to page 2 does not leave stale page-1 local state;
- [x] refresh after navigation requests the currently displayed page;
- [x] refresh fallback to a lower valid page becomes the new displayed page;
- [x] a subsequent refresh uses that fallback page;
- [x] existing busy-state duplicate-click protection remains;
- [x] no automatic polling is introduced.

Use the repository's existing test style. If direct component interaction tests
are not practical with the current dependencies, a focused extraction/helper or
source-contract test is acceptable, but the stale-prop regression itself must
be covered rather than merely inferred.

### Existing implementation preserved

Do not redesign the panel.

Preserve:

- authenticated resource loader;
- shop-scoped reader;
- manual Refresh;
- `Last updated`;
- safe unavailable behavior;
- tenant isolation;
- sensitive DTO redaction;
- page size 10;
- no global Redis scan;
- no automatic polling.

### Resolver / attempt handling

Attempt 2 is preserved as the completed Amendment 001 implementation attempt.

This coordination correction restores:

```yaml
status: ready
executor: null
claimed_at: null
attempt: 2
```

The next normal repository claim will become Attempt 3 for this same
`ARCH-003-SHOPIFY-002` task.

After implementation:

```text
status: review
Completion Report: Ready for Review
```

## Completion Report

### Status

Ready for Review.

### Work Items

- Implemented the authenticated `/app/pending-recoveries` resource loader.
- Added React Router `useFetcher` manual refresh with disabled busy state.
- Added server-generated `Last updated` timestamp and safe unavailable handling.
- Preserved the current pending page and reader-side fallback to the last valid page.
- Added authenticated tenant-isolation coverage for refresh requests.
- Synchronized local panel state with parent-loader pagination and timestamps.
- Added focused regression coverage for page navigation and state synchronization.

### Validation

- Focused pending-recovery tests: 6 passed.
- Full Shopify tests: 17 files passed, 1 skipped; 88 tests passed, 1 skipped.
- Production build: passed.
- Changed-file ESLint: passed.
- `git diff --check`: passed.
- Typecheck: existing baseline diagnostics remain in `app._index.jsx`, `app/db.server.js`, and unrelated route files; production build passes.
- Live Shopify/Redis verification was unavailable because no authenticated merchant session was available.

### Git / VCS

Implementation ready for developer commit/push.
Repository agent did not commit or push.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 3, including Architect Amendments 001 and 002, is architect-accepted
Complete.

The reviewed implementation provides a merchant-facing Pending recoveries panel
backed by the authenticated shop-scoped Redis/BullMQ reader.

Accepted behavior includes:

- authenticated shop resolution for both initial load and manual refresh;
- shop-scoped read from `pending-recovery:index:shop:<shopId>`;
- bounded page size of 10;
- strict validation of job name, BullMQ state, `data.shopId`, and normalized
  `data.shopDomain`;
- browser DTO redaction of checkout/cart tokens, recovery URL and Redis/BullMQ
  internals;
- merchant labels:
  - `delayed` -> Scheduled
  - `waiting` -> Waiting
  - `active` -> Processing;
- safe empty and unavailable states;
- manual refresh through a dedicated authenticated resource loader;
- no full-document reload for panel refresh;
- disabled `Refreshing...` state;
- `Last updated` sourced from successful pending-data reads;
- no Admin-style automatic polling;
- reader-side fallback to the last valid page when the result set shrinks;
- local component state synchronisation with new parent-loader props after
  Previous/Next navigation.

### Pagination state invariant

Amendment 002 is verified in the actual component:

```text
parent loader pendingRecoveries
        |
        v
useEffect
        |
        v
displayData

fetcher.data
        |
        v
useEffect
        |
        v
displayData
```

This keeps normal navigation and manual panel refresh aligned on the same
effective page.

### Reviewed Files

- `moda-interact/app/routes/app._index.jsx`
- `moda-interact/app/routes/app.pending-recoveries.jsx`
- `moda-interact/app/components/dashboard/UsageOverview.jsx`
- `moda-interact/app/components/dashboard/PendingRecoveries.jsx`
- `moda-interact/app/services/pending-recovery/pending-recovery-reader.server.ts`
- `moda-interact/tests/unit/pending-recovery-reader.test.ts`
- `moda-interact/tests/unit/pending-recoveries-route.test.ts`
- `moda-interact/tests/unit/pending-recoveries-display-state.test.ts`

### Validation Reviewed

Implementing-agent evidence:

- focused tests: 6 passed;
- full Shopify suite: 88 passed, 1 skipped;
- production build: passed;
- changed-file lint: passed;
- changed-file diagnostics: clean;
- `git diff --check`: passed;
- repository typecheck retains the documented baseline diagnostics.

The review archive does not contain `node_modules`, so the architect could not
rerun Vitest directly from the supplied ZIP. The implementation and test source
were inspected directly.

Live authenticated Shopify/Redis refresh verification remains outstanding and
is intentionally delegated to `ARCH-003-SYSTEM-TEST-002`.

### Architecture Conformance

Conforms.

No database migration, queue mutation control, global Redis scan, browser-side
Redis access, cross-tenant selection parameter, or automatic merchant polling
was introduced.

### Result

`ARCH-003-SHOPIFY-002` is Complete.

`ARCH-003-SYSTEM-TEST-002` is promoted to Ready for integrated live
verification.
