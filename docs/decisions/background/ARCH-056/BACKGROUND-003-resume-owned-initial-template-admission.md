---
id: ARCH-056-BACKGROUND-003
architecture_id: ARCH-056
title: Resume and fence the existing initial-template admission
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 40
executor: codex
claimed_at: 2026-11-04T02:06:06Z
attempt: 3
depends_on:
- ARCH-040-BACKGROUND-008
- ARCH-046-BACKGROUND-004
- ARCH-052-BACKGROUND-018
enables:
- ARCH-056-BACKGROUND-004
- ARCH-056-SYSTEM-TEST-001
created: '2026-11-03'
updated: 2026-11-04
---

# ARCH-056-BACKGROUND-003: Resume and fence the existing initial-template admission

## Architecture

Parent architecture: `ARCH-056`. Task touchpoint: the existing Background outbound initial-template admission, final-permit, cleanup and receipt boundary. Follow the parent architecture's common execution rules and the single-owner file map below.

## Objective

Make the existing outbound admission/delivery touchpoint safely resume an initial recovery template that has a durable pending message but no provider permit. Retain the same message and hard-limit UsageEvent, prove the exact reserved recovery credit again at the final permit, and preserve provider uncertainty after a permit. Make cleanup and receipt persistence safe when they race that continuation.

This is the supporting outbound contract for U2/C3. It does not repair the general conversation-turn consumer or claim all MSG-02/MSG-03 findings closed.

## Context

Optional prior evidence, if present, is `docs/architecture/reviews/background-database-20261103-212722-phase3/recovery-progress.md`. It is not an execution prerequisite; the source identities, decisions, and acceptance below are self-contained. Current implementation evidence is in `OutboundWhatsAppAdmissionService.sendTemplate`, `OutboundAdmissionReservationService.findExistingAdmission/reserve`, `OutboundMessageDeliveryService.sendPreparedTemplateInternal/markSent`, `OutboundProviderFailureService.failPrepared/afterProviderError`, and the Shopify/Woo final send fences.

`recovery-outreach:<attemptId>` is the hard-limit UsageEvent idempotency key. Shopify's provider key hashes the message ID; Woo's provider key hashes shop plus attempt. Neither provider key is the UsageEvent key. A permit is evidence that dispatch was admitted, not evidence of successful delivery. Durable `SENT`/`DELIVERED`/`READ` with an actual `sentAt`, correct ownership, and consistent lineage is the current successful-receipt contract.

## Scope

All paths below are relative to `moda-interact-background/`.

Modify only these production files:

- `src/services/outbound-whatsapp-admission.service.ts`
- `src/services/outbound-whatsapp-admission/outbound-whatsapp-admission.types.ts`
- `src/services/outbound-whatsapp-admission/outbound-admission-reservation.service.ts`
- `src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts`
- `src/services/outbound-whatsapp-admission/outbound-provider-failure.service.ts`
- `src/services/outbound-whatsapp-admission/failed-outreach-admission.ts`
- `src/services/recovery-conversation/outbound-send-fence.service.ts`
- `src/services/woocommerce-recovery/woo-guarded-initial-sender.service.ts`
- `src/services/woocommerce-recovery/woo-initial-send-fence.service.ts`
- `src/services/whatsapp.service.ts` — existing diagnostic projection/emission only; preserve request, provider, billing and retry behavior.

No new production file, migration, queue, schema field, general fence, billing policy service, or package script is required. Put additive admission types in the existing types file and bounded implementation helpers in their existing service owner. This task owns its unit and PostgreSQL tests; the terminal system task supplies additional proof, not implementation or a substitute test suite.

This task owns the following existing test files for contract/mock updates and focused assertions:

- `tests/unit/services/outbound-whatsapp-admission.service.test.ts`
- `tests/unit/services/outbound-whatsapp-admission/outbound-admission-reservation.service.test.ts`
- `tests/unit/services/outbound-whatsapp-admission/outbound-message-delivery.service.test.ts`
- `tests/unit/services/outbound-whatsapp-admission/outbound-provider-failure.service.test.ts`
- `tests/unit/services/outbound-whatsapp-admission/failed-outreach-admission.test.ts`
- `tests/unit/services/outbound-whatsapp-admission/outbound-admission.test-support.ts`
- `tests/unit/services/woocommerce-recovery/woo-guarded-initial-sender.service.test.ts`
- `tests/unit/services/woocommerce-recovery/woo-initial-send-fence.service.test.ts`
- `tests/unit/services/whatsapp.service.test.ts`

Create exactly these focused test modules and fixture file:

- `tests/unit/services/outbound-whatsapp-admission/initial-outreach-admission.test.ts`
- `tests/unit/services/recovery-conversation/initial-outreach-permit.test.ts`
- `tests/integration/initial-outreach-admission-resume.integration.test.ts`
- `tests/integration/initial-outreach-admission-races.integration.test.ts`
- `tests/integration/fixtures/initial-outreach-admission.fixture.ts`

Read-only production/test dependencies (not edit permission):

- `src/services/recovery-billing.service.ts`
- `src/services/recovery-billing/recovery-billing.types.ts`
- `src/services/recovery-conversation/recovery-conversation.sql.ts`
- `src/services/recovery-conversation/recovery-runtime-eligibility.service.ts`
- `src/services/recovery-delivery-compensation/lineage.ts`
- `src/services/recovery-delivery-compensation/reconcile.service.ts`
- `src/services/whatsapp-provider-status.service.ts`
- `src/services/conversation-moderation/moderation-assessment.service.ts`
- `src/services/conversation-moderation/moderation-failure-diagnostics.ts`
- `src/services/synchronous-recipient-failure.service.ts`
- `src/services/synchronous-recipient-failure-evidence.service.ts`
- `src/services/woocommerce-recovery/woo-recovery-outreach.service.ts`
- `src/services/woocommerce-recovery/woo-recovery-composition.ts`
- `database/prisma/schema.prisma`
- `tests/integration/woo-initial-send-fence.integration.test.ts`
- `tests/integration/woo-initial-send-fence-races.integration.test.ts`
- `tests/integration/general-outbound-stop-fence.integration.test.ts`
- `tests/integration/recovery-conversation.services.integration.test.ts`
- `tests/integration/arch055-follow-up-identity.integration.test.ts`

## Out of Scope

Covers the shared admission/resume/cleanup support required by U2/C3 and the corresponding initial-template subset of MSG-03. Selects the parent-first receipt correction, emitted failure diagnostics in these initial-path owners, and the existing Meta diagnostic projection corrections specified below. Defers the general AI turn consumer, broad MSG-02/MSG-03 completion semantics, O7 repeated fallback reads, schema/index tuning, provider-outcome guessing, and the blocked ARCH-028-BACKGROUND-013 financial uncertainty policy.

No edit to `conversation-turn-processor.service.ts`, no new technical-retry behavior for its unrelated general text/AGENT path, and no implicit activation of production Woo outbound. Existing schema, billing owner policy and sequence-two contracts remain owned elsewhere. The existing WhatsApp worker and its tests belong exclusively to BACKGROUND-001; this task does not edit them. No Shared implementation/version change, generic logger/redactor, new telemetry transport, provider parser, wire schema or per-call tracing protocol is authorized.

## Requirements

### Canonical read and resume rules

1. Validate shop, recovery, conversation, sequence-one `INITIAL` attempt, AUTOMATION sender, and the exact `recovery-outreach:<attemptId>` usage identity. Read the usage link and existing attempt link. If both exist they must identify the same message. Any MerchantConversationSendCommand associated with an AUTOMATION message is a lineage conflict, even if shop/attempt match. A tenant mismatch, deleted linked message, conflicting link, unsupported sender/sequence, malformed key, ambiguous ownership, or missing usage for an unlinked send is `held/lineage-conflict`; it is never `absent`.
2. `absent` is allowed only for a valid unsent eligible initial attempt with no outbound link, no sent/follow-up evidence, no canonical usage/message/permit evidence, and no conflicting legacy failed state. The billing owner independently proves absence of an existing credit reservation before fresh admission is permitted. An unlinked legacy `FAILED` attempt is not proof of absence.
3. `prepared` requires the exact owned message to be `PENDING`, `providerMessageId`, `sentAt`, `deliveredAt`, `readAt`, and `failedAt` all null, dispatch key/admitted-at/control-revision all null, canonical usage present with quantity one and normal initial-message source type, and an eligible unsent initial attempt. A partial permit (including control revision alone) is uncertainty, not an invitation to repair or resend. The message has no dispatch restriction-revision field; that field belongs to MerchantConversationSendCommand and must not be fabricated in SQL/projections.
4. A validated confirmed receipt wins over a misleading legacy attempt `FAILED` status; the caller still must settle its exact credit and satisfy the finalizer's transition guards. A `PENDING` message with any of the three dispatch fields set is `held/provider-outcome-unknown`. For a PENDING or otherwise inconsistent nonterminal message, a provider ID or any send/delivery/read/failure timestamp without a consistent confirmed durable receipt also holds; no such PENDING row is sendable or eligible for pre-permit cleanup. This nonterminal hold rule does not override a validated FAILED message: classify its authoritative rejection or pre-permit refusal under rule 5.
5. A durable failed receipt is returned as `failed` only when its pre-permit state or authoritative provider rejection is provable. Keep the special 131026 identity/compensation path. A failed message with inconsistent or insufficient rejection evidence holds.
6. `resumeInitialTemplate` rereads this scoped classification, checks the requested message ID, reconstructs only the existing normal recovery admission, and executes current execution, consent, STOP, recipient, current template registration, exact content, moderation, and final SQL checks. It never calls `reserve`, creates a message, inserts another hard-limit UsageEvent, creates a new attempt, or charges a new credit. Its existing quota reservation is not counted a second time as a fresh admission. A racing state change returns existing duplicate/suppression or throws a real dependency error; the caller rereads canonical state before deciding progress.

### Final permit and lock contract

Use the existing final fence and existing schema. Do not call either new BACKGROUND-002 billing method from inside this transaction.

For initial automated Shopify templates, the transaction order is **Shop → Conversation → initial attempt FOR UPDATE → prepared message FOR UPDATE → exact UsageReservation FOR SHARE → permit CAS**. Existing Woo retains its intervening Recovery/consent locks and their current order, but moves its credit SHARE read after its message UPDATE lock. There must be no reservation lock followed by a message lock. Do not request a parent or attempt lock after locking the message.

The agreed BACKGROUND-002 settlement and selected 131026 compensation order is **owned Shop FOR KEY SHARE → message FOR UPDATE → existing credit-owner counter operation → reservation CAS/ledger write**. Shop KEY SHARE is acquired before the message because UsageEvent insertion otherwise requests it implicitly through the immediate Shop FK. BACKGROUND-002 must never request a new Shop, Conversation, or attempt row lock after that message lock; it revalidates any pre-lock identity pointer under these locks. Do not add an explicit reservation UPDATE lock before a credit owner's counter lock. BACKGROUND-003 continues to use Shop FOR UPDATE; do not weaken the STOP/permit fence to work around this dependency.

At final admission, recheck all existing tenant, platform, control revision, consent, STOP, suppression, active shop, current policy, template, recipient, recovery lifecycle, and current prepared-content conditions. For the initial branch additionally require:

- The attempt is sequence one, trigger `INITIAL`, belongs to this recovery, has the same recipient, is `PENDING` or `CAPACITY_BLOCKED`, and has no sent timestamp, outbound link, or follow-up due date.
- The exact usage key is `recovery-outreach:<attemptId>`, owned by this shop, quantity one, metric `OUTBOUND_AUTOMATED_MESSAGE`, normal initial-message source type, and `sourceId` equal to this message ID.
- The exact reserved credit has the same shop, quantity one, `status = RESERVED`, no committed/compensated outcome, and has not expired at the post-lock permit time. Non-paid sources use `createRecoveryIdempotencyKey(shopId, usageKey)`. Paid included sources must match `paid-included:<owningPeriodId>:<logicalKey>` and the owning period must be current under the existing policy. The bounded source-candidate proof includes the logical key and all paid-period candidates; more than one candidate is a lineage conflict, including when a historical row is released. Validate the existing mutually consistent owner FKs and owner shop/counter kind; never guess a source from current free/paid policy or merely accept a matching suffix. Preserve Woo's currently accepted source restriction rather than silently enabling paid Woo.
- Verify applicable current source owner facts using existing owner fields and compatible read semantics, including promotional grant, selected campaign, and selection eligibility; no new counter/grant/lot lock is taken after the reservation. A cancelled/expired or otherwise ineligible owner fails closed. Reservation SHARE alone does not serialize a revocation writer that updates only a grant/campaign/selection. This is a fresh source/owner proof in the existing permit transaction, not a claim that every external cancellation writer is serialized. A broader cancellation protocol remains outside scope.
- Message predicates include ID, conversation, OUTBOUND direction, AUTOMATION sender, `status = PENDING`, dispatch key/admitted-at/control-revision **all** null, provider ID and sentAt/deliveredAt/readAt/failedAt all null, and content exactly equal to the currently prepared/moderated content. Include these predicates in the final conditional update, not only an earlier read. A zero-row update grants no permit.

All SQL is parameterized, schema-qualified, and local to PostgreSQL. No provider/Redis/SDK I/O occurs while locks are held. Provider HTTP starts only after successful permit commit. Preserve existing deterministic Shopify and Woo key formats and the independent Woo prior-permit check.

### Cleanup, refusal, and receipt semantics

`failPrepared` becomes an idempotent guarded operation. Its message failure and exact hard-limit usage removal form one transaction. Transition to failed only under `PENDING` plus dispatch key/admitted-at/control-revision all null, no provider ID or sentAt/deliveredAt/readAt/failedAt, and verified ownership; delete only the matching outbound UsageEvent after that conditional transition succeeds. A losing CAS rereads state and does nothing destructive. The permitted legacy residue is `FAILED` plus those three null dispatch fields, null provider ID/sentAt/deliveredAt/readAt/failedAt, and proven matching usage: finish only its cleanup. Never remove usage or overwrite status for a permitted, confirmed, or uncertain message.

When initial cleanup would erase the sole durable message lineage, preserve the original attempt/message association in the same transaction before deleting usage. For initial cleanup/linking, first validate the owned Shop identity, then lock Shop FOR UPDATE → initial attempt FOR UPDATE → message FOR UPDATE and validate the canonical association again. This serializes the new attempt/message write order against the selected status writer's Shop KEY SHARE → message → attempt path. Generic cleanup has no attempt mutation and does not acquire new initial-flow locks. Under an eligible unsent attempt CAS, set the exact outbound link, `status = FAILED`, `failureCode = PRE_PROVIDER_REFUSED` and actual closedAt together with the known pre-permit message failure. A pre-permit refusal remains a consumed, explicitly blocked initial attempt in this task; it is not silently turned into a new message on replay. Existing 131026 behavior remains delegated to its accepted owner.

For a definitive non-131026 initial provider rejection, use that same Shop UPDATE → attempt → message order and preserve the immutable attempt-to-failed-message association before the existing usage cleanup, in one guarded transaction. Require the same shop, recovery, sequence-one attempt, canonical key, recipient, and no conflicting prior link/sent state; retain permit and failure evidence. If lineage cannot be proved, retain evidence and surface a conflict rather than deleting its sole link. Extend the existing failed-outreach helper to recognize that exact linked failed identity. Do not implement a new generic non-131026 credit compensator or reopen the unresolved ARCH-028-BACKGROUND-013 admission policy.

For the scoped initial-template path only, technical preparation/moderation failures preserve a resumable pending message and usage. Explicit moderation denial remains a refusal. On that path a moderation result `retry` must not become boolean false, a business suppression, or destructive cleanup: throw exported `OutboundPreparationRetryError` (defined by the delivery owner, re-exported by the facade) with its bounded assessment ID/retry-at metadata. Propagate the initial scope explicitly into this decision; retain existing unrelated general text/AGENT consumer behavior and do not silently make its boolean moderation helper throw the new exception. Unexpected dependency exceptions propagate unchanged. If initial cleanup/reconciliation also fails, preserve both exceptions with an `AggregateError`; do not replace the original failure with only the cleanup error.

Separate the provider request `try/catch` from receipt persistence. Only an exception from provider HTTP enters `afterProviderError`. If HTTP succeeded and local persistence fails, retain the permit and propagate the original persistence error; do not reinterpret it as a provider rejection. The caller's durable-state classification owns the uncertainty decision.

Change private `markSent` to accept the already verified conversation ID as well as message/provider IDs. Its transaction acquires **Conversation before message**, validates the message's conversation/direction/sender and admitted state at the write, and atomically writes the receipt and `lastMessageAt`. Use one actual receipt time consistently. Do not first update message and then reread/lock Conversation. Pass the correct conversation ID from both template and text call sites. This selected correction is required for the newly competing resume fence; it does not claim the old lock-order audit lead was already reproduced. Test a competing final fence and receipt transaction with controlled lock barriers. Preserve existing provider-status/131026 reconciliation authority on conflicting state rather than overwriting it.

### Initial-path diagnostic ownership

Apply the parent architecture's mandatory revision-2 logging acceptance contract to each selected failure path. Preserve the original thrown object/cause; emitted fields are the actual safe source wording after explicit security redaction and bounded truncation. Keep reasonCode separate from source text. Include actual supplied Prisma code/clientVersion and only the allowed safe model/constraint/field metadata. An Error is not a substitute for explicit cause/component diagnostics: the inspected Shared serializer keeps only name/message. Use the actual locked installed Shared package for tests and record its version/resolution; do not certify the installed consumer with sibling Shared source.

Stage and correlation state are local to each invocation, never mutable singleton fields. Carry only already available shop/recovery/attempt/conversation/message identity. Actual source request IDs remain available in their source event; do not invent tracing IDs or change provider inputs to create correlation. Source diagnostics may have downstream contextual outcomes, but raw provider responses are not recopied through the pipeline.

| Selected boundary | Stable event and owner | Required emitted evidence |
|---|---|---|
| Meta source response/transport error | Existing WhatsAppService `whatsapp.meta.send.failed` | Preserve original safe response message/code/status/request ID/details, or existing sourceError/causeChain. No fabricated providerError on an internal error. Only the diagnostic corrections below change this owner. |
| Moderation dependency retry | Existing assessment `conversation.moderation.dependency_unavailable` (read-only source contract) | Preserve bounded exceptionMessage in canonical test/development environment and stage/code/request-attempted/status/assessment identity in production. Downstream typed retry carries assessmentId/retryAt; it never reconstructs raw SDK text/cause from the protected wrapper. |
| Initial preparation exception or known invalid input | Existing delivery `outbound.template.preparation.failed`, stage `preparation` | Original safe diagnostic plus known initial IDs. A real local validation error retains its safe source message even when converted to refusal; no fabricated upstream fields. |
| Initial moderation call throws outside a typed retry | Existing delivery `outbound.template.moderation.failed`, stage `moderation` | Actual permitted diagnostic and known IDs. Honor existing moderation privacy projections instead of bypassing them with a raw SDK object. |
| Shopify initial final-permit exception | Existing recovery fence, new `recovery.initial_outreach.sql_permit.failed` | Actual safe persistence error/code and known initial IDs; initial context only. Other actors' existing policy/log behavior stays unchanged. |
| Woo initial final-permit exception | Existing `woocommerce.recovery.initial.sql_permit.failed` | Actual safe persistence diagnostic; never new Error(PERSISTENCE_FAILURE). Existing lifetime-policy unavailable warnings retain their real missing/invalid reason and, when parsing actually threw, the safe validation error before conversion. Missing data has no fabricated source exception. |
| Initial HTTP request fails versus HTTP succeeds then receipt persistence fails | Delivery, new `outbound.initial.send.failed` | Distinct stage `provider_http` or `receipt_persistence`, actual safe exception/classification and known IDs. Preserve the source adapter event. A local DB error is not labeled provider_response or passed to the provider-rejection handler. |
| Initial operation and cleanup/reconciliation both fail | Aggregating delivery/failure catch, new `outbound.initial.cleanup.failed` | Independently bounded fixed-role fields: preparationError or moderationError with cleanupError, or sendError with reconciliationError, as applicable. Both actual messages appear before throwing the preserved aggregate; aggregate-only logging is insufficient. |
| Woo guarded sender contextual failure | Existing `woocommerce.recovery.initial.permit.failed` | Existing IDs and safe actual diagnostic/classification; preserve original throw identity and remove raw phone/token/URL spans rather than dropping all useful wording. |

Do not emit final sent/applied success inside a transaction that may still roll back. Keep provider_http, receipt_persistence, retry and final failure distinct. Logging failure must not affect the permit, receipt, cleanup, provider call count, suppression or thrown value. Expected suppression/held outcomes without an exception use their real reason and safe context; they do not acquire an invented error.

Replace the two contradictory existing assertions: Woo SQL-permit logging must no longer expect a replacement PERSISTENCE_FAILURE Error, and guarded-sender logging must no longer require a phone number in errorMessage. Verify safe source wording, actual supplied code and redaction flags together with unchanged application exception identity.

### Bounded Meta diagnostic projection corrections

In `WhatsAppService`'s existing diagnostic projection/emission only, apply `safeProviderIdentifier` to nested `providerError.fbtrace_id` as well as top-level `providerRequestId`. Emit the nested value only if its actual source value passes the existing validator; invalid text is omitted, not forwarded or guessed. In `safeProviderDetails`' array branch, combine each child's returned redactionApplied/truncated flags with the parent flags, including strings, primitives and nested arrays. Preserve existing transformed values and item/depth/text limits.

Use the existing helpers. Preserve HTTP requests, timeouts, provider input/output, exception classification, billing, dispatch and retry behavior. Do not create a new parser or generic logging module. Stack emission is not promised, and protected moderation SDK data must not be reattached downstream.


The selected BG002 provider-status entry also acquires owned Shop FOR KEY SHARE before message CAS, attempt, or usage operations; it rechecks any routing pointer after locking. BG002 owns that locking-only status/compensation correction. This task does not edit those services or change their delivery/accounting policy.

## Work Items

- [x] Extend the existing canonical lookup and add the scoped initial evidence/result types, preserving legacy facade compatibility.
- [x] Implement same-message initial-template resume and carry original source/attempt context through both provider-specific delivery paths.
- [x] Add the exact initial credit/content/attempt proof to the existing Shopify fence and reorder Woo message-before-credit locking.
- [x] Make initial cleanup and known rejection lineage atomic, conditional and parent-ordered; preserve 131026 ownership and uncertainty.
- [x] Scope the new technical moderation retry exception to initial templates; distinguish HTTP errors from receipt persistence failures.
- [x] Make receipt persistence Conversation-before-message with per-call ownership predicates and one atomic receipt/timestamp unit.
- [x] Add focused unit/PostgreSQL proofs and run every listed preservation gate.
- [x] Report the final additive contract to BACKGROUND-004; keep deferred general-consumer and billing-policy findings explicit.

- [x] Implement the declared initial-path diagnostic owners/stages and safe original-message/code fields, preserving existing source Meta/moderation diagnostics.
- [x] Emit both fixed-role original failures before selected cleanup/reconciliation aggregation; preserve exception identity and logging failure isolation.
- [x] Correct only the existing Meta diagnostic projection's nested trace validation and child-array transformation flags.
- [x] Replace synthetic-persistence and phone-retention expectations and verify actual installed Shared sink records, redaction, source metadata, correlation and business outcomes.

## Interfaces / Contracts

Retain `findExistingAdmission(idempotencyKey)`, `reserve`, `sendTemplate`, `sendPreparedText`, and `failPrepared` compatibility for existing general/AGENT callers. Extend the canonical projection to carry permit fields and ownership evidence; do not introduce a second unrelated lookup algorithm.

Export the following additive types from the existing types file and facade:

```ts
type InitialOutreachAdmissionScope = Readonly<{
  shopId: string;
  recoveryId: string;
  outreachAttemptId: string;
}>;

type InitialOutreachMessageEvidence = Readonly<{
  id: string;
  conversationId: string;
  status: MessageStatus;
  sentAt: Date | null;
  deliveredAt: Date | null;
  readAt: Date | null;
  failedAt: Date | null;
  providerMessageId: string | null;
  providerDispatchKey: string | null;
  providerDispatchAdmittedAt: Date | null;
  providerDispatchControlRevision: number | null;
  providerFailureCode: string | null;
}>;

type InitialOutreachAdmissionLookup =
  | { kind: "absent" }
  | { kind: "prepared"; message: InitialOutreachMessageEvidence }
  | { kind: "confirmed"; message: InitialOutreachMessageEvidence & { sentAt: Date } }
  | { kind: "failed"; message: InitialOutreachMessageEvidence;
      disposition: "pre-permit-refused" | "provider-rejected" | "recipient-unreachable" }
  | { kind: "held"; reason: "provider-outcome-unknown" | "lineage-conflict" };
```

Add these methods to `OutboundWhatsAppAdmissionService`, with the read implementation in the existing reservation owner and delivery delegated to the existing delivery owner:

```ts
inspectInitialOutreachAdmission(
  scope: InitialOutreachAdmissionScope,
): Promise<InitialOutreachAdmissionLookup>;

resumeInitialTemplate(input: InitialOutreachAdmissionScope & {
  messageId: string;
  recoveryCreditSourceKey: string;
  template: Omit<SendTemplateInput, "to"> & {
    to: string;
    expectedControlRevision?: number;
  };
}): Promise<OutboundAdmissionResult>;
```

Add optional `initialOutreach: InitialOutreachAdmissionScope` context to the existing initial-template call path, and propagate the existing `recoveryCreditSourceKey` into delivery and the final fence. The context is never provider payload. Existing unscoped APIs retain their contract; every selected initial-recovery caller is migrated by BACKGROUND-004. The scoped resume path always requires this context, an exact message ID, and a credit source key.

Add `initialOutreach` context to `DispatchInput` for the initial AUTOMATION/TEMPLATE branch, containing `outreachAttemptId`, `idempotencyKey`, `recoveryCreditSourceKey`, and `expectedContent`. It is invalid on HUMAN, AGENT, TEXT, and sequence-two calls. Do not reinterpret those existing branches as initial recovery.

The Woo guarded sender exposes `inspectInitialOutreachAdmission(scope)` by delegation. Its existing `sendInitial` handles a proven prepared message by delivering that same message through `sendPreparedWooInitialTemplate`; it never calls the generic Shopify final fence. Its interface declaration/consumer is updated by BACKGROUND-004, after this implementation is accepted. Keep its existing `findExistingAdmission` method compatible meanwhile.

## Dependencies

- `ARCH-040-BACKGROUND-008` — Complete. Preserve the accepted recovery final-dispatch window, control and configured follow-up fence.
- `ARCH-046-BACKGROUND-004` — Complete. Extend the accepted Woo initial consent/STOP final fence and retain explicit Woo dispatch routing.
- `ARCH-052-BACKGROUND-018` — Complete. Resume the accepted approved neutral initial-template contract without reintroducing enrichment dependence.

