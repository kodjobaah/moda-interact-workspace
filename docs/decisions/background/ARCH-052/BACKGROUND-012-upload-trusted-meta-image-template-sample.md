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
status: review
priority: 60
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-052-ADMIN-002
  - ARCH-047-BACKGROUND-003
enables:
  - ARCH-052-SYSTEM-TEST-001
  - ARCH-052-SYSTEM-TEST-002
created: 2026-10-30
updated: 2026-10-31
---

# ARCH-052-BACKGROUND-012: Upload controlled IMAGE sample for Meta template submission

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This task definition is materialised in the dedicated parent and implementation worktrees for Attempt 1.

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
- Treat Meta transient upload errors and timeouts as retryable without Graph template CREATE. Treat permanently invalid configured sample/configuration as actionable blocked failure; report the **actual originating Meta response error and original SDK exception** through the existing Shared logger, with the distinct internal reason code. Preserve provider message/code/request ID verbatim except marked security redaction/truncation. Never log **unredacted** Graph response bodies, full URL with credentials, image bytes, access tokens or handles. Unexpected exceptions must be logged and propagated through the existing failure path; do not silently swallow.
- Require a trusted Meta app ID. If the active Render/Blueprint configuration does not provide it, **report the exact missing deployment wiring to moda_architect for a bounded moda_gateway task**; do not invent an app ID or substitute the WABA. No secrets in `render.yaml` or committed files. This is a deployment integration check, not a reason to block Admin authoring.
- Read and comply with `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/observability/shared-logging.md`, task preparation packet and dedicated mirrored worktree synchronization evidence.

**Original Meta API errors (31 October 2026):** At resumable upload
session creation, binary upload and final Graph template CREATE, log each
actual Meta failure under the existing Shared logger: original `error.message`,
`error.code`, `error_subcode`, safely bounded `error_data`, HTTP status and
Meta request/trace ID when supplied; for SDK/TLS failures preserve the actual
exception name/message/cause and label it `sdk_exception`. The internal
`META_*`/retry reason is separate and must not replace the returned message.
Do not log upload bytes, sample download payload, Meta tokens, sample handles,
complete URLs, response headers or raw unredacted bodies. Source fields may be
redacted/truncated only for security with explicit flags. A successful retry or
blocked template CREATE still requires logging the originating failure.
Do not change Admin's immutable template intent or approval/registration
lifecycle solely for logging.

## Work Items

- [x] Add a focused sample-image retrieval/upload adapter (e.g. `src/services/meta-template-management/image-header-sample.ts`) with a fixed, allowlisted Moda URL, bounded validated JPEG bytes and injected HTTP/fetch dependencies for deterministic tests.
- [x] Obtain a Meta-issued `h` from the resumable upload response using the configured App ID, Graph credentials and upload session under current WABA sender trust; classify transient/definitive errors safely. Live credentials are not available in this task environment, so the provider exchange is validated with a stub and live deployment is called out below.
- [x] Adapt frozen vs outbound provider IMAGE component validation and attach the handle **only** to a copied provider CREATE payload, preserving immutable snapshot/semantic approval and reconciliation hashing.
- [x] Integrate with existing Meta template submit worker without weakening `recordPostIntent`, claim CAS, name collision, reconciliation, failure visibility or TEXT-only flow.
- [x] Cover success and malformed/redirect/oversized MIME, invalid/missing App ID, wrong WABA, 429/5xx, malformed session/handle, repeated jobs and unknown CREATE state with focused tests.
- [x] Redact the trusted sample handle from Meta HTTP/SDK failure diagnostics when a failed IMAGE CREATE response echoes it; assert it is absent from Shared logger fields.

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

- [x] A stubbed Meta Graph upload returns a syntactically valid `h` which is accepted **only from the trusted uploader** and produces exactly one correctly authenticated IMAGE CREATE request. The implementation is capable of using a real Meta-issued `h` in an authorised live environment; no actual provider approval is claimed without live evidence. Admin, merchants and customers cannot supply a sample handle.
- [x] No immutable schema, Prisma/registration bytes, digest, role, locale, WABA identity or published template fingerprint is modified by sample enrichment; final template POST fails closed when the sample upload fails.
- [x] Frozen IMAGE registration is allowed handle-free, but Graph IMAGE CREATE never lacks a proven handle. TEXT registration/create/reconciliation paths behave exactly as before.
- [x] Provider transport errors, retries, duplicate delivery, wrong WABA, malformed data and unsafe image bytes are observed without duplicate uncertain CREATE or silent failures.
- [x] No extra infrastructure service, DB migration, R2 persistence or five-minute proof contract.

- [x] Inject distinct Meta sample-session/upload/CREATE error payloads, response absent and token-bearing errors; assert original messages/codes retained when safe, redaction flags set, credentials/handles absent and existing retry/no-CREATE behaviour unchanged. Attempt 2 verifies echoed sample handles are redacted from the Shared logger fields.
- [x] Mock a failed IMAGE CREATE whose provider message and `error_data` echo the trusted handle; assert both are redacted and the redaction flag is set.

