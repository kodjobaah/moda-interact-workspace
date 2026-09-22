# ARCH-020 binding implementation contracts

This is a normative companion to the architecture and task definitions, authored
on local main for review. It defines requested behaviour, not implemented features.
All ARCH-020 tasks must use the same definitions below. An executor may choose
internal helper/file names unless a deliverable name is specified, but must not
change wire fields, ownership, state transitions, bounds or test outcomes.
User-confirmed decisions take precedence. Any conflict with existing source is
reported to the architect rather than resolved by inventing a second contract.

## C0. Existing WhatsApp boundary — reuse, do not redefine

Inspected `moda-interact-shared/src/whatsapp.ts`, `src/whatsapp.test.ts` and the
status schema in `src/billing.ts`. The existing `./whatsapp` inbound v1 contract
already supplies providerAccountId, providerPhoneNumberId, providerMessageId,
customerPhone, nullable contextMessageId, occurredAt and a strict text/audio/
unsupported union. Identifier bounds256, phone64, text4096; timestamps permit
explicit UTC offsets. It trims strings but does not validate phone ownership or
normalise national numbers. Its tests reject shopId, conversationId,
checkoutRecoveryId and rawPayload. Keep this producer/consumer wire shape and
version unchanged. Do not add tenant/routing/grant fields to webhook events,
redefine a Background-local inbound DTO or change text/audio handling at ingress.
Use safeParseNormalizedWhatsAppInboundMessage before routing and the inferred
NormalizedWhatsAppInboundMessage type. WhatsApp Reply's ID is contextMessageId;
ordinary messages carry null, not an empty string or missing key.

Status events use the separate `./billing` NormalizedWhatsAppStatusSchema v2:
sender account/phone/message IDs (max128), status SENT/DELIVERED/READ/FAILED,
occurredAt and optional pricing. It contains no recipient or provider error
message. Preserve it; look up ownership from stored sender/message evidence.
Do not infer a recovery from a delivery receipt or invent an error payload.
The new Commerce IDs' max128 does not change WhatsApp inbound IDs' max256.

No Messaging implementation task or inbound version bump is required for this
routing design. Background consumes fields already present. No new WhatsApp
database columns, processing-version fields or routing-receipt table are required.
Both producer and consumer contract fixtures remain part of terminal validation.

## C1. Ownership, order and feature selection

Only Background sends customer WhatsApp messages or invokes the production model.
Commerce performs read-only Shopify/tool work and manages staff-authored content.
Shared contains pure schemas/helpers and an injected runner; no Prisma, credentials
or provider discovery. Database owns all Prisma/SQL, including routing metadata.

The ordered path is: authenticate inbound sender -> route -> persist inbound ->
settle/claim conversation turn -> existing admission -> load/create grant -> model
and tools -> recheck version/lease/permissions/evidence -> send -> complete.
Uncorrelated identification guidance uses C3, not this agent path.

Capabilities are selected in release membership `position` order. BASE selects
`conversation_core` only (platform grounding/referral instructions, no mandatory
product tools). FEATURE selects when Feature.active AND the authoritative
current plan includes an enabled mapping AND (ALWAYS_ENABLED OR the
MERCHANT_OPT_IN preference is explicitly enabled). Missing opt-in means false. System-required
features cannot be toggled by this UI; do not use systemRequired to invent an
entitlement bypass absent from the current effective-billing-policy resolver.
RECOVERY_POLICY selects `discount_assistance` only when effective offer mode is
FIXED or AI_BEST_APPLICABLE, with existing unexpired Admin override precedence.
No paid-only discount feature is added. Effective policy is computed by adapters
using existing accepted billing/recovery-policy resolvers, never by model input.
Unknown plan/policy facts deny the affected capability, not assume eligibility.
A disabled BASE prevents a new grant; later revocation restricts existing grants.

Feature additions never expand existing grants. Removing permission denies tools
immediately. Re-enabling an originally granted capability can restore the same
original tool/version, but cannot add a different version, tool or capability.
Tool definitions are stored in CommerceToolRevision.definition and associated
through CommerceCapabilityRevision.toolBindings. Each definition has an exact SemVer
definitionVersion and a separately pinned query executorVersion or policy operationVersion. A new
supported definition, input schema or response template can be published without
deploying Commerce or Background. New public Shopify queries use the C14 generic executor without code changes;
new integration or privileged execution primitives require reviewed Commerce code. See C14 for the binding definition and example.

Capability BASE/FEATURE/RECOVERY_POLICY binding selects its database-defined
tools for the merchant. Existing capability -> Feature linkage is the mapping;
do not add a duplicate merchant feature catalogue or a redundant featureKey on
each tool definition. Tool names are globally unique; identical tool revisions across capabilities
deduplicate, conflicting revisions in one release are rejected.
Discount operations enforce current offer policy regardless of their display name
or feature binding. Renaming/rebinding a tool cannot bypass that restriction.
Local finalResponse remains outside remote tool definitions and grants.

## C2. Single-number recovery routing and existing batching

Moda owns one configured WhatsApp account/number serving every merchant. Merchants
need no WhatsApp account/number. Existing shared providerAccountId and
providerPhoneNumberId may be validated against that fixed configuration, but never
identify the merchant. No sender pool, number selection, new sender/recipient
columns or multi-number provisioning is in scope.

Canonicalise phones by trimming/removing a leading +; do not guess a country.
The same phone may belong to separate Customer records at different shops.
Never choose the first Customer row or merge those records globally.

Explicit contextMessageId: find the existing OUTBOUND ConversationMessage by
providerMessageId, require sentAt and a real Conversation.checkoutRecoveryId,
and verify the recovery customer's phone matches the inbound customerPhone.
Resolve shop ownership through that recovery. Unknown/wrong-customer references
must not fall back to phone-only routing or reveal another shop/basket. A later
FAILED delivery status does not erase a known sent message's correlation link.

No reference: query distinct CheckoutRecovery IDs across all shops where the
related customer's canonical phone matches and its unique Conversation contains
at least one OUTBOUND message with non-null providerMessageId and sentAt. Use
DISTINCT LIMIT 2 to distinguish zero/one/multiple; do not count outreach messages.
No recency/status filter: retained outreach for completed/expired/cancelled
recoveries also makes a message ambiguous. Do not exclude unavailable shops before
counting merely to manufacture one match. Use existing columns; no metadata
backfill or migration. Recovery generations remain distinct IDs.

- Exactly one: route automatically to its existing Conversation, then check shop
  execution eligibility. No identification question. Actual recovery status is
  authoritative; do not claim a completed/expired basket is still active.
- Multiple: send C3 Reply-option guidance; no agent/grant/engagement mutation.
- Zero: send C3 no-recovery guidance; no standalone conversation.
- Invalid explicit reference: C3 invalid-reference guidance, not fallback routing.
- Shop execution denied after valid routing: C3 store-contact guidance, no agent.

Initial outreach/follow-up/agent messages in one Conversation all identify the
same recovery. Never choose among multiple recoveries by elapsed hours, latest
outreach, remembered channel or a model guess. Every unreferenced follow-up uses
the same rules. Respond through the single configured Moda number.

Preserve existing quiet/max-settle batching, conversation inboundVersion,
lastProcessedVersion, timestamp-based fragment collection, leases and stale-turn
checks. Do not add receivedInboundVersion or redesign batch membership in this
architecture. Any demonstrated delayed/out-of-order batching defect is a separate
review item, not an implicit routing schema expansion.

Repair missing conversational context without a schema change: keep existing
current-fragment selection, prepend up to20 earlier customer/assistant messages
from the same Conversation ordered by createdAt,id, and deduplicate by message ID.
Include sent outbound messages only; exclude unsupported/pending transcription
content and failed-before-send placeholders. Never include another recovery or
rely on the unmaintained summary. History is not fresh product/discount evidence.
Bound history at32,000 Unicode code points by dropping oldest prior messages;
if current fragments alone exceed the bound, send a fixed shorter-question request
through normal admitted handling without model work. Test “yes, the second one”.

## C3. Lightweight platform identification guidance

Background owns a small fixed-text helper using existing Redis and the configured
WhatsApp transport. No new database table, migration, conversation, agent session,
outreach attempt, grant or merchant UsageEvent is created for this guidance.
The provider cost is platform-owned, not attributed to a guessed merchant. This
helper accepts a validated inbound event and a closed reason enum, never arbitrary
caller/model text, recipient or URL. Only raw-abuse-admitted text/audio events can
trigger it; route before audio download. Ignore unsupported inputs/status events.

| reason | English v1 text |
|---|---|
| MULTIPLE_RECOVERIES | Please use WhatsApp's Reply option on the basket message you'd like help with, so I can identify the right checkout. |
| NO_RECOVERY / INVALID_REFERENCE | Please use WhatsApp's Reply option on the basket message you'd like help with, so I can identify the right checkout. If you cannot find that message, please contact the store directly. |
| SHOP_UNAVAILABLE | Please contact the store directly for help with your basket. |

No model language detection, merchant inference or basket listing. Normal agent
referrals keep their existing language contract. A reply to this guidance does
not identify a recovery: only a stored recovery-linked outbound reference does.

After existing raw sender/global abuse admission, atomically claim Redis key
`moda:<environment>:whatsapp:clarification:<sha256(inbound providerMessageId)>`
using SET value=1 NX EX 86400. A duplicate/non-winning claim returns without sending.
The one claim winner sends the selected fixed text to the event's customerPhone
through the one configured Moda number, with a bounded 10-second provider timeout.
Redis errors suppress the guidance; never send without the guard. Use the existing
Redis connection; no new secret, service, budget ledger or SQL rate-limit locks.

Set the guard BEFORE sending and retain it for its full 24-hour TTL on success,
failure, timeout or cancellation. Do not delete it on error, release it for retry,
retry the provider call automatically, or treat it as proof of confirmed delivery.
A worker crash between claiming and sending can lose that clarification. Redis
loss/eviction or delivery of the same event after expiry can allow a duplicate.
These are accepted best-effort trade-offs, not exactly-once delivery guarantees.
A new customer message has a different providerMessageId and may trigger new
guidance, still subject to existing raw-abuse limits.

Log only bounded outcomes (sent,duplicate-suppressed,redis-unavailable,
send-failed-or-uncertain); no raw phone/body/credentials. Do not add provider-status
tracking for unpersisted guidance messages: the existing unknown-message status
path produces no merchant usage or resend. No administrative reconciliation UI,
receipt-retention job or durable send-state machine is required.

## C4. Shared wire contract

Export named strict Zod schemas and inferred types from `./commerce`; unknown
keys fail. `contractVersion` is exactly `commerce.v1`; runner API version starts
at SemVer `1.0.0`. IDs are nonempty strings <=128 characters, not the sentinel
`standalone`, `product-only` or `unknown-shop`. Validation proves shape only;
services must prove existence and cross-tenant ownership against persistence.
Dates are UTC ISO strings, money is a nonnegative decimal string with <=18 integer
and <=6 fractional digits, currency is uppercase ISO code validated against the
existing currency resolver. No floating-point monetary arithmetic.

Named contracts:

- CommerceTurnIdentity: {contractVersion, shopId, checkoutRecoveryId,
  conversationId, inboundVersion}; inboundVersion is a positive integer.
- CommerceConversationGrant: DATABASE-001's persisted fields with timestamps in
  ISO form and environment casing mapped to lower case where used. No browser
  can create a production grant. selectedCapabilityKeys max32; grantedTools max32 (zero is valid). The grant runnerVersion records the original host version; later hosts
  must satisfy the pinned release runnerCompatibility and contractVersion, not
  overwrite the grant or automatically upgrade any tool/prompt.
- CommerceManifest: {contractVersion, releaseId, runnerCompatibility,
  capabilities:[{key,revisionId,position,promptName,configuration,toolDescriptors}],
  selectedCapabilityKeys,grantedTools,responseContract,responseContractHash}; capability order is release position,
  all IDs and grant entries must agree with the immutable release/grant.
  toolDescriptors contain only toolId,toolRevisionId,name,definitionVersion,description,inputSchema;
  execution and responseTemplate stay on Commerce, not in the host manifest.
- CommerceToolResult<T>: {contractVersion, status:'OK', data:T, renderedText:string<=4096} OR
  {contractVersion,status:'ERROR',code,retryable,renderedText?:string<=4096}; error codes are INVALID_INPUT,
  DENIED, STALE_TURN, NOT_FOUND, UNAVAILABLE, THROTTLED, DEADLINE,
  INCOMPATIBLE_VERSION. Do not include arbitrary provider exception text.
- CommerceFinalResponse: {answerKind:'ANSWER'|'REFER_TO_STORE', replyText,
  referralReason, detectedLanguageTag, detectedLanguageConfidence, evidenceIds, details}.
  replyText 1..4096 characters; evidenceIds unique max3. ANSWER requires null
  referralReason. Referral requires the existing four-value reason enum and an
  empty evidenceIds array. Language tag/confidence are both null or both valid
  using existing internationalisation validators, confidence 0..1. Background
  renders referral text/contact itself; model text does not supply contacts.

Revision configuration is a strict object with optional maxRecommendations (integer1..3, default3) and maxSearchResults (integer1..20, default10); no other keys in v1. These settings only lower C6/C8 ceilings. Capability prompts are literal text with no template expression engine.

Common basket: {basketId,source:'RECOVERY_SNAPSHOT'|'PROPOSED',observedAt,
  currency,lines:[{lineId,productId,variantId,quantity,unitPrice}],fingerprint,
  unknownFields}. productId/variantId/unitPrice/currency and quantity can be null when provider data is
  unavailable; lineId remains a required stable snapshot identifier. Nonnull quantity
  is integer1..999; max100 lines, unknownFields a
  bounded array of schema field paths. Zero lines is a missing snapshot, never a
  free basket. basketId is a server-generated opaque fingerprint reference.
Product: {productId,variantId,title,url,available,unitPrice,currency,
  productType,vendor,observedAt}; unknown fields explicitly null, title <=512,
  URL HTTPS on verified canonical shop/store domain, no arbitrary provider hosts.
ProductId/variantId/title/observedAt are required. url/productType/vendor/unitPrice/
currency are nullable; available is boolean or null. Null availability is not
eligible for a recommendation. extraSpend is max(0, proposed gross basket total
minus original gross total); it is not the nominal discount or a guaranteed saving.

The baseline operation schemas below exclude shop/customer/recovery/token/domain/GraphQL.
C14 database definitions choose the actual exposed tool name/schema and may narrow
these inputs with mappings/literals; these are not six hard-coded MCP registrations:

| Tool | Exact arguments | Successful data |
|---|---|---|
| commerce_get_basket | {} | basket |
| commerce_search_products | {query:string 1..200,maximumPrice?:decimal string,availableOnly:boolean default true,limit:int1..20 default10,cursor:string<=2048 or null default null} | {products:max20,cursor:null or opaque string,truncated:boolean} |
| commerce_get_discount_options | {} | {mode:'NONE'|'FIXED'|'AI_BEST_APPLICABLE',offers:max50,truncated:boolean} |
| commerce_evaluate_discount | {offerId,proposal:null or Proposal} | Evidence |
| commerce_find_qualifying_products | {offerId,query:string1..200 or null,limit:int1..3 default3} | {alternatives:max3,truncated:boolean} |
| commerce_find_similar_products | {variantId,offerId:null or ID,limit:int1..3 default3} | {alternatives:max3,truncated:boolean} |

Proposal = {operations:[{kind:'ADD',variantId,quantity} OR
{kind:'REPLACE',lineId,variantId,quantity}]}, 1..3 operations, unique target line
for replacements, quantity1..999. Resolve all prices/ownership server-side.
Offer = {offerId,title,method:'AUTOMATIC'|'CODE',code:null or string<=128,
startsAt,endsAt,support:'SUPPORTED'|'UNSUPPORTED'|'UNKNOWN',reasonCodes:max16};
nullable dates/code, no fabricated code, offerId is the canonical catalogue row ID.
Alternative = {product,proposal,extraSpend,resultingTotal,currency,evidence:null
or Evidence,similarityReasons:max3}; null totals represent unknown facts.

Evidence = {evidenceId,turn:CommerceTurnIdentity,grantId,releaseId,offerId,
proposal:null or Proposal,basketFingerprint,ruleFingerprint,evaluatedAt,expiresAt,
outcome:'QUALIFIES_FOR_KNOWN_RULES'|'DOES_NOT_QUALIFY'|'UNKNOWN'|'UNSUPPORTED',
currency,savings,resultingTotal,evaluatedConditions,unresolvedConditions}.
Amounts/currency nullable when unprovable. Condition arrays max32 of bounded
{code:string<=64,description:string<=256}. Evidence expires 60 seconds after
evaluation, never later than offer expiry. Missing/unknown conditions prohibit
QUALIFIES_FOR_KNOWN_RULES. An expired offer returns DOES_NOT_QUALIFY with no usable
positive-evidence lifetime. Consumer must inspect outcome, not just evidence ID.

Evidence ID is SHA-256 of canonical complete evidence excluding evidenceId.
It is not a bearer credential or standalone proof. Runner registers actual tool
results in a turn-local evidence map; final evidence IDs must be a subset of that
map. Before delivery Background applies the exact-call refresh contract below
and replaces the proposed offer answer with a bounded referral on failure. Never
trust a model-supplied evidence object or accept a recomputed hash as authority.

### Exact-call evidence refresh (COMMERCE-004/014/016/007, BACKGROUND-002)

Background owns a turn-local provenance record for each registered evidence ID:
the actual successfully invoked granted tool name, its exact immutable revision,
a deep copy of validated call arguments, and the extracted trusted Evidence.
Capture this through the host tool wrapper/evidence extractor; no new Shared wire
field, database column, executor metadata disclosure or model-supplied provenance.
Only policy adapters can produce trusted Evidence; public GraphQL/template text
cannot. Commerce preserves structured Evidence independently of rendered text.

Before sending a claim, replay the evidence-producing call with identical arguments
and the same authenticated turn/grant. Never hard-code an example tool name, infer
an evaluator from its description, reverse-map authored inputs or add an ungranted
tool. Deduplicate identical calls within this final refresh pass. Charge every
refresh against the existing turn call/deadline budget; insufficient budget fails
closed. Recheck current permission at dispatch. A renamed evaluator or narrowed
literal/mapped input works because its actual original call is replayed unchanged.

For each referenced old evidence item require exactly one fresh structured item
matching offerId and canonical proposal (including null). Verify current turn,
grant/release, freshness and trusted origin, and identical outcome, currency,
savings, resultingTotal, basketFingerprint and ruleFingerprint. Timestamp/ID may
change. Recommendation replay must return the exact original proposal; a changed,
missing, duplicate, truncated or incomplete result cannot prove the claim. Absence
of a separately named evaluator does not block a valid exact-call refresh; absence
of replayable provenance, revocation, timeout or changed evidence yields one normal
admitted store referral. Recheck stale-turn/lease/send admission after refresh.

Required fixtures: renamed evaluator; narrowed/literal mapped input; evidence
from a recommendation without a separate evaluator; changed recommendation;
missing provenance; revoked producer; duplicate references sharing one refresh;
and exhausted call/deadline budget. Assert zero ungranted calls and no extra sends.

Canonical hashes: recursively sort object keys by Unicode code point, preserve
array order, reject undefined/nonfinite numbers and encode compact UTF-8 JSON.
Sort toolBindings by toolId before storing. Capability hashes exactly
{contractVersion,promptTemplate,configuration,toolBindings}; tool hashes exactly
{contractVersion,definition}; basket/rule hashes include all normalised semantic fields,
exclude observation timestamps, and include currency. Shared exports the pure
canonical encoder; use Node SHA-256 only in server adapters. Bound aggregate
HTTP input at128KiB, output at256KiB and prompt bundle at64,000 characters.
JSON database-size checks remain as separately defined in DATABASE-001.

## C5. MCP, service assertions and failure semantics

Use only POST `/api/mcp` for JSON-RPC Streamable HTTP requests, stateless per
request, JSON responses in v1. GET/DELETE return405, no SSE/session dependency,
no alternate transport path. COMMERCE-001 proves the chosen client/SDK supports
this profile with pinned versions; an unsupported profile is an architect issue,
not an invitation to expose a second endpoint. Maximum10 seconds per tool call.
MCP initialize/notifications follow the tested SDK profile; methods not named
below are rejected. No batch request support. Hosted requests with an Origin
header are rejected on MCP; CORS is not an authentication substitute.

Authorization is a short-lived RS256 JWT, fixed issuer `moda-background`, subject
`moda-messaging-worker`, audience `moda-commerce`, environment equal to deployment,
claims iat/exp/jti plus CommerceTurnIdentity and purpose `resolve` or `execute`.
Lifetime <=120 seconds; clock skew <=5 seconds; kid must name a configured public
key; reject none/HS algorithms, remote jwks/jku and unknown kids. Execute also
requires grantId/releaseId. Resolve forbids those claims. No preview purpose on
this endpoint. Key rotation accepts a bounded configured set (max2 keys); only
Background has private keys. Repeated signed assertions within a turn are allowed;
this is not a one-use token. Each call validates current processing version/lease,
ownership, grant and fresh permissions; replay cannot revive a completed turn.

Resolve permits initialize/ping and resources/read URI `commerce://capabilities`;
resources/list advertises only that resource. Existing grants return the original
manifest, never a new selection. Execute permits that resource, tools/list,
prompts/list, prompts/get and tools/call for the grant. Prompt name is
`commerce/<releaseId>/<capabilityKey>/<revisionId>`; arguments must be {}.
MCP resource payload has name `commerce.capabilities` and the C4 manifest JSON.
Resolve cannot obtain prompt content or invoke tools. Dispatcher resolves exact
implementation versions from the grant; version is not a model argument. Dispatch loads the pinned database definition
and invokes its approved executor operation; it does not require a code registry
entry for each configurable MCP tool name.

### Exact available-tool discovery sequence

Background's trusted CommerceAgent host supplies CommerceTurnIdentity (shopId,
checkoutRecoveryId, conversationId, inboundVersion) in the C5 signed assertion;
these are not caller-controlled tools/list parameters. A shopId alone cannot
identify the original grant or prove shop ownership. The customer/model never
selects the shop or the release.

On the first admitted turn: resolve-purpose resources/read obtains the selected
manifest candidate from current plan/features/policy and active release;
Background persists the one immutable grant using its existing unique-conversation
insert/winner-read flow. It then creates an execute-purpose assertion bound to
that grantId/releaseId. On later turns, reuse that original grant, never resolve
new tools from current publication. Current revocations still restrict access.

After MCP initialization, tools/list request is exactly
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}.
The Authorization header supplies the signed execute context. Return
{"jsonrpc":"2.0","id":2,"result":{"tools":[...]}}; each entry contains only
name,description,inputSchema, sorted by name, deduplicated by exact tool revision.
Max32 tools, no pagination cursor in v1. Omit currently denied/revoked tools; an
unavailable required executor/schema is a typed unavailable resolution failure,
not permission to substitute a tool or silently expand the set. Empty usable
grant returns tools:[]; Background retains grounding/referral behaviour.

tools/call accepts {name,arguments} only and again checks exact original grant
membership and current authority. Supplying shopId/grantId/releaseId as list/call
parameters cannot select another context; reject extraneous parameters. Studio
U13 computes the new-conversation preview with the same pure resolver, under
staff authentication; it never calls production MCP or creates a grant.

No-store caching for all personalised/authenticated responses. Authentication
failure is HTTP401, valid identity lacking authority403, body limit413; RPC schema
errors use SDK protocol errors. Business tool failures use isError plus the C4
structured error; do not return a success-shaped unknown string. Registry
unavailability never silently swaps versions. Validate before provider work.

## C6. Runner, prompts and budgets

Runner receives injected model/clock/AbortSignal/tool adapters and validated grant,
manifest, prompts and context. No provider env lookup in Shared. Platform
instructions precede capability prompts (membership position order) and explicitly
reserve tenant scope, tool grants, factual grounding, language and final format.
Templates are literal text, not JavaScript, expressions or arbitrary interpolation;
trusted context is a separate serialised data block with a clear trust boundary.
Tool/customer/catalogue text is untrusted data, never a new instruction layer.

### C6.1 Fixed instructions, recovery context and language

This section is binding for BACKGROUND-001, SHARED-001, COMMERCE-009 and
SYSTEM-TEST-001. It replaces vague requirements to preserve the old prompt.

Ownership and composition:

1. Apply C16 for the final ownership split: release-authored response instructions
   and details schema are editable in Studio; Shared enforces the stable envelope,
   grant and budget boundaries. Background supplies authoritative current recovery
   context and admission/language persistence. The behavioural matrix below must
   remain covered by the initial release and tests; it does not require hard-coded
   Shared prompt prose. C16 supersedes earlier fixed-prompt ownership wording.
2. Background loads current persisted recovery status, checkout token, totalPrice,
   completedAt, conversation type, resolved languageTag/languageSource and optional
   customer firstName from the routed recovery/conversation. Identity/ownership is
   checked before model work. Serialize context as data, never interpolate customer
   strings into instruction text. Null fields remain unknown: a missing completedAt
   must never override a COMPLETED status. A stored checkout total is historical
   recovery data, not evidence of current product pricing or currency.
3. Use C2 bounded same-conversation history; do not restore the old unmaintained
   summary as authoritative context. Names, messages, summaries, catalogue text and
   tool renderedText cannot provide instructions or change recovery state.
4. Compose the pinned C16 response instructions and capability prompts in the
   order specified by C16, with trusted context/history in separate data blocks.
   Authored prose cannot override enforced grant, envelope or admission rules. Prompts
   and tool revisions remain pinned to the original grant, while current recovery
   status and resolved language are freshly loaded each admitted turn.
5. Product discovery and purchasing assistance are conditional on the original
   grant. Never say "use Shopify tools" as an unrestricted permission or acquire
   additional tools to answer a question. Answers require trusted recovery facts
   or results from originally granted, currently authorised tools. Missing evidence
   produces REFER_TO_STORE; Background renders the verified store referral under C4.

Mandatory recovery instruction matrix:

| Persisted status | Required behaviour |
| --- | --- |
| COMPLETED | Never call this an abandoned or active checkout. Acknowledge the completed purchase when relevant. Continue only within the original tool grant; completion does not grant order-management capabilities. |
| EXPIRED | Never imply the original checkout is active. Current product facts require originally granted tools; otherwise refer to the store. |
| CANCELLED | Never imply the original checkout is active or restored. Current product facts require originally granted tools; otherwise refer to the store. |
| MESSAGE_SENT | Help with the identified recovery and only the product questions supported by the original grant. Do not infer current stock, prices or checkout validity from the message status. |
| ENGAGED | Apply the same bounded assistance as MESSAGE_SENT; engagement does not expand permissions. |
| Any other valid persisted status | State only supported recovery facts; do not infer active, abandoned or completed status or broaden the grant. Preserve existing admission checks. |

Mandatory language and final-output instructions:

- Keep WhatsApp replies concise and natural. Use resolved languageTag when present.
- Initialize from the shop language under C6.2; do not implement a separate
  customer-explicit preference path or phone-country lookup.
- When the latest substantive customer input clearly establishes a
  different language (or no language is resolved), answer in that language and emit
  its narrowest defensible BCP-47 tag with confidence in [0,1], using existing
  validators. Never invent a regional subtag. If no clear change is established,
  retain the resolved language and emit both fields as null. With no resolved or
  defensibly detected language, retain the existing host fallback; do not invent a
  new fallback locale or fabricate detection metadata. Existing fallback precedence
  is valid Shopify language, merchant default, then platform default; if none is
  valid, retain null language/source.
- Ambiguous, short, emoji-only, URL-only or numeric input emits both detection
  fields as null. Do not infer language from a customer name or product title.
- Language adaptation must not change prices, currency, URLs, order/recovery state
  or merchant policy. Persist detection only through existing host validation and
  confidence/precedence handling, never on stale or cancelled turns. Background
  accepts detection updates only for a stable language signal and confidence
  >=0.85 and <=1, preserving existing tag canonicalisation. Reuse
  conversation-language.service.ts; do not introduce a
  second detector, threshold or persistence path.
- Finish by calling host-local finalResponse exactly once, using the C4 schema.
  Include customer-facing replyText and either two null detection fields or one
  valid tag/confidence pair. No reasoning in replyText, no ordinary assistant text
  as a substitute, and no partial pair. Missing, duplicate or malformed final output
  is INVALID_FINAL, not a customer reply. finalResponse is outside remote grants.

Required fixtures (record IDs and outcomes in each owning task): P01 COMPLETED
with null completedAt; P02 EXPIRED; P03 CANCELLED; P04 MESSAGE_SENT/ENGAGED with
and without discovery tools; P05 a later turn changes status to COMPLETED while
retaining the original grant/prompt release; P06 starts with the French shop
language, switches on substantive English at confidence >=0.85, then retains
English for ambiguous input with null detection; P07 established English with
a substantive French message emits French plus a valid confidence >=0.85; P08 ambiguous,
short, emoji-only, URL-only and numeric messages emit null pairs; P09 missing
regional evidence never adds a regional subtag and localisation preserves supplied
amounts/currency/URLs/policy; P10 capability/customer/tool-text injection cannot
change platform rules or grants; P11 absent/duplicate/malformed finalResponse is
rejected; P12 no resolved language follows existing fallback without fabricated
metadata. Use scripted models for structural/dispatch/state assertions and explicit
adversarial evaluation cases for natural-language behaviour; do not claim scripted
outputs prove a live model can never hallucinate.

Maximum90 seconds end-to-end per admitted turn,12 model steps,10 remote calls,
800 output tokens. Reserve one remote call for each offer-evidence revalidation:
max3 offer references, at least that many remaining calls before accepting final.
One retry per transient read within remaining deadline counts as another call;
never retry DENIED, INVALID_INPUT, STALE_TURN or unsupported facts. No provider
mutation or WhatsApp send is retried by the runner. Cancellation aborts adapters;
late results cannot send, mutate language or complete a newer turn.

