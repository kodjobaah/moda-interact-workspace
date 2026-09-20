---
id: ARCH-020-SHARED-001
architecture_id: ARCH-020
title: Implement and publish commerce contracts and reusable runner
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 20
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-016-SHARED-001
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-BACKGROUND-001
  - ARCH-020-COMMERCE-003
  - ARCH-020-COMMERCE-004
  - ARCH-020-COMMERCE-009
  - ARCH-020-COMMERCE-011
  - ARCH-020-SHOPIFY-001
  - ARCH-020-SYSTEM-TEST-001
  - ARCH-020-COMMERCE-008
created: 2026-09-20
updated: 2026-09-20
---

# Implement and publish commerce contracts and reusable runner

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Implement, validate and publish one installable Shared package version containing the Commerce contracts and reusable runner. Downstream consumers require the verified published version before this task is Complete.

## Context

Merchant-selected capabilities should drive WhatsApp CommerceAgent behaviour through a separate Next.js MCP server with a team-only Studio. Production conversation admission, ordering, model hosting and delivery remain in Background. This is a pre-production breaking rollout, with no implicit permission to delete durable data.

Task definition is on local workspace main by the developer's explicit 2026-09-20 review request. It is not a claim, task-branch materialisation or implementation approval. All execution fields remain unclaimed.

## Scope

src/commerce schemas, pure selection helpers, ./commerce/runner implementation, package exports, focused tests, release metadata, publication and clean registry installation verification.

## Out of Scope

Other repositories' implementation, unrelated refactoring, automatic execution of enabled tasks, live deployment, main integration/push and changes to billing prices/merchant entitlements. No cart/order/discount mutation, WhatsApp sending from Commerce, arbitrary executable code or arbitrary-host HTTP endpoints; C14 validated read-only GraphQL definitions are explicitly permitted. No duplicate discount catalogue/merchant configuration system. Shared indexes and architecture reconciliation remain architect-owned.

## Requirements

Follow the parent architecture's tenant/policy/revision contracts and the assigned logical owner. Preserve unrelated changes. Read repository-local AGENTS.md if present. Commerce consumes the canonical database through its nested database/ Git submodule; schema and migrations belong to moda_database. For consumers, use actual accepted and published dependency revisions, not copied task snapshots or hypothetical versions.

### Runner implementation

Follow the parent architecture's tenant/policy/revision contracts and the assigned logical owner. Preserve unrelated changes. Read repository-local AGENTS.md if present. Commerce consumes the canonical database through its nested database/ Git submodule; schema and migrations belong to moda_database. For consumers, use actual accepted and published dependency revisions, not copied task snapshots or hypothetical versions.

## Work Items

- [x] Extend CommerceManifest with required C16 responseContract/hash and CommerceFinalResponse with details. Export strict definition/envelope types and generic pure subset/hash validation contracts. Keep release-specific properties out of compiled types; document fixed envelope versus configurable details.

- [x] Export the separate bounded structural draft definition schema and strict publishable definition schema from C14; draft-save acceptance is not execution/publication approval.

- [x] Export C14 strict reusable tool identity/revision/binding/grant-provenance schemas and discriminated SHOPIFY_STOREFRONT_QUERY/POLICY_OPERATION execution definitions; no fixed MCP tool-name enum. Export the schema/compiler interface consumed by Commerce, not a provider process in Shared.
- [x] Implement exact capability/tool hash inputs and deduplication: same tool revision across selected capabilities produces one entry with sorted original capabilityKeys; conflicting revisions reject. Allow zero remote tools for conversation_core.
- [x] Keep Admin feature keys dynamic and existing effective-billing semantics; no mandatory product_search feature or tool.

- [x] Define/export CommerceToolDefinitionSchema, the bounded C14 input-schema/mapping/template validators, typed operation descriptors, and schema-to-MCP descriptor conversion. Separate definitionVersion from executor operationVersion. Preserve the existing WhatsApp schemas.

- [x] Define versioned manifest, capability binding, release identity, authenticated turn identity, basket, tool input/output, evidence and final-response schemas with bounded examples. Distinguish resolve-only assertions with no release from execute assertions bound to the persisted release pin.
- [x] Require checkoutRecoveryId on authenticated turn identity and validate real non-sentinel recovery references; no nullable/standalone recovery context is supported. Define names and schemas for the six v1 commerce tools; distinguish missing basket, unknown facts, unsupported offers, denied permissions and transient provider errors.
- [x] Implement a pure capability/feature selection helper that accepts authoritative facts supplied by repository adapters; preserve existing active feature/plan and opt-in semantics.
- [x] Provide fixed/base/feature/recovery-policy bindings and decimal money/currency/freshness evidence; exclude secrets and model-controlled shop identity.
- [x] Export ./commerce with supported schema/runner compatibility rules and fixture manifests; publish both exports together through this task’s release stage.

