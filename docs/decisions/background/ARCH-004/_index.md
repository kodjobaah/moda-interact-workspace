# ARCH-004 — Background Tasks

Architecture:

```text
docs/architecture/ARCH-004-cart-activity-recovery-rescheduling.md
```

| Task | Description | Status | Dependencies |
|---|---|---|---|
| ARCH-004-BACKGROUND-001 | Add pending candidate inactivity clock | Complete | SHARED-002 |
| ARCH-004-BACKGROUND-002 | Apply checkout and cart activity to pending recovery | Complete | BACKGROUND-001 |

Background ARCH-004 implementation state:

```text
ARCH-004-BACKGROUND-001   Complete
ARCH-004-BACKGROUND-002   Complete
```

There is no remaining executable Background task for ARCH-004.


## Architect review — BACKGROUND-001

```text
Attempt 1   Changes Requested — Amendment 001
Attempt 2   Accepted
```

Current state:

```text
ARCH-004-BACKGROUND-001   Complete
ARCH-004-BACKGROUND-002   Ready
```

The complete Amendment 001 review history remains in the canonical
`BACKGROUND-001-add-pending-candidate-inactivity-clock.md` task file.


## Architect review — BACKGROUND-002

```text
Attempt 1   Accepted
```

Completion unlocks `ARCH-004-SHOPIFY-002`.