Export runCommerceTurn(input) as Promise<{ok:true,result:CommerceFinalResponse,
usage:{modelSteps,remoteCalls}} | {ok:false,error:{code,retryable}}>. Error codes
are INVALID_INPUT, INVALID_FINAL, BUDGET_EXHAUSTED, CANCELLED, DEADLINE,
UNAVAILABLE, DENIED, STALE_TURN and INCOMPATIBLE_VERSION; no provider error text.
Input includes turn, grant, manifest, prompt bundle, language/context/history and
injected dependencies. Pure runner tests never instantiate service credentials.
Exactly one finalResponse invocation is required. Duplicate/malformed/missing
final results are typed failures. Unknown facts, unavailable/ungranted/revoked
tools result in referral when a valid final can be generated; infrastructure
failure before final is handled by Background once, within existing admission.
Language detection uses existing validators. Capabilities cannot increase budgets
or remove grounding rules. Scripted tests prove checks/dispatch, not a guarantee
that all natural-language hallucinations are mechanically detectable. Include
adversarial evaluation fixtures; unsupported factual questions must refer.

## C7. Staff publication and replay

Default v1 is a separate Studio NextAuth browser session using the same existing
PlatformAdmin identity and Google subject as Admin; automatic cross-host SSO is
not assumed. ADMIN may read/create/edit/preview. SUPER_ADMIN additionally may
publish/activate/rollback/enable/disable. Direct requests recheck current identity
and role, not only UI controls/JWT age. Canonical hosted origin is configured;
mutation Origin must match, server methods are POST, NextAuth owns OAuth CSRF.
Use host-only secure HTTP-only session cookies with a Studio-specific name.

### C7.1 Google-only Studio auth and development principal

COMMERCE-002 owns the reusable server-only auth library. Hosted sign-in supports
Google only through NextAuth's Google provider; no password, credentials, email
link or additional OAuth providers. Existing active public.PlatformAdmin Google
identities, verified email, atomic subject binding and separate Studio JWT session
remain authoritative. Development bypass is not a NextAuth credentials provider.

Match Admin's src/lib/auth/environment.ts semantics: resolve environment from
trimmed/lowercased DEPLOYMENT_ENVIRONMENT_NAME, falling back to NODE_ENV, then
"unknown". Only resolved "development" enables bypass. If it resolves to
"development" while NODE_ENV is "production", throw a configuration error before
returning any principal. All other environments require AUTH_SECRET,
AUTH_GOOGLE_ID, AUTH_GOOGLE_SECRET and AUTH_URL; missing values fail closed.
Never infer bypass from absent credentials, a request header/query/cookie, hostname
or client flag. No NEXT_PUBLIC auth override. Document local development settings
and the production-build rejection, including local production-build testing.

Bypass returns {id:"development-platform-admin",role:"SUPER_ADMIN",
developmentBypass:true} without Google login. Match Admin's reserved backing
identity exactly: provider "development", providerSubject "development-platform-admin",
email "development-platform-admin@local.invalid", displayName "Development Platform
Admin", active true, role SUPER_ADMIN. Before FK-backed writes, ensure this row
inside the same transaction: INSERT ON CONFLICT(id) DO NOTHING then reload/check
all reserved fields; conflict fails closed without modifying an existing identity.
Do not silently promote real staff. No new table/migration or auth-row creation on
startup/ordinary reads. The helper is callable only for a server-resolved bypass
principal after rechecking the environment; never trust a client-supplied principal.
Hosted Google auth must reject this development provider identity.

Deliver src/lib/auth/index.ts as server-only public entry point, with environment,
principal, guards and development-identity modules behind it. Export
getStudioAdminPrincipal(): Promise<StudioAdminPrincipal|null>,
requireStudioAdmin(): Promise<StudioAdminPrincipal>,
requireStudioSuperAdmin(): Promise<StudioAdminPrincipal>,
requireStudioAdminPage(): Promise<StudioAdminPrincipal>, and
ensureDevelopmentStudioAdmin(transaction,principal): Promise<void>.
StudioAdminPrincipal is exactly {id,role:ADMIN|SUPER_ADMIN,developmentBypass:boolean}.
No module-global principal cache: production resolution reloads current identity
per request; request-local deduplication is permitted. Unit-test resolver receives
injected session/database/environment dependencies like Admin.

Use typed auth errors and one route/action adapter: missing session ->401,
inactive/provider/subject mismatch or insufficient role ->403; invalid configuration
->503 with no configuration values/secrets in response. Page guard redirects absent
session to U01 and denied identity to U02. Authenticated U01 redirects to U03.
Development U01 likewise resolves the bypass principal and redirects to U03, with
no Google credentials required. All Studio pages, protected reads, Route Handlers
and Server Actions call the library at their server entry point; a protected layout
or hidden button alone is insufficient. Mutations additionally enforce existing
Origin/CSRF/replay protections, including development; bypass changes identity
resolution only. No duplicated route-local role tests or hand-decoded JWTs.

Google callback/sign-in/out handlers and health routes retain their own specified
public/protocol access; production /api/mcp always uses C5 Background assertions.
Neither staff sessions nor development bypass authorise MCP. U03–U14 display a
persistent "Development — SUPER_ADMIN" badge for bypass identity only. U01 has
only Continue with Google outside bypass; no user-selectable development login.
COMMERCE-008 owns these page details; COMMERCE-002 provides auth state/helpers.

Required fixtures A01 verified allowlisted Google success; A02 other provider,
unlisted/unverified/subject-mismatched identity denied; A03 local development yields
SUPER_ADMIN without credentials; A04 production plus development override errors;
A05 test/production/unknown without credentials denies; A06 request-supplied bypass
flags ignored; A07 reserved row created once under concurrent FK-backed writes,
existing exact row reused and mismatched row rejected without update; A08 every
Studio route/action family uses guards, ADMIN cannot publish, SUPER_ADMIN can;
A09 inactive/revoked role takes effect next request; A10 bypass cannot access live
MCP or skip mutation Origin checks; A11 U01 redirects/badge/sign-in duplicate guard.
Test Google/development identity precedence with injected fixtures; no live OAuth
credentials required for local tests. Record separately any developer live OAuth check.

COMMERCE-003 exposes typed server operations createTool, updateTool,
createToolDraft, updateToolDraft, publishToolRevision, setToolEnabled,
createCapability, updateCapability,
createDraft, updateDraft, publishRevision, createRelease, activateRelease,
rollbackRelease, setCapabilityEnabled. Each requires operationId (opaque CUID,
client-generated), reason1..1000, strict operation arguments; versioned writes
also require expectedEditVersion. Capability metadata updates use expectedUpdatedAt
CAS because its table has no editVersion. Draft numbering is allocated while locking the owning capability/tool row.
Tool metadata uses expectedUpdatedAt CAS; tool drafts use expectedEditVersion.
Tool create/update expose displayName/description (name set only on create);
setToolEnabled takes an explicit desired boolean. createToolDraft takes toolId,
optional sourceToolRevisionId from that tool and proposed definition; update takes
toolRevisionId/full definition. Capability draft writes carry full toolBindings,
promptTemplate/configuration/contractVersion; association edits use the same
updateDraft operation, never an unaudited side action. An edit never mutates a published revision; create a
new draft from it. PublishRevision verifies exact installed tools/contract/hash,
then freezes its exact toolBindings and prompt/configuration. createRelease references already-published revisions,
positions0..n-1, contains conversation_core, and never appends to an existing release.

One operation -> one audit event whose id=operationId, with {payloadHash,result}
metadata. Hash binds operation name, actor ID, reason and all semantic input.
Authorise before replay lookup. Same actor/hash returns persisted result IDs;
different actor/hash is409 without disclosing original result. Distinct CAS
conflicts are409 and cannot overwrite data. Losing duplicate transactions roll
back fully and reread the winner. Pointer activation and its audit are atomic;
createRelease does not activate it implicitly. A UI “publish and activate” flow
runs the distinct reviewed operations with distinct stable operation IDs and can
resume at the incomplete stage; it must not falsely promise an atomic composite.
Initial seed command takes a real active SUPER_ADMIN and stable operation IDs;
it creates conversation_core with grounding/referral prompt and no tools. Optional
explicit sample import creates reusable product/discount tools and a
RECOVERY_POLICY discount_assistance configuration, no hypothetical paid features,
and uses the same validation/audit operations. No seed on startup/migration.

## C8. Product, discount and recommendation rules

Pin Shopify Admin GraphQL API to the existing implementation's reviewed version
(current source:2026-07), compile static allowlisted queries and validate actual
schema/scopes with the official provider schema during COMMERCE-006. No dynamic
host, URL fetch or model-supplied GraphQL. Use the existing offline installation
token lookup by verified Shop.domain. Missing scopes returns UNAVAILABLE; any new
OAuth scope needs an explicit owning Shopify task before activation.

Search pages <=20 variants, <=3 provider pages per tool; filter unavailable
variants, same currency and confirmed market context. Opaque cursors bind query,
shop and expiry; reject tampering/cross-shop reuse. Unknown availability is not
available. Never label historical recovery prices as current live checkout prices.

Support native basic percentage/fixed-amount offers only when every relevant
condition can be evaluated. Server time must satisfy startsAt<=now<endsAt when
bounded. Any unresolved customer/usage/combination restriction makes UNKNOWN;
unsupported families make UNSUPPORTED. Condition precedence: known expired/not
started/disabled or definite rule failure -> DOES_NOT_QUALIFY; otherwise unsupported
family -> UNSUPPORTED; otherwise missing fact -> UNKNOWN; otherwise qualifies.
Evaluation is for the exact snapshot/proposal, never a checkout acceptance promise.

Use decimal arithmetic and currency minor units from canonical currency metadata.
Percentage/fixed allocation, rounding and minimum-subtotal bases must match the
reviewed provider rule; if provider rule semantics cannot be established, mark
UNSUPPORTED rather than adopt an invented rounding formula. This is a closed
fallback, not permission to implement an approximate discount calculator.
AI compares at most50 authoritative eligible offers, sort known savings descending
then offerId ascending; truncation must be disclosed and never claim global best.
FIXED checks only configured offer; NONE returns no offers and denies discount tools.

Recommendations search <=60 variants and evaluate <=10 proposals per tool, bounded
by its10-second deadline. Similarity requires at least matching productType;
rank same vendor first, then descending count of intersecting title tokens,
then variantId ascending. Tokens are Unicode NFKC-normalised, lowercased with
locale-independent casing, split on non-letter/non-number characters, empty
tokens removed and deduplicated; no stemming, stop words or locale inference.
Missing attributes -> no similarity claim. Qualifying suggestions rank lowest
extraSpend then highest known savings then variantId. Return max3. Replacement
removes exactly the selected basket line; quantity must be explicit. Show extra
spend/resulting total separately; no claimed saving relative to the original basket
when the proposed purchase costs more. No match returns [], not invented products.
Before evaluating at most10 proposals, deduplicate by canonical proposal and
sort by extraSpend ascending then variantId then canonical proposal JSON ascending.
For qualifying-result ranking unknown savings sort after every known savings;
compare monetary decimals exactly, never using lexical or floating-point order.
All final ties use canonical proposal JSON ascending. Test Unicode/duplicate tokens,
equal scores and truncation before/after evaluation with named fixture expectations.
Effective search/recommendation limits are the minimum of requested value (or
operation default), platform ceiling and configured limits from all currently
eligible ORIGINAL provenance capabilities. An absent configured limit contributes
no restriction. Revoking a restrictive original association can remove its bound
only while another original association remains eligible; new associations never
contribute authority or bounds. Test this explicitly in COMMERCE-004/007.
Internal provider calls are additionally capped at12 requests per remote tool
(including pagination/evaluation, every retry and nested adapter request) and stop when either count/deadline is reached;
stop before issuing request13. All adapters share the same counter/deadline;
partial search results carry truncated=true. Exact evidence revalidation is not
allowed to report success from a truncated/incomplete rule evaluation.

## C9. UI and preview

Routes are the complete C15 route set; include `/sign-in`, `/access-denied`,
`/api/auth/*`, `/api/studio/*` and required `/_next/*` static assets. All business
reads/actions are server-authorised. Use stable paginated ordering createdAt,id,
page size25/max100, strict cursors (Feature and tool listings may use their
explicit C15/UI sort keys with stable ID tie-breakers). Include schema/operation/mapping/response-template forms for C14 definitions.
Allow the C14 constrained GraphQL query editor; no executable capability code editor, merchant override
editor or conversation grant reset. Published immutable content is visibly read-only.

Every mutation/paid preview uses a synchronous in-flight guard before await,
shared form/button handler, disabled conflicting controls and aria-busy/status.
Timeout keeps the same operationId/previewRunId for status reconciliation. Known
failure preserves inputs. Concurrent direct duplicates still enforce server replay.
UI tests assert effects and accessible feedback, not implementation-hook shape.

Preview conversation and turn IDs are separate. One synthetic grant persists for
one preview conversation; each intentional turn has one previewRunId and frozen
payload hash. Max20 turns per preview conversation,32,000-character history,
24-hour Redis retention. Real customer transcripts/shop tokens are not accepted.
Fixture mode is default; model mode is an explicit action with separate credentials.
MODEL transport is provider-neutral at PreviewService and supports exactly OpenAI-direct
and Groq through one OpenAI-compatible Chat Completions adapter owned by
COMMERCE-033. Provider selection is explicit (`openai|groq`), has no automatic
fallback and cannot configure an arbitrary base URL. Test/development hosted MODEL
validation selects Groq; FIXTURE constructs no provider request.
Only active ADMIN/SUPER_ADMIN can run. Budget per admin: at most10 model turns per
rolling hour, one in flight; platform at most2 concurrent model turns. Claim and
budget reservation are atomic in Redis across replicas; repeated run IDs reserve
once. Unknown/crashed/cancelled runs do not refund/restart automatically. A crashed
concurrency slot expires after120 seconds; retained result/dedupe state stays24h.
Missing Redis/model config fails closed for model preview; never use production
Background credentials. Deterministic fixtures require no paid model.

Preview status is RUNNING|COMPLETED|FAILED|CANCELLED|UNKNOWN with bounded result
<=64KiB. Cancel aborts the same run via distributed cancellation flag checked by
the owning runner before every step/tool, not a new run. Rerun explicitly creates
a new run ID; changing tools/prompts requires a new preview conversation. Audit
preview through redacted shared logs (admin ID/run ID/hash/runner/version/outcome),
not CommerceAuditEvent, whose enum covers only publication mutations.

### C9.1 Preview lifecycle and ownership (COMMERCE-009)

Use these authenticated JSON routes only; errors are `{code}` and use 400 for
INVALID_INPUT, 403 for DENIED, 404 for NOT_FOUND, 409 for ID_CONFLICT/CONVERSATION_BUSY/HISTORY_LIMIT, 429 for
QUOTA_EXCEEDED, 503 for UNAVAILABLE. Validate bodies strictly and return no stored
payload on errors. Every call rechecks active ADMIN/SUPER_ADMIN and owner identity.
Cross-admin conversation/run IDs return NOT_FOUND, including cancellation/status.
Preview conversation/run IDs below are client-generated UUIDs; scope Redis state by environment and admin.

