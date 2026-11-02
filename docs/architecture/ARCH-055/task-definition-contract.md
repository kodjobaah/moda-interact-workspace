# ARCH-055 deterministic implementation-definition contract — revision2

## Authority and scope

Canonical task files and parent ADRs govern execution. This revision uses the attached `DATABASE-001-persist-woo-restore-snapshot.md` as a precision/style example: concrete file insertions, schema-qualified SQL, preserved state, package script additions, fresh/upgrade proof and stop conditions. The example's completed status/commit evidence is not copied to ARCH-055.

Task count remains13. Every task retains attempt0 and its initial ready/pending dependency state. Definitions are portable, not materialised/claimed; no remote or developer worktree is inferred.

## Required definition elements

1. Exact owning repository, existing edit paths, exact new files and bounded operation matrix; identify insertions versus replacements. No placeholder interface/migration/test names delegated to an agent.
2. Persisted fields specify Prisma name/type/native type, nullable/default policy, SQL schema/table/type, affected indexes/constraints and legacy/backfill behavior. Expected executable SQL is provided where Database work is selected.
3. Local interfaces specify exported symbol, argument/return fields and who owns caller error mapping; database errors preserve the original cause. Public/Shared DTOs are unchanged unless a specifically identified OpenAPI documentation correction is authorised.
4. Mutation steps name tenant/revision/generation predicates, exact-one return/count checks, isolation/lock order and transaction/external-I/O boundary. No prior SELECT followed by an unconditional ID-only UPDATE is presented as a concurrency check.
5. Test rows name fixtures/interleavings and observable results, plus exact file/runner registration. Required unavailable checks remain unchecked and block acceptance. Existing helper models/mocks do not prove real migrated lock behavior.
6. Validation lists real baseline commands or clearly labelled new scripts, default migration target, no hosted resources, cleanup and evidence. Optional experiments retain baseline behavior and return findings, not autonomous architecture changes.
7. Stop at review; do not accept own task, modify indexes/other task status or begin enabled tasks.

## Forward-only migration policy

Every schema/guard correction is implemented in a NEW ordered `prisma/migrations/<named-id>/migration.sql` file. Existing applied migration bytes and `_prisma_migrations` records remain unchanged. Do not use reset/db-push/squash/repair-marking or an automatic down script. A later defect uses another named forward corrective migration after architectural definition.

Forward-only does not forbid correcting an installed SQL function or CHECK. DATABASE-001 explicitly replaces one function and one CHECK in a new transactional script; no other trigger removal or constraint weakening is implied. The separate claim-key metadata backfill temporarily disables one named existing trigger only under ACCESS EXCLUSIVE in the same transaction; it restores the original function/enabled state and has rollback tests. No blanket trigger-disable or replication-role change is permitted.

Migration1 corrects FAILED terminalisation only; API owns new current-Shop/principal policy. Migration2 adds one nullable command metadata column and preserves historical claim identity. Migration3 adds one nullable purpose column and one original-intake partial unique index with a fail-closed duplicate-history preflight. No new business-policy triggers, purpose immutability/nonblank checks or key=command.id SQL policy guards are created.

If a previously supplied ARCH-055 migration has already run, these proposed names cannot be reused with different SQL. Stop and collect names/checksums/current state; a new forward reconciliation must be authored. A documentation patch is not permission to rewrite executed history.

## Cross-owner rule allocation

| Rule | Owner |
|---|---|
| Current Shop/installation identity and version when admitting mutation | API-001 helper; API-007 caller |
| Callback/attempt expiry, current-generation revoke and replay acknowledgement | API-001 service transaction; existing guard narrowly corrected by Database |
| New human claim key generation and key/command/attempt binding | API-004 and SHOPIFY-001 |
| Dispatch/release comparisons and missing-key fail-closed behavior | BACKGROUND-001 |
| Stored metadata columns, exact historical claim backfill and original-intake uniqueness | DATABASE-001 |
| Purpose nonblank/unchanged, replay binding, MIME/expiry/asset cleanup coordination | API-005 |
| Prepared-message moderation identity | API-004, retaining existing schema/Background checks |

## Test-runner ownership

API-001 creates its isolated canonical installation runner; API-003 creates the canonical bootstrap/context/category runner. API-009 later wires both plus AI-delay/readiness into aggregate integration, preserving all prior suite registrations and eliminating the old db-push orchestration only after fixture owners are accepted. Concurrent agents must append their own known test files, not replace another task's runner from a stale copy.

All production schema changes remain in Database, never consumers' nested copies. Consumer tasks adopt an accepted nested Database commit through their own worktrees; system tests remain terminal dependencies only.
