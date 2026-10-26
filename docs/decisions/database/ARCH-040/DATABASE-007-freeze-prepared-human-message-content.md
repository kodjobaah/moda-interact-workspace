---
id: ARCH-040-DATABASE-007
architecture_id: ARCH-040
title: Persist a set-once prepared HUMAN_TEXT body and align moderation identity
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 15
executor: developer
claimed_at: 2026-10-26T12:10:12Z
attempt: 2
depends_on:
  - ARCH-040-DATABASE-001
  - ARCH-040-DATABASE-005
  - ARCH-040-DATABASE-006
enables:
  - ARCH-047-BACKGROUND-009
created: 2026-10-26
updated: 2026-10-26
---

# Persist a set-once prepared HUMAN_TEXT body and align moderation identity

## Architecture

- Architecture: `ARCH-040` — `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`.
- Cross-architecture consumer: `ARCH-047-BACKGROUND-009`, which renders a Moda Admin-authored HUMAN/SHARED conversation wrapper.
- Coordinator: `moda_architect`; owner: `moda_database` in `moda-interact-database/`.
- **Task definition:** materialised on parent branch `task/ARCH-040-DATABASE-007` in commit `78413186`. This task is independent of the in-progress BG009 implementation attempt.

## Developer Ownership Amendment

On 2026-10-26, `/moda_developer_create ARCH-040-DATABASE-007` was invoked to take over this ready agent-owned task. Execution and completion modes are now `developer`; `assigned_agent: moda_database`, coordinator, repository ownership, task scope, dependencies, requirements and acceptance criteria are unchanged. The task remains Ready at Attempt 0 until the canonical implementation worktree is prepared and the developer claim is committed.

## Objective

Extend the **existing** durable `whatsapp.MerchantConversationSendCommand` record with a set-once customer-visible HUMAN_TEXT body and wrapper provenance. Make that prepared text—not immutable original `textBody`—the exact database-validated HUMAN_COMMAND/TEXT moderation subject, while preserving every existing accepted-command, tenant, lease, template-parameter and one-way provider-permit protection.

## Context

The inspected 26 October BG009 worktree has:

- The command's original `textBody` and `payloadSha256` stored as immutable merchant intent.
- `whatsapp.arch040_command_guard()` (last defined by `20261017214500_arch040_remove_outreach_sequence_policy`) rejecting any mutation of accepted command identity/payload.
- `whatsapp.arch040_moderation_subject_guard()` (last defined by `20261018092000_arch040_moderation_template_content_digest`) checking HUMAN_COMMAND/TEXT `contentSha256` against SHA-256 of `command.textBody`.
- Background final admission and provider sending likewise reading `command.textBody`.

An ARCH-047 wrapper changes the **outbound content**, not the accepted merchant request. Overwriting `textBody`, allowing an in-memory-only prepared body, or moderating raw text and subsequently appending a footer would break idempotency or moderation evidence. Do **not** introduce another message table or modify accepted historical migrations.

## Scope

Exactly one Database-owned additive migration, Prisma fields, focused validators and isolated PostgreSQL proofs:

```text
prisma/schema.prisma
prisma/migrations/20261026080000_arch040_prepared_human_message_content/migration.sql
scripts/validate-arch040-human-prepared-schema.mjs
scripts/test-arch040-human-prepared-postgres.mjs
package.json                    (only new test script entries)
```

Allow additional *focused* test fixture/helpers only where required by the existing repository test harness. Keep schema changes inside the existing `whatsapp` model; do not create `PreparedMessage`, wrapper, audit or status tables.

## Out of Scope

- No BG009 wrapper rendering, merchant dispatcher changes, moderation service changes or final WhatsApp sending code. Those remain `ARCH-047-BACKGROUND-009`.
- No AI/AGENT/AUTOMATION moderation redesign, no change to post-window `RECOVERY_FOLLOW_UP_TEMPLATE` content digest, sequence-two credit, consent, STOP, HUMAN control, provider retries or provider-UNKNOWN compensation.
- No database-enforced wrapper eligibility, Admin publication policy, template type, service-window/consent rules, or source-text business validation. These belong in Background application services.
- No new Shared runtime contract. No changes to `docs/decisions/**/_index.md` or previously accepted SQL migration files.

## Requirements

### R1 — Exact Prisma additions

Inside the **existing** `MerchantConversationSendCommand` model, retain all original fields, relations, keys, indexes and `@@schema("whatsapp")`, and add exactly:

```prisma
preparedTextBody       String?   @db.Text
preparedWrapperEvidence Json?    @db.JsonB
preparedAt             DateTime? @db.Timestamptz(3)
```

`textBody` remains the **original immutable merchant text**. `payloadSha256` remains the **accepted request's original** digest and must not be recalculated from the prepared output. `preparedTextBody` is the complete customer-visible text, including any wrapper; it must also be populated with the unmodified raw text when no wrapper is configured. `preparedWrapperEvidence` holds bounded JSON provenance, not a copy of the customer message. `preparedAt` identifies the first durable freeze. Do not backfill already sent/terminal commands or alter a provider permit.

### R2 — Forward-only SQL migration

Create `20261026080000_arch040_prepared_human_message_content/migration.sql` (or, only if the canonical repository already uses that exact timestamp, the next available monotonically ordered timestamp documented in the Completion Report). Add three nullable columns to `whatsapp."MerchantConversationSendCommand"` with PostgreSQL types `TEXT`, `JSONB`, and `TIMESTAMPTZ(3)` respectively, **without defaults**.

Replace only the two currently installed functions using `CREATE OR REPLACE FUNCTION` in the new migration. Retain their original unrelated logic and existing trigger attachments:

1. `whatsapp.arch040_command_guard()` — preserve unchanged checks of same-recovery ownership, accepted payload identity (`textBody`, `payloadSha256`, idempotency/recipient/command kind), set-once outbound-message identity, provider-permit irreversibility, dispatch-attempt monotonicity, lease/reclaim and terminal state transitions.
2. `whatsapp.arch040_moderation_subject_guard()` — preserve all current subject/tenant checks and existing non-HUMAN_COMMAND moderation paths, including template-parameter digest handling.

Do not drop/recreate the command or moderation tables, weaken existing triggers, or modify the old migrations to change their historical contract.

### R3 — Set-once prepared-content integrity

Extend `arch040_command_guard()` only for technical preparation immutability:

- A newly INSERTed accepted command must have `preparedTextBody`, `preparedWrapperEvidence` and `preparedAt` all `NULL`: accepted command is still **raw intent**, not a pre-authorised send.
- For a pre-freeze command, the **first** update may set all three fields together only if `OLD.kind = HUMAN_TEXT`, `OLD.state = CLAIMED`, `OLD.leaseToken IS NOT NULL`, `OLD.leaseExpiresAt > statement_timestamp()`, and `OLD.providerDispatchKey IS NULL`. Reject blank/NULL prepared body, NULL provenance or NULL prepared timestamp at freeze. This is a structural current-claim guard; it does **not** authorise sending or choose a wrapper.
- Once any of these three fields is set, subsequent updates must preserve all three **byte-/value-identically**, even if a lease expires, a retry claims the command, Admin changes the wrapper, or the command becomes FAILED/UNKNOWN/SENT. Replays read the stored prepared body; they never rewrite it.
- If a caller attempts partial preparation, clearing, mutation after set, preparation on a post-window template command, or preparation after provider permit, reject the update with SQLSTATE `23514`.
- The existing accepted original command content fields remain immutable exactly as before. No new lifecycle/check constraint, trigger-driven wrapper selection or per-template rule is authorised.

The implementer must retain and validate the current pre-existing command guard's other cases. **Do not substitute this summary for the full existing function** when constructing the replacement SQL.

### R4 — HUMAN_TEXT moderation digest uses the frozen body

Update only `HUMAN_COMMAND` with `inputKind = TEXT` in `arch040_moderation_subject_guard()`:

- For `kind = HUMAN_TEXT`, look up the command's **non-null** `preparedTextBody` as the authoritative text; reject a new moderation assessment if that field is not yet frozen.
- Compare `NEW.contentSha256` against `encode(sha256(convert_to(preparedTextBody,'UTF8')),'hex')` and reject a mismatch with SQLSTATE `23514`.
- Keep `HUMAN_COMMAND` with `inputKind = TEMPLATE_PARAMETERS` strictly bound to the **existing** `whatsapp.arch040_moderation_template_input_v1` function and its unchanged name/language/parameters digest.
- Keep CUSTOMER/AGENT/AUTOMATION `ConversationMessage` moderation guards, tenant/subject identity, moderation assessment keys and update guards unchanged.

