---
id: ARCH-006-ADMIN-001
architecture_id: ARCH-006
title: Implement Admin merchant-support server capability
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 60
executor: copilot
claimed_at: 2026-09-06T18:20:00Z
attempt: 3
depends_on:
  - ARCH-006-DATABASE-002
  - ARCH-006-SHARED-002
  - ARCH-006-SHARED-004
  - ARCH-005-ADMIN-001
enables:
  - ARCH-006-ADMIN-003
created: 2026-09-05
updated: 2026-09-06T17:02:14Z
---

# ARCH-006-ADMIN-001: Implement Admin merchant-support server capability

## Architecture

`docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

## Objective

Provide protected Admin server-side thread/message queries and owner-enforced administrative compose/translation-recovery commands, with no support UI yet.

## Context

`ARCH-006-SHARED-004` is now architect-accepted Complete. Consume the exact corrected registry version `@modainteract/moda-interact-shared@0.7.1`. Do not consume an unpublished workspace copy and do not recreate equivalent local schemas, enums, validators, declaration shims or deterministic job-ID helpers.

Attempt 1 implemented the server capability and correctly returned control rather than starting `ADMIN-003`. Architect review found the implementation is not yet acceptable and has blocked the task pending the corrected Shared package release plus a bounded correction attempt.

### Published Shared Dependency

`@modainteract/moda-interact-shared@0.7.0` is historical and must not be used for the final implementation because its `merchant-communications/node` runtime export points at a nonexistent artifact.

`ARCH-006-SHARED-004` is now architect-accepted Complete. Consume the exact corrected registry version `@modainteract/moda-interact-shared@0.7.1`. Do not consume an unpublished workspace copy and do not recreate equivalent local schemas, enums, validators, declaration shims or deterministic job-ID helpers.

### Attempt 1 Architect Correction Contract

Attempt 1 production work is retained as the starting point. Attempt 2 is a correction, not a rewrite.

The correction is limited to:

1. corrected Shared package consumption;
2. message-kind-derived translation direction for additional translations;
3. Shared language-tag schema validation for additional targets;
4. correct reuse/enqueue semantics for an already-existing additional translation;
5. bounded Redis producer lifecycle;
6. focused tests for the acceptance-critical behavior listed below.

If satisfying the correction requires changes outside the explicit file scope below, stop and return `blocked` to `moda_architect`. Do not broaden the task.


### Attempt 3 Architect Correction Contract

Attempt 2 correctly repaired Shared `0.7.1` consumption, translation direction, Shared language validation, status-aware dispatch and the Redis producer lifecycle. Independent architect review found one remaining response-boundary defect in the retained compose transaction.

For a non-English merchant target, `composeAdministrativeMessage()` currently creates an `ADMINISTRATIVE` message in `PROCESSING` state but also advances `lastAdministrativeMessageAt` and clears `needsAdminResponse` immediately. ARCH-006 requires those two response-completion transitions only when the required `ADMIN_TO_MERCHANT` translation becomes `AVAILABLE`; that later transition is owned by `ARCH-006-BACKGROUND-006` and must re-check `respondsThroughMerchantVersion` against the then-current `merchantMessageVersion`.

Attempt 3 is therefore a narrow correction, not a rewrite:

1. an English target may continue to create `AVAILABLE` and clear the matching pending-response boundary in the compose transaction;
2. a non-English target must create `PROCESSING` + PENDING translation and update ordinary message chronology, but **must not** clear `needsAdminResponse` or advance `lastAdministrativeMessageAt` at compose time;
3. preserve `respondsThroughMerchantVersion` so BACKGROUND-006 can perform the eventual availability/boundary transition safely;
4. strengthen the focused test so the English and non-English branches prove these different thread-update semantics;
5. while touching the existing additional-translation focused test, assert that a canonicalisable input such as `en-gb` is persisted/looked up as canonical `en-GB`.

Do not modify Shared, Background, the database submodule, actions, UI, ownership workflow or the stale out-of-scope ARCH-005 `0.7.0` regression assertion in this correction.

## Scope

Admin repository server/data modules/actions and focused authorization/transaction tests. No visual inbox implementation.

### Attempt 2 File Boundary

Production changes are permitted only in:

- `package.json` — update the Shared dependency to the exact SHARED-004 published version only;
- `package-lock.json` — lockfile consequence of that exact dependency update only;
- `src/lib/admin/merchant-support.ts` — bounded corrections described in this task;
- `src/types/shared-merchant-communications.d.ts` — **delete** the temporary `0.7.0` declaration shim; remove `src/types/` only if it becomes empty;
- `tests/security/admin-merchant-support.test.mjs` — create/update focused tests for this task.

`src/app/actions/merchant-support.ts` is **read-only for Attempt 2** unless an acceptance test proves its existing action signature is wrong. If that occurs, stop and return `blocked` rather than changing the action contract without architect review.

No other source file is authorised.


### Attempt 3 File Boundary

Production/test changes are permitted only in:

- `src/lib/admin/merchant-support.ts` — correct the English versus non-English pending-response transition described above;
- `tests/security/admin-merchant-support.test.mjs` — prove the corrected branch behavior and canonical target persistence.

No package, lockfile, action, auth, Prisma/database-submodule, UI, queue-monitor, observability or other source file may change in Attempt 3.

## Out of Scope

- Ownership claim/release/reassign workflow (`ADMIN-003`).
- Admin inbox UI (`ADMIN-004`).
- Direct OpenAI calls or translation result application.
- Direct retry logic against failed BullMQ jobs.
- Generic `kind`, direction, admin identity, shop identity or language provenance supplied by a client.
- Any change to `moda-interact-background`, `moda-interact-shared`, or the database submodule.
- Any change to Admin auth, queue-monitor, observability, navigation or existing ARCH-005 internationalisation code.
- New testing frameworks or unrelated dependencies. If the existing test harness cannot prove a required invariant without a new framework/dependency, stop and return `blocked` for architect direction.

## Requirements

Read/query capability:
- authenticate active PlatformAdmin using existing guards;
- bounded shop/thread search/history and translation views;
- mark MERCHANT `readAt` first-read stable; reading does not clear pending;
- no cross-auth spoofing.

Compose capability:
- current admin identity is server-derived;
- transaction re-checks `thread.assignedPlatformAdminId == currentAdmin.id`;
- SUPER_ADMIN does not bypass thread ownership for sending;
- validate plain text with shared 1..500 grapheme schema;
- create only `ADMINISTRATIVE`;
- source language snapshot is `en-GB` platform support language;
- target/display snapshot comes from trusted shop `ShopSettings.defaultLanguageTag`/accepted ARCH-005 source;
- snapshot `respondsThroughMerchantVersion`.

English target (primary language `en`): create message `AVAILABLE`, no translation row/job, set `availableAt` and `lastAdministrativeMessageAt`, and clear `needsAdminResponse` in the same transaction only if the response boundary still matches.

Non-English target: create message `PROCESSING` + one PENDING `ADMIN_TO_MERCHANT` translation (`en-GB` -> target); commit first, then best-effort deterministic dispatch enqueue. Redis failure does not fail/delete the message.

Additional translation request:
- validate/canonicalise `targetLanguageTag` with the published Shared `LanguageTagSchema` from the internationalisation entrypoint; do not use a local regex or bare `Intl.Locale` as the validation boundary;
- load both `kind` and `sourceLanguageTag` from the durable message; the client must not provide direction or source language;
- derive direction only from the persisted message kind:
  - `MERCHANT` -> `MERCHANT_TO_ADMIN`;
  - `ADMINISTRATIVE` -> `ADMIN_TO_MERCHANT`;
  - `SYSTEM` -> `SYSTEM_TO_MERCHANT`;
- use the canonical target for `requiresMerchantTranslation`, uniqueness lookup and persistence;
- if source and target have the same base language, create no translation and enqueue no job;
- otherwise create/reuse the unique `(messageId, targetLanguageTag)` translation without changing `originalBody`;
- if the row already exists and is `AVAILABLE`, return/reuse it without dispatching work;
- if the row is `PENDING`, a best-effort deterministic dispatch hint is permitted;
- if the row is `FAILED`, do not bypass the reconciliation path by dispatching it directly; failed recovery is owned by the reconciliation commands below.

Failed translation recovery:
- any active PlatformAdmin with support read access may request targeted `TRANSLATION` reconciliation for a failed translation;
- `SUPER_ADMIN` may additionally create a bounded `FAILED_TRANSLATIONS` reconciliation request covering failed translations platform-wide;
- both commands persist `MerchantTranslationReconciliationRequest` first and may best-effort enqueue the shared reconcile hint;
- neither command inspects/removes BullMQ jobs or calls OpenAI;
- the request remains durable if Redis is down.

Shared runtime integration:
- after SHARED-004, import deterministic Node helpers from the corrected published `merchant-communications/node` entrypoint;
- remove the temporary local `.d.ts` declaration shim;
- do **not** catch module-resolution/import failures and disguise them as Redis outages. A broken package artifact is a build/deployment fault and should fail validation visibly;
- best-effort error handling should wrap the actual BullMQ enqueue operation, not the package import.

Redis producer lifecycle:
- do not construct an unbounded new BullMQ `Queue` connection for every server action invocation;
- reuse one module/process-scoped producer for the merchant-communications queue for the configured Redis URL, or otherwise deterministically close an internally-created producer after use;
- injected test queues must never be closed by production code.

## Work Items

Attempt 2 — now authorised because SHARED-004 is Complete:

- [x] Pin the exact corrected `@modainteract/moda-interact-shared` release published by SHARED-004 and update only the normal lockfile consequence.
- [x] Delete `src/types/shared-merchant-communications.d.ts`; do not replace it with another local declaration or helper.
- [x] Replace the `0.7.0` dynamic-import compatibility path with the corrected published Node helper entrypoint and keep Redis enqueue failure best-effort.
- [x] Validate additional `targetLanguageTag` using Shared `LanguageTagSchema`.
- [x] Query persisted message `kind` and derive translation direction using the exact three-way mapping in Requirements.
- [x] Preserve unique translation reuse and only dispatch durable PENDING work; AVAILABLE is reused without dispatch and FAILED uses reconciliation.
- [x] Bound the BullMQ producer lifecycle so repeated Admin actions do not leak Redis connections.
- [x] Add `tests/security/admin-merchant-support.test.mjs` covering the focused matrix below.
- [x] Run the complete Validation section.
- [x] Return this same task to `review` and STOP. Do not mark Complete and do not touch/promote `ADMIN-003`.


Attempt 3 — architect-authorised bounded correction:

- [x] Keep the English `AVAILABLE` compose path capable of advancing `lastAdministrativeMessageAt` and clearing `needsAdminResponse` only when the snapshotted merchant-message version still matches.
- [x] For non-English `PROCESSING` compose, do not advance `lastAdministrativeMessageAt` and do not clear `needsAdminResponse`; retain `respondsThroughMerchantVersion` for BACKGROUND-006.
- [x] Preserve `lastMessageAt`/message chronology for the newly-created administrative message without representing a PROCESSING reply as an available administrative response.
- [x] Strengthen focused tests to distinguish English immediate-availability behavior from non-English PROCESSING behavior.
- [x] Add the missing assertion that `en-gb` is canonicalised to `en-GB` before translation persistence/lookup.
- [x] Run focused tests, full repository validation as far as the known pre-existing stale `0.7.0` assertion permits, typecheck, lint, build, Prisma validation and `git diff --check`.
- [x] Return this same task to `review` and STOP. Do not mark Complete and do not touch/promote `ADMIN-003`.

## Interfaces / Contracts

Consumes the published SHARED-004 release and DATABASE-002 durable state. The UI later calls these accepted server capabilities.

Admin retry means **request reconciliation**, not “retry this BullMQ job”. Background owns job repair.

Translation direction is durable domain state derived from persisted message kind. It is never inferred from target language and never supplied by a client.

## Dependencies

Explicit task dependencies are listed in YAML frontmatter.

`ARCH-006-SHARED-004` is a hard correction dependency. The task may not return to Ready before SHARED-004 is architect-accepted Complete.

## Enables

`ARCH-006-ADMIN-003`

`enables` is informational only. The Admin agent must not mark `ADMIN-003` Ready, claim it, or begin it after returning this task for review.

## Acceptance Criteria

- [ ] Repository consumes the corrected SHARED-004 registry release for ARCH-006 shared contracts; no local declaration shim or structurally duplicated contract remains.
- [ ] Unauthenticated/inactive Admin is denied by the accepted auth guard path.
- [ ] Active non-owner may read but cannot send.
- [ ] Owner is rechecked at write time; SUPER_ADMIN does not bypass ownership.
- [ ] Body >500 graphemes is rejected server-side; complex Unicode is counted using the shared grapheme contract.
- [ ] English merchant target creates no translation/provider work.
- [ ] Non-English target creates durable PROCESSING + PENDING translation before enqueue.
- [ ] Queue failure leaves recoverable DB work and does not roll back/delete the committed message/translation or reconciliation request.
- [ ] Additional translation target is validated/canonicalised with Shared `LanguageTagSchema`.
- [ ] Additional translation direction is exactly `MERCHANT_TO_ADMIN`, `ADMIN_TO_MERCHANT`, or `SYSTEM_TO_MERCHANT` according to persisted message kind.
- [ ] Existing AVAILABLE additional translation is reused without dispatch; PENDING may receive a deterministic hint; FAILED is not directly redispatched.
- [ ] Original content is immutable and rendered/query-returned as text.
- [ ] Targeted retry creates durable reconciliation intent and works even if Redis enqueue fails.
- [ ] Platform-wide failed-translation reconciliation is SUPER_ADMIN-only and durable.
- [ ] Client cannot spoof admin, message kind, direction, shop identity or language provenance.
- [ ] Repeated server actions do not create an unbounded sequence of unreleased BullMQ Queue connections.
- [ ] Focused tests exercise the acceptance-critical paths; source-presence assertions alone are not sufficient for transaction/direction/queue-failure behavior where dependency injection can exercise the behavior.

## Validation

Create/update only `tests/security/admin-merchant-support.test.mjs` for new focused coverage.

The focused test matrix must include at minimum:

1. **Unicode body contract** — 500 user-perceived graphemes accepted and 501 rejected, including a multi-code-point emoji/grapheme case.
2. **Ownership** — assigned admin may compose; active non-owner is rejected; SUPER_ADMIN non-owner is also rejected.
3. **English branch** — creates AVAILABLE message, no translation row, no queue dispatch.
4. **Non-English transaction/order** — message + PENDING translation persist before queue invocation; queue failure occurs only after the transaction has committed and does not erase durable work.
5. **Direction mapping** — additional translation of persisted `MERCHANT`, `ADMINISTRATIVE`, and `SYSTEM` messages persists respectively `MERCHANT_TO_ADMIN`, `ADMIN_TO_MERCHANT`, and `SYSTEM_TO_MERCHANT`.
6. **Language validation** — a canonicalisable valid tag such as `fr-fr` persists as `fr-FR`; an invalid tag is rejected before a translation write.
7. **Existing-row semantics** — AVAILABLE is reused without dispatch, PENDING may dispatch, FAILED is not directly dispatched.
8. **Targeted reconciliation durability** — failed translation creates durable request even when queue add throws.
9. **Global reconciliation authorization** — non-SUPER_ADMIN denied; SUPER_ADMIN request persists before best-effort queue hint.
10. **Producer lifecycle** — repeated production-path queue acquisition reuses/bounds the producer; an injected queue is not closed by the service.

Then run:

```bash
node --test tests/security/admin-merchant-support.test.mjs
npm test
npx tsc --noEmit --pretty false
npm run lint
npm run build
npm run prisma:validate
git diff --check
```

Before returning to review, inspect:

```bash
git status --short
git diff --name-status
git diff -- package.json package-lock.json \
  src/lib/admin/merchant-support.ts \
  src/types/shared-merchant-communications.d.ts \
  tests/security/admin-merchant-support.test.mjs
