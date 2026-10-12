---
id: ARCH-034-MESSAGING-001
architecture_id: ARCH-034
title: Extract pure WhatsApp payload normalizers
task_kind: implementation
domain: messaging
repository: moda-interact-messaging
assigned_agent: moda_messaging
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on: ["ARCH-028-MESSAGING-001"]
enables: ["ARCH-034-MESSAGING-002"]
created: 2026-10-11
updated: 2026-10-11
---

# Extract pure WhatsApp payload normalizers

## Architecture

Architecture ID: `ARCH-034`.

Architecture document: `docs/architecture/ARCH-034-whatsapp-webhook-ingress-maintainability.md`.

Coordinator: `moda_architect`.

## Objective

Move existing inbound-message and provider-status normalization out of `app/routes/whatsapp.tsx` into small independently testable, Messaging-owned pure modules without changing accepted events or event identity.

## Context

The 467-line route currently hosts inbound text/audio/reply normalization and v3 provider-status/failure/pricing parsing. `ARCH-028-MESSAGING-001` is Complete on parent main and Shared `1.3.1` is already adopted. The helper exports are imported by two local test files; no cross-service TypeScript callers were found.

## Scope

- Create focused `app/lib/whatsapp/inbound-message-normalizer.ts`, `provider-status-normalizer.ts` and narrowly shared `normalization-utils.ts` (names may differ if responsibilities are equivalent).
- Move the pure existing normalizers and any directly required typed input helpers, including `asRecord`, `normalizeOccurredAt`, bounded pricing and numeric/string failure-code extraction.
- Update the route to import the extracted functions; update focused tests to import owning modules rather than require the route to expose helpers.
- Add focused regression assertions only where necessary for exact existing v1/v3 behaviour.

## Out of Scope

- GET/POST authentication, dispatch structure and queue publishing changes.
- Any changes to Shared contracts, numeric failure bounds, raw provider failure evidence or identifier values.
- Malformed top-level payload and partial-publication policy changes.

## Requirements

- Use exactly the published Shared `/whatsapp` and `/billing` safe-parse schemas; do not recreate their types/validation independently.
- Retain the v3 mapping SENT, DELIVERED, READ, FAILED; first valid bounded provider code and fallback after oversized numeric values; evidence only on FAILED.
- Preserve inbound context and text/audio/unsupported-content mapping, account/phone/message identity, timestamp/pricing semantics and null for malformed inputs.
- Pure normalization modules must perform no queue I/O, environment access, logging or HTTP response work.
- Keep new module sizes targeted at <=200 physical lines, never >300; avoid splitting one tiny helper into its own module unnecessarily.

## Work Items

- [x] Extract pure normalizers and update imports without altering the HTTP endpoint.
- [x] Move the two existing normalization test suites to direct module imports without dropping assertions.
- [x] Add/retain numeric-code overflow, v3 FAILED job-evidence data, audio/reply, pricing and malformed-input tests.
- [x] Run focused and repository validation; record before/after module line counts and changed files.

## Interfaces / Contracts

- Canonical provider status: `@modainteract/moda-interact-shared/billing` (`NormalizedWhatsAppStatus`, `safeParseNormalizedWhatsAppStatus`).
- Canonical inbound message: `@modainteract/moda-interact-shared/whatsapp` (`safeParseNormalizedWhatsAppInboundMessage`).
- The route and queue publisher continue consuming exactly the same normalized objects; no new external API.
- Dependency baseline: `ARCH-028-MESSAGING-001`, accepted and merged.

## Dependencies

- `ARCH-028-MESSAGING-001`

## Enables

- `ARCH-034-MESSAGING-002`

## Acceptance Criteria

- [x] The route delegates normalization to pure modules without changing accepted inputs or normalized payloads.
- [x] All current provider-status failure-code and deterministic-field assertions still pass.
- [x] Text, audio, reply context, unsupported media, identities and malformed-field cases are unchanged.
- [x] No queue/security side effects are moved into the normalizers.
- [x] No new code catch-all or source file above 300 lines.

## Validation

Inspect the current repository `package.json` and use its actual scripts. The following existed in the inspected baseline; if they have changed, record the difference without inventing scripts.

- [x] `node --import tsx --test tests/whatsapp-provider-status.test.mjs tests/whatsapp-inbound-normalization.test.mjs`
- [x] `npm test`
- [x] `npm run typecheck`
- [x] `npm run build`
- [x] `git diff --check`
- [x] Record focused changed-file sizes; no new source file above 300 physical lines

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are satisfied, record the Completion Report, set status to `review`, and STOP for `moda_architect`. Never start the enabled task automatically. Use the canonical mirrored task branches and launcher-resolved physical worktrees; do not implement in a shared/default checkout.

## Implementation Notes

This is one extraction boundary: both parsers convert untrusted Meta payload fragments into canonical Shared event objects and can share only small pure parsing helpers. Do not rewrite normalization semantics. Tests should import their true module owners; React Router `loader`/`action` exports are the stable route contract.

## Completion Report

### Status

