---
id: ARCH-007-SYSTEM-TEST-005
architecture_id: ARCH-007
title: Validate fragmented WhatsApp coalescing, inbound abuse admission and conversation safety
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
status: pending
priority: 121
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-007-BACKGROUND-010
  - ARCH-007-BACKGROUND-004
  - ARCH-007-BACKGROUND-011
enables: []
created: 2026-09-08
updated: 2026-09-08
---

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

# ARCH-007-SYSTEM-TEST-005: Validate coalescing, inbound abuse admission and conversation safety

Terminal/manual-gated integrated validation only.

Validate with real queue/database behavior:
- 3 fragmented inbound messages in the 3s window persist as 3 messages but produce 1 agent turn/reply;
- >3s separation produces separate turns;
- 10s maximum settling bound;
- no concurrent agent processing for one conversation;
- different conversations remain concurrent;
- stale response suppressed if a correction arrives while agent runs;
- outbound cap is reserved before agent;
- cap exhaustion prevents LLM/tool invocation;
- terminal response remains at most once;
- standalone product/support conversation and recovery conversation both obey coalescing;
- raw per-sender abuse limit suppresses excess signed inbound events before tenant/DB routing;
- raw global abuse limit suppresses a distributed multi-sender flood;
- settled-turn sender/conversation/shop/global limits suppress AI/provider work without deleting already persisted fragments;
- PRODUCT_DISCOVERY without reply context receives the stricter settled-turn limits;
- denied settled turns advance/clear their version/lease state and do not retry forever;
- abuse denial creates no inbound merchant billing metric, no `OUTBOUND_AUTOMATED_MESSAGE`, no CommerceAgent call and no provider send;
- rate-limit admission is concurrency-safe at the final slot and replay-idempotent;
- a new turn after window expiry can process normally.

Do not run until implementation dependencies are Complete and developer manually elects system validation.

## Luna execution rules

- Treat this file as the complete execution contract. Do not redesign the feature.
- Do not broaden scope into adjacent billing/conversation work.
- Before editing, inspect the exact named current files and repository `package.json`.
- Use only repository scripts that actually exist.
- Do not modify another repository unless this task explicitly authorises a dependency pointer/version update.
- Do not start a task listed under `enables`.
- Return only this task to `review` and STOP.
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-SYSTEM-TEST-005` branch and the mirrored parent-workspace `task/ARCH-007-SYSTEM-TEST-005` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.

## Completion Report

### Status
Pending

### Files Changed
None.

### Work Completed
None.

### Validation Results
Not run.

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

### Review Notes
None.

### Reviewed Files
None.

### Validation Reviewed
None.

### Architecture Conformance
Pending

### Follow-up
None.