The SQL guard only checks the digest and structural subject identity. Deciding `ALLOW`, `BLOCK`, `REVIEW_REQUIRED`, current policy/model, checkout wrapper activation or service-window eligibility remains application-owned.

### R5 — Migration/rollout boundaries

Existing commands, assessments, message history and provider permits survive untouched. Pending unprepared HUMAN_TEXT commands may be prepared on their **next current, valid claim**; they must not be auto-marked moderated/sent. Pre-migration provider-admitted/terminal commands must never be modified or resent by this migration. The new Background consumer must fail closed on an unprepared new HUMAN_TEXT attempt and preserve historical reconciliation for already-admitted UNKNOWN records. Roll out the migration and regenerate consumers' Prisma Client **before** BG009 performs any prepared-content writes. No one-time backfill, new ledger, or additional PostgreSQL business logic is required.

### R6 — Validation and proof

Implement focused schema/migration validation that checks field types/nullability and the guard branches, rather than merely checking token presence. Add disposable PostgreSQL tests covering:

1. Existing unrelated command creation, accepted-payload immutability, template moderation, shop/recovery linkage, and one-way provider permit continue to pass/fail as before.
2. New accepted HUMAN_TEXT insert has no prepared content; a valid claimed lease may freeze all three fields exactly once; retry with a fresh lease may read unchanged frozen fields.
3. Wrong/expired lease, wrong command kind, partial tuple, blank body, post-permit write and any rewrite/clear of frozen content fail with the intended guard error.
4. New HUMAN_COMMAND/TEXT moderation before freeze fails; after freeze, the SHA-256 of the **original** raw text fails when different, while the SHA-256 of the **complete wrapped body** succeeds. Passthrough with `preparedTextBody = textBody` succeeds through the same TEXT moderation path.
5. Post-window template (`TEMPLATE_PARAMETERS`) moderation hashes exactly the original canonical template-input text; `CUSTOMER_MESSAGE` and AGENT/AUTOMATION assessments are unchanged.
6. Existing assessments, pending commands and original `textBody`/idempotency keys remain unchanged after the additive migration.
7. Fresh migration and migration-upgrade rehearsals run in disposable databases; no production data, shared worktree or existing migration history is rewritten.

## Work Items

- [x] Add the three exact Prisma nullable fields and the additive migration.
- [x] Preserve the existing command guard while adding precise set-once/pre-lease invariants.
- [x] Update the HUMAN_COMMAND/TEXT moderation guard to use only frozen prepared content.
- [x] Add focused validators and PostgreSQL tests including regression and negative cases from R6.
- [x] Record migration, changed files, exact test commands, DB version, branch/worktree evidence and deviations in the Completion Report.

## Interfaces / Contracts

**Database port used by `ARCH-047-BACKGROUND-009`:**

```text
MerchantConversationSendCommand.id             stable accepted command ID
MerchantConversationSendCommand.textBody       immutable merchant-authored request
MerchantConversationSendCommand.payloadSha256  unchanged original request identity
MerchantConversationSendCommand.preparedTextBody    nullable until once-only freeze
MerchantConversationSendCommand.preparedWrapperEvidence  nullable until freeze
MerchantConversationSendCommand.preparedAt          nullable until freeze
ConversationModerationAssessment.subject = HUMAN_COMMAND
ConversationModerationAssessment.inputKind = TEXT
ConversationModerationAssessment.contentSha256 = SHA256(UTF8(preparedTextBody))
```

Example (application-owned JSONB, **not a DB-enforced business schema**):

```json
{
  "schemaVersion": 1,
  "outcome": "RENDERED",
  "wrapperDefinitionId": "definition-id",
  "localeId": "locale-id",
  "audience": "HUMAN",
  "slotEditVersion": 3,
  "applicationKey": "stable-bg005-application-key",
  "bodySha256": "sha256-of-complete-preparedTextBody"
}
```

For no wrapper, application writes `{"schemaVersion":1,"outcome":"PASSTHROUGH","reason":"NOT_CONFIGURED","bodySha256":"..."}` and freezes raw content through the same moderation contract. The database does not parse or validate this JSONB business structure. The current Background command lease is the CAS authority for initial freeze; normal application modules own atomic `UPDATE ... RETURNING` and status error handling.

## Dependencies

- `ARCH-040-DATABASE-001` — Complete.
- `ARCH-040-DATABASE-005` — Complete.
- `ARCH-040-DATABASE-006` — Complete.

