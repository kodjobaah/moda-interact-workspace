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
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
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

- [ ] Extract pure normalizers and update imports without altering the HTTP endpoint.
- [ ] Move the two existing normalization test suites to direct module imports without dropping assertions.
- [ ] Add/retain numeric-code overflow, v3 FAILED job-evidence data, audio/reply, pricing and malformed-input tests.
- [ ] Run focused and repository validation; record before/after module line counts and changed files.

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

- [ ] The route delegates normalization to pure modules without changing accepted inputs or normalized payloads.
- [ ] All current provider-status failure-code and deterministic-field assertions still pass.
- [ ] Text, audio, reply context, unsupported media, identities and malformed-field cases are unchanged.
- [ ] No queue/security side effects are moved into the normalizers.
- [ ] No new code catch-all or source file above 300 lines.

## Validation

Inspect the current repository `package.json` and use its actual scripts. The following existed in the inspected baseline; if they have changed, record the difference without inventing scripts.

- [ ] `node --import tsx --test tests/whatsapp-provider-status.test.mjs tests/whatsapp-inbound-normalization.test.mjs`
- [ ] `npm test`
- [ ] `npm run typecheck`
- [ ] `npm run build`
- [ ] `git diff --check`
- [ ] Record focused changed-file sizes; no new source file above 300 physical lines

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are satisfied, record the Completion Report, set status to `review`, and STOP for `moda_architect`. Never start the enabled task automatically. Use the canonical mirrored task branches and launcher-resolved physical worktrees; do not implement in a shared/default checkout.

## Implementation Notes

This is one extraction boundary: both parsers convert untrusted Meta payload fragments into canonical Shared event objects and can share only small pure parsing helpers. Do not rewrite normalization semantics. Tests should import their true module owners; React Router `loader`/`action` exports are the stable route contract.

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