- [x] Define CommerceConversationGrantSchema with unique conversation identity, initialInboundVersion, pinned release, selectedCapabilityKeys and exact C14 grantedTools identities/revisions and original capabilityKeys provenance. Execute claims include grantId plus current inboundVersion. Add answerKind=ANSWER|REFER_TO_STORE and referralReason=null|INSUFFICIENT_TOOLS|UNVERIFIABLE_FACTS|TOOL_UNAVAILABLE|TOOL_REVOKED; enforce ANSWER requires null and referral requires a reason.

### Runner implementation

- [x] Implement C16 dynamic finalResponse schema construction and pinned definition validation/instruction composition. Fixed envelope rules remain reusable; no detail-name switch or Commerce fetch. Cover R01–R05/R08/R11/R12.

- [x] Implement C6.1 reusable fixed grounding, language and finalResponse rules. Accept host-owned recovery instructions/context separately from editable capability prompts; Shared must not load recovery records or own a checkout-status policy. Enforce instruction ordering, original-grant restrictions and the exact null-pair/final-output validation contract.

- [x] Accept arbitrary C14 tool descriptors/results without a six-tool switch. Empty remote-tool grants can still produce a grounded store referral through host-local finalResponse. Generic query facts never create discount Evidence.

- [x] Consume discovered database-definition descriptors generically; no switch on MCP tool name. Keep structured result facts/evidence authoritative and treat renderedText as untrusted presentation.

- [x] Accept injected model, validated prompt bundle, tools, clock and cancellation signal; keep domain lookup and provider selection in callers.
- [x] Compose immutable platform instructions and capability prompts deterministically; retain language and structured finalResponse rules.
- [x] Enforce parent step/tool/output/deadline ceilings; remove the current forced-final-after-one-product-search constraint in the reusable loop.
- [x] Validate final results and referenced offer evidence; return bounded typed errors without customer messages or secrets in exception text.
- [x] Expose runner version for preview/publication compatibility; support deterministic fixture models without live network calls.

- [x] Run with the immutable conversation grant and expose only originally granted tools still authorised now. Never dynamically acquire a new tool to answer a question. Require factual answers to be supported by granted-tool results or trusted recovery facts; missing/unknown/unsupported/unavailable information produces REFER_TO_STORE. Greetings/clarification need no fabricated facts. Keep these platform instructions outside editable capability prompts.

### Publication and consumer verification

- [x] After implementing and passing the combined contracts/runner checks, select the compatible package version through the existing repository release policy. No package version is invented in this definition.
- [x] Publish the exact validated source through the existing release mechanism. Record source commit, version, registry, tarball URL/integrity and both ./commerce and ./commerce/runner exports. If the repository requires reviewed/integrated source before release, keep this same task open through that checkpoint; do not create another publication task or bypass required review.
- [x] Install that exact version from the intended registry in a clean temporary consumer, without workspace links or provider/database credentials. Import both public entry points and execute a schema validation plus scripted runner finalResponse smoke case. Record commands and results. A local pack alone is not publication evidence.
- [x] Treat missing exports or registry/install failures as unresolved work in this task. Fix scoped defects and rerun affected checks. Do not mark Complete or promote downstream consumers until the published artifact is verified and architect acceptance is recorded.

## Interfaces / Contracts

Read the binding schema contract in docs/decisions/database/ARCH-020/DATABASE-001-persist-capability-releases-and-turn-revision-pins.md. Its exact field names/types, enum values, JSON shapes/bounds, immutable release membership and selectedCapabilityKeys/grantedTools conversation grants are the persistence contract; do not invent alternative representations. Shared APIs serialize dates as ISO strings and map database environment enums to lower case.

Canonical @modainteract/moda-interact-shared/commerce; existing billing and recovery-policy exports.

### Implementation guidance

Apply binding contracts **C14–C15** for reusable tool revisions, query/policy execution, safe templates, original grant provenance and integrated Studio authoring. The page/traversal specification is required for UI owners.

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C0, C1, C4, C5**. These are required acceptance inputs, not optional examples.

Deliver src/commerce/index.ts plus schema/selection/canonical-json modules and tsup/package exports. Export strict named schemas from C4 and valid/invalid fixtures for every remote tool and final response. Reuse ./whatsapp and ./billing status contracts unchanged. Validation distinguishes shape checks from runtime database authorisation. No promised database lookup in a Zod parser.

### Required evidence

Deliver scripts/validate-commerce-entrypoints.mjs and package script validate:commerce-entrypoints; after npm run build, import both public exports in a clean process with provider/database env unset. Run npm run typecheck and focused node:test/tsx fixtures using existing repository conventions.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

### Runner implementation

SHARED-001 schemas; AI SDK/provider dependencies isolated to the runner entry point so unrelated consumers do not initialise a model runtime.

### Implementation guidance

Apply binding contracts **C14–C15** for reusable tool revisions, query/policy execution, safe templates, original grant provenance and integrated Studio authoring. The page/traversal specification is required for UI owners.

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C1, C4, C6**. These are required acceptance inputs, not optional examples.

Deliver src/commerce/runner/index.ts and a scripted injected-model harness. Define one exported runCommerceTurn(input) with typed success/failure union and runnerVersion; take dependencies explicitly. Keep platform instructions immutable; capability templates are literal text. Maintain turn-local trusted evidence map and reserve final revalidation budget. Do not equate a prompt instruction with enforceable tool permissions or universal hallucination detection.

