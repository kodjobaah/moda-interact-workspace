---
id: ARCH-066-SHARED-007
architecture_id: ARCH-066
title: define canonical standalone turn identity
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: superseded
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on: ['ARCH-066-SHARED-005']
enables: ['ARCH-066-SHARED-008']
created: 2026-11-08
updated: 2026-11-08
---
# Define canonical standalone turn identity

## Architecture
ARCH-066; docs/architecture/ARCH-066-conversation-product-context-and-whatsapp-preview-parity.md and consumer-contract C/D. Coordinator moda_architect.

## Objective
Represent a true standalone conversational turn without a fabricated checkout recovery ID.

## Context
BACKGROUND001 proved published5.7 CommerceTurnIdentitySchema.checkoutRecoveryId required, live-budget recoveryId required and routing/worker/context helper recovery-only. Existing Conversation already has canonical standalone shop/customer relations. Never fabricate a recovery ID or waive consent to satisfy task. Preserve prior accepted history.

## Scope
Existing CommerceTurnIdentitySchema and canonical assertions/grant/runner turn contracts plus tests. Introduce explicit canonical conversation ownership scope with backward-compatible recovery parsing: recovery scope requires real checkoutRecoveryId; standalone scope forbids it and requires existing shopId/conversationId and existing actor/version identity. Preserve all existing expiry/replay/tenant/grant binding fields; canonical signatures/hashes cover scope and identity, no local alternative hash. No entitlement/consent permission is granted by standalone identity. Runner must not infer checkout facts or make recovery-only actions available absent recovery. Publish browser-safe schemas/types/validators once; no service source imports. Document exact consumer migration and fail-closed old/new behavior before implementation.

## Out of Scope
New schema/customer mapping, arbitrary entitlement policy, fake checkout/recovery facts, provider sends, live deployment, main merge or automatic follow-on work.

## Requirements
Real recovery unchanged, explicit standalone valid, fake/ambiguous/mixed identities reject; assertion/grant scope/tenant/replay tampering fails. Required schemas/types/runner call paths accept canonical standalone without recovery facts.

## Work Items
- [x] Existing CommerceTurnIdentitySchema and canonical assertions/grant/runner turn contracts plus tests. Introduce explicit canonical conversation ownership scope with backward-compatible recovery parsing: recovery scope requires real checkoutRecoveryId; standalone scope forbids it and requires existing shopId/conversationId and existing actor/version identity. Preserve all existing expiry/replay/tenant/grant binding fields; canonical signatures/hashes cover scope and identity, no local alternative hash. No entitlement/consent permission is granted by standalone identity. Runner must not infer checkout facts or make recovery-only actions available absent recovery. Publish browser-safe schemas/types/validators once; no service source imports. Document exact consumer migration and fail-closed old/new behavior before implementation.

## Interfaces / Contracts
Canonical published Shared turn/assertion/grant identity; existing Conversation/Shop/customer ownership. Host/service policy remains owning runtime responsibility.

## Dependencies
- ARCH-066-SHARED-005

## Enables
- ARCH-066-SHARED-008

## Acceptance Criteria
- [x] Real recovery unchanged, explicit standalone valid, fake/ambiguous/mixed identities reject; assertion/grant scope/tenant/replay tampering fails. Required schemas/types/runner call paths accept canonical standalone without recovery facts.

## Validation
- [x] Focused recovery compatibility/standalone missing/mixed/forged/replay vectors, declared typecheck/build. No publication/service integration.

## Stop Condition
Publish source/report and submit review, then STOP. Explicit developer completion required; no enabled task auto-start.

## Implementation Notes
Exact evidence in BACKGROUND001 blocked report. Background same task later adapts loader/router/budget using existing canonical customer/shop, language/consent/general-admission and send fences; no fake recovery. Return actual incompatible contract/policy to architect rather than choose a fallback grant.

