---
id: ARCH-020-COMMERCE-012
architecture_id: ARCH-020
title: Add frequency-based tool-result caching
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 195
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-BACKGROUND-001
  - ARCH-020-BACKGROUND-002
  - ARCH-020-COMMERCE-001
  - ARCH-020-COMMERCE-002
  - ARCH-020-COMMERCE-003
  - ARCH-020-COMMERCE-004
  - ARCH-020-COMMERCE-005
  - ARCH-020-COMMERCE-006
  - ARCH-020-COMMERCE-007
  - ARCH-020-COMMERCE-008
  - ARCH-020-COMMERCE-009
  - ARCH-020-COMMERCE-010
  - ARCH-020-COMMERCE-011
  - ARCH-020-DATABASE-001
  - ARCH-020-GATEWAY-001
  - ARCH-020-GATEWAY-002
  - ARCH-020-SHARED-001
  - ARCH-020-SHOPIFY-001
  - ARCH-020-COMMERCE-013
  - ARCH-020-COMMERCE-014
  - ARCH-020-COMMERCE-015
  - ARCH-020-COMMERCE-016
  - ARCH-020-COMMERCE-017
  - ARCH-020-COMMERCE-018
  - ARCH-020-COMMERCE-019
enables:
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-21
---

# Add frequency-based tool-result caching

## Architecture

ARCH-020. Parent: [CommerceAgent Studio](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).
Coordinator: moda_architect. Follow the implementation handoff and binding C4–C7,
C9–C11, C14 and C16; caching never changes their authorization/grounding contracts.

## Objective

Reduce repeated eligible read calls through existing Redis when identical authorized
calls become frequent. Keep caching disabled initially. Deliver after the current
core implementation and before terminal system validation.

## Context

Initial task definition requested by the developer. This reserves the final
implementation feature; no caching code, new schema, package release or infrastructure
change is claimed. Frequency measures popularity, not permission or freshness.

## Scope

Commerce cache admission/lookup/storage, frequency tracking, exact keying, eligibility,
Studio tool-policy controls and isolated fixtures. Include Commerce-side metrics and
documentation. Use existing Redis; PostgreSQL remains definition authority.

## Out of Scope

Model-response caching, conversation/history caching, writes/mutations, personalized
customer data, merchant inference, permission caching, new Redis deployment,
automatic cache-policy tuning, global Redis configuration changes, unrelated code,
and edits to Shared/Database/Background/Gateway implementation repositories.

## Requirements

### Before promotion to Ready

The architect must reconcile this initial definition against the implemented tool
contracts and authorize the exact policy storage/API integration. Required policy
shape is {mode:DISABLED|FREQUENCY,threshold,windowSeconds,ttlSeconds}; specify strict
wire values and persistence location before implementation. Do not insert an unknown
cachePolicy field into the existing strict tool-definition schema or assume existing
Shared validators accept it. If persistence or Shared exports need changes, define
owner-specific prerequisite tasks and consume their accepted integrated/published
versions. Do not reopen completed tasks solely to add caching or bypass repository
ownership. Extend the exact U06/U14 page specs before promotion. This checkpoint is
required in addition to Complete dependencies; the initial definition is not Ready.

### Binding runtime behavior (policy storage still requires the readiness checkpoint)

- Policy belongs to a published tool revision and is disabled by default; enabled
  example is threshold=3, windowSeconds=60, ttlSeconds=30. Bounds: threshold integer
  2..100, windowSeconds integer 1..3600, ttlSeconds integer 1..300. Operation-specific
  freshness ceilings may lower TTL or forbid caching entirely. No unknown modes.
- Only execution types explicitly certified by Commerce as public, non-personalized,
  read-only and safe for bounded staleness may opt in. Unknown/custom policy operations
  are ineligible by default. Never cache basket/recovery/customer state, discount
  eligibility/evidence or final offer revalidation. Cached catalogue facts do not
  constitute current stock/price guarantees. Return appropriate freshness metadata.
