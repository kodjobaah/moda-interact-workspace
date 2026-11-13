---
id: ARCH-075-BACKGROUND-004
architecture_id: ARCH-075
title: Recognize explicit published localized opt-out commands
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 5
executor: codex
claimed_at: 2026-11-13T07:31:55Z
attempt: 1
depends_on:
  - ARCH-075-BACKGROUND-003
  - ARCH-075-SHARED-004
enables:
  - ARCH-075-SYSTEM-TEST-001
created: 2026-11-13
updated: 2026-11-13
---

# Recognize explicit published localized opt-out commands

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Recognize explicit published localized opt-out commands.

## Context

Actual reviewed translated opt-out copy instructs STOPP, DUR, PARAR and STOPPA, while existing exact command matcher accepts only STOP/UNSUBSCRIBE. No live locale approval or send should promise an unrecognized opt-out command. This is a bounded consent correction, not language inference.

## Scope

Existing whatsapp-contact-opt-out/phone.ts explicit command matcher and directly related opt-out routing/priority/fence regression tests. Add only exact STOPP, DUR, PARAR and STOPPA to existing STOP/UNSUBSCRIBE semantics, preserving case-insensitive matching, existing trim and optional single dot/exclamation punctuation.

## Out of Scope

Substring or NLP matching, additional unreviewed aliases, changing consent priority/shop scope, Shared release/schema, template translation edits, live sends/DB writes/replays/resets, source merges or unrelated refactors.

## Requirements

Text-only whole-command recognition: STOP, UNSUBSCRIBE, STOPP, DUR, PARAR, STOPPA, existing trim/case and optional single . or !. No sentences/prefix/suffix/substrings/extra punctuation or nontext intent. Route recognized localized commands through the exact existing durable opt-out/tenant resolution and priority path before ordinary conversation/AI handling. Existing quoted/standalone merchant scope, STOP persistence-before-notice, duplicate behavior, no-contact and final send/continuation fences remain unchanged. Use synthetic data; do not change provider/customer state.

The finite reviewed 91-footer cohort establishes exactly these four additional commands. Any future unexpected translated command must remain unapproved until explicitly reviewed; do not broaden the matcher speculatively.

## Work Items

- [x] Reproduce exact localized command omission before correction.
- [x] Extend only explicit matcher and meaningful consent priority/scope/fence regressions.
- [x] Complete declared validation, mirrored report and stop.

## Interfaces / Contracts

Existing Background-local explicit WhatsApp opt-out command and durable consent pipeline. Published inbound schemas unchanged. No new shared parser is required for this single owning runtime policy.

## Dependencies

ARCH-075-BACKGROUND-003; ARCH-075-SHARED-004

## Enables

ARCH-075-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Exact STOPP/DUR/PARAR/STOPPA variants follow existing recognized-command behavior; sentences/substrings/malformed variants/nontext refuse.
- [x] Existing durable consent priority, merchant scope, duplicate and final-send/continuation suppression remain proven.
- [x] Canonical physical isolation/sync and exact validation evidence reported; no live mutation.

## Validation

- [x] Red/green exact matcher cases and negative boundaries; existing opt-out routing/priority and relevant send-fence/continuation regressions.
- [x] Declared relevant focused tests, scoped lint/typecheck and exact-head full CI; additional persistence tests only where actual changed path needs them.
- [x] Diff/privacy hygiene, no dependency/runtime-policy expansion or live requests.

## Stop Condition

After scope and required checks complete, set review, submit mirrored Completion Report and STOP. No dependent implementation or live action.

## Implementation Notes

You are not alone; preserve all other work. Canonical packet owns startup/isolation/claim. Root owns source merges and live locale approval. Return any newly discovered translated opt-out commands before expanding this exact allowlist.
## Completion Report

### Status

Ready for Review. Implementation and validation complete; awaiting moda_architect review.

### Files Changed

Implementation commit `6ba473bdd84d9f4b4e1f47e4bf0dfbf32bff583b` on `task/ARCH-075-BACKGROUND-004`:

