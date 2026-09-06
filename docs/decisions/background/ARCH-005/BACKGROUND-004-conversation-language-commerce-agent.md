---
id: ARCH-005-BACKGROUND-004
architecture_id: ARCH-005
title: Resolve conversation language through CommerceAgent validated final result
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 60
executor: null
claimed_at: null
attempt: 4
depends_on:
  - ARCH-005-BACKGROUND-001
enables:
  - ARCH-005-SYSTEM-TEST-002
created: 2026-09-06
updated: 2026-09-06T02:59:13+01:00
---

# Resolve conversation language through CommerceAgent validated final result

## Architecture

This task remains owned by `moda_background` because the inbound WhatsApp worker,
Conversation persistence, CommerceAgent execution and outbound free-form response
all live in `moda-interact-background`.

Attempt 1 correctly introduced durable conversation language/source fields,
anti-flapping policy and structured language context for CommerceAgent, but it
placed language detection behind a `LanguageDetector` whose production default
always returned `null`.

Attempt 2 correctly moved language detection into the existing CommerceAgent turn,
but used provider Structured Outputs together with product tools.

Attempt 3 corrected that design by replacing `Output.object(...)` with a dedicated,
side-effect-free, schema-validated `finalResponse` tool in the same bounded agent
loop and by enforcing `customer-explicit` language precedence. Those parts are
architecturally accepted and MUST be retained.

Attempt 3's real-provider validation then exposed a different issue: production
hardcodes `openai/gpt-oss-20b`, and that particular model did not successfully
complete the declared tool loop in the opt-in integration path. The architecture
does **not** require GPT-OSS. The Groq model is a replaceable deployment/runtime
choice and must not be embedded as a CommerceAgent architectural constraint.

Attempt 4 therefore makes the CommerceAgent model explicitly configurable through
`GROQ_COMMERCE_MODEL`, keeps the accepted one-call `searchProducts -> finalResponse`
design, and validates that design against the same configured model used by the
real runtime.

Do **not** add a model-specific workaround for `openai/gpt-oss-20b`, a second LLM
call, an undeclared catch-all tool, or an unvalidated free-form fallback.

## Objective

Allow an active WhatsApp conversation to retain its existing resolved language,
respond naturally when the latest customer message clearly switches language,
and persist that switch only when the **existing CommerceAgent run** reports a
valid high-confidence language signal through its validated final-response tool
and that signal passes application stability rules.

## Context

`ARCH-005-BACKGROUND-001` already materialises initial Shopify/merchant
international context into durable Conversation fields.

The following work is already architecturally accepted and must be preserved:

- `Conversation.languageTag` / `languageSource` typed persistence;
- structured language fields in CommerceAgent context;
- BCP-47 canonicalisation;
- confidence/stability and anti-flapping policy;
- same-base locale preservation;
- stale-`inboundVersion` protection;
- independence from phone/country/currency/Market/shipping geography;
- one CommerceAgent `generateText()` invocation per turn;
- product tool execution followed by a schema-validated `finalResponse` tool;
- bounded failure when no valid final response is produced;
- `customer-explicit > detected > Shopify/merchant/platform fallback` precedence.

Attempt 3's optional real-provider test now exercises the real
`commerce.agent.ts` path. That test established that the hardcoded
`openai/gpt-oss-20b` choice is the remaining runtime blocker; it does **not**
justify redesigning the accepted agent loop around GPT-OSS behaviour.

The model identifier must therefore become runtime configuration. Production,
manual validation and the opt-in integration test must all resolve the same
`GROQ_COMMERCE_MODEL` value. A missing/blank value must fail with a bounded,
explicit configuration error rather than silently falling back to GPT-OSS or any
other model.

## Scope

- Retain Attempt 3's provider-compatible `finalResponse` tool architecture and
  all accepted language persistence/stability behaviour.
- Remove hardcoded Groq model identifiers from the production CommerceAgent path.
- Resolve the production model from a single explicit runtime setting:
  `GROQ_COMMERCE_MODEL`.
- Treat a missing/blank model setting as a bounded configuration error; do not
  silently fall back to `openai/gpt-oss-20b` or another model.
- Ensure the opt-in real-provider integration test uses the same configured model
  as production rather than hardcoding a separate model.
- Preserve exactly one CommerceAgent `generateText()` call and the existing
  bounded `searchProducts -> finalResponse` tool loop.
