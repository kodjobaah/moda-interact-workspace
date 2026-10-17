---
id: ARCH-043-ADMIN-001
architecture_id: ARCH-043
title: Implement contract-driven platform configuration editor
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-043-DATABASE-001
enables:
  - ARCH-043-GATEWAY-001
  - ARCH-043-SYSTEM-TEST-001
created: '2026-10-17'
updated: '2026-10-17'
---
# Contract-driven Platform Configuration Editor

## Architecture

- `ARCH-043` — `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Exact table contract, supported policy keys, shapes and bounds: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Source baseline: 17 October 2026 `moda-interact-admin`: `src/components/admin/mcp-execution-policy/mcp-execution-policy-fields.tsx`, `src/components/admin/commerce-model-policy/budget-policy-fields.tsx`, `src/app/actions/mcp-execution-policy.ts`, `src/lib/auth/platform-admin.ts`, `src/components/admin/sidebar.tsx`, `src/app/(protected)/system-controls/platform-policy/page.tsx`.
- Portable definition, **defined but not materialised**. `moda_architect` coordinates acceptance; implementation belongs to `moda_admin`.

## Objective

Provide **one reusable, trusted-contract-driven configuration editor and persistence service** for all six non-secret ARCH-043 policy groups. Adding an approved non-secret **field or configuration group** must require a registry contract change, not a bespoke React form, page, navigation entry, server action, or database write path. Consumer runtime behaviour remains independently owned by the consuming service.

## Context

`PlatformConfiguration` and `PlatformConfigurationAudit` are introduced by `ARCH-043-DATABASE-001`. Existing Admin pages already generate fields from definitions, but validation, versioning, saving and history are currently implemented per domain. ARCH-043 must not replicate that architecture six times. Admin is the authoring boundary; each runtime consumer still validates its own loaded settings. **No new Shared implementation or publication task** is required. Existing `@modainteract/moda-interact-shared` exports remain available for other use.

## Scope

1. An Admin-owned **server-side allowlisted registry** of six policy contracts. One contract declaration is authoritative for both render metadata and the server validator (types, required/nullable fields, ranges, enums and unknown-field rejection), safe defaults/reset behaviour and per-contract permissions. Group navigation is derived from the same registry.
2. A generic `<ConfigurationEditor>` and compact reusable field renderer for `integer`, `string`, `enum`, `boolean`, `nullable-https-url` and a reserved `secret` field kind. The `secret` field kind is UI-only in this task; secret writes are **rejected** until ADMIN-002.
3. A single authenticated Admin read/save/reset/history service using `PlatformConfiguration` and `PlatformConfigurationAudit`, environment scoping, monotonic compare-and-set (CAS), and transactional audit.
4. A single page under existing **System Controls > Platform Configuration**, with grouped selector and history panel, using existing `AdminShell` and `Sidebar` conventions; preserve existing platform-policy screens and their DB models.
5. `admin.grafana` navigation reads from the new validated config without changing exporter/runtime observability wiring.
6. Focused contract, form, security, concurrency, audit and UI tests, including a test-only contract proving that a new field and a new group work without feature-specific UI or persistence changes.

## Out of Scope

- No new Prisma models/migrations, new encryption/decryption or Shared package exports, domain policy migrations, Runtime consumers, Gateway edits, `_index.md` edits, or refactors to existing billing/MCP/model-policy forms.
- No plaintext/ciphertext secret listing or mutation through the ordinary settings endpoint. The `secret` renderer is introduced for ADMIN-002 reuse, but is disabled for ordinary policy saves.
- No bulk migration from `.env`, no environment switcher that can edit another deployment, and no freeform JSON editor.

## Requirements

### A. Closed, declarative contract registry (server is authoritative)

Each entry is a trusted, immutable typed declaration of the following conceptual shape (implementation may choose concrete TypeScript types):

```typescript
interface ConfigurationContract<T> {
  key: string;                    // allowlisted stable persisted key
  title: string;
  description: string;
  kind: 'policy' | 'secret';       // ADMIN-001 persists 'policy' only
  fields: readonly FieldContract[];
  validate(values: unknown): T;   // derived from field declarations plus optional cross-field refinement
  defaults?: T;                   // only where code-safe defaults exist
  canReset: boolean;             // true only when defaults are legitimate
  requiredRole: 'SUPER_ADMIN';
}
type FieldContract =
  | {name:string; kind:'integer'; label:string; description:string; min:number; max:number; unit?:string}
  | {name:string; kind:'boolean'; label:string; description:string}
  | {name:string; kind:'string'; label:string; description:string; maxLength:number}
  | {name:string; kind:'enum'; label:string; description:string; options:readonly string[]}
  | {name:string; kind:'nullable-https-url'; label:string; description:string; maxLength:number}
  | {name:string; kind:'secret'; label:string; description:string; writeOnly:true};
