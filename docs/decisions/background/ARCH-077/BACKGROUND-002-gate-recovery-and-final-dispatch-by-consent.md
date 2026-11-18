---
id: ARCH-077-BACKGROUND-002
architecture_id: ARCH-077
title: Gate Shopify recovery and outbound sends using signed checkout consent
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 60
executor: copilot
claimed_at: 2026-11-18T09:09:33Z
attempt: 5
depends_on: [ARCH-077-BACKGROUND-001]
enables: [ARCH-077-SHOPIFY-006, ARCH-077-SYSTEM-TEST-001]
created: 2026-11-17
updated: 2026-11-18
---

# Gate Shopify recovery and final proactive sends using signed checkout consent

**Ready for the next implementation claim under the existing-schema consent contract (18 November 2026).** The Attempt 1 blocked report and both prior architect reviews are preserved as historical evidence. The final architect reconciliation below supersedes the most recent blocker review: the developer has accepted the residual delayed cross-checkout replay risk, as already recorded in the [ARCH-077 signed receipt v1 contract](../../../architecture/ARCH-077/checkout-attribute-consent-v1.md) and parent architecture. Materialise only recoverable checkouts into existing PostgreSQL `CustomerPhone`; preserve STOP and final proactive-send gates. No Redis consent state or durable checkout evidence migration is required.

## Ownership and exact sequence

1. Keep existing authoritative Shopify abandoned-checkout lookup, merchant-configured maturity/visibility retries, payment/completion/cancellation guards and checkout identity before any consent decision. Determine `RECOVERABLE` independently of prior stored GRANT/REVOKE or whether an outreach record can be created.
2. Extract **one** `moda_wa_consent_v1` from `AbandonedCheckout.customAttributes {key value}` already read under B001. No additional provider call. Verify the exact v1 Shared AES-256-GCM authenticated receipt (`v1.` canonical envelope), rejecting incorrect version/shop/plan kind/binding/customer/locale, wrong AAD/tag/unknown key, malformed or duplicate attributes. Use the existing `MODA_ENCRYPTION_KEYS_JSON` Shared credential keyring and exact AAD/decoder/claims defined in `docs/architecture/ARCH-077/checkout-attribute-consent-v1.md`, **not** `SHOPIFY_CONSENT_RECEIPT_KEY_V1` or a duplicate HMAC/AES implementation, and the original authenticated checkout candidate token: `kind c` requires original authenticated checkout event `cart_token` matching signed base-cart SHA-256; `kind x` requires trusted checkout token matching signed checkout SHA-256. The GraphQL `AbandonedCheckout` object does **not** expose `cartToken`; don't invent it. If event tokens missing/ambiguous, fail closed; no Redis marker fallback.
3. Resolve the correct shop, verified Shopify customer and attributable recipient: valid customer phone, else billing, else shipping; a shipping recipient known unrelated is ineligible, and differing phone fields are not inherently ambiguous. Signed `customerId` must exactly match verified customer where present. Signed guest `-` still requires trusted token match and attributable recipient; never infer identity solely from phone/email or cart items. Preserve existing STOP/no-contact and canonical phone revision checks.
4. Only when checkout is **recoverable** and a verified explicit receipt exists, materialise `G`/`R` via existing `Customer`/`CustomerPhone` SQL transaction using `SHOPIFY_NATIVE`, `WHATSAPP_CHECKOUT_RECOVERY`, verified time and revision/decision sequence. A recoverable REVOKE must persist **before** B outreach is denied even if no `CheckoutRecovery` is created. A nonrecoverable/paid/completed checkout does not write consent; its signed receipt is ignored at materialisation time. Missing attribute means no *new* decision; reuse previously verified PostgreSQL GRANTED only under existing customer/recipient/STOP checks.
5. **Cart A / Cart B:** A first recoverable GRANT persists GRANTED and may send initial outreach; B later recoverable REVOKE persists REVOKED and blocks B outreach and A's future unsolicited follow-up. B paid normally => no SQL change; A's already delivered initial message and customer-initiated AI/human service replies remain valid if allowed under 24-hour WhatsApp/moderation/STOP. A subsequent independent recoverable GRANT can reauthorise new proactive sends absent STOP.
6. **Existing-schema idempotency; accepted delayed replay.** Reuse the current authenticated checkout/recovery identity, existing BullMQ retry/admission controls, durable checkout/recovery state where it actually proves prior application, and the existing PostgreSQL consent transaction/revision/STOP guards. Do not repeat an already-applied decision when durable state proves it, but do not infer prior application from a BullMQ acknowledgement, `CustomerPhone.revision`, receipt `acceptedAt`, or the mere existence of `CheckoutRecovery` (REVOKE need not create one). If prior application cannot be proven, process a newly verified, independently recoverable checkout through the normal consent transaction. **The developer has accepted the rare possibility that an older Cart A GRANT first materialised/replayed after a newer Cart B REVOKE may overwrite the current decision.** This v1 implementation does not promise cross-checkout exactly-once or total ordering. No per-checkout SQL evidence record, migration, Redis consent ledger, global lock, new queue or additional DATABASE task is authorised solely for that limitation. Preserve no mutation for paid/completed/ineligible checkouts, STOP independence and the final proactive-send gate.
7. For all future proactive outbound initial/retry/follow-up/multipart, retain the short current PostgreSQL final-send guard and STOP. Never check Redis consent or the old Shopify `defaultPhoneNumber.whatsAppMarketingConsent`; do not accidentally apply proactive rules to legitimate customer-initiated service replies or alter billing/ARCH-076 sender assignment.

## Typed outcomes

- `NOT_RECOVERABLE_TERMINAL`: no new SQL/outreach; `NO_EXPLICIT_CHOICE`: no new decision, current SQL only; `INVALID_OR_AMBIGUOUS_RECEIPT`: no new decision or proactive outreach relying on this evidence; `DEFER_CHECKOUT_BINDING`: no consent write/outreach if missing trusted event identity; `DEFER_IDENTITY_OR_RECIPIENT`: no SQL/outreach; `MATERIALISED_GRANTED`: one durable SQL write and normal admission; `MATERIALISED_REVOKED`: one durable SQL write, no new proactive outreach; `ALREADY_MATERIALISED`: SQL unchanged **only when existing durable evidence establishes prior application**; `BLOCKED_STOP`: preserve STOP; `MATERIALISATION_FAILURE`: no false success/partial materialisation. Reuse existing return shape, don't build a second state machine.

## Required integration tests and release blockers

