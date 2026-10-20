---
id: ARCH-035-WOOCOMMERCE-015
architecture_id: ARCH-035
title: Connect W003 and W004 to real feature and knowledge services
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 52
executor: developer
claimed_at: 2026-10-19T02:28:24Z
attempt: 1
depends_on: [ARCH-035-WOOCOMMERCE-003, ARCH-035-WOOCOMMERCE-004, ARCH-035-WOOCOMMERCE-014, ARCH-035-GATEWAY-001]
enables: [ARCH-035-SYSTEM-TEST-004]
created: 2026-10-16
updated: 2026-10-20
---

# ARCH-035-WOOCOMMERCE-015 — Connect W003 and W004 to real feature and knowledge services

## Architecture

- Parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`, approved 16 October functional knowledge extension.
- Owner: `moda_woocommerce`, repository `moda-interact-woocommerce`; coordinator: `moda_architect`.
- **Materialised and claimed — developer Attempt 1, 2026-10-19.** The canonical parent and implementation worktrees and mirrored task branches were created from refreshed `origin/main`; the developer explicitly took over execution and completion authority while preserving `assigned_agent: moda_woocommerce`.

## Objective

Replace fixture-only unavailable feature and Merchant Knowledge adapters with approved live WordPress data and actions without changing their existing UX architecture.

## Context

W003 supplies the conversation feature controls and W004 supplies the Merchant Knowledge section. Their UI-only acceptance allowed honest disabled states; API-014..017 and WOO-014 now make these states live.

## Scope

- Wire production `feature-preferences-client.js` to WOO-014; reconcile W003 controller body `preferences` to API-014 `changes` and stale CAS handling while showing effective vs optional feature state.
- Wire W004 knowledge client/controller to live read/add/edit/delete/refresh/reorder/upload/replace/reprocess; ensure configured sources remain accessible while merchant feature is off.
- Maintain source list statuses and cap counts from authoritative data, no fake success, dedupe actions, manual confirmation for destructive operations and local form validation; refresh after server ack.
- Implement **browser-direct R2 PUT** using API-018 signed intent metadata from same-origin WordPress WOO-014. Hash/validate CSV/XLSX file, bounded size/MIME, preserve required signed headers (`Content-Type`, `If-None-Match`, `x-amz-meta-sha256`), upload bytes to only the approved HTTPS R2 S3 endpoint without credentials, then call authenticated WordPress finalise. Handle preflight denial, aborted/expired uploads, 412, redirects and stale disconnect/credential rotation without phantom success or exposing old-session results.
- Preserve Shopify-style vertically stacked Add web page and Upload file disclosures, each with the approved responsive field grid, status/capacity display, source edit/reorder presentation and existing native 20-language admin locale; no duplicate Recovery Settings sections. Do not reintroduce the obsolete side-by-side web/file layout.
- On a connected, authorised merchant read, replace W004's unavailable fallback with the real source count, plan capacity, catalogue-defined purposes/formats, feature activation state and source records; do not use example values or hardcoded Shopify fixture records.

## Out of Scope

- New hosted service APIs, background business processing, Shopify UI changes and new database models.
- Enabling knowledge tools outside existing plan/provider eligibility or overriding feature preference server policy.

## Requirements

- Preserve existing tenant, credential, platform, entitlement and transaction boundaries; use the source-inspected contracts and Shared package where applicable, not independently guessed interfaces.
- Fail closed on missing or malformed configuration, unauthorised operations and external provider failures. W015 is browser-side WordPress JavaScript and must not import `@modainteract/moda-interact-shared/logging` or introduce a competing generic logger. Display bounded, localised user-facing errors; optional PHP diagnostics belong to WOO-014, and hosted Node.js structured logging belongs to the API owners.
- Keep production components modular and independently testable; no monolithic files or cross-repository implementation changes. Preserve Shopify runtime and existing Woo merchant Billing, recovery and navigation behaviour.
- If implementation discovers a genuine missing Background/Shared/Gateway capability, stop and return the precise evidence to `moda_architect` rather than extending another repository's scope.

## Work Items

- [ ] Wire production `feature-preferences-client.js` to WOO-014; reconcile W003 controller body `preferences` to API-014 `changes` and stale CAS handling while showing effective vs optional feature state.
- [ ] Wire W004 knowledge client/controller to live read/add/edit/delete/refresh/reorder/upload/replace/reprocess; ensure configured sources remain accessible while merchant feature is off.
- [ ] Maintain source list statuses and cap counts from authoritative data, no fake success, dedupe actions, manual confirmation for destructive operations and local form validation; refresh after server ack.
- [ ] Implement same-origin metadata intent/finalise plus **browser-to-R2 binary PUT** using exact required headers, size/hash limits, progress/cancel/timeout, no credentials/redirects, idempotency and stale installation protection; do not route bytes through WordPress PHP.
- [ ] Match the vertically stacked Shopify web-page and file-upload disclosures, responsive field grid, status/capacity, source edit/reorder presentation and existing native 20-language admin locale; no duplicate Recovery Settings sections.
- [ ] Verify the production UI transitions from W004's disabled, unavailable section to an authorised, live Merchant Knowledge configuration view using server-provided sources, catalogue, permissions, capacity and feature state.
- [ ] Add focused positive and negative coverage and complete the required validation/Completion Report.

## Interfaces / Contracts

- Consume WOO-014 WordPress responses based on API-014..017 OpenAPI and API-018 browser PUT contract. Read `effectiveEnabled` separately from plan entitlement and `merchantEnabled`. Signed R2 URL is ephemeral, not persisted or logged; only PUT file bytes and approved signed headers to the R2 endpoint, no Moda/WordPress credentials.
- Keep source language independent of WordPress admin locale, and use generated WordPress i18n assets.

## Dependencies

- `ARCH-035-WOOCOMMERCE-003` (must be Complete and architect accepted)
- `ARCH-035-WOOCOMMERCE-004` (must be Complete and architect accepted)
- `ARCH-035-WOOCOMMERCE-014` (must be Complete and architect accepted)
- `ARCH-035-GATEWAY-001` (must be Complete and architect accepted for direct browser upload readiness)

## Enables

- `ARCH-035-SYSTEM-TEST-004`

## Acceptance Criteria

- [ ] Feature toggle can be read/changed and persisted for eligible optional features; required features are non-editable and conflicts return actionable feedback.
- [ ] An entitled merchant can configure sources when feature off; toggle-off does not erase sources and no pending/active result is spoofed. Ingestion/retrieval eligibility is distinct from the right to configure sources.
- [ ] For a connected, authorised Woo merchant the Merchant Knowledge accordion shows the server-provided configured-source count, capacity, catalogue, vertically stacked Add web page / Upload file forms and source list instead of an integration-unavailable message; never fabricate data or permissions. The 2026-10-20 developer-owned LocalWP live-source checkpoint is documented below and must not be repeated during architect review; acceptance of the complete implementation still requires source/automated validation.
- [ ] Web source, CSV/XLSX browser-direct upload, edit, refresh/reprocess, reorder, delete and processing state are reflected by actual API state; errors preserve drafts. Failed R2/preflight/expired/no-finalise cannot show success.
- [ ] Automated desktop/narrow component/DOM-layout and interaction assertions reflect the Shopify reference; WordPress two-stage navigation, category and recovery settings remain intact; all 20 locales pass. Live LocalWP visual confirmation is a separate developer-owned checkpoint, not an agent acceptance criterion. The developer-owned 2026-10-20 Recovery Settings coupon smoke check is documented below and must not be repeated by the architect/reviewer.
- [ ] No `_index.md` files or unrelated domains modified; canonical dual-worktree/branch validation evidence recorded in real development workspace.

## Validation

- [ ] Focused React controller/component tests with real client contract fixtures, 401/403/409/503, disabled feature, disconnect, stale responses and duplicate click cases. Cover the transition from disabled unavailable shell to connected authoritative counts/catalogue/sources; separately cover feature-off-but-configurable, denied access and narrow-screen stacked disclosures. Browser direct upload tests cover signed headers, URL host, CORS/network failure, TTL, 412, abort, no redirected requests and no PHP binary transport.
- [ ] `npm run test:js`, `npm run test:i18n`, `npm run i18n:verify:20`, PHP facade tests if relevant, lint, build, plugin ZIP, automated responsive/browser fixtures where supported, `git diff --check`. Do not launch or operate LocalWP in agent validation; review both completed 2026-10-20 developer LocalWP checkpoints (coupon smoke and Merchant Knowledge) instead of repeating them. W015-specific automated validations remain required.
- [ ] Record concrete commands and results, implementation and parent task branch/commit evidence, canonical physical-isolation/synchronisation evidence, plus deviations and unresolved issues.

## Stop Condition

When this bounded task's Work Items, Acceptance Criteria and required Validation are satisfied, update Completion Report, set `status: review`, return to `moda_architect` and STOP. Do not start tasks listed under Enables.

## Implementation Notes

### Reconciled WooCommerce-structure handoff (2026-10-16 22:56 snapshot)

- This snapshot shows `WOOCOMMERCE-003` as `complete` with `src/recovery-settings/feature-preferences-{client,controller,panel}.js`, but `WOOCOMMERCE-004` as `ready`, and **no** `src/recovery-settings/merchant-knowledge/` files in the included Woo checkout. The previous W004 patch delivery is not proof that this revision is merged. Do not claim WOO-015 Ready until W004 is formally Complete **and** its accepted source is present in the launcher's implementation baseline; if absent, reconcile the source/gitlink rather than rebuilding W004 as part of WOO-015.
- After W004 is present, wire the existing `src/recovery-settings/feature-preferences-client.js` and W004's knowledge client/controller through the `includes/Rest/` and `includes/Api/` contracts completed by WOO-014. Preserve `src/recovery-settings/recovery-settings-screen.js` composition and existing `src/page/connected-workspace.js` connection-identity reset; do not implement hosted database/R2 business rules in React.
- The W003 controller currently submits `{expectedRevision, preferences:[{featureId,enabled}]}`, whereas API-014 defines `{expectedRevision, changes:[{featureId,enabled}]}`. Adapt the client contract without changing entitlement meaning. Extend the strict read parser for `schemaVersion`, `required` and `planEligible` (and bounded source DTO validation) without silently trusting missing/unknown fields.
- Keep configuration available for entitled shops even if the Merchant Knowledge feature is off, while clearly identifying current retrieval/processing eligibility. Preserve manual actions, stale read suppression, cancel/draft state and 20 native WordPress locales. Agent validation uses authenticated WordPress/API test fixtures and automated desktop/narrow/feature-off/feature-on assertions. **Only the developer** launches LocalWP, exercises authenticated live sessions and captures comparative screenshots. Treat that manual check as a separate checkpoint; do not block agent `review`/architect acceptance on LocalWP access or claim that the agent performed it.

The historical superseded ARCH-035-API-003/004/005 must **not** be revived; this task follows the newly agreed architecture amendment and consumes only approved contract owners. An unimplemented API or feature must never be represented as operational. Do not update any `docs/decisions/**/_index.md` until the developer closes the architectural session.

Logging/runtime boundary: W015 connects React components to authenticated same-origin WordPress REST responses. It must not bundle or call the Node-only `@modainteract/moda-interact-shared/logging` package or add a separate browser logging transport. Preserve existing UI error-handling and display safe, actionable, localised messages. Never log installation credentials, authorisation headers, signed upload URLs, uploaded file contents or customer data. WordPress/PHP diagnostics are owned by WOO-014; hosted API structured logging belongs to the API owners.


### 17 October 2026 browser-direct upload handoff

- W015 obtains metadata-only upload intent from W014; verify selected file bounds and calculate SHA-256 in the browser, then perform the R2 presigned `PUT` using exactly the returned headers and file bytes. Do not attach WordPress cookies, nonces, installation credentials, additional arbitrary headers or upload URL query strings to telemetry.
- Fail closed on R2 origin/presigned host/redirect mismatch, CORS preflight error, request timeout, cancellation, expiry, bad checksum, non-2xx/412. Do not show uploaded/succeeded or trigger finalise until the R2 `PUT` returns success; finalise's authoritative API response controls the resulting source state.
- Gateway-001 policy approval and registered actual Woo admin Origin are rollout gates. Do not create fallback binary proxy through WordPress PHP. If a provider-signing/CORS/WordPress boundary is missing, return it to `moda_architect`, not to another repository's source.

### 18 October 2026 LocalWP visual evidence (developer checkpoint; not agent validation)

- Shopify reference screenshot: Merchant Knowledge shows nested accordion, capacity summary and two vertically stacked source forms.
- WooCommerce LocalWP screenshot: Merchant Knowledge accordion is visible but its body shows only an unavailable message and Retry button; no live catalogue or configured-source read is demonstrated.
- W004 must preserve a disabled but complete section layout when unavailable; **W015** must replace that fallback with authoritative server data/actions when the merchant connection is authorised. These screenshots do **not** establish successful live upload or source management. The separate Store category versus Shopify Store profile layout difference is not part of W015.

### 20 October 2026 — completed developer LocalWP regression checkpoint (do not repeat during review)

- **Execution ownership:** The developer performed authenticated, live LocalWP/WordPress browser testing through the `editorial-floors-gnu-massachusetts.trycloudflare.com` HTTPS tunnel. Evidence supplied on 2026-10-20 consists of Recovery Settings screenshots, Chrome DevTools Network/Timing/Headers screenshots, Render recovery-worker logs and read-only PostgreSQL results. This is **developer-executed evidence**, not an architect- or repository-agent-executed test.
- **Observed PASS — Recovery Settings / coupon smoke:** The connected WordPress admin rendered Recovery Settings; the catalogue became `CURRENT` after the Render `test` recovery worker loaded `woo.couponSync` and ran the automatic dispatcher; five selectable coupons appeared; selecting coupons and saving produced `Recovery behaviour saved.` The browser request to `/wp-json/moda-interact/v1/merchant/discount-offers?_locale=user` used `POST` at the HTTP boundary and returned **200 OK**. A measured request took approximately **6.00 seconds**, of which **5.99 seconds** was waiting for the server response; successful saving is confirmed, but the latency merits separate investigation and is not asserted to be resolved.
- **Reviewer instruction — no LocalWP replay:** Treat the above as the completed **developer-owned LocalWP coupon/recovery-settings regression checkpoint**. The architect/reviewer **must not launch LocalWP, repeat the same manual coupon interactions, or require the developer to repeat them solely for review**. Review the documented observations and supplied evidence, source changes, repository-test results and acceptance criteria. Request a specific missing artefact or explanation if the evidence is insufficient; do not substitute an unrequested LocalWP rerun.
- **Scope limit:** The demonstrated coupon selection/save path belongs to the broader WooCommerce recovery-offer integration and is **not evidence that W015's live Conversation Feature controls, Merchant Knowledge read/add/edit/delete/refresh/reorder, CSV/XLSX browser-to-R2 upload/finalise, failed-upload behaviour, CORS gate or 20-locale tests passed**. Those W015-specific Work Items, Acceptance Criteria, automated Validation and implementation/branch Completion Report must be reviewed separately. Do not mark unchecked items complete or change `status` or `Architect Review` merely because this checkpoint passed.


### 20 October 2026 — completed developer LocalWP Merchant Knowledge checkpoint (do not repeat during review)

- **Execution and tenant identity:** The developer performed authenticated LocalWP/WordPress Admin testing through `https://editorial-floors-gnu-massachusetts.trycloudflare.com` for WooCommerce shop `cmvgaeepw0000pokbgpkbnkgc`. Evidence provided in this architecture session: four Merchant Knowledge/R2 screenshots, followed by Moda hosted API structured-log excerpts on 2026-10-20. The screenshot and log observations below are developer-supplied manual evidence, **not** an automated test run or independently captured architect session.
- **Observed PASS — connected live sources/capacity:** Recovery Settings rendered the Store & assistant context → Merchant Knowledge accordion, source count/capacity, vertically stacked Add web page and Upload file disclosures, source status labels and actionable controls. The counts observed were **5/10**, then **6/10**, then **7/10**; existing CSV, XLSX and web sources showed real names, formats, content-unit counts and `Ready` states. This establishes the live source-list/display checkpoint for this store, not every management action or feature-off entitlement case.
- **Observed PASS — web-page ingestion:** Adding a named web source for `https://www.justwinnys.com/` resulted in a new `Processing` card, followed by `Ready`, with **1,969 active content units** displayed and the 7/10 configured-source count. The screenshot sequence demonstrates an externally processed web-page source reaching a ready state.
- **Observed PASS — R2 object presence:** The Cloudflare R2 bucket view showed CSV and XLSX objects within `moda-interact/merchant-knowledge/development/woocommerce/cmvgaeepw0000pokbgpkbnkgc/editorial-floors-gnu-massachusetts.trycloudflare.com/`. This confirms objects exist under the shop/environment-specific storage prefix. It does **not alone** prove which browser/network request wrote each object, the exact signed headers, allowed/denied CORS preflight or the absence of a PHP binary fallback.
- **Corroborating hosted API logs (UTC, `development`):** For the **same shop ID**, `merchant.knowledge.upload` logged `operation: intent` at `14:15:54.941Z` and `operation: finalize` at `14:16:04.053Z`; `api.platform_configuration.read` reported `merchant.knowledge.r2` `require_r2_configuration: success` at `14:15:57.242Z` and `read_upload_policy: success` at `14:16:05.497Z`; `merchant.knowledge.read` at `14:16:10.337Z` returned `state: ENABLED`, `returnedSourceCount: 8`, `durationMs: 5485`. The latter read is later than the 7/10 screenshot and must not be described as that screenshot's source count. The log events demonstrate that the live hosted intent/finalisation/read paths were invoked and configuration could be read; the excerpts do **not** independently establish the browser's R2 `PUT` HTTP status, finalisation response status or signed-request security guarantees. The **5,485 ms** read duration is an observed API performance measurement, not a W015 correctness failure or a resolved latency issue.
- **Reviewer instruction — no LocalWP replay:** Treat the successful connected-source, web-source ingestion, source-list and R2 object-presence interactions above as a **completed developer-owned LocalWP checkpoint**. Do **not** launch LocalWP, request repetition of these interactions or require the developer to recreate these screenshots solely for architect review. The reviewer should inspect the source, supplied logs/screenshots, focused test results, metadata-only WordPress boundary and remaining acceptance criteria; request narrowly scoped missing evidence when a particular criterion cannot be established. Do not infer security acceptance from a successful upload.
- **Unverified by these manual artifacts:** Browser Network evidence for the actual R2 `PUT` (approved HTTPS host, exact signed headers, no WordPress credentials, successful response) and matching finalise HTTP response; negative preflight/redirect/expiry/412/abort/security tests; feature-toggle persistence and feature-off configuration; actual edit, delete, reorder, refresh/reprocess and file replace operations; all 20 locale, desktop/narrow automated checks; canonical implementation branch and Completion Report evidence. The snapshot task `ARCH-035-GATEWAY-001` remains `pending`, so its rollout-policy acceptance must be reconciled separately even if an observed R2 path worked. **Do not mark W015 complete, mark unchecked validation PASS, or change architect review state on this checkpoint alone.**

