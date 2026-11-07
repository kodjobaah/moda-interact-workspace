# Commerce Studio Render test investigation

Updated: 7 November 2026. Environment: Render test.

Track the remaining Commerce Studio issues and resolve them one at a time. Start with Shopify token refresh: product search worked after opening the Shopify app, but a later expired-token refresh failed again. Authentication must remain usable without repeated manual sign-in before product-search behaviour can be assessed reliably.

This is an investigation record, not an architecture task specification. Proposed fixes require evidence before implementation. Do not mark an issue resolved solely because a deployment or unit test passed; record the corresponding Render test outcome.

## Investigation order

| ID | Issue | Status | Completion criterion |
| --- | --- | --- | --- |
| CS01 | Shopify offline token refresh | Configuration corrected; expiry verification pending | Refresh after access-token expiry succeeds without manual login and the resulting token permits a product read. |
| CS02 | Required referral after failed tools | Open | A definitive failed tool produces a valid store-referral response instead of a failed conversation. |
| CS03 | Repeated product searches and empty results | Open | Search results are explained by provider data and filters, and the agent reaches a grounded answer within an agreed bounded number of calls. |
| CS04 | Merchant Knowledge denied | Open | The precise authorization decision is understood; authorized preview calls work and unauthorized calls remain denied. |
| CS05 | Unsupported Shopify brand integration | Open | App configuration can be released and brand acquisition uses a verified supported source with an explicit fallback. |

## Working method

1. Select one issue and record its reproduction, deployment commit, environment, conversation ID and run ID.
2. Trace the relevant caller, Shared library and provider boundary. Establish the cause before selecting a fix.
3. Make the smallest justified change. Keep authentication, tenant isolation and response validation intact.
4. Run focused tests and required type/lint checks; deploy to Render test.
5. Repeat the reproduction and record the result below. Only then close the issue and move to the next one.

Do not put tokens, secrets, raw OAuth responses or full customer/provider payloads in this document or logs. Compare credential identities using safe metadata or equality checks without exposing values.

## CS01 Shopify offline token refresh

### Confirmed evidence

- Earlier diagnostics returned HTTP 400, `invalid_request`, classified as `INVALID_CLIENT_CREDENTIALS`, with OAuth configuration source `DATABASE`, revision 2.
- Those diagnostics reported an expired access token and a refresh token whose stored expiry timestamp had not elapsed. That timestamp does not establish that Shopify still accepts the refresh token.
- Product-search calls subsequently succeeded after the merchant opened the Shopify app. This establishes usable access at that time, not that automatic refresh was fixed.
- At 15:40:59, refresh failed again with `REFRESH_REJECTED`. Search stopped before any catalogue request: `providerRequests: 0`, `providerItems: 0`.
- The latest excerpt does not contain the classified HTTP response for that exact refresh attempt. Do not assume its provider reason is identical to the earlier rejection.
- Definitive refresh rejections now reach the product adapter as `retryable: false`. This prevents automatic retries, but does not prevent a later model step requesting the tool again.

### Questions to resolve

- Do the Shopify app, Commerce, MCP and Background resolve credentials for the same app installation and environment?
- Does database revision 2 contain a matching client ID and secret, and is that the app that issued the stored offline session?
- Does Shared send the expected endpoint, grant type, form fields and current refresh token?
- Are refreshed credentials and expiry values persisted atomically, and do all consumers use the current session?
- Does a concurrent refresh wait for the persisted result rather than reuse an obsolete rotating refresh token?

### Touch points

- Shopify app: `moda-interact/app/shopify.server.js`, selected `shopify.app.moda-interact.toml`, OAuth/session persistence and the platform configuration reader.
- Commerce: `src/platform-configuration/shopify-oauth.ts`, `src/commerce/preview/shopify-refresh-diagnostics.ts`, `src/commerce/preview/local-provider-composition.ts`, and `src/commerce/preview/product-reads/registrations.ts`.
- Shared: offline-token provider implementation, expiry decision, refresh HTTP request, locking and session update. Locate the exact implementation and installed package versions at investigation time.
- MCP and Background: callers of the same provider and their credential readers; verify adoption rather than assuming identical behaviour.
- Database: sealed Shopify OAuth configuration and the shop's offline session metadata. Inspect no secret values in reports.

### Verification

Test a valid unexpired token, an expired access token with a usable refresh token, concurrent refresh attempts, and a definitive provider rejection. On Render test, prove an expired token refreshes without opening Shopify manually, then perform an authorized product read. Record whether the successful provider path was Commerce local preview or MCP; validate the other consumers separately.

