---
id: ARCH-053-SHARED-002
architecture_id: ARCH-053
title: Publish accepted Woo restoration contracts
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-053-SHARED-001
enables:
- ARCH-053-API-001
- ARCH-053-API-002
- ARCH-053-BACKGROUND-001
created: 2026-10-29
updated: 2026-10-30
---

# ARCH-053-SHARED-002 — Publish accepted Woo restoration contracts

## Architecture

Architecture ID: `ARCH-053`. Document: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Coordinator: `moda_architect`. **Portable canonical task: defined but not materialised**; no Git branch, worktree, commit, push, review or producer deployment claimed.

## Objective

Publish accepted Woo restoration contracts. One bounded outcome in `moda-interact-shared` owned by `moda_shared`.

## Context

The inspected snapshot is dated 2026-10-30 07:59. ARCH-052 owns dynamic discount discovery and is not a checkout-URL implementation domain. ARCH-048-BACKGROUND-007..011 task files are present, but none has been accepted Complete in this snapshot (007 Ready, 008–011 Pending). This task is **Pending** from the snapshot/dependency inventory, subject to fresh launcher re-gating.

## Scope

- Limit changed files to authorised release metadata and lockfile updates mechanically required by publication.

## Out of Scope

No new source changes, revalidation tests or API/Background integration.

No execution of Enabled tasks, unrelated cross-repository implementation, extra database objects or new generic logger.

## Requirements

- Publication-only work: do not rerun tests, lint, build or alter runtime implementation already validated in SHARED-001. If publishing reveals a code defect, stop and return it to architect.

### Mandatory workflow/security invariants

- Inspect `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/developer-task-workflow.md`, `docs/task-definition-materialization.md` and the launcher preparation evidence. Use the **dedicated, synchronized parent and implementation task worktrees**; do not operate from a shared checkout or claim a branch was pushed without evidence. Implement only the owning repository and assigned task metadata. No unrelated refactors, migrations, agent handoffs or remote pushes to `main`.
- Read the ARCH-053 parent architecture and all dependency tasks before claiming Ready. Any missing contract or incorrect owner is a blocking architect question; do not invent a local parallel schema or silently change another agent's task. System-test tasks must remain terminal.
- Never swallow unexpected errors: Node uses `@modainteract/moda-interact-shared/logging`; PHP uses the existing safe plugin diagnostics (not a competing generic Node logger). Report bounded event codes, ids and outcomes, propagate retryable failures to their owning boundary, omit tokens, full URLs, coupon codes and customer personal data from logs.
- The plugin cannot access PostgreSQL/Redis. The API cannot mutate merchant WordPress cart sessions. Background cannot directly call an unverified merchant endpoint to mint URLs. Do not enable Woo production WhatsApp sending, relax final consent/STOP/order gates, or add cross-generation outreach caps/cooldowns.

## Work Items

- [x] Apply approved package version and publish using existing release workflow.
- [x] Verify the exact published version exposes **the single offer-aware v1** types/schemas and fixture paths; record registry evidence.

## Interfaces / Contracts

The one browser-safe published `@modainteract/moda-interact-shared/woocommerce` subpath exposes the complete offer-aware `WooRestoreResolveRequestV1Schema`, `WooRestoreResolveResponseV1Schema`, `WooRestoreOutreachOfferV1Schema`, snapshot/extension schemas and the single `woo-restore-v1.json` fixture package export defined in SHARED-001. Publication may change only release metadata; the exported source and fixtures were already validated at implementation acceptance.

## Dependencies

- `ARCH-053-SHARED-001` — accepted complete v1 snapshot and offer-aware resolver contracts.

## Enables

- `ARCH-053-BACKGROUND-001`
- `ARCH-053-API-001`
- `ARCH-053-API-002`


## Acceptance Criteria

