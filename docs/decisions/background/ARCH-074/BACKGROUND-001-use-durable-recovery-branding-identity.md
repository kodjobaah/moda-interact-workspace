---
id: ARCH-074-BACKGROUND-001
architecture_id: ARCH-074
title: Use durable recovery identity for prepared branded replies
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 5
executor: codex
claimed_at: 2026-11-12T22:53:43Z
attempt: 1
depends_on: []
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Use durable recovery identity for prepared branded replies

## Architecture

ARCH-074; docs/architecture/ARCH-074-recovery-branding-billing-scope.md; coordinator moda_architect.

## Objective

Deliver legitimate recovery-linked branded AI replies independently of billing executionScope while safely finalizing deterministic pre-provider suppression.

## Context

Normal/free contract admission returns general billing scope even for a linked recovery. Delivery's new BRAND_IMAGE scope guard confuses billing with durable recovery identity, then returns before placeholder cleanup. Processor ignores suppression result and reports a send. Existing durable recovery/current-control/final fence can supply the correct authority.

## Scope

Owning Background prepared text/conversation delivery and narrowly related notice preparation gates if they use the same incorrect billing proxy; existing AiTurnOwnershipService/checkAutomatedTurn integration; affected processor result/outcome handling; regression tests/docs. Inspect current exact source first. Root owns merge/deploy/live verification.

## Out of Scope

Billing/usage/entitlement policy changes, generic lifecycle refactor, tenant fallback inference, dropping branding on valid recovery solely to evade proof, source/media policy relaxation, schema/Shared/npm/infrastructure changes, unrelated tests/features, production writes/requeue/reset/replay or extra WhatsApp sends.

## Requirements

Keep normal/free billing classification unchanged. Use current AiTurnOwnershipService durable Conversation→CheckoutRecovery identity, exact expected shop, AI mode/revision and original inbound/control/message receipt to authorize a new recovery BRAND_IMAGE even when billing executionScope is general. Never substitute billing scope for relationship authority, or recapture newer ownership to legitimize stale work. General/unbound, missing/mismatched recovery and wrong tenant/control/version remain refused. Existing final Shop/consent/header/source/current READY/policy-row/idempotency fences are unchanged.

Deterministic pre-provider invalid prepared-plan/identity refusal must use existing conditional failPrepared cleanup so no empty PENDING phantom remains. Cleanup must never overwrite a permit, provider message, actual duplicate/admitted or uncertain outcome. Do not convert ambiguous provider attempts to retry or falsely claim cleanup success. Preserve provider-boundary safety flags unless a concrete tested correction is needed. Actual result is consumed at the affected AI caller: suppressed outcome cannot log agent-response-sent; turn completion/cleanup follows existing version-scoped rules and preserves newer input/control. No broad new retry policy.

Use shared logger for semantic outcomes; do not add generic telemetry or private payload logs. You are not alone: preserve others' work and only modify assigned owning modules. Return genuine cross-owner/contract gaps rather than unsafe workaround.

## Work Items

- [x] Reproduce normal-contract recovery branded suppression against original code.
- [x] Correct durable recovery eligibility with existing tenant/control/final fences.
- [x] Finalize deterministic pre-provider refusal and truthful caller outcome without touching committed/unknown sends.
- [x] Validate focused/integration/CI and publish mirrored report, then stop.

## Interfaces / Contracts

Existing Background admission/billing result, AiTurnOwnershipService/checkAutomatedTurn, OutboundSendFence, conditional failPrepared and published Shared5.13.7 media contract. No new wire/schema/authority contract.

## Dependencies

None. Current implementation main includes accepted ARCH-073.

## Enables

Developer source merge/deployment and fresh genuine customer verification.

## Acceptance Criteria

- [x] Normal/free contract with general billing scope and real same-tenant recovery can send exactly one branded AI image with exact full header/footer caption.
- [x] Generic/unbound/wrong-tenant/stale-control/inbound/lease/media/policy cases remain refused with no provider call.
- [x] Deterministic pre-provider suppression leaves no phantom pending placeholder or false sent outcome; duplicate/admitted/uncertain states unchanged.
- [x] Billing/usage semantics and all existing receipt/final-permit checks remain intact.
- [x] Canonical mirrored worktree/synchronization/recursive proof recorded; no private payload/source scope expansion.

## Validation