## CS02 Required referral after a failed tool

### Confirmed evidence

Run `c53172b1-8980-49f3-a70a-fe271bd00a99`, conversation `98418428-c96d-4461-b534-c96681a8d265`, failed at 15:41:06 with:

- Code: `INVALID_FINAL`.
- Stage: `final.validate`.
- Reason: `FINAL_REFERRAL_REQUIRED`.
- Product search had returned `UNAVAILABLE`, nonretryable, after a refresh rejection.

Shared requires `answerKind: REFER_TO_STORE` after the relevant failed or denied tool. The final response did not satisfy that condition. The returned answer kind and why the model selected it are not established by the supplied excerpt.

### Investigation and touch points

Inspect Shared `src/commerce/runner/final-response.ts`, the state that sets `requiredReferral`, final-response schema and trusted instructions. Inspect the Commerce model bridge and how failed tool results reach the next model invocation. Log only the required and returned answer kinds and bounded identifiers; no reasoning text or full response bodies.

Determine whether instructions are missing, conflicting or ignored before choosing between instruction changes and bounded response recovery. Do not remove the referral validator merely to make the run pass. Verify both structured and natural-text finalization, and check Background's use of the same runner.

### Verification

A failed or denied tool must lead to an honest, valid referral. A successful empty search must remain distinguishable from an unavailable search. No product availability claim may be fabricated from a failed read.

## CS03 Repeated searches and product results

### Confirmed evidence

- A run starting at 13:10:17 completed using seven model steps and seven tool calls in approximately 34.5 seconds.
- A follow-up run starting at 13:11:57 made eight successful product-search calls, then failed when another tool call exceeded the configured allowance.
- Tool status `OK` proves contract-level success, not that any products were returned.
- New `commerce.preview.product.search.summary` events report provider rows, candidates, normalization/filter rejection counts, returned products, pagination, filters and a search fingerprint. Query text and full payloads are omitted.
- The 15:40 search summary records an authentication failure before catalogue access; it cannot explain the earlier successful empty results.

### Investigation and touch points

After CS01 is stable, compare search summaries by conversation and fingerprint. Distinguish zero provider rows, rejected normalization, availability/price/category filtering, and unconsumed pages. Use controlled test queries when exact query inspection is needed; do not introduce unrestricted query logging.

Inspect Commerce `src/commerce/preview/product-reads/shopify-core.ts`, `registrations.ts`, system product-tool definitions/result templates and model instructions. Compare MCP's equivalent adapter for any confirmed semantic defect. Count lower-level provider pagination separately from runner tool calls.

### Verification

Use known available, unavailable and absent products, a catalogue browse, category filters and pagination. Confirm the agent sees the normalized results, avoids repeating an unchanged completed search and gives a supported answer within a measured budget. Increasing limits alone is not closure.

## CS04 Merchant Knowledge denied

### Confirmed evidence

`merchant_knowledge_lookup` returned `DENIED`, nonretryable, in the 12:55 test conversation. The exact authorization reason has not been established. Selecting a Feature in Studio alone is not proof that every underlying authorization requirement is met.

### Investigation and touch points

Trace the selected Feature/capability binding, preview grant and manifest, local definition executor, Merchant Knowledge authorization checks and the selected shop's knowledge-source state. Compare the published MCP execution path. Distinguish permission denial from missing or unready knowledge data; preserve explicit authorization checks.

### Verification

An authorized, correctly configured shop can query its own ready knowledge source. Another shop, revoked grants and unauthorized capabilities remain denied. Missing knowledge is reported according to its contract rather than mislabeled as a permissions failure.

## CS05 Shopify brand integration

### Confirmed evidence

Both local preview and app-version creation were rejected by Shopify with `app_access` scope validation naming `read_brand`. The named Moda configuration was selected in the verbose capture, so selecting that configuration did not resolve the error.

The existing brand-permission implementation relied on Admin `BrandingBrand`/`shop.brand`. Documentation consulted during this investigation exposed that resource on the unstable surface, while the configured stable `2026-07` Shop reference did not expose `brand`. Treat a supported replacement as an investigation, not an already selected solution.

References checked on 7 November 2026:

- [Stable Shop reference](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/Shop).
- [Latest BrandingBrand reference](https://shopify.dev/docs/api/admin-graphql/latest/objects/BrandingBrand).
- [Unstable BrandingBrand reference](https://shopify.dev/docs/api/admin-graphql/unstable/objects/BrandingBrand).

### Investigation and touch points

Review both app TOML configurations, runtime `SCOPES`, the brand-scope gate under `moda-interact/app/services/shopify-brand/`, the ARCH-049 brand contract, Background brand acquisition and downstream template preparation. Verify current files before editing; no scope-removal implementation was completed as part of this investigation record.

Choose a supported acquisition mechanism only after validating its schema, permissions and availability for the deployed version. Define how existing stored brand data, missing logos and unavailable refreshes are handled. Removing a requested scope alone does not repair brand retrieval. Keep this separate from the WhatsApp R2 image-storage work and from CS01 OAuth credential rejection.

### Verification

Shopify accepts the intended app configuration; required brand fields come from a supported authenticated source or the defined fallback. Missing permissions or data do not produce blind retries or false success.

## Budget configuration and diagnostic baseline

The Studio test that progressed furthest used 8 model steps, 8 remote calls, 2,000 output tokens per model invocation and a 60-second turn deadline. These are investigation settings, not approved production defaults or a monetary cap.

- Temporary overrides: Studio Test Conversations, Custom test policy. They apply to a newly started conversation and are not saved as defaults.
- Preview ceiling: Admin, System Controls, Platform Configuration, Commerce Studio preview, TEST deployment. `commerce.preview` bounds the allowed deadline and output tokens.
- Saved Studio Preview policy and shop overrides are separate from that Admin ceiling.
- Background has separate caller-owned budgets; changing Studio does not change Background.
- DeepSeek previously consumed all 800 output tokens as reasoning and returned no usable answer, producing `MODEL_CALL_ROUTE_INVALID`. Increasing to 2,000 allowed a later run to complete; it does not establish optimal cost or reliability.

### Completed diagnostic changes

| Repository | Commit | Change |
| --- | --- | --- |
| Commerce | `07a9abd` | Bounded refresh-response classification and preservation of nonretryable failures. |
| MCP | `a8d54a8` | Preservation of nonretryable credential failures in the product adapter. |
| Commerce | `89e05c0` | Bounded search summaries with counts, filters and fingerprints. |
| Commerce | `4c909b5` | Specific failure reason, stage, tool and run ID retained for Studio; schema issue metadata retained in correlation logs. |

A pushed commit is not deployment proof. For each reproduction, record the actual Render deployment commit.

## Resolution record

Append one entry per completed investigation:

- Issue ID and date:
- Confirmed cause:
- Affected repositories and touch points:
- Fix commits and deployment commits:
- Focused checks:
- Render test reproduction and observed outcome:
- Remaining limitations or follow-up:

### CS01 configuration correction on 7 November 2026

Confirmed cause of the reproduced client-authentication rejection: TEST `shopify.oauth` revision 2 contained a different secret from the currently accepted secret for the same named Moda client ID. Equality checks confirmed that the client ID matched the named app rather than the separate template app.

A deliberately invalid refresh token was used to compare authentication without consuming the real session token. The database secret received HTTP 400 `invalid_request`, classified `INVALID_CLIENT_CREDENTIALS`; the current shell secret received HTTP 401 `invalid_grant`. Both JSON and form requests with the old database credentials received the client-credential rejection. This points to the stored secret rather than the request encoding for that reproduced failure.

The user explicitly approved updating TEST configuration. Applied encrypted revision 3 with the existing client ID and verified current secret, compare-and-set on revision 2, and a redacted configuration audit attributed to `operator:codex-user-approved`. No source-code change or production configuration change was needed.

Post-update checks:

- Shared's production OAuth reader reads revision 3 and the preserved client ID and corrected secret match the verified source.
- The same deliberately invalid-token probe now receives HTTP 401 `invalid_grant`, getting past the earlier client-credential rejection.
- Shared's production `getSession` returned the current offline session without a refresh because it was still valid.
- The production product-search GraphQL document returned HTTP 200 with zero GraphQL errors and zero variants for `product_status:ACTIVE`. Zero variants is a CS03 observation, not a token-refresh failure.
- Current stored access expiry: 7 November 2026 at 17:10:56 UTC. Shared's 320-second refresh window begins at approximately 17:05:37 UTC, also London time on this date.

Remaining CS01 verification: after approximately 17:06, request the session through a real consumer without manually opening Shopify, observe `shopify.offline_refresh.committed`, confirm the rotated pair and expiries persisted, and perform an authorized product read. Check other consumer deployments separately. The existing Shopify app captures OAuth configuration at process startup, so a process started before the correction can retain its old SDK secret until restarted; Shared refresh readers resolve credentials on demand. Do not mark CS01 closed until the expiry-path check passes.

No issue is closed yet. Next action: CS01 automatic refresh verification once the refresh window opens.