## Completion Report
### Status
Ready for Review — canonical standalone ownership implemented, validated and published.
### Files Changed
README.md; scripts/validate-commerce-entrypoints.mjs; src/commerce/turn-identity.ts; src/commerce/standalone-turn.test.ts; src/commerce/schemas.ts; src/commerce/definitions.ts; src/commerce/selection.ts; src/commerce/runner/preflight.ts; src/commerce/runner/tool-policy.ts; src/commerce/runner/observability.ts.
### Work Completed
Introduced canonical conversationScope RECOVERY/STANDALONE strict ownership branches. Historical recovery payloads parse without added defaults or changed bytes and still require checkoutRecoveryId; explicit RECOVERY requires it; standalone strictly forbids that field, including own undefined/null. Canonical resolve/execute assertions reuse the same ownership branches, preserving their existing purpose/grant/release/version fields. No fabricated actor or new crypto: Shared had no actor field; established host/private-ingress actor/customer authentication remains authoritative.

Scoped grants bind ownership; standalone grants omit recovery ID, explicit recovery grants bind exact recovery ID, legacy unscoped grants remain recovery-only. Exported commerceTurnMatchesGrant validates schemas and scope/shop/conversation/version floor plus optional injected retention time. Runner supplies its existing clock, closes pre-existing expiry enforcement gap and rejects scope mismatch/expired grant before model/provider work. Current inbound-version/actor/lease/consent/entitlement remains host responsibility.

Optional bounded allowedConversationScopes marker on published descriptors and pinned per-tool grants is copied by canonical deduplication and bound by manifest/grant descriptor equality. Missing metadata means RECOVERY-only; standalone requires explicit STANDALONE on both pinned descriptor and grant plus independent current adapter authorization. Both tool-list and call enforce scope; arbitrary tool names/text cannot make recovery actions available. Legacy built-ins remain recovery-only. Standalone initial recovery outreach fails closed. Runner creates no recovery/checkout facts; no live/provider/service source changes.

Documented exact migration before implementation in README: readers/writers/scoped grant/adaptor rollout; old strict readers refuse new fields; legacy signed recovery bytes unchanged; direct raw-schema `.extend()` consumers migrate to canonical assertion schemas. No legacy recovery-ID binding retroactively claimed: old grants historically bound shop/conversation/version only; new scoped RECOVERY grants add exact recovery binding. Canonical serialization includes complete scope/identity/markers with no alternate hash.
### Validation Results
- Focused recovery compatibility + canonical contracts/selection/runner/purpose regression suite: `npx tsx --test src/commerce/standalone-turn.test.ts src/commerce/contracts.test.ts src/commerce/selection.test.ts src/commerce/runner/runner.test.ts src/commerce/purpose-profile.test.ts`: PASS 92/92, zero skips/failures.
- Final standalone focused suite after full-read/current-authorization fixture: `npx tsx --test src/commerce/standalone-turn.test.ts`: PASS 6/6.
- Declared `npm run typecheck`: PASS after initial missing type-only ToolDescriptor import was corrected. Final repeat after added fixture: PASS.
- `npm run build`: PASS ESM and declarations for all runtime changes; only documentation/tests/public-check additions followed.
- `node scripts/validate-commerce-entrypoints.mjs`: PASS clean-process public commerce/runner imports and regression assertions; adds public scope/helper exports and mixed standalone identity denial assertions.
- `git diff --check`: PASS.
- Deterministic vectors cover unchanged recovery/assertion output, standalone missing/mixed/null/undefined/reserved fake identities, strict resolve/execute fields, canonical signing-byte changes under scope/tenant/version/grant/release tampering, recovery binding, replay floor, exact expiry boundary/legacy retention gap, marker forgery/dedup/manifest mismatch, unknown scopes, list/call denial, standalone outreach denial, full safe read with independent current authorization and no checkout facts.
### Deviations
Architect-approved explicit descriptor/per-tool grant scope markers were required because generic published tools have arbitrary names and no canonical recovery-action metadata. Absence fails closed for standalone. Actor identity does not exist in current Shared turn/assertion schemas, so no new actor model was invented. Runner's pre-existing grant-expiry enforcement gap closed with existing injected clock, preserving historical payload bytes and intended retention fields. Strict turn unions replace object-only extension; migration documented.
### Assumptions
A syntactically valid recovery ID is never proof of a real owned recovery; host validates canonical persisted Conversation/Shop/CheckoutRecovery relations and trusted actor. Identity/scope/marker never grants consent, entitlement, read authorization or send permission. Producer scope marking only for actually implemented safe adapters remains owning service task.
### Unresolved Issues
None scoped. No service integration or deployment claimed.
### Architectural Concerns
No fake checkout facts, recovery actions for absent scope, permissions or runtime registry inferred from conversational identity.
### Git / VCS
Task branch: task/ARCH-066-SHARED-007.

