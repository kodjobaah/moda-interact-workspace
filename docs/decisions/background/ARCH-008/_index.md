# ARCH-008 — Background

Architecture: `docs/architecture/ARCH-008-shopify-app-pricing-conformance.md`

| Task | Status | Purpose |
|---|---|---|
| `ARCH-008-BACKGROUND-001` | Complete | Correct App Events receipt wording and `409` retry semantics while preserving permanent identity. |
| `ARCH-008-BACKGROUND-002` | Ready | Remove pack activation from transport success and gate grants on provider-confirmed aggregate pack-meter units. |

Current frontier:

- `ARCH-008-BACKGROUND-001` Attempt 1 is architect-accepted Complete.
- Architectural reconciliation preflight found **no database migration is required**.
- `ARCH-008-SHOPIFY-001` Attempt 2 is architect-accepted Complete.
- `ARCH-008-BACKGROUND-002` is Ready; all listed dependencies are Complete.
- `ARCH-008-ADMIN-001` remains Pending behind BACKGROUND-002.
- `ARCH-008-SYSTEM-TEST-001` remains terminal/manual-gated.

Dependency edge:

```text
BACKGROUND-001 -----------+
                          |
SHOPIFY-001 --------------+--> BACKGROUND-002
```
