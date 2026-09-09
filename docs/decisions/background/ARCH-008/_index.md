# ARCH-008 — Background

Architecture: `docs/architecture/ARCH-008-shopify-app-pricing-conformance.md`

| Task | Status | Purpose |
|---|---|---|
| `ARCH-008-BACKGROUND-001` | Complete | Correct App Events receipt wording and `409` retry semantics while preserving permanent identity. |
| `ARCH-008-BACKGROUND-002` | Complete | Remove pack activation from transport success and gate grants on provider-confirmed aggregate pack-meter units. |

Current frontier:

- `ARCH-008-BACKGROUND-001` Attempt 1 is architect-accepted Complete.
- `ARCH-008-SHOPIFY-001` Attempt 2 is architect-accepted Complete.
- `ARCH-008-BACKGROUND-002` Attempt 2 is architect-accepted Complete.
- `ARCH-008-ADMIN-001` is now dependency-eligible and Ready.
- `ARCH-008-SYSTEM-TEST-001` remains terminal/manual-gated.

Dependency edge:

```text
BACKGROUND-001 -----------+
                          |
SHOPIFY-001 --------------+--> BACKGROUND-002 (Complete)
                                      |
                                      v
                              ADMIN-001 (Ready)
```