```

- The browser receives display-safe contract metadata only; never accepts a client-provided schema, default, authorised key list, `environment`, or role as authoritative.
- Use Zod or the repository's existing validation mechanism **in Admin**, with closed object checks, strict numeric parsing and bounded strings. The registry must be the **single source of truth** for per-field type, optionality, bounds, enum choices and display metadata; the server validator must be generated from, or mechanically tied to, the exact same field declarations. Permit a small server-only per-contract cross-field refinement for rules such as Commerce preview deadline; never maintain a second hand-written copy of the individual field definitions. Share *documented shapes* with runtime owners via ARCH-043 architecture. Do not duplicate existing ARCH-039 cryptography.
- Register exactly the **six policy keys** in the schema review, with every field and bound from that source:

| Contract key | Fields rendered from registry | Notes |
|---|---|---|
| `woo.couponSync` | `dispatchBatchSize`, `refreshIntervalMinutes`, `dispatchCooldownMinutes`, `unavailableRecheckMinutes`, `staleScanMinutes`, `maxPages`, `requestTimeoutMs`, `maxResponseBytes`, `maxScanDurationMs`, `workerConcurrency` | Ten strictly bounded integers; no invented `enabled` flag; workerConcurrency is a runtime-consumer concern |
| `merchantKnowledge.upload` | `maxUploadBytes`, `maxXlsxUncompressedBytes`, `r2Endpoint`, `r2Bucket` | Both R2 endpoint and bucket remain editable on every authorised revision; no placeholder URL/bucket accepted as production config; strict HTTPS and bucket validation; relocation owned by separate tasks |
| `speech.transcription` | `provider`, `groqModelId`, `openaiModelId` | Provider enum and bounded model IDs |
| `support.translation` | `provider`, `model` | Restrict to support-message translation; do not edit Commerce translation policy |
| `commerce.preview` | `deadlineMs`, `outputTokens` | Enforce bounded integers and `deadlineMs <= PREVIEW_SLOT_MS - 30000`; obtain actual slot limit from approved code contract, not guessed input |
| `admin.grafana` | `baseUrl`, `logsUrl`, `metricsUrl`, `tracesUrl`, `platformDashboardUrl` | Nullable HTTPS URLs <=2048, no embedded credentials, tokens or fragments intended to carry secrets |

- Do not invent defaults for required `merchantKnowledge.upload` endpoint/bucket or support-translation models. Where no safe full default exists, the editor starts unconfigured and **Reset** is unavailable. Field descriptions, units and existing enforced bounds are authoritative.
- Both form rendering and server-side validation use the server-owned registry; the validator re-runs on every mutation. The browser receives only safe serialisable presentation descriptors (not executable validators). No dynamically executed formulas or caller-provided executable contract.

### B. One editor component, no per-key bespoke form

- Proposed repository-local layout (adapt only if existing structure clearly warrants it):

```text
src/lib/admin/platform-configuration/
  contracts.ts              # allowlisted metadata, validation, defaults
  repository.ts             # DB transaction/CAS and audit
  service.ts                # authorised read/mutate API
  errors.ts                 # bounded typed domain outcomes
src/components/admin/platform-configuration/
  configuration-editor.tsx  # contract-driven form and save state
  configuration-field.tsx   # declarative renderer
  configuration-history.tsx # safe audit list
