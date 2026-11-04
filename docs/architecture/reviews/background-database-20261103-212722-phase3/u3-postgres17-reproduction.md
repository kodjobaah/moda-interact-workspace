# U3 PostgreSQL 17 two-session reproduction protocol

**Execution status: not run.** This review environment has no PostgreSQL binaries or Docker/Podman. These are reviewable future commands, not collected runtime evidence or an application regression test. They use only a newly created disposable database. No existing application URL or credentials are needed.

## Scope

The fixture preserves the source's parent primary key, immediate child FK with CASCADE actions, unique providerMessageId, and atomic version/pending mutation. It omits unrelated schema and triggers after confirming that the current inbound trigger branch does not take an earlier parent FOR UPDATE lock. It establishes the lock mechanism only. Full-schema service/queue tests remain required separately.

The container image matches the inspected Background runner (`moda-interact-background/scripts/test-integration.mjs:84`). Its tag can move; retain the actual image ID and server version from your run.

## 1. Create the disposable server

Use a controller terminal, from the directory containing `u3-postgres17-setup.sql`. The fixed name makes the two session commands copyable. If that name already exists, stop here and choose a different name consistently; **do not delete a pre-existing container**.

```sh
set -eu
u3_container_id=$(docker run --rm --detach \
  --name moda-bgdb-u3-20261103 \
  --label moda.review.u3=20261103 \
  --network none \
  --env POSTGRES_USER=u3 \
  --env POSTGRES_PASSWORD=u3-fixture-only \
  --env POSTGRES_DB=u3 \
  pgvector/pgvector:pg17 \
  -c deadlock_timeout=100ms -c log_lock_waits=on)
trap 'docker rm --force --volumes "$u3_container_id" >/dev/null' EXIT
u3_ready=0
for u3_try in $(seq 1 30); do
  if docker exec "$u3_container_id" pg_isready -U u3 -d u3; then
    u3_ready=1
    break
  fi
  sleep 1
done
if [ "$u3_ready" -ne 1 ]; then
  docker logs "$u3_container_id"
  exit 1
fi
docker inspect --format '{{.Id}} {{.Image}}' "$u3_container_id"
docker cp u3-postgres17-setup.sql "$u3_container_id":/tmp/u3-setup.sql
docker exec "$u3_container_id" psql -X -U u3 -d u3 -f /tmp/u3-setup.sql
```

Expected setup output: server major version 17; the fixture FK has condeferrable=false and condeferred=false. If the major version differs, stop and record that mismatch. This container publishes no host port and mounts no host directory.

Keep the controller shell open. Use it to observe waits:

```sh
docker exec -it "$u3_container_id" psql -X -U u3 -d u3
```

Controller psql setup:

```sql
\pset pager off
\set VERBOSITY verbose
```

Use this observer query whenever the protocol says “verify blocked”:

```sql
SELECT application_name, pid, state, wait_event_type, wait_event,
       pg_blocking_pids(pid) AS blockers, query
FROM pg_stat_activity
WHERE application_name IN ('u3-a', 'u3-b')
ORDER BY application_name;
```

The blocked session must be active with wait_event_type=Lock and the other session's PID in its blocker list. A timeout, disconnected session, or uncompleted earlier INSERT invalidates the intended schedule.

## 2. Open two independent sessions

In terminal A:

```sh
docker exec -it moda-bgdb-u3-20261103 psql -X -U u3 -d u3
```

Then in its psql:

```sql
\pset pager off
\set VERBOSITY verbose
\set ON_ERROR_STOP off
\set msg_id 'u3-a'
\set provider_id 'u3-provider-a'
\set received_at '2026-11-03 21:30:00.001'
SET application_name = 'u3-a';
SET statement_timeout = '2min';
SET lock_timeout = '0';
SELECT pg_backend_pid();
```

In terminal B, open the same container/database with the same docker exec command. Configure its psql:

```sql
\pset pager off
\set VERBOSITY verbose
\set ON_ERROR_STOP off
\set msg_id 'u3-b'
\set provider_id 'u3-provider-b'
\set received_at '2026-11-03 21:30:00.002'
SET application_name = 'u3-b';
SET statement_timeout = '2min';
SET lock_timeout = '0';
SELECT pg_backend_pid();
```

Session variables deliberately differ. Both sessions use distinct provider IDs against the same parent. The two-minute timeout is a stalled-run bound; it is not an expected successful outcome. Do not pause a blocked phase long enough to hit it.

## 3. Current child-first order: force the cycle

Run this block in A and wait until INSERT finishes and the ready marker is printed:

```sql
BEGIN;
INSERT INTO "whatsapp"."ConversationMessage"
  ("id", "conversationId", "providerMessageId", "direction",
   "senderType", "status", "content", "createdAt")
VALUES
  (:'msg_id', 'u3-conversation', :'provider_id', 'INBOUND',
   'CUSTOMER', 'DELIVERED', 'fixture message', :'received_at'::timestamp);
SELECT 'insert-finished' AS barrier, pg_backend_pid();
```

Run the identical block in B and wait for its marker. **Both INSERTs must finish before either next command.** This is the barrier missing from a simple Promise.all test.

In A, run only:

```sql
SELECT "id" FROM "whatsapp"."Conversation"
WHERE "id" = 'u3-conversation' FOR UPDATE;
```

It should block. Use the controller observer query to verify that A waits for B. Then run the same FOR UPDATE statement in B. PostgreSQL should report deadlock_detected, SQLSTATE **40P01**, in one session and allow the other to finish its SELECT. Do not assert which session is selected as victim.

In the victim, preserve the complete verbose error and run:

```sql
\errverbose
ROLLBACK;
```

In the survivor, finish the represented helper mutation:

```sql
UPDATE "whatsapp"."Conversation"
SET "inboundVersion" = "inboundVersion" + 1,
    "pendingTurnStartedAt" =
      COALESCE("pendingTurnStartedAt", :'received_at'::timestamp)
WHERE "id" = 'u3-conversation';
COMMIT;
```

In the controller, inspect the committed state:

```sql
SELECT c."inboundVersion", c."pendingTurnStartedAt", count(m."id") AS messages
FROM "whatsapp"."Conversation" c
LEFT JOIN "whatsapp"."ConversationMessage" m ON m."conversationId" = c."id"
WHERE c."id" = 'u3-conversation'
GROUP BY c."id";
SELECT "id", "providerMessageId" FROM "whatsapp"."ConversationMessage"
ORDER BY "id";
```

Expected: one committed message and inboundVersion=1. There must be no committed child from the aborted transaction.

### Replay the victim

In the victim session, rerun its BEGIN/INSERT block, then FOR UPDATE, then the survivor's UPDATE/COMMIT block. Run this serially, after the survivor committed. Expected controller result: exactly two distinct messages and inboundVersion=2. This models retry of the whole database unit; it does not execute BullMQ.

## 4. Reset between schedules

After both sessions have ended their transactions, run in the controller:

```sql
TRUNCATE TABLE "whatsapp"."ConversationMessage";
UPDATE "whatsapp"."Conversation"
SET "inboundVersion" = 0, "pendingTurnStartedAt" = NULL
WHERE "id" = 'u3-conversation';
```

Never reset with an active test transaction. Reset would acquire unrelated table locks and contaminate the schedule.

## 5. Parent-first order: prove blocking precedes the second INSERT

In A:

```sql
BEGIN;
SELECT "id" FROM "whatsapp"."Conversation"
WHERE "id" = 'u3-conversation' FOR UPDATE;
UPDATE "whatsapp"."Conversation"
SET "inboundVersion" = "inboundVersion" + 1,
    "pendingTurnStartedAt" =
      COALESCE("pendingTurnStartedAt", :'received_at'::timestamp)
WHERE "id" = 'u3-conversation';
SELECT 'parent-and-helper-ready' AS barrier;
```

In B, run only:

```sql
BEGIN;
SELECT "id" FROM "whatsapp"."Conversation"
WHERE "id" = 'u3-conversation' FOR UPDATE;
```

Verify B is blocked behind A. B has not yet issued any INSERT. In A, run the INSERT statement from section 3 **without its BEGIN**, then COMMIT. B's SELECT should complete. In B, run the UPDATE from section 3, its INSERT statement, then COMMIT.

Expected: no deadlock in this schedule; two messages, version 2, and the pending start retained from A. The update-before-INSERT sequence represents moving the existing helper wholesale, rather than introducing a redundant extra lock call.

Do not impose the old “both INSERTs ready” barrier on this scenario. The second INSERT is intentionally unreachable while A holds the parent.

## 6. FOR NO KEY UPDATE comparison

Reset. In both A and B, run the BEGIN/INSERT/ready block from section 3. After both INSERTs have completed, in A run:

```sql
SELECT "id" FROM "whatsapp"."Conversation"
WHERE "id" = 'u3-conversation' FOR NO KEY UPDATE;
```

It should complete while B still holds its FK KEY SHARE. Run the same NO KEY UPDATE SELECT in B; it should wait for A. Verify that wait, then let A run its UPDATE/COMMIT. Let B finish SELECT, then UPDATE/COMMIT.

Expected for this pair: both messages and version 2 without the original upgrade cycle. This only tests these two receivers. It does not establish equivalence with all other strong-lock writers, production triggers or mixed deployment states.

## 7. Duplicate rollback after moving the helper

Reset. Set B's provider ID equal to A's, keeping different message primary keys:

```sql
\set provider_id 'u3-provider-a'
```

Run the parent-first schedule from section 5. A commits successfully. B then acquires the parent and executes its version UPDATE. Its INSERT must fail with unique_violation, SQLSTATE **23505**. In B record the error, then ROLLBACK. Do not catch the error and commit a success result.

Expected controller result: one message and version 1, with A's original pending start. This checks the new order's essential coupled invariant: an INSERT failure cannot commit the preceding helper mutation. A later duplicate read finds the existing provider identity; the application still must verify Conversation ownership.

Also exercise a non-duplicate failure after the helper: reset, have A run BEGIN/parent lock/UPDATE, then deliberately run `SELECT 1/0;` and ROLLBACK before inserting. Expected: zero messages, version 0, pending start NULL. This synthetic statement validates rollback mechanics only; a real service test must inject the failure through receiveMessage and assert propagation of its original error.

Restore B's distinct provider ID before any fresh distinct-message schedule:

```sql
\set provider_id 'u3-provider-b'
```

## 8. Evidence and cleanup

Retain the image ID, server version, FK timing output, both session PIDs, A's pre-cycle wait graph, verbose SQLSTATE 40P01, survivor/victim outcome, retry state, parent-first wait graph, and duplicate rollback state. Record expected outcomes as observed only after running them. The unique violation is expected only in section 7, not a substitute for reproducing section 3.

Exit both test sessions and controller psql using `\q`. Back in the controller shell:

```sh
docker logs "$u3_container_id"
docker rm --force --volumes "$u3_container_id"
trap - EXIT
```

Cleanup targets the exact container ID created by this protocol. If a test is interrupted, exiting the controller shell invokes the same scoped cleanup trap. No application repository, migration, task status, or external database is changed.
