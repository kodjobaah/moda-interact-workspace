---
id: ARCH-040-SHOPIFY-004
architecture_id: ARCH-040
title: Localise remaining Shopify Recovery Detail informational copy
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-040-SHOPIFY-001
enables:
  - ARCH-040-SYSTEM-TEST-002
created: 2026-10-19
updated: 2026-10-19
---

# ARCH-040-SHOPIFY-004 — Complete 20-locale Recovery Detail copy

## Architecture

- ARCH-040 parent: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`.
- Owner: `moda_app`, repository `moda-interact`, coordinator `moda_architect`.
- Portable definition only. Pending accepted `ARCH-040-SHOPIFY-001` implementation; no feature code or existing _index.md edits in this task definition.

## Objective

Replace secondary English placeholder/fallback strings introduced by ARCH-040-SHOPIFY-001 in the **19 non-English** Shopify merchant locale catalogues, so all 20 supported locales present coherent Recovery Detail basket, conversation, follow-up and moderation information without changing runtime behavior.

## Context

The ARCH-040-SHOPIFY-001 Attempt 1 candidate modifies `app/i18n/locales/*.json` (20 locales). Most principal message-control/moderation strings are translated, but the following **16 new `recoveryDetail` keys** retain exactly the English value in each of the other 19 locales (confirmed from the candidate patch):

- `recoveryDetail.savedSnapshot`
- `recoveryDetail.basketUnavailable`
- `recoveryDetail.basketPartial`
- `recoveryDetail.emptyBasket`
- `recoveryDetail.humanControls`
- `recoveryDetail.windowOpen`
- `recoveryDetail.terminal`
- `recoveryDetail.staleRevision`
- `recoveryDetail.controlFailed`
- `recoveryDetail.latestReply`
- `recoveryDetail.templateUnavailable`
- `recoveryDetail.followUpTemplate`
- `recoveryDetail.customerFlagged`
- `recoveryDetail.sendStatus.CLAIMED`
- `recoveryDetail.sendStatus.DISPATCH_ADMITTED`
- `recoveryDetail.sendStatus.CANCELLED`

This is a Shopify presentation/content issue, **not** a Background follow-up reservation issue. Keep it separately owned and reviewable.

## Scope

- Update those sixteen keys in `cs, da, de, es, fi, fr, it, ja, ko, nb, nl, pl, pt-BR, pt-PT, sv, th, tr, zh-Hans, zh-Hant` JSON catalogues, using the established merchant UI terminology and natural local grammar.
- Preserve `en.json` as source-language reference; keep all 20 locale keysets/parity, interpolation syntax and nested/key ordering conventions intact.
- Extend the existing `tests/unit/shopify-ui-i18n-coverage.test.ts` or relevant existing translation coverage test to require translations for these introduced Recovery Detail keys. Permit deliberate language-neutral technical tokens only with explicit evidence; do not globally ban English words in translations.
- Run focused tests, JSON parse and 20-locale parity checks and report precise results.

## Out of Scope

- No changes to `moda-interact-background`, PostgreSQL, control/send actions, moderation logic, billing, HTTP contracts, token selection, or WooCommerce translations.
- Do not change user-facing state semantics, add separate conversations or alter React flows merely to accommodate strings.
- No `_index.md` updates until the architecture session is complete.

## Requirements

1. Every listed secondary label/message is meaningfully localised in all 19 target catalogues, using existing locale grammar and terminology.
2. Safety/failure status translations must distinguish **accepted/queued**, **sending/admitted**, **cancelled/not sent**, **moderation blocked/review**, and **provider confirmed sent**; a queue acceptance must not be presented as a completed send.
3. Preserve existing 20-locale fallback behavior for missing keys while preventing the sixteen specifically identified placeholders from silently falling back to English.
4. Do not interpolate customer text or PII into translated strings; preserve interpolation tokens exactly where present.

## Work Items

- [ ] Verify live SHOPIFY-001 accepted locale keys and translate the sixteen enumerated entries in 19 catalogues.
- [ ] Check native terminology across related Recoveries labels; preserve valid locale-specific formatting.
- [ ] Add a focused test detecting identical English placeholders only for these explicit keys (with documented intentional exceptions).
- [ ] Validate all 20 JSON files, key parity, focused Recovery Detail rendering and changed-file lint/typecheck as applicable.

## Interfaces / Contracts

- Existing `app/i18n/locales/*.json` dictionaries consumed by the merchant UI's current `t(...)` translation access.
- No new Shared schema or runtime API. User-visible strings remain attached to existing `recoveryDetail.*` keys.

## Dependencies

- `ARCH-040-SHOPIFY-001` (Ready in supplied definition snapshot; not yet accepted Complete).

## Enables

- `ARCH-040-SYSTEM-TEST-002` independent Shopify certification, including 20-locale smoke assertions.

## Acceptance Criteria

- [ ] The sixteen enumerated values are no longer placeholder English in any target locale (except independently justified language-neutral proper tokens).
- [ ] English source and all other Recovery Detail keys remain intact; 20 locale JSON catalogues parse and have parity.
- [ ] Key user-facing states remain accurate and never claim provider delivery from mere command acceptance.
- [ ] No changes to Background, database, or Shopify send logic; focused tests pass.

## Validation

- [ ] JSON parse and 20-locale key-parity comparison against `en.json`.
- [ ] `npm run test -- tests/unit/shopify-ui-i18n-coverage.test.ts tests/unit/merchant-i18n.test.ts tests/unit/recovery-detail-route.test.ts`
- [ ] `npm run typecheck`
- [ ] `npm run lint` (record any documented unrelated existing baseline issues separately).
- [ ] `git diff --check` and canonical worktree/synchronisation evidence.

## Stop Condition

After completing the scope and required validation, return a detailed Completion Report, set task to `review` and STOP. Do not begin the system-test task.

## Implementation Notes

This is a small content-parity correction and should not be merged into `ARCH-040-BACKGROUND-007`; its dependency is the accepted Shopify feature state. Verify the actual locale files before edits: the first attempt patch is evidence of the gap, not proof that every English placeholder is still present in a later worktree.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

The SHOPIFY-001 candidate patch is the initial English-fallback inventory; verify against the canonical implementation branch at task start.

### Unresolved Issues

None currently; blocked until SHOPIFY-001 becomes Complete.

### Architectural Concerns

None expected; any runtime semantic change requires separate architect review.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting translation quality and coverage evidence.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Independent Shopify SYSTEM-TEST-002 locale presentation smoke.
