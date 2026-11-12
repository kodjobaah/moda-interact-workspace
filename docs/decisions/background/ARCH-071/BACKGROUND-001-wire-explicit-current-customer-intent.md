---
id: ARCH-071-BACKGROUND-001
architecture_id: ARCH-071
title: Wire authoritative current customer utterances through published runner
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 10
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-071-SHARED-002
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Wire authoritative current customer utterances through published runner

## Architecture

ARCH-071; docs/architecture/ARCH-071-explicit-current-customer-intent.md; coordinator moda_architect.

## Objective

Wire authoritative current customer utterances through published runner without granting customer text policy or tenant authority.

## Context

Source inspection proves current customer text is nested only in data-only context whose instructions forbid establishing customer objective, while older user history has ordinary Human roles. A newer named subject was answered using prior product focus. Exact historical model reasoning/input is unavailable; structural contract mismatch is independently confirmed. ARCH070 is complete and remains closed. Root approved the additive typed contract and existing-budget constraints before execution.

## Scope

Exact published5.13.6 pin/lock/version assertions; host current-message mapping/removal of duplicate raw context field; authoritative current-window/moderation/role tests and actual published runner/model-boundary regressions.

## Out of Scope

Hardcoded product aliases, fuzzy ID guessing, clearing all prior product references, permission/tenant policy changes, alternate models, automatic product selection, additional repair loops, schema/infra/credentials, private prompt export and production replay.

## Requirements

Use only existing server-loaded context.conversation.messages from same-conversation INBOUND/CUSTOMER current-window, transcription-ready/moderation-allowed ordered rows under existing shop/recovery/version/control/lease fences. Map exact role:user/content messages to new typed field; validate roles rather than coerce merchant/assistant/system history. No raw database IDs required. Remove context.currentMessages duplicate only for this new typed caller; keep other recovery facts/history/product references/tools unchanged. No arbitrary JSON/tool/history extraction or synthesized fallback. Empty/malformed current branch must safely avoid model work under existing controlled failure/referral/suppression policy, not revive old intent or create repeated retries. Preserve32k existing history/current bounding, source privacy, before-model/tool/final control fences and all accepted ARCH069/070 behavior. Verify a new named subject supersedes prior focus via authorized lookup/clarification without hardcoded aliases or automatic product identity selection. Return additional runtime needs outside this wiring before broad refactor.

Approved scope clarification: this task wires the explicit current-input carrier and verifies named/typo switches. General underspecified multi-candidate semantic ambiguity is not deterministically solved or claimed; retain the two failed synthetic ambiguity samples/limitation, with no new resolver or restrictive choice UX. Uniquely supported named subjects may use authorized fresh reference lookup; no hardcoded alias/fuzzy identifier mapping is implemented.

## Work Items

- [x] Establish owned failing regression and exact caller/contract compatibility.
- [x] Implement only the defined owned outcome or approved exact release.
- [x] Validate required positive/negative boundaries and record exact artifact/heads.

## Interfaces / Contracts

Shared owns optional currentCustomerMessages exact role:user/content array contract and runtime validation. Producer Background attests its server-owned current-message source through existing turn identity/fences; the shape itself is not authentication. Runner forwards to ModelRequest, adapter presents dedicated current Human content; no arbitrary JSON promotion. Public package @modainteract/moda-interact-shared through appropriate commerce/model entrypoints. Legacy absence unchanged.

## Dependencies

ARCH-071-SHARED-002. Publication readiness additionally requires explicit user public-release approval; consumer waits actual canonical downloaded-byte acceptance.

## Enables

Next ARCH071 publication/consumer gate, followed by developer genuine production verification.

## Acceptance Criteria

- [x] Requirements hold, including current-intent objective boundary and unchanged security/budgets.
- [x] No silent truncation/drop/coercion, inferred input or tenant/permission promotion.
- [x] No private customer prose/operational identifiers in committed evidence or diagnostics.
- [x] Canonical mirrored physical isolation, synchronization and recursive submodule evidence recorded.

## Validation

- [x] Clean public exact artifact install/hash, actual authoritative loader/current-window/moderation/tenant/version/empty input tests, actual published runner/adapter history-context-current-tool ordering and no raw-context duplication; synthetic multi-turn named/typo search-or-clarify positive and injection/tenant/merchant-history negatives. Relevant controls/footer/regressions/types/scoped lint and final exact-head full CI; no real customer sends or processed input replay.
- [x] Scope/diff/secret hygiene.

