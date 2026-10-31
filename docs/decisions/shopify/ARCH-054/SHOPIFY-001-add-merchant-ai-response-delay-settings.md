---
id: ARCH-054-SHOPIFY-001
architecture_id: ARCH-054
title: Expose integer 0–30 AI delay in Shopify merchant settings
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-054-DATABASE-001
  - ARCH-054-SHARED-002
enables: []
created: 2026-10-31
updated: 2026-10-31
---


# ARCH-054-SHOPIFY-001: Expose integer 0–30 AI delay in Shopify merchant settings


## Architecture

Architecture: `ARCH-054`

Document: `docs/architecture/ARCH-054-merchant-configurable-ai-response-delay.md`

Coordinator: `moda_architect`. The task was materialised and claimed by the
prepared launcher for Attempt 1; see the Completion Report for the dedicated
parent and implementation worktrees and synchronization evidence.


## Objective

Add a merchant-editable independent AI response delay control on authenticated Shopify Recovery Settings with strict server-side persistence.


## Context

ARCH-054 adds a **merchant-selectable integer 0–30 minute AI reply delay** to the existing ARCH-040 recovery-conversation processor and handover controls, leaving merchant-authored HUMAN replies without configured delay. See the parent architecture and current snapshot for specific boundaries.


## Scope

Update `moda-interact/package.json` and `package-lock.json` to the exact architect-accepted Shared version from ARCH-054-SHARED-002; do not use sibling Shared source. Modify `app/routes/app/recovery-settings/route.tsx`, `app/routes/app/recovery-settings/RecoverySettingsView.tsx`, `app/routes/app/settings-save/route.ts`; create `app/services/ai-response-delay/ai-response-delay.server.ts` and `app/routes/app/recovery-settings/AiResponseDelaySettings.tsx`. Extend `app/components/settings/SettingsForm.tsx` only if needed for a new `ai-response-delay` intent; add exact label/help/error text in all 20 files under `app/i18n/locales/*.json`, preserving existing locale keys.


## Out of Scope

No unrelated architecture changes, new standalone chat service, per-user timer jobs, invented provider error explanations, or updates to `docs/decisions/**/_index.md`. No implementation outside the assigned repository.


## Requirements

- Read the authenticated shop via `settingsAccess(request)`; never take shopId from a form. Display a labeled accessible `number` input min=0 max=30 step=1, default 0, including explanation "AI replies wait this long after the first pending customer message. Human replies are not delayed." Do not conflate with recovery outreach delay or 3s/10s Admin message-settling controls.
- Use a distinct `intent=ai-response-delay` through existing `/app/settings-save` and whitelist exactly `intent,operationId,revision,aiResponseDelayMinutes`; server parses/validates the published Shared v1 integer schema (form string converted only after strict regex `^(?:0|[1-9]|[12][0-9]|30)$`; reject other numeric formats), CSRF/session controls and optimistic current settings timestamp revision. Reuse existing Shop lock `lockSettingsShop` and throw 409 on conflicts; write ONLY `aiResponseDelayMinutes` + `updatedAt`, not recovery policy or discounts.
- UI shows saved value, pending/errors and conflict refresh; settings changes affect future pending turns only. Support keyboard, accessible labels and all 20 catalogues. Human Take Over/Resume AI and human composer remain unchanged by this settings task.


## Work Items

- [x] Implement focused service, loader and separate save intent; view, form validation and 20 locales.
- [x] Add tests for default and 0,1,7,30, invalid non-integer/negative/31/unknown field, shop isolation, optimistic conflict and unchanged recovery policy.


## Interfaces / Contracts

Service consumes published `AiResponseDelayMinutesSchema`; form intent is Shopify-only internal wire, not a second shared external API. Saved data is `ShopSettings.aiResponseDelayMinutes`.


## Dependencies

- ARCH-054-DATABASE-001
- ARCH-054-SHARED-002


## Enables

None


## Acceptance Criteria

- [x] Every integer 0–30 can be saved by its owning merchant; invalid inputs rejected server-side; UI accurately explains HUMAN bypass and future-turn-only effect.
- [x] No changes to `recoveryDelayMinutes`, AI offer modes or existing locale text outside the new keys; all 20 locales compile. Shopify imports the published Shared version with a matching lockfile pin.


