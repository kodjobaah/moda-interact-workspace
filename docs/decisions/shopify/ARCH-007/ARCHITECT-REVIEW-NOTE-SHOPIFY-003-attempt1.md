# ARCH-007 SHOPIFY-003 Attempt 1 review note

Attempt 1 uninstall behavior is correct.

Changes Requested are limited to restoring the previously architect-accepted Shopify repository dependency baseline:

```text
@modainteract/moda-interact-shared
accepted SHOPIFY-002 baseline: package ^0.7.4 / lock 0.7.4
submitted SHOPIFY-003 bundle:  package 0.7.3 / lock 0.7.3
```

Return the SAME task for Attempt 2 after restoring 0.7.4 and revalidating.

Do not redesign the uninstall implementation and do not opportunistically upgrade this task to Shared 0.8.0.