- Authenticate and validate tenant, original grant membership, current revocation,
  arguments and eligibility before both counters and cache lookup. No denial may
  become a hit. Validation/final-response/offer checks remain unchanged.
- Identity includes environment, shopId, exact tool revision/definition hash,
  published cache policy, canonical validated arguments and every execution context
  value that affects the result (including locale/currency when applicable). Use
  RFC8785 canonical JSON and SHA-256; a tool with undeclared contextual inputs is
  ineligible. Never use tool name or phone number alone. Cross-shop sharing is forbidden.
- Namespace counters/results separately under moda:commerce:tool-cache:v1; no raw
  arguments/customer data in keys/logs. Preview uses a separate namespace and fixtures.
- Count each authorized eligible execution request once. Use an atomic Redis counter
  with TTL established on the first request, never extended by subsequent hits: this
  is a fixed window starting with that request, not an unspecified rolling window.
  Before threshold, execute normally without storing. The threshold-reaching request
  executes normally and stores its validated successful result. Later requests may
  hit until the independent result TTL expires; hits never extend result lifetime.
  Redis atomicity must ensure simultaneous increments do not lose counts/expiry.
- Cache only validated successful results within a 64KiB serialized-entry ceiling.
  Never cache errors, partial/unsupported outcomes or invalid payloads. Set fetchedAt when a fresh successful provider result is obtained and
  expiresAt=fetchedAt+effectiveTtlMs; insertion uses only the remaining lifetime.
  Record both timestamps and reject expired/malformed entries. Do not offer stale-while-revalidate. Failed calls may count as demand but
  never populate a result. No background refresh or retry introduced by caching.
- To keep v1 simple, concurrent misses may execute more than once; no distributed
  lock or promise of single-flight. Each remains within existing execution budgets.
- Bound Redis operations to 100ms each within the existing turn deadline. On timeout,
  unavailability or malformed entry, execute normally without automatic retries or
  caching; no failure may bypass the existing Shopify/concurrency/usage safeguards.
- Cache hits consume one tool-call budget slot and do not generate a synthetic Shopify
  request. Preserve existing billing rules; do not invent new merchant pricing.
- Use approved observability APIs for hit/miss/bypass/error/admission outcomes and
  saved upstream calls. No high-cardinality keys/shop IDs/arguments as metric labels.


### Exact call identity: separate frequency counter per equivalent request

Frequency is NOT a global count, a count per tool name alone or a measure of
concurrent execution. Sequential matching requests within the fixed window count.
Each different identity has its own counter AND cached result. Use this exact
key material after authorization, grant/revocation, schema validation, defaults and
server context resolution:

```text
{
  keyVersion: 1,
  environment,
  scope: {purpose: "live"}
      OR {purpose: "preview", adminId, simulationId},
  shopId,
  toolId,
  toolRevisionId,
  definitionHash,
  policy: {mode: "FREQUENCY", threshold, windowSeconds, ttlSeconds},
  executorVersion,
  arguments: validatedArguments,
  context: {shopDomain, locale, currency, bindings}
}
```

IDs, definitionHash and executorVersion come from the actual pinned definition and
installed adapter. The immutable policy belongs to that same revision; use neither
latest policy nor current active release as a substitute. shopDomain is the verified
canonical domain. locale/currency are resolved canonical values or explicit null
when the adapter does not use them. bindings is the strict declared map of all
other server-resolved values affecting this operation's result, or {} when none.
Personal/customer/basket-dependent calls remain INELIGIBLE even if their IDs could
be added to the key. Undeclared result-affecting context makes a tool ineligible.
Preview simulationId is server-issued and changes on Reset; enforce admin ownership.