### Required evidence

Harness verifies exact invocation sequence, max calls/steps/deadline, cancellation, invalid/duplicate final output, unknown evidence ID, missing grant tool, final referral and language-pair validation. assert model/tool side-effect counts; no live model required.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

## Dependencies

- ARCH-016-SHARED-001

Every dependency must be Complete and architect-accepted before execution. Reconcile accepted dependency metadata into the matching parent task branch before promotion. Developer integration or explicitly approved accepted-commit consumption is required to obtain prerequisite source. Readiness never launches a task. Commerce tasks additionally require the new-owner setup checkpoint.

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-BACKGROUND-001
- ARCH-020-COMMERCE-003
- ARCH-020-COMMERCE-004
- ARCH-020-COMMERCE-009
- ARCH-020-COMMERCE-011
- ARCH-020-SHOPIFY-001
- ARCH-020-SYSTEM-TEST-001
- ARCH-020-COMMERCE-008

## Acceptance Criteria

- [x] One exact package version is available in the intended registry, contains both accepted exports and passes clean installation/import/schema/runner smoke verification. Report publication metadata and tested source SHA; implementation-only completion does not satisfy this task.

- [x] Demonstrate the assigned C16 response-contract cases with named fixtures and actual outcomes; reference the exact published definition/hash or synthetic preview definition used.

- [x] A previously unknown feature key and query-based tool survive validation/manifest creation. Same shared revision deduplicates; different revisions conflict; grant provenance never widens after creation.

- [x] Cross-tenant references, unknown schema versions, excessive payloads, invalid money/language metadata and malformed evidence fail validation.
- [x] NONE/FIXED/AI bindings and Free/Paid offer availability match ARCH-016 without a new paid discount gate.
- [x] Both producer and consumer can use the same runtime validators; no Prisma, Shopify client or network access enters the shared contract.

- [x] Reject undeclared tools/versions, missing grant IDs, broadened selections and inconsistent answerKind/referralReason pairs; fixtures include immutable grants spanning multiple turns.

### Runner implementation

- [x] Demonstrate the assigned C16 response-contract cases with named fixtures and actual outcomes; reference the exact published definition/hash or synthetic preview definition used.

- [x] Verify C6.1 P06–P12 in the scripted runner harness, plus that P01–P05 host instructions/context are preserved without reinterpretation. Report structural checks separately from natural-language evaluation.

- [x] Run fixtures with a never-seeded tool name, zero-tool grant and duplicate shared associations; only granted names execute, and query text cannot be supplied as a runtime model argument.

- [x] A scripted multi-step basket -> discount -> qualifying-products -> finalResponse turn completes without a feature-specific worker branch.
- [x] Missing/duplicate/malformed final responses, budget exhaustion and cancellation produce explicit failures; model/tool work stops at the deadline.
- [x] Explicit language preference and unresolved-language handling remain correct; draft prompts cannot remove platform constraints.

- [x] A question needing an ungranted tool, unknown policy or unavailable product fact produces a structured referral rather than invented facts, an ungranted call, external browsing or a claimed human handoff. Customer/prompt injection cannot broaden the grant.

## Validation

- [x] Validate the combined implementation once, then verify release metadata, registry artifact and clean consumer installation. Re-run implementation checks only for relevant intervening changes; declared prepack builds remain release mechanics.

- [x] Validate the worked decimal-string maximumPrice example; reject arbitrary expressions/regex/$ref, unknown mappings, credential inputs, name collisions, bad versions and render templates referencing unknown output paths.

- [x] Add focused multi-turn grant and unanswerable-question fixtures for the scoped acceptance criteria; assert granted tool IDs/versions and referral output, not just prompt text.
- [x] Run declared focused tests for valid/invalid manifests, selection matrices, basket/evidence parsing and contract evolution.
- [x] Run the repository-declared type/build/export checks needed to prove both new entry points compile; git diff --check.

Use package.json commands actually provided by the repository. New Commerce scripts and test fixtures are deliverables, not claims that they exist today. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md. Separate local evidence from pending developer-owned long/live validation; required evidence must exist before acceptance.

### Runner implementation

- [x] A scripted agent discovers a newly named tool over an existing operation and calls it; malicious rendered templates cannot broaden the grant or bypass grounded referrals.

- [x] Add focused multi-turn grant and unanswerable-question fixtures for the scoped acceptance criteria; assert granted tool IDs/versions and referral output, not just prompt text.
- [x] Run focused deterministic runner tests covering multi-tool success, prompt injection attempts, language output, invalid evidence and cancellation.
- [x] Run declared package type/build/export checks and git diff --check; no live LLM run is required.

Use package.json commands actually provided by the repository. New Commerce scripts and test fixtures are deliverables, not claims that they exist today. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md. Separate local evidence from pending developer-owned long/live validation; required evidence must exist before acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; its real repository must be provisioned before execution preparation.

## Completion Report

