---
id: ARCH-020-COMMERCE-009
architecture_id: ARCH-020
title: Implement isolated preview lifecycle and execution service
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 130
executor: null
claimed_at: null
attempt: 4
depends_on:
  - ARCH-020-COMMERCE-002
  - ARCH-020-SHARED-001
  - ARCH-020-COMMERCE-001
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-010
  - ARCH-020-COMMERCE-013
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-21
---

# Implement isolated preview lifecycle and execution service

## Architecture

ARCH-020. [Parent architecture](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).
Binding [implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md):
C4/C5/C7/C8/C9/C14/C16/C18 as applicable, and exact ownership/interfaces in **C19**.

## Objective

Own C9.1 preview routes, synthetic runner/tool execution, Redis state/replay/budgets and cancellation. No U14 visual components.

## Context

This is the canonical narrowed definition from the 2026-09-21 task split, replacing
the former combined scope. No prior attempt or implementation is discarded. Normal
launcher/worktree/review policies apply. No task is claimed by this definition.

## Scope

Own C9.1 preview routes, synthetic runner/tool execution, Redis state/replay/budgets and cancellation. No U14 visual components.

## Out of Scope

Other C19 owners' modules; new Shared wire versions or database schema; live
deployment/provider calls; unrelated refactors; cart/order writes or WhatsApp sends.
Do not implement missing dependencies or substitute production fixtures to finish.

## Requirements

Use accepted auth/Shared/database source, canonical types and C19 ports. Preserve
others' changes. Exact business names remain database-authored. Fixtures are injected
only by tests; production missing adapters fail closed. Each case below has an
expected side effect, not just a screenshot/typecheck. C19 assigns final wiring.

## Work Items

- [x] Implement every C9.1 route and strict body/status/ownership shape using accepted auth guards. Fixture mode requires no live provider/model; explicit model mode has separate credentials.
- [x] Implement atomic environment/admin/run identity, creation replay, payload conflicts, conversation busy lock, 24h retention,20-turn/32k history, quotas and cancellation/UNKNOWN handling.
- [x] Reuse the accepted Shared runner, C16 synthetic frozen response definition and C6.2 language/status fixtures. No production transcript/shop credential or WhatsApp admission.
- [x] Use C19 PreviewBundleLoader against injected authorized synthetic bundle fixtures until013 supplies the real saved-bundle adapter. Unavailable production composition fails closed.
- [x] Expose the exact service contract and controlled runner fixtures to017. Do not implement UI forms/navigation/screens or production publication/compiler services.

## Interfaces / Contracts

Own `src/commerce/preview/` and exact C9.1 route handlers under the accepted App Router root.017 owns U14;013 owns real saved-bundle composition. This backend task can be accepted with strict loader fixtures;013 must verify real service wiring.


## Dependencies

- ARCH-020-COMMERCE-002
- ARCH-020-SHARED-001
- ARCH-020-COMMERCE-001

All listed prerequisites must be Complete and architect-accepted before a claim.
Use dedicated launcher worktrees and accepted source; do not launch enabled work.

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-010
- ARCH-020-COMMERCE-013
- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [x] P01: all C9.1 methods validate auth/owner/body and return exact statuses; other admin IDs leak no data.
- [x] P02: cross-replica same-ID replay reserves one budget/model call; changed payload conflicts; distinct run IDs on one conversation reject before any start.
- [x] P03: quotas, history/turn boundaries, cancellation/completion race, unknown/crash state, slot TTL and retained dedupe have explicit fake-clock assertions.
- [x] P04: C6.2 language and C16 response cases use frozen synthetic state and the same runner version; later publication never expands the preview grant.
- [x] P05: fixture output cannot send WhatsApp, access production providers or spend model quota; model mode never falls back to production keys.

## Validation

