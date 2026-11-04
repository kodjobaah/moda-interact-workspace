# ARCH-057 Shopify Tasks

Architecture: `docs/architecture/ARCH-057-shopify-application-database-correctness-and-simplicity.md`  
Execution plan: `docs/architecture/ARCH-057/execution-plan.md`  
Owner: `moda_app`  
Coordinator: `moda_architect`

Individual task YAML frontmatter is authoritative.

| Task | Bounded outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-057-SHOPIFY-001](SHOPIFY-001-resolve-authenticated-merchant-request-context.md) | Resolve authenticated merchant context once per request | Complete | — |
| [ARCH-057-SHOPIFY-002](SHOPIFY-002-stabilise-subscription-activation-and-provider-evidence.md) | Stabilise subscription activation and provider evidence | Ready | SHOPIFY-001 |
| [ARCH-057-SHOPIFY-003](SHOPIFY-003-simplify-recovery-credit-purchases-and-refunds.md) | Simplify recovery credit purchases, refunds and history admission | Complete | SHOPIFY-002 |
| [ARCH-057-SHOPIFY-004](SHOPIFY-004-consolidate-commercial-read-projections.md) | Consolidate commercial read projections | Ready | SHOPIFY-001, SHOPIFY-002, SHOPIFY-003 |
| [ARCH-057-SHOPIFY-005](SHOPIFY-005-simplify-support-inbox-reads-and-acknowledgements.md) | Simplify support inbox reads and acknowledgements | Ready | SHOPIFY-001 |
| [ARCH-057-SHOPIFY-006](SHOPIFY-006-reuse-recovery-read-context-and-preserve-command-admission.md) | Reuse recovery read context while preserving command admission | Ready | SHOPIFY-001 |
| [ARCH-057-SHOPIFY-007](SHOPIFY-007-unify-settings-reads-and-guard-policy-writes.md) | Unify settings reads and guard merchant policy writes | Ready | SHOPIFY-001 |
| [ARCH-057-SHOPIFY-008](SHOPIFY-008-simplify-merchant-knowledge-processing-and-refresh.md) | Simplify merchant knowledge processing and refresh | Pending | SHOPIFY-001, SHOPIFY-007 |
| [ARCH-057-SHOPIFY-009](SHOPIFY-009-preserve-session-lifecycle-and-webhook-configuration.md) | Preserve sessions across uninstall retries and reinstall admission | Ready | SHOPIFY-001 |
| [ARCH-057-SHOPIFY-010](SHOPIFY-010-bound-webhook-ingress-and-queue-publication.md) | Bound webhook ingress and queue publication | Pending | SHOPIFY-009 |
| [ARCH-057-SHOPIFY-011](SHOPIFY-011-complete-server-error-diagnostics.md) | Complete server error diagnostics after functional tasks | Pending | SHOPIFY-001–010 |
| [ARCH-057-SHOPIFY-012](SHOPIFY-012-enforce-domain-runtime-names.md) | Enforce descriptive runtime names and canonical development identities | Pending | SHOPIFY-011 |
| [ARCH-057-SYSTEM-TEST-001](../../system-test/ARCH-057/SYSTEM-TEST-001-verify-shopify-persistence-and-diagnostics.md) | Verify integrated Shopify persistence and diagnostics | Pending | SHOPIFY-012 and transitive prerequisites |

The task definitions and dependency frontier are maintained in the execution plan. A Ready status means all explicit prerequisites are Complete; it does not authorize starting several tasks in parallel without their normal launcher preparation.
