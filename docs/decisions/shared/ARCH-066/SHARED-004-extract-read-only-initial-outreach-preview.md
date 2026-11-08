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
depends_on: ["ARCH-066-SHARED-001", "ARCH-066-SHARED-002", "ARCH-066-SHARED-006"]
enables: ["ARCH-066-SHARED-005"]
created: 2026-11-08
updated: 2026-11-08
---
# Extract read-only checkout outreach evaluation and rendering

## Normative contract
Implement [the complete outreach contract](../../../architecture/ARCH-066-initial-outreach-contract.md), sections1–7. It fixes exported schemas/signatures, strict input/result shapes, source relocation, ordered live reads, error mapping, offer behavior, rendering and tests. It overrides the earlier shell definition. No architecture choices are delegated to the implementor.

## Owned files and work
- NEW `src/commerce/outreach/{contracts,evaluate,reconcile,selection,render,index}.ts` and matching `.test.ts` files; public package export `./commerce/outreach` and build/export checks. Internal pure helpers may be split under this directory only.
- Port sources listed in contract section3, including actual pure template helpers in `recovery-template-preparation`, not the service facade. Export evaluateInitialOutreach with preview alias; one implementation for production/preview.
- All public payloads use strict Zod and inferred types. Replace source z.custom placeholders for nested price/eligibility/combination data with actual field validators; canonical money/product/tool/offer schemas reused.
- Live exact product reads before selection and revalidation after selection, including NONE; sequential first-occurrence order, duplicate reuse, no catalogue search. Preserve checkout quantity and historical price. Existing production fingerprint/admission IDs stay host-owned.
- NONE uses zero model/offer calls. Existing bounded checkout-offer graph/eligibility/combination rules apply otherwise. New checkout-only schema rejects alternative-product choices; historical parsing stays host-owned.
- Render frozen approved initial template bindings using the same checkout summary/selection/parameter algorithms in both hosts. Prepared media and catalogue inputs only; no upload/DB/send orchestration. No conversation wrapper substitution.
- Add `scripts/validate-commerce-outreach.mjs`, registered as `validate:commerce-outreach`; import all four public schemas, evaluator and renderer from packed public JS/declarations. This task builds/packs locally but does not publish.

## Required acceptance evidence
- [ ] Strict schema fixtures and all closed refusal reasons from contract section5; malformed nested payload rejected before use.
- [ ] Ordered port-call spy: ready NONE reads each distinct checkout pair exactly twice, never model/offer/search; duplicate lines retain their quantities/order.
- [ ] Changed-price/current-facts, currency, missing product, wrong parent/tenant, revoked access, cancellation, deadline and exhausted-budget tests.
- [ ] Existing checkout-offer goldens preserved except explicit checkout-only restriction; no stale checkout price used as live evidence.
- [ ] Both-provider fixtures for clothing/nail varnish/trees/custom label; identical code path and no merchandise enum.
- [ ] Exact prepared-template parameter/body/header goldens, no-ready-image TEXT fallback, missing approved template/locale, escaped/control/Unicode/4096 boundaries.
- [ ] Package typecheck/build, focused tests, `validate:commerce-outreach`, pack public import/declaration check and diff check. Record unavailable checks candidly; no claimed publication.

## Execution / completion
Definition review only. Pending, Attempt0/unclaimed preserved; no implementation started. Complete prerequisites before canonical task launch. Preserve unrelated edits; Shared owns no service repository edits. SHARED-005 publishes accepted source. No production send/deploy authorized.

Generic product payload validation uses accepted SHARED-006 implementation as source prerequisite; no competing schema edits. Source subtree ordering is006 then004, followed by005 publication.
