---
id: ARCH-054-API-001
architecture_id: ARCH-054
title: Expose merchant AI reply delay via authenticated Woo API
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-054-DATABASE-001
  - ARCH-054-SHARED-002
enables:
  - ARCH-054-WOOCOMMERCE-001
created: 2026-10-31
updated: 2026-10-31
---


# ARCH-054-API-001: Expose merchant AI reply delay via authenticated Woo API


## Architecture

Architecture: `ARCH-054`

Document: `docs/architecture/ARCH-054-merchant-configurable-ai-response-delay.md`

Coordinator: `moda_architect`. Task **defined but not materialised**; no local Git/worktree/branch activity is claimed.


## Objective

Add standalone v1 Woo installation-authenticated GET/PUT for the shared shop AI-delay configuration, without changing recovery-delay policy or conversation commands.


## Context

ARCH-054 adds a **merchant-selectable integer 0–30 minute AI reply delay** to the existing ARCH-040 recovery-conversation processor and handover controls, leaving merchant-authored HUMAN replies without configured delay. See the parent architecture and current snapshot for specific boundaries.


## Scope

Create `src/merchant/ai-response-delay/contract.ts`, `service.ts`, `routes.ts`, `request.ts`; register in `src/composition/merchant.ts`. Update `moda-interact-api/package.json` and `package-lock.json` to the exact architect-accepted version published by ARCH-054-SHARED-002; do not import sibling Shared source. Add `tests/unit/merchant/ai-response-delay/settings.test.ts` and `scripts/test-arch054-ai-response-delay-postgres.mjs`. Reuse current WooInstallationAuthenticator and no-store JSON response helpers. Do not modify `src/merchant/recovery-policy/*` behavior.


## Out of Scope

No unrelated architecture changes, new standalone chat service, per-user timer jobs, invented provider error explanations, or updates to `docs/decisions/**/_index.md`. No implementation outside the assigned repository.


## Requirements

- Route exactly `GET/PUT /v1/merchant/ai-response-delay`, request/response JSON use published `MerchantAiResponseDelayWriteV1Schema`/`ReadV1Schema` from `@modainteract/moda-interact-shared/ai-response-delay`; no local structurally copied Zod. GET has no request body; PUT body <= 2048 bytes, `application/json`, strict keys. Both require authenticated ACTIVE verified Woo installation bound to current canonical site URL and active Shop; no browser-provided shop ID, no query override.
- GET returns `{schemaVersion:1,revision,aiResponseDelayMinutes}` from `ShopSettings`, with default 0/revision `UNCONFIGURED` only if authenticated shop has no settings row; `Cache-Control: no-store`.
- PUT requires `expectedRevision` equality and 0..30 integer, locks shop row, confirms installation state inside transaction and updates ONLY `aiResponseDelayMinutes` and monotonically `updatedAt` in existing ShopSettings; on first row create set safe established defaults and correct `shopId`. Return same read DTO/new revision. Idempotent identical value must not mutate or bump revision. Conflict 409 with stable `ai_response_delay_conflict` code; malformed 400; unauthorized 401/403; unauthenticated response must not disclose settings. Do not alter pending turn timestamps or admin overrides. Support original cause logging with sensitive redaction on error.


## Work Items

- [ ] Implement read/update service, strict request/response and route composition.
- [ ] Add tests for 0,7,30, bad -1/31/float/string/extra fields, conflict/retry, same-value no-op, revocation while updating, cross-tenant tampering, concurrent writes and recovery-policy unaffected.


## Interfaces / Contracts

Canonical Shared v1 examples (request) `{ "schemaVersion":1, "expectedRevision":"UNCONFIGURED", "aiResponseDelayMinutes":7 }`; (response) `{ "schemaVersion":1, "revision":"2026-10-31T16:28:55.123Z", "aiResponseDelayMinutes":7 }`. Owner Shared-001/002; consumers API and Woo PHP.


## Dependencies

- ARCH-054-DATABASE-001
- ARCH-054-SHARED-002


## Enables

- ARCH-054-WOOCOMMERCE-001


## Acceptance Criteria

- [ ] Only authenticated same-tenant Woo read/write succeeds; no Shop ID from browser; revision and changed value consistent. Hosted API consumes exactly the published Shared package version and records it in the lockfile.
- [ ] No modification to recovery-delay values, follow-up or human-send path; all failures return deterministic statuses and do not mutate settings.


## Validation

- [ ] `npx tsx --test tests/unit/merchant/ai-response-delay/settings.test.ts`; `node scripts/test-arch054-ai-response-delay-postgres.mjs`; `npm run lint`; `npm run typecheck`; `npm run build`; `git diff --check`.


## Stop Condition

After all required Work Items, Acceptance Criteria and Validation are complete, update Completion Report, set status to `review`, return control to `moda_architect` and **STOP**. Do not implement dependent tasks. Publication tasks do not rerun accepted implementation validation.


## Implementation Notes

Implement only the identified repository-owned changes; preserve original provider/SDK errors in shared structured logs and rethrow failures to the owning retry/admission boundary.


## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not Run

### Deviation / Assumptions / Unresolved Issues / Architectural Concerns

None

### Worktree and Git Evidence

Not materialised; implementing agent must record launcher-prepared dedicated parent/implementation worktree paths, start-of-attempt sync, branch SHAs, submodule pins and cleanup.


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

Pending

### Follow-up

None