Compute `digest = SHA256(UTF8(canonicalJson(material, "utf16")))`, lower-case hex,
using the accepted Shared canonical encoder (RFC8785 key order), not a second JSON
serializer. Object property order must not change the digest; array order and string
case do. Do not trim/lowercase queries, reorder arrays or coerce decimal strings
beyond the declared input schema/default behavior. Exclude request UUID, JSON-RPC
id, traceId, conversationId, inboundVersion and grantId: those are checked for
permission but must not prevent reuse of certified public facts across otherwise
equivalent calls in the SAME shop. There is no cross-shop sharing.

Redis keys, with braces literally enclosing the digest to keep related keys in one
Redis Cluster hash slot:

- `moda:commerce:tool-cache:v1:live:{<digest>}:frequency`
- `moda:commerce:tool-cache:v1:live:{<digest>}:result`
- Preview replaces `live` with `preview`; its material also includes admin/simulation.

Never put raw arguments, customer data or tokens in keys/logs. This digest is a
**cache identity**, not a command idempotency key.

### Required r1/r1/r2 example

Use one shop, revision, policy threshold=3/windowSeconds=60/ttlSeconds=30 and equal
context. r1 means this exact tool with `{query:"red shoes"}`; r2 means the same tool
with `{query:"blue shoes"}`. All requests below arrive within the same60-second
window. Here the first three fetches complete before the next request arrives:

| Incoming request | Red-shoes counter | Blue-shoes counter | Required action |
|---|---:|---:|---|
| r1 | 1 | absent | Fetch red shoes; do not store |
| r1 | 2 | absent | Fetch red shoes; do not store |
| r2 | 2 | 1 | Fetch blue shoes; do not store |
| r1 | 3 | 1 | Fetch red shoes; store only a validated eligible success |
| r1, after that fill and before expiry | 4 | 1 | Return red-shoes cache hit; no provider request |

After r1,r1,r2, NEITHER identity qualifies for caching. Three different arguments
produce three counters of1, not a counter of3. Different shops/revisions/context
also remain separate. Tests must assert keys, stored entries and provider counts,
not simply the total request count. This fixture must pass for sequential requests;
concurrency is not required to meet the threshold.

### Counting, retries and idempotency

One admitted server execution increments its identity's frequency once. Place the
increment at a single dispatch boundary; retries/pagination/internal provider reads
inside that execution never increment again. Calls that fail provider execution
may still count as demand, but errors/partial/unsupported results never populate.
Denied, invalid, disabled and ineligible calls neither increment nor look up results.

Do not add an execution-id header or alter tools/call. A new Background request
counts again, even if it is a transport retry with identical arguments. Neither
JSON-RPC id nor traceId is treated as a durable logical-call identifier. This is
explicit best-effort popularity accounting, not distinct-user/question counting
or exactly-once execution. It must not affect billing/reservations/send deduplication.

Redis counter/result operations have no automatic retries or offline queued replay.
A counter timeout may have incremented Redis; do not try again or pretend it did
not happen. For that request execute normally and skip cache insertion. A timed-out
insertion may have succeeded; return the already fetched result and do not retry.
No caching failure triggers an extra upstream call after one already succeeded.

For Studio draft saves/publication, the idempotency key remains C7's client-generated
opaque CUID `operationId`, persisted as `CommerceAuditEvent.id`. One intentional
mutation creates one ID BEFORE dispatch; double click, network retry and unknown
outcome reconciliation retain the same ID and payload. Changed actor/action/payload
with that ID conflicts. Save, publish and activate use distinct IDs. Do not use the
cache digest as a write idempotency key or bypass CAS checks. Any future policy
storage action must adopt this same contract at the readiness checkpoint.

### Atomic counting, concurrent fills and independent expiry

1. After eligibility/authorization checks, atomically increment this identity's
   frequency with an injected Redis script. On first creation set expiry to exactly
   windowSeconds; later increments never extend it. Counter increments/readback/first
   expiry are one atomic operation, not separate INCR then EXPIRE commands.
2. Look up only this identity's result. A validated unexpired result may be served
   regardless of whether the frequency window just reset. Count the hit once, but
   never extend result TTL or rewrite observation timestamps. Counter expiry does
   not invalidate an independently live result.