- Keep `customer-explicit` language precedence and all Attempt 3 regressions green.
- Document the new runtime setting in the repository's established environment/
  configuration documentation location if one exists; do not invent a second
  configuration mechanism.
- Record that deployment/system testing requires `GROQ_COMMERCE_MODEL` to be set
  in the Background service environment.

## Out of Scope

- A separate language-detection LLM/API call.
- A second CommerceAgent finalisation/model call.
- A GPT-OSS-specific compatibility shim.
- Registering an undeclared generic `json`/catch-all tool merely to satisfy a
  model-specific hallucinated tool call.
- An unvalidated free-form text fallback when `finalResponse` is missing.
- Choosing a permanent product-wide Groq model in source code.
- Changing Groq provider, API key ownership or billing.
- User-facing language preference UI/commands unless already present.
- Proactive template selection/send (`BACKGROUND-002` / `BACKGROUND-003`).
- Inferring language from phone, country, currency, Shopify Market, shipping
  destination, product names or customer names.
- Changing authoritative commerce currency/country/time-zone facts when language
  changes.
- Persisting model reasoning or language-detection prose.

## Requirements

### 1. Configurable Groq model with one validated CommerceAgent result

The architecture requires Groq tool use; it does **not** require a specific Groq
model identifier.

Production `runCommerceAgent()` MUST resolve its model from:

```text
GROQ_COMMERCE_MODEL
```

Rules:

1. do not hardcode `openai/gpt-oss-20b` (or a replacement model) in the production
   CommerceAgent path;
2. a missing or blank `GROQ_COMMERCE_MODEL` must fail with a bounded configuration
   error before making the provider request;
3. do not silently fall back to another model;
4. do not derive the model from tenant/customer/language/country/currency data;
5. the real-provider integration test must resolve the **same setting** rather
   than hardcoding its own model;
6. keep exactly one `generateText()` CommerceAgent invocation.

Retain Attempt 3's normal Groq/AI-SDK tool loop. It must support both:

```text
searchProducts   (when factual product lookup is required)
finalResponse    (required validated terminal result)
```

`finalResponse` remains side-effect-free with a Zod/schema input equivalent to:

```text
replyText: string
detectedLanguageTag: string | null
detectedLanguageConfidence: number | null
```

The final tool input schema remains the validation boundary. The loop must stop on
that final tool (using the installed-version equivalent of
`hasToolCall("finalResponse")`) while retaining a bounded maximum step count.

If the bounded loop ends without exactly one valid final-response result, fail
with the existing bounded CommerceAgent error. Do not fall back to unvalidated
free-form text and do not make a second model call.

Do not add special behaviour purely to accommodate `openai/gpt-oss-20b`. If the
configured Groq model cannot reliably execute the declared tool loop, the
real-provider test must expose that incompatibility so deployment configuration
can select a different supported model.

### 2. Meaning of detected-language metadata

The model reports the language of the **latest substantive inbound customer
message**, not a guess based on the merchant, phone number, country, currency,
Shopify Market, customer name, product name or previous assistant message.

For an ambiguous/non-linguistic message, return no detection:

```text
detectedLanguageTag = null
detectedLanguageConfidence = null
```

Do not request or persist free-form reasoning.

### 3. Do not invent regional subtags

Detection must return the narrowest defensible BCP-47 tag.

Example:

```text
French text with no regional evidence -> fr
```

not automatically:

```text
fr-FR
```

If the current durable language is more specific and the detected base language
is the same, preserve the durable language rather than degrading or region-
flapping it:

```text
current = en-GB
detected = en
=> keep en-GB
```

Likewise, text-only detection must not change `fr-CA` to `fr-FR` merely because a
model guessed a region. Same-base regional changes require an explicit trusted
customer preference, not ordinary message-language detection.

A confident different-base-language switch is valid:

```text
current = en-GB
detected = fr
=> accept fr with languageSource = detected
```

### 4. Application-owned acceptance policy

The model proposes detection; application code decides whether it is accepted.
Preserve/centralise the existing stability rules for cases such as:

```text
very short text
emoji-only
URL-only
numeric/non-linguistic input
ambiguous signal
```

Preserve a bounded confidence threshold (Attempt 1 used `0.85`) unless inspection
shows an established repository constant that should be reused.

Invalid BCP-47 tags, missing confidence, out-of-range confidence or low-confidence
results must not change the durable language.

### 5. Response language for the current turn

