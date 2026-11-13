---
id: ARCH-075-BACKGROUND-008
architecture_id: ARCH-075
title: Preserve verified Meta resumable upload session identity
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 5
executor: codex
claimed_at: 2026-11-13T13:39:17Z
attempt: 1
depends_on:
  - ARCH-075-BACKGROUND-007
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Preserve verified Meta resumable upload session identity

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Accept Meta's evidenced resumable upload session identity without changing its meaning or the trusted Graph request destination.

## Context

The new production worker receives HTTP200 at sample_session but fails locally with META_UPLOAD_SESSION_INVALID before uploading sample bytes or claiming template creation. Existing validation requires upload: followed only by8–256 URL-safe characters. Primary Meta-owned resumable upload documentation says the server-generated Upload-ID returned by session creation is reused in the upload-file request. A successful status alone does not prove a valid shape, so root is obtaining a protected bounded structural response through the existing trusted adapter/config/app-operation path before selecting the final validation grammar. No provider session token, signature or complete raw response belongs in source, reports, logs or tests.

## Scope

Background's image-header sample uploader session-identity validation and same-origin upload URL construction, directly related uploader/adapter tests and narrow operational documentation. Use the actual official contract plus protected observed response shape as evidence; retain existing provider-specific ownership. Root may provide a redacted structural fixture that preserves delimiters, escaping and signed-ID behavior without live values. No new generic cross-service runtime mechanism is needed.

## Out of Scope

Shared/schema/database changes or release; changed template bodies/common layout; caching/reusing samples; app throttle redesign; credential/permission changes; logging raw successful provider responses; automatic repair of historical BLOCKED rows; any provider CREATE/POST replay; production migration/deployment/send or live diagnostic by the task executor; changes to other repositories; main integration.

## Requirements

1. Establish the successful response's exact structural contract from primary Meta documentation and root's protected observed shape before implementing a grammar. Record public references and bounded non-sensitive structure only. If actual contract is still ambiguous, stop and return the evidence gap rather than broadening a regular expression speculatively.
2. Treat the returned upload identifier as opaque within evidenced limits. Preserve its meaningful bytes/escaping/query semantics when constructing the upload-file request. Do not strip a signature, double-encode a signed query or silently substitute an identifier.
3. Keep the upload destination on the server-configured trusted Graph origin and version namespace. Reject malicious absolute/network-path destinations, path traversal, credentials, controls, fragments and unapproved query ambiguity. Explicitly test URL parsing/percent-encoding normalization; a string-prefix check alone is insufficient. Accept only documented/evidenced opaque signed-ID structure, not arbitrary URLs.
4. Keep bounded JSON reads, source JPEG verification, same credential snapshot, environment/app/config identity, durable fenced app lease and beforeHttp checks before both session and byte HTTP operations, deadlines and failure behavior. Network remains outside SQL transactions. No leakage of access token, upload ID or signature through errors, URLs or telemetry.
5. Valid session response proceeds to the existing byte upload then validates its handle normally. Invalid response makes no byte-upload or template-create request. Existing preclaim/CREATE_INTENT/POST_INTENT and no-repost guarantees stay unchanged; uncertain preclaim failures use existing retry lifecycle.
6. Historical old403/code4 BLOCKED recovery remains the separate accepted BG007 exact-evidence root-only operator path. No new reset command, migration, blanket state update or generic recovery exception belongs here.

## Work Items

- [x] Confirm primary contract and sanitized actual success-shape evidence.
- [x] Correct only bounded identity validation/request construction while preserving trust and lifecycle guards.
- [x] Prove regression and malicious-identity refusal; complete mirrored report and return for review.

## Interfaces / Contracts

Meta provider resumable-upload session response and existing TrustedMetaImageSampleHandle are Background-local provider contracts. Published Shared5.13.9 logging/contracts remain unchanged. Database002/BG007 own durable app operation and preclaim recovery; consume them unchanged. Primary references: https://www.postman.com/meta/whatsapp-business-platform/request/vkmioqf/resumable-upload-create-an-upload-session and https://www.postman.com/meta/whatsapp-business-platform/request/jruartu/resumable-upload-upload-file-data . Do not treat a third-party example or HTTP200 alone as grammar authority.

## Dependencies

ARCH-075-BACKGROUND-007 (Complete/Accepted).

## Enables

None. Root deployment and operational verification are separate; no implementation task depends on terminal system testing.

## Acceptance Criteria