- Disposable PostgreSQL with real current `CustomerPhone` constraints, unit tests for Shared-authenticated receipt verifier, key-ID rotation with old key retained, token/AAD binding, guest/new customer, tampering/copy/wrong tag, missing/duplicate attr, provider errors and identical/no-choice.
- Recoverable A GRANT -> one initial outreach; B pre-recoverability REVOKE -> SQL unchanged; B paid -> SQL unchanged; B recoverable -> SQL REVOKED even when B has no outreach; A unsent proactive follow-up denied; legitimate inbound A reply/AI-human response remains eligible under service window; independent STOP remains immediate.
- Test ordinary duplicate delivery and worker retry/crash-after-commit with the actual current schema and queue/recovery fixtures. Verify no reapplication **where existing durable state genuinely proves the decision was applied**, and explicitly report where it cannot prove this; do not assert unconditional no-op replay. Verify recoverable REVOKE persists even without a `CheckoutRecovery` row, and no SQL writes for paid/completed checkouts. Exercise ordinary A GRANT -> B recoverable REVOKE -> A unsent proactive follow-up denial, plus a separate late-A-after-B test that documents the **accepted residual risk** rather than demanding impossible cross-checkout ordering. Failed transactions must not claim success; provider sends retain their existing outbound idempotency. STOP and final-send SQL fences remain release-critical; the accepted replay limitation is not a blocker.
- Preserve order completion, existing BullMQ retry/idempotency and provider error logs, billing credit compensation, 2 proactive cap, Woo regression and ARCH-076 sender route. Do not modify migrations, Woo/API, `_index.md` or create Redis consent infrastructure.

## Completion Report

**Status: Blocked — `MATERIALISATION_IDEMPOTENCY_BLOCKER`.**

Implementation stopped before source or test changes. The current schema does
not provide a durable Shopify checkout-decision record that can enforce
one-time materialisation and prevent a delayed Cart A replay from overwriting a
later Cart B revoke:

- `CustomerPhone` stores only the latest permission and monotonic revision /
  decision-sequence counters; it has no checkout identity or per-checkout
  idempotency key.
- `WhatsAppConsentEvidence` is not a Shopify evidence store: its required
  `installationId` foreign key targets `WooCommerceInstallation`. Reusing that
  model for Shopify would require an invalid/fabricated installation or a
  schema/ownership change.
- `CheckoutRecovery` has a unique `(shopId, checkoutToken, generation)` key,
  but a recovery row is not guaranteed for every eligible revoke and does not
  persist the applied consent decision. It cannot prove a decision was already
  materialised when no recovery row exists.
- `acceptedAt` is receipt audit data only and cannot safely order competing
  workers. The existing per-checkout Redis lock does not serialize distinct
  carts for the same recipient.

The existing SQL compare-and-set guards and final-send consent/STOP checks do
not close the replay gap: after B's revoke commits, a delayed first-time A
materialisation can still increment the phone sequence and grant permission
again. No ordering workaround, new schema, Redis store, or fake Woo evidence
was introduced. This blocks implementation and the required crash/replay and
overlapping-recovery acceptance tests. `moda_architect` must resolve the
durable per-checkout evidence contract and ownership before this task can
continue.

**Changes:** task report only; no implementation files changed.

**Validation:** not run; stopped at the explicit materialisation-idempotency
release blocker before implementation.

**Physical worktree isolation**

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-077-BACKGROUND-002`
- Parent branch: `task/ARCH-077-BACKGROUND-002`
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-077-BACKGROUND-002`
- Implementation branch: `task/ARCH-077-BACKGROUND-002`
- Shared workspace checkout switched/mutated for task work: no
- Shared implementation checkout switched/mutated for task work: no
- Another task worktree reused: no

**Start-of-attempt synchronization**

- Parent remote task branch fast-forwarded: not-needed
- Parent `origin/main` incorporated: already-current
- Implementation remote task branch fast-forwarded: not-needed
- Implementation `origin/main` incorporated: already-current

**Recursive implementation submodules**

- `git submodule sync --recursive`: passed
- `git submodule update --init --recursive`: passed
- Recorded submodule commit: `database` at `0a9edc7c0c30e0a405d89efec624bc9338b4ac17`


## Architect Review — 18 November 2026 (blocker resolved, Changes Requested)

### Review Status

**Changes Requested / unblock to `ready` for Attempt 2.** The original agent correctly stopped under the then-current absolute idempotency requirement. This is an **architectural scope correction**, not rejection of unimplemented source: the submitted Attempt 1 report remains intact; no B002 implementation or test work was claimed.

### Accepted design decision

- The developer explicitly **accepts the residual cross-checkout delayed-replay risk** and declines additional database columns, migrations, ledgers, Redis state or locking solely to eliminate that extreme case. Do not claim that a database revision counter or BullMQ acknowledgment can provide an absolute guarantee.
- Materialise an explicit G/R selection **only after** the independently verified checkout becomes recoverable. A normal completed/paid/ineligible checkout never changes SQL. In the ordinary A-then-B flow, B's materialised REVOKE becomes current `CustomerPhone` permission, blocks B's new proactive outreach and blocks A's unsent proactive follow-up; it does not prevent permitted customer-initiated AI/human replies to A. STOP remains independent and immediate.
- Keep the existing checkout-specific BullMQ admission, idempotent outbound attempt handling and SQL consent transaction/STOP/final-send fences. Consult existing durable state opportunistically to avoid proven same-checkout duplicates, but do not invent a record merely to support this check. In the absence of durable evidence proving prior application, normal recoverable-only SQL materialisation may proceed; its residual delayed-ordering risk is accepted.
- Avoid implementing a generic `ALREADY_MATERIALISED` answer solely on the basis of a retry marker, queue-job completion or timestamp unless the existing durable record proves the applied decision. Do not incorrectly equate `CheckoutRecovery` existence with persisted REVOKE. Do not silently turn a REVOKE into a GRANT due to missing evidence.

### Attempt 2 implementation and verification scope

1. Implement the existing signed Shopify AEAD attribute verifier and exact authenticated shop/cart/checkout/customer/recipient binding from receipt v1; reuse the B001 authoritative lookup, with no additional consent GraphQL query.
2. Apply G/R to existing PostgreSQL consent state only for a recoverable checkout; perform recoverable R **before** denying outreach even if no `CheckoutRecovery` record will be created. Preserve all actual SQL constraints, monotonic revisions, source/purpose, no-contact and STOP safeguards.
3. Reuse current checkout/recovery generation identity and existing durable guards where proven, without new schema or Redis. Report precisely which duplicate/retry scenarios are actually prevented and which remain susceptible to replay.
4. Test ordinary duplicate event/retry and worker-failure scenarios with actual current-schema fixtures, sequential Cart A GRANT / Cart B REVOKE, no-choice/current-SQL fallback, recipient mismatch, tampering, STOP, final proactive follow-up and legitimate reactive conversation. For an exceptionally late A application after B, assert/report the **accepted limitation**, not a fictional invariant.
5. Preserve billing/credit compensation, two-proactive-message cap, order completion, ARCH-076 sender routing, WooCommerce isolation and original safely redacted provider/SDK error details. Keep previously accepted B001 source untouched except for the minimal integration necessary to consume its typed output.
6. Record branch/commit SHAs, dedicated worktrees, submodule pins, targeted lint/typecheck, focused tests and disposable PostgreSQL verification in the new Completion Report. Do not claim tests previously blocked in Attempt 1 have run.

