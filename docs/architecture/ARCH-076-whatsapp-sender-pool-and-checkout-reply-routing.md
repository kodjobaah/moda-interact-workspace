---
id: ARCH-076
title: WhatsApp sender pool and checkout reply routing
status: proposed
coordinator: moda_architect
created: 2026-11-13
updated: 2026-11-13
---

# ARCH-076 — WhatsApp sender pool and checkout reply routing

## Product rule

The merchant's checkout system determines which baskets exist, remain open or supersede one another. Moda tracks each eligible abandoned checkout independently. For one customer phone, allocate **one registered WhatsApp sending number per shop with active recoveries**. All eligible baskets at that shop share that number. Other shops active for the same customer use different numbers. Other customers can use those same physical numbers concurrently.

| Customer A's activity | Sender used | What a reply can identify |
| --- | --- | --- |
| Shop A reports A1 with a blue linen shirt | Number 1 | Once its initial message is confirmed, A1 is the sole candidate |
| Shop A reports a distinct A2 with running shoes while A1 remains eligible | Number 1 again | “The basket with the running shoes” can identify A2. “Is the discount still valid?” needs clarification |
| Shop B reports B1 at the same time, with the same customer phone | Number 2 | A reply to Number 2 belongs to Shop B. B1 is its sole candidate |
| A1 expires while A2 remains eligible | A2 continues on Number 1 | A1 leaves the candidates. A verified quote of A1 retains its historical ownership |
| A2 also expires | Number 1 becomes available immediately for this customer | A new shop can claim Number 1. Fresh replies can enter that shop only after confirmed outreach and the event-time check |

Two registered numbers can serve two concurrent shops for the same customer, across any number of merchant-supported baskets in those shops. One number suffices for multiple baskets at a single shop. A repeated event for the same checkout still updates its existing recovery according to its integration. A genuinely new generation of the same Woo checkout supersedes its earlier generation. An independent checkout key at that shop stays independent. In the snapshot, Shopify recovery materialisation calls `findLatestRecovery(shopId, checkoutToken)`. The Woo checkout activity adapter reads generations under its own `shopId` and `checkoutToken`. No merchant setting or storefront change is required by this initiative.

## What the uploaded snapshot does today

Paths below are relative to the parent workspace. All runtime observations are from static inspection on 13 November 2026.

| Touchpoint | Observed behaviour |
| --- | --- |
| `moda-interact-database/prisma/schema.prisma` | `commerce.CheckoutRecovery` identifies a generation by shop, checkout token and generation. `whatsapp.Conversation.checkoutRecoveryId` is unique. `ConversationMessage` stores the provider message ID and dispatch permit. `RecoveryOutreachAttempt` stores the recipient. These rows do not record the selected Moda number. Conversation and message deletion can cascade. |
| `moda-interact-background/src/services/whatsapp.service.ts` | Text, image and template methods independently resolve the single encrypted `messaging.sender` and use its phone-number ID in the Meta endpoint. Selecting a number only in the initial worker would still send from the singleton. |
| `moda-interact-messaging/app/lib/whatsapp/inbound-message-normalizer.ts` and `provider-status-normalizer.ts` in the same directory | Inbound normalization carries the business account from `entry.id`, receiving phone-number ID from `metadata.phone_number_id`, customer number from `messages[].from`, and optional quote from `context.id`. Status normalization also carries both business identifiers. Shared already validates these envelopes. |
| `moda-interact-background/src/services/whatsapp-inbound-processing.service.ts` and `recovery-routing.service.ts` | The active worker handles STOP first. Its router permits the configured singleton, then checks a persisted inbound replay, a quoted outbound, or a recipient-only recovery query capped at two candidates. Two candidates produce neutral guidance. The worker already separates active and historical replies. |
| `moda-interact-background/src/services/checkout-recovery-expiry.service.ts` | Expiry uses `BackgroundRuntimeConfig.checkoutRecoveryLifetimeDays` and `lastExternalActivityAt`. The sweep records EXPIRED and cancels eligible unsent work. Use this same expiry rule when deciding if a sending number is available. |
| `moda-interact-background/src/services/whatsapp-provider-status.service.ts` | Status handling starts from provider message ID. Post-transaction paths can repair billing, reachability and merchant notices, including on duplicate statuses. The actual sending number is absent from that lookup. |

