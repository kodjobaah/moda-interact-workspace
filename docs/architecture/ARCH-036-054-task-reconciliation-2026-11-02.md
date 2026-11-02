# ARCH-036–ARCH-054 task-definition reconciliation — 2026-11-02

Scope: reconcile the 39 open task IDs, four completed records absent from main, and the ARCH-051 promotion identified in the previous audit. Current task worktrees and published implementation branches were inspected. This is architecture/task documentation reconciliation, with one focused implementation review; it does not certify unexecuted system scenarios.

## Source evidence

- Admin `420b86a`: catalogue query and recovery-settings presentation.
- Commerce `d0ade08`: existing Shopify discount reader/evaluator and preview adapter.
- Gateway `ac092dc`: both Render Blueprints, private MCP services, credential groups and validation scripts.
- Background main `10e72d7`; BG013 implementation `4fdc5c8`; BG054-001 implementation `7bb69d7`.
- API-006 implementation `53df5aa` plus concurrent uncommitted route/fixture corrections; Woo-003 active returning-consent/Blocks changes.
- System Test `41d7583`: 169 catalogue scenarios and existing recovery/messaging/language harness infrastructure.

## Decisions

- ARCH-052-BACKGROUND-013 Attempt 2 accepted after actual source review and 31/31 focused provider tests. Recorded lint/build remain applicable; no source changes made.
- Preserve accepted completion records from ARCH-043-MESSAGING-001, ARCH-044-COMMERCE-007, ARCH-044-COMMERCE-008 and ARCH-052-BACKGROUND-017 task branches; their previously identified publication gaps are now resolved on those task branches, while main still needs the task-record reconciliation.
- Restore the accepted ARCH-051 task/architecture/index; retire the conflicting old ARCH-050 stabilisation architecture. ARCH-050 remains the Support-notice initiative.
- Deduplicate ARCH-043 GATEWAY-001 and SYSTEM-TEST-001 using the paths named by the controlling inventory. Supersede legacy GATEWAY-002/SYSTEM-TEST-002 into those canonical tasks, preserving their useful security/rollback certification requirements.
- Retire deferred ARCH-036-SYSTEM-TEST-002 in favor of current ARCH-052 Woo initial-outreach certification; the old one-coupon/live-proof contract and superseded BG003 dependency no longer describe the accepted runtime. ARCH-036-COMMERCE-001 remains explicitly deferred.
- Correct ARCH-036 Admin/catalogue system-test definitions to the current merchant-selection semantics of isAvailable on both platforms.
- Promote only terminal tasks whose declared implementation prerequisites are Complete; keep manual execution gates and every unfulfilled scenario/acceptance item.
- Preserve active API/Woo source edits and claims. Docker is reachable now, but concurrent BG054 integration edits and missing stable run evidence prevent completion; the old environment failure is recorded as historical.

## Per-task disposition