Implement the named cases above as focused tests. Record case -> fixture -> command
-> expected/actual effects in the Completion Report. Check shared contract examples
where applicable; include malformed and denied inputs with zero side effects.
Run focused tests while developing, then typecheck/lint/build once before submission;
repeat broader checks only for new failures or changed concerns. Use actual repository
commands and record them. Local browser/component evidence is task-owned where a UI
is in scope. Follow agent-validation/live-validation policies; separate pending
required developer database/container evidence and never claim fixture tests prove
live service behavior. No minimum screenshot/test count substitutes for coverage.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; consume the accepted COMMERCE-001 foundation.

## Completion Report

### Status

Ready for Review.

### Files Changed

Implementation commit `5d4dcd3` in
`moda-interact-commerce`:

- `src/commerce/preview/types.ts`, `store.ts`, `redis-store.ts`, `service.ts`
- `tests/preview-service.test.ts`, `preview-store.test.ts`,
  `preview-redis-lua.test.ts`, `preview-routes.test.ts`

### Work Completed

- Added the C19 `PreviewPromptLoader` port without changing `PreviewBundleLoader`.
  Conversation creation validates exact manifest prompt membership and freezes the
  authored text; missing, duplicate and mismatched sources fail closed before a run.
- The Shared runner now receives all accepted completed history plus exactly one
  current user input. It uses the stored authored prompts and rejects before
  dispatch when the canonical 20-message runner bound would require truncation.
- Stored language now starts from the fixture and advances atomically only after a
  successful fenced C16 final with substantive input and high-confidence detection.
  Ambiguous, numeric, null and low-confidence cases retain the prior language.
- All fixture, model and tool-test ownership expires to retained UNKNOWN at120s in
  both stores. Completion sweeps first, stale tokens cannot append history/language,
  tool execution has a deadline, and a cross-replica watcher propagates cancellation
  to the active runner signal before cancellation is acknowledged.
- Redis transport now keeps bundle, prompts, language, history items and results as
  validated opaque JSON. The Lua state has a1MiB/128-conversation/1024-run aggregate
  capacity guard that rejects before SET, and adapter responses are schema checked.
- Added an isolated local Redis-compatible rehearsal that executes the actual Lua
  script for opaque round trips, simultaneous owners, expiry, fencing and capacity.
- Replaced the cancellation-only query with an atomic positive ownership check.
  In-memory and Redis implementations now authorize work only while the exact
  environment/admin/run/token owns an unexpired RUNNING run and its conversation
  lock, with no cancellation request. The service uses this check before the Shared
  runner and each model/tool dispatch, and the watcher aborts when ownership is lost.
- Added the Attempt 4 fake-clock regression: after run A expires and run B reserves
  the same admin's released model slot, A's delayed callback performs zero model or
  tool calls and cannot change UNKNOWN state, history, language or B's reservation.

### Correction Checklist

- A2-R1: actual message/history and exact frozen authored prompts reach the first
  ModelRequest; invalid prompt adapters fail before model admission.
- A2-R2: accepted language changes persist with history in the owner-token transition;
  reverse, ambiguous, low-confidence, cancelled and stale cases retain prior state.
- A2-R3: every execution kind has120s ownership expiry; completion/cancel sweep and
  fence, remote cancellation aborts waiting work, and timed-out tool results stay UNKNOWN.
- A2-R4: opaque validated Redis codecs preserve arrays/objects/null/Unicode, aggregate
  state is bounded, and actual Lua behavior is exercised rather than stubbed.
- A3-R1: expired, missing, terminal, cancelled and wrong-token owners fail closed;
  delayed callbacks stop before external effects while replacement ownership remains
  intact. Both in-memory and executable Redis Lua contracts cover the ownership edge.

### Validation Results

Agent-executed:

- `npm test -- tests/preview-redis-lua.test.ts tests/preview-service.test.ts tests/preview-routes.test.ts tests/preview-store.test.ts`:
  PASS,4 files /37 tests. The four Redis tests executed a disposable local
  `redis-server` over a Unix socket and removed it after the run.
- `npm run lint`: PASS, zero warnings/errors.
- `npm run typecheck`: PASS.
- `npm run build`: PASS; all C9.1 routes compiled and were listed by Next.js.
- `git diff --check`: PASS.
- `npm test`:219 passed,1 failed outside preview scope. The configured live
  `tests/discovery-limits.test.ts` timed out at30s while exercising Shopify discovery.
  All preview tests, including the isolated Redis Lua harness, passed.

