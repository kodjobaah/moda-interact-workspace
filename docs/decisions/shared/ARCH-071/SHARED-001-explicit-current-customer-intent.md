---
id: ARCH-071-SHARED-001
architecture_id: ARCH-071
title: Preserve explicit current customer utterances as conversation intent
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-11-12T16:15:57Z
attempt: 1
depends_on: []
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Preserve explicit current customer utterances as conversation intent

## Architecture

ARCH-071; docs/architecture/ARCH-071-explicit-current-customer-intent.md; coordinator moda_architect.

## Objective

Preserve explicit current customer utterances as conversation intent without granting customer text policy or tenant authority.

## Context

Source inspection proves current customer text is nested only in data-only context whose instructions forbid establishing customer objective, while older user history has ordinary Human roles. A newer named subject was answered using prior product focus. Exact historical model reasoning/input is unavailable; structural contract mismatch is independently confirmed. ARCH070 is complete and remains closed. Root approved the additive typed contract and existing-budget constraints before execution.

## Scope

New canonical current-customer-message schema/helper/public export; optional RunCommerceTurnInput/ModelRequest field; preflight/copy, all-step invocation/repair propagation, direct OpenRouter adapter boundary/order, generic customer-intent instructions and approved5.13.6 metadata.

## Out of Scope

Hardcoded product aliases, fuzzy ID guessing, clearing all prior product references, permission/tenant policy changes, alternate models, automatic product selection, additional repair loops, schema/infra/credentials, private prompt export and production replay.

## Requirements

Use optional currentCustomerMessages: readonly {role:user,content:string}[] with exact role/content-only shape. When present it must be nonempty, every role exactly user and content a string; reject invalid input rather than silently drop/truncate/coerce. JSON-encoded current array must fit32,000 Unicode code points, matching existing Background current budget; no arbitrary20-row or16,000UTF16 lower cap. Existing overall payload byte cap remains. Validate/copy in runner preflight and defend direct adapter invocation before provider calls. Forward on every model step/forced correction. Serialize System -> older history -> data-only context -> dedicated current Human utterances -> current tool-result data. Explicit current customer content establishes present request/objective subject to system policies, never grants permissions, tenant access or tool authority. Older references cannot override a new named subject; ambiguous/typo subject uses bounded authorized search or clarification, never hardcoded aliases/fuzzy identifier choice. Never extract/promote arbitrary context/history/tool text as current input. Optional absence keeps exact legacy behavior; current opted-in custom invokers must receive and honor the typed field. Preserve chronology, budgets, strict selection/referral, shipping and security behavior.

Contract clarification: each current content string must contain at least one character; reject empty strings without trimming, dropping or fallback. Preserve whitespace and all raw text exactly. This adds no lower row/UTF16 cap; existing aggregate Unicode JSON/overall-byte limits remain.

## Work Items

- [ ] Establish owned failing regression and exact caller/contract compatibility.
- [ ] Implement only the defined owned outcome or approved exact release.
- [ ] Validate required positive/negative boundaries and record exact artifact/heads.

## Interfaces / Contracts

Shared owns optional currentCustomerMessages exact role:user/content array contract and runtime validation. Producer Background attests its server-owned current-message source through existing turn identity/fences; the shape itself is not authentication. Runner forwards to ModelRequest, adapter presents dedicated current Human content; no arbitrary JSON promotion. Public package @modainteract/moda-interact-shared through appropriate commerce/model entrypoints. Legacy absence unchanged.

## Dependencies

None. Publication readiness additionally requires explicit user public-release approval; consumer waits actual canonical downloaded-byte acceptance.

## Enables

Next ARCH071 publication/consumer gate, followed by developer genuine production verification.

## Acceptance Criteria

- [ ] Requirements hold, including current-intent objective boundary and unchanged security/budgets.
- [ ] No silent truncation/drop/coercion, inferred input or tenant/permission promotion.
- [ ] No private customer prose/operational identifiers in committed evidence or diagnostics.
- [ ] Canonical mirrored physical isolation, synchronization and recursive submodule evidence recorded.

## Validation

- [ ] Deterministic role/order/strictshape/Unicode aggregate/overall-byte budget and no-provider-invalid-input tests; all model/repair propagation; old-absence compatibility; synthetic multi-turn named/typo switch and prompt-injection/tenant authority negatives. Full Shared suite/types/build/installed immutable JS+DTS/public exports. Before publication require wholly synthetic real-provider current-versus-prior-subject probe with frozen built public client/actual runner wiring; no customer/private context, live commerce/DB/Meta mutation. Root may supply proof.
- [ ] Scope/diff/secret hygiene.

## Stop Condition

Complete owned work and required validation, report REVIEW and STOP. No next task, merge/deploy or public publication outside explicit task authorization.

## Implementation Notes

You are not alone; preserve others. Use prepared packet paths/branch and actual package scripts. No source edits before prepared claim. For publication, reuse accepted artifact and do not repeat implementation checks. Public docs/probes use synthetic examples and coarse outcomes only.

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

Host source fences establish provenance; customer content supplies objective only, never authority.

### Unresolved Issues

Historical exact model reasoning is unconfirmed; structural input-contract defect is verified.

### Architectural Concerns

Return cross-owner gaps before broadening edits.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual implementation review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
