# ARCH-038 System Test Tasks

Architecture: [ARCH-038-commerce-agent-execution-budget-policies](../../../architecture/ARCH-038-commerce-agent-execution-budget-policies.md).

Reconciled on 2026-11-02. Individual task frontmatter and review reports are authoritative. Superseded tasks must not be executed.
Ready means implementation prerequisites are complete; system certification still requires explicit manual launch and a recorded passing result.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-038-SYSTEM-TEST-001](SYSTEM-TEST-001-certify-live-budget-policy-inheritance.md) | Certify LIVE execution budget precedence and runtime | ready | `ARCH-038-DATABASE-001`, `ARCH-038-ADMIN-001`, `ARCH-038-ADMIN-002`, `ARCH-038-ADMIN-003`, `ARCH-038-BACKGROUND-001` |
| [ARCH-038-SYSTEM-TEST-002](SYSTEM-TEST-002-certify-preview-budget-isolation.md) | Certify Studio Preview policy isolation and run snapshots | ready | `ARCH-038-DATABASE-001`, `ARCH-038-COMMERCE-001`, `ARCH-038-COMMERCE-002`, `ARCH-038-COMMERCE-003` |