### Handoff / workflow

- Preserve `attempt: 1` and historical Completion Report; set `status: ready`, `executor: null`, `claimed_at: null`. The standard `/moda-task ARCH-077-BACKGROUND-002` launcher must claim Attempt 2 and later submit `review`.
- Do not mark B002 `complete` or unblock SHOPIFY-006/SYSTEM-TEST-001 until a subsequent architect implementation review accepts the actual code and evidence.
- No `docs/decisions/**/_index.md`, legacy migrations or other agent-owned task files are changed by this handoff.


## Architect Review — 18 November 2026 (Attempt 2 blocked: evidence contract unresolved)

### Review Status

**Blocked.** The previous review did not define a durable per-checkout evidence contract sufficient to satisfy this task. It explicitly allowed materialisation without evidence when the current schema cannot prove prior application and accepted that a delayed first-time Cart A GRANT may overwrite a later Cart B REVOKE. That is not an evidence contract; it is a relaxation of the invariant. It also conflicts with the still-current ARCH-077 v1 architecture statement that an already-applied older checkout decision must never reapply after a newer decision.

### Review Notes

1. The Attempt 1 report identifies the missing durable facts: `CustomerPhone` has no checkout identity; `CheckoutRecovery` is optional and does not record an applied consent decision; WooCommerce `WhatsAppConsentEvidence` cannot represent Shopify evidence; and signed `acceptedAt` is audit data, not a durable ordering key.
2. The Attempt 2 resolution text proposed opportunistic reuse of existing state, but it does not establish (a) a unique durable identity for an applied checkout receipt, (b) an atomic evidence-plus-permission transaction for a REVOKE even without a recovery row, or (c) a trustworthy total ordering across distinct checkouts. In particular, accepting the late-A-after-B overwrite does not meet the parent architecture contract.
3. The task therefore cannot resume under the unchanged v1 contract. Before B002 implementation resumes, moda_architect must define and record an ARCH-077 contract that:
   - identifies each authenticated decision by shop, checkout binding, and exact receipt/decision identity, with durable uniqueness/idempotency;
   - stores proof of application in PostgreSQL atomically with the `CustomerPhone` update, including recoverable REVOKEs that create no `CheckoutRecovery`;
   - defines an authenticated, trustworthy ordering value across independent checkouts, and a transaction rule that rejects/supersedes an older decision rather than allowing it to overwrite newer permission;
   - specifies the issuer, persistence owner, schema owner, receipt version/compatibility, and required rollout/dependency order;
   - keeps paid/completed/ineligible checkouts from mutating permission, preserves STOP as independent and immediate, and retains final proactive-send SQL/STOP checks.
4. `acceptedAt`, a phone revision counter, queue-job state, or an optional recovery row must not be presented as satisfying those invariants unless a new reviewed contract proves how it does so. Do not implement a local workaround, use Redis as the consent ledger, or weaken the replay invariant in B002.
5. The canonical implementation worktree currently contains uncommitted Attempt 2 source/test changes. They were not reviewed or modified in this architecture-only review. Stop further B002 implementation; do not discard or commit those changes under this blocked task. The developer must preserve/reconcile that worktree state before any later prepared attempt, because the next launcher preparation requires a clean synchronized worktree.

### Handoff / Workflow

- Task status is `blocked`; `executor` and `claimed_at` are cleared. `attempt: 2` is preserved. No new claim is authorized.
- No dependent task is unblocked. After the architecture and prerequisite implementation/publication tasks are complete and architect-accepted, update this task's `depends_on`, then return B002 to `ready` through the canonical task workflow.
- This review changes only the ARCH-077 task report. No Background source, tests, schema, or migration files were changed or reviewed.


## Architect Review — 18 November 2026 (final reconciliation: accepted-risk contract; ready for Attempt 3)

### Decision and source of authority

**Changes Requested / unblock to `ready` for the next claim.** This review supersedes the immediately preceding *Attempt 2 blocked: evidence contract unresolved* review without deleting or rewriting it. The preceding review incorrectly treated absolute cross-checkout replay prevention as still required. In this uploaded parent task snapshot, both `docs/architecture/ARCH-077/checkout-attribute-consent-v1.md` (Background decision path, item 7) and `docs/architecture/ARCH-077-shopify-owned-whatsapp-checkout-consent.md` already explicitly document the developer-approved existing-schema design and the accepted rare delayed-replay limitation. The later blocked review did not identify a new operational failure or override that authorised scope choice.

### Binding implementation contract

1. Independently verify authenticated shop/checkout/cart/customer/recipient binding and Shared-AEAD receipt before SQL; first confirm recoverability using existing authoritative checkout/maturity/completion/payment gates. Read the signed attribute from the existing B001 lookup; no extra Shopify API call or Redis consent source.
2. Materialise verified GRANT or REVOKE to current `CustomerPhone` only for recoverable checkouts, with the existing PostgreSQL transaction/revisions/source/purpose/STOP guards. REVOKE persists before denying outreach even when no recovery row is created. Completed/paid/ineligible checkouts never update consent; missing explicit choice does not create a new choice.
3. Use existing checkout/recovery/BullMQ idempotency and durable proof where genuine. Do not equate `CheckoutRecovery` existence, worker ack, revision, or receipt time with proof that consent was applied. Where no durable proof exists, process a valid recoverable receipt normally. No additional migration, ledger, checkpoint, Redis key, lock, queue, receipt version or prerequisite DATABASE task.
4. The developer **accepts** that an exceptionally late older Cart A materialisation may overwrite a newer Cart B REVOKE. Do not write an absolute replay-prevention invariant, invent a fake duplicate-suppression outcome, or stop with `MATERIALISATION_IDEMPOTENCY_BLOCKER` solely because the existing schema cannot eliminate this scenario. Record what retry/duplicate cases are actually prevented, and test/document the residual case accurately.
5. Preserve STOP as an independent immediate suppression, current SQL/STOP checks at each proactive final send, existing reactive conversation policy, billing/credit, ARCH-076 routing and WooCommerce behaviour. Do not relax these safety checks to simplify consent materialisation.

### Worktree and acceptance workflow