Focused case matrix:

- P01 routes remain covered by executable auth/body/owner/replay/error tests.
- P02 races now include two service instances sharing a store and two Redis adapters
  racing through the actual Lua script; exactly one owner reserves work.
- P03 fake-clock and Lua cases cover20 failed dispatches, canonical history rejection,
  quotas,120s fixture/model/tool expiry, stale-token fencing, remote cancellation,
  tool timeout and24-hour dedupe.
- P04 ModelRequest assertions cover current input once, completed history, frozen
  authored prompts, English/French transitions and retained ambiguous language.
- P05 injected fixture/model/tool counters retain synthetic-only execution; no paid
  model, Shopify provider, WhatsApp, database migration or customer data was used.
- A3-R1 directly checks valid, expired, missing and wrong-token ownership in memory
  and Redis Lua, and proves an expired queued MODEL callback has zero external effects
  after a same-admin replacement reservation.

Developer/integration validation remains for deployed Redis and COMMERCE-013's real
saved-bundle/prompt/model/tool adapter pairing. Local Redis proves the committed Lua
contract only; it does not claim deployment configuration evidence.

### Deviations

None.

### Assumptions

- Accepted database revision consumed: `5abfd87f57038bae515aaa09ec7c8db62adcfb98`.
- Production runtime uses Redis state and fails closed until COMMERCE-013 injects
  the authorized saved-bundle and explicit preview model/tool adapters.

### Unresolved Issues

The full-suite discovery-limit timeout remains outside this task. Deployed Redis and
the real COMMERCE-013 adapter pairing remain developer/integration evidence.

### Architectural Concerns

None newly reported.

### Git / VCS

- Task branch: `task/ARCH-020-COMMERCE-009`.
- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-009`, `task/ARCH-020-COMMERCE-009`.
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-009`, `task/ARCH-020-COMMERCE-009`.
- Shared workspace/implementation checkout switched or mutated: no. Another task
  worktree reused: no.
- Start synchronization: parent remote task fast-forward not needed; parent
  `origin/main` already current; implementation remote task fast-forwarded and
  `origin/main` incorporated by the launcher.
- Recursive submodule sync/update: passed. Database pin:
  `5abfd87f57038bae515aaa09ec7c8db62adcfb98`.
- Implementation commit `5d4dcd3db0190940c603eefb1ac399ddc52c402a` pushed to
  `origin/task/ARCH-020-COMMERCE-009`.
- No main merge, main push, force push, parent gitlink update or unrelated parent
  file edit was performed.

## Architect Review

### Changes Requested — Attempt 3 — 2026-09-21

**Current decision: Ready for corrections; Attempt 3 retained; executor/claimed_at null; not accepted.** Reviewed implementation `8aaa2b39dc5515ca5642b59f7bb639d03541efeb` and parent report `fb3413bdda38eae44c9f0edc79c3150204d76633`, verified against remote task heads. Both dedicated worktrees were clean. The submission's frontmatter already said `ready` despite its Ready for Review report; this decision now explicitly confirms Ready for the correction below. No new attempt was claimed.

Independent validation: **34/34 focused tests passed**, including the three actual local Redis Lua tests, plus implementation diff check. Isolated `/tmp/c009-a3-review/review.test.ts` imports the submitted implementation and reproduces one functional failure: after a MODEL run expires to UNKNOWN at120s and a replacement run reserves the same admin's released slot, executing the old queued worker calls the model once (expected zero). No paid model/provider was contacted. Typecheck/lint/build and full-suite177 passed/one unrelated discovery timeout remain submitted evidence, not independently rerun.

