---
id: ARCH-072
title: Unified trusted recovery checkout footers
status: in_progress
coordinator: moda_architect
created: 2026-11-12
updated: 2026-11-12
---

# ARCH-072: Unified trusted recovery checkout footers

## Status and Problem

In Progress. User requests a checkout link on every recovery conversational outbound, including human takeover, with a visual divider. Existing domain helper/wrapper path is AI-only; human passthrough/frozen-command validation requires original text, and terminal notice text paths can replace prepared content with a fixed constant. ARCH070/071 remain completed.

## Goals / Non-Goals

One trusted footer/divider across all eligible known-recovery freeform AI/HUMAN/service/handoff/limit notices before immutable preparation. Preserve authored text and all consent/control/moderation/admission/permit guarantees. No appended mutation of approved templates or final permits, fabricated/unbound URL, schema/infra/credential/package release, new send authorization or production replay.

## Inspected Architecture and Target

Background conversation wrapper service loads trusted tenant/customer/status/lifetime/domain recovery context. Human preparation and persisted-command replay independently verify authored provenance; dispatcher moderates frozen effective text and sends committed permit content. Terminal text paths need the full trusted body prepared/moderated/fenced rather than a later constant override. Existing initial/follow-up templates already bind approved checkout parameters and cannot accept arbitrary post-appended text.

Reuse the domain helper for a consistent language-neutral divider and idempotent exact trusted URL/footer. Preserve labels/prose/unrelated links. Enable eligible HUMAN/AI and inventory every other freeform recovery send. A narrow trusted augmentation receipt/transform must be validated both during human preparation and persisted replay; do not broadly relax passthrough equality. Old frozen no-divider applications/commands remain byte-identical, and provider text equals the final committed/moderated body. Reject limits before admission without truncating URL; caption overflow retains existing full-text fallback.

## Event Flow and Ownership

Trusted recovery context -> authored/base body -> footer/divider -> immutable preparation/hash/media -> moderation/control/admission fence -> provider exact committed body -> existing durable status.

Background owns all identified helper/composition/human/notice paths. Existing Shared codecs/logging remain reused. No cross-service schema change is currently needed; return genuine contract gaps to architect. PostgreSQL schema, queue contracts, identity/ordering and retry semantics remain unchanged. User-controlled text cannot establish checkout/tenant authority.

## Coverage and Security

Every eligible known-recovery freeform conversational/service/limit send must be included. Inventory records all classes and exceptions. Successful approved templates retain approved body/checkout binding; unbound routing cannot invent tenant/basket context; STOP/consent/security/blocked prohibitions remain. Missing/expired/mismatched context follows existing safe policy without fabricated link. No old message replay or live implementation-test sends.

## Observability / Infrastructure / Scale

Existing shared structured semantic logs suffice; no generic logger/metric duplication or Gateway task. No topology/env change. Reuse loaded verified context where available; avoid new network work inside transactions, and preserve bounded preparation. No throughput claim or broad serialization change.

## Rollout / Migration

PRODUCTION / COMPATIBLE ROLLOUT. One Background-owned implementation -> architect acceptance -> developer merge/deploy -> authorized genuine human and AI/notice validation. No schema migration, queue drain or Shared publication. Preserve old frozen records and exact provider/permit equality; rollback code without rewriting durable messages.

## Decisions / Tasks

| Task | Owner | Status | Dependencies |
|---|---|---|---|
| ARCH-072-BACKGROUND-001 | moda_background | Ready | None |

## Validation / Completion Gate

Prior-code red human/terminal regressions, strict provenance/frozen replay/tamper tests, all eligible send classes/negative exclusions, actual preparation-moderation-fence-provider identity, relevant persistence integration, types/scoped lint/full CI and final developer production proof are required. No separate system-test task currently applies to this bounded same-repository footer mechanism; reassess if new cross-service/persistence work is discovered. Architecture remains In Progress until accepted integrated proof and documentation reconciliation.

## Open Questions / Change History

No blocking design question. Specialist inventory must enumerate coverage before completion; routine eligible notice inclusion is authorized. Public records use synthetic examples/coarse outcomes only.

- 2026-11-12: Read-only path review established AI guard, human dual provenance gates and terminal constant override; bounded unified recovery footer task defined.

- Inventory amendment: audio/transcription fallback and oversized-current clarification also bypass wrappers. Include their caller/local admission signatures under the same capability, using only server-owned recovery-only preparation for unfrozen notices before preparation/moderation/fence. Resolve verified context outside transactions; preserve ordinary frozen AI/media/legacy permits and all exclusions. No additional task/Shared wire or schema change is authorized.

- Final-permit identity amendment: delivery forwards existing optional expectedContent for recovery text, and automated permit SQL compares stored content only when supplied. Legacy absence/initial path and Shop lock ordering stay unchanged. Relevant disposable PostgreSQL match/mismatch/race proof is required; this closes the task existing exact prepared/moderated/provider-body criterion without schema or new wire.
