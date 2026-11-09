---
id: ARCH-067-BACKGROUND-001
architecture_id: ARCH-067
title: Use remembered identities and current stock in Background
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: review
priority: 20
executor: codex
claimed_at: 2026-11-09T12:28:17Z
attempt: 1
depends_on: ["ARCH-067-SHARED-002", "ARCH-067-MCP-001"]
created: 2026-11-09
updated: 2026-11-09
---
# Use remembered identities and current stock in Background

## Objective and binding specification
Implement the owned portion of [ARCH-067](../../../architecture/ARCH-067-product-reference-and-current-stock-parity.md). Every schema, mapping, persistence, rendering, diagnostic and compatibility rule there is normative. No merchandise-specific behavior. Dependencies must be complete before execution.

## Exact work and touch points
Own package.json/lock; src/commerce/host.ts model context, verified get_product observations and completion path; product-context-repository.ts validation/serialization/CAS; presentation.ts and recommendation presentation call sites; existing conversation application/replay transaction identified by productContextUpdate. No Prisma schema/table migration. Store extended v1 complete JSON object in existing references JsonB with existing revision/sourceInboundVersion fences. Use Shared recordCommerceProductPresentation with ordered pairs from actual verified rendered result; persist with final reply atomically, not on failed composition. Preserve retry/replay idempotence: replay stored body/context rather than re-read and change the count. Fresh MCP facts carry quantity into Shared verifier/composer, never extract it from history/model text. Initial outreach remains checkout-led with existing rendering and send fences; no new workflow. Test subsequent message 'first one' and variant-label follow-up, stale reference refresh, cross-shop rejection, CAS conflict, unavailable tracking and known0, failed turn leaves context unchanged, replay and final WhatsApp body parity. Run scoped host/repository/presentation tests, typecheck/lint. Record deployment reader gate before emitting new context fields.

## Acceptance criteria
All owned requirements above and architecture contract are implemented and verified. List every actual changed path and test result. Shared behavior must be imported through published public exports; no copied cross-repository source. Unknown inventory remains distinct from zero. Existing authorization, checkout ownership, WhatsApp composition and replay rules pass regression checks. No unresolved design choices may be silently substituted; report a concrete contract conflict before implementing an alternative.

## Non-goals
No inventory mutation, new database table, token-refresh redesign, new template approval/WABA validation, category sequencing redesign or budget increase.

## Completion Report

### Status

Ready for Review — Attempt 1 implemented and published by codex. No architect acceptance decision has been made by this repository agent. Execution remains agent-owned and completion remains developer-controlled.

### Implemented behavior and acceptance evidence

