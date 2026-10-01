---
id: ARCH-023-COMMERCE-004
architecture_id: ARCH-023
title: Enforce Merchant Knowledge merchant activation
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 62
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-023-COMMERCE-002
  - ARCH-023-ADMIN-004
enables: []
created: 2026-09-30
updated: 2026-10-01
---

# Enforce Merchant Knowledge merchant activation

## Objective

Enforce request-time Merchant Knowledge merchant activation after the accepted COMMERCE-002 bootstrap and ADMIN-004 product-policy reconciliation.

COMMERCE-002 is already accepted with the exact `MERCHANT_OPT_IN` bootstrap prerequisite. This task therefore owns only the remaining runtime correction: extend `merchantKnowledge.lookup` operation-level authority so an enabled `ShopFeaturePreference` is required independently of capability association.

Canonical invariant:

```text
retrievable = planEntitled && merchantEnabled
```

## Scope

Expected bounded surface:

```text
src/commerce/merchant-knowledge/entitlement.ts
merchantKnowledge.lookup operation tests
existing generic capability-selection integration only where needed for defence in depth
```

Do not modify or redesign the accepted COMMERCE-002 Tool/Capability/release bootstrap. Do not redesign pgvector retrieval.

## Requirements

### R1 — preserve accepted COMMERCE-002 bootstrap

COMMERCE-002 is Complete / Accepted Attempt 4 with the exact fixed Feature prerequisite:

```text
key = merchant_knowledge
active = true
activationMode = MERCHANT_OPT_IN
systemRequired = false
```

This task MUST NOT reopen, duplicate or replace that bootstrap guard and MUST NOT add any `ShopFeaturePreference` write to bootstrap.

### R2 — operation-level merchant activation authority

Extend current Merchant Knowledge entitlement resolution to require the exact current Feature preference:

```text
ShopFeaturePreference.shopId = trusted shopId
ShopFeaturePreference.featureId = merchant_knowledge Feature id
enabled = true
```

Missing/false preference -> `DENIED`, `retryable=false`, before query embedding or vector lookup.

Continue to ignore browser/model-supplied shop identity and pending future plans.

### R3 — defence in depth independent of capability grant

Even if the same Tool revision is granted through another eligible Capability, `merchantKnowledge.lookup` must still deny when Merchant Knowledge is OFF.

The generic Commerce capability selector may also remove the feature-bound capability because `MERCHANT_OPT_IN` is OFF; operation-level re-check remains mandatory.

### R4 — OFF is non-destructive

Commerce performs no source/revision mutation when disabled. Re-enabling immediately makes retained eligible ACTIVE chunks retrievable again, subject to current plan/source/provenance rules.

### R5 — tests

Prove:

```text
plan entitled + missing preference -> DENIED before embedding/vector query
plan entitled + false preference -> DENIED
plan entitled + true preference -> existing lookup path unchanged
Tool granted through another Capability cannot bypass preference gate
re-enable makes retained ACTIVE knowledge retrievable without re-ingestion
no ShopFeaturePreference row is created by Commerce
```

## Dependencies

- `ARCH-023-COMMERCE-002`
- `ARCH-023-ADMIN-004`

## Acceptance Criteria

- [x] Accepted COMMERCE-002 bootstrap remains unchanged and preference-neutral.
- [x] Lookup independently requires explicit merchant activation.
- [x] Disabled Merchant Knowledge cannot cause embedding or pgvector retrieval.
- [x] Re-enable reuses retained ACTIVE knowledge.

## Validation

- [x] focused Merchant Knowledge entitlement/operation tests
- [ ] live PostgreSQL/pgvector proof where existing COMMERCE-001 test contract requires it
- [x] `npm run typecheck`
- [x] targeted lint/diagnostics
- [x] `npm run build`
- [x] `git diff --check`

## Stop Condition

Set status `review`, complete Completion Report, return to `moda_architect` and STOP.

## Completion Report

