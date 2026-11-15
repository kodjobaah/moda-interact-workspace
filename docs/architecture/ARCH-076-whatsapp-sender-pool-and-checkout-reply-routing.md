---
id: ARCH-076
title: WhatsApp sender pool and checkout reply routing
status: agreed
coordinator: moda_architect
created: 2026-11-13
updated: 2026-11-15
---

# ARCH-076 — Sender routing and independent allowance renewal

## Status

Agreed design; user authorizes implementation, task tests, commit/push and integration, with test verification before production. SYSTEM-TEST remains explicitly deferred. DATABASE-001 is executing prepared attempt 1 (`executor: codex`, claimed 2026-11-15T11:46:23Z); preparation is not source implementation; the user has now authorized this revised schema. No migration or runtime change is claimed by these definition edits. Preserve completed chronological ARCH-069 unchanged.

## Problem and goals

One customer can have multiple open checkouts at one shop and several shops on the same WhatsApp number. Attribute each question without exposing another merchant's context or losing its original meaning. Use more registered numbers when available, without moving existing conversations. Separately, an existing basket may exhaust its automated allowance. Credit accounting must not influence sender ownership or basket attribution.

## Current architecture

Accepted Background b7cca48, Database 2e14f866 and published Shared 6.1.0 are the inspected baseline. Conversation.checkoutRecoveryId is unique. Existing recovery lifecycle/expiry, service-window, STOP, consent, moderation, control revision and credit services remain authoritative. Ordered ConversationDeliveryPart and status receipt rows already preserve per-part sender identities. Current normal automated admission counts Conversation lifetime UsageEvents; it cannot implement new funded allowances by resetting counters. CommerceAgentConfiguration has no agent-purpose discriminator; its existing active model/prompt pointers belong to the normal Commerce agent.

## Independent workstreams

**Sender routing:** DATABASE-001 → BACKGROUND-001 → BACKGROUND-002 → BACKGROUND-003 → BACKGROUND-004. ADMIN-001 manages inventory. ADMIN-002 supplies the neutral template; ADMIN-003 configures the routing agent and both precede BACKGROUND-004.

**Allowance accounting:** DATABASE-002 → BACKGROUND-005. Neither stream depends on the other. Shared ownership invariants apply regardless of whether allowance renewal is enabled, funded or exhausted. Do not exclude a checkout or select a different checkout because of credits or message allowance.

## Explicit sender storage — DATABASE-001

Five tables in schema `whatsapp` retain explicit customer/sender and shop generations. This restores the original five-entity model while retaining the R15 decision evidence, configured policy and independent allowance stream. Historical executable SQL is not copied blindly: the reviewed field contract below includes new evidence fields and must drive fresh migration authoring after approval.

| Table | Exact proposed columns |
| --- | --- |
| WhatsAppPoolSender | providerPhoneNumberId VARCHAR(64) PK; providerAccountId VARCHAR(64) NOT NULL; priority INTEGER NOT NULL DEFAULT 0; allocationEnabled BOOLEAN NOT NULL DEFAULT false; verifiedAt TIMESTAMPTZ(3) NOT NULL; createdAt/updatedAt TIMESTAMPTZ(3) NOT NULL DEFAULT now() |
| RecoverySenderThread | id TEXT PK (client cuid); canonicalRecipient VARCHAR(15) NOT NULL; providerPhoneNumberId VARCHAR(64) NOT NULL; openedAt TIMESTAMPTZ(3) NOT NULL DEFAULT now(); closedAt TIMESTAMPTZ(3) NULL |
| RecoverySenderRoute | id TEXT PK (client cuid); shopId TEXT NOT NULL; threadId TEXT NOT NULL; canonicalRecipient VARCHAR(15) NOT NULL; providerPhoneNumberId VARCHAR(64) NOT NULL; openedAt TIMESTAMPTZ(3) NOT NULL DEFAULT now(); closedAt TIMESTAMPTZ(3) NULL |
| RecoverySenderAssignment | conversationId TEXT PK; routeId TEXT NOT NULL; assignedAt TIMESTAMPTZ(3) NOT NULL DEFAULT now(); releasedAt TIMESTAMPTZ(3) NULL |
| RecoveryBasketRoutingTurn | inboundProviderMessageId TEXT PK; threadId TEXT NOT NULL; routeId TEXT NULL; promptScopeRouteId TEXT NULL; occurredAt/createdAt TIMESTAMPTZ(3) NOT NULL (createdAt DEFAULT now()); inputJson/candidatesJson/moderationJson JSONB NULL; configurationSnapshot/routingDecision JSONB NULL; parentProviderMessageId TEXT NULL; resolutionInboundProviderMessageId TEXT NULL; state VARCHAR(24) NOT NULL DEFAULT 'RECEIVED'; selectedConversationId TEXT NULL; promptText TEXT NULL; promptAdmittedAt/promptSentAt TIMESTAMPTZ(3) NULL; promptProviderMessageId TEXT NULL; expiresAt TIMESTAMPTZ(3) NOT NULL; resolvedAt TIMESTAMPTZ(3) NULL; workToken TEXT NULL; workLeaseUntil/nextRepairAt TIMESTAMPTZ(3) NULL; repairAttempt INTEGER NOT NULL DEFAULT 0; updatedAt TIMESTAMPTZ(3) NOT NULL DEFAULT now() |