## Validation

- [x] Existing ARCH-047 Background Meta template-management unit and integration suites, plus new mocked Meta upload/frozen-vs-provider validation and failure matrix.
- [x] Relevant Background typecheck, focused tests, changed-file lint and `git diff --check`, using actual package.json scripts.
- [x] Run the focused Meta template-management regression, lint/build and `git diff --check` after the handle-redaction correction. The focused suite passed (26 tests), lint and build passed.
- [x] Record environment/App ID and live Meta-approval checks separately; never mark actual provider approval as passing based on mocks. If environment cannot supply the App ID, return a bounded deployment gap to the architect.

## Stop Condition

Once Work Items, Acceptance Criteria and required local validation pass, complete the report, set the task to `review`, submit the mirrored implementation/parent task branches for architect review and STOP. Do not execute the enabled system tests, modify other repos or merge to main.

## Implementation Notes

Inspect the actual `src/services/meta-template-management/meta-graph.adapter.ts`, `service.ts`, `contracts.ts` and `repository.ts` at implementation start. Reuse `MetaGraphTemplateAdapter` and existing provider lifecycle; never create an Admin-to-Background HTTP API or another durable image record. Resolve Graph upload credentials and app identity in the owning Backend runtime without exposing them to the browser. Confirm which `META_APP_ID` variable is wired in the active Render Blueprint before deployment; report an ownership gap if absent.

## Completion Report

### Status

Attempt 1 was submitted for architect review. After the handle-redaction change
request, Attempt 2 is implemented and submitted for architect review.

### Files Changed

- `src/services/meta-template-management/contracts.ts`
- `src/services/meta-template-management/meta-graph.adapter.ts`
- `src/services/meta-template-management/service.ts`
- `src/services/meta-template-management/image-header-sample.ts` (new)
- `src/services/shop-brand-media/safe-fetch.ts`
- `tests/unit/services/meta-template-management/meta-management.test.ts`
- `tests/unit/services/meta-template-management/image-header-sample.test.ts` (new)
- `tests/unit/services/shop-brand-media/safe-fetch.test.ts`

### Work Completed

- Added fixed JPEG retrieval on the existing DNS-pinned HTTPS image transport with redirect rejection, peer verification, bounded timeout/bytes, exact MIME and JPEG signature checks.
- Added app-scoped Meta resumable upload with validated `META_APP_ID`, current `messaging.sender` token/WABA, exact file metadata, OAuth authorization, byte offset zero and strict session/handle parsing. A runtime-branded uploader result is required at the Graph CREATE boundary.
- Frozen IMAGE registration validation now permits a sample-free header while rejecting untrusted examples/handles. The service uploads before the durable claim and attaches the handle only to a copied provider CREATE component array. The frozen row, claim input, digest, approved semantics and reconciliation comparison remain unchanged. TEXT continues through the zero-upload flow.
- After claiming, the service verifies that the claimed frozen components still match the pre-upload snapshot before provider I/O; an intervening registration change is blocked without CREATE. The outbound copy is derived from the claimed components.
- Preserved existing WABA verification, durable claim, name-collision read, post intent, CAS persistence, unknown-state fence, retry and reconciliation behavior.
- Meta provider failures retain their original safe message/code/subcode/details/status/request ID or SDK exception/cause through the existing Shared logger. Credentials, URLs, email/phone spans, handles and bytes are excluded or redacted before emission; internal reason codes remain distinct.
- Blueprint inspection found neither `moda-messaging-worker-production` in `moda-interact-gateway/render.production.yaml` nor `moda-messaging-worker-test` in `moda-interact-gateway/render.test.yaml` explicitly declares `META_APP_ID`. Both reference WhatsApp environment groups whose contents cannot be verified from the checked-in Blueprint. The implementation blocks when `META_APP_ID` is absent. Gateway wiring is reported for architect routing; no Gateway-owned files were changed.
- Attempt-start synchronization evidence from the prepared launcher:
  - Parent task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-BACKGROUND-012`, branch `task/ARCH-052-BACKGROUND-012`, starting commit `db826ea7b4feaa0ab56900b17ede02d485a44640`; task branch fast-forward `not-needed`, `origin/main` `already-current`, claim commit `335bbfe1db05e5363bf65d3b5c4562fdc35329e0` pushed.
  - Implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-BACKGROUND-012`, branch `task/ARCH-052-BACKGROUND-012`, starting commit `f508c05dd60c37ce8125c9c4af98e292a90906e3`; task branch fast-forward `not-needed`, `origin/main` `already-current`, recursive submodules ready, database submodule at `af77c594ecbfc78c26d01c0021a090830884bbff`.

### Validation Results

