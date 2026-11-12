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
| ARCH-070-SHARED-001 | moda_shared | Complete | None |
| ARCH-070-SHARED-002 | moda_shared | Complete | ARCH-070-SHARED-001 |
| ARCH-070-BACKGROUND-001 | moda_background | Complete | ARCH-070-SHARED-002 |
| ARCH-070-BACKGROUND-002 | moda_background | Complete | None |
| ARCH-070-BACKGROUND-003 | moda_background | Complete | None |

## System Validation

No separate terminal system-test task is currently necessary for this bounded correction: deterministic host fixtures, lifecycle/repeated-repair and relevant PostgreSQL tests plus developer-owned production observation cover the affected paths. Reassess if cross-service/schema changes become required. Architecture remains In Progress until production verification is recorded.

## Open Questions

Exact valid refreshed product evidence mismatch and exact existing durable terminal representation must be established by owning investigators.

## Change History

- 2026-11-12: Split recommendation evidence and terminal retry amplification into disjoint independently reviewable Background tasks.

- 2026-11-12 dependency amendment: valid ACTIVE available catalogue products have null onlineStoreUrl; MCP permits this but Shared schema/render and Background refresh reject it. Shared5.13.3 adds nullable URL only PRODUCT_ONLY with link omission; mutations/non-null URL checks unchanged. Shared acceptance -> exact publication -> Background exact-version adoption. Retry task ships independently to stop terminal amplification.

- 2026-11-12 user amendment: BACKGROUND-003 independently owns deterministic trusted recovery checkout footer across eligible AI reply formats before final controls/media/hash. Reuse existing recovery context; do not rely on model or mutable wrapper content. Nonrecovery/STOP/blocked/security paths remain excluded; no host/processor overlap.

## Accepted Releases and Production Retry Verification

Shared001 Accepted/Complete implementation bf642ea, developer merged `72203015aa7daec41ed4aa76d13c11d7309b10a4`. Shared002 Accepted/Complete: canonical public5.13.3 metadata and506885 tarball bytes independently downloaded with SHA256 `34b17b2fd6fd4ec2dc9043ee8d2e6cd5d77c804b3b9c58b0f91f1d25f3175b5e`. Background001 resumed attempt2 on current main after publication. Shared validation719 pass/3 expected skips and focused26, types/build/installed exports passed.

Background002 Accepted/Complete at45170903 with130 focused tests, both fullCI3,951 tests and5 disposable PostgreSQL/Redis repair scenarios. Root/developer merged `1afff14201c3f55a7f6745686e16abf3090499da` and observed production deployment `dep-dbqrj20473hc738ctce0` Live. At13:07:24.906Z, worker logged terminal_failure for conversation `cmwcxdt0o0009kp164raxldna`, inboundVersion5, INVALID_FINAL. Repair passes13:07:43/13:08:13/13:08:43 all scanned0/requeued0; the older instance also observed zero after durable closure. Read-only production state at13:09:29.665Z confirmed inboundVersion5 equals lastProcessedVersion5, pending/processing fields null, AI control revision0. No manual DB/queue writes or input replay were performed. These correlated observations verify terminal retry suppression, not recommendation/footer correctness, which remain pending.

Footer clarification: canonicalize standalone exact raw trusted checkout URLs; preserve embedded Markdown/prose and append the required footer. This is eligible AI recovery composition only, excluding human/manual and STOP/consent/security/blocked paths. Existing prepared delivery replay remains immutable. Architecture remains In Progress pending both remaining task acceptances, final integration and fresh production recommendation/footer proof.

- Background003 Accepted/Complete b3b86c6: eligible AI recovery footer validated75 focused/2 disposable PostgreSQL tests, types/scoped lint and both exact-head full CI. Developer merge, combined recommendation integration and genuine production footer proof remain pending.

- Background001 Accepted/Complete Attempt2 at91f880e, with merged retry/footer ancestors. Exact public5.13.3 artifact, host90/focused57/typecheck/scoped lint and both combined CI pass. All five tasks now Accepted/Complete. Developer final merges/gitlinks and genuine production recommendation/footer verification remain pending; architecture is not yet Implemented.

## Final Runtime Integration and Rollout

Developer merged Shared PR77 at `72203015aa7daec41ed4aa76d13c11d7309b10a4`, Background retry PR200 at `1afff14201c3f55a7f6745686e16abf3090499da`, footer PR201 at `04317ce74b79192d0ce909de5edc0d1265e47b5c`, and combined recommendation PR202 at `244304adea723bcc18854e4f1bffcc25571d3346`. Parent gitlinks were reconciled to final Shared/Background merges in `35f20728f80ad7161b1a849d8e6cebd4ac999bc3`; unrelated primary-workspace changes were excluded.

Root/developer observed final production messaging worker deployment `dep-dbqrunrrjlhs738a5to0` Live on Background244304ad. Current instance started at13:32:24.712Z; prior footer-only instance terminated at13:34:15Z. Current-instance repair passes13:34:24/54 and13:35:24/54 all scanned0/requeued0. These observations establish final code rollout and continued absence of terminal retry amplification. A fresh genuine WhatsApp recommendation question, verified product response, trusted checkout footer and Meta/durable delivery remain pending. Architecture therefore remains In Progress.

## Fresh Production Validation — Incomplete

A genuine new inboundVersion6 at13:38:29Z (`cmwdlfp570001rf16ifuk2wcq`) asked “what other things do you sell”. On final deployed244304ad, two product searches succeeded and the third model step returned ANSWER. At13:38:49.622Z, composition recorded valid selection syntax but no product proposals (`MODEL_SELECTED_NO_RECOMMENDATIONS`, refresh plan0), then refused `MISSING_VERIFIED_PRODUCT_SELECTION`. Typed INVALID_FINAL was durably completed as terminal at13:38:49.710Z; subsequent repair passes remained zero.

This does not validate the null-URL gate or successful recommendation/footer delivery: no products reached refresh because the model omitted structured selections. Existing accepted null-URL, footer and terminal-retry changes remain independently tested. Root is inspecting the actual final response/runner contract read-only before defining another bounded correction; no product selection may be invented or tenant/evidence checks bypassed. Architecture stays In Progress and parent PR985 remains draft. Final customer-facing recommendation/footer success is not claimed.

## Semantic Selection Contract Amendment

Provider-free proofs establish two independently reproducible gaps: schema-valid nonempty productRecommendations without matching version is considered selected by runner but dropped by host; truthy null/null shipping without meaningful disposition similarly bypasses repair and is discarded. Historical exact production version6 final shape remains unconfirmed. Shared003 owns one canonical normalization/eligibility implementation and aligns the existing bounded runner repair, Shared004 publishes accepted5.13.4, Background004 adopts that helper and bounded shape-only diagnostics. No guessed IDs/version, automatic product choice or extra queue/model retry loop is authorized. Existing accepted tasks remain Complete; architecture remains In Progress.

| Task | Owner | Status | Dependencies |
|---|---|---|---|
| ARCH-070-SHARED-003 | moda_shared | Ready | ARCH-070-SHARED-002 |
| ARCH-070-SHARED-004 | moda_shared | Pending | ARCH-070-SHARED-003 |
| ARCH-070-BACKGROUND-004 | moda_background | Pending | ARCH-070-SHARED-004 |