- Set `status: ready`, `executor: null`, `claimed_at: null`, preserving `attempt: 2`. The next successful launcher claim will be Attempt 3. **This documentation-only unblocking is not implementation acceptance**; downstream tasks stay gated until B002 is reviewed and accepted.
- The prior blocked review reports **uncommitted Attempt 2 source/test changes in the separate implementation worktree**. Preserve them; review `git status` and export a binary Git diff (including staged changes separately and any untracked files) before cleaning or preparing that worktree. Reconcile those changes explicitly into Attempt 3 or a separate safe branch. Do not blindly rerun the launcher against dirty state, discard code, or claim those changes have been reviewed from this parent ZIP.
- Implementation must supply a new Completion Report with actual focused and disposable-PostgreSQL tests, exact changed paths/commits/submodule pin, lint/typecheck and clear evidence for the accepted limitations. No `_index.md` updates.


## Completion Report — Attempt 3

**Status: Ready for Review.** Implemented the recoverable-checkout consent gate and final proactive-send protections under the final accepted-risk contract. Attempt 2's preserved work was reconciled into this attempt. The task is submitted for `moda_architect` review; this report does not make an architect acceptance decision.

### Architect Review correction checklist

1. **Shared-AEAD receipt verification — implemented.** Added `src/services/shopify-consent-receipt-verifier.ts` using the Shared credential keyring/decrypt API, strict v1 envelope and claims validation, correct AAD, shop/plan/token/customer binding, and fail-closed outcomes. No duplicate cryptography, alternate key, provider lookup, or Redis consent state was added. Focused verifier tests passed.
2. **Recoverability-only SQL materialisation and revoke-before-denial — implemented.** `src/services/checkout-recovery/recovery-materialization.service.ts` gates consent application after terminal/order/completion checks and the authoritative checkout lookup. A verified recoverable revoke is persisted before outreach is denied, including when no recovery row is created. The disposable-PostgreSQL integration passed for paid no-write, recoverable revoke, and no-recovery-row behavior.
3. **Retry/duplicate behavior and accepted replay limitation — implemented and documented.** Existing checkout locking, recovery/admission behavior, SQL revisions/STOP checks and provider-send idempotency remain in use; no synthetic `ALREADY_MATERIALISED` result or new persistence/Redis mechanism was introduced. The PostgreSQL test simulates a crash after a grant commit but before recovery creation: retry has no durable per-checkout proof, re-verifies and writes normally (revision 1 to 2). A later recoverable B revoke persists and denies A's unsent proactive follow-up; a subsequent late A grant is explicitly tested as the accepted residual risk (revision 4), not represented as prevented.
4. **STOP, reactive conversation, sender routing and adjacent behavior — implemented/preserved.** STOP remains independent; proactive final-send checks remain in SQL, while the added freeform customer-reply test verifies reactive replies do not invoke proactive consent preflight. The ARCH-076 sender dispatch integration passed. No migrations, WooCommerce source, API, or architecture indexes were changed.
5. **Validation and evidence — recorded below.** Focused validation was run after the latest test edit. The STOP disposable integration could not start its ephemeral PostgreSQL container in the final isolated attempt; that limitation is recorded without claiming a pass.

### Changed files

- `src/domain/abandoned-checkout.ts`
- `src/providers/shopify-whatsapp-consent.provider.ts` (removed)
- `src/services/abandoned-checkout-lookup.service.ts`
- `src/services/checkout-recovery/recovery-materialization.service.ts`
- `src/services/shopify-checkout-consent-materialization.service.ts` (added)
- `src/services/shopify-consent-receipt-verifier.ts` (added)
- `src/services/shopify-whatsapp-consent.service.ts`
- `src/services/shopify-whatsapp-consent/projection-writer.ts`
- `src/services/shopify-whatsapp-consent/types.ts`
- `tests/integration/arch052-shopify-initial-no-offer-dispatch.integration.test.ts`
- `tests/integration/shopify-whatsapp-consent.integration.test.ts`
- `tests/integration/whatsapp-contact-opt-out.integration.test.ts`
- `tests/unit/providers/shopify-whatsapp-consent-domain.test.ts` (removed)
- `tests/unit/providers/shopify-whatsapp-consent.provider.test.ts` (removed)
- `tests/unit/services/abandoned-checkout-lookup.service.test.ts`
- `tests/unit/services/checkout-recovery/recovery-materialization.service.test.ts`
- `tests/unit/services/checkout-recovery/recovery-snapshot-builder.service.test.ts`
- `tests/unit/services/checkout-refresh.test.ts`
- `tests/unit/services/matured-candidate.materialization.test.ts`
- `tests/unit/services/outbound-whatsapp-admission/outbound-message-delivery.service.test.ts`
- `tests/unit/services/shopify-checkout-consent-materialization.service.test.ts` (added)
- `tests/unit/services/shopify-consent-receipt-verifier.test.ts` (added)
- `tests/unit/services/shopify-whatsapp-consent.service.test.ts`

### Validation

- Passed: changed consent/recovery unit suites — 9 files, 170 tests.
- Passed: `npm run lint`.
- Passed: `npm run build` (Prisma client generation, TypeScript builds, package sample generation).
- Passed: `npm run test:integration -- tests/integration/shopify-whatsapp-consent.integration.test.ts` — 1 file, 2 tests, disposable PostgreSQL.
- Passed: `npm run test:arch076-sender-dispatch:postgres` — 1 file, 12 tests.
- Passed: `git diff --check`.
- Not passed / environment blocked: isolated `tests/integration/whatsapp-contact-opt-out.integration.test.ts` invocation with `--testTimeout=30000` could not start `pgvector/pgvector:pg17`; `docker run` was killed with exit 143. Earlier combined execution also exposed a quoted-STOP assertion failure; the STOP integration therefore has no passing result claimed here.
- Broader ARCH-052 integration validation remains failing at `PROMPT_CONFIGURATION_DUPLICATE_OR_MISSING`; it is not claimed as task validation success. No known baseline ID was identified for that failure.

### VCS and worktree evidence

- Implementation commit: `9c8a12d073376b9315c998394e31012daaef5571` (`feat(background): gate recovery by signed checkout consent`), pushed to `origin/task/ARCH-077-BACKGROUND-002`.
- Parent task report is the only parent-worktree file changed in this completion update; no implementation submodule gitlink was staged.
- Physical worktree isolation:
  - canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  - parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-077-BACKGROUND-002`
  - parent branch: `task/ARCH-077-BACKGROUND-002`
  - implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-077-BACKGROUND-002`
  - implementation branch: `task/ARCH-077-BACKGROUND-002`
  - shared workspace checkout switched/mutated for task work: no
  - shared implementation checkout switched/mutated for task work: no
  - another task worktree reused: no
- Start-of-attempt synchronization, from the prepared launcher packet:
  - parent remote task branch fast-forwarded: not-needed
  - parent `origin/main` incorporated: already-current
  - implementation remote task branch fast-forwarded: not-needed
  - implementation `origin/main` incorporated: already-current
