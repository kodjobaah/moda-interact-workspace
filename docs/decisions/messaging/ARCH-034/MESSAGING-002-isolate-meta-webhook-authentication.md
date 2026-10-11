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
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
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

- [ ] Extract security helper; keep route verification ordering unchanged.
- [ ] Add focused authentication regression tests including valid request, mismatched signature and GET challenge.
- [ ] Run focused and repository checks; record changed files/line counts.

## Interfaces / Contracts

- Meta provider ingress transport remains `GET/POST /webhook/whatsapp`.
- Uses current environment variable names; no new Shared package or cross-service contract.
- Consumes normalizers from `ARCH-034-MESSAGING-001`; queue remains unchanged.

## Dependencies

- `ARCH-034-MESSAGING-001`

## Enables

- `ARCH-034-MESSAGING-003`

## Acceptance Criteria

- [ ] Exact raw-body HMAC acceptance/rejection matches the pre-extraction route.
- [ ] Signature comparison remains constant-time for equal-length digests and safely rejects absent/mismatched signature.
- [ ] GET verification retains existing challenge/status/content-type; missing-secret behaviour remains fail-closed.
- [ ] Build retains secret handling on server only; new modules <=300 physical lines.

## Validation

Inspect the current repository `package.json` and use its actual scripts. The following existed in the inspected baseline; if they have changed, record the difference without inventing scripts.

- [ ] `node --import tsx --test tests/whatsapp-webhook-auth.test.mjs` (or equivalent focused test file)
- [ ] `npm test`
- [ ] `npm run typecheck`
- [ ] `npm run build`
- [ ] `git diff --check`
- [ ] Record focused changed-file sizes; no new source file above 300 physical lines

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are satisfied, record the Completion Report, set status to `review`, and STOP for `moda_architect`. Never start the enabled task automatically. Use the canonical mirrored task branches and launcher-resolved physical worktrees; do not implement in a shared/default checkout.

## Implementation Notes

Keep HTTP result construction and `recordWhatsAppIngressTelemetry` with the route. The authentication helper must not parse JSON or enqueue jobs. Preserve the codepath that verifies before JSON parsing and before all queue effects.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

None.