This task is independently implementable against those accepted source contracts and the existing schema. It has no runtime or metadata dependency on ARCH-056-BACKGROUND-002; final credit proof uses existing durable fields. The coordinated counterpart lock contract is specified above. Component race tests can use a real PostgreSQL transaction following that fixed counterpart contract without importing an unimplemented new billing service; the terminal system task proves the actual accepted BG002/BG003 combination. Do not claim the unmodified snapshot already has the selected counterpart locking corrections.

## Enables

- `ARCH-056-BACKGROUND-004` consumes scoped lookup/resume and carries the exact initial source into new and resumed sends.
- `ARCH-056-SYSTEM-TEST-001` executes the actual accepted combined Background commit and verifies worker/SQL/provider behavior.

## Acceptance Criteria

- [ ] A proven prepared initial message resumes with exactly its original message, usage, attempt and credit; two workers cannot obtain two permits/provider calls.
- [ ] Missing, cross-shop, conflicting or partial-permit evidence fails closed, including controlRevision-only, any receipt/failure timestamp on PENDING, and any AUTOMATION merchant-command association.
- [ ] The final fence proves the current exact source and prepared content under the agreed locks; Woo still uses its explicit fence and production gate.
- [ ] Cleanup cannot alter a permitted/confirmed/uncertain message or delete its usage, and any initial failed-message cleanup retains durable same-attempt lineage.
- [ ] Initial technical moderation failure remains retryable; an HTTP-success/receipt-DB-failure preserves the permit and original DB error.
- [ ] Receipt persistence is parent-first and atomic; the selected deterministic races show no introduced message/reservation or message/Conversation cycle.
- [ ] Existing HUMAN, AGENT, general text, sequence-two, 131026, consent/STOP and follow-up behavior remains within its accepted contract.
- [ ] Every listed focused unit, PostgreSQL, build, lint and whitespace command passes with actual prerequisites; skipped setup is reported as blocked, not passed.

- [ ] Every selected unexpected preparation, final-permit, provider-call and receipt-persistence failure has its declared event with safe source wording, truthful stage and available identity; a reason code does not replace the original message.
- [ ] Both cleanup/reconciliation component messages survive actual Shared serialization, while both original objects remain retained in the thrown aggregate.
- [ ] Woo persistence output contains the real supplied DB diagnostic/code; guarded-sender output retains a harmless source marker and excludes injected phone/token/URL spans.
- [ ] Existing Meta source fields remain visible; invalid nested trace text is omitted and any retained array child's redaction/truncation is reflected in the outer flags. Provider/request/billing behavior is unchanged.
- [ ] Moderation keeps its permitted test/development preview and production-safe diagnostics. Actual installed Shared capture-sink tests prove these records, no fabricated provider fields, and unchanged business results when the sink throws.

## Validation

Unit tests cover scoped lookup classifications, exact ownership rejection, no generic API break, initial-template technical moderation retry versus denial, and the provider-error/receipt-error separation. PostgreSQL tests use real transactions and deterministic barriers for:

1. Two workers resuming the same prepared message: one message, one hard-limit event, one durable permit, and at most one provider call.
2. Missing/foreign/conflicting usage, attempt link, credit source, owner, period, partial permit, and PENDING with deliveredAt/readAt/failedAt: zero provider calls and no invented replacement rows.
3. Cleanup versus final permit: a permit winner retains its message status, usage, and credit; a cleanup winner cannot subsequently be admitted.
4. Exact-source reservation release versus final permit, including the agreed message-before-credit lock order; already changed grant/campaign/selection facts fail closed. Define the actual transaction boundary rather than relying on sleeps. Do not claim an overlapping grant-only revocation writer is serialized by a reservation lock.
5. A contract-conforming real PostgreSQL settlement/131026 contender (owned Shop KEY SHARE before message, then counter/reservation) competing with the actual initial fence: no message/reservation or implicit Shop-FK lock cycle. The billing task tests its actual owners independently; the terminal task runs both accepted services together.
6. Receipt persistence competing with a new fence: parent-first ordering, no message/Conversation cycle, and atomic receipt plus timestamp.
7. Known rejected initial message remains discoverable after usage cleanup; 131026 retains its original accepted compensation/idempotency behavior.
8. Woo uses its explicit final fence for both new and resumed prepared messages. Preserve production outbound disabled behavior and existing Woo order/consent/STOP checks. HUMAN, AGENT, terminal general messages, and sequence two retain their existing contracts.

Use the exact task-owned new modules and existing regression modules listed in Scope above. Keep each newly created source/test module within 300 lines by separating scenario fixtures from assertions. Assertions must inspect database rows and provider call counts, not only mocked return values or SQL text.

### Emitted-record logging matrix

In the owned unit tests use the actual installed `@modainteract/moda-interact-shared/logging` createLogger with a capture sink, or test-only factory interception delegating to it. Record package version/resolution and serialize/parse captured records. Assert event, level, service/environment, stage, known IDs and an independently recognizable harmless source message. A mock logger call or thrown-error assertion alone does not prove emission. Inject sensitive spans separately and verify their removal and honest flags; assert original throw identity/approved typed result, no fabricated provider fields, commit timing and sink-failure isolation. Do not replace or upgrade Shared to make the test pass.

| Owned test module | Required logging proof |
|---|---|
| `tests/unit/services/outbound-whatsapp-admission/outbound-message-delivery.service.test.ts` | Initial preparation exception, typed moderation retry, thrown moderation failure, provider error, HTTP-success/receipt-DB-error, and paired reconciliation error. Distinct source markers/stages; no wrong provider-error handler, retry HTTP or changed exception identity. |
| `tests/unit/services/recovery-conversation/initial-outreach-permit.test.ts` | Real Shared output for an injected initial Prisma failure with actual code/clientVersion and safe IDs; domain suppression/zero-row CAS has no invented originating error. |
| `tests/unit/services/woocommerce-recovery/woo-initial-send-fence.service.test.ts` | Replace synthetic PERSISTENCE_FAILURE expectation with actual safe message/code; verify original thrown object and invalid-policy parser diagnostic before typed suppression. |
| `tests/unit/services/woocommerce-recovery/woo-guarded-initial-sender.service.test.ts` | Replace raw-phone retention assertion. A source message with harmless marker plus phone/token/URL preserves the marker but removes sensitive spans; correct flags and original thrown object remain. |
| `tests/unit/services/outbound-whatsapp-admission/initial-outreach-admission.test.ts` | Preserve source-event ownership and typed moderation assessment correlation. Existing source diagnostics remain bounded; retry does not expose a protected SDK object/cause or claim a completed send. |
| `tests/unit/services/whatsapp.service.test.ts` | Actual Shared Meta response message/code/status/request ID/safe details; valid/invalid nested fbtrace_id; arrays and nested arrays with transformed primitive children; sourceError/causeChain on transport failure; no invented providerError without a response; throwing sink preserves request/error behavior. |

