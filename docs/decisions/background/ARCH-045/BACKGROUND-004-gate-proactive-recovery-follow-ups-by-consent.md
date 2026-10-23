---
id: ARCH-045-BACKGROUND-004
architecture_id: ARCH-045
title: Guard scheduled and merchant post-window recovery follow-ups
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 35
executor: developer
claimed_at: 2026-10-23T13:20:29Z
attempt: 1
depends_on:
  - ARCH-045-BACKGROUND-001
  - ARCH-045-BACKGROUND-002
  - ARCH-045-BACKGROUND-005
enables:
  - ARCH-045-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-23
---
# Guard scheduled and merchant post-window recovery follow-ups

## Developer Ownership Amendment

On 2026-10-23, `/moda_developer_create ARCH-045-BACKGROUND-004` was invoked
while this task was ready and agent-owned. This is an explicit developer
takeover. `execution_mode` and `completion_mode` are now `developer`;
`assigned_agent: moda_background`, repository ownership, dependencies, scope
and acceptance criteria are unchanged. The task remains at Attempt 0 until
canonical preparation claims Attempt 1.

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** materialised and published on parent branch `task/ARCH-045-BACKGROUND-004` during ARCH-045 dependency-frontier reconciliation after BACKGROUND-001, BACKGROUND-002 and BACKGROUND-005 were verified complete. The task is dependency-ready; no implementation execution claim exists.

## Objective

Apply the final shared Background consent guard to **all business-initiated WhatsApp recovery sends**, especially scheduled follow-ups, merchant post-window templates and first-send reentries, while also enforcing a Customer STOP hard prohibition across **all** outbound WhatsApp sends, including otherwise legitimate in-window service replies.

## Context

`BACKGROUND-002` owns the pre-creation and initial reentry admission seam; `BACKGROUND-001` owns the current CustomerPhone snapshot policy; live Shopify verification belongs to each new-checkout admission in BACKGROUND-002, not every subsequent send. Scheduled sequence-two follow-ups and ARCH-040 human post-window templates use distinct existing dispatch/credit paths and must converge at a safe **final outbound permit**.

## Scope

- Integrate one reusable injected consent decision into scheduled no-response follow-ups, merchant-initiated post-24-hour recovery templates and all business-initiated first-send reentries. Inspect the existing recovery and ARCH-040 human-command dispatch paths rather than duplicating business/Meta logic.
- For subsequent recovery messages, call only `ShopifyWhatsAppConsentService.evaluateStoredRecipient()` (database-backed, **no Shopify GraphQL request**). At the final short database fence verify the exact `CustomerPhone` `GRANTED` state, recipient, current consent revision, no-contact revision and existing checkout/attempt/control predicates. Local revoked/STOP, merchant suppression or unavailable database state denies sending.
- Keep existing `WhatsAppRecipientReachability` temporary delivery suppression separate from positive consent; do **not** require a newly invented permanent recipient STOP fence, source epoch or privacy-erasure table.
- Refuse or compensate denied sends without a Meta call, committed credit or permanently consumed sequence-two attempt. Preserve first-send billing compensation, single sequence-two claim ownership and existing HUMAN/AI control ordering; never issue a second recovery message because of duplicate final checking.
- Classify legitimate customer-initiated **in-window** human/free-form replies separately for Meta template/service-window purposes, but **block delivery if an applicable `CUSTOMER_STOP` exists**. Never interpret a service-window exemption as permission to contact a stopped recipient; apply the STOP predicate at the shared final outbound boundary to automated, human, queued and retrying messages.
- Treat **all business-initiated abandoned-cart/basket reminders** (first contact, automated reminder, sequence-two follow-up and merchant post-window recovery template) as **Marketing**. Verify the selected approved Meta template's actual Marketing category using trusted provider/template approval information; `WhatsAppTemplateVariant.purpose = checkout-recovery` and `status = APPROVED` alone are not evidence of Meta category in the inspected schema. Reject unknown, Utility or Authentication classifications without send/credit; if the existing template catalogue cannot supply trustworthy category evidence, report the precise ownership/contract gap to `moda_architect` rather than changing DATABASE-002 or silently passing the check.
- Document the unavoidable time gap between stored-state fence, SQL commit and Meta dispatch; use short revision checks and existing compensation rather than claiming cross-system atomicity. Shopify is queried anew at each **new checkout**, not before every follow-up.

