---
id: ARCH-045-SHARED-001
architecture_id: ARCH-045
title: Define Shopify consent-sync and canonical identity contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 20
executor: developer
claimed_at: 2026-10-21T17:59:48Z
attempt: 1
depends_on: []
enables:
  - ARCH-045-SHARED-002
created: 2026-10-20
updated: 2026-10-21
---
# Define Shopify consent synchronisation and canonical identity contracts

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** originally supplied as a portable definition and now materialised in the canonical parent task worktree; no implementation claim exists yet.

## Objective

Implement and test a **single published Shared implementation** containing (1) a minimal Shopify WhatsApp consent-state sync event for existing queues, (2) canonical E.164-equivalent exact-recipient phone helpers and portable golden vectors, and (3) validated Shopify numeric customer ID ↔ GraphQL Customer GID conversion. The sync event updates local consent via Background but can never request checkout reconciliation or start a recovery. `ARCH-045-SHARED-003` is Superseded and fully absorbed here; separate `ARCH-045-SHARED-002` publishes the accepted package.

## Context

Existing Shopify webhook/Background queues do not carry the WhatsApp consent-sync topic, and existing customer-phone helpers only trim/strip digits while Shopify privacy webhooks use numeric IDs versus GraphQL GIDs. All services should consume one versioned canonical event schema and one identity implementation, not independently reproduce them. Both sets of interfaces are defined and share `moda-interact-shared` ownership; this task consolidates the former SHARED-003 helper implementation into SHARED-001.

## Scope

**Shopify-to-Background event contract**
- Add the versioned `ShopifyWhatsAppConsentSyncJobV1Schema` (repository naming may vary), typed payload `{schemaVersion:1,shopId,shopifyCustomerId,deliveryId,triggeredAt}`, strict runtime validation, stable deterministic job ID and a **distinct** job name on an existing approved Shopify BullMQ queue. Exclude phone, consent Boolean, checkout key and recovery-wakeup fields; do not route it through checkout-created/updated parsing.
- Export producer/consumer runtime schemas and constants from published `@modainteract/moda-interact-shared` entrypoints; test malformed/replayed input, duplicate IDs, cross-shop identity and existing checkout event compatibility.

**Cross-platform exact recipient and Shopify customer identity**
- Implement one browser-safe/Node-safe canonical phone validator/normaliser that produces a verified E.164-equivalent recipient or a typed rejection. National-format numbers require **explicit verified country context**; do not infer permission or guess from locale. Provider `wa_id`/digits-only send addresses remain service-owned adapters.
- Implement validated numeric Shopify customer ID ↔ `gid://shopify/Customer/<numeric>` conversion/equality; reject malformed, zero/overflow and wrong-resource GIDs or arbitrary principal strings. Consumer services remain responsible for authenticated shop/tenant binding.
- Publish deterministic compatibility fixtures for UK national/international equivalence, ambiguity, extensions, rotation/reassigned phone, numeric webhook/GID conversion and invalid IDs. WooCommerce PHP code must pass matching vectors without importing Node implementation source.
- Keep only reusable codec, validator, identity/job helpers and tests in Shared; no Prisma, service secrets, API calls, business consent policy, provider sends or queue infrastructure creation.

## Out of Scope

- No new BullMQ queue, separate queue schema for Woo, HTTP handler, provider lookup, CustomerPhone write, recovery candidate, recovery retry job or source publication in this implementation task.

## Requirements

- [ ] Exactly one versioned consent-state synchronisation schema with deterministic job identity and no authority to create checkout recovery, send messages or carry consent decisions.
- [ ] Distinct job routing on existing queue infrastructure cannot be confused with checkout event parsing; Shopify ingress and Background use the same published runtime validator and version.
- [ ] Canonical phone identity is stable across explicitly scoped national/international representations and rejects unparseable/ambiguous input; shared fixtures cover Node writers/readers and Woo PHP compatibility.
- [ ] Numeric/GID Shopify customer identity conversion validates resource kind and format, but never substitutes for shop/customer authorisation.
- [ ] No independent copies of a cross-service event schema or identity helper, new queue, provider lookup, local consent policy or recovery wakeup.

## Work Items

