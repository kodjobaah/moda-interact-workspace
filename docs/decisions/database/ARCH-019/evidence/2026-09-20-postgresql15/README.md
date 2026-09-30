# Authorized PostgreSQL 15 rehearsal

User explicitly requested use of the existing local container. Command: `python3 /tmp/rehearse-arch019-existing.py`; runner preserved alongside this report. Tested implementation: `54c0ec2e092cd9db52d76e5bb46899efa4063965`. Exit: 0. PostgreSQL 15.19, local_postgres. This uses the committed migration and SQL fixtures unchanged, with temporary-database isolation instead of the committed harness's separate PostgreSQL 16 container. PostgreSQL 16 was not tested.

All prerequisite migrations applied to a new template0 database. Four target indexes applied transactionally to 20,000 recoveries and 201,980 messages. Fingerprint, prior-index preservation, valid/ready/nonunique index assertions passed. Both tenants, completed/ongoing status, related customer and chronological/latest transcript plans captured without planner forcing. Only the run-created database was dropped; existing databases/container were retained.

Recovery queries use new indexes after migration: date page 26 rows / 5 shared buffers; completed page 26 / 4; ongoing page 26 with 27 filtered / 7; related page 6 / 9. All avoid the former explicit sorts. These are synthetic local observations, not production latency/capacity guarantees.

Transcript finding for SHOPIFY-002: new message index is used, but joined query shapes retain top-N sorts over 760 and 1,000 messages. Chronological ownership lookup executes 760 times. Index existence does not guarantee bounded scanning. Resolve owned recovery/conversation once, then page messages with an equality-bound conversation ID and date/id cursor; retain tenant authorization and fixed query count. Verify the actual application query plans in that task. No additional database index is established as necessary by this result.

This evidence satisfies the database rehearsal. Architect accepted DATABASE-001 and reconciled the downstream frontier on 2026-09-20. No implementation source changed.
