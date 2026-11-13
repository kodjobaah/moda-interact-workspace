---
id: ARCH-076-SYSTEM-TEST-001
architecture_id: ARCH-076
title: Verify shop sender sharing, basket clarification and immediate reuse
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 95
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-076-ADMIN-001
  - ARCH-076-BACKGROUND-004
enables: []
created: 2026-11-13
updated: 2026-11-13
---
# Verify shop sender sharing, basket clarification and immediate reuse

## Architecture

Read the binding [ARCH-076](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md). Owner is `moda_system_test`. This is the terminal integrated validation task.

## Objective

Drive merchant-accepted checkouts and real WhatsApp callbacks through the application. Observe the physical number used by each customer/shop pair, the checkout that received each substantive message, the clarification sent for an ambiguous basket reference, the instant the last effective expiry made the sender reusable and the credit effects of parking or retrying an attempt.

## Context

Preserved from original local commit `59705bb589342f31054e6c1fd011dacf9d495ae6` under root-authorized ARCH-076 collision correction. Defined portable design only; Pending/unclaimed until current-main compatibility review and explicit architect promotion. No runtime implementation or launch is authorized by preservation.

The existing scenario fixture uses one emulator number and commonly sets `businessAccountId = phoneNumberId`. That configuration cannot distinguish the WABA from the sending number or exercise one merchant with two independently accepted checkouts. A checkout token/key identifies a basket. The merchant/platform accepts or supersedes it under its existing rules. Multiple accepted keys for one phone at one shop each require their own recovery and can share a sender. Reuse the real Messaging, Hosted API, checkout and recovery workers, their normal queues and their existing provider emulator. Existing single-sender scenarios are regression cases.

## Scope

All implementation paths below are relative to `moda-interact-system-test/`. Add four MESSAGING catalogue entries and their modular executors. Test-only changes can extend existing runtime and emulator helpers. Record actual accepted repo SHAs, Background and Admin database gitlink pins, and run results.

## Out of Scope

Application behavior fixes belong to their implementation owners. This task uses synthetic credentials and local provider surfaces. Production WhatsApp sends, remote configuration, and deployment are separate operator activities.

## Requirements

| Scenario ID | Exact exercise | Required observation |
| --- | --- | --- |
| `MESSAGING-POOL-001` | Use priority 10 for S1 and 20 for S2. For customer X, submit two independently eligible baskets A1 and A2 at Shop A and one B1 at Shop B. Wait for A1's initial receipt before adding A2 and B1. Exercise concurrent same-shop admission with a fresh phone and concurrent cross-shop admission with another. Reverse Shopify/Woo roles in a fresh fixture. Send ordinary text to one shop and audio to the other. | A1 and A2 both POST to S1 with distinct recovery, credit and receipt identities even while S2 was free. B1 uses S2 with the same `to`. A different customer can independently use S1. Same-shop races yield one route, two members and one actual initial send per admitted recovery. Cross-shop races use {S1,S2}. Checkout-specific follow-up, human and AI dispatch use the storefront's original sender and produce the correct merchant-visible thread. |
| `MESSAGING-POOL-002` | With only S1 enabled send A1 and A2 for X at one shop. Submit B1 at another. Restart with B1 waiting. Make only A1 due, run a reply for A2, then make A2 due. Run last-member expiry once through allocation before the sweep and once via the scheduled expiry sweep. Replay A1's terminal cleanup after B1 acquires S1. Also exercise last-member completion, cancellation, and authoritative Woo same-key supersession with another independent key still active. | A2 initially joined even with a full pool. B1 has zero provider submissions and zero reserved/committed recovery credits through A1's expiry. Replies for the sole active A2 go there directly. Once the last member becomes ineffective, dispatch B1 on S1 immediately through the worker and the original sequence-one attempt, with exactly one receipt/charge across restart/retry. Late release of A1 cannot free B1. A terminal sibling never frees a still-occupied route. |
| `MESSAGING-POOL-003` | After Shop A's last member expires, send a plain message in the gap before B1 confirmation. After B1 sends on S1 inject a fresh plain reply, delayed pre-B event, timestamp tie, old verified quote, stored inbound replay and signed status for A1. Test a mismatched sender or WABA, invalid/cross-number quote and wrong-number status. Exercise standalone and verified quoted STOP both with no dialogue and while a basket clarification is pending. | No merchant turn in the gap. Only a genuinely fresh unquoted reply enters B1. A verified quote or stored replay stays with the original history where eligible. Invalid, delayed and boundary-tied messages cannot become B1 turns. Positive/negative status and repair stay on the original message. Rejected events have zero merchant and billing effects. Standalone STOP suppresses each registered shop for X and a verified quoted STOP suppresses the owning shop; neither invokes basket selection. Capture neutral guidance on the actual receiving sender where the accepted rules call for it. |
| `MESSAGING-POOL-004` | Two active independent baskets at Shop A contain a red lantern and blue mug respectively; both contain a cleaning cloth. Add a similarly named product and a distinct sentinel at Shop B for the same X. Run the cases below against real workers with a scripted model/moderation provider boundary. | A uniquely supported reference selects that checkout. An ambiguous reference produces a clarification on S1, with no customer turn or checkout-specific side effect until the customer identifies one. The basket selector receives evidence from A1 and A2. Following selection, the ordinary Commerce model receives the substantive objective once, scoped to the selected recovery. The merchant transcript preserves the authentic selection reply under its own provider identity. Merchant B receives no message or disclosure. |

