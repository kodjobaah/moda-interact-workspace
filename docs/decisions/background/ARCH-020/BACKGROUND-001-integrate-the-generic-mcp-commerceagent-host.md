---
id: ARCH-020-BACKGROUND-001
architecture_id: ARCH-020
title: Integrate the generic MCP CommerceAgent host
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 150
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-020-DATABASE-002
  - ARCH-020-SHARED-004
  - ARCH-016-BACKGROUND-003
  - ARCH-020-SHARED-001
  - ARCH-020-DATABASE-001
  - ARCH-020-COMMERCE-001
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-BACKGROUND-002
  - ARCH-020-SYSTEM-TEST-001
  - ARCH-020-GATEWAY-001
created: 2026-09-20
updated: 2026-09-20
---

# Integrate the generic MCP CommerceAgent host

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Replace hard-coded feature prompts and local product tools with the published MCP capability path.

## Context

Merchant-selected capabilities should drive WhatsApp CommerceAgent behaviour through a separate Next.js MCP server with a team-only Studio. Production conversation admission, ordering, model hosting and delivery remain in Background. This is a pre-production breaking rollout, with no implicit permission to delete durable data.

Task definition is on local workspace main by the developer's explicit 2026-09-20 review request. It is not a claim, task-branch materialisation or implementation approval. All execution fields remain unclaimed.

## Scope

Background agent adapter, MCP client/auth, context normalisation, shared runner integration and conversation grant pinning, plus review scope amendments A1 initial language/template selection and A2 configurable spoken-language voice transcription.

## Out of Scope

Other repositories' implementation, unrelated refactoring, automatic execution of enabled tasks, live deployment, main integration/push and changes to billing prices/merchant entitlements. No cart/order/discount mutation, WhatsApp sending from Commerce, arbitrary executable code or arbitrary-host HTTP endpoints; C14 validated read-only GraphQL definitions are explicitly permitted. No duplicate discount catalogue/merchant configuration system. Shared indexes and architecture reconciliation remain architect-owned.

## Requirements

Follow the parent architecture's tenant/policy/revision contracts and the assigned logical owner. Preserve unrelated changes. Read repository-local AGENTS.md if present. Commerce consumes the canonical database through its nested database/ Git submodule; schema and migrations belong to moda_database. For consumers, use actual accepted and published dependency revisions, not copied task snapshots or hypothetical versions.

## Work Items

- [x] Pass the pinned C16 response definition to Shared and consume only the stable finalResponse envelope; never interpret/send custom details. Cover R02/R07/R08/R12 and grant/hash persistence across turns.

- [x] Implement C6.1 host-owned recovery instructions and freshly loaded, serialized recovery/customer/language context. Apply the explicit status matrix including COMPLETED with null completedAt; replace unrestricted product-help wording with original-grant-only assistance. Keep the pinned prompt release separate from fresh recovery state; use C2 history rather than an authoritative summary.

- [x] Implement the C5 Exact available-tool discovery sequence: trusted shop/recovery/conversation/turn claims, first resolve then immutable grant persistence, execute-purpose tools/list with empty params, and tools/call bound to that original grant. shopId alone is not a grant selector.

- [x] Consume C14 exact reusable tool/revision identities and original capabilityKeys provenance without copying query execution into Background. Manifest may contain arbitrary new names or no remote tools; retain existing conversation grant through reconnects.

- [x] Discover feature-selected tools and schemas dynamically from MCP; invoke by discovered name with the existing pinned grant. Do not download/execute database operations or response templates in Background.

- [x] Search phone-matched recoveries across all merchants on the receiving Moda sender before counting distinct recoveries. Two shop-scoped customers with the same phone and one recovery each require identification; never pick the first customer, infer a merchant from Moda providerAccountId or process the message for both shops. V1 reuses the single Moda sender and requires no merchant WABA/number setup.

- [x] Preserve C13 outbound categories: initial/follow-up attempts each retain their own provider ID and outboundMessageId but share one recovery Conversation. Replies to either template or a later agent message route to that same recovery; repeated outreach counts once. Do not create a grant until the first admitted CommerceAgent turn.