| Task | Reconciled status | Attempt | Remaining prerequisites / disposition |
|---|---|---:|---|
| [ARCH-036-ADMIN-001](../decisions/admin/ARCH-036/ADMIN-001-make-internal-discount-catalogue-provider-aware.md) | ready | 0 | Execution/validation remains; see task reconciliation note. |
| [ARCH-036-COMMERCE-001](../decisions/commerce/ARCH-036/COMMERCE-001-adapt-existing-discount-evaluator-to-woo-normalized-rules.md) | pending | 0 | Deferred by ARCH-036 scope. |
| [ARCH-036-SYSTEM-TEST-001](../decisions/system-test/ARCH-036/SYSTEM-TEST-001-certify-shared-catalogue-and-merchant-selection.md) | pending | 0 | ARCH-036-ADMIN-001 (ready) |
| [ARCH-036-SYSTEM-TEST-002](../decisions/system-test/ARCH-036/SYSTEM-TEST-002-certify-eligible-discount-outreach-and-revocation.md) | superseded | 0 | Superseded by ARCH-052-SYSTEM-TEST-002 |
| [ARCH-038-SYSTEM-TEST-001](../decisions/system-test/ARCH-038/SYSTEM-TEST-001-certify-live-budget-policy-inheritance.md) | ready | 0 | Execution/validation remains; see task reconciliation note. |
| [ARCH-038-SYSTEM-TEST-002](../decisions/system-test/ARCH-038/SYSTEM-TEST-002-certify-preview-budget-isolation.md) | ready | 0 | Execution/validation remains; see task reconciliation note. |
| [ARCH-039-SYSTEM-TEST-001](../decisions/system-test/ARCH-039/SYSTEM-TEST-001-certify-cross-service-credential-security.md) | ready | 0 | Execution/validation remains; see task reconciliation note. |
| [ARCH-040-SYSTEM-TEST-001](../decisions/system-test/ARCH-040/SYSTEM-TEST-001-certify-one-conversation-and-shared-follow-up-credit.md) | ready | 0 | Execution/validation remains; see task reconciliation note. |
| [ARCH-040-SYSTEM-TEST-002](../decisions/system-test/ARCH-040/SYSTEM-TEST-002-certify-shopify-customer-inbox-end-to-end.md) | ready | 0 | Execution/validation remains; see task reconciliation note. |
| [ARCH-040-SYSTEM-TEST-003](../decisions/system-test/ARCH-040/SYSTEM-TEST-003-certify-woo-customer-inbox-end-to-end.md) | ready | 0 | Execution/validation remains; see task reconciliation note. |
| [ARCH-041-SYSTEM-TEST-001](../decisions/system-test/ARCH-041/SYSTEM-TEST-001-certify-refactored-hosted-api-http-and-billing-parity.md) | ready | 0 | Execution/validation remains; see task reconciliation note. |
| [ARCH-043-GATEWAY-001](../decisions/gateway/ARCH-043/GATEWAY-001-retire-policy-environment-variables.md) | ready | 0 | Execution/validation remains; see task reconciliation note. |
| [ARCH-043-GATEWAY-002](../decisions/gateway/ARCH-043/GATEWAY-002-retire-migrated-provider-secrets.md) | superseded | 0 | Superseded by ARCH-043-GATEWAY-001 |
| [ARCH-043-MESSAGING-001](../decisions/messaging/ARCH-043/MESSAGING-001-database-backed-meta-webhook-credentials.md) | complete | 2 | Accepted record reconciled; no implementation acceptance invented. |
| [ARCH-043-SYSTEM-TEST-001](../decisions/system-test/ARCH-043/SYSTEM-TEST-001-certify-platform-runtime-configuration.md) | pending | 0 | ARCH-043-GATEWAY-001 (ready) |
| [ARCH-043-SYSTEM-TEST-002](../decisions/system-test/ARCH-043/SYSTEM-TEST-002-encrypted-provider-config-cutover.md) | superseded | 0 | Superseded by ARCH-043-SYSTEM-TEST-001 |
| [ARCH-044-COMMERCE-007](../decisions/commerce/ARCH-044/COMMERCE-007-repair-postgres-cas-and-publication.md) | complete | 2 | Published architect acceptance reconciled; historical expiry cause remains explicitly uncertain. |
| [ARCH-044-COMMERCE-008](../decisions/commerce/ARCH-044/COMMERCE-008-correct-markdown-prompt-editor-refs.md) | complete | 1 | Accepted record reconciled; no implementation acceptance invented. |
| [ARCH-045-SYSTEM-TEST-001](../decisions/system-test/ARCH-045/SYSTEM-TEST-001-certify-whatsapp-consent-and-recovery-resumption.md) | ready | 0 | Execution/validation remains; see task reconciliation note. |
| [ARCH-046-API-006](../decisions/api/ARCH-046/API-006-read-proof-backed-woo-whatsapp-consent-status.md) | ready | 1 | Execution/validation remains; see task reconciliation note. |
| [ARCH-046-SYSTEM-TEST-001](../decisions/system-test/ARCH-046/SYSTEM-TEST-001-certify-woo-precheckout-opt-in-capture.md) | pending | 0 | ARCH-046-API-006 (ready); ARCH-046-WOOCOMMERCE-003 (in_progress) |
| [ARCH-046-SYSTEM-TEST-002](../decisions/system-test/ARCH-046/SYSTEM-TEST-002-certify-woo-consent-block-notice-and-resume.md) | blocked | 0 | ARCH-046-API-006 (ready); ARCH-046-WOOCOMMERCE-003 (in_progress) |
| [ARCH-046-WOOCOMMERCE-003](../decisions/woocommerce/ARCH-046/WOOCOMMERCE-003-allow-later-consent-on-returning-woo-checkout.md) | in_progress | 1 | Execution/validation remains; see task reconciliation note. |
| [ARCH-047-SYSTEM-TEST-001](../decisions/system-test/ARCH-047/SYSTEM-TEST-001-certify-whatsapp-template-catalogue-and-assignment.md) | ready | 0 | Execution/validation remains; see task reconciliation note. |
| [ARCH-048-SYSTEM-TEST-001](../decisions/system-test/ARCH-048/SYSTEM-TEST-001-certify-woo-first-recovery-lifecycle.md) | pending | 0 | ARCH-046-WOOCOMMERCE-003 (in_progress) |
| [ARCH-049-SYSTEM-TEST-001](../decisions/system-test/ARCH-049/SYSTEM-TEST-001-certify-shop-brand-media-pipeline.md) | ready | 0 | Execution/validation remains; see task reconciliation note. |
| [ARCH-050-SYSTEM-TEST-001](../decisions/system-test/ARCH-050/SYSTEM-TEST-001-verify-shopify-initial-recovery-support-notices.md) | ready | 0 | Execution/validation remains; see task reconciliation note. |
| [ARCH-050-SYSTEM-TEST-002](../decisions/system-test/ARCH-050/SYSTEM-TEST-002-verify-woo-initial-recovery-support-notices.md) | ready | 0 | Execution/validation remains; see task reconciliation note. |
| [ARCH-051-BACKGROUND-001](../decisions/background/ARCH-051/BACKGROUND-001-classify-and-remediate-test-suite-failures.md) | complete | 2 | Accepted record reconciled; no implementation acceptance invented. |
| [ARCH-052-BACKGROUND-013](../decisions/background/ARCH-052/BACKGROUND-013-capture-complete-shopify-combination-identities.md) | complete | 2 | Accepted record reconciled; no implementation acceptance invented. |
| [ARCH-052-BACKGROUND-017](../decisions/background/ARCH-052/BACKGROUND-017-enforce-initial-checkout-items-at-send.md) | complete | 1 | Accepted record reconciled; no implementation acceptance invented. |
| [ARCH-052-GATEWAY-001](../decisions/gateway/ARCH-052/GATEWAY-001-configure-private-recovery-product-read-transport.md) | ready | 0 | Execution/validation remains; see task reconciliation note. |
| [ARCH-052-SYSTEM-TEST-001](../decisions/system-test/ARCH-052/SYSTEM-TEST-001-certify-shopify-initial-outreach-modes.md) | pending | 0 | ARCH-052-GATEWAY-001 (ready) |
| [ARCH-052-SYSTEM-TEST-002](../decisions/system-test/ARCH-052/SYSTEM-TEST-002-certify-woocommerce-initial-outreach-modes.md) | pending | 0 | ARCH-052-GATEWAY-001 (ready) |
| [ARCH-052-SYSTEM-TEST-003](../decisions/system-test/ARCH-052/SYSTEM-TEST-003-certify-shared-sender-contextual-replies.md) | ready | 0 | Execution/validation remains; see task reconciliation note. |
| [ARCH-052-SYSTEM-TEST-004](../decisions/system-test/ARCH-052/SYSTEM-TEST-004-certify-mandatory-initial-checkout-items.md) | ready | 0 | Execution/validation remains; see task reconciliation note. |
| [ARCH-053-SYSTEM-TEST-001](../decisions/system-test/ARCH-053/SYSTEM-TEST-001-certify-woo-checkout-links-coupons-and-generations.md) | pending | 0 | ARCH-046-WOOCOMMERCE-003 (in_progress) |
| [ARCH-053-SYSTEM-TEST-002](../decisions/system-test/ARCH-053/SYSTEM-TEST-002-certify-original-coupon-restoration.md) | pending | 0 | ARCH-046-WOOCOMMERCE-003 (in_progress) |
| [ARCH-053-SYSTEM-TEST-003](../decisions/system-test/ARCH-053/SYSTEM-TEST-003-certify-confirmed-outreach-coupons.md) | pending | 0 | ARCH-053-SYSTEM-TEST-001 (pending); ARCH-053-SYSTEM-TEST-002 (pending); ARCH-046-WOOCOMMERCE-003 (in_progress) |
| [ARCH-054-BACKGROUND-001](../decisions/background/ARCH-054/BACKGROUND-001-capture-pending-ai-delay-for-text-and-audio.md) | blocked | 1 | Execution/validation remains; see task reconciliation note. |
| [ARCH-054-BACKGROUND-002](../decisions/background/ARCH-054/BACKGROUND-002-enforce-pending-ai-deadline-and-control-fencing.md) | pending | 0 | ARCH-054-BACKGROUND-001 (blocked) |
| [ARCH-054-BACKGROUND-003](../decisions/background/ARCH-054/BACKGROUND-003-repair-overdue-delayed-ai-turns.md) | pending | 0 | ARCH-054-BACKGROUND-002 (pending) |
| [ARCH-054-SYSTEM-TEST-001](../decisions/system-test/ARCH-054/SYSTEM-TEST-001-certify-delayed-ai-and-human-bypass.md) | pending | 0 | ARCH-054-BACKGROUND-001 (blocked); ARCH-054-BACKGROUND-002 (pending); ARCH-054-BACKGROUND-003 (pending) |
| [ARCH-054-SYSTEM-TEST-002](../decisions/system-test/ARCH-054/SYSTEM-TEST-002-certify-delayed-ai-capacity-and-repair.md) | pending | 0 | ARCH-054-SYSTEM-TEST-001 (pending); ARCH-054-BACKGROUND-003 (pending) |

## Validation and publication boundaries

- Architect provider regression run: 1 suite / 31 tests passed on BG013 `4fdc5c8` with Node 24.19.0.
- Docker daemon probe returned 29.5.2; no BG054 integration success is inferred.
- No system suite was launched and no new scenario coverage is claimed.
- Structural metadata checks passed: unique task IDs, task/path identity, no missing or superseded active prerequisites, no active dependency cycles, and every Ready task has Complete prerequisites. Documentation whitespace is checked before publication.
- Coordination changes are published on a dedicated documentation branch. Existing implementation branches and main are not merged by the architect.



## Remaining work count

35 active tasks remain: 26 system-certification tasks and 9 implementation/deferred tasks. 14 system-certification tasks are Ready for manual execution. Superseded records are excluded.
