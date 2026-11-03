# Validation and owner handoff

This document distinguishes checks performed during review from implementation acceptance gates. It does not create new task IDs, alter existing acceptance status or replace the workspace's task/worktree ownership rules.

## Checks performed in this review

| Check | Result and limit |
|---|---|
| Updated archive identification | Exact filename and SHA-256 recorded; all original regular files checked again during patch validation |
| API/canonical schema and migration audit | Executed; two missing field lines, three missing migrations, all common migration bytes identical |
| Existing ARCH-047 selector | Executed with built-in Node modules only; default selects API's stale nested schema; explicit override selects canonical |
| Source tracing | Actual worker, materializer, initiation, fallback, reservation, final-fence, receipt, billing, Support and scheduling paths inspected |
| PostgreSQL lock mechanism | Source/constraint/lock-rule analysis completed; no PostgreSQL engine or Docker/Podman available for execution |
| Reproduction SQL | Reviewed as a minimal disposable two-session mechanism protocol; does not stand in for migrated application tests |
| Delivery patch | Strict apply/check, whitespace, exact added-path allowlist, ZIP byte equality and original-source preservation results are recorded in the delivery validation file |

No dependencies were installed. No application test, Prisma generation, TypeScript build, migration application, external provider request, Redis mutation, benchmark or EXPLAIN was executed. Historical completion reports are not fresh test output. Temporary Git repositories used to construct and check this documentation patch establish no real branch history or submodule pin.

## U1 implementation gate

The API owner first resolves its real recorded gitlink and materialized dependency. Do not hand-copy model fields or infer a Git pin from the ZIP. The [schema appendix](schema-integration.md) contains the exact inspection commands, accepted/merged-document provenance, normal API build/generation path and existing focused test commands.

Acceptance requires coherent recorded and materialized dependency bytes, successful normal API typecheck/build, and the owning-task migration-backed checks against the accepted contract. Preserve the three ordered migrations and existing Database/Background/both-producers rollout. Cross-platform completion remains owned by the terminal ARCH-055 system task after its prerequisites; this review does not mark it ready or complete.

## U3 implementation gate

Run the supplied minimal PostgreSQL 17 protocol in a fresh disposable database. Then validate the actual application change using the existing migrated ingress fixture and two independently controlled database sessions. Required outcomes are:

1. With current insert-first ordering, the explicit two-session barrier can expose the FK lock-upgrade mechanism; record the actual SQLSTATE and wait evidence without assuming which session loses.
2. With parent-first ordering, simultaneous distinct messages serialize and both commit; each advances the version exactly once, with the correct pending-turn deadline/revision behavior.
3. Concurrent duplicate provider messages leave one message and one committed version increment. The losing unique violation rolls back every earlier helper write.
4. Control mode, expired pause, existing pending/processing state, future deadlines and interleaved audio completion retain current behavior.
5. Failure after the moved helper and before message insert leaves no partial pending state. Current locked-state freshness remains intact.

A weaker lock-mode substitution is not part of the minimum recommendation. An existing language-staleness race and the separate receipt/fence lock-order lead are recorded explicitly; no whole-system deadlock-freedom claim is warranted.

## U2/C3 implementation gate

Use the real candidate worker/materializer path and actual fallback/delivery/finalization owners for integration cases. Direct initiation mocks can prove a local call but cannot prove the queue's actual retry reaches it. The [recovery appendix](recovery-progress.md) supplies the full interruption-state and deterministic test matrices. At minimum, demonstrate:

| Boundary | Required assertion |
|---|---|
| Recovery or initial attempt inserted, required read fails | Next actual retry continues the same generation and attempt; it does not acknowledge an incomplete `DETECTED` row as successful work |
| Usage and PENDING message committed before permit | Same message and same usage resume; two workers cannot obtain two final permits or perform two provider calls |
| Permit committed, outcome unknown | No automatic resend or release, including when attempt status says FAILED |
| Provider HTTP succeeds, local receipt write fails | Original database error preserved; uncertainty retained; no fabricated provider receipt or second send |
| Definitive failure and 131026 | Exact failed-message lineage retained; existing compensation/reachability owner completes once |
| `failPrepared` interrupted or races a permit | Cleanup CAS requires PENDING and both permit fields null; usage removal belongs to the winning claim; zero rows reclassifies without invalidating admitted/confirmed state |
| Confirmed receipt with credit not settled | Original reservation resolved; only COMMITTED/verified already-COMMITTED permits successful accounting progression |
| Commit returns already-ambiguous or already-released | Outcome remains an explicit conflict; no Support/sent-state progression justified by a fulfilled promise alone |
| Historical paid RESERVED source or multiple candidate sources | Existing period/lineage constraint remains visible; no current-policy readmission, arbitrary selection or extra debit |
| Credit committed, Support transaction fails | Exact committed source replays; Support notice and attempt transition occur at most once |
| Attempt finalized, recovery update fails | Current receipt bypasses unsent-template guards; recovery converges without undoing a newer terminal/engaged state |
| Follow-up enqueue fails | Existing deterministic identity and persisted due date are reused; current eligibility still controls future sends |
| Follow-up policy changes after attempt finalization | Stored date stays that date and stored null stays null; replay does not invent a new decision or conflict with the exact Support finalizer |
| New STOP/order/expiry after confirmed send | Existing receipt and credit reconcile; no further provider send is authorized |
| Technical retry exhaustion | Failed work remains visible/replayable; no false success and no claim of automatic repair without a specified discovery owner |

Tests must use actual durable key formats, not invented rows where a usage key is stored as a provider-dispatch key. Include tenant/source mismatches, absent usage with retained attempt evidence, incomplete permit fields, FAILED/CANCELLED legacy attempts with a confirmed receipt, and both Support enablement states. Keep HTTP and queue publication outside database transactions. Preserve the original error object in Shared structured logging with the established redaction policy.

## Scope and sequencing

The dependency and ingress corrections can be independently implemented by their existing owners. The initial-recovery correction must combine real retry reachability, canonical message classification, guarded same-message continuation, exact billing settlement and finalizer replay. The specification deliberately leaves uncertain provider acceptance and unprovable credit ownership as visible holds; calling those successful would weaken safety, while calling them automatically repairable would overstate progress.

No generic outbox, new queue, schema field, new trigger, global cache or periodic scanner is selected by this review. If a later implementation needs stronger source binding or durable discovery, it must demonstrate the concrete gap and define the smallest approved contract rather than silently expanding this documentation handoff.