src/app/actions/platform-configuration.ts
src/app/(protected)/system-controls/platform-configuration/page.tsx
```

- Render title, description, units, controls, inline field/server errors, version, modified timestamp, actor, reason, Reset when allowed, and paginated audit. A changed setting does not require adding a hand-written page.
- No auto-refresh while editing; show explicit Refresh. Dirty edits must not be silently overwritten; disable duplicate Save/Reset while submitting; show version conflicts with reload guidance. Preserve accessibility labels and keyboard form submission.
- `secret` field kind may render a write-only password control in the reusable component, but must *never* be populated from persistence. No secret API is authorised in this task.

### C. Extensibility contract — add settings without writing another form

- **Adding a field:** Register one reviewed `FieldContract` on an existing allowlisted group; the generic editor, field-level errors, strict server validator, default presentation, versioned Save/Reset, and audit path must recognise it without any new per-key React component, server action, repository function, navigation entry or Prisma migration. Update the consuming service separately when it must act on the new setting. An illustrative `maxRetries` value is **not** part of the six approved production contracts and must not be added to `woo.couponSync` by this task.
- **Adding a group:** Register one reviewed `ConfigurationContract` in the server's allowlisted registry. The group selector, generic read/save/reset/history handlers and persistence of `(environment, key)` must work without adding a dedicated page/route or database table. Registration is a code change reviewed and deployed with the Admin application, **not** creation of arbitrary keys/contracts by an administrator or browser.
- **Single validation source:** Per-field input type, bounds, enum membership, nullable/required status and display labels derive from the same descriptors. Complex inter-field invariants may be expressed in one separate server-owned contract refinement, without duplicating individual field constraints. Unknown properties remain rejected; only `policy` contracts may be persisted by ADMIN-001.
- **Existing records:** When a reviewed contract adds a field, a prior JSON row may lack it. The generic loader must report a missing/invalid field safely, or present a **contract-approved** default without silently mutating PostgreSQL on read. Saving the complete validated document uses the same CAS/audit transaction. Never fabricate defaults for required values (for example, R2 endpoint or bucket), delete records, or reset the version to zero.
- **Test-only extension proof:** In tests, inject a temporary allowlisted policy contract, for example `fixture.sample` containing an `enabled:boolean` and `retryLimit:integer` field with a range. Assert that it appears in the group selector, renders the appropriate controls, rejects invalid values at the server boundary, persists through the **existing generic** create/update method, and produces version 1 and one audit entry. Add a test-only field to that contract and prove the renderer and persistence handle it without changes to the generic UI/server action/repository. The fixture must **not** ship in the production registry or appear as a production setting.
- **Scope of automatic behaviour:** Contract registration automates Admin rendering, validation, navigation and persistence only. It does not implement new consumer business behaviour, authorise dynamic schemas, or avoid service-side validation/deployment when adding a runtime feature.

### C. One persistence contract and transaction

Implement server-side functions with equivalent semantics:

```typescript
readPlatformConfiguration(key: ApprovedKey): Promise<{
  key: ApprovedKey; value: unknown | null; version: number; updatedAt: string | null;
}>;
updatePlatformConfiguration(input: {
  key: ApprovedPolicyKey; expectedVersion: number;
  values: unknown; reason?: string;
}): Promise<{key:ApprovedPolicyKey; version:number}>;
resetPlatformConfiguration(input: {
  key: ApprovedPolicyKey; expectedVersion: number; reason?: string;
}): Promise<{key:ApprovedPolicyKey; version:number}>;
listPlatformConfigurationAudit(key: ApprovedKey, cursor?: string): Promise<PaginatedRedactedHistory>;
```

- **Security:** use `requirePlatformAdminRead/Mutation()` and check an active `SUPER_ADMIN` principal server-side; never trust client-provided actor/environment; explicitly reject unsupported keys, nested extra fields, secret keys and sensitive values. Allow development bypass only according to current auth policy, with explicit tests that hosted/production cannot bypass auth.
- **Environment:** resolve from trusted deployment configuration, validate allowlist, reject `unknown` and any cross-environment request. Never fall back from production to development.
- **CAS/audit:** `expectedVersion:0` creates row at version 1; `expectedVersion:N` updates only row whose current version equals N and sets N+1. Use unique constraint and `updateMany`/transaction conditional logic; stale replay after Reset still fails. A Reset overwrites with validated approved defaults and increments version—never delete row. Successful create/update/reset writes precisely one audit event in the **same PostgreSQL transaction**, with verified `actorId`, `beforeValue`, `afterValue`, expected/resulting revision and optional bounded reason. Failed/conflicting transactions create no audit. No outbound provider/network calls inside DB transaction.
- **Read:** never return all environments, raw secret envelopes, or unauthorised audit entries; stable error codes for invalid input, forbidden, not configured, stale/conflict and DB-unavailable cases, with no error object or credentials leaked to UI.
- Pagination on audit to avoid unbounded history. Existing `PlatformConfiguration` has no durable `operationId` uniqueness field; do not claim retry-exactly-once beyond CAS/no duplicate changes.
- For `admin.grafana`, render only valid safe HTTPS links and retain the current observability page if policy is absent. Do not change OTEL/LOKI secrets or exporters.

## Work Items

- [ ] Implement the closed six-key Admin registry with **one authoritative field declaration** driving both form rendering and strict server validation; allow only bounded server-owned cross-field refinements.
- [ ] Implement generic field renderer, edit form, inline errors, pending state, Refresh, Reset where safe and audit/history UI.
- [ ] Integrate a single System Controls page and sidebar navigation; no bespoke forms for individual policy groups.
- [ ] Implement authenticated Admin-only read/save/reset/audit server handlers with strict allowlist and trusted environment.
- [ ] Implement transactional create/update/Reset CAS and append-only audit with actor and no deletion/version reset.
- [ ] Integrate validated `admin.grafana` navigation safely.
- [ ] Add an isolated test-only contract extension fixture proving new-field and new-group rendering, validation, generic Save and transactional audit without new feature-specific UI or persistence code. Do not ship the fixture in the production allowlist.
- [ ] Add required tests and document actual files/validation/isolation in Completion Report; stop at Review.

## Interfaces / Contracts

- Persistence owner: `ARCH-043-DATABASE-001` (`PlatformConfiguration` and `PlatformConfigurationAudit`). Confirm migration and generated Prisma client are available before coding.
- Policy shapes/defaults/ranges: `docs/architecture/ARCH-043-configuration-schema-review.md`; Admin owns the authoring/rendering registry and service-side validation, while each consumer validates its own loaded snapshot against this documented contract.
- No new Shared exports/publication. Existing login/role checks: `src/lib/auth/platform-admin.ts`. Existing Admin shell/sidebar, React field patterns and structured logging remain in use.
- `ADMIN-002` extends this renderer/registry with protected secret contracts and a separate secret writer; `ADMIN-001` must not implement that writer.

## Dependencies

- `ARCH-043-DATABASE-001`

## Enables

- `ARCH-043-ADMIN-002`
- `ARCH-043-GATEWAY-001`
- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] A single `ConfigurationEditor` renders all six approved policy contracts; the field registry generates both UI and server field validation, without duplicate per-field definitions.
- [ ] A test-only **new field and new policy group** are rendered, validated and saved with the existing generic editor/action/repository, appear in registry-driven navigation, and produce a versioned value and audit entry; no bespoke page, mutation handler or database migration is required. The fixture is absent from the production registry.
- [ ] An existing row missing a newly introduced field is read safely, and any approved default is only persisted through an explicit version-checked Save; invalid/missing required values never become silently valid.
- [ ] Server independently validates each field/value; unknown keys, unknown fields, secret-purpose keys and client-provided schema/environment/role are rejected.
- [ ] Only an authorised SUPER_ADMIN can update; non-admin read/edit/CSRF-protected action tests retain existing Admin security model.
- [ ] First create produces version 1; concurrent/stale updates and create→Reset→replay cannot overwrite newer values.
- [ ] Every successful mutation writes exactly one matching audit event atomically; failures write none, and Reset does not delete/recreate.
- [ ] The UI displays version, safe field errors and audit, disables duplicate actions, and does not auto-refresh while editing.
- [ ] Unsafe/absent R2 values are not silently defaulted; Grafana URLs are safe and optional; no sensitive content leaks into server output or logs.

## Validation

- [ ] Contract tests for all 26 specified policy fields, strict bounds, missing required values, unknown fields and reserved secret keys.
- [ ] Component tests for declarative controls, field errors, Submit/Reset, pending state, refresh, accessibility and conflict handling; prove selector and controls derive from registry additions (including a test-only new field and group).
- [ ] Auth/authz tests including role, environment spoofing, development-bypass boundaries and redacted read endpoints.
- [ ] Disposable PostgreSQL integration: create/update/Reset, concurrent CAS, create→Reset→stale replay, audit atomicity, unique scope isolation, pagination; a test-only registered contract must exercise the same generic save/audit path with no extra tables or per-key SQL.
- [ ] Existing Admin relevant unit suites plus typecheck, lint, build, `git diff --check`; record actual commands and outcomes.

## Stop Condition

Complete only this task. Set `status: review`, complete its report with launcher-resolved physical worktree isolation and synchronization evidence, return to `moda_architect` and STOP. Do not begin ADMIN-002 or change `_index.md`.

## Implementation Notes

- Keep field descriptors and server-side validators derived from one Admin-owned registry rather than maintaining separate hand-written schema copies. Support a test-only registry injection (or equivalent pure registry factory) so extensibility is proven without modifying the production key allowlist. Separate generic UI rendering from privileged persistence to permit testing without a database.
- Prefer existing Admin Zod/testing conventions, authenticated Server Actions and existing `@modainteract/moda-interact-shared/logging`; do not create an additional generic logger or shared framework.
- Do not change the meanings of existing six policy keys or existing domain-specific database models.

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

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

Awaiting implementation and validation evidence.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Not yet assessed.

### Follow-up

None