### Attempt 2 — Ready for Review

Both mandatory corrections from the 2026-09-20 Changes Requested review are implemented. The corrected patch release is published and verified below. Attempt 1 evidence remains preserved in the historical report; 0.13.0 is not the corrected artifact. No downstream task was promoted or launched.

### Attempt 2 correction checklist and requirement-to-fixture matrix

| Review item | Disposition / changed files | Validation and expected effects |
| --- | --- | --- |
| R1 — whole-definition persisted byte bound | Implemented in src/commerce/definition-size.ts and definitions.ts. Draft and strict definitions share the 65,536-byte jsonb-text ceiling, accounting for UTF-8, separator whitespace, escaped strings and numeric exponent expansion. Canonical hash encoding is unchanged. README documents the separate storage measurement. | contracts.test.ts exercises both schemas with ASCII and multibyte aggregate definitions at 65,535/65,536 bytes (accepted) and 65,537 (rejected). Over-limit fixtures remain under 65,536 compact JSON bytes and fail solely with the size issue. Both original 80KB review reproductions reject solely for aggregate size; individual members remain valid. Separate numeric/escape/hash fixture passes. No persistence writes occur. |
| R1 — prove boundary matches persistence | Independent read-only PostgreSQL 15 verification against local_postgres. | Six boundary SELECTs reported calculated/persisted lengths 65535/65535, 65536/65536 and 65537/65537 for ASCII and multibyte fixtures. Numeric extreme/exponent/escaped-string fixture matched 742/742. PostgreSQL, rather than a second compact JSON count, supplied actual octet_length(value::jsonb::text). No schema, table or data mutations. |
| R2 — malformed model call classification | Implemented in src/commerce/runner/index.ts. Validate the entire step/call shape before name inspection or dispatch; serialization and shape errors in model output become INVALID_FINAL. | runner.test.ts tests null/scalar/array calls, missing/null/numeric/empty names, missing/non-object/partial/cyclic final arguments. Every malformed output returns exactly {ok:false,error:{code:INVALID_FINAL,retryable:false}}, one model invocation and zero tool executions, without error text. Invalid host inboundVersion remains INVALID_INPUT with zero model/tool calls. Existing valid zero-tool and four-step/three-tool fixtures pass. |
| Corrected published consumer | scripts/validate-commerce-entrypoints.mjs now includes both review regressions in addition to imports/schema/finalResponse smoke. package.json/package-lock.json carry the patch release. | Fresh exact-version registry install imports both exports, validates the manifest, completes scripted finalResponse, rejects the aggregate oversized draft and classifies calls:[null] as INVALID_FINAL. Child process receives PATH only. |

### Attempt 2 validation

Node 24.19.0 selected through the canonical workspace bootstrap. Commands ran in the dedicated implementation worktree unless explicitly identified:

- `npm run typecheck`: passed.
- `node --import tsx --test src/commerce/contracts.test.ts src/commerce/runner/runner.test.ts`: **30 passed, zero failures**.
- `npm test`: **160 passed, zero failures, one skipped** (existing live BullMQ trace case requires TEST_REDIS_URL). No live LLM is required or claimed.
- Storage oracle: `node --import tsx --input-type=module` generated `/tmp/shared020-a2-jsonb.sql` using exampleDefinition and the same boundary payloads as the tests. `docker exec -i local_postgres sh -c 'exec psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "${POSTGRES_DB:-$POSTGRES_USER}" -tA' < /tmp/shared020-a2-jsonb.sql` executed seven read-only SELECTs; results in `/tmp/shared020-a2-jsonb.log` matched exactly as above.
- `npm run build`: passed JavaScript and declarations.
- `npm run validate:commerce-entrypoints`: passed imports, schema, finalResponse and R1/R2 smoke.
- `npm pack --dry-run --json`: inspected final JSON after prepack build output and verified both commerce/commerce-runner JS/type declaration exports. Prepack rebuilds are release mechanics.
- `git diff --check`: passed.

### Attempt 2 publication and clean registry consumer

- Corrected package: `@modainteract/moda-interact-shared@0.13.1`, a patch selected under the existing README SemVer policy. Registry latest was 0.13.0 before release; 0.13.0 was not overwritten or reused.
- Validated source SHA: `a83bfc12721423f06af8f8732b07f7dd7153e067`, committed/pushed before publication. Both `./commerce` and `./commerce/runner` have ESM and declaration exports. runnerVersion remains 1.0.0; its interface is unchanged.
- `npm publish --access public --registry=https://registry.npmjs.org/`: succeeded.
- `npm view @modainteract/moda-interact-shared@0.13.1 version dist --json --prefer-online --registry=https://registry.npmjs.org/`: verified version 0.13.1 and metadata.
- Tarball: https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-0.13.1.tgz
- Integrity: `sha512-qano76oJ3McL/EYMq7D0GM0W+kAY0wMsSHzWP1NdXSGCa19YiakjkDjZ9WtUylFCDud+kO+uboR4PTSIBoXEBQ==`; SHA-1: `fde3c4dc74963509e6483a42388e54024ffc94c1`; 75 files.
- Clean consumer: `/tmp/shared020-a2-consumer.KM8kB1`, freshly initialized private package.json with no workspace links.
- `npm install --ignore-scripts --no-audit --no-fund --save-exact @modainteract/moda-interact-shared@0.13.1 --registry=https://registry.npmjs.org/`: succeeded. Installed lockfile version/integrity match the registry, without a link flag. All 75 installed files match final local publication files byte-for-byte.
- `COMMERCE_CONSUMER_DIRECTORY=/tmp/shared020-a2-consumer.KM8kB1 node /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-SHARED-001/scripts/validate-commerce-entrypoints.mjs`: PASS both imports, schema, scripted finalResponse and R1/R2 regressions, with provider/database environment absent.


