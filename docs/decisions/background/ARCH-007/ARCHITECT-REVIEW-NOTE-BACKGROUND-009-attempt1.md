# ARCH-007 BACKGROUND-009 Attempt 1 review note

Attempt 1 received **Changes Requested**.

The core purchased-credit reservation/activation/admission implementation is
sound and should be preserved.

Attempt 2 is limited to:

1. prevent terminal RecoveryCreditPurchase reconciliation from being starved by
   an older page of non-terminal purchases;
2. keep post-REPORTED credit-activation failures out of the Shopify provider
   retry/attention state machine;
3. add the missing explicit recovery-pack concurrency/replay/lifecycle and
   publisher/reconciliation regressions.

The Background `_index.md` and canonical parent frontier are intentionally not
included because ARCH-007-BACKGROUND-010 has already been started in the live
workspace after this B009 review snapshot was created. Applying an older index
would risk overwriting that active claim.
