---
id: ARCH-057
title: Shopify application database correctness and simplicity
status: proposed
coordinator: moda_architect
created: 2026-11-04
updated: 2026-11-04
---

# ARCH-057: Shopify application database correctness and simplicity

## Status and scope

Definition revision 2: **twelve Shopify tasks and one terminal system-test task, defined but not materialised**. This package contains architect-owned task/decision documents only. It makes no implementation, acceptance, worktree, branch, commit, deployment or production-performance claim.

The user requested tasks grouped by touchpoints, simplicity with functional correctness, original server error messages for pre-production diagnosis, and descriptive runtime names rather than architecture IDs. Each functional owner implements/tests its own error handling. SHOPIFY-011 closes remaining server diagnostic gaps; SHOPIFY-012 replaces the three architecture-derived Shopify billing namespaces with descriptive canonical names under the user-confirmed development-only baseline; no preservation of old identities is required.

The latest baseline is `moda-interact-workspace(20261104-005051).zip`, SHA-256 `a2c582c7aecb087b5c997d953bb1ab398f4e0d90d4fa79d555f8dd267b7233ee`. [Snapshot reconciliation](ARCH-057/snapshot-reconciliation.md) confirms no Shopify, Shared, canonical/nested Database or Background implementation change from the reviewed archive. The new ARCH-056 tasks retain their own API/Background ownership. ARCH-057 is unused in the latest supplied archive; live materialisation must reject a conflicting allocation rather than overwrite it.

The existing [Shopify assessment](reviews/shopify-database-20261103-235702-r01/review.md) and its evidence are already in this snapshot. This patch does not replace them or require another prior patch. [Finding disposition](ARCH-057/finding-task-map.md) accounts for every finding, including preserved/deferred policy.

## Problem

Merchant page composition independently resolves the same shop and reads overlapping subscription/settings/billing inputs. Support acknowledgements multiply whole authenticated requests. Purchase history repeats current-provider checks per row. Some no-op saves still write, and knowledge refreshes can duplicate framework revalidation.

Correctness defects also exist at specific boundaries: the initial paid lock names an absent relation; malformed provider evidence can become no-contract; refund admission performs network/root reads while a transaction is open; duplicate uninstall cleanup can delete reinstall credentials; repository webhook declarations drift from implemented handlers.

Several server failures lose their original message/cause or become an unrelated reason code. Naming includes explanatory task labels and three legacy hash-domain values whose persisted identity must be treated separately.

## Selected architecture

### 1. One request owns merchant read composition

Use the already enabled React Router context/middleware facility. SHOPIFY-001 owns one authenticated context and lazy scalar subscription/settings reads per GET/HEAD request. The parent page middleware and authentication entry explicitly own remote profile refresh. Established standalone resources and mutations resolve current local tenant state without routine profile GraphQL. Missing prerequisite rows retain the existing authenticated bootstrap/repair contract.

Authentication, SDK Responses/headers and independent capability checks remain. Non-GET actions do not reuse a GET data cache; post-action loaders see committed state. No cross-request cache, TTL, profile scheduler, new webhook, generic repository or hosted API is added. Domain task owners compose their readers using the fixed context API. Cached rows never replace locked mutation admission.

### 2. Billing owns evidence and transaction admission

SHOPIFY-002 uses `commerce.Shop → shopify.ShopSettings → billing.Subscription` as the relevant lifecycle order, consistent with inspected Background activation/reinstall writers. It distinguishes explicit provider absence from malformed evidence, preserves onboarding milestone/category ordering and removes only the confirmed duplicate operation/period writes.

SHOPIFY-003 owns purchase/refund/history work in the credit service touchpoint. Display eligibility shares one provider context and bounds refund summaries. A refund obtains provider evidence before the transaction, then revalidates local ownership/identity/cycle/amount under its transaction. Existing new-purchase lifecycle revalidation and receipt replay remain authoritative. No external provider work inside the refund transaction is selected.

SHOPIFY-004 composes commercial reads from existing scalar state and distinct related data. It removes unconsumed aggregate work, shares identical catalogue/context reads, bounds translated promotion results correctly and combines usage count/sum. Different balance types, provider/live plan disagreement and history semantics remain explicit.

### 3. Merchant areas own their read/write improvements

SHOPIFY-005 owns support badge/list/compose/visible-ID acknowledgement behaviour. It batches a maximum of fifty rendered message IDs, preserves first-read time and valid already-read success, and uses tenant/visibility predicates.

SHOPIFY-006 owns recovery page composition/resources and the small reuse of already locked Shop status in command admission. It preserves standalone ownership, pagination purpose, revision/idempotency/current send checks and the internal follow-up claim identity already accepted elsewhere.

SHOPIFY-007 owns settings/category access and policy writes. Read context is shared; unchanged discount policy performs no selection writes; category mutation requires ACTIVE under the existing Shop row lock. This does not move onboarding completion after category activation.

SHOPIFY-008 owns knowledge sources/uploads/order/refresh. It consumes the settings guard/read contract, removes unused reads and identical-order writes, retains source/asset/revision/entitlement boundaries, differentiates dependency failure from denial/absence, removes redundant fetcher-success revalidation and proves stable polling with the installed router. Dormant sources and plain-fetch upload refresh remain usable.

### 4. Lifecycle cleanup and ingress stay separate touchpoints

SHOPIFY-009 owns the existing uninstall transition, session cleanup, reinstall admission and intended named webhook configuration. Session deletion belongs to the same successful guarded transition; duplicates do not delete replacement sessions. Reinstall marker/schedule creation requires a usable durable offline session under the existing Shop lock. If SDK-authenticated context outlives a deleted session, route back through authentication without persisting false reinstall progress. No SDK storage wrapper or new uninstall identity is selected.

SHOPIFY-010 owns generic ingress and queue publication. Preserve the one-read tenant/lifecycle admission for supported events, narrow its projection, classify unsupported topics before lookup, and use deterministic queue identity with one bounded publication deadline. Keep existing consumer payloads, replay/terminal safeguards and direct BullMQ acceptance. Do not add an ingress outbox, durable quarantine or general cache.

### 5. Server diagnostics are part of each outcome

[The mandatory task contract](ARCH-057/task-contract.md) requires actual original safe message/cause/code/provider evidence, truthful origin and correlation through `@modainteract/moda-interact-shared/logging`. Internal codes supplement original errors. Caught fallback, typed unavailable result, postcommit enqueue and emitter failures retain an owner.

Every affected task tests emitted Shared JSON with a distinct harmless original error marker and sensitive sentinels. Shared sink failure must not alter business behaviour. Current Shared Error serialization only supplies name/message, so source adapters explicitly include available safe cause/code fields. No replacement logging kernel or raw response/request dump is authorised.

SHOPIFY-011 audits final server catch/error-event/uncaught paths and closes entry/bootstrap/configuration/health/pending-work gaps. Expected validation/redirects remain normal control flow. The resulting coverage register distinguishes logged, propagated, expected and logging-internal isolation paths.

### 6. Runtime naming follows the domain

New runtime files, symbols, events, environment/queue/route names describe their behaviour. Task/architecture IDs remain valid in documents, tests and test-catalogue traceability. SHOPIFY-012 removes explanatory task labels from current production comments and adds a deterministic naming gate.

The user confirmed on 4 November 2026 that the application has not gone live and existing development identities do not need preservation. SHOPIFY-012 therefore directly replaces all three `arch027` namespaces with `shopify-billing-operation-key-v1`, `shopify-billing-recurring-v1` and `shopify-billing-topup-v1`. There is no runtime exception, legacy lookup, dual format, backfill or migration. Fresh fixtures prove fixed vectors and ordinary same-format replay/conflict behaviour under the new canonical names. Existing development billing records can be discarded/reseeded through the existing development workflow; no automatic application-startup reset is introduced.

The change is confined to Shopify-owned builders. API's similarly spelled namespaces belong to guarded WooCommerce command paths and already use different recurring fingerprint framing; they are not a shared Shopify digest contract. This package does not claim a workspace-wide runtime naming cleanup.

## Current review handoff

