# ARCH-007 ADMIN-001 Attempt 1 review note

Attempt 1 received **Changes Requested**.

The catalog, authorization, validation, immutable-handle and transactional audit
structure is retained.

Attempt 2 is limited to:

1. make update audit `beforeValue` come from the actual persisted BillingPlan
   rather than the new form values;
2. stop existing PAID_METERED forms from injecting a Free allowance of `5`;
3. add focused behavioral regressions for both corrections.

Per developer instruction, this task remains under the legacy no-commit/no-push
workflow until ADMIN-001 and BACKGROUND-010 are both architect-accepted.
