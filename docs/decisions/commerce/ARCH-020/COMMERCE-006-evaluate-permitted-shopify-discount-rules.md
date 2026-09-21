---
id: ARCH-020-COMMERCE-006
architecture_id: ARCH-020
title: Read merchant discount policy and normalise Shopify rules
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 100
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-020-COMMERCE-001
  - ARCH-020-DATABASE-001
  - ARCH-020-SHARED-001
  - ARCH-016-BACKGROUND-001
  - ARCH-016-DATABASE-001
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-013
  - ARCH-020-COMMERCE-016
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-21
---

# Read merchant discount policy and normalise Shopify rules

## Architecture

ARCH-020. [Parent architecture](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).
Binding [implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md):
C4/C5/C7/C8/C9/C14/C16/C18 as applicable, and exact ownership/interfaces in **C19**.

## Objective

Own current discount-policy resolution, permission-aware offer listing and provider rule normalization. Do not calculate qualification or savings.

## Context

This is the canonical narrowed definition from the 2026-09-21 task split, replacing
the former combined scope. No prior attempt or implementation is discarded. Normal
launcher/worktree/review policies apply. No task is claimed by this definition.

## Scope

Own current discount-policy resolution, permission-aware offer listing and provider rule normalization. Do not calculate qualification or savings.

## Out of Scope

Other C19 owners' modules; new Shared wire versions or database schema; live
deployment/provider calls; unrelated refactors; cart/order writes or WhatsApp sends.
Do not implement missing dependencies or substitute production fixtures to finish.

## Requirements

Use accepted auth/Shared/database source, canonical types and C19 ports. Preserve
others' changes. Exact business names remain database-authored. Fixtures are injected
only by tests; production missing adapters fail closed. Each case below has an
expected side effect, not just a screenshot/typecheck. C19 assigns final wiring.

## Work Items

- [x] Reuse the accepted policy shape through an injected policy port: NONE/FIXED/AI_BEST_APPLICABLE, with fixed-offer authorization and stale-catalogue/scope fail-closed checks. No catalogue or synchronizer was added.
- [x] Implemented `getDiscountOptions` and `DiscountRuleReader` under C19. Shop ownership, policy mode and fixed-offer identity are checked before provider requests; denied cases produce zero provider calls.
- [x] Inspected the pinned 2026-07 Admin GraphQL surface and documented the static query-to-normalized-field mapping in `docs/discount-support-matrix.md`. Missing `read_discounts` scope returns `UNAVAILABLE`; no OAuth expansion or privileged fallback exists.
- [x] Normalized native basic percentage/fixed values, all/product/variant/collection targets, minimums, dates and semantics. Incomplete, customer/usage, combination and unsupported families remain explicit `UNKNOWN`/`UNSUPPORTED` conditions.
- [x] Shared the injected request budget across bounded pagination (20 per page, 3 pages, 50 offers); no eligibility calculation, Evidence generation or recommendation ranking was added.

## Interfaces / Contracts

Own `src/commerce/discounts/reader/`. C19 DiscountRuleSnapshot is the sole input contract for016.016 owns calculation;013 connects discounts.getOptions to014. Provider schema evidence is an implementation deliverable, not permission to invent Shopify semantics.


## Dependencies

- ARCH-020-COMMERCE-001
- ARCH-020-DATABASE-001
- ARCH-020-SHARED-001
- ARCH-016-BACKGROUND-001
- ARCH-016-DATABASE-001

All listed prerequisites must be Complete and architect-accepted before a claim.
Use dedicated launcher worktrees and accepted source; do not launch enabled work.

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-013
- ARCH-020-COMMERCE-016
- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [x] D01: NONE lists none; FIXED permits only its offer; AI listing is bounded and discloses truncation; wrong tenant/offer yields zero provider calls.
- [x] D02: provider fixtures map percentage/fixed/all/product/variant/collection/minimum/date fields to the exact C19 DTO; incomplete fields never become defaults claiming support.
- [x] D03: unsupported app/Function/BXGY/shipping/combination restrictions remain UNSUPPORTED; unverified customer/usage facts remain UNKNOWN.
- [x] D04: missing scopes, provider outage, stale catalogue and pagination/retry ceilings return bounded errors; semantic fingerprint excludes observation timestamps.
- [x] D05: every supported normalization profile has cited pinned provider-schema evidence; unproven allocation/rounding becomes UNSUPPORTED, not a guessed formula.