A WhatsApp physical chat thread (RecoverySenderThread) is NOT a new checkout Conversation. Thread is one immutable recipient/sender generation; route is one immutable shop ownership generation on that thread; assignment links each existing recovery Conversation to its route. A routing request always has exact threadId; unknown-shop request has routeId NULL. Once shop is verified, routeId may bind once to a route on that same thread. promptScopeRouteId freezes the prompt's actual scope at admission: NULL for a neutral prompt, even when the original later binds to a shop. Neither field is inferred later from the selected Conversation.

FKs and deletion actions:

- Thread.providerPhoneNumberId → inventory providerPhoneNumberId, RESTRICT; inventory exposes unique `(providerPhoneNumberId,providerAccountId)` for exact sender-account evidence.
- Route.shopId → Shop.id CASCADE; `(threadId,canonicalRecipient,providerPhoneNumberId)` → Thread matching unique target, CASCADE. Route identity fields immutable.
- Assignment.conversationId → Conversation.id CASCADE; routeId → Route.id NO ACTION DEFERRABLE INITIALLY DEFERRED. Isolated route/thread deletion cannot detach a surviving Conversation and permit a new sender assignment; whole-shop deletion succeeds only when both owning Conversation and route cascades complete. Assignment conversationId/routeId/assignedAt immutable; release monotonic.
- Turn.threadId → Thread.id CASCADE; parentProviderMessageId → Turn.inboundProviderMessageId NO ACTION DEFERRABLE INITIALLY DEFERRED; selectedConversationId → Conversation.id SET NULL. Immutable resolved decision retains historical identity and cannot be rebound when a pointer is deleted.
- Turn.routeId and promptScopeRouteId are historical scalar scope stamps deliberately without cascading shop FKs. A guard verifies referenced route exists on exactly this thread at initial binding/prompt admission. If shop/route is physically deleted, retain the original scope stamp and terminalize/scrub affected pending input; never convert it back into a neutral selectable request or another shop. Neutral requests on a surviving thread remain neutral. Closed routes/threads remain historical rows until owner deletion; status evidence stays on existing provider messages.

Uniqueness/indexes: partial unique live Thread `(canonicalRecipient,providerPhoneNumberId)` WHERE closedAt IS NULL; unique Thread `(id,canonicalRecipient,providerPhoneNumberId)` composite target; partial unique live Route `(canonicalRecipient,shopId)` WHERE closedAt IS NULL; assignment Conversation PK; unique non-null promptProviderMessageId. Index Route `(threadId,closedAt,shopId)`, Assignment `(routeId,releasedAt)`, Turn `(threadId,state,occurredAt)`, partial pending expiry/due indexes, and enabled inventory allocation order. Inbound provider identity remains immutable global provider ID as in the existing ingress/message contract; verify its receiving WABA/sender through the pinned thread, never trust ID alone.

Identity guards make inventory providerPhoneNumberId AND providerAccountId immutable; Thread id/recipient/sender/openedAt immutable; Route id/shop/thread/recipient/sender/openedAt immutable; Assignment conversationId/routeId/assignedAt immutable. Thread/Route closedAt and Assignment releasedAt permit only a monotonic NULL→timestamp transition. No generation identity can be updated to transfer history.

CHECK digit-normalized sender/WABA/recipient, nonnegative priority/repairAttempt, paired work lease, time ordering, state allowlist RECEIVED/PROMPT_ADMITTED/PROMPT_UNKNOWN/RESOLVED/EXPIRED/IGNORED, prompt evidence consistency and terminal input scrubbing. Owner/identity guards require RECOVERY assignment Conversation's recovery shop equals route shop, compatible with legacy nullable Conversation.shopId. Same-thread prompt/parent/selected-assignment guard and application transactions prevent cross-scope binding. routingDecision is nullable until one structural versioned decision freezes; semantic business evidence validation belongs to Background. candidatesJson freezes offered assignment Conversation IDs and complete safe candidate facts; no fictitious JSON foreign keys.

