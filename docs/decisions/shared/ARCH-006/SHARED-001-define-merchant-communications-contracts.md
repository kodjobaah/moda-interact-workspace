---
id: ARCH-006-SHARED-001
architecture_id: ARCH-006
title: Define merchant-communications validation and BullMQ contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: complete
priority: 20
executor: copilot
claimed_at: 2026-09-06T13:03:47Z
attempt: 1
depends_on:
  - ARCH-005-SHARED-001
  - ARCH-006-DATABASE-002
enables:
  - ARCH-006-SHARED-002
created: 2026-09-05
updated: 2026-09-06T13:14:57Z
---

# ARCH-006-SHARED-001: Define merchant-communications validation and BullMQ contracts

## Architecture

Canonical: `docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

Detailed translation reliability: `docs/architecture/ARCH-006-translation-batching-reliability.md`

## Objective

Publish one canonical in-repo contract for support body validation, English-base translation decisions, translation lifecycle values and minimal deterministic BullMQ work identities.

## Context

Luna agents must not invent queue names, payload shapes, language rules or job IDs in each consumer. ARCH-005 language-tag validation/canonicalisation is reused. BullMQ custom job IDs in this workspace are colon-free and collision-safe.

## Scope

New shared merchant-communications exports and focused tests. Prefer a browser-safe core export plus a Node-only export for hashing/job-ID helpers if current package conventions require it.

## Out of Scope

- Provider SDK/API implementation.
- Database access.
- UI/server orchestration.
- Hard-coded runtime translation model.
- Human-language allowlists beyond the English-base rule.

## Requirements

Define canonical values/schemas matching DB002, plus:

```text
PLATFORM_SUPPORT_LANGUAGE_TAG = en-GB
queueName = merchant-communications
jobs:
  translation-dispatch
  translation-batch-submit
  translation-batch-poll
  translation-batch-results
  translation-reconcile