Provision test WABA `770000009999`, senders `770000001111` and `770000002222`, and independent eligible recipients via existing fixtures. Reserve synthetic aliases for evidence. Senders use priorities 10 and 20. In a separate fixture use equal priorities to check the deterministic provider-ID tie break. Cover one eligible sender that is also the configured singleton. Cover zero enabled senders and draining the only inventoried sender after A1 is confirmed. A new A2 still joins and sends from the existing Shop A route; B1 for X and a new route for Y wait until eligible inventory becomes available. Retries of the same provider-uncertain initial send must not switch numbers or create duplicate outbound/credit; correlate the late receipt to the original message where an original provider ID is available.

## Work Items

- [ ] Extend `catalogue/scenarios.json`, `src/harness/messaging/constants.js`, and `src/harness/messaging/index.js` with the four IDs and a thin registration call. Start from the declared `MESSAGING-STATUS-001` evidence class and existing catalogue conventions. Set `sourceRequirements` to this task, use `BLACK_BOX` for externally observed behavior and `liveAuthorizationRequired: false`.
- [ ] Add `src/harness/messaging/sender-pool-scenarios.js`, `sender-pool-fixtures.js`, `sender-pool-observation.js` and `sender-pool-runtime.js`. Extend `src/whatsapp-emulator.js` through its existing fixture interface. Start one real emulator instance per sender and put a run-local HTTP proxy in front of them, dispatching by the actual versioned phone-ID path. Unknown phone IDs receive an error. Record attempted POSTs and successful receipts separately, preserving the observed URL, recipient alias and provider message ID. Use the existing failure proxy pattern for response loss. Do not fake successful sends from the proxy.
- [ ] In `src/harness/platform-configuration-fixture.js` allow an explicit distinct WABA in `messagingSenderValue`, preserving old callers. In `src/harness/messaging/provider-status-fixtures.js` allow distinct WABA and phone IDs. Reuse the signed-payload helpers in `src/harness/messaging/helpers.js`. The stock emulator has a singleton identity: for precise pooled inbound/status cases post fixture-generated, signed, native Meta envelopes for the specified WABA and phone through the real `/webhook/whatsapp`. Isolate stock emulator auto-callbacks on a recorder if they use a synthetic WABA different from the scenario. The scenario must contribute exactly the intended callbacks.
- [ ] Use the disposable data plane and `src/harness/recovery/outreach-runtime.js` plus `src/harness/messaging/provider-status-runtime.js` on the same PostgreSQL/Redis instance. Reuse the local Shopify provider, `src/harness/moderation/runtime.js`, and `src/harness/language/model-fixture.js` plus the existing run-local model transport. Script the external model result and receipt, leaving the real worker, candidate projection, response validation and dialogue storage in the test path. Set up store entitlements, registered `CustomerPhone`, verified consent, approved templates, merchant credentials and spendable credits. Use actual enrolled sender rows from the accepted schema as fixture prerequisites. Cite the accepted ADMIN-001 tests for operator enrol/enable/disable with a stubbed Graph read. This runtime scenario can seed verified inventory as a precondition. Assert that enabling a seeded row during the run permits a waiting checkout to resume through the real worker.
- [ ] Use signed Shopify checkout webhooks as in `RECOVERY-OUTREACH-001`. For Woo start the accepted hosted API and its workers, apply the installation-authenticated `POST /v1/woocommerce/whatsapp-consent` and `POST /v1/woocommerce/activity` (`woo.activity.v1`, `CHECKOUT_UPDATED`). For this run set the Woo recovery workers to `NODE_ENV=test`, `MODA_WOO_TEST_OUTBOUND=1` and a run-local HTTP `WHATSAPP_API_BASE_URL` on `127.0.0.1` or the container's `host.docker.internal`. Use the existing guarded test transport. Capture a negative control with the switch off. The snapshot's ordinary production Woo activation is outside this initiative. Create A1/A2 using two independent Shopify checkout tokens at one shop for the first run. In the mirrored Woo run, use distinct checkout keys at the same installation and recipient. Send a later generation for one Woo key as a control and verify only its original generation is superseded. Include a merchant fixture that submits just one checkout to show direct routing without any clarification prompt. Bind distinguishable basket products under each merchant. Confirm routing by its visible message in the Shopify recovery detail page or Woo `GET /v1/merchant/recoveries/{id}/messages` under that shop's credentials. Distinguish authorized history from active responses. Companion negative checks use the other shop's session. Read-only SQL may corroborate receipts and billing; it cannot be the sole evidence for an externally observable send or reply.
- [ ] Seed the expiry clock condition only on disposable fixtures. Set the old checkout's last activity due and keep B within the same configured lifetime. For precise equality/race SQL assertions reuse the accepted BG001 PostgreSQL tests. For the end-to-end before-sweep case interpose the real repair/dispatch before the next expiry sweep using the existing runtime cadence controls. Never mark the old owner released directly in a PASS path. Use a unique provider ID per new inbound. For each new member use `T = floor(max(member.assignedAt, member.initialConfirmedAt)/1 second)`, send events at T−1, T and T+1, with the last event actually occurring after confirmation. Use stored provider times for delayed delivery, independent of arrival order.
- [ ] Add `src/harness/messaging/basket-clarification-scenario.js` and `basket-clarification-fixtures.js` for POOL-004. Send an explicit quoted reply to A2 and compare with an independent fresh unquoted “Does the blue mug ship today?” event resolved to A2. Send “Is the cleaning cloth in stock?” and “Can I change the delivery address?” against fresh fixtures. Each ambiguous event produces a short, shop-scoped clarification with enough safe information to distinguish the baskets. Check its signed receiving number, recipient and permitted labels. Capture the initial exact text and assert replay adds no provider POST. Before a choice, neither A1 nor A2 should show the event or an AI/human turn, command, activity extension, recovery credit or offer. The basket selector's server-supplied context contains no Shop B marker, session, phone, raw internal ID or checkout URL and exposes no commercial tool. Place both merchant and recipient sentinel values in the other fixtures and assert absence at the local routing model boundary and in the prompt text delivered to X.
- [ ] Use the accepted routing-turn states as supporting transaction evidence. While a question is pending, quote a verified original checkout outbound with an independently substantive new question and verify it follows that checkout independently. A quote of the actual confirmed clarification identifies only that question. A valid choice inside that quote is causal even in the same provider second; an unquoted number at that same second cannot resolve it. For distinct fresh dialogues, respond to the question with a product reference (“the lantern one”) and with a numbered option from the actual confirmed prompt. The order must be the order presented. Verify the selected checkout receives the original substantive question once under its original provider identity and the commerce response addresses that question. Check the other checkout, duplicate prompt delivery and duplicate answer across worker restart. Inspect the selected checkout’s merchant transcript and its Commerce-model inputs independently. The transcript contains the original request and the authenticated choice in chronological order, each under its own provider ID. The Commerce model receives the original substantive request as current customer input. A routing-only selection is absent from both the current customer input and commerce history, including if another ordinary turn on the same checkout was processed before the clarification answer arrived. Verify a single pending transition and service-window update under the selected checkout’s existing control. A later *independent* unquoted message must consider all eligible checkouts again. A new question referring to the other basket can select it. Customer Y's selection and a choice posted to the wrong receiving number cannot resolve X's dialogue.
- [ ] Add a model-boundary assertion helper at `src/harness/messaging/basket-clarification-model-observation.js` and cover it in `test/harness/messaging-basket-clarification.test.js`. Capture the synthetic run's actual provider requests in memory at the model fixture and correlate them to the run's chosen recovery and worker pass. Identify the routing request by its sole local `chooseBasket` signature and the substantive Commerce request by the existing Commerce turn. Assert on parsed message roles, selected basket context, available actions and provider/tool calls, not substrings anywhere in the full serialized request (an option number can legitimately occur in a product price). Keep raw payloads out of persisted evidence.
- [ ] Give A1 and A2 distinct synthetic line-item/variant/total markers, different earlier customer-history markers, and a confirmed outreach for each. Seed separate unrelated markers on B1 and on another customer's checkout at Shop A without adding those product markers to the selected shop's catalogue/tool fixtures. On an ambiguous fresh reply, the classifier gets one opaque key per eligible A-member, both sets of allowed product facts and the customer text. No earlier customer-history marker, foreign-shop/customer marker, checkout URL or private recovery identifier reaches the classifier. Its response cannot invoke a commerce tool. Before selection there are zero full Commerce runs for that question. Quote the resulting prompt and choose its actual second option. Wire the normal Commerce fixture to trust only that selected checkout when reading current checkout items and history. On every model call in that resumed logical turn assert only the selected checkout’s context and history are available. Neither the unselected sibling’s basket-only facts and conversation markers nor B1’s or the other customer's markers may appear. Verify by provider observation and actual tool arguments when supported; never grant the fake model authority to choose a real conversation ID.
- [ ] Use the exact original request “Can this basket be delivered on Friday?” and reply to the confirmed numbered clarification with the single character “2”. In the resumed first Commerce request assert one new original customer objective, with its original wording, and no user-role selection message “2”. Assert the actual proposed/dispatched reply addresses Friday delivery, with no quantity interpretation, offer or quantity-dependent side effect from the choice. After replay there is one resolved checkout turn. In a new independently quoted substantive turn on that same recovery, inspect the first Commerce request again: the prior permitted original question may appear in history exactly once and the prior routing-only “2” is absent. Check the real merchant-facing transcript contains both inbound messages once under their distinct IDs. Observe current moderation allowance separately for the original and the choice (including its voice equivalent), with denial/review preventing projection/commerce. Repeat with the chosen conversation in HUMAN mode: its owner can read the original and selection, and the Commerce model is never invoked.
- [ ] Use a separate direct-route numeric control. Have the selected conversation explicitly ask “How many mugs do you need?”, then send the ordinary genuine reply “2” with an exact checkout quote or in a fresh eligible singleton without a pending basket clarification. The direct numeric event retains ordinary moderation and reaches Commerce as customer text. Number filtering by text alone fails this case.
- [ ] Test a mixed customer reply to the sole confirmed clarification for “Can I change the delivery address?”. Send the exact text “2. Can I collect on Friday?” against unchanged eligible options and no competing basket reference. The existing moderator and merchant transcript receive the unchanged, authentic message. In the first resumed Commerce request assert the two current customer objectives in original order, the address-change question and the exact contiguous suffix “Can I collect on Friday?”. Each occurs once. The model receives neither the selector prefix nor its interpretation as a quantity. Repeat observation on a later turn after restart to ensure history also uses only the genuine objective suffix. Corroborate with a resolved routing row linked to the parent question whose only retained input metadata is `{v:1,role:"mixedObjective",startCodePoint:3,endCodePoint:27}` (half-open Unicode code points). Its offsets reproduce the exact suffix from the original moderated, persisted content. Assert the source has its canonical full-message moderation assessment and the mixed turn holds a matching, content-free suffix approval from the configured policy. Independently reject or expire that suffix approval in the moderation fixture and verify the suffix cannot enter Commerce or carry out an instruction until its exact projection passes moderation; policy refresh preserves the original pending admission time. Verify the resolved root retains only `{v:1,role:"objective"}` in inputJson. For a pure confirmed selector “2”, check the resolved row retains only `{v:1,role:"selectionOnly"}`; the checkout transcript retains the full genuine choice. An IGNORED routing turn has SQL NULL inputJson. On a disposable fixture clear the selector’s nullable parent link through its real parent-delete FK behavior, then inspect the next Commerce request: the retained selectionOnly role still excludes that control from history. A direct ordinary message having no routing row follows existing Commerce behavior. An unrecognised or malformed resolved role grants no model input. Supply a second mixed reply, “2. Can you gift-wrap the red lantern in the other basket?”, and an unsupported/uncertain split. Neither can apply both pieces to option 2. Assert a focused clarification/restatement and zero wrong-target checkout actions. No substring may be silently discarded, applied to another basket or replaced with model-authored wording.
- [ ] Run deterministic external-provider outcomes for ambiguous/insufficient evidence, invented option, model output incompatible with the response schema, provider timeout and an input containing instructions to pick a foreign basket. An invalid answer grants no checkout access. Model or credential unavailability, refusal, timeout, nonunique evidence and invalid output all require clarification when its independent permit is valid. Allow exactly the structured chooseBasket operation with no business tools. Run a unique full amount/currency match and a second basket with the same amount/currency to prove the server rejects an otherwise confident ambiguous choice. Test blocked/review customer text and exhausted moderation availability (IGNORED, no classifier, no basket turn), plus denied outgoing prompt moderation (no WhatsApp POST). Duplicate titles and a shared item must not decide a basket by recency or query order. Exercise a non-distinguishable pair, 51 active baskets, the 16,000-byte model bound and the 1,000-code-point prompt bound. When the complete set cannot be represented under the contract, expect instructions to use WhatsApp Reply on the original basket message with the fixed basket-choice wording from BACKGROUND-004. Never display a partial list or silently choose a hidden alternative. For a fresh indistinguishable or oversized fixture, send the independent original question “Can I change the delivery address?” and observe its sole eligible confirmed clarification directing the customer to quote the original basket outreach. Quote A2’s actual initial provider message with “this is the basket I meant”. Verify the merchant transcript for A2 retains the original address-change question and the explicit basket choice once. The original request alone reaches the full Commerce model in AI mode. The choice stays a routing-only control; the customer need not retype the question. Replay both IDs and assert no duplicate turn or action. In a separate fixture with that same pending root, quote A2’s initial with an independently substantive new question. Only the new request reaches A2; the pending original is untouched. Two plausible live roots, no eligible root, a foreign sender, or a quoted basket that was absent at the original question cannot use this control reply to claim another request. Prove all 51 merchant-accepted baskets still use one open sender route.
- [ ] Race classification/follow-through against a member expiring, active membership changing, last-member close and S1's reassignment to Shop B. Introduce the change after candidate discovery and before the commit/send using external-provider response barriers. The result can only use the still-validated original route and eligible member(s). Even if only one original option survives, a stale answer cannot silently select it. The original unresolved request cannot move to a new shop/member. If appropriate new options are offered on this same route, they are restricted to eligible-at-root survivors and use a new explicit-quote prompt. Verify answers use the frozen order. After all eligible-at-root members end a permitted instruction asks to quote original outreach and repeat the question. Redeliver the original message ID, answer ID and provider callback after restart; assert no repeated visible prompt, credit, action or substantive turn. Exercise a definitely rejected prompt send and a lost response after the real emulator accepted the request. Assert the original stays PROMPT_ADMITTED on missing receipt/uncertain delivery; neither replay nor a numeric answer can resend or confirm it. A definite terminal reject closes IGNORED. Confirmed receipt carries the original trusted number. A local attempt is insufficient proof of delivery.
- [ ] Send two independently ambiguous original questions on the same route, then unquoted “2”. Check both originals remain pending and the control instruction asks the customer to quote the intended question and choose its option or quote an original basket and restate the request. The instruction itself never becomes a selectable question. Answer one by verified prompt quote and show that no unrelated objective moves with it. Also run a second ambiguous answer to a sole first prompt, confirm its child and prove follow-through reaches the original substantive question only once. Exercise a fresh independent request that uniquely identifies a different item while an earlier question is pending. Check it reaches only that newly referred checkout and leaves the earlier question pending. Repeat at the exact 24-hour root boundary with recent child activity. No reopened window, stale option, new recovery turn or duplicate prompt; bounded maintenance scrubs pending content even without further webhook traffic while retaining dedupe evidence. Use controlled fixture timestamps to avoid a real 24-hour wait.
- [ ] Run an audio case on a single proven shop with multiple eligible baskets, and an unowned/mismatched number case. Check one stored transcript for a successful audio message and its replay, moderation of that transcript and the same checkout decision as text. For a terminal unreadable/oversized recording expect only the permitted request to restate it, with no invented original question. Exercise the existing unsupported-content path under BG003’s published envelope and neutral/no-turn rules. Use the local media/transcription request counter to assert no unowned/cross-shop download or dispatch. Preserve each selected recovery's existing human-versus-AI control; a conversation held by a human must not run the commerce agent. Correlate sanitized provider evidence, merchant-visible conversation history and database assertions separately.
- [ ] Update `test/harness/messaging-executors.test.js` and add `test/harness/messaging-sender-pool.test.js` and `test/harness/messaging-basket-clarification.test.js` for registration, distinct sender-aware fixtures, proxy rejection, duplicate suppression, cleanup and evidence redaction. Append both suites to the existing explicit file list in `package.json` script `test:messaging-harness` so normal verification executes them. Align pre-existing recovery fixtures with the new runtime: new recoveries use enrolled inventory, genuinely pre-cutover dedicated legacy fixtures use the exact positive evidence required by BG003. Keep older test cases' intended outcomes. Add the four scenarios to `docs/MESSAGING.md` with the actual proof boundary. Keep scenario, fixture and assertion files modular within existing structure limits.

