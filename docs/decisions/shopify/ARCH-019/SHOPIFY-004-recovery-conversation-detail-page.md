---
id: ARCH-019-SHOPIFY-004
architecture_id: ARCH-019
title: Build the read-only recovery conversation page
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 50
executor: codex
claimed_at: 2026-09-20T13:58:35Z
attempt: 2
depends_on:
  - ARCH-019-SHOPIFY-002
  - ARCH-019-SHOPIFY-003
enables:
  - ARCH-019-SHOPIFY-005
  - ARCH-019-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
---

# Build the read-only recovery conversation page

## Architecture

Architecture ID: ARCH-019

Architecture document: docs/architecture/ARCH-019-merchant-recovery-experience.md

Coordinator: moda_architect. Read the complete parent architecture and referenced dependency tasks before execution; it supplies exact data, route, access, compatibility and rollout contracts.

## Objective

Open a recovery directly into an accessible conversation with checkout context and related recoveries.

## Context

This task contributes one bounded capability to the recovery-first merchant journey. The previous UI mixed billing-period navigation, all-time recovery figures and a customer modal. The new design separates recovery performance, recovery conversation history and billing usage.

## Scope

app/routes.ts; new recovery detail/resource route modules and transcript/context components; recovery list link activation; focused tests and merchant locales.

## Out of Scope

Other repository implementation; billing/credit/provider semantics; new automated messages; reply/takeover controls; unrelated refactoring; main merges/pushes; live deployment. Do not start enabled tasks. Parent architecture/index reconciliation belongs to moda_architect.

## Requirements

The parent architecture's behavioural contracts are binding. Preserve current tenant/lifecycle rules and accepted ARCH-017 onboarding behaviour; do not restore stale ARCH-013 permissions. Follow repo-local AGENTS.md and the assigned logical agent definition. Never copy mockup sample data into production. Preserve unrelated changes by using canonical task worktrees.

## Work Items

- [x] Register /app/recoveries/:recoveryId with its own RECOVERY_HISTORY guard; use sibling routes or an outlet-only layout so the list loader is not unnecessarily run for detail.
- [x] Render chronological chat bubbles with explicit sender labels, merchant-zone date separators and applicable recorded delivery metadata.
- [x] Implement bounded message navigation and Jump to latest, plus the same-customer related-recovery selector using SHOPIFY-002.
- [x] Provide Back to recoveries preserving validated list filters/cursor and router scroll restoration; direct links use a safe default list.
- [x] Add desktop context column, compact mobile summary and secondary context, no-conversation/unsupported-message and section-local failure/retry states.

## Interfaces / Contracts

SHOPIFY-002 detail/transcript DTOs and SHOPIFY-003 RECOVERY_HISTORY/list context; do not widen lifecycle permissions.

## Dependencies

- ARCH-019-SHOPIFY-002
- ARCH-019-SHOPIFY-003

All listed dependencies must be Complete and architect-accepted. Consume actual accepted source revisions; a copied initial task snapshot is not acceptance evidence. The architect must reconcile accepted dependency metadata into this parent task branch before promotion; the prepared launcher gates dependencies from this branch, not directly from sibling worktrees. Unmerged accepted implementation prerequisites require the normal developer integration or explicit approved dependency-commit consumption before this task can use their code.

## Enables

- ARCH-019-SHOPIFY-005
- ARCH-019-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Opening a recovery never requires a modal or an extra recovery dropdown step.
- [x] Switching between a customer’s baskets preserves the original list return context; query parameters cannot become an arbitrary external return URL.
- [x] Transcript remains read-only; no reply, takeover, retry-send, cancellation or new provider call is introduced.
- [x] Message text is escaped and direction-aware; safe links exclude dangerous schemes; unknown data is represented honestly.
- [x] Keyboard navigation, long text/URLs, translated labels and RTL content fit narrow layouts without nested modal scrolling.
- [x] Detail/resource routes independently enforce authorization; foreign IDs look unavailable and never disclose another shop’s name.

## Validation

- [x] Run npm test -- tests/unit/recovery-detail-route.test.ts tests/unit/recovery-detail-readers.test.ts tests/unit/merchant-route-access-policy.test.ts tests/unit/merchant-i18n.test.ts.
- [x] Run npm run typecheck, npm run lint and git diff --check.
- [x] Use local browser fixtures to verify list → detail → related recovery → Back, reload/direct link, 100+ messages, keyboard operation and narrow layout.

