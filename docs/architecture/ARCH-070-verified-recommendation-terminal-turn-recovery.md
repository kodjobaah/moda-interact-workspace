---
id: ARCH-070
title: Verified recommendation evidence and terminal turn recovery
status: in_progress
coordinator: moda_architect
created: 2026-11-12
updated: 2026-11-12
---

# ARCH-070: Verified recommendation evidence and terminal turn recovery

## Status

In Progress. Background retry correction is independently executing. Recommendation correction waits for Shared nullable PRODUCT_ONLY URL contract and exact publication. ARCH-069's verified product-details answer remains valid; this initiative addresses a later recommendation failure.

## Problem

Production inboundVersion 4 recommendation refreshed three candidates but rejected all as PRODUCT_REFRESH_NOT_VERIFIED, then MISSING_VERIFIED_PRODUCT_SELECTION / INVALID_FINAL with retryable false. Pending-turn repair nevertheless repeated processing every 30 seconds. Candidate verification and terminal repair eligibility are distinct defects and ownership scopes.

## Goals

Accept legitimate provider-shaped refreshed product evidence while preserving tenant/domain checks. Stop repeated processing of a terminal failure for the same inbound version while admitting genuinely newer messages and preserving crash/transient recovery.

## Non-Goals

Relaxed verification, arbitrary model changes, schema/contract changes without owning tasks, new telemetry, infrastructure changes, reset/replay of processed messages and unrelated refactors.

## Current Architecture

Background host refreshes and verifies recommendation products before final composition. Conversation processor classifies failures and pending repair scans durable pending turns. Existing correlated production logs establish the observed failure sequence; task owners must corroborate precise causes in actual code/fixtures before correction.

## Proposed Architecture

Retain contracts and existing reusable Shared primitives. Correct evidence consumption in the host once actual MCP shape is established. Enforce a durable, inbound-version-scoped terminal failure condition consistently in processor and repair. If existing durable models cannot represent this correctly, return the dependency for a Database task rather than inventing unsafe process-local state.

## Request / Event Flow

Inbound -> durable version/turn -> model/tools -> refreshed product evidence -> verified final response or classified failure -> repair only where durable state and retry policy permit.

## Repository Responsibilities

Background001 owns commerce host evidence composition. Background002 owns processor/repair lifecycle. Neither edits the other's modules. MCP, Shared and Database changes require separately defined tasks if investigation proves them necessary. Root/developer owns final merges/deployments and production checks.

## Data Model / Consistency / Ordering

No schema migration currently authorized. Preserve existing transactions, leases, deduplication and concurrency. Terminal eligibility is scoped to the exact inbound version; a newer version remains eligible. Never mark a failed old version as delivered or reset processed input to test.

## Contracts / Security

Published Shared contracts and MCP evidence remain canonical. Cross-shop/domain/product/variant mismatch and malformed evidence fail closed. No credentials or unnecessary customer payloads in committed evidence.

## Failure Handling

Nonretryable failures must not trigger periodic repeated model/tool work. Retryable failures and worker crash recovery remain bounded and recoverable. No blanket skipping of pending conversations.

## Scalability

Remove retry amplification on terminal turns without adding per-message provider calls or broad serialization. No capacity claim is made.

## Observability / Infrastructure Assessment

Existing turn, model, tool and repair events suffice; no telemetry implementation or Gateway task is required. No topology/env changes. Record production environment identity and correlation in bounded evidence.

## Rollout / Migration

PRODUCTION / COMPATIBLE ROLLOUT. Independently accept both tasks, developer integrates both Background commits, runs CI and deploys. No queue drain or schema migration planned. No automatic replay. Verify new genuine customer request after rollout, provider acceptance and durable delivery; separately verify repair stops on the same terminal version.

## Decisions / Tasks

| Task | Owner | Status | Dependencies |
|---|---|---|---|
| ARCH-070-SHARED-001 | moda_shared | Ready | None |
| ARCH-070-SHARED-002 | moda_shared | Pending | ARCH-070-SHARED-001 |
| ARCH-070-BACKGROUND-001 | moda_background | Pending | ARCH-070-SHARED-002 |
| ARCH-070-BACKGROUND-002 | moda_background | In Progress | None |
| ARCH-070-BACKGROUND-003 | moda_background | Ready | None |

## System Validation

No separate terminal system-test task is currently necessary for this bounded correction: deterministic host fixtures, lifecycle/repeated-repair and relevant PostgreSQL tests plus developer-owned production observation cover the affected paths. Reassess if cross-service/schema changes become required. Architecture remains In Progress until production verification is recorded.

## Open Questions

Exact valid refreshed product evidence mismatch and exact existing durable terminal representation must be established by owning investigators.

## Change History

- 2026-11-12: Split recommendation evidence and terminal retry amplification into disjoint independently reviewable Background tasks.

- 2026-11-12 dependency amendment: valid ACTIVE available catalogue products have null onlineStoreUrl; MCP permits this but Shared schema/render and Background refresh reject it. Shared5.13.3 adds nullable URL only PRODUCT_ONLY with link omission; mutations/non-null URL checks unchanged. Shared acceptance -> exact publication -> Background exact-version adoption. Retry task ships independently to stop terminal amplification.

- 2026-11-12 user amendment: BACKGROUND-003 independently owns deterministic trusted recovery checkout footer across eligible AI reply formats before final controls/media/hash. Reuse existing recovery context; do not rely on model or mutable wrapper content. Nonrecovery/STOP/blocked/security paths remain excluded; no host/processor overlap.
