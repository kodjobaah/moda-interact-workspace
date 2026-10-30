---
id: ARCH-052-BACKGROUND-012
architecture_id: ARCH-052
title: Upload a controlled IMAGE sample for Meta template submission
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-052-ADMIN-002
  - ARCH-047-BACKGROUND-003
enables:
  - ARCH-052-SYSTEM-TEST-001
  - ARCH-052-SYSTEM-TEST-002
created: 2026-10-30
updated: 2026-10-30
---

# ARCH-052-BACKGROUND-012: Upload controlled IMAGE sample for Meta template submission

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a portable canonical definition (**defined but not materialised**). It does not imply a parent or implementation worktree, Git branch, commit, or push.

## Objective

At the existing Meta template-creation boundary, turn Moda's one fixed JPEG sample into a real Meta resumable-upload `h` handle and attach it only to the outbound IMAGE template CREATE request, without changing the Admin-approved immutable registration.

## Context

Admin's `frozenLocaleSnapshot()` and `confirmMetaSubmission()` own compilation and durable registration intent; they do not call Meta Graph. Background's accepted ARCH-047-BACKGROUND-003 owns `src/services/meta-template-management/meta-graph.adapter.ts`, `service.ts` and provider create/reconciliation. Existing `validatedComponents()` currently requires `example.header_handle` even when validating the **stored** frozen IMAGE registration. An attempt to make Admin manufacture a provider handle would cross boundaries and block ARCH-052-ADMIN-002 unnecessarily.

The user's approved **sample for Meta template review** (not the merchant's customer-facing product image) is:

`https://www.modainteract.com/assets/whatsup-sample.jpeg`

The public URL displayed an image on 30 October 2026, but the exact original byte length and content signature were not independently measured here. The implementing task **must** validate them before upload. Meta template header images permit JPEG/PNG samples up to 5 MB; the provider does not prescribe one fixed pixel resolution. This task uses the provided JPEG only.

## Scope

- Implement a single server-side **trusted example-image** source for IMAGE header template registration. Keep this URL as a code-owned exact allowlist entry; do not accept a browser, merchant, model, checkout or MCP-provided URL or sample handle.
- Integrate with the existing Background Meta template-management adapter/worker. Use the authenticated Meta sender credentials and current WABA from `platformConsumerConfiguration.read("messaging.sender")` **after verifying the Meta token is authorised for the app-scoped upload operation**; obtain the Meta **application ID** from a validated deployment configuration (`META_APP_ID`, or an already-approved equivalent if the deployed source proves one exists). A WABA ID, phone number ID and Meta App ID are distinct.
- Fetch fixed sample safely with bounded time/bytes, strict hostname/path/HTTPS, no redirects, SSRF-safe DNS/peer rules, valid `image/jpeg` MIME and JPEG signature. Reject HTML/error responses, redirects, unsafe resolutions, empty/oversized or mismatched contents (<= 5,000,000 bytes). Prefer existing Shared-approved network/security primitives; do not create a generic competing HTTP/security library.
- Implement the Meta Graph resumable upload flow for the image sample: open upload session via `/{META_APP_ID}/uploads` using exact byte length/type/name, upload bytes to the returned session endpoint using the appropriate authenticated method and file offset, and parse a genuine returned `h` handle. Use the versioned Graph base already configured by the Meta adapter. Handle/token is opaque; a normal message media ID or a URL is **not** a template sample handle. Fail closed on missing/invalid/mismatched upload confirmation.
- From the current frozen registration, form a **new in-memory provider-only copy** of components and insert `HEADER.example.header_handle: [h]` into its IMAGE header, then submit through the current `MetaTemplateProvider.create()` path. Never mutate the Prisma-frozen `componentsSnapshot`, Admin AST, `submittedContentHash`, semantic bindings or publication identity; no new database table, R2 object, queue message or Shared runtime schema.
- Preserve existing validated provider CREATE preflight (`verifyWaba`, name collision GET), durable claim, POST intent/CAS, uncertain outcome reconciliation and idempotency. A sample-upload failure must not issue a Graph template-create POST, silently become a successful submission, or prevent independently approved TEXT templates from proceeding. Design the upload **before the durable CREATE claim** where practical so a temporary sample-fetch/upload failure does not strand a CREATE intent; upload retries are safe because they are not template CREATE retries.