New test filenames above are required deliverables, not claims that those suites already exist. Use current package.json scripts; do not invent success when a command cannot run. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md: fast local checks are agent-owned; long infrastructure/live commands are developer-owned unless exactly authorized. Required developer evidence may remain pending at review, never at acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's Work Items, Acceptance Criteria, Validation and Completion Report, publish task-owned mirrored branches and return to review. Record exact pending developer-validation commands if needed. Stop; do not start enabled tasks, merge/push main, or mark your own task Complete.

## Implementation Notes

Use scripts/start-agent-task.py through the normal /moda-task preparation path. Task creation has not claimed execution. Dedicated parent and implementation worktrees, synchronization and recursive database submodule preparation are mandatory when execution starts. Follow docs/agent-vcs-ownership-policy.md. The repository agent may update only this task's execution/report fields in parent docs; shared indexes and parent architecture remain architect-owned.

## Completion Report

### Status

Ready for Review. Attempt 1, executor codex. No architect acceptance decision has been made by this agent. Existing Architect Review remains unchanged.

### Files Changed

- `app/routes.ts`, `app/routes/app/recovery-detail/`: independently guarded detail page and message/related resources, safe list-return URL builders, chronological transcript, truthful message metadata, bounded navigation, section-local loading/errors/retries, and responsive context.
- `app/routes/app/recoveries/{access.server.ts,loader.server.ts,RecoveryList.tsx}`: extract the existing history guard unchanged for reuse by every endpoint, and activate native detail links.
- `app/root.jsx`: key recovery-list scroll restoration by pathname/query so the explicit Back link restores its prior position; other routes retain location-key behavior.
- All 20 locale catalogues: 23 translated detail keys, with all existing values preserved.
- `tests/unit/recovery-detail-route.test.ts`, `tests/unit/recovery-list-route.test.ts`: new detail/resource boundary tests and updated expectations for activated list links.
- `tests/browser/recovery-detail/`: synthetic 125-message fixture, actual viewport screenshots and reproduction/observation README.
- Parent report: this task file. Earlier synchronization conflict resolution was separately and explicitly authorized by the developer.

### Work Completed

- Detail is a sibling of the recovery list beneath the embedded app shell; it does not execute the list loader. Both standalone resource loaders independently authenticate, resolve the owned shop and enforce RECOVERY_HISTORY before calling the accepted readers. Permissions remain unchanged.
- The prepared implementation baseline includes accepted SHOPIFY-002 `1a60f1e17a27b9b927bb9a8b0bfff4c032a85e16` and SHOPIFY-003 `37c62cde6c23f78b8cb61472d6bd0b4c4ee53199` as integrated ancestors. No prerequisite feature merge or reader modification was necessary.
- Header presents customer/email/Guest, recorded decimal checkout value, current status and merchant-local start time. Transcript opens immediately, first chronological window; Previous/Next/Jump to latest use the accepted bounded reader. Related recoveries use the same owned-customer reader with five-row pages.
- Sender labels stay distinct from direction. Outbound receipt labels and timestamps use only persisted DTO fields. Inbound records have no outbound receipt. Unknown content/sender/status remains explicitly unavailable or unsupported. Voice messages show only successful persisted text or localized pending/rejected/failed/unavailable transcription labels.
- Text is escaped React content with automatic direction. Only explicit HTTP(S) links without URL credentials become external links with noopener/noreferrer. No media playback, raw metadata, provider IDs, composer, mutation controls or new provider calls.
- Back and related links serialize only normalized list filters, validated tenant-bound cursor and bounded embed context. Invalid return context falls back to the default list; arbitrary returnTo/shopId parameters never authorize or redirect. Root scroll restoration preserves the list query's position.
- Recorded milestones have no invented cancellation event. Responsive desktop context column becomes secondary collapsible context on mobile. Resource refresh revalidates only the selected section and retains the checkout header. Focus moves to the updated section heading after paging/retry.

### Validation Results

Agent-executed:

- Required command `npm test -- tests/unit/recovery-detail-route.test.ts tests/unit/recovery-detail-readers.test.ts tests/unit/merchant-route-access-policy.test.ts tests/unit/merchant-i18n.test.ts`: **122 passed, 4 files**, exit 0.
- Final expanded run adding `tests/unit/recovery-list-route.test.ts`: **145 passed, 5 files**, exit 0. Covers independent endpoint lifecycle/authentication, tenant input isolation, missing/foreign equivalence, bounded reader invocation, return URL validation, error containment, escaped content, sender/audio/receipt semantics and all-locale ICU parity. Accepted reader tests cover real keyset cursor semantics.
- `npm run typecheck`: non-zero, **173 diagnostics across 28 unchanged files**, no task-owned diagnostics. Every diagnostic file was compared with prepared HEAD and is unchanged. This is existing broader TYPECHECK-001 debt (the historical 48-error summary is stale), including accepted dependency helper diagnostics; it is not a clean repository typecheck.
- `npm run lint`: non-zero, **20 errors and 2 warnings across 15 unchanged files**. Each diagnostic file is byte-identical to prepared HEAD.
- Focused ESLint covering all new detail/access modules, touched recovery routes/root/registration, both changed test suites and the browser fixture: passed, no diagnostics.
- `git diff --check` and staged whitespace check: passed. Parsed locale comparison confirmed exactly 23 additions per catalogue and no changed existing values.
- Actual Chromium local fixture: list → detail → related → Back, same filters retained; list scroll restored from/to 900px. Direct detail and reload worked. First 50 messages, Next starting at 51, latest 76–125, previous 26–75; related Next bounded and controls/focus updated. Section failure retained checkout/related context; retry recovered. No-conversation and unavailable states rendered safely. Native disclosure toggled with Enter.
- Screenshots at 320px English, 390px German and 1024px desktop show wrapped long URLs/RTL text and responsive layouts, with no horizontal overflow. Structural loading/focus and safe literal script text observed. Evidence: `tests/browser/recovery-detail/README.md` and `evidence/{320,390,1024,error}.png`. Synthetic local component validation is separate from deployed Shopify embedding/system validation.
- Shopify toolkit search was unavailable (`fetch failed`); official Shopify React Router documentation was consulted as fallback for authenticate.admin and boundary header/error patterns: https://shopify.dev/docs/api/shopify-app-react-router/latest . Instrumentation was disabled; no user prompt telemetry was sent.

Developer validation required for this bounded task: none pending. Terminal architecture/system and deployed embedding validation remain later work; no live provider or infrastructure rehearsal was run here.

### Deviations

The task needs a small root ScrollRestoration change to fulfill its explicit list scroll-return requirement. Extracting the list guard avoids duplicating lifecycle policy and is covered by the existing list suite. No unrelated permission, schema, accounting or service change.

The first preparation encountered architecture/dependency documentation conflicts. The developer explicitly authorized the reviewed resolution; synchronization commits `33e0a064` and `1d6016ab` preserve accepted SHOPIFY-002 history and SHOPIFY-004 readiness while incorporating main. These precede the durable claim and do not constitute a new architect decision. The inherited database gitlink/config changes came from main synchronization, not implementation-agent feature pointer edits.

### Assumptions / Unresolved Issues

Full repository typecheck/lint remain non-zero only in untouched files. Browser fixture mocks authorization/data; actual server guard behavior is established by unit tests, not the fixture. The implementation uses the existing installed dependencies through an ignored node_modules symlink. No pending task-owned validation failure.

### Architectural Concerns

None newly required. No cross-repository implementation, new contracts, media/provider operations or downstream task launch.

### Git / VCS