- Exact public `@modainteract/moda-interact-shared`5.11.0 replaces5.9.0 in package/lock. Integrity verified against the immutable handoff below: `sha512-VwVUszfUz0Bgs0alcnjJYK0m5bY7Jt9Nb/LuPRPgrWqk/JCFYqrWbzf7rnsXP2Z8EWlf4yfojbibnOQ4/9YyOg==`. No other dependency refresh or sibling/internal-dist import.
- Installed Shared runner propagates presentation order and selectedOptions to model request context. Scripted native selections for “first one” and “the green finish” assert that exact order/options survive request serialization; remembered stock is absent from reference authority. The host's existing fresh get_product verification uses the upgraded public output schema/fact verifier/composer. A remembered quantity7 followed by fresh2 renders2, independently of model prose; zero, PRODUCT/VARIANT scope, NOT_TRACKED and UNAVAILABLE are covered separately. No arbitrary-language parser or merchandise-specific runtime field was added.
- Native presentation receipts come from verified render inputs through public Shared rendering functions. Full/first/minimal candidate bodies are matched to their native pairs using the same bounded prepared-wrapper renderer; there is no title/URL/customer-text parsing. Recommendation pairs retain retained proposal order; details/options retain verified fact order. Shared recordCommerceProductPresentation records only the actual successful candidate's ordered pairs, separate from general reference sorting. Ordinary unrendered responses do not replace the latest presentation. Minimal product fallback records an empty displayed list. Missing recommendation pair metadata fails closed.
- Existing JSONB stores the complete extended schemaVersion1 object, with the same ownership/platform, 24-hour freshness, 32768-byte bounds, conversation row lock, inbound-version and revision/CAS fences. Production processor writes pass the exact composed assistant body and reserved message ID into the same transaction as context. The pending AGENT/OUTBOUND message must belong to that conversation, have no provider dispatch, and contain the pending placeholder or identical body. Invalid message preparation rolls back the context. Same-version identical context/body is UNCHANGED; a different body conflicts instead of changing a stored count.
- Refused composition and replayed wrapper applications do not write context; duplicate admission still stops before model/provider reads. Processor suppresses delivery for SKIPPED as well as STALE/CONFLICT so an atomic preparation failure cannot send a reply with unsaved reference state. Existing moderation, control/inbound rechecks, provider permit, outbox, initial-outreach and send ownership remain in place. Persistence is atomic with the durable composed/prepared reply, not with an external Meta network call.
- Readers always accept legacy and extended v1 JSON. Only literal server value `COMMERCE_PRODUCT_REFERENCE_V2_WRITE_ENABLED=true` persists presentation/selectedOptions. Default/false/TRUE/1 strip just those fields, preserving native IDs, titles and timestamps. The gate is enforced at repository persistence, without disabling stock verification. Added .env.example and README deployment instructions; no gate was enabled.
- Authorized final detail/option refresh diagnostics extend the existing Shared logger with native IDs, shop/conversation/recovery correlation, stock status/scope and reference/presentation counts. KNOWN/NOT_TRACKED and legacy missing-field reasons are truthfully known here. Canonical UNAVAILABLE carries no provider-specific reason on the wire, so the host logs null rather than inventing PARENT_MANAGED/INVALID_PROVIDER_QUANTITY; exact provider reasons remain at the MCP lookup boundary. No raw provider/customer/model text, credentials or quantity is logged. No generic logger or telemetry runtime was created.

### Actual changed paths (21)

- package.json; package-lock.json: exact immutable public dependency pin.
- .env.example; README.md: default-off server gate and reader-first deployment instructions.
- src/agents/types.ts: trusted host-only recommendation pair metadata.
- src/commerce/host.ts: retained recommendation identity order and bounded final-read diagnostics; existing fresh verification consumes public stock facts.
- src/commerce/presentation-receipt.ts: verified render-candidate/native-pair mapping using public renderers.
- src/commerce/presentation-receipt.test.ts: exact Shared recommendation candidate equality and unrendered-response behavior.
- src/commerce/product-context-write.ts: Shared presentation recording and persistence gate.
- src/commerce/product-context-write.test.ts: nonlexical ordered native pairs, selected options, rejected foreign pairs, no persisted stock authority, exact literal gate values.
- src/commerce/product-context-repository.ts: gated complete JSON persistence and atomic prepared-reply transaction/replay equality.
- src/commerce/product-context-repository.test.ts: real PostgreSQL extended-object read/write, exact body replay/conflict and failed-message rollback, retaining existing owner/CAS/TTL/size/race cases.
- src/commerce/presentation.test.ts: intentional Shared stock-line goldens and fresh zero/positive/scoped/untracked/unavailable fact/composition tests.
- src/services/conversation-turn-processor.service.ts: records rendered pairs only after successful composition, supplies the exact reply for atomic preparation, fails closed on preparation failure.
- src/services/conversation-wrappers/contracts.ts; src/services/conversation-wrappers/compose-ai-outbound.ts; src/services/conversation-wrappers/service.ts: local presentation receipt propagation and actual bounded candidate selection without changing Shared contracts.
- tests/unit/services/conversation-wrappers/service.test.ts: full/first/minimal native receipts within existing wrapper limits.
- tests/unit/services/conversation-turn-processor/ai-wrapper.cases.ts: atomic reply input, actual rendered order/composed body and unchanged refusal/replay fences.
- tests/integration/commerce/host-suites/product-context-acceptance.ts: scripted ordinal/option follow-up request propagation and fresh7→2 selection, preserving existing deleted-reference/denial/clarification regressions.
- scripts/test-arch066-product-context-postgres.mjs: extends the existing disposable fixture with the existing message enums/minimal table needed to prove atomic reply/context storage. No production database schema or migration changed.