## Completion Report

### Status

In Progress — developer takeover and Attempt 1 claim recorded on 2026-10-19. Implementation work is now assigned to the developer in the canonical implementation worktree.

### Files Changed

No implementation files changed yet. The implementation worktree is prepared at `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-WOOCOMMERCE-015` on `task/ARCH-035-WOOCOMMERCE-015`.

### Work Completed

Canonical task preparation completed. The developer owns the implementation attempt and must update this report with actual implementation and validation evidence before requesting review.

### Validation Results

Not run; implementation has not begun.

### Deviations

None.

### Assumptions

The uploaded ZIP represents a portable design baseline, not the developer's current on-disk branches. Confirm source, task status and dependency state with the launcher before execution.

### Unresolved Issues

None.

### Architectural Concerns

Report any cross-repository contract, R2 identity, reconciliation or security mismatch to `moda_architect`.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting implementation and validation evidence.

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending.

### Follow-up

Developer completion is explicit because `completion_mode: developer`; after implementation and review, use `/moda_developer_update ARCH-035-WOOCOMMERCE-015` and then the explicit `complete` action.

## Developer Execution Ownership Amendment

On 2026-10-19, the developer invoked `/moda_developer_create ARCH-035-WOOCOMMERCE-015`, explicitly taking over this ready agent-owned task. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_woocommerce`, repository ownership, scope, dependencies, acceptance criteria and validation requirements are unchanged.

## Developer Claim — Attempt 1

**Claimed — 2026-10-19T02:28:24Z.** The task transitioned from `ready`, Attempt 0, null executor to `in_progress`, Attempt 1, `executor: developer`.

- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-WOOCOMMERCE-015`, branch `task/ARCH-035-WOOCOMMERCE-015`, created from refreshed `origin/main` at `9392e960f9fffab51337222c8c679975c033a9ee`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-WOOCOMMERCE-015`, branch `task/ARCH-035-WOOCOMMERCE-015`, created from the WooCommerce repository's refreshed `origin/main` at `afe307401664efdc11efe833e0da841013116e74`.
- Both task branches were absent remotely before preparation, are now attached to their canonical physical worktrees, and were created without modifying `main`. Both worktrees were clean at claim time.
- Canonical dependency readiness was confirmed before claim; the launcher reported this task `ready` and all explicit dependencies were complete.
- Required validation remains to be run during implementation: focused JavaScript/controller/component and browser-direct upload tests, `npm run test:js`, i18n verification, lint/build/package checks, responsive/browser fixtures where supported, and `git diff --check`. LocalWP authenticated visual validation is a separate developer checkpoint and is not part of agent validation.
