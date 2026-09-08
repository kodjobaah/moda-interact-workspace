# ARCH-007 BACKGROUND-010 acceptance and workflow transition

`ARCH-007-BACKGROUND-010` Attempt 4 is architect-accepted Complete.

Immediate dependency promotion:

```text
ARCH-007-BACKGROUND-011 -> Ready
```

`ARCH-007-SYSTEM-TEST-005` remains Pending/manual-gated until B011 is Complete.

## Git workflow transition

The developer explicitly deferred the new mirrored feature-branch workflow until
both of these tasks were accepted:

```text
ARCH-007-ADMIN-001
ARCH-007-BACKGROUND-010
```

Both are now Complete.

Therefore the **next newly claimed task** should use the mirrored feature-branch
workflow defined by the v2 workflow overlay:

```text
parent workspace:
  task/<TASK_ID>

implementation repository:
  task/<TASK_ID>
```

The agent may commit/push both task branches but must not merge either branch
into main.

Do not retrofit feature-branch history onto ADMIN-001 or BACKGROUND-010.

A full workspace architecture/state reconciliation can be performed after the
developer applies the ADMIN-001 and BACKGROUND-010 acceptance overlays plus the
feature-branch workflow overlay.
