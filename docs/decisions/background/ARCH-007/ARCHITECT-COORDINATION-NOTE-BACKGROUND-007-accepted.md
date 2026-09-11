# ARCH-007 BACKGROUND-007 acceptance coordination note

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

`ARCH-007-BACKGROUND-007` Attempt 3 is architect-accepted Complete on 2026-09-08.

Current Background consequences:

- BACKGROUND-005 remains Ready.
- BACKGROUND-009 remains Pending until DATABASE-005 and SHARED-006 are Complete.
- BACKGROUND-008 remains Pending and now explicitly depends on BACKGROUND-009 as well as BACKGROUND-005, BACKGROUND-007 and SHOPIFY-001.
- BACKGROUND-008 must wire the accepted BACKGROUND-009 recovery-credit purchase activation reconciliation path into its recurring billing worker scan.

The selective Background archive does not include the current canonical parent ARCH-007 or Admin domain task files. On the next full-workspace reconciliation, update the parent task table/frontier and check whether any Admin task whose final dependency was BACKGROUND-007 can now become Ready.

This note is coordination state, not a replacement for canonical ARCH-007.