- [x] Enforce the parent "WhatsApp reply correlation decision" before recovery engagement, grant creation or MCP/model execution. Validate referenced outbound message ownership against the incoming customer and configured provider sender; never resolve ambiguity by recency or prior channel binding. For messages without a reference, automatically route exactly one distinct recovery found for the customer/sender; do not request identification in that case.
- [x] For unreferenced messages with zero or multiple candidate recoveries, do not invoke CommerceAgent, create standalone conversations, or mutate a guessed recovery. Exactly one candidate follows the normal recovery conversation path and original tool grant. Use the fully specified C3 lightweight Redis clarification guard; never attach guidance to a guessed merchant.

- [x] Consume the exact published shared version; adapt the real whatsapp.worker.ts runAgent entry path to the shared runner.
- [x] After existing admission, resolve/persist one immutable tool grant per conversation and load manifest/prompts/tools explicitly. First resolution uses resolve-only credentials; persist with unique-key concurrency handling, then use execute credentials bound to the winning pin. All subsequent inbound versions and retries reuse the grant.
- [x] Sign short-lived turn assertions with fixed audience/purpose; keep credentials/tenant identity outside model-controlled tool arguments.
- [x] Require a real checkoutRecoveryId in every wire turn context and verify Conversation -> CheckoutRecovery -> Shop ownership before MCP/model work. Reject missing/sentinel recovery IDs; no standalone or direct-shop fallback. Adapt MCP schemas/results without a feature-specific worker switch.
- [x] Propagate deadline/cancellation and bounded errors through the existing reservation/lease retry lifecycle; remove forced final-after-search and legacy local tool fallback.

- [x] Before the first model invocation create or load one immutable grant per Conversation.id after admission; later inbound versions always reuse it. Supply trusted verified store contact/canonical Shop.domain separately from model arguments, and pass grantId/current turn identity to MCP. Never delete/recreate a grant for capability expansion.

## Scope amendments requested during Attempt 1 review

These are **new user-requested scope amendments A1/A2**, not defects against the original task or its submitted implementation `c3042825ac54f6fbb366baef6dd44b2adbef6972`. Preserve the original Completion Report and validation history. Expanded scope is not yet implemented or accepted. The binding details are also recorded as C6.2/C6.3 in the architecture implementation contracts; they supersede conflicting assumptions about initial language/customer-preference inputs for this recovery path.

### A1 — Initial language selection and subsequent conversation language

- Begin with the shop's configured language. Resolve the customer's numbering country using validated international-number parsing, not prefix slicing, a guessed default region, customer names or an LLM. Require a valid number and an unambiguous country result; a shared calling code alone does not identify a country.
- Apply a deterministic, explicitly approved country-to-language mapping only after validation. Initial approved mapping for this amendment: **FR -> fr**; thus a UK shop with a valid French +33 customer starts in French. Document the supported mapping table and parsing-library metadata/version. Other mappings require explicit approval; an unmapped, unknown, invalid, non-geographic or ambiguous country retains the shop language. Do not infer additional countries from a shared calling prefix.
- Do not add customer language-preference settings, assume those settings exist, or synthesize customer-explicit provenance. The shop baseline and approved phone mapping govern the initial selection. Existing generic legacy source enum support is not evidence that a customer configured a preference.
- Apply the initial selection consistently to initial recovery messages and follow-ups until substantive customer language is established. Select an available, approved WhatsApp template translation for the selected language. If unavailable, use the shop-language approved template; if that is unavailable too, preserve the existing no-approved-template handling. Record the language of the actual selected translation honestly; never relabel untranslated text. Template fallback does not masquerade as customer language evidence.
- Once substantive customer text or a completed spoken-language transcript establishes a language, use that language for subsequent replies and retain it across turns. Short/ambiguous, numeric, URL-only or emoji-only input cannot switch it. Reuse the existing stable-signal/confidence and stale-turn persistence safeguards; phone initialization must not repeatedly overwrite an established conversation language. Subsequent applicable follow-ups use the established language subject to the same approved-template/shop fallback.
- Never change currency, prices, URLs or merchant policy as a language side effect. Preserve the trusted store contact in referrals; document coverage and actual fallback language for fixed reply/referral text. The reported seven-language referral catalogue must not be represented as universal language coverage.
- Shared owner coordination confirms 0.13.1 has no truthful source for phone-country selection. A new **phone-country** source requires Shared-owned schema/type/commerce-runner validation tests and publication. Persisting it also requires Database-owned **PHONE_COUNTRY** LanguageSource enum support and Background's wire/Prisma mappings. Do not label it detected, shopify, merchant-default or customer-explicit, or bypass the source validator. Compatible storage/readers and an accepted published contract must precede emitting the new value. Preserve accepted SHARED-001/DATABASE-001 history; these are new-scope owner handoffs, not retroactive defects. No other repository implementation belongs to this task.

