---
id: ARCH-003-ADMIN-015
architecture_id: ARCH-003
title: Add bounded shop and status queue-job reader API
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 44
executor: copilot
claimed_at: 2026-09-04T22:22:32Z
attempt: 1
depends_on:
  - ARCH-003-ADMIN-011
enables:
  - ARCH-003-ADMIN-016
created: 2026-09-04
updated: 2026-09-04
---

# Add bounded shop and status queue-job reader API

## Objective

Introduce a protected, read-only queue-job list contract that can browse jobs
by:

```text
Shop -> Status -> Direction
```

without exposing raw payload data in the list response.

Initial supported statuses are:

```text
failed
active
```

Waiting/delayed are intentionally not part of this task.

## Required API shape

Add a new generic Admin route rather than weakening the existing failed-only
route:

```text
GET /api/admin/queues/jobs
```

Supported query parameters:

```text
queue=<allowlisted queue>
status=failed|active
shop=*|__orphan__|<normalized shop value>
page=<bounded positive integer>
limit=<bounded positive integer>
direction=asc|desc
```

Defaults:

```text
status=failed
shop=*
page=1
limit=10
direction=desc
```

The old `/api/admin/queues/failed` route may remain for compatibility during the
migration. Do not silently change its contract.

## Shop identity contract discovery

Before implementing filtering, identify the actual explicit shop association
present in current queue-job payloads.

Preferred evidence order:

1. read the existing queue producer contracts/code in the workspace, read-only;
2. if producer shape is not sufficient, inspect a small live Redis sample using
   a safe diagnostic.

The diagnostic must never dump full payloads.

For each observed queue/job type, record only:

```text
queue name
job name
shop field path used
shop found: yes/no
```

A normalized shop domain/value may be logged if needed. Do not emit unrelated
customer data, message content, tokens, phone numbers, addresses, or full job
data.

## Shop extraction rules

Create one conservative Admin-local shop projection function, conceptually:

```text
extractQueueJobShop(queueName, jobName, data) -> string | null
```

Rules:

- use only explicit, documented shop/domain fields from the real producer
  contract;
- do not recursively search arbitrary payload strings;
- do not infer shop from customer email, phone, checkout URL, job ID, or other
  indirect fields;
- trim and case-normalize a valid string;
- missing, blank, malformed, or unsupported shop association => `null`.

`null` means:

```text
Orphan / No shop
```

A job with a non-empty explicit shop value remains associated with that value
even if the tenant is no longer present in the Admin database. That is not the
same as a no-shop orphan.

## Shop filter semantics

Use:

```text
*             -> all jobs, including orphans
__orphan__    -> only jobs where projected shop is null
<shop value>  -> exact normalized shop match
```

Return `shop` on every list row as:

```text
string | null
```

Do not return the raw job payload.

## Shop filter options

The client needs stable shop choices before choosing a status.

Provide a bounded queue-level shop facet capability, either within the same API
response or a protected companion route.

The facet source must consider both supported statuses:

```text
failed + active
```

and return unique normalized shop values plus whether orphan jobs were observed.

Conceptual result:

```json
{
  "shops": [
    {"value": "alpha.myshopify.com", "label": "alpha.myshopify.com"},
    {"value": "beta.myshopify.com", "label": "beta.myshopify.com"}
  ],
  "hasOrphans": true,
  "scanTruncated": false
}
```

Do not pretend the facet list is exhaustive if a bounded scan ceiling is hit.

## Job summary model

The generic list model should contain only operational list fields:

```text
id
queueName
name
status
shop
attemptsMade
eventAt
failedReason
```

`failedReason` is populated only where relevant.

`eventAt` is status-aware:

```text
failed -> finishedOn, then processedOn, then timestamp
active -> processedOn, then timestamp
```

Sort by `eventAt`, then `id` as a deterministic tie-breaker.

Direction is the only sort control in this new workflow.

## Pagination

Filtering occurs before pagination.

Keep scans bounded. The response must distinguish a known bounded total from a
truncated scan.

Return enough metadata for truthful navigation, for example:

```text
page
limit
hasPrevious
hasNext
knownTotal: number | null
scanTruncated: boolean
```

If the scan ceiling is reached, do not report an exact total beyond what was
actually observed.

## Security / boundaries

- platform-admin authorization must occur before queue access;
- queue names remain allowlisted;
- status is allowlisted to `failed|active`;
- shop is a filter value only and must never become a Redis key selector;
- no payload, stacktrace, Redis URL, environment values, or credentials in the
  list response;
- no mutation operations;
- preserve bounded fail-fast Redis behavior.

## Work Items

- [x] Inspect actual producer/live job shop field paths safely.
- [x] Add explicit tested shop projection rules.
- [x] Add generic failed/active queue-job list reader.
- [x] Add shop facet discovery with orphan support.
- [x] Add bounded status/shop/direction/page parsing.
- [x] Add protected generic API route(s).
- [x] Add pagination/truncation metadata.
- [x] Add focused orphan/shop/status/security tests.
- [x] Run full Admin validation.
- [x] Return to `review` and STOP.