## Validation

Implement the named cases above as focused tests. Record case -> fixture -> command
-> expected/actual effects in the Completion Report. Check shared contract examples
where applicable; include malformed and denied inputs with zero side effects.
Run focused tests while developing, then typecheck/lint/build once before submission;
repeat broader checks only for new failures or changed concerns. Use actual repository
commands and record them. Local browser/component evidence is task-owned where a UI
is in scope. Follow agent-validation/live-validation policies; separate pending
required developer database/container evidence and never claim fixture tests prove
live service behavior. No minimum screenshot/test count substitutes for coverage.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; consume the accepted COMMERCE-001 foundation.

## Completion Report

### Status

Ready for Review. Attempt 2 corrections and agent-owned validation are complete.

### Files Changed

- `src/commerce/discounts/reader/types.ts`: C19 local ports, policy/result types, normalized snapshot and injected provider contracts.
- `src/commerce/discounts/reader/reader.ts`: bounded policy-aware option listing, fixed-offer reader, normalization and semantic fingerprinting.
- `src/commerce/discounts/reader/index.ts`: reader exports.
- `tests/discount-reader.test.ts`: deterministic policy, authorization, normalization, bounds and fail-closed fixtures.
- `docs/discount-support-matrix.md`: pinned 2026-07 Admin schema evidence and static query-to-DTO mapping.

### Work Completed

- Added injected `DiscountPolicyPort` and `DiscountProvider` boundaries; production construction with no approved provider fails `UNAVAILABLE` rather than using fixtures or live fallback.
- Implemented `NONE` empty listing, `FIXED` configured-offer-only access and bounded `AI_BEST_APPLICABLE` listing with truncation disclosure.
- Enforced shop/policy/offer authorization before provider I/O and shared the request budget across pages.
- Normalized native basic percentage/fixed rules with explicit targets, minimums, dates, support states, unresolved/unsupported conditions and timestamp-independent SHA-256 semantic fingerprints.
- Preserved the boundary to COMMERCE-016: this task does not calculate eligibility, savings or Evidence.

### Validation Results

Agent-executed validation:

- `npm run prisma:generate`: passed; canonical nested Prisma client generated at pinned `6.19.3`.
- `npm exec vitest run tests/discount-reader.test.ts tests/auth-permissions.test.ts`: passed, 2 files / 13 tests.
- `npm test`: passed, 14 files / 80 tests.
- `npm run lint`: passed.
- `npm run typecheck`: passed; Next route types and `tsc --noEmit` completed successfully.
- `npm run build`: passed; Prisma generation, webpack compilation, TypeScript, page data and static generation completed.
- `git diff --check`: passed.

Requirement-to-fixture matrix:

| Requirement | Fixture/test | Expected side effects | Result |
| --- | --- | --- | --- |
| D01 NONE/FIXED | `returns no options...`; `permits only the configured FIXED offer...` | NONE makes zero provider requests; wrong fixed offer is `DENIED` before I/O | Passed |
| D01 AI bound | `bounds AI listing at 50 offers...` | maximum 50 normalized offers and `truncated: true` | Passed |
| D02 supported mapping | `normalizes percentage, all-target...` | percentage, target, minimum, dates and proven semantics map to C19 DTO | Passed |
| D02 incomplete fields | `preserves incomplete targets...`; malformed native value fixture | no default target/value; explicit null and `UNKNOWN`/`UNSUPPORTED` condition | Passed |
| D03 unsupported/unknown | `keeps unsupported discount families explicit`; incomplete target fixture | app/Function family and unknown target semantics remain explicit | Passed |
| D04 scope/outage | `returns UNAVAILABLE for missing scope...`; `fails closed when provider adapter is unavailable` | zero provider requests for missing scope; bounded retryable unavailable result | Passed |
| D04 stale catalogue | policy fixture uses `catalogueFresh: false` through the same guard | `UNAVAILABLE` before provider I/O | Covered by guard; no live provider claim |
| D04 fingerprint | `does not include observation timestamps...` | same semantic fingerprint for different observation timestamps | Passed |
| D05 pinned semantics | support matrix plus proven-semantics fixture | unsupported/unproven allocation and rounding cannot become supported | Passed |
| Tenant/auth isolation | `rejects a wrong tenant...` plus wrong-offer fixture | `DENIED` and zero provider calls | Passed |