- Recursive implementation submodules, from the prepared launcher packet:
  - `git submodule sync --recursive`: passed
  - `git submodule update --init --recursive`: passed
  - recorded pin: `database` at `0a9edc7c0c30e0a405d89efec624bc9338b4ac17`

Implementation changes are committed and pushed on the mirrored task branch. The parent report is ready to commit and push on its mirrored task branch; the task awaits architect review.


## Architect Review — 18 November 2026 — Attempt 3: Changes Requested

**Decision: CHANGES REQUESTED; return to `ready` for Attempt 4.** The submitted implementation commit is `9c8a12d073376b9315c998394e31012daaef5571`; the Attempt 3 parent report is preserved above. This is not acceptance. Architect review used the uploaded `moda-interact-workspace-ARCH-077-BACKGROUND-002(3).zip` source; the agent's test results are reported evidence, not independently rerun by the architect.

### Accepted implementation findings — preserve intact

- The existing bounded authoritative `AbandonedCheckout.customAttributes` lookup supplies one signed attribute; the verifier reuses Shared `decryptCredential`/`parseCredentialKeyring`, checks v1 envelope/AAD, shop, plan kind, candidate token and Shopify customer binding, and does not create Redis preference storage.
- `RecoveryMaterializationService` checks existing terminal/order/completion and shop admission gates before applying a verified checkout decision; a recoverable REVOKE is persisted before outreach is denied, without requiring a recovery row.
- Current `CustomerPhone` CAS/consent revisions, STOP and the separate proactive final-send SQL fence are retained; customer-initiated service responses are not incorrectly subjected to the proactive fence.
- PostgreSQL consent integration documents A GRANT, B paid no-write, B recoverable REVOKE without a B recovery row, normal retry after interruption, and the **explicitly accepted** exceptional late A replay. Do **not** reinstate `MATERIALISATION_IDEMPOTENCY_BLOCKER`, impose cross-checkout total ordering, or add a migration, checkout ledger, Redis consent record, new queue or distributed lock.

### Blocking correction 1 — operational verifier failure must not masquerade as invalid customer evidence

**Source:** `moda-interact-background/src/services/shopify-consent-receipt-verifier.ts`, and its direct consumers `src/services/shopify-checkout-consent-materialization.service.ts` / `src/services/checkout-recovery/recovery-materialization.service.ts`.

Today `parseCredentialKeyring(input.keyringJson)` is inside the same `try/catch` as `decryptCredential`. Any missing/malformed deployment keyring configuration is converted to `INVALID_OR_AMBIGUOUS_RECEIPT`, and the materialisation path maps it to `discarded-consent-invalid`. That silently turns a recoverable valid customer decision into a non-retryable invalid-receipt outcome while obscuring the real operational issue.

- Distinguish **missing/invalid Shared keyring configuration** from **malformed/tampered receipt, unknown/retired receipt key ID or authentication-tag failure**. The latter remain invalid evidence and never grant outreach. Reuse the existing Shared parser and decryptor; do not introduce alternate crypto or a key service.
- For keyring configuration unavailable, return an existing typed operational materialisation-failure outcome (or throw a bounded, typed error that the existing pending-candidate worker retries) rather than `INVALID_OR_AMBIGUOUS_RECEIPT`. Log the original parser/configuration exception message, name and available error code through the existing server structured logger. Do not log encryption-key contents or Shopify authentication credentials. Preserve the actual exception as the cause rather than substituting only an opaque reason code.
- Add focused regression tests: absent keyring and invalid keyring are **operational failures**, not invalid receipts; unknown receipt key ID, tampered tag, malformed envelope and wrong binding remain invalid evidence; no SQL write/outreach occurs in either failure category. Test the end-to-end mapping to worker retry versus terminal invalid evidence. Keep code modular and avoid additional provider reads.

### Required diagnostic logging contract — independent stages, original error messages (part of correction 1)

**Pre-production priority: visibility into actual values and actual failures.** The implementing agent MUST use the existing server structured logger (`createLogger` / `StructuredLogger` from `@modainteract/moda-interact-shared/logging`) with the current Background logging conventions. Do not add an environment flag, opt-in debug mode, separate logger, new storage or configuration system. Do not create architecture/task-ID-prefixed runtime event names. Normal production logging restriction/hardening is a separate pre-launch concern; this task must not artificially reduce the detail available in pre-production. Exclude Shopify access tokens, authentication credentials and the encryption keyring/key material, which are not GraphQL response data and are not needed for debugging. Existing Shared logging-kernel behaviour remains in place; do not bypass its infrastructure to print directly to stdout.

1. **Independent verifier failure boundaries:** separate missing `MODA_ENCRYPTION_KEYS_JSON` from `parseCredentialKeyring()` parser exceptions, and handle `decryptCredential()` errors in their own catch. Missing/malformed keyring is an operational error routed to the existing retry path; a valid keyring and rejected receipt (unknown key ID, tampered tag, malformed envelope, wrong binding) remains invalid evidence. Log a separate named event for each outcome, at the actual failure boundary. These must never manufacture a GRANT.
2. **Preserve original errors:** for keyring parsing, receipt decryption, JSON claims, identity parsing, PostgreSQL consent writes, Shopify transport/HTTP/GraphQL responses and STOP regressions, log the original `error.message` (or non-Error string), `error.name`, available `code`, provider/Prisma response details, and the specific operation/stage. Preserve the original exception as `cause` when propagating. Do not invent or substitute generic messages for real exceptions. Where a validation guard does not throw, log a precise factual message and validation reason without fabricating an exception. Keep the error message intact under the existing structured logger rather than adding an ad-hoc redaction or allowlist that removes diagnostic details.
3. **Discriminating events:** use stable events such as `shopify.consent.receipt.keyring_missing`, `.keyring_invalid`, `.decrypt_rejected`, `.claim_parse_failed`, `.claim_invalid`, `.identity_deferred`, `.verified`, `shopify.consent.materialization.failed`, `.granted`, `.revoked`, and `shopify.consent.outbound.blocked`. Record `shopId`, operation, stage, outcome, decision/reason code, existing recovery/job identifiers and checkout correlation; ensure the same checkout can be traced from Shopify lookup through SQL and final dispatch. Use `error` for configuration/SQL failures, `warn` for invalid evidence, and `info` for verified outcomes and suppression. `NO_EXPLICIT_CHOICE` is a normal outcome, not an exception.
4. **What must be visible:** the initial Shopify GraphQL payload is logged in full in the subsection below (including the complete encrypted `moda_wa_consent_v1` value, checkout URL, basket, addresses and Shopify customer details exactly as returned), then a separate verification event records whether the receipt validated, what GRANT/REVOKE decision was extracted, and why it was admitted/deferred/denied. Record the durable PostgreSQL decision/write outcome and the later STOP/final-send gate. Do not misrepresent a GraphQL-received encrypted receipt as a verified decision. Do not log the keyring JSON, encryption secrets, Shopify access tokens or authentication headers; these are credentials, not returned basket data.
5. **Tests:** spy on the existing logger. Assert distinct events and the *original* parser, decryptor, JSON, identity and Prisma error messages, not merely a `reasonCode`. Test missing/invalid keyring operational retry separately from invalid/tampered receipt terminal handling, no SQL grant in either failure case, verified GRANT/REVOKE and proactive STOP/final-send refusals. Assert real returned provider payload fields are retained, including the exact sample encrypted consent attribute and customer/basket values used in the GraphQL response fixture. Assert Shopify API access tokens and encryption key material are not emitted. No live Shopify merchant is required for these logger unit tests.
6. **STOP regression diagnostics:** a failed Docker/Testcontainers start must include its exit code, original error and stderr in the report, distinguished from an actual STOP assertion failure. A quoted-STOP assertion failure must include the real assertion diff and corresponding structured STOP admission log. Do not relax existing merchant-scoped/standalone STOP rules or replace failure messages with generic reason strings.

