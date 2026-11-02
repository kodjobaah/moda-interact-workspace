# ARCH-054 Background Tasks

Architecture: [ARCH-054-merchant-configurable-ai-response-delay](../../../architecture/ARCH-054-merchant-configurable-ai-response-delay.md).

The individual task YAML frontmatter is authoritative. BACKGROUND-002 is Accepted and Complete at Attempt 2; BACKGROUND-003 is Ready and unclaimed. System certification remains pending.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-054-BACKGROUND-001](BACKGROUND-001-capture-pending-ai-delay-for-text-and-audio.md) | Capture the frozen AI delay for text and audio turns | Complete | `ARCH-054-DATABASE-001` |
| [ARCH-054-BACKGROUND-002](BACKGROUND-002-enforce-pending-ai-deadline-and-control-fencing.md) | Enforce AI deadlines and original control revision | Complete | `ARCH-054-BACKGROUND-001`, `ARCH-054-API-002`, `ARCH-054-SHOPIFY-002` |
| [ARCH-054-BACKGROUND-003](BACKGROUND-003-repair-overdue-delayed-ai-turns.md) | Repair overdue delayed AI turns | Ready | `ARCH-054-BACKGROUND-002` |