## Acceptance Criteria

- [x] Failed and Active are supported; no other states are accepted.
- [x] Shop filtering supports All, a concrete shop, and Orphan / No shop.
- [x] Missing shop is never silently discarded.
- [x] Shop extraction does not use fuzzy payload inference.
- [x] Each list row includes explicit `shop: string | null`.
- [x] Raw payload and stacktrace are absent from list responses.
- [x] Shop facets consider failed + active jobs and report truncation truthfully.
- [x] Direction defaults to Descending.
- [x] Pagination is bounded and truthful.
- [x] Existing failed-only APIs are not silently weakened.
- [x] Full tests/typecheck/lint/build/`git diff --check` pass.

## Completion Report

### Status
Ready for architect review.

### Implemented Files

- `moda-interact-admin/src/lib/admin/queue-monitor.ts`
- `moda-interact-admin/src/app/api/admin/queues/jobs/route.ts`
- `moda-interact-admin/tests/security/admin-queue-jobs.test.mjs`

### Producer Contract Evidence

- `checkout-events` / `checkout-created`: `data.tenant.shopDomain`, found.
- `checkout-events` / `checkout-updated`: `data.tenant.shopDomain`, found.
- `order-events` / `order-completed`: `data.tenant.shopDomain`, found.
- `pending-recovery-candidates` / `Pending recovery candidates`: only `data.shopId`, no documented domain, treated as orphan.
- `whatsapp-events` / `WhatsApp events`: no documented shop domain, treated as orphan.

Only the explicit documented Shopify tenant domain is projected. Unsupported,
missing, blank, and malformed values become `shop: null`; no fuzzy payload
inference is used.

### Validation

- Focused ADMIN-015 tests: 5 passed.
- Full Admin tests: 65 passed.
- `npm exec tsc -- --noEmit`: passed.
- `npm run lint`: passed with two pre-existing `react-hooks/exhaustive-deps` warnings in `src/components/admin/queue-monitor.tsx`.
- `npm run build`: passed; existing warnings for workspace-root inference and optional BullMQ `@valkey/valkey-glide` resolution remain.
- `git diff --check`: passed.

### Assumptions and Deviations

- Queue scans are bounded at 1,000 jobs per status; `knownTotal` is `null` and truncation is reported when the ceiling is reached.
- Facets scan both `failed` and `active` for the selected allowlisted queue.
- The existing `/api/admin/queues/failed` contract and reader remain unchanged.

### Unresolved Issues

None blocking this review handoff.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 is architect-accepted Complete.

The source implementation remains additive to the previously accepted queue
snapshot path and introduces the new bounded generic queue-job list contract
without weakening the legacy failed-only contracts.

Live developer verification after restarting/using the final working tree
confirmed:

```text
GET /api/admin/queues
  -> HTTP 200
  -> 4 queues

GET /api/admin/queues/jobs
  queue=checkout-events
  status=failed
  shop=*
  page=1
  limit=10
  direction=desc
  -> HTTP 200
  -> 10 rows returned
  -> knownTotal=12
  -> hasNext=true
  -> hasOrphans=true
```

The returned historical checkout jobs had `shop: null`, which is correct for
jobs that do not expose a supported explicit shop association. The agent did
not infer tenant identity from job IDs or unrelated payload fields.

The developer also live-verified:

- `status=active` returns the normal bounded response contract;
- `shop=__orphan__` returns the explicit orphan subset correctly.

### Reviewed Files / Evidence

- `moda-interact-admin/src/lib/admin/queue-monitor.ts`
- `moda-interact-admin/src/app/api/admin/queues/jobs/route.ts`
- `moda-interact-admin/tests/security/admin-queue-jobs.test.mjs`
- ADMIN-015 Completion Report
- live `/api/admin/queues` HTTP 200 / four-queue proof
- live failed queue-job list response
- developer confirmation of Active and explicit orphan filtering

### Validation Reviewed

Implementing-agent evidence records:

- focused ADMIN-015 tests: 5 passed;
- full Admin tests: 65 passed;
- TypeScript: pass;
- lint: pass with two pre-existing hook warnings;
- production build: pass;
- `git diff --check`: pass.

### Architecture Conformance

Accepted.

The implementation remains read-only, bounded, allowlisted, payload-redacted at
list level, and preserves truthful orphan/truncation behavior.

### Follow-up

`ARCH-003-ADMIN-016` is now Ready.

A separate ARCH-004 initiative now owns future producer-side tenant-identifiable
Shopify BullMQ job metadata. It is not a blocker for ADMIN-016 because the
current Admin reader already supports legacy/orphan jobs and current canonical
`data.tenant.shopDomain` jobs.
