---
id: ARCH-067-SHARED-002
architecture_id: ARCH-067
title: Publish the accepted shared correction
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-067-SHARED-001"]
enables: ["ARCH-067-COMMERCE-001", "ARCH-067-MCP-001", "ARCH-067-BACKGROUND-001"]
created: 2026-11-09
updated: 2026-11-09
---
# Publish the accepted shared correction

## Objective and binding specification
Implement the owned portion of [ARCH-067](../../../architecture/ARCH-067-product-reference-and-current-stock-parity.md). Every schema, mapping, persistence, rendering, diagnostic and compatibility rule there is normative. No merchandise-specific behavior. Dependencies must be complete before execution.

## Exact work and touch points
Own package.json/package-lock.json and publication receipt only. Reuse accepted SHARED-001 build; inspect registry, select the next unused compatible version, record it explicitly, publish the exact reviewed archive and verify downloaded integrity/runtime/types. Record exact version, sha512 integrity, archive sha256, source SHA and imports for all three consumers. Do not rebuild different source or edit functional code. Consumer tasks remain pending until artifact verification and task completion.

## Exact public artifact checks
This is publication-only: no additional Zod schemas may be designed here. The authoritative schema definitions and exact signatures are in SHARED-001, section “Exact Zod additions and public API”. The downloaded installed package must export these runtime values through `/commerce`: CommerceProductStockSchema, normalizeCommerceStockQuantity, CommerceProductReferencePairSchema, CommerceConversationProductReferenceSchema, CommerceProductPresentationSchema, CommerceConversationProductContextSchema, recordCommerceProductPresentation, CommerceProductFactSchema, verifyCommerceProductFacts, renderCommerceProductFacts. Verify declaration imports for CommerceProductStock, CommerceProductReferencePair, CommerceProductPresentation, CommerceConversationProductContext and CommerceProductFact.

The archive smoke parses KNOWN quantity0 with scopeVARIANT, rejects KNOWN quantity-1 and NOT_TRACKED with quantity, parses legacy context without presentation/selectedOptions, and records ordered native Woo pairs20,3 without reordering. It verifies an omitted legacy stock becomes UNAVAILABLE in verified facts. Use fixed clock and literal fixtures; no provider/model/database calls or source imports. Record exact package version and integrity in Completion Report for all three consumer tasks. Do not publish if any named export is absent or schemas differ from the accepted SHARED-001 archive.

## Acceptance criteria
Release mechanics only: prerequisite implementation Complete/Accepted; exact accepted source/dist reused; versionmetadata-only diff; publication succeeds; exact registry archive downloadable with matching integrity/SHA256 and installed publicruntime/declarations includingstock/reference/canonicalpurposecompiler exports. No implementation tests, lint, typecheck or productionbuild revalidation. Report a source defect to architect rather than fix it here.

## Non-goals
No inventory mutation, new database table, token-refresh redesign, new template approval/WABA validation, category sequencing redesign or budget increase.

## Completion Report
Status: Not started.
Implementation SHA: Pending.
Validation: Pending.
Deployment/compatibility evidence: Pending.

## Architect Review
Status: Not reviewed.


## Architect publication readiness — 2026-11-09
SHARED001explicitlyCompleteAcceptedAttempt1, source467cc1abf5afc467f73861f9830430524022bacd/review77917fb2d69a3efbd47cf99b26db4991f766bf35 cleanpublished. Ready unchangedAttempt0/unclaimed. Metadata task_kind corrected topublication to match original exactrelease-onlyscope; generic regressionboilerplate above replaced withrelease-specificchecks, no scopeexpansion. Reuse finalvalidated /private/tmp/arch067-shared001-validated-5.10.0.tgz SHA25644a81c0468a0a6dd62c0df75a12fa5877038028435f897057874c0478eb138a8 and canonicaldist; thisunpublishedbuildmetadata versiondoesnotauthorizeoverwritingpublic5.10.0. Inspectallpublishedversions, select/recordunusedcompatiblerelease beforepublishing, no range/latestguess. Onlypackage/lockversionmetadata andpublicationreceipt; no rebuild/test/lint/typecheck, consumers or gateenablement. Ifacceptedsource/dist unavailable or differs, returnconcreteartifactgap.
Allconsumers remainPendinguntilthispublicationactuallyComplete, notjustAcceptedreview. Reader-firststockdeployment and COMMERCE_PRODUCT_REFERENCE_V2_WRITE_ENABLED defaultfalseuntilbothreaders remainmandatory; no deployment happenshere.
