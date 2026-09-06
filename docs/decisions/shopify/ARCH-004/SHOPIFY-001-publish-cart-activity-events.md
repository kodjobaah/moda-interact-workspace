---
id: ARCH-004-SHOPIFY-001
architecture_id: ARCH-004
title: Publish Shopify cart activity events
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: complete
priority: 30
executor: copilot
claimed_at: 2026-09-05T17:19:05Z
attempt: 1
depends_on:
  - ARCH-004-SHARED-002
enables:
  - ARCH-004-SYSTEM-TEST-001
created: 2026-09-05
updated: 2026-09-05
---

# Publish Shopify cart activity events

## Objective

Stop discarding Shopify `carts/create` and `carts/update` webhooks and publish
their minimal recovery-relevant activity into the existing `checkout-events`
BullMQ queue.

## Current state

The Shopify application is already subscribed to:

```text
carts/create
carts/update
```

but the ingress currently classifies cart topics as unsupported and acknowledges
them without publication.

## Shared package

Adopt the package version accepted/published by:

```text
ARCH-004-SHARED-002
@modainteract/moda-interact-shared@0.6.0
```

Do not locally duplicate the shared schema.

## Normalization

Support:

```text
CARTS_CREATE
CARTS_UPDATE
```

Normalize only recovery-relevant data.

Canonical payload:

```text
cartToken
isEmpty
```

Use the provider's stable cart token field established by the actual Shopify
webhook payload/fixture.

Do not infer a token from customer information.

`isEmpty` must be:

```text
true
```

only when the provider payload proves there are zero cart line items;

```text
false
```

when it proves one or more items exist;

```text
null
```

when emptiness cannot safely be established.

Do not reject an otherwise valid cart activity event merely because emptiness
is unknown.

## Activity time

Do not duplicate activity timestamp inside the cart payload.

Use the existing canonical event envelope:

```text
occurredAt
receivedAt
```

Background will derive:

```text
activityAt = occurredAt ?? receivedAt
```

## Publication

Publish using:

```text
eventType = cart.activity
queue     = checkout-events
jobName   = cart-activity
```

Reuse the existing webhook publication timeout, retry and tenant-readable job-ID
semantics.

Publication remains lightweight.

## Observability

Cart activity should no longer be recorded as a generic ignored cart topic.

Record the same bounded ingress outcomes used for other supported commerce
events:

```text
ENQUEUED
DUPLICATE
REJECTED_...
publication failure
```

Do not log cart contents or customer PII.

## Acceptance criteria

- [ ] carts/create produces canonical `cart.activity`.
- [ ] carts/update produces canonical `cart.activity`.
- [ ] event carries canonical tenant identity.
- [ ] valid cart token is required.
- [ ] empty/non-empty/unknown semantics are tested.
- [ ] event goes to `checkout-events`; no new queue exists.
- [ ] tenant-readable job ID behaviour is preserved.
- [ ] duplicate delivery remains idempotent.
- [ ] unsupported/malformed cart payload cannot publish malformed events.
- [ ] ingress remains fast and retryable publication failures return the
      existing failure semantics.
- [ ] no cart/customer PII is added to logs/event payload beyond cartToken.
- [ ] focused/full tests, build/lint/diff checks pass subject to documented
      repository baseline.

## Completion Report

### Status

Ready for architect review.

### Implementation

- Adopted `@modainteract/moda-interact-shared@0.6.0` in `package.json` and
  `package-lock.json`.
- Added strict cart normalization using Shopify's stable `token` field.
- Classified `CARTS_CREATE` and `CARTS_UPDATE` as `cart.activity` events.
- Preserved `isEmpty` as `true`, `false`, or `null` based only on whether
  `line_items` is present and provable.
- Published `cart-activity` jobs to the existing `checkout-events` queue with
  the existing timeout, retry, duplicate, and tenant-readable job-ID logic.
- Preserved canonical tenant identity and envelope activity timestamps without
  adding cart contents or customer PII.

### Validation

- Focused webhook tests: 37 passed.
- Full Shopify app tests: 96 passed, 1 skipped.
- Production build: passed.
- Typecheck: baseline failure in unrelated existing JSX/routes; no errors were
  reported for the touched webhook files.
- Lint: baseline failure in unrelated existing files plus the new queue test's
  existing `process` global rule; no cart implementation lint error.

### Files Changed

- `app/services/webhooks/cart-activity-normalization.ts`
- `app/services/webhooks/shopify-webhook-ingress.service.ts`
- `app/services/webhooks/shopify-webhook-queue.server.ts`
- `tests/unit/webhooks/shopify-normalization.test.js`
- `tests/unit/webhooks/shopify-webhook-ingress.service.test.js`
- `tests/unit/webhooks/shopify-webhook-queue.server.test.js`
- `package.json`
- `package-lock.json`

### VCS Note

No commit or push performed. Existing unrelated working-tree changes were left
untouched.

## Architect Review

### Review Status

Accepted

### Review Notes

Architect reviewed the supplied Shopify workspace archive directly.

Accepted implementation:

```text
carts/create
carts/update
    |
    v
cart.activity
    |
    v
checkout-events
jobName = cart-activity
```

The implementation:

- adopts `@modainteract/moda-interact-shared@0.6.0`;
- normalizes Shopify's cart `token` into canonical `cartToken`;
- derives `isEmpty` only from provable `line_items` state:
  `true`, `false`, or `null`;
- publishes only the minimal canonical cart payload;
- preserves tenant identity and canonical envelope timestamps;
- uses the accepted collision-safe cart ordering key;
- reuses the existing checkout-events queue rather than introducing a new
  queue;
- preserves tenant-readable webhook job IDs and legacy/new job-ID duplicate
  checks;
- preserves the existing bounded publication timeout/retry semantics;
- records cart events through the supported ingress outcome path rather than
  treating them as ignored;
- does not add cart contents/customer PII to the canonical event.

Current Shopify webhook documentation was also checked during architect review:
the current `carts/create` and `carts/update` sample payloads use `token` as the
cart token and expose `line_items`, matching the implementation assumptions.

### Validation Reviewed

Implementing-agent evidence:

- focused webhook tests: 37 passed;
- full Shopify application tests: 96 passed, 1 skipped;
- production build: passed;
- touched TypeScript files: no editor diagnostics;
- typecheck: repository baseline failures outside touched webhook files;
- lint: repository baseline failures; the reported `process` globals in the
  queue test pre-date this task;
- task resolver: `review`;
- no commit or push performed.

The architect additionally compared the reported queue-test lint locations
against the published baseline and confirmed both `process.env.REDIS_URL`
usages already existed before ARCH-004-SHOPIFY-001.

### Architecture Conformance

Conforms.

### Result

`ARCH-004-SHOPIFY-001` is Complete.

No additional Shopify ARCH-004 task is promoted by this acceptance alone.
`ARCH-004-SHOPIFY-002` remains dependency-gated by
`ARCH-004-BACKGROUND-002`.

`ARCH-004-BACKGROUND-001` remains the parallel executable implementation path
after SHARED-002 acceptance.