On 2026-11-04, ARCH-057-SHOPIFY-002 Attempt 3 was accepted and marked complete with its claim cleared. All three prior findings are resolved. Independent validation passed 395 unit tests, the isolated 2-test PostgreSQL suite, typecheck, build and changed-file lint. The review preserves an initial milestone-transaction timeout and teardown error before the unchanged isolated rerun passed; its root cause is not claimed as proven. SHOPIFY-003 is ready and unclaimed; SHOPIFY-004 and SHOPIFY-011 remain pending on additional prerequisites. See the [task review](../decisions/shopify/ARCH-057/SHOPIFY-002-stabilise-subscription-activation-and-provider-evidence.md#architect-review) for evidence and historical findings. The table below records initial task states, not current lifecycle status.

## Task map

| Task | Touchpoint | Initial state | Prerequisite |
|---|---|---|---|
| ARCH-057-SHOPIFY-001 | Authenticated merchant request context | Ready | None |
| ARCH-057-SHOPIFY-002 | Subscription activation and provider evidence | Pending | 001 |
| ARCH-057-SHOPIFY-003 | Credit purchases, refund admission and history | Pending | 002 |
| ARCH-057-SHOPIFY-004 | Billing, promotions and usage read composition | Pending | 001, 002, 003 |
| ARCH-057-SHOPIFY-005 | Support inbox, badge and acknowledgements | Pending | 001 |
| ARCH-057-SHOPIFY-006 | Recovery readers and command context | Pending | 001 |
| ARCH-057-SHOPIFY-007 | Merchant settings/category policy | Pending | 001 |
| ARCH-057-SHOPIFY-008 | Knowledge lifecycle and UI refresh | Pending | 001, 007 |
| ARCH-057-SHOPIFY-009 | Uninstall/reinstall and webhook configuration | Pending | 001 |
| ARCH-057-SHOPIFY-010 | Ingress and queue publication | Pending | 009 |
| ARCH-057-SHOPIFY-011 | Remaining server diagnostic coverage | Pending | 001–010 |
| ARCH-057-SHOPIFY-012 | Domain naming and canonical development billing identities | Pending | 011 |
| ARCH-057-SYSTEM-TEST-001 | Integrated verification through existing runner | Pending | 012, transitively all functional tasks |

Numeric prerequisites in this display are shorthand only; canonical task frontmatter and references use fully qualified IDs. See [execution plan](ARCH-057/execution-plan.md) and [task manifest](ARCH-057/task-manifest.json) for exact paths and order.

No Database, Shared, API or Background implementation task is created. The selected fixes use existing persisted contracts. A real need to change a schema or cross-repository contract is a stop-and-amend boundary, not permission to edit a nested copy.

## Preservation and deferred decisions

- Keep tenant isolation, independent resource access, action origin protection, FROZEN/support-only/reinstall policy and current merchant UI/locales.
- Keep transaction-bound current eligibility, accounting CAS, bounded retries, accepted no-op/idempotency and source/claim/provider identities.
- Preserve intentional new-purchase provider observations and current mutation-time verification; display reuse does not authorize future writes.
- Preserve recovery snapshot/keyset/index designs, knowledge durable revisions, bounded queue hints and existing postcommit repair.
- Keep accepted ARCH-017/023 onboarding/category milestone separation and ARCH-055 internal follow-up claim semantics.
- Preserve ARCH-056 payloads, producer/consumer ownership, final admission and accounting policy. Current implementation bytes show no new required Shopify consumer change.

Privacy export/redaction/Shop-retention work in F17 needs explicit cross-repository fulfilment, erasure, retention and rehydration ownership. It remains a visible open functional gap, not an implicitly completed part of query cleanup. No blanket CASCADE or revival of superseded ARCH-045 tasks is authorised. Subscription-ended notification remains best-effort with corrected diagnostics; durable delivery needs a separate approved contract. The ACK/discard outcome for inactive/unknown webhook shops is not silently converted to durable quarantine.

## Validation contract

Task-specific tests exercise the installed code and canonical migrations. Real PostgreSQL 17 + pgvector and independent connections/barriers prove locking, concurrency and rollback; real disposable Redis proves selected queue behaviour. Actual pinned-router tests prove context and refresh lifetimes. Provider observations use controlled synthetic boundaries and are labelled accordingly.

Record before/after method calls, SQL/transaction control, affected rows, provider calls and outcomes on the same fixtures. Query inventories and mocks are not measured SQL/concurrency evidence. No workload/latency claim is derived from a small sample, and 20,000 inbound events/min is not certified.

The terminal task extends the existing system-test runner with domain-named selectors/executors, captures actual application logs and package/source provenance, and labels CONTRACT, INTEGRATION and BLACK_BOX evidence truthfully. It does not duplicate application policy or create another runner. New test code stays modular and below 300 lines per file.

## Definition acceptance versus implementation acceptance

Definition validation checks canonical sections/YAML, unique IDs, dependencies, path ownership, findings coverage, latest-source alignment and patch applicability. Runtime validation remains unchecked until an implementation agent executes and the architect reviews it.

This package adds only new ARCH-057-owned files. Every `_index.md`, earlier task/architecture, source file, migration and submodule pointer is unchanged. The developer applies/reviews the definition patch, then the normal launcher materialises matching task branches/worktrees. Parent-definition publication is not a claim that implementation has started.