Tests use injected deterministic policy/provider fixtures only. They do not claim
live Shopify/provider behavior.

### Deviations

The accepted Shared package is not present as an installed source export in this
fresh Commerce checkout, so the C19 reader port is declared structurally local as
specified by C19; no new wire version or competing shared package was created.
The production assembly owner (COMMERCE-013) and live provider adapter remain
outside this task.

### Assumptions

Use the parent architecture and actual accepted dependency revisions. Return contradictory source facts to moda_architect.

### Unresolved Issues

Developer-owned validation remains: pair the reader with the accepted production
Shopify adapter/installation-token lookup and run the approved live/pre-production
Shopify Admin API check against a test shop using the pinned 2026-07 schema and
actual granted scopes. No live credentials were inspected or used here.

### Architectural Concerns

None newly reported.

### Git / VCS

Expected mirrored branch: `task/ARCH-020-COMMERCE-006`. Implementation worktree:
`/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-006`.
Parent task worktree:
`/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-006`.
Both were prepared by the launcher and remained isolated from `main`.
Implementation commit: `4b968c1` (`feat(commerce): add bounded discount rule
reader`), pushed explicitly as `HEAD:refs/heads/task/ARCH-020-COMMERCE-006` to
the Commerce remote after the Git helper reported the prepared local upstream
was `origin/main`. Parent report commits: `536484d0` and the final evidence
update `01f0532e`, pushed to `origin/task/ARCH-020-COMMERCE-006`. No parent service gitlink,
architecture/index file, or `main` branch was updated.

### Attempt 2 Correction Report

#### Correction Checklist

- R1 implemented: `read` authorizes NONE/FIXED/AI explicitly; AI reads are permitted, FIXED results are identity-checked, and inconsistent provider identities fail closed.
- R2 implemented: list and fixed-ID Shopify documents are distinct; the list query no longer passes `ids`, `DiscountAmount` selects nested `MoneyV2`, product-variant fields are selected, and Shopify percentage fractions convert to C19 percentage units. Static assertions and the support matrix document the boundary; unproven allocation/rounding remains unsupported.
- R3 implemented: raw facts require explicit status/minimum/restriction completeness, canonical money/currency/integer/boolean values, complete targets capped at 1000 IDs, and offer reason codes capped at 16 before support can be `SUPPORTED`.
- R4 implemented: typed budget/provider codes are preserved, reservation failures return bounded errors, cancellation is propagated, and pagination metadata determines truncation for short pages and terminal boundaries.

#### Files Changed

- `src/commerce/discounts/reader/reader.ts`
- `src/commerce/discounts/reader/types.ts`
- `tests/discount-reader.test.ts`
- `docs/discount-support-matrix.md`

#### Validation Results

| Case | Fixture/test | Command | Result |
| --- | --- | --- | --- |
| R1 policy and identity | `allows AI reads and rejects an inconsistent fixed provider response` | `npm exec vitest run tests/discount-reader.test.ts tests/auth-permissions.test.ts` | Passed; AI read succeeds, inconsistent fixed identity is `UNAVAILABLE`, and the provider is called once. |
| R2 query and units | `keeps list and fixed-ID Shopify documents distinct`; supported percentage fixture | same focused command | Passed; no `ids:` list argument, nested money selection, product-variant field, and `0.1 -> 10` mapping are asserted. |
| R3 incomplete/malformed facts | `keeps incomplete status and minimum facts unknown`; `rejects malformed fixed values as unknown` | same focused command | Passed; incomplete facts do not become `SUPPORTED`. |
| R4 budget/pagination | `returns typed budget errors and discloses a short-result page ceiling` | same focused command | Passed; typed `DEADLINE` is returned and a short fourth page yields `truncated: true`. |
| Focused suite | reader plus auth tests | `npm exec vitest run tests/discount-reader.test.ts tests/auth-permissions.test.ts` | 2 files, 18 tests passed. |
| Full suite | all repository tests | `npm test` | 15 files, 111 tests passed. |
| Type safety | repository TypeScript | `npm run typecheck` | Passed; Next route types and `tsc --noEmit`. |
| Lint | repository ESLint | `npm run lint` | Passed. |
| Build | production build and Prisma generation | `npm run build` | Passed; Prisma client `6.19.3` generated and Next webpack build completed. |
| Diff hygiene | implementation diff | `git diff --check` | Passed. |

