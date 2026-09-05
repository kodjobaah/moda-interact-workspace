---
id: ARCH-003
title: Admin operational queue observability UI
status: in_progress
coordinator: moda_architect
created: 2026-09-04
updated: 2026-09-04
---

# ARCH-003: Admin operational queue observability UI

## Status

In Progress.

The queue-observability foundation, live Redis integration, sidebar, queue
table, and resizable queue-details overlay are architect-accepted.

Current authoritative remaining sequence:

```text
ARCH-003-ADMIN-015   Complete
        |
        v
ARCH-003-ADMIN-016   Complete
        |
        v
ARCH-003-ADMIN-012   Ready
        |
        v
ARCH-003-ADMIN-013   Pending
```

`ARCH-003-ADMIN-009` remains Superseded.

ARCH-003 closes only after ADMIN-016, ADMIN-012, and ADMIN-013 are each
implemented, returned to architect review, and accepted.

## Problem

The Admin UI now has enough Redis/BullMQ connectivity to expose live queue
signals, but the current presentation is not aligned with the intended product
shape.

`Tenant Directory` is intended to remain a concise operational overview for
platform administrators, yet the current in-page queue monitor occupies too much
space and makes the screen feel cluttered.

At the same time, administrators need a practical read-only workflow for
observing queue health and understanding job failures without leaving the Admin
product and opening a raw Redis UI.

## Goals

- keep `Tenant Directory` clean and overview-oriented;
- retain the four compact queue-activity overview cards created by
  `ARCH-003-ADMIN-001`;
- observe the four current BullMQ queues:
  - `checkout-events`
  - `order-events`
  - `pending-recovery-candidates`
  - `whatsapp-events`;
- show only current **active** job counts in the Tenant Directory overview;
- move operational queue inspection to `Observability > Shopify Queues`;
- preserve read-only access only;
- allow an administrator to inspect failed jobs for a selected queue;
- allow sorting the failed-job list by failure-oriented fields;
- allow selecting one failed job and viewing detailed BullMQ diagnostic data;
- keep the entire solution confined to `moda-interact-admin`.

## Non-Goals

- retrying, requeueing, deleting, pausing or resuming jobs;
- changing producer/consumer application behavior in Shopify, Background,
  Messaging, or Gateway services;
- database schema changes or persistent user preferences;
- Render Blueprint changes;
- introducing a separate observability backend;
- exposing Redis credentials, environment values or unrelated infrastructure
  secrets.

## Architecture decisions

### Screen separation

The Admin IA becomes:

```text
Tenant Directory
  - Active Tenants
  - Active Recoveries (Now)
  - Four queue overview cards showing active jobs only
  - Tenant table

Observability
  - Shopify Queues
      - compact table of queue metrics for the four queues
      - refresh controls
      - failed-job browser for a selected queue
      - failed-job detail panel for a selected job
  - existing Grafana entry
```

The large queue-monitor card must be removed from `Tenant Directory` after the
compact overview cards exist.


### Left navigation shell parity

The approved reference includes a substantially richer left navigation shell
than the current implementation.

Approved visual characteristics include:

- persistent Moda Interact brand/header at the top;
- vertically stacked icon + label navigation;
- Observability rendered as a grouped/expanded parent rather than one flat link;
- indented child destinations:
  - Overview
  - Shopify Queues
  - Grafana;
- clear active child treatment for Shopify Queues;
- administrator identity/profile treatment anchored at the bottom;
- stable sidebar width and spacing while queue details open on the right.

The reference also visibly contains Dashboard, Billing, and Settings entries.
At the time of this architecture correction, the current Admin repository has
no corresponding application routes for those destinations.

ARCH-003 must **not** create dead or fabricated links merely for screenshot
similarity. ADMIN-010 must make the existing shell and Observability hierarchy
match the reference, and must record the absence of Dashboard/Billing/Settings
as an explicit visual-parity deviation. Real implementation of those product
destinations requires separately scoped architecture/tasks if desired.

### Queue scope

ARCH-003 observes:

```text
checkout-events
order-events
pending-recovery-candidates
whatsapp-events
```

`checkout-events` and `order-events` continue to use existing shared queue
contract information where useful.

Additional queue identities required only for Admin read-only observability may
remain Admin-owned configuration because ARCH-003 does not change producer or
consumer runtime contracts.

### Tenant Directory overview

The four overview cards show only the current BullMQ `active` count for each
queue.

They do not show failed, waiting, delayed or worker counts and they do not carry
visible refresh controls.

### Detailed queue screen

