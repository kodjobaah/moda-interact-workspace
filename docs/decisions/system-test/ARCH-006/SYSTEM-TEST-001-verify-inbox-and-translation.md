---
id: ARCH-006-SYSTEM-TEST-001
architecture_id: ARCH-006
title: Verify merchant/Admin inbox, ownership, language routing and read semantics
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
status: pending
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-006-ADMIN-004
  - ARCH-006-SHOPIFY-003
  - ARCH-006-GATEWAY-001
enables: []
created: 2026-09-05
updated: 2026-09-06
---

# ARCH-006-SYSTEM-TEST-001: Verify merchant/Admin inbox, ownership, language routing and read semantics

## Architecture

`docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

## Objective

Verify the integrated user-facing support inbox and authorization/language semantics after implementation and deployment are manually accepted.

## Context

This system test does not own resilience edge cases of Redis/Batch recovery; those are isolated in SYSTEM-TEST-003.

## Scope

Architecture-level test fixtures/scenarios for Admin/merchant inbox, ownership, 500-grapheme input, English/no-translation and non-English translation display/read behavior.

## Out of Scope

- Implementation fixes.
- Paid/provider load testing.
- Subscription-ended system trigger (SYSTEM-TEST-002).
- Deep queue recovery matrix (SYSTEM-TEST-003).

## Requirements

Cover at least:
- all authorised shop staff share one thread; cross-shop access denied;
- all active Admins may read; only durable owner sends;
- atomic take ownership and assignment persists across session/process boundary represented by test topology;
- merchant message sets pending/version; reading does not clear pending;
- admin response boundary clears only when no newer merchant message;
- 501st grapheme rejected without truncation;
- English merchant/admin directions create no translation work;
- non-English merchant original immediately visible to Admin while translation may be pending;
- non-English outbound hidden until exact display translation AVAILABLE;
- View original/readAt semantics and source immutability.

## Work Items

- [ ] Reuse/create bounded shop/admin/language fixtures.
- [ ] Add authorization/ownership/pending/read scenarios.
- [ ] Add grapheme-limit scenario including emoji/combined grapheme.
- [ ] Add English bypass and non-English translation scenarios using architecture-approved fake/test provider path.
- [ ] Record integrated evidence/results in task Completion Report.

## Interfaces / Contracts

Use deployed/test interfaces; do not reach into repository internals unless the system-test architecture already provides fixtures/seed helpers.

## Dependencies

Explicit task dependencies are listed in YAML frontmatter.

## Enables

None

## Acceptance Criteria

- [ ] Tenant/admin ownership boundaries pass.
- [ ] 500-grapheme contract passes end-to-end.
- [ ] English bypass produces no unnecessary translation.
- [ ] Non-English inbound/outbound availability semantics pass.
- [ ] Pending/read/response-boundary semantics pass.
- [ ] Original content remains immutable/viewable.

## Validation

Run the task's architecture test scenarios using existing system-test commands/topology. Record any opt-in/provider prerequisites explicitly.

## Implementation Notes

System-test tasks become executable only after implementation tasks are accepted and the developer has had the opportunity to validate deployment manually.

## Completion Report

### Status

Not started.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

None yet.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending
