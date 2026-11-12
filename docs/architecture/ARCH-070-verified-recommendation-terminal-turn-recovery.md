---
id: ARCH-070
title: Verified recommendation evidence and terminal turn recovery
status: implemented
coordinator: moda_architect
created: 2026-11-12
updated: 2026-11-12
---

# ARCH-070: Verified recommendation evidence and terminal turn recovery

## Status

Implemented. All eleven tasks are architect-accepted Complete. Final Shared and Background changes are merged and deployed. A genuine production recommendation response included a trusted recovery footer, was accepted by Meta, delivered and read. Public evidence is deliberately limited to coarse outcomes and source/release identities; detailed operational correlation remains outside source control.

## Problem

Valid catalogue products without storefront URLs were rejected during recommendation refresh. Nonretryable answer failures were repeatedly resurrected by pending-turn repair, and eligible AI recovery replies lacked a guaranteed checkout footer. Subsequent validation identified semantic selection/provider-schema gaps and a strict referralReason envelope failure.

## Goals and Non-Goals

Accept verified linkless PRODUCT_ONLY recommendations, durably finish terminal failures for the same inbound version, guarantee a trusted footer for eligible AI recovery replies, and align semantic selection/shipping evidence and provider guidance within existing bounded execution.

No automatic product selection, inferred identifiers/version fields, invalid-value coercion, additional repair loop, model/provider switching, consent/STOP change, schema migration, infrastructure change or processed-message replay is introduced.

## Architecture and Contracts

Shared owns canonical semantic normalization, shipping-result qualification, finalResponse provider schema, strict validation and existing bounded runner repair. Background imports these published mechanics and retains tenant authorization, observations, fresh verification, budgets, ownership, composition and delivery. Final Background pins `@modainteract/moda-interact-shared@5.13.5` through existing public commerce/model/presentation exports.

Null product URLs are allowed only for PRODUCT_ONLY presentation. Basket actions retain required safe verified URLs. Nonnull domain/URL checks and missing, unavailable, malformed or mismatched product/variant rejection remain enforced. No link is fabricated.

The canonical semantic parser preserves valid independent dispositions and legitimate policy selections without changing structural optional-field schemas. Canonical pinned recommendation contracts require a valid version/list pair; custom pinned contracts retain supported-field behavior. Shipping alternatives after product observations require matching authorized current-turn evidence, followed by existing budgeted fresh provider/identity verification. Truthy placeholders or mismatched limitations cannot bypass product-selection requirements. Matched unavailable-policy limitations remain supported.

Provider referralReason declares explicit nullable-string type and the unchanged allowed enum. ANSWER requires actual JSON null; REFER_TO_STORE requires an allowed reason. Common guidance covers both existing forced correction paths. Strict validation, mandatory referral and step/deadline/token/correction limits remain unchanged.

## Request / Event Flow

Authenticated inbound -> durable conversation version -> current-turn model/tools -> strict semantic/final validation and existing bounded correction -> fresh product/shipping verification -> eligible trusted footer -> media/length/provenance and final moderation/control gates -> Meta delivery -> durable status.

## Repository Responsibilities

Shared owns and publishes reusable parser/qualifier/schema mechanics. Background's former local parser delegates to the published implementation and retains domain/tenant/evidence policy. The coordinating developer owns final merges, runtime rollout and genuine production verification. No duplicate generic logger or telemetry mechanism was added.

## Data Model, Consistency and Ordering

No migration, queue payload or uniqueness contract changed. Typed nonretryable failures before provider send complete only the owned inbound version after confirmed reservation cleanup. Existing version/control-revision CAS protects newer input and takeover changes. Unknown/retryable failures, cleanup/commit failures and uncertain provider sends remain recoverable. Repair SQL and crash/transient recovery remain intact.

## Recovery Footer and Security

Existing recovery context checks tenant/customer, status/lifetime and trusted HTTPS shop domain. Eligible AI replies receive that context's checkout URL before final limits, media planning and delivery hashes. Standalone raw trusted links are canonicalized at the end while authored labels and embedded Markdown/prose are preserved. Plain, details, recommendation, wrapped/unwrapped and image-caption paths are covered; long captions fall back to complete text. Trusted augmentation is bound into provenance. Previously prepared applications replay immutably.

Human/manual and STOP/consent/security/blocked flows are outside this augmentation. No new consent grant or purchase action is inferred. Recovery URLs, recipient details, private prompts, raw payloads and operational/customer/provider identifiers are excluded from committed evidence.

## Failure Handling and Scalability

Terminal failures no longer amplify model/tool work for the same inbound version. Newer input remains eligible. Selection/envelope correction uses only the existing bounded mechanism; exhaustion fails closed. No additional hot-path database/provider reads or broad serialization were introduced. No increased capacity claim is made.

## Observability and Infrastructure Assessment

Existing shared structured logs correlate model, turn, composition and provider outcomes. New selection-shape diagnostics use bounded enums, booleans and capped counts, without arbitrary coercion or model prose. No new logging transport, generic telemetry, Gateway task, environment variable or topology change is required. Production observations remain distinct from local fixtures and synthetic probes.

