# U1 deep dive: API Database dependency and ARCH-055 integration

Date: 3 November 2026. Reviewed export: `moda-interact-workspace(20261103-212722).zip`.

## Decision

**The smallest correction is to reconcile the API's nested Database dependency with the accepted ARCH-055 Database tree and regenerate the API client through its normal build path.** The exported API source already uses the two new fields, while its exported `database/prisma/schema.prisma` and migration tree predate them. The canonical Database, Background, Shopify app (`moda-interact`), and Admin copies have the same new schema and migration bytes. No further schema addition or producer field-format change is indicated by this focused review.

That correction closes the observed source/dependency mismatch; it does not by itself prove a compatible installed database or a completed deployment. The existing contract also requires the three forward migrations, coordinated producer/consumer rollout, focused migration-backed validation, and the terminal system task. In particular, manually adding two model fields would omit the REST-read guard correction, historical command backfill, and original-intake uniqueness contract.

The ZIP has no usable Git metadata for the inspected repositories. It therefore cannot distinguish an old recorded API gitlink from a correct recorded gitlink whose exported nested checkout was stale. The handoff below explicitly separates those cases. This review changes no application code, schema, migration, task status, submodule pointer, branch, or deployment.

## 1. Reproducible observations

Run the dependency-free audit from the analysis directory or with its full path:

```bash
python3 audit-schema-integration.py /absolute/path/to/moda-interact-workspace > schema-integration-evidence.json
```

The audit reads schema/migration bytes, package scripts and source references, then imports and executes only the existing built-in-only ARCH-047 schema selector. It installs nothing, imports no application services, connects to no database, and makes no Git mutation. Its successful exit means that the audit completed, not that the application passed validation.

Observed in this review:

| Exported Database copy | Schema bytes | Models | Migration files | SQL migrations | Difference from canonical |
|---|---:|---:|---:|---:|---|
| `moda-interact-database/prisma` | 191,864 | 130 | 72 | 71 | Reference |
| `moda-interact-background/database/prisma` | 191,864 | 130 | 72 | 71 | Identical schema and migration bytes |
| `moda-interact/database/prisma` | 191,864 | 130 | 72 | 71 | Identical schema and migration bytes |
| `moda-interact-admin/database/prisma` | 191,864 | 130 | 72 | 71 | Identical schema and migration bytes |
| `moda-interact-api/database/prisma` | 191,707 | 130 | 69 | 68 | Two missing model fields; three missing migrations |

Migration-file counts include `migration_lock.toml`. All 69 common API/canonical migration files have identical bytes. Removing exactly the two new field lines from the canonical schema produces the API schema byte for byte. This narrows U1 to a specific dependency divergence; it does not describe arbitrary schema drift.

Schema SHA-256 values:

- Canonical, Background, Shopify and Admin: `5c68e467f392cafe2e6b5be730b81e000a3590e31567135c4037791bcfe11052`.
- API: `45df5e44bdc1e7e29495e391a1754477f0df362c667d648f4b6893b6541f5c0d`.

The exact field definitions and source use are:

| Model field | Accepted definition | Current API use | Consequence of the old API schema |
|---|---|---|---|
| `MerchantConversationSendCommand.followUpClaimKey` | `String? @db.VarChar(255)` | `src/merchant/conversations/messages/admission.service.ts:188` includes it in typed command creation | Normal client generation has no field corresponding to the creation argument |
| `MerchantKnowledgeUploadedAsset.intentPurposeKey` | `String? @db.VarChar(64)` | `src/merchant/merchant-knowledge/upload.service.ts:156,170,196,207,211,244,251` reads, creates, selects and compares it | Normal client generation has no corresponding scalar/input/select property |

The canonical definitions are in `moda-interact-database/prisma/schema.prisma:601` and `:4191`. The API imports the generated Prisma client and uses its typed transaction/client services. This is direct source/schema incompatibility. Actual compiler error text or runtime failure was **not** produced here; no installed API dependencies or generated client are present in the supplied export.