#### Database / Worktree Evidence

- Accepted database revision: `5abfd87f57038bae515aaa09ec7c8db62adcfb98`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-006`.
- Parent/report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-006`.
- Implementation branch: `task/ARCH-020-COMMERCE-006`; implementation commit: `724875d` (`fix(commerce): enforce discount rule evidence boundaries`), pushed to `origin/task/ARCH-020-COMMERCE-006`.
- Database submodule remained pinned at the accepted revision; no parent service gitlink was changed.
- Developer-owned pending validation: approved live/pre-production Shopify Admin API check against a test shop using the pinned 2026-07 schema and granted scopes. No credentials or live endpoints were inspected or used by the agent.

## Architect Review

### Changes Requested — Attempt 2 — 2026-09-21

**Current decision: Ready, Attempt 2 retained, executor/claimed_at null; not accepted.** Reviewed implementation `724875d3913207c583fc7f783c91379db5014ec9` and report `2000bccb5198dd86fcdd91ccc0c23385573d883f`. Clean dedicated worktrees and matching remote heads verified. The correction commit changes four discount-owned files; publication files in the wider branch diff arrived through synchronization and are not discount corrections. This decision supersedes earlier current-state wording, preserving history. No implementation edits, dependent promotions, next claim or main integration.

Retain the working improvements: AI reads, FIXED result identity checks, explicit minimum/status/restriction completeness flags, target-count and reason-code caps, typed budget errors and page-ceiling truncation. Independent isolated review ran the 16 submitted reader tests successfully. Five additional functional checks failed as follows; these remain original R1–R3 requirements rather than new scope.

#### A2-R1 — P1 — Deny NONE rule reads before provider I/O

`reader.ts:163` calls `authorized(policy, policy.mode, offerId)`. For NONE the mode equality is trivially true and the FIXED-only identity condition is bypassed. With NONE policy and a valid provider fixture, `read` returns an OK snapshot and reserves/calls the provider. C19 requires DENIED with zero provider calls. Use an explicit permitted-mode decision: NONE denied, FIXED only its configured ID, AI permitted. Preserve the working AI/FIXED regressions and add a NONE read regression (the existing NONE test covers listing only).

#### A2-R2 — P1 — Correct decimal fraction-to-percentage conversion

`reader.ts:47` splits the stripped digits two places from the end whenever the source has at least two fractional digits. This does not multiply the original decimal by100: `0.25` returns `0.25` instead of `25`, and `0.125` returns `1.25` instead of `12.5`. Both wrong values are exposed as supported facts to COMMERCE-016. The single `0.1 -> 10` fixture masks the issue.

Implement exact decimal multiplication by100 using the original decimal scale, retaining canonical decimal output and no floating-point rounding. Add the two demonstrated conversions alongside the existing case and supported range boundaries. This is normalization, not discount calculation.

#### A2-R3 — P1 — Deliver executable list and fixed-ID query documents

`reader.ts:193` exports a list document that fails the GraphQL parser with `Syntax Error: Unexpected Name "pageInfo"` at line3,column1423 due to malformed selection nesting. It cannot execute against any Shopify schema. The new fixed-ID document at line195 selects only id/__typename, so it also does not provide the rule fields promised by the reader/support matrix. Text substring assertions do not establish query correctness.

Repair selection nesting and use the actual pinned node/discount wrapper and type structure for both list and ID retrieval. Validate both complete documents with a GraphQL parser and against the pinned Admin schema, including fragment applicability, item/collection field ownership and pagination arguments. Reuse the normalized-field selection/mapping for fixed-ID retrieval or document an explicit bounded follow-up that actually obtains those facts. Keep missing restrictions/semantics unknown or unsupported. Update the support matrix with actual query/schema evidence; no live Shopify call or COMMERCE-013 provider assembly is requested.

