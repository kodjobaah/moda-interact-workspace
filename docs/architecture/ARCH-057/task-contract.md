# ARCH-057 task execution and diagnostic contract

## Authority and baseline

This contract is mandatory for every ARCH-057 task. The parent decision is `docs/architecture/ARCH-057-shopify-application-database-correctness-and-simplicity.md`. Definitions use the latest supplied `moda-interact-workspace(20261104-005051).zip`, SHA-256 `a2c582c7aecb087b5c997d953bb1ab398f4e0d90d4fa79d555f8dd267b7233ee`. The original Shopify review remains valid: Shopify, canonical/nested Database, Shared and Background implementation bytes are unchanged. See `snapshot-reconciliation.md`.

All new tasks are **defined but not materialised**, unclaimed, attempt 0. Status ready/pending is dependency readiness, not a claim of execution. Use the canonical launcher for matching parent and implementation branches `task/<TASK_ID>`. Record the prepared packet, actual parent/implementation worktree paths, start/end SHAs, accepted nested Database recorded/working pins, installed Shared version, commands and container cleanup. No snapshot-derived SHA is a claimed Git commit. The implementation agent returns review; only the authorised architect review may accept/complete.

Read the assigned repository's `AGENTS.md` and use its prescribed tooling for implementation. Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/developer-task-workflow.md`, `docs/task-definition-materialization.md` and `docs/observability/shared-logging.md`. The launcher owns preparation. Do not reconstruct worktree paths from a previous task, create a second claim, start a downstream task, merge main or change parent gitlinks to unmerged implementation commits.

Use repository-relative edits in the assigned repository. Its task owns only its declared paths and Completion Report. Do not modify any `_index.md`, another task's state, an old architecture, copied Database schema, old migration, Shared package or another implementation repository. Unexpected file ownership or changed interface requires a scoped architect amendment. Existing API/Background work stays with ARCH-055/056.

Before the first Node command in an execution environment:

```sh
command -v node >/dev/null 2>&1 || source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"
```

`MODA_WORKSPACE_ROOT` must be the launcher-provided primary workspace. Use existing locked tooling. New dependency, package upgrade, schema/index/trigger/outbox or compatibility framework is not implied by these tasks.

## Simplicity and behavioural preservation

Choose the implementation specified in the task. Do not turn evidence-only/deferred findings into extra implementation. Share reads within one request; use direct local service composition. Preserve independent endpoint authentication, trusted tenant identity, action origin checks, source/asset ownership, no-op/replay semantics, fresh mutation admission, exact cycle/accounting predicates, revision CAS, and established queue-after-commit boundaries.

A request read cache is neither a cross-request cache nor a transaction snapshot. It must not authorize a mutation after a concurrent lifecycle change. No provider/Redis/R2 I/O inside a database write transaction. Domain-specific state rereads under a lock are retained unless the task supplies an equally authoritative transaction-bound result.

Keep the existing 20 locale catalogues complete. Most selected changes preserve copy. If a task adds a visible error distinction or control, its exact key must exist in every current locale; do not show provider text or invent English-only server responses.

Historical task names in documents/tests are allowed. Runtime modules, symbols, log events, environment variables, route names and new queue identities use domain names. The user explicitly confirmed a development-only, not-live baseline with no historical billing-identity preservation requirement. SHOPIFY-012 owns the direct replacement of all three architecture-derived Shopify billing namespaces with its exact canonical names, with no runtime allowlist or old-format compatibility. Earlier functional tasks keep identity generation stable within their own scope; the final naming task changes the namespaces deliberately and tests fresh same-format replay/conflict behaviour. No legacy reader, dual-write, backfill or migration is required. Do not conceal labels through concatenation, numeric encoding or base64.

## Mandatory server error contract

Every operational failure in the selected server boundary must have an owning diagnostic, including failures converted into fallback, retry, unavailable, best-effort continuation or typed results. A catch that preserves success after a durable commit still records the actual failure.

Use `@modainteract/moda-interact-shared/logging`. Reuse existing domain observability adapters. A thin domain event adapter is permitted; another generic logger, JSON/error serializer, redaction engine, sink, telemetry wrapper or global error registry is not. Use `resolveDeploymentEnvironmentName()` for the service environment.

### Required fields when they exist at the source

| Field | Requirement |
|---|---|
| `event` | Stable domain/action name, e.g. `shopify.billing.provider_failed`; no architecture/task ID |
| `operation` / `stage` | Actual failed operation or phase, not an assumed provider cause |
| `origin` | `provider_response`, `sdk_exception`, `transport`, `database` or `internal`, according to evidence |
| `error` | Original safe exception; its actual name/message must reach the emitted Shared record |
| `cause` / `causeChain` | Available original causes, supplied explicitly through Shared fields; bounded to four known cause entries, without a custom serializer |
| `databaseCode` | Actual Prisma/driver code when available, e.g. P2021/P2034; never a guessed code |
| `provider` / `httpStatus` / `providerRequestId` | Actual safe source values; omit absent values |
| `providerError` | Original safe provider code/message/details, including GraphQL HTTP-200 errors |
| `reasonCode` | Optional Moda classification in addition to original evidence |
| Correlation | Available trusted Shop/operation/recovery/job/delivery/command IDs and fixed route name; never credentials |
| `redactionApplied` / `truncated` | Explicit when error text/details were redacted or shortened |

