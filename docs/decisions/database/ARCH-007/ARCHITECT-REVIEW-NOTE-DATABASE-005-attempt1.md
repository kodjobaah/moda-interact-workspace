# ARCH-007 DATABASE-005 Attempt 1 review note

Attempt 1 received **Changes Requested** for one database CHECK-semantics defect.

The migration currently uses:

```sql
NOT "recoveryCreditPackEnabled"
OR "recoveryCreditsPerPack" > 0
```

which permits `recoveryCreditPackEnabled = true` with `recoveryCreditsPerPack = NULL` because PostgreSQL CHECK constraints accept an UNKNOWN/NULL result.

The authoritative Attempt 2 correction contract is the latest `## Architect Review` in:

```text
docs/decisions/database/ARCH-007/DATABASE-005-repeatable-recovery-credit-packs.md
```

Correct the unapplied migration in place so enabled packs explicitly require a non-null, positive `recoveryCreditsPerPack`, and strengthen the deterministic validator to assert that NULL-safe shape.

Do not redesign the recovery-credit schema or start DATABASE-006/SHARED-005.