### Attempt 2 deviations, assumptions and unresolved issues

No requested correction is blocked. JSONB size measurement assumes normal JSON.stringify transport of JavaScript values, matching producer serialization; no canonical hash change or database migration is introduced. Domain ownership/compiler/live-model limitations from Attempt 1 remain unchanged. Architect acceptance is pending, and downstream consumers must wait for acceptance. The existing unrelated Redis-dependent test remains skipped.

### Attempt 2 Git / VCS and prepared launcher evidence

- Canonical workspace: /Users/kwadwoadomafriyie/project/moda-interact-workspace.
- Parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-SHARED-001.
- Implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-SHARED-001.
- Both branches: task/ARCH-020-SHARED-001; launcher reused both correct physical worktrees. Both remote task branches required no fast-forward; origin/main already current. Initial parent HEAD 2e0cb0463116a9d84745d9bb0c784f181664edef; initial implementation HEAD 34be9702f39ee638631b99222562365c2fb0a4af.
- Dependency gate passed for ARCH-016-SHARED-001. Recursive submodule sync/update passed, ready, entries empty (no database submodule SHA).
- Attempt 2 claim: 176fc7665cbc06c20b22c0b46c242e4014bb4efa, committed/pushed by launcher, codex at 2026-09-20T20:13:31Z. No repeated claim or startup synchronization.
- Implementation source SHA: a83bfc12721423f06af8f8732b07f7dd7153e067, pushed on the same task branch before publication. Parent submission is a subsequent task-only commit; its identifier is reported in the final execution response.
- No shared/default checkout switch, other worktree reuse, Architect Review edit, architecture/index/frontier edit, parent service gitlink update, main integration/push or force push.

### Historical Attempt 1 report (preserved)

### Status

Ready for Review, Attempt 1 (codex). Contracts, runner and publication are implemented; architect acceptance remains pending. No downstream task was started or promoted.

### Files Changed

Implementation: package.json, package-lock.json, tsup.config.ts, scripts/validate-commerce-entrypoints.mjs; src/commerce/{index,canonical-json,primitives,subset,definitions,schemas,response,selection,fixtures,contracts.test}.ts; src/commerce/README.md; src/commerce/runner/{index,runner.test}.ts and adversarial-evaluations.json. Parent: this task file only.

### Work Completed

Added provider-neutral commerce.v1 schemas, C14 draft/publication definitions and compiler interface, six baseline policy operation contracts, deterministic hashes, dynamic feature selection, immutable grant/provenance checks and C16 response.v1 details validation. Dynamic tool and detail names need no compiled switch. Existing exports remain intact.

Added injected runCommerceTurn with runnerVersion 1.0.0, ordered immutable instructions, current authorization checks, generic multi-step dispatch, one bounded transient retry, call/step/token/deadline limits, cancellation, typed failures, turn-local evidence validation and reserved final revalidation capacity. Added fixtures, documentation and clean-process validation.

Selected additive minor 0.13.0 using the repository README SemVer policy. Published the committed source through npm publish and verified both runtime/type exports in the packed artifact. Release metadata and registry-consumer evidence follow below.

### Validation Results

Node 24.19.0 through scripts/bootstrap-node.sh. Implementation commands ran in the prepared Shared worktree:

- `npm run typecheck`: passed, including after the final schema/history corrections.
- `npm test`: 154 passed, 0 failed, 1 skipped. The existing live BullMQ trace test skips without TEST_REDIS_URL. No new live dependency was introduced.
- `npx tsx --test src/commerce/contracts.test.ts src/commerce/runner/runner.test.ts`: final affected-check run 26 passed, 0 failed (includes two additional regressions after the full-suite run).
- `npm run build`: passed JS and declarations. Repeated prepack builds are npm release mechanics.
- `npm run validate:commerce-entrypoints`: passed with provider/database environment absent.
- `npm pack --dry-run --json`: 75 files; verified dist/commerce/index.js, index.d.ts and dist/commerce/runner/index.js, index.d.ts. Prepack writes build output before the JSON; artifact inspection parsed the final JSON array.
- `git diff --check`: passed; implementation worktree clean after commit/push.

Requirement-to-fixture matrix (all deterministic fixtures passed):

