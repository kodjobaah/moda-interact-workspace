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
enables:
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
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

### Proposed bounded behaviour to retain in that reconciliation

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
  Never cache errors, partial/unsupported outcomes or invalid payloads. TTL begins
  after successful fetch; record fetchedAt/expiresAt and reject expired/malformed
  entries. Do not offer stale-while-revalidate. Failed calls may count as demand but
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

## Work Items

- [ ] Close the readiness checkpoint and consume approved owner dependencies.
- [ ] Implement pure key/policy/eligibility helpers and Redis adapter with injected clock.
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

All are deliberately explicit: this is the final current implementation feature.
New owner-specific cache prerequisites, if required by the readiness checkpoint,
must be added reciprocally. Never depend on SYSTEM-TEST-001.

## Enables

- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

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