## Out of Scope

- No merchant product image fetch, variant identity, product-media revocation checking, five-minute runtime proof, send-time IMAGE resolution, TEXT fallback selection or customer WhatsApp delivery: BACKGROUND-007 owns those.
- No Admin source changes or new template authoring/translation, Meta Graph public API route, provider media cache/database record, R2 pipeline, arbitrary image URL, image transformation service, or new infrastructure service.
- No provider update/adopt or duplicate CREATE on an uncertain provider result. Do not implement a live Meta approval bypass.

## Requirements

- Only an approved immutable IMAGE registration with exact role, locale, current sender WABA, purpose/promotion target, hash and review eligibility can reach sample upload/provider create. Reject or quarantine untrusted `example` content in frozen snapshots; TEXT remains the existing zero-upload path.
- Split/adjust Background validation explicitly: a frozen IMAGE registration **without** `header_handle` is the expected Admin transport shape, while a final **provider CREATE request** with IMAGE **must** contain exactly one valid Meta-produced handle. Keep `IMAGE_SAMPLE_HANDLE_REQUIRED` (or an equivalent fail-closed provider error) at the provider boundary, not the Admin registration-intent boundary. Never treat a nonempty arbitrary string as proof it came from Meta; only the trusted uploader return value is authorised for injection.
- Preserve `observedContentHash()`'s existing example-free comparison and the submitted digest relationship. Mock Meta examples/handles in tests but do not hardcode, print or persist live returned handles. Exact identity, category and approved semantic binding remain fixed.
- Treat Meta transient upload errors and timeouts as retryable without Graph template CREATE. Treat permanently invalid configured sample/configuration as actionable blocked failure; report bounded reason codes through the existing shared logger `@modainteract/moda-interact-shared/logging`, never raw Graph response bodies, full URL with credentials, image bytes, access tokens or handles. Unexpected exceptions must be logged and propagated through the existing failure path; do not silently swallow.
- Require a trusted Meta app ID. If the active Render/Blueprint configuration does not provide it, **report the exact missing deployment wiring to moda_architect for a bounded moda_gateway task**; do not invent an app ID or substitute the WABA. No secrets in `render.yaml` or committed files. This is a deployment integration check, not a reason to block Admin authoring.
- Read and comply with `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/observability/shared-logging.md`, task preparation packet and dedicated mirrored worktree synchronization evidence.

## Work Items

- [ ] Add a focused sample-image retrieval/upload adapter (e.g. `src/services/meta-template-management/image-header-sample.ts`) with a fixed, allowlisted Moda URL, bounded validated JPEG bytes and injected HTTP/fetch dependencies for deterministic tests.
- [ ] Obtain the real Meta `h` sample handle with the correct App ID, Graph credentials and upload session, under existing WABA sender trust; classify transient/definitive errors safely.
- [ ] Adapt frozen vs outbound provider IMAGE component validation and attach the handle **only** to a copied provider CREATE payload, preserving immutable snapshot/semantic approval and reconciliation hashing.
- [ ] Integrate with existing Meta template submit worker without weakening `recordPostIntent`, claim CAS, name collision, reconciliation, failure visibility or TEXT-only flow.
- [ ] Cover success and malformed/redirect/oversized MIME, invalid/missing App ID, wrong WABA, 429/5xx, malformed session/handle, repeated jobs and unknown CREATE state with focused tests.

## Interfaces / Contracts

**No new cross-service wire contract.** Input is the existing Admin-persisted `WhatsAppTemplateMetaRegistration`: `componentsSnapshot` with `HEADER.format: "IMAGE"`, no sample handle, preserved `parameterBindingsSnapshot`, `submittedContentHash`, current locale and WABA. Output is the existing provider call `MetaTemplateProvider.create({ ...claim, components: providerOnlyComponents })` with one `HEADER.example.header_handle = [metaIssuedH]`. The uploader returns a **Background-local** typed result such as `{kind:"READY", handle:string}` or throws a typed failure; the sample handle is never part of immutable provider identity or approval hashes. Reuse existing `MetaManagementError` dispositions and `observedContentHash()` conventions.