Add nullable paired ConversationMessage.dispatchProviderAccountId/dispatchProviderPhoneNumberId VARCHAR(64) root permit evidence; preserve current ordered-part sender/status proofs. No sender credit fields, additional Conversation or mass history migration. Upgrade 80 predecessor migrations through `20261113111320_arch075_meta_app_operation_state`, then target `20261113120000_whatsapp_sender_pool`. Final SQL object counts must be regenerated for these new evidence fields, not asserted from the historical migration.

## Sender allocation and attribution

Serialize allocation by canonical recipient using transaction advisory lock across replicas, then lock relevant thread/route rows in deterministic order. Reuse same recipient/shop's open route and add assignment; draining its inventory does not migrate existing route. Otherwise rank enabled verified WABA senders by count of distinct open shop routes for this recipient, priority and phone ID in C collation. Establish/reuse live recipient/sender thread and create new shop route. Zero routes wins; pool exhaustion permits explicit shared thread. Freeze recipient in thread/route because mutable customer phone is not historical address proof. Provider verification populates inventory verifiedAt; no fabricated default proves verification.

Release terminal/expired basket assignment using existing inclusive expiry rule. Close route only after its last live assignment, thread only after its last live route. Same recipient lock covers concurrent additions and last-member closure. New thread/route generation gets a new ID; never migrate existing assignments or pending originals to it. This is explicit durable ownership, but still requires eligibility queries and tested application transactions; FKs do not prove consent, receipt, credit, moderation or service window.

Exact quote/replay follows original provider message, sender and immutable generation. HTTP acceptance or provider ID alone does not establish contacted candidate after definitive failed initial delivery such as 131049. Persist each unresolved original before clarification with exact thread/optional route and candidate assignments. Closing candidate expires/reclarifies the old choice; never substitute a new route or basket. Multiple originals coexist. No merchant receives unresolved cross-shop input. STOP/history/human handling remain independent. No model/provider network inside database locks.

## Configurable routing — ADMIN-002, ADMIN-003 and BACKGROUND-004

Before shop proof use deterministic exact identity/quote matching and a dedicated Admin-authored ROUTER conversation template. It has exactly one response.body slot, neutral static copy, no tenant/customer/checkout variables, conditionals, product image or composite profile. Existing immutable source, locale review, publication CAS/audit and generic prepared reader/renderer are reused. Application-owned ROUTER selection has no fallback to SHARED/AI/HUMAN. Normal Shared chooseSlot sees only its existing three audiences; never pass ROUTER into that selector. No Meta registration is needed for ordinary customer-initiated in-window clarification.

After a shop is proven, semantic basket selection may use complete safe basket facts from that shop only. Register `recovery.routingAgent` in existing PlatformConfiguration JSON, version/CAS/audit; no new AI configuration table. Proposed fields: schemaVersion; enabled; modelBinding (FIXED_CATALOGUE modelCatalogueEntryId or explicit VERIFIED_SHOP_INHERIT); distinct published platform promptRevisionId; wrapperAudience ROUTER; confidenceThreshold; budget(deadlineMs,outputTokens,toolCalls); retry(maxAttempts,backoffMs); input(maxHistoryMessages,maxInputCharacters,maxCandidates); decisionTTLms; retentionMs. Admin manages all business values with no implicit numeric/prompt defaults. Model provider/model ID/request parameters/reasoning come from existing catalogue configuration/schemaVersion; protected provider credentials remain in existing credential resolver. Reference IDs are checked on save and use, not DB FKs inside JSON. A fixed model must be platform-available; inherited model resolution receives only a verified actual shopId. Never overwrite the normal Commerce agent's active model or prompt.

Snapshot configuration version, model entry editVersion, published prompt ID/hash and resolved parameters before a request. A changed snapshot invalidates stale selection at admission. Current CommerceModelPolicy supports deadlineMs/outputTokens/initialOutreachToolCalls and lacks purpose; do not silently reuse/mutate its normal agent budget. Missing/invalid router policy or oversized complete candidate context uses clarification, never a hidden model/default or truncated semantic guess. Code retains structural confidence 0..100, offered-key validation, tenant isolation, bounded provider-safe requests, idempotency, STOP/window and authorization; business threshold/retry/input values are saved configuration.

## R15 question and clarification contract