- [ ] Add minimal versioned consent-sync schema, distinct existing-queue job name and deterministic ID generator; validate/reject extraneous consent/phone/recovery payload fields.
- [ ] Implement exact international phone normalisation/validation requiring verified country context when needed; publish typed failures and deterministic vectors.
- [ ] Implement strict Shopify numeric ID/GID conversion and customer-kind validation with fixtures for malformed, other-resource and out-of-range identities.
- [ ] Export browser/Node-safe entrypoints and compatibility fixtures from the approved package subpaths, without importing server-only code in browser exports; keep hashing primitives in a Node-only subpath when required.
- [ ] Add focused schema, idempotency, checkout queue compatibility, exact recipient, ID conversion, PHP fixture parity and export tests; preserve existing published contract compatibility.

## Interfaces / Contracts

**Owner:** `moda_shared` (`moda-interact-shared`), single implementation task `ARCH-045-SHARED-001`; release owner `ARCH-045-SHARED-002`.

- **Sync event:** `ShopifyWhatsAppConsentSyncJobV1Schema` (or repository-equivalent), `{schemaVersion:1,shopId,shopifyCustomerId,deliveryId,triggeredAt}`, deterministic job ID, existing queue with distinct job name. Producer `ARCH-045-SHOPIFY-001`, consumer `ARCH-045-BACKGROUND-003`. No checkout recovery side effect.
- **Canonical recipient helper:** Node Shopify/Background/Woo API callers import the published identity entrypoint; Woo PHP consumers test equivalent golden vectors.
- **Shopify ID helper:** numeric webhook IDs and GraphQL customer GIDs compare after strict validation; shop ownership is validated by consumers.
- **Publication:** `ARCH-045-SHARED-002` publishes this *one accepted implementation task*; no implementation in publication task.

## Dependencies

None

## Enables

- `ARCH-045-SHARED-002`

## Acceptance Criteria

- [ ] Event schema and deterministic ID reject malformed/PII/consent/recovery fields; existing checkout parser and event versions remain intact with distinct routing.
- [ ] A valid numeric Shopify customer ID and GraphQL Customer GID normalise consistently, while invalid/wrong-resource/out-of-scope identities fail validation without granting authorisation.
- [ ] Exact phone helpers produce the same canonical result under verified country context, reject ambiguous/invalid input, and have deterministic UK, international, extension, rotation, reused number and PHP parity vectors.
- [ ] Published entrypoint exports are runtime safe (no server-only secret or Node imports in browser-safe surfaces); all downstream consumers can import one shared contract without copying helpers.
- [ ] No new queue, consent-triggered recovery, provider lookup or consent business policy in Shared.

## Validation

- [ ] Repository-declared focused sync-event schema/job ID and checkout-queue compatibility tests.
- [ ] Repository-declared phone/Shopify ID codec fixture tests and PHP interoperability golden vectors.
- [ ] Entrypoint/export typecheck/build as applicable and `git diff --check`.

## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. Publication is separately owned by SHARED-002; stop after implementation review.

## Implementation Notes

Use existing Shopify Shared naming/style. Preserve published export compatibility. Stop at review: publication is a separate task.

Before claiming, use the deterministic `/moda-task` launcher and its **actual** prepared packet, read the task's complete current Architect Review, and verify task/dependency status in the developer's canonical workspace. Preserve `docs/decisions/**/_index.md` untouched until the developer explicitly closes the architecture documentation session. New runtime structured logging uses `@modainteract/moda-interact-shared/logging` where applicable. No source outside this task's owner repository may be changed unless explicitly authorised by the architecture.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-21T17:59:48Z. Attempt 0 review history is preserved below.

### Files Changed

None — not implemented.

### Work Completed

None.

### Validation Results

Not run; the supplied snapshot is not the developer's task worktree.

### Deviations

None.

### Assumptions

Use the 2026-10-20 snapshot for orientation; revalidate active code/configuration when the task is materially claimed. ARCH-045 does not impose a consent-expiry window; current Shopify consent and actual checkout eligibility are separate.

### Unresolved Issues

None recorded at definition time; report any discovered cross-repository dependency rather than implementing outside ownership.

### Architectural Concerns

None recorded at definition time.

## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

None.

### Reviewed Files

None — portable definition only.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.

## Developer Takeover and Materialisation Amendment — 2026-10-21

The developer explicitly invoked `/moda_developer_create ARCH-045-SHARED-001` for this ready agent-owned task. The portable definition was materialised on the canonical parent task branch. Execution ownership is transferred to the developer and completion requires an explicit developer decision after architect review. The logical repository owner remains `moda_shared`; task scope, dependencies, acceptance criteria and validation requirements are unchanged.