### A2 — Voice transcription and CommerceAgent input

- Reuse SpeechTranscriptionService and add an OpenAI adapter with explicit provider/model configuration. Proposed OpenAI default: **gpt-4o-mini-transcribe**, only when OpenAI is selected. Preserve Groq and its existing deployment selection; no silent provider switch and no automatic paid/provider fallback. Validate configuration and report bounded configuration failure rather than selecting another provider.
- Transcribe speech in its spoken language. Use transcription, not English translation; do not force shop/phone language into the transcription request. French audio must yield French text and English audio English text, independently of initial locale. Feed the persisted transcript through the same stable language handling as substantive text.
- Make this order explicit and test it: **resolve recovery -> download and validate audio -> transcribe -> persist transcript -> normal conversation admission -> CommerceAgent -> WhatsApp text reply**. Preserve the existing raw abuse gate and engagement timing. Routing/ownership must precede audio download; normal merchant admission must follow successful transcript persistence. Do not create a second admission, reservation or delivery path.
- Verify actual WhatsApp container/codec/MIME combinations, including representative Ogg/Opus voice notes, against the selected adapter. Supply matching content type and an extension-bearing filename. Use bounded conversion only for a demonstrated incompatibility; never simply relabel bytes. If needed, constrain input/output bytes, duration, process time, concurrency and temporary-file lifecycle, and have Background own the image dependency. Do not assume all provider/model/format combinations work from a mock alone.
- Preserve current audio size/duration limits, media validation, provider timeouts, retry classification/budgets, duplicate protection, engagement handling, lease/version checks and stale-result suppression. Conversion/provider retries must fit those bounds, not introduce an unbounded extra retry layer.
- Empty, failed, unsupported or exhausted/timed-out transcription must not invoke CommerceAgent. Use the existing request-to-type fallback and its duplicate/safe-delivery handling. A duplicate or late completion must not generate another inbound turn, spend another agent reservation or send a stale reply.
- Persist the successful transcript through existing protected conversation records, and record provider/model metadata. Do not log audio, credentials or transcript content, including SDK exceptions and diagnostic payloads. Metadata must describe the adapter actually used.
- Coordinate hosted configuration with Gateway through GATEWAY-001: final selector/model variable names, allowed values/defaults, selected-provider credentials, messaging-worker scope, independent test/production values, and explicit rollout/rollback. Existing translation-worker OpenAI configuration does not provision messaging transcription. Preserve Groq selection until an explicit OpenAI configuration change; no live deployment is authorized by this amendment.

### Amendment acceptance matrix

All cases below require named deterministic fixtures and observed side effects, not only prompt assertions. Keep them separate from the original Attempt 1 results.

| Case | Required outcome |
|---|---|
| A1-L01 UK shop / validated French +33 customer | FR -> fr mapping selects approved French initial and follow-up templates; correct actual translation metadata. |
| A1-L02 unknown/invalid/unmapped number | Shop language retained; no guessed language or country. |
| A1-L03 ambiguous numbering country | Unresolved shared-code/country fixture retains shop language; no first-country selection. |
| A1-L04 missing French template translation | Approved shop-language template selected and honestly labelled; unavailable shop variant follows existing no-template outcome. |
| A1-L05 customer replies in another language | Substantive text or persisted transcript establishes the new language for subsequent replies; amount/currency/URLs/policy unchanged. |
| A1-L06 ambiguous replies | Short, numeric, URL-only, emoji-only and otherwise ambiguous input retain current language and do not emit false detection. |
| A2-V01 French and English voice notes | Provider mocks preserve spoken language despite opposite shop/phone language; request does not force initial language or request English translation. |
| A2-V02 successful transcript-to-reply | Full ordered workflow persists once, admits once, invokes CommerceAgent once and delivers the WhatsApp text reply. |
| A2-V03 unsupported audio | Validation/bounded conversion decision is explicit; unsupported result uses request-to-type with zero CommerceAgent calls. |
| A2-V04 empty transcription | Request-to-type, zero CommerceAgent calls/reservations and no invented transcript. |
| A2-V05 timeout/provider failure | Existing bounded retry/terminal handling, request-to-type on exhaustion, no silent provider fallback, no agent invocation. |
| A2-V06 duplicate delivery | Single transcript completion/turn/admission/reply; preserve existing engagement semantics. |
| A2-V07 stale completion | Late audio/model completion cannot send or mutate the newer turn/language; assert version/lease checks and zero stale delivery. |

Representative real-audio quality checks are a **separate evidence record**, not deterministic workflow-test results: identify synthetic/consented fixture IDs, French/English spoken language, container/codec/MIME, duration, provider/model/date, conversion if any, language retention and material transcription errors. Do not put transcript/audio/credentials in runtime logs. Report any not-run checks and their validation limitation explicitly; mocks cannot prove real codec acceptance or transcription quality. Do not automatically run paid/provider tests as part of unit tests.

### Completion gates for amended scope

- [ ] A1-L01–L06 implemented and validated; approved mappings documented.
- [ ] Shared/Database source extension coordinated, independently accepted and available before phone-country emission; exact consumed revisions/version recorded. Architect must materialise the new owner prerequisites and reconcile dependencies before returning the whole amended task to Ready.
- [ ] A2-V01–V07 implemented and validated with deterministic provider mocks; Groq retained and explicit OpenAI provider/model behavior verified.
- [ ] Gateway configuration handoff recorded; no reverse dependency on deployment/system-test is introduced.
- [ ] Representative real-audio quality evidence recorded separately with exact outcomes/limits; original build/focused workflow checks rerun as appropriate.

## Interfaces / Contracts

Read the binding schema contract in docs/decisions/database/ARCH-020/DATABASE-001-persist-capability-releases-and-turn-revision-pins.md. Its exact field names/types, enum values, JSON shapes/bounds, immutable release membership and selectedCapabilityKeys/grantedTools conversation grants are the persistence contract; do not invent alternative representations. Shared APIs serialize dates as ISO strings and map database environment enums to lower case.

Shared ./commerce and ./commerce/runner. Consume accepted database schema via Background database submodule; server fixtures allow independent implementation.

### Implementation guidance

Apply binding contracts **C14–C15** for reusable tool revisions, query/policy execution, safe templates, original grant provenance and integrated Studio authoring. The page/traversal specification is required for UI owners.

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C0, C1, C2, C3, C4, C5, C6**. Also apply **C13** for outreach/continuation semantics. These are required acceptance inputs, not optional examples.

Own routing service, conversation/audio persistence, generic MCP host and narrow platform routing-reply service. Reuse existing message/provider IDs, recovery/customer links and shared inbound/status parsers unchanged. Add no WhatsApp schema fields. Preserve batching and assemble prior same-conversation history using existing records. Remove standalone/clarify-basket agent branches.

### Required evidence

Unit/integration fixtures cover valid reference delayed1h/10h, no-reference0/1/2 distinct recoveries, duplicate outreach for one recovery, terminal recovery ambiguity, invalid explicit reference without fallback, existing stored-message ownership, voice routing before download, prior-question follow-up and unchanged batching/stale-turn safeguards. Routing guidance tests assert exact fixed text, no merchant usage/grant, one Redis SET NX winner per event within 24h, existing abuse limits, Redis-error suppression, and retained guard after failed/ambiguous sends.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

## Dependencies

- ARCH-020-DATABASE-002
- ARCH-020-SHARED-004

- ARCH-016-BACKGROUND-003
- ARCH-020-SHARED-001
- ARCH-020-DATABASE-001
- ARCH-020-COMMERCE-001

Every dependency must be Complete and architect-accepted before execution. Reconcile accepted dependency metadata into the matching parent task branch before promotion. Developer integration or explicitly approved accepted-commit consumption is required to obtain prerequisite source. Readiness never launches a task. Commerce tasks additionally require the new-owner setup checkpoint.

## Enables

- ARCH-020-COMMERCE-012

- ARCH-020-BACKGROUND-002
- ARCH-020-SYSTEM-TEST-001
- ARCH-020-GATEWAY-001

## Acceptance Criteria

- [ ] Demonstrate the assigned C16 response-contract cases with named fixtures and actual outcomes; reference the exact published definition/hash or synthetic preview definition used.

- [ ] Verify C6.1 P01–P12 through host integration fixtures, including fresh status on later turns, explicit-language precedence, validated detection persistence and no delivery from invalid/stale final results.

