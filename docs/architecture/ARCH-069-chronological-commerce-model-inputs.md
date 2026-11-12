---
id: ARCH-069
title: Chronological Commerce model conversation inputs
status: implemented
coordinator: moda_architect
created: 2026-11-12
updated: 2026-11-12
---

# ARCH-069: Chronological Commerce model conversation inputs

## Status

Implemented. All three tasks are architect-accepted Complete. Production deployed the accepted Background merge and a fresh genuine question received a grounded snowboard answer, confirmed read and visible in the customer screenshot. No infrastructure or schema redesign.

## Problem

Production's 2026-11-12 snowboard question reached the model, which returned an inappropriate internal-looking indicator. The indicator's exact causal origin is not yet proven. Source inspection independently establishes a chronological ordering defect: Shared's OpenRouter adapter emits current trusted context (including the latest customer question) before older user/assistant history, potentially leaving a previous assistant failure notice as the latest conversational message.

## Goals

Send chronological prior history before current context, preserve current-turn tool results after current context, and consume the corrected published Shared package in Background. Record a bounded paired provider probe where practical without sending Meta messages or mutating production state. Do not claim that ordering caused the exact indicator unless evidence establishes it.

## Non-Goals

Sentinel blocklists, changing moderation or STOP policy, provider/model switching, prompt redesign, credential changes, message replay/duplicate sends, database migrations, queue contracts, new telemetry mechanisms and unrelated dependency upgrades.

## Current Architecture

Shared owns `OpenRouterModelClient` and model request serialization. Background supplies tenant-scoped current context, prior history, the pinned release and tools, then owns admission and delivery. The pre-fix serializer ordered System -> current-context Human -> older history -> tool results; the accepted serializer places current context after older history.

## Proposed Architecture

Retain the existing request contract and validation. Serialize System -> validated older history -> current-context Human -> current-turn tool results. Preserve every message's content and role, tool-result ownership, request budgets and cancellation semantics.

## Request / Event Flow

Background scoped context/history -> published Shared serializer -> OpenRouter -> Shared runner -> Background admission/delivery. Production verification remains separately gated and must not resend an already-delivered message merely to validate serialization.

## Repository Responsibilities

Shared implements and validates ordering, then publishes the exact accepted artifact. Background adopts that version and validates consumption. The coordinating developer performs final Git integration and production verification.

## Data Model

No schema or durable state changes. Production diagnostic reconstruction is read-only and never alters processed inbound versions, grants, usage or consent.

## Contracts

Owner: moda-interact-shared. Published entrypoint: `@modainteract/moda-interact-shared/commerce/model/node`; existing ModelRequest/ModelStep contracts and schemas stay unchanged. Background consumes the published package rather than sibling source imports.

## Consistency and Transactions

No transaction or idempotency changes. Diagnostic probes must not invoke WhatsApp delivery and must not create or replay production turns.

## Ordering

Older user/assistant history precedes current trusted context; current-turn tool results follow that context. Invalid histories remain rejected.

## Failure Handling

Keep provider failure classification, cancellation, deadline, retry and tool-call semantics unchanged. Do not hide malformed input or replace the indicator with a hard-coded answer.

## Scalability

This is per-model-call serialization work, with no additional database/network calls in the production hot path. No capacity increase is claimed or required.

## Security

Preserve system/data trust boundaries, tenant isolation and current tool grants. No credentials or private reconstructed prompts in source control or generic logs. Private live probe artifacts stay protected outside committed files.

## Observability

Existing correlated model/turn/provider events and Meta response logs suffice. No new metric, span, logger or observability task is required. Diagnostic results must distinguish reconstructed/no-send checks from actual customer-facing production verification.

## Infrastructure Assessment

No Gateway task is required: service exposure, private networking, environment variables and topology do not change.

## Rollout / Migration