Ready for Review — retrospective developer-applied patch, Attempt 1; all repository validation reported passing on 2026-10-11.

### Files Changed

- `app/routes/whatsapp.tsx` — delegates to the extracted normalization modules, 467 -> 288 physical lines.
- `app/lib/whatsapp/inbound-message-normalizer.ts` — new, 63 physical lines.
- `app/lib/whatsapp/provider-status-normalizer.ts` — new, 111 physical lines.
- `app/lib/whatsapp/normalization-utils.ts` — new, 10 physical lines.
- `tests/whatsapp-inbound-normalization.test.mjs` — imports the new inbound owner.
- `tests/whatsapp-provider-status.test.mjs` — imports the new status owner.

### Work Completed

Extracted the existing v1 inbound-text/audio/reply/unsupported normalization and v3 status/failure-evidence/pricing normalization into pure typed modules. The route continues to own its original HTTP authentication, queue publication, deterministic job identity and response/telemetry handling. Tests import their new module owners and retain the existing normalization assertions. No Shared contract or message/job identity changes were introduced. New focused source modules stay under 200 physical lines.

### Validation Results

Developer's final terminal output (2026-10-11) reports:

- `npm test`: **42 passed, 0 failed, 1 skipped** (43 total); the Redis-dependent trace integration test remained conditionally skipped.
- `npm run typecheck`: **PASS**, `react-router typegen && tsc` completed with no errors.
- `npm run build`: **PASS**, client and SSR builds completed; existing Vite Node-core/browser externalisation warnings remain non-fatal.
- Existing focused provider-status and inbound-normalization tests are included in the passed full suite. A separate successful focused-only rerun is not shown in the final excerpt.
- `git diff --check`: **PASS** on a fresh baseline with the identical extracted source patch; the developer's final terminal excerpt does not include a separate Git whitespace command.
- Physical line counts verified independently from the exact generated patch: route 288; inbound 63; provider status 111; helpers 10.

An earlier test run showed v2/v3 Shared-contract resolution failures, which are absent from the final successful test and TypeScript run. The exact local remediation command and resolved package version were not captured in the final terminal excerpt, so neither is invented here.

### Deviations

The developer requested the manual `.patch`/`.zip` workflow and applied the implementation from the primary Messaging checkout. This was **not** a canonical `/moda-task` mirrored-worktree execution. No launcher claim, synchronized task-worktree evidence, dedicated implementation-task branch, implementation commit/push or remote test run is claimed. This workflow deviation is recorded explicitly rather than represented as compliant agent-execution evidence.

### Assumptions

The final terminal validation refers to the six-file Attempt 1 extraction previously supplied and applied by the developer. The test run did not perform a Redis-backed trace integration scenario because the environment lacked its optional `TEST_REDIS_URL` configuration.

### Unresolved Issues

No bounded source or regression defect remains identified in MESSAGING-001. The broader webhook malformed-envelope and pre-publication validation concerns remain scoped to `ARCH-034-MESSAGING-005`.

### Architectural Concerns

None introduced by this pure extraction. The canonical task-worktree policy was not exercised under the developer's manually applied patch workflow; future agent-executed tasks should use the standard launcher.

## Architect Review

### Review Status

Accepted — Attempt 1 (2026-10-11), developer-managed patch workflow deviation recorded.

### Review Notes

Reviewed the mechanical extraction against the accepted ARCH-028 Messaging baseline. It preserves the existing normalization implementations and Shared safe-parse calls, including the 64-character provider-code bound and later-valid-code fallback. Inbound v1 message content, audio/reply context, status v3 metadata, job ID calculation and HTTP/queue effects remain unaffected. The developer's terminal evidence closes the earlier local test/typecheck failures; no code correction is necessary for this task.

The manual main-checkout application does not satisfy normal launcher worktree isolation. It is documented as an explicit developer-managed workflow deviation and no corresponding VCS provenance is inferred.

### Reviewed Files

- `app/routes/whatsapp.tsx`
- `app/lib/whatsapp/inbound-message-normalizer.ts`
- `app/lib/whatsapp/provider-status-normalizer.ts`
- `app/lib/whatsapp/normalization-utils.ts`
- `tests/whatsapp-inbound-normalization.test.mjs`
- `tests/whatsapp-provider-status.test.mjs`

### Validation Reviewed

- Developer-reported complete suite: 42 pass, 0 fail, 1 conditional skip.
- Developer-reported TypeScript typecheck and React Router client/SSR build: PASS.
- Architect's pre-delivery mechanical source extraction, syntax, patch and whitespace checks: PASS.
- No independent full test execution or signed webhook / Redis-backed system test performed by the architect.

### Architecture Conformance

Conforms to the narrowly scoped ARCH-034-MESSAGING-001 pure-normalization extraction. No database, Shared contract, HTTP/queue publication, signature verification or observability behaviour changes were introduced. Later refactor and hardening tasks retain their original distinct ownership.

### Follow-up

`ARCH-034-MESSAGING-002` is eligible for Ready. Domain `_index.md` reconciliation remains deferred until the user confirms the architecture session is complete. Do not start dependent implementation automatically.
