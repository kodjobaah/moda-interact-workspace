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
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-066-SHARED-003"]
enables: ["ARCH-066-COMMERCE-002"]
created: 2026-11-08
updated: 2026-11-08
---
# Use shared read-only outreach evaluation in Background

## Scope and exact work
Read ARCH-066 and its two sequence diagrams. This task is definition only; implement only after dependencies complete, in canonical task worktrees. You are not alone in the codebase; preserve unrelated edits. No merchandise-specific assumptions or new per-category schema.

Own Background only. Touch `src/services/recovery-offers/{initial-outreach-agent-context,initial-outreach-offer-selection,current-outreach-offer-revalidation}.service.ts`, `src/services/recovery-pricing/checkout-price-reconciliation.service.ts`, `src/agents/initial-outreach-offer.*`, `src/services/recovery-template-integration/automated-recovery-template.service.ts`, related Woo outreach adapters, package/lockfile and scoped tests.

Adopt exact SHARED-003 release containing SHARED-004 exports. Replace duplicated pure decisions/rendering with Shared delegates. Keep trusted checkout/attempt ownership, generation/fingerprint, policy/instructions and credential reads in Background. Adapt existing exact product reader into shared ports; ensure every checkout product/variant receives live verification even when recoveryOfferMode=NONE (currently price reconciliation is skipped in this mode). Preserve historical/current amounts distinctly. No unrelated catalogue recommendations for initial outreach.

Keep existing current-offer admission revalidation/token, transaction fences, recovery eligibility, credit reservation/settlement, outbox, moderation, Meta send and support notices in their existing production host. Shared preview result never substitutes for send admission. Use existing fallback policy only; never reinterpret a refused preview as an authorized message. Preserve existing no-offer production behavior when live verified products and configured policy permit it. Delete duplicate pure implementations after all callers delegate; maintain public entry points where callers need them.

Acceptance: unchanged existing initial outreach regressions, both provider fixtures, NONE live product read assertion, checkout generation change, offer expiry between selection/admission, replay/credit/send fences and byte parity with Shared renderer. Record exact fixture inputs/results for Studio parity; no real customer sends.

## Completion report
Not started. Record implementation commit, scoped checks and parity evidence before completion. No production deployment or real message sending authorized.
