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
claimed_at: 2026-11-18T03:09:53Z
attempt: 2
depends_on: [ARCH-077-BACKGROUND-001]
enables: [ARCH-077-SHOPIFY-006, ARCH-077-SYSTEM-TEST-001]
created: 2026-11-17
updated: 2026-11-18
---

# Gate Shopify recovery and final proactive sends using signed checkout consent

**Ready for Attempt 2 after architect resolution of the reported blocker (18 November 2026).** The previous blocked Completion Report is preserved below as historical evidence; the latest Architect Review is the binding rework contract. Follow the [ARCH-077 signed receipt v1 contract](../../../architecture/ARCH-077/checkout-attribute-consent-v1.md). This **replaces** Redis consent read/materialisation while preserving existing PostgreSQL `CustomerPhone` and final-SQL permission guards.

## Ownership and exact sequence

1. Keep existing authoritative Shopify abandoned-checkout lookup, merchant-configured maturity/visibility retries, payment/completion/cancellation guards and checkout identity before any consent decision. Determine `RECOVERABLE` independently of prior stored GRANT/REVOKE or whether an outreach record can be created.
2. Extract **one** `moda_wa_consent_v1` from `AbandonedCheckout.customAttributes {key value}` already read under B001. No additional provider call. Verify the exact v1 Shared AES-256-GCM authenticated receipt (`v1.` canonical envelope), rejecting incorrect version/shop/plan kind/binding/customer/locale, wrong AAD/tag/unknown key, malformed or duplicate attributes. Use the existing `MODA_ENCRYPTION_KEYS_JSON` Shared credential keyring and exact AAD/decoder/claims defined in `docs/architecture/ARCH-077/checkout-attribute-consent-v1.md`, **not** `SHOPIFY_CONSENT_RECEIPT_KEY_V1` or a duplicate HMAC/AES implementation, and the original authenticated checkout candidate token: `kind c` requires original authenticated checkout event `cart_token` matching signed base-cart SHA-256; `kind x` requires trusted checkout token matching signed checkout SHA-256. The GraphQL `AbandonedCheckout` object does **not** expose `cartToken`; don't invent it. If event tokens missing/ambiguous, fail closed; no Redis marker fallback.
3. Resolve the correct shop, verified Shopify customer and attributable recipient: valid customer phone, else billing, else shipping; a shipping recipient known unrelated is ineligible, and differing phone fields are not inherently ambiguous. Signed `customerId` must exactly match verified customer where present. Signed guest `-` still requires trusted token match and attributable recipient; never infer identity solely from phone/email or cart items. Preserve existing STOP/no-contact and canonical phone revision checks.
4. Only when checkout is **recoverable** and a verified explicit receipt exists, materialise `G`/`R` via existing `Customer`/`CustomerPhone` SQL transaction using `SHOPIFY_NATIVE`, `WHATSAPP_CHECKOUT_RECOVERY`, verified time and revision/decision sequence. A recoverable REVOKE must persist **before** B outreach is denied even if no `CheckoutRecovery` is created. A nonrecoverable/paid/completed checkout does not write consent; its signed receipt is ignored at materialisation time. Missing attribute means no *new* decision; reuse previously verified PostgreSQL GRANTED only under existing customer/recipient/STOP checks.
5. **Cart A / Cart B:** A first recoverable GRANT persists GRANTED and may send initial outreach; B later recoverable REVOKE persists REVOKED and blocks B outreach and A's future unsolicited follow-up. B paid normally => no SQL change; A's already delivered initial message and customer-initiated AI/human service replies remain valid if allowed under 24-hour WhatsApp/moderation/STOP. A subsequent independent recoverable GRANT can reauthorise new proactive sends absent STOP.
6. **Approved minimal idempotency, with explicit residual risk:** Preserve the existing per-checkout worker identity, BullMQ retry/idempotency, checkout/recovery-generation guards, SQL transaction/row-lock and consent revision/STOP safeguards. Before updating `CustomerPhone`, use already-loaded, durable recovery/checkout state **only where that state actually proves the same checkout's choice was processed**; if proved, return `ALREADY_MATERIALISED` without a new consent write. Do **not** assume a `CheckoutRecovery` row always exists (a recoverable REVOKE may produce no recovery), or treat an incrementing phone revision as a checkout identifier. Where the existing schema cannot prove prior application, perform the normal recoverable-only consent write using the existing transaction and current SQL guards. The architect explicitly accepts that an exceptionally late, first-time materialisation or replay of an older checkout could then overwrite a newer materialised decision; no absolute cross-checkout ordering/exactly-once promise is made. Do not introduce a checkout ledger, CustomerPhone columns, Woo evidence, Redis consent state, global lock, timestamp-based checkout sorting, or migration to close that accepted gap. A failure in the ordinary SQL/STOP/final-send invariants remains a genuine blocker.
7. For all future proactive outbound initial/retry/follow-up/multipart, retain the short current PostgreSQL final-send guard and STOP. Never check Redis consent or the old Shopify `defaultPhoneNumber.whatsAppMarketingConsent`; do not accidentally apply proactive rules to legitimate customer-initiated service replies or alter billing/ARCH-076 sender assignment.

## Typed outcomes

- `NOT_RECOVERABLE_TERMINAL`: no new SQL/outreach; `NO_EXPLICIT_CHOICE`: no new decision, current SQL only; `INVALID_OR_AMBIGUOUS_RECEIPT`: no new decision or proactive outreach relying on this evidence; `DEFER_CHECKOUT_BINDING`: no consent write/outreach if missing trusted event identity; `DEFER_IDENTITY_OR_RECIPIENT`: no SQL/outreach; `MATERIALISED_GRANTED`: one durable SQL write and normal admission; `MATERIALISED_REVOKED`: one durable SQL write, no new proactive outreach; `ALREADY_MATERIALISED`: SQL unchanged **only when existing durable evidence establishes prior application**; `BLOCKED_STOP`: preserve STOP; `MATERIALISATION_FAILURE`: no false success/partial materialisation. Reuse existing return shape, don't build a second state machine.

## Required integration tests and release blockers

- Disposable PostgreSQL with real current `CustomerPhone` constraints, unit tests for Shared-authenticated receipt verifier, key-ID rotation with old key retained, token/AAD binding, guest/new customer, tampering/copy/wrong tag, missing/duplicate attr, provider errors and identical/no-choice.
- Recoverable A GRANT -> one initial outreach; B pre-recoverability REVOKE -> SQL unchanged; B paid -> SQL unchanged; B recoverable -> SQL REVOKED even when B has no outreach; A unsent proactive follow-up denied; legitimate inbound A reply/AI-human response remains eligible under service window; independent STOP remains immediate.
- Test ordinary duplicate delivery, retries and worker crash after SQL commit, recording which cases existing durable checkout/recovery guards truly suppress. Do not assert exactly-once consent materialisation where no durable per-checkout checkpoint exists. Test sequential A GRANT then B REVOKE, B duplicate, existing SQL/STOP and final-send fences, and document the accepted possibility of exceptionally late first-time A after B. A failed transaction must not claim success; provider sends still use existing outreach idempotency. Do not reintroduce `MATERIALISATION_IDEMPOTENCY_BLOCKER` solely because strict cross-checkout ordering is unprovable under the unchanged schema.
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