## Out of Scope

- No new billing/attempt tables, sequence-two slots, customer contact mode, Shopify cookie/CMP work, generic Meta sender-wide consent rule or new recovery scheduler.

## Requirements

- [ ] Every proactive follow-up, post-window template and first-send reentry has a consent check before reservation and a safe final pre-provider permit; **every** outbound path also checks the authoritative CustomerPhone STOP flag, including in-window AI/HUMAN replies. No independent fallback can bypass STOP.
- [ ] The final consent check uses **stored CustomerPhone** only; no Shopify API call occurs on follow-up/re-entry dispatch, and no Redis/network I/O is introduced inside the short SQL fence.
- [ ] Denial or source outage before dispatch produces no provider call, committed charge or lost unique sequence-two attempt; historical attempts retain existing semantics; valid in-window service replies remain distinct from Marketing but are suppressed when STOP is active.

## Work Items

- [ ] Identify the concrete scheduled, manual post-window, initial reentry and outbound fence entry points and inject BACKGROUND-001's shared policy.
- [ ] Inject the database-only stored recipient decision and revision/no-contact predicates into the existing final send-fence boundary, without a Shopify preflight for follow-ups.
- [ ] Add cross-path denial, stored-read-to-fence local revocation, billing compensation, sequence-two contention and permitted service-window reply tests.

## Interfaces / Contracts

Consumes `ARCH-045-BACKGROUND-001` policy, `ARCH-045-BACKGROUND-002` initial admission integration and `ARCH-045-BACKGROUND-005` durable CustomerPhone STOP, plus existing ARCH-040 outbound-send-fence, conversation control and recovery credit interfaces. No Shared queue addition.

## Dependencies

- `ARCH-045-BACKGROUND-001`
- `ARCH-045-BACKGROUND-002`
- `ARCH-045-BACKGROUND-005`

## Enables

- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Neither scheduled nor merchant-initiated post-window WhatsApp recovery may send after stored withdrawal, local STOP, merchant suppression, recipient change or database failure; no per-follow-up Shopify verification occurs.
- [ ] First-send retries/resumptions and both sequence-two paths use the final permit, preserving the one allowed follow-up and billing/idempotency guarantees.
- [ ] Shopify is **not called** during follow-up dispatch; a credit/attempt is not irreversibly consumed when stored consent or Meta Marketing-template eligibility is denied. In-window service replies retain non-Marketing rules but cannot bypass customer STOP.
- [ ] No provider HTTP/Redis in SQL transaction, source epoch, erasure fence or reachability consent schema is introduced.

## Validation

- [ ] Focused `recovery-outreach-follow-up-processor`, human post-window command dispatcher/evaluator, first-send capacity/suppression reentry and outbound-send-fence tests, including local revocation between stored read and SQL fence and assertion of zero Shopify GraphQL calls for follow-ups.
- [ ] Concurrent human/automation sequence-two claim and compensation tests, in-window HUMAN_TEXT permitted-without-STOP and blocked-with-STOP tests, repository-declared checks and `git diff --check`.
- [ ] Approved Marketing versus Utility/Authentication/unverifiable template category tests for automated first/follow-up and merchant recovery templates; no attempt/charge/provider call on invalid category. Verify actual template metadata source, or report an explicit blocker when the catalogue only exposes purpose/status.

## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. For publication task, do not rerun implementation validation.

## Implementation Notes

Audit the implementation state of concurrent ARCH-040 tasks before editing their owned paths. If the canonical worktree has diverged from the snapshot, update against current accepted API rather than overwriting its human command work. Avoid changing human-text messages into marketing sends; STOP blocks all outbound types without changing their message-category classification.

Before claiming, use the deterministic `/moda-task` launcher and its **actual** prepared packet, read the task's complete current Architect Review, and verify task/dependency status in the developer's canonical workspace. Preserve `docs/decisions/**/_index.md` untouched until the developer explicitly closes the architecture documentation session. New runtime structured logging uses `@modainteract/moda-interact-shared/logging` where applicable. No source outside this task's owner repository may be changed unless explicitly authorised by the architecture.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-23T13:20:29Z. Attempt 0 review history is preserved below.

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
