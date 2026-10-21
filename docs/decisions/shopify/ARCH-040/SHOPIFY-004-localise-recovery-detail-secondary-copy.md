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

- [x] Verify the SHOPIFY-001 Recovery Detail keys and translate the sixteen enumerated entries in 19 non-English catalogues (304 target values).
- [x] Check native terminology and delivery-state distinctions across related Recoveries labels while preserving locale-specific formatting.
- [x] Extend the existing Shopify UI i18n coverage test to detect the identified untranslated English placeholders.
- [x] Validate locale JSON/key parity, focused Recovery Detail rendering, and repository ESLint; capture the 55/55 focused-test evidence below.
- [ ] Obtain a passing repository-wide typecheck after the separately owned ARCH-043 `seal.server.ts` typing defect is corrected, or obtain an explicit architect-approved baseline disposition. Record final physical-worktree/branch/commit and prerequisite acceptance evidence before review.

## Interfaces / Contracts

- Existing `app/i18n/locales/*.json` dictionaries consumed by the merchant UI's current `t(...)` translation access.
- No new Shared schema or runtime API. User-visible strings remain attached to existing `recoveryDetail.*` keys.

## Dependencies

- `ARCH-040-SHOPIFY-001` (Ready in supplied definition snapshot; not yet accepted Complete).

## Enables

- `ARCH-040-SYSTEM-TEST-002` independent Shopify certification, including 20-locale smoke assertions.

## Acceptance Criteria

- [x] All sixteen enumerated values have non-placeholder translations in all nineteen target locales (304 values checked in the prepared locale patch).
- [x] The English reference and other Recovery Detail keys remain intact; all twenty locale JSON catalogues parse and retain key parity (692 keys per locale in patch verification).
- [x] Distinct queued/admitted/sending, cancelled/not-sent and provider-confirmed statuses are preserved; queue acceptance is not displayed as confirmed delivery.
- [x] The localisation patch is limited to nineteen locale JSON files plus the existing i18n coverage test; focused tests pass (55/55). No Background, database or Shopify send-logic edits are part of this patch.

**Review gate:** the repository-wide typecheck did not pass because of an unrelated ARCH-043 `seal.server.ts` error. This must receive correction and successful revalidation, or an explicit architect baseline disposition, before claiming the complete validation contract.

## Validation

- [x] All twenty JSON catalogues parse and retain 692-key parity against `en.json` (localisation patch verification).
- [x] `npm run test -- tests/unit/shopify-ui-i18n-coverage.test.ts tests/unit/merchant-i18n.test.ts tests/unit/recovery-detail-route.test.ts`: **55/55 passed** (4 UI coverage, 15 merchant i18n, 36 Recovery Detail route; 3/3 test files).
- [ ] `npm run typecheck`: **failed with one unrelated `TS2345`** in `app/services/platform-configuration/seal.server.ts:75`; corrective owner is the ARCH-043 Shopify configuration task. This is **not a passing typecheck**.
- [x] `npm run lint`: completed with no lint errors reported in the supplied terminal log.
- [x] `git diff --check`: no whitespace errors reported in the supplied terminal log.
- [ ] Record actual launcher-prepared parent and Shopify implementation worktree/branch synchronisation, final commit SHA and the accepted `ARCH-040-SHOPIFY-001` dependency in the final Completion Report.

## Stop Condition

After completing the scope and required validation, return a detailed Completion Report, set task to `review` and STOP. Do not begin the system-test task.

## Implementation Notes

This is a small content-parity correction and should not be merged into `ARCH-040-BACKGROUND-007`; its dependency is the accepted Shopify feature state. Verify the actual locale files before edits: the first attempt patch is evidence of the gap, not proof that every English placeholder is still present in a later worktree.

## Completion Report

### Status

Implementation and focused localisation validation evidenced; **not yet submitted for review**. Preserve the task's actual launcher-managed execution state and attempt history. The supplied snapshot still has `status: ready`, `attempt: 0`; do not infer a claim or transition from this evidence-only amendment.

### Files Changed