A2-R1 and A2-R2 are resolved: exact current input, completed history and frozen authored prompts reach the Shared runner; successful language transitions persist atomically. A2-R4 is resolved for component acceptance: validated opaque JSON preserves nested types, strict aggregate capacity rejects before mutation, and actual Lua transitions have local executable evidence. Retain these changes. A2-R3's result fencing, tool deadline and cross-replica cancellation improvements are valid, but execution fencing remains incomplete as below. Deployment Redis and013's saved-source/model/tool composition remain separate integration validation;017 owns U14.

#### A3-R1 — P1 — Stop expired owners before they execute model or tool work

Files: `src/commerce/preview/service.ts` (`cancelled`, cancellation watcher and dispatch boundaries), `store.ts` (`isCancelRequested` or a replacement ownership-check port), `redis-store.ts` equivalent Lua transition, and focused tests.

Both stores sweep expired runs to UNKNOWN and release their model slots, but `isCancelRequested` returns only whether the matching token has `cancelRequested=true`. UNKNOWN, missing and mismatched-owner runs therefore return false. The service treats false as permission to continue. A delayed worker can consequently spend model quota after its ownership expired and after a replacement run has acquired the released concurrency slot. Fencing only `completeRun` prevents stale history writes but does not prevent the external call.

Implement these steps:

1. Add or adapt a store operation that atomically sweeps and validates that the exact environment/admin/run/token still owns a RUNNING, unexpired run and its conversation lock, with no cancellation request. Implement equivalent behavior in memory and Redis. Missing, expired, terminal or mismatched ownership must not authorize execution.
2. Use that check before starting the Shared runner and immediately before every model/tool dispatch. Have the existing watcher abort the same active execution signal when ownership is lost, as well as on explicit cancellation. Preserve UNKNOWN and retained replay state; do not convert expired ownership into a new run, refund quota, append history/language or clear another run's lock. Keep the existing completion token fence.
3. Add a fake-clock regression using the reproduction above: queue MODEL run A, advance to120s, observe UNKNOWN, reserve run B for the same admin, then invoke A's delayed callback. Assert zero A model/tool calls, unchanged UNKNOWN/history/language and B's reservation intact. Check the ownership operation's expired/missing/wrong-token outcomes against both stores using the existing local Lua harness. Retain the passing explicit remote-cancel and completion-race cases. This is a targeted functional correction, not a requirement for exhaustive coverage or live providers.

### Attempt 3 resubmission instructions

Implement A3-R1 only within009-owned backend modules/tests. Run focused preview validation and required lint/typecheck/build/diff checks, update the Completion Report with actual results, commit/push the same implementation and parent task branches, clear the claim and set the submission status to `review`. The architect retains acceptance authority. Do not launch enabled tasks, alter017 UI or implement013 production adapters. No dependent promotion, implementation edit, main merge/push or gitlink update was performed by this review.

### Changes Requested — Attempt 2 — 2026-09-21

**Current decision: Ready; Attempt 2 retained; executor/claimed_at null; not accepted.** Verified implementation `e614a032c73463584fd6c9be91b97ed74b3deccb` and parent report `36d174b0f497af47be1be715948c47983e5a9ab9` against remote task heads. Dedicated worktrees clean; preparation/database evidence recorded. No implementation edits, new claim, dependent promotion, main integration or gitlink update.

Independent submitted suite: **19/19 passed**, covering service, routes and store. Isolated `/tmp/c009-a2-review/review.test.ts` imports committed code:11 copied service tests pass and3 added behavioral cases fail (current message absent from ModelRequest; second-turn language resets to English after French detection; abandoned FIXTURE dispatch still RUNNING at120s). Broader162-pass/2-infrastructure-failure, typecheck/lint/build remain submitted evidence. Diff check passed. No live Redis/model/provider/database checks were run. The Redis test only stubs EVAL with a constant CONFLICT response and asserts script text; it does not execute or validate Lua transitions.

Retain the improvements: actual Shared runner invocation, canonical saved IDs, strict body/result schemas, atomic in-memory replay/quotas, retained tool tests and route error mapping. The following are remaining R1/R2 component requirements, not scope amendments.013 still owns real saved-source/provider assembly;017 owns UI.