- [x] EVIDENCED valid signed/opaque session form completes actual session→bytes→handle path without changing identity semantics.
- [x] Wrong destination/path/query/normalization/control/oversize/nonstring responses fail before byte HTTP; tests inspect actual constructed URL and headers.
- [x] Existing durable app throttle/fence/config/deadline/secret safety and template intent uncertainty behavior remain intact.
- [x] Required focused validation, canonical physical isolation/synchronization and mirrored publication evidence recorded truthfully; no live provider action as BG008 task executor.

## Validation

- [x] Regression red/green uploader tests using sanitized actual valid form, prior simple valid form where still contract-valid, byte-exact query/encoding preservation and malformed/malicious forms including encoded traversal, fragment, backslash, origin and repeated query ambiguity.
- [x] Existing focused uploader/Meta management/app-operation regression suites; typecheck, relevant lint and production build using actual declared scripts; exact-head local full suite passed and pushed CI pending. No unchanged database migrations rerun or Shared publication.
- [x] Error/log privacy assertions for token/session/signature; diff hygiene and unchanged cross-service/schema/intent guards.

## Stop Condition

When the bounded work and required validation pass, publish both matching task branches, set review, return the Completion Report to moda_architect and STOP. Do not deploy, execute live diagnostic/recovery/provider sends, merge main, or proceed to another task.

## Implementation Notes

You are not alone; preserve all other work. Use the launcher-resolved dedicated parent and implementation worktrees and normal prepared claim. Accepted BG007 merged source ce9d6e1017f553d307f21899c20f713d514189fd remains the baseline; don't mutate BG007's accepted worktree. Root owns protected live evidence and any diagnostic authority. Source/data fixes must be independently reviewable; no new Shared release or architecture-wide redesign.

## Completion Report

### Status

Ready for Review

### Files Changed

- `src/services/meta-template-management/image-header-sample.ts`
- `tests/unit/services/meta-template-management/image-header-sample.test.ts`
- `docs/operations/meta-upload-session-identity.md`
- This task file only in the parent repository.

### Work Completed