```

Authored support body contract:

```text
plain text
1..500 user-perceived Unicode grapheme clusters
reject over-length input; never silently truncate
translatedBody is NOT capped at 500
```

Implement/reuse a Unicode grapheme counter using `Intl.Segmenter` or the workspace-supported equivalent; do not use JS UTF-16 `.length` as the business count.

English-base routing helper must use canonical primary language:

```text
en-* -> en-* : no translation required
non-English merchant -> en-GB : translation required
en-GB admin/system -> non-English merchant : translation required
```

Queue payloads are strict and contain IDs/version only; never body/shop/admin text:

```text
translation-dispatch    { schemaVersion: 1, translationId }
translation-batch-submit{ schemaVersion: 1, translationBatchId }
translation-batch-poll  { schemaVersion: 1, translationBatchId, pollSequence }
translation-batch-results{schemaVersion: 1, translationBatchId }
translation-reconcile   { schemaVersion: 1, reconciliationRequestId? }
```

Provide deterministic BullMQ-safe job-ID helpers. IDs MUST NOT contain `:`. Poll identity includes `pollSequence`; other logical work uses its durable ID.

## Work Items

- [x] Inspect ARCH-005 shared language exports and existing BullMQ contract/job-ID helpers/tests.
- [x] Add support message/translation/Batch/reconciliation value schemas aligned with DB002.
- [x] Add 1..500 grapheme authored-body validation and focused Unicode tests.
- [x] Add English-base translation-decision helper/tests.
- [x] Add strict queue job schemas and schema version.
- [x] Add deterministic colon-free Node job-ID helpers/tests, including poll sequence.
- [x] Export through package subpaths following existing package style.

## Interfaces / Contracts

Producers/consumers import these contracts from `@modainteract/moda-interact-shared` rather than redefining them.

Job ID semantics:

```text
dispatch -> exactly one logical current dispatch identity per translation
submit   -> exactly one logical submit identity per TranslationBatch
poll     -> one identity per TranslationBatch + durable pollSequence
results  -> exactly one logical result identity per TranslationBatch
reconcile-> deterministic for a durable manual request when requestId supplied
```

A failed queue job may later be removed and re-created with the same deterministic ID; the durable DB state remains authoritative.

Provider Batch `custom_id` is a separate provider-result correlation concern: retries that create a new historical `MerchantTranslationBatchItem` must use a new Batch-item custom ID while preserving deterministic lookup of the owning translation. Do not define a translation-stable provider custom ID that would conflict with historical retry membership.

## Dependencies

Explicit task dependencies are listed in YAML frontmatter.

## Enables

`ARCH-006-SHARED-002`

## Acceptance Criteria

- [x] DB enum/value alignment is tested.
- [x] 500-grapheme contract handles emoji/non-BMP/combined graphemes correctly.
- [x] Translated output has no 500 limit in the shared result schema.
- [x] `en-US`, `en-GB`, `en-CA` to admin do not request translation.
- [x] Non-English routing is deterministic.
- [x] Queue payload schemas reject extra/untrusted fields.
- [x] No queue payload contains message body/shop/admin identity.
- [x] Deterministic job IDs are collision-safe and contain no colon.
- [x] Existing shared exports/contracts remain compatible.

## Validation

Run focused tests plus repository-declared full tests/typecheck/build/lint as applicable and `git diff --check`.

## Implementation Notes

Keep the task bounded to contracts/helpers. Do not create a queue producer or provider client here.

## Completion Report

### Status

Ready for Review

### Files Changed

Added the browser-safe merchant-communications contract and Node-only
deterministic job-ID modules, focused tests, and package/build exports:

- `src/merchant-communications.ts`
- `src/merchant-communications.node.ts`
- `src/merchant-communications.test.ts`
- `src/merchant-communications.node.test.ts`
- `src/index.ts`
- `package.json`
- `tsup.config.ts`

### Work Completed

Published canonical ARCH-006 support message, translation, Batch and
reconciliation schemas aligned with DATABASE-002; the 500-grapheme authored
body contract using `Intl.Segmenter`; English-primary-language routing; strict
versioned BullMQ payload schemas; and deterministic colon-free Node job IDs for
dispatch, submit, poll, results and reconciliation work.

### Validation Results

Passed:

- `npx tsx --test src/merchant-communications.test.ts src/merchant-communications.node.test.ts` — 9 passed.
- `npm test` — 92 passed, 1 skipped because `TEST_REDIS_URL` is not configured.
- `npm run typecheck` — passed.
- `npm run build` — passed, including browser-safe and Node-only package subpaths and declarations.
- `git diff --check` — passed.

The skipped Redis integration test is pre-existing and unrelated to this
contract-only task.

### Deviations

No lint script is declared by the repository, so no lint command was invented.

### Assumptions

Primary-language equality is the canonical ARCH-006 English-base routing rule;
regional English tags remain equivalent for translation decisions.

### Unresolved Issues

None within task scope.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted by `moda_architect` on 2026-09-06 after independent review.

### Decision

Complete. No correction attempt is required.

### Review Findings

- Shared support/translation/Batch/reconciliation enum values align with the architect-accepted `ARCH-006-DATABASE-002` Prisma enums.
- Authored body validation uses Unicode grapheme clusters and enforces `1..500` without truncation; translated output remains uncapped.
- English-base routing canonicalises BCP-47 tags and correctly avoids English-to-English translation while requiring the approved English/non-English directions.
- All five BullMQ payload schemas are strict and contain only schema version plus durable identifiers/sequence values; message body, shop and admin identity are absent.
- Node-only deterministic job-ID helpers are colon-free, collision-resistant and include durable `pollSequence` for successive legitimate polls.
- Browser-safe exports remain separated from the Node `crypto` helper subpath.
- Provider Batch `custom_id` remains outside this shared job-ID contract and is correctly documented as per historical Batch item/attempt rather than translation-stable.

### Validation Evidence

The repository Completion Report records 9 focused tests passing, 92 full tests passing with one pre-existing Redis integration skip when `TEST_REDIS_URL` is absent, plus successful typecheck, build and `git diff --check`. The supplied review snapshot does not include `node_modules`, so those commands could not be independently re-run by `moda_architect`; the relevant implementation/tests/exports were inspected directly.

### Workflow Note

The repository agent prematurely wrote its own architect approval. Repository agents must return implementation tasks to `review` and stop; only `moda_architect` may transition `review -> complete`. This review now supplies the real acceptance.
