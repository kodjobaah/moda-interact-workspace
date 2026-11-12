---
id: ARCH-069
title: Chronological Commerce model conversation inputs
status: in_progress
coordinator: moda_architect
created: 2026-11-12
updated: 2026-11-12
---

# ARCH-069: Chronological Commerce model conversation inputs

## Status

In Progress. A bounded production correctness fix; no infrastructure or schema redesign.

## Problem

Production's 2026-11-12 snowboard question reached the model, which returned an inappropriate internal-looking indicator. The indicator's exact causal origin is not yet proven. Source inspection independently establishes a chronological ordering defect: Shared's OpenRouter adapter emits current trusted context (including the latest customer question) before older user/assistant history, potentially leaving a previous assistant failure notice as the latest conversational message.

## Goals

Send chronological prior history before current context, preserve current-turn tool results after current context, and consume the corrected published Shared package in Background. Record a bounded paired provider probe where practical without sending Meta messages or mutating production state. Do not claim that ordering caused the exact indicator unless evidence establishes it.

## Non-Goals

Sentinel blocklists, changing moderation or STOP policy, provider/model switching, prompt redesign, credential changes, message replay/duplicate sends, database migrations, queue contracts, new telemetry mechanisms and unrelated dependency upgrades.

## Current Architecture

Shared owns `OpenRouterModelClient` and model request serialization. Background supplies tenant-scoped current context, prior history, the pinned release and tools, then owns admission and delivery. The current serializer orders System -> current-context Human -> older history -> tool results.

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
| ARCH-069-BACKGROUND-001 | moda_background | In Progress | ARCH-069-SHARED-002 |

## System Validation

No separate system-test implementation task is introduced for this bounded serialization/dependency correction: deterministic adapter regression, Background integration checks and coordinator-owned no-send paired probe plus developer-authorized production conversation verification cover the change. Actual production correctness remains unverified until recorded by the coordinator; this architecture must not be marked Implemented prematurely.

## Open Questions

Does the paired real-model request probe reproduce the indicator, and does chronological ordering restore a grounded tool-using answer? If not, preserve the independently valid fix and return remaining causal investigation without overstating resolution.

## Change History

- 2026-11-12: Defined bounded ordering, exact-artifact publication and consumer tasks from inspected serializer behavior and production trace.

- 2026-11-12 review: Shared001 Accepted/Complete at8fefac2; publication Ready, Background Pending. Paired anonymized probes establish improved current-turn intent, not deterministic marker causality. Production customer answer remains pending.

- 2026-11-12 publication review: Shared002 Accepted/Complete from exact public registry metadata/integrity and publish receipt; Background Ready with mandatory actual public-registry install/CI integrity gate. Transient tarballCDN404 is not represented as verified deployment availability.
