# Architecture reconciliation and production readiness — 5 November 2026

## Decision

Ready to begin production preparation; production launch is not yet substantiated. Completed implementation records are substantial, but required runtime certifications, deployment ownership and unresolved accounting/cutover decisions remain. A limited Shopify pilot and a Shopify-plus-Woo launch require different release scope; do not treat every open formatting or optional Studio task as a launch blocker.

## Evidence and limits

Audited every canonical task file in docs/decisions: **1285 unique task IDs**, across **56 initiatives**. Status counts: blocked: 4, complete: 1006, pending: 57, ready: 76, review: 5, superseded: 137.

System-test records: blocked: 2, complete: 7, pending: 42, ready: 42, superseded: 6. These are recorded lifecycle states, not independently rerun results.

Read all task frontmatter and dependency lists. Read selected open task contracts and earlier reconciliation reports. Direct implementation/configuration inspection in this pass is limited to two Gateway Blueprint files (render.production.yaml and render.test.yaml), at Gateway HEAD ac092dc783d715db3b0e2136bce1cc51abaee5a1. No application source diff was independently accepted, no tests/build/load tests were run, no hosted deployment or registry was checked, and no remote refs were refreshed. Historical Complete records retain their authority; this audit does not re-certify all accepted implementations or their physical worktrees. Parent snapshot: 69ff2a6e3e1e6f49e97f32c1f5cfe085470d475a. Existing unrelated working changes were preserved.

## Prioritized production gates

1. **Release scope and billing safety.** Resolve ARCH-028-BACKGROUND-013: durable dispatch admission occurs before provider HTTP, so billing uncertain outcomes requires an explicit policy decision. ARCH-011 upgrades are wholly unimplemented. Either complete that initiative or explicitly exclude upgrades and prove the shipped UI/runtime cannot invoke them. Review pending billing/refund operations under ARCH-007/009/010/027 against the selected launch scope.
2. **Production infrastructure.** ARCH-002-GATEWAY-013 explicitly requires production-safe environment-group ownership. ARCH-052-GATEWAY-001 private provider connectivity and ARCH-027-GATEWAY-001 Woo billing ingress remain Ready. ARCH-032-GATEWAY-002 is deliberately held for separately approved endpoint cutover; do not execute it from this audit. Existing split test/production Blueprints require a documented exception to the generic render.yaml convention; filename absence alone is not missing infrastructure. Test and production configuration already declare distinct environment identities and secret placeholders.
3. **Integrated certification.** Finish in-scope terminal scenarios for subscription/entitlement/refunds, tenant/security isolation, consent and STOP, delivery compensation, recovery lifecycle, human handover, templates and observability. System tests remain manually invoked after developer validation. Woo launch additionally needs ARCH-046/048/053 real checkout/consent/restore evidence and Marketplace sandbox billing certification.
4. **Capacity proof.** ARCH-002-SYSTEM-TEST-008 is unexecuted. Its target is 22,000 Shopify webhook requests/minute; the architectural reference is roughly 20,000 inbound events/minute. Neither is measured capacity in this audit. Prove acknowledgement latency, queue lag/drain, early filtering cost, PostgreSQL/Redis headroom and hot-tenant behavior separately from messaging/LLM capacity.
5. **Operational release evidence.** Assemble versioned deployment inputs, forward migration order, backup/restore rehearsal, rollback constraints, environment/credential ownership, alert delivery and incident/on-call responsibility for the actual release. Existing architecture/task evidence must be checked before defining any new work.

## Dependency reconciliation

No duplicate canonical IDs and no missing dependency IDs after accepting valid whitespace around YAML delimiters. No non-system-test YAML task depends on a system-test task. The initial strict delimiter scan omitted ARCH-010-SHOPIFY-002; it exists and is Complete at Attempt 8.

The following Ready task is not executable under its explicit prerequisites; apply the correction on its matching parent task branch, with its index and architecture plan, before handoff:

- ARCH-009-ADMIN-002: Ready → Pending; unmet: ARCH-009-ADMIN-001.

Pending records with all YAML prerequisites Complete are listed below. This is a dependency-ready candidate list, not approval to override explicit holds or start system tests. Their individual contracts must control promotion:

