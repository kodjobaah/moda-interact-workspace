# ARCH-008 — Background

Architecture: `docs/architecture/ARCH-008-shopify-app-pricing-conformance.md`

| Task | Status | Purpose |
|---|---|---|
| `ARCH-008-BACKGROUND-001` | Ready | Correct App Events receipt wording and `409` retry semantics while preserving permanent identity. |
| `ARCH-008-BACKGROUND-002` | Pending | Remove pack activation from transport success and gate grants on provider-confirmed aggregate pack-meter units. |

Execution order:

```text
BACKGROUND-001 -> BACKGROUND-002
```

The tasks are intentionally separate so the transport contract can be reviewed without simultaneously changing entitlement reconciliation.