- Implementation commit `36acc5f7b88276b404dcb024275451cd7dcf56d4` pushed to `origin/task/ARCH-075-BACKGROUND-008`. Draft implementation PR requested; CI results remain a root/architect integration gate.
- Primary Meta-owned Postman pages above require reusing the server-generated Upload-ID. Root-delegated protected diagnostic at13:38:52Z (before this task's13:39:17Z claim) returned HTTP200, object with sole `id` key, string length211: `upload:` +180 alphanumeric characters +`?sig=` +19 alphanumeric characters. Protected raw-response SHA256 `446e49a5c02dcab111a7be6c678b533e0eef8ed802189ad5dea1f253a02781e3`; actual values are excluded from source/report/tests. Only the sanitized structure is reproduced. The diagnostic used the accepted adapter/config/SQL lease and stopped at the old validator before bytes or template create; no live actions occurred as BG008 task executor.
- Preserve optional single signed query unchanged, bound path/signature character sets and lengths, and independently enforce same configured origin, canonical version namespace, no credentials/fragment/normalization. Existing unsigned form remains supported; unobserved percent/Base64 punctuation is refused rather than speculatively accepted.
- Redact full session identity, opaque path and signature from byte-upload provider errors, SDK diagnostics and retained Error cause. Existing shared logger remains the only generic logging surface.
- No changes to app lease/backoff, credential snapshot, JPEG source verification, deadlines, `beforeHttp`, template claims/intents, historical recovery, schema or Shared dependency.

### Physical isolation and synchronization

- Canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-BACKGROUND-008`, branch `task/ARCH-075-BACKGROUND-008`.
- Implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-BACKGROUND-008`, same task branch.
- Launcher preparation: parent reused; remote task fast-forward not-needed; origin/main incorporated. Implementation created from accepted main `ce9d6e1017f553d307f21899c20f713d514189fd`; origin/main already-current; recursive database submodule initialized exactly at `6f42b71112efe7ac63654d55f41cd74ca569b1ae`.
- Claim Attempt1/executor codex committed/pushed at `bc5cb15c61cd6e282f7e2fa0bef558d0083882b0`.
- No shared/default checkout switched for implementation; no other task worktree reused or edited; no parent gitlink/index/architecture/policy changes.

### Validation Results

- RED: sanitized actual signed-form regression failed with `META_UPLOAD_SESSION_INVALID`;44 prior/negative tests passed.
- GREEN focused Meta management directory:9 files /152 tests passed. Includes actual URL/query/header/bytes assertions, old unsigned form,26 malformed/malicious identities, trusted Graph/emulator origins and versions, namespace normalization attacks, second-phase fence loss, provider/transport Error/log privacy.
- Full local suite on final source:390 files passed,1 skipped;4,294 tests passed,10 skipped;139.99s. No test failure. Existing configured skips retained.
- `npm run build` passed: actual Prisma6.19.3 generation, primary TypeScript and provisioning TypeScript compilers, sample artifact packaging.
- Targeted ESLint for both changed TypeScript files passed. `git diff --check` passed.
- Full `npm run lint` equivalent (`eslint .`) FAILED with four pre-existing `@typescript-eslint/no-unused-vars` findings in untouched `candidate-index.store.ts` (one) and `recovery-offer-resolver.service.ts` (three). Exact accepted baseline `ce9d6e1` files piped to ESLint via stdin reproduced the identical four findings; `git diff --exit-code ce9d6e1 -- <both files>` was empty. No matching durable baseline ID was found; coordinator explicitly instructed preservation/reporting rather than widening scope. This is not a full-lint-green claim.
- Detailed red/green/build/lint/baseline logs retained in protected root-owned `local-backups/arch075-live-20261113/bg008-*.log`; no raw provider identity committed.

### Deviations

Full repository lint remains limited by the verified four unchanged unrelated baseline findings; targeted task lint/build/full tests pass. Exact pushed-head CI is pending at report publication and must be checked before integration.

### Assumptions

Meta-owned primary docs describe opaque reuse; the protected observed success establishes the supported signed structure. Other unobserved identity encodings remain rejected. The successful synthetic sequence proves request construction, not actual production approval or recipient delivery.

### Unresolved Issues

Root retains provider rollout, normal uncertain-preclaim retry, old403 exact-evidence recovery, approvals, common activation and genuine WhatsApp delivery verification. No live completion claim is made.

### Architectural Concerns

None currently. Return any cross-repository/schema/lifecycle gap before expanding scope.

## Architect Review

### Review Status

Accepted

### Review Notes

Independently reviewed exact implementation `36acc5f7b88276b404dcb024275451cd7dcf56d4` and report `127c84b7967a12ad4b73079d37a6bbc9330e956f`. No findings. Primary Meta opaque reuse contract and protected actual structural receipt establish the optional signed suffix; the code does not infer a grammar from HTTP200 alone. This accepts the bounded source correction and local validation, not live registration/approval or ordered recipient delivery. Root explicitly retains exact-head hosted CI success as an additional pre-merge integration gate.

### Reviewed Files

- `src/services/meta-template-management/image-header-sample.ts`: exact session URL construction and provider/transport diagnostic redaction.
- `tests/unit/services/meta-template-management/image-header-sample.test.ts`: sanitized actual signed form, malformed/foreign/path/query/normalization refusals, byte request/fence and privacy assertions.
- `docs/operations/meta-upload-session-identity.md`, final Completion Report, canonical prepared packet and protected structural/validation receipts.

### Validation Reviewed

Observed RED regression and GREEN152 focused tests, final full suite390 passing files/4,294 passing tests with one file/ten existing conditional skips, successful production build/TypeScript/Prisma packaging and scoped lint/diff checks. Exact unchanged accepted-main file lint reproduced all four unrelated full-lint findings; no suppression or out-of-scope cleanup was introduced. Full lint remains explicitly nongreen. Prepared packet proves matching isolated parent/implementation worktrees, main synchronization, recursive accepted Database submodule and pushed Attempt1 claim. Implementation/report publication verified. Hosted exact-head run43436906240 succeeded; run43436977039 was still in progress at review and root must verify its success before merging.

### Architecture Conformance

Conforms to bounded Background provider-adapter ownership. Opaque signed identity is retained byte-for-byte under explicit bounds and same trusted Graph origin/version/path/href equality; unexpected normalization, credentials, fragments, repeated/foreign query and unsupported encodings fail closed before bytes. Existing source verification, app/config/lease fences, deadlines, provider-intent uncertainty and historical recovery semantics remain unchanged. Signed identity/path/signature are redacted from byte-operation diagnostics and retained Error cause. No Shared/schema/release change, caching, blanket repair or task-executor live mutation. Root-delegated preclaim diagnostic predates this task claim and is recorded separately.

### Follow-up

Root may integrate the exact accepted source only after both exact-head CI runs pass, then verify actual compatible worker rollout before normal preclaim retries. Old403/code4 blocks still require accepted BG007 exact-evidence recovery. Common activation, remaining provider approvals/environment copy and genuine Meta/AI/HUMAN ordered WhatsApp acceptance remain outstanding; ARCH-075 stays In Progress. No new Shared release or task dependency on terminal system validation is introduced.
