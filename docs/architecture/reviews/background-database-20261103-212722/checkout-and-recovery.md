# Updated snapshot: checkout and recovery impact review

## Scope and evidence

Compared `moda-interact-workspace(20261102-112817).zip` with `moda-interact-workspace(20261103-212722).zip`. All source evidence below refers to the updated archive unless stated otherwise.

This is a read-only static re-review. Application source, configuration and schema are unchanged by this review; the delivery adds review/evidence documents. No tests, live provider requests, database or Redis commands were run. Test files were inspected; their presence or assertions are not evidence that they passed. Code references below are to the **new** snapshot; `BG/` means `moda-interact-background/` relative to its workspace root. Runtime incidents, SQL statement counts, deployed schema state and throughput remain unmeasured.

I re-traced current entrypoints and collaborators rather than using matching checksums as proof of continued relevance. `BG/src/entrypoints/recovery.ts:44–48` constructs the current Woo runtime and pending candidate/capacity workers; `BG/src/entrypoints/shopify-event.ts:21–22` uses the same Woo runtime. `BG/src/services/checkout-recovery.service.ts:60–99,180–205` wires the Shopify materializer and capacity processor into the changed initiation service. The focus is checkout capture, maturity, initiation, offer selection/fallback, initial dispatch, confirmed-send repair, order correlation, capacity repair and expiry. Shared messaging internals are referenced where necessary to establish the fallback's real database identity and final send guards; wider findings appear in the messaging appendix.

## Executive result

**C3 is partially mitigated, not resolved.** Merchants configured with offer mode `NONE`, and selected classified enrichment failures, now use an independently approved neutral initial template. The general Shopify retry gap remains: a required-state failure after creating a `DETECTED` recovery still causes a worker retry that skips that existing recovery. The new fallback explicitly returns a retry result, making that unresolved boundary particularly visible.

**Woo production outbound remains disabled by the same test-only gate.** Optional offer admission tokens now permit neutral fallback dispatch within an enabled test runtime, but no production enabling mechanism was added to the normal composition. Confirmed-send reconciliation remains reachable before the gate.

**One newly introduced concrete defect:** fallback looks up the wrong durable identity. It searches `ConversationMessage.providerDispatchKey` with a `UsageEvent.idempotencyKey`. Normal Shopify and Woo final send fences write different dispatch keys, so this new preflight cannot find their real permits. Existing downstream idempotent reservation and final fences still protect normal sends; this finding does not establish duplicate provider delivery.

The earlier C1, C2, C4 and C5 concerns and O1–O6 candidates remain relevant. The new fallback also creates a narrowly identifiable duplicate-read opportunity on the `NONE` branch, while avoiding the much larger optional offer-enrichment path. Both effects should be described separately; there is no measured net performance result.

## Disposition matrix

