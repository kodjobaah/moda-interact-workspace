---
id: ARCH-007-BACKGROUND-004
architecture_id: ARCH-007
title: Route every Moda-originated WhatsApp send through one durable safety-admission boundary
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 90
executor: null
claimed_at: null
attempt: 4
depends_on:
  - ARCH-007-BACKGROUND-003
  - ARCH-007-DATABASE-004
enables:
  - ARCH-007-BACKGROUND-005
  - ARCH-007-BACKGROUND-010
created: 2026-09-07
updated: 2026-09-08
---

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

# ARCH-007-BACKGROUND-004: Route every Moda-originated WhatsApp send through one durable safety-admission boundary

## Architecture

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Eliminate direct provider-send bypasses by introducing one outbound WhatsApp service boundary that persists message intent, enforces effective per-conversation automated-message safety and sends either normal content or one reserved deterministic terminal response.

## Context

`whatsapp.worker.ts` currently contains several direct `sendWhatsAppText()` calls (including product/clarification paths). Counting only some ConversationMessage rows would leave cost/safety gaps.

## Scope

Background WhatsApp send abstraction, existing recovery/AI/product/clarification call sites, durable ConversationMessage/UsageEvent updates and focused tests. Preserve provider adapter itself as a low-level transport behind the new boundary.

## Out of Scope

- Meta webhook normalization (MESSAGING-001).
- Shopify billing conversation charges.
- Changing CommerceAgent reasoning other than preventing invocation when hard cap reached.

## Requirements

- Every Moda-originated WhatsApp send in Background must call the new accepted boundary; raw provider transport may only be invoked from that boundary/adapter layer and its tests.
- Count only outbound AUTOMATION/AGENT Moda messages against automated cap, not CUSTOMER inbound/HUMAN future messages.
- Use effective policy from BACKGROUND-001 including global/shop pause and platform-bounded soft/hard limit.
- Reserve exactly one terminal slot inside hard cap. Define `normalLimit = hardLimit - terminalReservedSlots` (initially one reserved slot). Validate hard limit always leaves terminal semantics meaningful.
- If normal slot remains, persist outbound message intent/status PENDING before provider call; successful send records providerMessageId/SENT and one OUTBOUND_AUTOMATED_MESSAGE usage event with deterministic identity.
- If normal slots exhausted and terminal slot unused: DO NOT invoke LLM/tool flow; send one deterministic non-LLM terminal message through same persistence/provider boundary and consume terminal slot.
- If terminal already used or automation paused, do not call provider; return typed suppression reason.
- Provider definitive failure updates durable message FAILED and does not count a successful outbound send unless architecture/provider lifecycle explicitly considers acceptance billable; tests must match chosen local SENT semantics.
- Provider ambiguous outcome preserves message state/correlation and prevents blind duplicate provider send.
- Approaching soft threshold should be exposed to CommerceAgent prompt/context only where an existing bounded mechanism exists; do not invent a second agent architecture. Hard cap correctness is mandatory.

## Work Items

- [x] Inventory every `sendWhatsAppText`/template transport call in production Background code.
- [x] Implement common admission/persistence/send service.
- [x] Rewire all production call sites; prove no business workflow directly calls transport.
- [x] Implement terminal response path and usage recording.
- [x] Add tests for inbound-not-counted, normal cap, terminal exactly once, global/shop pause, duplicate send identity and provider failure/ambiguity.
- [x] Add a focused static/import test or architecture test preventing direct provider transport imports from business workers where practical.

## Interfaces / Contracts

Boundary:

```text
Business workflow -> OutboundWhatsAppAdmissionService -> low-level WhatsAppService transport -> Meta
```

The low-level transport remains testable but is not a business entrypoint.

## Dependencies

Explicit task dependencies are authoritative in YAML frontmatter. Do not begin unless every listed dependency is architect-accepted `complete` and any accepted Shared/database artifact required by this repository is available to consume.

## Enables

- ARCH-007-BACKGROUND-005

## Acceptance Criteria

