---
id: ARCH-020-COMMERCE-004
architecture_id: ARCH-020
title: Authenticate MCP requests and resolve immutable grants
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 80
executor: null
claimed_at: null
attempt: 3
depends_on:
  - ARCH-020-COMMERCE-003
  - ARCH-020-SHARED-001
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-010
  - ARCH-020-COMMERCE-014
  - ARCH-020-COMMERCE-013
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-21
---

# Authenticate MCP requests and resolve immutable grants

## Architecture

ARCH-020. [Parent architecture](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).
Binding [implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md):
C4/C5/C7/C8/C9/C14/C16/C18 as applicable, and exact ownership/interfaces in **C19**.

## Objective

Own /api/mcp transport, assertion verification, durable ownership/grant reads and manifest/prompt/tool discovery. Inject definition execution through the C19 port.

## Context

This is the canonical narrowed definition from the 2026-09-21 task split, replacing
the former combined scope. No prior attempt or implementation is discarded. Normal
launcher/worktree/review policies apply. No task is claimed by this definition.

## Scope

Own /api/mcp transport, assertion verification, durable ownership/grant reads and manifest/prompt/tool discovery. Inject definition execution through the C19 port.

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

- [x] Implement the accepted001 Streamable HTTP profile, method/purpose matrix, request bounds and Origin rejection; no alternate endpoint.
- [x] Validate C5 JWT algorithm/key/issuer/audience/subject/expiry/environment and durable Conversation -> Recovery -> Shop ownership, turn/lease and current original-provenance permission.
- [x] Resolve candidate manifest, read/verify existing immutable grant, prompts and tool list. Background alone inserts grants; simulate its winner-write in transport fixtures.
- [x] Produce server-only AuthorizedToolCall context with pinned definition and effective C8 limits; dispatch to injected DefinitionExecutionPort. Never execute operation mappings or templates here.
- [x] Propagate typed C4/C5 failures and AbortSignal/deadline; return the C16 response contract/hash. Missing execution adapter is UNAVAILABLE, never a fake success.

## Interfaces / Contracts

Own `src/commerce/mcp/` and the existing /api/mcp entry. C19 AuthorizedToolCall/DefinitionExecutionPort separates004 transport from014 execution.013 installs the production014 adapter;004 acceptance uses a contract-faithful executor double.


## Dependencies

- ARCH-020-COMMERCE-003
- ARCH-020-SHARED-001

All listed prerequisites must be Complete and architect-accepted before a claim.
Use dedicated launcher worktrees and accepted source; do not launch enabled work.

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-013
- ARCH-020-COMMERCE-010
- ARCH-020-COMMERCE-014
- ARCH-020-SYSTEM-TEST-001
## Acceptance Criteria

- [x] M01: resolve vs execute matrix, malformed JWT/Origin/body and mismatched tenant/turn deny before executor calls.
- [x] M02: grant race fixture reads one winner; changed release/features never expand existing discovery; exact names/versions and zero-tools result are preserved.
- [x] M03: revocation across replicas and conflicting original-association bounds enforce C8 minima; newly added association cannot grant authority.
- [x] M04: pinned authorized call reaches the injected executor once with trusted context; ungranted/wrong revision reaches it zero times; execute failure is encoded by the accepted profile.

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

Implementation branch `task/ARCH-020-COMMERCE-004`, commit `c97a85be3a1561adca06eb03577dd84ad30ed306`:

- `package.json`, `package-lock.json`
- `app/api/mcp/route.ts`
- `src/commerce/mcp/authentication.ts`
- `src/commerce/mcp/ports.ts`
- `src/commerce/mcp/service.ts`
- `src/commerce/mcp/authorization.ts`
- `tests/mcp-service.test.ts`
- `tests/mcp-authorization.test.ts`
- `tests/mcp-compatibility.test.ts`
- `tests/auth-entrypoints.test.ts`

### Work Completed