| Prior item | Disposition | Current evidence and implication |
|---|---|---|
| C1: Shopify checkout lease expiry / non-atomic release | **Still applies** | `pending-recovery-candidate/checkout-order-guard.service.ts:8–10,26–52` still uses a 10-second unrenewed lease and GET then DEL. `checkout-recovery/recovery-materialization.service.ts:64–170` still holds it over provider lookup and initiation. Changed initiation still prepares a template (`260–264`), can validate an offer with a 15-second timeout (`335–340`) and sends (`350–359`). The no-offer branch avoids optional enrichment but does not make these network/DB sections bounded below ten seconds. |
| C2: snapshot refresh can lag its activity watermark | **Still applies** | `checkout-recovery/checkout-event-orchestrator.service.ts:83–105,226–259` advances activity under a short lock, ignores update count, performs the remote lookup outside that lock, then updates the basket without activity/source-version CAS. A late earlier response can overwrite a later basket. New fallback consumes saved `lineItems`/URL (`initial-no-offer-fallback.service.ts:114–123,192–200`); it adds no snapshot version fence. |
| C3: partial initial recovery is skipped on generic retry | **Mitigated for optional enrichment; still applies to required-state and partial-finalization failures** | New `automated-recovery-template.service.ts:374–392,403–405,420–425` offers safe neutral fallback for specified failures. But initiation inserts recovery at `195` and creates the attempt at `250–255` before fallible preparation. Fallback retry at `initial-no-offer-fallback.service.ts:166–171,231–245` becomes an exception at `automated-recovery-template.service.ts:256–257`. Worker re-entry remains limited to two suppression markers (`pending-recovery-candidate.worker.ts:157–162,237–243`); materializer skips existing active recoveries (`recovery-materialization.service.ts:98–110`). |
| C4: capacity repair first-page starvation | **Still applies** | `recovery-capacity-resume.service.ts:47–81` always selects the first ordered distinct shops with a fixed take; no persisted/rotating cursor was added. `workers/recovery-capacity-resume.worker.ts:92–102` likewise selects the first blocked recovery page. `domain/recovery-capacity-resume.ts:17–24` places the last recovery ID in the trigger name but not in a query cursor. Permanently blocked early shops can exclude later shops from this repair sweep. Other billing/checkout wakeups are separate opportunities, not proof of sweep fairness. |
| C5: Shopify completion history can report stale fromStatus | **Still applies** | `checkout-recovery/order-recovery-correlation.service.ts:90–141` reads a status, updates any active status, then inserts history using the earlier read. `recovery-outreach-finalization.service.ts:90–95` still transitions DETECTED to MESSAGE_SENT separately. Capacity resume invokes initiation after leaving its lock (`recovery-capacity-resume-processor.service.ts:161–250`), so checkout Redis locking cannot be assumed to serialize every writer; C1 is another gap. Completion remains terminal-safe; historical fromStatus can be inaccurate. Woo uses exact observed-status CAS and retries on conflict (`woo-order-reconciliation.service.ts:300–330`). |
| O1: broad offer-policy reads on scheduling-only branches | **Still applies** | Pending service `93–94,138–139,270–271` and Woo checkout activity `413–414` still resolve the complete policy for `recoveryDelayMinutes`. `recovery-policy.service.ts:25–33` reads settings and override including fixed discount/catalogue; `54–55` can read Shop again. Preserve override expiry and platform semantics when narrowing. |
| O2: one-statement interactive transaction | **Still applies** | `checkout-event-orchestrator.service.ts:246–259` still wraps only one `updateMany`; it does not make the earlier activity write/provider read atomic. Correct C2, then use a directly guarded atomic write unless genuine multi-statement work is required. |
| O3: latest-recovery helper loads all columns | **Still applies** | `checkout-recovery/latest-recovery.ts:3–7` has no select. Materializer `98–110` uses identity/status/generation, yet receives basket/restoration JSON and other scalar columns. Narrow by purpose; other consumers use more fields. It returns one latest row; this is a projection concern, not an unbounded row scan claim. |
| O4: overlapping Woo preflight reads | **Still applies; full outbound remains gated** | Composition `woo-recovery-composition.ts:86–88` reads Shop platform before services. Admission `woo-recovery-admission.service.ts:261–271` separately reads Shop, installation and subscription-with-Shop. Order reconciliation `woo-order-reconciliation.service.ts:221–235,300–309` reads recovery/history then rereads recovery in its transition transaction. Final guards remain necessary. The template adapter also reads conversation language at `woo-recovery-outreach.adapters.ts:83–92`, while initial template preparation forces conversation language to null (`automated-recovery-template.service.ts:558`); that existing redundant read affects only enabled template-selection paths. |
| O5: duplicate generation index | **Still applies in declared schema; deployed impact needs measurement** | `database/prisma/schema.prisma:390–391` retains both unique and ordinary indexes for `(shopId, checkoutToken, generation)`. The original migration still creates both (`20260916150000_arch016_recovery_policy_discounts_outreach_generations/migration.sql:184–187`). New ARCH055 migrations concern REST attempt lifecycle, human follow-up claim identity and upload intake identity; none removes this index. Keep the uniqueness constraint. Actual deployed catalog and index/write cost are unverified. |
| O6: expiry per-row transactions | **Still applies; optimization candidate** | `checkout-recovery-expiry.service.ts:31–80` retains page size 100 and one transaction per candidate, with exact-status/activity CAS, history and attempt cancellation. A fully successful selected page is 301 delegate calls plus 100 transaction callbacks. Preserve all three effects; do not remove history or CAS simply to reduce counts. |
| Woo gate caveat | **Still applies** | `woo-recovery-outreach.service.ts:499–500` requires `NODE_ENV === "test" && enableTestOutbound() === true`. Normal composition `woo-recovery-composition.ts:71–74` supplies no enable callback. `enqueueInitial:306` and `processInitial:376` return disabled before offer selection/new admission. Confirmed message branches `269–304,331–375` run before those gates. |
| Diagnostic caveat | **Scope changed; original Woo issues still apply** | Initial agent now logs the original failure (`initial-outreach-offer.agent.ts:200–203,229–233`); selection adds original error logging (`initial-outreach-offer-selection.service.ts:169–190`); fallback logs its original required-state error (`initial-no-offer-fallback.service.ts:231–245`). However Woo SQL-permit catch still logs `new Error("PERSISTENCE_FAILURE")` instead of the caught error (`woo-initial-send-fence.service.ts:272–284`). Admission catch still reports only errorType at `woo-recovery-admission.service.ts:233–239`. Original errors are rethrown and may be logged upstream; these local events remain less diagnostic. |

