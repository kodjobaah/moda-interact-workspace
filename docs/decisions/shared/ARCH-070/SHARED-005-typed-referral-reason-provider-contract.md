---
id: ARCH-070-SHARED-005
architecture_id: ARCH-070
title: Make referral reason provider nullability and forced guidance explicit
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-070-SHARED-004
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Make referral reason provider nullability and forced guidance explicit

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; coordinator moda_architect.

## Objective

Make referral reason provider nullability and forced guidance explicit within existing strict final-envelope and bounded execution guarantees.

## Context

Fresh production version7 entered selection repair but failed final schema at referralReason invalid_value. Exact raw invalid value is unknown and must not be assumed. User explicitly authorized correcting referralReason, testing, commit/push/merge and fresh production recommendation/footer verification. All previous eight accepted tasks remain valid; architecture stays In Progress.

## Scope

Shared finalResponse provider JSON schema and common forced-finalization instructions; strict referralReason validation regressions, public export smoke and approved5.13.5 metadata.

## Out of Scope

Unknown-value normalization, schema weakening, missing-field dropping, extra repair/queue loops, automatic selections, provider/model switching, credentials, unrelated refactors, production replay and unsolicited Meta sends.

## Requirements

Explicitly represent nullable string type for provider referralReason JSON schema. Common forced guidance must distinguish ANSWER uses JSON null from REFER_TO_STORE uses an allowed pinned reason, preserving required-referral constraints. Keep exact strict runtime validator, mandatory fields and existing single correction/step/deadline/token budgets. Never normalize unknown strings, drop invalid fields, guess historical raw value or add another retry loop. If diagnostics are needed, emit only bounded ABSENT/NULL/recognized-enum/other-STRING/OTHER shape classification through existing shared logger; no raw value/private prose. Preserve previously accepted selection, shipping-evidence, chronology and security behavior.

## Work Items

- [ ] Establish owned source/release behavior and preserve relevant regression evidence.
- [ ] Complete only the bounded owned correction or exact artifact release.
- [ ] Record required validation, exact hashes/heads and return review.

## Interfaces / Contracts

Shared owns canonical finalResponse provider schema, validator and bounded runner. Background consumes published @modainteract/moda-interact-shared package and retains tenant/host/evidence/delivery policy. No new wire/schema version or mandatory-referral change authorized.

## Dependencies

ARCH-070-SHARED-004. Publication additionally requires developer implementation merge; consumer starts only after actual public artifact integrity acceptance.

## Enables

Next ARCH-070 publication/consumer gate, then root/developer fresh production verification.

## Acceptance Criteria

- [ ] Requirements and required validation pass without weakening strict validation or bounded execution.
- [ ] No private prompts/prose, raw invalid values, customer data or secrets in diagnostics/probes.
- [ ] No unrelated files or implementation-owner boundary violation.
- [ ] Launcher mirrored physical isolation, synchronization and recursive submodule evidence recorded.

## Validation

- [ ] Deterministic provider-schema/forced-guidance and strict final validation red-green tests including JSON null vs literal string, invalid reason, allowed referral and mandatory-referral behavior; full Shared suite, types/build/installed immutable JS+DTS/public exports. Before publication require a wholly synthetic real-provider conformance probe using current anonymous pinned schema and final actual public built client; synthetic products/history only, no customer/private prompts or Meta sends. Root may supply that proof; report its limits separately from production.
- [ ] Diff scope/hygiene and secret validation.

## Stop Condition

When owned work and required validation are complete, set review, report and STOP. No follow-on task, merge/deploy or publication outside explicit task scope.

## Implementation Notes

You are not alone; preserve others' changes. Use canonical prepared packet paths and matching mirrored branch. Read actual package scripts; do not rerun accepted implementation validation in publication. Existing shared structured logger only if diagnostics needed. Exact historical invalid referral value remains unconfirmed.

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

Historical exact raw invalid referralReason is unavailable.

### Unresolved Issues

None beyond owned correction/release.

### Architectural Concerns

Return cross-owner gaps before modifying outside scope.

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