| Requirement | Fixture / checks | Expected and observed effects |
| --- | --- | --- |
| C0/C4 identities, assertions, unknown versions and payloads | contracts: strict identity/assertion/language; six policy input/output; runner cross-tenant/expanded grant | Reject malformed/sentinel identities, invalid money and mismatched tenants/grants; zero model/tool calls on runner admission failure. Tenant existence remains adapter-owned. |
| C1 dynamic feature and effective offer policy | dynamic feature selection matrix | Unknown feature key survives; active/plan/opt-in semantics retained; NONE/FIXED/AI selection has no new paid offer gate; pure function, no I/O. |
| C14 arbitrary tool revisions and provenance | never-seeded query definition; shared-revision dedup/conflict; current revocation | Exact revisions deduplicate with original capability keys; conflicts reject; revocation removes execution without granting replacements. |
| C14 schema/mapping/template restrictions | draft versus strict; decimal maximumPrice; injected compiler path checks | Draft acceptance does not approve execution. Unknown mapping/credential inputs, expressions, unsupported regex/ref and output paths reject; no provider calls. |
| C4/C16 canonical hashes | canonical JSON fixture; response hash checks | C4 code-point sorting and C16 UTF-16 sorting remain explicit; non-JSON input rejects; mismatch stops before model work. |
| C16 R01/R02/R03/R08 | dynamic details and zero-tool referral | Synthetic response.v1 definitions hashed by injected SHA-256; newly named required fields validate; wrong/missing/extra details reject; referral uses empty details. Zero-tool success is one model call, zero remote calls. |
| C16 R04/R05/R12 | invalid schema/envelope/hash fixtures and limits | Unsupported schemas, envelope edits, missing/wrong hashes, release mismatch and oversize data fail. Final regressions also cover optional required keyword and nullable enum behavior. |
| C16 R11 / C6.1 P10 | instruction order and injection | Platform, host, response and capability order preserved; capability/tool text cannot authorize an ungranted call. |
| C6.1 P01–P05 / release pinning | host statuses including COMPLETED with null timestamp; original grant versus new active release | Host context is preserved without status reinterpretation. Later turns retain original release/response hash; attempted replacement fails before model effects. |
| C6.1 P06–P09/P12 | explicit preference, null-pair and fallback scenarios | Explicit preference rejects detection metadata; invalid language pairs reject; supplied context/amount/currency/URL remain unchanged. Scripted language choices are examples, not proof of live natural-language correctness. |
| C6.1 P11 and C6 budgets | missing/duplicate/malformed finals, oversized output, call/step budget, deadline, in-flight cancellation and history overflow | Explicit failures; unauthorized adapters never execute; cancellation reaches in-flight adapter and late results are ignored; >32,000 code-point serialized history rejects before model work. Host owns history trimming. |
| Generic multi-step execution and referral | newly named basket/discount/qualifying tools; unavailable/missing/revoked adapters | Four model steps, three remote calls in order; empty/missing/revoked/unsupported tool paths produce scripted referrals and block subsequent ANSWER after tool failure. |
| C4/C5 evidence | trusted evidence turn/grant/hash/freshness/reservation fixture | Unknown/foreign/expired evidence rejects; only actual policy-adapter extraction registers evidence; Storefront facts do not; remaining remote-call capacity is reserved for host revalidation. |

Structural enforcement is separate from model evaluation. adversarial-evaluations.json records natural-language cases; no live LLM run is required or claimed. Compiler implementations, database authorization, domain adapters, actual Shopify calls, host recovery policy and final pre-delivery revalidation remain their assigned owners' work.

### Publication and clean consumer

- Package: `@modainteract/moda-interact-shared@0.13.0`; registry: `https://registry.npmjs.org/`.
- Source SHA: `34be9702f39ee638631b99222562365c2fb0a4af` (clean committed source before publication; npm metadata does not expose gitHead).
- Exports: `./commerce` and `./commerce/runner`, each with ESM JavaScript and declarations.
- Tarball: https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-0.13.0.tgz
- Integrity: `sha512-LNw7L1D7e+TGXT8GP2qZJMj2m3iU07fMONQPdGYWJjbtShgXd8H3/NZ1El4FJWLCa33s2OBEFw9/igxwBS92bg==`.
- SHA-1: `0b94ce311e616c93c6375ca06310464d44cb205a`. The installed consumer lockfile integrity matches the registry. All 75 installed package files were compared byte-for-byte with the final local publication files and match. The earlier dry-run archive reported a different archive integrity; it is not used as publication-integrity evidence.
- `npm publish --access public --registry=https://registry.npmjs.org/`: succeeded. Initial lookup returned E404 while npm processed the new version; subsequent online lookup succeeded without republishing.
- `npm view @modainteract/moda-interact-shared@0.13.0 version dist gitHead --json --prefer-online --registry=https://registry.npmjs.org/`: returned exact version and metadata above.
- Fresh consumer: `/tmp/shared020-consumer.hIjnbO` with a newly created private package.json, no workspace links.
- `npm install --ignore-scripts --no-audit --no-fund --save-exact @modainteract/moda-interact-shared@0.13.0 --registry=https://registry.npmjs.org/`: succeeded. Its lockfile resolves the registry tarball with matching integrity and no link flag; `npm ls @modainteract/moda-interact-shared --json` confirms 0.13.0.
- `COMMERCE_CONSUMER_DIRECTORY=/tmp/shared020-consumer.hIjnbO node /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-SHARED-001/scripts/validate-commerce-entrypoints.mjs`: PASS both entrypoint imports, manifest validation and scripted finalResponse. The smoke subprocess receives PATH only, no provider/database credentials.


