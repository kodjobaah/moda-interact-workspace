# ARCH-048 Background Tasks

Architecture: [`ARCH-048-woocommerce-checkout-recovery-pipeline.md`](../../../architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md).

Assigned agent: `moda_background`. Coordinator: `moda_architect`.

ARCH-048 BG001–BG006 are Complete. The current published frontier is BG007, BG008 and BG010 Complete; BG009 Ready; BG011 Pending. BG007, BG008 and BG010 have accepted reviews and published implementation and workspace task branches. No integrated deployment, live Woo sending or terminal system-test result is implied.

The individual task YAML is authoritative. Definitions are based on the 2026-10-29 code snapshot; each task's materialization, implementation and publication state is recorded in its task file.

| Task | Outcome | Status | Required Complete dependencies |
|---|---|---|---|
| [`BACKGROUND-001`](BACKGROUND-001-schedule-woo-checkout-maturity.md) | Schedule delayed recovery candidates from checkout snapshots | **Complete** | `BACKGROUND-006`, `ARCH-035-BACKGROUND-001`, `ARCH-035-API-008` |
| [`BACKGROUND-002`](BACKGROUND-002-reconcile-woo-order-outcomes-and-terminal-fences.md) | Reconcile order outcomes and prevent terminal sends | **Complete** | `BACKGROUND-006`, `ARCH-035-BACKGROUND-002`, `ARCH-035-API-019` |
| [`BACKGROUND-003`](BACKGROUND-003-admit-and-create-first-woo-recovery.md) | Admit initial recovery and persist first checkout snapshot | **Complete** | `BACKGROUND-006`, `ARCH-046-BACKGROUND-001`, `ARCH-045-BACKGROUND-005` |
| [`BACKGROUND-004`](BACKGROUND-004-integrate-woo-initial-outreach-and-credit-billing.md) | Enforce Woo initial outreach and billing | **Complete** | `BACKGROUND-006`, `ARCH-045-BACKGROUND-005` |
| [`BACKGROUND-005`](BACKGROUND-005-compose-woo-recovery-services-and-wire-workers.md) | Wire accepted Woo services and workers | **Complete** | `BACKGROUND-001`, `BACKGROUND-002`, `BACKGROUND-003`, `BACKGROUND-004`, `ARCH-046-BACKGROUND-002`, `ARCH-046-BACKGROUND-004` |
| [`BACKGROUND-006`](BACKGROUND-006-define-local-woo-recovery-service-contracts.md) | Define local Woo recovery runtime contracts | **Complete** | `ARCH-035-BACKGROUND-001`, `ARCH-035-BACKGROUND-002` |
| [`BACKGROUND-007`](BACKGROUND-007-close-resumed-woo-recoveries-and-stage-next-candidate.md) | Close resumed recovery; stage generation-aware candidate safely | **Complete** | `BACKGROUND-005` |
| [`BACKGROUND-008`](BACKGROUND-008-admit-subsequent-woo-recovery-generations.md) | Admit next-generation recoveries and repair same-generation retries | **Complete** | `BACKGROUND-007` |
| [`BACKGROUND-009`](BACKGROUND-009-settle-resumed-outreach-and-fence-old-generations.md) | Settle unsent old outreach; preserve committed/uncertain sends | **Cpmplete** | `BACKGROUND-007` |
| [`BACKGROUND-010`](BACKGROUND-010-route-inbound-messages-across-woo-recovery-generations.md) | Route current and historical WhatsApp conversations safely | **Complete** | `BACKGROUND-007` |
| [`BACKGROUND-011`](BACKGROUND-011-compose-multi-generation-woo-recovery-workers.md) | Wire generation-aware worker, queue, retry and index handling | **Ready** | `BACKGROUND-007`, `BACKGROUND-008`, `BACKGROUND-009`, `BACKGROUND-010` |

## Execution frontier

1. BG007, BG008, BG009 and BG010 are Complete after architect review and publication of their implementation branches and completion records. BG010 retains a documented pre-live logging remediation gate.
2. BG011 Ready; BG007, BG008 and BG010 are already Complete. Do not skip the composed-worker correction.
3. ARCH-048-SYSTEM-TEST-001 is terminal and must wait for all implementation, publication (if any) and existing consent dependencies.

## Implementation and review constraints

- Each task must run through `/moda-task <TASK_ID>` with launcher-resolved dedicated parent and implementation worktrees; never execute code changes in the shared workspace.
- Repository agent modifies only its explicitly permitted files, its own task metadata/Completion Report and tests. The architect alone modifies architecture documents, indexes and Architect Review.
- Use the canonical shared logger and fail-visible retries; never suppress technical exceptions or log customer carts/PII/secrets.
- Keep each generation independently eligible for initial outreach, but never allow duplicate attempts/charges inside a generation. Consent, STOP, order, MARKETING, provider and production-default-off guards remain mandatory.
