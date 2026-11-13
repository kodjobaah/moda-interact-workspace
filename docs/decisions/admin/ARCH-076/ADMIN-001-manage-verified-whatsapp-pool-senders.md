---
id: ARCH-076-ADMIN-001
architecture_id: ARCH-076
title: Manage verified WhatsApp pool senders in platform configuration
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-076-DATABASE-001"]
enables: ["ARCH-076-SYSTEM-TEST-001"]
created: 2026-11-13
updated: 2026-11-13
---

# Manage verified WhatsApp pool senders in platform configuration

## Architecture

[ARCH-076](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md), coordinated by `moda_architect`.

## Objective

Expose verified operator enrolment, priority and eligibility for the registered Moda sender pool in the existing platform configuration surface.

## Context

Preserved from original local commit `59705bb589342f31054e6c1fd011dacf9d495ae6` under root-authorized ARCH-076 collision correction. Defined portable design only; Pending/unclaimed until current-main compatibility review and explicit architect promotion. No runtime implementation or launch is authorized by preservation.

Implement the operator inventory in [ARCH-076](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md). A server-authenticated SUPER_ADMIN enrols already registered Meta phone-number IDs under Moda's current WhatsApp Business Account (WABA), assigns priority and can disable allocation to a number. Admin never assigns numbers to checkouts. The single existing encrypted sender configuration supplies the server-side account and token. The inventory contains only non-secret IDs, status, priority and timestamps. Storefront and merchant checkout policy governs how many distinct baskets can coexist. When several recoveries share one shop and customer, Background attaches them to their existing sender route. A different shop still needs a separate active route for that customer. Closing the final active member ends that route. Admin only manages the available number inventory and never imposes a per-shop basket limit.

## Scope

Use the accepted Database migration in the Admin `database` submodule via the established developer integration/pin workflow. Run `npm run prisma:generate` against it. Do not edit a vendored schema or generate hand-written substitute Prisma types.

| Repository-relative path | Required change |
| --- | --- |
| `src/app/(protected)/system-controls/platform-configuration/page.tsx` | Render a sender pool panel only on the existing `?key=messaging.sender` section below the current credential editor. Use server-side authorised data. |
| `src/components/admin/platform-configuration/whatsapp-sender-pool.tsx` (new) | Enrol input for the Meta **Phone Number ID**, integer priority, ordered row list, enable/disable and edit-priority controls. Show current WABA, sender ID and whether available for **new shop/customer routes**. Disabling a sender stops creation of new routes. The already-open route stays available for the same customer and shop, including a new eligible basket in that shop. Explain that enrolling a previous singleton dedicates it to pooled recoveries. Never suggest entering the displayed international phone number in place of Meta's resource ID. |
| `src/app/actions/whatsapp-sender-pool.ts` (new) | Typed Server Actions as below. Revalidate `/system-controls/platform-configuration` on a successful mutation. |
| `src/lib/admin/platform-configuration/whatsapp-sender-pool.ts` (new) | Server-only inventory workflow, Prisma reads/transactions, authenticated mutation/read and audit. |
| `src/lib/admin/platform-configuration/whatsapp-phone-membership.ts` (new) | Server-only credential resolution and Meta membership lookup, injectable fetch for offline tests. |
| `src/i18n/locales/en.json`, `src/i18n/required-keys.ts` | Add operator labels/actions, statuses, help and mapped failure messages under `senderPool.*`. Use the existing Admin translation runtime. The uploaded internal console loads this single catalogue in `src/i18n/index.ts`; no WhatsApp template copy, merchant locale generation or new language framework. |
| `package.json`, `tests/unit/whatsapp-sender-pool.test.ts`, `tests/unit/whatsapp-sender-pool-components.test.tsx`, `tests/integration/whatsapp-sender-pool.postgres.test.ts`, `scripts/test-whatsapp-sender-pool-postgres.mjs` (new except manifest) | Wire component, request/authorization, provider, database and concurrency tests. |

## Out of Scope

No checkout assignment, customer UI, Meta phone registration, template mutation, schema authoring or live provider send. Persist no token or provider response in inventory rows.

## Requirements

