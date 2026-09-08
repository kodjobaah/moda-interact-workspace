# ARCH-007 BACKGROUND-010 Attempt 2 review note

Attempt 2 received **Changes Requested**.

Attempt 2 successfully corrected the broad provider-send ownership structure and
added the settled-turn processor seam.

Attempt 3 is limited to:

1. replace active-job `changeDelay()` with a BullMQ-supported active-job delay
   transition while preserving the deterministic job id;
2. make settled clarification routing distinguish current
   resolved/clarify/unresolved outcomes, including the 11-row fail-closed
   sentinel;
3. add the missing persisted-fragment/dedupe/deterministic recovery-order
   regressions;
4. retain one definitive-provider regression alongside the accepted ambiguous
   provider case.

Per developer instruction, this task remains under the legacy no-commit/no-push
workflow until BACKGROUND-010 and ADMIN-001 are both architect-accepted.