## What the new fallback changes

### It reduces the dependency surface for a neutral first message

For initial outreach with policy `NONE`, `automated-recovery-template.service.ts:374–375` routes directly to fallback after its initial recovery/lifetime reads. It does not construct the offer agent context or invoke the agent/current-discount revalidator on that branch. This removes optional prompt/price/discount/model dependencies from a neutral message, and is a useful architectural simplification.

Classified AI/model-invocation or retryable MCP failures receive a similar fallback: graph `initial-outreach-offer.graph.ts:109–113` recognizes model invocation failure; selection `initial-outreach-offer-selection.service.ts:29–47,169–190` preserves and classifies known operational errors; the facade `automated-recovery-template.service.ts:269–305,383–393` limits which failure results qualify. Caller cancellation, invalid input, identity/configuration failures and required current-state uncertainty must remain distinct. For example `current-outreach-offer-revalidation.service.ts:323–339` now distinguishes caller cancellation, owned deadline and second-fence availability. The facade tests explicitly reject `SOURCE_FENCE_F2_READ_FAILED` as optional (`automated-recovery-template.service.test.ts:584–599`); do not blindly treat every retryable reason as permission to send fallback.

Fallback rereads the recovery/attempt, requires active correct tenant/platform, DETECTED recovery and an unsent initial sequence-one attempt, validates saved checkout items/URL and current lifetime, then delegates to the existing approved-template preparer (`initial-no-offer-fallback.service.ts:112–229`). It supplies no discount/product offer and no product image. The shared preparer chooses a TEXT binding when no product-image request is supplied and retains sender/registration/binding checks. The metadata contains `{kind:"NO_OFFER"}` through the existing `templateSendFields` adapter.

The removed mandatory `admissionToken` branches are therefore purposeful: an independently prepared neutral message has no current-offer claim to authorize. Shopify initiation `335–359` and Woo `431–454` continue validating a token when one exists. Neither change removes billing, consent/STOP, moderation, approved-template or final SQL send checks. Shopify still goes through `OutboundMessageDeliveryService.fenceProviderSend` (`outbound-message-delivery.service.ts:383–443`), including current consent at `415–431` and the recovery fence. Woo still uses its distinct guarded sender and initial SQL permit. The changed `expectedInboundVersion` argument in shared delivery applies to prepared-text/current-turn paths, not this initial template caller.

### It does not solve partial-initialization retry ownership

Concrete new branch:

1. Shopify maturity inserts a DETECTED recovery, then persists sequence one (`recovery-initiation.service.ts:195,250–255`).
2. The neutral fallback encounters a required DB/config error, returns `RETRY/REQUIRED_STATE_UNAVAILABLE` and the facade throws `INITIAL_FALLBACK_REQUIRED_STATE_UNAVAILABLE` (`initial-no-offer-fallback.service.ts:231–245`; facade `256–257`).
3. The worker records the failure, removes the candidate lookup indexes even on failure, then rethrows (`pending-recovery-candidate.worker.ts:169–203`).
4. BullMQ retries, but the error is neither supported suppression marker. Materialization sees the DETECTED row and returns `no-op-existing` (`98–110`), without re-entering initiation.

Even before fallback, the facade's first lifetime read returns ordinary `unavailable("CHECKOUT_UNAVAILABLE")` for missing/invalid persisted policy (`automated-recovery-template.service.ts:331–345`); initiation `265` returns the DETECTED recovery. The two lifetime reads consequently have different retry signals, and neither establishes autonomous repair in this worker.