1. Bind the credential read to this database's environment and the existing `public.PlatformConfiguration(environment,key='messaging.sender')`. Require a saved, enabled valid sealed record just as Background's `platformConsumerConfiguration.read("messaging.sender")` does. Reuse existing Admin `seal.ts` (`loadConfigUnsealKeyring`, `unsealSecret` with the actual row version/AAD), `secret-validation.ts` (`validateSecretPayload`) and `environment.ts`. Return a server-private snapshot with version, WABA, legacy phone ID and token. Keep the existing sealed object and its three keys unchanged. The Meta template readers only return a WABA; do not widen their client interface, use a plaintext reveal action, or take an environment-variable token on a missing/corrupt row.
2. For a new enrolment and every disabled→enabled transition, verify membership outside a write transaction. Use server-only GET `https://graph.facebook.com/v25.0/{trustedWaba}/phone_numbers?fields=id,status&limit=100` with `Authorization: Bearer <token>`, `cache: "no-store"`, `redirect: "error"` and one 10-second total request deadline. Match the exact resource ID on that WABA with `status === "CONNECTED"`. Omitted/other status, or an absent ID on a verified complete listing → `NOT_CONNECTED`. HTTP/transport/invalid shape/incomplete paging → `PROVIDER_UNAVAILABLE`. Follow `paging.cursors.after` only when `paging.next` indicates another page, with the same origin and path built locally and `after` URL-encoded. Reject missing/repeated cursors when paging indicates continuation. Never use Graph's supplied absolute next URL or log it. Stop as soon as the requested ID is verified. No Graph call for list, disable or priority-only edit. Use an injected stub for tests. No `/register`, number provisioning, template mutation or production provider invocation.
3. Enrolment inserts only a **disabled** inventory row, with the server-derived WABA and requested priority. The runtime default is disabled. First insertion makes that number recovery-pool inventory, even before enabling. On duplicated enrolment of the same verified WABA/phone return the existing settings unchanged; any differing old account → `IDENTITY_CONFLICT`. Only `priority` and `allocationEnabled` are updatable. For updates, load the row, accept an exact replay if current equals next, otherwise match both expected settings atomically and give `STALE_SETTINGS` on mismatch. Enabling requires a matching current WABA. Disabling/priority edits stay possible when Graph or credentials are down. Admin never deletes a sender row. No automatic renumber, route/member closure, merge of shop checkouts, reassignment, backfill or change to existing conversations, pending clarification, attempt/credit or dispatch proof.
4. In the final short transaction for enrolment or enabling, acquire the configuration row `FOR SHARE` and check version/identity against the snapshot used by Graph. If it changed, roll back with `CONFIGURATION_CHANGED`; the operator can submit again. Token rotation during the lookup must not authorise a stale write. Serialize first enrolment on the same transaction-scoped key used by the Background non-pooled-send fence: `pg_advisory_xact_lock(hashtextextended('whatsapp-pool-membership:' || $1::text, 0))`, binding the phone ID. Take this lock before the final collision check/insert, with no Shop locks. A concurrent non-pooled permit admitted first must be visible to the enrolment preflight. A provider GET never runs while a DB lock is held. Use conflict-safe insert and re-read under the membership lock; CAS or row lock on single-row settings update.
5. First-deployment cutover: retire old workers capable of sending without a pool-membership check and drain their in-flight I/O before handing the singleton to the pool. In the above transaction, reject `LEGACY_SENDER_IN_USE` on protected legacy use. Examine only outbound messages with dispatch/receipt evidence (`providerDispatchAdmittedAt`, `providerMessageId` or `sentAt`), and match the new frozen dispatch pair if present. Treat both NULL on the current legacy singleton as possible legacy activity. Follow `Conversation.checkoutRecoveryId` for unassigned recoveries. A nonterminal `DETECTED/MESSAGE_SENT/ENGAGED` recovery with evidence and no `RecoverySenderAssignment` blocks enrolment **while it has not effectively expired**, applying the same inclusive cutoff from the `default` BackgroundRuntimeConfig. Completed, expired, cancelled or already effectively expired recoveries never reserve or block a pool number. Fetch the config only when assessing recovery conflicts. Use exact non-negative days semantics even for zero and the full signed PostgreSQL integer range (compare elapsed milliseconds using numeric arithmetic; never overflow a timestamp by subtracting an enormous interval). Do not update recoveries in Admin.
6. For an independent standalone conversation, reject if the matched sender has a general outbound still in flight (`providerDispatchAdmittedAt` present, PENDING and no provider receipt) or if an open general conversation (`checkoutRecoveryId IS NULL`, `outcome='IN_PROGRESS'`) has sender evidence and latest inbound or confirmed send within the rolling 24-hour window. Evaluate timestamps at UTC database time; strictly older/closed, settled standalone history is not a permanent reservation. If historic sender identity is unknown after a previous credential change, use a clean registered number or drain the ambiguous active traffic in the environment under the cutover procedure. No client checkbox overrides an identified conflict. Record these instructions in the existing Admin README under platform configuration. Once enrolled, Background excludes this number from new non-pooled/standalone sends even when disabled; prior histories and provider callbacks remain addressable.
7. Log bounded success/outcome with the authenticated actor and deployment using existing `src/lib/auth/audit.ts`. At the server owning the failure, use `@modainteract/moda-interact-shared/logging` with operation and original exception message, safe HTTP status, Meta `error.code`, `error_subcode`, `error.message` and request/trace ID when provided. Scrub credentials from provider text before emitting, preserving other original wording. Never log bearer/token, request headers, request/response dumps, decrypted config, pagination URLs or customer data. Keep error causes for diagnosis; expected validation failures use their own reason. Unknown or invalid response cannot mutate inventory.