## Validation

- [x] Focused React Router loader/action tests; locale catalog validation; typecheck/lint/build per package.json; `git diff --check`.


## Stop Condition

After all required Work Items, Acceptance Criteria and Validation are complete, update Completion Report, set status to `review`, return control to `moda_architect` and **STOP**. Do not implement dependent tasks. Publication tasks do not rerun accepted implementation validation.


## Implementation Notes

Implement only the identified repository-owned changes; preserve original provider/SDK errors in shared structured logs and rethrow failures to the owning retry/admission boundary.


## Completion Report

### Status

Ready for architect review; implementation attempt complete.

### Files Changed

`package.json`, `package-lock.json`; `app/services/ai-response-delay/ai-response-delay.server.ts`;
`app/routes/app/recovery-settings/route.tsx`,
`app/routes/app/recovery-settings/RecoverySettingsView.tsx`,
`app/routes/app/recovery-settings/AiResponseDelaySettings.tsx`,
`app/routes/app/settings-save/route.ts`,
`app/components/settings/SettingsForm.tsx`; all 20
`app/i18n/locales/*.json` catalogues; focused unit tests for the service,
loader, control, save action and locale contract; and the `database` submodule
pointer to the accepted ARCH-054-DATABASE-001 commit.

### Work Completed

- Pinned the published Shared package and lockfile to `3.1.0`, which exports
  `AiResponseDelayMinutesSchema`.
- Added an authenticated settings loader and a separate
  `ai-response-delay` save intent. The service applies the strict form-string
  regex and Shared schema, locks the authenticated shop, enforces the current
  settings timestamp revision, and updates only the delay and `updatedAt`.
- Added the accessible 0–30 minute control, with translated help stating that
  HUMAN replies are not delayed and changes affect future AI turns only.
- Logged unexpected persistence errors through the published Shared logger and
  rethrew them. Existing recovery settings and recovery policy fields remain
  unchanged.
- Added regression coverage for default 0, accepted values 0/1/7/30, malformed
  and out-of-range input, extra/shop ID fields, authenticated shop scope,
  optimistic conflicts, no-op saves, unchanged recovery policy fields, loader
  fallback and input accessibility.

### Validation Results

- Focused Vitest: 5 files passed, 54 tests passed, including loader/action,
  service, accessibility and locale-contract coverage.
- Locale populator `--check`: all 20 catalogues validated for each of the three
  new keys; no missing translations, duplicate keys or whitespace violations.
- `npm run typecheck`: passed.
- `npm run lint`: passed.
- `npm run build`: passed. Rollup reported dependency/build warnings for Zod
  pure-comment annotations, an unresolved `.prisma/client/index-browser`
  external import, and chunks over 500 kB; these did not fail the client or
  server build.
- `git diff --check`: passed.

### Deviation / Assumptions / Unresolved Issues / Architectural Concerns

The prepared implementation worktree initially contained the older database
submodule pin. Following the already-authorised dependency update, the pointer
was advanced to accepted database commit
`7c377282aa5819b3008b7d7f3018f44f4161523e`, which contains the required
`ShopSettings.aiResponseDelayMinutes` schema and migration. No database source
was changed by this task. No other deviations or unresolved implementation
issues.

### Worktree and Git Evidence

Launcher-prepared parent worktree:
`/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-054-SHOPIFY-001`
(branch `task/ARCH-054-SHOPIFY-001`, start-of-attempt HEAD
`12450c44ed20b8c30150117e706b7bd495e0308c`).

Launcher-prepared implementation worktree:
`/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-054-SHOPIFY-001`
(branch `task/ARCH-054-SHOPIFY-001`, start-of-attempt HEAD
`303d2c4a952a3bdc2dea2498a1f20882ec0c8828`). The launcher synchronized both
prepared worktrees, passed the dependency gate, and reported implementation
submodules ready. The implementation worktree started with database gitlink
`af77c594ecbfc78c26d01c0021a090830884bbff` and now records accepted commit
`7c377282aa5819b3008b7d7f3018f44f4161523e`. Implementation commit
`25294b693f302584d530c8712be5d4922c3a34f1` is pushed to
`origin/task/ARCH-054-SHOPIFY-001`. This report is being submitted on the
mirrored parent task branch for architect review.


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