The CommerceAgent prompt/output contract must distinguish:

```text
current accepted conversation language
latest customer-message language
```

If the latest substantive customer message is confidently in another language,
the **same CommerceAgent run** may answer in that detected language and report the
same detection metadata for persistence.

If the message is ambiguous or no confident switch exists, reply in the current
accepted conversation language when one exists.

The model must not alter product facts, prices, currencies, URLs, order state or
merchant policy while adapting language.

### 6. Explicit customer preference remains stronger than detection

ARCH-005 language precedence is:

```text
customer-explicit
then detected
then Shopify / merchant / platform fallback
```

If the current durable language has:

```text
languageSource = customer-explicit
```

ordinary CommerceAgent message detection MUST NOT replace it, even when the
model reports a high-confidence different-base language. Only a new trusted
explicit-language input may replace an existing explicit preference.

The CommerceAgent prompt must follow the same rule for the current reply: when a
customer-explicit language is active, ordinary message-language detection must
not make the reply switch away from that preference.

Add a regression equivalent to:

```text
current = de-DE / customer-explicit
message = clear French
detected = fr / 0.99
=> reply contract remains governed by de-DE
=> durable language remains de-DE / customer-explicit
```

### 7. Persistence and stale-turn safety

Inbound message persistence/inbound-version increment remains authoritative and
must not depend on an LLM call.

Do not persist model-detected language before the CommerceAgent returns.

After the CommerceAgent returns:

1. verify the agent result corresponds to the still-current inbound version;
2. apply the language acceptance/stability policy to the latest inbound message
   plus structured detection metadata;
3. if accepted, persist `Conversation.languageTag` and
   `Conversation.languageSource = DETECTED` using typed Prisma;
4. do not allow a stale agent result to mutate language after a newer inbound
   message has arrived;
5. then continue the existing pending-message/provider-send lifecycle.

Use the narrowest safe implementation. A version-guarded conditional persistence
operation is preferred where practical. Do not weaken the existing stale-response
protection.

### 8. Initial/fallback language remains independent

Do not use the LLM to recreate initial Shopify/merchant/platform fallback
resolution that is already materialised upstream.

When a Conversation already has:

```text
languageTag = en-GB
languageSource = shopify
```

that remains the accepted language unless an explicit trusted preference or an
accepted different-language signal supersedes it.

### 9. No inference from commerce/geography

The language acceptance API must not accept or inspect these as language inputs:

```text
currencyCode
countryCode
phone country
Shopify Market
shipping country/timezone
```

A customer may validly have:

```text
languageTag = fr
countryCode = GB
currencyCode = CHF
```

## Work Items

- [x] Re-read Attempt 1 code and retain accepted persistence/context/stability work.
- [x] Remove/no longer use the no-op production detector path for ordinary inbound
      detection.
- [x] Define one typed/schema-validated `CommerceAgentResult` containing reply text
      and bounded detected-language metadata.
- [x] Update the real CommerceAgent generation path to produce that structured
      result while retaining product tools.
- [x] Adjust bounded AI SDK step budgeting for structured final output when needed.
- [x] Update CommerceAgent pipeline state/types and fake/integration helper
      consistently.
- [x] Update WhatsApp worker(s) to consume `replyText` and post-agent detection from
      the same result.
- [x] Move/apply language acceptance after agent execution with stale-version
      protection.
- [x] Ensure same-base detection preserves an existing more-specific locale.
- [x] Ensure confident different-base detection can persist `DETECTED`.
- [x] Add tests for structured-output and tool coexistence.
- [x] Add tests proving no separate detector/model call occurs.
- [x] Add stale-result, ambiguous-message and same-base-regional-stability tests.
- [x] Verify product-only/free-form response path remains functional; do not invent
      durable Conversation persistence where no Conversation exists.
- [x] Remove `Output.object(...)` from the production tool-bearing Groq call.
- [x] Add the internal schema-validated `finalResponse` (or equivalent) tool and
      return its validated input as `CommerceAgentResult`.
- [x] Stop the loop on final-response tool call while preserving a bounded max
      step count and the existing product-tool capability.
- [x] Fail boundedly if no valid final response is produced.
- [x] Make `customer-explicit` durable language immune to ordinary detected-language
      overwrite and align the CommerceAgent prompt with that precedence.
- [x] Replace/rework obsolete detector-only tests/code where they would falsely
      imply a production detector still exists.