- [ ] Two conversations for one shop with different pinned releases retain different original lists; a second shop cannot select those grants. tools/list contains exact descriptors only, omits revoked tools, rejects caller-supplied shopId parameters and never expands after publication.

- [ ] Newly published query tool works for new grants without a Background build, while a retained grant cannot discover it; no fixed conversation_core/product_search admission dependency remains beyond legitimate current feature entitlement checks.

- [ ] Valid explicit replies resume only their referenced recovery and original grant, including replies delayed by one or ten hours with intervening outreach to other recoveries.
- [ ] Unreferenced messages with exactly one recovery route without clarification. Unreferenced zero/multiple-candidate, unknown-reference, wrong-customer, wrong-provider and missing-recovery cases cannot invoke CommerceAgent or access merchant tools. Replying to an unowned clarification cannot manufacture a recovery link.

- [ ] New conversations consume compatible tool/prompt revisions without redeploying Background; all turns/retries of existing conversations reuse their original exact tool grant and prompt release.
- [ ] Unknown contract/runner versions, MCP outage and invalid results fail explicitly; no hard-coded discount fallback is used.
- [ ] Existing language handling, admission ordering and structured final-response semantics remain intact with the generic runner.

- [ ] Two turns of the same conversation use the same grant despite a new release/feature or worker restart. Concurrent first turns select one winning grant; a different eligible new conversation may receive the new release.

## Validation

- [ ] Publish a newly named supported tool without Background deployment, use it for an eligible new conversation, and prove an existing conversation cannot list/call the new name or template version.

- [ ] Add focused multi-turn grant and unanswerable-question fixtures for the scoped acceptance criteria; assert granted tool IDs/versions and referral output, not just prompt text.
- [ ] Run focused Vitest tests with a local mock MCP server for discovery, prompt retrieval, tool calls, tenant headers, release pin races and deadlines.
- [ ] Run declared npm run build and git diff --check; do not assume lint/typecheck scripts exist.
- [ ] Record the client/server compatibility set established by Commerce foundation before acceptance; mocks alone cannot prove cross-SDK interoperability.

Use package.json commands actually provided by the repository. New Commerce scripts and test fixtures are deliverables, not claims that they exist today. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md. Separate local evidence from pending developer-owned long/live validation; required evidence must exist before acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; its real repository must be provisioned before execution preparation.

## Completion Report

### Status

Review — Attempt 1, executor codex. Scoped implementation and local validation submitted; no architect acceptance or Complete decision is made. Architectural acceptance checkboxes remain for the coordinator to assess against the evidence and limits below.

### Files Changed