3. On a miss, fetch normally. Counter value returned for THIS request determines
   admission: below threshold never stores, even if another concurrent request later
   crosses it. At or above threshold may store a validated eligible success.
4. Store with atomic `SET resultKey entry NX PX remainingMs`. First successful fill
   wins; a losing fill cannot overwrite or extend an existing entry. No single-flight
   lock, blocking wait or background refresh. Multiple simultaneous misses may each
   call the provider, with the existing per-call budgets still enforced.
5. effectiveTtlMs is1000*min(policy.ttlSeconds, adapter freshness ceiling). Compute
   remainingMs=expiresAt-now immediately before insertion; skip if <=0. Never start
   another full TTL when delayed validation or a losing concurrent fetch finishes.
   An old slow fetch can fill an expired slot only if ITS result is still within its
   own original freshness lifetime. No re-stamping as newly fetched data.
6. Cache entry is strict `{version:1,digest,fetchedAt,expiresAt,result}` with epoch-ms
   integer timestamps. Validate the whole successful result against the operation
   schema on both store/read; maximum65,536 UTF-8 bytes for the entire entry. Check
   digest match, fetchedAt<=now<expiresAt, lifespan<=effectiveTtlMs and positive Redis
   TTL. Errors, malformed timestamps, missing expiry or oversize entries are bypasses.
   Never delete/overwrite a possibly replaced entry using an unchecked DEL.
7. Counter/result expiry are independent. If result expired while the counter is
   still >=threshold, next successful fetch can fill it again. If both expired,
   restart at1 and wait for threshold. TTLs never slide on reads. No stale serving.
8. Redis operations each have a100ms ceiling and share the remaining tool deadline.
   If Redis fails/times out or an entry is malformed, bypass caching for that request,
   perform at most the normal tool execution and skip further cache operations.
   Preserve admission/permission checks and cancellation; caching adds no retries.

### Mandatory implementation fixtures

- K01: the exact sequential r1/r1/r2/r1/r1 table above; provider calls=4, one result
  key populated, blue count remains1. Assert separate keys after the first3 requests.
- K02: permuted object keys match; changed arguments/array order/shop/revision/policy/
  environment/executor/context produce separate identities. Defaults normalize only
  as the declared schema specifies. Unknown contextual dependency bypasses caching.
- K03: concurrent increments maintain exact counts and fixed first-request TTL;
  requests below threshold do not store after a late completion.
- K04: concurrent threshold misses may fetch twice; the first successful NX fill
  remains unchanged, including timestamps/TTL, when the second finishes.
- K05: frequency expiry with live result still hits; result expiry with live hot
  counter refills; expiry of both restarts cold. Boundary now==expiresAt is a miss.
- K06: internal provider retries count once; two separate identical inbound requests
  count twice. Redis uncertainty causes no increment retry or extra upstream fetch.
- K07: changed permission is checked before any hit; malformed/oversize/expired data,
  unknown/ineligible operation and evidence/customer/basket results cannot populate.
- K08: same Studio operationId/payload has one write/audit; mismatch conflicts;
  intentional new save gets a new ID. Runtime cache digest is never the audit ID.
- K09: preview reset/admin/environment isolates counters/results; no live-provider
  call or live cache entry is touched by the simulation.

Execute real Redis Lua/TTL/NX fixtures in an isolated test instance as required by
repository validation policy; a fake EVAL returning constants or source-text checks
cannot establish atomicity. Provide exact command and observed outcomes separately
from pure fake-clock/key tests. No production Redis or paid provider is required.

## Work Items

- [ ] Close the readiness checkpoint and consume approved owner dependencies.
- [ ] Implement the exact identity/key, counting, NX fill and expiry contracts below
  with an injected clock; satisfy K01–K09. No global or tool-name-only counter.
