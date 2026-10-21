---
id: ARCH-045-BACKGROUND-001
architecture_id: ARCH-045
title: Synchronise and evaluate current Shopify phone consent
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-045-DATABASE-002
  - ARCH-045-SHARED-002
enables:
  - ARCH-045-BACKGROUND-002
  - ARCH-045-BACKGROUND-003
  - ARCH-045-BACKGROUND-004
  - ARCH-045-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-21
---
# Synchronise and evaluate current Shopify phone consent

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** portable definition, **not** materialised in a developer task worktree or committed/pushed; no execution claim exists.

## Objective

Provide one injected Shopify-native WhatsApp-consent reader and current-state synchroniser for an existing shop-owned customer and **exact active `CustomerPhone` recipient**. Both ordinary checkout admission and proactive sending consume this policy; consent-sync webhooks reuse its synchronisation operation.

## Context

Shopify is the source of truth for its native WhatsApp marketing opt-in. `ARCH-045-DATABASE-002` holds the current local `CustomerPhone` projection, not a separate Shopify consent table. `BACKGROUND-003` handles webhook job routing; `BACKGROUND-002` owns first recovery creation; `BACKGROUND-004` owns final proactive-send integration.

## Scope

- Implement injectable, typed provider operations for current Shopify WhatsApp consent and phone (`{shopId, shopifyCustomerId, recipient?}` or equivalent), with bounded timeout and distinct `ALLOWED`, `NOT_AUTHORISED`, `UNAVAILABLE` and `AMBIGUOUS` results. A GraphQL HTTP 200 response with `errors`, missing protected fields or an unusable recipient is **not** an affirmative grant.
- Resolve Shopify identity through the existing shop-owned `Customer` and Shared numeric/GID helper. Do **not** attach a Shopify customer ID to an existing Customer solely because its phone matches, or permit an unidentified guest to inherit a consent grant.
- Compare the checkout recipient with the Shopify-authoritative current phone using Shared canonical international-phone rules and an explicit country context where required. Use/update only the associated **active** `CustomerPhone`; a changed, missing or ambiguous phone cannot carry a previous number's grant.
- Project the provider's current state and observation timestamp monotonically onto CustomerPhone; newer revoke/unknown state and local customer STOP/merchant no-contact take precedence over stale positives. A sync event may refresh an already verified Customer/phone but must never create a checkout or recovery.
- Expose one injectable eligibility/snapshot interface used by `BACKGROUND-002/004`, including exact recipient, `customerPhoneId`, current consent revision and no-contact revision. Provide a **fresh Shopify preflight outside** the final short database send transaction; the final fence rechecks durable local revisions, not Shopify over the network under SQL locks.
- Test source failures, duplicates/reordering, shop isolation, changed phone, phone-only legacy merges, GraphQL access denial and preflight/revision races. Use the published Shared logging API without customer phone or payload logging.

## Out of Scope

- No checkout materialisation or merchant notices, consent-event worker routing, new consent/identity/erasure table, generic customer-identity redesign, recipient-reachability schema change, or consent-triggered checkout queue.

## Requirements

- [ ] A matching current Shopify-native `SUBSCRIBED` decision for the correct existing Shopify customer and exact recipient is necessary for a positive result; unknown, revoked, wrong-number, ambiguous and unavailable states fail closed.
- [ ] Phone equality is not proof of Shopify customer identity or consent. Local STOP and merchant suppression cannot be cleared by a delayed native grant.
- [ ] The current-state synchroniser and fresh-provider preflight are reusable by both normal admission and proactive dispatch without duplicated GraphQL/parsing logic.
- [ ] Customer privacy erasure implementation remains outside ARCH-045-DATABASE-002; existing customer lifecycle checks are respected, not replaced by a new fence.

## Work Items

- [ ] Implement the injectable Shopify consent adapter and one exact-recipient CustomerPhone selector/synchroniser.
- [ ] Expose a typed snapshot/fresh-preflight policy for admission and final dispatch with local revision/no-contact precedence.
- [ ] Add focused identity, provider failure, timestamp ordering, STOP, phone rotation and send-race tests.

## Interfaces / Contracts

Consumes `ARCH-045-DATABASE-002` current CustomerPhone schema and published `ARCH-045-SHARED-001/002` identity helpers. `BACKGROUND-003` invokes its sync operation; `BACKGROUND-002/004` inject its eligibility/preflight policy. No new inter-service contract or queue.

## Dependencies

- `ARCH-045-DATABASE-002`
- `ARCH-045-SHARED-002`

## Enables

- `ARCH-045-BACKGROUND-002`
- `ARCH-045-BACKGROUND-003`
- `ARCH-045-BACKGROUND-004`
- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Verified native consent is projected to the correct tenant-scoped active CustomerPhone; newer revocation/local STOP never regresses due to stale synchronisation.
- [ ] No mismatched, unidentified or changed recipient is considered authorised by phone equality alone; no recovery is created by this reader/synchroniser.
- [ ] Provider errors, absent fields, ambiguous identities and stale preflight results cannot authorise a proactive send; no provider HTTP/Redis I/O occurs inside the SQL send fence.

## Validation

- [ ] Focused GraphQL provider and DB-backed CustomerPhone tests for subscribed/revoked/unknown, HTTP-200 GraphQL errors, shop/customer-ID conversion, UK/international phone variants, ambiguous identity, changed phone, duplicate/out-of-order observations, STOP and provider timeouts.
- [ ] Injected preflight and concurrent local-revision/final-fence tests; run repository-declared build/checks and `git diff --check`.

## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. For publication task, do not rerun implementation validation.

## Implementation Notes

Exact Shopify customer GID must be constructed only from a validated shop-linked customer identifier. Do not use a recovery phone number to search for another customer. Keep this shared across Background admission paths by dependency injection, not copy-pasted GraphQL calls.

Before claiming, use the deterministic `/moda-task` launcher and its **actual** prepared packet, read the task's complete current Architect Review, and verify task/dependency status in the developer's canonical workspace. Preserve `docs/decisions/**/_index.md` untouched until the developer explicitly closes the architecture documentation session. New runtime structured logging uses `@modainteract/moda-interact-shared/logging` where applicable. No source outside this task's owner repository may be changed unless explicitly authorised by the architecture.

## Completion Report

### Status

Not Started — external portable definition, not materialised.

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
