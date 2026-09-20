# ARCH-019 implementation handoff

Canonical architecture: [ARCH-019](ARCH-019-merchant-recovery-experience.md).

Current frontier: DATABASE-001, SHOPIFY-001 and SHOPIFY-003 accepted/Complete at Attempt 1; SHOPIFY-002 accepted/Complete at Attempt 3; SHOPIFY-004 accepted/Complete at Attempt 2 (`ffb7b86`). SHOPIFY-005 Ready after Attempt 1 Changes Requested: legacy explicit unavailable billing periods must not silently fall back (`d5319e8` not accepted); SHOPIFY-006 and SYSTEM-TEST-001 Pending. Architecture remains In Progress; system validation is terminal and developer-invoked. Accepted dependency records are reconciled into SHOPIFY-005; readiness does not launch implementation or authorize unmerged dependency consumption.

SHOPIFY-001 accepted implementation: `08af00b85508d3ae7e653890abbc8a5ca0c0cc9d`; reviewed report: `181e3a91b3cfc10e099b913db6d2e5fbb6f5dcfb`. DATABASE-001 accepted `54c0ec2` is integrated in database `9c6a4d8` with an identical tree. The complete experience still requires all remaining tasks and terminal validation. The developer explicitly delegated commit/push of these review updates on 2026-09-20.

Dependency sequence:

```text
DATABASE-001 -> SHOPIFY-001 -> SHOPIFY-003 --+
            -> SHOPIFY-002 ---------------+-> SHOPIFY-004
SHOPIFY-001 + SHOPIFY-003 + SHOPIFY-004 -> SHOPIFY-005 -> SHOPIFY-006
DATABASE-001 + SHOPIFY-001..006 -> SYSTEM-TEST-001 (manual invocation)
```

The complete architecture/task/index packet is present on each parent task branch at definition time so every task is self-contained before main integration. Copies describe the initial frontier only. Each task's matching canonical parent worktree is its authoritative execution/review state. Before promoting a downstream task, the architect must inspect that authoritative accepted record and reconcile the dependency task metadata and shared frontier into the downstream parent branch, using the developer-owned publication path for review overlays. The prepared launcher gates dependencies from the downstream parent branch itself. Stale initial copies must never be treated as accepted or left behind when promoting a task. Developer main integration followed by normal task synchronization is also a valid way to obtain current accepted records.

Materialisation creates only parent task worktrees/branches. Execution creates the implementation worktree through the normal launcher. No main merge, implementation worktree, claim, deployment or live test is authorized merely by this handoff.

All new task branches start from current origin/main. Developer integrates accepted implementation dependencies before downstream execution or explicitly authorizes the appropriate accepted dependency commit consumption. Additive database migration precedes the final app release; app deploy follows SHOPIFY-006 acceptance. Retain existing billing URLs and legacy detail redirects. System testing is terminal, after developer manual exercise, and cannot gate unfinished implementation.

Historical baseline documents: ARCH-013 routing and accepted ARCH-017 onboarding/current-period behaviour. ARCH-019 changes navigation/read presentation only; keep the current source lifecycle policy. Do not edit unrelated pending-recovery or recovery-settings work present in shared checkouts.

## SHOPIFY-002 final acceptance

Accepted `1a60f1e` (Attempt 3), with all five PostgreSQL tests and four bounded index plans at tested `eb34340`; production readers unchanged. Correction PR #40 and accepted SHOPIFY-003 implementation must follow developer integration/approved consumption rules before SHOPIFY-004 execution. Report PR #159 contains the acceptance record.
