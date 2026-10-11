---
id: ARCH-034-MESSAGING-002
architecture_id: ARCH-034
title: Isolate Meta webhook authentication
task_kind: implementation
domain: messaging
repository: moda-interact-messaging
assigned_agent: moda_messaging
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on: ["ARCH-034-MESSAGING-001"]
enables: ["ARCH-034-MESSAGING-003"]
created: 2026-10-11
updated: 2026-10-11
---

# Isolate Meta webhook authentication

## Architecture

Architecture ID: `ARCH-034`.

Architecture document: `docs/architecture/ARCH-034-whatsapp-webhook-ingress-maintainability.md`.

Coordinator: `moda_architect`.

## Objective

Extract GET verification-token access and raw-body POST signature verification into a small server-only module, keeping the existing responses and security requirements unchanged.

## Context

After the pure normalization extraction the route still owns both `WHATSAPP_VERIFY_TOKEN` lookup and HMAC-SHA256 validation against `META_APP_SECRET`. Those are security-sensitive server-only responsibilities distinct from HTTP composition.

## Scope

- Add a small `app/lib/whatsapp/webhook-auth.server.ts` helper to own verification-token retrieval and Meta signature validation.
- Make the route call the helper for existing GET token/challenge verification and POST raw-body authentication.
- Add focused tests for valid/tampered/missing signatures, missing secrets, GET challenge acceptance/rejection and absence of leaked secret values.

## Out of Scope

- Queue publishing, provider-status normalization, webhook dispatcher extraction or HTTP response changes.
- New secrets/config, weaker comparisons, logging raw headers/bodies or moving verification after JSON parse.

## Requirements

- POST HMAC uses the unmodified raw UTF-8 request body and `x-hub-signature-256`, with SHA-256 and `crypto.timingSafeEqual` after checking byte-length equality.
- Preserve fail-closed handling and existing behaviour when `META_APP_SECRET`/`WHATSAPP_VERIFY_TOKEN` is missing.
- Keep `loader` GET `hub.mode`, `hub.verify_token`, `hub.challenge` checks and HTTP status/text unchanged.
- Server-only secret/HMAC utilities must never be browser-bundled. Preserve no raw payload/token logging.

## Work Items

- [x] Extract security helper; keep route verification ordering unchanged.
- [x] Add focused authentication regression tests including valid request, mismatched signature and GET challenge.
- [x] Run focused and repository checks; record changed files/line counts.

## Interfaces / Contracts

- Meta provider ingress transport remains `GET/POST /webhook/whatsapp`.
- Uses current environment variable names; no new Shared package or cross-service contract.
- Consumes normalizers from `ARCH-034-MESSAGING-001`; queue remains unchanged.

## Dependencies

- `ARCH-034-MESSAGING-001`

## Enables

- `ARCH-034-MESSAGING-003`

## Acceptance Criteria

- [x] Exact raw-body HMAC acceptance/rejection matches the pre-extraction route.
- [x] Signature comparison remains constant-time for equal-length digests and safely rejects absent/mismatched signature.
- [x] GET verification retains existing challenge/status/content-type; missing-secret behaviour remains fail-closed.
- [x] Build retains secret handling on server only; new modules <=300 physical lines.

## Validation

Inspect the current repository `package.json` and use its actual scripts. The following existed in the inspected baseline; if they have changed, record the difference without inventing scripts.

- [x] `node --import tsx --test tests/whatsapp-webhook-auth.test.mjs` (or equivalent focused test file)
- [x] `npm test`
- [x] `npm run typecheck`
- [x] `npm run build`
- [x] `git diff --check`
- [x] Record focused changed-file sizes; no new source file above 300 physical lines

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are satisfied, record the Completion Report, set status to `review`, and STOP for `moda_architect`. Never start the enabled task automatically. Use the canonical mirrored task branches and launcher-resolved physical worktrees; do not implement in a shared/default checkout.

## Implementation Notes

Keep HTTP result construction and `recordWhatsAppIngressTelemetry` with the route. The authentication helper must not parse JSON or enqueue jobs. Preserve the codepath that verifies before JSON parsing and before all queue effects.

## Completion Report

### Status

Ready for Review — retrospective developer-applied Attempt 1; developer reports all requested validation checks passing on 2026-10-11.

### Files Changed

- `app/routes/whatsapp.tsx` — import Meta authentication helpers instead of implementing them; route 288 -> 243 physical lines.
- `app/lib/whatsapp/webhook-auth.server.ts` — new 48-line server-only verification-token/HMAC module.
- `tests/whatsapp-webhook-auth.test.mjs` — new 161-line focused HTTP/authentication suite with 10 declared tests.

