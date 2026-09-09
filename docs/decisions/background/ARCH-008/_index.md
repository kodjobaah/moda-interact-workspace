# ARCH-008 — Background

Architecture: `docs/architecture/ARCH-008-shopify-app-pricing-conformance.md`

| Task | Status | Purpose |
|---|---|---|
| `ARCH-008-BACKGROUND-001` | Complete | Correct App Events receipt wording and `409` retry semantics while preserving permanent identity. |
| `ARCH-008-BACKGROUND-002` | Ready | Remove pack activation from transport success and gate grants on provider-confirmed aggregate pack-meter units. |

Execution order:

```text
BACKGROUND-001 -> BACKGROUND-002
```

The tasks are intentionally separate so the transport contract can be reviewed without simultaneously changing entitlement reconciliation.

Current frontier:

- `ARCH-008-BACKGROUND-001` Attempt 1 is architect-accepted Complete.
- `ARCH-008-BACKGROUND-002` is Ready because BACKGROUND-001 and all declared
  ARCH-007 dependencies are Complete.
- `ARCH-008-ADMIN-001` remains Pending behind BACKGROUND-002.
- `ARCH-008-SYSTEM-TEST-001` remains Pending / terminal-manual-gated.