**Configuration:** `META_APP_ID` identifies the Meta application for `/{app-id}/uploads`; `platformConsumerConfiguration.read("messaging.sender")` remains owner of the current WABA and Meta access token. The canonical image URL is code-owned and is not a merchant setting. Versioned Graph endpoint stays on the current adapter config. Validate actual credentials and `META_APP_ID` before live requests; no fabricated environment fallback.

## Dependencies

- `ARCH-052-ADMIN-002` — accepted sample-free immutable IMAGE registration intent and existing authoring/selection.
- `ARCH-047-BACKGROUND-003` — accepted existing Meta registration provider adapter, durable intents, reconciliation and logging.

## Enables

- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] A stubbed Meta Graph upload returns a syntactically valid `h` which is accepted **only from the trusted uploader** and produces exactly one correctly authenticated IMAGE CREATE request. The implementation is capable of using a real Meta-issued `h` in an authorised live environment; no actual provider approval is claimed without live evidence. Admin, merchants and customers cannot supply a sample handle.
- [ ] No immutable schema, Prisma/registration bytes, digest, role, locale, WABA identity or published template fingerprint is modified by sample enrichment; final template POST fails closed when the sample upload fails.
- [ ] Frozen IMAGE registration is allowed handle-free, but Graph IMAGE CREATE never lacks a proven handle. TEXT registration/create/reconciliation paths behave exactly as before.
- [ ] Provider transport errors, retries, duplicate delivery, wrong WABA, malformed data and unsafe image bytes are observed without duplicate uncertain CREATE or silent failures.
- [ ] No extra infrastructure service, DB migration, R2 persistence or five-minute proof contract.

## Validation

- [ ] Existing ARCH-047 Background Meta template-management unit and integration suites, plus new mocked Meta upload/frozen-vs-provider validation and failure matrix.
- [ ] Relevant Background typecheck, focused tests, changed-file lint and `git diff --check`, using actual package.json scripts.
- [ ] Record environment/App ID and live Meta-approval checks separately; never mark actual provider approval as passing based on mocks. If environment cannot supply the App ID, return a bounded deployment gap to the architect.

## Stop Condition

Once Work Items, Acceptance Criteria and required local validation pass, complete the report, set the task to `review`, submit the mirrored implementation/parent task branches for architect review and STOP. Do not execute the enabled system tests, modify other repos or merge to main.

## Implementation Notes

Inspect the actual `src/services/meta-template-management/meta-graph.adapter.ts`, `service.ts`, `contracts.ts` and `repository.ts` at implementation start. Reuse `MetaGraphTemplateAdapter` and existing provider lifecycle; never create an Admin-to-Background HTTP API or another durable image record. Resolve Graph upload credentials and app identity in the owning Backend runtime without exposing them to the browser. Confirm which `META_APP_ID` variable is wired in the active Render Blueprint before deployment; report an ownership gap if absent.

## Completion Report

### Status

Not Started.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

`ARCH-052-ADMIN-002` will emit a frozen IMAGE registration with no example handle after its accepted correction; ARCH-047-BACKGROUND-003 remains the owner of actual Graph CREATE.

### Unresolved Issues

None established by implementation. `META_APP_ID` deployment wiring is a required live integration check.

### Architectural Concerns

Return provider/credential boundary changes to `moda_architect` instead of editing another repository.

## Architect Review

### Review Status

Pending.

### Review Notes

Planning only. This task is Pending until ADMIN-002 is architect-accepted Complete. No Background implementation or live Meta upload has been performed.

### Reviewed Files

The existing Background Meta adapter and ADMIN-002 task/source were inspected to define the split.

### Validation Reviewed

No implementation tests executed.

### Architecture Conformance

To be determined after implementation review.

### Follow-up

Materialise through `/moda-task ARCH-052-BACKGROUND-012` only when `depends_on` is Complete.
