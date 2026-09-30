# ARCH-020: Admin feature ownership review

Source inspection on local main, 2026-09-20. No application implementation,
migration, provider call or runtime verification was performed.

## Verified current behaviour

| Concern | Current implementation |
|---|---|
| Catalogue | Admin reads all database Feature rows, ordered by systemRequired, displayName and key. No named-feature whitelist. |
| Creation | SUPER_ADMIN creates a unique key, display name, optional description and activation mode. New records are active and not system-required. Creation and billing audit are transactional. |
| Editing | Display name and description can change. Key and activation mode are not accepted as editable fields. Non-system-required features can be deactivated/reactivated. |
| Plan inclusion | Plan save resolves selected feature keys from the database, rejects unknown or newly selected inactive features, includes active system-required features and retains existing inactive mappings. |
| Operational mapping | Saving an already materialized pricing plan synchronizes its BillingPlanFeature rows. Merely creating a Feature does not add it to a plan. |
| Effective runtime access | Background requires an enabled operational plan mapping and active Feature. ALWAYS_ENABLED then applies automatically; MERCHANT_OPT_IN additionally requires enabled ShopFeaturePreference. |
| Merchant preference storage | ShopFeaturePreference already stores one enabled preference per shop/feature, default false. |
| Merchant preference UI | Search of the current merchant app found no ShopFeaturePreference/activationMode editor. SHOPIFY-001 remains necessary; this is not already implemented. |

Source files inspected:

- [Admin catalogue action](../../moda-interact-admin/src/app/actions/feature-catalogue.ts)
- [Admin catalogue reader](../../moda-interact-admin/src/lib/admin/feature-catalogue.ts)
- [Admin catalogue UI](../../moda-interact-admin/src/components/admin/feature-catalogue.tsx)
- [Admin pricing-plan save](../../moda-interact-admin/src/app/actions/merchant-pricing-plan.ts)
- [Canonical Prisma schema](../../moda-interact-database/prisma/schema.prisma)
- [Background effective policy](../../moda-interact-background/src/services/effective-billing-policy.service.ts)

## Required Studio integration

Keep Feature as the authoritative catalogue and link Commerce configuration by
Feature.id. Studio must read arbitrary catalogue rows, not recognize only seed
keys such as product_search. It configures behaviour without altering catalogue
metadata, plan mappings or merchant preferences. A feature need not have Commerce
behaviour to remain a valid billing feature.

Show global availability, plan eligibility, opt-in and published implementation
separately. For a feature-bound configuration, grant eligibility is the existing
runtime feature decision AND applicable live Commerce configuration. Publishing
cannot grant plan eligibility or enable an opt-in preference. Missing live
configuration grants no tools for that configuration; do not claim the entire
billing feature is disabled or rewrite its preference.

New arbitrary feature keys must pass end-to-end fixtures: Admin creation, plan
mapping, merchant opt-in where required, Studio configuration/publication and new
conversation discovery. Existing conversations must not gain newly published
tools. Include inactive, unmapped, missing-opt-in and unpublished cases.

## Task impact

The ownership clarification preserves DATABASE-001's Feature foreign key and the
existing SHARED-001 eligibility semantics. COMMERCE-003 and COMMERCE-008 require
read-only catalogue integration. SHOPIFY-001 must implement generic preferences
against actual plan eligibility. No second feature-creation task is needed.

The broader user-authored-tools requirement is now reconciled in C14/C15:
independent tool revisions, capability toolBindings, generic public Shopify query
execution, and a dedicated discovery task COMMERCE-011. Full U01–U13 definitions
are embedded in COMMERCE-008; U14 in COMMERCE-009. Their dependencies and acceptance
criteria follow those services. See the [binding UI design](ARCH-020-studio-ui-design.md).
These are implementation requirements, not claims of completed application work.

## Additional observation

The existing Admin catalogue form/action is not an example of the required
ARCH-020 duplicate-action protections: the inspected form has no explicit
in-flight guard, and its availability action inverts current state. Concurrent
repeated toggles could undo one another. Studio must use explicit desired values
and replay protection. This review did not change Admin or add an Admin task.