## 2. Why an alternate test schema does not repair the API

`moda-interact-api/package.json:12,14,19` establishes the ordinary path:

```text
build            -> npm run prisma:generate && tsc -p tsconfig.build.json
typecheck        -> npm run prisma:generate && tsc --noEmit -p tsconfig.json
prisma:generate  -> prisma generate --schema database/prisma/schema.prisma
```

Neither the build nor the typecheck uses the workspace's sibling canonical schema. Their first step would overwrite any transient client generated from another schema. The API package declares Prisma and `@prisma/client` 6.19.3. No schema output override or TypeScript path indirection was found in the inspected schema/configuration.

The human-send harness has a separate schema selector whose scope remains ARCH-047:

- `scripts/arch047-canonical-schema.mjs:6` requires only the two ARCH-047 migrations and three template models.
- Its lineage predicate checks that the candidate contains the API's existing migrations with unchanged bytes. Additional candidate migrations are allowed.
- Its default candidate order starts with the API's nested schema (`:118`). The stale schema satisfies these ARCH-047 checks.
- `scripts/test-arch040-woo-human-send-postgres.mjs:56` always generates the client from `database/prisma/schema.prisma`.
- That harness deploys migrations from the selected `canonicalSchema` at `:60`.

The existing selector was actually executed against the export, with these results:

| Probe | Observed result |
|---|---|
| Default selection with workspace root supplied | API's stale nested schema |
| Explicit canonical-schema selection | Workspace canonical Database schema |
| Old API schema accepted by the ARCH-047 predicate | `true` |
| API/canonical common migration lineage compatible | `true` |

Thus `ARCH047_CANONICAL_DATABASE_SCHEMA` can select a newer disposable **database migration source**, while the generated **API client** remains old. This split is an integration trap, not evidence that the ARCH-047 helper promised ARCH-055 validation. Expanding a helper or using an override would not replace the dependency correction: the ordinary build still uses the recorded nested path.

The knowledge-upload harness is simpler: both generation and `migrate deploy` use the nested API schema (`scripts/test-arch035-knowledge-upload-postgres.mjs:39,41`). Its new ARCH-055 tests therefore also depend on correcting that tree.

## 3. The three migrations are one integration contract

All paths below are under `moda-interact-database/prisma/migrations/`. They are absent from the API copy and present, byte-identically, in the other four inspected copies.

| Ordered migration | Bytes and SHA-256 | Required behavior |
|---|---|---|
| `20261102120000_arch055_rest_read_lifecycle/migration.sql` | 3,465; `c129466fdb53190b7f8ce6c2d3a04867c6bacbd55e334c5e0bceeb1b28e4e53b` | Replaces the named attempt time CHECK and `arch026_rest_read_attempt_guard` so failure terminalization can happen after expiry or credential change while preserving identity and single-use checks; successful bearer consumption retains its expiry/current-installation checks |
| `20261102121000_arch055_human_follow_up_claim_identity/migration.sql` | 1,263; `e4689790fbba7f606803b2d0370a66ba8b4f57bb3cb0b67b154336f90c2d41fb` | Adds the nullable claim key and backfills historical template commands from their own original public idempotency keys without changing attempt ownership |
| `20261102122000_arch055_upload_intake_identity/migration.sql` | 975; `e9ce08d49576f84a4e1b95c39637c69e97f0f620b4fae608fadf2712fefb6a37` | Adds nullable upload purpose and a partial unique original-intake index, rejecting duplicate existing original-intake history |

### REST-read lifecycle

The API's current `WooRestReadAuthorizationService.revoke` transaction requires a current principal, then sets current-generation pending attempts to `FAILED` with `consumedAt` and `failureCode` (`src/woocommerce/rest-read/authorization.service.ts:159`). Its predicate deliberately does not exclude expired attempts. Migration 1 supplies the corresponding database permission for failure terminalization. Synchronizing only Prisma model fields cannot update that installed function or CHECK. The new failed branch cannot mint a successful grant; successful consumption still follows the existing eligibility and transaction-identity path.

