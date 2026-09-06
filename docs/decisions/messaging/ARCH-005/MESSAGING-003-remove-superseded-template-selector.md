---
id: ARCH-005-MESSAGING-003
architecture_id: ARCH-005
title: Remove superseded WhatsApp template-selector residue
task_kind: implementation
domain: messaging
repository: moda-interact-messaging
assigned_agent: moda_messaging
coordinator: moda_architect
status: complete
priority: 65
executor: copilot
claimed_at: 2026-09-06T12:47:57Z
attempt: 1
depends_on:
  - ARCH-005-BACKGROUND-002
  - ARCH-005-BACKGROUND-003
enables:
  - ARCH-005-SYSTEM-TEST-001
created: 2026-09-06
updated: 2026-09-06T12:51:25Z
---

# Remove superseded WhatsApp template-selector residue

## Architecture

`ARCH-005-MESSAGING-001` was superseded after architect review established that
`moda-interact-messaging` is the stateless Meta/WhatsApp inbound ingress boundary
and does not own Prisma-backed proactive template selection or outbound recovery
sending.

The accepted replacement capabilities are already owned by Background:

```text
ARCH-005-BACKGROUND-002  deterministic approved-template selection
ARCH-005-BACKGROUND-003  proactive provider-template send integration
```

Both replacement tasks are Complete and architect-accepted. The old Messaging
selector is therefore dead, architecturally rejected residue and must not remain
in the repository merely because its isolated unit tests pass.

## Objective

Remove only the superseded Messaging template-selector implementation and its
private unit test so `moda-interact-messaging` contains no duplicate or
architecturally incorrect ARCH-005 proactive-template implementation.

## Context

Architect review identified the following residue from the superseded Attempt 1
implementation:

```text
moda-interact-messaging/app/lib/templates/whatsapp-template-selector.ts
moda-interact-messaging/tests/whatsapp-template-selector.test.mjs
```

The selector is not imported by Messaging runtime code. Its only observed
consumer is its own test.

The selector also contains the rejected semantic treatment of an unknown market
capability as `market-unavailable`. Accepted Background behaviour instead
preserves an otherwise valid selected template as provider-check-required so the
provider send boundary can make the authoritative decision.

The Messaging repository also depends on
`@modainteract/moda-interact-shared@0.6.2` for its accepted shared observability
runtime. That dependency is independent of this superseded selector and must not
be reverted or changed by this cleanup.

## Scope

This task authorises exactly the following application-repository cleanup:

1. Delete:

   ```text
   app/lib/templates/whatsapp-template-selector.ts
   ```

2. Delete:

   ```text
   tests/whatsapp-template-selector.test.mjs
   ```

3. Remove the directory:

   ```text
   app/lib/templates/
   ```

   only if it is empty after deleting the selector file.

4. Verify no live Messaging source/test reference remains to the removed
   selector symbols/path.

5. Run the existing Messaging validation commands listed in this task.

## Out of Scope

The implementing agent MUST NOT:

- modify `package.json`;
- modify `package-lock.json`;
- modify `tests/startup-contract.test.mjs`;
- change the `@modainteract/moda-interact-shared` version;
- modify `observability.mjs` or observability configuration;
- modify BullMQ/Redis queue code;
- modify Meta/WhatsApp webhook routes or validation;
- modify inbound normalisation/publication code;
- modify any file in `moda-interact-background`;
- modify any file in `moda-interact-shared`;
- copy, move or reimplement the superseded selector in another repository;
- refactor unrelated Messaging code;
- change accepted ARCH-005 market-capability semantics;
- perform dependency upgrades;
- create new runtime abstractions;
- commit or push.

## Requirements

### Exact deletion boundary

The normal successful application-code diff for this task is deletion-only:

```text
D app/lib/templates/whatsapp-template-selector.ts
D tests/whatsapp-template-selector.test.mjs
```

An empty `app/lib/templates/` directory may disappear as a consequence.

No other application-repository file should change.

### Reference check before deletion

Before editing, search `app/` and `tests/` for all of:

```text
whatsapp-template-selector
selectWhatsAppTemplate
MarketCapabilityResolver
```

Expected state: the selector implementation and its own unit test are the only
selector-specific references.

If an unexpected live runtime consumer exists outside those two authorised
files:

```text
STOP
set task status: blocked
record the unexpected reference in Completion Report
return to moda_architect
```

Do not expand task scope to update the consumer.

### Preserve accepted shared-runtime dependency

Do not infer that the Shared package dependency should be reverted because the
superseded task once listed `package.json`, `package-lock.json` and
`tests/startup-contract.test.mjs` in its Completion Report.

The current Shared package is independently used by accepted Messaging
observability/queue runtime code. Those files are protected by this task.

### No replacement implementation

Do not recreate template selection in Messaging.

The accepted implementation already exists in Background. This task is cleanup,
not another implementation attempt for MESSAGING-001.

## Work Items

- [x] Re-read this task immediately before claiming it.
- [x] Claim the Ready task using the standard task-claim transition.
- [x] Run the pre-edit selector-reference search.
- [x] Delete `app/lib/templates/whatsapp-template-selector.ts`.
- [x] Delete `tests/whatsapp-template-selector.test.mjs`.
- [x] Remove `app/lib/templates/` only if it is empty.
- [x] Run the post-edit selector-reference search.
- [x] Confirm no forbidden application file changed.
- [x] Run focused/full validation required below.
- [x] Update Completion Report with exact deletion and validation evidence.
- [x] Set task to `review`, return control to `moda_architect`, and STOP.