A new inbound message is not automatically the answer to an older clarification. Persist a structured role decision before admitting input to a merchant Conversation. The four application-owned roles are `SELECT_ONLY`, `NEW_QUESTION`, `SELECT_AND_QUESTION`, and `CLARIFY`.

| Customer input while “Can it arrive Friday?” is pending | Required result |
| --- | --- |
| “running shoes”, linked to exactly one confirmed prompt and one offered basket | SELECT_ONLY: resume the original Friday question for that basket; do not replace it with the selection text. |
| “Do the shoes come in black?” | NEW_QUESTION: process this independent product question if its own owner can be proven; leave the Friday question pending. A product mention alone is not consent to resolve an older question. |
| “2. Can I collect on Saturday?”, linked to a verified prompt whose option 2 identifies that same basket | SELECT_AND_QUESTION: preserve the original Friday question and the exact new collection question for the selected basket. Moderate the new clause independently before admission; do not paraphrase or discard it. |
| Bare “2” while several independent prompts are pending | CLARIFY: identify which prompt/request is being answered; do not choose newest or closest. |
| Numeric text in an ordinary already-attributed conversation, without a matching pending prompt | Normal authentic customer input, not an invented selection control. |

A verified reference is a quote of the exact confirmed clarification provider ID, an explicit request token, or exactly one eligible outstanding confirmed prompt whose offered option uniquely matches. Prompt admission without a confirmed receipt is not enough. Multiple matches, missing evidence, conflicting shop/basket facts or confidence below saved policy produce CLARIFY. Semantic role classification uses the configured routing prompt/model/threshold; code validates evidence and offered identities. No hardcoded 80% rule, keyword-only heuristic, history recency or allowance/credit tie-breaker.

Add `RecoveryBasketRoutingTurn.routingDecision JSONB NULL`, separate from `configurationSnapshot`. Schema version 1 contains: role; originalTurnId and originalInboundProviderMessageId (nullable for independent NEW_QUESTION); currentInboundProviderMessageId; promptTurnId and confirmedPromptProviderMessageId (required when resuming a pending clarification; nullable for an independent NEW_QUESTION routed directly by verified ownership); selectedAssignmentConversationId (nullable on CLARIFY) and offeredOptionKey (required for a numbered selection, otherwise nullable with exact alternative ownership evidence); immutable candidate-snapshot fingerprint; exact original text hash; authentic existing ConversationMessage IDs once associated; clause offsets/hash referencing the authentic current inbound text (never plaintext clause in routingDecision); moderation assessment identity/hash for each admitted original/new clause; configuration version/model editVersion/prompt revision/hash; confirmed clarification template definition/locale/prepared-content hash; owner/control revision and admission inboundVersion when assigned; decision timestamp. These are bounded structural evidence, not a second copy of model reasoning or private customer context. Candidate fingerprints use the existing approved deterministic hashing machinery; do not invent a competing codec.

Keep original inbound and selection as authentic transcript records after ownership is established; model completion context receives only the saved original for SELECT_ONLY, the saved original plus the exact genuine additional clause for SELECT_AND_QUESTION, and only the current substantive question for NEW_QUESTION. A direct verified quote of an original basket message can establish the owner of a NEW_QUESTION without a clarification prompt; it does not by itself resume an older pending question. A SELECT_ONLY control is not the new substantive question. A NEW_QUESTION decision cannot resolve, consume or overwrite an older request. A CLARIFY decision cannot issue merchant-specific tools or mutate an owner. Never put unresolved merchant data in another merchant's transcript.

Freeze the decision and its evidence atomically with exactly-once original/selection association. A retry after crash reuses that persisted decision and original identities, not a fresh model guess. Before final admission recheck sender/recipient, candidate assignment still open and contacted, prompt still the exact confirmed offered option, content/moderation hashes, configured policy and template revisions, control revision, service window and STOP/expiry. Changed policy/template before admission, changed control/eligibility or stale offered candidates holds/reclarifies; it must not reinterpret the old option against a new prompt or silently reassign the original. After successful atomic admission the immutable terminal resolution wins on replay; later edits cannot admit again. A human-mode interval does not delete the pending original, and switching back to AI rechecks the current control revision. UNKNOWN prompt send remains uncertain without automatic resubmission.

## Maintenance decision — explicit five-table ownership

The user selected five routing tables for understandable, directly inspectable thread/shop generations. Three tables would store fewer objects but reconstruct grouping with joins and application locking. Five makes those identities and lifecycle relations explicit; it still needs runtime queries, same-owner validation, recipient serialization and eligibility checks. No claim of zero inference or business validation by FK is made. Allowance renewal remains independent.

