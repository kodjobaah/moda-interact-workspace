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
status: ready
priority: 5
executor: null
claimed_at: null
attempt: 0
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

- [ ] Confirm primary contract and sanitized actual success-shape evidence.
- [ ] Correct only bounded identity validation/request construction while preserving trust and lifecycle guards.
- [ ] Prove regression and malicious-identity refusal; complete mirrored report and return for review.

## Interfaces / Contracts

Meta provider resumable-upload session response and existing TrustedMetaImageSampleHandle are Background-local provider contracts. Published Shared5.13.9 logging/contracts remain unchanged. Database002/BG007 own durable app operation and preclaim recovery; consume them unchanged. Primary references: https://www.postman.com/meta/whatsapp-business-platform/request/vkmioqf/resumable-upload-create-an-upload-session and https://www.postman.com/meta/whatsapp-business-platform/request/jruartu/resumable-upload-upload-file-data . Do not treat a third-party example or HTTP200 alone as grammar authority.

## Dependencies

ARCH-075-BACKGROUND-007 (Complete/Accepted).

## Enables

None. Root deployment and operational verification are separate; no implementation task depends on terminal system testing.

## Acceptance Criteria

- [ ] EVIDENCED valid signed/opaque session form completes actual session→bytes→handle path without changing identity semantics.
- [ ] Wrong destination/path/query/normalization/control/oversize/nonstring responses fail before byte HTTP; tests inspect actual constructed URL and headers.
- [ ] Existing durable app throttle/fence/config/deadline/secret safety and template intent uncertainty behavior remain intact.
- [ ] Required focused validation, canonical physical isolation/synchronization and mirrored publication evidence recorded truthfully; no live provider action.

## Validation

- [ ] Regression red/green uploader tests using sanitized actual valid form, prior simple valid form where still contract-valid, byte-exact query/encoding preservation and malformed/malicious forms including encoded traversal, fragment, backslash, origin and repeated query ambiguity.
- [ ] Existing focused uploader/Meta management/app-operation regression suites; typecheck, relevant lint and production build using actual declared scripts; exact-head full CI where available. Do not rerun unchanged database migrations or publish Shared.
- [ ] Error/log privacy assertions for token/session/signature; diff hygiene and unchanged cross-service/schema/intent guards.

## Stop Condition

When the bounded work and required validation pass, publish both matching task branches, set review, return the Completion Report to moda_architect and STOP. Do not deploy, execute live diagnostic/recovery/provider sends, merge main, or proceed to another task.

## Implementation Notes

You are not alone; preserve all other work. Use the launcher-resolved dedicated parent and implementation worktrees and normal prepared claim. Accepted BG007 merged source ce9d6e1017f553d307f21899c20f713d514189fd remains the baseline; don't mutate BG007's accepted worktree. Root owns protected live evidence and any diagnostic authority. Source/data fixes must be independently reviewable; no new Shared release or architecture-wide redesign.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

### Deviations

None

### Assumptions

None; actual successful response shape must be established before implementation.

### Unresolved Issues

Protected actual upload-session structural evidence pending from root.

### Architectural Concerns

None currently. Return any cross-repository/schema/lifecycle gap before expanding scope.

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending implementation review

### Follow-up

Root retains live registration, coordinated common activation and ordered WhatsApp acceptance; architecture remains In Progress.