#### A2-R1 — P1 — Execute the current message and actual frozen instructions

Files: `src/commerce/preview/service.ts` execute/startConversation, types.ts stored snapshot and prompt port, service tests. run.message is saved in state but never passed into runCommerceTurn. The first ModelRequest has history=[] and messages=[] and does not contain the submitted message anywhere. Every capability prompt is also replaced by `Synthetic preview instructions for ${capability.key}.`, so authored behavior is not being previewed.

For each invocation construct runner history from the bounded completed history plus exactly one `{role:'user',content:run.message}`. Do not persist the pending message into completed history until successful fenced completion. Remove the unconditional slice(-20): preserve all accepted history within the canonical runner bounds or reject before dispatch if those bounds would be exceeded; do not silently drop accepted context. Add assertions on actual ModelRequest, not only on final canned replies.

Resolve actual prompt texts for the exact frozen manifest revision/prompt names at conversation creation. Keep C19 PreviewBundleLoader's existing `{grant,manifest}` result; add a separate typed PreviewPromptLoader dependency if prompt contents cannot be obtained from that result. It accepts principal and validated bundle and returns bounded `{name,text}[]` corresponding exactly to required manifest prompt names.009 validates and freezes the returned text in StoredConversation;013 supplies the authorized production implementation, fixtures inject explicit texts. Missing/mismatched prompt adapters return503 before a run is admitted. Never synthesize placeholder authored instructions. This is an architect-approved local composition port clarification; no Shared wire or database change.

Tests: unique current-message sentinel reaches first model request exactly once; second request contains first completed exchange plus current input once; later loader/source mutations cannot alter stored prompt text; invalid/missing/duplicate required prompt names reject before model execution; a model stub asserts selected authored prompt text is in its actual instructions. Keep fixture data clearly synthetic, without replacing the behavior being tested.

#### A2-R2 — P1 — Persist preview conversation language transitions

Files: service.ts execute, types.ts StoredConversation, store.ts/redis-store.ts atomic completion. Current execute always passes fixture.language; valid final detection is never applied. Reproduction uses the English fixture and a successful French detectedLanguageTag/confidence final; the next ModelRequest still has `{tag:'en',source:'merchant-default'}`.

Initialize conversation language from its fixture once. Apply accepted language-resolution semantics to a successful validated final and the actual substantive input; persist the resulting language atomically with completed history under the run owner token. Subsequent turns use this stored state. Ambiguous/short/numeric/URL/emoji input or null/low-confidence detection retains current language; failed/cancelled/stale results cannot update it. Do not invent customer preferences or modify currency/policy. Reuse accepted Shared language helpers where provided rather than inventing thresholds.

Tests: English initial -> substantive French -> ambiguous numeric reply remains French; reverse language change; null/low-confidence/ambiguous detection does not switch; cancelled or fenced-out completion does not change language. Assert both stored state and the next ModelRequest, with valid C16 finals and controlled fixtures. The current test only verifies initial French fixture context and does not prove language lifecycle.

#### A2-R3 — P1 — Complete crash fencing and distributed cancellation

Files: store.ts sweep/completeRun/completeToolTest, redis-store.ts Lua transitions, service.ts cancelled/execute/cancelRun/runToolTest. Expiry iterates only modelSlots, so fixture runs and tool tests never become UNKNOWN after crashed ownership. A suppressed fixture dispatch remains RUNNING at120s. In-memory completeRun also does not sweep before committing, so a late model completion can win if no intervening read triggers sweep. Tool tests execute synchronously with an AbortController that has no timeout. Remote cancel only writes a flag; an in-flight model on another service instance is not notified until it returns or another step begins.

Track ownership expiry for every RUNNING run/tool-test independently of paid model quota slots. Apply120s expiry before read/reservation/completion/cancel transitions in both stores, fence expired tokens, retain UNKNOWN results/dedupe for24h and block an UNKNOWN conversation until Reset. Do not refund dispatched quotas. Add an explicit bounded tool execution deadline and never allow a late result to overwrite UNKNOWN. No automatic rerun.

