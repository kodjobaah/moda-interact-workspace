---
id: ARCH-066-SYSTEM-TEST-002
architecture_id: ARCH-066
title: Verify checkout outreach preview and Background parity
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-066-COMMERCE-002", "ARCH-066-BACKGROUND-002"]
enables: []
created: 2026-11-08
updated: 2026-11-08
---
# Verify checkout outreach preview and Background parity

## Scope and exact work
Read ARCH-066 and its two sequence diagrams. This task is definition only; implement only after dependencies complete, in canonical task worktrees. You are not alone in the codebase; preserve unrelated edits. No merchandise-specific assumptions or new per-category schema.

Own system-test only. NEW `src/scenarios/arch066-initial-outreach-preview.js`, deterministic fixture files, existing scenario registration, provider harness and WhatsApp emulator.

For Shopify and WooCommerce seed checkout lines with native parent/variant IDs, historical prices and quantities; provider fixture returns changed current prices/details. Run actual Studio route and Background host with identical pinned profile/policy/model-decision/template/locale/clock inputs. Compare selected checkout IDs, fresh observations, reconciliation, offer selection, complete template parameters/header reference and rendered initial text. Assert provider exact reads for every distinct line identity including NONE policy. Do not call live merchants in deterministic suite; separately record optional Render TEST smoke as live verification.

Matrix: clothing, nail varnish, trees and unseen attribute; duplicate lines; deleted/foreign/wrong-parent IDs; 0/101 lines; invalid currency/quantity; price changes; eligible/ineligible/expired/no offer; fingerprint changes; missing locale/template/header parameter; denied role; cancellation/replay/purge; provider outage. No unrelated product search allowed. Studio must create no recovery/attempt/credit/customer/outbox/send/Meta mutation; Background sends only through emulator using existing gates. Compare production send-admission assertions separately from pure rendering parity. Existing conversational and initial-outreach regression scenarios remain passing.

Record pinned commits/package integrity, fixture hashes, commands, run IDs and exact comparison artifacts. Disposable integration run required; unit tests alone do not complete task.

## Completion report
Not started. Record implementation commit, scoped checks and parity evidence before completion. No production deployment or real message sending authorized.

## Review corrections
Use the normative outreach contract and new SHARED-005 exact artifact. Assert ordered initial/revalidation product calls (NONE exactly two per distinct pair), zero model/offer calls for NONE, checkout-only rejection of alternative-product promotion, changed-fact refusal and READY-media/TEXT fallback parity. Exercise actual app/api/studio/preview/initial-outreach routes including list, start, status and cancel, status codes and tenant ownership. Fixture model responses and observed clock fixed; no stochastic wording comparisons. Preserve production admission regression tests separately.

## Deterministic implementation checklist
- [ ] Register arch066-initial-outreach-preview in existing scenario catalogue and package script test:arch066:outreach using existing harness. Pin Shared005/database/Background/Commerce commits and record commands.
- [ ] Run all contract7 cases through both platform fixtures and actual Studio routes/Background host. NONE ready call trace exactly two get_product per distinct pair, checkout duplicate quantities unchanged, zero model/offer/search. FIXED/AI scripted offer decisions use bounded ports; current-facts change refuses before rendered ready.
- [ ] Seed ready R2 IMAGE projection, missing IMAGE with approved TEXT fallback, and missing both assignments; compare provenance/full params/header/body with Background same explicit inputs. No media generation or Meta requests from Studio.
- [ ] Persist machine-readable PASS/FAIL artifacts and exact text/parameter equality; tests assert zero forbidden writes and actual emulator delivery fences. Required skipped scenario blocks completion; screenshots/unit-only evidence insufficient.

## Checkout-led scope amendment — 2026-11-08

This amendment supersedes earlier standalone-production-conversation requirements, including consumer contract C1 and the standalone prerequisite reported by BACKGROUND-001. It preserves historical reports, attempts and acceptance evidence; it does not accept, complete, reclaim or start any task.

- Every production conversation in this scope originates from a real abandoned checkout/CheckoutRecovery. Initial outreach uses that checkout; subsequent CommerceAgent turns retain the same recovery identity even when discussing other products. No independent customer-start conversation, new admission/recipient/consent policy or fabricated recovery ID is required.
- Background resolves the current conversation's real CheckoutRecovery and its shop/customer through existing routing. Missing recovery or conflicting tenant/owner fails closed before model/provider I/O under existing admission rules. Preserve current consent/window/billing/outbox fences. Conversation.shopId, when populated, must agree with recovery ownership; it is not an alternate admission route.
- Studio conversational preview remains an isolated, explicitly synthetic test using its existing preview identity. Do not persist a fake production recovery/customer, weaken live MCP authorization, or add a production standalone route to accommodate preview. Initial-outreach testing remains COMMERCE-002: select an existing same-shop checkout recovery and verify its items using live product reads. Synthetic conversational preview must not claim production admission was evaluated.
- Retain generic product references, fresh authorized fact verification, shared WhatsApp composition, budgets, wrapper provenance, storage fencing and parity requirements. These apply to any merchant goods. No new table/schema is needed for standalone admission. Keep the existing ARCH-066 reference-context table and its recovery-linked owner checks.
- SHARED-007/008 and MCP-002 standalone support is withdrawn from the required acceptance/dependency path for this checkout-led scope. Any existing work is subject to review for removal of unused standalone-only identity/admission branches; do not remove existing supported recovery behaviour or rewrite immutable published artifacts. This does not withdraw SHARED-009/010's independent productDetailSelections/PRODUCT_DETAILS compatibility correction and immutable publication. Consumers must wait for that accepted correction when using those fields; do not locally fork Shared schemas.

### Mandatory review corrections

Review BACKGROUND-001 and COMMERCE-001 against this amendment before acceptance. Inspect the actual implementation and require corrections on their same task branches: remove newly introduced standalone-only routing/budget/authorization code that has no checkout-led or isolated-preview caller; retain real recovery ownership rejection; confirm product-context persistence and verified WhatsApp body composition; prove missing recovery is rejected and a later product question retains the original recovery. For Commerce also prove synthetic preview stays isolated, real-checkout outreach preview remains separate, and no fabricated production records or weakened grants were added. Preserve and re-run relevant existing tests after corrections; report exact files, package pin/integrity, call order and final body evidence. A historical standalone blocker alone is no longer grounds to reject recovery-linked behaviour. Other genuine blockers, unfinished acceptance work and manual system-test gates remain in force. Do not declare acceptance from partial provider tests.

### Pull reconciliation — 2026-11-08

The checkout-led requirements above are preserved as scope history. Later published Accepted reviews/completion decisions and immutable release evidence in this file remain authoritative; the earlier requirement to review before acceptance does not reopen those accepted attempts. Current required product-detail correction artifact is the accepted SHARED-010 release (5.8.0); earlier5.7.0 handoff text remains historical. No lifecycle decision, execution or new release is authorized by this pull reconciliation. Terminal system-test execution remains manually gated.
