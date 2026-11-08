---
id: ARCH-066-SHARED-004
architecture_id: ARCH-066
title: Extract read-only checkout outreach evaluation and rendering
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-066-SHARED-001", "ARCH-066-SHARED-002"]
enables: ["ARCH-066-SHARED-003"]
created: 2026-11-08
updated: 2026-11-08
---
# Extract read-only checkout outreach evaluation and rendering

## Scope and exact work
Read ARCH-066 and its two sequence diagrams. This task is definition only; implement only after dependencies complete, in canonical task worktrees. You are not alone in the codebase; preserve unrelated edits. No merchandise-specific assumptions or new per-category schema.

Own Shared only: NEW `src/commerce/outreach/{contracts,evaluate,render,index}.ts`, package export `./commerce/outreach`, export/build tests and lockfile if needed. Port the reusable read-only decisions from Background `src/agents/initial-outreach-offer.{types,graph,eligibility,combinations,instructions}.ts`, `initial-outreach-offer-product-target.ts`, and pure initial-template parameter/rendering helpers called by `src/services/recovery-template-integration/automated-recovery-template.service.ts`. Do not import Background or copy DB/send orchestration.

Export `evaluateInitialOutreachPreview(input,ports)` and `renderInitialOutreachPreview(input)`. Zod input is strict schemaVersion=1, server-resolved shopId/platform/environment, pinned profile/instruction revisions, checkout currency/URL and ordered lines {lineKey,productId,variantId,quantity,checkoutUnitPrice}; 1..100 lines, positive safe integer quantity, existing native ID/money/URL validators. Preserve checkout quantities and historical prices separately from current product facts. No customer phone/email required. Existing production adapter supplies trusted recovery/attempt identities separately; preview uses run identity only and never produces a send-admission token.

Ports supply abort signal, exact authorized product reader, existing bounded model invoker/selector, resolved recovery policy, offer reader, clock and logger. Reuse current outreach eligibility/combinations/price reconciliation semantics; no alternate discount algorithm. Exact-read every distinct checkout product+variant at run start, including policy NONE; deduplicate reads but preserve line order/quantity. No catalogue search, replacement products or products outside checkout. Never guess missing IDs by title. Missing identity, deleted product, wrong parent/shop/provider or unavailable read yields structured line limitation and refuses a ready preview. No historical-price fallback labelled current. Recheck selected product/offer facts before rendering; recheck failure refuses. Current totals are merchandise totals only; never invent taxes/shipping or overwrite checkout totals.

Rendering uses the existing approved initial template contract, chosen locale/header and validated parameters; do not use MODA_CONVERSATION_WRAPPER. Preserve current escaping, parameter limits, offer terms and fallback classification. Return {kind:ready|refused,reasonCode,lineDiagnostics,productObservations,offerDecision,templateProvenance,parameters,headerPreview,renderedText,toolActivity}; all outputs bounded using existing contracts; no secrets/provider bodies. Same explicit observations/model decision/template inputs produce identical production/preview parameters and text. Missing template/locale/required parameter refuses. Header preview uses existing configured media reference; never upload/register with Meta. If a pure helper cannot be moved without changing behavior, preserve it behind an injected port and prove identical fixtures; no service imports.

Acceptance: both platforms, duplicate lines, variants, changed current price, NONE/FIXED/AI policies, eligible/ineligible/no offer, missing/deleted/foreign product, provider outage, malformed template, locale/header and Unicode bounds. Existing outreach golden decisions/rendering must remain identical except the explicitly required always-live product reads. No billing/delivery side effects.

## Completion report
Not started. Record implementation commit, scoped checks and parity evidence before completion. No production deployment or real message sending authorized.