- [x] Add a production-agent provider compatibility regression/integration path;
      the Groq integration test must exercise `commerce.agent.ts`, not only the
      fake agent, when `GROQ_API_KEY` is available.

### Attempt 4 model-configuration correction

- [x] Remove hardcoded `openai/gpt-oss-20b` from the production CommerceAgent model selection.
- [x] Resolve and validate `GROQ_COMMERCE_MODEL` through the existing provider/configuration boundary.
- [x] Fail boundedly and clearly when `GROQ_COMMERCE_MODEL` is missing/blank; do not silently default.
- [x] Make the opt-in real-provider integration path use the same configured model.
- [x] Preserve the Attempt 3 `searchProducts -> finalResponse` loop with exactly one `generateText()` invocation.
- [x] Preserve `customer-explicit` precedence and all accepted language/stale-version regressions.
- [x] Add focused configuration tests proving configured model selection, missing-model failure and no GPT-OSS fallback.
- [ ] When provider credentials are available, prove the configured real model can complete the real production agent path.
- [x] Update the Completion Report for Attempt 4, return this same task to `review`, and STOP.

## Interfaces / Contracts

### CommerceAgent input

Continue to use the existing `RecoveryAgentContext`, including:

```text
conversation.languageTag
conversation.languageSource
conversation.messages
```

### CommerceAgent output

Retain one repository-owned result type equivalent to:

```text
{
  replyText: string;
  detectedLanguageTag: string | null;
  detectedLanguageConfidence: number | null;
}
```

This is an internal Background contract, not a new shared cross-service contract.
For the current Groq runtime, the validated values are supplied as the input to
the internal final-response tool rather than Groq Structured Outputs.

### Conversation language policy

Retain/refactor `ConversationLanguageService` as an application policy if useful,
but it must not own a production model/provider call. It may expose functions for:

```text
explicit/fallback resolution
post-agent detection acceptance
stability/canonicalisation policy
```

Exact method names are implementation details.

## Dependencies

- `ARCH-005-BACKGROUND-001` — Complete.
- Existing CommerceAgent AI SDK/tool path in `moda-interact-background`.
- DATABASE-001 Conversation language fields already adopted by this repository.
- Runtime/deployment must provide a non-blank `GROQ_COMMERCE_MODEL` before real-provider validation and deployment.

## Enables

- `ARCH-005-SYSTEM-TEST-002` after architect acceptance and after all other
  system-test dependencies are Complete.

## Acceptance Criteria

- [x] production CommerceAgent model is read from `GROQ_COMMERCE_MODEL`; no Groq model identifier is hardcoded as the runtime default.
- [x] missing/blank `GROQ_COMMERCE_MODEL` fails with a bounded explicit configuration error and makes no provider request.
- [ ] opt-in real-provider integration uses the same configured model as production and completes `searchProducts -> finalResponse` successfully when credentials/configuration are supplied.
- [x] live runtime no longer depends on a no-op language detector.
- [x] no second LLM/provider call is added for language detection/finalisation.
- [x] CommerceAgent returns schema-validated reply + bounded language metadata through a provider-compatible final-response tool.
- [x] existing product tools still function before the validated final-response tool.
- [x] current accepted language is supplied structurally to CommerceAgent.
- [x] production Groq request does not combine Structured Outputs with tool use.
- [x] an existing `customer-explicit` language cannot be overwritten by ordinary detected language.
- [x] clear different-language message can be answered in that language in the
      same turn.
- [x] accepted confident switch persists canonical `languageTag` with
      `languageSource = DETECTED`.
- [x] `en-GB + detected en` preserves `en-GB` rather than degrading to `en`.
- [x] same-base guessed regional differences do not flap durable locale.
- [x] clear `en-GB -> fr` switch is allowed without inventing `fr-FR`.
- [x] short/emoji/URL/numeric/ambiguous messages do not change durable language.
- [x] stale CommerceAgent results cannot mutate Conversation language.
- [x] phone/country/currency/Market/shipping data cannot drive language selection.
- [x] authoritative commerce facts remain unchanged across language adaptation.
- [x] proactive template approval boundary remains untouched.
- [x] focused tests pass.
- [x] repository build/typecheck, Prisma validation and `git diff --check` pass.
- [x] full test suite has no new task-caused failures; pre-existing unrelated
      baseline failures are documented exactly if still present.

## Validation

At minimum add/retain cases equivalent to:

```text
A. Existing Shopify language, no switch
current = en-GB/shopify
latest message = clear English
model output detection = en / high confidence
=> reply in English
=> durable language remains en-GB/shopify

B. Confident language switch
current = en-GB/shopify
latest message = "Bonjour, pouvez-vous m'aider avec ma commande ?"
model output detection = fr / >= threshold
=> same CommerceAgent result contains French reply
=> persist fr / detected

C. Do not invent region
current = en-GB
latest message = clear French without regional evidence
=> detected/persisted tag is fr, not fabricated fr-FR

D. Same-base stability
current = fr-CA
model proposes fr or fr-FR from ordinary text
=> preserve fr-CA unless an explicit trusted preference exists

E. Ambiguous/no-language input
emoji / URL / numeric / very-short input
=> detection ignored/null
=> existing language retained

F. Stale turn
agent returns language detection for inboundVersion N
a newer inbound message advances to N+1 before acceptance
=> stale result does not update language and stale response is not sent

G. Independence
language = fr
country = GB
currency = CHF
=> no commerce/geography inference or mutation

H. Tool path / provider compatibility
product question requires `searchProducts`
=> tool executes
=> finalResponse/equivalent tool is then called with validated CommerceAgentResult
=> exactly one `generateText()` agent invocation is used
=> production call has tools and does NOT configure `Output.object(...)`

I. Explicit preference precedence
current = de-DE / customer-explicit
latest message = clear French
model proposes fr / high confidence
=> durable language remains de-DE / customer-explicit
=> prompt contract keeps the current reply governed by explicit preference

J. Configured real-provider integration
when both `GROQ_API_KEY` and `GROQ_COMMERCE_MODEL` are present, exercise the real
`commerce.agent.ts` path using that configured model and a fake/local product tool
=> production and test resolve the same model setting
=> product tool can execute
=> final-response tool completes
=> validated CommerceAgentResult returns
=> exactly one `generateText()` invocation is used
=> no model-specific fallback/catch-all tool is involved
```

Run the focused language/conversation/agent/worker suites plus repository-standard
validation and `git diff --check`.

## Implementation Notes

- Use the installed AI SDK version and inspect its actual types/APIs before editing.
- AI SDK supports tool-loop stop conditions such as `hasToolCall(...)`; use the
  installed-version equivalent to stop when the internal final-response tool is
  called while retaining a bounded maximum step count.
- Keep Attempt 3's tool-based validation boundary; do not reintroduce `Output.object(...)` on the production tool-bearing call.
- Resolve the Groq model from `GROQ_COMMERCE_MODEL`; do not hardcode a fallback model.
- The configured model must support the declared local tool loop used by the real CommerceAgent path.
- Do not add a second `generateText`, `generateObject`, provider call or dedicated
  detector invocation merely to obtain language metadata.
- Do not persist chain-of-thought, detector explanation or other free-form model
  reasoning.
- Do not edit architect-owned review text.
- Return this same task to `review` and STOP.
- Do not start system testing.
- Do not commit or push.

## Completion Report

### Status

Implemented and returned to review.

### Attempt 1 retained work

Attempt 1 added durable language/source persistence, canonicalisation,
anti-flapping policy and CommerceAgent language context. Retain those pieces where
they remain compatible with the corrected single-CommerceAgent-run design.

### Attempt 2 required correction

Replace the unusable no-op production detector path with structured language
metadata emitted by the **existing CommerceAgent run**, then apply the existing
application-owned stability/confidence policy after that result and before durable
language mutation.

### Attempt 2 Implementation

- Added schema-validated `CommerceAgentResult` output to the existing AI SDK
  `generateText` call, including bounded detected-language metadata.
- Preserved product tool execution and increased the bounded step budget to
  account for the structured final-output step.
- Updated the pipeline, fake agent, WhatsApp worker and observability/integration
  consumers to use `replyText`.
- Moved ordinary detection out of inbound receipt and into a version-guarded
  post-agent acceptance path using the existing application stability policy.
- Preserved same-base regional locales, rejected unstable signals, accepted
  confident different-base switches, and avoided a second model invocation.

### Validation

- Focused language, conversation and agent tests: 14 passed.
- Agent integration, observability and pipeline tests: 5 passed.
- Full suite: 160 passed, 4 skipped, 3 pre-existing unrelated failures in
  `recovery-routing.service.test.ts` and `pending-recovery-candidate.service.test.ts`.
