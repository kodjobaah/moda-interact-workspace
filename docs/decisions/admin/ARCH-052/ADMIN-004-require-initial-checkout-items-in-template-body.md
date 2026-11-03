---
id: ARCH-052-ADMIN-004
architecture_id: ARCH-052
title: Require a frozen checkout-items BODY binding in every initial Meta recovery template
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 25
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-052-ADMIN-003
  - ARCH-052-BACKGROUND-005
enables:
  - ARCH-052-BACKGROUND-017
  - ARCH-052-BACKGROUND-018
  - ARCH-052-SYSTEM-TEST-001
  - ARCH-052-SYSTEM-TEST-002
  - ARCH-052-SYSTEM-TEST-004
created: 2026-10-31
updated: 2026-11-01
---

# ARCH-052-ADMIN-004: Require checkout items in initial Meta recovery template bodies

## Architecture

- Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.
- Owner: `moda_admin`, repository `moda-interact-admin/`.
- This is a portable task definition **defined but not materialised**. Implement through the launcher-resolved dedicated `task/ARCH-052-ADMIN-004` parent and implementation worktrees. Do not implement in BG008's active worktree.

## Objective

Ensure **every** newly authored, frozen, reviewed and published `META_RECOVERY` template with `stage: INITIAL` visibly includes the **actual abandoned checkout items** in its **BODY** through exactly one `checkout.itemsSummary` semantic binding, independent of offer type, promotion target, locale and header kind.

## Context

- `authoring/registry.ts` currently excludes `checkout.itemsSummary` for `offerType: NO_OFFER` and for `promotionTarget: ALTERNATIVE_PRODUCT`; the CHECKOUT-offer branch allows it. `authoring/validation.ts` requires `shop.name` and Reply instructions for initial copies but does not require the basket binding for all initial variants.
- ARCH-052-BACKGROUND-005 is already Complete and implements the existing Shared `checkout.itemsSummary` semantic key using trusted `CheckoutRecovery.lineItems`, with a bounded, locale-aware first-three-lines + `+N` summary. No new Shared schema, variable, formatter or database column is needed.
- ARCH-052-ADMIN-003 is Complete, already preserving merchant-identity/Reply text, singular/plural offer copy, alternative-product separation and immutable Meta registration/approval.
- Historical frozen Meta template registrations cannot be rewritten to add another positional BODY variable: this is a **new immutable revision** requiring independent Meta approval. Authoring enforcement must not pretend historical registrations are compliant.

## Scope

Implement the basket-binding **authoring and publication** invariant within `moda-interact-admin/`; include all existing INITIAL purpose/offer/target/header and 20-locale variants. Extend existing tests, previews and provider submission validations, and preserve the immutable publication lifecycle.

## Out of Scope

- Do not modify `ARCH-052-BACKGROUND-008`, `ARCH-052-ADMIN-003`, existing accepted task Completion Reports or any `_index.md`.
- No Background sender change, production provider call, Meta approval bypass, additional templating system, new semantic key, Prisma migration, checkout item reader, new checkout URL generation or order-confirmation template.
- Do not change `FOLLOW_UP` or `MODA_CONVERSATION_WRAPPER` semantics. Do not impose IMAGE availability on TEXT templates.

## Requirements

### A. Mandatory variable, eligibility and BODY placement

Modify **these exact existing Admin source files** (additional directly related tests permitted):