## Enables

- `ARCH-047-BACKGROUND-009` can be returned to `ready` after this task is accepted `complete` and the Database submodule/client is updated in the implementation worktree.

## Acceptance Criteria

- [x] Exact three-field additive persistence and Prisma relation stability, no extra table.
- [x] Original merchant intent and idempotency remain immutable; set-once prepared body/provenance/timestamp cannot be rewritten or cleared.
- [x] New HUMAN_COMMAND/TEXT moderation digest is bound to the full prepared body and cannot be inserted against an unprepared command; template and message moderation are unchanged.
- [x] Database rejects technical invalid writes but does not choose/validate wrappers, moderation outcomes, consent, 24-hour windows or send eligibility.
- [x] Fresh and upgrade migrations plus direct PostgreSQL positive/negative cases pass; no unrelated existing record or trigger semantics regress.
- [ ] DB Completion Report contains dedicated worktree/branch/synchronisation, exact validation and migration evidence for architect review. Technical validation and paths are evidenced; the Attempt 2 launcher preparation/synchronisation packet is not present in the submitted materials.

## Validation

- [x] `npm run prisma:validate` and `npm run prisma:generate` using scripts declared by `moda-interact-database/package.json`.
- [x] Add and pass `npm run test:arch040-human-prepared-schema` (focused exact schema/migration validator).
- [x] Add and pass `npm run test:arch040-human-prepared:postgres` (fresh, upgrade and negative SQL cases in disposable PostgreSQL).
- [x] Re-run the repository's existing focused ARCH-040 human command/moderation regression commands as discovered in `package.json`; record actual names/results rather than assuming a uniform test script.
- [x] `git diff --check` and inspect changes against the exact task scope.

## Stop Condition

After schema, migration, integration tests and the Completion Report are finished, mark `review`, return the independently reviewable database implementation and parent task branch to `moda_architect`, and STOP. Do not alter BG009 source, author new Background modules, merge task branches, mark yourself Complete or update any `docs/decisions/**/_index.md`.

