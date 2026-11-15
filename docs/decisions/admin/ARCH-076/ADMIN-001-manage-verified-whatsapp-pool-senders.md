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
status: review
priority: 20
executor: codex
claimed_at: 2026-11-15T14:04:09Z
attempt: 1
depends_on: ["ARCH-076-DATABASE-001"]
enables: []
created: 2026-11-13
updated: 2026-11-15
---

# Manage verified WhatsApp pool senders in platform configuration

## Architecture

[ARCH-076](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md), coordinated by `moda_architect`.

## Objective

Expose verified operator enrolment, priority and eligibility for the registered Moda sender pool in the existing platform configuration surface.

## Context

Preserved from original local commit `59705bb589342f31054e6c1fd011dacf9d495ae6` under root-authorized ARCH-076 collision correction. Defined portable design only; Pending/unclaimed until current-main compatibility review and explicit architect promotion. No runtime implementation or launch is authorized by preservation.

Implement the operator inventory in [ARCH-076](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md). A server-authenticated SUPER_ADMIN enrols already registered Meta phone-number IDs under Moda's current WhatsApp Business Account (WABA), assigns priority and can disable allocation to a number. Admin never assigns numbers to checkouts. The single existing encrypted sender configuration supplies the server-side account and token. The inventory contains only non-secret IDs, status, priority and timestamps. Storefront and merchant checkout policy governs how many distinct baskets can coexist. When several recoveries share one shop and customer, Background attaches them to their existing sender route. A different shop receives an independent route; when every enabled sender is occupied, Background shares the sender serving the fewest active shops for that recipient, under the canonical architecture ranking. Admin does not enforce one shop per physical sender. Closing the final active member ends that route. Admin only manages the available number inventory and never imposes a per-shop basket limit.

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

- [x] Wire the authorised page, operator controls, input validation, localized presentation and typed Server Actions.
- [x] Verify connected phone membership on the trusted WABA and handle unavailable, malformed, duplicate, stale and rotated configuration deterministically.
- [x] Implement DB membership locking, duplicate enrolment, legacy cutover preflight, guarded setting edits and original-error diagnostics.
- [x] Write and run all declared unit, component, disposable PG and baseline checks. Document operator use and publish the parent and implementation task report for architect review.

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

- [x] Demonstrate the actual authenticated route, form and server actions. Include empty/missing config, stable tie-break, stale update, safe error display and disabled status; Console/DTOs never carry secrets. Lower roles and forged input fail including direct invocation. Disabling does not fetch Graph.
- [x] Stub Graph for paged success, wrong WABA, disconnected/absent ID, missing status, repeated cursor/hostile link, HTTP failure, timeout, invalid envelope, token rotation and safe diagnostics. Assert no remote registration or message send for **any** case.
- [x] In real disposable Postgres verify idempotent/concurrent enrolment, disabled default, immediate disable, re-enable with new membership proof, negative/fractional priority rejection, enable/disable conflicting edits, immutable account, and no writes to routes, route members or pending clarification on disable. Two admitted checkouts at one shop for the same phone share one route. Their existing memberships must survive priority edits and disabling allocation; Admin never caps the number of eligible checkouts.
- [x] Exercise existing singleton enrolment with an active pre-cutover recovery and standalone message; assert blocked including grant-of-permit vs enrolment race. Exercise same recipient with expired-only checkout evidence before and after the sweep; assert no enrolment conflict. Seed a different pool sender and show mixed-use checks do not block it solely because an unrelated legacy singleton is busy.
- [x] Document numbered operator steps for enrol, enable, order and drain. Record changed paths, database pin and actual provider-fixture/loopback DB cleanup in the Completion Report.

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

Executed the launcher-prepared attempt 1 claim in the canonical isolated worktrees below. The accepted D001 schema was consumed at its exact main commit with root authorization; no schema was authored here. The active-pool appendix was reconciled from current parent main before reporting. No production/provider invocation, deployment, pool activation, system validation or main merge was performed.

After Work Items, Acceptance Criteria and Validation pass, set status to review, deliver the Completion Report to `moda_architect` and stop. Do not run terminal system validation as part of this task.

## Completion Report

### Status