`Observability > Shopify Queues` is the operational diagnosis screen.

It provides:

- four queue summary rows;
- queue-level metrics;
- refresh interval selection;
- manual refresh;
- queue selection/read-only details action;
- queue-scoped failed-job browsing;
- selection of one failed job;
- a separate detailed job inspection view.

### Failed-job list

Failed jobs are retrieved through a bounded Admin server reader/API.

The list UI is a separate task from the server reader so Luna does not need to
solve Redis access, sorting semantics and UI state in one execution.

The failed-job browser must:

- clearly identify the selected queue;
- default to most recently failed first;
- support bounded sorting by approved fields;
- make one failed row selectable;
- remain read-only.

### Failed-job detail

Selected-job retrieval is also separated from its UI.

The server detail model should expose, at minimum:

```text
id
queueName
name
state
attemptsMade
timestamp
processedOn
finishedOn
failedReason
stacktrace
data
```

Additional safe BullMQ metadata may be included only where it materially aids
operational diagnosis.

The UI may render large stack trace / JSON values in scrollable or collapsible
regions and may provide copy controls.

The UI must not expose Redis URLs, environment variables or unrelated secrets.

## Approved visual reference

The visual/interaction target for the Shopify Queues screen is stored at:

`docs/architecture/ARCH-003-shopify-queues-approved-reference.png`

This image is an **acceptance reference**, not a loose inspiration.

The important approved composition is:

```text
Admin shell / left sidebar
  -> preserve Moda Interact branding
  -> use the approved persistent vertical navigation composition
  -> Observability is an expandable/grouped section exposing:
       Overview
       Shopify Queues
       Grafana
  -> selected child route has a clear nested active state
  -> administrator identity/profile treatment is anchored at the bottom

Shopify Queues main area
  -> breadcrumb/title/subtitle
  -> queue summary table
  -> refresh controls
  -> selected queue row remains visibly selected

Selecting View details
  -> right-hand Queue details drawer
       queue name + job labels
       worker-online indicator
       current metrics
       queue information
       recent failed jobs
       refresh failed-job list
       route into all failed jobs / selected failed-job diagnostics
```

The existing protected APIs, queue readers, sorting rules, failed-state guard,
and read-only security boundaries must be reused.

The current implementation's inline failed-job browser/detail sections below the
queue table are **not** the approved final composition.

The mockup also contains illustrative top-level entries such as Dashboard,
Billing, and Settings. Those must not be added as dead/fabricated navigation
destinations by ARCH-003. Only navigation backed by the current Admin product
or explicitly created within these corrective tasks may be rendered.

## Repository responsibilities

All ARCH-003 implementation remains confined to:

```text
repository: moda-interact-admin
assigned_agent: moda_admin
```

No ARCH-003 task authorises another repository change.

## Execution plan

```text
ARCH-002-ADMIN-011
        |
        v
ARCH-003-ADMIN-001   [Complete]
        |
        v
ARCH-003-ADMIN-002   [Complete] Move diagnostics to Observability page shell
        |
        v
ARCH-003-ADMIN-008   [Complete] Fix queue overview cold-connection readiness
        |
        v
ARCH-003-ADMIN-003   [Complete] Present four queues in compact summary table
        |
        v
ARCH-003-ADMIN-004   [Complete] Add bounded failed-job server reader/API
        |
        v
ARCH-003-ADMIN-005   [Complete] Add sortable failed-job browser UI
        |
        v
ARCH-003-ADMIN-006   [Complete] Add selected failed-job server detail reader
        |
        v
ARCH-003-ADMIN-007   [Complete] Add failed-job detail panel UI
```


### Visual parity correction

```text
ARCH-003-ADMIN-007   [Complete]
        |
        v
ARCH-003-ADMIN-010   [Complete] Align Admin sidebar shell and Observability navigation
        |
        v
ARCH-003-ADMIN-014   [Complete] Fix detailed queue snapshot cold readiness
        |
        v
ARCH-003-ADMIN-011   [Complete] Recompose Shopify Queues into resizable overlay drawer
        |
        v
ARCH-003-ADMIN-015   [Ready] Add shop/status queue-job list API
        |
        v
ARCH-003-ADMIN-016   [Pending] Add active/failed selected-job detail API
        |
        v
ARCH-003-ADMIN-012   [Pending] Populate queue drawer metrics + filtered recent jobs
        |
        v
ARCH-003-ADMIN-013   [Pending] Integrate paginated filtered queue-job diagnostics
```

## Tasks

