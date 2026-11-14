---
id: ARCH-070-BACKGROUND-011
architecture_id: ARCH-070
title: Send trusted basket fallback after eligible AI failure
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-070-BACKGROUND-010
enables: []
created: 2026-11-14
updated: 2026-11-14
---

# Send trusted basket fallback after eligible AI failure

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; moda_architect.

## Objective

Admit one deterministic saved-template basket reply after an eligible AI completion failure through the existing guarded delivery lifecycle.

## Context

User explicitly requests honest unable-to-answer wording, abandoned basket summary and existing shop/checkout template instead of silent AI technical failure. BG010 selection work remains separate and must be preserved. This fallback does not fix the failed AI selection or guarantee Meta delivery.

## Scope

Application-owned failure classification, trusted localized fallback body from current abandoned basket snapshot, existing saved common reference/rendering and outbound lifecycle admission; focused host/processor and real disposable lifecycle proof. Exact implementation seam must be confirmed from current source before execution.

## Out of Scope

LLM retries/new model calls, fabricated selections/product claims, human prose summaries, Shared changes/releases, model/provider/configuration changes, sending without consent/window/controls, manual outbound/DB flags, template activation/provider registration, main merges/live operations.

## Requirements

Use only authoritative current recovery/basket facts already available to the processor; do not reuse unverified AI prose/history/product observations as basket authority. State inability honestly in existing resolved locale, list complete basket item names/quantities and only trusted available money fields, preserve currency and avoid current stock/price/discount promises. Saved common template is sole shop/header/footer source, checkout exactly once in its canonical footer. Do not synthesize product-detail selections or label the fallback verified AI success.

Classify explicitly eligible model/provider AI completion failures (including invalid final/selection, output exhaustion and model unavailable) at the owning boundary. NEVER catch stale inbound, cancellation, lost lease, human takeover, optout, consent/window/cap/entitlement/authorization failure or unsafe/missing basket/common/checkout proof into a send. A model deadline may use fallback only if a fresh existing bounded delivery admission budget remains and current ownership is valid; never ignore aborted signal/deadline or extend a protected permit. Meta send failures are NOT AI fallback triggers; preserve existing retry/UNKNOWN/no-resend semantics.

Route through existing idempotent outbound/application identity, current common-template final fence, conversation/control rechecks, permit/usage/billing lifecycle and provider adapter. One admitted response per inbound, no double-send if AI admission or provider outcome is uncertain. STOP and checkout mandatory content never lost. If full basket body cannot fit branded caption safely, use existing canonical full TEXT fallback rather than truncate facts/footer; no guarantee of single image bubble for oversized basket. Missing trusted basket/source fails closed with explicit internal outcome, no invented details. Preserve original AI failure diagnostics and separate fallback outcome without raw customer/secrets in logs; reuse shared logging, no competing logger.

Before source execution, architect must reconcile read-only seam findings into this task; task remains Pending and unclaimed. Final source bases/syncs accepted BG010 and preserves its guards. No infrastructure/DB change expected; return concrete gaps instead of expanding.

## Work Items

- [ ] Confirm exact failure classification/composition/admission seams with architect.
- [ ] Add trusted localized basket fallback and guarded failure integration.
- [ ] Prove no duplicate/unsafe send and preserved provider retry/usage behavior.
- [ ] Return immutable source/report.

## Interfaces / Contracts

Existing Background recovery/common-layout/outbound contracts and published Shared machinery only. No new queue/database schema or generic runner policy.

## Dependencies

ARCH-070-BACKGROUND-010; architect seam review before Ready.

## Enables

Root-owned deployment and genuine failure fallback verification after all current delivery/Meta gates permit.

## Acceptance Criteria

- [ ] Eligible AI failure produces honest saved-common basket body and canonical checkout footer.
- [ ] Trusted facts only; missing/oversized inputs handled without fabricated claims/truncation.
- [ ] Control/consent/window/stale/authorization/cancel exclusions remain fail closed.
- [ ] Existing idempotency/permit/usage/UNKNOWN/retry behavior preserved.
- [ ] Original AI failure and distinct fallback outcome remain observable without sensitive data.

## Validation

- [ ] Focused classification/localization/body/footer/basket trust tests.
- [ ] Actual processor failure path and negatives for controls/stale/cancel/window/unsafe context.
- [ ] Disposable PG lifecycle: one fallback/usage; duplicate inbound, UNKNOWN no resend, missing common and revoked authority no send.
- [ ] Declared types/build/scoped lint and exact remote checks.

## Stop Condition

After defined checks, set Review, complete report and STOP. No actual provider/model/customer sends or main merges.

## Implementation Notes

Normal launcher dedicated mirrored sibling worktrees only when Ready. Not alone; preserve all other source/local work. Existing specialist read-only assessment supplies exact seam before execution.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

Current recovery basket and normal delivery machinery available; verify before Ready.

### Unresolved Issues

Exact failure/admission seam review and BG010 dependency pending.

### Architectural Concerns

No fallback may bypass control or provider uncertain-outcome fencing.

## Architect Review

### Review Status

Pending

### Review Notes

Materialized definition only; read-only seam assessment pending.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Background-owned fallback through existing guarded delivery; no Shared business policy.

### Follow-up

Reconcile exact seams and dependency before Ready.

