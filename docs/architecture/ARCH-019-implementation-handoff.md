# ARCH-019 implementation handoff

Canonical architecture: [ARCH-019](ARCH-019-merchant-recovery-experience.md).

Eight agent-executed tasks; attempt 0; no executor/claim. Initial Ready frontier is **ARCH-019-DATABASE-001**. Start only that task with `/moda-task ARCH-019-DATABASE-001` when the developer chooses to begin.

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
