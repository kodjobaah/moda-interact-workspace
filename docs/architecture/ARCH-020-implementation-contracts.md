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
  selectedCapabilityKeys,grantedTools}; capability order is release position,
  all IDs and grant entries must agree with the immutable release/grant.
  toolDescriptors contain only toolId,toolRevisionId,name,definitionVersion,description,inputSchema;
  execution and responseTemplate stay on Commerce, not in the host manifest.
- CommerceToolResult<T>: {contractVersion, status:'OK', data:T, renderedText:string<=4096} OR
  {contractVersion,status:'ERROR',code,retryable,renderedText?:string<=4096}; error codes are INVALID_INPUT,
  DENIED, STALE_TURN, NOT_FOUND, UNAVAILABLE, THROTTLED, DEADLINE,
  INCOMPATIBLE_VERSION. Do not include arbitrary provider exception text.
- CommerceFinalResponse: {answerKind:'ANSWER'|'REFER_TO_STORE', replyText,
  referralReason, detectedLanguageTag, detectedLanguageConfidence, evidenceIds}.
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
map. Before delivery Background repeats evaluate_discount with the exact trusted
proposal/offer, rejects changed outcome/currency/totals/rule/basket fingerprints,
and replaces the proposed offer answer with a bounded referral on failure. Never
trust a model-supplied evidence object or accept a recomputed hash as authority.

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

This section is binding for BACKGROUND-001, SHARED-002, COMMERCE-009 and
SYSTEM-TEST-001. It replaces vague requirements to preserve the old prompt.

Ownership and composition:

1. Shared owns reusable platform constraints: grant enforcement, factual grounding,
   language rules, budgets and structured final output. Background owns the fixed
   checkout-recovery status instructions and supplies them to the runner as trusted
   host instructions. Neither instruction set is editable in Studio.
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
4. Compose platform constraints and host recovery instructions before the pinned
   capability prompts in membership order, with context/history in separate data
   blocks. Capability text cannot override either fixed instruction layer. Prompts
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
- When languageSource is customer-explicit, that resolved preference governs the
  reply. Ordinary message-language detection cannot replace it; emit both detection
  fields as null. Explicit preference changes continue through the existing
  preference-resolution path, not an invented model-driven override.
- Otherwise, when the latest substantive customer input clearly establishes a
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
  >=0.85 and <=1, preserving customer-explicit preference and existing tag
  canonicalisation. Reuse conversation-language.service.ts; do not introduce a
  second detector, threshold or persistence path.
- Finish by calling host-local finalResponse exactly once, using the C4 schema.
  Include customer-facing replyText and either two null detection fields or one
  valid tag/confidence pair. No reasoning in replyText, no ordinary assistant text
  as a substitute, and no partial pair. Missing, duplicate or malformed final output
  is INVALID_FINAL, not a customer reply. finalResponse is outside remote grants.

Required fixtures (record IDs and outcomes in each owning task): P01 COMPLETED
with null completedAt; P02 EXPIRED; P03 CANCELLED; P04 MESSAGE_SENT/ENGAGED with
and without discovery tools; P05 a later turn changes status to COMPLETED while
retaining the original grant/prompt release; P06 customer-explicit French with an
English message retains French and null detection; P07 non-explicit English with
a substantive French message emits French plus a valid confidence; P08 ambiguous,
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
rank same vendor then shared normalised title tokens, then variantId ascending.
Missing attributes -> no similarity claim. Qualifying suggestions rank lowest
extraSpend then highest known savings then variantId. Return max3. Replacement
removes exactly the selected basket line; quantity must be explicit. Show extra
spend/resulting total separately; no claimed saving relative to the original basket
when the proposed purchase costs more. No match returns [], not invented products.
Internal provider calls are additionally capped at12 requests per remote tool
(including pagination/evaluation) and stop when either count/deadline is reached;
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
COMMERCE_STUDIO_ORIGIN, optional ADMIN_ORIGIN (server-only HTTPS navigation origin), AUTH_SECRET, AUTH_GOOGLE_ID, AUTH_GOOGLE_SECRET,
COMMERCE_PREVIEW_ENABLED (false default), COMMERCE_PREVIEW_MODEL,
COMMERCE_PREVIEW_API_KEY.
Reuse existing DATABASE_URL, REDIS_URL and deployment-environment conventions.
No NEXT_PUBLIC secret; fake examples only. Validate hosted origins as HTTPS,
MCP URL as configured private host; fail startup/readiness on malformed config.
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

Publication-only SHARED-003 consumes accepted artifacts and performs release
mechanics/registry verification; no repetition of implementation test suites.
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
COMMERCE-009 implements U14; COMMERCE-011 supplies discovery/validation services.
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