ARCH-012 explicitly deferred sender pooling. ARCH-020 C2 and ARCH-052 document why a single shared sender requires quoted replies or neutral guidance on ambiguity. ARCH-076 replaces the unquoted lookup for newly assigned chats. Keep existing shop-scoped customer identity, consent, ARCH-040 conversation control, ARCH-045/046 STOP and ARCH-028 delivery reconciliation.

## How the application selects the sending number

1. **Enrol the registered numbers.** A super-admin records the Meta phone-number ID and priority. Verify CONNECTED membership on the configured WhatsApp Business Account (WABA) at enrolment and enablement. The inventory row starts disabled. Each immutable ID identifies one real registered business number. The existing encrypted account credential authorises sends on eligible numbers in that account.
2. **Look up the customer and shop before the first send for each basket.** Canonicalize the customer's international phone. If an open, eligible route for that customer/shop exists, attach this checkout's recovery conversation to it. Reuse its number even when another number is free or the route's number has since been disabled for new allocations. If the existing route has no live members, close that generation first. The next claim starts a new generation.
3. **For a new shop route, pick deterministically.** From verified enabled numbers in this environment and account, select the first one free for this customer, in ascending priority and then provider phone-number ID using PostgreSQL C collation. A number held by another shop for the same customer is busy. Repair due expiries and empty routes before declaring exhaustion. Reserve the route and membership before the recovery's credit reservation. A tentative reservation never authorises sending.
4. **Pass the choice to WhatsApp.** The Shopify or Woo final send permit rechecks this precise recovery, current generation, recipient, shop, consent, lifetime and membership. It returns the selected WABA and phone-number ID. Background uses that ID in `POST /{phone-number-id}/messages`, with the customer's phone in `to`. Registration makes the number available to Meta. This lookup and the explicit endpoint tell Moda which registered number to use. Initial outreach, follow-ups, human replies and AI replies use the basket's pinned route. Clarification uses the verified incoming shop route.
5. **Release only the ending basket.** Completion, cancellation, expiry and genuine checkout-generation supersession release that conversation's membership. The existing inclusive last-activity cutoff applies even before a scheduled expiry sweep. Close the route when its last live membership ends. The number can immediately serve another shop for this customer. A late receipt, retry or close updates its original lineage only.
6. **Wait when every number is busy for this customer.** Persist `WHATSAPP_SENDER_POOL_EXHAUSTED` on the same pending initial attempt, before credit or provider admission. The existing `RECOVERY_CAPACITY_REPAIR` cadence retries through the normal workflow, including after a worker crash between claim and billing. A sibling basket can join a live same-shop route even with no free numbers. Zero eligible numbers for a new route also takes the wait path.

## Stored ownership and concurrency

| Record | Ownership and lifetime |
| --- | --- |
| `whatsapp.WhatsAppPoolSender` | Enrolled phone-number ID and immutable owning WABA. Draining prevents allocation of a new route and preserves existing routes, replies and receipt validation. |
| `whatsapp.RecoverySenderRoute` | One immutable generation for a shop, canonical recipient and provider phone-number ID. Two partial unique indexes for open rows (`closedAt IS NULL`) cover `(canonicalRecipient, shopId)` and `(canonicalRecipient, providerPhoneNumberId)`. |
| `whatsapp.RecoverySenderAssignment` | One row keyed by recovery conversation, linked to its route, with assigned/released timestamps. Many active conversations may reference one route. Retain the immutable link for quotes, statuses and retries under existing retention. |
| `whatsapp.RecoveryBasketRoutingTurn` | One row per inbound provider ID entering the shop-level resolver. Retains original request, candidate/choice snapshot and parent link while needed, separately from checkout history. Records selection or admission and receipt of a clarifying prompt. Remove transient content on resolution, abandonment or timeout under BACKGROUND-004. |

BACKGROUND-001 specifies the transaction and lock order for allocating, joining, releasing and reclaiming routes. Serialize last-member closure with sibling admission, and retry unique-index conflicts from fresh state. If the conversation is deleted by the existing cascade and leaves an empty route, reclaim it before capacity refusal. Conditional expiry preserves a concurrent legitimate external activity update and records normal status history and cancellation of eligible unsent attempts. Never hold one shop's locks while cleaning another shop. Keep network and model calls outside database transactions.

## How the agent gets the right basket

