# ARCH-015 system-test tasks

| Task | Status | Summary |
|---|---|---|
| [ARCH-015-SYSTEM-TEST-001](SYSTEM-TEST-001-end-to-end-recovery-credit-refactor.md) | pending | Terminal integrated acceptance across purchase, carry-forward, consumption and refunds. |


## Post ADMIN-001 Attempt 2 acceptance — historical state

At ADMIN-001 acceptance, every then-declared implementation dependency was Complete and SYSTEM-TEST-001 became Ready. The later cross-repository integration audit added SHOPIFY-004 and BACKGROUND-004, so that Ready state is superseded by the current Pending/manual-test-gated state below.


## Post-implementation integration audit — manual-test gate

`ARCH-015-SYSTEM-TEST-001` returns to **Pending** because it now depends on SHOPIFY-004 and BACKGROUND-004. Separately, the architect has explicitly deferred terminal system-test execution until after manual testing. When both correction tasks are Complete, do not auto-launch SYSTEM-TEST-001; wait for explicit `moda_architect` authorization after the manual test pass.

## Post BACKGROUND-004 Attempt 2 acceptance

`ARCH-015-BACKGROUND-004` is now **Complete**. `ARCH-015-SYSTEM-TEST-001` remains
**Pending**: accepting one of the two parallel provider-meter correction tasks does not
authorize terminal system testing. Wait until every declared correction dependency,
including SHOPIFY-004, is architect-accepted Complete and the architect explicitly
authorizes the manual/integrated test phase.