## Stop Condition

Complete owned work and required validation, report REVIEW and STOP. No next task, merge/deploy or public publication outside explicit task authorization.

## Implementation Notes

You are not alone; preserve others. Use prepared packet paths/branch and actual package scripts. No source edits before prepared claim. For publication, reuse accepted artifact and do not repeat implementation checks. Public docs/probes use synthetic examples and coarse outcomes only.

## Completion Report

### Status

Ready for Review. Implementation and required exact-head validation committed/pushed; awaiting moda_architect review.

### Files Changed

- Exact Shared5.13.6 package/lock and three existing version-consumer assertions.
- `src/commerce/host.ts`: validate/copy authoritative current CUSTOMER/INBOUND batch using published helper after existing Shop/recovery/domain/AI/version/lease checks; forward typed field to runner and remove duplicate raw JSON field.
- `src/commerce/host-diagnostics.ts`: fixed safe typed invalid-current diagnostic, no raw validation cause.
- Actual host current-input/security and named-subject acceptance suites; loader provenance, production proxy and installed SDK serialization tests; terminal INVALID_INPUT processor regression.

### Work Completed

Only server-owned `context.conversation.messages` supplies the new currentCustomerMessages field. Roles/content are validated exactly, never coerced, trimmed, truncated or synthesized from history, merchant text, tools or arbitrary JSON. Shared prepares an immutable copy; host fails empty/malformed/invalid-role/over-budget batches with bounded typed nonretryable INVALID_INPUT before MCP/model work. No Zod cause or private current content is retained in the failure diagnostic. Existing terminal failure policy completes that exact inbound version after cleanup without sending or requeuing; no lifecycle source behavior changed.

Existing authoritative loader is preserved: same conversation and current pending-window, INBOUND/CUSTOMER, transcription-ready, moderation-approved, ascending createdAt/id. Tests assert query boundaries and actual filter invocation/order. Existing host tenant/version/control/lease/model/tool/final fences remain unchanged. Existing32k Unicode JSON budget is reused, including21 current fragments and a >16k UTF16 content example; no new lower row/text cap.

Audited all Background production model paths: host forwards the runner ModelRequest to production-model invoker; production-model.ts forwards the complete request to the published client unchanged. A production-proxy regression verifies exact typed-field identity. Actual installed public OpenRouter adapter regression intercepts only SDK construction, forbids provider network, and proves System→history→data context→dedicated current Human text→tool data, exact body once and no duplicate JSON body. Legacy optional-absent serializer tests remain green.

Synthetic named and misspelled new-subject host scenarios retain old-focus presentation and both candidate labels, carry latest text across all model steps, perform an authorized target search/fresh read and verify the new selected product rather than prior focus. These deterministic tests establish plumbing and evidence behavior, not language-model intelligence. Prior Shared frozen-provider exact/typo/harder named samples passed; two underspecified multi-candidate samples failed and remain an explicit known ambiguity limitation. No alias map, fuzzy identifier selection, automatic product choice or deterministic general ambiguity resolver was added or claimed. Existing footer, strict referral/selection, shipping, controls, retries and initial-outreach optional-absent consumers remain compatible.

### Validation Results

- Exact public5.13.6 fresh-cache installation `/tmp/moda-arch071-bg001-public-cache` succeeded609 packages; canonical tarball actual GET HTTP200/cache miss. Accepted517461-byte artifact hashfbe8e97a verified at publication gate; canonical lock integrity sha512-bcc7jKLRQU/c7uzLJxXtQbbILsYfCsBXwpdX4fwtejsPvV0fN98eWr49dqmoC7M+4BucF2CJ84n193qbIAJuew==.
- Prior host red proof: all10 new authoritative-current scenarios failed, demonstrating missing typed carrier/guard. Source restored unconditionally; no unrelated edits reverted.
- Full published runner/host suite125/125 passed, including named/typo new-focus lookup, empty/role/type/shape/Unicode budget, all-step propagation, trust and no-input-fallback negatives.
- Loader/current-window/moderation, production proxy and actual installed SDK serialization33 tests/5 files passed serially; no provider network.
- Recovery footer/control/legacy initial-outreach compatibility200 tests/11 files passed serially; final processor suite75/75 passed including new INVALID_INPUT terminal-cleanup/no-send vector.
- Final TypeScript and task-owned lint passed after added terminal vector. Existing untouched main four-unused-declaration lint baseline excluded from unrelated cleanup.
- All tests explicitly use loopback port1 DATABASE_URL/REDIS_URL and test deployment environment. No live provider, Meta send, production mutation, processed-input replay or private prompt export.
- PR https://github.com/kodjobaah/moda-interact-background/pull/205, final immutable implementationa570a6b33797044c04e0be76ac39244e5a9123fb. Both required exact-head full CI runs passed3,990 tests/369 files, including clean dependency install/Prisma generation/typecheck: https://github.com/kodjobaah/moda-interact-background/actions/runs/43264477203 and https://github.com/kodjobaah/moda-interact-background/actions/runs/43264461715.