Implemented the private `/api/mcp` POST transport with Origin/content/body bounds,
JSON-RPC validation, resolve/execute method-purpose authorization, RS256 JWT
verification, tenant/turn/grant/release/expiry checks, immutable manifest and
response-contract hash checks, bounded discovery, prompt retrieval, and
server-only `AuthorizedToolCall` dispatch through the injected
`DefinitionExecutionPort`. Missing runtime adapters fail closed as
`UNAVAILABLE`; execution results are schema-validated and encoded in the MCP
response contract. Deterministic fixtures cover deny-before-executor,
revocation, expiry, stale tenant/turn, exact pinned revision, malformed input,
origin rejection, and JWT verification. The stale entry-point test now asserts
that the required MCP route is private rather than absent.

Requirement-to-fixture matrix:

| Requirement | Fixture/test | Expected and observed effect |
| --- | --- | --- |
| M01 | `tests/mcp-service.test.ts`: resolve/execute matrix; origin, batch, params and argument bounds; JWT verifier | Resolve discovery succeeds, resolve execution and malformed/Origin inputs deny, executor calls remain zero, and RS256 issuer/audience/subject/kid/purpose/lifetime checks pass. |
| M02 | `tests/mcp-service.test.ts`: exact pinned revision, manifest contract hash, zero-tool fixture | Only the granted tool whose name/version/revision match the immutable definition is listed/callable; bad contract denies before discovery and zero-tool discovery remains empty. |
| M03 | `tests/mcp-service.test.ts`: tenant/turn mismatch, release mismatch, expiry and revocation mutations | Stale turn, wrong release, expired grant and revoked tool deny; no executor call occurs. Authorization is re-read for each request through the injected port. |
| M04 | `tests/mcp-service.test.ts`: pinned `tools/call` executor double and denied-call assertions | One authorized call reaches the executor with pinned grant/release context; denied or revoked calls reach it zero times; typed execution failures map to unavailable/error responses. |

### Validation Results

Agent-owned checks:

- `npm test -- --run tests/auth-entrypoints.test.ts tests/mcp-service.test.ts tests/mcp-compatibility.test.ts` -> passed, 3 files / 13 tests.
- `npm run lint` -> passed.
- `npm run typecheck` -> passed after the build regenerated Prisma Client.
- `npm run build` -> passed; Prisma Client generated from `database/prisma/schema.prisma`, Next.js compiled, and `/api/mcp` was included as a dynamic route.
- `npm test` -> 20 files passed, 150 tests passed; one Redis-backed test failed by timeout: `tests/discovery-limits.test.ts` requires `REDIS_URL` and timed out after 30 seconds. No MCP test failed.
- `git diff --check` -> passed.
- `git submodule status --recursive` -> database submodule at recorded SHA `5abfd87f57038bae515aaa09ec7c8db62adcfb98`.

Developer-owned live/integration validation remains pending: run
`REDIS_URL=<developer Redis> npm test -- --run tests/discovery-limits.test.ts`
and the live Background-signed assertion plus production execution-adapter/system
integration checks in the developer environment. Fixture tests do not prove live
issuer keys, network admission, Redis, database, provider, or deployment behavior.

### Deviations

The existing `tests/auth-entrypoints.test.ts` expected no `/api/mcp` route from a pre-task baseline; it was updated to assert the required private route. Full validation retains one unrelated Redis timeout as pending developer evidence.

### Assumptions

The accepted Shared commerce contracts and the recorded database submodule SHA are authoritative. The injected authorization/execution ports represent the C19 composition boundary; production adapter wiring remains with its owning task.

### Unresolved Issues

Live Redis-backed discovery validation is unavailable in this agent worktree and
must be run by the developer with configured infrastructure. No implementation
blocker remains for the bounded Commerce-004 scope.

### Architectural Concerns

None newly reported.

### Git / VCS

Status: Ready for Review. Attempt: 1. Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-004`, branch `task/ARCH-020-COMMERCE-004`, pushed commit `c97a85be3a1561adca06eb03577dd84ad30ed306`. Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-004`, branch `task/ARCH-020-COMMERCE-004`, based on pushed claim `1b1258f664eeb3f6c834d24f6fc68aeec17fb499`; this report update is the next parent task commit. The recursive database submodule remained at recorded SHA `5abfd87f57038bae515aaa09ec7c8db62adcfb98`. No parent service gitlink or main branch integration was performed.

### Attempt 2 Completion Update — 2026-09-21