### Validation

Workspace bootstrap supplied Node24.19.0/npm11.17.0. Exact Shared version/archive integrity verified. No live model, merchant/provider or Meta request was used.

- `npm run test:commerce-host`: **78 passed**, including scripted follow-ups, stale/deleted references, hard denials, tenant/authority, budget/language, recommendation refresh and existing host scenarios.
- `npx vitest run src/commerce tests/unit/services/conversation-turn-processor.service.test.ts tests/unit/services/conversation-wrappers tests/unit/commerce tests/unit/agents/initial-outreach-offer.agent.test.ts`: **312 passed, 6 skipped**, 32 files. Skips are opt-in PostgreSQL cases; all seven repository cases were executed separately below. This run includes the corrected full/first/minimal wrapper fixture respecting existing header/body limits. Initial invalid oversized-header fixture was corrected rather than increasing any runtime cap.
- Final receipt-specific `npx vitest run src/commerce/presentation-receipt.test.ts tests/unit/services/conversation-wrappers/service.test.ts`: **18 passed**, including new exact recommendation candidate comparison after the final minimal-offer mapping correction. Broader tests were not redundantly repeated after that bounded change.
- `npm run test:arch066-product-context:postgres`: **7 passed** against an isolated disposable PostgreSQL fixture, covering ownership/platform/TTL/size, row-lock/version/CAS conflicts, atomic reply/context commit, same-body replay/different-body conflict and rollback on missing message. Initial new message fixture lacked the existing Prisma enum types; the fixture was corrected and all cases passed. No shared local/test/production database was reset, seeded or changed; the disposable container was removed by the existing harness.
- `npx tsc --noEmit`: passed. No repository typecheck script exists; this is the declared TypeScript compiler against the repository tsconfig.
- `npm run build`: passed on final source, including pinned Prisma6.19.3 generation, production/provision TypeScript and sample packaging. No database migration or gitlink change.
- Changed-path ESLint: passed, including all changed TS/test/harness paths and the final receipt/host edits. `npm run lint` was also run: it reports one pre-existing no-control-regex error at src/providers/shopify-whatsapp-consent.provider.ts:151. That file is byte-identical to starting implementation b583f8154f8382748a73dfd039ab6c22806e307c; no task-owned lint error remains. No matching baseline entry was found; the unrelated file was preserved and this full-lint limitation is explicitly returned for review.
- `git diff --check` and staged diff check: passed. No budget/permission/tenant/resource cap was raised.

Local validation receipts: /tmp/arch067-bg-host.log, /tmp/arch067-bg-final-tests2.log, /tmp/arch067-bg-postgres2.log, /tmp/arch067-bg-receipt-final.log, /tmp/arch067-bg-final-types2.log, /tmp/arch067-bg-scoped-lint2.log, /tmp/arch067-bg-receipt-lint.log and /tmp/arch067-bg-final-build.log. These are local execution logs, not separately published artifacts.

### Git / VCS and physical isolation

Task branch: task/ARCH-067-BACKGROUND-001 in both repositories.
Canonical workspace: /Users/kwadwoadomafriyie/project/moda-interact-workspace.
Reused parent: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-067-BACKGROUND-001.
Created implementation: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-067-BACKGROUND-001.
No shared checkout switched for implementation; no other task worktree reused; no subagent assistance.

