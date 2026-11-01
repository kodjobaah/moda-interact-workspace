---
id: ARCH-035-SYSTEM-TEST-004
architecture_id: ARCH-035
title: Certify Woo feature toggles and Merchant Knowledge lifecycle
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-035-API-014, ARCH-035-API-015, ARCH-035-API-016, ARCH-035-API-017, ARCH-035-API-018, ARCH-035-GATEWAY-001, ARCH-035-WOOCOMMERCE-015]
enables: []
created: 2026-10-16
updated: 2026-10-16
---

# ARCH-035-SYSTEM-TEST-004 — Certify Woo feature toggles and Merchant Knowledge lifecycle

## Architecture

- Parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`, approved 16 October functional knowledge extension.
- Owner: `moda_system_test`, repository `moda-interact-system-test`; coordinator: `moda_architect`.
- **Defined but not materialised.** This portable task definition did not create a parent/implementation worktree, branch, commit, push or claim. The real `/moda-task ARCH-035-SYSTEM-TEST-004` launcher owns canonical materialisation and start-of-attempt evidence.

## Objective

Validate complete authenticated Woo feature/knowledge workflows end to end against existing Shopify semantics and shared Background storage/processing.

## Context

This is terminal integrated certification only, after API, plugin and required infrastructure/observability tasks are architect accepted. It does not gate any implementation task.

## Scope

- Use disposable PostgreSQL/Redis/R2-compatible fixtures and real API/plugin boundaries to prove plan eligible and ineligible feature preference reads/writes and Merchant Knowledge configured-source flows.
- Cover create/edit/refresh/reorder/delete URL sources, **browser-direct R2 PUT** for CSV/XLSX upload/replacement/reprocess, durable revision statuses, quota/allowed-type enforcement, feature-off source retention and feature-on processing/reconciliation.
- Exercise WordPress nonce/capability/auth/URL-change/revoked-credential boundaries; two-shop isolation; repeated requests, concurrency and delayed/out-of-order queue jobs.
- Validate 20-locale UI gate, automated desktop/mobile component/browser parity, safe logs and regression against existing Shopify source semantics. `moda_system_test` **may use LocalWP** for integrated system-test certification; separate such evidence from developer manual sign-off.
- Provide repeatable evidence paths, clear prerequisite state, and observed outcomes.

## Out of Scope

- Changing production services, publishing shared packages or marking architecture Implemented without architect review.
- Inventing fixtures that substitute for a required real storage/queue boundary without flagging the gap.

## Requirements

- Preserve existing tenant, credential, platform, entitlement and transaction boundaries; use the source-inspected contracts and Shared package where applicable, not independently guessed interfaces.
- Fail closed on missing or malformed configuration, unauthorised operations and external provider failures. Record bounded structured logging through `@modainteract/moda-interact-shared/logging` when changing generic application logs.
- Keep production components modular and independently testable; no monolithic files or cross-repository implementation changes. Preserve Shopify runtime and existing Woo merchant Billing, recovery and navigation behaviour.
- If implementation discovers a genuine missing Background/Shared/Gateway capability, stop and return the precise evidence to `moda_architect` rather than extending another repository's scope.

## Work Items

- [ ] Use disposable PostgreSQL/Redis/R2-compatible fixtures and real API/plugin boundaries to prove plan eligible and ineligible feature preference reads/writes and Merchant Knowledge configured-source flows.
- [ ] Cover create/edit/refresh/reorder/delete URL sources, CSV and XLSX upload/replacement/reprocess, durable revision statuses, quota/allowed-type enforcement, activation-off retention and activation-on processing/reconciliation.
- [ ] Exercise WordPress nonce/capability/auth/URL-change/revoked-credential boundaries; two-shop isolation; repeated requests, concurrency and delayed/out-of-order queue jobs.
- [ ] Validate 20-locale UI gate, automated and (where needed) system-test-owned LocalWP desktop/mobile parity, no signed URLs/secrets in logs and Shopify regressions; distinguish developer manual evidence.
- [ ] Provide repeatable evidence paths, clear prerequisite state, and observed outcomes.
- [ ] Add focused positive and negative coverage and complete the required validation/Completion Report.

## Interfaces / Contracts

- Consumes API-014..017 HTTP contracts, accepted API-018 browser signed PUT contract, GATEWAY-001 R2 origin policy and WOO-014/015 WordPress/browser flows; references Background reconciliation and Shopify baseline.

## Dependencies

- `ARCH-035-API-014` (must be Complete and architect accepted)
- `ARCH-035-API-015` (must be Complete and architect accepted)
- `ARCH-035-API-016` (must be Complete and architect accepted)
- `ARCH-035-API-017` (Complete and architect accepted)
- `ARCH-035-API-018` (must be Complete and architect accepted)
- `ARCH-035-GATEWAY-001` (must be Complete and architect accepted)
- `ARCH-035-WOOCOMMERCE-015` (must be Complete and architect accepted)

## Enables

None

## Acceptance Criteria

- [ ] Actual source lifecycle and feature toggle persistence, off/enable reconciliation and entitlement changes meet Shopify parity.
- [ ] Tenant isolation, R2 origin CORS preflight/PUT method/header safety, replay/expiry/cancel/412 and failed-finalisation paths fail closed; no WordPress binary proxy, leaked signed URL or cross-Shop data.
- [ ] Certified validation artefacts and results distinguish manual/UI and integrated automated proofs.
- [ ] No `_index.md` files or unrelated domains modified; canonical dual-worktree/branch validation evidence recorded in real development workspace.

## Validation

- [ ] Disposable integration/system harness with real API, WP, PostgreSQL and queue/R2-compatible components plus a **real browser-origin preflight and signed PUT** check where infrastructure is available. Confirm fail-closed behaviour for an unregistered Woo origin.
- [ ] Automated UI/DOM snapshots and responsive tests, 20-locale, source/contract regression checks and `git diff --check`; inspect developer-supplied LocalWP screenshots only when available.
- [ ] Record concrete commands and results, implementation and parent task branch/commit evidence, canonical physical-isolation/synchronisation evidence, plus deviations and unresolved issues.

## Stop Condition

When this bounded task's Work Items, Acceptance Criteria and required Validation are satisfied, update Completion Report, set `status: review`, return to `moda_architect` and STOP. Do not start tasks listed under Enables.

## Implementation Notes

### Reconciled system-test handoff (2026-10-16 22:56 snapshot)

- Route certification must exercise the refactored API's real `src/composition/merchant.ts` registration and canonical `src/auth/woo-installation/` principal (not an old Woo installation catch-all), then the actual `includes/Runtime.php` / WordPress REST facade and Woo client/controller. Reject fixtures that bypass the new public route composition or tenant boundary.
- Confirm durable `PENDING` web/upload revisions are eventually claimed by Background's existing `MerchantKnowledgeReconciliationService`, including when API-to-Redis direct publication is absent and when merchant preference changes from off to on. Verify an uploaded Woo-scoped R2 key is readable by the unchanged Background asset acquirer while existing Shopify-key assets still work.
- Include separate fail-closed proof for revoked/rotated installation, site URL mismatch, unregistered browser Origin/CORS denial, wrong signed headers/host/redirect, expired upload intent, cancelled upload, overwrite replay, forged cross-Shop source IDs, duplicate finalisation and malformed shared-contract inputs. Prove that browser sends file bytes **only** to R2 and WordPress brokers metadata only. `moda_system_test` may operate LocalWP when needed for integrated system certification; the developer independently owns manual feature sign-off. Label evidence by producer and do not present developer screenshots as automated tests.

The historical superseded ARCH-035-API-003/004/005 must **not** be revived; this task follows the newly agreed architecture amendment and consumes only approved contract owners. An unimplemented API or feature must never be represented as operational. Do not update any `docs/decisions/**/_index.md` until the developer closes the architectural session.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

The uploaded ZIP represents a portable design baseline, not the developer's current on-disk branches. Confirm source, task status and dependency state with the launcher before execution.

### Unresolved Issues

None evidenced beyond the explicit implementation and test dependencies above.

### Architectural Concerns

Report any cross-repository contract, R2 identity, reconciliation or security mismatch to `moda_architect`.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting implementation and validation evidence.

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending.

### Follow-up

None until implementation submission.
