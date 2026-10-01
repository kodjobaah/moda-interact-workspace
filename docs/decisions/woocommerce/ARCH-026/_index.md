# ARCH-026 WooCommerce tasks

Architecture: [`ARCH-026`](../../../architecture/ARCH-026-woocommerce-application-foundation.md).

Assigned agent: `moda_woocommerce`.

Repository: `moda-interact-woocommerce`.

Coordinator: `moda_architect`.

ARCH-026 is being defined iteratively. Only the extension-foundation task is
materialised at this stage.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [WOOCOMMERCE-001](WOOCOMMERCE-001-establish-woocommerce-extension-foundation.md) | Establish a reproducible installable PHP + React WooCommerce extension foundation and minimal Woo Admin page | Pending | - |

## Execution frontier

```text
No WooCommerce task is Ready.
```

WOOCOMMERCE-001 has no architecture-task dependency, but it has a mandatory
repository-provisioning readiness gate. `moda-interact-woocommerce` does not exist in
the supplied snapshot and therefore cannot yet have a launcher-created implementation
worktree.

Before the architect promotes WOO-001 to Ready, verify:

```text
private/canonical repository exists and is reachable
workspace .gitmodules registers moda-interact-woocommerce
workspace gitlink points to the approved initial main commit
WOOCOMMERCE launcher route resolves moda_woocommerce/moda-interact-woocommerce
Codex/Claude moda_woocommerce definitions are synchronized
```

Do not execute WOO-001 from another repository or a shared/default checkout to bypass
that gate.