- [x] Apply approved package version and publish using existing release workflow.
- [x] Verify the exact published version exposes **the single offer-aware v1** types/schemas and fixture paths; record registry evidence.
- [x] No regression in tenant isolation, historical generation preservation, valid shopper cart or consent/STOP/terminal order guards.
- [x] No change outside assigned domain repository code plus owned task Completion Report; no ARCH-052 work.

## Validation

- [x] Registry visibility and unchanged release-specific code check; `git diff --check`

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are complete, update ONLY this task's authorised execution metadata, checklists and Completion Report, set `status: review` and return to `moda_architect`; **STOP**. Do not begin Enables, merge task branches, push `main` or change Architect Review yourself.

## Implementation Notes

This is a `task_kind: publication` gate for **one** accepted Shared implementation (SHARED-001). It must not rerun its tests, lint, typecheck or build. Consumers may only pin/import a registry-visible package version containing the single offer-aware v1 and the one canonical JSON fixture. If a missing export needs code changes, STOP and return to architect; do not fix source in this publication task. Architect reviews publication evidence only. No consumer is permitted to use unpublished sibling code.

## Completion Report

### Status

Not Started

### Files Changed

None — portable task definition only.

### Work Completed

kwadwoadomafriyie@kwadwos-iMac moda-interact-shared % npm view @modainteract/moda-interact-shared@2.7.2

@modainteract/moda-interact-shared@2.7.2 | Proprietary | deps: 24 | versions: 53
Shared TypeScript contracts and reusable platform primitives used by multiple Moda Interact services.

dist
.tarball: https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-2.7.2.tgz
.shasum: f4115d4ce89cab7a45d535ad8d6d1808862cb9b8
.integrity: sha512-quqPSi/dIB3WbfYsYOO4tt12CVRboA8OPDi/obsAQhrMTaHcgYzMpbRoBRIxmehpbGDOOAjdL3j4xBRNTsyU+Q==
.unpackedSize: 1.2 MB

dependencies:
zod: ^4.0.0, semver: 7.8.5, winston: 3.19.0, bullmq-otel: ^2.0.1, winston-loki: 6.1.7, @langchain/core: 1.2.13, libphonenumber-js: 1.12.30, @opentelemetry/api: ^1.9.0, intl-messageformat: ^10.7.18, @langchain/langgraph: 1.4.15, @langchain/openrouter: 0.4.15, @opentelemetry/api-logs: 0.221.0, @opentelemetry/sdk-logs: 0.221.0, @opentelemetry/sdk-node: 0.221.0, @prisma/instrumentation: ^6.19.3, @opentelemetry/resources: ^2.10.0, @opentelemetry/sdk-metrics: ^2.10.0, @opentelemetry/sdk-trace-base: ^2.10.0, @opentelemetry/context-async-hooks: ^2.10.0, @opentelemetry/instrumentation-http: 0.221.0, @opentelemetry/instrumentation-undici: 0.31.0, @opentelemetry/exporter-logs-otlp-http: 0.221.0, @opentelemetry/exporter-trace-otlp-http: 0.221.0, @opentelemetry/exporter-metrics-otlp-http: 0.221.0

maintainers:
- kwadwoafriyie <kodjo_baah@hotmail.com>

dist-tags:
latest: 2.7.2

published 5 minutes ago by kwadwoafriyie <kodjo_baah@hotmail.com>
kwadwoadomafriyie@kwadwos-iMac moda-interact-shared %

### Validation Results

Not Run — no implementation claimed.

### Deviations

None.

### Assumptions

Design reconciled against uploaded 2026-10-30 07:59 source snapshot; re-check source and prior task acceptance before implementation.

### Unresolved Issues

None asserted as executed; dependencies must be materialised/accepted.

### Architectural Concerns

Return any cross-service schema/provider/transaction concern to `moda_architect` before improvising.

## Architect Review

### Review Status

Pending

### Review Notes

Not Reviewed — task not executed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

To be assessed after implementation.

### Follow-up

None.
