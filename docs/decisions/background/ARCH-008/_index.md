# ARCH-008 — Background

Architecture: `docs/architecture/ARCH-008-shopify-app-pricing-conformance.md`

| Task | Status | Purpose |
|---|---|---|
| `ARCH-008-BACKGROUND-001` | Complete | Correct App Events receipt wording and `409` retry semantics while preserving permanent identity. |
| `ARCH-008-BACKGROUND-002` | Ready — Changes Requested | Remove pack activation from transport success and gate grants on provider-confirmed aggregate pack-meter units. |

Current frontier:

- `ARCH-008-BACKGROUND-001` Attempt 1 is architect-accepted Complete.
- `ARCH-008-SHOPIFY-001` Attempt 2 is architect-accepted Complete.
- `ARCH-008-BACKGROUND-002` Attempt 1 was reviewed on 2026-09-09 and returned
  **Changes Requested**. The same task is Ready for Attempt 2.
- `ARCH-008-ADMIN-001` remains Pending until BACKGROUND-002 is
  architect-accepted Complete.
- `ARCH-008-SYSTEM-TEST-001` remains terminal/manual-gated.

Dependency edge:

```text
BACKGROUND-001 -----------+
                          |
SHOPIFY-001 --------------+--> BACKGROUND-002 (Ready — Changes Requested)
```
