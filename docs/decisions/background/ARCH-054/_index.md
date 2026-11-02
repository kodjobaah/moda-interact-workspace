# ARCH-054 Background Tasks

Architecture: [ARCH-054-merchant-configurable-ai-response-delay](../../../architecture/ARCH-054-merchant-configurable-ai-response-delay.md).

Reconciled on 2026-11-02. Individual task frontmatter and review reports are authoritative. Superseded tasks must not be executed.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-054-BACKGROUND-001](BACKGROUND-001-capture-pending-ai-delay-for-text-and-audio.md) | Atomically freeze AI delay when inbound text or voice opens a turn | blocked | `ARCH-054-DATABASE-001` |
| [ARCH-054-BACKGROUND-002](BACKGROUND-002-enforce-pending-ai-deadline-and-control-fencing.md) | Gate AI execution by frozen deadline and original control revision | pending | `ARCH-054-BACKGROUND-001`, `ARCH-054-API-002`, `ARCH-054-SHOPIFY-002` |
| [ARCH-054-BACKGROUND-003](BACKGROUND-003-repair-overdue-delayed-ai-turns.md) | Repair missed or overdue delayed AI turn jobs | pending | `ARCH-054-BACKGROUND-002` |