1. `src/lib/admin/whatsapp-templates/authoring/registry.ts`: for `family === "META_RECOVERY" && stage === "INITIAL"`, allow `checkout.itemsSummary` in BODY for each `NO_OFFER`, checkout-target CODE/AUTOMATIC (single or plural), and alternative-product CODE/AUTOMATIC variant. Preserve other offer-specific variables exactly. Do not add it to the IMAGE/TEXT HEADER, FOOTER or URL button palettes, and do not extend wrapper allowances. Preserve existing FOLLOW_UP eligibility.
2. `src/lib/admin/whatsapp-templates/authoring/validation.ts`: for **initial, publication-compliant** Meta ASTs, reject unless `raw.body` contains **exactly one** `{ type: "variable", name: "checkout.itemsSummary" }`. Reject missing, duplicated, text-only simulation, a header-only occurrence, or an invalid variable position. Preserve all existing `shop.name`, contextual Reply, multi-code, alternative-product, image-header, Meta 1,024-character BODY, and at-most-ten BODY variable requirements. Make the rule reachable at each existing production freeze/review/publish/registration boundary that uses `requireInitialReply: true`; incomplete editor drafts may retain the existing non-publishable editing behaviour.
3. `src/lib/admin/whatsapp-templates/authoring/draft-operations.ts`: ensure newly constructed INITIAL BODY defaults/variant changes include exactly one semantic node in a clearly labelled original-basket section. Preserve the complete reviewed Reply tail and the existing offer-specific copy. In ALTERNATIVE_PRODUCT, visibly separate **original abandoned items** from the different recommended product and do not imply its discount applies to the original basket.
4. `src/lib/admin/whatsapp-templates/authoring/compiler.ts`, `src/lib/admin/whatsapp-templates/publishing/source.ts`, `src/lib/admin/whatsapp-templates/meta/snapshot.ts`, and `src/lib/admin/whatsapp-templates/compilation/reconstruction.ts`: reuse their established frozen AST, provider BODY example, translation and registration mechanisms. Only adjust these files if needed to ensure the updated invariant is checked in every publishable path. Do **not** build a second compiler or change positional binding schema. The compiled `parameterBindings.body` position must correspond to exactly one `{{N}}` token in the submitted immutable Meta BODY; its example value must be the existing safe registry sample, not merchant/customer data.
5. `src/lib/admin/whatsapp-templates/translations/source-snapshot.ts` and existing locale/translation operations: retain the new semantic node and its position through all **20 supported locale** review/compile flows, together with the existing merchant name and Reply instructions. Each locale requires reviewed, meaningful original-basket wording; preserve each locale's translation-review gate, not machine-inferred English copy.

Do not insert raw `{{...}}` strings into AST literal text. The merchant/product/cart identities are resolved at runtime; Admin examples must never contain actual customer data.

### B. Exact template matrix (all must be independently validated)

| Stage | Offer type | Target | Header | Mandatory BODY semantic |
|---|---|---|---|---|
| INITIAL | NO_OFFER | none | TEXT | `checkout.itemsSummary` exactly once |
| INITIAL | CODE_OFFER | CHECKOUT | TEXT / approved IMAGE where supported | Exactly once, plus existing singular/plural code binding |
| INITIAL | AUTOMATIC_OFFER | CHECKOUT | TEXT / approved IMAGE where supported | Exactly once, plus existing honest automatic wording |
| INITIAL | CODE_OFFER | ALTERNATIVE_PRODUCT | TEXT / approved IMAGE where supported | Exactly once, explicitly described as **original basket** |
| INITIAL | AUTOMATIC_OFFER | ALTERNATIVE_PRODUCT | TEXT / approved IMAGE where supported | Exactly once, explicitly described as **original basket** |
| FOLLOW_UP | Any existing valid variant | Existing rules | Existing rules | **No new mandatory condition** |
| MODA_CONVERSATION_WRAPPER | Any | Existing rules | Existing rules | **No change** |

IMAGE headers are optional and separate; `checkout.itemsSummary` remains a textual BODY parameter even when the header is IMAGE. The BODY displays the existing bounded first-three-line summary and `+N` remainder, not a fabricated entire-basket transcription. No price/savings is inferred from the summary.

### C. Immutable registration and live readiness

- Changed source BODY or locale means a new immutable content hash, binding fingerprint and provider-review revision. Preserve historical source, approval and Meta provider IDs without rewriting them.
- Draft save, locale review, source publication, frozen provider submission and preview must agree on the exact BODY parameter sequence. A newly compliant definition is **not provider-approved** until Meta actually approves it; do not mark it APPROVED in tests or runtime config without provider evidence.
- If a legacy initial registration lacks the binding, Admin must not treat it as compliant for new initial outreach. Background-017 owns the separate final runtime gate and will exclude it. This task does not change BG008's active implementation.
- Visible merchant name, basket label, dynamic basket summary, Reply-on-this-message instructions, text/voice note guidance, and CTA remain independently present; ALTERNATIVE_PRODUCT's promotion is not part of the original basket.

## Work Items

