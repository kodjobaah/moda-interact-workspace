# ARCH-057 execution plan — definition revision 2

## Scope and starting point

This package defines twelve Shopify implementation tasks plus one terminal system-test task. The definitions are materialised. Task YAML frontmatter is authoritative; normal launcher dependency/integration checks remain required before execution.

## Current dependency frontier

Reconciled against the task records in this branch on 2026-11-05 after SHOPIFY-010 Attempt 1 acceptance.

| State | Tasks |
|---|---|
| Complete | ARCH-057-SHOPIFY-001, ARCH-057-SHOPIFY-002, ARCH-057-SHOPIFY-003, ARCH-057-SHOPIFY-005, ARCH-057-SHOPIFY-006, ARCH-057-SHOPIFY-007, ARCH-057-SHOPIFY-008, ARCH-057-SHOPIFY-009, ARCH-057-SHOPIFY-010 |
| Review | ARCH-057-SHOPIFY-004 |
| Ready | None |
| Pending | ARCH-057-SHOPIFY-011, ARCH-057-SHOPIFY-012, ARCH-057-SYSTEM-TEST-001 |

SHOPIFY-010 Attempt 1 is architect-accepted at `6e8029deb30de8903e937dc092b68f8b304e4dce`; independent validation passed 168 tests. Reviewed recorded Redis evidence passed 9 tests; it was not rerun by the architect. Its claim is cleared. SHOPIFY-011 remains Pending solely on SHOPIFY-004, which is still in Review in this branch. Later tasks remain Pending transitively. No downstream execution, main merge, live drain or deployment is implied. Historical frontier notes below do not override current task records.

Apply the definition patch directly to the latest supplied `moda-interact-workspace(20261104-005051).zip` baseline. It already includes the original Shopify review. No earlier patch needs to be applied again. The new API/Background work occupies ARCH-056; it remains unchanged and does not add a Shopify prerequisite.

Each task owns exact files, selected interfaces/behaviour, preservation requirements, focused tests, diagnostic cases and a stop condition. [The mandatory contract](task-contract.md) governs Shared logging, original errors, source privacy, worktree provenance, domain naming and honest evidence.

## Recommended sequential order

1. **ARCH-057-SHOPIFY-001** — request context and explicit profile refresh.
2. **ARCH-057-SHOPIFY-002** — paid activation relation/order and trustworthy provider evidence.
3. **ARCH-057-SHOPIFY-009** — uninstall/reinstall sessions and intended webhook declarations.
4. **ARCH-057-SHOPIFY-003** — purchase/refund/history admission and bounded display checks.
5. **ARCH-057-SHOPIFY-010** — lean ingress and bounded deterministic queue publication.
6. **ARCH-057-SHOPIFY-005** — support badge and visible-message batch acknowledgements.
7. **ARCH-057-SHOPIFY-004** — shared commercial presentation inputs.
8. **ARCH-057-SHOPIFY-006** — recovery read composition and preserved command admission.
9. **ARCH-057-SHOPIFY-007** — settings/category policy and true no-op writes.
10. **ARCH-057-SHOPIFY-008** — knowledge lifecycle/order/refresh.
11. **ARCH-057-SHOPIFY-011** — final server error coverage.
12. **ARCH-057-SHOPIFY-012** — descriptive runtime names and canonical development billing namespaces.
13. **ARCH-057-SYSTEM-TEST-001** — integrated certification of selected outcomes.

This order resolves lifecycle/billing correctness early and leaves diagnostic/naming reconciliation after functional edits. It is a valid dependency order, not permission to auto-claim multiple tasks.

## Safe parallel groups

After 001 is accepted/integrated, the billing, support, recovery, settings and lifecycle branches can run in isolated worktrees. Preserve the following chains:

| Branch | Chain |
|---|---|
| Billing | 002 → 003 → 004 |
| Support | 005 |
| Recovery | 006 |
| Settings/knowledge | 007 → 008 |
| Webhook lifecycle/ingress | 009 → 010 |
| Final application review | All 001–010 → 011 → 012 |
| Terminal verification | 012 → SYSTEM-TEST-001, including all transitive prerequisites |

The short numbers in this table all mean `ARCH-057-SHOPIFY-NNN`. Do not run 001 concurrently with consumers that touch its common routes/Shop service. Do not run 009/010 against competing webhook observability edits. 011 audits the integrated result and therefore runs after the functional branches.

Use the launcher-prepared matching parent/implementation worktrees and its dependency checks. Shared files such as package scripts are merged additively; a task cannot remove another accepted task's entrypoint. Final system-test registration preserves ARCH-056 and other suites without inventing a dependency on unrelated runtime work.

## Launch commands

After importing this definition package into the real parent workspace:

```text
/moda-task ARCH-057-SHOPIFY-001
```

When supplying a portable file directly, the interactive workflow supports:

```text
/moda-task ARCH-057-SHOPIFY-001 --definition docs/decisions/shopify/ARCH-057/SHOPIFY-001-resolve-authenticated-merchant-request-context.md
```

`--definition` is an interactive workflow convention, not an argument to `scripts/start-agent-task.py`. The normal launcher owns physical isolation, dependency validation, submodule preparation and claiming. No implementation worktree is created merely by applying the definition patch.

## Required diagnostic outcome

Every operational failure has a named server owner using `@modainteract/moda-interact-shared/logging`. Original safe message/cause, actual database/provider code, status/request ID and trusted correlation survive; internal reason codes supplement them. Caught fallback/retry/typed-unavailable paths remain diagnosable.

Tests inspect actual Shared JSON, inject distinct original-message markers, verify secret/PII absence before harness redaction, and exercise throwing-sink isolation. No raw provider/SQL error appears in the merchant UI. Expected validation and redirects are documented control flow.

## Naming outcome

Runtime names and comments describe the domain. Architecture IDs remain valid in task documents/tests. The user confirmed that the application is still in development, has not gone live, and needs no preservation of existing billing identities. All three old hash-domain literals are replaced by SHOPIFY-012 with its fixed descriptive names. The naming gate has zero runtime exceptions; fixed vectors and fresh-operation replay tests validate the new canonical format. No legacy lookup, backfill, migration or compatibility flag is added. This is Shopify-scoped naming work.

## What this package does not close

Privacy export/redaction/retention F17 remains separate functional work requiring an approved data-lifecycle contract. Subscription-ended notification remains best-effort with diagnostic correction. Inactive/unknown webhook ACK/discard is not new durable quarantine. Completing these tasks does not certify production capacity or the entire platform.

## Review and evidence

Per task, record actual parent/implementation paths and SHAs, nested Database pins, installed Shared/router versions, exact commands/results, relevant SQL/provider/log case artifacts and task-owned container cleanup. Required blocked/skipped tests remain unchecked. Return to architect review and stop; repository agents do not accept their own tasks or start downstream work.

Definition validation and patch apply checks are supplied with the handoff. They are separate from future implementation tests.

## Settings Task Acceptance (2026-11-04)

ARCH-057-SHOPIFY-007 Attempt 1 is architect-accepted and Complete at `e1533e4658e7e69eeb33e7efd6516211f0bcbe2e`. Its task records independent 135-test validation, reviewed 23-test PostgreSQL evidence and review limits. Earlier ready/pending snapshots for this task are historical. SHOPIFY-008 is now ready and unclaimed; SHOPIFY-011 remains pending on remaining prerequisites. No downstream execution, main merge or architecture completion is implied.
