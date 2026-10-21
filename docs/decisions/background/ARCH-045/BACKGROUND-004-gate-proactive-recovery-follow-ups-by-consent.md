---
id: ARCH-045-BACKGROUND-004
architecture_id: ARCH-045
title: Guard scheduled and merchant post-window recovery follow-ups
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-045-BACKGROUND-001
  - ARCH-045-BACKGROUND-002
  - ARCH-045-BACKGROUND-005
enables:
  - ARCH-045-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-21
---
# Guard scheduled and merchant post-window recovery follow-ups

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** portable definition, **not** materialised in a developer task worktree or committed/pushed; no execution claim exists.

## Objective

Apply the final shared Background consent guard to **all business-initiated WhatsApp recovery sends**, especially scheduled follow-ups, merchant post-window templates and first-send reentries, without changing the rules for legitimate customer-initiated in-window service replies.

## Context

`BACKGROUND-002` owns the pre-creation and initial reentry admission seam; `BACKGROUND-001` owns the injected current-state policy and fresh Shopify authority preflight. Scheduled sequence-two follow-ups and ARCH-040 human post-window templates use distinct existing dispatch/credit paths and must converge at a safe **final outbound permit**.

## Scope

- Integrate one reusable injected consent decision into scheduled no-response follow-ups, merchant-initiated post-24-hour recovery templates and all business-initiated first-send reentries. Inspect the existing recovery and ARCH-040 human-command dispatch paths rather than duplicating business/Meta logic.
- Perform a fresh Shopify GraphQL opt-in preflight for the immutable exact recipient **outside** the short SQL send-fence transaction; at the final database fence verify current CustomerPhone `GRANTED`, phone/recipient, consent revision, local no-contact revision and relevant existing checkout/attempt/ownership predicates. Provider unavailable or a later local revoke/STOP is a denial, not a permission cache hit.
- Keep existing `WhatsAppRecipientReachability` temporary delivery suppression separate from positive consent; do **not** require a newly invented permanent recipient STOP fence, source epoch or privacy-erasure table.
- Refuse or compensate denied sends without a Meta call, committed credit or permanently consumed sequence-two attempt. Preserve first-send billing compensation, single sequence-two claim ownership and existing HUMAN/AI control ordering; never issue a second recovery message because of duplicate final checking.
- Classify legitimate customer-initiated **in-window** human/free-form replies separately: they remain governed by existing Meta service-window and moderation rules, not incorrectly blocked as business-initiated recovery templates.
- Document the unavoidable time gap between provider preflight, SQL commit and Meta dispatch; use bounded freshness/revision checks and existing compensation, rather than claiming cross-system atomicity.

## Out of Scope

- No new billing/attempt tables, sequence-two slots, customer contact mode, Shopify cookie/CMP work, generic Meta sender-wide consent rule or new recovery scheduler.

## Requirements

- [ ] Every proactive follow-up, post-window template and first-send reentry has a consent check before reservation and a safe final pre-provider permit; no independent fallback path can bypass this policy.
- [ ] Shopify provider/Redis/network I/O is never executed inside the short SQL send-fence transaction; durable local revision/no-contact is checked under the applicable existing transaction/fence.
- [ ] Denial or source outage before dispatch produces no provider call, committed charge or lost unique sequence-two attempt; historical attempts and in-window service replies retain existing semantics.

## Work Items

- [ ] Identify the concrete scheduled, manual post-window, initial reentry and outbound fence entry points and inject BACKGROUND-001's shared policy.
- [ ] Add provider preflight outside and revision/no-contact predicate inside the existing final send-fence boundary.
- [ ] Add cross-path denial, preflight-to-fence revocation, billing compensation, sequence-two contention and permitted service-window reply tests.

## Interfaces / Contracts

Consumes `ARCH-045-BACKGROUND-001` policy, `ARCH-045-BACKGROUND-002` initial admission integration and `ARCH-045-BACKGROUND-005` durable CustomerPhone STOP, plus existing ARCH-040 outbound-send-fence, conversation control and recovery credit interfaces. No Shared queue addition.

## Dependencies

- `ARCH-045-BACKGROUND-001`
- `ARCH-045-BACKGROUND-002`
- `ARCH-045-BACKGROUND-005`

## Enables

- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Neither scheduled nor merchant-initiated post-window WhatsApp recovery may send after grant withdrawal, local STOP, merchant suppression, recipient change or a provider verification failure.
- [ ] First-send retries/resumptions and both sequence-two paths use the final permit, preserving the one allowed follow-up and billing/idempotency guarantees.
- [ ] The provider is not called and a credit/attempt is not irreversibly consumed when consent is denied before dispatch; valid customer-initiated in-window replies remain available under applicable rules.
- [ ] No provider HTTP/Redis in SQL transaction, source epoch, erasure fence or reachability consent schema is introduced.

## Validation

- [ ] Focused `recovery-outreach-follow-up-processor`, human post-window command dispatcher/evaluator, first-send capacity/suppression reentry and outbound-send-fence tests, including revocation between preflight and SQL fence.
- [ ] Concurrent human/automation sequence-two claim and compensation tests, separate legitimate in-window HUMAN_TEXT test, repository-declared checks and `git diff --check`.

## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. For publication task, do not rerun implementation validation.

## Implementation Notes

Audit the implementation state of concurrent ARCH-040 tasks before editing their owned paths. If the canonical worktree has diverged from the snapshot, update against current accepted API rather than overwriting its human command work. Avoid changing human-text messages into marketing sends.

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