| Method/path | Strict input | Success |
|---|---|---|
| GET /api/studio/preview/fixtures | no body | 200 `{fixtures}`: bounded catalogue of synthetic `{id,label,recoveryStatus,shopLanguage}` entries |
| POST /api/studio/preview/tool-tests | `{previewRunId,toolRevisionId,fixtureId,arguments}`; arguments satisfy the selected revision schema | 200 `{previewRunId,status,result}`; fixture-only structured data, rendered text and validation trace |
| GET /api/studio/preview/tool-tests/[runId] | no body | 200 `{previewRunId,status,result}` with the same owner/replay rules |
| POST /api/studio/preview/conversations | `{previewConversationId,mode,selection,fixtureId}`; mode FIXTURE or MODEL; fixtureId from the server's synthetic catalogue | 201 `{previewConversationId}`; matching replay 200 |
| POST /api/studio/preview/conversations/[id]/runs | `{previewRunId,message}`; synthetic text 1–4000 characters | 202 `{previewRunId,status}`; replay 200 existing status/result |
| GET /api/studio/preview/conversations/[id]/runs/[runId] | no body | 200 `{previewRunId,status,result}`; result null until available, bounded C9 result otherwise |
| POST /api/studio/preview/conversations/[id]/runs/[runId]/cancel | empty object | 200 `{previewRunId,status}`; repeated cancel returns current status |

Selection is a discriminated union: `{kind:"RELEASE",releaseId}` or
`{kind:"DRAFT",capabilityRevisionIds,toolRevisionIds,responseContract}`. Revision
arrays contain unique IDs, at most32 capabilities and64 tools, at least one total;
validate the selected bundle against Shared limits and C16. IDs reference saved
authorized revisions (including saved unpublished revisions), never arbitrary
executable definitions from the browser. Optional unsaved responseContract is
allowed only for DRAFT and uses the full C16 validator; omission uses the baseline.
Freeze loaded revisions, definitions and fixture state at creation. fixtureId
selects synthetic shop language/status/basket/feature flags; the server catalogue
covers P01–P12 (C6.2 governs language) and exposes labels/values to U14 selectors.
No real shop/customer identifiers or imported transcripts. Draft selection changes
require Reset and a new ID. Tool-test mode uses a selected frozen tool revision,
fixture adapter and schema-validated arguments through the same bounded service;
it does not invoke a model or consume paid-model quota.

Tool tests use the same admin/run-ID hash and24-hour replay rules, validate current
revision access and execute fixture adapters only. GET fixtures returns at most100
entries with IDs<=64 and labels<=128 characters; it contains no stored conversation
data. A tool-test response uses the same <=64KiB result bound.

Canonical creation payload hash makes same-ID creation idempotent; different
payload gives ID_CONFLICT. Check run-ID replay before busy/quota checks. Different
payload for the same run ID gives ID_CONFLICT. Atomically allow only one active
run per preview conversation, even with distinct IDs and FIXTURE mode; reject
CONVERSATION_BUSY before starting a model, changing history or reserving budget.
Completed/failed/cancelled runs release that slot; UNKNOWN blocks further turns
until Reset, never silently retries. Expired conversation/run state returns404,
never recreates history during a status request. Reset allocates a new conversation
and cannot bypass the per-admin/model concurrency budget of an old running call.
Cancellation is a request, not an immediate success: keep RUNNING until runner
acknowledges it; a completed result wins a late cancel. A lost runner becomes UNKNOWN.
Reserve turn count/history changes atomically; failed/cancelled/unknown dispatched
runs count toward20, rejected requests do not. History includes only completed
turns; reject HISTORY_LIMIT before dispatch if the new input exceeds32,000 chars,
and fail closed rather than truncate a completed result that would exceed it.
No automatic provider/model retry. Test races on separate service replicas.

## C10. Deployment and health

Commerce Node runtime port uses PORT (default3000); bind0.0.0.0. GET /health/live
returns200 {status:'ok'} without external checks. GET /health/ready checks database
SELECT1, required schema/keys/config and Redis (required by discovery rate limits),
within2 seconds; return200 {status:'ready'} or503 {status:'not_ready'} without
secrets. Absence of a published release is observable but not a startup deadlock:
Studio must be usable to publish the first release. No migrations on startup.

New secret/config names: COMMERCE_MCP_URL (Background only, private URL ending
/api/mcp), COMMERCE_ASSERTION_PRIVATE_KEY and COMMERCE_ASSERTION_KEY_ID (messaging
worker only), COMMERCE_ASSERTION_PUBLIC_KEYS (Commerce only, max2 kid/PEM entries),
COMMERCE_STUDIO_ORIGIN, optional ADMIN_ORIGIN (server-only HTTPS navigation origin), AUTH_SECRET, AUTH_GOOGLE_ID, AUTH_GOOGLE_SECRET, AUTH_URL,
COMMERCE_PREVIEW_ENABLED (false default), COMMERCE_PREVIEW_PROVIDER
(`openai|groq` when enabled), COMMERCE_PREVIEW_MODEL, COMMERCE_PREVIEW_API_KEY.
When preview MODEL is enabled all three provider/model/key values are required; when
disabled FIXTURE mode requires none of them. Provider endpoint selection is code-owned:
`openai` -> `https://api.openai.com/v1/chat/completions`; `groq` ->
`https://api.groq.com/openai/v1/chat/completions`. No configurable preview base URL or
automatic provider fallback. The hosted test/development environment uses
`COMMERCE_PREVIEW_PROVIDER=groq` and
`COMMERCE_PREVIEW_MODEL=openai/gpt-oss-20b`; API key remains an external secret.
Reuse existing DATABASE_URL, REDIS_URL and deployment-environment conventions.
No NEXT_PUBLIC secret; fake examples only. Validate hosted origins as HTTPS,
MCP URL as configured private host. Invalid required config fails readiness and
protected operations closed; liveness/static shell may start, consistent with the
accepted foundation. AUTH_URL must match COMMERCE_STUDIO_ORIGIN under C7.1.
Actual repository URL, Studio hostname and secret values are deployment inputs,
not guessed by task authors.

Gateway has a dedicated configured Studio host and explicit C9 path/method
allowlist. UI pages GET/HEAD plus authenticated Next server-action POST; auth and
studio APIs only documented methods; deny `/api/mcp` before proxying irrespective
of verb, query, case/encoding/dot-segment/trailing-slash variants. Reject ambiguous
normalisation, encoded separators and double decoding. No root blanket API proxy.
Health routes private; asset wildcard does not allow API routing. Upstream body
limit128KiB, read timeout100 seconds for bounded preview; MCP is only on the private
service URL. A gateway allowlist is not a substitute for NextAuth/action guards.

Build contract: recursive submodule init -> npm ci -> npm run prisma:generate ->
npm run build. `npm start` serves production. COMMERCE-001 pins Node from workspace
.nvmrc and compatible Next/React/MCP/client versions in lockfile and documents
`docs/runtime-compatibility.md`; do not install unbounded `latest` at deployment.

## C11. Observability and alerts

Reuse shared logging and available framework/OpenTelemetry technical signals.
COMMERCE-010 must deliver `docs/observability-commerce.md` mapping every dashboard
need to actual emitted metric/span names, units, attributes and local fixture
samples. Only add domain signals missing from that inventory. Required bounded
semantic outcomes: manifest granted/denied/unavailable, tool allowed/revoked/error,
eligibility four outcomes, preview completed/cancelled/denied/unknown; routing
outcomes belong to Background. IDs may correlate redacted logs/traces, never
metric labels; never record phone, prompt, provider payload, token or transcript.
Telemetry failure cannot change business outcome. Use purpose live/preview and
explicit environment; normal automated tests export only to local sinks.

Gateway dashboards use actual accepted inventory, never guessed metric names.
Initial alert policy (operational defaults, not measured capacity): readiness
unavailable2min; MCP failures >5% over5min with >=20 calls; oldest pending
conversation turn >120s for5min; evidence-revalidation failures >10% over10min
with >=20 evaluations. Distinguish expected permission denial from server errors.
Every alert includes service/environment and runbook link, preview excluded from
production alerts. No-data states shown explicitly; no traffic is not an error.

## C12. Required review evidence and execution boundaries

All implementation tasks provide a requirements-to-test matrix with fixture name,
expected outcome, command and actual result. Assertions must cover side effects
(model/provider call count, durable rows, usage and state), not just returned text.
Record commands available in the actual repository; new commands named by tasks
are deliverables. Don't claim runtime tests were run during architecture review.

SHARED-001 implements contracts and runner, validates them and publishes one
verified package version in the same task. Registry installation and both public
entry-point smoke checks are required before completion; code-only completion
does not unblock consumers. Re-run checks only when intervening changes require it.
COMMERCE-001 produces the SDK compatibility fixture before BACKGROUND-001 executes.
The dispatcher profile and compatibility document are inputs; the implementer
cannot claim compatibility merely by matching a package major version.
System tests depend on every implementation/publication/infrastructure task and
remain a manual terminal gate, never an implementation prerequisite.

Prototype tests using mocked model/Shopify/WhatsApp do not prove live behaviour.
Required live/provider/schema and deployed smoke evidence is developer-owned per
workspace policy; missing evidence prevents acceptance, not silent assumed success.

## C13. Initial outreach, follow-up outreach and conversation replies

Preserve the existing ARCH-016 model and merchant Recovery Settings implementation.
The merchant configures followUpEnabled and followUpDelayMinutes (1..10080 when
enabled), not a new conversation. ARCH-016 v1 allows one no-response follow-up.

| Outbound category | Existing identity | Conversation/recovery | Credit rule |
|---|---|---|---|
| Initial proactive outreach | RecoveryOutreachAttempt sequence1, trigger INITIAL, outboundMessageId | Existing unique Conversation for this recovery generation | Existing proactive admission consumes one recovery credit on confirmed success |
| Configured no-response follow-up | sequence2, trigger NO_RESPONSE_FOLLOW_UP, its own outboundMessageId | Same Conversation and CheckoutRecovery as sequence1 | Separate proactive admission/credit if sent, regardless of elapsed hours |
| CommerceAgent conversational reply | ConversationMessage senderType AGENT, ordinary outbound reservation; no new outreach attempt | Same routed recovery Conversation | No new recovery credit; existing outbound message limits/accounting still apply |
| Other recovery-linked automation | AUTOMATION message without a proactive outreach-attempt link (e.g. voice fallback) | Existing routed recovery Conversation | Existing automation admission; not automatically a proactive outreach credit |
| Unowned identification guidance | Fixed guidance with Redis guard (C3) | No Conversation/recovery | Platform-owned, never an invented merchant credit |

Derive proactive classification from RecoveryOutreachAttempt.outboundMessageId
and trigger/sequence. senderType=AUTOMATION alone is insufficient, as several
kinds of automation use it. Do not add a parallel message-kind enum or business
classification to the shared inbound contract. Replies to an initial template,
its follow-up template or a later recovery-linked agent message all use that
outbound providerMessageId to recover the same Conversation. One initial plus
one follow-up is one distinct recovery candidate for unreferenced messages.
Two recovery generations are two candidates even if the checkout token matches.

Every proactive send retains its own existing providerMessageId; attach the correct outboundMessageId to its
own attempt using existing confirmed-send finalisation. Never overwrite the
initial attempt's message link with the follow-up's ID. Include already-sent
initial/follow-up context in the agent's bounded same-conversation history; a
stored template descriptor must not be misrepresented as the actual customer-
visible template body. Use trusted attempt/policy facts where text is unavailable.

Follow-up due time remains initial confirmed sentAt plus the governing snapshotted
followUpDelayMinutes, with existing durable scheduling/repair and current execution
checks. Reuse accepted ARCH-016-BACKGROUND-003 code and semantics. Before the
follow-up's provider send, recheck durable customer engagement, terminal recovery,
shop eligibility and credit admission. A routed inbound reply to the initial
message engages the recovery and suppresses a not-yet-sent no-response follow-up;
it must not leave sequence2 sendable merely because sequence1 was referenced.
Preserve original context ID for provenance and mark the appropriate current
waiting attempt engaged under existing sequence/timestamp rules. A reply after
sequence2 engages the same recovery; it does not create sequence3. A delayed job
is not authority to send. Never restart follow-up timing after an agent reply,
delivery/read receipt, clarification guidance or publication in Studio.

Uncorrelated guidance does not identify which recovery was engaged, so it cannot
mark all candidate attempts engaged or cancel their follow-ups. Only successful
routing provides that ownership. For valid routed audio, preserve engagement on
durable receipt independently of later transcription success; retry/duplicate
handling uses the existing message's authoritative conversation, not a newly
computed route. Do not charge another credit on customer/agent continuation.

Initial/follow-up templates do not themselves invoke CommerceAgent or create a
new tool grant. The grant is created at the first admitted CommerceAgent turn;
later messages and any outreach in the same Conversation never replace/reset it.
New outreach does not expand the toolset or reinterpret which basket a customer
means. Customer-engagement/provider-send races must be tested with barriers:
engagement committed before the final send recheck suppresses follow-up; a send
already submitted cannot be retroactively unsent and must not be billed/sent twice.

## C14. Database-defined tools and response templates

### Independent tool identity and versioning

CommerceTool owns a globally unique MCP name and emergency enabled state.
CommerceToolRevision owns the entire immutable published definition; a capability
revision holds toolBindings [{toolId,toolRevisionId}], not copied tool definitions.
Only published tool revisions can be attached. Each binding is distinct by toolId;
max32, sorted by toolId for hashing. No automatic latest-version association.
One tool can be associated with multiple features. A release cannot reference
conflicting revisions of the same tool; identical references deduplicate in
MCP tools/list. Tool changes require explicit capability revision and release
publication before they affect new conversations.

A definition has exactly name, definitionVersion, description, inputSchema,
execution, responseTemplate. name matches its immutable CommerceTool.name and
^[a-z][a-z0-9_]{0,127}$; definitionVersion is SemVer<=64 chars, unique per tool.
Changes to any definition field require a greater SemVer than the highest
published version for that tool; a new tool starts at1.0.0. No prerelease/build
suffixes in v1. Drafts can correct their proposed version before publication.
Tool hash is SHA-256 of canonical {contractVersion,definition}. Capability hash
is SHA-256 of {contractVersion,promptTemplate,configuration,toolBindings}.

Grant entries are {toolId,toolRevisionId,toolName,definitionVersion,capabilityKeys}.
capabilityKeys is the sorted, nonempty set of originally selected capabilities
binding that exact tool revision. Unique toolId and toolName, max32 entries.
The original release, capability revisions and tool revisions remain immutable.
Execution requires enabled CommerceTool and at least one of those ORIGINAL
capabilityKeys still enabled and eligible. A newly enabled different capability
cannot authorize an old grant. Re-enabling an original permission restores only
the original revision. Revocation does not rewrite the persisted grant.

### Draft versus publication validation

Shared exports CommerceToolDraftDefinitionSchema separately from the strict
publishable CommerceToolDefinitionSchema. Drafts have the same six top-level
keys and scalar/size bounds, but inputSchema/execution/responseTemplate may be
incomplete bounded objects. No incomplete definition can publish, enter a release
or execute. createToolDraft without a source uses name from CommerceTool,
proposed version, description from displayName, and empty objects for those three
fields; mark Not ready to publish. All semantic validation results bind the
current editVersion/content hash and are stale after edits. Capability Create
draft without a source asks for nonblank initial prompt and starts with {} settings
and [] toolBindings. Source drafts copy only from their own tool/capability.

