---
id: ARCH-070-BACKGROUND-003
architecture_id: ARCH-070
title: Append trusted recovery checkout links to eligible AI replies
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 10
executor: codex
claimed_at: 2026-11-12T12:48:28Z
attempt: 1
depends_on: []
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Append trusted recovery checkout links to eligible AI replies

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; coordinator moda_architect.

## Objective

Deterministically include the verified recovery checkout link once in every eligible checkout-initiated AI response.

## Context

The user explicitly requires checkout links on subsequent replies. Published AI wrapper body may contain only response.body, so the model or wrapper definition cannot guarantee this. Existing wrapper context verifies conversation/recovery tenant/customer, status/lifetime and trusted HTTPS shop domain, exposing checkoutAvailable and checkout.url.

## Scope

Conversation wrapper service composition, dedicated recovery footer helper, compose-ai-outbound provenance adapter and directly related tests. Inspect actual paths before implementation. No host.ts or conversation-turn-processor edits (owned by other tasks).

## Out of Scope

Templates, credentials, model prompting, consent/STOP/moderation policy changes, unrelated Shared primitives, schema or infrastructure, duplicate sends or old-message replay.

## Requirements

Reuse existing trusted recovery context. For eligible AI recovery replies, append a deterministic checkout footer once across plain text, details, recommendations, wrapped and image-caption responses. Use existing localized checkout label/renderer if available; never fabricate a URL or accept model-supplied checkout links. Include footer before media/text limits, final moderation/control gates and delivery hashes. Preserve strict raw/provenance semantics with an explicit narrow trusted augmentation if required. Prevent repeated footer duplication. Missing/expired/wrong-tenant/unsafe recovery context remains fail-closed. Nonrecovery and STOP/consent/blocked/security responses must not accidentally reengage a checkout. Preserve privacy and deterministic retries. Return concrete Shared/contract gaps before implementing outside scope.

## Work Items

- [x] Establish exact source/fixture cause and preserve a failing regression.
- [x] Implement only the owned correction.
- [x] Validate positive and failure/recovery behavior and report evidence.

## Interfaces / Contracts

Consume published Shared contracts and existing MCP product evidence / durable conversation lifecycle. No new wire or schema contract is authorized. Cross-repository gaps return to architect.

## Dependencies

None. Disjoint wrapper assembly can execute independently of host recommendation and processor retry tasks.

## Enables

Developer integration and production verification after architect acceptance of both tasks.

## Acceptance Criteria

- [x] Requirements demonstrated with deterministic positive and negative regression tests.
- [x] Existing tenant, domain, message identity and lifecycle guarantees preserved.
- [x] No duplicate delivery, live test send, secret logging or unrelated changes.
- [x] Completion Report records canonical launcher packet, physical isolation, synchronization and recursive submodule evidence.

## Validation

- [x] Regression across plain/details/recommendation/wrapped/image caption paths; exactly one trusted URL footer.
- [x] Negative nonrecovery, expired/mismatched recovery, unsafe URL, STOP/blocked/control paths.
- [x] Provenance, length/media fallback, final control/moderation and deterministic delivery-hash tests.
- [x] Relevant existing wrapper/compose tests, typecheck, lint, required repository CI and diff hygiene.

## Stop Condition

Complete owned work and required validation, set review, return report and STOP. Do not merge, deploy or begin another task.

## Implementation Notes

You are not alone in the codebase. Preserve others' changes. Use the prepared dedicated mirrored worktrees and task branch. Verify actual package scripts before running checks. Existing structured semantic logs suffice; do not introduce competing logging or repeated provider work as a diagnostic mechanism.

## Completion Report

### Status

Ready for Review. Implementation committed and pushed on `task/ARCH-070-BACKGROUND-003`; no merge or deployment performed by this agent.

### Files Changed

- `src/services/conversation-wrappers/recovery-checkout-footer.ts`
- `src/services/conversation-wrappers/service.ts`
- `src/services/conversation-wrappers/contracts.ts`
- `src/services/conversation-wrappers/compose-ai-outbound.ts`
- `tests/unit/services/conversation-wrappers/recovery-checkout-footer.test.ts`
- `tests/integration/conversation-wrapper-rendering.integration.test.ts`

Implementation head: `b3b86c611633a6dc75a4e912960d8d76997cde9a`.
PR: https://github.com/kodjobaah/moda-interact-background/pull/201

### Work Completed

The published response-only wrapper previously returned an AI answer without the recovery link. A failing regression against the original service demonstrated the missing footer. The service now uses the existing tenant/customer/lifetime/status-verified `checkout.url` context to append the checkout footer to eligible AI replies before media planning, application/delivery hashes, and the existing downstream moderation/control/send gates.

