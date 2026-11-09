---
id: ARCH-067-SHARED-002
architecture_id: ARCH-067
title: Publish the accepted shared correction
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-067-SHARED-001"]
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
All owned requirements above and architecture contract are implemented and verified. List every actual changed path and test result. Shared behavior must be imported through published public exports; no copied cross-repository source. Unknown inventory remains distinct from zero. Existing authorization, checkout ownership, WhatsApp composition and replay rules pass regression checks. No unresolved design choices may be silently substituted; report a concrete contract conflict before implementing an alternative.

## Non-goals
No inventory mutation, new database table, token-refresh redesign, new template approval/WABA validation, category sequencing redesign or budget increase.

## Completion Report
Status: Not started.
Implementation SHA: Pending.
Validation: Pending.
Deployment/compatibility evidence: Pending.

## Architect Review
Status: Not reviewed.