During execution use a bounded cancellation watcher or equivalent owner notification that aborts the same model/tool signal when another replica requests cancellation. Stop/clean up watchers in finally. Remote cancel must not acknowledge CANCELLED until execution stops; completed-before-cancel remains completed. Test cancellation while the model is waiting, not merely between calls. Do not swallow cancellation and subsequently label an unfinished response COMPLETED. Handle rejected dispatch/store completion without unhandled background promise rejections; leave durable recoverable UNKNOWN when terminal persistence fails.

Tests: fixture/model/tool-test crash at120s; completion at the boundary without a preceding GET; stale token cannot append history or language; two distinct PreviewService instances share a store and service B cancels service A's waiting signal-aware model, with no manual release; no subsequent model/tool effect; tool timeout becomes terminal and late completion is fenced; completed-wins-late-cancel retained. Use fake clocks/barriers and effect counts, no live deployment.

#### A2-R4 — P1 — Validate Redis serialization and bound the shared state document

Files: redis-store.ts transport codec/Lua and tests/preview-store.test.ts. Every operation decodes/re-encodes the entire environment's nested bundles/history/results with Lua cjson and writes one global JSON document. This does not preserve the distinction between empty JSON arrays and objects through ordinary Lua tables; accepted manifests and empty history contain arrays whose types matter. The TypeScript `JSON.parse(...) as T` assertion cannot validate round-trip shape. The same environment document has no size/item cap and is rewritten on every poll/cancel, so per-result bounds do not bound work per EVAL. This is source-level review; the submitted test does not execute Lua and no live Redis behavior is claimed here.

Preserve schema-bearing opaque JSON exactly (for example, store grant/manifest/result and history as explicit JSON strings with a typed adapter codec, while Lua handles only the small transition metadata), or use an explicitly verified array-preserving codec. Validate returned state before it reaches the runner; don't cast malformed transport data to StoredConversation. Avoid a single unbounded environment-wide payload: use scoped per-conversation/run data and bounded atomic quota indexes, or enforce documented strict aggregate byte/item bounds before state mutation with a bounded typed capacity error. Idle retention alone is not a capacity bound under continued fixture creation/polling. Keep atomic replay/quota/fencing behavior.

Execute the actual Lua transition contract in an isolated deterministic local harness or compatible controlled evaluator. A mocked EVAL returning a fixed constant is not transition validation. Required round trips include nested empty arrays/objects, manifests/grants, empty/completed history, result details, nulls and Unicode; validate Shared schemas before/after and run a fixture through the returned state. Reuse the same race/expiry/cancel/quota tests against the Lua adapter and in-memory model, including simultaneous owners and configured capacity boundary rejection with no partial mutation. Live deployment Redis remains developer-owned and is not required; report runtime coverage limits honestly if the local evaluator is unavailable.

### Resubmission

Implement A2-R1–R4 only in009-owned backend paths and tests. Publish the prompt port clarification for013 and preserve PreviewBundleLoader compatibility. Update P01–P05 mappings to actual tested effects; separate constant transport-envelope checks from Lua behavior. Run focused and required validation, commit/push the same branch pair and return to review. No UI or live provider work is added. This parent review overlay is published before handoff; normal preparation owns the next claim.


### Changes Requested — Attempt 1 — 2026-09-21

**Current decision: Ready, Attempt 1 retained, executor/claimed_at null; not accepted.** Reviewed implementation `fa795af310d0df76a1553e4adb7d77dbe6c7b149` and report `4081872461747617aa103e222456262dd7ff0443`. Remote task heads verified and dedicated worktrees clean. No new claim, implementation edits, dependent promotion or main integration.

Independently ran the submitted focused suite: **4/4 passed**. Isolated harness `/tmp/c009-review/preview-review.test.ts` imports the committed service/schemas and extends the submitted fixtures: **4 original tests pass; 4 added review tests fail**. Two concurrent same-ID creations both return201; turn21 is accepted; matching tool-test replay executes twice; canonical saved CUID-style revision identity is rejected. Diff check passed. Lint/typecheck/build and full72-pass/one-readiness-failure remain submitted evidence, not independently rerun. The readiness failure is not the acceptance blocker. No live Redis/model/provider or database operation was run.

