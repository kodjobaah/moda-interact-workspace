---
id: ARCH-071
title: Explicit current customer conversation intent
status: in_progress
coordinator: moda_architect
created: 2026-11-12
updated: 2026-11-12
---

# ARCH-071: Explicit current customer conversation intent

## Status

In Progress. Root approved additive typed current-customer contract after read-only owner/source investigation. Shared source task Ready; publication and consumer Pending. ARCH070 remains completed and unchanged.

## Problem and Current Architecture

A genuine newer named-product question received a new answer about prior focus. Transport/delivery succeeded; no sticky host override or replay was established. Exact historical complete model input/reasoning is unavailable. Independently inspected source places current customer text only inside context.currentMessages, serialized as data-only JSON; runtime-data authority instructions forbid that context from establishing objective. Older customer history is serialized as ordinary Human content. This is a structural current-intent contract mismatch.

Background authoritative history loader already selects same-conversation INBOUND/CUSTOMER current-window rows, transcription-ready and moderation-allowed, in chronological order. Existing host checks shop/recovery/domain, AI control, inbound/processing version and lease before model/tools. Current entries use role/content shape and existing32,000 Unicode-code-point JSON budget; older history trims separately. The adapter's16,000 legacy history cap is not the current-message contract.

## Goals / Non-Goals

Explicit server-owned current customer utterances establish present objective through dedicated Human messages, while history remains reference and context/tools remain data. Preserve permission/tenant/system policy, exact chronology, old optional-absent compatibility and all prior accepted selection/referral/footer/retry behavior. No hardcoded product aliases, fuzzy identifier selection, automatic product choice, extra retry loop, provider switch, schema/infra/credential change or production replay.

## Proposed Architecture and Contracts

Shared defines optional currentCustomerMessages: readonly {role:user,content:string}[], strict and nonempty when present, role/content only. Current JSON-encoded array fits32,000 Unicode code points with no arbitrary lower row/pertext limit; existing overall payload byte cap still applies. Invalid role/shape/budget fails closed without provider work, truncation, dropping or coercion. Runner preflight validates/copies, every step/repair forwards, and direct adapter validates independently. Optional absence leaves legacy behavior unchanged; opted-in custom invokers must honor the new field.

Serialization order is System -> older history -> data-only context -> dedicated current Human utterances -> current-turn tool data. Explicit current utterances can establish request/objective, never permissions or tenant authority. Latest named subject takes precedence over prior focus; typo/ambiguity uses bounded authorized lookup or clarification, not aliases or guessed IDs. Arbitrary JSON, tool text and merchant/history rows are never promoted into current input.

Background maps only its authoritative current customer source under existing turn fences and removes duplicate context.currentMessages only for the new typed caller. Other context facts, history and product references stay intact. Empty/malformed current batches must safely avoid model work under existing failure/referral/suppression policy, never synthesize intent or revive older focus.

## Request / Event Flow

Authoritative current-window loader -> existing tenant/version/control/lease fences -> optional typed current field -> Shared validation/copy -> model history/context/current/tools ordering -> bounded authorized search/clarification or verified answer -> existing final controls/footer/delivery.

## Repository / Data / Failure Boundaries

Shared owns canonical contract/validation/serialization/instruction mechanics and exact release. Background owns source provenance, domain data and existing authorization/control/freshness. No database migration, queue contract or durable lifecycle change. Keep existing cancellation, budgets, strict final validation, retries and idempotency. New input validation must not cause repeat-processing amplification.

## Security and Observability

Current text remains untrusted for policy/tool/tenant authority even though it supplies customer objective. Prompt injection, fake current fields in context/tool/history and cross-tenant/stale inputs require negative regressions. Existing shared logging suffices; diagnostics, if needed, use counts/lengths/booleans only. Public records use synthetic examples/coarse outcomes; no private customer text or operational identifiers. No new telemetry/Gateway task required: topology/env unchanged.

## Rollout / Migration

PRODUCTION / COMPATIBLE ROLLOUT. Shared additive implementation acceptance -> explicit user approval for concrete tested public5.13.6 artifact -> exact publication/download integrity -> Background adoption/wiring acceptance -> developer merge/deploy -> genuine new-subject production validation. No queue drain or migration. Optional absence preserves old callers; new Background uses published field, never sibling source. Rollback is prior code/package without rewriting processed messages.

## Decisions / Tasks

| Task | Owner | Status | Dependencies |
|---|---|---|---|
| ARCH-071-SHARED-001 | moda_shared | Ready | None |
| ARCH-071-SHARED-002 | moda_shared | Pending | ARCH-071-SHARED-001 and explicit public-release approval |
| ARCH-071-BACKGROUND-001 | moda_background | Pending | ARCH-071-SHARED-002 |

## Validation and Completion Gate

Deterministic schema/order/all-step propagation and security tests, actual published runner/host source-provenance regressions, synthetic multi-turn real-provider named/typo switch conformance and final genuine production new-subject response are required. Old-subject automatic answering is not accepted; valid new lookup or clear ambiguity clarification is. No separate system-test task currently applicable to this bounded request contract; reevaluate if implementation discovers wider boundaries. Architecture remains In Progress until genuine integrated proof and documentation reconciliation.

## Open Questions

No blocking design question; root approved exact role/content shape, existing32k budget, optional absence and trust distinction. Exact historical reasoning is not inferred.

## Change History

- 2026-11-12: Read-only source findings established current-input/data-authority mismatch; root approved additive explicit current-customer conversation contract and gated release/adoption.

- Routine contract clarification: present current batches and each content string are nonempty; raw whitespace/text is preserved without trimming. Empty strings fail closed, with no synthesized fallback or silent dropping. Existing32k Unicode JSON and overall-byte limits unchanged.

- Synthetic provider validation finding before acceptance: exact new-name and typo cases used appropriate fresh identity/read or authorized search, but a multiple-candidate ambiguous case selected a known candidate without clarification. No private customer context or real commerce calls were used. Acceptance/publication remains gated; generic identity-resolution guidance is refined and final checks/provider cases must rerun on the frozen candidate. Fresh facts alone do not establish intended subject; recency does not resolve multiple plausible candidates. These model samples are empirical conformance evidence, not a deterministic semantic resolver or historical-reasoning proof.
