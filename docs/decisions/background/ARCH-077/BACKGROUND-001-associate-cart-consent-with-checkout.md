---
id: ARCH-077-BACKGROUND-001
architecture_id: ARCH-077
title: Read Shopify abandoned checkout attributes through existing recovery verification
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 55
executor: copilot
claimed_at: 2026-11-17T20:27:28Z
attempt: 1
depends_on: [ARCH-077-SHOPIFY-001, ARCH-077-SHARED-001, ARCH-077-SHOPIFY-002]
enables: [ARCH-077-BACKGROUND-002, ARCH-077-SYSTEM-TEST-001]
created: 2026-11-17
updated: 2026-11-17
---

# Integrate authoritative Shopify checkout attributes into recovery candidates

**Pending; after accepted S002 and completed historical Shared/S001 dependencies.** The [signed-attribute receipt v1 contract](../../../architecture/ARCH-077/checkout-attribute-consent-v1.md) supersedes the former B001 Redis marker-to-checkout association and Redis consent cleanup task. No new marker map, consent TTL extension, Redis choice reader or consent-specific BullMQ job is required.

## Existing Background touchpoints (inspect actual repo before editing)

- Existing checkout-created/updated V2/V3 consumer, checkout candidate identity, mature-at calculation, verification/retry and order-completion paths. Preserve current queue names, job IDs, dueAt, pending indexes, locks and `pending-recovery:order-completed:*` tombstones.
- Existing authoritative `AbandonedCheckout` GraphQL query/service: ensure **only this already needed query** selects `customAttributes {key value}` on the matching checkout. Do not call Shopify again solely for consent; do not put receipt into the existing queue message or save it in Redis.
- Preserve original authenticated webhook checkout token and (where available) the cart token along the existing candidate identity. If existing candidate transport cannot prove they belong to the same abandoned checkout, stop: do not guess from basket items, timestamp, email, customer name, or reuse the optional old SHARED-001 marker fields.
- Provide typed `authoritativeCheckoutAttributes` and trusted webhook checkout/cart token input to B002's verifier **within the existing maturity handoff**, no new queue/evidence store. Do not decide or materialise GRANT/REVOKE in B001; B002 owns signed receipt verification, SQL consent revision and final proactive admission.

## Lifecycle and failure outcomes

- No B001 consent cleanup on cart empty, order completion, abandoned checkout materialisation or Redis TTL. Shopify's checkout owns its attribute lifecycle; B001 retains only *existing* worker indexes and retries. A completed/paid/terminal checkout does not create SQL consent or outreach.
- A missing attribute is `NO_EXPLICIT_CHOICE`; duplicate named attributes, malformed provider shape, missing authenticated event token, unavailable provider data or mismatched checkout identity are typed denial/defer, not a default GRANT. The actual HMAC decision is verified by B002; do not treat an unverified string as consent.
- Existing unrelated Redis cache, BullMQ and checkout queues continue as before. No new DB schema, Redis namespace, timed cleanup job or Shopify API call. Existing privacy logs and provider error redaction stay intact.

## Tests/acceptance

- The prior live non-Plus probe was present in GraphQL `customAttributes`. New tests must prove **signed consent receipt** survives from S003 cart into the same authoritative query; Plus S004 is tested separately.
- Mocked and disposable Redis worker tests: created/updated before/after maturity, duplicate/out-of-order events, missing/duplicate attribute, delayed provider visibility, completion and cancellation, no change to existing BullMQ job identities, indexes/TTL, billing, STOP or sender routing. Validate no extra GraphQL query solely for consent.
- If candidate lacks authenticated checkout/cart token needed by the receipt binding rules, return the exact blocker to architect; do not add back a marker correlation service or alter Shared schema unilaterally.

## Completion Report

Implemented in the Background worker:

- The existing bounded `AbandonedCheckouts` GraphQL query now selects `customAttributes { key value }`; no consent-only Shopify query was added.
- The matched checkout exposes typed `authoritativeCheckoutAttributes`. Valid entries and duplicates are preserved for downstream verification; malformed provider shapes are tagged rather than treated as an absent choice.
- The existing maturity path retains the candidate's authenticated checkout/cart tokens alongside the authoritative checkout result for B002's verifier. Receipt data is not added to a BullMQ payload, recovery seed, database record, or Redis state.
- Added lookup and maturity-path tests for receipt propagation, duplicates, malformed attributes, the existing checkout/cart token input, and the single authoritative query.

Validation:

- Focused Vitest: 3 files passed, 39 tests passed (`REDIS_URL=redis://localhost:6379 pnpm exec vitest run tests/unit/services/abandoned-checkout-lookup.service.test.ts tests/unit/services/checkout-recovery/recovery-materialization.service.test.ts tests/unit/services/checkout-recovery/recovery-snapshot-builder.service.test.ts`).
- TypeScript: `tsc --noEmit` passed.
- Focused ESLint on all changed TypeScript files passed.