Physical isolation from prepared packet:
- canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
- parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-066-SHARED-007
- parent branch: task/ARCH-066-SHARED-007
- implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-066-SHARED-007
- implementation branch: task/ARCH-066-SHARED-007
- shared/default checkouts switched or mutated for task implementation: no
- another task worktree reused: no
- active product-detail SHARED-009/010 worktrees/source/claims touched: no

Start-of-attempt synchronization from prepared packet:
- parent remote task branch fast-forwarded: not-needed
- parent origin/main incorporated: already-current
- implementation remote task branch fast-forwarded: not-needed
- implementation origin/main incorporated: already-current
- recursive submodule sync/update: passed; no entries; ready
- Attempt 1 claim 254e5511eab89c651f51b2f0fba827aeefd7e758 pushed; no duplicate claim

Implementation b10fe65779839c46bfbc31aaae88421f1e7b908d pushed to origin/task/ARCH-066-SHARED-007; implementation tree clean. Parent report committed/pushed on matching task branch after this edit; exact report commit available in task Git history. Submodule gitlink staged: no. Main branches merged/pushed: no. Package version changed/published: no. Enabled tasks started: no.

## Architect Review
### Review Status
Accepted — explicit developer completion pending.
### Review Notes
Inspected actualb10fe65779839c46bfbc31aaae88421f1e7b908d and report10fb6a8ca0381d3ac5bb0a8dff41830acdab2dc0. Strict canonical legacy/RECOVERY/STANDALONE identity/assertions represent real standalone without invented recovery. Legacy omitted-scope recovery parsed bytes remain unchanged; explicit RECOVERY requires/binds recoveryId, standalone forbids own recovery field even null/undefined. No actor/signature field invented where existing Shared has none; host authentication/consent/version authority explicit.

Scoped grants bind scope/shop/conversation/version/expiry, old unscoped grants recovery-only. Immutable descriptor/grant allowedConversationScopes markers must exactly match and explicitly include standalone; absence is recovery-only. Runner list/call filters and existing authorization remain mandatory, standalone recovery-outreach purpose denied. No generic name inference, fake checkout facts or identity-derived permission. Existing grant expiry gap closed with injected runner clock; compatibility/migration limits documented. No outstanding correction.
### Reviewed Files
turn-identity.ts, schemas/definitions/selection, runner preflight/tool-policy/observability, focused standalone/assertion/runner tests, README migration and public entrypoint script.
### Validation Reviewed
92 focused tests and final6 standalone fixtures passed, declared typecheck/full ESM+DTS build/public clean-process commerce+runner imports/diff checks passed. Recovery compatibility/HMAC bytes, strict missing/mixed identity, scope/tenant/recovery/version/expiry tamper, descriptor/grant marker equality, complete safe standalone read/current revocation and standalone outreach denial covered. Actor auth and current persisted owner/version remain service responsibilities.
### Architecture Conformance
Conforms to bounded Shared standalone correction, no service/MCP/Background/live/source duplication or package publication. Canonical isolated worktrees/preparation/claim/publication evidence verified. Concurrent coordinator resolved ID collision by retiring unclaimed old product-detail007 and moving that task to active009; current007 unique standalone,009/010 claims/source untouched. No reset/rebase/main/consumer/release execution.
### Follow-up
Explicit completion: `/moda_developer_update ARCH-066-SHARED-007 complete`. Existing SHARED008 standalone publication and MCP002 consumer correction remain gated, materialize exact definitions from Background39d66aab when needed. Background remains Blocked until corrected artifact/private admission and actual standalone host integration. No enabled task auto-start or integrated/deployed completion claim.