### Deviations

None to task scope. Schema hashes use an injected digest so the contracts remain provider-neutral; Commerce supplies the authoritative query compiler and retained Shopify schema. History admission conservatively counts serialized history code points (including metadata) within 32,000; host adapters trim prior messages before invocation.

### Assumptions

Adapters supply authoritative tenant, entitlement, grant and recovery facts, accurate model token usage, and cancellable I/O. Only reviewed policy adapters extract actual structured evidence. Scripted outputs cannot establish universal grounding or language detection correctness.

### Unresolved Issues

No scoped implementation/publication issue remains. Architect acceptance is pending; downstream consumers must not be promoted by this report. Existing unrelated live Redis trace test was not run because TEST_REDIS_URL is absent.

### Architectural Concerns

No cross-repository changes made. Shape validation does not claim tenant existence or GraphQL executability; these boundaries are documented and represented by injected interfaces.

### Git / VCS

- Canonical workspace: /Users/kwadwoadomafriyie/project/moda-interact-workspace.
- Parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-SHARED-001.
- Implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-SHARED-001.
- Both branches: task/ARCH-020-SHARED-001. Prepared launcher reused correct worktrees, fetched/pruned and synchronized them; remote fast-forward not needed, origin/main already current. Initial parent HEAD 1edb9a54df861eadbef67a5be2cbb36d531abb9e; initial implementation HEAD 5cfa64b199dbfcc4ccad27bcabd2610adee5d479.
- Dependency gate passed for accepted ARCH-016-SHARED-001. Recursive submodule sync/update verification returned ready with an empty entries list: Shared has no recursive database submodule SHA to report.
- Durable Attempt 1 claim: cbb03e1ba73a9147e37ace1eda908264b45e3da0, pushed; executor codex, claimed 2026-09-20T19:16:50Z. One initial launcher fetch raced another task's remote ref update; normal retry succeeded without ref rewriting.
- Validated/published implementation source: 34be9702f39ee638631b99222562365c2fb0a4af, pushed to origin/task/ARCH-020-SHARED-001; local HEAD equals remote branch.
- This report is submitted in a subsequent parent task-only commit. Its final commit/push identifier is recorded in the execution response (a commit cannot include its own identifier).
- No parent service gitlink, architecture/index/frontier, other task, main merge, main push or force push occurred.

## Architect Review

### Accepted — Attempt 2 — 2026-09-20

**Accepted / Complete**, moda_architect. Automatic completion mode applies; Attempt 2 is preserved, executor/claimed_at remain null. The historical Attempt 1 Changes Requested review below is superseded; R1 and R2 are closed.

Reviewed implementation `a83bfc12721423f06af8f8732b07f7dd7153e067` and parent report `595566cac566230ba18caf291a969796e7518670`, with both remote task heads independently verified. Prepared claim `176fc7665cbc06c20b22c0b46c242e4014bb4efa` and the canonical dedicated parent/implementation worktree synchronization evidence are conformant. No new claim was made during review.

R1: both draft and strict schemas use the same whole-definition 65,536-byte storage guard. The separate encoder accounts for jsonb separator spacing, UTF-8, escaped strings and exponent expansion without changing canonical hashing. Regression tests accept 65,535/65,536 and reject 65,537 for ASCII and multibyte aggregates, asserting the size issue alone. Both original oversized reproductions reject. Inspected the seven-row PostgreSQL oracle log: six boundary lengths and the 742-byte exponent/escape fixture match persisted jsonb text exactly.

R2: model step/call shape and serialization are validated before name access or tool dispatch. Malformed calls/final arguments return exactly INVALID_FINAL with no tool effects or error text; invalid host input remains INVALID_INPUT. Existing valid zero-tool and multi-step flows pass.

Independent validation: typecheck passed; focused contracts/runner tests **30/30 passed**; clean registry consumer imports, schema, finalResponse and R1/R2 smoke passed. Inspected developer full-suite evidence: **160 passed, one existing Redis-dependent skip**, zero failures; build/export checks passed. No live LLM execution is required or claimed.

Accepted consumer artifact: `@modainteract/moda-interact-shared@0.13.1`, both `./commerce` and `./commerce/runner`. Independently queried registry integrity `sha512-qano76oJ3McL/EYMq7D0GM0W+kAY0wMsSHzWP1NdXSGCa19YiakjkDjZ9WtUylFCDud+kO+uboR4PTSIBoXEBQ==`; clean consumer lock matches with no workspace link, and all **75 installed files** independently byte-match publication files. 0.13.1 supersedes unaccepted 0.13.0 for this architecture; runnerVersion remains 1.0.0.

