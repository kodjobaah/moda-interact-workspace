# Latest snapshot reconciliation

## Result

The Shopify assessment remains applicable to `moda-interact-workspace(20261104-005051).zip`. The task definitions are based on this latest archive. Its existing Shopify review package is byte-identical to the delivered revision 01.

| Archive | SHA-256 |
|---|---|
| Reviewed `moda-interact-workspace(20261103-235702).zip` | `6890c8d7cfbc68d9814920ef154d0d18b4aca7af8e1e6cc9dd9a95ff04239c6e` |
| Latest `moda-interact-workspace(20261104-005051).zip` | `a2c582c7aecb087b5c997d953bb1ab398f4e0d90d4fa79d555f8dd267b7233ee` |

Comparison uses archive member content hashes/modes, excluding macOS resource metadata. There are 23 added files, four changed files and no removed files.

## Changed areas

| Area | Observed change | Shopify impact |
|---|---|---|
| `moda-interact` | No changed/added/removed implementation or package files | All reviewed Shopify paths and package pins remain applicable |
| Canonical and Shopify nested Database | No changes | Existing schema and migration conclusions remain applicable |
| Shared and Background implementation | No changes | No new imported/runtime contract to consume |
| `docs/architecture/ARCH-056*` and six ARCH-056 task files | Background/API dependency and persistence/progress task definitions added | New work has separate repository ownership; reserve ARCH-056 and allocate ARCH-057 here |
| Existing Shopify review directory | Twelve files added, identical to delivered review patch | Already present; do not reapply or replace that review |
| `docs/architecture/ARCH-055-woocommerce-api-database-correctness-and-efficiency.md` | Existing API review/dependency reconciliation | Does not reopen Shopify's already accepted human-follow-up identity |
| `docs/decisions/api/ARCH-055/API-004-correct-recovery-inbox-and-human-send-persistence.md` | Accepted Attempt 3 and preserved history | No Shopify implementation diff |
| `docs/decisions/api/ARCH-055/API-009-bound-readiness-and-reconcile-api-validation.md` | Ready promotion after API prerequisites | Remains owned by existing API task |
| `moda-interact-api/tests/integration/merchant/conversations/arch055-transaction-config.postgres.test.ts` | Assertion now expects the production ApiPlatformConfigurationError DATABASE_UNAVAILABLE with original Prisma P2021 cause | Test-only change; no Shopify runtime contract change |

ARCH-056 API-001 concerns the API's own Database dependency provenance. Shopify's canonical/nested files already match in this archive; no artificial dependency on that task is created. ARCH-056 Background tasks concern inbound persistence, exact-source settlement and initial recovery continuation. ARCH-057 preserves their producer/consumer queue payloads, message/claim identities, accounting policy and final admission. It does not duplicate or modify that work.

Both terminal system-test tasks may append their own registrations to the existing runner/catalogue. They must preserve each other's keys/scenarios when integrated; a shared registration file is not permission to rewrite the other initiative. No fabricated acceptance dependency is introduced solely because both extend the runner.

## Evidence scope

The full file list is `snapshot-delta.json`. `source-baseline.json` verifies the 264 original source baseline hashes against the latest archive and records all task-definition input hashes. The original source probes remain evidence of unchanged source control flow; no new live API, database, provider or performance run is claimed by this comparison.

This task-definition patch adds only ARCH-057-owned documents. Existing ARCH-055/056 files, every `_index.md`, the prior Shopify report, all runtime/test implementation and submodule pointers are preserved.
