# ARCH-054 System Test Tasks

Architecture: [ARCH-054-merchant-configurable-ai-response-delay](../../../architecture/ARCH-054-merchant-configurable-ai-response-delay.md).

Reconciled on 2026-11-02. Individual task frontmatter and review reports are authoritative. Superseded tasks must not be executed.
Ready means implementation prerequisites are complete; system certification still requires explicit manual launch and a recorded passing result.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-054-SYSTEM-TEST-001](SYSTEM-TEST-001-certify-delayed-ai-and-human-bypass.md) | Certify delayed AI replies and immediate human response end to end | ready | `ARCH-054-DATABASE-001`, `ARCH-054-SHARED-001`, `ARCH-054-SHARED-002`, `ARCH-054-API-001`, `ARCH-054-API-002`, `ARCH-054-SHOPIFY-001`, `ARCH-054-SHOPIFY-002`, `ARCH-054-WOOCOMMERCE-001`, `ARCH-054-BACKGROUND-001`, `ARCH-054-BACKGROUND-002`, `ARCH-054-BACKGROUND-003` |
| [ARCH-054-SYSTEM-TEST-002](SYSTEM-TEST-002-certify-delayed-ai-capacity-and-repair.md) | Certify 10k pending turns and durable Redis/worker recovery | pending | `ARCH-054-SYSTEM-TEST-001`, `ARCH-054-BACKGROUND-003` |

BACKGROUND-002 and BACKGROUND-003 are Complete at Attempt 2. SYSTEM-TEST-001 is dependency-ready and requires manual launch; SYSTEM-TEST-002 remains Pending until SYSTEM-TEST-001 is Complete.