PRODUCTION / COMPATIBLE ROLLOUT. Shared implementation acceptance -> exact package publication -> Background adoption acceptance -> developer merges/deploys -> bounded production verification. No queue drain or database migration. Existing request shapes remain compatible; rollback is the prior package version without rewriting durable messages.

## Decisions / Tasks

| Task | Owner | Status | Depends On |
|---|---|---|---|
| ARCH-069-SHARED-001 | moda_shared | Complete | None |
| ARCH-069-SHARED-002 | moda_shared | Complete | ARCH-069-SHARED-001 |
| ARCH-069-BACKGROUND-001 | moda_background | Complete | ARCH-069-SHARED-002 |

## System Validation

No separate system-test implementation task is introduced for this bounded serialization/dependency correction: deterministic adapter regression, Background integration checks and coordinator-owned no-send paired probe plus developer-authorized production conversation verification cover the change. The coordinator verified the fresh production conversation below after deployment; the integrated verification gate is complete.

## Open Questions

None blocking. Paired anonymized probes demonstrated incorrect intent with the old order and correct product-tool selection with chronological inputs. The exact indicator is stochastic model output; deterministic marker-specific causality is not claimed.

## Change History

- 2026-11-12: Defined bounded ordering, exact-artifact publication and consumer tasks from inspected serializer behavior and production trace.

- 2026-11-12 review: Shared001 Accepted/Complete at8fefac2; publication Ready, Background Pending. Paired anonymized probes establish improved current-turn intent, not deterministic marker causality. Production customer answer remains pending.

- 2026-11-12 publication review: Shared002 Accepted/Complete from exact public registry metadata/integrity and publish receipt; Background Ready with mandatory actual public-registry install/CI integrity gate. Transient tarballCDN404 is not represented as verified deployment availability.

- 2026-11-12 consumer review: Background001 Accepted/Complete at6ccad024; actual public-registry artifact install/hash gate and both3,941-test CI runs passed, resolving CDN propagation. Production customer-answer verification remains pending; no Implemented claim.


## Integrated Production Verification — 2026-11-12

Shared PR76 merged at `ea82023e831e77cd4c964df9a697ad17a9c1a1fb`; Background PR199 merged at `4ab78673b0fd479f74ef84acaccf1445c837c34b`. Developer-owned parent gitlinks were reconciled in `135a4965144668293033f9880e98ce71e79615bc`. Production messaging worker `srv-dbpojjmc6qcc73e56on0` was Live on that Background merge in Render deploy `dep-dbqqc52jnfac73bsnv0g`.

The coordinating developer correlated genuine fresh inbound `cmwdivna20041qu15ck1dwcvt` at 12:26:54.708Z, conversation `cmwcxdt0o0009kp164raxldna`, inboundVersion 3, asking “Can you tell me about this snowboard?”. `commerce_get_product` started 12:27:03.751Z and completed successfully 12:27:04.941Z. The two-step model turn made one remote call and returned ANSWER with verified PRODUCT_DETAILS, detailCount 1. Outbound `cmwdivqsg0043qu15e2dzh00l` correctly described The Multi-managed Snowboard, USD 629.95, stock 100 and Multi-managed Vendor.

Existing `whatsapp.meta.send.response` at 12:27:16.736Z recorded HTTP 200 / HTTP_ACCEPTED, request ID `AkZTKrSgqdUEMzyOPsPIMC_`, and an untruncated response with contacts redacted. The turn job completed 12:27:17.019Z on attempt 1. Durable status advanced to DELIVERED at 12:27:19Z and READ at 12:27:47Z with no failure code. The user's 12:28:36 screenshot independently confirmed the snowboard image and factual caption visible at 12:27. No processed inbound was reset or replayed. Evidence was supplied by the coordinating developer from production logs/state and the user's screenshot; no credentials, recipient numbers or private full prompts are committed.

- 2026-11-12 final review: production deployment, grounded tool-using answer, Meta acceptance, delivery, read receipt and customer-visible screenshot verified. Architecture marked Implemented. No further implementation or infrastructure changes required.