| Task | Owner | Status | Depends On |
|------|-------|--------|------------|
| ARCH-003-ADMIN-001 | moda_admin | Complete | ARCH-002-ADMIN-011 |
| ARCH-003-ADMIN-002 | moda_admin | Complete | ARCH-003-ADMIN-001 |
| ARCH-003-ADMIN-008 | moda_admin | Complete | ARCH-003-ADMIN-002 |
| ARCH-003-ADMIN-003 | moda_admin | Complete | ARCH-003-ADMIN-008 |
| ARCH-003-ADMIN-004 | moda_admin | Complete | ARCH-003-ADMIN-003 |
| ARCH-003-ADMIN-005 | moda_admin | Complete | ARCH-003-ADMIN-004 |
| ARCH-003-ADMIN-006 | moda_admin | Complete | ARCH-003-ADMIN-005 |
| ARCH-003-ADMIN-007 | moda_admin | Complete | ARCH-003-ADMIN-006 |

| ARCH-003-ADMIN-010 | moda_admin | Complete | ARCH-003-ADMIN-007 |
| ARCH-003-ADMIN-014 | moda_admin | Complete | ARCH-003-ADMIN-010 |
| ARCH-003-ADMIN-011 | moda_admin | Complete | ARCH-003-ADMIN-010, ARCH-003-ADMIN-014 |
| ARCH-003-ADMIN-015 | moda_admin | Ready | ARCH-003-ADMIN-011 |
| ARCH-003-ADMIN-016 | moda_admin | Pending | ARCH-003-ADMIN-015 |
| ARCH-003-ADMIN-012 | moda_admin | Pending | ARCH-003-ADMIN-016 |
| ARCH-003-ADMIN-013 | moda_admin | Pending | ARCH-003-ADMIN-012 |

## Rollout / handoff

Architect acceptance history:

- `ARCH-003-ADMIN-001`: Complete after Attempt 3.
- `ARCH-003-ADMIN-002`: Complete after Attempt 1.
- `ARCH-003-ADMIN-008`: Complete after Attempt 2.
- `ARCH-003-ADMIN-003`: Complete after Attempt 1.
- `ARCH-003-ADMIN-004`: Complete after Attempt 1.
- `ARCH-003-ADMIN-005`: Complete after Attempt 1.
- `ARCH-003-ADMIN-006`: Complete after Attempt 2.
- `ARCH-003-ADMIN-007`: Complete after Attempt 1.

`ARCH-003-ADMIN-010` is architect-accepted Complete after Attempt 1.

`ARCH-003-ADMIN-014` is architect-accepted Complete after Attempt 2.

`ARCH-003-ADMIN-011` is Ready for Attempt 2 and is the only executable corrective task.

`ARCH-003-ADMIN-011` remains in Review pending runtime/visual verification after ADMIN-014.

The completed architecture delivers:

```text
Tenant Directory
  -> concise tenant KPIs
  -> four active-job queue KPIs

Observability > Shopify Queues
  -> four-queue operational summary
  -> refresh controls
  -> bounded sortable failed-job browser
  -> protected selected failed-job detail
  -> lifecycle / failure / stacktrace / job data
  -> read-only operation throughout
```

`ARCH-003` is Complete.


## Reopen decision

ARCH-003 is reopened because the approved visual reference was not converted
into explicit task-level layout acceptance criteria during the original
decomposition.

The functional implementation remains valid. The corrective sequence is
presentation/interaction work only unless a tiny existing UI-facing model
addition is explicitly required by an individual task.

ARCH-003 must not return to Complete until the Shopify Queues screen is compared
against `ARCH-003-shopify-queues-approved-reference.png` and the approved
table-plus-right-drawer composition is visibly present.


## ADMIN-010 acceptance

ADMIN-010 is architect-accepted Complete after Attempt 1.

The accepted shell provides the branded persistent sidebar, nested
Observability hierarchy, active child state, Grafana fallback behavior, and
bottom administrator role treatment. Dashboard/Billing/Settings remain
intentionally absent because no real destinations exist.

`ARCH-003-ADMIN-011` is now Ready.


## Detailed snapshot runtime prerequisite

Current runtime evidence after ADMIN-011 shows the Shopify Queues screen in an
unavailable/no-snapshot state. Source inspection identified that
`readQueueMonitorSnapshot()` still issues detailed BullMQ and raw Redis commands
against lazy fail-fast readers before explicitly establishing readiness.

`ARCH-003-ADMIN-014` owns this bounded runtime correction. It must not fabricate
queue data or weaken fail-fast Redis settings.