The current Background worker calls `RecoveryAgentContextService.getAgentContext(checkoutRecoveryId, conversationId, ...)`. It loads one recovery, verifies that the conversation belongs to it and reads that conversation's history. The commerce host uses one shop, checkout recovery, conversation and inbound version for its tool permissions. The production model invoker also supports a call with a trusted shop ID and no conversation ID. Use that entry point for a small routing decision before the regular Commerce agent runs.

1. **Create the association at outbound admission.** On first contact with Customer X at Shop A, Background opens a `RecoverySenderRoute` for X, A and the selected sender S1. It inserts a `RecoverySenderAssignment` for the first basket's conversation. When Shop A contacts X about a second independent basket, Background inserts a second assignment with the same `routeId`. Each conversation still points at its own `checkoutRecoveryId`. This grouping is explicit in the database before any ambiguous reply arrives.
2. **Read the candidates when X replies.** Validate the receiving WABA/phone. Resolve its open route using X's canonical phone and S1. Follow `RecoverySenderRoute.id → RecoverySenderAssignment.routeId → Conversation.id → Conversation.checkoutRecoveryId → CheckoutRecovery.id`. Restrict the read to unreleased members of the verified shop/customer route whose outreach was confirmed in time and whose recovery is still eligible. Read line items, variants, total and currency from those recoveries. A second shop's route never contributes a basket.
3. **Give the routing model a comparison it can actually make.** Assign temporary keys to these basket descriptions for this decision. Send only the moderated customer message and the eligible descriptions into the shop-scoped model call. Keep the key-to-recovery/conversation mapping in Background. Accept a selected key only when the worker verifies the cited words uniquely distinguish it from every eligible alternative. A verified quote of an original checkout message can identify its target directly. Evidence missing from the descriptions, such as an earlier offer mentioned in conversation, requires a quote or clarification.
4. **Give the Commerce agent one objective and one checkout.** Hold an ambiguous original question in `RecoveryBasketRoutingTurn`, outside all basket conversations, until it is resolved. Under the same ownership transaction recheck eligibility, select the real conversation, and record the original question and its genuine clarification answer there once. Both messages remain visible to the merchant and pass the existing moderation rules. For an answer used only to select a basket, omit the routing instruction from Commerce's current customer objective and its later model history. The original substantive request is the objective. When a customer answers “2. Can I collect on Friday?”, a verified same-basket choice can also carry the genuine new question. Keep and moderate the complete reply for the merchant. Verify moderation on the exact customer-authored clause before passing it to Commerce alongside the original request. If the requested target is unclear, clarify before acting. Direct messages that never answered a routing prompt retain their normal meaning. Run the selected conversation's existing human/AI control and checkout-specific tool permissions.

For example, X has two Shop A checkouts on number S1. Identifiers and amounts below are illustrative.

| Private association in Background | Candidate facts visible to the routing model |
| --- | --- |
| `b1` maps to conversation C1 and recovery A1 | Blue linen shirt, size M, GBP 40 |
| `b2` maps to conversation C2 and recovery A2 | Black running shoes, size 9, GBP 80 |

“Can the running shoes arrive Friday?” supports `b2`. Background verifies the match and runs C2 with recovery A2. “Can it arrive Friday?” prompts “Which basket did you mean? 1. Blue linen shirt  2. Black running shoes.” On a valid reply of “2”, the merchant can see both authentic customer messages in C2. Commerce receives “Can it arrive Friday?” as the customer objective under A2. The digit cannot be used to change quantity. A later fresh question can identify A1.

## How the application identifies the checkout