The moderation source files are read-only dependencies. Verify its existing safe preview contract using controlled diagnostics/fixtures; no moderation privacy-policy edit or broad AI-consumer fix is authorized. The actual provider source test owns response detail proof, so downstream tests do not duplicate a provider parser or raw payload logs.

Run from the task checkout of `moda-interact-background/`, after its declared PostgreSQL/Redis prerequisites are ready. Commands are standalone and do not depend on this drafting manifest:

```sh
npx --no-install vitest run tests/unit/services/outbound-whatsapp-admission.service.test.ts tests/unit/services/outbound-whatsapp-admission tests/unit/services/recovery-conversation/initial-outreach-permit.test.ts tests/unit/services/woocommerce-recovery/woo-guarded-initial-sender.service.test.ts tests/unit/services/woocommerce-recovery/woo-initial-send-fence.service.test.ts tests/unit/services/whatsapp.service.test.ts
```

```sh
npm run test:integration -- tests/integration/initial-outreach-admission-resume.integration.test.ts tests/integration/initial-outreach-admission-races.integration.test.ts tests/integration/woo-initial-send-fence.integration.test.ts tests/integration/woo-initial-send-fence-races.integration.test.ts tests/integration/general-outbound-stop-fence.integration.test.ts tests/integration/recovery-conversation.services.integration.test.ts tests/integration/arch055-follow-up-identity.integration.test.ts
```

```sh
npm run build
```

```sh
npx --no-install eslint src/services/outbound-whatsapp-admission.service.ts src/services/outbound-whatsapp-admission/outbound-whatsapp-admission.types.ts src/services/outbound-whatsapp-admission/outbound-admission-reservation.service.ts src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts src/services/outbound-whatsapp-admission/outbound-provider-failure.service.ts src/services/outbound-whatsapp-admission/failed-outreach-admission.ts src/services/recovery-conversation/outbound-send-fence.service.ts src/services/woocommerce-recovery/woo-guarded-initial-sender.service.ts src/services/woocommerce-recovery/woo-initial-send-fence.service.ts tests/unit/services/outbound-whatsapp-admission.service.test.ts tests/unit/services/outbound-whatsapp-admission/outbound-admission-reservation.service.test.ts tests/unit/services/outbound-whatsapp-admission/outbound-message-delivery.service.test.ts tests/unit/services/outbound-whatsapp-admission/outbound-provider-failure.service.test.ts tests/unit/services/outbound-whatsapp-admission/failed-outreach-admission.test.ts tests/unit/services/outbound-whatsapp-admission/outbound-admission.test-support.ts tests/unit/services/woocommerce-recovery/woo-guarded-initial-sender.service.test.ts tests/unit/services/woocommerce-recovery/woo-initial-send-fence.service.test.ts tests/unit/services/outbound-whatsapp-admission/initial-outreach-admission.test.ts tests/unit/services/recovery-conversation/initial-outreach-permit.test.ts tests/integration/initial-outreach-admission-resume.integration.test.ts tests/integration/initial-outreach-admission-races.integration.test.ts tests/integration/fixtures/initial-outreach-admission.fixture.ts src/services/whatsapp.service.ts tests/unit/services/whatsapp.service.test.ts
```

```sh
git diff --check
```

## Implementation Notes

Use the parent architecture's common worktree, error/logging, ownership and completion-evidence requirements. Add no new production modules. New test modules target at most 200 physical lines and must not exceed 300; split fixtures/assertions only within the explicitly declared files. Preserve original error objects in application propagation and verify safe emitted diagnostic projections through the installed Shared logger. Keep provider/customer content out of diagnostics and obey the bounded source privacy contracts.

The receipt-order change is a selected supporting architecture correction for the new competing continuation path, not a claim that the previous audit lead had already been reproduced. Source-owner cancellation eligibility is a fresh proof with the precise limitations stated above; do not expand it to a general cancellation protocol.

Stop and report a blocking contract conflict if safe final admission requires changing an unowned writer's lock order, inventing source association, admitting an ambiguous source, changing Woo activation, creating persistence infrastructure, or changing general conversation-turn semantics. Retain uncertain evidence. On passing the scoped gates, report concrete evidence, publish normal task mirrors, set status to review, return to the architect and stop; do not execute enabled tasks.

## Completion Report

### Current review status

Changes Requested — Attempt 2, 2026-11-04. Architect review found and reproduced a sequence-two cleanup regression in `failPrepared`; see the appended review. Attempt 2 is preserved, the claim is cleared, and the task returns to Ready. BACKGROUND-004 and SYSTEM-TEST-001 remain gated. The implementation is published at `a68fe273bde3503605e64fb412143ac9dc1c563d`; this architect overlay is published on the matching parent task branch under the developer’s explicit commit/push instruction.

### Historical Attempt 1 status

Blocked during Attempt 1. Implementation draft `32b80bf` is published on the Background task branch. The required PostgreSQL preservation gate has a contradictory read-only assertion. The task is not submitted for review.

### Files Changed and Work Completed

- Existing admission facade, types and reservation owner expose scoped initial evidence and same-message resume, with normal usage identity and ownership checks.
- Existing Shopify and Woo permit owners check the original attempt, prepared message and exact credit. Woo retains its explicit fence. The credit read follows the prepared-message lock.
- Existing delivery and failure owners distinguish moderation retry, provider HTTP and receipt persistence. Receipt writes acquire Conversation first. Guarded pre-permit cleanup and known initial rejection keep the attempt link in the transaction that removes usage.
- Existing Meta diagnostic projection validates trace identifiers and propagates nested array transformation flags. Initial failure owners emit bounded source evidence through the installed Shared logger.
- Added the five scoped test/fixture modules declared by the task. Updated only owned regression tests and source files. No schema, gitlink, queue contract or other task record changed.

### Validation Results

- The declared focused Vitest selection passed 135 tests across 11 files. The declared ESLint selection, production build and `git diff --check` passed.
- Installed Shared version was 3.0.0. The logging import resolved through its `./dist/logging/index.js` export. Capture-sink tests cover stage and source evidence, provider versus receipt failure, paired errors, protected retry identity, and Meta nested flags.
- The declared integration selection ran on disposable PostgreSQL/Redis and reported 31 passed and five failed across seven files. New real PostgreSQL cases passed for Woo same-message resume, inconsistent pending receipts, refusal lineage, cleanup versus permit, released credit and the competing receipt transaction. General STOP and follow-up preservation passed.
- Four HUMAN-send failures in `recovery-conversation.services.integration.test.ts` reproduced using an untouched archive of `afac7c3766d92fb14beff669232c1b01c2ed0be0` and the prepared schema. They involve provider admission before takeover, definitive rejection settlement, UNKNOWN resolution, and rate denial.
- The fifth failure is `tests/integration/woo-initial-send-fence-races.integration.test.ts:209–216`. This read-only required test explicitly requires `Error("PERSISTENCE_FAILURE")` and rejects the actual injected source message. The task's logging requirement explicitly prohibits that synthetic error and requires safe source wording. Production emits the bounded source diagnostic and preserves the original throw. The test remains untouched.
- The database check constraint rejects a control-revision-only permit at write time. The defensive read classification is covered in unit tests. No constraint was disabled for integration testing.