## Independent allowance storage — DATABASE-002

New table `billing.ConversationAllowanceBlock`, deliberately reusing existing financial/provider evidence:

| Fields | PostgreSQL type / nullability |
| --- | --- |
| id | TEXT PK, client cuid |
| shopId, conversationId | TEXT NOT NULL |
| ordinal | INTEGER NOT NULL, nonnegative |
| fundingKind | VARCHAR(16) NOT NULL: INITIAL, FOLLOW_UP, CONTINUATION |
| state | VARCHAR(16) NOT NULL: PENDING, ACTIVE, EXHAUSTED, CLOSED, CANCELLED |
| predecessorId, creditReservationId | TEXT NULL |
| hardMessageLimit, terminalReservedSlots | INTEGER NOT NULL; derive normal limit as hard minus reserve |
| repairAt, repairLeaseUntil, repairDeadlineAt | TIMESTAMPTZ(3) NULL |
| repairLeaseToken | TEXT NULL |
| createdAt, updatedAt | TIMESTAMPTZ(3) NOT NULL DEFAULT now() |

Add `ConversationMessage.allowanceBlockId TEXT NULL`. No duplicated financial/dispatch state: reservation status/source key come from exact UsageReservation, admitted/unknown/confirmed provider results from pinned messages and existing delivery parts. No opening-message FK, logical-source column, message counters or extra timestamps duplicating those records. A deterministic continuation admission source derives from immutable block ID; preserve the exact resulting reservation link, including period-qualified source keys.

Unique `(conversationId,ordinal)`, `(id,conversationId)`, creditReservationId (NULL allowed). Independent partial unique one ACTIVE per Conversation and one PENDING per Conversation. No unique predecessor: cancelled intent can have a later replacement with a fresh monotonic ordinal. Conversation/shop FKs ON DELETE CASCADE. Composite `(creditReservationId,shopId)` → UsageReservation(id,shopId), predecessor `(predecessorId,conversationId)` → block(id,conversationId), and message `(allowanceBlockId,conversationId)` → block(id,conversationId): NO ACTION DEFERRABLE INITIALLY DEFERRED, permitting whole-owner cascade while rejecting isolated evidence deletion.

Owner trigger validates RECOVERY → CheckoutRecovery.shopId and lower-ordinal same-owner predecessor, compatible with legacy nullable Conversation.shopId. Message block pin immutable at insert, including rejection of later NULL→block retagging. Funding identity/reservation immutable after binding. CHECK ordinal≥0, hard>0, reserve≥0 and reserve≤hard, lease token/time paired, INITIAL ordinal0 without predecessor, successor with predecessor, and required reservation proof for funded successor. PENDING may exist before reservation acquisition. Application revalidates reservation status/provider evidence across I/O; SQL CHECK cannot prove external financial state. Index message block and partial PENDING repair due `(repairAt,id)`.

Existing NULL messages remain initial block-zero usage; lazy initial adoption only with proven historical original funding, no mass backfill or invented credit. Repair fields are necessary because current pending-turn repair filters AI pending turns and can miss unresolved funding after mode/turn changes. Extend existing repair scheduling to independently discover due PENDING blocks; do not create a competing generic worker. PENDING requires repairDeadlineAt. repairAt may become NULL when bounded repair parks uncertain evidence with a visible incident; the PENDING intent still blocks a new successor. Clear leases when parked and scheduling on terminal states. Token-fence every funding transition. Lease expiry never authorizes resend. Deadline bounds automatic attempts, never permits uncertain resend/refund.

## Independent allowance lifecycle — BACKGROUND-005

On exhausted allowance emit one merchant SYSTEM notice keyed Conversation+exhausted ordinal. No debit simply for crossing the cap. Next genuine automated continuation uses one eligible canonical credit against new explicit continuation source identity, same Conversation/recovery/history. Existing paid admission drops custom sourceKey when outreachAttemptId is absent; explicitly fix that path, do not fabricate sequence-two IDs. Create the unique PENDING intent under Conversation owner lock BEFORE any reservation I/O. Its immutable block ID is the deterministic source identity across every credit bucket. Reserve outside locks, then re-lock/token-fence and attach the exact reservation once (NULL→ID, never replace). Recheck owner/current block/control/window/STOP before model/provider permit.

