---
id: ARCH-003-SHOPIFY-001
architecture_id: ARCH-003
title: Correct Shopify dashboard CheckoutRecovery conversation relation
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: complete
priority: 20
executor: copilot
claimed_at: 2026-09-05T07:51:12Z
attempt: 1
depends_on: []
enables: []
created: 2026-09-05
updated: 2026-09-05T08:59:00Z
---

# Correct Shopify dashboard CheckoutRecovery conversation relation

## Architecture

`docs/architecture/ARCH-003-admin-operational-ui.md`

## Problem

Dashboard test-data verification exposed a runtime Prisma validation failure on
the Shopify merchant dashboard.

The current Prisma schema defines the CheckoutRecovery relationship as singular:

```prisma
model CheckoutRecovery {
  ...
  conversation Conversation?
  statusHistory CheckoutRecoveryStatusHistory[]
}
```

and `Conversation.checkoutRecoveryId` is unique, so a recovery can have at most
one related Conversation.

However the current Shopify dashboard loaders still query an older plural
relation:

```text
conversations
```

Prisma therefore rejects the loader before the dashboard renders:

```text
Unknown field `conversations` for include statement on model `CheckoutRecovery`
```

## Inspected Current Implementation

The stale plural relation is present in exactly these current application
locations:

```text
moda-interact/app/routes/app._index.jsx
moda-interact/app/routes/app.usage.jsx
```

Current main-dashboard query:

```js
include: {
  customer: { ... },
  conversations: {
    include: {
      messages: true,
    },
  },
}
```

Current usage-dashboard query:

```js
include: {
  customer: { ... },
  conversations: {
    include: {
      messages: {
        select: { id: true },
      },
    },
  },
}
```

Both routes also dereference:

```js
recovery.conversations[0]
```

The current component DTO in:

```text
app/components/dashboard/RecoveryChart.jsx
```

still expects a UI property named:

```js
selectedRecovery.conversations
```

That UI DTO name is not itself a Prisma relation and may remain plural.

## Required Change

Update the Prisma loader boundary to use the canonical singular relation:

```js
conversation
```

### Main dashboard

In:

```text
app/routes/app._index.jsx
```

the Prisma include must use:

```js
conversation: {
  include: {
    messages: true,
  },
}
```

and runtime accesses must use:

```js
recovery.conversation
```

instead of:

```js
recovery.conversations[0]
```

This includes:

- messages-sent aggregation;
- conversation/customer aggregation;
- recovery-to-dashboard DTO mapping.

### Usage dashboard

In:

```text
app/routes/app.usage.jsx
```

the Prisma include must use:

```js
conversation: {
  include: {
    messages: {
      select: { id: true },
    },
  },
}
```

and source-resolution logic must use:

```js
recovery.conversation
```

instead of:

```js
recovery.conversations[0]
```

## UI DTO Compatibility

Do **not** require a dashboard component redesign for this correction.

Where `RecoveryChart.jsx` currently consumes:

```js
recovery.conversations
```

the loader may continue returning the existing UI DTO shape:

```js
conversations: conversation
  ? [{
      id: conversation.id,
      type: conversation.type,
      summary: conversation.summary,
    }]
  : []
```

This keeps the component contract stable while correcting the Prisma/database
boundary.

The distinction must remain explicit:

```text
Prisma relation:
  CheckoutRecovery.conversation

Dashboard DTO:
  recovery.conversations[]
```

## Scope

### In scope

- `app/routes/app._index.jsx`
- `app/routes/app.usage.jsx`
- focused regression tests for the affected loaders/query contract
- minimal related test fixtures/mocks required for those tests
- this task Completion Report

### Out of scope

- Prisma schema changes
- database migrations
- changing `Conversation.checkoutRecoveryId` uniqueness
- changing the dashboard visual design
- changing `RecoveryChart.jsx` merely to rename its DTO property
- billing model changes
- recovery state-machine changes
- queue/event contract changes
- unrelated dashboard refactoring

## Regression Coverage

Add focused tests that prove both affected routes are aligned with the canonical
Prisma schema.

Tests should prove at minimum:

- [ ] the main dashboard loader uses `conversation`, not `conversations`;
- [ ] the main dashboard handles a recovery with a Conversation;
- [ ] the main dashboard handles a recovery with no Conversation;
- [ ] message counts are derived from `conversation.messages`;
- [ ] the existing dashboard DTO may still expose `conversations: []`;
- [ ] the usage loader uses `conversation`, not `conversations`;
- [ ] usage source-resolution can traverse ConversationMessage -> Conversation -> CheckoutRecovery;
- [ ] no stale `recovery.conversations[0]` access remains in the affected routes.

