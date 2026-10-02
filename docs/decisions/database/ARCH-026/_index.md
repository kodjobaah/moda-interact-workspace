# ARCH-026 Database tasks

Architecture: [`ARCH-026`](../../../architecture/ARCH-026-woocommerce-application-foundation.md).

Assigned agent: `moda_database`.

Repository: `moda-interact-database`.

Coordinator: `moda_architect`.

The database stream establishes the minimum durable Woo installation identity and the provider-neutral one-time merchant onboarding milestone needed by Shopify and Woo. Shared tenant/platform/onboarding state remains in `commerce`; Woo-specific installation/authentication state is persisted in the dedicated `woocommerce` PostgreSQL schema. The existing `shopify.ShopSettings.onboardingCompleted` field is retained temporarily and is not removed by DATABASE-001.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [DATABASE-001](DATABASE-001-persist-woocommerce-installation-identity.md) | Add shared Shop platform + onboarding lifecycle fields and one secure `woocommerce.WooCommerceInstallation` record per Woo tenant, retaining the legacy Shopify onboarding field | Ready | - |
| [DATABASE-002](DATABASE-002-establish-provider-neutral-international-context.md) | Add provider-neutral Shop locale/language/time-zone/country context while retaining Shopify compatibility fields | Pending | DATABASE-001 |

## Execution frontier

```text
ARCH-026-DATABASE-001 is Ready and may execute independently of the blocked/pending Woo plugin tasks. DATABASE-002 remains Pending until DATABASE-001 is architect-accepted Complete.
```

DATABASE-001 enables API-002 plus SHOPIFY-001 and BACKGROUND-001. The latter migrate runtime onboarding reads/writes to the shared Shop milestone while keeping the legacy Shopify field as a compatibility mirror. DATABASE-002 then establishes provider-neutral merchant international context and enables SHOPIFY-002 plus API-003. Do not remove the retained Shopify compatibility fields in either database task.