The requested correction was applied in `tests/mcp-compatibility.test.ts`: the
MCP client's `result.content` is narrowed with `Array.isArray`, then the first
element is narrowed to an object with `type === 'text'` before asserting its
payload. This is the smallest type-safe fix for the SDK's `unknown` content
type; no production code changed for this correction.

Implementation commit `5ef60bd304e08b5b7a6099697bc73b5f55ff87ed` is pushed to
`task/ARCH-020-COMMERCE-004`. Validation from the implementation worktree
`/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-004`:

- `npm run typecheck` passed.
- `npm run build` passed; Prisma Client generated from
  `database/prisma/schema.prisma` and `/api/mcp` compiled as a dynamic route.
- `npm test` ran 23 files / 180 tests: 22 files and 179 tests passed; the
  unrelated Redis-backed `tests/discovery-limits.test.ts` timed out after 30s.
- `git diff --check` passed.

The Redis timeout remains pending developer validation with configured Redis;
the required command is `REDIS_URL=<developer Redis> npm test -- --run
tests/discovery-limits.test.ts`. Live Background-signed, provider, database,
and system integration evidence remains developer-owned and is not claimed by
fixture tests.

Parent task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-004`
is on `task/ARCH-020-COMMERCE-004`; its recorded recursive submodule evidence
includes Commerce `01c550c3e3f55dd23a4ecc9514c846bb88cf2067` and database
`9c6a4d8402a01840e2ea8dc18e89171f00564d29`. The task status is `review`,
`executor` and `claimed_at` are cleared, and no parent service gitlink or main
integration was performed.

### Attempt 3 Completion Update — 2026-09-21

Implementation commit `0411babc90182f41ad3f036096eb51427f128ac0` is pushed to
`task/ARCH-020-COMMERCE-004`. Attempt 3 addresses every retained A2-R1–A2-R3
review item within the task-owned MCP transport, authorization resolver and tests.

The resolver now retains all original capability associations, verifies their
pinned revision provenance and identity, validates C8 bounds, computes minima
across every surviving applicable original, and prevents newly added associations
from supplying authority. Current tool authorization is explicit: revoked tools
are omitted, while enabled granted tools require their exact definition and
authored name/version. Required prompt revisions and their JSON-encoded aggregate
are bounded; legitimate zero-tool discovery remains valid.

The production handler now uses a request-scoped pinned `McpServer` with
`WebStandardStreamableHTTPServerTransport`, JSON responses and no session. It
retains the resolve/execute purpose matrix, exact application parameters,
streaming 128 KiB input rejection, no-store responses and a 256 KiB final encoded
response bound. Malformed JSON, unsupported methods/protocol versions and invalid
notifications are protocol/input errors rather than infrastructure failures.
Assertion verifier construction enforces the fixed issuer, audience and subject,
one or two local keys, and the existing remote-key-header rejection.

Tool execution is raced against request cancellation and the smaller of the
ten-second budget or assertion expiry. A non-cooperative executor can no longer
hold the HTTP response open; late settlement is observed and discarded, timers
and listeners are removed, typed execution failures remain C4 results with
`isError`, and denied calls still reach the executor zero times.

Requirement-to-effect evidence for this attempt:

| Requirement | Fixture/test | Expected and observed effect |
| --- | --- | --- |
| M01 | `tests/mcp-service.test.ts` protocol, origin, streamed-body and purpose cases; `tests/mcp-compatibility.test.ts` real SDK client | Resolve discovery succeeds; execute-only methods, malformed JSON, invalid notifications/protocol, Origin and >128 KiB input fail before execution; the pinned client interoperates with the production handler. |
| M02 | `tests/mcp-authorization.test.ts` absent/malformed/mismatched definitions, prompt aggregate and zero-tool cases | Missing current or pinned records fail closed with typed availability/compatibility errors; escaped aggregate prompt content is bounded; legitimate zero-tool discovery stays empty. |
| M03 | duplicate original associations in both orders plus resolver-to-service execution/revocation fixture | Both orders produce `1/2` minima, removed/new provenance cannot restore authority, those limits reach the executor once, and current tool revocation removes the method with no additional execution. |
| M04 | ignored-abort deadline and typed-failure service cases | A never-settling executor yields a bounded `DEADLINE` result by assertion expiry, successful dispatch occurs once, and typed `NOT_FOUND` remains a C4 `isError` tool result. |

Agent-owned validation from the implementation worktree:

- Focused MCP suite: 3 files / 18 tests passed.
- Final escaped prompt regression: 1 file / 4 tests passed.
- `npm run typecheck`, `npm run lint`, `npm run build`, and `git diff --check` passed; the build generated Prisma Client and included `/api/mcp` as a dynamic route.
- Full `npm test`: 22/24 files and 196/199 tests passed. The known Redis-backed `tests/discovery-limits.test.ts` timed out without configured Redis. Two unrelated readiness child-process tests missed their setup barrier under the 24-worker full-suite load; an immediate isolated rerun passed all 10/10 readiness tests.

Developer-owned live validation remains unchanged: the Redis-backed discovery
case requires a configured `REDIS_URL`, and live Background-signed assertions,
production composition/provider calls and system integration remain outside this
fixture-only task validation. No live behavior is claimed.

Parent task status is `review`; `executor` and `claimed_at` are cleared. No
enabled task was started, no parent service gitlink or main integration was
performed, and the retained Architect Review below was not edited.

## Architect Review

### Changes Requested — Attempt 2 — 2026-09-21

**Current decision: Ready; Attempt 2 retained; executor/claimed_at null; not accepted.** Reviewed implementation `5ef60bd304e08b5b7a6099697bc73b5f55ff87ed` and parent report `5d54102bba4d0cc293658b2968e9545d686ec0a7`; remote task heads verified, dedicated worktrees clean. No implementation edit, new claim, downstream promotion, main integration or gitlink update. This decision supersedes earlier current-state wording.

Retain actual pinned prompt lookup, task-owned resolver, snapshot environment/domain checks, remote-key-header rejection, streaming body bound, initialized notification and real-handler SDK-client interoperability improvements. Independently ran the submitted MCP/resolver/interoperability suite: **12/12 passed**. `/tmp/c004-a2-review/{authorization,service}.test.ts` imports committed code:9 copied submitted tests pass and4 added regressions fail (duplicate association minima, absent pinned definition, malformed JSON503, deadline not settling ignored-abort executor). Diff checks passed. Typecheck/lint/build and full179/180 remain submitted evidence; no live Redis/provider/database validation was run. These are outstanding R1/R2/R4 behaviors, not scope amendments.

#### A2-R1 — P1 — Preserve every original association and required pinned record

Files: authorization.ts resolveAuthorizedSnapshot/CurrentCapabilityAssociation, ports.ts, service.ts availableTools and resolver tests. `new Map(...[association.key,association])` overwrites original associations sharing a capability. Reproduction with original enabled limits1/2 followed by3/10 returns3/10, violating the C8 minima requirement. Order also determines eligibility when duplicate rows disagree. The missing-definition test supplies an invalid object, not an absent map entry: an empty definitions map passes resolver and discovery silently returns no tools.

Replace key-to-single-row reduction with grouping that retains every original association. Compute eligibility from surviving permitted original provenance according to C8; take effective minima across ALL surviving original applicable bounds, plus the fixed platform ceiling. Newly added associations never supply authority. Preserve association identity/current source fields needed to distinguish originals rather than accepting last-write order. Validate finite integer bounds within accepted C8 ranges before use. Do not use disabled/non-surviving associations as fresh authority or let their ordering discard a surviving original.

For each currently authorized granted tool, require its exact pinned revision definition, matching authored name/version and immutable ownership; missing/mismatched records produce typed UNAVAILABLE/INCOMPATIBLE_VERSION, not silent omission. Deliberately revoked tools may be omitted. Add current tool enabled/revoked records to the trusted resolver input: enabledToolIds is currently inferred only from eligible capability membership and cannot express tool revocation while its capability stays enabled. Check required prompt revision presence/aggregate bounds similarly; retain legitimate zero-tool grants.

Tests: two original associations for the SAME capability in both orders yield1/2 minima; one removed original and one surviving original retain only permitted authority; new association cannot restore revoked authority; current tool disabled while capability remains enabled=>0 calls/omitted tool; absent map entry vs malformed definition tested separately; exact-name/version mismatch unavailable; legitimate zero tools remains empty. Exercise resolver -> actual service -> executor effect counters, not only direct hand-built snapshots. This completes existing M02/M03; no new provider or grant writer.

#### A2-R2 — P1 — Complete protocol/error and aggregate-bound corrections

Files: service.ts requestShape/handle/dispatch/response, authentication.ts config validation, compatibility/service tests. The handler remains a handwritten dispatcher despite R1 requesting the accepted request-scoped SDK server. The new happy-path real-handler SDK test is useful, but malformed JSON still falls into the generic503 catch. It also accepts unvalidated initialized/cancelled notification payloads, arbitrary initialize params and several extraneous resource-list/envelope fields. The code checks tool payload size before JSON-RPC/text encoding, not actual aggregate encoded output; resource/list/prompt responses have no common output bound. Prompt64,000 limit is per text, not bundle total.

Use the already-pinned McpServer/WebStandardStreamableHTTPServerTransport with request-scoped authenticated registrations as previously specified. Keep JSON-only/no-session profile and current true-handler client test. Let SDK perform protocol validation/error construction; retain explicit purpose/method and exact application parameter checks. Add malformed JSON/invalid notification/unsupported protocol and extraneous params cases; protocol input errors must not report infrastructure unavailable. Bound every final encoded response at256KiB and the complete selected prompt bundle at64,000 characters, including JSON escaping/wrappers. Preserve streaming128KiB input413 and no-store responses. Treat typed tool failures as C4 result/isError; framework/authentication errors retain their specified HTTP semantics.

Complete the outstanding authentication config guard from R2: fixed C5 issuer/subject/audience, configured public-key count1–2, and explicit rejection of forbidden remote-key references. Header rejection improved; config remains arbitrary and unbounded. Validate config at construction and test invalid fixed values/three keys without network calls. Keep legitimate two-key rotation and repeated signed assertions within an admitted turn.

Acceptance fixtures invoke actual production handler: malformed JSON yields protocol input error (the isolated test observes503); initialize/notifications validated; oversized escaped output rejected before sending; two allowed prompts individually under64k but aggregate over64k rejected; valid two-key rotation/invalid config; typed execution failure remains structured. No alternative endpoint or live deployment testing is added.

#### A2-R3 — P1 — Bound waiting, not only the abort signal

File: service.ts tools/call executor await. The timer aborts a child signal, but the handler still awaits execution unconditionally. A fake-clock test advances past10 seconds while an executor ignores abort: the HTTP promise remains pending until the fixture manually releases it. This is the exact ignored-signal case required by R4.

Race execution against a cancellation/deadline promise wired to the combined signal before invocation; that promise rejects/returns a bounded typed DEADLINE when the remaining window ends. Observe eventual executor rejection so it cannot become unhandled, discard any late resolution, and clean timer/listeners in finally. Retain pre-dispatch and post-result deadline guards plus shared request12/13 checks. A client disconnect must also settle the handler without waiting for a non-cooperative executor. The executor still receives abort and owns stopping its internal work;004 cannot claim the external operation was forcibly terminated.

Permanent fake-clock/barrier tests: never-settling executor=>handler settles by10s/assertion expiry; signal-aware executor sees abort; late resolve/reject cannot replace the deadline response or produce unhandled rejection; disconnect settles;0 executor on pre-expired/pre-aborted call; normal successful call executes once. Use the existing contract-faithful executor double; no014 implementation or paid/provider call is required.

### Resubmission

Implement A2-R1–A2-R3 within004-owned MCP files/tests, preserve working prompt/interop changes, and map each prior R1–R4 claim to actual effect evidence. Publish same implementation/report branch pair and return to review after focused/required checks. Live Redis and Background/provider integration remain developer-owned and are not blockers here. Parent overlay is committed/pushed before handoff; preparation owns the next attempt. No downstream task is promoted.


### Changes Requested — Attempt 1 — 2026-09-21

**Current decision: Ready; Attempt 1 retained; executor/claimed_at null; not accepted.** Reviewed implementation `c97a85be3a1561adca06eb03577dd84ad30ed306` and report `566ecd9f74cda640f7ae5281dfead9c47d1657c1`; both remote task heads verified and dedicated worktrees clean. No implementation edits, next claim, dependent promotion, main integration or gitlink update. This supersedes pre-implementation readiness wording below.

Independent submitted suite: **13/13 passed** across auth-entrypoints, mcp-service and mcp-compatibility. The compatibility test exercises a separate test-only SDK server, not createMcpService or the production route. Isolated `/tmp/c004-review/review.test.ts` imports the committed implementation:6 original service tests pass,4 new checks fail (initialized notification400, elapsed dispatch deadline still invokes executor, environment mismatch still invokes executor, malformed JSON503). The deadline case uses the submitted verifier double and past assertion expiry; it proves a missing dispatch guard, not a signature-verifier bypass. Diff check passed. Submitted full150/151, lint/typecheck/build remain reported evidence; no live Redis/provider/database/Background integration was executed.

#### R1 — P1 — Use the accepted SDK transport and test the real handler

Files: `src/commerce/mcp/service.ts`, `app/api/mcp/route.ts`, tests/mcp-service.test.ts and mcp-compatibility.test.ts. requestShape requires an id on every message, so the pinned client's `notifications/initialized` is rejected400. The compatibility suite passes only because it uses tests/fixtures/mcp-app's different SDK server. JSON.parse failure becomes503 and request.text consumes the entire body before checking64KiB; this is not a bounded reader or the C5 protocol-error contract.

Use the accepted COMMERCE-001 request-scoped McpServer/WebStandardStreamableHTTPServerTransport profile with sessionIdGenerator undefined and enableJsonResponse true. Register the authenticated resource/prompt/tool callbacks against the request's trusted context. Handle initialize/initialized notification/ping through the SDK, including202 notification acknowledgement and negotiated protocol validation. Keep POST only, GET/DELETE405, Origin rejection, no sessions/SSE/batches. Enforce exact params and bounded IDs/envelopes through SDK plus task-specific validation; unknown method/parse/schema failures must be protocol errors, not503 infrastructure failures.

Read streamed bytes incrementally and stop/cancel when C4 aggregate input128KiB is exceeded; return413 per C5. Validate the bounded JSON before dispatch. Bound serialized output256KiB and prompt bundle64,000 characters. Keep operation argument schema/size constraints independently. Do not use an arbitrary smaller HTTP bound as a replacement for the accepted contract. HTTP401/403 remain authentication/authority errors; business execution errors must be C4 structured results with isError, not unrelated RPC exceptions or HTTP503 for every failure.

Replace/extend compatibility test so the pinned Client connects through the same createMcpService transport used by /api/mcp, injecting verifier/authorization/executor only. Verify initialization notification, resource/list/read, prompt/get, tools/list/call, typed tool failure, unsupported method, malformed JSON, streamed413 and output bounds. Keep the old foundation fixture as historical coverage if useful; do not count it as this handler's interoperability evidence. Production missing composition remains fail-closed until013 supplies it.

#### R2 — P1 — Implement the task-owned grant/permission resolver

Files: `src/commerce/mcp/ports.ts`, new authorization/resolution module(s), service.snapshot/availableTools and focused resolver fixtures. McpAuthorizationPort currently returns a final arbitrary snapshot; no implementation reads durable Conversation -> Recovery -> Shop ownership, processing lease, existing-grant winner, original association provenance or C8 minima. Passing caller-fixture sets to currentlyGrantedTools cannot prove these decisions. M02 grant-race and M03 conflicting-association cases claimed by the report are absent.

Keep an injectable database/read port, but004 must implement the resolver that consumes authoritative ownership/turn/lease, active release, immutable grant and current association/permission records.013 wires the production data dependencies; it does not supply all of004's missing policy logic. Existing grant resolution returns its original manifest under both purposes; only no-grant resolve may produce a candidate. Background alone writes the grant. Validate original grant owner/release/manifest identities, supported versions/hash and exact original tool/revision provenance. Recompute current eligibility and effective C8 minima from surviving originally recorded associations; newly added association cannot expand authority. Disabled/revoked original associations remove access across replicas. Missing required pinned definition/schema must be typed unavailable, not silently omitted as an empty usable tool set.

Reject snapshot/assertion/deployment environment mismatch and invalid verified shop-domain/ownership relationships before execution. Schema-validate immutable grant data and definitions, not only manifest. Add deterministic two-reader/winner-write fixtures, current release changed after grant, removed original association, newly added association, conflicting original limits taking minima, stale lease/completed turn, wrong tenant, wrong environment and unavailable exact revision. Assert candidate/grant identity, discovered names and0 executor/provider effects for denials. Do not create a grant writer, execute mappings, or implement014 here. Correct M02/M03 report claims to name actual cases and effects.

Harden authentication.ts's config/header boundary to C5: fixed issuer/audience/subject values, at most2 configured public keys, and explicit rejection of jku/jwks header references even for a token signed by a configured key. The implementation currently ignores those references rather than rejecting them. Add valid/expired/future/wrong-environment/wrong-purpose and remote-key-header tests with signed fixtures; the existing JWT case only exercises a valid token and HS256 rejection. No network key lookup or credential use is needed.

#### R3 — P1 — Return actual pinned capability prompt text

Files: authorization snapshot/read ports, service prompts/list/get and resolver tests. prompts/get currently returns the string `commerce/<release>/<key>/<revision>` as the message content. That is the prompt identifier, not the authored immutable promptTemplate. Background cannot receive merchant capability behavior through this implementation.

Resolve the exact authorized capability revision's stored promptTemplate with the grant, return it through a typed bounded prompt field/map, and use the C5 exact prompt name as the key. prompts/list exposes only currently permitted original capabilities; prompts/get requires arguments={} and emits the actual stored text as literal content. Never execute/interpolate templates or replace them with names/placeholders. Revoked/missing content must fail closed; new publication does not change an existing grant's text. Enforce aggregate64,000-character prompt bounds and exact release/revision ownership.

Tests: unique authored text retrieved exactly, release changes leave original text unchanged, denied/revoked prompt does not leak text, wrong name/revision/extra arguments rejected, empty/oversized/missing source handled according to accepted capability schema. Test through the real SDK client, not just a fixture resource string.

#### R4 — P1 — Enforce deadline and abort at dispatch and completion

Files: service tools/call, ProviderBudget and executor fixture tests. deadlineAt is computed but never enforced before invoking runtime.execution.execute or before returning successful results. Only an executor that happens to call reserveProviderRequest notices expiry; CPU-only execution or a late resolver can run after the assertion deadline. Current fixtures even invoke the executor with a deadline in the past. ProviderBudget does not check request.signal.

Before dispatch check now>=deadlineAt or aborted and return the bounded C4 DEADLINE failure with0 executor calls. Use a child AbortController combined with request cancellation and a timer for the remaining <=10-second/assertion-expiry window; pass that signal to014 and every nested provider reservation. Reject late successful output after cancellation/deadline. Stop timers/listeners in finally. Bound waiting so an executor which ignores its signal cannot keep the request open indefinitely; discard its late result safely. Preserve typed C4 errors, exact original context, and shared12-request ceiling; do not retry or reset the budget in nested work.

Tests using fake clocks/barriers: valid assertion expires during authorization, pre-abort, abort/deadline during execution, executor ignores signal then resolves late, exact request12/13 boundary, current environment mismatch, typed executor error and successful once-only dispatch. Assert executor count, provider reservations, abort delivery and no success after expiry. Keep014 business validation out of004.

### Resubmission and scope boundary

Implement R1–R4 in004-owned MCP files and fixtures; update preparation/synchronization evidence and precise M01–M04 mapping. Commit/push the same implementation/report branches, then return to review. No new trusted commerce adapter work belongs in this task:015/006/016/007 and014 retain their separate ownership and normal preparation. The submitted “Starting: Implement trusted commerce adapters” progress line is not authorization to expand004. Parent overlay is published before handoff; no next attempt is claimed here. Live Background/Redis/provider integration remains developer-owned and is not the acceptance blocker.


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

## Architect readiness reconciliation — 2026-09-21

COMMERCE-003 Attempt 4 and SHARED-001 are architect-accepted Complete.
Promoted to Ready on the COMMERCE-003 acceptance branch; attempt and claim remain unchanged.
Normal task preparation owns materialisation, synchronization and the next claim.