```

If any production file outside the Attempt 2 File Boundary changed, revert it if it is clearly accidental. If it is genuinely required, do not expand scope: return `blocked` to `moda_architect` with the reason.

## Implementation Notes

Do not build React pages/components in this task. That is deliberately `ADMIN-004`.

Do not implement ownership take/release/reassign. That is deliberately `ADMIN-003`.

Do not manufacture a replacement for the broken Shared package in Admin. SHARED-003/SHARED-004 own the package repair/publication.

The current Attempt 1 implementation's dynamic import + local `.d.ts` shim was a temporary way to typecheck against a broken artifact; it is not an accepted final integration pattern.

## Attempt 2 Completion Report

### Status

Ready for Architect Review

### Work Completed

- Consumes `@modainteract/moda-interact-shared@0.7.1` through static published imports and removes the temporary declaration shim.
- Validates additional targets with Shared `LanguageTagSchema` and derives translation direction from persisted message kind.
- Reuses existing translations by status: `AVAILABLE` is not dispatched, `PENDING` may be hinted, and `FAILED` remains on reconciliation.
- Closes the previous cached BullMQ producer when `REDIS_URL` changes; injected queues are never closed.
- Added focused behavioral coverage for Unicode bounds, ownership including SUPER_ADMIN non-owner denial, transaction ordering, direction, language validation, status semantics, targeted reconciliation durability, global reconciliation authorization/durability, and queue lifecycle assertions.

### Files Changed

- `moda-interact-admin/package.json`
- `moda-interact-admin/package-lock.json`
- `moda-interact-admin/src/lib/admin/merchant-support.ts`
- `moda-interact-admin/tests/security/admin-merchant-support.test.mjs`
- Deleted `moda-interact-admin/src/types/shared-merchant-communications.d.ts`

### Validation Results

- Focused merchant-support tests: 8 passed.
- TypeScript check: passed.
- Prisma validation: passed.
- Production build: passed with existing Next workspace-root and optional BullMQ Valkey warnings.
- Lint: 0 errors and 2 existing warnings.
- `git diff --check`: passed.
- Full Admin tests: 89 passed, 1 failed out of 90 because the pre-existing out-of-scope `tests/security/admin-internationalization.test.mjs` still expects Shared `0.7.0` after this task correctly pins `0.7.1`.

### Deviations and Unresolved Issues

The stale `0.7.0` assertion was outside the Attempt 2 file boundary and remains unchanged. Pre-existing `database` submodule and internationalization-test changes were preserved. No `ADMIN-003` or other repository was modified.

### Architectural Concerns

None introduced within the authorized Attempt 2 scope.

## Attempt 3 Completion Report — 2026-09-06

### Status

Ready for Architect Review

### Work Completed

- Kept `lastMessageAt` advancing for every administrative message while restricting `lastAdministrativeMessageAt` and `needsAdminResponse` completion to matching English `AVAILABLE` responses.
- Preserved `respondsThroughMerchantVersion` for the later BACKGROUND-006 translation availability transition.
- Strengthened compose coverage for the distinct English and non-English response-boundary conditions.
- Asserted that additional-translation input `en-gb` is persisted canonically as `en-GB`.

### Validation Results

- Focused merchant-support tests: 8 passed.
- Full Admin tests: 89 passed, 1 failed because the pre-existing out-of-scope ARCH-005 `admin-internationalization.test.mjs` assertion still expects Shared `0.7.0` instead of the required `0.7.1`.
- TypeScript check: passed.
- Prisma validation: passed.
- Production build: passed with existing Next workspace-root and optional BullMQ Valkey warnings.
- Lint: 0 errors and 2 existing hook-dependency warnings.
- `git diff --check`: passed.

### Scope and Deviations

Only the authorized merchant-support implementation and focused test were edited for Attempt 3. Existing unrelated worktree changes were preserved. No Shared, Background, Database, actions, UI, or `ADMIN-003` work was modified or promoted.

## Completion Report

### Status

Attempt 1 returned for architect review; architect blocked acceptance.

### Files Observed

Attempt 1 implementation is concentrated in:

- `src/lib/admin/merchant-support.ts`;
- `src/app/actions/merchant-support.ts`;
- `src/types/shared-merchant-communications.d.ts`;
- `package.json` / `package-lock.json` for Shared `0.7.0` consumption.

### Work Completed

Attempt 1 added support-thread/message reads, administrative compose, additional-translation request, targeted/global reconciliation commands and best-effort queue hints.

### Validation Results

Agent reported the repository-wide validation passed: typecheck, build, lint, 82 tests and `git diff --check`.

Those broad checks do not satisfy this task's focused acceptance coverage because no dedicated merchant-support behavior tests were added.

### Deviations

- Used the broken Shared `0.7.0` Node helper entrypoint behind a local declaration shim and dynamic import fallback.
- Additional translations persisted `ADMIN_TO_MERCHANT` regardless of durable message kind.
- Additional target language used bare `Intl.Locale` rather than the published Shared language-tag schema.
- Focused authorization/transaction/Unicode/direction/Redis-failure tests were not added.

### Assumptions

Attempt 1 code is retained as the base for the bounded correction after SHARED-004.

### Unresolved Issues

Task is blocked on `ARCH-006-SHARED-004` and the correction contract above.

### Architectural Concerns

The final Admin server capability must not silently hide a broken shared-package runtime export as if it were a transient Redis failure.

## Architect Review

### Review Status

Blocked — Attempt 1 not accepted.

### Decision

`moda_architect` independently reviewed the supplied Admin snapshot. The task is blocked for correction after SHARED-004 because:

1. Shared `0.7.0` cannot resolve the required Node job-ID runtime entrypoint and the local declaration shim is not an acceptable final package boundary.
2. `requestAdditionalTranslation` always persists `ADMIN_TO_MERCHANT`; direction must derive from the persisted message kind using the canonical three-way mapping.
3. Additional targets are canonicalised with bare `Intl.Locale` rather than validated through the published Shared `LanguageTagSchema`.
4. Existing additional translations are redispatched without regard to durable status, which can bypass the dedicated FAILED reconciliation path and needlessly dispatch AVAILABLE work.
5. The current producer factory creates a new BullMQ Queue for each non-injected call and does not bound/close that connection lifecycle.
6. The task has no focused tests proving ownership, transaction ordering, Unicode bounds, direction, language validation, reconciliation durability or Redis-failure behavior.

The implementation should not be discarded. Once SHARED-004 is Complete, architect may return this task to Ready. The Admin agent must then claim Attempt 2, make only the bounded corrections above, return this same task to `review`, and STOP.

`ARCH-006-ADMIN-003` remains Pending and must not be started or promoted by the Admin agent.


### Architect Re-entry Decision — 2026-09-06

SHARED-004 is accepted Complete and `@modainteract/moda-interact-shared@0.7.1` passed registry/clean-consumer verification. ADMIN-001 is returned from Blocked to Ready for **Attempt 2**. Attempt remains `1` until the Admin agent claims the task; the claim must atomically increment it to `2`. Perform only the existing Attempt 2 correction contract, return the task to `review`, do not promote or claim ADMIN-003, and STOP.

## Attempt 2 Architect Review — 2026-09-06

### Review Status

Not accepted — returned to Ready for bounded Attempt 3 correction.

### Independent Findings

Attempt 2 successfully fixed the previously identified correction set: the Admin repository consumes exact Shared `0.7.1`, the temporary declaration shim is gone, deterministic Node helpers use the corrected published entrypoint, additional-translation direction derives from persisted message kind, Shared `LanguageTagSchema` is used, AVAILABLE/PENDING/FAILED redispatch semantics are correct, and the process-scoped BullMQ producer lifecycle is bounded.

One remaining business-state defect prevents acceptance. `composeAdministrativeMessage()` updates `lastAdministrativeMessageAt` and conditionally clears `needsAdminResponse` for **both** English and non-English targets. For a non-English target the newly-created message is only `PROCESSING`; ARCH-006 requires the merchant-response boundary to remain pending until BACKGROUND-006 applies the required translation and makes the message `AVAILABLE`. Clearing it at compose time can remove a merchant from the pending-support queue before a merchant-readable reply exists, including when translation later fails.

The correct ownership boundary is:

```text
English target:
  Admin compose transaction
    -> message AVAILABLE
    -> lastAdministrativeMessageAt may advance
    -> needsAdminResponse may clear if merchantMessageVersion still matches