- `npm run build`: passed.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.

### Attempt 3 required correction

Attempt 2's application policy, version-guarded persistence and same-base locale
stability are retained. Attempt 3 must replace Groq-incompatible
`Output.object(...) + tools` with one validated final-response tool inside the
same CommerceAgent tool loop, and must enforce `customer-explicit` precedence
against ordinary detected-language updates.

### Attempt 3 Implementation

- Replaced production `Output.object(...)` with a side-effect-free,
  schema-validated `finalResponse` tool in the existing CommerceAgent loop.
- Added `hasToolCall("finalResponse")`, bounded `stepCountIs(6)`, and a
  `prepareStep` handoff that requires `finalResponse` after product search.
- Added bounded failure when the loop ends without a validated final response.
- Preserved one `generateText()` invocation and updated the production prompt
  to enforce explicit customer-language precedence and final-tool completion.
- Added regression coverage preventing detected language from overriding
  `customer-explicit` language and updated consumers to exercise final-tool
  capture.

### Attempt 3 Validation

- Focused agent, language-policy and observability tests: 17 passed.
- `npm run build`: passed.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.
- Full suite: 161 passed, 4 skipped, 3 pre-existing unrelated failures in
  `recovery-routing.service.test.ts` and `pending-recovery-candidate.service.test.ts`.
- Optional real Groq integration reaches `commerce.agent.ts` but remains
  provider-blocked: `openai/gpt-oss-20b` emits an undeclared `json` tool call.
  The application makes no second model call and fails boundedly as required.

### Attempt 4 required correction

Attempt 3 successfully implemented the one-call validated `finalResponse` tool
architecture and explicit-language precedence. Its real-provider test then exposed
that the remaining failure is tied to the hardcoded `openai/gpt-oss-20b` runtime
choice. ARCH-005 does not require that model.

Attempt 4 must make the Groq CommerceAgent model an explicit deployment setting
(`GROQ_COMMERCE_MODEL`), retain the accepted tool-loop/language work unchanged,
and validate the **configured** model through the real production agent path.

A missing/blank setting must fail boundedly; there must be no implicit GPT-OSS or
other model fallback.

## Attempt 4 Completion Report

### Status

Ready for Review

### Files Changed

- `src/agents/commerce.agent.ts`
- `tests/unit/agent/commerce.agent.configuration.test.ts`
- `tests/integration/commerce.agent.integration.test.ts`
- `tests/unit/observability/genai-observability.test.ts`
- `README.md`

### Work Completed

- Removed the hardcoded `openai/gpt-oss-20b` production model selection.
- Added bounded resolution of the trimmed `GROQ_COMMERCE_MODEL` setting with an
  explicit `CommerceAgentConfigurationError` when it is missing or blank.
- Kept the single `generateText()` call and the existing
  `searchProducts -> finalResponse` tool loop unchanged.
- Updated the opt-in integration path to use the same runtime model setting and
  added focused configured/missing/blank model tests.
- Documented the required deployment setting in `README.md`.

### Validation Results

- Focused regression/configuration tests: `4` files, `21` tests passed.
- `npm run build`: passed.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.
- Full `npm test`: `20` files passed, `165` tests passed, `3` skipped, with `3`
  pre-existing unrelated failures in
  `recovery-routing.service.test.ts` and
  `pending-recovery-candidate.service.test.ts`.
- ESLint was not run because the package has no local ESLint binary and `npx`
  requested installation of undeclared `eslint@10.10.0`; installation was
  declined.
- Real-provider integration was not run: `GROQ_API_KEY` is present but
  `GROQ_COMMERCE_MODEL` is unset, so the required configured runtime cannot be
  exercised in this environment.

### Deviations

The configured real-provider integration criterion remains unchecked because the
required model setting is unavailable in the environment. No code workaround or
implicit fallback was added.

### Assumptions

The three full-suite failures are the existing unrelated baseline failures
recorded by the prior attempt and are outside this task's model-configuration
scope.

### Unresolved Issues

The configured Groq model's real-provider tool-loop compatibility remains to be
validated after deployment configuration supplies `GROQ_COMMERCE_MODEL`.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted — Attempt 4

### Accepted portions from Attempt 3

The following Attempt 3 work passed architectural review and MUST be retained:

