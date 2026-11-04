---
id: ARCH-058-SHARED-004
architecture_id: ARCH-058
title: Remove the obsolete MCP conversation tool-context contract
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 36
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-058-SHARED-003
enables:
  - ARCH-058-SHARED-005
  - ARCH-058-SHARED-006
  - ARCH-058-SYSTEM-TEST-001
created: 2026-11-04
updated: 2026-11-04
---

# ARCH-058-SHARED-004: Remove the obsolete MCP conversation tool-context contract

## Architecture

Architecture ID: `ARCH-058`.

Parent: `docs/architecture/ARCH-058-commerce-agent-product-discovery.md`.

Boundary decision: MCP is a shop-scoped tool provider/executor. Background owns conversation identity, inbound version, retained grants, leases and human-control state. `docs/architecture/ARCH-058/contracts.md`, section 4.1, is authoritative.

Coordinator: `moda_architect`.

This task replaces the unexecuted revision-9 SHARED-004 publication task. Publication is now SHARED-006 because the final package must contain SHARED-003, SHARED-004 and SHARED-005 together.

## Objective

Remove the unused `CommerceConversationToolContextSchema` and `CommerceConversationToolContext` public exports that imply MCP understands conversation state, while preserving the legitimate Background/runner conversation contracts and the separately accepted outreach tool context.

## Context

The current source exports `CommerceConversationToolContextSchema` with `conversationId`, `inboundVersion` and `grantId`, but the corrected ARCH-058 runtime explicitly does not send or interpret that structure in MCP. Keeping the export invites future agents to restore the incorrect ownership boundary.

Background may continue to use `CommerceTurnIdentitySchema`, `CommerceAssertionSchema` and `CommerceConversationGrantSchema` locally. Existing initial-outreach adapters may continue to use `CommerceOutreachToolContextSchema` through the opaque trusted MCP `toolContext`; this task must not remove or change that separate contract.

## Scope

Modify only:

- `src/commerce/schemas.ts`
- `src/commerce/product-discovery-contracts.test.ts`
- `scripts/validate-commerce-entrypoints.mjs`
- `README.md`

If generated declarations are produced by the ordinary build, validate them but do not commit generated output unless that is already repository policy.

## Out of Scope

- Removing `CommerceTurnIdentitySchema`, `CommerceResolveAssertionSchema`, `CommerceExecuteAssertionSchema`, `CommerceAssertionSchema` or `CommerceConversationGrantSchema`.
- Removing or changing `CommerceOutreachToolContextSchema` or outreach execution behavior.
- Changing MCP request parsing, opaque `toolContext`, Background transport code or application behavior.
- Any hash work; SHARED-003 owns built-in identity.
- Date/time validation; SHARED-005 owns it.
- Package version/publication; SHARED-006 owns it.

## Requirements

1. Remove `CommerceConversationToolContextSchema` and `CommerceConversationToolContext` from the `/commerce` public surface.
2. Delete focused tests and entrypoint assertions whose only purpose is to validate/export that obsolete contract.
3. Update README export documentation to state the ownership boundary explicitly: Background owns conversation/grant/turn state; MCP receives authenticated shop identity and may forward only already accepted opaque adapter context such as outreach context.
4. Preserve the existing public conversation/runner schemas listed under Out of Scope without shape changes.
5. Preserve `CommerceOutreachToolContextSchema` unchanged.
6. Do not introduce a replacement conversation-to-MCP schema under another name.

## Work Items

- [ ] Remove the obsolete schema/type exports.
- [ ] Remove their focused tests and clean-process export check.
- [ ] Correct README contract ownership text.
- [ ] Prove legitimate conversation/grant and outreach exports remain available.
- [ ] Run the required validation.

## Interfaces / Contracts

Removed public API in the later SHARED-006 major release:

```text
CommerceConversationToolContextSchema
CommerceConversationToolContext
```

Preserved examples include:

```text
CommerceTurnIdentitySchema
CommerceAssertionSchema
CommerceConversationGrantSchema
CommerceOutreachToolContextSchema
```

## Dependencies

- `ARCH-058-SHARED-003`

## Enables

- `ARCH-058-SHARED-005`
- `ARCH-058-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] `CommerceConversationToolContextSchema` and `CommerceConversationToolContext` are absent from source/declarations/entrypoint inventory.
- [ ] No replacement public contract sends conversation ID, grant ID, inbound version, lease or human-control state to MCP.
- [ ] `CommerceAssertionSchema`, `CommerceConversationGrantSchema` and `CommerceOutreachToolContextSchema` retain their current shapes.
- [ ] Product-discovery and runner focused tests pass.
- [ ] No application repository is modified by this task.

## Validation

```bash
npm ci --no-audit --no-fund
npm run test:product-discovery-contracts
npm run typecheck
npm run build
npm run validate:commerce-entrypoints
rg -n 'CommerceConversationToolContext' src/commerce --glob '!*.test.ts' || true
git diff --check
```

The grep must produce no occurrence in production Commerce source. Negative tests, the entrypoint verifier and README may name the removed export while proving/documenting its absence. `npm run validate:commerce-entrypoints` must prove the built `/commerce` package does not export either removed symbol.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, set status to `review`, complete the report, return to `moda_architect` and STOP. Do not begin SHARED-005 or publication.

## Implementation Notes

Do not confuse the removed conversation-specific contract with the existing opaque `toolContext` transport extension point. The latter remains available for already accepted adapters such as initial outreach; MCP discovery/authorization does not interpret it as conversation authority.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

SHARED-003 will already have removed built-in hashes before this task starts.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Not reviewed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