ADMIN-011 remains in Review until ADMIN-014 is accepted and the drawer can be
visually exercised against the approved reference.


## Drawer overlay clarification

The Queue details drawer is a **true overlay**, not a split-pane layout.

On desktop, opening the drawer must not reduce the queue table's layout width.
A normal-flow flex/grid sibling is not acceptable.

The rejected implementation is documented at:

`docs/architecture/ARCH-003-ADMIN-011-rejected-inflow-drawer.png`

The drawer should be independently fixed/portal-positioned on the right,
full-height, opaque, elevated, and internally scrollable.

## Failure-list density and pagination

The queue-summary drawer shows at most the 5 most recent failures.

`View all failed jobs` transitions to a paginated full-list workflow:

```text
default page size: 10
Previous | Page X of Y | Next
```

Queue/sort/direction changes reset to page 1. Pagination must reuse the bounded
ADMIN-004 API contract and must not make false exact-total claims when the
server's bounded scan ceiling is reached.


## ADMIN-011 resizable overlay clarification

The accepted final Queue details interaction is not a fixed-width 560px drawer.

On open, the panel fills the entire Admin workspace to the right of the visible
sidebar and the full viewport height. On mobile it fills the entire viewport.

On desktop it is resizable from the left edge:

```text
min width: approximately 28rem
max width: full available workspace
default on every open: max/full workspace
```

Resizing is overlay-only and must never alter the queue table's layout width.

A keyboard-accessible resize affordance and a Maximize/reset control are
required.

Pagination remains separate:

- ADMIN-012 summary: at most 5 recent failures;
- ADMIN-013 full browser: default 10 rows/page with Previous/Page/Next.


## ADMIN-011 final acceptance

ADMIN-011 is architect-accepted Complete after Attempt 4.

The Queue details overlay now provides:

- full-workspace initial open;
- true fixed overlay with zero table reflow;
- pointer and keyboard resizing;
- Maximize/reset;
- queue-name selection;
- preserved narrowed width while switching queues;
- fresh-open maximization.

## Shop / Status queue-job browsing

The diagnostic browser is no longer failed-only.

The accepted filter order is:

```text
Shop | Status | Direction
```

Defaults:

```text
All shops | Failed | Descending
```

Initial Status choices:

```text
Failed
Active
```

This architecture deliberately does not add Waiting/Delayed yet.

### Shop association

Every queue-job list row projects:

```text
shop: string | null
```

The projection must use explicit producer-contract fields only.

A missing/blank/unsupported shop association becomes:

```text
null -> Orphan / No shop
```

No fuzzy inference from customer data, URLs, phone numbers, job IDs, or arbitrary
nested strings is permitted.

A non-empty explicit shop value remains a concrete shop even if the current
tenant database no longer contains that shop.

### Filter choices

Shop:

```text
All shops
<bounded discovered shop values>
Orphan / No shop
```

Status:

```text
Failed
Active
```

Direction:

```text
Descending
Ascending
```

The server supplies bounded shop facets across both supported statuses and must
report when the facet scan is truncated.

### List and detail boundaries

ADMIN-015 introduces a new generic protected queue-job list API. It leaves the
existing failed-only route intact during migration.

ADMIN-016 introduces a generic selected-job detail API for Failed and Active.
The requested status must match the current BullMQ state; state races return the
same safe not-found contract.

### Density and pagination

ADMIN-012 shows at most 5 recent jobs matching the current Shop/Status filters.

ADMIN-013 provides the full browser:

```text
default page size: 10
Previous | Page X of Y | Next
```

Shop/status changes reset pagination to page 1.

Pagination and total metadata must remain truthful under bounded Redis scans.


## ADMIN-015 acceptance

ADMIN-015 is architect-accepted Complete after live verification of:

- the existing four-queue snapshot API;
- failed queue-job listing;
- Active status;
- explicit Orphan / No shop filtering;
- bounded pagination metadata.

`ARCH-003-ADMIN-016` is Ready.

Future producer-side enrichment of Shopify BullMQ jobs is deliberately owned by
the separate ARCH-004 initiative so ARCH-003 does not mutate producer contracts
inside an Admin architecture task.


## Producer tenant metadata clarification

The current canonical Shopify recovery-event envelope already contains:

```text
job.data.tenant.shopId
job.data.tenant.shopDomain
```

ADMIN-015 intentionally projects shop identity from that explicit canonical
shape.

Historical retained queue jobs that predate that envelope may still appear as:

```text
Orphan / No shop
```

This is truthful legacy-data behavior and must not be "fixed" by fuzzy
inference from opaque job IDs or unrelated payload fields.