## Implementation Notes

Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/developer-task-workflow.md` and the canonical `/moda-task` launcher. Use matching dedicated parent/implementation worktrees under `task/ARCH-040-DATABASE-007`; never use a shared/default checkout or a previous task worktree as the task root. Use the established Prisma/migration/test conventions; keep exact guards narrowly scoped; if a discrepancy would require cross-repository changes, return it to the architect rather than implementing another repository's source.

## Completion Report

### Status

In Progress — Attempt 2 claimed by developer at 2026-10-26T12:10:12Z. All task-required technical validation passed in the 12:30–12:35 UTC rerun; the original Attempt 2 launcher preparation/synchronisation evidence remains unverified. Attempt 1 review history is preserved below.

### Files Changed

Six files in `moda-interact-database/` (combined implementation commits):

- `prisma/schema.prisma`
- `prisma/migrations/20261026080000_arch040_prepared_human_message_content/migration.sql` (new)
- `scripts/validate-arch040-human-prepared-schema.mjs` (new)
- `scripts/test-arch040-human-prepared-postgres.mjs` (new; corrected in `12102f0`)
- `scripts/test-arch040-moderation-postgres.mjs` (focused existing-fixture adjustment)
- `package.json` (task-specific validation scripts)

No existing historical migration, other service, or domain `_index.md` was intentionally changed.

### Work Completed

- Added nullable `preparedTextBody` (`TEXT`), `preparedWrapperEvidence` (`JSONB`) and `preparedAt` (`TIMESTAMPTZ(3)`) to the existing `whatsapp.MerchantConversationSendCommand` model and one forward-only SQL migration; original `textBody` and `payloadSha256` remain the accepted merchant intent.
- Preserved the existing command guard and added a tightly scoped first-write freeze under a current `CLAIMED` lease, followed by immutable replay/retry behavior. Invalid partial, blank, wrong-kind, expired-lease, post-permit and rewrite attempts fail with SQLSTATE `23514`.
- Bound `HUMAN_COMMAND`/`TEXT` moderation to SHA-256 of the complete, durably prepared body, not the raw merchant text; retained the existing template-parameter and nonhuman-message moderation contracts.
- Added structural validation and disposable PostgreSQL 17 fresh-install/upgrade exercises for command history, moderation evidence, terminal and provider-permit invariants, tenant isolation, contention and concurrency.
- Corrected the test to assert the command/message dispatch-key mismatch separately from the one-way provider-permit timestamp immutability guard. No production migration or trigger changes were needed for that correction.

### Validation Results

Executed in the developer's dedicated Database task worktree, as recorded in the supplied terminal logs dated **26 October 2026**:

| Check | Result / Evidence |
| --- | --- |
| `npm ci` | Completed; npm reported five high-severity audit advisories, not investigated within this task's scope. |
| `npm run prisma:validate` | Passed; Prisma schema validated. |
| `npm run prisma:generate` | Passed; generated Prisma Client v6.19.3. |
| `npm run test:arch040-human-prepared-schema` | Passed exact columns, migration order, trigger-preservation and moderation-guard structural checks. |
| `npm run test:arch040-human-prepared:postgres` | **Passed both modes in final 11:39–11:41 run** on disposable PostgreSQL **17.11**: fresh install and upgrade; tested frozen-body moderation, lease and provider permits, historical upgrade preservation and concurrent first-writer-wins. Expected `23514` errors in negative test cases were asserted. |
| `npm run test:arch040-recovery-human-handover` | Passed structural contract checks. |
| `npm run test:arch040-moderation-schema` | Passed structural contract checks. |
| `npm run test:arch040-follow-up-release-schema` | Passed structural contract checks. |
| `npm run test:arch040-recovery-human-handover:postgres:fresh` | Passed full existing fresh PostgreSQL regression suite. |
| `npm run test:arch040-moderation:postgres:fresh` | Passed full existing moderation PostgreSQL regression suite. |
| `npm run test:arch040-follow-up-release:postgres:fresh` | Passed full existing follow-up PostgreSQL regression suite. |
| `git apply --check --whitespace=error-all` and `git diff --check` | Patch checks reported successful; no whitespace errors were shown. |
| Git publication | Initial `26b3cd2` and correction `12102f0` pushed to implementation `task/ARCH-040-DATABASE-007`; final push confirmed in the 11:41 terminal log. |
| Reviewer rerun (2026-10-26) | From the canonical implementation worktree, `npm run prisma:validate`, `npm run prisma:generate`, `npm run test:arch040-human-prepared-schema`, `npm run test:arch040-human-prepared:postgres` (fresh and upgrade), `npm run test:arch040-recovery-human-handover`, `npm run test:arch040-moderation-schema`, `npm run test:arch040-follow-up-release-schema`, `npm run test:arch040-recovery-human-handover:postgres:fresh`, `npm run test:arch040-moderation:postgres:fresh`, `npm run test:arch040-follow-up-release:postgres:fresh`, and `git diff --check origin/main...HEAD` all completed successfully. Expected SQL errors in negative PostgreSQL cases were asserted by the harness; all four migration suites reported PASS. |
| Attempt 2 rerun (2026-10-26, 12:30–12:35 UTC; supplied `typescript(20261026-123521)`) | PASS: `prisma:validate`, `prisma:generate`, `test:arch040-human-prepared-schema`, `test:arch040-human-prepared:postgres` (PostgreSQL 17.11 fresh and upgrade), the three ARCH-040 structural regression scripts, the three PostgreSQL fresh regression scripts, and `git diff --check origin/main...HEAD` (no whitespace errors). Deliberate negative-case SQL errors are followed by harness PASS. No production change is indicated by this rerun. |
| Attempt 2 launcher/worktree preparation (claimed at 12:10:12 UTC) | **NOT EVIDENCED** in the supplied 12:30–12:35 terminal log or latest workspace ZIP: exact prepared execution packet, parent and implementation branch fetch/fast-forward/main sync, and recursive submodule status at attempt start. Current archive paths and a successful rerun do not establish these historical steps. |

`npm test`, `npm run typecheck`, `npm run build` and `npm run test:arch047-follow-up:postgres` are not declared scripts in this Database repository; their missing-script messages in an exploratory run are not failures of the task-defined validations. `npm run lint` was launched without a reported lint failure, but is not counted as one of the task's required acceptance checks.

### Deviations

- One focused change to the existing `scripts/test-arch040-moderation-postgres.mjs` fixture was necessary to comply with the new prepared HUMAN_TEXT moderation contract; production scope remains unchanged.
- The provider-permit test was refined in a second patch because the database first rejects a divergent dispatch key through an existing earlier guard. The corrected test separately verifies dispatch-key consistency and one-way provider-permit immutability. Both PostgreSQL modes passed thereafter.

### Assumptions

- The task executes in the pre-production development environment described by the parent architecture; no historical accepted migration is rewritten and no existing command is backfilled.
- BG009 and its consumers will regenerate their Prisma Client from the accepted Database version before attempting prepared HUMAN_TEXT writes. This handoff does not implement those consumers.

### Unresolved Issues

- **Attempt 2 start-of-attempt evidence pending:** The original Attempt 1 launcher/synchronisation evidence was not retained (as documented in the preserved Changes Requested review). Attempt 2 was claimed at `2026-10-26T12:10:12Z`, but the newly provided terminal recording begins around 12:30 with tests. It does not show the canonical `/moda_developer_create` preparation packet, both worktrees' synchronized branch/HEAD state, or recursive implementation submodule status for the start of Attempt 2. Provide the *actual* launcher/claim output from that invocation if retained. If it was not retained, return this evidence gap to the authorised reviewer for the appropriate next attempt; do not reconstruct or backdate the missing record. The `review` transition remains gated on this evidence.
- Application-level BG009 wrapper rendering, fail-closed final send, and recompiled Prisma consumer are outside this task and remain gated on Database acceptance and developer-controlled completion.

### Architectural Concerns

None identified within Database ownership. Preserve the cross-architecture `ARCH-047-BACKGROUND-009` dependency: do not promote it until `ARCH-040-DATABASE-007` is architect-accepted and explicitly marked `complete` by the developer.

## Architect Review

### Review Status

Pending — no implementation to review.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending implementation.

### Follow-up

After a passing review and explicit developer completion, re-gate `ARCH-047-BACKGROUND-009` on this task's `status: complete` and hand it back to its configured developer execution path.

## Developer Self-Review - Changes Requested (Attempt 1)

### Review Decision

The implementation diff is limited to the six Database-owned files specified by the task. The new SQL migration adds exactly the three nullable columns, replaces only the two existing guard functions, and the schema validator reconstructs the prior function bodies after reversing the authorized changes to verify preservation of unrelated guard logic. The disposable PostgreSQL tests cover fresh and upgrade migrations, set-once concurrent freeze, lease and permit denial cases, prepared-body moderation digests, passthrough, templates, nonhuman moderation and historical-row preservation. The required technical validations passed both in the submitted evidence and in a reviewer rerun.

Review is nevertheless **Changes Requested** because the task's required physical worktree/start-of-attempt evidence is incomplete. The Completion Report expressly states that the launcher preparation packet and start-of-attempt parent/submodule synchronization record were not retained. Current route resolution, clean branches and current test results cannot prove that historical start condition.

### Required Correction

Use the next canonical `/moda_developer_create ARCH-040-DATABASE-007` attempt and retain its exact launcher-resolved preparation/claim output, parent and implementation synchronization results, and recursive submodule status. Rerun the task-required validations from the canonical implementation worktree after that synchronization and record the actual evidence in the Completion Report. Keep the implementation unchanged unless those checks reveal a concrete defect. Do not claim or recreate historical Attempt 1 evidence.

### Validation Reviewed

- **PASS** — `npm run prisma:validate` and `npm run prisma:generate`.
- **PASS** — `npm run test:arch040-human-prepared-schema`.
- **PASS** — `npm run test:arch040-human-prepared:postgres`; fresh and upgrade PostgreSQL migration/behavior suites passed.
- **PASS** — `npm run test:arch040-recovery-human-handover`, `npm run test:arch040-moderation-schema`, and `npm run test:arch040-follow-up-release-schema`.
- **PASS** — `npm run test:arch040-recovery-human-handover:postgres:fresh`, `npm run test:arch040-moderation:postgres:fresh`, and `npm run test:arch040-follow-up-release:postgres:fresh`.
- **PASS** — `git diff --check origin/main...HEAD`; implementation diff is six task-scoped files, clean and published at `12102f0b611973b1436f4c0d4ec33f3e15fa9a78`; parent report branch was clean and published at `a791e34647a03d48fc93e2332932f336f4dc8d5c` before this review update.
- **NOT EVIDENCED** — Attempt 1 canonical launcher packet and start-of-attempt parent/implementation synchronization plus recursive submodule proof.

### State Transition

Returned to `ready`; `executor: null`, `claimed_at: null`, Attempt 1 unchanged. The parent task branch will be committed and pushed with this review decision. No implementation change or merge to `main` was made by the review.