Implementation commit: `0294ae1` (`feat(background): expose authoritative checkout attributes`), pushed to `task/ARCH-077-BACKGROUND-001`.

Physical worktree isolation:

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-077-BACKGROUND-001` on `task/ARCH-077-BACKGROUND-001`
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-077-BACKGROUND-001` on `task/ARCH-077-BACKGROUND-001`
- Shared workspace checkout switched/mutated for task work: no
- Shared implementation checkout switched/mutated for task work: no
- Another task worktree reused: no

Start-of-attempt synchronization, from the prepared launcher packet:

- Parent remote task branch fast-forwarded: not-needed; parent `origin/main` incorporated: already-current.
- Implementation remote task branch fast-forwarded: not-needed; implementation `origin/main` incorporated: already-current.

Recursive implementation submodules, from the prepared launcher packet:

- `git submodule sync --recursive`: passed.
- `git submodule update --init --recursive`: passed.
- Recorded submodule commit: `database` at `0a9edc7c0c30e0a405d89efec624bc9338b4ac17`.

Task status: review. Awaiting `moda_architect` review; no architect acceptance decision has been made by this agent.

## Architect Review

### Review Status

**Accepted — 17 November 2026 (Attempt 1, B001 scope only).** Task status is `complete`. Implementation commit `0294ae1` and parent Completion Report commit `4f122f6` are agent-reported pushed references. This acceptance does not merge either task branch or certify runtime deployment.

### Reviewed Files

- `moda-interact-background/src/domain/abandoned-checkout.ts`
- `moda-interact-background/src/services/abandoned-checkout-lookup.service.ts`
- `moda-interact-background/tests/unit/services/abandoned-checkout-lookup.service.test.ts`
- `moda-interact-background/tests/unit/services/checkout-recovery/recovery-materialization.service.test.ts`
- `moda-interact-background/tests/unit/services/checkout-recovery/recovery-snapshot-builder.service.test.ts`
- The submitted parent task Completion Report and the accepted ARCH-077 receipt-v1 contract.

### Review Notes and Architecture Conformance

1. The existing bounded `AbandonedCheckouts` GraphQL query now requests `customAttributes { key value }` **on the same lookup** already required to establish recoverability. Its existing count precheck, exact abandoned-checkout URL match and bounded candidate limit remain. No additional consent-only Shopify request is introduced.
2. The `AuthoritativeCheckoutAttributes` result distinguishes `available` (including an empty array) from `malformed`. It preserves original key/value pairs and duplicate consent-attribute names for BACKGROUND-002 to deny rather than silently choosing one. Missing/non-array or malformed provider data never becomes a synthetic GRANT.
3. The original authenticated `PendingRecoveryCandidate` retains its checkout token and optional cart token; `toLookupInput` preserves both, and the existing maturity flow passes the matched checkout alongside the candidate. BACKGROUND-002 must verify their binding against the signed receipt; B001 does not make a consent decision or persist the receipt to a queue, Redis or PostgreSQL.
4. Source review found no new Redis consent storage/TTL, marker association, scheduler, queue, separate consent query or change to existing BullMQ/pending-recovery ownership. Existing checkout, order, billing, sender and consent-final-send behaviour remains the responsibility of the existing pipeline and later tasks.
5. The supplied task report records a dedicated parent and implementation worktree, launcher start-of-attempt synchronization and recursive submodule initialization (`database` at `0a9edc7c0c30e0a405d89efec624bc9338b4ac17`). These are **reported worktree/launcher facts**, not independently verified against the developer's live Git worktrees.

### Validation Reviewed

The agent reports 39 focused Vitest tests (three test files), `tsc --noEmit` and focused ESLint passed. The architect inspected the test fixtures and assertions in the supplied ZIP but did **not** independently execute the suite or verify the remote commits. Keep reported results distinct from independently executed validations.

### Follow-up and Acceptance Boundary

- **BACKGROUND-002 may become `ready`.** It owns the unique `moda_wa_consent_v1` selection, Shared AEAD decryption, tenant/checkout/customer/recipient binding, malformed/duplicate rejection, recoverable-only PostgreSQL GRANT/REVOKE materialisation, idempotency, STOP and final proactive-send consent gate. It must not assume GraphQL contains an authenticated `cartToken`: the candidate supplies the token, while the abandoned-checkout lookup supplies the matching authoritative checkout.
- The non-Plus prior live probe proves attribute transport, not a real signed receipt's integrity or recipient binding. Actual signed-receipt readback, live Plus issuance, Background independent verification and integrated system-test evidence remain outstanding under their respective tasks.
- Do not restore Redis consent state/cleanup, add a consent-only GraphQL query, create a new queue or change the published Shared contract solely to pass B002. If B002 cannot implement the approved existing-schema materialisation/idempotency contract, it must report the precise architect blocker rather than invent schema changes.

**Decision:** Accept ARCH-077-BACKGROUND-001 as a bounded authoritative attribute-lookup integration. Only the task status and its explicitly dependent Background-002 readiness are advanced; no deployment or end-to-end certification is implied.
