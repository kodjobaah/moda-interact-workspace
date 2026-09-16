---
id: ARCH-016-ADMIN-002
architecture_id: ARCH-016
title: Add tenant recovery-policy visibility and explicit admin override
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 20
executor: copilot
claimed_at: 2026-09-16T16:44:56Z
attempt: 1
depends_on:
- ARCH-016-DATABASE-001
- ARCH-016-SHARED-001
enables:
- ARCH-016-SYSTEM-TEST-001
created: 2026-09-16
updated: 2026-09-16
---

# ARCH-016-ADMIN-002

## Objective

Give platform admins a tenant-scoped view of merchant recovery settings, current Shopify discount catalogue state and a durable complete policy override.

## Published Shared dependency

Install/pin the exact package version published by `ARCH-016-SHARED-001` in `package.json` and `package-lock.json`. Import the canonical recovery-policy runtime schema/types from `@modainteract/moda-interact-shared/recovery-policy`. Do not recreate `RecoveryOfferMode`, effective-policy cross-field validation, or an equivalent local runtime schema in Admin.

## Authorized implementation surface

Use the existing tenant administration surface. Current snapshot relevant files include:

```text
package.json
package-lock.json
src/components/admin/tenant-administration.tsx
src/app/actions/tenant.ts
src/lib/admin/types.ts
current tenant detail/drawer/page wiring
focused tenant security/action/component tests
```

Create small recovery-policy admin helpers under existing `src/lib/admin/` conventions when needed.

Do not use ARCH-010 Promotions admin pages.

## Replace direct recovery-delay overwrite behavior

Current Admin can write `ShopSettings.recoveryDelayMinutes` directly.

ARCH-016 changes this behavior:

- merchant `ShopSettings` remains merchant-owned;
- Admin must not silently overwrite merchant recovery-delay/settings;
- Admin creates/updates/deletes `ShopRecoveryPolicyOverride` instead.

Remove/replace the old direct recovery-delay write action from the tenant admin UI.

## Tenant view

Display three columns/sections for every policy field:

```text
Merchant configured value
Admin override value (when active)
Effective value
```

Fields:

```text
Recovery start delay
Recovery offer mode
Fixed Shopify discount (when applicable)
No-response follow-up enabled
No-response follow-up delay
```

Also display:

```text
Shopify discount catalogue status
lastSuccessfulSyncAt
number of currently running discounts
number fixedSelectable
CheckoutRecovery current generation/status/lastExternalActivityAt where recovery detail already exists
```

Do not expose secrets/provider access tokens or full raw providerSnapshot in normal Admin UI.

## Canonical policy validation

Use the published Shared recovery-policy schema for enum/cross-field validation after applying Admin-specific authorization and shop-scoped FIXED-discount checks. Database writes remain Prisma-owned; Shared is the canonical runtime contract, not a database model.

## Override create/update

Admin form starts from current effective policy values.

Require:

```text
complete snapshot of every policy field
reason 1..1000 chars
optional expiresAt in future
```

Validate same constraints as merchant policy plus:

```text
FIXED discount belongs to target shop
catalogue CURRENT
fixed discount currently running/selectable
```

Persist `updatedByPlatformAdminId` from authenticated Admin identity. Never accept admin ID from the submitted form.

Use one transaction for authorization recheck + validation + write.

## Override precedence

An override is effective when:

```text
row exists AND (expiresAt is null OR expiresAt > now)
```

Expired override remains historical row until Admin updates/removes it, but the effective resolver treats it as inactive. UI labels it expired.

Provide explicit Clear Override action with confirmation/reason. In the same transaction as every UPSERT or CLEAR, create `ShopRecoveryPolicyOverrideAuditEvent` with authenticated admin ID, action, reason, and bounded before/after JSON. A CLEAR deletes the live override only after its audit event is created; historical audit events remain. Do not misuse an unrelated billing audit enum.

## AI boundary

Admin may set/view `AI_BEST_APPLICABLE` exactly like merchant mode. Do not implement AI selection or preview.

## Required tests

Security:

- unauthenticated denied;
- non-authorized admin role denied per existing tenant-admin policy;
- submitted fake platformAdminId ignored;
- cross-shop fixed discount rejected.

Behavior:

- view merchant vs effective values;
- complete override changes effective values without changing ShopSettings;
- override expiry restores merchant effective policy;
- clear override restores merchant policy;
- FIXED requires current selectable discount;
- AI_BEST_APPLICABLE stored with null fixed ID;
- direct legacy Admin recoveryDelay write path no longer modifies ShopSettings;
- catalogue state shown without provider secrets.

## Validation

```text
npm run test:unit
npm test
npm run lint
npm run build
git diff --check
```

## Stop conditions

STOP if:

- implementation requires Admin to mutate merchant ShopSettings directly;
- override would become field-by-field nullable inheritance;
- AI selection logic is introduced;
- raw provider access tokens/secret payloads would be displayed.

## Completion protocol

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.