| Incoming message | Action |
| --- | --- |
| Verified quote of an original basket message | Match the exact outbound provider ID, original recipient, WABA and sending number. Route to that basket directly while eligible. A closed owner uses only the historical path. A broken or cross-number quote grants no fallback. |
| New unquoted message | Establish the shop from the verified receiving account and the open customer/number route. Check every member's eligibility and confirmed initial outreach at the provider event time. With one clear candidate and no pending clarification, process the message in that basket. |
| Several eligible baskets at the identified shop | Use the customer's words and permitted customer-visible facts from those baskets. Accept a choice only if the evidence identifies exactly one eligible basket. “The running shoes” can select the only basket containing running shoes, even when another was created later. |
| Insufficient or conflicting evidence | Ask one focused question on the same number. For example, “Do you mean the basket with the blue linen shirt or the one with the running shoes?” If the baskets have no safe distinguishing detail, ask the customer to reply to the relevant original checkout message. Do not guess, switch to the most recent basket or perform a checkout action yet. |
| Customer answers a clarification | Bind the answer to the confirmed question and the choices actually shown. An explicit “this is the basket I meant” quoting the eligible original outreach can answer a uniquely associated pending question. A new question quoting that outreach is independent. Check those memberships again and resume the original request once for the identified basket. If the selection expired, the reference is stale or several questions could fit, ask for a current unambiguous reference. Never silently reinterpret a choice as the surviving basket. |
| Delayed message, duplicate, old quote or status after number reuse | An original provider message stays with its original route generation and basket, if any. Fresh unquoted input must postdate the new route and confirmed outreach. At a same-second boundary with ambiguous ownership, request a quote through neutral handling. Delivery events for clarification cannot affect checkout billing or reachability. |
| Explicit typed STOP | Process first on a recognised number. A verified quote of a shop-owned outreach or shop-specific clarification applies to that merchant. A standalone STOP or unproven quote suppresses all merchants where that customer is registered, following the existing policy. |

A bare reply sent after reassignment can contain no evidence about an older shop. Lookup uses the current eligible customer/number route. The system never searches other merchants' baskets to infer intent from text. Preserve shop identification in outreach and support the customer's ability to reply to a specific message.

Route-only classification has no commerce tools or checkout side effects. A follow-up question is a response to customer input, uses the existing consent, moderation, customer-service window and admission rules, and consumes no proactive attempt or recovery credit. Shop verification precedes basket lookup and voice processing. Preserve individual conversation control, including human takeover. No clarification refreshes all candidate baskets' expiry clocks. An exception or unsupported input is never affirmative evidence for a selection. BACKGROUND-003 defines attribution, strict time boundaries and deduplication. BACKGROUND-004 defines allowed model evidence, prompt persistence, concurrency and exact continuation.

## Implementation boundaries and rollout

The current Shared v1 inbound and v2/v3 status envelopes already carry both provider IDs. Keep existing Messaging ingress, public schemas, queues, merchant checkout behaviour, and credential administration. Database owns the forward migration. Admin owns inventory management. Background owns dispatch, lifecycle, reply attribution and clarification. System Test owns end-to-end evidence using deterministic provider/model fixtures.

Apply DATABASE-001, integrate the database pin, then deploy Admin and the complete sender-aware Background build. Quiesce incompatible old send workers and drain old requests before enabling pool traffic. Enrol and enable verified numbers. The previous singleton is eligible for enrolment after active legacy use has drained. Enrolment and general dispatch share the membership lock. New general sends may use the singleton only when it is outside recovery inventory, storing the exact account and phone on the dispatch permit. Rollback pauses new pooled admissions while retaining sender-aware readers and reconciliation for already admitted work.

Use BACKGROUND-003's exact persisted sender proof for legacy messages. Missing proof, a wrong account/number, database errors or a genuinely full pool cannot justify a guess or a fallback to the encrypted singleton for pooled sends. Preserve structured errors and bounded diagnostics for allocations, releases, exhaustion, routing and clarification, without customer phones, basket contents or message text in logs.

## Acceptance examples

- Capture the pre-routing model request, the selected checkout model request, and the merchant transcript independently. Only the pre-routing request has multiple candidate summaries. A selection-only “2” appears in the authentic transcript and moderation evidence. It never becomes a commerce objective, order quantity, later model-history instruction or mutation. A direct numeric answer in a normal checkout conversation remains customer input.
- Shop A can have three or more live baskets on one number for the same customer. Replaying one checkout webhook yields one recovery for its existing lineage. Closing one basket leaves all siblings and their delivery histories intact.
- A distinct active Shop B for the same customer needs another number. With one number and two active Shop A baskets, Shop B remains pending after the first expires and becomes eligible immediately when the last expires, including before the sweep. Another customer's capacity is independent.
- The older of two baskets can win on unique message evidence. A generic question yields clarification on the original number. The customer's answer resumes the original question, without a duplicate provider send, wallet charge or merchant action. Identical descriptions, stale choices, overlapping questions and quoted old messages are exercised independently.
- Verify actual Meta endpoint and recipient for initial, follow-up, AI, human, guidance and clarification sends. Exercise customer opt-out, human control, effective expiry mid-turn, voice, status spoofing, late receipts, confirmed prompt replays and restart after an uncertain provider outcome. Use disposable PostgreSQL, Redis and provider/model fixtures.

