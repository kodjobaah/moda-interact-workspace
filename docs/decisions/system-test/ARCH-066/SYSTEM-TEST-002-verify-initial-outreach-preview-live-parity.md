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