One ACTIVE predecessor may coexist with one unresolved successor. CONTINUATION requires exhausted predecessor. Legitimate future FOLLOW_UP uses its own exact sequence-two reservation once to fund successor (followup send consumes first slot), without extra continuation debit; preserve cancellation on customer return. Confirmed successor opening settlement atomically closes predecessor and activates successor. Definitive pre-permit no-send cancels/releases; cancelled identity is never reused. UNKNOWN/ADMITTED cannot be refunded or resent merely because time elapsed. Bounded work lease and existing repair tick reclaim provable work; exhausted automatic retries expose operational reconciliation with retained proof. Late failed opening compensates only if no other provider-admitted block consumption; otherwise preserve funding and expose incident. Zero credit holds the original request for existing capacity repair; no rerouting, auto-purchase, history reset or cap bypass. HUMAN sends do not renew automated allowance; funding never extends Meta service window or changes controlMode.

## Rollout, security and observability

Production-compatible additive migration; preserve queued events/current provider evidence, no obsolete-format runtime adapters. Parent definition edits do not activate functionality. Root must hold affected production auto-deploy before runtime merges, migrate/deploy test first and verify focused/manual test behavior before production approval. User explicitly defers SYSTEM-TEST-001: leave it Pending and unexecuted; do not claim integrated architecture validation. Owner unit/component/disposable PostgreSQL/provider-fixture checks remain required. Architecture is not Implemented until required integrated validation is later accepted.

Use existing Shared logging and framework telemetry. Emit bounded domain decisions with request/assignment/block/config IDs and environment, never secret credentials, complete customer content or cross-shop candidate facts. No new Render service, public route, transport or Shared publication is required; existing worker repair ticks and protected connections are reused. If implementation reveals missing infrastructure, stop for owner task rather than inventing it.

## Tasks

| Task | Owner | State | Direct dependencies |
| --- | --- | --- | --- |
| ARCH-076-DATABASE-001 | moda_database | In progress, active attempt1 | None |
| ARCH-076-ADMIN-001 | moda_admin | Pending | DATABASE-001 |
| ARCH-076-BACKGROUND-001 | moda_background | Pending | DATABASE-001 |
| ARCH-076-BACKGROUND-002 | moda_background | Pending | BACKGROUND-001 |
| ARCH-076-BACKGROUND-003 | moda_background | Pending | BACKGROUND-002 |
| ARCH-076-ADMIN-002 | moda_admin | Complete | None |
| ARCH-076-ADMIN-003 | moda_admin | In progress, task-branch attempt1 | None |
| ARCH-076-BACKGROUND-004 | moda_background | Pending | BACKGROUND-003, ADMIN-002, ADMIN-003, COMMERCE-001 |
| ARCH-076-DATABASE-002 | moda_database | In progress, attempt1 | None |
| ARCH-076-BACKGROUND-005 | moda_background | Pending | DATABASE-002 |
| ARCH-076-COMMERCE-001 | moda_commerce | Ready | None |
| ARCH-076-SYSTEM-TEST-001 | moda_system_test | Pending, user-deferred | ADMIN-001, ADMIN-002, ADMIN-003, BACKGROUND-004 |

All dependency labels in this table abbreviate the ARCH-076 prefix. See authoritative domain indexes under docs/decisions/{database,background,admin,system-test}/ARCH-076. D001 and independent D002 are active attempt1; ADMIN002 is Complete; ADMIN003 has a canonical task-branch attempt1 claim at 2026-11-15T13:00:12Z (its merged-main definition remains Ready until that task branch is integrated). Dependent definitions remain Pending. D002 and BG005 independent of sender tasks. ADMIN002/003 independent of sender schema. No non-system-test task depends on SYSTEM-TEST.

## Change history

Original ARCH076 sender proposal retained in Git history. 15 November: preserve completed chronological ARCH069; retain explicit five-table ownership/request design; separate renewed credit accounting from routing; configure router through existing model/prompt/config machinery; preserve prepared claim and user-authorized implementation frontier.

15 November R15: restore explicit independent-question/selection roles and frozen decision evidence without adding grouping tables or coupling renewal. This is a definition amendment only.

15 November R15 ownership amendment: user selects five explicit routing entities; restore thread/route generations without changing allowance design or decision-role semantics.

15 November execution authorization: user approves implementation of the five-table sender design, independent allowance renewal, configurable router and R15 behavior. D001 prepared attempt1 resumes; D002/ADMIN002/ADMIN003 Ready with no dependencies. All other implementation tasks wait for accepted prerequisites. SYSTEM-TEST remains deferred; test-first production rollout remains mandatory.

## R15 evidence privacy and destructive cleanup amendment