Non-English target:
  Admin compose transaction
    -> message PROCESSING + PENDING translation
    -> needsAdminResponse remains unchanged
    -> lastAdministrativeMessageAt remains unchanged

  BACKGROUND-006 result application
    -> required translation AVAILABLE
    -> message AVAILABLE
    -> lastAdministrativeMessageAt advances
    -> clear needsAdminResponse only if current merchantMessageVersion
       still equals respondsThroughMerchantVersion
```

The focused suite is otherwise useful. It uses a canonicalisable `en-gb` additional-translation target but does not assert that the canonical `en-GB` value is actually used; Attempt 3 should add that assertion while already editing the same focused test.

The reported repository-wide 89/90 result is not itself a blocker: the sole failure is the pre-existing out-of-scope ARCH-005 assertion that still expects Shared `0.7.0`. It may remain recorded as known baseline evidence for this correction.

### Workflow Decision

`ARCH-006-ADMIN-001` returns to `Ready` with `attempt: 2`; the next repository-agent claim must increment it to Attempt 3 and set executor/claimed timestamp atomically. `ARCH-006-ADMIN-003` remains Pending. The agent must perform only the bounded Attempt 3 correction above, return ADMIN-001 to `review`, and STOP.



## Attempt 3 Architect Review — 2026-09-06

### Review Status

Accepted — Complete.

### Independent Findings

The bounded Attempt 3 correction is architecturally correct. The compose transaction now distinguishes immediate English availability from non-English translation processing: `lastMessageAt` advances for the newly-created administrative message, while `lastAdministrativeMessageAt` and `needsAdminResponse` change only when no translation is required and the current `merchantMessageVersion` still matches the snapshotted response boundary. Non-English compose therefore preserves the pending-response boundary for `ARCH-006-BACKGROUND-006`, which will apply the required translation and re-check `respondsThroughMerchantVersion` before completing that boundary.

The focused test now distinguishes the English and non-English branch conditions and also proves that canonicalisable additional-translation input `en-gb` is used as canonical `en-GB`. The Attempt 3 repository diff contains only the two authorised substantive files; the `tsconfig.tsbuildinfo` difference is a generated TypeScript build artifact rather than an additional source change.

Validation evidence is accepted: focused merchant-support coverage passed 8/8, TypeScript, Prisma validation, build, lint and `git diff --check` passed. The repository-wide 89/90 result retains the previously identified out-of-scope ARCH-005 assertion pinned to historical Shared `0.7.0`; it is not caused by this task and does not block acceptance.

### Coordination Decision

`ARCH-006-ADMIN-001` is Complete. Its only downstream task, `ARCH-006-ADMIN-003`, now has all declared dependencies satisfied and is promoted by `moda_architect` from Pending to Ready. `ARCH-006-ADMIN-004` remains Pending because it depends on both ADMIN-003 and `ARCH-006-BACKGROUND-007`.