- [x] Meaningful prior-code red for normal/free contract actual recovery billing-general BRAND_IMAGE path.
- [x] Actual processor/admission policy→prepared branded delivery→final fence→mock provider regression with real PostgreSQL recovery state; Free/normal contract semantics exercised, not manually changing billing policy.
- [x] General/unbound and tenant/control/version negatives; pre-provider failPrepared leaves finalized row, already-admitted/duplicate/provider-uncertain preservation; caller outcome truthful.
- [x] Relevant existing billing/admission/processor/media regressions and actual PostgreSQL identity/cleanup checks.
- [x] Task-owned lint/typecheck/declared build and exact final-head full CI; inspect actual package scripts first.
- [x] Diff/privacy hygiene, synthetic/mocked providers, no production mutation/live sends during task validation.

## Stop Condition

After required work and validation complete, set review, submit Completion Report and STOP. Do not merge/deploy, retry production message or begin adjacent work.

## Implementation Notes

No broad billing-scope rename needed. Existing ownership read is durable linkage, not a model assertion. Existing conditional cleanup protects admitted messages. Source/turn completion must remain version-scoped. Preserve user changes and use the canonical prepared packet.

## Completion Report

### Status

Ready for Review. Implementation committed/pushed and all required validation passed; awaiting moda_architect review.

### Files Changed

- `outbound-message-delivery.service.ts`: BRAND_IMAGE authority uses current durable recovery/shop/AI-control identity and original receipt, independent of billing scope; related notice decoration uses durable ownership; deterministic invalid-presentation refusal performs scoped untouched-reservation cleanup; duplicate/uncertain permits and concurrent prepared winners remain unchanged.
- `outbound-provider-failure.service.ts`: optional expected tenant/conversation/untouched reservation predicates are checked in the existing transaction and conditional UPDATE, retaining all provider-outcome guards and legacy one-argument behavior; any existing moderation assessment conservatively blocks this new early-cleanup mode.
- `outbound-whatsapp-admission.types.ts` and reservation service: reuse the existing server-owned pending placeholder constant locally; no Shared/wire change.
- `conversation-turn-processor.service.ts`: consume returned delivery suppression and record `agent-response-suppressed` rather than claiming a send, preserving original version-scoped completion and conservative provider-boundary flags.
- Focused delivery/policy/processor/Woo compatibility and actual PostgreSQL normal Free-contract branding/cleanup regressions.

### Work Completed

The billing resolver and billing/usage policy are unchanged. Normal/Free contracts still return general billing scope for a recovery. New brand plans require `checkAutomatedTurn` with the original expected revision and exact shop; final recovery/consent/header/source/READY/public-policy/idempotency gates remain in place. Actual unbound or mismatched identity is not authorized by a billing flag.

Deterministic pre-provider validation can finalize only the exact untouched own reservation. Foreign, already prepared, provider-admitted/unknown and concurrent body winners are preserved. Existing legacy cleanup call arity is unchanged. No broad retry, lifecycle or provider-uncertainty policy was added. A failed preparation CAS is not blanket-cleaned, and assessed text is treated as frozen even when it matches the placeholder bytes.

### Validation Results

