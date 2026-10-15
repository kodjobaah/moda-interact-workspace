---
id: ARCH-039-BACKGROUND-001
architecture_id: ARCH-039
title: Migrate Background runtime credential readers to Shared
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 20
executor: developer
claimed_at: 2026-10-15T00:53:53Z
attempt: 2
depends_on:
  - ARCH-039-SHARED-004
enables:
  - ARCH-039-GATEWAY-001
  - ARCH-039-SYSTEM-TEST-001
created: 2026-10-14
updated: 2026-10-15
---


# Migrate Background runtime credential readers to Shared

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_background` / `moda-interact-background`

## Objective

Migrate Background runtime credential readers to Shared. This is one bounded, repository-owned outcome; do not move to another task on completion.

## Context

ARCH-039 makes one published credential security mechanism authoritative for hosted Node services. The developer has chosen a non-production data clear rather than historical encryption-key migration. This task is part of the agreed staged adoption plan; see the parent architecture for exact cross-service invariants.

## Scope

- Replace `src/commerce/credential-keyring.ts` parser and generic `src/security/aes-gcm-credential.ts` crypto usage for in-scope OpenRouter and translation/embedding provider credential consumers.
- Retain existing worker domain error taxonomy and model/provider retry behaviour.

## Out of Scope

Woo grant read is BACKGROUND-002; do not modify API sources.

## Requirements

- **Mandatory closed-set credential configuration:** for AES credential encryption/decryption, credential key selection and Commerce connection-command HMAC, the **only permitted environment variable names anywhere in ARCH-039 runtime configuration** are `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`. No other names, aliases, old Woo keyring variables, service-specific encryption/HMAC variables, dual-read, fallback, generated defaults or alternate sources may be used for these purposes. Other unrelated application environment settings are unaffected.
- **Staged-adoption review boundary:** the closed set above is mandatory for the **integrated ARCH-039 cutover**, not a requirement for BACKGROUND-001 to implement BACKGROUND-002. For this task, enforce it on the OpenRouter, translation and embedding readers that BACKGROUND-001 owns. Existing Woo grant reads are deliberately **not certified by BACKGROUND-001** and must not be treated as final-compliant or deployed as an ARCH-039-complete service. BACKGROUND-002 must remove `MODA_WOO_REST_READ_KEYRING` and local Woo cryptography before Gateway cutover and system certification. This is not approval of a legacy alias or compatibility fallback.
- This Background credential-reader task may read **only** `COMMERCE_CONNECTION_KEYS_JSON` from the closed set; it **must not** consume the active-key selector or the command-HMAC key. Decryption chooses the persisted envelope key ID.

- Reader-only Background services consume canonical `COMMERCE_CONNECTION_KEYS_JSON`, never active-key selector or HMAC.
- Reconstruct `CredentialEnvelope` from existing provider-credential columns and call only published `decryptCredential({ keyring, envelope, aad }): string`, with existing Shared model AAD; do not require an active selector for reads. Malformed/missing keyring, invalid UTF-8 and authentication failures are unavailable, never plaintext/config fallback.
- No change to queue admission, billing, provider calls, stored versions or provider outcome behaviour.

## Work Items

- [x] Migrate parser and production credential readers to Shared.
- [x] Run focused Background credential tests including malformed env and tamper/missing key ID.
- [ ] Verify the Woo grant service and its tests have no net changes introduced by BACKGROUND-001 relative to the **task start baseline**; keep Woo grant mapping and removal of `MODA_WOO_REST_READ_KEYRING` exclusively in BACKGROUND-002. Preserve the local generic AES helper only while the existing Woo reader still needs it. Record the baseline and task-branch diff evidence in the Completion Report.

## Interfaces / Contracts

- `decryptCredential`, `CredentialEnvelope` and keyring helpers from `@modainteract/moda-interact-shared/security/credentials/node`; existing Shared OpenRouter/translation AAD builders. No local crypto/open implementation or binary-plaintext helper.

## Dependencies

- ARCH-039-SHARED-004

## Enables

- ARCH-039-GATEWAY-001
- ARCH-039-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] **In-scope OpenRouter, translation and embedding credential readers** require only the canonical keyring, never active-key/HMAC or a legacy alias; missing or legacy-only configuration fails closed. Woo grant reads are excluded and explicitly remain a blocking requirement of BACKGROUND-002 and final ARCH-039 certification. Neither task may introduce a new credential environment variable.

- [x] Background credential readers call published `decryptCredential` and receive validated UTF-8 string plaintext; no local parser, decryptor or alternative old Shared function remains for the in-scope readers.
- [x] Read-only worker paths do not depend on active selector.
- [x] Worker business/queue behaviour unchanged by the migration.

## Validation

- [x] Focused Background credential/runtime tests
- [x] Background typecheck and build (where provided)
- [ ] Changed-file lint and `git diff --check`; run lint on the files **actually changed by this task** and separately record any baseline/out-of-scope lint failures without silently changing them. Review task-owned diff relative to the recorded task-start base as well as the mainline comparison; do not assume every `origin/main...HEAD` difference originated with this task.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. For developer completion, an explicit developer approval is required after accepted review.

## Implementation Notes

Any local adapter remaining must be only a service-specific error mapping. Retain the local generic AES helper temporarily where Woo still imports it; delete it in BACKGROUND-002 after Woo migration.

Task acceptance certifies only the in-scope migrated readers. The ARCH-039 release/cutover remains blocked until BACKGROUND-002 removes the pre-existing Woo keyring variable and uses published Shared decryption. Do not move that work into BACKGROUND-001 just to satisfy an architecture-wide gate early. The historical Completion Report and review entries below must remain intact; a new review should record updated evidence rather than rewriting old findings.

Use the canonical parent/implementation task-worktree preparation protocol, preserve dedicated worktree and start-of-attempt synchronization evidence, and do not edit `docs/decisions/**/_index.md` before architecture-session confirmation. No direct changes to another agent's repository.

## Completion Report

### Status

In Progress — Attempt 2 claimed by developer at 2026-10-15T00:53:53Z. Attempt 1 review history is preserved below.

### Files Changed

- `moda-interact-background/package.json`
- `moda-interact-background/package-lock.json`
- `moda-interact-background/src/commerce/credential-keyring.ts`
- `moda-interact-background/src/commerce/openrouter-credential.ts`
- `moda-interact-background/src/commerce/provider-credential-validation.ts`
- `moda-interact-background/src/commerce/translation-provider-credential.ts`
- `moda-interact-background/src/services/merchant-knowledge-embedding-runtime.ts`
- `moda-interact-background/tests/unit/commerce/credential-keyring.test.ts`
- `moda-interact-background/tests/unit/commerce/openrouter-credential.test.ts`
- `moda-interact-background/tests/unit/commerce/translation-provider-credential.test.ts`
- `moda-interact-background/tests/unit/services/merchant-knowledge-embedding.test.ts`
- `moda-interact-background/src/providers/shopify-partner-billing.provider.ts` (latest task-branch commit)
- `moda-interact-background/src/services/woo-coupon-grant.service.ts` (latest task-branch commit)
- `moda-interact-background/src/services/woo-coupon-legacy-keyring.ts` (latest task-branch commit)
- `moda-interact-background/tests/unit/services/woo-coupon-grant.service.test.ts` (latest task-branch commit)

### Work Completed

- Background keyring parsing now delegates to Shared and reads only `COMMERCE_CONNECTION_KEYS_JSON`.
- OpenRouter, translation-provider, and Merchant Knowledge embedding readers reconstruct Shared `CredentialEnvelope` values and call `decryptCredential` with their domain-specific Shared AAD builders. Provider-domain validation and existing bounded error mappings are retained.
- Implementation commit `d2953b8f67c507b316357a2358c50ceb313e774b` is published on `task/ARCH-039-BACKGROUND-001`.

### Validation Results

- Original focused keyring/OpenRouter/translation/embedding tests: 53 passed, 0 failed. Current in-scope focused suite: 54 passed, 0 failed across four files. Latest combined suite including the out-of-scope Woo grant test: 69 passed, 0 failed across five files.
- `npm run build`: passed; Prisma Client generation and `tsc` completed successfully.
- ESLint 10.12.0 passes for the nine in-scope credential implementation/test files. Lint over the existing changed files in the full branch fails on the unrelated Shopify provider edit (`@typescript-eslint/no-explicit-any`, line 452). The first expanded lint invocation also referenced the deleted `src/services/woo-coupon-legacy-keyring.ts`.
- `git diff --check origin/main...HEAD`: passed; implementation worktree status was clean and synchronized with `origin/task/ARCH-039-BACKGROUND-001` at review time.
- The Background database submodule is initialized at `40674aea91527d5645aa922c9627af673b487223`.
- Current implementation branch tip `3e47d225bf195c617167b280fcabc205df87345c` contains Woo grant/keyring changes and a Shopify billing-provider edit outside this task's scope; review is held for branch-scope and lint correction.

### Deviations

None

### Assumptions

None beyond the parent architecture.

### Unresolved Issues

- Remove/rehome the Woo grant service and test changes under BACKGROUND-002; BACKGROUND-001 must not read `MODA_WOO_REST_READ_KEYRING` or otherwise expand the ARCH-039 configuration closed set. Preserve published history and use a corrective commit.
- Remove the unrelated Shopify billing-provider edit from BACKGROUND-001 in a corrective commit; it also currently fails the configured `@typescript-eslint/no-explicit-any` lint rule.
- Keep the restored 128-character key-ID regression test; it is present in the current branch.
- Confirm and document the Background `database` submodule pointer advance from `8936f3b` to `40674ae` (an ARCH-038 database-task merge), including why this dependency belongs on this branch; do not modify the database repository as part of this task.
- After correcting branch scope, rerun the in-scope focused credential tests, build, changed-file lint, and `git diff --check`. The prior untracked `.package.json.swp` issue is resolved.

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

Not yet reviewed.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending review.

### Follow-up

None

## Developer Self-Review - Changes Requested (Initial)

Attempt 1's implementation, focused tests and build pass. Review is held because required changed-file lint could not be run: `moda-interact-background` has no lint script and no installed/configured linter. In addition, final inspection found an untracked `.package.json.swp` in the implementation worktree. It was not opened, staged, or modified because it may be a user/editor artifact. Resolve that artifact and confirm the worktree is clean; then run changed-file lint with an approved tool or explicitly amend the validation requirement to accept the repository's lack of lint tooling, and resubmit Attempt 1. The implementation source commit is published; do not increment the attempt for this review decision.

## Developer Self-Review - Changes Requested (Reconciliation)

Attempt 1's focused credential tests (53 passed), build, changed-file lint (ESLint 10.12.0), and `git diff --check` pass. The previously reported `.package.json.swp` is absent and the implementation worktree is clean. Review remains Changes Requested because the current published BACKGROUND-001 branch tip `390a8a1944ebd56a4b5326a493bd58a755311830` includes Woo grant/keyring implementation and tests assigned to BACKGROUND-002, an unrelated Shopify billing-provider edit, and removal of the 128-character key-ID test. Remove/rehome the out-of-scope changes in a corrective commit without rewriting published history, restore or account for the removed test coverage, then rerun focused tests, build, lint, and diff check. Attempt remains 1; `status: ready`, `executor: null`, and `claimed_at: null` for correction and resubmission.

## Developer Self-Review - Changes Requested (Current Branch Review)

Attempt 1 remains Changes Requested. Current implementation tip `3e47d225bf195c617167b280fcabc205df87345c` is published, clean, and synchronized with its task remote. The 128-character key-ID case is a rejection-boundary test; the Shared parser accepts key IDs through 64 characters and rejects the 128-character value. The in-scope focused suite passes (54/54 across four files), the combined suite including Woo passes (69/69 across five files), `npm run build` passes, in-scope ESLint passes on nine files, and `git diff --check origin/main...HEAD` passes. Full changed-file ESLint fails because the unrelated `src/providers/shopify-partner-billing.provider.ts` edit widens `isRecord` to `Record<string, any>` and violates `@typescript-eslint/no-explicit-any` at line 452.

Review is held because `src/services/woo-coupon-grant.service.ts` is BACKGROUND-002 scope and now reads `MODA_WOO_REST_READ_KEYRING`; this violates the ARCH-039 closed-set requirement and replaces the canonical Shared-backed keyring bridge. The Woo grant test was also changed to accept that legacy variable. The Shopify billing-provider edits are unrelated to BACKGROUND-001 and fail full-branch lint. The branch also advances the `database` submodule pointer from `8936f3b` to `40674ae`, which includes an ARCH-038 database-task merge and needs its dependency rationale confirmed. Rehome/remove the Woo and Shopify changes through a corrective commit without rewriting published history, confirm the database pointer dependency, then rerun the in-scope focused tests, build, lint, and diff check. Keep the 128-character rejection-boundary test.

No source changes were made during this review. Attempt remains 1; task state remains `ready`, with `executor: null` and `claimed_at: null`, for correction and resubmission.