routingDecision contains only structural roles, identities, offsets and hashes; never customer plaintext, model reasoning or copied basket facts. Exact original and new-clause wording remains in immutable pending inputJson until atomic association writes the authentic owned ConversationMessage records. The decision then references those existing messages and clause boundaries; no second durable plaintext copy is retained. Retries recover exact pending text or those associated messages, validate hashes and do not paraphrase. Terminal RESOLVED/EXPIRED/IGNORED cleanup clears inputJson, candidatesJson, moderationJson and promptText; configurationSnapshot stores revision/parameter evidence only, never customer content. If any transient configuration payload contains customer content it must be scrubbed too. routingDecision remains immutable hash/identity evidence; deletion of an authentic message fails closed for replay, not reconstruction from hidden retained plaintext.

Freeze original input, candidate snapshot and configuration snapshot once captured; freeze parent request and role scope when decision is recorded. Ordinary retries cannot replace them. Only explicit destructive terminal cleanup (value→NULL, never replacement) and FK SET NULL cleanup on actual referenced-object deletion may remove evidence. A deleted parent/selected pointer cannot be rebound. Scrub is atomic with terminalization/association, and database guards distinguish this permitted destruction from reauthoring input or choice evidence. Test a terminal record cannot resurrect payloads. Payload retention is bounded by the frozen expiresAt; UNKNOWN provider dispatch retains necessary identifiers/uncertainty without permitting indefinite plaintext retention.

## Parent request binding and routing prompt publication refinement

Persist the inbound routing row before calling the model. parentProviderMessageId may bind NULL→the exact existing original request ID once after classification, under same-thread/evidence guards. It is not INSERT-only. Once bound it cannot be cleared or rebound, including after a decision. The parent FK is NO ACTION DEFERRABLE INITIALLY DEFERRED, not SET NULL: physical retention cleanup deletes eligible parent and dependent requests as one cohort after their retention obligations expire, or deletes the whole thread cascade atomically. It must not orphan a live dependent request. selectedConversationId binds only atomically with the frozen decision; actual Conversation deletion may SET NULL but cannot authorize later reassociation. These rules supersede the earlier generic parent FK cleanup exception.

The existing platform Commerce prompt lineage has one PLATFORM prompt, and ordinary publication also activates the normal agent. Routing publication must reuse that lineage's revision machinery without its normal activation side effect: publish a distinct revision tagged in sourceContextJson with purpose RECOVERY_ROUTING, then point only recovery.routingAgent.promptRevisionId to it. Do not mutate CommerceAgentConfiguration.activePromptRevisionId, promptEditVersion or effective normal Commerce prompt. Ordinary Commerce activation rejects routing-tagged revisions; router activation requires a published platform revision with the routing purpose tag and expected hash. Admin owns role authorization, CAS/audit and this separate publish/activation flow; no new prompt table or database schema is required. Test routing draft/publish/configure leaves normal model/prompt pointers and versions unchanged, rejects ordinary activation of tagged revisions, rejects untagged/draft/foreign routing activation, and handles concurrent normal/router publication without clobbering either reference.

## R15 immutable classification versus later resolution

Each inbound routingDecision records that inbound's classification; it does not mean the original request is already resolved. Q1 “Can it arrive Friday?” may freeze CLARIFY, then receive a confirmed clarification prompt and remain pending. Q2 selection freezes SELECT_ONLY or SELECT_AND_QUESTION referencing Q1's exact prompt/candidates. Preserve Q1's CLARIFY decision permanently; do not replace it with Q2's classification.

Add nullable `RecoveryBasketRoutingTurn.resolutionInboundProviderMessageId TEXT`, self-FK → inboundProviderMessageId NO ACTION DEFERRABLE INITIALLY DEFERRED. This is an explicit immutable resolution witness, distinct from the classifier decision and parent relation. In the owner-locked transaction that admits the original, bind Q1.selectedConversationId and Q1.resolutionInboundProviderMessageId=Q2 together, set Q1 resolved/terminal timestamps and scrub transient payloads. Q2's frozen decision must reference Q1, the exact confirmed prompt, eligible same-thread/route offered assignment and current policy/moderation/control evidence. Initial owner/witness binding remains permitted when Q1.routingDecision is already CLARIFY; after binding neither can be changed or cleared by ordinary writes. Actual selected Conversation FK SET NULL still preserves immutable witness and cannot permit rebinding.

A directly attributed NEW_QUESTION may resolve with witness=self, admitting only its current question; it never resolves older pending Q1. A resolving child may also record its own self-resolution, therefore do NOT globally UNIQUE the witness column. Child.parentProviderMessageId plus same-owner transaction locks and witness validation constrain a selection to its intended original; no reverse-child search or newest-prompt inference. Retention deletes dependent witness/parent cohorts atomically after eligibility or through whole-thread cascade. No extra table or index is needed merely for this scalar proof.