Ready for Review. Implementation [PR 104](https://github.com/kodjobaah/moda-interact-admin/pull/104), commit `2c48d70449b1ce1fb8c9f0d8a8645e988da10616`, is pushed on `task/ARCH-076-ADMIN-001`. Parent review submission uses the same branch name and preserves the original claim metadata.

### Files Changed

- Protected platform-configuration page, new sender-pool Client Component and authenticated Server Action; English catalogue/required keys and numbered README operator steps.
- Server inventory service/core, strict Admin-local DTO/input validator, provider membership reader, legacy-use preflight, shared environment fence and bounded Shared-logger diagnostic adapter.
- Extracted the existing SUPER_ADMIN guard without changing its policy. Narrow `messaging.sender` secret-writer integration takes the same environment fence, guards active WABA transitions and retains real CAS/redacted durable audit.
- Unit/component/service-entrypoint tests, disposable PostgreSQL tests/harness and two package scripts. Source nested `database` gitlink consumes accepted D001; no schema, Shared package or parent implementation gitlink edits.

### Work Completed

- Prepared canonical root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-076-ADMIN-001`; source worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-076-ADMIN-001`. Both use `task/ARCH-076-ADMIN-001`.
- Launcher claim `e0796e1734d900c9d6d723f330f587611c976b16` was already prepared. Initial parent main was `a01d784df230ff1a74b50b798acc1e7dcf867f8a`; initial source main was `e4e4b0a2b5400f5cb7a49014dae17f3822eb1cd2`. Parent fetched/merged current `origin/main` at the reporting boundary, preserving attempt/executor/claimed_at and the authoritative active-pool clarification.
- Root explicitly authorized source nested Database consumption from packet pin `2e14f8668346dfc135aa12f8d1fbc94e05c12ce7` to accepted D001 main `a7c204618c6b0ad83952a7b661482cfd03acf899`. Prisma Client was generated from this real schema.
- New registration verifies exact CONNECTED membership on the saved sealed WABA, starts disabled, and only explicit fresh verification enables allocation. Inventory identities stay immutable; settings edits are CAS guarded and exact replays do not rewrite state.
- Real short transactions serialize configuration/enrolment/drain changes; Graph calls remain outside locks. Active last drain/direct switch to an empty WABA are refused. Priority/non-final drain remain Graph-free during outages; unreadable potentially-final identity fails closed; revoke/set bootstrap remains available.
- Legacy dispatch proof, effectively expired baskets, standalone rolling-window/in-flight history and permit/enrolment races are checked without modifying conversations/routes/assignments/clarifications. UTC handling is explicit for historical naive timestamps. Same-shop two-basket memberships survive edits/drain byte-for-byte.
- Credentials never enter client DTOs or inventory. Provider diagnostics redact tokens/URLs and retain bounded safe code/subcode/trace and causes; malformed decrypted JSON cannot appear in logs.

### Validation Results

All final commands below passed in the prepared source worktree:

| Command | Result |
| --- | --- |
| `npm ci` | Exit 0; existing audit advisories reported, no dependency upgrade. |
| `npm run prisma:generate` | Exit 0 against accepted D001 pin. |
| `npm run test:sender-pool:unit` | Exit 0, 12/12 including rendered component controls, provider fixtures, secret/AAD safety and actual public service-entry execution of auth plus real SUPER_ADMIN policy before DB access. |
| `npm run test:arch043-admin-secrets:unit` | Exit 0, existing 16/16. |
| `npm run test:sender-pool:postgres` | Exit 0, 10/10; all recorded migrations on invocation-owned pg17/pgvector. Real locks, membership race, CAS/rotation, final drains/switch race, zero/full-int/inclusive expiry including non-UTC session, standalone proof and pinned-state preservation. |
| `npx tsc --noEmit` | Exit 0. |
| `npm run lint` | Exit 0, no errors; one unchanged nested `database/eslint.config.mjs` anonymous-default-export warning. That file is unchanged across both Database pins. |
| `npm run build` | Exit 0, optimized production build. Existing queue-monitor/BullMQ optional `@valkey/valkey-glide` warning; queue code and dependency lockfile were not modified. |
| `git diff --check` / staged equivalent | Exit 0. |

Final fixture: `moda-arch076-sender-pool-c4769521-0a78-4c49-b89a-4a06280aea4b`, container ID `5e70b5f6e00b93a648a4e90c8bf2b7f2c34b8f3d60abf4e42c4330bd2b53af22`; Docker destroy event confirms cleanup. Harness finally removes its generated bundle and container. Earlier failing harness attempts also cleaned up. Initial failures were esbuild synchronous-plugin collection and invalid legacy dispatch/clock-boundary fixtures; the final suite uses async bundling, the real required dispatch tuple and DB-safe timestamp fixture. PostgreSQL advisory locks return a supported scalar through a MATERIALIZED CTE, and are exercised rather than mocked.

### Deviations

- Root approved using the established `scripts/test-unit.mjs` ESM bundler instead of the task's direct `tsx --test` spelling: current Shared exports are import-only. No global module conditions, package/dependency change or substitute contracts.
- Disposable PostgreSQL harness substitutes only the HTTP Auth.js module with fail-closed functions to avoid Next's extensionless runtime resolver outside Next. Trusted workflows retain real role checks, real PostgreSQL locks and existing secret CAS/audit. Independently, unit tests execute the actual public service entrypoints with injected authentication and the real SUPER_ADMIN policy; browser identity/OAuth itself is outside this fixture.
- Root coordinated resource windows; canonical bootstrap selected the workspace Node version. One retry reused the already-verified runtime at root's then-explicit instruction; later launches returned to canonical bootstrap in a persistent shell when that instruction was retracted. No Node/dependency/version change.

### Assumptions

The current sealed sender record and verified inventory define active-pool state exactly as the accepted appendix. Operator cutover must retire unfenced workers and drain provider I/O; this task does not perform rollout or live enrollment.

### Unresolved Issues

None within this task. Coordinated Background/runtime rollout, test-first verification and deferred SYSTEM-TEST remain with their owning tasks/root.

### Architectural Concerns

No new cross-service contracts, schema or Shared release. The optional BullMQ build warning and nested Database lint warning are unrelated unchanged paths; no unrelated fixes were introduced.

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

## Reconciled active-pool configuration invariant

For the current canonical shared-number design, sender occupancy is not exhaustion. Admin must reject disabling the last enabled verified sender of an active WABA and switching active messaging configuration to a WABA with no enabled verified sender. Serialize these checks with competing inventory/configuration writes; test concurrent disables and WABA switch against inventory enable/drain. Preserve the existing credential format and authenticated server-only boundary. An empty inventory is permitted before coordinated activation. A drained sender retains its original live and historical routes. The Active-pool predicate and bootstrap compatibility section below is the controlling transition rule, including initial/revoked bootstrap.


## Explicit storage amendment — 15 November 2026

Five sender entities exist: WhatsAppPoolSender, RecoverySenderThread, RecoverySenderRoute, RecoverySenderAssignment and RecoveryBasketRoutingTurn. Admin inventory operations manage only WhatsAppPoolSender; Background owns thread/route/assignment lifecycle. Drain preserves pinned conversations; no allowance/credit dependency.

Inventory verification contract: populate verifiedAt only after successful provider CONNECTED/WABA verification at enrollment/enablement. New inventory remains allocationEnabled=false until explicit enabled verification. No unverified default timestamp is proof.

## Active-pool predicate and bootstrap compatibility

This is the authoritative interpretation of the active-pool invariant; it supersedes a blanket prohibition on zero inventory or all enabled credential writes. A pool is active exactly when the current environment's messaging.sender is a valid enabled sealed secret AND its WABA has at least one enabled, provider-verified inventory row. No activation column is introduced.

- Reject an inventory change that would take that active WABA from one enabled verified sender to zero. Draining a non-final sender and priority-only changes remain Graph-free. Existing routes/history remain pinned even on drained inventory.
- Reject a direct enabled messaging.sender WABA switch from an active pool to a target WABA with no enabled verified sender. Rotation within the same active WABA preserves the pool; secret values remain protected and normal CAS/audit applies.
- Initial/zero/inactive bootstrap may save credentials before inventory exists, then provider-verify enrollment (disabled row), then provider-verify enable. Zero inventory is a Background configuration/repair hold, not permission to send or a fabricated active pool. Deliberate authorized revoke→set replacement uses the same bootstrap path; existing secret-service revocation stores DISABLED_SECRET and does not preserve editable staged plaintext. Do not invent an enabled flag inside the existing payload or require an impossible enrollment before credentials exist.
- Credential/provider outage does not block priority-only changes or provably non-final drains. If the current sealed identity cannot be verified, refuse a potentially-final drain with bounded CONFIGURATION_UNAVAILABLE; never guess the WABA or expose decrypted values. Authorized secret revoke remains available for shutdown/security response.

Fence all inventory mutations that alter enablement and messaging.sender set/update/rotate/revoke with one environment-scoped transaction advisory key `whatsapp-pool-configuration:<environment>`. Take it first in the final short transaction, before existing phone-membership advisory lock (when needed), configuration row lock and deterministic inventory row locks. Read the current actual configuration and inventory under the fence, compute before/after active transition and CAS outcome, then write/audit atomically. This also serializes a missing first config row; locking only an existing row is insufficient. Membership Graph lookup stays outside locks; recheck snapshot version/WABA after acquiring the fence, so rotated credentials cannot authorize a stale enrollment/enable. Never hold network work inside a DB transaction. Use this same lock ordering in secret-service and inventory paths; preserve the existing non-pooled membership fence.

Required owner tests: initial credentials→zero inventory→disabled enroll→verified enable; deliberate revoke→set new WABA bootstrap; active direct switch to empty target refusal; last drain refusal; two concurrent drains cannot both succeed; switch versus enable/drain races; provider outage permits priority/non-final drain; unreadable sealed identity rejects potentially-final drain; stale Graph verification after credential rotation; audit/CAS and absence of plaintext/secrets in errors. No live provider calls. This clarification does not add a sender-runtime activation feature or couple routing to renewal.