- Prepared execution `/tmp/moda-arch074-bg001-prepare.json`: task ARCH-074-BACKGROUND-001, both dedicated mirrored task branches, implementation base51043bfe8ba62ac11f10acdf9f7f28c7d7bd60cf; claim93d74adc4528a5977a889ae0ec796c5f3e28201e. Launcher already synchronized both worktrees and recursive database submodule5329d5390d346042895219663f3a040ea54ae168. No repeated claim or alternate checkout.
- Physical isolation: primary workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-074-BACKGROUND-001`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-074-BACKGROUND-001`; both branches `task/ARCH-074-BACKGROUND-001`. Launcher remote-task fast-forward was not needed and origin/main was already current for both. No shared/default checkout was switched or used for implementation, and no previous task worktree was reused. Recursive submodule sync/update passed at the recorded database commit.
- Safe actual-context reproduction supplied by root: normal contract/general billing, durable recovery/AI ownership, valid rendered BRAND_IMAGE/receipt/policy, followed by suppressed delivery before DB-write/provider/model work. No production message/requeue occurred.
- Original-code focused regression:7 meaningful failures/132 passing; updated owning source:139 passing across the same3 files. Additional CAS-winner and real PostgreSQL integrated tests passed as recorded below.
- Actual disposable PostgreSQL:33/33 passed across4 files (`arch074-recovery-branding.integration.test.ts`, existing ARCH073 logo/header and general STOP integration),53s. The new12 cases exercise actual Free-plan ACTIVE Subscription/default billing resolver returning general, actual processor/admission/wrapper/delivery/assessment/SQL final fence and exactly one mock-provider image; complete persisted TEXT caption, footer, original receipt and usage identity are asserted. Negatives cover unbound/foreign plan/stale control/inbound and exact scoped cleanup against foreign/frozen/modified/assessed/unknown-permit rows plus a real competing-body READ→UPDATE race.
- Focused owning3-file group139/139 passed after7 meaningful old-code reds. Latest affected Woo/outbound compatibility group64/64 passed, including exact legacy one-argument cleanup forwarding; additional CAS-winner coverage passed.
- Initial concurrent full local suite:4116 passed/10 skipped,9 failed (5 exact cleanup mock-arity failures corrected without weakening assertions;4 unchanged chronology subprocess timeouts under host contention). The isolated unchanged chronology file passed5/5 in5.43s. No timeout increase or unrelated source change.
- Source typecheck passed. Final declared `npm run build` passed (exit0) after PostgreSQL validation, without concurrent Prisma regeneration/tests; final9-file scoped ESLint passed. Implementation source committed/pushed at `d2060966cccdcd12e27cb8959e6c771d0de06a84`; PR [211](https://github.com/kodjobaah/moda-interact-background/pull/211). Both final exact-head full CI checks passed on `d2060966cccdcd12e27cb8959e6c771d0de06a84`: [push43328703989](https://github.com/kodjobaah/moda-interact-background/actions/runs/43328703989) (2m12s) and [PR43328740800](https://github.com/kodjobaah/moda-interact-background/actions/runs/43328740800) (2m33s). `gh pr checks211` confirms both required checks passed. No production writes, sends, requeues or input resets.

### Deviations

This agent's filesystem sandbox could not write the launcher-supplied sibling task worktree (EPERM on node_modules). As explicitly coordinated, source/test unified patches were prepared only in allowed `/tmp`; root applied them and runs validation in the exact canonical task worktree with its authorized access. The assigned repository agent reviews the resulting source read-only. No alternate implementation checkout, permission bypass or production network escalation was used.

### Assumptions

Existing verified media/source evidence and actual authenticated recovery authority remain required. This action-path fix creates no queue/schema/provider contract and does not change usage accounting; unused usage is released only under existing conditional cleanup plus the new exact untouched-identity predicates.

### Unresolved Issues

Root owns source integration/deployment, old-worker drain and a fresh genuine customer question. The previously consumed production turn must not be requeued/reset or represented as newly sent by this task. No live customer send is part of implementation validation.

### Architectural Concerns

Do not infer recovery identity from billing scope. Do not broaden scoped cleanup to a failed preparation CAS, prepared/frozen row, foreign tenant or an ambiguous/committed provider permit. Those preservation cases are explicit regression boundaries.

## Architect Review

### Review Status

Accepted

### Review Notes

Reviewed actual final `d2060966cccdcd12e27cb8959e6c771d0de06a84`, scoped cleanup follow-up, real PostgreSQL regression and durable report `34901d781`. Correct authority is the existing durable recovery/shop/original AI control receipt; billing policy remains unchanged. Scoped early cleanup rechecks exact untouched tenant/conversation/placeholder, SQL-null plan, no assessment and all no-provider/permit predicates. No findings.

### Reviewed Files

Prepared delivery/notice ownership checks, provider-failure conditional cleanup, local placeholder identity and reservation use, processor result/outcome, focused policy/delivery/processor compatibility cases and ARCH074 actual PostgreSQL test.

### Validation Reviewed

Original behavior7 red/132 passing then139/139 green; affected compatibility64; real PostgreSQL33 across4 files including actual Free policy→processor→branded single provider send and tenant/control/version/cleanup races. Types/scoped lint/build pass; both exact final-head CI passed. Initial local compatibility failures were corrected and chronology contention failures passed isolated without weakening; clean exact CI confirms final suite. Prepared dedicated mirrored isolation/base/database evidence verified. Owner-authored patches/root-applied tests in the same canonical worktree are transparent authorized execution assistance, not a shared-checkout exception.

### Architecture Conformance

Conforms to bounded Background correction, no billing/schema/Shared/infrastructure/permission change. Recovery unbound/wrong tenant/stale control remains refused, original receipts/final fences and uncertain-provider replay protected. Processor reports suppression truthfully and version-scoped completion remains. No production retry/reset/send occurred during implementation.

### Follow-up

Developer merges/deploys and verifies fresh genuine customer flow after old-reader drain. Architecture remains In Progress until actual branded AI provider delivery is observed. Historical orphan cleanup, if operationally authorized, must use existing conditional domain method and never requeue/reset the consumed turn or send an extra diagnostic message.
