---
id: ARCH-014-ADMIN-009
architecture_id: ARCH-014
title: Add intuitive version-safe background runtime controls to Admin
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 66
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-014-DATABASE-004
- ARCH-014-ADMIN-007
enables:
- ARCH-014-SYSTEM-TEST-003
created: 2026-09-16
updated: 2026-09-16
---

# ARCH-014-ADMIN-009

## Objective

Expose the approved `BackgroundRuntimeConfig` fields in Admin Controls using an intuitive, explanatory UI.

The page must be understandable without reading source constant names.

It must also be safe when multiple Admin replicas/users edit concurrently.

## Location

Integrate with the retained Admin Controls surface after accepted ADMIN-007.

Do not create a second top-level Admin application.

Primary route remains the existing controls route under Billing/Controls unless ADMIN-007 establishes an architect-approved equivalent route.

## Authorization

- Reading follows existing protected Admin access.
- Every mutation in this task requires `SUPER_ADMIN`.
- A non-SUPER_ADMIN may see current values read-only if the existing Controls page permits that role; it must not receive enabled mutation controls.

## Required files

Use existing conventions and add at minimum:

```text
src/components/admin/background-runtime-controls.tsx
src/lib/admin/background-runtime-control-validation.ts
src/app/actions/background-runtime-controls.ts
```

Add focused unit/security tests.

Do not merge this into the old superseded BillingPlan economics control component removed by ADMIN-007.

## UI information architecture

Top heading:

```text
Runtime Controls

Change how background processing behaves without redeploying workers.
Changes are shared across all worker replicas.
```

Use exactly three primary classifications:

```text
Operational
Advanced
Abuse Protection
```

Desktop (`md` and above): accessible tab list.

Small screens: one select/dropdown with the same three choices.

Do not render one giant form.

## Table pattern

Inside each tab, group by domain using sections/accordions.

Each settings table has exactly these conceptual columns:

```text
Setting | Value | Purpose / Guidance
```

Each value row includes:

- input;
- human unit;
- `Default: ...`;
- `Allowed: ...`;
- no raw database/environment constant as the primary label.

Technical field name may appear only inside collapsed `Show technical details`.

## Operational tab

### Billing

**Reconciliation interval**
- field: `billingReconciliationIntervalSeconds`
- UI unit: seconds
- default 60
- guidance:
  `How often Moda checks Shopify billing state. Lower values detect changes sooner but increase Shopify and database activity.`

**Shops per reconciliation cycle**
- `billingReconciliationShopBatchSize`
- unit shops
- default 50
- guidance:
  `Maximum merchants checked during one reconciliation pass. Increase this as the merchant base grows, while watching provider and database load.`

**Usage events per publish cycle**
- `shopifyUsagePublishBatchSize`
- unit events
- default 50
- guidance:
  `Maximum pending Shopify App Events submitted during one billing publish pass. Higher values drain backlog faster but create more provider traffic.`

### Recovery

**Repair interval**
- `recoveryRepairIntervalSeconds`
- display using seconds/minutes, default `5 min`
- guidance:
  `How often Moda looks for recoveries blocked because recovery capacity was unavailable.`

**Shops per repair**
- `recoveryRepairShopBatchSize`
- default 100
- guidance:
  `Maximum shops inspected during one recovery-capacity repair pass.`

**Recoveries per resume job**
- `recoveryResumeBatchSize`
- default 25
- guidance:
  `Maximum blocked baskets resumed by one job before Moda schedules continuation work.`

### Merchant communications

**Translation reconciliation interval**
- `translationReconciliationIntervalSeconds`
- default `5 min`
- guidance:
  `How often Moda repairs missing or stale translation jobs. Lower values recover work sooner but increase database and queue activity.`

**Translations per provider batch**
- `translationBatchMaxRequests`
- default 100
- guidance:
  `Maximum translation requests grouped into one provider batch. Larger batches reduce submission overhead but increase the size of each provider operation.`

### Messaging

**Wait after customer message**
- `conversationQuietWindowMs`
- UI unit seconds; support decimal display only if exact ms is not a whole second
- default `3 sec`
- guidance:
  `Moda waits this long after the most recent customer message before responding, so rapid follow-up messages can be handled as one turn.`

**Maximum message settle time**
- `conversationMaxSettleWindowMs`
- default `10 sec`
- guidance:
  `The longest Moda waits for additional messages before responding. This value cannot be lower than the wait-after-message setting.`

## Advanced tab

### Billing retries

Rows:

```text
Frozen subscription recheck
  billingFrozenRecheckSeconds
  default 60 min
  "How frequently Moda rechecks subscriptions currently reported as frozen."

Provider-state retry
  billingProviderRetrySeconds
  default 5 min
  "Delay before retrying when Shopify billing state cannot be confirmed."

Usage-event retry base
  shopifyUsageRetryBaseSeconds
  default 60 sec
  "Starting delay for retryable Shopify App Event failures before exponential backoff."

Usage-event maximum retry delay
  shopifyUsageRetryMaxSeconds
  default 60 min
  "Upper bound on the usage-event exponential retry delay."
```

### Translation recovery/retries

Rows:

```text
Reconciliation page size
Translation claim timeout
Translation submission retry
Initial provider poll
Provider poll interval
Translation result retry
Translation submission attempts
Translation automatic retries
```

Map exactly to DATABASE-004 fields.

Guidance must distinguish provider polling from result-application retry. Do not describe them as the same control.

### Worker throughput

Section intro:

```text
These values are fleet-wide queue limits across all worker replicas.
Adding replicas does not multiply the configured cap.
```

Rows:

```text
Checkout events                  checkoutQueueGlobalConcurrency          default 10
Order events                     orderQueueGlobalConcurrency             default 5
Pending recovery candidates      pendingRecoveryQueueGlobalConcurrency   default 10
Recovery capacity resume         recoveryResumeQueueGlobalConcurrency    default 10
WhatsApp events                  whatsappQueueGlobalConcurrency          default 20
Merchant communications          merchantCommunicationsQueueGlobalConcurrency default 10
Billing subscription reconcile   billingSubscriptionQueueGlobalConcurrency default 10
```

Guidance for every row must say it is the maximum simultaneous jobs **across the fleet**, not per replica.

## Abuse Protection tab

Intro:

```text
These controls affect platform protection from excessive WhatsApp traffic.
Window lengths are fixed by the application; only the allowed message/turn counts are editable.
```

Group:

```text
Incoming WhatsApp messages
Conversation turns
Product discovery
```

Use labels with the fixed window in human text, for example:

```text
Sender limit — 1 minute
Global limit — 1 minute
Sender limit — 10 minutes
Conversation limit — 1 minute
...
```

Map exactly to all 12 DATABASE-004 abuse fields.

Example guidance:

`Maximum new product-discovery turns accepted from one customer during a one-minute window. Lower values provide stronger abuse protection but can suppress legitimate rapid conversations.`

Do not expose Redis key names or constant identifiers as primary UI.

## System-managed information

At the bottom of Advanced, add a collapsed non-editable section:

```text
System-managed settings
```

Explain that these remain application/deployment/merchant-managed and are intentionally not editable here:

```text
Readiness probe timeout
WhatsApp HTTP timeout
Abandoned-checkout lookup safety bounds
Database/Redis lock and low-level retry timings
Queue telemetry sampling/retention
Translation provider output safety bounds
Provider credentials / provider identity / translation model
Billing lifecycle retry tier structure
Usage-event stale-claim recovery timeout
Recovery queue retry/backoff
Merchant recovery delay (configured per merchant)
```

Do not create inputs or `BackgroundRuntimeConfig` fields for them.

## Save behaviour

Each primary tab has its own form/save action.

Sticky footer on dirty tab:

```text
<N> unsaved changes

[ Reset unsaved changes ]                  [ Save changes ]
```

Every save requires:

```text
Reason
[ ... ]
```

Reason: trimmed `1..1000`.

`Reset unsaved changes` resets client values only; it does not write the DB.

Section-level `Restore defaults` may set the section's form values to DATABASE-004 defaults, but still requires Save + reason.

## Optimistic concurrency — binding

Every rendered form includes hidden:

```text
expectedVersion = current BackgroundRuntimeConfig.version
```

Server action:

1. authenticate SUPER_ADMIN;
2. parse only fields belonging to that tab;
3. start transaction;
4. read `BackgroundRuntimeConfig(id="default")`;
5. if missing, fail:
   `Background runtime configuration is missing.`;
6. if current version != expected:
   return concurrency conflict without changing anything;
7. validate full prospective config including cross-field relationships;
8. `updateMany` where `{ id: "default", version: expectedVersion }`;
9. update only the submitted tab fields + `version: { increment: 1 }`;
10. require count `1`;
11. read resulting row;
12. create `BackgroundRuntimeConfigAuditEvent` in same transaction with exact before/after JSON, expected/resulting versions, section, actor id and reason;
13. commit;
14. revalidate Controls route.

Exact user conflict message:

```text
Runtime controls changed since this page was loaded. Reload the current values and reapply your changes.
```

Do not automatically merge concurrent edits, even if they touched different tabs.

A failed/conflicted update creates no audit row.

## Horizontal-scaling copy

After successful save:

```text
Runtime controls updated.

The committed values are shared by all worker replicas. Running work is not interrupted; workers adopt the new configuration automatically.
```

For queue concurrency:

```text
Fleet-wide queue limits converge without redeploying workers.
```

Do not promise instantaneous interruption of active jobs.

## Validation rules

Mirror every DATABASE-004 bound and every cross-field rule server-side.

Client `min`/`max` is convenience only; server validation is authoritative.

Use integer validation for integer fields. Convert human seconds/minutes to exact stored seconds/milliseconds deterministically.

## Mandatory tests

1. all three tabs/classifications render;
2. desktop tabs and small-screen selector expose same classifications;
3. every approved field appears exactly once;
4. system-managed values have no editable input;
5. guidance text exists for every editable row;
6. defaults/ranges display;
7. abuse windows are labels, not editable fields;
8. worker throughput says fleet-wide;
9. non-SUPER_ADMIN cannot mutate;
10. valid save increments version exactly once;
11. successful save creates one audit row;
12. two concurrent saves using same expected version: exactly one succeeds;
13. loser creates no audit;
14. conflict returns exact message and does not silently refresh/overwrite the user's form;
15. cross-field invalid values fail;
16. restore-defaults is client-only until save;
17. reason required;
18. missing singleton fails rather than upserts;
19. no environment-variable values are mutated;
20. Controls page contains no legacy Upgrade ladder/Verified Shopify economics surface after ADMIN-007.

## Validation

```bash
npm test
npm run build
npm run lint --if-present
git diff --check
```

## Stop conditions

STOP if ADMIN-007 is not accepted, DATABASE-004 is absent, or implementation would require a generic JSON/key-value editor instead of the defined human UI.