### Execution union and no-deployment boundary

Shared owns a strict execution union; executable code is never stored in it:

1. {kind:"SHOPIFY_STOREFRONT_QUERY",executorVersion:"1.0.0",apiVersion:"2026-07",
   schemaHash,document,operationName,variables,resultPath}.
2. {kind:"POLICY_OPERATION",operation,operationVersion:"1.0.0",arguments}.

The first is a reusable read-only GraphQL executor. Staff can author new queries,
input schemas and templates in Studio within its supported public Shopify data
surface, without adding a named code handler or deploying Commerce/Background.
The second reuses reviewed recovery and discount policy operations for privileged
or calculated facts. Those operations are not the catalogue of all possible
features/tools. Creating a feature in Admin or a new supported query in Studio
requires no code registration, feature-name switch or new merchant-app build.

V1 uses Shopify Storefront tokenless public reads for authored queries. This
avoids giving arbitrary authored queries the app's privileged Admin credential.
Allowed root fields: product, products, collection, collections, search,
predictiveSearch, page, pages, blog, blogs, articles and shop, only where present
in the pinned schema. Disallow mutation/subscription, cart/customer, node/nodes,
introspection except __typename, and any other root. Token-required fields are
shown as unavailable in this execution mode; no automatic privileged fallback.
No caller credentials, domain, headers, API URL or customer access token.
Admin-only discount/recovery data stays behind POLICY_OPERATION checks. Adding a
new authenticated integration or write primitive remains a separately reviewed
platform change; it is not required for a new public-data query or feature.

COMMERCE-011 provides the exact official 2026-07 Storefront schema artifact and
SHA-256 through the accepted dependency. COMMERCE-005 executes against that same
artifact; publication and calls reject mismatched/unknown schemaHash or versions.
Retain accepted schema artifacts for retained grants. Provider version fallback
(header reports a different API version) returns UNAVAILABLE, never silently
changes the published contract. Discovering newer docs never upgrades a tool.

### Query validation and execution

Parse GraphQL structurally: exactly one named query matching operationName,
no extra operation definitions, no fragment definitions/spreads or directives
in v1; field aliases are allowed. Validate fields, arguments and variable types
against the pinned official schema, then the Moda root/credential restrictions.
Document <=16,384 UTF-8 bytes, field depth<=8, <=100 field selections. Every
connection requires first as an integer literal1..20; disallow last and variable
page sizes. Multiply enclosing first values for each field, sum those weights
across selections and require <=500. Unbounded list fields require an explicit
schema-backed bound or are rejected. These are Moda limits, not claims about
Shopify's cost algorithm. Fixed documents cannot be supplied by the customer/model.

variables and policy arguments map keys to {input:"topLevelProperty"} with optional
omitIfMissing:true, or {literal:boundedJSON}. Query variable names/types must agree
with the document and inputSchema; all required variables must resolve. No text
interpolation, coercion or expressions. Model inputs are only declared values,
not query structure. resultPath is a nonempty dot-separated field/alias path
(max256 chars, schema-proved object/list target under returned data); no wildcards,
array indexing, prototype keys or expressions. Projection selects facts only,
never computes eligibility. Query output schema is derived from the selection
and resultPath, not an unrelated author assertion.

Commerce derives the canonical *.myshopify.com host from the recovery-owned shop,
uses HTTPS /api/<pinned-version>/graphql.json, no redirects, no customer/Studio
host input. Tokenless requests carry no Admin/Storefront/Background credentials.
One request per call,10-second overall deadline, no hidden pagination or automatic
retry inside the executor. Honor provider throttling through typed THROTTLED;
network/API-version/schema failures are UNAVAILABLE. Any GraphQL errors reject
the result even if partial data exists. Bound decoded response to256KiB before
processing; overflow fails. Success data for authored queries is
{source:"SHOPIFY_STOREFRONT",apiVersion,schemaHash,observedAt,values}; values is
selected at resultPath. A null resultPath target returns NOT_FOUND. Empty lists
remain successful empty results. Raw facts are not discount Evidence.

### Concrete query-based definition

The following authored tool can be reused by any Admin-created product-information
feature. It requires no bespoke product-summary executor. Replace schemaHash's
placeholder with the actual artifact hash when constructing a fixture or saving.

```json
{
  "name": "read_product_description",
  "definitionVersion": "1.0.0",
  "description": "Read a product description to answer questions about its stated details; refer to the store when the detail is absent.",
  "inputSchema": {
    "type": "object",
    "properties": {"handle": {"type":"string","minLength":1,"maxLength":255}},
    "required": ["handle"],
    "additionalProperties": false
  },
  "execution": {
    "kind": "SHOPIFY_STOREFRONT_QUERY",
    "executorVersion": "1.0.0",
    "apiVersion": "2026-07",
    "schemaHash": "<actual SHA-256 of the accepted schema artifact>",
    "document": "query ProductDetails($handle: String!) { product(handle: $handle) { title description } }",
    "operationName": "ProductDetails",
    "variables": {"handle": {"input":"handle"}},
    "resultPath": "product"
  },
  "responseTemplate": {
    "kind": "text",
    "text": "{{result.values.title}}: {{result.values.description}}",
    "unavailable": "Product details could not be verified."
  }
}
```

MCP tools/list exposes name, description and inputSchema only; the manifest adds
pinned definitionVersion/identity. Execution configuration stays on Commerce.
The template returns text to the agent, not directly to WhatsApp. Unknown product
facts must not become affirmative claims; discounts require existing Evidence.

### Bounded input schema and policy operation library

inputSchema: root object, additionalProperties:false, max32 properties, depth3.
Types string/integer/boolean/object/array, nullable via [T,"null"]. Keywords:
type,properties,required,additionalProperties,description,enum,minLength,maxLength,
minimum,maximum,minItems,maxItems,items,pattern. Strings max4096, arrays max100,
enums max32 scalar values. No external references, coercion or expression code.
pattern only supports the regex `^[0-9]{1,18}(\.[0-9]{1,6})?$` for decimal money strings.
Optional missing values stay absent. All inputs/mapped variables validate again
on execution. Output selection may exceed input-schema depth but is constrained
by the query bounds above.

POLICY_OPERATION names initially recovery.getBasket, shopify.searchProducts,
discounts.getOptions, discounts.evaluate, products.findQualifying and
products.findSimilar, all version1.0.0. C4/C8 retain their exact input/output and
policy evidence. COMMERCE-005 owns basket/product adapters plus the generic query
executor, COMMERCE-006 discount evaluation, COMMERCE-007 recommendations. Renaming
a tool or binding it to a different feature never bypasses these checks. The
six adapters are reusable platform helpers and sample definitions, not mandatory
merchant features. Missing adapter versions block publication and fail retained
calls as UNAVAILABLE; never substitute another version.

### Response rendering

responseTemplate is one of:
- {kind:"text",text,unavailable}; tokens may reference allowed result scalar paths.
- {kind:"items",itemsPath,item,empty,unavailable}; itemsPath is an array field in
  the operation output, item tokens reference item scalar paths; render at most
  the operation's result limit and join with newline.
Each template string max4096 chars; total rendered text max4096. Allowed tokens
are {{result.path}} or {{item.path}} only, with dot-separated schema-declared field
names. No expressions, helpers, conditions, includes, HTML, dynamic property
access, prototype keys or code execution. Render values once; a provider string
containing {{...}} is data and must not be evaluated a second time.

On missing/null required token facts, render unavailable rather than inventing
values; include explicit unknown fields in structured data. Empty array renders
empty, not unavailable. Never format an ERROR result through the successful-item
template. Return the existing C4 typed error and fixed unavailable text. Overflow
returns a bounded INVALID_INPUT/template-output error rather than silently losing
facts. Studio previews show data and rendered text side by side.

C4 tool success becomes {contractVersion,status:"OK",data,renderedText}; ERROR
retains its typed code/retryable and may include bounded renderedText from the
fixed unavailable template. Host evidence validation uses data, never template
text. Treat malicious or factually unsupported template prose as editable content
under the immutable grounding/referral policy; publication requires staff review
and adversarial fixtures, not a claim of automatic truth checking.

### Publication acceptance

PublishToolRevision validates its schema, execution, response fields and hash;
publishRevision validates exact published toolBindings; createRelease rejects
conflicting tool revisions and transport-limit overflow. Activation checks all
referenced execution versions and schema artifacts. Seeds are explicit audited
commands, never automatic live feature creation or mandatory product_search use.
Prove a never-seeded tool/query can be authored, published and called without
service deployments; changed queries/templates stay invisible to old grants.

## C15. Studio authoring UI and Shopify discovery

The [Studio UI design](ARCH-020-studio-ui-design.md) is binding, including its
screen IDs and acceptance matrix. COMMERCE-008 implements screens U01–U13;
COMMERCE-017 implements U14; COMMERCE-009 supplies preview backend routes;
COMMERCE-011 supplies discovery/validation services.
Admin owns Feature creation/plan membership; Studio reads that catalogue and
associates Commerce behaviour. No new feature-creation action or duplicate table.

COMMERCE-011 runs a pinned @shopify/dev-mcp dependency as one supervised stdio
child per Commerce replica, with no listening port. Pin exact package version
and executable in lockfile/runtime-compatibility docs; no npx @latest at runtime,
no arbitrary command configuration and no browser-supplied MCP URL/tool name.
Expose only typed documentation search, documentation fetch, schema browse and
query-validation operations after ADMIN/SUPER_ADMIN server authentication. Resolve
the actual upstream tool names/schemas/initialization against the pinned version
and record fixtures; do not assume names from older documentation. Whitelist
those read/developer-validation capabilities only; never forward Shopify CLI,
store management, file operations, tool installation or live commerce calls.

Ship the verified Storefront2026-07 schema artifact with the service; compute its
hash, record official provenance and package version. It is the authoritative
form/compiler schema. Live developer resources add explanations/examples, not
execution authority. Build/review must verify schema-version support, upstream
compatibility and license/distribution conditions; unsupported upstream schema
must be resolved before COMMERCE-011 acceptance, not faked. No Redis-only schema
retention; deploy artifacts retain all versions referenced by active/retained
releases. No schema import/editor UI in v1.

Discovery API under /api/studio/discovery: POST search {query:string1..500},
POST document {path:string1..512}, GET schema with apiVersion=2026-07,
optional parentType:string1..128, search:string<=200 and cursor:string<=2048,
POST validate {definition:bounded draft definition}. No other query/body keys.
Missing parentType means query-root fields. Search returns {items:[{title,text,
sourceUrl}]} max10 (title<=255,text<=2000). Document returns {title,text,sourceUrl}
<=64KiB. Schema returns {apiVersion,schemaHash,parentType,fields,nextCursor}; each
field has name,type,description,nullable,arguments,selectable,restrictionReason
and optional example; max100 fields/page and256KiB total, stable field-name sort.
Arguments expose their schema types, required flags and applicable C14 bounds.
Unrecognized parentType/cursor returns field-level INVALID_INPUT, not another
schema. Validate returns {valid,schemaHash,errors:[{code,path,message}]} max50;
path is a JSON field path or GraphQL line/column, message<=512. Structural and
semantic draft errors return valid:false, never execute or publish the draft.
Only canonical https://shopify.dev/docs/ URLs are accepted for docs; no arbitrary
URL proxy, redirects to other domains or customer content in searches/logs.
Use20-second deadline, max2 concurrent calls/admin and4/replica; Redis rolling
limit60 requests/admin/minute for discovery requests, fail closed if unavailable.
Schema-page reads can use the local artifact without outbound calls; authenticated
rate limits still apply. No retries hidden behind duplicate submissions.

Search/docs unavailable: show in-Studio retryable error and retain draft, with
local schema browsing, validation and fixtures still usable. Saving drafts never
requires internet access. A tool that passes the authoritative local schema and
policy checks can publish while documentation search is unavailable; missing
schema/required executor must block publication. The full Studio cannot be
accepted with discovery stubbed or requiring an external IDE. AI prose-to-tool
generation is not required; guided schema selection and inline explanations are.

New routes: / -> /features; /features, /features/[id], /tools, /tools/[id],
/explore, /capabilities, /capabilities/[id], /releases, /releases/[id], /shops,
/shops/[id], /preview, auth/denied routes and explicit studio APIs. Capability
routes are internal configuration editors, not another billing catalogue.
Every direct read/write is authorized; C7 role/replay and C9 preview limits apply.
Public gateway includes these UI/studio routes; neither production /api/mcp nor
the developer-resource child is reachable publicly as an MCP endpoint.