- Task branch in both repositories: `task/ARCH-019-SHOPIFY-004`.
- Canonical primary workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-019-SHOPIFY-004` (reused).
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-019-SHOPIFY-004` (created by launcher).
- Prepared parent HEAD `1d6016ab4a8c8f2051c8084f6d6b0f60edf243b5`; remote task fast-forward not-needed, origin/main already-current after authorized conflict resolution.
- Prepared implementation HEAD `3e83d7ecdbebbca881552b67af182a30c22c068a`; remote task fast-forward not-needed, origin/main already-current.
- Recursive submodule sync/update passed; database ready at recorded `9c6a4d8402a01840e2ea8dc18e89171f00564d29`, unchanged by implementation.
- Durable launcher claim `7f2e23ed1b754cc2c1e3d7aba90feb53bf0746db`, Attempt 1, codex, `2026-09-20T13:26:33Z`, committed and pushed.
- Implementation commit **`1c89d3bd5e3bd3dd4f2cbb4afc496c1613bb57a0`**, pushed to `origin/task/ARCH-019-SHOPIFY-004` at the canonical `github.com/kodjobaah/moda-interact` remote. Automatic approval initially rejected unverified egress; matching origin/.gitmodules and explicit workflow publication requirements established destination trust, and retry succeeded.
- Parent review submission is the task-only commit containing this report; exact hash/push result is supplied in the final handoff to avoid a self-referential hash.
- Shared/default checkout switched/mutated for task implementation: no. Another task worktree reused: no. Parent implementation gitlink staged for review: no. Neither task branch merged into main; no main push, deployment, or enabled task execution.

## Architect Review

### Review Status

**Changes Requested — Attempt 1, 2026-09-20, moda_architect.**

Reviewed implementation `1c89d3bd5e3bd3dd4f2cbb4afc496c1613bb57a0` and submitted parent report `b471c06aecb54def1000d70d15f70b58cb23ecdd`; both remote task heads verified. Task returns to Ready with executor/claimed_at cleared and attempt 1 preserved. No architect acceptance is granted.

### Review Notes

**[P2] Restore list scroll across equivalent list URLs (`app/root.jsx:22-25`).** The new scroll key is the raw pathname plus search string, whereas the detail Back link reconstructs the list URL with explicit normalized defaults and a fixed parameter order. A normal entry at `/app/recoveries` therefore saves a different key from the Back destination. The list loader does not redirect that initial URL to its normalized equivalent. The submitted browser evidence only exercises a URL already serialized in the Back link's exact format.

Architect reproduction in the submitted local browser fixture: open `/app/recoveries`, scroll to `window.scrollY = 720`, open basket 5, then click **Back to recoveries**. The destination becomes `/app/recoveries?from=2026-09-01&to=2026-09-20&status=all&q=&pageSize=25&shop=fixture.myshopify.com` and `window.scrollY = 0`. This violates the explicit preserved-list-scroll acceptance criterion. Differently ordered equivalent filter URLs have the same key mismatch.

Use one stable, validated list identity for saving and restoring scroll, or preserve the original list entry identity through detail/related navigation while retaining the safe direct-link fallback. Do not introduce an arbitrary return URL or weaken tenant/cursor validation. Add regression coverage for omitted defaults and reordered filter parameters, including list → detail → related → Back; retain coverage for canonical URLs, cursor pages and direct detail entry.

### Reviewed Files

Detail route/section loaders and route registration; extracted recovery-history access guard; detail component, message rendering, navigation helpers and CSS; list detail links; root ScrollRestoration; route tests and browser fixture/evidence; Completion Report and prepared isolation/synchronization record.

### Validation Reviewed

- Architect reran the exact expanded command: `npm test -- tests/unit/recovery-detail-route.test.ts tests/unit/recovery-detail-readers.test.ts tests/unit/merchant-route-access-policy.test.ts tests/unit/merchant-i18n.test.ts tests/unit/recovery-list-route.test.ts`: **145 tests passed, 5 files**.
- Architect independently reproduced the default-list scroll defect in the running synthetic fixture using the production list/detail components and the submitted restoration key.
- Submitted report records full typecheck/lint failures in unchanged files and focused lint success. Those broad commands were not rerun for this Changes Requested decision; they are not represented as clean checks.
- Dedicated parent and implementation worktrees, matching task branches, prepared base/claim and recursive database evidence are recorded. Implementation remained unchanged during review.

### Architecture Conformance

Independent authentication/ownership guards, bounded section readers, safe message rendering and read-only behavior conform to the inspected contract. Scroll restoration remains an unresolved task-owned acceptance failure. ARCH-019 remains In Progress; SHOPIFY-005/006 and terminal SYSTEM-TEST-001 remain Pending.

### Follow-up

moda_app must reclaim the same task for Attempt 2, repair the restoration identity, rerun focused validation and the expanded navigation scenarios, and resubmit both task branches. Preserve Attempt 1 evidence and this review. No downstream task was launched or promoted.