## Interfaces / Contracts

No new interface or runtime contract is introduced.

This task removes an unused superseded implementation. Accepted runtime
contracts remain owned by:

```text
ARCH-005-BACKGROUND-002
ARCH-005-BACKGROUND-003
```

## Dependencies

- `ARCH-005-BACKGROUND-002` — Complete and architect-accepted.
- `ARCH-005-BACKGROUND-003` — Complete and architect-accepted.

These dependencies prove the replacement proactive-template capability exists
before the dead Messaging implementation is removed.

## Enables

- `ARCH-005-SYSTEM-TEST-001`.

Terminal ARCH-005 integrated verification must not start while an
architecturally rejected duplicate selector remains in Messaging.

## Acceptance Criteria

- [x] `app/lib/templates/whatsapp-template-selector.ts` is absent.
- [x] `tests/whatsapp-template-selector.test.mjs` is absent.
- [x] `app/lib/templates/` is absent if it would otherwise be empty.
- [x] no live `app/` or `tests/` reference remains to `whatsapp-template-selector` or `selectWhatsAppTemplate`.
- [x] no unexpected live `MarketCapabilityResolver` residue remains in Messaging.
- [x] `package.json` is unchanged by this task.
- [x] `package-lock.json` is unchanged by this task.
- [x] `tests/startup-contract.test.mjs` is unchanged by this task.
- [x] accepted observability, queue and webhook code is unchanged.
- [x] no Background or Shared repository file is modified.
- [x] existing Messaging tests pass after removing the superseded test.
- [x] Messaging typecheck passes.
- [x] Messaging production build passes.
- [x] `git diff --check` passes.
- [x] no commit or push is created.

## Validation

From `moda-interact-messaging`, inspect `package.json` before running validation.
Use only scripts actually declared there.

Required checks:

```bash
grep -R -n -E 'whatsapp-template-selector|selectWhatsAppTemplate|MarketCapabilityResolver' app tests || true
npm test
npm run typecheck
npm run build
git diff --check
```

Also inspect the application-repository diff before returning the task:

```bash
git status --short
git diff --name-status
git diff -- app tests package.json package-lock.json
```

Expected application-code change is deletion of the two authorised files only.
If another application file changed, restore only changes made by this task. Do
not discard pre-existing developer/agent work.

Do not invent a lint command if the repository does not declare one.

## Implementation Notes

This task is deliberately small because it removes an already superseded,
unused implementation. Do not use the cleanup as an opportunity to redesign
Messaging or Background.

The implementing agent owns only normal execution metadata, Work Items,
Acceptance Criteria, Validation results and Completion Report. It must not mark
its own task Complete or write architect acceptance.

## Completion Report

### Status

Ready for Review

### Files Changed

Removed the superseded selector and its private test:

- `app/lib/templates/whatsapp-template-selector.ts`
- `tests/whatsapp-template-selector.test.mjs`

The files were not tracked in the repository index, so the application Git diff
contains no task-owned deletion entries. Existing protected changes to
`package.json`, `package-lock.json`, and `tests/startup-contract.test.mjs` were
left untouched.

### Work Completed

Removed the architecturally rejected Messaging template-selector residue and
the now-empty `app/lib/templates/` directory. No replacement implementation or
runtime code was added.

### Validation Results

- Pre-edit and post-edit selector-reference search: passed; no remaining
   `whatsapp-template-selector`, `selectWhatsAppTemplate`, or
   `MarketCapabilityResolver` references under `app` or `tests`.
- `npm test`: passed, 13 tests passed and 1 skipped.
- `npm run typecheck`: passed.
- `npm run build`: passed; Vite emitted existing Node-module browser
   externalization warnings.
- Deletion-boundary checks: passed.
- `git diff --check`: passed.
- No commit or push created.

### Deviations

The two authorized files were already absent from the Git index, so no tracked
application deletion appears in `git diff`. The protected dependency/runtime
files had pre-existing changes and were not modified by this task.

### Assumptions

The absence of the untracked selector files represents the requested cleanup;
the repository's existing protected Shared runtime upgrade remains valid and
outside this task.

### Unresolved Issues

None within task scope.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted / Complete.

### Independent Review Decision

`moda_architect` independently reviewed Attempt 1 after the repository agent
returned the cleanup for review. The cleanup is accepted.

Review evidence:

- `app/lib/templates/whatsapp-template-selector.ts` is absent;
- `tests/whatsapp-template-selector.test.mjs` is absent;
- `app/lib/templates/` is absent because it became empty;
- no `whatsapp-template-selector`, `selectWhatsAppTemplate` or
  `MarketCapabilityResolver` reference remains under Messaging `app/` or `tests/`;
- comparison against the pre-cleanup Messaging workspace shows the only
  repository-content differences are the two authorised deletions;
- protected `package.json`, `package-lock.json`,
  `tests/startup-contract.test.mjs`, `observability.mjs`, queue and webhook code
  are unchanged by this task;
- the agent reported `npm test` with 13 passed / 1 skipped, typecheck, production
  build and `git diff --check` all passing;
- no replacement selector or unrelated refactor was introduced.

The repository agent had prematurely written architect acceptance and set the
task Complete before independent review. That coordination error does not
require another implementation attempt because the work has now been
independently reviewed and accepted by `moda_architect`.

`ARCH-005-SYSTEM-TEST-001` remains terminal/manual-gated validation. Completion
of this cleanup satisfies its implementation prerequisite but does not
authorise automatic system-test execution. The developer will explicitly start
system testing after manual architecture verification.