### Human command identity

Migration 2 takes an access-exclusive command-table lock, verifies that `arch040_command_guard` is enabled, and disables only that named trigger inside the same transaction for the metadata backfill. It restores the trigger before commit. Historical template commands receive `followUpClaimKey = idempotencyKey`; human text retains null. It deliberately adds no new NOT NULL requirement, blank-key CHECK or insertion trigger.

Current API admission preallocates a command UUID only after resolving replay and uses that UUID for both the command's persisted key and sequence-two attempt `initiationKey`, inside the same transaction (`admission.service.ts:109–195`). The Shopify producer does the same after its replay lookup (`moda-interact/app/services/recoveries/recovery-human-commands.server.ts:180–280`). Both preserve the public shop-scoped retry key, and both set the new private field to null for human text.

Background loads and consumes the **stored field** in its command service, dispatcher, outbound fence and claim-cancellation service. Historical commands may have keys different from their command IDs, so deriving a key from `command.id` would be incorrect. Missing or blank template keys cause a fail-closed integrity path; the owner claim/credit is held for repair rather than released using a guessed key. Relevant predicates include `outbound-send-fence.service.ts:128–152`, `human-command-dispatcher.service.ts:510–526`, and `follow-up-claim-cancellation.service.ts:82–83,162–172,227` under `moda-interact-background/src/services/recovery-conversation/`.

No additional mismatch was found between the two current producers' key format and the Background consumer. A mixed rollout with an old producer is nevertheless incompatible: because the database field is nullable and has no new insert guard, that producer could insert a new template command without a key after the one-time backfill. Background intentionally refuses that command. This is already addressed by ARCH-055's coordinated rollout contract, not by a new fallback or schema constraint proposed here.

### Upload identity

Migration 3 has no purpose backfill. Existing pending uploads with no bound purpose require a new intent/key under the documented rollout; the API rejects their purpose mismatch rather than silently binding them. Completed historical uploads can replay their original intake when persisted source provenance and identity match. `originalIntakeReplay` locates only `CREATE`/`FILE_REPLACE` revisions for that asset and returns the original generation even after subsequent reprocessing.

The partial index is on non-null `uploadedAssetId` for revision reasons `CREATE` and `FILE_REPLACE`. It permits reprocessing, entitlement-change revisions and null assets. A preflight groups existing original intakes and raises SQLSTATE `23505` before creating the index if duplicates exist; it does not delete or relabel history. The whole migration is transactional. Again, adding a Prisma field alone would not establish this invariant.

The upload service's persisted purpose, finalization locking and original-intake lookup agree with this migration shape. This finding does not resolve the separately tracked Background cleanup/external-object acknowledgement issue.

## 4. Recorded acceptance versus verifiable Git state

The supplied task records contain useful historical evidence:

| Record | What it says | What this review can establish |
|---|---|---|
| `docs/decisions/database/ARCH-055/DATABASE-001-establish-api-lifecycle-persistence-contracts.md:539` | Accepted implementation is `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`; consumers adopt the accepted dependency in their own task worktrees | The recorded SHA and accepted contract exist in the document; no commit object or remote ref was inspected |
| `docs/decisions/api/ARCH-055/API-005-correct-knowledge-source-and-upload-lifecycle.md` | Accepted API work used that Database pin and reports generated-client/typecheck/upload-suite success | Historical task evidence; not a fresh run against this ZIP |
| `docs/decisions/shopify/ARCH-055/SHOPIFY-001-bind-human-follow-up-commands-to-internal-claim-key.md:254` | Merged Database revision `8e74634ff92be9900f693c0c449ffce888e7d617` has the same tree as accepted `5907b…` | Both SHAs and the tree-equivalence claim are documentary evidence, not independently verified current pins |
| `docs/architecture/ARCH-055-woocommerce-api-database-correctness-and-efficiency.md:237` | API-004 remains Ready; API-009 and SYSTEM-TEST-001 still have incomplete prerequisites | Source presence alone does not establish acceptance or architecture-wide completion |