Sources checked 2026-09-20: [Shopify AI Toolkit](https://shopify.dev/docs/apps/build/ai-toolkit)
for developer-resource integration and
[Storefront authentication](https://shopify.dev/docs/api/storefront/latest#authentication)
for tokenless public data versus token-required fields. Actual pinned schema,
provider behaviour and SDK compatibility are implementation evidence, not claims
that this documentation review exercised a live merchant store.

## C15.1 Document retrieval provider amendment — 2026-09-21

Architect resolution of COMMERCE-011 Attempt 4: the verified tool list of pinned
@shopify/dev-mcp@1.15.4 provides search chunks, not a full-document fetch operation.
Keep that pin for documentation search and the verified schema artifact. For the
existing typed document operation only, Commerce may use a server-owned HTTPS
adapter to official `https://shopify.dev/docs/` pages. This explicitly supersedes
any assumption that every documentation operation must be an MCP tool. The C15
Studio API and U07/N04 workflow remain unchanged; no browser/external IDE handoff
or search-excerpt substitution is accepted.

COMMERCE-011 owns this narrow adapter, preferably `lib/discovery/document.ts`.
It accepts the existing validated path, never a configurable origin, transport,
headers or tool name. Normalize with URL parsing before any fetch; require HTTPS,
exact hostname shopify.dev, default port, no userinfo, query or fragment, and a
normalized path under /docs/. Reject ambiguous encoded separators/traversal.
Use a fresh credential-free request with fixed headers: never forward browser,
Studio, store or environment credentials. Fetch only this public documentation
origin. Handle redirects manually, at most two, applying the same validation at
each hop before fetching; off-origin/non-doc redirects fail closed. No retries.

Use the existing authenticated admission and 20-second total operation deadline,
including redirects/body reading; propagate cancellation to fetch and body reads.
Bound decoded streamed input to 1 MiB before full accumulation/parsing, and return
a typed unavailable/too-large failure if exceeded. Extract the actual document
title and complete main documentation content from verified HTML or a verified
official text representation; do not invent a .md endpoint or schema. A missing
article/title, malformed representation or incomplete content is a typed failure.
The existing response {title,text,sourceUrl} must fit 64 KiB serialized UTF-8,
with title <=255 characters; reject oversized documents rather than silently
truncating. sourceUrl is the final approved canonical documentation URL. Render
text/escaped sanitized Markdown only; no active HTML/scripts or fetched resources.
Documentation is untrusted explanatory content, never executable tool authority.

Evidence: fixture-based selected-document traversal using a sanitized real public
page representation (including content beyond 2,000 characters), exact canonical
source/title, error handling, streamed oversize, timeout/cancellation and rejected
redirect/URL controls. Exercise the production adapter with controlled transports;
no live merchant store, deployed OAuth or Redis saturation run is required. Record
the sample source/acquisition and parser behavior. Search continues to require
actual verified upstream response mapping. COMMERCE-013 owns assembled provider
integration; COMMERCE-008 consumes unchanged typed document results.

## C16. Release-owned response contracts and Studio authoring

This section extends C4/C6/C7/C9. Shared fixes only the delivery envelope; it must
not hard-code release-specific response fields or instructions. Commerce publishes
response definitions as release data. Adding/changing supported details fields or
response guidance requires publication, not a Shared package or worker deployment.
Changing the delivery envelope or introducing unsupported schema constructs requires
an explicit coordinated implementation change; Studio cannot perform that change.

### Persisted definition and compatibility

Add two required columns to CommerceRelease (no new table): responseContract
Json/JSONB and responseContractHash String/varchar(64). No defaults: createRelease
must supply a validated definition; explicit seed supplies the empty-details
baseline. Existing release immutability rules cover both columns. No separate
mutable release draft or response-definition registry. releaseId already pins the
contract for a ConversationGrant; do not add a mutable second version selector.

responseContract is exactly {version:"response.v1", instructions, detailsSchema}.
Instructions are literal text, 1..8000 characters, subordinate to C6.1 platform
and host instructions, before capability prompts. They can guide style and details
but cannot override grounding, language, grants, referral or final-output rules.
Hash is lowercase SHA-256 of RFC8785 canonical JSON of this complete definition;
release ID identifies the published version. Validate/recompute hash on publication
and verify on manifest consumption. Missing/mismatched/unsupported contracts fail
closed as INCOMPATIBLE_VERSION, never fall back to the current active release.

The C4 envelope retains answerKind, replyText, referralReason, detectedLanguageTag,
detectedLanguageConfidence and evidenceIds with exactly their existing constraints.
Add required details, an object validated against detailsSchema. Background ignores
details for sending, routing, billing, language and evidence decisions. Never send
raw details to WhatsApp, render them as replyText or treat them as trusted actions.
For REFER_TO_STORE details is always {} and bypasses required detail properties;
all existing referral constraints remain. For ANSWER details must satisfy the
published schema. C4's named envelope validator accepts details as an object;
Shared's generic runner additionally performs the pinned schema validation.

Supported schema subset is deliberately finite: JSON Schema 2020-12, root object,
additionalProperties:false at every object, types object/string/number/integer/
boolean/array; keywords type, description, properties, required, additionalProperties,
items, enum, minLength, maxLength, minimum, maximum, minItems, maxItems only. No
$ref, regex/pattern, format, defaults, unions, conditionals or external resolution.
Reject unknown keywords. Depth <=4 including root, <=32 property definitions in
total, names match ^[A-Za-z][A-Za-z0-9_]{0,63}$; required names must exist and be
unique. Descriptions <=1000 chars; enum <=20 unique scalar values matching type.
String maxLength is mandatory <=4096; array maxItems mandatory <=20 with one items
schema. Bounds must be nonnegative for length/count and ordered; numeric bounds
must be finite. Definition <=32KiB UTF-8; runtime details <=16KiB UTF-8 and entire
finalResponse remains within existing runner output-token limits. Empty baseline
schema is {"type":"object","properties":{},"required":[],"additionalProperties":false}.
Baseline instructions: "Write a concise, natural WhatsApp reply supported by the
available facts. Return an empty details object." Never require invented detail
values: unsupported factual requests use the existing referral path.

### Publication and MCP/runner consumption

createRelease takes required responseContract along with existing members/reason/
operationId, validates schema and immutable envelope compatibility, computes hash
and persists both atomically with memberships/audit. Replay payloadHash includes
the definition. No edit-in-place endpoint for a published response contract.
Provide ADMIN/SUPER_ADMIN authenticated POST /api/studio/response-contract/validate
with {responseContract,example:{...complete finalResponse}}; return
{valid,errors:[{path,code,message}]} max50, stable JSON Pointer paths. No DB mutation,
model invocation or publication. Use the same pure validation in publish/preview.
Existing staff mutation/CSRF and body-size protections apply. Creation/activation
remain SUPER_ADMIN operations; ADMIN may author locally, validate and preview.

C5 resolve manifest includes responseContract and responseContractHash, loaded from
the selected immutable release. Every subsequent manifest uses the grant's release;
no extra remote tool or public live MCP route. Shared receives this definition,
constructs the host-local finalResponse tool dynamically from the fixed envelope
and details schema (ANSWER/referral branches), injects release instructions and
validates final output against both. It must not switch on detail field names or
fetch definitions itself. Background passes the pinned manifest, retains the stable
envelope adapter and does not interpret custom fields. Reconnects, rollbacks and
active-release changes cannot change an existing conversation's response definition.
If the model SDK cannot express the supported schema subset, fail compatibility
validation; do not silently weaken validation or discard required fields.

### Preview and acceptance

U14 accepts the unsaved composer definition only through its authenticated preview
input, freezes it with the synthetic grant on Start conversation, and displays
replyText plus a separate structured details view and validation errors. Reset is
required to change the definition. No live MCP or production grant accepts browser
contracts. Default fixtures require no model/network. Explicit Model mode retains
existing isolation, quotas, pending-action guards and cancellation semantics.

Required cases R01 empty baseline; R02 add a required bounded string detail and
publish without Shared/Background code change; R03 missing/wrong-type/additional
field rejected; R04 forbidden schema keyword/depth/size rejected; R05 incompatible
envelope cannot be edited or published; R06 simultaneous duplicate create returns
one immutable release; R07 existing conversation stays on old response hash after
activation/rollback while new conversation uses new hash; R08 referral accepts {}
without fabricating required details; R09 ADMIN can validate/preview but cannot
publish; R10 U11 clone/edit/cancel/validate/test/publish traversal; R11 definition
instructions cannot override C6.1; R12 wrong/missing manifest hash fails closed.
Record structural assertions separately from model-behaviour evaluation.



## C6.2. Shop language and subsequent customer language — final amendment

This supersedes prior phone-country and assumed customer-preference requirements
for this recovery path, including conflicting C6.1 language precedence. Initialize
from the shop's configured language using existing merchant-default source. Do not
infer language from phone/country or create preference settings. Missing/invalid
shop configuration uses the existing platform fallback, not a newly guessed locale.

Substantive customer text or persisted spoken-language transcript establishes the
reply language using existing detection, confidence >=0.85, canonicalization and
stale-turn safeguards. Persist detected language for later turns; do not reset it
from shop settings every turn. Short/ambiguous/numeric/URL-only/emoji-only input
retains current language with null detection. Keep prices/currency/URLs/state/policy
unchanged. No new Shared enum, database migration or country mapping is needed.

Initial outreach uses the approved shop-language template; follow-ups use established
conversation language with approved shop-language fallback if its variant is absent.
Record actual template language without replacing detected conversation language.
If no approved fallback exists, preserve existing no-template handling. BACKGROUND-001
A1-L01–L06 is the binding fixture matrix. C6.3 voice requirements remain in force.

## C6.3. Spoken-language voice input — user scope amendment

The Background task's A2 requirements and A2-V01–V07 matrix are binding. Reuse SpeechTranscriptionService; retain Groq and add explicitly selected OpenAI provider/model configuration with proposed OpenAI default gpt-4o-mini-transcribe. No silent switch or automatic paid fallback. Transcribe the spoken language, never force initial shop language or request English translation.

resolve recovery -> download/validate audio -> transcribe -> persist transcript -> normal conversation admission -> CommerceAgent -> WhatsApp text reply. Preserve raw abuse admission, engagement timing, audio bounds/timeouts/retries, duplicate protection and stale-turn checks. Empty/failed transcription uses existing request-to-type handling and never invokes CommerceAgent. Persist metadata without logging audio, transcript contents or credentials.

Verify actual WhatsApp format/codec compatibility with matching MIME/filename. Bounded conversion is justified only by a demonstrated incompatibility; Background owns required image/runtime dependencies. Gateway owns environment-specific provider/model/secret wiring to the messaging runtime, preserving existing Groq selection and explicit rollout/rollback. No reverse Background dependency on deployment or terminal system testing.

Deterministic provider mocks prove workflow. Record representative French/English real-audio quality and format evidence separately, including unrun checks; never claim mocks prove acoustic quality. Official [OpenAI transcription reference](https://developers.openai.com/api/reference/cli/resources/audio/subresources/transcriptions/methods/create) describes input-language transcription, lists gpt-4o-mini-transcribe and accepted audio formats, and recommends format-identifying filename/content type. Provider documentation alone does not prove a particular WhatsApp fixture works; do not mandate conversion without evidence.


## C17. Parallel publication and Studio implementation

COMMERCE-003 and COMMERCE-008 can start and complete their component work after
002, DATABASE-001 and SHARED-001. They prove their contracts using deterministic
fixtures. COMMERCE-013 owns backend integration; COMMERCE-018 owns Studio
integration and COMMERCE-019 owns preview integration, as specified in C20. Each
waits for its explicit prerequisites. GATEWAY-001 requires all three Complete.
This is a task split, not a launcher bypass or deferred acceptance within003/008.
No active011 attempt is reclaimed and no accepted task implementation is reopened.

### Ports and file ownership

COMMERCE-003 owns `src/commerce/publication/` (domain operations, persistence,
read models and port types) and its focused tests.
COMMERCE-008 owns `src/studio/` (page components, view models, ports and adapters),
U01–U13 page entry points and browser fixtures. C20 divides production adapters
and composition among 013 backend, 018 Studio and 019 preview, with separate
owned directories and entry points. Follow the accepted App Router root;
do not create a second app directory. Existing002 auth handlers/helpers remain
owned by their accepted implementation.011 keeps its discovery/compiler modules.
Use separate launcher-resolved worktrees. Never edit another task's port/provider
module to make local tests pass. New adapters wrap accepted exports; incompatible
semantics must be reconciled by the architect, never solved by weakening validation.

Publication defines `QueryValidationPort.validate` with input `{definition}` using
the exact accepted Shared tool-definition type. Result is the discriminated union
`{ok:true}` or `{ok:false,code,issues}`; code is INVALID_DEFINITION,
SCHEMA_UNAVAILABLE or VALIDATOR_UNAVAILABLE; issues are at most32 objects with
`path` (JSON Pointer, max512 chars) and `message` (max512 chars). The013 production
adapter translates011's actual compiler API into this local port and does not
reimplement parsing, projection or semantic checks. Schema identity remains in the
canonical definition; never invent an alternative schema hash. A true result is
not proof of installed runtime executors: publication checks its registry separately.
Fixtures cover each result and thrown timeout/error; unexpected errors fail closed.

Studio defines `StudioServices` with publication commands named exactly as C7,
discovery/schema operations exactly as C15, and read models for each U03–U13 page.
Command argument fields, CAS tokens, role checks, replay operation IDs and results
come from C7/DATABASE-001/C16, not browser-specific substitutes. Read models contain
only the fields required in the binding page specification, use its exact sort/
pagination and preserve IDs/revision versions. Define and test these typed ports
before page implementation. Fixtures and production adapters implement the same
interfaces; UI components never import fixture implementations or provider modules.
003 owns command/read service implementation;008 owns UI port definitions;
013 owns real service translation into those ports.
011's exports supply discovery;005/006/007 supply descriptors, not business-name
lists hard-coded into the UI. Ports remain Commerce-local, with no Shared release
or database change. Record exported method signatures and their canonical-field
mapping in `docs/studio-service-contract.md` in008 and
`docs/publication-service-contract.md` in003 for integration review.

### Fixture isolation and acceptance

Fixture composition is injected by the test harness only, not a public route,
request flag, environment fallback or production dependency factory. Production
adapters use real accepted services; unavailable services return the specified
unavailable/error state and cannot publish, activate or report synthetic success.
Fixtures include success, empty, not found, forbidden, unavailable, stale CAS,
matching replay, conflicting replay and uncertain timeout, with operation counts.
Test UI double-click/keyboard activation against those counts; 018 repeats the
required UI cases against real adapters, while 013 proves backend replay/CAS. Contract tests must run
against both fixture and production adapter with controlled external transports;
matching TypeScript types alone is not integration evidence.

Any shared route/barrel/package configuration edit must be minimal and reconciled
on synchronization.003 does not build Studio pages;008 does not add competing
publication mutations or compiler endpoints. 003/008 submit component/fixture
evidence; 013/018/019 submit their C20 integration evidence. GATEWAY-001 and
terminal caching/system-test gates require all three; 009/017 feed 019.
Fixture acceptance never asserts that the assembled application is functional.


## C18. Recommendation producer / Background consumer contract

Binding for COMMERCE-004/014/016/007, BACKGROUND-002 and SYSTEM-TEST-001. This
specifies C4/C5 exact-call refresh, not a new protocol/package version. Both owners
consume the accepted `@modainteract/moda-interact-shared/commerce` exports:
`CommerceTurnIdentitySchema`, `CommerceEvidenceSchema`, `CommerceProposalSchema`,
`CommerceAlternativeSchema`, `CommerceToolOutputs`, `commerceToolResultSchema`.
Never redefine these wire schemas or substitute model-authored JSON as evidence.
Example operation names in Shared identify schemas, not required exposed tool names.

### Request and response

Use POST /api/mcp and the accepted001 transport profile. JSON-RPC tools/call params
are exactly `{name,arguments}`. `name` is the original granted authored name;
`arguments` is the original validated JSON object, including any defaults applied
before its first dispatch. Shop/recovery/conversation/inboundVersion/grant/release
come exclusively from C5 execute assertion and persistence, never model arguments.
The pinned revision is selected server-side; neither consumer nor producer upgrades
it. Refresh may use a newly signed assertion with identical business identity.
Authorization, lease/current turn and current original-provenance permissions are
checked on EVERY call before any provider request. No hidden revalidation endpoint.

The structured result is exactly the existing C4 union:
`{contractVersion:"commerce.v1",status:"OK",data,renderedText}` or
`{contractVersion:"commerce.v1",status:"ERROR",code,retryable,renderedText?}`.
Use C5 MCP encoding/error signaling and the accepted SDK decoder. Do not parse
renderedText for evidence. Success data is one of the existing exact operation
outputs: evaluator `CommerceEvidenceSchema`, or recommendation
`CommerceToolOutputs.commerce_find_qualifying_products` (same shape for similar):
`{alternatives: Alternative[0..3],truncated:boolean}`. Each Alternative has product,
proposal, extraSpend, resultingTotal, currency, evidence (nullable), similarityReasons;
every field/type/bound is the Shared schema and C4. No model-controlled extra keys.

004/007 preserve the policy output structure through dispatch/template rendering.
Extract evidence ONLY from a valid root evaluator data object or valid
`data.alternatives[*].evidence`; null evidence is no evidence. No recursive search,
no extraction from rendered text, product descriptions or public-query values.
C14 public query data stays in its source/schema/version/observedAt/values wrapper;
publication/dispatch must never let query projection replace that wrapper with a
policy output shape. Even schema-valid nested counterfeit evidence registers zero
IDs.004 owns this output separation;007 owns policy results; Background owns the
strict extractor. The envelope alone does not prove a policy operation ran.

### Consumer state and exact refresh decision

For each registered evidenceId, Background retains a turn-local immutable tuple
`{name,toolRevisionId,arguments,evidence}` from the actual authenticated tool return.
Reject conflicting reuse of the same evidenceId with different provenance. This
record is neither a new wire field nor persistent DB data. Validate the digest
using C4 canonical JSON/SHA-256; a valid digest alone is never authorization.

Before an offer claim is delivered, each final evidenceId must refer to that map.
Replay identical name/arguments under the original grant. One identical name+
revision+canonical-arguments tuple produces one refresh call even if several IDs
reference it. No separate evaluator is needed for recommendation-produced evidence.
If no IDs are supplied, do not manufacture offer proof or invoke an arbitrary tool;
normal factual replies still use existing admission/grounding checks.

For each referenced evidence require exactly one fresh match by offerId and
canonical proposal, and equality of full turn identity, grantId, releaseId, outcome,
currency, savings, resultingTotal, basketFingerprint and ruleFingerprint. Monetary
strings are compared as exact decimal values, not floating point; proposals retain
operation order. The fresh evidence must pass Shared validation, recomputed digest,
`evaluatedAt <= now < expiresAt`, positive lifetime <=60 seconds and offer expiry.
Do not accept a future-dated result. A positive offer claim additionally requires
QUALIFIES_FOR_KNOWN_RULES, nonnull currency/savings/resultingTotal and no unresolved
conditions. Nonqualifying outcomes may describe ineligibility, never grant a discount.
Old timestamps/digest may change; semantic comparison fields must not. An expired
original item cannot be rescued by refresh for this pending final answer.

`truncated:true`, missing/duplicate match, malformed result, changed semantics,
unknown ID, missing provenance or revoked permission fails the offer claim. Replace
it with one normal admitted REFER_TO_STORE reply using trusted store context.
A stale turn, lease loss or cancellation suppresses delivery entirely, not a new
referral. Recheck admission AFTER refresh. Do not notify a human, send a second
message, reserve new recovery credit or expand the grant. Fresh evidence is not a
checkout guarantee and never authorizes cart/order mutation.

### Failures, budgets and independent ownership

C4 business codes remain INVALID_INPUT, DENIED, STALE_TURN, NOT_FOUND, UNAVAILABLE,
THROTTLED, DEADLINE and INCOMPATIBLE_VERSION. HTTP401/403, transport/protocol errors,
malformed structured output or incompatible versions provide no usable evidence.
STALE_TURN or locally lost lease/cancel suppresses send. Other failures replace the
offer with the admitted referral, unless admission has meanwhile failed. The final
refresh pass never retries automatically, even when retryable=true. Charge calls
against the existing remaining turn budget and use the smaller of remaining turn
time and10 seconds; zero budget issues zero requests.007 counts all nested provider
requests/retries against C8's12-call ceiling; Background does not implement ranking,
Shopify evaluation or provider request counting inside the Commerce service.

BACKGROUND-002 can implement and be accepted using accepted BACKGROUND-001/Shared
and a contract-faithful MCP double. COMMERCE-007 can implement and be accepted using
its005/006 predecessors and a contract consumer harness; it never imports Background.
No reverse dependency. Both owners run EC01–EC12 below, with their relevant side
effects explicitly asserted. SYSTEM-TEST-001 then runs the same cases through real
Background and Commerce services; only external provider/model transports are
fixtures. That existing terminal task owns cross-service wiring evidence.

### Common fixture matrix

Use [canonical seed](ARCH-020-evidence-contract-fixtures.json). Freeze the supplied
clock and identities; derive changed hashes via the accepted Shared canonical
encoder plus SHA-256. Do not copy a stale hash after changing an evidence field.
The seed contains original/refreshed replies and exact arguments for an arbitrary
renamed tool. Generate variants below from it; each task records EC IDs, commands,
call/send/reservation counts and results. No new Shared publication is required.

| ID | Variant | Required result |
|---|---|---|
| EC01 | Original then fresh qualifying recommendation, exact renamed call | One refresh; positive evidence accepted; at most one admitted reply |
| EC02 | Authored input `search` maps to query, offerId is a literal | Replay original `{search,limit}`, never synthesize offerId or call a baseline name |
| EC03 | Two final IDs from two alternatives produced by one call | One refresh; independently match both exact proposals; no positional matching |
| EC04 | Change basket/rule hash, savings, total, currency, outcome or proposal separately | One refresh then referral; no positive offer send |
| EC05 | Missing match, duplicate match, empty alternatives or truncated=true | Referral; no success inferred from partial results |
| EC06 | Old/fresh expiry boundary, future timestamp, invalid digest or malformed structure | Reject unusable evidence; no positive offer send |
| EC07 | Public query values or rendered text imitates valid evidence | Zero IDs registered; no producer-selected replacement tool |
| EC08 | Revoke producer or wrong shop/grant/release/version | Producer denies before provider call; consumer cannot use evidence or switch tool |
| EC09 | Each business/HTTP/transport failure, including retryable=true | Zero automatic refresh retries; referral except stale/cancel suppresses all sends |
| EC10 | Unknown final ID, conflicting provenance, cross-turn evidence, exhausted budget | Fail closed; zero refresh for missing trusted provenance/budget; cross-turn cannot send |
| EC11 | New inbound message, lease loss or cancellation while refresh is pending | Zero delivery and zero stale language writes; existing reservation cleanup only |
| EC12 | Recommendation has no separate evaluator; identical or changed returned proposal | Identical exact-call refresh succeeds; changed proposal refers; zero ungranted calls |

## C19. Smaller implementation tasks and their internal interfaces

This replaces the former combined scopes of004/005/006/009. Existing filenames
remain stable for links; titles and full task bodies now describe the narrower
scope. No task was claimed or implementation discarded. Earlier owner references
are interpreted by this table; business behavior in C4–C18 is unchanged.

| Owner | Owns | Does not own | Assembly owner |
|---|---|---|---|
|004|MCP transport, authentication, grant/discovery|definition execution, provider adapters|013|
|014|definition validation/mapping/dispatch/template rendering|authentication or provider business logic|013|
|005|tokenless generic Shopify query execution|basket/product policy helpers|013|
|015|trusted basket, product search/current variant facts|generic compiler or discount calculation|013|
|006|current offer policy, listing, rule retrieval/normalization|eligibility/savings/Evidence calculation|013|
|016|pure eligibility calculation, discounts.evaluate orchestration|provider rule parsing or recommendations|013|
|009|preview routes, runner lifecycle, Redis state/budgets|U14 controls or browser navigation|019|
|017|U14 frontend, typed API client, browser interactions|routes, Redis, database loaders or service composition|019|
|033|OpenAI/Groq PreviewModelPort transport + server config|PreviewService composition, U14, Redis, Background model credentials|019|
|034|U14 tool-vs-conversation source gating correction|preview backend, model transport, synthetic capabilities/prompts|019|

013 wires 004 ->014, then 014 ->005/015/006/016/007, and publication services.
019 wires017 U14 ->009 with actual saved-bundle loading and008 composer return after
033 supplies the accepted provider adapter and034 corrects U14 source gating;018
connects U01–U13. SYSTEM-TEST-001 retains cross-service/Background/gateway acceptance.012 still follows ALL other
implementation tasks. No new interface package publication or DB migration.

### Contract ownership and concurrency

Each port below is Commerce-local TypeScript, not a new wire API. Use the accepted
Shared schemas for all existing identities, grants, definitions, inputs, products,
baskets, evidence and typed errors. Unknown external keys remain rejected. Names
below are required exported interfaces; implementations/files may use existing
repository conventions inside the task-owned directories. No new app root.
Publish the owned type declaration and a success/failure example with its focused
contract test before building the adapter. Producer and consumer use those exact
types; never maintain parallel hand-written copies or simplify fields to fit a UI.

004 owns AuthorizedToolCall and DefinitionExecutionPort in its MCP module;014
imports them.014 owns QueryExecutionPort and PolicyOperationRegistry declarations
in its execution module;005/015/006/016/007 can implement equivalent structural
adapters independently, and013 installs/types-checks them against those ports.
015 owns ProductFactsPort;006 owns DiscountRuleReader/Snapshot;016 imports both.
009 owns PreviewBundleLoader and route schemas;017 imports them. Component tests
inject ports, never dynamically import another task's unfinished implementation.
Any required provider field that cannot map to the declared normalized DTO is
UNKNOWN/UNSUPPORTED, not an excuse to discard a restriction. A required contract
change is reconciled by the architect before either side changes its meaning.

### Transport and execution boundary

`AuthorizedToolCall` has exactly these server-side fields:

- `turn`: CommerceTurnIdentity; `grantId`, `releaseId`, `toolId`, `toolRevisionId`:
  canonical IDs; `name`: exact granted authored name; `definition`: exact pinned
  accepted Shared tool definition; `arguments`: JSON object supplied to tools/call.
- `shopDomain`: verified canonical shop domain; `environment`: existing runtime
  environment type; `limits:{maxRecommendations,maxSearchResults}`: C8 effective
  integers; `deadlineAt`: absolute epoch milliseconds; `signal`: AbortSignal.
- `budget`: shared task-local budget object with
  `reserveProviderRequest(): void`, throwing typed DEADLINE on elapsed time and
  typed DEADLINE on exhausted12 requests. Every actual provider
  request, retry and nested read reserves BEFORE I/O. No reset in nested adapters.

Only004 constructs production context after C5 authentication/ownership/current
permission checks. No route accepts it from JSON. Fixture constructors exist only
in tests. Context contains no token; privileged adapters perform trusted lookup.
`DefinitionExecutionPort.execute(call): Promise<CommerceToolResult>` consumes this
context.014 validates authored arguments, applies input mappings/literals, and
validates exact operation input before provider invocation. Invalid input returns
INVALID_INPUT with zero provider requests. Missing installed revision/adapter
returns INCOMPATIBLE_VERSION or UNAVAILABLE as C4/C5 specify, never latest fallback.
The014 response is the unchanged C4 structured union;004 alone performs MCP encoding.

`QueryExecutionPort.execute({context,execution,variables})` returns the C14 query
fact object `{source,apiVersion,schemaHash,observedAt,values}` inside the existing
success/error union. `execution` is the canonical SHOPIFY_STOREFRONT_QUERY branch,
not arbitrary SQL/URL/code; `variables` is the validated mapped JSON object. Reuse
005/011's canonical fact field names if the accepted Shared query schema specifies
them differently:013 must document the exact mapping, never omit source identity
or return bare projected values. Provider content cannot become policy Evidence.

`PolicyOperationRegistry.get(operation,operationVersion)` returns null or an adapter
`execute({context,input}): Promise<CommerceToolResult>`. The input/output schema is
selected by the canonical operation, not its authored tool name. Keys are exact
installed versions; registration is immutable after service composition.005 has no
privileged fallback.015 owns recovery.getBasket/shopify.searchProducts,006 owns
discounts.getOptions,016 owns discounts.evaluate and007 owns products.findQualifying/
products.findSimilar.014 owns mappings/rendering; providers return structured facts.

Common provider errors use C4's codes/retryable flag, never exception strings.
Cancellation/deadline propagate without fallback or background continuation.
Contract fixtures include concurrent different shops, missing adapter/version,
malformed mappings, nested request ceiling and unchanged structured output after
rendering. Production factories never install fixture adapters.

### Product facts for discount evaluation

`ProductFactsPort.readVariants({context,variantIds})` accepts1–103 unique canonical
IDs (at most100 basket lines plus3 proposed additions), then returns the C4 result
union whose success data is `{variants,complete}`. `variants` is an array ordered
by variantId with one row per requested ID:
`{variantId,product,collectionIds,collectionsComplete}`. `product` is the canonical
Shared Product or null; `collectionIds` is a sorted unique array of IDs, capped1000
per variant; `collectionsComplete` is boolean. Missing product/null price/currency/
availability and partial memberships are unknown, not fabricated absent membership.
`complete` means every requested product was retrieved, not that all its nullable
facts are known. Exceeding membership bounds sets collectionsComplete=false. An
unavailable/throttled request is a typed error rather than a complete empty result.
Use the same context budget across all reads. No discount calculation in015.

### Normalized discount rule contract

`DiscountRuleReader.read({context,offerId})` returns the C4 result union with
`DiscountRuleSnapshot` below.006 verifies current policy/tenant/scope before I/O;
NONE or a different FIXED offer is DENIED. Offer-list success remains the existing
Shared discounts.getOptions shape. Snapshots are internal immutable values, never
new database rows or model-authored arguments.

`DiscountRuleSnapshot` fields (all required, explicit null where permitted):

- `offer`: canonical Shared Offer; `enabled`: boolean or null; `observedAt`: UTC ISO;
  `ruleFingerprint`: C4 SHA-256 of normalized semantic fields, excluding observedAt
  and fingerprint itself; `support`: SUPPORTED | UNSUPPORTED | UNKNOWN.
- `discount`: null or `{kind:"PERCENTAGE",value}` or
  `{kind:"FIXED_AMOUNT",value,currency,appliesPerItem}`. Values are canonical
  nonnegative decimal strings; percentage is >0 and<=100; fixed amount>0;
  currency is canonical and appliesPerItem boolean. Unknown fixed semantics ->null.
- `targets`: null (unknown) or `{kind:"ALL"}` or `{kind:"PRODUCT"|"VARIANT"|"COLLECTION",ids}`;
  ids sorted/unique/nonempty/max1000. If target data is incomplete, use
  null, support UNKNOWN and unresolved code TARGETS_INCOMPLETE; never ALL or a
  partial supported list.
- `minimum`: null or `{kind:"QUANTITY",value,basis}` or
  `{kind:"SUBTOTAL",value,currency,basis}`; quantity positive integer, money canonical,
  basis BASKET | ELIGIBLE_LINES. null with no unresolved MINIMUM_UNKNOWN means authoritatively no minimum;
  otherwise null plus MINIMUM_UNKNOWN records an unknown minimum and cannot qualify.
- `semantics`: null or `{subtotalBasis:"PRE_DISCOUNT_EXCLUDING_TAX_SHIPPING",
  allocation:"ACROSS_ELIGIBLE_LINES"|"PER_ELIGIBLE_ITEM",
  rounding:"HALF_UP"|"HALF_EVEN"|"DOWN",roundAt:"LINE"|"TOTAL"}`.
  A profile is populated only when pinned provider evidence proves every choice;
  unsupported bases/modes yield support UNSUPPORTED and semantics=null. These
  enum values are normalized calculation choices, not assertions about Shopify.
- `unresolvedConditions` and `unsupportedConditions`: arrays max32 of C4 bounded
  `{code,description}`. Restrictions involving customer/usage/combination cannot
  be omitted. SUPPORTED requires known discount/targets/semantics, enabled not null,
  targets not null, complete minimum facts and both arrays empty. Dates use `offer.startsAt/endsAt`.

Where targets/minimum cannot be fully read, use the exact null/unresolved
representations above;016 cannot use them to establish qualification. Never claim
unsupported conditions have been evaluated.016 applies C8 known-failure/unsupported/unknown precedence.

`evaluateDiscount({turn,grantId,releaseId,basket,proposal,rule,variantFacts,now})`
is016's pure function returning canonical CommerceEvidence. `basket`/`proposal`
use Shared schemas, rule is the DTO above and variantFacts is015's success data.
No network/DB/clock lookup inside this function. The discounts.evaluate adapter
loads current inputs through006/015 and passes frozen now; orchestration and pure
calculation tests are separate. The reader proves rule interpretation; evaluator
proves arithmetic against it. Unprovable provider semantics remain UNSUPPORTED.
Do not create a second rule engine in007; it calls016 for every exact proposal.

Required common reader/evaluator fixtures: percentage10 on eligible subtotal100
has savings10/result90 when the proved profile yields that calculation; fixed5
across eligible100 yields5/95; subtotal exactly at and just below its minimum;
expired at exactly endsAt; unknown collection membership; missing currency;
unsupported family; known expired plus unsupported; unproved rounding profile.
Use canonical currency precision and explicit expected results. Production013
runs these through actual006 normalization and016 evaluation, not reader doubles.

### Preview service/page boundary

009 exposes C9.1 routes unchanged. `PreviewBundleLoader.load({principal,selection,
fixtureId})` returns exactly `{grant,manifest}` in the accepted Shared shapes, both validated
and frozen for the synthetic preview conversation. `principal` is the accepted staff principal, selection is C9.1's
strict RELEASE/DRAFT union, fixtureId belongs to the server catalogue. No customer
identity or live provider credentials are accepted. Lookup owner/role/revision
access before returning. The loader maps canonical saved revisions into synthetic
IDs/context; it does not write a production conversation grant. Typed not-found,
denied and unavailable errors use C9.1 status mapping.

009 accepts loader fixtures to test lifecycle independently.013 supplies the real
saved-bundle loader using003 and exercises017 UI against actual009 routes. It
uses014's actual interpreter with fixture provider operations, never production
MCP/Shopify or WhatsApp. C16 U10/U11 response composer stays008-owned. U14 screen,
N10/N11 and the U14 part of N13 move from009 to017; no other pages move.017 must
show populated Tool test and Conversation views with contract fixtures;013 pairs
them with the real service and retain all C9.1 concurrency,
unknown-outcome, reset, role and draft-handoff semantics.

### Completion evidence and integration

Component tasks provide one successful port example and each named failure fixture,
plus their focused behavior matrix. Builds/typechecks or many empty screenshots
cannot substitute for working components.013 performs real backend adapter pairing;
018 pairs Studio services and019 pairs preview/page services; terminal SYSTEM-TEST owns cross-service
conversations. All25 task start edges must be reciprocal and acyclic. This split
adds no automatic task execution or new definition-time provider calls.


Frontend boundary rule for C19:017 can start after008/auth/Shared are accepted,
without009. `PreviewClient` exposes `listFixtures()`, `startConversation(body)`,
`sendRun(conversationId,body)`, `getRun(conversationId,runId)`,
`cancelRun(conversationId,runId)`, `runToolTest(body)` and `getToolTest(runId)`.
Each body/result/error is exactly C9.1, not a second DTO; methods map one-to-one to
its routes. HTTP transport is injected. UI contract fixtures exercise exact outgoing
payloads and return statuses; production client uses authenticated same-origin HTTP.
019 owns saved-bundle loading and I09 actual client/server pairing under C20. Backend task009
never edits page components; frontend017 never edits DB/Redis/route handlers.

## C20. Integration task ownership and parallel execution

This replaces the combined013 ownership in C17/C19. Component behavior and public
contracts remain unchanged.013 is backend-only;018 connects U01–U13;019 connects
preview/U14.018 and019 have NO dependency on each other and may run concurrently
once013 and their own listed components are accepted. Both stay Pending until
those prerequisites complete.012/GATEWAY-001/SYSTEM-TEST-001 require both.

### Fixed file boundaries and producer inventory

All paths below are relative to moda-interact-commerce.013 owns
`src/commerce/integration/backend.ts`, `integration/backend/**` and MCP production
composition.018 owns `integration/studio/**`, the Studio service/action/client
composition and U01–U13 entry points only.019 owns `integration/preview/**`,
`lib/preview/runtime.ts` and U14 client composition. Both consumers import the013
facade; neither edits it. Neither edits the other's application routes or tests.
No shared catch-all integration barrel, global mutable registry or combined factory.

At preparation, inspect each accepted producer SHA and fill the task's
`docs/commerce-<backend|studio|preview>-integration.md` table with source file/export,
input/output mapping, destination adapter, errors and test ID. Most source exports
are pinned in the task definitions from inspected code;007 recommendation and017
client symbols must come from their eventual accepted implementation reports.
Missing export is a concrete gap, not permission to invent another implementation.
013 must finish/freeze its typed facade before either consumer claims work.

### Backend facade contract

013 exports server-only `getCommerceBackend()` from integration/backend.ts.
It returns a read-only object with these members, using the actual accepted types:

- `publication`: CommerceLifecycle; all calls take the server-resolved Principal.
- `discovery`: return type of createDiscoveryService; use existing011 operations.
- `compiler`: return type of createCommerceCompiler; no alternative parser.
- `execution`: DefinitionExecutionPort with real query/policy adapters.
- `createFixtureExecution(registrations, queryAdapter)`: creates the same014
  interpreter with explicit caller-owned fixture ports, without loading live
  installation credentials or the live policy registry. Used only by preview/tests.
- `saved.readSelection({principal,selection})`: authorized read-only saved revision
  selection. selection is the accepted009 RELEASE/DRAFT shape; result supplies exact
  immutable release members or selected draft revisions, definitions, prompts,
  content hashes and responseContract/hash.013 defines the typed result by composing
  accepted003/Shared record types; both consumers import it, never redefine it.
- `inspection.listShops({principal,search})` and
  `inspection.inspectShop({principal,shopId})`: canonical read-only merchant/feature
  eligibility records plus candidate manifest/exclusion reasons for U13. No token,
  customer history, server execution definitions or persisted grant write.

Stateless clients/pools may be reused; principal/turn/grant/policy stay request-local.
Environment comes from validated deployment config, never browser input. Publication
reads and methods do not rely on a previously authorized browser session; each
protected entry rechecks current staff identity/role. Preview selection rechecks
saved-record ownership, conflicts and schema bounds before returning.

013 owns real missing persistence/admission/transport adapters, not only imports:
`createProductionLifecycle()` currently throws unavailable and MCP currently uses
createUnavailableMcpRuntime. Replace those boundaries with durable adapters. Use
canonical Prisma models, C7 READ COMMITTED/locking/CAS/replay and one transaction
for business rows plus audit. Rebuild replay state from durable audit metadata;
never persist process-local Map state as the authority. Never truncate/reinsert
catalogue tables or overwrite unchanged snapshot rows during a state-to-DB diff.
Recheck locked current versions and persist only owned changes. No migrations or
startup seeds. Missing schema/dependency remains unavailable.

Known interface mismatch:008's setCapabilityEnabled includes expectedUpdatedAt,
while inspected003's strict method/schema omits it.013 owns the narrow correction:
accept/validate that timestamp, compare it in the same locked transaction as the
explicit enabled-value write, include it in operation replay hashing and update
the metadata timestamp. Apply the same contract check to tool enable/disable.
A stale timestamp fails without write/audit; altered replay payload conflicts.
Do not perform an unlocked precheck or silently remove the CAS token in018. This
is required C7 compatibility work, not authorization to redesign publication.
Other semantic gaps must be recorded with the exact source/reproduction and resolved
before producer acceptance; consumers must not silently weaken guarantees.

### Studio field and error mappings (018)

Every command retains operationId/reason byte-for-byte, and principal is supplied
only by server auth. Method names are the existing StudioServices interface.

| Studio field/operation | Publication translation |
|---|---|
| createToolDraft.proposedDefinition | definition; sourceToolRevisionId/toolId unchanged |
| createCapability.type | selectionBinding; validate BASE/FEATURE/RECOVERY_POLICY; featureId preserved/null per canonical rule |
| createDraft.sourceCapabilityRevisionId | sourceRevisionId; group promptTemplate/configuration/contractVersion/toolBindings under draft |
| updateDraft.capabilityRevisionId | revisionId; full draft grouped as above; expectedEditVersion unchanged |
| publishRevision.capabilityRevisionId | revisionId; expectedEditVersion unchanged |
| createRelease.members | validate exact capability ownership, unique revisions and contiguous positions; sort by position then pass memberRevisionIds in that order; preserve responseContract |
| activateRelease/rollbackRelease.expectedActiveReleaseVersion | expectedEditVersion; environment from server configuration; selected releaseId unchanged |
| metadata/enable expectedUpdatedAt | unchanged, mandatory;013 supplies atomic support |
| returned publication result IDs | re-read the exact saved record and construct Studio view model; never fabricate revision ID/number, use array position as ID or return latest revision instead |

For createRelease, use publication's documented contractVersion/runnerCompatibility
and description defaults when absent from the UI; do not derive them from user text.
Read models preserve distinct metadata IDs, revision IDs, SemVer, revision numbers,
editVersion and timestamp CAS tokens. Feature.active, plan and merchant preference
remain separate eligibility reasons; U13 never issues live MCP assertions.

Map known NOT_FOUND -> not-found; permission denial -> forbidden;
CAS_CONFLICT -> conflict/STALE_CAS; OPERATION_REUSE_CONFLICT ->
conflict/CONFLICTING_REPLAY; definitive availability errors -> unavailable.
Ambiguous write transport/commit outcome -> unknown with the SAME operationId,
never a retry with a fresh ID. Validation errors retain field paths/content and
make zero writes. If the existing Studio union lacks a required structured validation
variant, add a bounded typed adapter/UI error presentation in018; never relabel an
invalid definition as a committed success. Unexpected exceptions expose no internals.

### Preview mapping and isolation (019)

Use009's PreviewBundleLoader, PreviewPromptLoader, PreviewToolExecutionPort and
PreviewServiceDependencies; lib/preview re-exports those types.019 installs real
implementations in getPreviewService, replacing unavailableLoader, while retaining
RedisPreviewStateStore and009's lifecycle. No duplicate quota/cancel/replay engine.
PreviewPromptLoader returns the actual selected authored prompt text in release
order. Response definition comes from the selected release or validated local C16
draft, not the currently active release after Start. Do not replace prompts with
hard-coded generic instructions.

saved.readSelection feeds a bounded immutable synthetic bundle; freeze definitions
as well as descriptors/prompts. For mutable saved drafts use a grant-scoped frozen
snapshot, never reload draft content by ID during a later turn.019 owns this
server-side snapshot adapter. It may add private snapshot-handle plumbing to009's
internal composition if needed; no new public C9.1 field, DB table or model argument.
Use Redis's existing preview environment/admin/grant isolation and24-hour retention,
maximum32 definitions each<=65,536 bytes, prompt total<=64,000 characters, and
maximum3MiB serialized snapshot. Fail unavailable/invalid selection when bounds
cannot be met; no silent dropping of tools or fresh reload after eviction. Restart
fixtures must prove old conversations retain their exact frozen content.

Only createFixtureExecution with isolated fixture operations is reachable from
preview, including MODEL mode. MODEL changes only the model transport and retains
separate credentials; it never enables live tools. COMMERCE-033 provides the only
production preview model adapter: native-fetch OpenAI-compatible Chat Completions
against the fixed OpenAI/Groq endpoints in C10, `tool_choice=required`,
`parallel_tool_calls=false`, actual `usage.completion_tokens`, direct AbortSignal,
zero adapter retries and no arbitrary base URL/provider fallback. COMMERCE-019 only
injects that accepted adapter; it does not redesign provider transport. Fixture adapters are authorized
preview composition, not a production MCP fallback. Permit no call to live /api/mcp,
Shopify transport, checkout admission or WhatsApp. Tests assert those call counts0.
019 uses013 saved services directly and can mount real008 composer components with
injected source data to prove handoff; it does not wait for018 page-service wiring.

### Shared integration fixture and acceptance ownership

013 supplies an isolated seed/helper consumed by018/019: two active admins with
ADMIN/SUPER_ADMIN roles; two shops, distinct recoveries/conversations; one arbitrary
existing Feature with plan/merchant selection; tool metadata plus exact revisions;
base and feature capability members; two releases and one active pointer; one
original persisted grant. IDs are generated by schema-compatible helpers and returned
in a typed fixture object, never parsed for meaning. Seed explicit unique operation
IDs/reasons and current schema/environment values. Reset only isolated test-owned
rows/Redis namespaces; reject non-test targets. No seed on application startup.

Keep provider/query responses deterministic, model scripted, clock injectable and
DB/Redis real for transaction/distributed-state evidence. Successful duplicate
mutation adds exactly one business effect and audit; failed validation/CAS adds0.
Exact rows differ by command: assert tool/revision/member/pointer IDs and versions,
not a vague total table count. C7 ledger behavior remains the source of truth.

| Former013 acceptance | New owner |
|---|---|
| I01 full authoring traversal |018 S01|
| I02 compiler/publication failure |013 B01;018 displays its actual result|
| I03 MCP pinning/execution |013 B03|
| I04 installed operation registration |013 B04|
| I05 transaction/replay plus UI duplicate behavior |013 B02/B06 and018 S03|
| I06 navigation/composer |018 S02/S06;019 P02 for U14 portion|
| I07 discovery outage/draft retention |018 S04|
| I08 real production composition/no fixture fallback |013 B05,018 S04,019 P05/P06|
| I09 actual preview/Redis/UI pairing |019 P01–P06|

Before final submission each owner runs its named suite, records producer revisions
and demonstrates its success path plus rejection paths. Build/typecheck alone is
not integration evidence. No arbitrary additional screenshot count.013 acceptance
unblocks both consumers; acceptance of one consumer must not block the other's
execution. Gateway/terminal gates require all three completed integrations.

## C21. External API tools and response processing

The binding [external API extension](ARCH-020-external-api-tools.md) adds approved
read-only HTTPS connections, encrypted platform/per-shop credentials, external
execution definitions, visual filtering and sandboxed JavaScript over JSON/text.
C21 defines exact schemas, routes U15/U16 and U06/U14 changes, validation, budgets,
publication sample evidence and task ownership. Existing MCP/Background wire
contracts and grant pinning remain unchanged.012 bypasses external-result caching.

C21 [section9](ARCH-020-external-api-tools.md#9-tightened-implementation-boundaries-and-evidence)
supersedes combined020/024/026 ownership with explicit producer factories, reusable
sandbox proof and scenario-level evidence. No change to existing MCP wire contracts.

## COMMERCE-035 Attempt 4 architect acceptance — 2026-09-22

**Accepted / Complete, Attempt 4** (`9a0120b`; parent report `b357be28`).

The C20 isolated integration fixture boundary has now executed successfully against
real task-owned disposable PostgreSQL and Redis targets. The guarded reset and
focused fixture proof passed, closing the remaining F02/F03/F05/F06 infrastructure
and relational-proof gates. Repository-wide typecheck/lint/build remain blocked only
by previously documented unrelated Shared/external-response/Connections diagnostics;
no COMMERCE-035-owned file is implicated and `git diff --check` passes.

The C20 producer gate is therefore satisfied. This acceptance does not automatically
launch a consumer and does not rewrite newer COMMERCE-018/019 task branches from the
older COMMERCE-035 parent snapshot. Reconcile each current consumer branch after this
acceptance is integrated.