#### R1 — P1 — Implement the actual Shared-runner preview lifecycle

Assigned location: `src/commerce/preview/` per C19, moving current `lib/preview/{types,service,runtime}.ts` responsibilities there; a compatibility re-export is fine. `PreviewBundle` currently contains unknown grant/manifest values and execute ignores both, returning fixture-prefixed user text or unchanged user text for MODEL. There is no Shared runner invocation, C16 final validation, tool dispatch, model call or C6.2 language behavior. Environment-variable presence must not turn an echo into a reported completed model preview.

Define PreviewBundleLoader with accepted Shared grant/manifest types exactly as C19; validate and freeze both plus synthetic fixture state at creation. Execute through accepted `runCommerceTurn` with the frozen prompts, response definition/hash, grant and tool descriptors. Fixture mode uses deterministic scripted model/tool adapters, with no paid model or live provider; explicit MODEL uses a separately injected configured model transport and preview-only credentials, never Background fallback. Missing adapters/config produce503 UNAVAILABLE before admission/dispatch as applicable.013 owns real saved-bundle loading and actual interpreter/provider composition;009 still owns runner lifecycle and its controlled fixtures.

Propagate one cancellation signal through each model/tool step, validate bounded final/trace results, record redacted preview telemetry using the accepted shared logging/observability infrastructure, and never invoke WhatsApp or production grants/transcripts. Async dispatch must durably record RUNNING before execution; first run POST returns202 status, polling observes terminal state. Crashed ownership becomes UNKNOWN, never a completed echo. Provide fake-clock/barrier P04/P05 fixtures: French/English language rules, frozen later-publication independence, C16 valid/invalid final details and hash, fixture0 paid calls, explicit model mock1 call, model failure/cancel with no retry/fallback. No live paid/provider execution is required.

#### R2 — P1 — Own atomic Redis state, limits and cancellation as C19 requires

Files: `src/commerce/preview/store.ts`, Redis adapter, lifecycle service and focused store/runner tests. The existing store has separate get/put calls, keys only admin/id (no environment), mutable read references and no atomic claim/quota operations. C19 explicitly assigns Redis state/budgets to009; it does not transfer them to013. Correct the report's contrary deviation. The unavailable loader is permitted; an in-memory production state factory is not the required distributed lifecycle implementation.

Expose atomic create/replay, run reservation, completion/cancel and quota transitions in the state port; implement Redis operations with atomic scripts/transactions and inject a controlled Redis transport for tests. Provide a detached in-memory equivalent in test fixtures only. Use environment/admin/conversation/run identity. Check canonical payload hash with Shared canonicalJson (not JSON.stringify property order), same-ID replay BEFORE busy/quota, then atomic conversation lock and budget reservation. Matching concurrent creation returns one201 plus replay200 and freezes one winner bundle; changed identity/payload conflicts without overwriting state. Two service instances must share the same atomic test store.

Implement C9's20 dispatched-turn limit,32,000-character completed history/input reservation,10 model turns/admin/rolling hour,1 model run/admin and2 platform-wide. Reject before dispatch with exact409/429 statuses and zero side effects. Failed/cancelled/unknown dispatched runs count; rejected requests do not. Store assistant and user text only for completed turns; do not push pending input into completed history. Bound completion before append, never truncate. Retain run/result/dedupe24h, expire crashed in-flight slots120s, and keep UNKNOWN conversations blocked until Reset. Cancellation is a distributed request checked by the owning runner; acknowledge only when stopped, preserve completed-wins-late-cancel, and never clear a newer owner's lock via unconditional finish. Reset does not refund or bypass old-call quotas. Missing Redis fails closed for model execution.