Localisation patch inventory: nineteen non-English JSON files under `app/i18n/locales/` (`cs`, `da`, `de`, `es`, `fi`, `fr`, `it`, `ja`, `ko`, `nb`, `nl`, `pl`, `pt-BR`, `pt-PT`, `sv`, `th`, `tr`, `zh-Hans`, `zh-Hant`) and `tests/unit/shopify-ui-i18n-coverage.test.ts`. English catalogue unchanged. **Final committed-file inventory/commit SHA are not yet supplied**; confirm them from the implementation worktree before review.

### Work Completed

- Localised the sixteen task-enumerated `recoveryDetail.*` strings in the nineteen non-English Shopify catalogues (304 target translations), retaining the English reference, key parity and existing runtime semantics.
- Added focused assertions in existing Shopify UI i18n coverage to catch the enumerated English placeholders and preserve distinct delivery-state meanings.
- Initial test environment was missing npm dependencies and generated Prisma Client; local `npm ci`, initialisation of the repository-pinned `database` submodule, and `npm run prisma:generate` restored the test environment. No Prisma schema or application runtime implementation was changed for this task.

### Validation Results

**Developer-supplied 21 October 2026 terminal log (after environment repair):**

- `git submodule update --init --recursive database`: checked out recorded Shopify repository gitlink `caee3df61dbb38c8319ebcd3cfaf68522743245e`; `database/prisma/schema.prisma` present.
- `npm run prisma:generate`: successful; Prisma Client v6.19.3 generated using that schema.
- Focused Vitest: **3/3 files, 55/55 tests passed**: `shopify-ui-i18n-coverage` **4/4**, `merchant-i18n` **15/15**, `recovery-detail-route` **36/36**. React Router server-renderer `useLayoutEffect` warnings were emitted during Recovery Detail tests but did not fail the tests.
- `npm run lint`: completed without a reported error.
- `git diff --check`: completed without a reported whitespace error.
- `npm run typecheck`: **FAILED**, one `TS2345` at `app/services/platform-configuration/seal.server.ts:75`: `configurationFailure` requires `ShopifyConfigurationErrorCode`, but the call concatenates `"UNSEAL_FAILED"` with raw exception text and supplies a plain `string`. This file is outside SHOPIFY-004's allowed localisation scope. Do not claim typecheck passed or silently modify that other owner's source.
- Independent patch verification prior to local execution: all twenty JSON catalogues parsed; 692-key parity per locale; 304 targeted entries were not identical to the English placeholders; outbound-status labels remained distinct. This is validation of the prepared localisation patch, not evidence of an independently reviewed commit.

### Deviations

No requested production-behaviour changes. Local test environment required npm dependency installation and the repository-pinned database submodule/Prisma generation. Repository-wide typecheck is not green because of an out-of-scope ARCH-043 configuration defect.

### Assumptions

The last supplied parent workspace snapshot is the patch baseline; no current parent task branch, launcher claim or final Shopify implementation commit SHA was independently supplied in this handoff. Verify actual task state before transitioning to `review`.

### Unresolved Issues

1. **Repository typecheck:** `app/services/platform-configuration/seal.server.ts:75` must be corrected by its ARCH-043 Shopify configuration owner and revalidated, or receive a documented architect baseline disposition. `"UNSEAL_FAILED" + error.message` also risks exposing underlying exception text; do not migrate that fix into SHOPIFY-004 just to unblock review.
2. **Handoff evidence:** record final implementation branch/HEAD and changed-file inventory, clean/synchronised parent and implementation worktrees, launcher physical-isolation evidence and accepted `ARCH-040-SHOPIFY-001` dependency. The terminal test output alone is not proof of Git commit or review status.
3. **Formal review:** no durable Accepted review has been recorded; leave architect-controlled `## Architect Review` unchanged.

### Architectural Concerns

The separate ARCH-043 Shopify configuration unseal error should use a bounded, typed, secret-safe reason code; its remediation belongs to its owning task, not to Recovery Detail localisation. No ARCH-040 runtime/contract changes are requested.

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
