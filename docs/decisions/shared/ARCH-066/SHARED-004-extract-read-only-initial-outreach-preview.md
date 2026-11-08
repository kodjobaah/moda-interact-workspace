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
status: review
priority: 50
executor: null
claimed_at: null
attempt: 1
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
- [x] Strict schema fixtures and all closed refusal reasons from contract section5; malformed nested payload rejected before use.
- [x] Ordered port-call spy: ready NONE reads each distinct checkout pair exactly twice, never model/offer/search; duplicate lines retain their quantities/order.
- [x] Changed-price/current-facts, currency, missing product, wrong parent/tenant, revoked access, cancellation, deadline and exhausted-budget tests.
- [x] Existing checkout-offer goldens preserved except explicit checkout-only restriction; no stale checkout price used as live evidence.
- [x] Both-provider fixtures for clothing/nail varnish/trees/custom label; identical code path and no merchandise enum.
- [x] Exact prepared-template parameter/body/header goldens, no-ready-image TEXT fallback, missing approved template/locale, escaped/control/Unicode/4096 boundaries.
- [x] Package typecheck/build, focused tests, `validate:commerce-outreach`, pack public import/declaration check and diff check. Record unavailable checks candidly; no claimed publication.

## Execution / completion
Attempt 1 implemented and submitted for developer reconciliation/review. Explicit developer completion remains required. Preserve unrelated edits; Shared owns no service repository edits. SHARED-005 publishes accepted source. No production send/deploy authorized.

Generic product payload validation uses accepted SHARED-006 implementation as source prerequisite; no competing schema edits. Source subtree ordering is006 then004, followed by005 publication.

## Dependency frontier reconciliation — 2026-11-08

ARCH-066-SHARED-006 is Complete at accepted Attempt 1, recorded and pushed in parent task commit `918e45713ff5ca80d7832ca46480ddb2514894a1`, with accepted implementation `2bc7f02c16840a41154f2135a26f9ba52c71fad7`. Together with completed SHARED-001 and SHARED-002, all explicit dependencies are satisfied. This task is Ready, unclaimed at Attempt 0; this reconciliation does not start implementation. SHARED-005 remains Pending until SHARED-004 completes.

## Completion Report

### Status

Ready for Review — Attempt 1. Implementation and report published; developer acceptance/completion pending.

### Preparation

Canonical launcher synchronized dedicated parent and implementation task worktrees, verified completed dependencies and recursive submodules, and set developer Attempt 1. Its report update stopped because the original definition lacked this section. Added the required section and published the existing claim without incrementing again. Explicit implementation and task-branch publication authorization retained; developer completion remains explicit.

### Implementation / source evidence

Implementation `2a31e9cd7202833bd4a35242e3999fed191a7289` is pushed to `origin/task/ARCH-066-SHARED-004`; local HEAD equals the remote tracking ref and the implementation worktree is clean. Source baseline `b8743a2` already contains accepted SHARED-006 `2bc7f02c16840a41154f2135a26f9ba52c71fad7` (ancestry verified). No competing generic product schemas, consumer changes or package version bump. Source package remains 5.6.0; this local packed artifact has not been published. SHARED-005 owns the immutable release.

28 task-owned files changed: package export/script and tsup entry; new `scripts/validate-commerce-outreach.mjs`; the outreach contracts/evaluator/reconciliation/selection/renderer and extracted pure eligibility, combinations, money, instructions, template bindings/summary/initial-slot/variable helpers; focused fixtures/tests and source-relocation README. Background source reference `d7e78bdb5e75248b9a15e2c84d07dcdc89027c19` was inspected read-only. No service repository was edited. Existing source algorithms are retained under Shared-local imports; model/tool services are replaced with injected ports. The deliberate checkout-only amendment excludes alternative-product search/promotion and rejects unexpected choices with OUTSIDE_CHECKOUT. Host recovery/admission identity and write/send fences remain outside Shared.

### Acceptance / implementation review report