## Task definitions and execution order

All seven definitions are portable and unclaimed. The parent architecture and each linked task belong to the parent workspace. Source, repository-local tests and submodule pins belong to their implementation repositories. The launcher resolves isolated task worktrees. The developer integrates accepted branches. All tasks remain Pending and unclaimed until current-source compatibility is reviewed and the architect explicitly promotes a task through the normal lifecycle.

| Task and source of detail | Owner | Initial status | Direct dependencies |
| --- | --- | --- | --- |
| [DATABASE-001](../decisions/database/ARCH-076/DATABASE-001-create-sender-pool-and-active-assignments.md) — exact Prisma additions, SQL, fresh/upgrade and concurrency checks | moda_database | Pending | None |
| [ADMIN-001](../decisions/admin/ARCH-076/ADMIN-001-manage-verified-whatsapp-pool-senders.md) — enrol, enable, reorder and drain registered numbers | moda_admin | Pending | DATABASE-001 |
| [BACKGROUND-001](../decisions/background/ARCH-076/BACKGROUND-001-allocate-and-release-recovery-senders.md) — shop route, basket membership, immediate expiry and waiter discovery | moda_background | Pending | DATABASE-001 |
| [BACKGROUND-002](../decisions/background/ARCH-076/BACKGROUND-002-pin-senders-through-provider-dispatch.md) — Shopify/Woo dispatch, billing order, repair worker and transport | moda_background | Pending | BACKGROUND-001 |
| [BACKGROUND-003](../decisions/background/ARCH-076/BACKGROUND-003-route-replies-and-status-by-sender.md) — shop attribution, exact quotes, STOP, guidance and provider status | moda_background | Pending | BACKGROUND-002 |
| [BACKGROUND-004](../decisions/background/ARCH-076/BACKGROUND-004-resolve-same-shop-baskets-and-clarify-replies.md) — identify the basket from the message, ask when ambiguous and resume the original request | moda_background | Pending | BACKGROUND-003 |
| [SYSTEM-TEST-001](../decisions/system-test/ARCH-076/SYSTEM-TEST-001-verify-sender-selection-expiry-reuse-and-reply-ownership.md) — same-shop baskets and clarification, cross-shop routing, reuse and credit effects | moda_system_test | Pending | ADMIN-001, BACKGROUND-004 |

After a current-source compatibility review and explicit task promotion, start DATABASE-001. After its accepted implementation is available at the intended database pin, ADMIN-001 and BACKGROUND-001 can proceed in parallel. Continue the Background stream in order through BACKGROUND-002, BACKGROUND-003 and BACKGROUND-004. The final system test is developer-launched after its prerequisites are accepted. No implementation task depends on the system test. The published Shared schemas already contain both provider IDs. Shopify and Woo storefront clients do not pick or persist a Moda sender. No new Shared, Messaging ingress, merchant client, Hosted API or infrastructure task is required.

Implementation agents use their task's exact change set, validation cases and stop condition. If actual source contradicts the specified ordering, schema or contract, record the file, symbol, command and observed result and return it to the architect. An agent may make routine local coding choices while preserving this contract.

## Change history

13 November 2026, revision 04. The product owner confirmed merchant control of concurrent baskets, one sender per customer/shop, and a clarifying question when the customer's message cannot identify a basket. This revision supersedes the earlier one-active-checkout allocation design. The seven implementation and verification tasks are defined but not materialised.

13 November 2026, revision 05. Documented how the model receives the same-shop candidate set and how the single-checkout Commerce agent resumes the substantive request. Corrected selection-only clarification answers in the Commerce prompt, and added acceptance checks at both model boundaries and in the merchant transcript.

## Preservation and compatibility gate

This proposed initiative preserves the sender-pool design from original local commit `59705bb589342f31054e6c1fd011dacf9d495ae6` (previously colliding with the already Implemented chronological-input ARCH-069). Root authorized identifier correction only. The original commit remains recoverable through the protected full Git bundle and a named preservation ref. IDs/links/status/provenance were reconciled; product intent is retained. No runtime source or task execution is authorized by this preservation. Recheck current schema, message contracts, ordered delivery, dispatch permits, provider template/account behavior, rollout and observability against current main before agreeing the design or promoting any task. ARCH-069 and its accepted tasks remain untouched.
