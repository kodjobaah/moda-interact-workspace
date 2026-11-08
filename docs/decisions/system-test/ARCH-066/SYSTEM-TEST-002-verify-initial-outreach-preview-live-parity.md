---
id: ARCH-066-SYSTEM-TEST-002
architecture_id: ARCH-066
title: Verify checkout outreach preview and Background parity
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-066-COMMERCE-002", "ARCH-066-BACKGROUND-002"]
enables: []
created: 2026-11-08
updated: 2026-11-08
---
# Verify checkout outreach preview and Background parity

## Scope and exact work
Read ARCH-066 and its two sequence diagrams. This task is definition only; implement only after dependencies complete, in canonical task worktrees. You are not alone in the codebase; preserve unrelated edits. No merchandise-specific assumptions or new per-category schema.

Own system-test only. NEW `src/scenarios/arch066-initial-outreach-preview.js`, deterministic fixture files, existing scenario registration, provider harness and WhatsApp emulator.

For Shopify and WooCommerce seed checkout lines with native parent/variant IDs, historical prices and quantities; provider fixture returns changed current prices/details. Run actual Studio route and Background host with identical pinned profile/policy/model-decision/template/locale/clock inputs. Compare selected checkout IDs, fresh observations, reconciliation, offer selection, complete template parameters/header reference and rendered initial text. Assert provider exact reads for every distinct line identity including NONE policy. Do not call live merchants in deterministic suite; separately record optional Render TEST smoke as live verification.

Matrix: clothing, nail varnish, trees and unseen attribute; duplicate lines; deleted/foreign/wrong-parent IDs; 0/101 lines; invalid currency/quantity; price changes; eligible/ineligible/expired/no offer; fingerprint changes; missing locale/template/header parameter; denied role; cancellation/replay/purge; provider outage. No unrelated product search allowed. Studio must create no recovery/attempt/credit/customer/outbox/send/Meta mutation; Background sends only through emulator using existing gates. Compare production send-admission assertions separately from pure rendering parity. Existing conversational and initial-outreach regression scenarios remain passing.

Record pinned commits/package integrity, fixture hashes, commands, run IDs and exact comparison artifacts. Disposable integration run required; unit tests alone do not complete task.

## Completion report
Not started. Record implementation commit, scoped checks and parity evidence before completion. No production deployment or real message sending authorized.

## Review corrections
Use the normative outreach contract and new SHARED-005 exact artifact. Assert ordered initial/revalidation product calls (NONE exactly two per distinct pair), zero model/offer calls for NONE, checkout-only rejection of alternative-product promotion, changed-fact refusal and READY-media/TEXT fallback parity. Exercise actual app/api/studio/preview/initial-outreach routes including list, start, status and cancel, status codes and tenant ownership. Fixture model responses and observed clock fixed; no stochastic wording comparisons. Preserve production admission regression tests separately.

## Deterministic implementation checklist
- [ ] Register arch066-initial-outreach-preview in existing scenario catalogue and package script test:arch066:outreach using existing harness. Pin Shared005/database/Background/Commerce commits and record commands.
- [ ] Run all contract7 cases through both platform fixtures and actual Studio routes/Background host. NONE ready call trace exactly two get_product per distinct pair, checkout duplicate quantities unchanged, zero model/offer/search. FIXED/AI scripted offer decisions use bounded ports; current-facts change refuses before rendered ready.
- [ ] Seed ready R2 IMAGE projection, missing IMAGE with approved TEXT fallback, and missing both assignments; compare provenance/full params/header/body with Background same explicit inputs. No media generation or Meta requests from Studio.
- [ ] Persist machine-readable PASS/FAIL artifacts and exact text/parameter equality; tests assert zero forbidden writes and actual emulator delivery fences. Required skipped scenario blocks completion; screenshots/unit-only evidence insufficient.