### Worktree and synchronization evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-056-BACKGROUND-003`, `task/ARCH-056-BACKGROUND-003`, origin/main incorporated, remote task fast-forward not needed. Durable claim `6c4d06f5cea3b67617863c21b33d836625424e33`.
- Implementation: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-056-BACKGROUND-003`, `task/ARCH-056-BACKGROUND-003`, origin/main already current at `afac7c3766d92fb14beff669232c1b01c2ed0be0`, remote task fast-forward not needed.
- Recursive sync and initialization passed. Database gitlink `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`. Shared checkouts and other task worktrees were not used for implementation.

### Unresolved Issues and Architect Handoff

Authorize an update to the read-only Woo race-test logging assertion or assign that correction to its owner. Reconcile the four independently reproduced baseline failures with the mandatory preservation gate. The implementation remains a draft. Complete the remaining matrix evidence, including Shopify resume/provider concurrency, historical and paid candidate ambiguity, promotional owner invalidation, and the settlement contender's ledger insertion. Do not infer full coverage from the passing focused cases. BACKGROUND-004 and terminal system testing were not started.

### Attempt 2 — Submitted for architect review

- Updated only the authorized Woo race-test diagnostic assertion. It checks the supplied source marker, final-permit stage, scoped IDs and safe projection flags. The original exception identity, rollback and retry checks remain in place.
- The Shopify resume test uses the public admission facade and real SQL fence with controlled consent and moderation prerequisites. A provider barrier holds the first worker after permit commit. The second worker observes the permit and returns duplicate. The test checks the original message, one usage event, one credit reservation and one provider call.
- Added held legacy-attempt evidence, ambiguous historical paid credit and invalidated promotional selection cases. The paid and promotional cases suppress dispatch and preserve the credit records. The settlement race acquires Shop KEY SHARE, then the message and funding rows, and commits a recovery usage event. The losing fence does not create a permit.
- Added installed Shared capture-sink tests for unexpected preparation and thrown moderation errors. The records retain independent source markers and scoped IDs, redact the injected phone, and preserve the thrown objects without a provider call or usage deletion. Shared resolved to version 3.0.0 through `./dist/logging/index.js`.

#### Validation

- The exact focused Vitest command in Validation exited 0 with 137 passed in 11 files. The declared ESLint command, lint reruns for the final edited test files, `npm run build` and `git diff --check` exited 0.
- The seven-file `npm run test:integration -- …` command in Validation exited 1 with 36 passed and 4 failed across 7 files. The isolated baseline command `npm run test:integration -- tests/integration/recovery-conversation.services.integration.test.ts` on untouched Background `afac7c3766d92fb14beff669232c1b01c2ed0be0` exited 1 with 7 passed and 4 failed. Both used the prepared Database schema at `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`, the same installed dependencies and the repository's disposable PostgreSQL and Redis runner. The runner completed teardown.
- The following tests in `recovery-conversation.services.integration.test.ts` had the same signature on baseline and candidate, `AssertionError: expected 'suppressed' to be 'admitted' // Object.is equality`.
  - `provider admission commits before later takeover, then UNKNOWN is reconciliation-only`
  - `verified definitive provider rejection settles one message and never permits retry`
  - `UNKNOWN with verified definitive failure resolves to FAILED without a second send`
  - `rate denial stops evaluation before final durable eligibility/billing admission`
- All task-owned cases and the other required regression cases passed. The four matching failures meet the narrow baseline exception in Architect Review. The HUMAN test module and runtime remain untouched. No further task was started.

#### Git and worktree evidence

- Canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-056-BACKGROUND-003`. Attempt 2 claim `8c4103867eafc05132cd45edccb4c826009d3334`.
- Background worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-056-BACKGROUND-003`. Implementation commit `a68fe273bde3503605e64fb412143ac9dc1c563d` pushed to `origin/task/ARCH-056-BACKGROUND-003`.
- Both worktrees use `task/ARCH-056-BACKGROUND-003`. Both were already current with `origin/main` at preparation, with no remote task fast-forward needed. Recursive submodule initialization passed. Only the task file is staged for the parent review commit on the same remote branch. No gitlink, shared checkout or other task worktree changed. Neither repository was merged to main.

### Attempt 3 — Submitted for architect review

- `failPrepared` resolves the canonical usage key to the stored attempt and verifies the recovery, sender, usage source and existing message association before selecting cleanup. Proven sequence-one INITIAL attempts retain their locked, atomic lineage path. Valid sequence-two follow-ups retain guarded generic cleanup. Unresolved or conflicting recovery identities keep their evidence.
- PostgreSQL regressions exercise the public facade with a genuine sequence-two attempt. An unpermitted message becomes FAILED and only its exact outbound usage is removed. An existing permit, inconsistent receipt evidence and an unresolvable attempt key each preserve the message and usage. The original initial-outreach usage and sequence-two attempt row remain intact in every case.
- BACKGROUND-004 handoff. Use `inspectInitialOutreachAdmission(scope)` and `resumeInitialTemplate` with the original message and exact credit source. Pass `initialOutreach` and `recoveryCreditSourceKey` on fresh Shopify initial delivery. Keep Woo on its explicit guarded sender. General AI consumer behavior, broader completion semantics and ARCH-028-BACKGROUND-013 uncertainty policy remain deferred. No downstream task was started.

#### Validation

- The exact focused Vitest selection in Validation passed 137 tests across 11 files. The declared ESLint command, production build and whitespace check exited 0.
- The exact seven-file PostgreSQL/Redis selection in Validation exited 1 with 40 passed and four failed. The unchanged HUMAN integration module on untouched current Background main `eb6d7a6` exited 1 with seven passed and four failed using the same installed dependencies and Database gitlink `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`. Both used the disposable runner and completed teardown. An earlier baseline run also hit an expired Prisma transaction during the concurrent claim case. The repeat baseline completed that case successfully and reproduced only the four authorized failures.
- The four failure names listed under Attempt 2 matched on current main and candidate, all with `AssertionError: expected 'suppressed' to be 'admitted' // Object.is equality`. The authorized exception is unchanged. All task-owned tests and the remaining regression cases passed.

#### Git and worktree evidence

