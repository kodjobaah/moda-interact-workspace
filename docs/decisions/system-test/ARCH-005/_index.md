# ARCH-005 — System Test Tasks

| Task | Description | Status | Dependencies |
|---|---|---|---|
| SYSTEM-TEST-001 | Verify multi-market context and proactive template selection | Pending / manual-gated | SHOPIFY-001, SHOPIFY-003, BACKGROUND-001, BACKGROUND-002, BACKGROUND-003, SHOPIFY-002, SHOPIFY-004, MESSAGING-003 |
| SYSTEM-TEST-002 | Verify multilingual conversation language behaviour | Pending / manual-gated | SYSTEM-TEST-001, BACKGROUND-004 |
> **State synchronization — 2026-09-08:** The task table above is regenerated from the individual task YAML frontmatter. Those task files remain authoritative. Historical narrative below may describe earlier frontiers.
System tests remain terminal. They must not become Ready until every listed
implementation dependency is Complete and architect-accepted.

## Manual invocation gate

These are terminal validation tasks. They do not block any implementation, publication, infrastructure or other non-system-test task. Even after dependencies are Complete, keep system-test execution dormant until the developer has manually reviewed the completed ARCH-005 implementation and explicitly authorises `moda_system_test`.
