---
id: ARCH-016-SHOPIFY-002
architecture_id: ARCH-016
title: Expose merchant recovery settings and Shopify recovery-offer configuration
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-016-DATABASE-001
- ARCH-016-SHARED-001
enables:
- ARCH-016-SYSTEM-TEST-001
created: 2026-09-16
updated: 2026-09-16
---

# ARCH-016-SHOPIFY-002

## Objective

Add one coherent merchant-facing Recovery Settings experience for subscribed Free and Paid merchants.

## Authorized implementation surface

```text
app/routes.ts
app/services/shop/merchant-route-access-policy.ts
app/routes/app/recovery-settings/route.tsx              # new
app/components/recovery-settings/*                      # new
app/services/recovery-policy/*                          # new server policy resolver/repository
app/locales/*.json or existing translation catalogue files
navigation component(s) that own merchant app navigation
focused route/component/service tests
package.json/package-lock.json only for exact Shared version pin from SHARED-001
```

Do not change `/app/promotions`; it remains ARCH-010 recovery-credit promotions.

## Route/access

Add canonical route:

```text
/app/recovery-settings
```

Add one merchant-access capability consistent with current policy naming.

Allow for merchant experience states corresponding to active subscribed use:

```text
ACTIVE
TRIALING if represented separately by route policy
```

Do not expose as functional configuration in NO_CONTRACT, UNINSTALLED or blocked execution states.

Add navigation label `Recovery settings` in the existing merchant navigation.

## Effective policy resolver

Create one server-only resolver used by loader/UI and available for Background-equivalent implementation semantics:

```text
active, unexpired ShopRecoveryPolicyOverride
  -> effective = override complete snapshot, source ADMIN_OVERRIDE
otherwise
  -> effective = ShopSettings, source MERCHANT
```

Do not implement field-by-field precedence.

The merchant save action updates ONLY ShopSettings. It never edits/clears admin override.

When an override is active:

- show a clear banner that platform administration currently controls the effective recovery policy;
- show merchant configured values and effective values;
- merchant may edit underlying merchant values;
- explain those values take effect when override is removed/expires.

## Page sections

Render exactly these logical sections.

### 1. Recovery start

```text
Start recovery after [N] minutes of checkout inactivity
```

Use existing `ShopSettings.recoveryDelayMinutes`.

Valid merchant range:

```text
0..10080 minutes
```

### 2. Recovery offer

Radio/select modes:

```text
NONE
  label: No discount

FIXED
  label: Always use a specific Shopify discount

AI_BEST_APPLICABLE
  label: Let Moda AI choose the best applicable discount
```

For `AI_BEST_APPLICABLE`, explanatory text MUST state only that Moda AI will choose from the merchant's Shopify discounts when that future capability is available. Do not describe ranking/eligibility semantics as already implemented by ARCH-016.

For FIXED show local synchronized discount catalogue grouped/displayed with:

```text
title
summary
method (Automatic / Code)
redeem code when exactly one exists
start/end where present
current provider status
```

Show all currently running catalogue rows. Rows with `fixedSelectable = false` are visible but disabled and explain `Not available for fixed recovery selection`.

Only selectable when:

```text
catalogue status CURRENT
isAvailable true
providerStatus ACTIVE
startsAt absent or <= now
endsAt absent or > now
fixedSelectable true
same shop
```

If catalogue is SYNC_REQUIRED/SYNCING/ERROR/UNAVAILABLE, do not present stale rows as selectable. Show a bounded synchronization/unavailable state.

### 3. No-response follow-up

Controls:

```text
[ ] Send one follow-up when the customer has not replied
After [N] minutes/hours
```

V1 supports exactly one follow-up.

Persist as minutes. UI may display convenient hour/day units but server receives/normalizes exact whole minutes.

Allowed persisted delay:

```text
1..10080 minutes
```

Required merchant explanation:

```text
If the customer replies, continuing the recovery conversation does not use another recovery credit.
If the customer has not replied and Moda sends the scheduled follow-up, that follow-up is a new proactive recovery attempt and uses another recovery credit.
Follow-up timing is measured from the last proactive recovery message sent.
```

Do not state that `<24h` is free. It is not.

## Save validation

Server action MUST re-read the shop-scoped discount/catalogue. Never trust hidden form IDs.

Validation:

```text
RecoveryOfferMode valid
recoveryDelay 0..10080
follow-up cross-field rules
FIXED discount belongs to authenticated shop
catalogue CURRENT
fixed discount currently running/selectable
non-FIXED has no fixed discount ID
```

Use a DB transaction for policy write where appropriate.

Do not clear an existing fixed discount merely because the catalogue temporarily becomes ERROR unless merchant explicitly saves another valid mode. Runtime execution will fail-soft according to Background task rules.

## AI scope boundary

The UI may persist `AI_BEST_APPLICABLE`.

MUST NOT:

- invoke CommerceAgent;
- call an LLM;
- run best-discount calculations;
- show fake AI-selected result;
- automatically convert AI mode to FIXED.

## Internationalization

Add every new user-visible string to every currently supported merchant locale file. Preserve existing translation-key conventions. Do not leave English-only fallback keys for this page.

## Required tests

- route allowed for eligible Free merchant;
- route allowed for eligible Paid merchant;
- NO_CONTRACT denied/redirected consistently;
- existing recovery delay loads/saves;
- NONE saves with null fixed ID;
- FIXED requires same-shop current selectable discount;
- cross-shop ID rejected;
- stale/unavailable catalogue cannot be selected;
- non-selectable active discount visible but disabled;
- AI_BEST_APPLICABLE persists without invoking AI;
- enabled follow-up requires delay;
- disabled follow-up persists null delay;
- credit warning appears;
- active admin override banner/effective values appear;
- merchant save does not modify override;
- all locale files contain new keys.

## Validation

```text
npm test
npm run typecheck
npm run lint
npm run build
git diff --check
```

Use actual repository scripts; document any unchanged baseline diagnostics by baseline ID.

## Stop conditions

STOP if:

- implementing the UI would require changing ARCH-010 `/app/promotions` semantics;
- a local GraphQL call to Shopify is proposed just to render the page;
- AI/CommerceAgent selection logic would need to be invented;
- a fixed discount requires inventing Meta template body-parameter positions. Persist/select/snapshot the offer; do not invent a WhatsApp template contract.

## Completion protocol

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.