Required positive PostgreSQL case: persist Q1, freeze CLARIFY, admit/confirm prompt, persist Q2 with exact parent and SELECT_ONLY, bind Q1 owner+witness and admit original exactly once, preserving both classifier decisions and exact original message content. Also test SELECT_AND_QUESTION exact clause admission, independent NEW_QUESTION leaving Q1 pending, concurrent Q2/Q3 attempts, replay after crash, wrong-parent/prompt/thread/assignment forged witness, terminal rebinding and deferred retention deletion. SQL enforces structural identity/freeze; application revalidates current eligibility and authentic evidence.

15 November ADMIN002 accepted and automatically Complete: tested Admin source4bfefc5 merged main5558daadd (identical Git tree). Parent gitlink records actual merged main. BG004 still waits for BG003 and ADMIN003; SYSTEM-TEST remains deferred.

Completion frontier correction: D001 active implementation, D002 claimed attempt1 at 2026-11-15T12:59:02Z, ADMIN003 canonical branch claimed attempt1 at 2026-11-15T13:00:12Z. ADMIN002 clears active claim fields on automatic completion while retaining historical evidence. No other task claim metadata is changed by this reconciliation.

## R15 explicit two-stage shop then basket clarification

This is the required unknown-shop→known-shop→basket flow, not an optional extension. Keep a star relation anchored to the substantive original, without recursive/newest-child search:

1. Q1 is the customer's substantive original (for example “Can it arrive Friday?”), parentProviderMessageId=NULL. Its frozen CLARIFY classification and exact original input remain authoritative; a neutral confirmed shop prompt may live on Q1.
2. Q2 is the verified shop-selection response. It binds parentProviderMessageId=Q1 once, uses that verified same-thread route and freezes its own CLARIFY decision when basket selection is still needed. Q2 holds the exact admitted/confirmed shop-scoped basket prompt and frozen offered candidate facts. Q1 is not resolved merely by choosing a shop.
3. Q3 is the basket-selection response. It also binds parentProviderMessageId=Q1 (not Q2). Its frozen role decision names originalTurnId=Q1 and promptTurnId=Q2 plus the exact Q2 confirmedPromptProviderMessageId and offered assignment/option. SELECT_ONLY resumes only Q1; SELECT_AND_QUESTION admits Q1 plus the authentic moderated Q3 new clause.
4. Resolve Q1 once with resolutionInboundProviderMessageId=Q3 and selectedConversationId in the same owner-locked transaction as original admission and destructive scrub. Preserve Q1/Q2 CLARIFY decisions and Q3 selection decision; no synthetic replacement question or new Conversation.

Prompt validation reads the explicitly named prompt ID only. Require promptTurnId==Q1 OR that exact prompt row's immutable parentProviderMessageId==Q1; same thread, compatible verified route, frozen promptScopeRouteId and confirmed receipt must agree with the selected route/assignment and original. A neutral original prompt scope may remain NULL; a later basket prompt retains its exact verified route scope. Reject a prompt belonging to another original, foreign thread/shop, unconfirmed prompt, stale candidate or conflicting role—even if its display text/number matches. Do not infer prompt by reverse-child query, newest message, recursive ancestry or credit/allowance state. These rules require no new columns, tables or weakened evidence constraints.

Required positive disposable PostgreSQL/provider-fixture case: Q1 unknown-shop original→confirmed neutral prompt→Q2 verified shop selection→confirmed basket prompt on Q2→Q3 selection naming Q1/Q2 explicitly→exactly-once Q1 admission via Q3 witness. Include multiple simultaneous originals, Q3 additional exact question clause, duplicate/restart replay, forged Q2 from another root, wrong route/prompt scope, missing confirmation, expiry/control/template changes and concurrent resolution attempts. Keep SYSTEM-TEST deferred; these are owner task-local checks.

## Commerce Studio routing-purpose isolation

ARCH-076-COMMERCE-001 (moda_commerce, Ready, no dependencies) closes the existing Studio setPointer/read/seed gap for RECOVERY_ROUTING-tagged revisions. It preserves exact-scope/auth/CAS and actual shared-lineage revision numbering. ADMIN003 source remains independently acceptable; BG004 acceptance and live routing activation require this Commerce task Complete. No schema or Shared change. SYSTEM-TEST depends on this final owning implementation and remains user-deferred.