- The canonical workspace is `/Users/kwadwoadomafriyie/project/moda-interact-workspace`. The isolated parent is `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-056-BACKGROUND-003`. The isolated Background worktree is `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-056-BACKGROUND-003`.
- Both worktrees use `task/ARCH-056-BACKGROUND-003`. The launcher incorporated current `origin/main` in both worktrees, with no remote task fast-forward needed. Recursive sync and initialization passed at the recorded Database gitlink. The durable Attempt 3 claim was `8e8f79cae7b8066c70bcaf0c3af46ae24892def2`.
- Implementation commit `d343450d2b7537db316f607cc418a0e2b42c5098` was pushed on the Background task branch. The parent review submission uses the same task branch and changes only this task file. Shared checkouts, other task worktrees and gitlinks were left intact.

## Architect Review

This section belongs only to moda_architect. Definition authoring is not implementation acceptance.

### Review Status

Changes Requested — Attempt 1, 2026-11-04.

### Review Notes

Reviewed the Attempt 1 blocker report and published implementation draft `32b80bf`. The following narrow scope and validation clarifications supersede the conflicting read-only instruction. Implementation acceptance remains pending.

1. Edit only the contradictory persistence diagnostic assertion in `tests/integration/woo-initial-send-fence-races.integration.test.ts` and any strictly necessary local diagnostic assertion imports. Verify the supplied harmless source marker and actual safe diagnostic metadata where present. Keep original exception identity, rollback, no-send, contention and persistence assertions intact. Do not require a fabricated `PERSISTENCE_FAILURE` error message. The remainder of that integration module stays read-only.
2. Retain and run `tests/integration/recovery-conversation.services.integration.test.ts`. The four HUMAN failures independently reproduced on untouched `afac7c3766d92fb14beff669232c1b01c2ed0be0` with prepared schema are the comparison baseline. Record exact test names and failure signatures for baseline and candidate with matching prerequisites, and the actual command results. The preservation gate can pass only when there are no new or materially changed failures and every task-owned case and other required regression passes. Report a nonzero integration exit as such. Keep HUMAN tests and runtime untouched. A mismatched or unreproduced failure remains a validation blocker.
3. Finish the outstanding matrix in the Attempt 1 report, including Shopify resume/provider concurrency, historical and paid ambiguity, promotional ownership invalidation, and the settlement contender ledger insertion. Retain the real PostgreSQL barriers, row and provider call assertions, emitted-record logging checks, scoped lint/build and full declared integration selection.

The blocker is resolved at the definition level. Release the Attempt 1 claim and return the same task to Ready for normal launcher preparation of Attempt 2. Preserve the published draft and the historical Attempt 1 report. Enabled work remains gated.

### Reviewed Files

Attempt 1 report, task-owned implementation draft summary and the conflicting Woo race-test diagnostic contract.

### Validation Reviewed

Attempt 1 reported validation and isolated baseline comparison. Fresh required validation is pending Attempt 2.

### Architecture Conformance

Pending review against the parent architecture, task allowlist, interface contracts, repository boundaries and failure requirements.

### Follow-up

Pending implementation review; no enabled task may be started by this task's executor.

## Architect Review — Changes Requested (Attempt 2, 2026-11-04)

### Finding — P2: preserve sequence-two pre-permit cleanup

`src/services/outbound-whatsapp-admission/outbound-provider-failure.service.ts:18–20` treats every `recovery-outreach:<attemptId>` usage key as an initial attempt and returns immediately if `lockInitial` fails. The existing sequence-two follow-up sender uses the same key format (`recovery-outreach-follow-up-processor.service.ts:177`), while `lockInitial` requires sequence one and trigger INITIAL. Therefore ordinary pre-provider suppression/moderation refusal of a sequence-two message silently skips cleanup. The message remains PENDING and its hard-limit UsageEvent remains present. A later replay sees duplicate/PENDING and cannot resume the unchanged follow-up flow, and the leaked usage consumes its message limit. This violates the explicit sequence-two preservation contract; it is not one of the four approved HUMAN baseline exceptions.

Independently reproduced on disposable PostgreSQL with canonical migrations: create a valid new sequence-two NO_RESPONSE_FOLLOW_UP attempt, a PENDING AUTOMATION message with no permit/receipt, and its exact normal outbound UsageEvent; call the public facade's `failPrepared(messageId)`. Expected `{status: FAILED, usage: 0}`; observed `{status: PENDING, usage: 1}`. No production constraint was disabled. The temporary review test was removed from the implementation worktree afterward; its reproducer is retained at `/tmp/arch056-review-sequence-two.integration.test.ts` and output at `/tmp/arch056-bg003-review-sequence-two-retry.log` for local follow-up.

### Required correction

Resolve the owned attempt identity before selecting initial-only cleanup. Apply the new initial association/lock behavior only to proven sequence-one INITIAL attempts; preserve the existing guarded generic cleanup for valid sequence-two follow-ups, without allowing malformed/conflicting initial lineage to fall through unsafely. Add a durable regression in the already-owned test modules for a valid sequence-two pre-permit refusal, asserting FAILED message and removal of only its exact hard-limit usage, plus preservation of permitted/uncertain follow-up evidence. Rerun the declared preservation gates and reconcile Work Items/Completion Report before resubmission. Do not modify the read-only follow-up processor or broaden the HUMAN baseline exception.

### Validation independently performed

- Reviewed the full `afac7c3..a68fe27` task implementation diff and the Attempt 2 correction. The task uses the canonical dedicated parent and implementation worktrees; both were clean at review start. Remote implementation equals `a68fe273bde3503605e64fb412143ac9dc1c563d`, and remote parent report equals `5d1b3730ecb5b6af3ccd8615249d41eecccaa0d3`.
- Exact required unit selection: 137 passed across 11 files.
- Exact required seven-file PostgreSQL/Redis selection: 36 passed, four failed. All four failure names and `expected 'suppressed' to be 'admitted'` signatures match the previously authorized HUMAN baseline exception. This remains a nonzero exit, not a completely passing integration suite. The unchanged baseline archive was not rerun during this review.
- Production build, all changed TypeScript-file ESLint, and `git diff --check afac7c3..HEAD` passed with Node 24.19.0.
- The additional valid sequence-two database regression fails with the concrete state mismatch above. An earlier draft fixture attempted to mutate immutable attempt identity and was rejected by the database; the successful reproduction creates a new valid attempt instead. An intervening runner failed before tests on disposable Redis readiness; the retry reached the assertion and reproduced the defect.
- No permanent implementation source or test changes were made by the reviewer. No implementation commit/push, merge, main update, or downstream promotion was performed.

### Lifecycle

`status: ready`, `executor: null`, `claimed_at: null`, `attempt: 2`. The next normal launcher claim creates Attempt 3. Architect acceptance remains withheld. This review overlay is applied only to the matching parent task branch and published under the developer’s explicit commit/push instruction. No implementation branch or main branch is changed by this publication.