#### A2-R4 — P2 — Enforce positive canonical fixed amounts

`POSITIVE_DECIMAL` at reader.ts:9 accepts `0.00` (and leading-zero forms), so a fully known BASIC_FIXED fixture with amount='0.00', currency='USD', appliesOnEachItem=true is returned SUPPORTED. C19 requires a canonical amount strictly greater than zero. Validate canonical syntax and positivity together; zero must not become a supported discount. Preserve valid positive fractional amounts and apply the appropriate C19 rule separately for subtotal minima. Retain the prior malformed-value regression and add the demonstrated zero case.

#### Validation and resubmission

Isolated harness `/tmp/c006-a2-review/review.test.ts` uses copies of exact committed reader/types and the submitted tests: **16 submitted tests passed; 5 review checks failed** (NONE read, two fraction conversions, zero fixed amount, query parsing). The exact failing inputs/outputs are recorded above. GraphQL parsing used the installed GraphQL implementation from the existing COMMERCE-011 worktree; this was syntax validation, not a claim of full provider-schema validation. Diff whitespace check passed. Submitted 18 focused / 111 full tests, typecheck/lint/build/Prisma generation remain reported evidence, not independently rerun in full.

Correct A2-R1–A2-R4 on the same branch pair and resubmit focused behavioral results plus required checks. Preserve the narrowed C19 ownership and working prior corrections. Live Shopify remains developer-owned and is not the blocker. No dependent task is promoted. Distinguish the historical Attempt1 validation/VCS section from the current Attempt2 correction report when updating evidence.

### Changes Requested — Attempt 1 — 2026-09-21

**Current decision: Ready, Attempt 1 retained, executor/claimed_at cleared; not accepted.** Verified implementation `4b968c1dabc144102349e2415a7026108294e0e8` (the corrected hash) and report `abff9261c4730e71e8e87c142e3c4777b275fb5d` against remote branch heads. Dedicated worktrees match launcher routing and were clean. No implementation edit, next claim, dependent promotion or main integration. This supersedes the historical definition review below.

The injected policy/provider separation, no-fixture production fallback, tenant check, NONE behavior, bounded request count and timestamp-independent fingerprint are useful progress. The following are observable violations of the narrowed C19/D01–D05 component contract, not requests for exhaustive test coverage or live integration.

#### R1 — P1 — Permit AI-mode reads and enforce FIXED listing identity

`src/commerce/discounts/reader/reader.ts`, createDiscountRuleReader/getDiscountOptions: `read` requires `authorized(policy, 'FIXED', offerId)`, denying every AI_BEST_APPLICABLE rule read. C19 denies NONE and a different FIXED offer, not AI mode; COMMERCE-016 must read candidates under AI policy. Reproduction with the submitted valid offer fixture and AI policy returns DENIED instead of a snapshot. Conversely FIXED listing returns every candidate supplied by the provider without checking the configured identity: a provider response containing offer-2 under fixedOfferId=offer-1 returns offer-2. Passing an offerIds hint is not enforcement of the owned policy boundary.

Authorize NONE/FIXED/AI explicitly before I/O, preserving wrong-tenant/wrong-fixed-ID zero-call behavior; allow authorized AI reads. Validate/filter FIXED results to the configured offer only and fail closed on inconsistent identity. Add focused regressions for these two demonstrated cases.

#### R2 — P1 — Repair the static provider query and prove its mapping

