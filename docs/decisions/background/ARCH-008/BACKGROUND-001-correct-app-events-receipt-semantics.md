---
id: ARCH-008-BACKGROUND-001
architecture_id: ARCH-008
title: Correct Shopify App Events receipt and retry semantics
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 20
executor: copilot
claimed_at: 2026-09-09T13:05:47Z
attempt: 1
depends_on:
  - ARCH-007-BACKGROUND-006
  - ARCH-007-BACKGROUND-007
enables:
  - ARCH-008-BACKGROUND-002
created: 2026-09-09
updated: 2026-09-09
---

# ARCH-008-BACKGROUND-001: Correct Shopify App Events receipt and retry semantics

## Architecture

Canonical: `docs/architecture/ARCH-008-shopify-app-pricing-conformance.md`

## Objective

Make App Events transport state exactly match Shopify's asynchronous contract: HTTP `202` means **submitted/received by Shopify**, and HTTP `409` is retryable using the same permanent idempotency key.

## Why this task is deliberately narrow

This task owns **transport semantics only**. It does not redesign recovery-credit entitlement activation; that is `ARCH-008-BACKGROUND-002`.

The inspected baseline currently:

- posts App Events in `src/providers/shopify-app-events.provider.ts`;
- classifies 429, 5xx, 408 and 425 as retryable but not 409;
- marks successful events `REPORTED` in `src/services/shopify-usage-event-publisher.service.ts`;
- writes provider summary text equivalent to `reported`;
- preserves a durable `shopifyIdempotencyKey`.

## Required preflight — do before editing

1. Enter the launcher-resolved ARCH-008-BACKGROUND-001 implementation worktree.
2. Verify the worktree isolation/start-sync evidence required by workspace policy.
3. Verify ARCH-007-BACKGROUND-006/007 capability is present on synchronised source:
   - durable UsageEvent publisher exists;
   - permanent Shopify App Events idempotency key is persisted and reused;
   - App Events provider exists and uses the current versioned endpoint configured by the accepted implementation.
4. If those capabilities are absent after synchronisation, **STOP** and report a prerequisite integration gap to `moda_architect`. Do not recreate ARCH-007 work in this task.
5. Inspect `moda-interact-background/package.json` and confirm the named validation scripts still exist before implementation.

## Primary files

Expected baseline targets:

- `moda-interact-background/src/providers/shopify-app-events.provider.ts`
- `moda-interact-background/src/services/shopify-usage-event-publisher.service.ts`
- existing focused App Events provider/publisher tests under `moda-interact-background/tests/unit/**`

If filenames have been legitimately renamed on current main, follow the accepted implementation to the equivalent ownership boundary; record the actual files in Completion Report. Do not search unrelated repositories.

## Required implementation

### A. Preserve the durable state enum

Do **not** add a new database enum value for “submitted”. Keep:

```text
ShopifyReportState.REPORTED
```

Its ARCH-008 meaning is:

```text
REPORTED = the App Events request was accepted at the transport boundary
           (normally HTTP 202) using the durable event identity.
```

It does **not** mean billing validation/financial confirmation.

Do not rename the database field `reportedAt` in this task.

### B. Classify HTTP 409 as retryable

In `shopify-app-events.provider.ts` (or current equivalent), update the existing response classifier so:

```text
409 -> existing retryable transient category
```

Prefer the existing `transient` error kind rather than introducing a new error-kind enum solely for 409.

The resulting classified error must satisfy the existing publisher retry contract:

```text
retryable = true
needsAttention = false at first response
```

Keep the same permanent event idempotency key on every retry. Do not generate a replacement key after 409.

### C. Make successful provider-summary wording truthful

In the publisher's success path, keep the durable transition to `REPORTED` and existing `reportedAt` field, but replace any provider response summary that implies completed billing (for example `reported`) with the exact neutral transport wording:

```text
submitted-to-shopify-app-events
```

This is an internal bounded summary, not a user-facing sentence.

### D. Do not change pack activation in this task

If the current publisher invokes recovery-credit activation immediately after `markReported`, **leave that call unchanged in BACKGROUND-001**. `ARCH-008-BACKGROUND-002` owns removal/replacement. This separation is intentional so each review has one behavioural outcome.

### E. Preserve existing retry bounds and error categories

Do not redesign:

- retry-attempt counts;
- backoff algorithm except what is already used by the publisher for retryable responses;
- 401 refresh behavior;
- 429 handling;
- 5xx/408/425 handling;
- permanent request/configuration/period/meter handling.

Only make the minimum changes required for 409 and submission semantics.

## Required tests

Add/adjust focused tests proving at minimum:

1. **202 success**
   - provider call succeeds;
   - UsageEvent becomes `REPORTED`;
   - durable idempotency key is unchanged;
   - provider response summary is exactly `submitted-to-shopify-app-events`.
2. **409 Conflict**
   - provider classifies it retryable/transient;
   - publisher does not move directly to `NEEDS_ATTENTION` on the first 409;
   - retry uses exactly the same idempotency key.
3. Existing 429/5xx/non-retryable behavior remains unchanged.

Do not write a test that asserts `REPORTED` means provider billing confirmation.

## Out of Scope / MUST NOT

- Do not remove pack activation yet.
- Do not add schema/migrations.
- Do not change Shopify plan selection.
- Do not create Partner Active Subscription reconciliation.
- Do not change Admin UI.
- Do not add another provider library or endpoint.
- Do not change event economics, quantity or meter handles.
- Do not perform unrelated refactors.

## Acceptance Criteria

- [ ] 409 is retryable through the existing retry path.
- [ ] Retry preserves the permanent App Events idempotency key.
- [ ] 202 success still becomes `REPORTED` but no internal summary calls it billing-confirmed.
- [ ] Successful summary is `submitted-to-shopify-app-events`.
- [ ] No database migration/state enum change is introduced.
- [ ] No entitlement behaviour is deliberately redesigned in this task.
- [ ] Focused provider/publisher tests cover 202 + 409 + identity reuse.
- [ ] Repository validation passes except unchanged documented baseline failures.

## Validation — run from `moda-interact-background`

First identify the exact focused test files changed/added and run them directly with Vitest, for example:

```bash
npx vitest run <focused-provider-test> <focused-publisher-test>
```

Then run:

```bash
npm run test:unit
npm run build
npm run prisma:validate
git diff --check
```

Do **not** invent `npm run lint`; the inspected package does not declare a lint script. If current `package.json` materially differs, use its declared scripts and record the difference.

## Stop / return rule

After Work Items and Validation are complete:

1. complete the task Completion Report;
2. set task status to `review`;
3. return control to `moda_architect`;
4. **STOP**.

Do not start BACKGROUND-002.

## Completion Report

### Status

In Progress

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