Permanent tests: the concurrent-creation and21st-turn reproductions; same-run replay/changed payload; two distinct runs racing one conversation; separate-admin/platform quota boundaries; canonical key-order equivalence;120s/24h exact boundaries; cancel/complete race; crash UNKNOWN; stale completion fencing; no quota refund/automatic retry. Use barriers, two instances and effect counts, not sequential get/put fixtures. Real deployment validation can remain separately unrun, but implementation of these owned operations cannot be deferred.

#### R3 — P1 — Persist and replay tool tests; implement their GET route

Files: lifecycle/store, `app/api/studio/preview/tool-tests/route.ts`, `app/api/studio/preview/tool-tests/[runId]/route.ts`. runToolTest directly calls the optional loader method on every submission and never stores a run. GET unconditionally returns NOT_FOUND. Reproduction submits the same run ID and payload twice: execution count2, expected1. This breaks C9.1/U14 even with injected fixtures.

Use the same environment/admin/run namespace, canonical hash, atomic claim and24h retention as conversation runs, including cross-kind ID conflicts. Recheck current admin/revision access; load and freeze the exact authorized saved revision, validate arguments against its accepted schema, then invoke only fixture tool execution. Persist bounded {previewRunId,status,result}; repeated same input recovers it without executing again, changed input returns409 ID_CONFLICT, wrong owner/expired returns404. Implement GET from retained state. Tool tests never invoke a model or consume paid-model quota. Loader's exact C19 load return remains {grant,manifest}; inject a separate typed fixture tool execution port rather than using an unvalidated optional loader method as a shortcut.

Tests: POST -> GET -> matching replay with execution1, concurrent duplicate1, changed arguments conflict0 extra, different admin404, invalid arguments0 execution, expiry404, <=64KiB result bound and no model/provider/WhatsApp calls.

#### R4 — P1 — Correct saved IDs, C16 validation and HTTP contract tests

Files: preview schemas/http and every C9.1 route; add executable route tests. Preview conversation/run IDs are UUIDs; saved release/tool/capability revision IDs are canonical database IDs, not UUID-only. The submitted selection/tool-test schemas reject valid saved CUID-style IDs such as `cmflq1234000008l79abc1234`. Reuse accepted Shared identity bounds/types for saved IDs, keep UUID validation for preview IDs, and perform saved ownership/access checks through the loader. DRAFT responseContract must use full accepted C16 schema; z.unknown is not validation. Validate loaded Shared limits and unique selected membership before freezing.

Bound body reading before unbounded JSON accumulation and enforce serialized result<=64KiB. Use the exact C9.1 bounded {code} mappings for unexpected loader/store/runner failures as well as known errors; don't rethrow arbitrary exceptions as uncontrolled500 responses. The run POST currently discards result on replay; first acceptance returns202 {previewRunId,status}, matching replay returns200 existing status/result as C9.1 specifies. Keep active-admin and cross-owner checks on every method/status/cancel; ensure body/path inputs are strict. Keep fixture catalogue and model mode distinctions per C6.2/C9 rather than claiming four labels cover all named status/language outcomes.

Route tests must invoke actual handlers with injected service/transport: unauthorized/revoked, saved non-UUID identity, malformed and extra keys, unsupported response contract, oversized streamed body/result, cross-owner status/cancel, first/replay/conflict HTTP statuses, tool-test retrieval, and bounded503 on infrastructure failure. Assert zero execution/budget on rejected input. Use correct release and revision fixtures, not `{grant:{id:'grant'},manifest:{version:'fixture'}}` placeholders as accepted bundles.

### Evidence and resubmission gate

Implement R1–R4 within009's owned backend paths; do not implement017 screens or013 saved-source adapters. Publish typed ports with validated success/failure examples so017/013 can consume them without guessing. Replace the report's unsupported Redis/lifecycle deferral and map P01–P05 to actual tests with reserve/model/tool/history/result effects. Record preparation synchronization and nested dependency pin evidence, passing focused/type/lint/build/diff checks, and the full-suite baseline limitation accurately. No task-count minimum or live provider/Redis run is added. Commit/push the same implementation/report branches and resubmit for review. This parent overlay is published before handoff; normal preparation owns the next claim.


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