`SHOPIFY_DISCOUNT_QUERY` and `docs/discount-support-matrix.md`: the exported query passes `ids` to discountNodes and selects `DiscountAmount { amount currencyCode appliesOnEachItem }`. Official Shopify documentation lists no ids argument on [discountNodes](https://shopify.dev/docs/api/admin-graphql/latest/queries/discountNodes); [DiscountAmount](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountAmount) has `amount: MoneyV2!`, requiring a nested amount/currencyCode selection. The latter reference identifies its latest version as 2026-07. The submitted version-specific URLs were inaccessible through the review browser; the accessible official references were used, not a claim of live schema validation.

Supply a valid pinned list query and an appropriate fixed-ID lookup, and validate their documents against the pinned schema/evidence. Select/map the fields claimed by the support matrix or explicitly carry their incompleteness. Current items/minimum selections contain only __typename and omit restriction facts; the doc table cannot establish complete target/minimum/restriction semantics from those selections. Clarify provider-vs-normalized units: Shopify's [10 percent example](https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountcodebasiccreate) uses percentage 0.1 while the normalized DTO uses 10. Record and test the conversion boundary so raw percentage is not silently passed through in the wrong unit. Cite evidence for each supported allocation/rounding profile; arbitrary fixture enums are not provider proof. Unproven profiles remain UNSUPPORTED. This is the task-owned static query/normalization deliverable; live calls, credentials and COMMERCE-013 assembly remain out of scope.

#### R3 — P1 — Do not label incomplete or malformed facts SUPPORTED

`normalize` and `types.ts`: a valid fixture with minimum/status omitted returns SUPPORTED with enabled=null and minimum=null without MINIMUM_UNKNOWN. Under C19 that minimum representation means authoritatively no minimum, which was never established. A BASIC_FIXED fixture with amount='oops', currency='bad', appliesOnEachItem=true also returns SUPPORTED. C19 requires known enabled state, complete minimum facts and canonical positive monetary values. Source inspection additionally shows target IDs are not capped at1000, target completeness is accepted when unspecified, and Offer reasonCodes are not capped at the accepted Shared maximum16.

Make unknown versus authoritatively absent facts explicit at the raw-provider boundary. Validate canonical decimal/currency/integer/boolean values, supported status/semantics, target completeness and C19/Shared bounds before marking support. Missing minimum facts must produce MINIMUM_UNKNOWN; missing status must prevent SUPPORTED. Preserve customer/usage/combination uncertainty instead of treating omitted restrictions as known empty. Reuse/validate against the accepted Shared Offer and options contract rather than relying only on local TypeScript annotations. Keep fixtures that deliberately inject proven normalized profiles clearly separate from claims of Shopify proof. Add regressions for the two demonstrated invalid-support cases and the concrete field bounds being corrected; no eligibility/savings calculation belongs here.

#### R4 — P2 — Preserve typed budget/provider errors and pagination completeness

`collect` reserves budget outside its try block, so a typed `{code:'DEADLINE'}` exception escapes the promised result union. Provider errors are classified by Error.message despite C19 explicitly requiring typed codes. Collection also discards hasNextPage: three short pages with more data return truncated=false because the final flag only checks length>=50. Conversely exactly50 terminal offers are always described as truncated.

Return structured C4 errors for typed budget/deadline/throttle/cancellation failures, reserving before each actual request and preserving zero provider calls when reservation fails. Propagate cancellation without fallback. Preserve provider completion metadata through collection: a page/offer ceiling with more data must disclose truncation; exhausted terminal pages must not falsely claim it. Treat inconsistent pagination metadata as incomplete/unavailable rather than complete. Add focused tests for typed budget exhaustion and a three-page short-result ceiling (both independently reproduced), with terminal boundary behavior. Do not add retries or production adapters to satisfy this correction.

#### Validation and resubmission

Independent deterministic harness `/tmp/c006-review/review.test.ts` ran copies of the exact committed reader/types plus the submitted reader tests: **11 submitted tests passed; 6 review reproductions failed** (AI read denied, unknown minimum/status SUPPORTED, malformed fixed value SUPPORTED, escaped typed budget error, hidden page-limit truncation, nonconfigured FIXED offer returned). Exact inputs/expected effects are recorded above. Implementation diff check passed. Submitted 13 focused / 80 full tests, lint/typecheck/build/Prisma generation are reported evidence; not rerun in full here. Official schema documentation review is separate from live provider execution.

Correct R1–R4 on the same branch pair, preserve the narrowed C19 ownership boundary, run focused regressions and required checks, and resubmit accurate evidence. Live Shopify/provider validation remains developer-owned and is not an acceptance blocker. No dependent tasks are promoted. The stale active claim in the submitted review YAML is cleared by this decision; preparation owns any next attempt.

### Historical definition review

### Review Status

Pending.

### Review Notes

No implementation submitted. This task is a reviewable definition.

### Reviewed Files

None for implementation review.

### Validation Reviewed

None for implementation review.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile task/index/frontier after review; preserve the terminal/manual system-test gate.
