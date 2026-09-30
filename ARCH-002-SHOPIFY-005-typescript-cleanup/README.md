# ARCH-002-SHOPIFY-005 TypeScript Cleanup Task Overlay

This overlay creates a new bounded architecture task:

```text
ARCH-002-SHOPIFY-005
Eliminate existing Shopify application TypeScript baseline debt
```

It is based on the captured current baseline:

```text
48 TypeScript errors
8 affected files

TS7006  27
TS2307   9
TS7031   7
TS7017   3
TS2339   2
```

The task requires the existing:

```bash
npm run typecheck
```

to reach zero without weakening TypeScript/JavaScript checking or suppressing
the errors.

## Files applied

```text
docs/decisions/shopify/ARCH-002/SHOPIFY-005-eliminate-typescript-baseline-debt.md
docs/decisions/shopify/ARCH-002/_index.md
```

The overlay does not modify application source.

## Apply

Extract/copy this folder into `moda-interact-workspace`, then run from the
workspace root:

```bash
python3 ARCH-002-SHOPIFY-005-typescript-cleanup/apply-task.py
```

Then hand the task to the Shopify application agent:

```text
@moda_app start ARCH-002-SHOPIFY-005. Read the task file, eliminate the
documented TypeScript baseline without weakening typechecking, validate
npm run typecheck reaches zero, then return the task with status: review.
```

The task deliberately does not add itself as a new dependency of existing
ARCH-002 work. It depends on accepted `ARCH-002-SHOPIFY-002` but otherwise
remains a bounded cleanup task.

On architect acceptance, `TYPECHECK-001` should be changed from
`KNOWN BASELINE DEBT` to `RESOLVED`.
