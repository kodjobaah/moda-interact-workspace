---
id: ARCH-006-SHARED-002
architecture_id: ARCH-006
title: Publish merchant communications shared release
task_kind: release
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-006-SHARED-001
enables:
  - ARCH-006-BACKGROUND-001
  - ARCH-006-ADMIN-001
  - ARCH-006-SHOPIFY-001
created: 2026-09-05
updated: 2026-09-05
---

# Publish merchant communications shared release

Publish only after SHARED-001 architect acceptance.

Record previous/new version, `npm pack` inspection, registry result and install/resolution evidence.

Do not modify consumers in this task.

Acceptance:
- accepted contracts packaged;
- exports intact;
- tests/typecheck/build pass;
- package contents inspected;
- registry publication succeeds;
- exact published version recorded and resolvable.

## Completion Report

### Status

Not started.

## Architect Review

### Review Status

Pending