Standalone exact raw checkout links are canonicalized once at the end. A selected complete link line retains its authored/localized label; other nonselected link-line words remain in ordinary content. Embedded Markdown/parenthesized links and unrelated URLs remain unchanged rather than being rewritten into dangling markup. A language-neutral raw URL is used when there is no authored link line. This is the root/coordinator-approved clarification of exactly-once raw link semantics.

Plain text, product details, recommendations, configured/unconfigured wrappers and image captions share the same footer assembly. Invalid URL augmentation and final overlength/control content fail closed. Captions exceeding 1024 code points fall back to the complete text plan. New augmentation is bound into application provenance; the adapter retains its exact no-wrapper body comparison except for the explicit verified footer. Original model envelopes and response digests remain unchanged.

A narrow pure second rendering is allowed only for `ALREADY_WRAPPED` with a trusted recovery context: the second call omits the optional checkout conditional while retaining all other authored header/footer guards. This handles a raw AI answer already ending in the checkout link without bypassing genuine wrapper detection. There are no placeholders or additional provider calls.

Previously prepared applications replay exactly as stored, including older applications lacking a footer. Nonrecovery/expired checkout contexts and HUMAN sources receive no new footer; STOP/consent/blocked/security processing paths remain outside normal AI composition. No source change was made to the commerce host, conversation processor, schema, credentials, templates, settings or provider configuration.

### Validation Results

- Regression against a temporary original-service fixture failed as expected: original body lacked the required checkout footer. Temporary baseline files removed afterward.
- Final focused wrapper suite: **75 passed**, including **29** task-specific footer tests. Coverage includes authored labels/custom footer, multiple-labelled-link idempotence, existing raw link, preserved embedded Markdown, unrelated URLs, unavailable/nonrecovery/HUMAN/tenant mismatch, unsafe URLs, control characters, exact passthrough, plain/details/recommendation plans, immutable replay/tampering, 4096 bounds, image caption and text fallback, unchanged original envelope and genuine `ALREADY_WRAPPED` rejection.
- Disposable PostgreSQL wrapper integration: **2 passed**. The existing fixture now explicitly seeds its seven-day persisted lifetime and asserts exactly one final checkout link. Schema migrations and disposable infrastructure are owned by the existing integration runner; no production access occurred.
- `npx tsc --noEmit`: passed.
- Scoped ESLint on all changed source/tests: passed.
- `git diff --check`: passed.
- Exact-head full CI: SUCCESS at https://github.com/kodjobaah/moda-interact-background/actions/runs/43225830011/job/131208628684 and https://github.com/kodjobaah/moda-interact-background/actions/runs/43225767629/job/131208404544 .
- An earlier accidentally broad unit invocation ran while source tests were in progress and produced seven SDK/startup timeouts and two stale footer assertions. It fully exited; it is diagnostic evidence only and is superseded by final focused and both green exact-head full CI runs. No unrelated process was stopped.

Physical worktree isolation (launcher packet `/tmp/moda-arch070-bg003-prepare.json`):

- canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-070-BACKGROUND-003`
- parent branch: `task/ARCH-070-BACKGROUND-003`
- implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-070-BACKGROUND-003`
- implementation branch: `task/ARCH-070-BACKGROUND-003`
- shared workspace/implementation checkout switched or mutated: no
- another task worktree reused: no

Start-of-attempt synchronization from the prepared packet:

- parent remote task branch fast-forward: not needed
- parent origin/main: already current
- implementation remote task branch fast-forward: not needed
- implementation origin/main: already current (`4ab78673b0fd479f74ef84acaccf1445c837c34b`)
- claim: codex attempt 1 at `2026-11-12T12:48:28Z`, parent claim commit `28d105b0ff426e2295d420994bdf64c0a393b944`
- recursive submodule sync/update: passed; `database` at recorded `5329d5390d346042895219663f3a040ea54ae168`
- final implementation tree: clean after commit/push

### Deviations

No functional scope deviation. The root/coordinator explicitly approved preserving embedded Markdown while canonicalizing only exact standalone raw checkout links, and retaining immutable prior-application replay. Initial integration attempt could not resolve Docker from the lean bootstrap PATH; adding the already-installed `/usr/local/bin` runtime tool directory resolved it without installation or configuration changes. Node was recovered only through the canonical bootstrap (`.nvmrc` 24.19.0).

### Assumptions

Eligibility is supplied by the existing verified recovery wrapper context. A footer is not a new checkout, purchase action or consent grant. Normal final moderation, ownership, admission and provider sending remain with their existing owners.

### Unresolved Issues

None in the bounded implementation. Root owns accepted merge/deployment and genuine production recommendation/footer verification.

### Architectural Concerns

No new Shared, schema, wire, infrastructure, logging or credential contract was required. Awaiting architect review.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual implementation review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