### Blocking correction 1A — Complete Shopify GraphQL response logging (same lookup, no new provider call)

**Source:** `moda-interact-background/src/services/abandoned-checkout-lookup.service.ts` and `tests/unit/services/abandoned-checkout-lookup.service.test.ts`.

The bounded authoritative lookup makes up to **two GraphQL HTTP POST calls per invocation**: `AbandonedCheckoutsCount` then, when `0 < count <= maxCandidates`, `AbandonedCheckouts`. The detail query already returns basket, customer, plan and `customAttributes { key value }` (including `moda_wa_consent_v1`). Do not add another query or change the existing bound. Subsequent retries may reissue these two calls.

Using the existing `lookupLogger` and Shared structured logging kernel, record the **complete JSON response body as actually received from Shopify** for each successful count and detail call, rather than an allowlisted, redacted, flattened or debug-only field selection. Include all returned nodes and nested fields, all customer/phone/email/address information, full checkout/recovery URLs, all basket product/variant/price/currency fields, and every custom attribute with its exact `key` and `value`, including the complete encrypted signed consent receipt. Retain the distinction between missing fields, explicit `null`, empty arrays, malformed values and valid values. Preserve raw JSON semantics; do not fabricate default values in the response log. If parsing fails, log the actual received response text and the original JSON parse exception as separate diagnostic data.

Log structured request/response event pairs for `AbandonedCheckoutsCount` and `AbandonedCheckouts` with the operation name, `shopId`, checkout/job correlation, actual HTTP status, query bounds and timing if available, plus the full provider response body. For non-2xx and GraphQL `errors[]`, log the **actual Shopify response body and the original error messages, extensions, paths and status**—not only `PROVIDER_ERROR` or a reason code. Log count-query bounds decisions (zero, over-bound, missing count) and exact match/ambiguity decisions separately so the developer can see both the raw data and the downstream Moda interpretation. For a verified receipt, log the materialisation decision after decryption; never infer a decision merely from the encrypted attribute.

This is pre-production validation logging and should be emitted through the existing logger at a level enabled by the current non-production configuration; do not require a new environment variable, extra opt-in switch or a separate custom logger. Do not impose an artificial item count or response truncation in the logs: the GraphQL query already has existing candidate and line-item limits. Never log Shopify authentication headers, access tokens or encryption keys; do not build a second network request or change control flow solely for logging. Do not catch-and-continue when the provider or JSON parser fails.

**Focused logging assertions:** mock count and detail responses and assert the full exact returned JSON is recorded for both calls, including phone/email/address, basket items, checkout URL, receipt attribute `key` and the **entire test receipt `value`**, and Shopify's full GraphQL `errors[]` structure. Assert missing/null fields are visibly different, and that original HTTP/parsing/provider exception messages are preserved. Assert the existing zero/over-bound branch skips the detail call; the normal success branch uses exactly one count and one detail query per lookup. Assert no Shopify access token, request authentication header or encryption key is logged. No live store is required.

**Acceptance criterion:** from the logs, the developer can reconstruct exactly which values Shopify returned in the count and detail responses and correlate those payloads with signature verification, consent SQL state changes, STOP and the final outbound decision. Error logs must show the original failure message and relevant provider/SDK details. No new infrastructure or protective logging mode is part of BACKGROUND-002.

### Blocking correction 2 — independently resolve the STOP integration gap

**Test:** `moda-interact-background/tests/integration/whatsapp-contact-opt-out.integration.test.ts`.

The Attempt 3 Completion Report explicitly says the isolated disposable PostgreSQL run could not start `pgvector/pgvector:pg17` (Docker exit 143), and an earlier combined run produced a quoted-STOP assertion failure. Neither is a passing STOP regression. Obtain a clean focused PostgreSQL run and record exact commands, test counts, and any error/failed assertion. If the quoted-STOP test still fails, diagnose the real cause and correct only the relevant source/test fixture without weakening merchant-scoped STOP or the standalone-STOP fallback. If environment/container setup fails, preserve full diagnostics and do not claim a functional pass. Do not change an unrelated service merely to make the test green.

### Scope clarification (not an additional schema task)

The current service deliberately defers `customerId:"-"` guest receipts without an independently verified Shopify-customer/CustomerPhone principal. That is an appropriate fail-closed result in the absence of attribution; document this observable v1 limitation rather than inferring customer identity from phone/email or manufacturing a guest principal. Terminal system-test coverage must distinguish actual guest non-support from a validated customer-linked flow. No new guest-identity system is authorised by this review.

### Acceptance tests / stop conditions

- Re-run the bounded abandoned-checkout GraphQL lookup tests including exact complete count/detail response payload logs and original provider-error assertions, along with focused Shared-AEAD verifier, checkout consent materialisation and recovery admission suites; re-run disposable PostgreSQL consent integration and **passing** STOP regression; re-run ARCH-076 sender tests, lint, build, and `git diff --check`. Report exact failures rather than claiming a pass when Docker cannot start.
- Record whether the broader ARCH-052 `PROMPT_CONFIGURATION_DUPLICATE_OR_MISSING` failure is unchanged baseline; do not silently attribute that issue to B002 or expand this task without causal evidence.
- Preserve current source changes, successful tests, parent Attempt 3 report and prior architect reviews. Do not change existing migrations, Woo/API/Shared, `_index.md`, or create consent Redis state.
- Task metadata becomes `status: ready`, `executor: null`, `claimed_at: null`, `attempt: 3`; the launcher may claim **Attempt 4**. SHOPIFY-006 and SYSTEM-TEST-001 remain gated until a later architect acceptance. Stop and report a concrete unsupported requirement rather than making new architecture decisions.