## Work Items

- [ ] Wire the authorised page, operator controls, input validation, localized presentation and typed Server Actions.
- [ ] Verify connected phone membership on the trusted WABA and handle unavailable, malformed, duplicate, stale and rotated configuration deterministically.
- [ ] Implement DB membership locking, duplicate enrolment, legacy cutover preflight, guarded setting edits and original-error diagnostics.
- [ ] Write and run all declared unit, component, disposable PG and baseline checks. Document operator use and publish the parent and implementation task report for architect review.

## Interfaces / Contracts

Use `requirePlatformAdminRead()` or `requirePlatformAdminMutation()`, then `requireConfigurationSuperAdmin(principal)` on **every service entry**. The protected page's role check alone does not authorise Server Actions. Derive deployment via `getConfigurationEnvironment()`. The browser never supplies the environment, WABA, access token, actor ID, endpoint or membership proof. Number IDs are strings, matching the existing credential validator `^[0-9]{4,32}$`; never convert them to JS numbers. Validate priority as a JSON integer from 0 through 2147483647, including zero. Whitelisted exact input shapes:

```ts
type SenderSettings = { priority: number; allocationEnabled: boolean };
type PoolAction =
  | { op: "enrol"; providerPhoneNumberId: string; priority: number }
  | { op: "update"; providerPhoneNumberId: string; expected: SenderSettings; next: SenderSettings };
type PoolRow = SenderSettings & {
  providerPhoneNumberId: string; providerAccountId: string;
  createdAt: string; updatedAt: string;
};
```

`readWhatsAppSenderPool()` returns `{ providerAccountId: string | null, rows: PoolRow[] }`. Return rows ordered by `priority ASC, providerPhoneNumberId COLLATE "C" ASC` even if all are disabled. IDs are ASCII digits. The null account state displays a configuration-required explanation and permits retiring existing rows. Missing credentials cannot enable/enrol one. Render only the account ID and inventory fields. No client Graph request, token reveal, decrypted credential blob, transport URL or customer phone appears in the result.

`mutateWhatsAppSenderPoolAction(input: unknown)` returns `{ok:true,row:PoolRow}` or `{ok:false,code}`, with codes `INVALID_INPUT`, `FORBIDDEN`, `CONFIGURATION_UNAVAILABLE`, `CONFIGURATION_CHANGED`, `PROVIDER_UNAVAILABLE`, `NOT_CONNECTED`, `LEGACY_SENDER_IN_USE`, `SENDER_NOT_FOUND`, `IDENTITY_CONFLICT`, `STALE_SETTINGS` or `DB_UNAVAILABLE`. The UI maps the code to a catalogue key. Do not expose raw provider/SDK/DB errors to browsers.