Capacity repair remains limited to `RECOVERY_CAPACITY_EXHAUSTED` and suppression/checkout-triggered re-entry has its own predicates. The new classifier's `RETRY_EXISTING_ATTEMPT` and `RECONCILE_EXISTING_SEND` values (`initial-outreach-fallback-selection.ts:29–32`) are not a general durable repair implementation: the production facade invokes that classifier only with `OPTIONAL_ENRICHMENT_FAILURE` (`automated-recovery-template.service.ts:239–243`).

Recommended narrow correction: use the existing recovery/attempt/message identities to decide on retry whether to continue an unsent initial attempt, reconcile an already-confirmed send, wait for an uncertain outcome, or stop for a true terminal/mandatory denial. Preserve original sequence/usage keys. Do not add a second recovery, resend uncertain provider outcomes, or assume a generic queue retry alone provides this behavior.

## New static defect: fallback checks the wrong persisted dispatch key

`initial-no-offer-fallback.service.ts:151–153` queries:

```ts
conversationMessage.findFirst({
  where: { providerDispatchKey: `recovery-outreach:${attempt.id}` },
  select: { id: true },
})
```

In the actual send path:

- `recovery-initiation.service.ts:353` supplies `recovery-outreach:<attempt>` as **usage idempotency key**.
- `outbound-admission-reservation.service.ts:53–65` resolves this by `UsageEvent.idempotencyKey` then reads the message by `sourceId`. Its reservation duplicate check uses the same identity (`82–89`).
- Shopify final recovery fence stores `arch040-auto-<sha256(messageId)>` in `ConversationMessage.providerDispatchKey` (`recovery-conversation/outbound-send-fence.service.ts:232–234,274–284`).
- Woo final fence stores `arch046-woo-initial-<hash(shop,attempt)>` (`woo-initial-send-fence.service.ts:248–266`).
- Schema already separately constrains both domains: `ConversationMessage.providerDispatchKey` is unique (`schema.prisma:693`); `UsageEvent.idempotencyKey` is unique (`1602`). No new index is required to use the correct existing lookup.

The alternate linked-message branch is also unreachable for a non-null ID: fallback rejects any `attempt.outboundMessageId` at `138–141`, before checking it at `145–149`. A normal unfinalized attempt has no link yet, so the wrong-key query is exactly where the guard matters.

**Confirmed consequence:** the new early guard can return “prepare fallback” even when an ordinary durable message already represents the attempt's provider outcome. It cannot deliver its advertised early uncertainty detection against real persisted key formats. Later reservation/final fences still enforce duplicate suppression with intact canonical data; no duplicate-delivery incident is claimed.

The new unit test named “reconciles an existing durable provider dispatch” (`initial-no-offer-fallback.service.test.ts:115–124`) mocks `findFirst` to return a row for this incorrect query and asserts only RETRY, not any reconciliation. Conversely the new PostgreSQL integration test explicitly expects the real Shopify key prefix `arch040-auto-` (`arch052-shopify-initial-no-offer-dispatch.integration.test.ts:159–166`), but defines only one successful initiation. Together these test sources expose the missing integration case, not evidence that the guard works; neither was executed in this reassessment.

**Smallest direction:** reuse the established attempt-to-usage-to-message lookup (including its failed-recipient handling) and handle confirmed, pending and failed durable outcomes before new template preparation. A confirmed message needs finalization, not another preparation or blanket “uncertain” classification. Use a real persisted receipt/key in the test, then inject a failure between provider confirmation and each finalization stage.

This also reinforces C3's existing partial-finalization issue: the support-notice transaction can commit the attempt as WAITING_FOR_RESPONSE (`recovery-initial-outreach-support-notice.service.ts:189–212`) before the separate recovery MESSAGE_SENT update (`recovery-outreach-finalization.service.ts:88–99`). A retry must be able to repair that partial state before invoking preparation, which expects an unsent attempt. This ordering predated fallback and should remain part of C3, not be mislabeled a wholly new regression.

## Database-call counts and new read candidate

Counts below mean application Prisma delegate/raw-query invocations along the named branch. They are **not SQL statements**, physical scans, network round trips or timings: relation reads can expand into multiple SQL statements. Transaction begin/commit, Redis, logs, provider calls and background configuration polling are excluded. Nested collaborator work is included only when explicitly stated.

### New narrowly bounded fallback counts