## Completion Report — Attempt 4

**Status: Blocked — `FULL_GRAPHQL_RESPONSE_LOGGING_CONFLICT`.** The operational
keyring classification, consent failure propagation/diagnostics and STOP
integration gap were addressed and validated. The required complete Shopify
GraphQL response logging cannot safely be implemented under the still-current
shared logging and ARCH-077 receipt contracts; that conflict requires
`moda_architect` resolution before this task can return for review.

### Architect Review correction checklist

1. **Operational verifier failure and consent/STOP diagnostics — partially
   implemented.**
   - Missing `MODA_ENCRYPTION_KEYS_JSON` or a Shared
     `parseCredentialKeyring` failure now returns
     `KEYRING_CONFIGURATION_FAILURE`, logs distinct `keyring_missing` /
     `keyring_invalid` events with the original exception, and maps to
     `MATERIALISATION_FAILURE` with the original cause. Recovery materialisation
     rethrows that cause so BullMQ can retry; no SQL write or outreach is
     attempted.
   - Unknown/retired receipt key, malformed/tampered envelope and wrong binding
     remain invalid evidence. Decrypt, claim-JSON, claim-validation, identity,
     SQL-write, proactive preflight/final-fence and STOP write failures use the
     Shared structured logger with operation/stage, checkout/recovery
     correlation where available and original errors. Grant/revoke, identity
     deferral, STOP suppression and proactive send blocks have semantic events.
   - Focused tests cover missing and malformed keyring as operational failures,
     terminal unknown-key/tag evidence, retry propagation, no SQL/outreach on
     configuration failure, and preservation of the original preflight error.
   - **Still blocked:** complete count/detail GraphQL response-body logging and
     the associated payload/provider-error assertions in correction 1A were not
     implemented. See item 2 below.

2. **Complete Shopify GraphQL response logging — blocked by policy conflict.**
   - The latest Architect Review requires logging complete count/detail response
     bodies containing customer name/email/phone/address, checkout/recovery URL,
     basket data and the full signed receipt value.
   - `docs/observability/shared-logging.md` expressly prohibits passing complete
     provider response bodies and customer email/phone/address to the logger,
     and requires provider data to be filtered before Shared logger emission.
     `docs/architecture/ARCH-077/checkout-attribute-consent-v1.md` separately
     says never to emit a complete receipt to logs. These are direct
     contradictions, not a missing implementation detail.
   - No raw response body, complete consent receipt, customer PII, access token,
     auth header or key material was added to logs; the shared logger's
     redaction/bounds were not bypassed. The requested full-payload logging
     tests are consequently not claimed.
   - **Requested architect action:** reconcile the current task review with the
     shared logging and ARCH-077 receipt contracts, defining a compliant
     field-level diagnostic contract. Until then, correction 1A cannot be
     completed safely.

3. **STOP PostgreSQL integration gap — implemented.**
   - The first rerun exposed a real quoted-STOP fixture failure (expected
     unrelated shop B to remain `false`, received `true`). The fixture lacked
     the required durable provider-dispatch identity and linked initial
     `RecoveryOutreachAttempt`, so the production verifier correctly used the
     standalone global-STOP fallback. The fixture now represents a confirmed
     outbound with provider dispatch key/admission/control revision, numeric
     sender IDs, and a sent initial recovery attempt. A structured
     `whatsapp.stop.quote_resolution` event records verified-shop scoping versus
     global fallback; STOP errors preserve their original exception.
   - Final focused PostgreSQL run passed all 8 tests, including verified
     quoted-shop scope and unresolvable-quote global fallback. Docker/Testcontainers
     started successfully; no container-start failure remains.

### Changed files

- Consent verifier/materialisation, SQL projection writer and types:
  `src/services/shopify-consent-receipt-verifier.ts`,
  `src/services/shopify-checkout-consent-materialization.service.ts`,
  `src/services/shopify-whatsapp-consent.service.ts`,
  `src/services/shopify-whatsapp-consent/projection-writer.ts`,
  `src/services/shopify-whatsapp-consent/types.ts`,
  `src/services/checkout-recovery/recovery-materialization.service.ts`.
- Outbound and STOP diagnostics:
  `src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts`,
  `src/services/recovery-conversation/recovery-stored-consent.service.ts`,
  `src/services/whatsapp-contact-opt-out.service.ts`.
- Focused verifier, materialisation, retry, final-consent and STOP tests:
  `tests/unit/services/shopify-consent-receipt-verifier.test.ts`,
  `tests/unit/services/shopify-checkout-consent-materialization.service.test.ts`,
  `tests/unit/services/checkout-recovery/recovery-materialization.service.test.ts`,
  `tests/unit/services/recovery-conversation/recovery-stored-consent.test.ts`,
  `tests/integration/whatsapp-contact-opt-out.integration.test.ts`.

### Validation

- Passed: focused consent/recovery/outbound unit suites — 5 files, 107 tests.
- Passed: bounded abandoned-checkout lookup unit suite — 1 file, 13 tests.
  These validate existing lookup behavior only; they do not prove the
  unimplemented full-response logging assertions.
- Passed: disposable PostgreSQL consent integration —
  `npm run test:integration -- tests/integration/shopify-whatsapp-consent.integration.test.ts`
  — 1 file, 2 tests.
- Passed: disposable PostgreSQL STOP integration —
  `npm run test:integration -- tests/integration/whatsapp-contact-opt-out.integration.test.ts`
  — 1 file, 8 tests.
- Passed: ARCH-076 sender dispatch regression —
  `npm run test:arch076-sender-dispatch:postgres` — 1 file, 12 tests.
- Passed: targeted ESLint over all changed source/test files after the final
  edits; full `npm run lint` also passed earlier in Attempt 4, before the final
  outbound/STOP diagnostic additions. `npm run build` and `git diff --check`
  passed after the final edits.
- Not run in Attempt 4: broader ARCH-052 validation. Its earlier
  `PROMPT_CONFIGURATION_DUPLICATE_OR_MISSING` failure is not reclassified or
  claimed as an unchanged baseline by this attempt.

### VCS and worktree evidence

- Implementation commit `6e26516` (`fix(background): distinguish consent configuration failures`) is pushed to `origin/task/ARCH-077-BACKGROUND-002`.
- Parent task report commit `a87c05b45` is pushed to
  `origin/task/ARCH-077-BACKGROUND-002`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-077-BACKGROUND-002`;
  branch `task/ARCH-077-BACKGROUND-002`.
- Parent task worktree:
  `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-077-BACKGROUND-002`;
  branch `task/ARCH-077-BACKGROUND-002`.
- Canonical workspace root:
  `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Launcher synchronization evidence: both task branches were already current
  with their remote task branches and `origin/main`; recursive submodule sync
  and initialization passed; `database` remained pinned at
  `0a9edc7c0c30e0a405d89efec624bc9338b4ac17`.
