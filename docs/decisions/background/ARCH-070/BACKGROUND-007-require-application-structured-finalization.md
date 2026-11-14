---
id: ARCH-070-BACKGROUND-007
architecture_id: ARCH-070
title: Require application structured finalization using pinned response fields
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-11-14T09:18:12Z
attempt: 1
depends_on:
  - ARCH-070-BACKGROUND-006
enables: []
created: 2026-11-14
updated: 2026-11-14
---

# Require application structured finalization using pinned response fields

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; moda_architect.

## Objective

Make recovery application finalization guidance consistently request the existing finalResponse envelope and supported pinned selection fields without altering model outputs or semantic admission.

## Context

Diagnostic BG006 is integrated at Background be077bf7bd6b5e7f5a91fad1ee84c75dc76e13fa and parent6191af7439674d3edec1fa78d9b986144a3b9790. Genuine09:08:47 turn succeeded: ordinary step3 plain text required existing repair, then forcedstep4 supplied one detail selection; one composite was delivered. Original08:20 forcedstep4 omission remains unexplained. This corrects observed routine raw-text completion friction, not a proven original failure cause. Root causal audit found Shared runner/model/response/selection files byte-unchanged between5.13.10 release44356b4 and6.0.0 ade292b; Background host/product-discovery unchanged across composite adoption. Layout changes did not change those selection sources.

## Scope

Background-owned trusted host instructions and a small pinned-schema-aware format guidance helper if needed; focused actual-host request/unchanged-semantic tests and documentation of evidence limits.

## Out of Scope

Shared edits/releases; model/provider/schema changes; fabricated IDs or automatic selections; argument mutation; new retries or higher budgets; layout/media changes; live operations or main merges.

## Requirements

- Recovery trusted instructions require customer-facing completion through existing finalResponse, including simple answers/clarifications. Ordinary tool access and current forced-repair mechanism remain unchanged; do not force finalResponse at initial request.
- Derive any concrete field guidance only from the verified pinned response contract. Explain exact observed product/variant identities for supported nonempty detail/option/recommendation fields; never invent enum values or canonical fields absent from a custom contract.
- Preserve referral, language, nonproduct and custom contract behavior. Nonproduct completion must not invent products/evidence. Pinned schema validation and existing terminal missing-selection guard remain authoritative.
- No logs containing prose, identifiers or private contract contents beyond already approved bounded diagnostics.
- Root performs a bounded synthetic unforced actual-production-model baseline versus explicit-guidance comparison, without customer input or WhatsApp sends. Record actual outcomes before claiming measured benefit. Unit guidance assertions alone do not prove model efficacy; original forced omission remains unknown.
- No infrastructure, database or observability capability changes are needed.

## Work Items

- [ ] Add bounded application finalization guidance through existing trusted instruction assembly.
- [ ] Add pinned-contract-aware field guidance where supported without copying validators.
- [ ] Prove host/tool/semantic constraints unchanged through focused tests.
- [ ] Record exact source, isolation and validation plus measured/unknown evidence distinction.

## Interfaces / Contracts

Consume published Shared6.0.0 runner/verified response contracts as-is. Background owns recovery format policy; Shared generic plain-text allowance remains unchanged. Existing finalResponse and selection schemas remain canonical.

## Dependencies

ARCH-070-BACKGROUND-006 Complete, accepted and integrated.

## Enables

None; root-owned deployment and genuine verification follow accepted integration.

## Acceptance Criteria

- [ ] Actual host request includes specific recovery structured-finalization guidance while ordinary tools remain available.
- [ ] Supported canonical selection fields receive accurate guidance; custom unsupported fields/enums are not invented.
- [ ] Referral/nonproduct/language envelopes and model args remain unchanged by host processing.
- [ ] Missing/invalid selections still fail closed with existing single repair and budgets.
- [ ] Root comparison evidence is recorded honestly; no assertion of original forced-step failure cause.

## Validation

- [ ] Inspect declared package scripts and run focused instruction/helper tests plus declared commerce-host suite.
- [ ] Typecheck, production build, scoped lint and diff hygiene.
- [ ] Exact-head configured remote CI passes; disclose known unchanged lint baseline with evidence.
- [ ] Record root-owned bounded provider comparison outcome; no agent live calls.

## Stop Condition

After required work/checks, publish implementation and mirrored parent report, set review and STOP. Root owns all merges/live actions.

## Implementation Notes

Use normal moda-task launcher from primary root, dedicated sibling parent/implementation worktrees and preparation packet. You are not alone; preserve all other edits. Existing Background owner may inspect prior diagnostics but must use this task's worktrees. Prefer concise trusted instructions over a new adapter or policy framework. Root probe may run alongside implementation after exact proposed instruction is available; no efficacy claim ahead of result.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Pending

### Deviations

None

### Assumptions

None

### Unresolved Issues

Original forced-step omission remains unknown.

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

Review actual source and measured guidance outcome independently; diagnostic success alone does not close incident.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

Root deployment/genuine verification after acceptance and integration.
