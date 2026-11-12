---
id: ARCH-071
title: Explicit current customer conversation intent
status: implemented
coordinator: moda_architect
created: 2026-11-12
updated: 2026-11-12
---

# ARCH-071: Explicit current customer conversation intent

## Status

Implemented within the documented current-input carrier and named-switch scope. All three tasks are architect-accepted Complete. Final source is merged/deployed, and two successive genuine production named-product changes returned the requested products with the trusted recovery footer and confirmed delivery/read status. General underspecified multi-candidate ambiguity remains a transparent model limitation.

## Problem and Inspected Architecture

A newer named-product question received an answer about prior product focus. No transport replay or automatic sticky host override was established. Independently inspected source placed current customer text only in data-only context whose authority rules forbid establishing customer objective, while older customer history had ordinary Human roles. This was a structural request-contract mismatch; exact historical model reasoning was not captured or inferred.

The existing Background loader already selects same-conversation current-window INBOUND/CUSTOMER rows, checks transcription readiness and moderation, and orders them deterministically. Existing host fences verify shop/recovery/domain, control, inbound/processing version and lease before model/tool work. Those ownership boundaries remain unchanged.

## Goals and Non-Goals

Present explicit authoritative-source current customer utterances as conversation content, preserving older history and context/tool data separation. Current content establishes the customer objective subject to system policy; it grants no tenant, tool, consent or policy authority.

No hardcoded product aliases, implemented fuzzy identifier mapping, automatic product selection, clearing all references, new retry loop, alternate provider/model, database migration, infrastructure change or processed-input replay is introduced. A deterministic semantic ambiguity resolver or restrictive explicit-choice UX is outside this bounded fix.

## Contract and Serialization

Shared owns optional `currentCustomerMessages`, a readonly array of exact `{role: "user", content: string}` rows. When present, the array and content strings are nonempty, unknown fields/other roles are rejected, and raw whitespace/text is preserved. JSON-encoded current rows fit the existing 32000 Unicode-code-point budget without a new lower row/UTF16 cap. Context/history/current share the existing 131072-byte payload limit. Invalid input fails closed without dropping, truncation, coercion or provider work.

Runner preflight validates and freezes a copy. Every model step and forced correction forwards that snapshot. The direct adapter independently validates, suppresses private validation causes and serializes System -> older history -> data-only context -> dedicated current Human utterances -> current tool-result data. Optional absence retains legacy serialization/instructions; custom invokers opting in must preserve the new semantics, not merely compile against the type.

Opt-in instructions prioritize an explicitly named current subject over prior focus and retain bounded lookup/clarification guidance. Historical references remain candidate labels, not current facts or automatic identity. Context/tool/history JSON is never extracted or promoted into current customer input.

## Producer, Provenance and Event Flow

Background passes only its server-loaded current customer window through the published helper after existing owned-turn checks. It preserves roles rather than converting merchant/assistant history and removes the duplicate raw current-message context field only for the new typed caller. Other recovery facts, history, references and tools remain intact. Empty/malformed current input produces a bounded nonretryable host failure before model/MCP work; existing terminal cleanup prevents retry amplification. There is no invented fallback from older dialogue.

Authoritative loader -> tenant/version/control/lease fences -> strict current snapshot -> Shared model/correction propagation -> dedicated current Human content -> authorized lookup or answer -> existing fresh evidence, final controls, footer and delivery.

## Repository and Durable-State Boundaries

Shared owns canonical validation/types, propagation, serialization and opt-in instruction mechanics, published through existing commerce/model entrypoints. Background owns source provenance and service policy and consumes the exact published package rather than sibling source. No database schema, queue contract, transaction, ordering, lease or idempotency mechanism changed. Existing cancellation/budgets, strict final response, shipping evidence, recovery footer and delivery behavior from ARCH-069/070 remain intact.

## Security, Observability and Infrastructure

Current text supplies objective only; existing grants and tenant/control fences continue to deny unauthorized actions. Tests cover malformed roles/keys, fake current input in context/history, unauthorized tools, private error causes, moderation and current-window provenance. Diagnostics use bounded fixed states without customer prose or arbitrary validation keys.

Existing shared logging and operational signals suffice. No new generic logger/telemetry, Gateway task, service topology, environment variable or infrastructure configuration is required. Public evidence contains coarse outcomes and public source/release identities only; no operational/customer/provider identifiers, private prompt, recipient details or recovery URL is committed.

## Scope Decision and Known Limitation

