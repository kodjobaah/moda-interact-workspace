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
status: in_progress
priority: 30
executor: codex
claimed_at: 2026-10-31T21:06:17Z
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

Coordinator: `moda_architect`. Task **defined but not materialised**; no local Git/worktree/branch activity is claimed.


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

- [ ] Implement focused service, loader and separate save intent; view, form validation and 20 locales.
- [ ] Add tests for default and 0,1,7,30, invalid non-integer/negative/31/unknown field, shop isolation, optimistic conflict and unchanged recovery policy.


## Interfaces / Contracts

Service consumes published `AiResponseDelayMinutesSchema`; form intent is Shopify-only internal wire, not a second shared external API. Saved data is `ShopSettings.aiResponseDelayMinutes`.


## Dependencies

- ARCH-054-DATABASE-001
- ARCH-054-SHARED-002


## Enables

None


## Acceptance Criteria

- [ ] Every integer 0–30 can be saved by its owning merchant; invalid inputs rejected server-side; UI accurately explains HUMAN bypass and future-turn-only effect.
- [ ] No changes to `recoveryDelayMinutes`, AI offer modes or existing locale text outside the new keys; all 20 locales compile. Shopify imports the published Shared version with a matching lockfile pin.


## Validation

- [ ] Focused React Router loader/action tests; locale catalog validation; typecheck/lint/build per package.json; `git diff --check`.


## Stop Condition

After all required Work Items, Acceptance Criteria and Validation are complete, update Completion Report, set status to `review`, return control to `moda_architect` and **STOP**. Do not implement dependent tasks. Publication tasks do not rerun accepted implementation validation.


## Implementation Notes

Implement only the identified repository-owned changes; preserve original provider/SDK errors in shared structured logs and rethrow failures to the owning retry/admission boundary.


## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not Run

### Deviation / Assumptions / Unresolved Issues / Architectural Concerns

None

### Worktree and Git Evidence

Not materialised; implementing agent must record launcher-prepared dedicated parent/implementation worktree paths, start-of-attempt sync, branch SHAs, submodule pins and cleanup.


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