Implementation commit `c3042825ac54f6fbb366baef6dd44b2adbef6972`, [Background PR #48](https://github.com/kodjobaah/moda-interact-background/pull/48):

- `src/commerce/`: MCP transport/assertions, grant persistence, Shared runner/model adapter, fixed recovery instructions, history, verified referral rendering and bounded tool observation.
- `src/agents/commerce.agent.ts`, `types.ts`: production entry adapter and Shared stable response envelope; deleted unused legacy `commerce.agent.fake.ts` local-tool path.
- Routing/guidance, worker, checkout context, conversation/turn processing, audio ownership and WhatsApp timeout support under `src/services/` and `src/workers/whatsapp.worker.ts`.
- Focused routing, guidance, MCP HTTP integration, model adapter, history, ordering, language/lease, audio and observability fixtures under `tests/`.
- `package.json`, lockfile and `docs/commerce-host.md`.

Parent changes are restricted to this task file. No schema, other implementation repository, architecture/index, or parent service gitlink changes.

### Work Completed

The admitted WhatsApp worker now uses Shared 0.13.1 through private MCP rather than hard-coded product tools. Resolve credentials select a candidate only; the unique conversation grant is persisted before execute credentials retrieve prompts/list/call. A P2002 loser reloads the winning pin, including when its release differs. Existing grants retain original capability provenance, exact tool/revision identities and release response hash; current tools/list may only reduce the usable set.

Reply correlation now validates the configured Moda sender, confirmed outbound reference and recovery-customer ownership, without invalid-reference fallback. Unreferenced candidate discovery uses a database DISTINCT/LIMIT 2 query across merchants and all recovery statuses; repeated outreach is represented once by the unique recovery conversation. Stored inbound ownership is preserved. Guidance uses fixed C3 text, the existing raw abuse admission, Redis SET NX EX 86400 and a 10-second provider deadline, with no guessed merchant conversation, grant or usage reservation. Voice guidance precedes download/transcription.

Fresh persisted status/customer/language is separated from pinned prompts and bounded prior conversation history. The current input is supplied separately from the prior history to preserve Shared's 20-entry history bound. No summary is authoritative. Current-only overflow takes the admitted shorter-question path without model/grant work. Language persistence and delivery checks reject changed versions/expired leases. Custom details are dropped from the host result; only the stable envelope leaves it.

### Validation Results

All commands ran in the prepared implementation worktree using the canonical workspace Node bootstrap. No live Groq, Shopify, Meta, Commerce deployment, managed database or queue was contacted.

- `npm run build` — passed, including Prisma generation and TypeScript compilation; rerun after final production changes.
- Focused 17-file regression invocation below — **181 passed**, 5.51 seconds.
- Final changed-fixture invocation `npx vitest run tests/integration/commerce/host.test.ts tests/unit/services/recovery-routing.service.test.ts` — **46 passed** in two files, 3.20 seconds. Includes 28 host cases and 18 routing cases; supersedes the earlier versions of those fixtures.
- `git diff --check` — passed before commit.
- Implementation worktree clean after commit/push.

```sh
npx vitest run tests/integration/commerce/host.test.ts tests/integration/commerce.agent.integration.test.ts tests/unit/agent tests/unit/observability/genai-observability.test.ts tests/unit/services/commerce-history.test.ts tests/unit/services/checkout-refresh.test.ts tests/unit/services/conversation.service.test.ts tests/unit/services/inbound-whatsapp-audio.service.test.ts tests/unit/services/conversation-turn-processor.service.test.ts tests/unit/services/conversation-language.service.test.ts tests/unit/services/outbound-whatsapp-admission.service.test.ts tests/unit/services/recovery-routing.service.test.ts tests/unit/services/routing-guidance.service.test.ts tests/unit/workers/whatsapp.worker.test.ts tests/unit/services/whatsapp.service.test.ts tests/unit/recovery-outreach-follow-up.test.ts
```

Compatibility actually exercised: Node 24.19.0, npm 11.17.0, Prisma client/generator 6.19.3, Shared **0.13.1** / runner **1.0.0**, MCP SDK client and server **1.30.0**, protocol **2025-11-25**. The HTTP fixture runs the actual SDK Client and WebStandardStreamableHTTPServerTransport in the stateless JSON profile established by COMMERCE-001. Empty 202 notification acknowledgements are handled; no SSE/session dependency is introduced. Persistence and model behavior are mocked/scripted, not represented as a live database or live-model rehearsal.

#### Requirement-to-fixture matrix

| Requirement | Fixture / expected side effects | Actual outcome |
| --- | --- | --- |
| C2 delayed explicit reference | `recovery-routing.service.test.ts`: 1h/10h confirmed outbound, including later FAILED delivery state; select only referenced recovery, no phone fallback query | Passed |
| C2 0/1/2 distinct; cross-shop terminal ambiguity | Same file: DISTINCT/LIMIT 2 query shape, 0/2 guidance before eligibility, 1 normal route; completed/expired candidates remain ambiguous | Passed with mocked query results; SQL not executed against PostgreSQL in this task |
| C13 initial/follow-up/agent reference | Same file: each outbound category routes to one recovery conversation; query uses EXISTS so multiple sent messages cannot multiply candidates; existing `recovery-outreach-follow-up.test.ts` remains green | Passed |
| Invalid/unknown/wrong-customer/provider/missing ownership | Routing fixtures: no fallback or execution; stored inbound mismatch rejected; audio persistence ownership race rejected before download | Passed |
| C3 platform guidance | `routing-guidance.service.test.ts`: exact four reason texts; hashed environment key, EX 86400/NX, concurrent one-winner, Redis errors, guard retained after failed send, unsupported/wrong sender suppressed | Passed; no merchant service dependency in helper |
| Routing before audio/model/admission side effects | `whatsapp.worker.test.ts`: ambiguous voice never downloads, records recovery activity or enqueues agent; raw abuse guard precedes routing | Passed |
| C2 history/order/bounds | `commerce-history.test.ts`, checkout context ordering fixture: prior question retained, ID dedupe, Unicode cap/drop-oldest, current overflow and explicit automation-descriptor label; query excludes unsupported/incomplete audio/unsent outbound | Passed; query filters inspected, not a database query-plan rehearsal |
| C5 first resolve / execute credentials | `commerce/host.test.ts`: verify RS256 signature, fixed iss/sub/aud/environment, <=120s lifetime, no resolve grant selector; tools/list params exactly {}, tool calls carry no credentials in model args | Passed over actual local SDK HTTP |
| Grant retry/restart/new turn and release race | Host fixtures: persistent mock row reused across independent host invocations; concurrent inserts select one grant; P2002 winner with a different release replaces the losing candidate | Passed; database uniqueness itself is accepted DATABASE-001 evidence |
| C14 newly authored tool / no expansion | Host fixture uses distinct new tool/revision IDs and arbitrary name for a new conversation, while old grant excludes it; server expansion denied, revocation omits tools, empty original grant remains usable for referral | Passed with synthetic immutable manifests; not a live Studio publication |
| C6.1 P01–P04 | Host table fixtures for COMPLETED with null completedAt, EXPIRED, CANCELLED, MESSAGE_SENT and ENGAGED: fresh status as data, fixed status matrix/original-grant restrictions, historical total preserved; separate zero-tool fixture | Passed scripted/context composition evidence |
| C6.1 P05 | Second version loads COMPLETED while retaining original release/grant/hash | Passed |
| C6.1 P06 | Explicit French blocks model language replacement; host referral uses French and verified Shop.domain, never model contact text | Passed |
| C6.1 P07–P09, P12 | Host metadata/null fallback cases plus existing language service and conversation tests: confidence/stability rules, explicit preference, no invented regional upgrade, amount unchanged, version/lease CAS persistence | Passed; fixed referral locale coverage noted below |
| C6.1 P10 | Customer instruction-like name stays in data, summary omitted; extra model shopId tool argument rejected INVALID_INPUT before tools/call | Passed; not a semantic guarantee for arbitrary model prose |
| C6.1 P11 | Invalid final rejected; changed version/expired lease/cancellation cannot return a deliverable result; processor does not persist language or send when stale | Passed |
| C16 R02/R08 | Synthetic response.v1 details schema requires bounded `summary` for ANSWER; custom details validate but never leave host, referral permits {} despite required answer detail | Passed |
| C16 R07/R12 | Old release response hash survives publication/turn; missing/wrong hash, unknown contract/runner fail before model use | Passed |
| C6 deadlines/outage | MCP outage gives bounded failure, cancellation interrupts model; accelerated timer fixture asserts real 90,000ms host/10,000ms request timeout configuration and DEADLINE result | Passed; no 90-second wall-clock wait |
| Existing lifecycle/telemetry | Quiet/max-settle, admission/reservations, outreach, duplicate handling, language, stale result and provider fixtures; fixed `commerce-mcp` telemetry identity excludes sensitive fields | Passed |

### Deviations

No cross-repository workaround or schema change. The prior-history/current-input split accommodates Shared's explicit 20-history-entry bound while retaining up to 20 earlier messages plus current fragments. Serialized aggregate character counting is conservative relative to content-only length.

The old live test that depended on a local product-tool override was replaced by a deterministic AI SDK adapter fixture; it no longer auto-invokes a model just because a developer key exists. Required cross-SDK evidence is the local real-SDK HTTP fixture, not a handwritten transport mock.

### Assumptions

The canonical single Moda sender remains the inbound authority. MCP URL/key provisioning is deployment-owned. Current entitlement/revocation enforcement on every remote call remains Commerce-owned; Background enforces that discovered descriptors are a subset of the immutable grant and never executes downloaded query definitions/templates.

### Unresolved Issues

- Fixed host referral translations currently cover en/fr/de/es/it/pt/nl; other locales fall back to English. Architect must assess this explicit coverage limit against the desired merchant language scope before acceptance.
- Local scripted fixtures prove host enforcement and fixed instruction/context composition, not factual/semantic compliance of a live model. No live Studio publication/query, database SQL routing rehearsal, or deployed service call is claimed. Full cross-service publication/execution remains the explicitly invoked SYSTEM-TEST-001 acceptance path after its dependencies are ready.
- Discount evidence extraction and pre-send re-evaluation belong to enabled BACKGROUND-002. This implementation does not register discount evidence; unregistered evidence IDs fail Shared validation. Do not treat this host submission as acceptance of discount delivery safeguards.
- npm reported three high-severity audit findings in the installed dependency tree during installation. No forced unrelated major upgrade was performed.

No developer long/live command was invented or run. The exact local rerun commands are above; deployment/system-test execution remains a separate explicit task invocation, not an automatically started follow-up.

### Architectural Concerns

Review the referral translation fallback explicitly. The synthetic SDK fixture is independent of unfinished production Commerce endpoints; accepted COMMERCE-001 establishes transport compatibility, while production authorization/query integration still requires the remaining architecture tasks. No claim of end-to-end deployment readiness.

### Git / VCS

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-BACKGROUND-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-BACKGROUND-001`.
- Both branches: `task/ARCH-020-BACKGROUND-001`; Attempt 1 retained, no re-claim.
- Prepared parent incorporated origin/main at `05d3dfa3dea5dc71633fed4e4cab9d401b6cf329`; claim `1a6ccebb3f6e38cefd4b8aa72d6e3e8befe9f7ed` committed/pushed by launcher. Implementation prepared at `58e394ad91a1404ba36863e765148d986f0ff29c`, main already current.
- Recursive database submodule initialized/verified at `5abfd87f57038bae515aaa09ec7c8db62adcfb98`, unchanged.
- Implementation `c3042825ac54f6fbb366baef6dd44b2adbef6972` committed/pushed; [PR #48](https://github.com/kodjobaah/moda-interact-background/pull/48).
- This parent report is submitted as a separate task-branch commit/PR; its publication result is recorded in the session and PR history (no self-referential commit hash).
- No main merge/push, parent service gitlink update, architecture/index edits, dependency launch or architect acceptance.

## Architect Review

### Review disposition — scope amended, acceptance pending — 2026-09-20

Status remains **Review**, Attempt 1, claim cleared. User-requested A1/A2 above are scope amendments, **not original-task defects**. No Accepted/Complete or Changes Requested defect verdict is asserted by this amendment. Original report/implementation remain preserved; no new attempt is claimed and no downstream task is promoted. Do not reclaim until the new Shared/Database owner prerequisites have been materialised/reconciled and the architect returns the expanded task to Ready.

Reviewed submission heads: implementation `c3042825ac54f6fbb366baef6dd44b2adbef6972` (PR #48), report `4deb753816f49436e11f0dfa3dd0a2097e0f923d` (PR #168); remote PR heads verified. Inspected report, grants/host and language/referral/transcription/audio/template paths. Independently ran four focused files covering host, recovery routing, inbound audio and conversation language: **66 passed**. Initial sandbox invocation failed before tests while writing Vitest temporary configuration; the authorized rerun passed. Submitted build and broader tests remain developer-reported evidence. This scoped review does not assert full original-scope acceptance or amended-scope validation.

Shared owner confirmed the new phone-country source requires both Shared validation/publication and Database enum support; no accepted task is reopened. Gateway owner confirmed messaging worker needs its own scoped transcription configuration/credentials; the translation worker's OpenAI key is not sufficient. Handoffs are durable in the contract and domain coordination notes. The seven-language fixed referral coverage remains an explicit item to assess under A1; do not silently treat English fallback as matching another language.

### Historical definition review


### Review Status

Pending.

### Review Notes

No implementation submitted. This task is a reviewable definition.

### Reviewed Files

None for implementation review.

### Validation Reviewed

None for implementation review.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile task/index/frontier after review; preserve the terminal/manual system-test gate.


## Dependency readiness — 2026-09-20

All listed prerequisites are architect-accepted Complete following SHARED-001 Attempt 2 acceptance. Consume exact published Shared 0.13.1 (commerce and commerce/runner exports). Ready is eligibility only: no claim or execution is made by this review. Normal preparation must synchronize the canonical task worktrees and verify dependency source availability; do not silently use an older database/service revision.

### Architect prerequisite reconciliation — 2026-09-20

Document conflicts with current main are resolved, preserving A1/A2 and the original
Attempt 1 report. New prerequisites are ARCH-020-DATABASE-002 and
ARCH-020-SHARED-004, both Ready and unclaimed. Background remains Review with
claim cleared; no rejection of original scope is implied. After both are accepted
Complete, consume the integrated enum/client and published Shared version, then
architect promotes this same Background task to Ready for Attempt 2. Do not claim
now or use the old package to emit phone-country.
