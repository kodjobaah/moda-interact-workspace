# ARCH-054 Background Tasks

Architecture: `docs/architecture/ARCH-054-merchant-configurable-ai-response-delay.md`
Owner: `moda_background`
Coordinator: `moda_architect`

The individual task YAML frontmatter is authoritative. BACKGROUND-002 stays Pending until BACKGROUND-001, API-002, and SHOPIFY-002 are all Complete.

| Task | Bounded outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-054-BACKGROUND-001](BACKGROUND-001-capture-pending-ai-delay-for-text-and-audio.md) | Capture the frozen AI delay for text and audio turns | Ready | `ARCH-054-DATABASE-001` |
| [ARCH-054-BACKGROUND-002](BACKGROUND-002-enforce-pending-ai-deadline-and-control-fencing.md) | Enforce AI deadlines and original control revision | Pending | `ARCH-054-BACKGROUND-001`, `ARCH-054-API-002`, `ARCH-054-SHOPIFY-002` |
| [ARCH-054-BACKGROUND-003](BACKGROUND-003-repair-overdue-delayed-ai-turns.md) | Repair overdue delayed AI turns | Pending | `ARCH-054-BACKGROUND-002` |
