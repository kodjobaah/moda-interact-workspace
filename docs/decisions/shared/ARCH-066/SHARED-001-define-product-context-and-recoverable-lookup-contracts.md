---
id: ARCH-066-SHARED-001
architecture_id: ARCH-066
title: Define product options, trusted context and lookup recovery contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 50
executor: developer
claimed_at: 2026-11-08T12:32:03Z
attempt: 1
depends_on: []
enables: ["ARCH-066-SHARED-002", "ARCH-066-DATABASE-001", "ARCH-066-SHARED-003"]
created: 2026-11-08
updated: 2026-11-08
---
# Define product options, trusted context and lookup recovery contracts

## Objective and read first
Implement only the owned work below. Read `docs/architecture/ARCH-066-conversation-product-context-and-whatsapp-preview-parity.md` first: its numbered contract decisions are normative and must not be redesigned by the implementor.

## Context / scope
Observed failure: a later sizing question used an invalid Woo product ID; several corrected calls failed and a successful search could not clear the runner's referral latch. Product outputs currently omit options. Own Shared schemas, context reducer and runner recovery; never edit service repositories.

## Touch points and exact work
- `src/commerce/schemas.ts`: add optional `options` and `selectedOptions` to CommerceProductSchema, according to architecture decision 1; retain commerce.v1 and all existing required fields. Existing persisted products must still parse.
- NEW `src/commerce/product-context.ts`; export from `src/commerce/index.ts`: implement CommerceConversationProductContextSchema, `mergeConversationProductContext(previous, observations, identity)` and `resolveConversationProductReference(context, reference)`. Use decision 2 exactly; no prices or tool authority from persisted context. Export observation type `{toolName, products: CommerceProduct[], observedAt}`; identity `{shopId,conversationId,platform,now}`; reference `{productId?:string,variantId?:string|null,title?:string}`. Return resolution `{kind:'MATCH',productId,variantId}|{kind:'AMBIGUOUS'}|{kind:'MISSING'}`; case-folded trimmed exact title matches only, no fuzzy guessing.
- `src/commerce/runner/types.ts`, `preflight.ts`, graph state, `tool-execution.ts`, `graph/nodes/validate-final-response.ts`, `final-response.ts`, `diagnostics.ts`, `diagnostic-messages.ts`, `graph/nodes/invoke-model.ts`: implement decision 3. Keep optional input `productContext` separate from arbitrary history; validate shop/conversation match before model I/O, project it into model context as untrusted references, never evidence.
- Add optional bounded result metadata `productContextUpdate` to successful runner results, populated only from successful validated commerce_search_products / commerce_get_product observations. No raw provider data, credentials or model-created IDs. Host supplies platform; preserve current final-response schema and selection authority.
- Recoverable errors: INVALID_INPUT and NOT_FOUND do not set requiredReferral. DENIED/revocation remains sticky. UNAVAILABLE/THROTTLED/DEADLINE remain sticky for the turn. STALE_TURN/cancellation remain terminal. Do not clear hard failures after a success. Correctable failures still consume normal budgets and appear in tool activity.
- On provider finishReason length with neither visible text nor calls return BUDGET_EXHAUSTED diagnostic MODEL_OUTPUT_TOKENS_EXHAUSTED at model.route, not MODEL_CALL_ROUTE_INVALID. Never fabricate a reply or silently retry/increase budgets.

## Acceptance / validation
- [ ] Contract fixtures: old product, options bounds/duplicates/controls, partial options, selected variation, no sizes and malformed source handling.
- [ ] Context tests: two products same name => AMBIGUOUS; foreign tenant/conversation rejected before model/tool I/O; expiry; deterministic eviction; deleted ID corrected through search; no price becomes evidence.
- [ ] Runner tests: NOT_FOUND -> valid product lookup -> ANSWER allowed; invalid arguments -> valid lookup allowed; DENIED -> success still requires referral; provider outage -> success preserves hard latch; token truncation precise diagnostic.
- [ ] Existing runner, grants, final-response/evidence, product-discovery and response.v1 tests pass. Run package typecheck/lint/build using repository scripts. No npm publication in this task.

## Execution boundary
Definition only. Do not claim or implement until explicit dependency tasks are Complete. Use the canonical launcher-resolved parent and implementation task worktrees; execution_mode and completion_mode are developer. Do not change unrelated work or another repository. Record exact Shared package version/integrity, database migration and provider schema artifact used. No production customer messages, Meta registrations or live mutations are authorized by this task.

## Completion Report

### Status

In Progress — Attempt 1; developer-authorized implementation and publication.