## Rollout / Migration

PRODUCTION / COMPATIBLE ROLLOUT: accepted Shared implementation -> exact immutable public release/download verification -> accepted consumer -> developer merge/deploy -> genuine production verification. No queue drain or database migration. Rollback changes code/package revisions without rewriting processed input or delivered messages.

Final Shared merge is `596eaa455f9b6eb72f316c76c1c7a4657faa1f60` (PR79). Final Background merge is `bada81e6a1a74add0c124de6c60eb72114c04e46` (PR204), retaining earlier accepted fixes. Developer updated final parent gitlinks in `a7e7a3c59`; unrelated workspace changes were excluded.

The accepted public 5.13.5 artifact was published once after explicit user permission. Canonical metadata and actual downloaded bytes matched SHA256 `71118ab02b14ffb36659a8cc6ba5caa91055bb8f3da48a23b3c731c7366ba6ed`. Publication reused the validated artifact without rebuilding or repeating implementation checks. Earlier approval rejection caused no publication and was resolved through explicit approval and canonical task resumption.

## Decisions / Tasks

| Task | Owner | Status | Dependencies |
|---|---|---|---|
| ARCH-070-SHARED-001 | moda_shared | Complete | None |
| ARCH-070-SHARED-002 | moda_shared | Complete | ARCH-070-SHARED-001 |
| ARCH-070-BACKGROUND-001 | moda_background | Complete | ARCH-070-SHARED-002 |
| ARCH-070-BACKGROUND-002 | moda_background | Complete | None |
| ARCH-070-BACKGROUND-003 | moda_background | Complete | None |
| ARCH-070-SHARED-003 | moda_shared | Complete | ARCH-070-SHARED-002 |
| ARCH-070-SHARED-004 | moda_shared | Complete | ARCH-070-SHARED-003 |
| ARCH-070-BACKGROUND-004 | moda_background | Complete | ARCH-070-SHARED-004 |
| ARCH-070-SHARED-005 | moda_shared | Complete | ARCH-070-SHARED-004 |
| ARCH-070-SHARED-006 | moda_shared | Complete | ARCH-070-SHARED-005 |
| ARCH-070-BACKGROUND-005 | moda_background | Complete | ARCH-070-SHARED-006 |

## Validation

Task reports retain exact commands, reviewed heads and launcher isolation/synchronization evidence. Final Shared checks passed 112 focused tests, 743 full tests with three expected integration skips, types, ESM/declarations build and installed immutable public exports. A coordinator-run real-provider probe used wholly synthetic context/products and the final built client/correction nodes; strict JSON-null ANSWER and exact synthetic selections passed without customer context, commerce reads, DB writes or Meta sends.

Final Background passed 113 host and 211 footer/control/dependency tests, types/scoped lint and both exact-head full CI runs (3985 tests across 368 files). Earlier disposable PostgreSQL/Redis proofs covered terminal completion, repeated repair, newer inbound and trusted wrapper context. Four untouched pre-existing full-lint unused declarations remain documented; no unrelated cleanup or full-lint success is claimed.

No separate system-test task is applicable to this bounded correction. Deterministic published-package/host/wrapper checks, disposable lifecycle proofs, synthetic provider conformance and genuine production verification cover the affected boundaries; no unrun terminal task is implied.

## Integrated Production Verification

The coordinator confirmed the final source revision Live and the prior worker drained before requesting a genuinely new customer test. The new request exercised one bounded selection correction and completed ANSWER. Three selected products passed fresh verification and composition was ready. The outbound catalogue prose referenced five items; the evidence establishes three freshly verified selected recommendations.

The actual delivered body ended with the exact active trusted recovery URL. Meta returned HTTP200/HTTP_ACCEPTED; durable status progressed to delivered and read. The turn completed on its first job attempt, processed version caught up, pending/processing state cleared, and the historical failure count did not increase. No spoofed input, manual queue/database mutation or processed-version replay was used.

The trusted link was also checked read-only without submitting an order. The development store redirects unauthenticated access to its existing password page. Footer/link identity and delivery are verified; direct unauthenticated checkout access and payment completion were not validated. No store password was disabled or changed.

## Evidence Limits and Open Questions

None blocking. Earlier exact raw model values remain unknown; deterministic semantic gaps were reproduced independently, and later strict referral validation failure was observed without inferring its raw value. Synthetic conformance is not represented as production proof. Successful genuine recommendation/footer delivery and read receipt close this architecture's acceptance gate; the existing development-store password gate remains a transparent access limitation.

## Change History

- 2026-11-12: Defined bounded catalogue evidence, terminal recovery and eligible AI footer tasks.
- 2026-11-12: Added canonical semantic/shipping qualification and strict referral provider guidance through separately accepted releases/consumers.
- 2026-11-12: All eleven tasks accepted; final genuine production recommendation/footer delivery and read receipt verified. Architecture marked Implemented with redacted public evidence and password-gate qualification.
