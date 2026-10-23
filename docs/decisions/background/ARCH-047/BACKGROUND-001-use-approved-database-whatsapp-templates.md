---
id: ARCH-047-BACKGROUND-001
architecture_id: ARCH-047
title: Use approved database templates without Meta metadata checks
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-047-ADMIN-001
enables:
  - ARCH-047-SYSTEM-TEST-001
created: 2026-10-23
updated: 2026-10-23
---

# Use approved database templates without Meta metadata checks

## Architecture

`ARCH-047` — `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`; coordinator `moda_architect`. Source snapshot: 23 October 2026, 16:40.

## Objective

Replace Meta template category/approval preflight with **database-authoritative `WhatsAppTemplateVariant` selection** across all initial, scheduled, merchant-initiated and final outbound WhatsApp recovery-template paths, while preserving existing consent, STOP, billing and final-send protections.

## Context

Merged ARCH-045-BACKGROUND-004 added provider `message_templates` metadata reads and `verifiedCategory` gates. That work is complete historically, but the agreed new architecture supersedes only the **template metadata verification behaviour**; it does not reopen or remove its accepted consent/STOP/marketing/final-fence protections. Admin, rather than runtime sending services, now controls which variants are locally approved and assigned.

## Scope

- Modify `src/services/whatsapp-template-selector.service.ts` to read existing approved enabled per-shop records, matching sender WABA, recovery purpose and deterministic canonical-language fallback. Remove `verifyCategory` callbacks and `verifiedCategory` fields from selection API as no longer needed.
- Modify `src/services/checkout-recovery/recovery-initiation.service.ts` and `src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts` so neither calls Meta for template metadata/category. Preserve the configured recipient/attempt/credit policy and deterministic template selection.
- Modify `src/services/recovery-conversation/human-command-dispatcher.service.ts`, `src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts`, and `src/services/recovery-conversation/outbound-send-fence.service.ts` where they currently depend on Meta `verifiedCategory`. Use only assigned approved/enabled database template identity for *post-window recovery templates*; in-window human plain text remains a separate non-template path subject to STOP.
- Remove `src/services/whatsapp-template-category.service.ts` only if all production imports and related tests no longer require it; otherwise leave dead code unmapped and report the dependency. Do not leave hidden provider `message_templates` calls in a fallback path.
- At the final short database-backed outbound permit, verify the selected exact variant is still approved/enabled and matches shop, WABA, purpose and template language/name. A stale or deactivated assignment fails closed with no provider call/committed charge. This is **local assignment existence**, not validation against Meta.
- Update focused unit/integration tests to prove initial/automated/human paths select per-shop records, global Admin changes take effect on subsequent decisions, and no Meta template metadata HTTP calls occur. Keep actual Meta **send** API and provider failure handling unchanged.

## Out of Scope

- No changes to ARCH-045 Shopify consent API reads, archived STOP handling, Woo consent API, database migrations, Admin UI or new Shared events.
- Do not remove customer consent/STOP checks, moderation, capacity/billing checks, single sequence-two claim/final send fences or Meta send/delivery error handling.
- Do not introduce Meta category caching, polling, background template sync or new provider verification abstraction.

## Requirements

- [ ] `WhatsAppTemplateSelectorService` selects only `APPROVED` and `enabled` rows assigned to the target shop and actual WABA, `purpose=checkout-recovery`, with deterministic language precedence and refusal of ambiguous active slots.
- [ ] No `message_templates` metadata request exists in any recovery-template send path, including first send, scheduled follow-up, manual post-window template, retry/re-entry or outbound admission. Provider calls to **send** a message remain intact.
- [ ] The final database gate independently refuses disabled/unassigned/stale templates, without outside-provider metadata I/O in the transaction.
- [ ] A catalogue change becomes effective without Background restart; no stale in-memory category approval cache.
- [ ] Consent/STOP, recipient match, credit reservation/compensation and in-window support messages are not weakened or reclassified by this work.

## Work Items

- [ ] Trace and replace every listed template-category caller, then search entire Background runtime for residual `metaWhatsAppTemplateCategoryService`, `verifyCategory` and `message_templates` provider reads.
- [ ] Reuse the current shop-scoped Prisma selector; remove unused category-verification plumbing without changing unrelated provider sending mechanics.
- [ ] Preserve existing final SQL send permit/credit compensation and add exact assigned-record state checks.
- [ ] Add tests for approved/enabled selection, deactivation or shop reassignment race, no approved template, ambiguous locale, no Meta metadata calls, STOP and consent races.

## Interfaces / Contracts

Consumes ADMIN-001-populated existing `whatsapp.WhatsAppTemplateVariant`; no new Shared runtime contract. Existing sending contracts remain unchanged except for removal of provider metadata-category fields where they were invented only for the former Meta preflight. For non-template free-text messages, retain ordinary service-window and STOP constraints.

## Dependencies

- `ARCH-047-ADMIN-001`

## Enables

- `ARCH-047-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Initial Shopify recovery and scheduled sequence-two follow-up use assigned DB templates without any Meta template-category request.
- [ ] Merchant post-window recovery template and automated outbound checks use the same catalogue and preserve current STOP/consent, billing and final permit behaviour.
- [ ] Disabled/absent/wrong-shop/wrong-WABA/ambiguous template rows cannot result in a send or permanently consumed credit.
- [ ] Provider template *delivery* failure remains observable and recoverable under existing Meta send response and credit/attempt safeguards.
- [ ] Focused test proves the Meta metadata verifier is not called in all relevant business-initiated recovery paths; no unrelated send protocol changes.

## Validation

- [ ] Existing/revised `whatsapp-template-selector`, `recovery-initiation`, `recovery-outreach-follow-up-processor`, human dispatcher, outbound-delivery/fence unit tests; a PostgreSQL integration path for approved/disabled assignment changes.
- [ ] Negative no-catalogue and STOP/consent/billing regression tests; repository-declared lint/typecheck/build checks if applicable; `git diff --check`.
- [ ] Source grep/static test showing no reachable Meta template-listing/category calls from recovery send flows.

## Stop Condition

After completing the defined Work Items, Acceptance Criteria and required Validation, record task-isolated parent and implementation worktrees, start-of-attempt synchronisation and relevant commit evidence in the Completion Report; set `status: review`, return control to `moda_architect`, and **STOP**. Do not implement dependent tasks or modify domain `_index.md` files.

## Implementation Notes

Respect `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/task-definition-materialization.md` and `docs/developer-task-workflow.md`. `/moda-task` owns preparation and the canonical claim; never infer worktrees from a previous task or operate in shared/default checkouts. Existing application code has evolved: inspect current implementation immediately before claiming and return cross-domain contract gaps to `moda_architect`. Use the shared structured logger where new runtime domain logging is needed, not a duplicate generic logger. All tasks are portable definitions until materialised in the developer's real workspace.


Additional task-specific guidance:

The previous task `ARCH-045-BACKGROUND-004` remains historically Complete. This is a new, narrowly scoped correction to catalogue selection after that merge, not a re-review of its customer consent/STOP work. A direct Meta *send* API call is of course still required to deliver a WhatsApp message.

## Completion Report

### Status

Not Started — portable definition; not materialised or claimed.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

Based on `moda-interact-workspace(20261023-164023).zip`; revalidate against launcher-resolved task worktree when execution begins.

### Unresolved Issues

None recorded at definition time.

### Architectural Concerns

None recorded at definition time.

## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