- one `generateText()` CommerceAgent invocation per turn;
- schema-validated, side-effect-free `finalResponse` tool;
- bounded tool-loop stopping/failure behaviour;
- product tool execution before final response where required;
- no `Output.object(...)` on the production tool-bearing call;
- post-agent typed Prisma persistence guarded by `inboundVersion`;
- same-base locale preservation and different-base switching;
- no language inference from country/currency/phone/Market/shipping geography;
- `customer-explicit` language precedence over ordinary detection;
- `replyText`/language result propagation through worker, pipeline and observability consumers;
- product-only path remains non-durable.

### Finding — model choice is configuration, not architecture

Attempt 3's opt-in integration test now reaches the **real** `commerce.agent.ts`
path and therefore did exactly what Architect Review required. It exposed that the
hardcoded model `openai/gpt-oss-20b` does not successfully complete this declared
tool loop in the current provider path, emitting an undeclared `json` tool call.

That does not justify a GPT-OSS-specific workaround. ARCH-005 requires a reliable
Groq CommerceAgent tool loop, not that particular model.

The remaining correction is to remove the hardcoded model from production and
resolve it from `GROQ_COMMERCE_MODEL`. The same setting must drive the real-provider
integration test. This allows deployment to select a Groq model that actually
supports Moda's required local-tool behaviour without another code change.

### Required correction

1. Production model selection reads `GROQ_COMMERCE_MODEL` through the existing
   provider/configuration boundary.
2. Missing/blank configuration fails boundedly and explicitly before provider use.
3. There is no implicit `openai/gpt-oss-20b` or other model fallback.
4. The opt-in integration path uses the same configured model as production.
5. Retain the accepted Attempt 3 one-call `searchProducts -> finalResponse` design.
6. Retain `customer-explicit` precedence and all existing language/stale-version
   regressions.
7. Do not add a generic `json` tool, second model call, unvalidated free-form
   fallback or model-specific compatibility shim.

### Validation required before re-review

Prove all of the following:

1. configured model ID is passed to the Groq provider by the production agent;
2. missing/blank `GROQ_COMMERCE_MODEL` produces the bounded configuration failure
   and does not invoke the model;
3. exactly one production `generateText()` invocation remains;
4. `searchProducts` can execute before `finalResponse`;
5. `finalResponse` values remain Zod/schema validated;
6. current `customer-explicit` language survives conflicting ordinary detection;
7. same-base, different-base, ambiguity and stale-version regressions remain green;
8. when `GROQ_API_KEY` and `GROQ_COMMERCE_MODEL` are present, the opt-in integration
   test exercises the **real** `commerce.agent.ts` path using that configured model
   and completes successfully;
9. repository-standard build/Prisma/tests/diff checks pass with no new failures.

If the configured model still cannot complete the declared tool loop in the real
integration test, STOP and report the configured model/provider compatibility
failure. Do not redesign around it inside this task.

### Attempt 4 — Accepted

Accepted after code review plus the required real-provider validation.

Architect inspection confirmed that Attempt 4:

- removes the hardcoded Groq model from the production CommerceAgent path;
- requires a non-blank `GROQ_COMMERCE_MODEL` and fails boundedly before provider use when it is absent;
- preserves exactly one production `generateText()` invocation;
- retains the validated, side-effect-free `finalResponse` tool and bounded tool loop;
- retains product lookup before final response where required;
- retains `customer-explicit > detected > fallback` language precedence;
- retains same-base locale preservation, different-base switching and stale-`inboundVersion` protection;
- introduces no GPT-OSS-specific compatibility shim, generic catch-all tool, second model call or unvalidated response fallback.

The developer then ran the opt-in integration test through the **real** production
`commerce.agent.ts` path with runtime configuration:

```text
GROQ_COMMERCE_MODEL=qwen/qwen3.6-27b
```

The integration completed successfully:

```text
commerce agent integration
  uses product search when the customer asks about products  PASS

Test Files  1 passed
Tests       1 passed
```

This closes the provider-compatibility criterion that remained unchecked in the
implementation agent's Completion Report. The successful model is evidence that
the configurable CommerceAgent contract works; it is **not** a new hardcoded
architecture requirement. Deployment remains free to select a compatible Groq
model through `GROQ_COMMERCE_MODEL`.

`ARCH-005-BACKGROUND-004` is Complete. `ARCH-005-SYSTEM-TEST-002` remains Pending
until every dependency in its authoritative task metadata is Complete. The
Background Render deployment must provide `GROQ_COMMERCE_MODEL` before integrated
system validation.

