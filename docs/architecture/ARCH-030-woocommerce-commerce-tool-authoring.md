---
id: ARCH-030
title: WooCommerce REST tool Test and Review in CommerceAgent Studio
status: in_progress
coordinator: moda_architect
created: 2026-10-14
updated: 2026-10-16
---

# ARCH-030: WooCommerce REST tool Test and Review in CommerceAgent Studio

## Status

In Progress. The COMMERCE-001 task is materialised and its Attempt 1 remains Ready for correction following developer review; no implementation has been accepted.

## Problem

CommerceAgent Studio already lets a user configure a WooCommerce `GET` operation (Request), select response fields (Response), and edit the Result Template. Its WooCommerce-specific Test and Review components are placeholders, Test -> Review navigation is disabled, and WooCommerce provider drafts do not yet become persistable tool definitions. The desired outcome is to finish these **two steps only**, for the selected WooCommerce store.

## Goals

- Test **every WooCommerce GET operation already offered by** `src/commerce/woocommerce/read-operation-catalogue.ts`, using the selected store and its legitimate existing WooCommerce connection and authorization.
- Keep store-specific permissions as an execution-time outcome. Do not remove an operation from the authoring selector merely because a particular store rejects it; show permission-denied/unauthorized responses to the user without disconnecting the store.
- Supply examples for `AGENT_INPUT` parameters, combine them with configured `FIXED` values, validate them and show the resolved safe request summary, bounded response, mapped output and rendered template.
- Require a successful current-draft/current-store test before unlocking Review; invalidate stale results after relevant edits, store changes or overlapping responses.
- Show a complete, accurate WooCommerce Review summary and save a valid WooCommerce tool as a draft using Commerce's established authoring workflow, with one-shot protection and visible errors.
- Retain current staff Studio access while enforcing shop authorization server-side in a way that does not rely on the browser being trusted; merchant Studio rollout is separate.

## Non-Goals

- New `moda-interact-api`, `moda-interact-shared`, `moda-interact-gateway`, `moda-interact-database`, WordPress plugin, or other repository tasks.
- Reauthoring the existing WooCommerce Request, Response or Result Template steps, except minimal wiring strictly needed for Test/Review.
- Arbitrary host/URL execution, arbitrary HTTP methods, WooCommerce write operations, generic external-HTTP tools, Shopify tools or a cross-provider test framework.
- Production Woo tool execution, tool publication, Background/MCP support, merchant-facing Studio access or new credential onboarding.

## Current Architecture

- `moda-interact-commerce/src/studio/tools/authoring/test/woocommerce-rest-test.tsx`: placeholder.
- `moda-interact-commerce/src/studio/tools/authoring/review/woocommerce-rest-review-summary.tsx`: placeholder.
- `moda-interact-commerce/src/studio/tools/new-tool-editor.tsx`: Woo Test's Next is disabled; the Woo branch does not enter the normal definition-backed Review flow.
- `moda-interact-commerce/src/studio/tools/new-tool-authoring-state.ts`: Woo request, response and template drafts, revision-based Test state, but no persistable Woo provider definition.
- `moda-interact-commerce/src/commerce/tool-definition/contracts.ts`: no Woo execution discriminant in the persisted definition schema.
- `moda-interact-commerce/src/commerce/woocommerce/read-operation-catalogue.ts`: the existing store-specific read-operation source of truth.

## Proposed Architecture

```text
Selected, authorised WooCommerce store + Woo tool draft
    -> Woo Test (example inputs + FIXED parameters)
    -> Commerce-owned, server-side validation and approved store-specific GET request
    -> WooCommerce store REST endpoint (not a new Moda API product endpoint)
    -> bounded sanitised result OR explicit Woo permission/connection failure
    -> response mapping + result-template preview
    -> current Shop/draft Test gate -> Review -> Save Commerce draft
```

**Approved implementation boundary (14 October 2026):** Both tasks belong to `moda-interact-commerce` (`moda_commerce`). The developer explicitly approved a **Commerce-local, server-only, WooCommerce GET test executor**, using `shopId` to locate the **existing** WooCommerce installation and active REST-read grant and **ARCH-039's canonical `COMMERCE_CONNECTION_KEYS_JSON` plus published Shared credential decryption/AAD helpers** to read the grant. This is the same canonical keyring/envelope convention used by API-002 and Background; the earlier `MODA_WOO_REST_READ_KEYRING` name is superseded. Commerce must not create its own grant store, credential lifecycle, installation authorization or new encryption scheme. The store itself supplies operation-specific success/denial. The execution boundary is **not** a Commerce-to-API call, a new hosted API endpoint or a gateway/Shared contract. The permitted provider request is only a catalogued GET against the installation's canonical site, using a bounded SSRF-safe transport (DNS/IP checks, pinned peer address, TLS validation, no redirects, response limits and timeout). Every execution independently authorizes the principal and shop, checks the active REST-read scope and rechecks the grant after I/O. Credentials remain server-only, never reach browser previews or logs, and the test does not mutate WooCommerce. An absent/invalid approved grant or inability to enforce these safeguards must fail closed. A passing mock is not live-store evidence.

