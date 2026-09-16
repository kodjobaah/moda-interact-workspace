---
id: ARCH-015-ADMIN-002
architecture_id: ARCH-015
title: Superseded — merged into ARCH-015-ADMIN-001
task_kind: documentation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: manual
status: superseded
priority: 0
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-09-16
updated: 2026-09-16
---

# ARCH-015-ADMIN-002 — SUPERSEDED

Do not execute this task.

The server/read-model work and redesigned Refund Requests UI work were intentionally merged into the single atomic implementation task:

```text
ARCH-015-ADMIN-001
```

Reason: the server actions/types and UI imports/status semantics change together. Splitting them would either require temporary compatibility code or leave the Admin repository internally inconsistent between attempts. Moda Interact is still pre-production, so no legacy compatibility layer is required.
