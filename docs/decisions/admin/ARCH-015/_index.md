# ARCH-015 admin tasks

| Task | Status | Summary |
|---|---|---|
| [ARCH-015-ADMIN-001](ADMIN-001-manual-refund-fallback.md) | complete | Atomic replacement of the superseded Admin refund workflow plus redesigned Refund Requests UI integration, deterministic manual-settlement guardrails, App Event drill-through and architect-supplied 20-locale refund translations. |
| [ARCH-015-ADMIN-002](ADMIN-002-refund-requests-ui-lifecycle.md) | superseded | Do not execute. UI scope merged into ADMIN-001 so the Admin repo changes atomically without compatibility/intermediate-state code. |

Localization contract: [ADMIN-001-localization-matrix.json](ADMIN-001-localization-matrix.json)


## Post BACKGROUND-003 Attempt 3 acceptance

`ARCH-015-BACKGROUND-003` is architect-accepted Complete, so the sole declared prerequisite of `ARCH-015-ADMIN-001` is satisfied. `ARCH-015-ADMIN-001` is now **Ready** and is the current ARCH-015 implementation frontier.

`ARCH-015-SYSTEM-TEST-001` remains Pending until ADMIN-001 is architect-accepted Complete.


## Post ADMIN-001 Attempt 2 acceptance

`ARCH-015-ADMIN-001` Attempt 2 is architect-accepted **Complete**. The ARCH-015 Admin surface now
implements the final manual-settlement boundary and the required automatic/manual refund
presentation contract without legacy REQUESTED mutations or Admin App Event submission.

All declared implementation prerequisites of `ARCH-015-SYSTEM-TEST-001` are now satisfied, so the terminal system-test task is **Ready**.