| Named branch and boundary | Calls | Evidence / exclusions |
|---|---:|---|
| `InitialNoOfferFallbackService.prepare`: invalid recovery or attempt after initial parallel load | 2 | Recovery + attempt (`113–141`). |
| Same method: valid unsent recovery/attempt, matching result from its dispatch lookup, then RETRY | 3 | Adds one `conversationMessage.findFirst` (`151–157`); currently wrong key. Linked-message query cannot run because the prior guard rejects a link. |
| Same method: valid saved checkout and lifetime, proceeds to delegated sender/template preparation | 4 | Adds persisted lifetime `findUnique` (`168`; lifetime reader `47–51`). Excludes sender-resolution and preparer internals. |
| `AutomatedRecoveryTemplateService.prepare`, INITIAL + policy NONE, valid URL/lifetime, through fallback's pre-preparer checks | 6 | Outer recovery + lifetime (`308,334`) plus the four above. No transaction in this bounded section. Excludes sender/config/preparer, billing and dispatch. |
| Full fallback result `TEMPLATE_UNAPPROVED` | previous subtotal + 1 history write | `initial-no-offer-fallback.service.ts:205–217`, plus whatever read calls the delegated preparer actually executed. Do not call this a fixed total for the complete method. |
| `WooRecoveryOutreachService.enqueueInitial` direct call, valid Woo recovery, no previous attempt, normal default-disabled runtime | 3 | Recovery read, locked recovery reread and initial attempt read (`272,277–278`); returns at `306` before policy/template/billing/send. Does not include orchestrator/admission work before calling this method. |

**O7 — optimization candidate:** on the NONE branch, the outer facade and fallback each read the same recovery and the persisted lifetime policy. The branch has no offer-enrichment interval to justify those two extra reads. Route that branch directly into the validated fallback or share an operation-scoped read at the appropriate boundary, preserving all fallback identity/eligibility checks. Do not apply the same shortcut automatically after model/MCP work: fresh state after a long external call can be a necessary correctness check. No cross-operation caching or new service layer is needed for this candidate.

The new NONE path avoids `InitialOutreachOfferSelectionService.resolve` altogether. That resolver would build offer context before the agent (`154–159`), again after it (`192–197`) and enter current-source revalidation (`198–204`). A context build contains four direct parallel delegate calls (`initial-outreach-agent-context.service.ts:168–184`) plus policy resolution and optional price reconciliation (`218–229`). These are deliberately not collapsed into a single universal SQL total; offers, source fences, pricing and provider branches vary.

### Earlier selected branch counts revalidated against current collaborators

`+1 FIXED` below means policy mode FIXED with a non-null selected discount causes the extra platform lookup in `recovery-policy.service.ts:54–55`.

| Named successful/early-return branch | Delegate/raw calls | Transaction callbacks |
|---|---:|---:|
| Shopify eligible checkout-created candidate scheduling | 3 (+1 FIXED) | 0 |
| Shopify checkout-updated matching delayed candidate, newer activity, ordinary no-enrichment branch | 3 (+1 FIXED) | 0 |
| Shopify matching stale candidate, no context enrichment | 1 | 0 |
| Shopify checkout-updated, no candidate and no durable recovery, schedules candidate | 5 (+1 FIXED) | 0 |
| Shopify cart absent/stale candidate, no enrichment | 1 | 0 |
| Shopify cart newer delayed candidate | 3 (+1 FIXED) | 0 |
| Shopify order with neither checkout nor cart correlation | 0 | 0 |
| Shopify order absent/inactive shop, or active shop cancelling a pending candidate | 1 | 0 |
| Shopify order with no candidate, absent or terminal latest recovery | 2 | 1 |
| Shopify order completes an active recovery and inserts history | 4 | 1 |
| Shopify matured candidate, existing active recovery and no suppression-retry entry | 4 | 0 |
| Woo new checkout, ordinary scheduling, no durable recovery or observed order; includes orchestrator platform assertion | 5 (+1 FIXED) | 0 |
| Woo stale/duplicate active recovery at watermark early return; includes platform assertion | 2 | 0 |
| Woo order transition path, absent recovery; includes platform assertion | 3 | 1 |
| Woo order existing terminal recovery with no conflicting recorded order | 4 | 1 |
| Woo order successful status/history/attempt-cancellation transition | 7 | 1 |
| Capacity repair selecting S shops, each eligibility read attempted | 1 + S | 0 |
| Expiry selected page of 100 rows, all CAS transitions succeed | 301 | 100 |