- Focused Meta template-management and safe-fetch suites: **56 tests passed**.
- Guarded ARCH-047 Meta template-management PostgreSQL lifecycle integration: **1 test passed** using the disposable PostgreSQL runner.
- `npm run build` (Prisma generation and TypeScript build): **passed**.
- Changed-file ESLint and `git diff --check`: **passed**.
- Dependencies were installed in isolated `/private/tmp/moda-background-012-deps` from the task worktree lockfile; Shared 2.8.1 was used. No package manifest/lockfile changes were made.
- No live Meta upload or provider approval was performed. Mocked responses establish code path behavior only.

### Git / VCS

- Task branch: `task/ARCH-052-BACKGROUND-012` in both repositories.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-BACKGROUND-012`; implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-BACKGROUND-012`.
- Both worktrees were the prepared dedicated worktrees; neither shared checkout was switched, and no other task worktree was reused.
- Implementation repository commit: `c12419e850ea082058d69c060ebba0f4821b1865`; pushed to `origin/task/ARCH-052-BACKGROUND-012`.
- Parent workspace task file: this report, committed and pushed on `origin/task/ARCH-052-BACKGROUND-012` for this review submission.
- Submodule gitlink staged: no. Merged into implementation or workspace `main`: no.

### Deviations

Gateway worker `META_APP_ID` wiring is outside Background ownership and needs architect routing to a bounded `moda_gateway` task. Live provider credentials and approval were not exercised.

### Assumptions

`ARCH-052-ADMIN-002` is Complete and emits a frozen IMAGE registration with no example handle; ARCH-047-BACKGROUND-003 remains the owner of actual Graph CREATE.

### Unresolved Issues

Live configuration still needs Gateway confirmation: both checked-in Render Blueprints omit an explicit `META_APP_ID` entry for the messaging worker and only point at WhatsApp environment groups. Add or confirm the App ID through Gateway-owned deployment configuration before live IMAGE registration; no secret value should be committed.

### Architectural Concerns

Route the missing `META_APP_ID` Blueprint wiring to a bounded `moda_gateway` task. The Background implementation fails closed until that configuration is supplied.

## Architect Review

### Review Status

Changes Requested — Attempt 1.

### Review Notes

The failed IMAGE CREATE path can leak the trusted Meta sample handle into Shared logs when Meta echoes it in `error.message` or `error_data`. `MetaGraphTemplateAdapter.call()` currently redacts the access token but not the handle carried in the CREATE payload. Redact the trusted handle from provider/transport diagnostics and add a focused regression proving it is absent from serialized logger fields. The reported Attempt 1 validation was not rerun during this review.

### Reviewed Files

Reviewed `src/services/meta-template-management/meta-graph.adapter.ts` and its provider-error regression tests.

### Validation Reviewed

No validation rerun during this review. Run the focused handle-echo regression and task-declared lint/build for the correction.

### Architecture Conformance

The trusted sample handle must remain absent from Shared logger diagnostics on a failed IMAGE CREATE.

### Follow-up

Attempt 1 remains preserved. The task is Ready for Attempt 2.

## Attempt 2 Completion Report

### Status

Implemented and returned to `review`. Attempt 1's implementation and review
history remain preserved.

### Files Changed

- `src/services/meta-template-management/meta-graph.adapter.ts`
- `tests/unit/services/meta-template-management/meta-management.test.ts`

### Work Completed

The provider diagnostic redactor now accepts trusted sensitive values and
replaces the Meta-issued sample handle before the message, `error_data`, request
ID, or string code fields enter Shared logger diagnostics. The IMAGE CREATE path
passes only the validated trusted handle as a sensitive value. The regression
uses a Meta-issued test handle echoed in both `error.message` and `error_data`,
then asserts the Shared logger fields and serialized error contain no handle
and set `redactionApplied`. Implementation commit `82448f2` is pushed to
`origin/task/ARCH-052-BACKGROUND-012`.

### Validation Results

- Focused Meta management suite: 1 file, 26 tests passed.
- `npm run lint` — passed.
- `npm run build` — passed, including Prisma Client generation and TypeScript compilation.
- `git diff --check` — passed.
- Dependencies were installed from the task lockfile in `/private/tmp/moda-background-012-attempt2-deps`; Shared 2.8.1 was used. No package manifest or lockfile changes were made.

### Physical Worktree Isolation

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-BACKGROUND-012`, branch `task/ARCH-052-BACKGROUND-012`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-BACKGROUND-012`, branch `task/ARCH-052-BACKGROUND-012`.
- Shared workspace checkout switched/mutated for task work: no; shared implementation checkout switched/mutated: no; another task worktree reused: no.

### Start-of-Attempt Synchronization

- Parent remote task branch fast-forwarded: not needed; parent `origin/main` incorporated: yes.
- Implementation remote task branch fast-forwarded: not needed; implementation `origin/main` incorporated: already current.
- Recursive submodule sync and init/update passed; status ready. Database submodule commit: `af77c594ecbfc78c26d01c0021a090830884bbff`.

### Deviations and Unresolved Issues

No scope deviations or new blockers. The prior Gateway `META_APP_ID` configuration
follow-up remains unchanged. The task awaits architect review; this agent makes
no acceptance decision.
