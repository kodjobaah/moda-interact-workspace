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

Prevent scheduled no-response and merchant post-window recovery templates from sending or consuming recovery credits when Shopify WhatsApp consent is absent or revoked.

## Context

`recovery-outreach-follow-up-processor.service.ts` and ARCH-040 `recovery-conversation/human-command-*` are currently separate proactive sequence-two admission paths. Initial-only checks would leave a bypass.

## Scope

- In scheduled sequence-two and merchant post-window recovery template paths, use BACKGROUND-001 `CustomerPhone` current consent and **fresh Shopify native authority** for exact immutable recipient before billing/attempt claim and near Meta dispatch.
- Deny/defer missing/revoked/changed-phone/unavailable consent without outbound send or committed credit, preserving existing sequence-two ownership, compensation and human handover semantics.
- An ordinary, legitimate customer-initiated in-window human reply follows existing Meta 24-hour service rules and must not be misclassified as a new business-initiated recovery template.

## Out of Scope

- No new follow-up slot, no extra charge source, no generic Meta sender-wide consent rule that would block valid in-window replies.
- No Shopify Customer Privacy cookie setting or new merchant bypass control.
- No new recovery generations or conversation rows.

## Requirements

- [ ] Scheduled follow-up and merchant post-window template cannot bypass consent if initial send was previously authorised.
- [ ] A negative fresh consent check after reservation releases/compensates credit before provider dispatch; provider-unknown outcomes still use existing reconciliation.
- [ ] Consent denied before sequence-two claim does **not** irrevocably consume the only sequence-two attempt; preserve retry/claim ordering against another human or automation claimant.
- [ ] Human `HUMAN_TEXT` in current verified customer window remains governed by existing messaging/WhatsApp policy rather than blanket marketing opt-in.

- **C3/H5:** Besides sequence-two follow-ups, guard all proactive **first-send reentries** that leave an already-created DETECTED row; BACKGROUND-002 owns the common first-creation logic, this task owns final cross-path send policy integration.
- Fresh Shopify GraphQL preflight must run **outside** the ARCH-040 short SQL `outbound-send-fence` transaction. Under that transaction, check exact immutable recipient + current CustomerPhone decision/revision/source epoch + no-contact/erasure fence before a durable send permit; no network/Redis I/O under lock. Document the unavoidable provider/DB-to-Meta time-of-check race and use best-effort final freshness and compensation rather than claiming perfect atomicity.
- STOP/merchant no-contact overrides win over Shopify SUBSCRIBED; deliberate customer-initiated in-window service replies remain governed by WhatsApp service messaging rules, not silently blocked as marketing templates.
- Any consent denial after a pre-billing reservation but before provider dispatch must release/compensate credit and preserve sequence-two attempts per existing ARCH-040 rules.

- Final SQL send permit must check the permanent shop/recipient negative STOP fence alongside CustomerPhone revision; temporary reachability suppressUntil is a separate condition and cannot cancel a permanent opt-out.

## Work Items

- [ ] Trace both sequence-two paths and locate existing shared admission/dispatch seam.
- [ ] Add one injected policy check to both proactive paths and final pre-provider fence.
- [ ] Test revoked/missing consent, human-vs-automation ownership race, no charge/slot burn and valid 24h human text.

- [ ] Exercise scheduled sequence-two, post-window human templates, first-send capacity/suppression reentry and direct pre-provider outbound fence with provider preflight outside transaction.
- [ ] Test revoked-between-preflight-and-fence, unchanged consent, STOP and legitimate in-window human text with idempotent billing.

## Interfaces / Contracts

Consumes BACKGROUND-001 consent policy and existing ARCH-040 sequence-two Attempt, control revision and billing/outbound interfaces. No new queue contract or UI route.

## Dependencies

- `ARCH-045-BACKGROUND-001`
- `ARCH-045-BACKGROUND-002`
- `ARCH-045-BACKGROUND-005`

## Enables

- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Both proactive paths deny stale or revoked phone grants even if the CustomerPhone webhook mirror is delayed.
- [ ] No double-charge or lost sequence-two slot; valid customer-initiated in-window human replies unaffected.

- [ ] No provider/network I/O inside send-fence transaction; a newer local STOP/phone change always invalidates the older provider preflight and proactive permit.
- [ ] Both initial reentry and follow-up send paths fail closed without phantom charge or consumed unique attempt; service-window replies are not misclassified as promotional sends.

## Validation

- [ ] Focused scheduled follow-up and human dispatcher/evaluator tests, with actual sequence-two and billing invariant assertions; repository-declared build and `git diff --check`.

- [ ] Cross-path permit/compensation tests with mocked provider preflight and SQL fence concurrency; no accidental blocking of valid ARCH-040 customer-service reply.

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
