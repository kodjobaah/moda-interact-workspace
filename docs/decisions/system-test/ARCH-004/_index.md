# ARCH-004 — System Test Tasks

Architecture:

```text
docs/architecture/ARCH-004-cart-activity-recovery-rescheduling.md
```

| Task | Description | Status | Dependencies |
|---|---|---|---|
| SYSTEM-TEST-001 | Verify cart activity resets recovery inactivity clock | **Ready** | SHARED-002, SHOPIFY-001, BACKGROUND-002, SHOPIFY-002 |
> **State synchronization — 2026-09-08:** The task table above is regenerated from the individual task YAML frontmatter. Those task files remain authoritative. Historical narrative below may describe earlier frontiers.
All implementation dependencies are architect-accepted.

`SYSTEM-TEST-001` is Ready, but the developer may leave it Ready while manually
testing the completed feature before invoking the system-test agent.
