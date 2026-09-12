# ARCH-010 — System Test

All ARCH-010 system-test tasks are **terminal/manual-gated**. They never auto-start merely because their dependencies become Complete, and no implementation/publication/infrastructure task depends on them.

| Task | Status | Purpose |
|---|---|---|
| ARCH-010-SYSTEM-TEST-001 | Pending / manual-gated | Validate fresh Free/Paid activation, final capacity order, top-up App Events, exhaustion/resume, billing-period rollover and hosted plan changes. |
| ARCH-010-SYSTEM-TEST-002 | Pending / manual-gated | Validate uninstall/reinstall, scheduled/effective cancellation, FROZEN/UNFROZEN and the early/downstream execution gates. |
| ARCH-010-SYSTEM-TEST-003 | Pending / manual-gated | Validate FIFO purchased refunds plus opt-in GLOBAL/PLAN/SHOP campaigns, one selected promo, promo-first consumption, expiry/reopen and permanent campaign/merchant history. |
| ARCH-010-SYSTEM-TEST-004 | Pending / manual-gated | Final cross-scenario merchant lifecycle acceptance matrix after the three focused terminal tests are accepted. |

Recommended order: `001`, `002`, `003` may be invoked independently after their own dependencies and developer smoke checks; `004` runs last.