## Repository Responsibilities

| Task | Owner | Outcome |
|---|---|---|
| ARCH-030-COMMERCE-001 | moda_commerce | WooCommerce Test, store-specific execution/preview and current-test navigation gate |
| ARCH-030-COMMERCE-002 | moda_commerce | WooCommerce Review summary and Save draft in Commerce |

No other tasks are part of this agreed scope.

## Data and Contracts

- The existing WooCommerce operation catalogue and Request/Response/Result Template drafts remain Commerce-owned.
- A test uses only the chosen catalogued `GET` operation, validated path/query values and a server-authorized store. Do not accept arbitrary destinations or credential/header overrides from the browser.
- Test results remain ephemeral, do not persist provider payloads as tool definitions, and must be bound to store identity and all relevant authoring revisions. A successful test supplies server-verifiable, expiring proof bound to the authorised store, canonical draft, validated example inputs and resolved effective GET path; browser-only status is not trusted proof. COMMERCE-002 must carry the ephemeral tested examples into its server-side Save verification so it can recompute the same request/fingerprint; examples and provider payloads must not become persisted tool-definition data.
- Review/Save must build a valid Commerce-local Woo tool draft from its existing authoring fields, extend only Commerce-owned validation/persistence where necessary, and not claim published runtime executability.
- Permission, missing connection, not found, timeout and malformed response are distinct user-visible outcomes; a provider `401`/`403` alone must not silently disconnect a store.

## Failure Handling, Security and Observability

- Server authorization checks are mandatory and must be independently re-evaluated for every test and save. Future merchant access must not allow a merchant to test another store.
- Bound time, response size, page sizes, preview size and concurrent requests. Apply field/path-aware PII and sensitive-setting redaction **even when an author selects the sensitive field**, and render any displayed Result Template preview from preview-safe projected values. Preserve useful non-sensitive selected values. Never expose API keys, auth headers, secrets or complete sensitive customer responses in UI/logs or signed test proof.
- Retry is user-triggered, duplicate-click safe and does not manufacture a passing result on failure. Older in-flight results cannot overwrite the newer Shop/draft.
- Use existing shared structured logging for any new runtime log events, with bounded metadata and no sensitive request/response bodies. Do not add duplicate generic HTTP telemetry.

## Rollout and Dependencies

Classification: pre-production for WooCommerce Studio tool authoring. Existing merchant store/grant data is preserved. COMMERCE-001 has no new cross-repository task dependency and is Ready as a portable definition; COMMERCE-002 depends on its architect-accepted completion. Save is draft-only unless existing Commerce validation authorizes more. Neither task may begin a follow-on feature after completion. Integrated system tests can be considered separately after both tasks and manual testing.

## Decisions / Tasks

| Task | Status (definition only) | Depends on |
|---|---|---|
| ARCH-030-COMMERCE-001 | ready | None |
| ARCH-030-COMMERCE-002 | pending | ARCH-030-COMMERCE-001 |

## Open Questions

- The approved Commerce-local credential consumption/GET transport boundary is limited to Studio testing. If security checks cannot be demonstrated, fail closed and escalate instead of delegating arbitrary provider requests to a new service.
- A production merchant-approved WooCommerce store is still needed for live integration evidence; mock transports do not satisfy this evidence.
- Production execution of saved Woo tools and future merchant Studio access remain intentionally out of scope.

## Change History

- 2026-10-14: Defined exactly two Commerce-owned tasks: WooCommerce Test and WooCommerce Review/Save. Supersedes the previous ARCH-030 task-definition proposals including Shared, API and Gateway tasks.
- 2026-10-14: Recorded developer approval for Commerce-local server-only decryption of existing WooCommerce read grants and secure GET transport; the earlier speculative API/Gateway requirement is expressly superseded. No new credential ownership or grant lifecycle was authorized.

- 2026-10-16: Reconciled the previously approved Commerce-local transport with ARCH-039's later canonical keyring and Shared credential API. Only the obsolete environment-variable/keyring mechanism is superseded; the two-task ARCH-030 boundary, Commerce-local GET test execution and COMMERCE-002 implementation are unchanged. Clarified that selected sensitive customer fields and Woo settings must be redacted in all displayed previews and rendered template output.
