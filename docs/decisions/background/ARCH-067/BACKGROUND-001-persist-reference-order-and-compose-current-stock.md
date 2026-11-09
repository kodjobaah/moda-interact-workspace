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
status: in_progress
priority: 20
executor: codex
claimed_at: 2026-11-09T13:56:31Z
attempt: 2
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

Changes Requested — reviewed Attempt 1 on 2026-11-09. One required persistence-lifecycle correction remains; the implementation report below is preserved as submitted evidence and does not establish acceptance. Status Ready, executor/claimed_at null, attempt 1 unchanged.

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

## Developer Self-Review — Changes Requested, Attempt 1

2026-11-09: Explicit `/moda_developer_update ARCH-067-BACKGROUND-001` authorizes developer-as-architect review of this submitted agent implementation. Execution_mode agent and completion_mode developer are preserved; this review is not an execution takeover or a new claim. Reviewed the complete task/architecture requirements, 21-path implementation diff from b583f8154f8382748a73dfd039ab6c22806e307c, provider fact/presentation paths, persistence transaction, delivery/moderation ordering, tests, published package receipt and recorded validation/isolation evidence.

### Publication and validation reconciliation

Both dedicated task worktrees were clean before this review. Source8374d721a30a6ae7ec78a4b588c82bb7cdc06a17 and parent report799428b6d1195d7316f64360fe76c74aacc49dbb match their respective local HEAD/tracking refs and directly queried remote task refs. Exact Shared5.11.0 public pin/integrity, default-false literal gate, verified native render receipts and existing source/DB worktree isolation were reconciled. No subagent assistance or source change occurred during review.

Fresh focused command `npx vitest run src/commerce/product-context-write.test.ts src/commerce/presentation-receipt.test.ts src/commerce/presentation.test.ts tests/unit/services/conversation-turn-processor.service.test.ts` passed **91/91**, no failures/skips; local receipt /tmp/arch067-bg-review-tests.log. Earlier312 regression tests,78 host cases,7 PostgreSQL cases,18 final receipt tests, type checking/build and changed-path lint remain relevant for unchanged source. The full-lint error in untouched Shopify consent code is accurately disclosed and is not the reason for Changes Requested. Passing existing tests do not cover the required failed-turn persistence invariant below.

### R1 — [P1] Do not replace remembered presentation before final delivery eligibility succeeds

**Evidence:** src/services/conversation-turn-processor.service.ts:641-645 commits product context/presentation and the PENDING composed message before the post-transaction control/inbound checks at652-658 and before sendPreparedText at662. The latter still performs admission revalidation, whole-message moderation at src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts:118-120 and final provider fence at122-128. Any of these can suppress delivery after the context transaction has committed; no rollback/restoration follows. The current test tests/unit/services/conversation-turn-processor/ai-wrapper.cases.ts:47-56 expressly expects a successful context write and then no send on an inbound race. Repository PostgreSQL tests establish that WRITTEN is durable, not a tentative update.

**Impact:** With the reference gate true, a moderated/obsolete reply can replace the last successfully displayed ordered list even though that reply never reaches the customer. The next “first one”/option follow-up can target an unseen product. Even with the gate false, failed turns can replace the general reference snapshot. This contradicts the normative ARCH-067 requirement “Failed turns leave previous context/presentation unchanged.” Atomicity with a PENDING body alone does not meet that lifecycle guarantee.

**Required source correction:** Coordinate persistence with the existing successful durable reply-admission/application boundary, retaining moderation, control/inbound version, tenant, message ownership, CAS and provider permit protections. For a turn refused or superseded before final admission, leave the prior reference/presentation snapshot and revision unchanged. Keep the exact chosen composed body and its native presentation pairs atomic at the successful boundary; do not solve this by holding a database transaction over a network send, blindly restoring an old context over a concurrent winner, introducing a new table/schema, or weakening moderation/send/replay fences. Preserve explicit behavior for already-admitted/unknown provider outcomes through the existing replay machinery rather than regenerating facts or text.

**Required regression proof:** Add deterministic orchestration plus real-transaction coverage starting with a previously presented list A and proposing B. Demonstrate that (1) whole-message moderation refusal, (2) takeover/new inbound arriving during preparation, and (3) final pre-admission/version/CAS rejection leave A and its revision intact and do not send B. The existing race test must assert retained state, not only a call to write followed by no send. A successful eligible turn must durably store B with its exact composed stock body and rendered order once; replay must retain that body/context without an extra provider fact read or a changed stock count. Run affected processor/delivery/context/presentation tests, the isolated PostgreSQL transaction cases, type checking/build and changed-path lint. Keep the unrelated full-lint limitation explicit unless separately resolved within authorized scope.

### Decision

Changes Requested; no passing acceptance or completion decision. Attempt1 unchanged; status Ready; executor and claimed_at null. The next authorized execution claim creates Attempt2 exactly once on the same canonical branch/worktrees. No source implementation was changed, no downstream task promoted, no architecture/index altered, and no main merge/push, feature gitlink update, package publication, deployment or gate enablement occurred. The separate Architect Review placeholder is preserved; this developer review is the durable correction contract for the next attempt.