Launcher passed both explicit dependencies Complete; parent task branch fast-forwarded and origin/main incorporated; implementation remote FF not needed and origin/main already current. Recursive submodule sync/update passed, database b7f58d5a93e41d54b2fd92a5d483aec4c2c5b595 initialized at its recorded commit. Parent preclaim6bc753ef79c0c6b20438f8ddf915501104ddb048; implementation baselineb583f8154f8382748a73dfd039ab6c22806e307c. Durable Attempt1 codex claim at2026-11-09T12:28:17Z: parent3e9ec917ae9b6a55576195e12db5f688d248d204, pushed.

Implementation: moda-interact-background `8374d721a30a6ae7ec78a4b588c82bb7cdc06a17`, committed and pushed to origin/task/ARCH-067-BACKGROUND-001, clean after publication. This corresponding parent task report is committed/pushed on the matching parent branch. No parent submodule gitlink staged; no main merge/push or force-push; no package publication or deployment.

### Deployment, review and remaining limits

The complete Architect Review was read before source inspection; outcome Not reviewed, no Changes Requested list. That section is preserved. All owned implementation items are submitted for review; full-repository lint has the explicit unrelated baseline limitation above. Terminal cross-host system validation and operational deployment receipts remain separately owned/manual-gated. No live end-to-end rollout is claimed.

Deploy Background and Studio Shared5.11.0 readers before the MCP stock writer; local Studio reader/writer upgrade together. Keep COMMERCE_PRODUCT_REFERENCE_V2_WRITE_ENABLED absent/false until both readers have deployment receipts and the terminal manual operational gate is recorded. Only literaltrue enables reference emission. No reference write flag, deployment, migration, real customer message or live environment mutation was enabled here. No downstream task/index/architecture frontier was changed by this implementation agent; dependency promotion awaits authorized review/completion.

## Architect Review
Status: Not reviewed.


## Architect exact publication handoff — 2026-11-09
SHARED002explicitlyCompleteAcceptedAttempt1; import ONLY exact @modainteract/moda-interact-shared5.11.0, integrity sha512-VwVUszfUz0Bgs0alcnjJYK0m5bY7Jt9Nb/LuPRPgrWqk/JCFYqrWbzf7rnsXP2Z8EWlf4yfojbibnOQ4/9YyOg==; archiveSHA25628db9055f58355fb9779b190beb0eccda356e20fd9a52cf0b753cd1564789309, release-source1ad0d7c47c0a9e1d3d12072b62e238aec1cc92fe/acceptedimplementation467cc1abf5afc467f73861f9830430524022bacd. No range/latestguess or sibling/internaldist import. Publicstock/reference/helper/types/canonicalpurposeoneOf+constcompiler verified.
No deployment occursbytaskclaim/Complete. Newreadersacceptlegacystock, oldstrictreadersrejectnewfield; upgradeBackground/Studio Sharedreaders beforedeployingMCPstockwriter, localStudio reader/writer upgrade together. Keep COMMERCE_PRODUCT_REFERENCE_V2_WRITE_ENABLED absent/falseuntilbothreadersdeployed, literaltrueonlyaftermanualoperationalgate interminalsystemreceipt. MCPsourcecanbeimplemented/acceptedbeforeBackgrounddependentcode; deploymentsequence remainsreader-first, no taskdependencycycle. No inventory/providerwrite, main/live/rollout/gateenablement authorized here.

StillPendingunchangedAttempt0/unclaimed: MCP001notComplete. Publicationavailability alone doesnotclearMCPdependency.

## Dependency readiness reconciliation — 2026-11-09
All explicit prerequisites Complete: SHARED002 accepted immutable5.11.0 and MCP001 independently Accepted/developer-completed Attempt1 (completion1ecd2038e). Exact current MCP completion record carried in this canonical parent branch. Pending→Ready at unchanged Attempt0, executor/claimed_at null; ownership/execution_mode agent/completion_mode developer unchanged. Read exact published5.11.0/integrity from handoff. No claim/implementation worktree or task execution initiated; normal deterministic preparation required on invocation. Reader-first deployment and literaltrue-only default-off reference-write gate remain mandatory and unexecuted.
