---
id: ARCH-004-SHOPIFY-002
architecture_id: ARCH-004
title: Show last activity for pending recoveries
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: complete
priority: 50
executor: copilot
claimed_at: 2026-09-05T18:17:14Z
attempt: 1
depends_on:
  - ARCH-004-BACKGROUND-002
enables:
  - ARCH-004-SYSTEM-TEST-001
created: 2026-09-05
updated: 2026-09-05T19:30:00Z
---

# Show last activity for pending recoveries

## Objective

Make the merchant Pending recoveries panel describe the new inactivity-clock
semantics accurately.

## Current UI

The first column currently says:

```text
CHECKOUT CREATED
```

Once cart/checkout activity can reschedule the candidate, that timestamp is no
longer the correct operational meaning.

## UI change

Rename the column to:

```text
LAST ACTIVITY
```

Display the candidate's safe:

```text
lastActivityAt
```

alongside the existing:

```text
scheduledFor
status
```

## Reader contract

Extend the pending-recovery reader/browser DTO to expose:

```text
lastActivityAt
```

Do not expose raw job data.

For a rolling deployment containing legacy active candidate jobs without
`lastActivityAt`, display may safely fall back to:

```text
checkoutCreatedAt
```

The fallback is for compatibility/display only and must not redefine new
scheduling semantics.

## Preserve

Keep:

```text
manual Refresh
pagination
page synchronisation/fallback
available/unavailable degradation
tenant validation
Scheduled / Waiting / Processing labels
```

unchanged.

## Sensitive fields

Continue to exclude:

```text
checkoutToken
cartToken
abandonedCheckoutUrl
REDIS_URL
Redis keys
raw job data
opts
stacktrace
```

## Acceptance criteria

- [x] column is `LAST ACTIVITY`.
- [x] new candidate displays `lastActivityAt`.
- [x] scheduled time still comes from authoritative shop index score.
- [x] legacy candidate can fall back safely for display.
- [x] manual Refresh reflects a rescheduled candidate without full-page reload.
- [x] pagination state remains correct.
- [x] no sensitive field exposure regression.
- [x] focused/full tests and build/lint/diff checks pass subject to documented
      baseline.

## Completion Report

### Status

Ready for Review.

### Files Changed

- `moda-interact/app/components/dashboard/PendingRecoveries.jsx`
- `moda-interact/app/services/pending-recovery/pending-recovery-reader.server.ts`
- `moda-interact/tests/unit/pending-recovery-reader.test.ts`

### Work Completed

- Exposed safe `lastActivityAt` in the pending-recovery browser DTO.
- Used the candidate's `lastActivityAt` when present and fell back to
  `checkoutCreatedAt` for legacy candidate jobs.
- Renamed the first panel column to `Last activity` and preserved the existing
  scheduled-for ZSET score, status labels, refresh, pagination, degradation,
  tenant validation, and sensitive-field redaction behavior.
- Added focused coverage for modern activity timestamps and legacy fallback.

### Validation Results

- Focused DTO/display tests: 6 passed.
- Full test suite: 97 passed, 1 skipped.
- `npm run build`: passed.
- `git diff --check`: passed.
- `npm run lint`: baseline failure with 9 unrelated errors and 2 warnings in
  existing onboarding, billing, privacy, and webhook telemetry files.
- `npm run typecheck`: baseline failure from existing implicit-`any` diagnostics
  in `PendingRecoveries.jsx`; the changed behavior itself is covered by the
  passing focused and full test suites.
- No commit or push performed.

### Deviations

None.

### Assumptions

- `lastActivityAt` is a trusted ISO timestamp when present in candidate job
  data; legacy jobs use the existing checkout creation timestamp for display
  compatibility only.

### Unresolved Issues

- Existing repository lint and typecheck baselines remain documented above.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

The architect reviewed the supplied `moda-interact` workspace directly rather
than relying only on the Completion Report.

The implementation is a narrow UI/reader change and conforms to ARCH-004.

### Reviewed Files

```text
app/services/pending-recovery/pending-recovery-reader.server.ts
app/components/dashboard/PendingRecoveries.jsx
tests/unit/pending-recovery-reader.test.ts
app/routes/app.pending-recoveries.jsx
app/routes/app._index.jsx
```

The architect also compared the changed reader/component/tests against the
previous accepted Shopify workspace to confirm the change remained bounded to
the intended capability.

### Architecture Conformance

**Safe DTO — accepted**

The pending-recovery browser DTO now exposes:

```text
lastActivityAt
```

without exposing raw BullMQ job data.

For current candidates:

```text
lastActivityAt = job.data.lastActivityAt
```

For legacy jobs:

```text
lastActivityAt = checkoutCreatedAt
```

The fallback is display-only and does not alter Background scheduling
semantics.

**Authoritative scheduled time — preserved**

`scheduledFor` continues to be derived from the shop-scoped Redis ZSET score:

```text
pending-recovery:index:shop:<shopId>
```

The UI therefore continues to display the schedule maintained by Background
rather than reconstructing it from the activity timestamp.

**Merchant presentation — accepted**

The first table column is now:

```text
Last activity
```

and renders:

```text
item.lastActivityAt
```

while preserving:

```text
Recovery scheduled
Scheduled / Waiting / Processing
manual Refresh
pagination
unavailable degradation
last-updated presentation
```

**Tenant isolation and redaction — preserved**

The reader still requires both authenticated:

```text
shopId
shopDomain
```

to match the candidate before it enters the browser DTO.

The DTO remains an explicit projection and does not expose:

```text
checkoutToken
cartToken
abandonedCheckoutUrl
Redis keys
REDIS_URL
raw job data
BullMQ opts
stacktrace
```

The focused test retains explicit redaction assertions.

**Refresh path — preserved**

The existing `/app/pending-recoveries` refresh route continues to call the same
reader, so a Background reschedule is reflected by manual Refresh without a
full-page reload. No new browser-side scheduling calculation was introduced.

### Validation Reviewed

The Completion Report records:

```text
focused DTO/display tests: 6 passed
full suite: 97 passed, 1 skipped
npm run build: passed
git diff --check: passed
```

`npm run lint` and `npm run typecheck` retain documented pre-existing baseline
diagnostics. Comparison against the previous accepted workspace confirms the
ARCH-004 change itself is limited to the DTO field, display label/value,
PropTypes and focused reader coverage rather than introducing a new lint/type
surface.

No commit or push was performed.

### Follow-up

No correction task is required.

`ARCH-004-SHOPIFY-002` is **Complete**.

All ARCH-004 implementation dependencies required by the system-test task are
now architect-accepted. `ARCH-004-SYSTEM-TEST-001` may therefore become
**Ready**.

Per the architect system-test terminal-gate rule, Ready does not mean it must be
run immediately. The developer may now manually validate the completed
implementation first and invoke the system-test task afterwards.
