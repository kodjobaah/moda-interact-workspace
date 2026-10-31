---
id: ARCH-054-SHARED-001
architecture_id: ARCH-054
title: Define strict v1 merchant AI response delay wire schemas
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-054-SHARED-002
created: 2026-10-31
updated: 2026-10-31
---


# ARCH-054-SHARED-001: Define strict v1 merchant AI response delay wire schemas


## Architecture

Architecture: `ARCH-054`

Document: `docs/architecture/ARCH-054-merchant-configurable-ai-response-delay.md`

Coordinator: `moda_architect`. Task **defined but not materialised**; no local Git/worktree/branch activity is claimed.


## Objective

Publish one canonical, typed Zod wire contract for merchant response-delay GET/PUT, shared between hosted API and Shopify and documented for Woo PHP.


## Context

ARCH-054 adds a **merchant-selectable integer 0–30 minute AI reply delay** to the existing ARCH-040 recovery-conversation processor and handover controls, leaving merchant-authored HUMAN replies without configured delay. See the parent architecture and current snapshot for specific boundaries.


## Scope

Create `src/ai-response-delay.ts` and `src/ai-response-delay.test.ts` in `moda-interact-shared`. Modify `package.json` exports to expose `./ai-response-delay` and `tsup.config.ts` to declare `"ai-response-delay": "src/ai-response-delay.ts"` in the existing entry map; change `tsconfig` only if necessary. No consumers in this task.


## Out of Scope

No unrelated architecture changes, new standalone chat service, per-user timer jobs, invented provider error explanations, or updates to `docs/decisions/**/_index.md`. No implementation outside the assigned repository.


## Requirements

- Export the literal `AI_RESPONSE_DELAY_SCHEMA_VERSION = 1 as const`. Export `AiResponseDelayMinutesSchema = z.number().int().min(0).max(30)`; use Zod 4 as pinned by the repository.
- Export `AiResponseDelayRevisionSchema = z.union([z.literal("UNCONFIGURED"), z.string().regex(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/)])`; consumers also verify actual Date parsing when receiving a revision; do not interpret revision as a duration.
- Export `MerchantAiResponseDelayReadV1Schema = z.strictObject({ schemaVersion:z.literal(1), revision:AiResponseDelayRevisionSchema, aiResponseDelayMinutes:AiResponseDelayMinutesSchema })`.
- Export `MerchantAiResponseDelayWriteV1Schema = z.strictObject({ schemaVersion:z.literal(1), expectedRevision:AiResponseDelayRevisionSchema, aiResponseDelayMinutes:AiResponseDelayMinutesSchema })`.
- Export the exact inferred types `AiResponseDelayMinutes`, `AiResponseDelayRevision`, `MerchantAiResponseDelayReadV1`, `MerchantAiResponseDelayWriteV1`; no aliases/legacy v2 or optional fields. Do not encode database, tenant, auth, concurrency or lifecycle policy in Zod.
- Illustrative request `{ "schemaVersion":1, "expectedRevision":"UNCONFIGURED", "aiResponseDelayMinutes":7 }`; response `{ "schemaVersion":1, "revision":"2026-10-31T16:28:55.123Z", "aiResponseDelayMinutes":7 }`.
- Test valid 0,1,7,30; invalid -1,31,0.5,"7",null,missing/extra fields, wrong schemaVersion; both revision variants, malformed timestamps; strict unknown keys. Verify package subpath works from built `dist/ai-response-delay.js` and `.d.ts` and from `package.json` resolution.


## Work Items

- [ ] Add exact schemas/types with comments identifying producer/consumers.
- [ ] Add focused positive/negative tests for READ and WRITE contracts.
- [ ] Add exact `"ai-response-delay": "src/ai-response-delay.ts"` to `tsup.config.ts` entry map, declare `./ai-response-delay` with `types: ./dist/ai-response-delay.d.ts` and `import: ./dist/ai-response-delay.js` in `package.json`, build both JS and type declarations, and test exported subpath.


## Interfaces / Contracts

Exact file: `src/ai-response-delay.ts` (publish unchanged through `./ai-response-delay`):

```typescript
import { z } from "zod";

export const AI_RESPONSE_DELAY_SCHEMA_VERSION = 1 as const;

export const AiResponseDelayMinutesSchema =
  z.number().int().min(0).max(30);

export const AiResponseDelayRevisionSchema = z.union([
  z.literal("UNCONFIGURED"),
  z.string().regex(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/),
]);

export const MerchantAiResponseDelayReadV1Schema = z.strictObject({
  schemaVersion: z.literal(AI_RESPONSE_DELAY_SCHEMA_VERSION),
  revision: AiResponseDelayRevisionSchema,
  aiResponseDelayMinutes: AiResponseDelayMinutesSchema,
});

export const MerchantAiResponseDelayWriteV1Schema = z.strictObject({
  schemaVersion: z.literal(AI_RESPONSE_DELAY_SCHEMA_VERSION),
  expectedRevision: AiResponseDelayRevisionSchema,
  aiResponseDelayMinutes: AiResponseDelayMinutesSchema,
});

export type AiResponseDelayMinutes =
  z.infer<typeof AiResponseDelayMinutesSchema>;
export type AiResponseDelayRevision =
  z.infer<typeof AiResponseDelayRevisionSchema>;
export type MerchantAiResponseDelayReadV1 =
  z.infer<typeof MerchantAiResponseDelayReadV1Schema>;
export type MerchantAiResponseDelayWriteV1 =
  z.infer<typeof MerchantAiResponseDelayWriteV1Schema>;
```

Exact valid PUT:

```json
{"schemaVersion":1,"expectedRevision":"UNCONFIGURED","aiResponseDelayMinutes":7}
```

Exact valid GET/PUT response:

```json
{"schemaVersion":1,"revision":"2026-10-31T16:28:55.123Z","aiResponseDelayMinutes":7}
```

Exact invalid examples: `{"schemaVersion":1,"expectedRevision":"UNCONFIGURED","aiResponseDelayMinutes":31}`, `{"schemaVersion":1,"expectedRevision":"UNCONFIGURED","aiResponseDelayMinutes":"7"}`, `{"schemaVersion":1,"expectedRevision":"UNCONFIGURED","aiResponseDelayMinutes":7,"shopId":"forged"}`. No `.optional()`, coercion, unknown-key stripping, or v2. Ownership: Shared; consumers: hosted Woo API, Shopify settings; PHP WordPress server validates the same wire surface but cannot import Node package.


## Dependencies

None


## Enables

- ARCH-054-SHARED-002


## Acceptance Criteria

- [ ] Export names, field names and strictness match architecture verbatim.
- [ ] Unknown fields and invalid 0–30 values are rejected; existing `./recovery-policy` remains unchanged.
- [ ] All tests and package build pass; no duplicate local TypeScript contract is introduced in consumer repositories.


## Validation

- [ ] `npx tsx --test src/ai-response-delay.test.ts`; `npm run typecheck`; `npm run build`; `git diff --check`.


## Stop Condition

After all required Work Items, Acceptance Criteria and Validation are complete, update Completion Report, set status to `review`, return control to `moda_architect` and **STOP**. Do not implement dependent tasks. Publication tasks do not rerun accepted implementation validation.


## Implementation Notes

The regex is a wire shape check, not business eligibility. Never silently coerce floats/strings. Use no unrelated Shared refactor.


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