Dependency reconciliation: BACKGROUND-001 and SHOPIFY-001 become Ready with their listed prerequisites Complete. Consume exact Shared 0.13.1. Neither task is claimed or launched; preparation must synchronize its canonical worktrees and verify required source availability. Remaining dependants retain incomplete prerequisites and stay Pending; SYSTEM-TEST-001 remains terminal/manual. This acceptance does not merge main, update service gitlinks, or complete ARCH-020.

### Historical Attempt 1 architect review


### Review Status

**Changes Requested — Attempt 1, 2026-09-20, moda_architect.** Not accepted or Complete. Return the same task to `ready`; preserve Attempt 1, with executor/claimed_at null. No downstream promotion.

### Reviewed Source and Evidence

Implementation `34be9702f39ee638631b99222562365c2fb0a4af`; parent report `f713caed8a074b1863ef0fd1a4c4fd4c1dcb3786`. Both remote task heads independently verified. Reviewed commerce schemas, definitions/compiler, canonicalisation, selection, response validation, runner, fixtures/tests, exports/build configuration and publication report. Prepared claim/worktree/synchronization evidence is conformant; canonical parent and implementation worktrees were clean.

Independent typecheck and entrypoint smoke passed. Focused contracts/runner tests independently passed **26/26** using `node --import tsx --test src/commerce/contracts.test.ts src/commerce/runner/runner.test.ts`; the tsx CLI initially hit sandbox IPC permissions, so that failed invocation is not test evidence. Full 154-pass/one-skipped suite is developer-reported evidence. Reproductions below import the installed registry package in `/tmp/shared020-consumer.hIjnbO`, version 0.13.0.

### R1 — P2: enforce the persisted whole-definition size bound

`src/commerce/definitions.ts:136–177` omits a total size bound from CommerceToolDefinitionSchema and gives CommerceToolDraftDefinitionSchema a 131,072-byte total ceiling. C14 requires the same scalar/size bounds for drafts and publication; DATABASE-001 specifies the complete definition at <=65,536 bytes. Accepted database migration `20260920182429_arch020_commerce_capability_releases/migration.sql` enforces `octet_length(v::text)<=65536` on jsonb definitions. Independently bounding each child object is insufficient.

Reproduction: a six-key draft with name `oversize_tool`, definitionVersion `1.0.0`, description `Review fixture`, inputSchema `{}`, and execution/responseTemplate each `{x: "x" repeated 40000}` has compact UTF-8 size **80,149 bytes**, yet draft safeParse succeeds. The exported exampleDefinition with ten variables v0..v9 each `{literal: "x" repeated 8000}` has size **80,974 bytes**, yet strict safeParse also succeeds. The strict reproduction demonstrates structural size admission, not GraphQL compilation approval. Such definitions can pass Shared's authoring boundary and fail persistence.

Correction contract: enforce a whole-definition bound consistently for both draft and strict schemas, compatible with the database's jsonb text byte measurement (account for serialization overhead; changing 131072 to 65536 for compact JSON alone is insufficient at the boundary). Keep canonical hashing semantics unchanged. Add valid near-boundary controls and over-boundary rejections for both paths, including multibyte text and aggregate objects whose individual members fit. Demonstrate admitted boundary fixtures fit the persisted limit, with expected failures attributable to size rather than an unrelated schema constraint.

### R2 — P2: classify malformed model calls as INVALID_FINAL

`src/commerce/runner/index.ts:294–304` checks the calls array but dereferences each element before validating it. A model adapter returning `{calls:[null],outputTokens:1}` with otherwise valid zero-tool fixture inputs produces `{ok:false,error:{code:"INVALID_INPUT",retryable:false}}`. The TypeError is caught as host input failure. C6.1/P11 requires missing or malformed model final output to be INVALID_FINAL; consumers must be able to distinguish malformed model output from invalid host input.

Correction contract: validate the model step/call shape before inspecting or dispatching calls, and map malformed model output to INVALID_FINAL without provider error text or tool side effects. Add null/non-object call, missing/non-string name and malformed final-arguments regression cases with exact error-code assertions; retain INVALID_INPUT for actual invalid host inputs and existing valid multi-step/zero-tool behavior.

### Architecture Conformance and Follow-up

The published 0.13.0 artifact is not architect-accepted for ARCH-020 consumers. Correct R1/R2 on the same implementation task branch, add focused regressions, rerun required validation, and publish a new version greater than 0.13.0 under the existing combined implementation/publication scope. Do not overwrite/reuse 0.13.0. Verify both exports and runner smoke from a clean registry consumer and report the new implementation SHA, version/integrity and test results. Preserve the existing report as historical evidence when submitting Attempt 2.

The parent review overlay is to be committed/pushed using the previously delegated parent-publication workflow before preparation reclaims the task. Preparation owns the next claim; this review does not claim Attempt 2. Downstream task states, implementation code, gitlinks and main integration are unchanged. Architecture remains in implementation; terminal system validation remains required.

### Historical Definition Review


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