## Checkout-led scope amendment — 2026-11-08

This amendment supersedes earlier standalone-production-conversation requirements, including consumer contract C1 and the standalone prerequisite reported by BACKGROUND-001. It preserves historical reports, attempts and acceptance evidence; it does not accept, complete, reclaim or start any task.

- Every production conversation in this scope originates from a real abandoned checkout/CheckoutRecovery. Initial outreach uses that checkout; subsequent CommerceAgent turns retain the same recovery identity even when discussing other products. No independent customer-start conversation, new admission/recipient/consent policy or fabricated recovery ID is required.
- Background resolves the current conversation's real CheckoutRecovery and its shop/customer through existing routing. Missing recovery or conflicting tenant/owner fails closed before model/provider I/O under existing admission rules. Preserve current consent/window/billing/outbox fences. Conversation.shopId, when populated, must agree with recovery ownership; it is not an alternate admission route.
- Studio conversational preview remains an isolated, explicitly synthetic test using its existing preview identity. Do not persist a fake production recovery/customer, weaken live MCP authorization, or add a production standalone route to accommodate preview. Initial-outreach testing remains COMMERCE-002: select an existing same-shop checkout recovery and verify its items using live product reads. Synthetic conversational preview must not claim production admission was evaluated.
- Retain generic product references, fresh authorized fact verification, shared WhatsApp composition, budgets, wrapper provenance, storage fencing and parity requirements. These apply to any merchant goods. No new table/schema is needed for standalone admission. Keep the existing ARCH-066 reference-context table and its recovery-linked owner checks.
- SHARED-007/008 and MCP-002 standalone support is withdrawn from the required acceptance/dependency path for this checkout-led scope. Any existing work is subject to review for removal of unused standalone-only identity/admission branches; do not remove existing supported recovery behaviour or rewrite immutable published artifacts. This does not withdraw SHARED-009/010's independent productDetailSelections/PRODUCT_DETAILS compatibility correction and immutable publication. Consumers must wait for that accepted correction when using those fields; do not locally fork Shared schemas.

### Mandatory review corrections

Review BACKGROUND-001 and COMMERCE-001 against this amendment before acceptance. Inspect the actual implementation and require corrections on their same task branches: remove newly introduced standalone-only routing/budget/authorization code that has no checkout-led or isolated-preview caller; retain real recovery ownership rejection; confirm product-context persistence and verified WhatsApp body composition; prove missing recovery is rejected and a later product question retains the original recovery. For Commerce also prove synthetic preview stays isolated, real-checkout outreach preview remains separate, and no fabricated production records or weakened grants were added. Preserve and re-run relevant existing tests after corrections; report exact files, package pin/integrity, call order and final body evidence. A historical standalone blocker alone is no longer grounds to reject recovery-linked behaviour. Other genuine blockers, unfinished acceptance work and manual system-test gates remain in force. Do not declare acceptance from partial provider tests.

### Review disposition for this correction task

The standalone-production objective above is superseded by the checkout-led amendment. No new standalone identity/admission implementation is required by ARCH-066. At review, assess any partial changes for unused scope and preserve the published recovery contract. Record a scope-withdrawal disposition rather than claiming implementation completion. Do not publish a standalone package merely to unblock BACKGROUND-001. Existing claim/status/history are preserved pending review.

## Explicit Developer Scope-Withdrawal Decision — 2026-11-08
Developer explicitly directed: follow checkout-led amendment, record ARCH-066-SHARED-007 superseded and do not publish SHARED-008. Status superseded (valid project lifecycle value), unchanged Attempt1, executor/claimed_at null. This is withdrawal of the standalone-production objective, not successful implementation completion. Historical Accepted technical review/sourceb10fe65779839c46bfbc31aaae88421f1e7b908d retained for audit; no source rollback/main merge/package publication performed. Unpublished standalone-only source must not enter release merely to unblock Background. Existing immutable published recovery artifacts and independent product-detail009/010 remain untouched. SHARED008/MCP002 standalone definitions retired as superseded, no claims or execution.