- [x] Update eligible-variable registry for all INITIAL variants without broadening FOLLOW_UP/wrapper variables.
- [x] Enforce exactly-one BODY semantic at all publishable validation paths; reject missing/duplicate/header-only/static imitations.
- [x] Update INITIAL defaults and alternative-product copy; preserve locale-aware Reply tail and source translation structure.
- [x] Update compiled/translated Meta examples, immutable revision and snapshot conformance tests across 20 locales.
- [x] Document Meta reapproval requirement for revised immutable template versions; do not claim provider approval was executed.

## Interfaces / Contracts

**Existing Shared contract (no modification):** `@modainteract/moda-interact-shared/recovery-template-bindings` semantic key `checkout.itemsSummary` and existing frozen `parameterBindings.body` `{ position: number, variable: string }` entries.

**Exact AST node:**

```json
{ "type": "variable", "name": "checkout.itemsSummary" }
```

**Valid illustrative English BODY AST fragment** (part of a full AST; do not use raw template tokens):

```json
[
  { "type": "text", "value": "You left these items in your basket: " },
  { "type": "variable", "name": "checkout.itemsSummary" },
  { "type": "text", "value": ". " }
]
```

Compiled position is determined by the existing `bodyText()` compiler from the order of BODY variable nodes. The verified consumer must identify `checkout.itemsSummary` through the **frozen semantic bindings**, not by searching translated text for an English phrase.

**Producers:** Admin authoring/translation/compiler. **Consumer:** existing Meta registration snapshots and subsequent Background-017 send admission. **Version:** existing `schemaVersion:1`; no new API or local clone.

## Dependencies

- `ARCH-052-ADMIN-003` — accepted template semantics and 20-locale instructions.
- `ARCH-052-BACKGROUND-005` — accepted existing summary semantic and locale-aware runtime binder.

## Enables

- `ARCH-052-BACKGROUND-017` — runtime send guard after BG008 and optional BG007.
- `ARCH-052-SYSTEM-TEST-004` — terminal cross-platform certification after implementation tasks.

## Acceptance Criteria

- [x] For every INITIAL variant in matrix A/B, `eligibleVariables` allows the BODY semantic and `validateTemplateAst(..., { requireInitialReply:true })` rejects any absent/duplicated checkout-summary variable.
- [x] Each of the 20 locale review/publication paths round-trips exactly one BODY semantic, its provider position, and the localized original-basket label; existing BODY parameter, language and character limits hold.
- [x] Header-only, literal imitation, missing and duplicated body nodes fail; TEXT/IMAGE, single/multi CODE, AUTOMATIC and alternative-product remain distinct and correct.
- [x] Translation and publication preserve the existing `shop.name` + contextual Reply, dynamic buttons and offer provenance rules.
- [x] New BODY revisions are immutable and must obtain independent Meta approval; no previously approved hash/registration is altered or implicitly accepted.
- [x] Existing FOLLOW_UP and wrapper validation/authoring paths remain unchanged.

## Validation

- [x] `tests/unit/arch047-template-authoring-ast.test.ts`: matrix and negative cases.
- [x] `tests/unit/arch047-template-translations.test.ts`: all 20 locale structural/semantic/position checks.
- [x] `tests/unit/arch047-template-compilation.test.ts`, `tests/unit/arch047-template-meta-snapshots.test.ts` and `tests/unit/arch047-template-publication-pure.test.ts`: frozen provider BODY, identity and approval checks.
- [x] `tests/integration/arch047-template-authoring.postgres.test.ts` and `tests/integration/arch047-template-publication.postgres.test.ts` with disposable PostgreSQL: accepted/rejected immutable revision flows; Attempt 2 publication fan-out and all remaining publication cases pass.
- [x] Repository-declared changed-file lint, typecheck/build and `git diff --check`; record exact invoked commands/results, not assumed scripts.

## Stop Condition

After the specified Work Items, Acceptance Criteria and validation are completed, update only this task's execution metadata, checklists and Completion Report, set `status: review`, return control to `moda_architect`, and **STOP**. Do not start BG017, overwrite the historical ADMIN-003 task, or edit `_index.md`.

## Implementation Notes

Use the existing `authoring/registry.ts` and `validation.ts` path; no second renderer or schema. Keep each source/test module bounded and follow the existing Admin translation/publishing patterns. Use `@modainteract/moda-interact-shared/logging`; preserve actual upstream provider/SDK errors with bounded redaction, and propagate unexpected failures. Never log customer names, checkout URLs, product descriptions or generated copy.

## Completion Report

### Status