- ARCH-046-SYSTEM-TEST-001
- ARCH-048-SYSTEM-TEST-001
- ARCH-015-SYSTEM-TEST-001
- ARCH-014-SYSTEM-TEST-003
- ARCH-007-SYSTEM-TEST-005
- ARCH-007-SYSTEM-TEST-004
- ARCH-053-SYSTEM-TEST-001
- ARCH-053-SYSTEM-TEST-002
- ARCH-018-SYSTEM-TEST-001
- ARCH-016-SYSTEM-TEST-001
- ARCH-010-SYSTEM-TEST-005
- ARCH-010-SYSTEM-TEST-002
- ARCH-035-SYSTEM-TEST-002
- ARCH-035-SYSTEM-TEST-005
- ARCH-035-SYSTEM-TEST-004
- ARCH-002-SYSTEM-TEST-008
- ARCH-010-SHOPIFY-020
- ARCH-010-SHOPIFY-008
- ARCH-032-GATEWAY-001
- ARCH-002-GATEWAY-013

## Review queue

These records need actual branch/worktree/code/report review before any acceptance:

- ARCH-006-BACKGROUND-009: Correct PostgreSQL enum parameter bindings in translation lifecycle
- ARCH-006-ADMIN-005: Improve Merchant Messages search and translation language selection
- ARCH-010-ADMIN-003: Lock and settle withdrawn recovery-credit purchases through Shopify Partner Dashboard
- ARCH-003-ADMIN-019: Simplify Observability navigation and remove queue CTA from Grafana page
- ARCH-006-GATEWAY-001: Deploy the independently scalable merchant-communications worker

## Full architecture ledger

| Architecture | Complete | Superseded | Ready | Pending | Review | Blocked |
|---|---:|---:|---:|---:|---:|---:|
| ARCH-001 | 9 | 0 | 1 | 0 | 0 | 0 |
| ARCH-002 | 61 | 5 | 2 | 3 | 0 | 0 |
| ARCH-003 | 23 | 1 | 0 | 1 | 1 | 1 |
| ARCH-004 | 6 | 0 | 1 | 0 | 0 | 0 |
| ARCH-005 | 18 | 2 | 1 | 1 | 0 | 0 |
| ARCH-006 | 21 | 2 | 0 | 3 | 3 | 0 |
| ARCH-007 | 33 | 0 | 2 | 5 | 0 | 0 |
| ARCH-008 | 7 | 1 | 1 | 0 | 0 | 0 |
| ARCH-009 | 5 | 0 | 2 | 2 | 0 | 0 |
| ARCH-010 | 70 | 8 | 0 | 7 | 1 | 0 |
| ARCH-011 | 0 | 0 | 3 | 9 | 0 | 0 |
| ARCH-012 | 6 | 2 | 2 | 0 | 0 | 0 |
| ARCH-013 | 2 | 0 | 0 | 0 | 0 | 0 |
| ARCH-014 | 24 | 1 | 2 | 1 | 0 | 0 |
| ARCH-015 | 12 | 1 | 0 | 1 | 0 | 0 |
| ARCH-016 | 13 | 0 | 0 | 1 | 0 | 0 |
| ARCH-017 | 7 | 0 | 0 | 0 | 0 | 0 |
| ARCH-018 | 3 | 0 | 0 | 1 | 0 | 0 |
| ARCH-019 | 7 | 0 | 1 | 0 | 0 | 0 |
| ARCH-020 | 46 | 0 | 2 | 1 | 0 | 0 |
| ARCH-021 | 106 | 8 | 8 | 0 | 0 | 0 |
| ARCH-022 | 0 | 0 | 10 | 0 | 0 | 0 |
| ARCH-023 | 28 | 4 | 1 | 1 | 0 | 0 |
| ARCH-024 | 17 | 0 | 0 | 0 | 0 | 0 |
| ARCH-025 | 51 | 0 | 0 | 0 | 0 | 0 |
| ARCH-026 | 33 | 0 | 1 | 0 | 0 | 0 |
| ARCH-027 | 20 | 3 | 3 | 2 | 0 | 0 |
| ARCH-028 | 20 | 2 | 2 | 0 | 0 | 1 |
| ARCH-029 | 5 | 0 | 1 | 0 | 0 | 0 |
| ARCH-030 | 2 | 5 | 0 | 0 | 0 | 0 |
| ARCH-031 | 7 | 1 | 0 | 0 | 0 | 0 |
| ARCH-032 | 24 | 6 | 3 | 2 | 0 | 1 |
| ARCH-033 | 7 | 1 | 1 | 0 | 0 | 0 |
| ARCH-034 | 5 | 0 | 1 | 0 | 0 | 0 |
| ARCH-035 | 33 | 15 | 3 | 3 | 0 | 0 |
| ARCH-036 | 9 | 14 | 1 | 0 | 0 | 0 |
| ARCH-038 | 8 | 1 | 2 | 0 | 0 | 0 |
| ARCH-039 | 15 | 0 | 1 | 0 | 0 | 0 |
| ARCH-040 | 19 | 12 | 3 | 0 | 0 | 0 |
| ARCH-041 | 14 | 0 | 1 | 0 | 0 | 0 |
| ARCH-043 | 15 | 2 | 1 | 1 | 0 | 0 |
| ARCH-044 | 8 | 0 | 0 | 0 | 0 | 0 |
| ARCH-045 | 10 | 6 | 1 | 0 | 0 | 0 |
| ARCH-046 | 12 | 8 | 0 | 1 | 0 | 1 |
| ARCH-047 | 22 | 2 | 1 | 0 | 0 | 0 |
| ARCH-048 | 13 | 3 | 0 | 1 | 0 | 0 |
| ARCH-049 | 11 | 0 | 1 | 0 | 0 | 0 |
| ARCH-050 | 10 | 0 | 2 | 0 | 0 | 0 |
| ARCH-051 | 1 | 0 | 0 | 0 | 0 | 0 |
| ARCH-052 | 36 | 21 | 3 | 2 | 0 | 0 |
| ARCH-053 | 21 | 0 | 0 | 3 | 0 | 0 |
| ARCH-054 | 11 | 0 | 1 | 1 | 0 | 0 |
| ARCH-055 | 12 | 0 | 1 | 0 | 0 | 0 |
| ARCH-056 | 5 | 0 | 1 | 1 | 0 | 0 |
| ARCH-057 | 11 | 0 | 1 | 1 | 0 | 0 |
| ARCH-058 | 12 | 0 | 1 | 2 | 0 | 0 |