- `src/services/whatsapp-contact-opt-out/phone.ts`: extend only exact command alternatives with STOPP, DUR, PARAR, STOPPA.
- `tests/unit/services/whatsapp-contact-opt-out.service.test.ts`: all-six-command boundary matrix and existing quoted scope, standalone duplicate and persistence-before-notice repair regressions.
- `tests/unit/workers/whatsapp.worker.test.ts`: parameterize consent priority ahead of abuse/routing/conversation work.
- `tests/integration/whatsapp-contact-opt-out.integration.test.ts`: all-six-command durable PostgreSQL consent, duplicate, later Shopify grant and merchant re-enable regression.

Draft implementation PR: https://github.com/kodjobaah/moda-interact-background/pull/215

### Work Completed

Added the finite reviewed four aliases exactly as amended by the architect in parent commit `27dc6c28c`. Existing trim/case/single optional punctuation, text-only boundaries, durable tenant resolution, consent priority and final fences are unchanged. No queue, database, Shared contract, dependencies, logging or runtime policy changed. Hot-path change is only four bounded regex alternatives; action-path database/provider costs remain unchanged. No live requests, provider mutations or developer/live database changes occurred; integration used the existing disposable infrastructure runner and synthetic fixtures.

Self-review: four implementation files only; exact regex anchors preserved; sentence/prefix/suffix/extra punctuation/nontext negatives covered; no customer content added. Latest Architect Review is Pending; there are no Changes Requested items to disposition. No architect decision is asserted.

### Validation Results

- Red: `npx vitest run tests/unit/services/whatsapp-contact-opt-out.service.test.ts` against unchanged source with complete six-command test matrix: 16 expected alias failures, 15 passes. Each missing alias failed matcher, quoted scope, standalone scope and persistence-before-notice scenarios.
- Green: `npx vitest run tests/unit/services/whatsapp-contact-opt-out.service.test.ts tests/unit/workers/whatsapp.worker.test.ts tests/unit/services/recovery-conversation tests/unit/services/conversation-turn-processor.service.test.ts tests/unit/services/woocommerce-recovery/woo-initial-send-fence.service.test.ts`: 18 files, 294 tests passed.
- `npx eslint src/services/whatsapp-contact-opt-out/phone.ts tests/unit/services/whatsapp-contact-opt-out.service.test.ts tests/unit/workers/whatsapp.worker.test.ts tests/integration/whatsapp-contact-opt-out.integration.test.ts`: passed.
- `npm run prisma:generate` and `npx tsc --noEmit`: passed.
- `node scripts/test-integration.mjs tests/integration/whatsapp-contact-opt-out.integration.test.ts tests/integration/woo-initial-send-fence.integration.test.ts tests/integration/woo-initial-send-fence-races.integration.test.ts tests/integration/conversation-turn-scheduling.integration.test.ts`: 4 files, 25 tests passed using disposable PostgreSQL/Redis. Includes durable no-contact, duplicate consent, final initial-send fence/races and continuation scheduling.
- `git diff --check`: passed. Dependency manifests/lockfile and database submodule unchanged.
- Exact-head full CI: passed (Prisma generation, TypeScript and full unit suite), run https://github.com/kodjobaah/moda-interact-background/actions/runs/43388148830 at `6ba473bdd84d9f4b4e1f47e4bf0dfbf32bff583b`.

### Physical Worktree Isolation and Launcher Evidence

Prepared packet `/tmp/moda-arch075-background004-prepare.json` supplied the following evidence; preparation/claim was not repeated:

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-BACKGROUND-004`; branch `task/ARCH-075-BACKGROUND-004`, reused.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-BACKGROUND-004`; same task branch, created by launcher.
- Shared workspace/implementation checkouts switched or mutated for task work: no. Another task worktree reused: no.
- Parent/implementation remote task fast-forward: not-needed; both origin/main incorporations: already-current.
- Recursive implementation submodule sync/update: passed. Database initialized at recorded commit `a9b6ab852a8245dfd14447808aac288a23b113d0`.
- Dependency gate passed; durable claim commit `0eb48f3a1dc5ba575efddf89a54d5d6146077e5e`, attempt 1, executor codex.

### Deviations

None. Additional reviewed aliases PARAR and STOPPA were implemented only after the authoritative task amendment.

### Assumptions

Future unexpected translated commands remain unapproved pending explicit review; no speculative aliases were introduced.

### Unresolved Issues

None. Exact-head remote CI passed.

### Architectural Concerns

None identified. Deployment and continued live locale verification remain outside this implementation task.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual source review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