## Dependencies

`ARCH-076-DATABASE-001`, architect accepted and integrated in the consumption pin.

## Enables

`ARCH-076-SYSTEM-TEST-001` uses the accepted Admin surface together with the Background implementation.

## Acceptance Criteria

- [ ] Demonstrate the actual authenticated route, form and server actions. Include empty/missing config, stable tie-break, stale update, safe error display and disabled status; Console/DTOs never carry secrets. Lower roles and forged input fail including direct invocation. Disabling does not fetch Graph.
- [ ] Stub Graph for paged success, wrong WABA, disconnected/absent ID, missing status, repeated cursor/hostile link, HTTP failure, timeout, invalid envelope, token rotation and safe diagnostics. Assert no remote registration or message send for **any** case.
- [ ] In real disposable Postgres verify idempotent/concurrent enrolment, disabled default, immediate disable, re-enable with new membership proof, negative/fractional priority rejection, enable/disable conflicting edits, immutable account, and no writes to routes, route members or pending clarification on disable. Two admitted checkouts at one shop for the same phone share one route. Their existing memberships must survive priority edits and disabling allocation; Admin never caps the number of eligible checkouts.
- [ ] Exercise existing singleton enrolment with an active pre-cutover recovery and standalone message; assert blocked including grant-of-permit vs enrolment race. Exercise same recipient with expired-only checkout evidence before and after the sweep; assert no enrolment conflict. Seed a different pool sender and show mixed-use checks do not block it solely because an unrelated legacy singleton is busy.
- [ ] Document numbered operator steps for enrol, enable, order and drain. Record changed paths, database pin and actual provider-fixture/loopback DB cleanup in the Completion Report.

## Validation

Add scripts `test:sender-pool:unit` = `tsx --test tests/unit/whatsapp-sender-pool.test.ts tests/unit/whatsapp-sender-pool-components.test.tsx`, and `test:sender-pool:postgres` = `npm run prisma:generate && node scripts/test-whatsapp-sender-pool-postgres.mjs`. Reuse the isolated pg17/pgvector pattern in `scripts/test-arch047-admin-meta-postgres.mjs` with the new integration test, migration and finally cleanup. From the prepared Admin worktree run:

```bash
npm ci
npm run prisma:generate
npm run test:sender-pool:unit
npm run test:sender-pool:postgres
npx tsc --noEmit
npm run lint
npm run build
git diff --check
```

Use only invocation-owned disposable DB/Redis or mock services for checks. Record actual results for any independently reproducible existing baseline under the normal repository protocol.

## Implementation Notes

Defined but not materialised. Run `/moda-task ARCH-076-ADMIN-001` only after accepted Database schema is available on the intended dependency pin. Use the canonical prepared packet, mirrored parent/implementation branches, and finish with architect review. Do not contact production, provision phones, deploy, enable pool rows, send messages or merge main as part of authorship/validation. Stop with path, error and command if the accepted schema/credential contract differs from this definition. Blocking provider failures on the running application are typed operator outcomes, not a reason to change architecture.

After Work Items, Acceptance Criteria and Validation pass, set status to review, deliver the Completion Report to `moda_architect` and stop. Do not run terminal system validation as part of this task.

## Completion Report

### Status

Not Started.

### Files Changed

Pending implementation.

### Work Completed

Pending implementation. Record launcher-resolved parent and implementation worktrees, mirrored branch names, start sync and final SHAs, consumer submodule pin where applicable, and cleanup.

### Validation Results

Pending. Record exact commands, exit status, container IDs, cleanup, failures and warnings. Report baseline issues separately from this change.

### Deviations

None recorded.

### Assumptions

None recorded.

### Unresolved Issues

None recorded.

### Architectural Concerns

None recorded.

## Architect Review

### Review Status

Pending.

### Review Notes

Pending.

### Reviewed Files

Pending.

### Validation Reviewed

Pending.

### Architecture Conformance

Pending.

### Follow-up

Pending.