Supporting current boundaries: `pending-recovery-candidate.service.ts:114–139,251–284`; `shop-execution-eligibility.service.ts:37–55,107–120`; `checkout-event-orchestrator.service.ts:111–185`; `pending-recovery-candidate/candidate-activity.service.ts` early stale/deferred paths; `recovery-materialization.service.ts:50–110`; `woo-checkout-activity.service.ts:149–175,235–243`; `woo-checkout-activity.adapters.ts:24–39,111–138`; `woo-recovery-composition.ts:86–88`; `woo-order-reconciliation.service.ts:221–235,300–349`; capacity/expiry refs above. These are branch budgets, not “every webhook costs N” claims. The 20K/min reference remains ingress workload, not materialized recoveries or outbound messages.

## Tests inspected and remaining evidence

Inspected new/changed bodies and relevant current regressions, without executing them:

- `tests/unit/services/recovery-template-integration/initial-no-offer-fallback.service.test.ts:58–151`: neutral template inputs; wrong tenant/terminal/invalid attempt blocks; mocked existing dispatch; unapproved-template audit; original error log plus RETRY.
- `tests/integration/arch052-shopify-initial-no-offer-dispatch.integration.test.ts:19–21,139–192`: gated disposable PostgreSQL test, one successful neutral dispatch/credit finalization and a consent-denied case. Provider/model-related side effects are mocked by fixture. It does not run the actual candidate worker retry sequence or inject post-insert/finalization failure.
- `tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts:558–605,655–705`: direct-service finalization replay, duplicate pending/missing admission, mocked token-free fallback dispatch and stale offer token rejection. Directly calling initiation again is not the same as worker re-entry through materialization.
- `tests/unit/services/recovery-template-integration/automated-recovery-template.service.test.ts:540–599` and subsequent identity/promotion cases: explicit allowed versus rejected failure classification. The F2 required-state rejection is deliberate in these tests.
- `tests/unit/services/recovery-offers/current-outreach-offer-revalidation.service.test.ts:143–183`: fence change, caller cancellation and service deadline remain distinct; later tests cover F3 source/policy changes.
- Existing checkout guard/materialization/capacity repair tests and Woo worker fault/admission race tests were revisited for scope; they still do not establish Shopify GET/DEL atomicity, generic post-insert worker convergence, reversed provider refresh coherence or fair global repair pagination.
- `tests/integration/arch048-woo-initial-outreach.integration.test.ts` contains explicit default-off production coverage (`571` onward) alongside enabled-test send/replay/resumption cases. Treat send-path tests as test-enabled capability evidence, not production reachability proof.

Prioritized reproduction/measurement requirements:

1. Run the actual pending-candidate worker through post-recovery insert and post-attempt insert DB/config failures, then its BullMQ retry, asserting the same attempt is repaired or an explicit durable pending state remains. Include neutral fallback REQUIRED_STATE_UNAVAILABLE.
2. Persist real Shopify/Woo dispatch key formats and usage relations. Invoke fallback while the attempt is still unfinalized. Cover confirmed, uncertain and definitive failed outcomes; no second provider delivery and correct eventual finalization/charge.
3. Fail after support-notice/attempt finalization but before the recovery status update; retry must repair without requiring an unsent-attempt preparation path.
4. Exercise ten-second Shopify lease expiry and the GET/DEL race with a successor; keep final database permits in place. Exercise out-of-order provider refreshes and concurrent order completion versus message-sent update.
5. Populate more shops than the repair batch, keep the first page blocked and a later shop eligible; verify bounded eventual processing. Actual Prisma distinct SQL and row scans need tracing.
6. Measure SQL count/rows/bytes, pool wait, query/transaction time and queue lag for separately named NONE, offer-success, classified-fallback, mandatory-denial and replay paths. Validate deployed indexes and query plans before choosing O1/O3/O5/O6/O7 work.

No new queues, cross-request caches, generalized outbox framework or extra orchestration layer is justified by these static observations alone. The immediate correctness work is to align existing identities and retry ownership, then use measured branch costs to choose narrow projection/query improvements while preserving billing, consent, STOP, moderation and provider ambiguity guards.