### Physical Isolation / Launcher Evidence

Authoritative `/tmp/moda-arch071-bg001-prepare.json`; ARCH-071-BACKGROUND-001 attempt1 codex; claimed8fe40fe9872f0bb80c8de642b94c7d162499da committed/pushed by launcher. Canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-071-BACKGROUND-001`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-071-BACKGROUND-001`; both branches `task/ARCH-071-BACKGROUND-001`. Shared/default checkouts switched/mutated: no. Another task worktree reused: no.

Parent and implementation remote task fast-forward not needed; origin/main already current. Implementation basebada81e6a1a74add0c124de6c60eb72114c04e46. Recursive sync/update passed; database5329d5390d346042895219663f3a040ea54ae168 initialized at recorded commit. No parent implementation gitlink staged. Coordinator-owned architecture/index edits are excluded from this agent's staging.

### Deviations / Assumptions / Unresolved Issues

No scope deviation. No database/queue contract change or additional calls/repair loop. Host/loader use fixture database; database behavior unchanged and no broad unrelated PostgreSQL suite required. Historical exact model reasoning remains unknown. Generic underspecified ambiguity remains explicitly unresolved and is not claimed corrected. Root/developer owns merge/deploy and genuine named-subject production/Meta/footer verification after review; no production success claimed here.

### Architectural Concerns

None newly discovered beyond documented semantic ambiguity limitation. Implementation authority stops at review.

## Architect Review

### Review Status

Accepted — Attempt 1, under the documented carrier/named-switch scope.

### Review Notes

Reviewed exact a570a6b33797044c04e0be76ac39244e5a9123fb and durable report ae7bc9802. Published Shared 5.13.6 helper validates/copies only server-loaded current messages after existing owned-turn fences; malformed or empty input fails with a fixed nonretryable diagnostic and no raw validation cause. Host passes the explicit field and removes its raw context duplicate. No merchant/history promotion, invented fallback, new read or repair loop. Production proxy forwards the complete request unchanged. Runtime edits are limited to host wiring and a bounded diagnostic; loader/processor behavior is unchanged.

### Reviewed Files

Package/lock, host and host diagnostic; current-customer/known-reference host cases, authoritative loader/current-window tests, actual production proxy and installed SDK serialization tests, version assertions and terminal-input vector.

### Validation Reviewed

Ten prior-host red scenarios; final 125 host, 33 loader/proxy/SDK, 200 compatibility and 75 processor tests passed. Types/scoped lint/diff hygiene passed; unchanged existing full-lint baseline remains outside scope. Independently confirmed both exact-head CI runs passed 3990 tests/369 files. Clean public artifact installation/integrity and prepared physical worktree/start-sync/recursive database evidence verified. Fixtures used no live provider/database/customer sends.

### Architecture Conformance

Conforms to authoritative current-input provenance and existing tenant/version/control/lease, footer and delivery fences. Strict Unicode/shape limits preserve existing budgets without lower row/text caps. Deterministic tests prove carrier/authority boundaries; synthetic named/typo provider successes are separate empirical evidence. Both ambiguous multi-candidate samples remain failed and a general semantic resolver is not claimed.

### Follow-up

Developer may merge PR205 at exact reviewed head and deploy. Verify a genuinely new named/typo subject after prior focus on the final Live worker, grounded requested product and existing footer/Meta delivery without replay. Final parent gitlinks and architecture completion remain gated on that evidence; disclose the ambiguity limitation.