ARCH-004 separately improves the readability of future Shopify BullMQ `jobId`
values. It does not change the job-data envelope.


## ADMIN-016 acceptance

ADMIN-016 is architect-accepted Complete.

The Admin server now has a generic selected queue-job detail boundary for:

```text
Failed
Active
```

A requested/current BullMQ state mismatch is returned as safe not-found, which
contains races where an Active job moves state between list and detail reads.

The remaining ARCH-003 sequence is:

```text
ADMIN-012   Ready
    -> ADMIN-013   Pending
```


## ADMIN-012 architecture amendment: Waiting and Delayed are first-class job states

Live runtime inspection exposed a missing operational state in the original
ADMIN-015/016/012 design.

Observed on `pending-recovery-candidates`:

```text
WAITING  = 0
ACTIVE   = 0
DELAYED  = 5
FAILED   = 0
```

RedisInsight simultaneously showed retained `pending-recovery-*` jobs.

The queue overview was therefore correct, but the job browser could not show the
jobs because the generic job-list/detail contract only accepted:

```text
failed | active
```

This is an architecture defect, not a Redis defect.

### Corrected status contract

The Admin read-only queue diagnostics contract MUST support:

```text
failed
active
waiting
delayed
```

This applies consistently to:

```text
GET /api/admin/queues/jobs
GET /api/admin/queues/jobs/detail
```

and to the Queue details drawer Status selector.

### Required state behavior

```text
requested state == current BullMQ state
    -> return normalized job

requested state != current BullMQ state
    -> safe not_found for detail reads
```

The existing ADMIN-016 race protection therefore extends unchanged to Waiting
and Delayed.

### List time semantics

Use one truthful sortable `eventAt` per state:

```text
failed
  finishedOn ?? processedOn ?? timestamp

active
  processedOn ?? timestamp

waiting
  timestamp

delayed
  timestamp + max(delay, 0)
```

For Delayed this represents the scheduled execution time rather than merely the
time the job was originally inserted.

### Drawer selector

The Status options are now:

```text
Failed
Active
Waiting
Delayed
```

The default remains:

```text
All shops -> Failed -> Descending
```

### Labels

Failure-specific fixed labels must not survive when another status is selected.

Use:

```text
Recent jobs
View all jobs
```

or an equivalent correctly status-aware heading.

Do not show `View all failed jobs` while Active, Waiting, or Delayed is selected.

### Pending recovery candidates

A pending recovery is normally represented as a BullMQ Delayed job until its
scheduled recovery time.

Therefore:

```text
pending-recovery-candidates + Status=Delayed
```

must return those jobs.

Jobs without a currently supported canonical `shopDomain` remain visible under
`All shops` and render explicitly as:

```text
Orphan / No shop
```

They MUST NOT be hidden merely because shop attribution is absent.

Tenant-attribution enrichment for non-Shopify-envelope jobs is a separate
architectural concern and is not required to make Delayed jobs visible.

### Scope correction

ADMIN-012 may extend the already accepted ADMIN-015/016 generic readers/routes in
`moda-interact-admin` as necessary to implement the four-state read-only
contract.

This amendment does not reopen ADMIN-015 or ADMIN-016 as separate tasks and does
not introduce queue mutation.


## ADMIN-012 acceptance and final ARCH-003 task

ADMIN-012 Attempt 1, including Waiting/Delayed Amendment 001, is
architect-accepted Complete.

The final ARCH-003 implementation task is now:

```text
ARCH-003-ADMIN-013   Ready
```

ADMIN-013 owns the final paginated queue-job drawer workflow, all four job
states, and the final screenshot-level runtime comparison.

The delayed pending-recovery screenshot that was previously requested from
ADMIN-012 is explicitly deferred into ADMIN-013 final visual acceptance.


## Architecture scope correction — fold tenant-attribution follow-up into ARCH-003

The previously drafted `ARCH-005` split is withdrawn.

The remaining tenant-attribution issues were discovered while completing the
ARCH-003 operational queue UI and directly affect whether that UI represents the
four operational queues truthfully.

They therefore remain part of ARCH-003.

Correct remaining execution after ADMIN-013:

```text
ARCH-003-ADMIN-013
        |
        v
ARCH-003-BACKGROUND-001
        |
        v
ARCH-003-ADMIN-017
        |
        v
ARCH-003-ADMIN-018
        |
        v
ARCH-003-SYSTEM-TEST-001
```

### Remaining queue attribution corrections

`pending-recovery-candidates`:

```text
data.shopId
data.shopDomain
jobId = <shopId>--<existingDeterministicJobId>
```

where the producing background workflow already knows both tenant values.

Admin then projects the explicit `data.shopDomain`.

`whatsapp-events`:

If tenant identity is legitimately unknown at ingress, Admin must represent the
job as:

```text
Unresolved
```

rather than conflating it with:

```text
Orphan / No shop
```

No synchronous tenant-resolution lookup is added to WhatsApp ingress merely for
Admin observability.

### Classification invariant

```text
Known
  explicit normalized shop domain is present

Unresolved
  this queue boundary legitimately permits tenant identity to be unknown

Orphan / No shop
  tenant metadata is expected for this job type but is absent or invalid
```

No tenant identity may be guessed from email, phone, URL, opaque job ID, or
arbitrary nested payload strings.

### ARCH-005 withdrawal

`ARCH-005` was an unnecessary architecture split.

It is superseded by this correction and its files must be removed from the
workspace after this overlay is applied so deterministic task resolution does
not retain stale ARCH-005 work.


## ADMIN-013 acceptance

ADMIN-013 Attempt 1 is architect-accepted Complete.

The Admin implementation phase of the queue-details workflow is complete.

The final screenshot showed a truthful Delayed empty state because there were no
delayed jobs at capture time. This does not invalidate ADMIN-013.

The remaining ARCH-003 chain now addresses the tenant-attribution gaps discovered
during live testing:

```text
ARCH-003-BACKGROUND-001   Ready
        |
        v
ARCH-003-ADMIN-017        Pending
        |
        v
ARCH-003-ADMIN-018        Pending
        |
        v
ARCH-003-SYSTEM-TEST-001  Pending
```

The final system test owns the real delayed pending-recovery proof before
ARCH-003 closure.


## BACKGROUND-001 acceptance

`ARCH-003-BACKGROUND-001` is architect-accepted Complete.

New pending-recovery candidates now expose:

```text
data.shopId
data.shopDomain
jobId = <shopId>--<existingDeterministicJobId>
```

without changing recovery scheduling or business behavior.

The remaining ARCH-003 execution chain is:

```text
ARCH-003-ADMIN-017        Ready
        |
        v
ARCH-003-ADMIN-018        Pending
        |
        v
ARCH-003-SYSTEM-TEST-001  Pending
```


## ADMIN-017 acceptance

`ARCH-003-ADMIN-017` is architect-accepted Complete.

New pending-recovery jobs carrying:

```text
data.shopDomain
```

are now projected into the Admin queue diagnostics as their normalized shop.

Historical pending-recovery jobs without that field remain explicitly
`Orphan / No shop`.

The remaining ARCH-003 execution chain is:

```text
ARCH-003-ADMIN-018        Ready
        |
        v
ARCH-003-SYSTEM-TEST-001  Pending
```


## Observability navigation simplification

Live review after ADMIN-018 identified unnecessary navigation duplication.

Final left-navigation contract:

```text
Tenant Directory

Observability
  Shopify Queues
  Grafana
```

There is no `Overview` child.

The Observability parent navigates to:

```text
/observability/queues
```

making Shopify Queues the default operational Observability workspace.

The protected `/observability` route remains available for the existing Grafana
configuration/status fallback, but it must not contain a Shopify Queues
promotional card/CTA.

This final UI correction is owned by `ARCH-003-ADMIN-019`.


## Shopify dashboard Prisma relation correction

Dashboard test-data verification exposed a repository-local Prisma contract
drift in `moda-interact`.

The canonical database relation is:

```text
CheckoutRecovery.conversation
```

but both Shopify dashboard loaders still query:

```text
CheckoutRecovery.conversations
```

and dereference:

```text
recovery.conversations[0]
```

This causes Prisma validation to fail before `/app` can render.

The correction is folded into the existing ARCH-003 execution rather than
creating another architecture identifier.

Task:

```text
ARCH-003-SHOPIFY-001
```

Owner:

```text
moda_app
```

Repository:

```text
moda-interact
```

Design boundary:

```text
Prisma/database relation
    CheckoutRecovery.conversation
              |
              v
Shopify dashboard loader
              |
              v
UI DTO may preserve conversations[] for RecoveryChart compatibility
```

No Prisma schema change or migration is required.

`ARCH-003-SHOPIFY-001` is independently Ready and may execute in parallel with
the remaining Admin task(s). ARCH-003 must not be closed until this correction
has been architect-reviewed if it remains part of the initiative.


## Shopify dashboard conversation correction accepted

