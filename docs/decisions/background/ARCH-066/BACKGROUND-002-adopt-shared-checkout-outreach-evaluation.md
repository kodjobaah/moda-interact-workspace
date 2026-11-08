---
id: ARCH-066-BACKGROUND-002
architecture_id: ARCH-066
title: Use shared read-only outreach evaluation in Background
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-066-SHARED-005", "ARCH-066-BACKGROUND-001"]
enables: ["ARCH-066-SYSTEM-TEST-002", "ARCH-066-COMMERCE-002"]
created: 2026-11-08
updated: 2026-11-08
---
# Use shared read-only outreach evaluation in Background

## Scope and exact work
Read ARCH-066 and its two sequence diagrams. This task is definition only; implement only after dependencies complete, in canonical task worktrees. You are not alone in the codebase; preserve unrelated edits. No merchandise-specific assumptions or new per-category schema.

Own Background only. Touch `src/services/recovery-offers/{initial-outreach-agent-context,initial-outreach-offer-selection,current-outreach-offer-revalidation}.service.ts`, `src/services/recovery-pricing/checkout-price-reconciliation.service.ts`, `src/agents/initial-outreach-offer.*`, `src/services/recovery-template-integration/automated-recovery-template.service.ts`, related Woo outreach adapters, package/lockfile and scoped tests.

Adopt exact version/integrity recorded by SHARED-005. Shared5.6.0 does not contain this export. Replace duplicated pure decisions/rendering with Shared delegates. Keep trusted checkout/attempt ownership, generation/fingerprint, policy/instructions and credential reads in Background. Adapt existing exact product reader into shared ports; ensure every checkout product/variant receives live verification even when recoveryOfferMode=NONE (currently price reconciliation is skipped in this mode). Preserve historical/current amounts distinctly. No unrelated catalogue recommendations for initial outreach.

Keep existing current-offer admission revalidation/token, transaction fences, recovery eligibility, credit reservation/settlement, outbox, moderation, Meta send and support notices in their existing production host. Shared preview result never substitutes for send admission. Use existing fallback policy only; never reinterpret a refused preview as an authorized message. Preserve existing no-offer production behavior when live verified products and configured policy permit it. Delete duplicate pure implementations after all callers delegate; maintain public entry points where callers need them.

Acceptance: unchanged existing initial outreach regressions, both provider fixtures, NONE live product read assertion, checkout generation change, offer expiry between selection/admission, replay/credit/send fences and byte parity with Shared renderer. Record exact fixture inputs/results for Studio parity; no real customer sends.

## Completion report
Not started. Record implementation commit, scoped checks and parity evidence before completion. No production deployment or real message sending authorized.

## Normative review correction
[Outreach contract](../../../architecture/ARCH-066-initial-outreach-contract.md) is mandatory. Use evaluateInitialOutreach and shared frozen-template rendering; no duplicated algorithm or arbitrary render callback. Preserve historical/current prices and checkout-only restriction. Production ALTERNATIVE_PRODUCT_PROMOTION is explicitly refused for this initial path; preserve historical receipt parsing and conversational recommendations. Ready media only in Studio; IMAGE unavailable selects approved TEXT fallback or refuses.

## Deterministic implementation checklist
- [ ] Apply outreach contract1–7 and consumer contract A/E. Keep production facade inputs/real attempt metadata, but map to shared evaluation input; decorate validated decision afterward. No fake attempt in Shared/Studio.
- [ ] Replace initial-outreach-offer graph pure logic and checkout price arithmetic with Shared delegates; context builder no longer skips current product observation in NONE. Existing admission revalidator remains production host and revalidates before sending; no shared result treated as admissionToken.
- [ ] Map old ALTERNATIVE_PRODUCT_PROMOTION to explicit initial-path refusal OUTSIDE_CHECKOUT, preserving previousPromise historical parsing and conversational graph. Include regression showing an offer on a non-checkout item cannot enter new initial message.
- [ ] Template preparer resolves repository/WABA/media outside shared rendering. Production may prepare derivative in existing media owner; pass ready frozen projection/variables to same shared renderer, retain binding fingerprints/assignment validation and send-fields shape.
- [ ] Tests prove price/quantity/offer mappings, NONE two exact reads, changed facts refused, credit/consent/admission/replay unchanged and prepared body equals Studio fixture. Existing fallback service may decide later production action but must not transform a shared identity/denial refusal into a permitted send.

## Release dependency reconciliation — 2026-11-08

SHARED-005 is Complete at accepted Attempt1, with accepted immutable `@modainteract/moda-interact-shared@5.7.0` and integrity `sha512-2/Ew2Blo83eY/LKthULJh84kHoJfq701e3RCpjPEQNXYnSai6IEQO08n4QNct1QzwWGyNxf9M2lokLlCHKyoXg==` (source `09e249c5717c8866996624f8855a7d649dfd2c43`). Use this exact artifact and canonical consumer contract; never guess/latest/ranges. Remaining explicit blockers: ARCH-066-BACKGROUND-001. Status Pending, unchanged Attempt0/unclaimed. No implementation, deployment or task claim is started by reconciliation.

## Dependency frontier — 2026-11-08
BACKGROUND001 explicitly Complete at Accepted Attempt2; Shared005 Complete immutable5.7.0 lineage retained (current corrected artifact5.8.0 available through accepted010). Both explicit prerequisites satisfied. Ready, unchanged Attempt0/unclaimed, execution/completion developer retained. This promotion does not execute or amend implementation scope; use `/moda_developer_create ARCH-066-BACKGROUND-002` when ready. No standalone publication or main/live action.

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