- [ ] Integrate authorization-first lookup and threshold-based store into Commerce tool dispatch.
- [ ] Add U06 cache-policy controls (Disabled/Frequency; X/Y/Z values, units, bounds,
  eligibility explanation) in a new tool draft; publish changes as a new revision.
  Existing grants cannot silently adopt a new policy. U14 runs fixture calls and
  shows counter/admission/hit/miss/freshness outcomes with a resettable synthetic clock.
- [ ] Apply synchronous duplicate-action guards and existing server replay protection
  to policy edits/publication. Read-only simulations remain isolated from production.
- [ ] Add bounded operational metrics, failure behaviour documentation and fixtures.

## Interfaces / Contracts

Final persistence/API/schema ownership is intentionally unresolved in this initial
backlog definition and must be recorded before Ready. Runtime safety and bounded
semantics above are binding inputs. Redis availability never becomes an authorization
or correctness dependency. Do not expose cache controls as model tool arguments.

## Dependencies

- ARCH-020-BACKGROUND-001
- ARCH-020-BACKGROUND-002
- ARCH-020-COMMERCE-001
- ARCH-020-COMMERCE-002
- ARCH-020-COMMERCE-003
- ARCH-020-COMMERCE-004
- ARCH-020-COMMERCE-005
- ARCH-020-COMMERCE-006
- ARCH-020-COMMERCE-007
- ARCH-020-COMMERCE-008
- ARCH-020-COMMERCE-009
- ARCH-020-COMMERCE-010
- ARCH-020-COMMERCE-011
- ARCH-020-DATABASE-001
- ARCH-020-GATEWAY-001
- ARCH-020-GATEWAY-002
- ARCH-020-SHARED-001
- ARCH-020-SHOPIFY-001
- ARCH-020-COMMERCE-013
- ARCH-020-COMMERCE-014
- ARCH-020-COMMERCE-015
- ARCH-020-COMMERCE-016
- ARCH-020-COMMERCE-017
- ARCH-020-COMMERCE-018
- ARCH-020-COMMERCE-019

All dependencies must be Complete and architect-accepted before execution.

## Enables

- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] K01–K09 pass with explicit counter/key/TTL/upstream/write counts. In particular,
  r1,r1,r2 yields independent counts2/1 and no cache fill at threshold3.

- [ ] Disabled tools execute every call; below-threshold calls do not store; threshold
  call stores only validated success; subsequent identical calls hit before expiry.
- [ ] Tests cover window/result expiry independently, threshold races, non-sliding TTL,
  changed shop/arguments/revision/locale/currency, malformed/oversize results and Redis loss.
- [ ] Revoked/ungranted requests cannot hit or populate; protected freshness operations
  always execute fresh. Existing conversation policy pins survive new publication.
- [ ] U06 edit/validate/publish and U14 simulation flows meet approved exact page spec,
  role permissions, replay and double-click requirements.
- [ ] No model call, WhatsApp send, production customer payload or policy decision is cached.

## Validation

Use declared package scripts and deterministic Redis/clock fixtures. Assert actual
upstream call counts, key isolation and stored TTLs, not just returned values. Compare
cache-disabled behaviour to the accepted baseline. Record exact commands/results;
live load/provider validation remains developer-owned under workspace policy.

## Stop Condition

Submit scoped implementation/report for architect review; do not mark own task
Complete or launch the terminal system test. No production enablement by default.

## Implementation Notes

Definition authored on main by the developer's established review workflow. Execution
uses the normal moda-task launcher, dedicated mirrored task worktrees and repository
ownership/validation policies. Do not claim an attempt while prerequisites or the
explicit policy-contract checkpoint remain unresolved.

## Completion Report

Not Started. No implementation, validation, package publication or deployment claimed.

## Architect Review

Initial backlog definition only. Pending prerequisite completion and policy storage/API
and UI reconciliation before Ready. Review scope includes safety eligibility and all
cross-repository dependencies; no implementation acceptance is implied.