The accepted implementation SHA and documented merged SHA must not be treated as interchangeable Git ancestry evidence. A squash can preserve a tree while changing ancestry. Likewise, a correct API gitlink may have been exported alongside the wrong materialized nested files. The observed source mismatch does not retroactively invalidate another worktree's historical test report, and those historical reports do not validate this export.

## 5. Smallest owner handoff and validation order

### A. Resolve the real dependency state first

In the developer/launcher-resolved **API task or integration worktree**, inspect before changing anything. `API_WORKTREE` below is the real worktree path supplied by that workflow, not this extracted snapshot.

```bash
git -C "$API_WORKTREE" status --short
git -C "$API_WORKTREE" ls-tree HEAD -- database
git -C "$API_WORKTREE" submodule status -- database
git -C "$API_WORKTREE/database" rev-parse HEAD
git -C "$API_WORKTREE/database" status --short
```

Inspect the recorded commit's schema and three migration paths with `git show`/`git ls-tree`, using the actual gitlink SHA returned above. Verify its relationship to the accepted merged Database revision in accessible Git history; compare trees if the accepted task and merged revisions differ. Do not infer the current target from a ZIP hash or substitute an unmerged task commit because it appears in a completion report.

- **Recorded gitlink already has ARCH-055, working checkout is stale:** materialize the recorded dependency through the existing recursive submodule workflow, then repeat the audit. No new gitlink commit is needed if the index already names the correct accepted revision.
- **Recorded gitlink is old:** the API owner advances only the API repository's `database` gitlink to the verified accepted/merged revision through its existing task/integration process. Generated dependencies remain generated output. No nested schema or migration is hand-edited, and no parent workspace gitlink is advanced to an unmerged implementation commit.

For the first case, once local changes and the intended recorded pin have been checked, the existing materialization commands are:

```bash
git -C "$API_WORKTREE" submodule sync -- database
git -C "$API_WORKTREE" submodule update --init --recursive -- database
```

These commands materialize the recorded pin. They do **not** select a newer accepted revision when the recorded pin itself is old. The second case therefore requires a deliberate owning-repository gitlink change, using the verified revision from the real checkout. No executable pin-changing command with a guessed SHA is supplied or run here.

**Expected changed implementation path, only if the gitlink is actually old:** `moda-interact-api/database` as a Git dependency pointer. A completion/evidence report belongs to the owning workflow. U1 does not justify another Database migration, duplicated local schema, public DTO change, Shared release or broad application rewrite.

### B. Regenerate and check through the normal API commands

After the recorded dependency is coherent and the project's existing locked dependencies are available:

```bash
npm run typecheck
npm run build
```

Run these from the API worktree. Both invoke normal Prisma generation. Record the resolved Database commit, schema/migration hashes, actual Prisma client version, exact command results and any remaining errors. Do not bypass `prisma:generate`, retain an out-of-band client, suppress new type errors or assert a pass from the source audit. Additional errors, if observed, become concrete follow-up evidence; this review cannot rule them out without execution.

### C. Reuse the existing migration and application proofs