## Interfaces / Contracts

Consume the public provider, application and merchant interfaces already exercised in this repository, and the accepted DATABASE-001, ADMIN-001 and BACKGROUND-001 through BACKGROUND-004 definitions. Capture the actual HTTP `/{phoneNumberId}/messages` path. Distinguish recipient number (`to`), sender phone-number ID and WABA in every evidence assertion.

## Dependencies

ARCH-076-ADMIN-001 and ARCH-076-BACKGROUND-004 complete and architect-accepted. DATABASE-001 and BACKGROUND-001 through BACKGROUND-003 are transitive prerequisites. Operator manual validation can precede launch.

## Enables

None. Return results to the architect for the final cross-repository review.

## Acceptance Criteria

- [ ] Each new scenario passes individually and in a single suite run. Required assertions distinguish no-send, neutral guidance, historical persistence and active merchant processing.
- [ ] The provider endpoint, shop route, independent checkout identities, original question and credit effects agree across Shopify and Woo. Confirm all POOL-004 branches, including model rejection, no-turn ambiguity, validated follow-through, stale choices, duplicate delivery and foreign-basket isolation. Reassignment succeeds with one physical sender and no cooldown.
- [ ] Observe candidate evidence at the routing model boundary and selected-only authoritative context at the Commerce model boundary. Verify the original request appears once, a routing-only ordinal is preserved for merchant history/moderation, an independently substantive numeric answer still reaches Commerce, and a replay cannot create a second checkout turn.
- [ ] No unexpected provider POST, duplicate charge, foreign merchant marker, credential exposure, leaked container, worker or Redis job survives cleanup. Report a blocked service/fixture as blocked with its actual error.

