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
enables:
  - ARCH-045-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-20
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

- Inject BACKGROUND-001 consent reader into scheduled sequence-two and merchant `RECOVERY_FOLLOW_UP_TEMPLATE` evaluation/dispatch at the smallest shared policy boundary appropriate to these paths.
- Verify current Shopify customer and exact immutable recipient snapshot before follow-up attempt claim/billing where possible, and recheck near provider dispatch if state could change before send.
- On absent/revoked/mismatched consent deny or defer proactive follow-up without a Meta request or recovery-credit consumption; preserve existing sequence-two unique ownership, human-control revision and compensation.
- Retain regular `HUMAN_TEXT` replies inside verified customer-initiated 24-hour service window and existing moderation/provider compliance checks.

## Out of Scope

- No new follow-up slot, no extra charge source, no generic Meta sender-wide consent rule that would block valid in-window replies.
- No Shopify Customer Privacy cookie setting or new merchant bypass control.
- No new recovery generations or conversation rows.

## Requirements

- [ ] Scheduled follow-up and merchant post-window template cannot bypass consent if initial send was previously authorised.
- [ ] A negative fresh consent check after reservation releases/compensates credit before provider dispatch; provider-unknown outcomes still use existing reconciliation.
- [ ] Consent denied before sequence-two claim does **not** irrevocably consume the only sequence-two attempt; preserve retry/claim ordering against another human or automation claimant.
- [ ] Human `HUMAN_TEXT` in current verified customer window remains governed by existing messaging/WhatsApp policy rather than blanket marketing opt-in.

## Work Items

- [ ] Trace both sequence-two paths and locate existing shared admission/dispatch seam.
- [ ] Add one injected policy check to both proactive paths and final pre-provider fence.
- [ ] Test revoked/missing consent, human-vs-automation ownership race, no charge/slot burn and valid 24h human text.

## Interfaces / Contracts

Consumes BACKGROUND-001 consent policy and existing ARCH-040 sequence-two Attempt, control revision and billing/outbound interfaces. No new queue contract or UI route.

## Dependencies

- `ARCH-045-BACKGROUND-001`
- `ARCH-045-BACKGROUND-002`

## Enables

- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Both proactive paths fail closed for non-SUBSCRIBED or mismatched recipient and issue zero provider sends and committed recovery credits.
- [ ] Exactly one sequence-two follow-up remains possible on valid consent under current ownership policy; duplicate claims cannot double-charge.
- [ ] Ordinary eligible customer-initiated in-window human replies still work; no new generic consent bypass.

## Validation

- [ ] Focused scheduled follow-up and human dispatcher/evaluator tests, with actual sequence-two and billing invariant assertions; repository-declared build and `git diff --check`.

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

Use the 2026-10-20 snapshot for orientation; revalidate active code/configuration when the task is materially claimed. ARCH-045's provisional 72-hour consent-wait deadline is the exact v1 task contract unless the developer and architect amend it before implementation.

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
