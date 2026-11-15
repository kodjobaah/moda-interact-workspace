# ARCH-076 final database proposal for review

User-authorized implementation contract; this document itself applies no migration or runtime change. User-selected five explicit sender tables plus one independent allowance table: six new tables total, three nullable ConversationMessage columns. No new Conversation, credit ledger or AI configuration table. Preserve DATABASE001 prepared attempt1; no new claims.

## Sender routing — DATABASE-001


Five tables in schema `whatsapp` retain explicit customer/sender and shop generations. This restores the original five-entity model while retaining the R15 decision evidence, configured policy and independent allowance stream. Historical executable SQL is not copied blindly: the reviewed field contract below includes new evidence fields and must drive fresh migration authoring after approval.

| Table | Exact proposed columns |
| --- | --- |
| WhatsAppPoolSender | providerPhoneNumberId VARCHAR(64) PK; providerAccountId VARCHAR(64) NOT NULL; priority INTEGER NOT NULL DEFAULT 0; allocationEnabled BOOLEAN NOT NULL DEFAULT false; verifiedAt TIMESTAMPTZ(3) NOT NULL; createdAt/updatedAt TIMESTAMPTZ(3) NOT NULL DEFAULT now() |
| RecoverySenderThread | id TEXT PK (client cuid); canonicalRecipient VARCHAR(15) NOT NULL; providerPhoneNumberId VARCHAR(64) NOT NULL; openedAt TIMESTAMPTZ(3) NOT NULL DEFAULT now(); closedAt TIMESTAMPTZ(3) NULL |
| RecoverySenderRoute | id TEXT PK (client cuid); shopId TEXT NOT NULL; threadId TEXT NOT NULL; canonicalRecipient VARCHAR(15) NOT NULL; providerPhoneNumberId VARCHAR(64) NOT NULL; openedAt TIMESTAMPTZ(3) NOT NULL DEFAULT now(); closedAt TIMESTAMPTZ(3) NULL |
| RecoverySenderAssignment | conversationId TEXT PK; routeId TEXT NOT NULL; assignedAt TIMESTAMPTZ(3) NOT NULL DEFAULT now(); releasedAt TIMESTAMPTZ(3) NULL |
| RecoveryBasketRoutingTurn | inboundProviderMessageId TEXT PK; threadId TEXT NOT NULL; routeId TEXT NULL; promptScopeRouteId TEXT NULL; occurredAt/createdAt TIMESTAMPTZ(3) NOT NULL (createdAt DEFAULT now()); inputJson/candidatesJson/moderationJson JSONB NULL; configurationSnapshot/routingDecision JSONB NULL; parentProviderMessageId TEXT NULL; state VARCHAR(24) NOT NULL DEFAULT 'RECEIVED'; selectedConversationId TEXT NULL; promptText TEXT NULL; promptAdmittedAt/promptSentAt TIMESTAMPTZ(3) NULL; promptProviderMessageId TEXT NULL; expiresAt TIMESTAMPTZ(3) NOT NULL; resolvedAt TIMESTAMPTZ(3) NULL; workToken TEXT NULL; workLeaseUntil/nextRepairAt TIMESTAMPTZ(3) NULL; repairAttempt INTEGER NOT NULL DEFAULT 0; updatedAt TIMESTAMPTZ(3) NOT NULL DEFAULT now() |

A WhatsApp physical chat thread (RecoverySenderThread) is NOT a new checkout Conversation. Thread is one immutable recipient/sender generation; route is one immutable shop ownership generation on that thread; assignment links each existing recovery Conversation to its route. A routing request always has exact threadId; unknown-shop request has routeId NULL. Once shop is verified, routeId may bind once to a route on that same thread. promptScopeRouteId freezes the prompt's actual scope at admission: NULL for a neutral prompt, even when the original later binds to a shop. Neither field is inferred later from the selected Conversation.

FKs and deletion actions:

- Thread.providerPhoneNumberId → inventory providerPhoneNumberId, RESTRICT; inventory exposes unique `(providerPhoneNumberId,providerAccountId)` for exact sender-account evidence.
- Route.shopId → Shop.id CASCADE; `(threadId,canonicalRecipient,providerPhoneNumberId)` → Thread matching unique target, CASCADE. Route identity fields immutable.
- Assignment.conversationId → Conversation.id CASCADE; routeId → Route.id NO ACTION DEFERRABLE INITIALLY DEFERRED. Isolated route/thread deletion cannot detach a surviving Conversation and permit a new sender assignment; whole-shop deletion succeeds only when both owning Conversation and route cascades complete. Assignment conversationId/routeId/assignedAt immutable; release monotonic.
- Turn.threadId → Thread.id CASCADE; parentProviderMessageId → Turn.inboundProviderMessageId SET NULL; selectedConversationId → Conversation.id SET NULL. Immutable resolved decision retains historical identity and cannot be rebound when a pointer is deleted.
- Turn.routeId and promptScopeRouteId are historical scalar scope stamps deliberately without cascading shop FKs. A guard verifies referenced route exists on exactly this thread at initial binding/prompt admission. If shop/route is physically deleted, retain the original scope stamp and terminalize/scrub affected pending input; never convert it back into a neutral selectable request or another shop. Neutral requests on a surviving thread remain neutral. Closed routes/threads remain historical rows until owner deletion; status evidence stays on existing provider messages.

Uniqueness/indexes: partial unique live Thread `(canonicalRecipient,providerPhoneNumberId)` WHERE closedAt IS NULL; unique Thread `(id,canonicalRecipient,providerPhoneNumberId)` composite target; partial unique live Route `(canonicalRecipient,shopId)` WHERE closedAt IS NULL; assignment Conversation PK; unique non-null promptProviderMessageId. Index Route `(threadId,closedAt,shopId)`, Assignment `(routeId,releasedAt)`, Turn `(threadId,state,occurredAt)`, partial pending expiry/due indexes, and enabled inventory allocation order. Inbound provider identity remains immutable global provider ID as in the existing ingress/message contract; verify its receiving WABA/sender through the pinned thread, never trust ID alone.

Identity guards make inventory providerPhoneNumberId AND providerAccountId immutable; Thread id/recipient/sender/openedAt immutable; Route id/shop/thread/recipient/sender/openedAt immutable; Assignment conversationId/routeId/assignedAt immutable. Thread/Route closedAt and Assignment releasedAt permit only a monotonic NULL→timestamp transition. No generation identity can be updated to transfer history.

CHECK digit-normalized sender/WABA/recipient, nonnegative priority/repairAttempt, paired work lease, time ordering, state allowlist RECEIVED/PROMPT_ADMITTED/PROMPT_UNKNOWN/RESOLVED/EXPIRED/IGNORED, prompt evidence consistency and terminal input scrubbing. Owner/identity guards require RECOVERY assignment Conversation's recovery shop equals route shop, compatible with legacy nullable Conversation.shopId. Same-thread prompt/parent/selected-assignment guard and application transactions prevent cross-scope binding. routingDecision is nullable until one structural versioned decision freezes; semantic business evidence validation belongs to Background. candidatesJson freezes offered assignment Conversation IDs and complete safe candidate facts; no fictitious JSON foreign keys.

Add nullable paired ConversationMessage.dispatchProviderAccountId/dispatchProviderPhoneNumberId VARCHAR(64) root permit evidence; preserve current ordered-part sender/status proofs. No sender credit fields, additional Conversation or mass history migration. Upgrade 80 predecessor migrations through `20261113111320_arch075_meta_app_operation_state`, then target `20261113120000_whatsapp_sender_pool`. Final SQL object counts must be regenerated for these new evidence fields, not asserted from the historical migration.


## Independent allowance — DATABASE-002


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


## Separation and review

Sender tasks have no allowance prerequisite. Configurable AI uses existing PlatformConfiguration/catalogue/published prompt machinery; neutral ROUTER template is application owned. R15 role decisions persist in routingDecision and remain subject to the exact parent question/clarification contract. No runtime or migration is implemented.