`ARCH-003-SHOPIFY-001` is architect-accepted Complete.

The merchant dashboard now uses the canonical singular Prisma relation:

```text
CheckoutRecovery.conversation
```

while preserving the plural UI DTO expected by `RecoveryChart`.

Live `/app` evidence against the generated test dataset shows Usage overview
rendering without the previous Prisma validation failure.

## Merchant active pending-recovery extension

The merchant Usage overview is extended to show the authenticated store's
currently active pending-recovery candidates.

### Architectural constraint

Moda Interact's shared queue can carry high multi-tenant event volume.

The merchant dashboard MUST NOT implement:

```text
scan entire pending-recovery-candidates queue
```

or:

```text
SCAN global Redis keyspace for checkout-index keys
```

for each page request.

That would make one merchant's dashboard query cost proportional to platform
traffic and Redis key cardinality.

### Shop-scoped listing index

Background owns a transient sorted secondary index:

```text
pending-recovery:index:shop:<shopId>
```

Members:

```text
active pending candidate BullMQ job IDs
```

Score:

```text
current candidate scheduled due time (epoch ms)
```

Lifecycle:

```text
candidate scheduled/refreshed
        -> ZADD/update

candidate waiting/active
        -> remains visible

candidate cancelled or matured
        -> ZREM
```

BullMQ remains the execution/source-of-truth boundary. The ZSET exists only to
support efficient tenant-scoped listing and ordering.

No PostgreSQL migration is required.

### Merchant read path

```text
Shopify authenticated request
        |
        v
resolve internal Shop
        |
        v
ZCARD / bounded ZRANGE
pending-recovery:index:shop:<shop.id>
        |
        v
Queue.getJob(page members)
        |
        v
validate:
  job.name
  job state
  data.shopId
  data.shopDomain
        |
        v
safe merchant DTO
        |
        v
Usage overview
  Pending recoveries
```

### Merchant-visible states

```text
BullMQ delayed -> Scheduled
BullMQ waiting -> Waiting
BullMQ active  -> Processing
```

Failed/completed/missing jobs are not active pending candidates and are not
shown.

### Sensitive fields

The browser view must not expose:

```text
checkoutToken
cartToken
abandonedCheckoutUrl
REDIS_URL
Redis key names
raw BullMQ internals
```

The recovery URL embeds recovery credentials and is not a dashboard display
field.

### Availability

Pending-recovery visibility is supplementary to the merchant usage dashboard.

Redis/BullMQ read failure must degrade only that section rather than preventing
current/past usage from rendering.

### Scalability

Per page, the target complexity is proportional to the merchant page size, not
global queue size:

```text
ZCARD                     O(1)
ZRANGE 10 members         bounded shop-local read
Queue.getJob x <= 10      bounded
```

This preserves tenant isolation and avoids global queue/keyspace scans.

### Tasks

```text
ARCH-003-SHOPIFY-001       Complete
        |
        +-----------------------------+
                                      |
ARCH-003-BACKGROUND-001    Complete   |
        |                             |
        v                             |
ARCH-003-BACKGROUND-002    Ready      |
        |                             |
        +-------------+---------------+
                      |
                      v
ARCH-003-SHOPIFY-002       Pending
                      |
                      v
ARCH-003-SYSTEM-TEST-002   Pending
```


## BACKGROUND-002 acceptance

`ARCH-003-BACKGROUND-002` is architect-accepted Complete.

The scalable merchant pending-recovery listing prerequisite is now available:

```text
pending-recovery:index:shop:<shopId>
```

Properties:

```text
type:     Redis ZSET
member:   active pending-candidate BullMQ job ID
score:    scheduled due time
states:   delayed | waiting | active
cleanup:  idempotent ZREM
```

The implementation does not use a global Redis scan or queue scan.

The merchant application task is now executable:

```text
ARCH-003-SHOPIFY-002   Ready
        |
        v
ARCH-003-SYSTEM-TEST-002   Pending
```


## SHOPIFY-002 Amendment 001 — merchant manual refresh

The initial merchant Pending recoveries panel is visually accepted as the
baseline.

Before `ARCH-003-SHOPIFY-002` is accepted Complete, add a lightweight manual
refresh affordance:

```text
Pending recoveries                         <N> active

Last updated HH:mm                         Refresh
```

The merchant screen deliberately does not copy the Admin operational polling
controls.

Architecture:

```text
merchant clicks Refresh
        |
        v
authenticated server-only pending endpoint/loader
        |
        v
same shop-scoped ZSET + BullMQ validation
        |
        v
safe pending DTO only
        |
        v
update Pending recoveries panel
```