- Shared checkouts and other task worktrees were not switched or mutated. No
  implementation submodule gitlink was staged. The parent task report is the
  only parent-worktree file changed in this attempt.

Task remains blocked pending architect reconciliation of the logging contract;
this report makes no architect acceptance decision.


## Architect Review — 18 November 2026 (Attempt 4: reconcile pre-production GraphQL diagnostics)

**Decision: Changes Requested; previous `FULL_GRAPHQL_RESPONSE_LOGGING_CONFLICT` resolved by a narrow, synthetic-data-only test-environment exception.** This review supersedes the conflicting diagnostic requirements in the Attempt 3 review above *only where specifically stated*; preserve all prior reviews and Attempt 4 Completion Report. The previously accepted cross-checkout replay limitation remains unchanged.

### Accepted Attempt 4 implementation — no repeat work

- Accept the source/test corrections for missing and malformed Shared keyring handling, error propagation with original causes, receipt failure classification, verified/failed consent outcome diagnostics, STOP/final-send gates and the quoted-STOP fixture. Preserve commit `6e26516`. The reported disposable PostgreSQL consent suite (2 tests), STOP suite (8 tests), ARCH-076 sender suite (12 tests), focused unit tests, and targeted ESLint/build are evidence for those corrections. These are architect source findings, **not final B002 acceptance**.
- The developer continues to accept the rare delayed A-after-B materialisation risk. Do not request new schema, history records, Redis state or queues to address it. Do not modify `docs/decisions/**/_index.md`.

### Binding logging reconciliation: full diagnostic data for controlled Shopify test checkouts

The developer needs to inspect what Shopify actually returned from the existing `AbandonedCheckoutsCount` and `AbandonedCheckouts` queries, including complete `customAttributes` and the **opaque encrypted** `moda_wa_consent_v1` value, alongside the original failure messages. The general Shared logging contract intentionally rejects full provider payloads, customer PII and long values. This review and the linked Shared/ARCH-077 documentation therefore authorise a **narrow exception for synthetic checkout/customer test data only in `test` or `development` deployment environments**. This is *not* permission to record genuine customers' personal data or to turn off generic Shared redaction across services. No new environment switch, opt-in option, provider request, log sink or logging framework is authorised. Render test can have `NODE_ENV=production`, so use the existing `resolveDeploymentEnvironmentName()` (`DEPLOYMENT_ENVIRONMENT_NAME` / `OTEL_DEPLOYMENT_ENVIRONMENT` precedence), **not `NODE_ENV` alone**, to determine the deployment group. Never emit raw-payload chunks when the group is `production`, unknown or anything other than `test`/`development`. The owner of the Shopify test store must use synthetic customer/phone/address data for these raw-payload diagnostics.

- In `src/services/abandoned-checkout-lookup.service.ts`, instrument the *existing* single GraphQL POST helper, not an extra fetch. Determine operation explicitly from the supplied named operation (`AbandonedCheckoutsCount` / `AbandonedCheckouts`); record start/completion, HTTP status, query bounds and safe shop/checkout correlation. Read the HTTP response **once** as text and parse that same text without changing error propagation, bounded candidate guards or normalisation. Preserve Shopify's actual JSON fields, missing/null distinctions and original `errors[]` in test-environment diagnostics. Do not log request headers or GraphQL authorization credentials.
- A nested `logger.info({response})` cannot satisfy this contract: Shared sanitises keys such as `phone`, `email`, `address`, caps strings at 4,096 and arrays at 50. For the approved **synthetic-data-only** exception, serialise the captured response text into deterministic, ordered string chunks of at most **1,024 Unicode code points per chunk**, log each chunk as a plain `responseChunk` **through the existing `lookupLogger`** with a common request/correlation ID, `operation`, `chunkIndex` (zero-based), `chunkCount`, HTTP status, and an explicit `syntheticTestData: true` marker. Keep chunks in order, never duplicate or omit; a chunk containing a private query credential may be modified by the Shared sanitiser, so flag `redactionApplied` rather than claim it was byte-for-byte preserved. This purpose-specific exception is for synthetic development/test data, not a general strategy for circumventing logger redaction. Do not alter Shared runtime code, its redactor, sinks, global field limits or production behaviour.
- Emit clear separate structured events for parsed count, detail node count, raw-attribute present/missing/duplicate status, receipt verification result and GRANT/REVOKE decision, recoverability decision, SQL mutation/rejection, STOP and final-send outcome. Do not present an unverified ciphertext as accepted consent. Preserve all original Shopify transport, HTTP, JSON parse and GraphQL `errors[].message`, `extensions` and paths via the existing original-error logger contract and typed exception cause chain. Log the precise original exception message when present. An ordinary valid lookup still performs at most one count query and one detail query; no new consent query.
- For **non-synthetic or production** data, use the existing structured field-level diagnostics and Shared redaction; no complete raw response, email/phone/address, signed receipt or private checkout URL is authorised. Do not log tokens, authorization headers, credential keyrings or AEAD plaintext in any environment. Retain the existing production policy; pre-launch removal of this synthetic-data-only exception can be a separate explicit decision.

### Tests and completion

- Test exact reconstruction of a synthetic Shopify count response and detail response from the **emitted Shared-logger records after sanitisation**, across more than one chunk. The fixture must cover a multi-node basket, synthetic name/phone/email/address, a full `v1.` receipt value, null/missing attributes, and an `errors[]` response; prove request credentials are absent. Assert that `production` and unknown environment names do not emit raw chunks, including when `NODE_ENV=production` but the deployment group is `test` (Render test case).
- Assert a response with a private query credential is visibly redacted and not misleadingly asserted to be raw-identical; do not assert arbitrary literal bytes survive existing Shared redaction. Test invalid-JSON original message, original GraphQL message/extensions and one-count/one-detail / early-exit behaviour. Use existing unit-test logger injection/mocks without bypassing Shared when checking emitted records.
- Rerun focused GraphQL lookup, receipt verifier, materialisation, STOP, consent PostgreSQL and ARCH-076 sender regressions plus lint/build/`git diff --check`; report exact counts and any failures. The passing Attempt 4 STOP and keyring work should be preserved, not redesigned.
- Return to `review` on completion; keep downstream SHOPIFY-006/SYSTEM-TEST-001 gated. No claim of live Shopify checkout propagation is made by these tests.

**Task metadata:** `status: ready`, `executor: null`, `claimed_at: null`, `attempt: 4`; the launcher may claim Attempt 5.
