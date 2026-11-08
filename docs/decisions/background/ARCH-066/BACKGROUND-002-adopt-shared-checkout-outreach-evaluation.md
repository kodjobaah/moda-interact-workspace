---
id: ARCH-066-BACKGROUND-002
architecture_id: ARCH-066
title: Use shared read-only outreach evaluation in Background
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: in_progress
priority: 50
executor: codex
claimed_at: 2026-11-08T20:41:44Z
attempt: 1
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

## Execution ownership amendment — 2026-11-08
Developer explicitly invoked moda-task agent implementation and authorized synchronization/claim/source/report publication. Ready Attempt0/unclaimed with Complete001/005; agent execution is authorized, completion remains developer. Preserve checkout-led withdrawal and real checkout/send ownership. Use the exact accepted5.8.0 artifact/integrity already adopted by completed BACKGROUND001 and published by SHARED010; it includes accepted005 outreach exports, so do not downgrade the prerequisite implementation to5.7.0 or mutate published code. No live/main/standalone/follow-on execution.