## Validation

Run from the dedicated system-test implementation worktree, with Node 24+, Docker and accepted local checkout builds.

```bash
npm ci
npm run typecheck
npm run lint
npm run validate:catalogue
npm run test:messaging-harness
node --test test/harness/messaging-sender-pool.test.js test/harness/messaging-basket-clarification.test.js
npm run system:run -- --scenario MESSAGING-POOL-001,MESSAGING-POOL-002,MESSAGING-POOL-003,MESSAGING-POOL-004 --list
npm run system:run -- --scenario MESSAGING-POOL-001 --execute
npm run system:run -- --scenario MESSAGING-POOL-002 --execute
npm run system:run -- --scenario MESSAGING-POOL-003 --execute
npm run system:run -- --scenario MESSAGING-POOL-004 --execute
npm run system:run -- --scenario MESSAGING-POOL-001,MESSAGING-POOL-002,MESSAGING-POOL-003,MESSAGING-POOL-004 --execute
npm run system:run -- --scenario RECOVERY-OUTREACH-001,MESSAGING-TEXT-002,MESSAGING-STATUS-001 --execute
git diff --check
```

## Implementation Notes

Use launcher-prepared mirrored worktrees. Collect sanitized scenario outputs, task branch/commit, fixture images and submodule SHAs, timing cutoffs, bounded absence checks after worker/queue drain, and container cleanup. Do not weaken a source implementation to pass a system test. Stop and return a concrete reproducible failure to the owning agent through the architect. Submit passing work for architect review and stop.

## Completion Report

Not started. Record isolated worktrees, commits, dependency pins, external observations, supporting SQL assertions and commands/results.

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Pending.

### Deviations

None.

### Assumptions

None beyond the accepted task contract.

### Unresolved Issues

None at definition.

### Architectural Concerns

None at definition.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

None.