### Status
Ready for Review — Attempt 1
### Files Changed
`src/commerce/merchant-knowledge/entitlement.ts`, `src/commerce/merchant-knowledge/operation.ts`, `tests/merchant-knowledge-entitlement.test.ts`, `tests/merchant-knowledge-policy.test.ts`, and `tests/merchant-knowledge-bootstrap.test.ts`.
### Work Completed
Merchant Knowledge entitlement now resolves the active plan's current `merchant_knowledge` Feature ID and requires `ShopFeaturePreference` for the authenticated turn's shop and that Feature ID. Missing or disabled preferences return non-retryable `DENIED`; preference database failures map to retryable `UNAVAILABLE`. The operation performs this check before testing embedding configuration, so an opted-out shop causes no embedding, source query, or vector lookup. Tests cover missing/false/true preferences, exact composite-key lookup, preference lookup failure, another-capability context, OFF-to-ON retrieval of retained ACTIVE knowledge, and the bootstrap's lack of preference mutations. The accepted bootstrap implementation was not changed.
### Validation Results
Prepared launcher evidence (2026-10-01T08:27:30Z):

```text
canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-023-COMMERCE-004
parent branch: task/ARCH-023-COMMERCE-004
implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-023-COMMERCE-004
implementation branch: task/ARCH-023-COMMERCE-004
shared workspace checkout switched/mutated for task work: no
shared implementation checkout switched/mutated for task work: no
another task worktree reused: no
parent remote task branch fast-forwarded: not-needed
parent origin/main incorporated: yes; synchronized head 93bb4f80ac05eb8090eeea4aad10f8d8d597f905
implementation remote task branch fast-forwarded: not-needed
implementation origin/main incorporated: already-current; synchronized head efee1b366f325c4d8b8c7c350950558699fcdff8
git submodule sync --recursive: passed
git submodule update --init --recursive: passed
database submodule: 6a8602e67d2308189af81ee0091e5189f1ffd71a (initialized, recursive)
claim: Attempt 1, copilot, committed and pushed as bd0fce1089b0325e33dbba52bb4d72a2ab57c88a
implementation commit: ea88b43cbdf676ee9963b88a7bbae5a6676a66ec (pushed to task/ARCH-023-COMMERCE-004)
```

Focused entitlement/policy/bootstrap tests: 3 files passed, 27 tests passed. Extended Merchant Knowledge tests (entitlement, policy, bootstrap, bootstrap startup, retrieval and contract): 6 files passed, 36 tests passed. Targeted ESLint on all five changed files passed with no output. `npm run typecheck` passed. `npm run build` passed, including manual/runtime package smoke checks, Prisma generation and Next.js production compilation; it emitted the existing Nunjucks dynamic-dependency warning. `git diff --check` passed.

The adjacent `tests/merchant-knowledge-embedding.test.ts` was also tried; one existing config-contract test fails because its `readConfig(base)` fixture omits the required `COMMERCE_BOOTSTRAP_ADMIN_EMAIL`. This task does not change that fixture or configuration contract. Live PostgreSQL/pgvector validation was not run: the guarded test requires an explicit safe loopback disposable `COMMERCE_TEST_DATABASE_URL`, which is not configured in this environment. No deployment database was used.
### Deviations
Live PostgreSQL/pgvector proof remains unrun because no safe disposable test URL is configured. The unrelated embedding-config fixture failure is recorded above and is not changed in this bounded task.
### Assumptions
The current active plan Feature relation is the source of truth for the `merchant_knowledge` Feature ID; `ShopFeaturePreference` absence is equivalent to opted out, consistent with the model's `enabled` default and opt-in activation mode.
### Unresolved Issues
Architect attribution is requested for the adjacent embedding-config test fixture failure and the unavailable disposable PostgreSQL/pgvector target.
### Architectural Concerns
None. The check remains operation-level and independent of the eligible Capability set; bootstrap and pgvector retrieval design are unchanged.

## Architect Review

### Review Status
Pending
### Review Notes
Pending.
### Reviewed Files
Pending.
### Validation Reviewed
Pending.
### Architecture Conformance
Pending.
### Follow-up
Pending.