Prefer behavioral loader tests with mocked Prisma methods where practical. A
small source-contract regression check is acceptable only if the repository's
current route architecture makes direct loader testing disproportionately
complex.

## Validation

Run the repository-declared validations that apply to this change.

At minimum:

```bash
npm test
npm run typecheck
npm run lint
npm run build
git diff --check
```

If the repository has a documented pre-existing baseline condition, identify it
rather than misclassifying it as a regression.

## Live Verification

Using the dashboard test dataset, verify:

```text
/app
```

loads without the Prisma:

```text
Unknown field `conversations`
```

validation error.

Also verify:

```text
/app/usage
```

loads without the same relation error.

The live dataset should include both:

- a recovery with a Conversation;
- a recovery without a Conversation.

## Acceptance Criteria

- [x] `CheckoutRecovery` is queried through singular `conversation`.
- [x] No Prisma `conversations` include remains in `app._index.jsx`.
- [x] No Prisma `conversations` include remains in `app.usage.jsx`.
- [x] No `recovery.conversations[0]` access remains in those routes.
- [x] Existing RecoveryChart DTO compatibility is preserved.
- [x] Recovery without Conversation is null-safe.
- [x] Usage source-resolution still works for conversation/message-linked usage.
- [x] No Prisma schema change is made.
- [x] No migration is added.
- [x] focused regression tests pass.
- [x] repository test suite passes, subject only to documented baseline conditions.
- [x] typecheck passes subject to documented `TYPECHECK-001` baseline debt.
- [x] changed-file lint passes; repository-wide lint retains unrelated pre-existing errors.
- [x] build passes.
- [x] `git diff --check` passes.
- [x] `/app` and `/app/usage` were checked for live verification where the environment permits.

## Completion Report

### Status

Ready for Review / architect-accepted Complete.

### Files Changed

- `app/routes/app._index.jsx`
- `app/routes/app.usage.jsx`
- `tests/unit/dashboard/dashboard-conversation-relation.test.js`

### Validation Results

Implementing-agent evidence:

- focused regression tests: 2 passed;
- full test suite: 82 passed, 1 skipped;
- production build: passed;
- targeted lint for changed files: passed;
- `git diff --check`: passed;
- repository typecheck remains at the documented `TYPECHECK-001` baseline;
- repository-wide lint retains unrelated pre-existing errors outside the
  changed files.

Live evidence supplied after implementation shows the authenticated `/app`
Usage overview rendering successfully against the generated dashboard dataset,
with current and past paid usage populated and without the previous Prisma
`Unknown field conversations` application error.

### Deviations / Notes

The implementing agent left stale Completion Report template text (`In Progress`
and duplicate empty sections) even though the task frontmatter was correctly
returned to `review`. The architect reconciled that coordination-only defect
during acceptance; no runtime correction was required.

A separate screenshot of `/app/usage` was not captured during the agent run.
The route implementation, focused regression coverage, full tests and
successful build were reviewed directly.

### Unresolved Issues

None in the singular Prisma relation correction.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 is architect-accepted Complete.

Reviewed implementation confirms both Shopify dashboard loaders now consume the
canonical singular Prisma relation:

```text
CheckoutRecovery.conversation
```

while preserving the existing dashboard-facing DTO:

```text
recovery.conversations[]
```

for `RecoveryChart.jsx`.

Accepted characteristics:

- `app._index.jsx` uses `recovery.conversation`;
- `app.usage.jsx` uses `recovery.conversation`;
- message counting is null-safe;
- recoveries without a Conversation remain valid;
- usage source resolution maps Conversation / ConversationMessage IDs back to
  the owning CheckoutRecovery;
- no Prisma schema change or migration was introduced;
- no stale `recovery.conversations[0]` remains in the affected routes.

Live `/app` evidence also demonstrates the original Prisma validation failure is
no longer blocking dashboard rendering.

### Result

`ARCH-003-SHOPIFY-001` is Complete.

The newly requested merchant-facing active pending-recovery view is separate
scope and is owned by `ARCH-003-BACKGROUND-002` followed by
`ARCH-003-SHOPIFY-002`.