Frozen synthetic provider cases passed exact-name, typo and harder-misspelling switches after a different prior focus. Both original and revised underspecified multiple-candidate samples still selected a candidate without clarification. They are failed samples and are not relabeled as successes.

Root explicitly approved separating the proven carrier/named-switch correction from a deterministic semantic resolver before acceptance. Fresh fact verification alone cannot prove intended identity. A reliable broader ambiguity boundary would require a separately designed resolution/choice contract, including presentation/ordinal/naming semantics. No additional prompt iteration or unrequested restrictive UX was silently added. Generic clarification guidance remains empirical model guidance; ambiguous requests can still be misinterpreted.

## Rollout and Compatibility

PRODUCTION / COMPATIBLE ROLLOUT: accepted Shared source -> explicit approval of the tested public artifact -> exact publication/download verification -> accepted Background wiring -> developer merge/deploy -> genuine production validation. No migration or queue drain was required. Optional absence preserves old callers. Rollback changes code/package revisions without rewriting processed messages.

Final Shared merge: `11c47feac3a823a586e5f597583c7eb0359b99ca` (PR80). Final Background merge: `60b8d0b2f2f80922e8194020e65dd74c16327cf7` (PR205). Developer reconciled final parent gitlinks in `63f4107a8`, excluding unrelated workspace changes.

Exact public package `@modainteract/moda-interact-shared@5.13.6` was published once after explicit user approval. Canonical metadata and actual downloaded 517461-byte artifact independently matched SHA256 `fbe8e97a3018ddcfbd29f85c4acc4fdab5447681bf94d4bc41695e6f6c44e049`. Release reused the accepted artifact without rebuilding or repeating implementation validation.

## Decisions / Tasks

| Task | Owner | Status | Dependencies |
|---|---|---|---|
| ARCH-071-SHARED-001 | moda_shared | Complete | None |
| ARCH-071-SHARED-002 | moda_shared | Complete | ARCH-071-SHARED-001; explicit public-release approval obtained |
| ARCH-071-BACKGROUND-001 | moda_background | Complete | ARCH-071-SHARED-002 |

## Validation

Task reports retain exact commands, reviewed heads and prepared mirrored isolation/synchronization evidence. Shared passed 755 full tests with three expected integration skips, types, ESM/DTS build, immutable installed JS/DTS/public exports and carrier/security regressions. Exact/typo/harder synthetic provider successes and both ambiguity failures are recorded separately; no private customer data or real commerce mutation was used.

Background passed 125 host,33 loader/proxy/installed-SDK,200 compatibility and75 processor checks, types/scoped lint and both exact-head full CI runs (3990 tests across369 files). Ten prior-host red cases established the original missing carrier/guard. Existing untouched full-lint unused declarations remain documented; no unrelated cleanup or full-lint success is claimed. Loader/database behavior is unchanged, so fixture/current-query tests were appropriate without a broad unrelated PostgreSQL suite.

No separate system-test task is applicable to this bounded request contract. Published-package/host/source-provenance/SDK tests, synthetic provider conformance and genuine production observation below cover the affected boundaries; no unrun terminal task is implied.

## Genuine Production Verification

The coordinator confirmed final source Live and the previous worker drained before requesting a fresh named-product change after a different prior focus. The misspelled named request reached the expected newly requested product, with fresh verified details and the correct product image/caption. The body ended with the exact active trusted recovery footer. Meta returned HTTP200/HTTP_ACCEPTED and durable status progressed to delivered and read. The first verified job completed on its first attempt.

A subsequent genuinely different named-product request also switched correctly and included the trusted footer, with delivered/read confirmation. Current turns closed, pending/processing state cleared and no new failed rows were observed. No spoofed request, manual database/queue mutation or processed-version replay was used. Detailed operational correlation remains protected outside source control.

These observations verify the reported named/typo switch in production; they do not establish a general ambiguity-resolution guarantee. The development store's previously documented password gate and lack of payment-completion testing are unchanged.

## Open Questions and Change History

None blocking for this scoped correction. Historical exact reasoning remains unconfirmed and general multi-candidate ambiguity remains disclosed.

- 2026-11-12: Source findings established the current-input/data-authority mismatch; additive contract and existing budgets approved.
- 2026-11-12: Synthetic ambiguity failures preserved and semantic resolver scope explicitly separated before acceptance.
- 2026-11-12: All three tasks accepted, exact approved release adopted, and successive genuine named switches verified through delivery/read. Architecture marked Implemented within stated limits.