| Owner / worktree | Existing command | Purpose and boundary |
|---|---|---|
| Canonical Database accepted task/history context | `npm run test:arch055-database-contracts` | Exact accepted schema/SQL/change-scope validation, including original migration bytes |
| Canonical Database | `npm run test:arch055-database-contracts:postgres:fresh` | All three forward contracts on fresh disposable PostgreSQL |
| Canonical Database | `npm run test:arch055-database-contracts:postgres:upgrade` | Historical-key preservation, trigger restoration/rollback, duplicate-intake abort and retry on populated predecessor state |
| API | `npm run test:arch026-woo-rest-read:postgres` | Updated failure lifecycle, concurrent callbacks, current-generation revoke and rollback on actual migrations |
| API | `npm run test:arch035-knowledge-upload:postgres` | Intent retry/purpose matching, original-intake replay, reprocessing and cleanup-lock interleaving |
| API | `npm run test:arch040-human-send:postgres` | Same public key across shops produces distinct private owners; matching replay and claim/command atomicity; transaction-bound configuration and prepared evidence |
| Background | `npm run test:arch040-recovery-conversation` followed by `npm run test:arch040-background-runtime:postgres` | Persisted key unit coverage plus actual historical-key release, reclaim races and missing-key fail-closed behavior |
| Shopify | `npx --no-install vitest run tests/unit/arch040-shopify-command.test.ts tests/unit/arch047-shopify-follow-up-sender.test.ts` | Existing producer argument/replay coverage; this is not cross-platform PostgreSQL proof |

The Database static validator requires the recorded baseline `7c377282aa5819b3008b7d7f3018f44f4161523e` and an exact changed-file allowlist (`scripts/validate-arch055-database-contracts.mjs:10–54`). It should be interpreted/run in its accepted task/history context. Do not report it as runnable in this Git-free export, or broaden its allowlist to make an unrelated integrated revision pass. Fresh/upgrade database scripts separately exercise the named migration chain through the ARCH-055 target and are existing focused gates.

The API REST-read runner does not itself regenerate the client, so the normal generation/typecheck step above matters. The human-send and knowledge-upload runners regenerate and apply migrations. Their success requires actual local test dependencies and disposable PostgreSQL/pgvector; Background's existing integration runner additionally provisions disposable Redis through Shared. Preserve exact outputs and cleanup outcomes. Do not point any command at a shared/live database or replace migrated fixtures with `db push`.

These are the existing owning-task boundaries, not newly invented acceptance gates. ARCH-055-SYSTEM-TEST-001 owns real cross-platform integration after its prerequisites are accepted. Shopify's two unit suites cannot prove the API/Shopify/Background contract against one migrated database, and an API suite alone cannot prove Background dispatch/reclaim. The terminal task remains the appropriate owner of that final evidence.

### D. Respect the existing coordinated rollout

The architecture's explicit pre-production contract (`ARCH-055…md:156–166`) requires inventory/backups and preflights, quiescing both human-command producers and relevant dispatch/cleanup work, applying the ordered migrations, deploying compatible Background and both producer versions against the same accepted Database dependency, and resuming after the specified smoke checks. Preserve queued/durable work and leave duplicate-intake reconciliation explicit. Historical unbound pending uploads may require new intents. A rolling-deploy requirement would be a changed architectural premise, not something established by this snapshot.

Rollback preserves the compatible application set under quiescence or rolls forward. It does not remove stored keys/fields, rewrite provider evidence or resume an old producer against the new consumer. This review performs none of those operational steps.

## 6. Evidence status and closure condition

**Actually verified:** schema byte differences, model counts, all common and missing migration files/hashes, ordinary API generation/build script wiring, selected producer/consumer call sites and SQL predicates, task/rollout text, and execution of the existing ARCH-047 selector. The audit completed with exit 0 and its JSON result was inspected. All inspected application dependency directories are absent in the export.

**Not executed:** Prisma generation, TypeScript compilation, application tests, PostgreSQL migration rehearsal, a Git dependency update, actual Git pin/remote verification or deployment. Historical accepted task results remain explicitly historical. No compiler pass, physical rollback, affected-row count, provider result or production readiness is inferred from static code.

U1 can close when a real checkout demonstrates (1) the API's recorded and materialized Database dependency contains the accepted two-field/three-migration contract, (2) the normal API client generation and build/typecheck succeed, and (3) the appropriate owning-task migration-backed checks pass against that dependency. Architecture-wide release remains subject to the already documented task and coordinated-rollout obligations. No additional schema/application correction is presently evidenced by this focused U1 trace; remaining runtime validation may reveal one.