- Strict public evaluation/render input/result schemas and inferred types; real nested eligibility/group/price/registration/binding validators replace source placeholder validation. Canonical Commerce product, currency, money, environment and tool contracts are reused. Input native IDs, unique line keys, nullable merchant revision pair, discount authorization and pre-I/O UTF8 bound are checked. Unknown tool names/arguments and malformed nested results fail closed; all closed evaluation refusal codes have exercised paths.
- Ready NONE has sequential first-occurrence exact reads before and after selection, deduplicated by product/variant pair; duplicates retain original line order and quantities. No model, offer or search calls occur in NONE. Current availability, exact parent/variant, provider and observation freshness are checked; authenticated tenant scoping is the host port's responsibility, with trusted run/shop/platform/signal supplied by Shared. Foreign output envelopes are rejected rather than trusted.
- Reconciliation retains historical and current unit prices, uses decimal-safe minor units and original quantities, and labels only a current merchandise subtotal. Fingerprint uses the ordered canonical price-basket content algorithm without host recovery/attempt identity. No payable-total or checkout-repricing proof is fabricated.
- FIXED reads authorized details only; AI lists bounded checkout options, reads tied details and submits identifier-only choices. Existing eligibility and max-three compatible combination algorithms remain authoritative, including unknown targeting/customer/usage restrictions and Shopify/Woo rules. Existing POLICY_NONE/NO_AUTHORISED_DISCOUNTS/NO_APPLICABLE_OFFER reason codes retained. Missing eligible discounts produce a successful no-offer decision. Malformed or outside-checkout choices refuse.
- Same signal, admitted deadline/model-step/remote-call/token budgets and bounded activity apply throughout. Every actual tool/model attempt counts, deduplicated reuse does not; no automatic retry loop. Cancellation/deadline overrides late results. Final reads verify every distinct product and every selected offer's details/eligibility. Observation timestamp refresh alone is not a fact change; changed facts or revoked access cannot return ready. No raw provider body/credentials enter diagnostics.
- Frozen registration/variant/binding field names and digest/token/slot/summary/parameter algorithms are preserved. Synchronous prepared variable/media resolution performs no DB/network/upload calls. Optional host-prepared approved TEXT fallback goes through the same selection/status/locale/hash checks when IMAGE lacks ready media. Exact parameter order, provenance and full text header/body/footer are tested; body 4096 UTF16 admitted and 4097 refused without truncating parameters/URLs/offer terms. Missing approved assignment, locale, bindings, values or media refuses. No conversation wrapper substitute.
- Both-provider clothing/nail-varnish/tree/custom-label fixtures use the same evaluator with open merchant facts. Existing product-fact/presentation/runner compatibility checks pass; no merchandise enum is introduced. Packed public imports include generic description/attributes, verifyCommerceProductFacts and PRODUCT_DETAILS alongside outreach.

### Validation

Node 24.19.0 from canonical workspace bootstrap; `npm ci --ignore-scripts` installed the existing lockfile with no dependency/version edits.

- `npm run typecheck`: passed after final source changes.
- `npx tsx --test src/commerce/outreach/*.test.ts src/commerce/product-facts.test.ts src/commerce/product-context.test.ts src/commerce/presentation/facts.test.ts src/commerce/presentation/presentation.test.ts src/commerce/runner/runner.test.ts`: **156 passed, 0 failed, 0 skipped**. Includes all new contract/reconciliation/assignment/offer/evaluation/render goldens and affected existing compatibility tests.
- `npm run build`: ESM plus declarations passed for final runtime source.
- `npm run validate:commerce-entrypoints`: passed; existing commerce/runner clean-process imports and R1/R2 regressions retained.
- `npm run validate:commerce-presentation`: passed in Node and browser-like bundled context, with no new browser export dependency on server globals.
- `npm run validate:commerce-outreach`: passed. Packs locally, installs that exact tarball in an isolated temporary project, typechecks all four public schemas and exported types/functions through the public declaration path, then evaluates deterministic NONE and renders a hash-verified ready frozen template through installed public JS. Verifies strict rejection, exact subtotal/call count/parameters/text/provenance, alias identity, prior presentation imports and generic description/attribute/PRODUCT_DETAILS compatibility. Temporary project removed; no npm publication.
- `git diff --check` and staged diff check: passed.
- Lint unavailable: package declares no lint script or lint dependency. It is not claimed passed, and unrelated tooling was not added.

### Isolation / publication / lifecycle

Canonical dedicated parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-066-SHARED-004` and implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-066-SHARED-004` were used on mirrored `task/ARCH-066-SHARED-004` branches. Deterministic developer preparation fetched/synchronized parent and implementation, verified the completed 001/002/006 dependency gate and recursive submodules, then set Attempt 1. Report-format repair and durable claim `3340bc39b` retained that same attempt. Current primary checkout was used only as canonical routing/read-only source reference. No subagent assistance was used in this attempt; the Codex root adopted moda_shared implementation scope under the developer's explicit implementation/publication authorization.

Implementation publication succeeded; this parent record is the corresponding review submission. No task branch was merged into main, no main push or feature gitlink staging, and no package release, migration, deployment or production message occurred. No known scoped acceptance item remains incomplete at submission. Formal `/moda_developer_update ARCH-066-SHARED-004` reconciliation/acceptance and subsequent explicit completion are pending; no passing Architect Review is fabricated here. Attempt stays 1, executor/claimed_at cleared for review. SHARED-005 remains Pending until this task is accepted and explicitly completed; no downstream task is claimed.
