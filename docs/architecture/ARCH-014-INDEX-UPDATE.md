# ARCH-014 architecture-index update fragment

When reconciling `docs/architecture/_index.md`, add:

```markdown
| ARCH-014 | pending 3, ready 2 | [Admin-managed merchant pricing catalogue and portfolio economics](ARCH-014-admin-managed-merchant-pricing-catalogue.md) |
```

Initial task state in this overlay:

```text
ready:
  ARCH-014-DATABASE-001
  ARCH-014-ADMIN-001

pending:
  ARCH-014-ADMIN-002
  ARCH-014-SHOPIFY-001
  ARCH-014-SYSTEM-TEST-001
```

`SHOPIFY-001` is pending only on `DATABASE-001`; after Database architect acceptance it may execute independently of `ADMIN-002`.