### Work Completed

Moved `getWhatsAppVerifyToken`, `verifyMetaSignature`, and the private `getMetaAppSecret` helper into a narrow `.server.ts` module. The route still checks method, verifies Meta signature on the unmodified raw UTF-8 body before JSON parsing or publication, and returns the same GET verification and POST response statuses, response bodies and telemetry. Preserved digest length comparison followed by `crypto.timingSafeEqual`, missing-header behavior, missing-secret failure, and server-side-only secret access. No queue, job identity, Shared contract, normalizer or webhook traversal changes.

Added ten focused tests covering exact UTF-8 body and tamper rejection, missing/wrong-length signatures, missing secret handling, GET success/rejection/missing token, signed-empty-body success, unauthenticated/malformed POST, non-POST response, and no token logging or route-level secret access.

### Validation Results

- **Developer-reported:** "all test have passed" following the instructions to execute the new focused authentication suite, complete `npm test`, `npm run typecheck`, `npm run build`, and `git diff --check`. No command output or exact runtime pass counts were attached in this turn; they are not represented as independently witnessed results.
- **Architect-verified statically:** the implementation patch moves the original HMAC/token functions without altering their logic or verification ordering; the new suite declares 10 test cases and has targeted assertions for GET/POST and fail-closed cases.
- **Architect pre-delivery patch validation:** fresh-baseline application, whitespace, syntax, and isolated HMAC smoke tests passed when the Attempt 1 source patch was prepared. Source counts: route 243, server-only auth module 48, test module 161 physical lines.
- Runtime full-suite, typecheck and production build were **not rerun by the architect** in this review environment. Existing Vite browser-externalization warnings related to remaining queue/job-identity imports are addressed, if applicable, by MESSAGING-003, not this authentication extraction.

### Deviations

The developer applied an architect-supplied patch in the primary Messaging checkout instead of a launcher-prepared mirrored task-branch/worktree execution. No canonical claim, dedicated physical task worktrees, synchronized task branches, implementation commit/push or parent report commit/push is claimed. This intentional manual implementation workflow is recorded as a worktree-policy deviation, not disguised as launcher compliance.

### Assumptions

The developer's test-success confirmation refers to the `ARCH-034-MESSAGING-002` Attempt 1 implementation and the requested validation command sequence. No signed live Meta or Redis-backed system test is claimed by this report.

### Unresolved Issues

No defect has been reported in the bounded authentication extraction. The broader webhook malformed-envelope and pre-publication hardening remains the separate `ARCH-034-MESSAGING-005` task.

### Architectural Concerns

None introduced by this bounded extraction. The standard worktree isolation policy was not exercised under the user's manual-patch workflow and must remain required for normal agent execution.

## Architect Review

### Review Status

Accepted — Attempt 1 (2026-10-11); developer-reported validation and manual task-worktree deviation recorded.

### Review Notes

Reviewed the three-file source patch and focused tests against the accepted MESSAGING-001 baseline. Meta signature verification remains on the exact raw body before JSON parsing and queue publication. GET challenge status/text/content-type, POST 401/400/405/200 behavior, missing-header and missing-secret handling, and HMAC digest-length/timing-safe semantics are unchanged. The extracted helper uses the `.server.ts` boundary and does not enqueue or log secrets.

The developer reports all requested tests succeeding. This is a manual-patch retrospective review; launcher worktree/branch/commit evidence and independently rerun full validation are not claimed.

### Reviewed Files

- `app/routes/whatsapp.tsx`
- `app/lib/whatsapp/webhook-auth.server.ts`
- `tests/whatsapp-webhook-auth.test.mjs`

### Validation Reviewed

- Developer success confirmation for the requested validation sequence (raw output not attached).
- Architect's inspected source diff, HMAC semantics, test assertions, module boundaries and pre-delivery patch/syntax/smoke evidence.
- No independent complete runtime test/typecheck/build execution by the architect.

### Architecture Conformance

Conforms to ARCH-034-MESSAGING-002: server-side Meta authentication is isolated without changing HTTP behavior, queue contract, retries, normalization, security ordering or telemetry. Existing authentication conditions remain fail-closed. Later queue extraction and webhook preflight remain separate tasks.

### Follow-up

Promote `ARCH-034-MESSAGING-003` to Ready. It may extract queue publication and job IDs while preserving existing behaviour. No `docs/decisions/**/_index.md` files change before the developer explicitly closes the architecture session.