Shared 3.1.0 serializes an Error's name/message, not its custom properties/cause automatically. Passing `{error}` alone therefore does not prove that a Prisma code or cause survived. The owning adapter supplies those available fields explicitly, lets Shared own serialization/bounds, and preserves the actual Error `cause` during propagation. Known wrapper chains can supply their existing cause objects; do not invent a reusable competing recursive serializer.

Provider adapters extract the provider's original error object or safe bounded non-JSON error excerpt before creating the emitted record. Preserve wording/value semantics except necessary security redaction and truncation. Never replace an actual message with only “provider failed”, `PARTNER_API_ERROR`, a guessed explanation, or an error type. A malformed success body has an internally generated diagnostic; do not fabricate a provider-supplied message for it.

Do not pass raw request/response bodies, webhook payloads, GraphQL data, customer message text, cookies, Authorization, tokens, signed URLs, keyrings, database/Redis connection strings, customer identifiers such as email/phone/name/address, or payment details. Domain adapters remove sensitive spans before Shared's defence-in-depth sanitization. If a portion cannot be safely extracted, redact that portion explicitly while preserving safe status/code/request ID and source metadata. Avoid bulk secret enumeration or logging environment variables.

Emit full source/provider diagnostic evidence at the documented owning boundary. A downstream framework/SSR outcome record may repeat the bounded safe exception name/message and add stage, status and correlation; it must not re-extract or repeat provider bodies/details. “Once” governs ownership of the full diagnostic payload, not the number of contextual records across the request lifecycle. Do not add a global deduplication registry or require exactly one emitted record for an entire lifecycle. A rethrow-only caller relies on its documented owner. A failure first handled by the framework uses that framework boundary as its owner. Redirect Responses, invalid form/cursor input and ordinary business denials remain control flow, not fabricated operational errors. Recognised transient DB retries may log at warn per attempt, with final failure at error; an exhausted retry cannot disappear.

Logging must not change success, rollback, retry, HTTP status, authorization or dispatch. A throwing log sink is isolated by Shared. No blanket catch-and-continue for business exceptions. No process-wide `uncaughtException` handler that lets corrupted execution continue.

### Required emitted-log assertions

Each task's failure matrix identifies producer/owner, injection point, actual output and outcome. Capture the **real Shared logger output**, not only a mocked logger method call.

1. Inject a unique harmless source error message, database/provider code, cause marker and safe request ID. Assert original marker/code/cause where supplied in the actual JSON record.
2. Inject credential/PII/signed-URL sentinels within the provider error as well as structured fields. Assert absence from raw captured records and evidence artifacts; do not rely solely on harness redaction.
3. Check every caught fallback/retry/typed-error branch named by the task. Diagnostic ownership must be explicit for propagated failures.
4. Verify origin/classification is truthful, absent source fields remain absent, and internally generated errors are not labelled upstream messages.
5. Exercise real Shared throwing-sink isolation. Verify the business operation's status, durable state and retry decision remain unchanged.
6. Keep browser/merchant responses bounded and free of internal error details. Debugging evidence is server-side.
7. Do not add a second HTTP metric/span or perform a DB read solely to decorate a failure log.

SHOPIFY-011 reconciles the remaining server surfaces and catch/error-event inventory. It does not excuse missing diagnostics in earlier tasks.

## Validation and evidence

Run only the task's mandatory focused tests and relevant gates. Use disposable PostgreSQL `pgvector/pgvector:pg17` with the canonical **forward migration sequence**, and real separate connections/explicit barriers for lock/race assertions. Do not use `db push`, copied schemas, mocks or timing sleeps as proof of database concurrency. Real Redis is required where the task verifies BullMQ ID/deadline behaviour. External providers are controlled synthetic boundaries; no live charges/refunds or production tenant data are authorised.

Before/after query evidence uses the same fixture and operation branch. Record repository method calls separately from emitted SQL, transaction-control statements, affected rows, provider calls and returned outcome. Timings are descriptive; do not claim capacity or latency improvements from small samples. Reuse existing test helpers; new helpers must have explicit paths. Test code remains modular, with new files below 300 lines; return a scope amendment if the declared split cannot support that constraint.

A required suite that skips due to missing opt-in, Docker, provider fixture, package/build or source provenance is **blocked/not run**, never passed. Preserve failures; do not prune shared Docker resources or repair the developer's host as an implicit task step. Cleanup only task-owned resources.

Completion Reports record actual source/build/provenance, required case results, SQL/provider/log artifacts, source/identity preservation, deviations and unresolved issues. No pre-checked acceptance items or invented branch/commit/test results.