## Durable reconciliation boundary

This report and machine-readable inventory supersede the September workspace rollup for this audit snapshot. They do not overwrite historical task acceptance, complete an outstanding review or change active execution ownership. Task-specific lifecycle overlays must be applied in the matching parent task worktrees; the policy reserves their commit/push to the developer unless specifically delegated. No branch was merged, no main branch pushed and no production action taken.

## Published task correction — 2026-11-05

At the developer's explicit follow-up, fetched origin and created the launcher-resolved parent worktree for task/ARCH-009-ADMIN-002 from origin/main 4b300e7ec. Changed ADMIN-002 Ready → Pending, preserving attempt 0 and empty claims; updated its domain index and ARCH-009 frontier. ADMIN-001 is Ready on integrated main and Review on origin/task/ARCH-009-ADMIN-001; neither is Complete. ADMIN-003 remains Pending. Published parent commit fe04b31ff to origin/task/ARCH-009-ADMIN-002 successfully; no implementation worktree, feature edit or main merge. The inventory above remains the original audit snapshot; the published overlay is the subsequent correction awaiting developer integration.

## Authorized retirement — 2026-11-05

The developer explicitly superseded ARCH-009-ADMIN-001/002/003 after source-grounded scope review. Published matching parent task branches: ADMIN-001 60f660673 (preserved Attempt 1 and prior review), ADMIN-002 77b5e4356 (Attempt 0), ADMIN-003 726a4de41 (Attempt 0). Empty claims; no implementation accepted. ARCH-010 supersedes local cancellation ownership; ARCH-015 replaces Admin refund approval/settlement. ADMIN-003 retains its generic correction safety rule for future ARCH-007-ADMIN-004 or equivalent capability. Each branch updates its task, index and architecture retirement note. No downstream task was promoted. ARCH-009-SYSTEM-TEST-001 remains Pending/manual-gated; its obsolete matrix requires scope reconciliation before execution. This supersedes the preceding Pending overlay for ADMIN-002. No feature edits, merges or deployment.