- [x] All current direct business-worker sends are routed through one boundary.
- [x] Automated outbound hard cap cannot be exceeded under duplicate/concurrent conversation work.
- [x] Terminal response is deterministic, non-LLM and at most once.
- [x] Customer inbound messages never consume automated cap.
- [x] Every admitted send has durable message identity before provider call.
- [x] No raw SQL/new provider bypass exists.
- [x] Tests/validation pass.

## Validation

Inspect the repository `package.json` first. Run the focused tests required by this task plus the repository-declared typecheck/lint/build/Prisma validation that actually exists, and `git diff --check`. Do not invent missing npm scripts.

## Implementation Notes


Luna deterministic-execution guardrails:

- Treat this task file as the complete implementation contract. Do not infer additional product policy from old billing code.
- Inspect the named current implementation before editing, but if old code conflicts with ARCH-007, implement ARCH-007.
- Do not start an enabled/dependent task. Return only this task to `review` and STOP.
- Do not modify another repository except an explicitly permitted database submodule/package dependency pointer in this task.
- Do not add new billing raw SQL (`$queryRaw`, `$executeRaw`, `Prisma.sql`, raw driver SQL) to compensate for an unavailable Prisma delegate. Adopt/regenerate the accepted Prisma schema instead.
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-BACKGROUND-004` branch and the mirrored parent-workspace `task/ARCH-007-BACKGROUND-004` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.


## Completion Report

### Status

Ready for Review (Attempt 4)

### Files Changed

- `moda-interact-background/src/services/outbound-whatsapp-admission.service.ts`
- `moda-interact-background/src/services/recovery-routing.service.ts`
- `moda-interact-background/src/workers/whatsapp.worker.ts`
- `moda-interact-background/tests/unit/services/outbound-whatsapp-admission.service.test.ts`
- `moda-interact-background/tests/unit/services/recovery-routing.service.test.ts`
- `docs/decisions/background/ARCH-007/BACKGROUND-004-common-whatsapp-outbound-admission.md`

### Work Completed

- Implemented deterministic terminal admission handling: both CommerceAgent paths bypass agent/tool/language work, terminal sends use `TERMINAL_MESSAGE`, prepared text is defensive, and template admission falls back to low-level text transport.
- Added fail-closed ambiguous tenant routing for product-only phone matches and multi-recovery clarification matches; duplicate active phone rows for one `(shopId, customerId)` remain valid and same-owner clarification reuses its active scope.
- Preserved durable conversation ownership validation, per-conversation usage aggregation, 24-hour standalone expiry, serializable unique-race retry, pause/duplicate/provider failure handling, and the low-level transport boundary.
- Added focused regressions for terminal agent bypass (recovery and product contexts), terminal text/template behavior, per-conversation independence and accumulation, standalone expiry, P2002 winner reuse, clarification reuse, ambiguous ownership, same-owner deduplication, ownership suppression, and direct transport imports.
- Added overflow-sentinel tenant isolation for both bounded exact-phone lookups: `take: 11` fails closed before ownership resolution when 11 rows are returned.
- Added regressions for 11-row product/recovery overflow, exact-10 same-owner product rows, exact-10 same-owner active recoveries, and both Prisma query bounds.

### Validation Results

- Focused Attempt 4 suites: 26 passed across admission and routing services.
- Full test suite: 314 passed, 7 skipped; 2 unrelated baseline failures remain in `tests/unit/services/pending-recovery-candidate.service.test.ts`.
- `npm run build`: passed, including Prisma generation and strict TypeScript compilation.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.
- Editor diagnostics for changed routing source/tests: no errors.
- Production source scan found only the admission service importing the low-level WhatsApp adapter; no business workflow directly invokes its transport methods.

### Deviations

- No schema migration was required; this attempt consumes the accepted DATABASE-004 conversation fields.
- The two full-suite failures are unrelated pending-recovery candidate baseline failures and were not modified.
- The production transport scan remains unchanged: only the admission boundary imports the low-level WhatsApp adapter.

### Assumptions

- Terminal admissions always use the deterministic non-LLM response, including when a caller supplies ordinary text or a template request.

### Unresolved Issues

- The two unrelated baseline failures remain for their owning task/workflow.

### Architectural Concerns

None identified within the Attempt 4 correction scope.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 4 is architect-accepted Complete.

The final Attempt 3 correction is implemented correctly:

- both exact-phone bounded routing queries now use `take: 11`;
- the 11th returned row is treated strictly as an overflow sentinel;
- overflow fails closed before tenant/customer ownership resolution;
- product-only overflow creates no standalone conversation;
- active-recovery overflow creates no clarification conversation and exposes no recovery references;
- exactly 10 same-owner product-phone rows remain resolvable;
- exactly 10 same-owner active recoveries remain eligible for same-owner clarification.

The accepted behavior from earlier attempts remains present:

1. every production Moda-originated Background WhatsApp send crosses the common outbound admission boundary;
2. `conversationId` is mandatory at the business boundary;
3. outbound automated usage is counted per durable conversation, not shop-wide;
4. supplied Conversation ownership is validated against `shopId`;
5. normal outbound capacity is reserved before CommerceAgent execution;
6. terminal admission bypasses CommerceAgent/LLM/tool work;
7. terminal prepared-text/template callers cannot overwrite the deterministic terminal response;
8. terminal template admission does not call template transport;
9. one reserved terminal response is allowed at most once per conversation;
10. standalone PRODUCT_DISCOVERY / PRODUCT_SUPPORT scope is stable within the 24-hour inactivity lifecycle;
11. stale standalone scope is expired/cleared before a new lifecycle is created;
12. concurrent standalone creation losing the unique-key race re-reads/reuses the winner;
13. product/clarification inbound messages are persisted before normal agent/admission work;
14. returned ownership candidates are deduplicated by `(shopId, customerId)`;
15. ambiguous/multi-tenant ownership fails closed;
16. definitive provider failure releases its outbound reservation;
17. ambiguous provider outcome preserves durable pending intent;
18. low-level WhatsApp transport remains behind the admission/provider boundary;
19. BACKGROUND-010 turn coalescing has not been implemented prematurely.

### Reviewed Files

- `moda-interact-background/src/services/outbound-whatsapp-admission.service.ts`
- `moda-interact-background/src/services/recovery-routing.service.ts`
- `moda-interact-background/src/workers/whatsapp.worker.ts`
- `moda-interact-background/tests/unit/services/outbound-whatsapp-admission.service.test.ts`
- `moda-interact-background/tests/unit/services/recovery-routing.service.test.ts`
- `docs/decisions/background/ARCH-007/BACKGROUND-004-common-whatsapp-outbound-admission.md`

### Validation Reviewed

Attempt 4 Completion Report records:

- focused admission/routing suites: 26/26 passed;
- full suite: 314 passed, 7 skipped, with 2 documented unrelated baseline failures;
- build / strict TypeScript: passed;
- Prisma validation: passed;
- diagnostics: clean;
- transport-boundary source scan: passed;
- `git diff --check`: passed.

Architect inspection additionally verified:

- both production lookup sites use `take: 11`;
- both check the 11-row overflow sentinel before ownership resolution;
- exact-10 same-owner success regressions exist for product and active-recovery routes;
- overflow regressions assert the query bound and fail-closed result;
- previously accepted terminal/per-conversation/lifecycle regressions remain present.

The architect did not rerun the Node test suite from the extracted review archive because installed dependencies were not included.

### Architecture Conformance

Accepted.

### Follow-up

`ARCH-007-BACKGROUND-005` is now Ready because all of its dependencies are architect-accepted Complete:

```text
BACKGROUND-004 Complete
MESSAGING-001 Complete
SHARED-004 Complete
```

`ARCH-007-BACKGROUND-010` remains Pending because `ARCH-007-DATABASE-006` is not yet Complete.

This acceptance does not alter `ARCH-007-BACKGROUND-007`, which remains on its separate Changes Requested lifecycle.