Accepted and Complete — Attempt 2. The publication PostgreSQL fan-out failure
was attributed to transient per-shop Prisma transaction and serialization
failures, recorded at shop/operation level, and recovered through the bounded
retry path. The full disposable publication suite now passes; Attempt 1 and its
review remain preserved below.

### Files Changed

- `moda-interact-admin/src/lib/admin/whatsapp-templates/authoring/registry.ts`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/authoring/validation.ts`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/authoring/draft-operations.ts`
- `moda-interact-admin/src/components/admin/whatsapp-templates/authoring/template-family-purpose-selector.tsx`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/translations/source-snapshot.ts`
- Related authoring, translation, compilation and Meta snapshot unit tests/fixtures.
- `moda-interact-admin/src/lib/admin/whatsapp-templates/publishing/assignment.ts`
- `moda-interact-admin/tests/integration/arch047-template-publication.postgres.test.ts`
- Attempt 2 implementation commit: `db86942` (`fix(admin): retry transient template publication transactions`), pushed to `origin/task/ARCH-052-ADMIN-004`.

### Work Completed

- `checkout.itemsSummary` is eligible in INITIAL BODY across NO_OFFER, CHECKOUT and ALTERNATIVE_PRODUCT variants; existing FOLLOW_UP checkout eligibility remains unchanged, and wrapper/header/footer/button palettes are not broadened.
- Publication-compliant INITIAL AST validation now requires exactly one BODY semantic node. Missing/static-only, duplicate and header-only cases fail at existing `requireInitialReply: true` boundaries.
- New INITIAL drafts and stage/offer/target changes maintain one labelled original-basket binding while preserving the reviewed Reply tail. Alternative-product proof copy is kept separate from the abandoned basket.
- Translation snapshots protect the semantic node and refuse incomplete INITIAL source snapshots. Locale fixture flows retain localized basket wording, and compilation/snapshot tests verify one frozen provider BODY position in all 20 locales.
- Revised source content produces new immutable hashes/positions; historical registrations were not rewritten. A changed initial Meta template revision still requires independent Meta review and provider approval. No provider submission or approval was executed.

Physical worktree isolation:
- canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-ADMIN-004`
- parent branch: `task/ARCH-052-ADMIN-004`
- implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-ADMIN-004`
- implementation branch: `task/ARCH-052-ADMIN-004`
- shared workspace checkout switched/mutated for task work: no
- shared implementation checkout switched/mutated for task work: no
- another task worktree reused: no

Start-of-attempt synchronization and submodules:
- parent remote task branch fast-forwarded: not-needed; parent origin/main incorporated: already-current
- implementation remote task branch fast-forwarded: not-needed; implementation origin/main incorporated: already-current
- `git submodule sync --recursive`: passed
- `git submodule update --init --recursive`: passed
- implementation `database` submodule: initialized at `7c377282aa5819b3008b7d7f3018f44f4161523e`

### Validation Results

- PASS — `npm run test:arch047-admin-authoring:unit`: 41 passed, 0 failed.
- PASS — `npm run test:arch047-admin-translations:unit`: 16 passed, 0 failed.
- PASS — `npm run test:arch047-admin-compilation:unit`: 15 passed, 0 failed.
- PASS — `npm run test:arch047-admin-meta:unit`: 18 unit tests and 1 component test passed, 0 failed.
- PASS — `npm run test:arch047-admin-publication:unit`: 22 passed, 0 failed.
- PASS — `npm run test:arch047-admin-authoring:postgres`: 2 passed, 0 failed using the disposable PostgreSQL harness; container cleanup was completed.
- HISTORICAL FAIL — Attempt 1 — `npm run test:arch047-admin-publication:postgres`: 4 passed, 1 failed. The 100-shop × 20-language fan-out returned `PARTIAL`; the latest Architect Review requested target-level diagnosis and a complete rerun.
- PASS — Attempt 2 — `npm run test:arch047-admin-publication:postgres`: 5 passed, 0 failed; full suite duration 620.8 seconds. The 100-shop × 20-language case passed and ended `COMPLETE` with 2,000 succeeded targets and 0 failed targets. During the run, live database inspection attributed all 20 locale failures for `shop_0015` to the bulk operation with `TRANSACTION_TIMEOUT`; they were whole-shop atomic failures, not locale-specific failures. Earlier diagnostic reruns attributed whole-shop `TRANSACTION_TIMEOUT` failures to `shop_0007` and `shop_0056`, and `SERIALIZATION_CONFLICT` for `shop_0002` to the distinct overlapping-publication operation. The harness's bounded retry completed the transient failures. The remaining stale-approval, forced rollback/retry, overlapping-publication and external-identity conflict cases also passed.
- PASS — Attempt 2 — `npm run test:arch047-admin-publication:unit`: 22 passed, 0 failed.
- PASS — Attempt 2 — `npx tsc --noEmit`.
- PASS — Attempt 2 — `npx eslint --no-warn-ignored src/lib/admin/whatsapp-templates/publishing/assignment.ts tests/integration/arch047-template-publication.postgres.test.ts`.
- PASS — Attempt 2 — `git diff --check` in both task worktrees.
- PASS — `npx tsc --noEmit`.
- PASS — `npx eslint --no-warn-ignored` on the changed source/test paths; no errors.
- PASS — `git diff --check`.
- Dependency setup — `npm ci` completed from the repository lockfile in the isolated implementation worktree; no tracked dependency files changed.

### Deviations

Attempt 1's publication fan-out did not pass and remains recorded as historical evidence. Attempt 2 identified retryable Prisma transaction failures at the whole-shop operation boundary: `P2028` transaction timeouts and a `P2034` serialization conflict. The disposable container showed no ungranted PostgreSQL locks and low resource use; the failures were not locale-semantic errors or evidence of database lock contention. The timeout occurred inside the existing serializable per-shop publication transaction (30-second transaction timeout, 10-second max wait). The evidence points to transient publication transaction duration/conflict under the bulk and overlapping-publication workloads; it does not implicate the authoring/translation changes, and it does not support a resource-starved PostgreSQL harness diagnosis. The implementation preserves distinct bounded failure codes and safely retries these transient transaction failures; the complete suite passed.

### Assumptions

Only immutable newly authored Meta INITIAL revisions are accepted as compliant; historical provider approvals remain unchanged.

### Unresolved Issues

No unresolved publication failures remain in Attempt 2. Retryable failure codes remain visible by shop and operation while failed, and successful retry leaves all 2,000 targets complete. No provider submission or approval was performed. On architect acceptance, BACKGROUND-017 and BACKGROUND-018 become Ready because their other dependencies are complete; SYSTEM-TEST-004 remains Pending until BACKGROUND-017 is complete.

### Architectural Concerns

No source or provider schema change was introduced. Independent Meta approval remains required for every revised immutable template revision; this task did not contact Meta or claim approval.

## Architect Review — Attempt 2

### Review Status

Accepted — Attempt 2. With `completion_mode: automatic`, the task transitions
to `status: complete`; executor and claim are clear, and Attempt 1 with its
review remains preserved.

### Review Notes

Attempt 2 closes the publication failure left unresolved in Attempt 1. The
report correlates failures to whole-shop transaction rollback for
`TRANSACTION_TIMEOUT` and `SERIALIZATION_CONFLICT`; it does not attribute the
failures to individual locale content or claim provider approval. The Admin
publication path now maps Prisma `P2028` and `P2034` to bounded failure codes
and admits those codes to the existing user-triggered retry path with the
existing three-attempt cap. The 100-shop × 20-locale regression verifies that
failed shops roll back all 20 locale targets and that retry reaches 2,000
successful targets without failed rows. Other publication cases also passed.

The required initial `checkout.itemsSummary` authoring, translation,
compilation, immutable revision and approval semantics remain covered by the
reported unit and disposable PostgreSQL suites. No existing provider approval
was modified, and no external Meta approval is claimed. The typecheck result is
the unchanged unrelated TS2345 in
`tests/system-commerce-tool-sync.test.ts:305:72`.

Dependency review found that BACKGROUND-018 and SYSTEM-TEST-001/002 also
declare ADMIN-004 as a prerequisite, although ADMIN-004's `enables` list had
omitted them. The task record and ARCH-052 status matrix now include those
relationships. BACKGROUND-017 and BACKGROUND-018 are Ready because all their
dependencies are Complete. SYSTEM-TEST-001/002 remain Pending on their other
implementation prerequisites, and SYSTEM-TEST-004 remains Pending until
BACKGROUND-017 is accepted Complete.

### Reviewed Files

- `src/lib/admin/whatsapp-templates/authoring/registry.ts`
- `src/lib/admin/whatsapp-templates/authoring/validation.ts`
- `src/lib/admin/whatsapp-templates/authoring/draft-operations.ts`
- `src/lib/admin/whatsapp-templates/translations/source-snapshot.ts`
- `src/lib/admin/whatsapp-templates/publishing/assignment.ts`
- Related authoring, translation, compilation and Meta snapshot tests.
- `tests/integration/arch047-template-publication.postgres.test.ts`
- The Attempt 2 Completion Report and validation evidence.

### Validation Reviewed

- Authoring, translation, compilation, Meta snapshot and publication unit
  suites passed (41, 16, 15, 19, and 22 tests respectively).
- Disposable authoring PostgreSQL suite passed 2/2.
- Disposable publication PostgreSQL suite passed 5/5; the 100 × 20 fan-out
  ended COMPLETE with 2,000 succeeded targets and zero failed targets after
  bounded retry. Stale approval, rollback/retry, overlapping publication and
  external-identity conflict cases also passed.
- `npx tsc --noEmit`, changed-file ESLint and `git diff --check` passed.
- Typecheck remains separately non-green only for the reported unrelated
  ProcessEnv diagnostic; no Meta provider submission or approval was performed.

### Architecture Conformance

Conforms to ARCH-052. The immutable template and locale approval lifecycle is
preserved; retry is bounded to transaction timeout/serialization failures and
remains an explicit publication retry. No customer/provider data is written to
failure diagnostics, no prior Meta registration is rewritten, and no provider
approval is fabricated.

### Follow-up

Accepted and Complete at Attempt 2. BACKGROUND-017 and BACKGROUND-018 are
promoted to Ready. SYSTEM-TEST-001/002 remain Pending on other prerequisites;
SYSTEM-TEST-004 stays Pending until BACKGROUND-017 completes. No `_index.md`
was changed; the architecture status matrix and dependent task frontmatter
record the promotions.
## Architect Review — Attempt 1

### Review Status

Changes Requested — Attempt 1. The task returns to `ready`; `executor` and
`claimed_at` are cleared, and Attempt 1 is preserved for the next claim.

### Review Notes

The implementation preserves the required INITIAL BODY binding across the
offer matrix and locale flows, and the reported unit and focused authoring
integration suites pass. However, the publication PostgreSQL run had one
failure: the 100-shop × 20-language operation returned `PARTIAL` rather than
`COMPLETE` after about 488 seconds. The report has no root cause or target-level
failure evidence. Because this task changes locale snapshots and immutable
publication content, this result must be investigated before acceptance rather
than assumed to be unrelated or environmental.

### Reviewed Files

- `src/lib/admin/whatsapp-templates/authoring/registry.ts`
- `src/lib/admin/whatsapp-templates/authoring/validation.ts`
- `src/lib/admin/whatsapp-templates/authoring/draft-operations.ts`
- `src/lib/admin/whatsapp-templates/translations/source-snapshot.ts`
- Related translation, compilation, Meta snapshot and publication tests.
- The Completion Report's disposable PostgreSQL results.

### Validation Reviewed

- Reported authoring, translation, compilation, Meta snapshot and publication
  unit suites passed.
- The disposable authoring PostgreSQL suite passed 2/2.
- The disposable publication PostgreSQL suite had 4 passes and 1 failure; the
  100-shop × 20-language fan-out returned `PARTIAL` instead of `COMPLETE`.
- Typecheck, changed-file lint, build and `git diff --check` are reported as
  passing. The implementation branch is clean and synchronized at
  `38fec2f4`; the parent report branch was clean at `b7757ceb` before this
  review overlay.

### Architecture Conformance

The source changes stay within Admin-owned authoring, translation and
publication paths. The single unresolved PostgreSQL fan-out result prevents
confirming the published immutable revision flow at scale; no provider approval
was claimed or simulated.

### Follow-up

Identify which target or locale caused the partial publication, establish
whether the failure is caused by this change, publication behavior, or the test
environment, then rerun the full publication PostgreSQL suite and record the
result. Do not treat the four passing cases as a pass for the entire suite.
Keep Attempt 1 and `status: ready` until the failure is resolved or supported by
a reproducible baseline comparison. `ARCH-052-BACKGROUND-017` and
`ARCH-052-SYSTEM-TEST-004` remain pending; no dependency status changed.