Do not re-query unrelated billing/usage data merely to refresh the panel.

Preserve the current pending page where valid. If refresh causes the current
page to exceed the new page count, move to the last valid page.

No automatic polling is introduced.


## SHOPIFY-002 resolver coordination correction

The first Amendment 001 handoff accidentally set:

```text
status: in_progress
claimed_at: null
```

which is not claimable by the authoritative repository resolver.

The task is therefore returned to:

```text
status: ready
executor: null
claimed_at: null
attempt: 1
```

The next repository claim will create execution Attempt 2 for the same
`ARCH-003-SHOPIFY-002` task.

No runtime or architectural scope has changed.


## SHOPIFY-002 Amendment 002 — pagination/local-state synchronisation

Architect review of the manual-refresh implementation exposed a client-state
edge case.

`PendingRecoveries` keeps a local copy of loader data so `useFetcher` can update
only that panel. Normal Previous/Next navigation, however, updates the parent
loader props rather than `fetcher.data`.

The component must therefore support both inputs:

```text
parent loader props
    -> navigation / initial load

fetcher.data
    -> manual panel refresh
```

and keep its rendered page aligned with whichever source most recently supplied
new data.

Required invariant:

```text
URL / parent loader page
        ==
displayed pending page
        ==
page used by the next manual Refresh
```

This is a local Shopify UI-state correction only. The Background index,
shop-scoped read contract, tenant isolation and server-only Redis architecture
remain unchanged.


## SHOPIFY-002 architect acceptance

`ARCH-003-SHOPIFY-002` is architect-accepted Complete.

The merchant Usage overview now has the architecture-approved Pending recoveries
panel:

```text
Pending recoveries                         <N> active
Last updated HH:mm                         Refresh
```

Implementation boundaries:

```text
authenticated merchant
      |
      v
resolved internal Shop
      |
      v
shop-scoped pending ZSET
      |
      v
strict BullMQ/tenant validation
      |
      v
safe merchant DTO
      |
      v
Pending recoveries panel
```

Refresh uses a dedicated authenticated resource loader and updates only the
pending-recovery panel.

Normal Previous/Next navigation and manual Refresh are now state-synchronised:

```text
parent loader props -> local display state
fetcher refresh     -> local display state
```

No merchant auto-polling is introduced.

The remaining integrated gate for this merchant extension is:

```text
ARCH-003-SYSTEM-TEST-002   Ready
```


## SYSTEM-TEST-002 evidence-gate clarification

The merchant pending-recovery system-test task has two distinct stages:

```text
1. implement a deterministic evidence validator
2. validate concrete live developer-owned evidence
```

The validator is support tooling, not a substitute for the integrated proof.

Architect review of Attempt 1 identified that the validator must be tightened
before use:

- require the indexed active candidate to appear in merchant data;
- require it to disappear from both the shop index and merchant view after
  maturity/cancellation;
- explicitly prove page-2 refresh and fallback/subsequent-page behavior;
- prove `Last updated` moves forward chronologically;
- enforce sensitive-field redaction at the browser boundary rather than across
  internal developer evidence.

After the validator correction is accepted, live evidence remains mandatory
before `ARCH-003-SYSTEM-TEST-002` can be marked Complete.


## SYSTEM-TEST-002 validator accepted / live evidence pending

The `ARCH-003-SYSTEM-TEST-002` local evidence validator, including Architect
Amendment 001, is accepted.

The architecture remains open because system-test completion requires concrete
live proof across:

```text
Shopify ingress
  -> Background
  -> pending-recovery-candidates
  -> pending-recovery:index:shop:<shopId>
  -> authenticated merchant dashboard
```

Current state:

```text
ARCH-003-BACKGROUND-001    Complete
ARCH-003-BACKGROUND-002    Complete
ARCH-003-SHOPIFY-001       Complete
ARCH-003-SHOPIFY-002       Complete
ARCH-003-SYSTEM-TEST-002   Blocked — developer live evidence
```

No additional runtime implementation is requested at this point.

The final gate is evidence collection and architect review.


## SHOPIFY-003 accepted

The merchant pending-recovery resource boundary is now explicit JSON:

```text
GET /app/pending-recoveries?pendingPage=n
        |
        v
application/json
        |
        v
{
  pendingRecoveries,
  refreshedAt
}
```

`ARCH-003-SHOPIFY-003` is Complete.

Live integration evidence remains owned by `ARCH-003-SYSTEM-TEST-002`.
