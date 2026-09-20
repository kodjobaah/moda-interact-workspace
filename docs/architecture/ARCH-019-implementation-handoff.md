# ARCH-019 implementation handoff

Canonical architecture: [ARCH-019](ARCH-019-merchant-recovery-experience.md).

Current frontier: DATABASE-001 and SHOPIFY-001 accepted/Complete. SHOPIFY-002 Ready for Attempt 3 corrections (Attempt 2 preserved); SHOPIFY-003 In Progress at Attempt 1. SHOPIFY-004/005/006 and SYSTEM-TEST-001 remain Pending. Accepted dependency metadata is reconciled into the newly Ready task worktree. The developer authorized publication of these review updates on the matching parent task branches on 2026-09-20. Readiness does not launch execution or authorize prerequisite integration.

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

## SHOPIFY-002 Attempt 2 review

Changes Requested: timezone correction passes, but the pg harness sends a psql-only fixture directive as SQL. Correct setup and supply all five PostgreSQL tests/plans before acceptance. Implementation PR #38 was merged early at `49526b5`; report PR #159 remains open. No automatic revert: the finding concerns test setup and these readers are not wired into routes. Future corrections require developer integration after review.

## Parent branch reconciliation — 2026-09-20

At the developer’s request, incorporated parent `origin/main` at `3ffc6a58ce0e3b88f0ca06aa511472f4db334a63` into `task/ARCH-019-SHOPIFY-002`. Resolved six documentation conflicts by retaining the reviewed Attempt 2 report and Changes Requested contract, SHOPIFY-001 acceptance, and SHOPIFY-003’s independently verified active Attempt 1. SHOPIFY-002 stays Ready with attempt 2 and no claim; the next prepared execution claims Attempt 3. This reconciliation does not launch implementation or change either main branch.
