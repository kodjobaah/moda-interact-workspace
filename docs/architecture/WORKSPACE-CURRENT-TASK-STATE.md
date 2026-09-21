# Workspace current durable task state

> Synchronized by `moda_architect` on 2026-09-08 from individual task YAML frontmatter,
> with explicit restoration of previously accepted task records where the supplied workspace had drifted.
> Individual task files remain authoritative for execution/correction contracts.

## Workflow rules

- `complete` tasks are architect-accepted and must have no active executor/claim.
- `review` tasks await architect decision.
- `in_progress` tasks retain their active claim and must not be re-claimed.
- `ready` tasks may be claimed when repository concurrency rules allow.
- system-test tasks are terminal/manual-gated and are not auto-run merely because dependencies complete.

## ARCH-001

Current counts: `complete` 9, `ready` 1

| Task | Domain | Status | Attempt | Dependencies |
|---|---|---|---:|---|
| ARCH-001-SHARED-001 | shared | Complete | 1 | — |
| ARCH-001-SHOPIFY-001 | shopify | Complete | 2 | ARCH-001-SHARED-001 |
| ARCH-001-SHOPIFY-002 | shopify | Complete | 1 | ARCH-001-SHOPIFY-001 |
| ARCH-001-BACKGROUND-001 | background | Complete | 2 | ARCH-001-SHARED-001 |
| ARCH-001-BACKGROUND-002 | background | Complete | 1 | ARCH-001-BACKGROUND-001 |
| ARCH-001-BACKGROUND-003 | background | Complete | 2 | ARCH-001-BACKGROUND-001 |
| ARCH-001-BACKGROUND-004 | background | Complete | 1 | ARCH-001-BACKGROUND-002, ARCH-001-BACKGROUND-003 |
| ARCH-001-BACKGROUND-005 | background | Complete | 1 | ARCH-001-BACKGROUND-004 |
| ARCH-001-BACKGROUND-006 | background | Complete | 1 | ARCH-001-BACKGROUND-003 |
| ARCH-001-GATEWAY-001 | gateway | **Ready** | 0 | ARCH-001-SHARED-001, ARCH-001-SHOPIFY-001, ARCH-001-BACKGROUND-001 |

## ARCH-002

Current counts: `complete` 61, `pending` 3, `ready` 2, `superseded` 5

| Task | Domain | Status | Attempt | Dependencies |
|---|---|---|---:|---|
| ARCH-002-DATABASE-001 | database | Complete | 1 | — |
| ARCH-002-SHARED-002 | shared | Complete | 1 | ARCH-002-GATEWAY-001 |
| ARCH-002-SHARED-003 | shared | Complete | 1 | ARCH-002-SHARED-002 |
| ARCH-002-SHARED-004 | shared | Complete | 1 | ARCH-002-SHARED-003 |
| ARCH-002-SHARED-005 | shared | Complete | 1 | ARCH-002-SHARED-004, ARCH-002-SHARED-006 |
| ARCH-002-SHARED-006 | shared | Complete | 1 | ARCH-002-SHARED-004 |
| ARCH-002-SHARED-007 | shared | Complete | 1 | ARCH-002-SHARED-005 |
| ARCH-002-SHARED-008 | shared | Complete | 1 | ARCH-002-SHARED-007 |
| ARCH-002-SHARED-009 | shared | Complete | 1 | ARCH-002-SHARED-007 |
| ARCH-002-SHARED-010 | shared | Complete | 1 | ARCH-002-SHARED-007, ARCH-002-SHARED-008, ARCH-002-SHARED-009, ARCH-002-SHARED-011 |
| ARCH-002-SHARED-011 | shared | Complete | 1 | ARCH-002-SHARED-009 |
| ARCH-002-SHARED-012 | shared | Complete | 1 | ARCH-002-SHARED-010 |
| ARCH-002-SHARED-013 | shared | Complete | 1 | ARCH-002-SHARED-012 |
| ARCH-002-SHOPIFY-001 | shopify | Complete | 0 | ARCH-002-GATEWAY-001 |
| ARCH-002-SHOPIFY-002 | shopify | Complete | 1 | ARCH-002-GATEWAY-001 |
| ARCH-002-SHOPIFY-003 | shopify | Superseded | 1 | ARCH-002-GATEWAY-001, ARCH-002-SHARED-010 |
| ARCH-002-SHOPIFY-004 | shopify | Complete | 1 | ARCH-002-GATEWAY-001 |
| ARCH-002-SHOPIFY-005 | shopify | **Ready** | 0 | ARCH-002-SHOPIFY-002 |
| ARCH-002-SHOPIFY-006 | shopify | Complete | 1 | ARCH-002-GATEWAY-001, ARCH-002-SHARED-010 |
| ARCH-002-SHOPIFY-007 | shopify | Complete | 1 | ARCH-002-SHOPIFY-006 |
| ARCH-002-SHOPIFY-008 | shopify | Complete | 1 | ARCH-002-SHOPIFY-002 |
| ARCH-002-MESSAGING-001 | messaging | Complete | 1 | ARCH-002-GATEWAY-001 |
| ARCH-002-MESSAGING-002 | messaging | Superseded | 0 | ARCH-002-GATEWAY-001, ARCH-002-SHARED-010 |
| ARCH-002-MESSAGING-003 | messaging | Complete | 1 | ARCH-002-GATEWAY-001, ARCH-002-SHARED-010 |
| ARCH-002-MESSAGING-004 | messaging | Complete | 1 | ARCH-002-MESSAGING-003 |
| ARCH-002-MESSAGING-005 | messaging | Complete | 1 | ARCH-002-MESSAGING-003 |
| ARCH-002-BACKGROUND-001 | background | Complete | 1 | ARCH-002-GATEWAY-001 |
| ARCH-002-BACKGROUND-002 | background | Complete | 1 | ARCH-002-BACKGROUND-001 |
| ARCH-002-BACKGROUND-003 | background | Superseded | 0 | ARCH-002-BACKGROUND-001, ARCH-002-SHARED-010 |
| ARCH-002-BACKGROUND-004 | background | Complete | 1 | ARCH-002-GATEWAY-001, ARCH-002-SHARED-010 |
| ARCH-002-BACKGROUND-005 | background | Complete | 1 | ARCH-002-BACKGROUND-001, ARCH-002-BACKGROUND-002, ARCH-002-BACKGROUND-004, ARCH-002-SHARED-010 |
| ARCH-002-BACKGROUND-006 | background | Complete | 1 | ARCH-002-BACKGROUND-005 |
| ARCH-002-BACKGROUND-007 | background | Complete | 1 | ARCH-002-BACKGROUND-006 |
| ARCH-002-BACKGROUND-008 | background | Complete | 2 | ARCH-002-BACKGROUND-006, ARCH-002-SHARED-013 |
| ARCH-002-BACKGROUND-009 | background | Complete | 1 | ARCH-002-BACKGROUND-008 |
| ARCH-002-BACKGROUND-010 | background | Complete | 1 | — |
| ARCH-002-ADMIN-001 | admin | Complete | 1 | ARCH-002-GATEWAY-001 |
| ARCH-002-ADMIN-002 | admin | Superseded | 0 | ARCH-002-GATEWAY-001, ARCH-002-SHARED-010 |
| ARCH-002-ADMIN-003 | admin | Complete | 2 | ARCH-002-DATABASE-001 |
| ARCH-002-ADMIN-004 | admin | Complete | 1 | ARCH-002-ADMIN-008, ARCH-002-GATEWAY-006 |
| ARCH-002-ADMIN-005 | admin | Complete | 1 | ARCH-002-ADMIN-003 |
| ARCH-002-ADMIN-006 | admin | Complete | 1 | ARCH-002-ADMIN-003 |
| ARCH-002-ADMIN-007 | admin | Complete | 1 | ARCH-002-ADMIN-005, ARCH-002-ADMIN-006, ARCH-002-SHARED-005 |
| ARCH-002-ADMIN-008 | admin | Complete | 4 | ARCH-002-ADMIN-003, ARCH-002-ADMIN-005, ARCH-002-ADMIN-006, ARCH-002-ADMIN-007 |
| ARCH-002-ADMIN-009 | admin | Complete | 2 | ARCH-002-GATEWAY-001, ARCH-002-SHARED-010 |
| ARCH-002-ADMIN-010 | admin | Superseded | 1 | ARCH-002-ADMIN-009 |
| ARCH-002-ADMIN-011 | admin | Complete | 2 | ARCH-002-ADMIN-005 |
| ARCH-002-GATEWAY-001 | gateway | Complete | 1 | — |
| ARCH-002-GATEWAY-002 | gateway | Complete | 1 | ARCH-002-GATEWAY-001 |
| ARCH-002-GATEWAY-003 | gateway | Complete | 1 | ARCH-002-GATEWAY-002, ARCH-002-GATEWAY-005, ARCH-002-GATEWAY-006, ARCH-002-GATEWAY-007, ARCH-002-SHOPIFY-001, ARCH-002-SHOPIFY-002, ARCH-002-MESSAGING-001, ARCH-002-ADMIN-001, ARCH-002-ADMIN-008, ARCH-002-BACKGROUND-001, ARCH-002-BACKGROUND-002 |
| ARCH-002-GATEWAY-004 | gateway | Complete | 1 | ARCH-002-GATEWAY-003 |
| ARCH-002-GATEWAY-005 | gateway | Complete | 1 | ARCH-002-GATEWAY-001, ARCH-002-SHOPIFY-004, ARCH-002-BACKGROUND-004 |
| ARCH-002-GATEWAY-006 | gateway | Complete | 1 | ARCH-002-GATEWAY-002, ARCH-002-SHOPIFY-006, ARCH-002-MESSAGING-003, ARCH-002-ADMIN-009, ARCH-002-BACKGROUND-005 |
| ARCH-002-GATEWAY-007 | gateway | Complete | 1 | ARCH-002-GATEWAY-002, ARCH-002-ADMIN-008 |
| ARCH-002-GATEWAY-008 | gateway | Complete | 1 | ARCH-002-GATEWAY-003, ARCH-002-ADMIN-004, ARCH-002-ADMIN-009 |
| ARCH-002-GATEWAY-009 | gateway | Complete | 1 | ARCH-002-GATEWAY-003, ARCH-002-GATEWAY-008, ARCH-002-GATEWAY-010, ARCH-002-GATEWAY-011 |
| ARCH-002-GATEWAY-010 | gateway | Complete | 1 | ARCH-002-GATEWAY-008 |
| ARCH-002-GATEWAY-011 | gateway | Complete | 2 | ARCH-002-GATEWAY-010 |
| ARCH-002-GATEWAY-012 | gateway | Complete | 2 | ARCH-002-GATEWAY-009, ARCH-002-GATEWAY-011 |
| ARCH-002-GATEWAY-013 | gateway | Pending | 0 | ARCH-002-GATEWAY-012 |
| ARCH-002-GATEWAY-014 | gateway | Complete | 8 | ARCH-002-GATEWAY-009, ARCH-002-GATEWAY-012 |
| ARCH-002-SYSTEM-TEST-001 | system-test | Pending / manual-gated | 0 | ARCH-002-SYSTEM-TEST-002, ARCH-002-SYSTEM-TEST-006, ARCH-002-SYSTEM-TEST-007, ARCH-002-SYSTEM-TEST-008 |
| ARCH-002-SYSTEM-TEST-002 | system-test | Complete | 3 | ARCH-002-SHOPIFY-007, ARCH-002-BACKGROUND-007, ARCH-002-BACKGROUND-009, ARCH-002-MESSAGING-004, ARCH-002-MESSAGING-005, ARCH-002-ADMIN-009, ARCH-002-GATEWAY-006, ARCH-002-GATEWAY-004, ARCH-002-SYSTEM-TEST-003, ARCH-002-SYSTEM-TEST-004, ARCH-002-SYSTEM-TEST-005 |
| ARCH-002-SYSTEM-TEST-003 | system-test | Complete | 1 | — |
| ARCH-002-SYSTEM-TEST-004 | system-test | Complete | 2 | ARCH-002-BACKGROUND-010 |
| ARCH-002-SYSTEM-TEST-005 | system-test | Complete | 2 | — |
| ARCH-002-SYSTEM-TEST-006 | system-test | Complete | 11 | ARCH-002-GATEWAY-004, ARCH-002-ADMIN-004, ARCH-002-SHOPIFY-008, ARCH-002-GATEWAY-008, ARCH-002-GATEWAY-009, ARCH-002-GATEWAY-010, ARCH-002-GATEWAY-012, ARCH-002-GATEWAY-014 |
| ARCH-002-SYSTEM-TEST-007 | system-test | Complete | 3 | ARCH-002-GATEWAY-004 |
| ARCH-002-SYSTEM-TEST-008 | system-test | Pending / manual-gated | 0 | ARCH-002-SYSTEM-TEST-002, ARCH-002-SYSTEM-TEST-006, ARCH-002-SYSTEM-TEST-007, ARCH-002-SYSTEM-TEST-009 |
| ARCH-002-SYSTEM-TEST-009 | system-test | Complete | 3 | ARCH-002-GATEWAY-010, ARCH-002-GATEWAY-011, ARCH-002-GATEWAY-012, ARCH-002-SYSTEM-TEST-007 |
| ARCH-002-SYSTEM-TEST-010 | system-test | **Ready** | 0 | ARCH-002-GATEWAY-014 |

## ARCH-003

Current counts: `blocked` 1, `complete` 23, `pending` 1, `review` 1, `superseded` 1

| Task | Domain | Status | Attempt | Dependencies |
|---|---|---|---:|---|
| ARCH-003-SHOPIFY-001 | shopify | Complete | 1 | — |
| ARCH-003-SHOPIFY-002 | shopify | Complete | 3 | ARCH-003-SHOPIFY-001, ARCH-003-BACKGROUND-002 |
| ARCH-003-SHOPIFY-003 | shopify | Complete | 1 | ARCH-003-SHOPIFY-002 |
| ARCH-003-BACKGROUND-001 | background | Complete | 1 | ARCH-003-ADMIN-013 |
| ARCH-003-BACKGROUND-002 | background | Complete | 1 | ARCH-003-BACKGROUND-001 |
| ARCH-003-BACKGROUND-003 | background | Complete | 3 | ARCH-003-BACKGROUND-002 |
| ARCH-003-ADMIN-001 | admin | Complete | 3 | ARCH-002-ADMIN-011 |
| ARCH-003-ADMIN-002 | admin | Complete | 1 | ARCH-003-ADMIN-001 |
| ARCH-003-ADMIN-003 | admin | Complete | 1 | ARCH-003-ADMIN-008 |
| ARCH-003-ADMIN-004 | admin | Complete | 1 | ARCH-003-ADMIN-003 |
| ARCH-003-ADMIN-005 | admin | Complete | 1 | ARCH-003-ADMIN-004 |
| ARCH-003-ADMIN-006 | admin | Complete | 2 | ARCH-003-ADMIN-005 |
| ARCH-003-ADMIN-007 | admin | Complete | 1 | ARCH-003-ADMIN-006 |
| ARCH-003-ADMIN-008 | admin | Complete | 2 | ARCH-003-ADMIN-002 |
| ARCH-003-ADMIN-009 | admin | Superseded | 0 | ARCH-003-ADMIN-008 |
| ARCH-003-ADMIN-010 | admin | Complete | 1 | ARCH-003-ADMIN-007 |
| ARCH-003-ADMIN-011 | admin | Complete | 4 | ARCH-003-ADMIN-010, ARCH-003-ADMIN-014 |
| ARCH-003-ADMIN-012 | admin | Complete | 1 | ARCH-003-ADMIN-016 |
| ARCH-003-ADMIN-013 | admin | Complete | 1 | ARCH-003-ADMIN-012 |
| ARCH-003-ADMIN-014 | admin | Complete | 2 | ARCH-003-ADMIN-010 |
| ARCH-003-ADMIN-015 | admin | Complete | 1 | ARCH-003-ADMIN-011 |
| ARCH-003-ADMIN-016 | admin | Complete | 1 | ARCH-003-ADMIN-015 |
| ARCH-003-ADMIN-017 | admin | Complete | 1 | ARCH-003-BACKGROUND-001 |
| ARCH-003-ADMIN-018 | admin | Complete | 1 | ARCH-003-ADMIN-017 |
| ARCH-003-ADMIN-019 | admin | **Review — Attempt 1** | 1 | ARCH-003-ADMIN-018 |
| ARCH-003-SYSTEM-TEST-001 | system-test | Pending / manual-gated | 0 | ARCH-003-BACKGROUND-001, ARCH-003-ADMIN-019 |
| ARCH-003-SYSTEM-TEST-002 | system-test | **Blocked** | 2 | ARCH-003-SHOPIFY-002 |

## ARCH-004

Current counts: `complete` 6, `ready` 1

| Task | Domain | Status | Attempt | Dependencies |
|---|---|---|---:|---|
| ARCH-004-SHARED-001 | shared | Complete | 1 | — |
| ARCH-004-SHARED-002 | shared | Complete | 1 | ARCH-004-SHARED-001 |
| ARCH-004-SHOPIFY-001 | shopify | Complete | 1 | ARCH-004-SHARED-002 |
| ARCH-004-SHOPIFY-002 | shopify | Complete | 1 | ARCH-004-BACKGROUND-002 |
| ARCH-004-BACKGROUND-001 | background | Complete | 2 | ARCH-004-SHARED-002 |
| ARCH-004-BACKGROUND-002 | background | Complete | 1 | ARCH-004-BACKGROUND-001 |
| ARCH-004-SYSTEM-TEST-001 | system-test | **Ready** | 0 | ARCH-004-SHARED-002, ARCH-004-SHOPIFY-001, ARCH-004-BACKGROUND-002, ARCH-004-SHOPIFY-002 |

## ARCH-005

Current counts: `complete` 17, `pending` 2, `ready` 1, `superseded` 2

| Task | Domain | Status | Attempt | Dependencies |
|---|---|---|---:|---|
| ARCH-005-DATABASE-001 | database | Complete | 2 | ARCH-005-SHARED-001 |
| ARCH-005-DATABASE-002 | database | Complete | 2 | ARCH-005-DATABASE-001 |
| ARCH-005-SHARED-001 | shared | Complete | 4 | — |
| ARCH-005-SHARED-002 | shared | Complete | 1 | ARCH-005-SHARED-001 |
| ARCH-005-SHARED-003 | shared | Complete | 1 | ARCH-005-SHARED-002 |
| ARCH-005-SHARED-004 | shared | Complete | 1 | ARCH-005-SHARED-003 |
| ARCH-005-SHARED-005 | shared | Complete | 2 | ARCH-005-SHARED-004 |
| ARCH-005-SHARED-006 | shared | Complete | 1 | ARCH-005-SHARED-005 |
| ARCH-005-SHOPIFY-001 | shopify | Complete | 3 | ARCH-005-SHARED-002, ARCH-005-DATABASE-001 |
| ARCH-005-SHOPIFY-002 | shopify | Complete | 6 | ARCH-005-SHARED-006, ARCH-005-DATABASE-001 |
| ARCH-005-SHOPIFY-003 | shopify | Complete | 1 | ARCH-005-SHARED-004, ARCH-005-BACKGROUND-001 |
| ARCH-005-SHOPIFY-004 | shopify | **Ready** | 0 | ARCH-005-SHOPIFY-002, ARCH-006-SHOPIFY-003, ARCH-007-SHOPIFY-002 |
| ARCH-005-MESSAGING-001 | messaging | Superseded | 1 | ARCH-005-SHARED-002, ARCH-005-DATABASE-001, ARCH-005-DATABASE-002, ARCH-005-BACKGROUND-001 |
| ARCH-005-MESSAGING-002 | messaging | Superseded | 0 | ARCH-005-MESSAGING-001 |
| ARCH-005-MESSAGING-003 | messaging | Complete | 1 | ARCH-005-BACKGROUND-002, ARCH-005-BACKGROUND-003 |
| ARCH-005-BACKGROUND-001 | background | Complete | 4 | ARCH-005-SHARED-004, ARCH-005-DATABASE-001 |
| ARCH-005-BACKGROUND-002 | background | Complete | 1 | ARCH-005-BACKGROUND-001, ARCH-005-DATABASE-002 |
| ARCH-005-BACKGROUND-003 | background | Complete | 2 | ARCH-005-BACKGROUND-002 |
| ARCH-005-BACKGROUND-004 | background | Complete | 4 | ARCH-005-BACKGROUND-001 |
| ARCH-005-ADMIN-001 | admin | Complete | 4 | ARCH-005-SHARED-006 |
| ARCH-005-SYSTEM-TEST-001 | system-test | Pending / manual-gated | 0 | ARCH-005-SHOPIFY-001, ARCH-005-SHOPIFY-003, ARCH-005-BACKGROUND-001, ARCH-005-BACKGROUND-002, ARCH-005-BACKGROUND-003, ARCH-005-SHOPIFY-002, ARCH-005-SHOPIFY-004, ARCH-005-MESSAGING-003 |
| ARCH-005-SYSTEM-TEST-002 | system-test | Pending / manual-gated | 0 | ARCH-005-SYSTEM-TEST-001, ARCH-005-BACKGROUND-004 |

## ARCH-006

Current counts: `complete` 21, `pending` 3, `review` 3, `superseded` 2

| Task | Domain | Status | Attempt | Dependencies |
|---|---|---|---:|---|
| ARCH-006-DATABASE-001 | database | Complete | 1 | — |
| ARCH-006-DATABASE-002 | database | Complete | 1 | ARCH-006-DATABASE-001 |
| ARCH-006-SHARED-001 | shared | Complete | 1 | ARCH-005-SHARED-001, ARCH-006-DATABASE-002 |
| ARCH-006-SHARED-002 | shared | Complete | 1 | ARCH-006-SHARED-001 |
| ARCH-006-SHARED-003 | shared | Complete | 1 | ARCH-006-SHARED-002 |
| ARCH-006-SHARED-004 | shared | Complete | 1 | ARCH-006-SHARED-003 |
| ARCH-006-SHARED-005 | shared | Complete | 1 | ARCH-006-SHARED-004 |
| ARCH-006-SHARED-006 | shared | Complete | 1 | ARCH-006-SHARED-005 |
| ARCH-006-SHOPIFY-001 | shopify | Complete | 1 | ARCH-006-DATABASE-002, ARCH-006-SHARED-002, ARCH-006-SHARED-004, ARCH-005-DATABASE-001 |
| ARCH-006-SHOPIFY-002 | shopify | Complete | 5 | ARCH-006-SHOPIFY-001 |
| ARCH-006-SHOPIFY-003 | shopify | Complete | 4 | ARCH-006-SHOPIFY-001, ARCH-006-BACKGROUND-007, ARCH-005-SHOPIFY-002 |
| ARCH-006-BACKGROUND-001 | background | Complete | 1 | ARCH-006-DATABASE-002, ARCH-006-SHARED-002 |
| ARCH-006-BACKGROUND-002 | background | Superseded | 0 | — |
| ARCH-006-BACKGROUND-003 | background | Superseded | 0 | — |
| ARCH-006-BACKGROUND-004 | background | Complete | 2 | ARCH-006-BACKGROUND-001, ARCH-006-SHARED-004 |
| ARCH-006-BACKGROUND-005 | background | Complete | 2 | ARCH-006-BACKGROUND-004 |
| ARCH-006-BACKGROUND-006 | background | Complete | 3 | ARCH-006-BACKGROUND-005 |
| ARCH-006-BACKGROUND-007 | background | Complete | 3 | ARCH-006-BACKGROUND-006 |
| ARCH-006-BACKGROUND-008 | background | Complete | 1 | ARCH-006-BACKGROUND-004, ARCH-006-SHARED-006 |
| ARCH-006-BACKGROUND-009 | background | **Review — Attempt 1** | 1 | ARCH-006-BACKGROUND-005, ARCH-006-BACKGROUND-006, ARCH-006-BACKGROUND-007, ARCH-006-BACKGROUND-008 |
| ARCH-006-ADMIN-001 | admin | Complete | 3 | ARCH-006-DATABASE-002, ARCH-006-SHARED-002, ARCH-006-SHARED-004, ARCH-005-ADMIN-001 |
| ARCH-006-ADMIN-002 | admin | Complete | 1 | ARCH-006-BACKGROUND-007 |
| ARCH-006-ADMIN-003 | admin | Complete | 1 | ARCH-006-ADMIN-001 |
| ARCH-006-ADMIN-004 | admin | Complete | 6 | ARCH-006-ADMIN-003, ARCH-006-BACKGROUND-007 |
| ARCH-006-ADMIN-005 | admin | **Review — Attempt 2** | 2 | ARCH-006-ADMIN-004 |
| ARCH-006-GATEWAY-001 | gateway | **Review — Attempt 2** | 2 | ARCH-006-BACKGROUND-007 |
| ARCH-006-SYSTEM-TEST-001 | system-test | Pending / manual-gated | 0 | ARCH-006-ADMIN-004, ARCH-006-SHOPIFY-003, ARCH-006-GATEWAY-001 |
| ARCH-006-SYSTEM-TEST-002 | system-test | Pending / manual-gated | 0 | ARCH-006-SHOPIFY-002, ARCH-006-SHOPIFY-003, ARCH-006-GATEWAY-001 |
| ARCH-006-SYSTEM-TEST-003 | system-test | Pending / manual-gated | 0 | ARCH-006-BACKGROUND-007, ARCH-006-GATEWAY-001, ARCH-006-ADMIN-001, ARCH-006-SHOPIFY-001 |

## ARCH-007

Current counts: `complete` 21, `pending` 13, `ready` 5

| Task | Domain | Status | Attempt | Dependencies |
|---|---|---|---:|---|
| ARCH-007-DATABASE-001 | database | Complete | 2 | — |
| ARCH-007-DATABASE-002 | database | Complete | 2 | ARCH-007-DATABASE-001 |
| ARCH-007-DATABASE-003 | database | Complete | 1 | ARCH-007-DATABASE-002 |
| ARCH-007-DATABASE-004 | database | Complete | 1 | ARCH-007-DATABASE-003 |
| ARCH-007-DATABASE-005 | database | Complete | 2 | ARCH-007-DATABASE-004 |
| ARCH-007-DATABASE-006 | database | Complete | 1 | ARCH-007-DATABASE-005 |
| ARCH-007-SHARED-001 | shared | Complete | 6 | ARCH-007-DATABASE-003 |
| ARCH-007-SHARED-002 | shared | Complete | 1 | ARCH-007-SHARED-001 |
| ARCH-007-SHARED-003 | shared | Complete | 1 | ARCH-007-SHARED-002 |
| ARCH-007-SHARED-004 | shared | Complete | 1 | ARCH-007-SHARED-003 |
| ARCH-007-SHARED-005 | shared | Complete | 1 | ARCH-007-DATABASE-005 |
| ARCH-007-SHARED-006 | shared | Complete | 1 | ARCH-007-SHARED-005 |
| ARCH-007-SHOPIFY-001 | shopify | Complete | 3 | ARCH-007-SHARED-002, ARCH-007-DATABASE-003 |
| ARCH-007-SHOPIFY-002 | shopify | Complete | 3 | ARCH-007-SHOPIFY-001 |
| ARCH-007-SHOPIFY-003 | shopify | **Ready** | 1 | ARCH-007-SHOPIFY-001 |
| ARCH-007-SHOPIFY-004 | shopify | Pending | 0 | ARCH-007-SHOPIFY-002, ARCH-007-DATABASE-005, ARCH-007-SHARED-006, ARCH-007-ADMIN-005 |
| ARCH-007-MESSAGING-001 | messaging | Complete | 3 | ARCH-007-SHARED-002, ARCH-007-SHARED-004 |
| ARCH-007-BACKGROUND-001 | background | Complete | 2 | ARCH-007-SHARED-002, ARCH-007-DATABASE-003 |
| ARCH-007-BACKGROUND-002 | background | Complete | 2 | ARCH-007-BACKGROUND-001 |
| ARCH-007-BACKGROUND-003 | background | Complete | 2 | ARCH-007-BACKGROUND-002, ARCH-007-SHOPIFY-001 |
| ARCH-007-BACKGROUND-004 | background | Complete | 4 | ARCH-007-BACKGROUND-003, ARCH-007-DATABASE-004 |
| ARCH-007-BACKGROUND-005 | background | **Ready** | 0 | ARCH-007-BACKGROUND-004, ARCH-007-MESSAGING-001, ARCH-007-SHARED-004 |
| ARCH-007-BACKGROUND-006 | background | Complete | 2 | ARCH-007-SHARED-002, ARCH-007-DATABASE-002 |
| ARCH-007-BACKGROUND-007 | background | Complete | 3 | ARCH-007-BACKGROUND-003, ARCH-007-BACKGROUND-006 |
| ARCH-007-BACKGROUND-008 | background | Pending | 0 | ARCH-007-BACKGROUND-005, ARCH-007-BACKGROUND-007, ARCH-007-BACKGROUND-009, ARCH-007-SHOPIFY-001 |
| ARCH-007-BACKGROUND-009 | background | **Ready** | 0 | ARCH-007-DATABASE-005, ARCH-007-SHARED-006, ARCH-007-BACKGROUND-007 |
| ARCH-007-BACKGROUND-010 | background | **Ready** | 0 | ARCH-007-DATABASE-006, ARCH-007-BACKGROUND-004 |
| ARCH-007-BACKGROUND-011 | background | Pending | 0 | ARCH-007-BACKGROUND-010 |
| ARCH-007-ADMIN-001 | admin | **Ready** | 0 | ARCH-007-SHARED-002, ARCH-007-DATABASE-003 |
| ARCH-007-ADMIN-002 | admin | Pending | 0 | ARCH-007-ADMIN-001 |
| ARCH-007-ADMIN-003 | admin | Pending | 0 | ARCH-007-ADMIN-002, ARCH-007-BACKGROUND-007, ARCH-007-SHOPIFY-001 |
| ARCH-007-ADMIN-004 | admin | Pending | 0 | ARCH-007-ADMIN-003, ARCH-007-BACKGROUND-008 |
| ARCH-007-ADMIN-005 | admin | Pending | 0 | ARCH-007-ADMIN-001, ARCH-007-DATABASE-005, ARCH-007-SHARED-006 |
| ARCH-007-GATEWAY-001 | gateway | Pending | 0 | ARCH-007-BACKGROUND-008 |
| ARCH-007-SYSTEM-TEST-001 | system-test | Pending / manual-gated | 0 | ARCH-007-SHOPIFY-002, ARCH-007-BACKGROUND-003, ARCH-007-ADMIN-002 |
| ARCH-007-SYSTEM-TEST-002 | system-test | Pending / manual-gated | 0 | ARCH-007-SHOPIFY-002, ARCH-007-BACKGROUND-008, ARCH-007-ADMIN-004, ARCH-007-GATEWAY-001 |
| ARCH-007-SYSTEM-TEST-003 | system-test | Pending / manual-gated | 0 | ARCH-007-SHOPIFY-003, ARCH-007-MESSAGING-001, ARCH-007-BACKGROUND-005, ARCH-007-BACKGROUND-008, ARCH-007-ADMIN-004, ARCH-007-GATEWAY-001 |
| ARCH-007-SYSTEM-TEST-004 | system-test | Pending / manual-gated | 0 | ARCH-007-SHOPIFY-004, ARCH-007-BACKGROUND-009, ARCH-007-BACKGROUND-008, ARCH-007-ADMIN-005 |
| ARCH-007-SYSTEM-TEST-005 | system-test | Pending / manual-gated | 0 | ARCH-007-BACKGROUND-010, ARCH-007-BACKGROUND-004, ARCH-007-BACKGROUND-011 |

## ARCH-010

> Synchronized by `moda_architect` on 2026-09-13 from authoritative individual task YAML after DATABASE-014 and ADMIN-010 acceptance and dependency-frontier recomputation. ARCH-010 is a PRE-PRODUCTION / BREAKING ROLLOUT. Superseded tasks are history only; system-test tasks remain terminal/manual-gated.

Current counts: `complete` 41, `ready` 3, `pending` 34, `superseded` 8

| Task | Domain | Status | Attempt | Dependencies |
|---|---|---|---:|---|
| ARCH-010-ADMIN-001 | admin | Complete | 2 | ARCH-010-DATABASE-006 |
| ARCH-010-ADMIN-002 | admin | Pending | 0 | ARCH-010-DATABASE-014, ARCH-010-BACKGROUND-022, ARCH-010-SHOPIFY-025, ARCH-010-SHARED-008, ARCH-010-ADMIN-010 |
| ARCH-010-ADMIN-003 | admin | Pending | 0 | ARCH-010-ADMIN-002, ARCH-010-BACKGROUND-022, ARCH-010-SHARED-008, ARCH-010-DATABASE-014, ARCH-010-BACKGROUND-021 |
| ARCH-010-ADMIN-004 | admin | **Ready** | 0 | ARCH-010-DATABASE-013, ARCH-010-ADMIN-010 |
| ARCH-010-ADMIN-005 | admin | Pending | 0 | ARCH-010-ADMIN-004 |
| ARCH-010-ADMIN-006 | admin | Pending | 0 | ARCH-010-ADMIN-005, ARCH-010-DATABASE-013 |
| ARCH-010-ADMIN-007 | admin | Complete | 2 | — |
| ARCH-010-ADMIN-008 | admin | **Ready** | 0 | ARCH-010-DATABASE-013, ARCH-010-ADMIN-001, ARCH-010-ADMIN-010 |
| ARCH-010-ADMIN-009 | admin | Pending | 0 | ARCH-010-ADMIN-007, ARCH-010-ADMIN-008 |
| ARCH-010-ADMIN-010 | admin | Complete | 2 | ARCH-010-DATABASE-013, ARCH-010-SHARED-008, ARCH-010-ADMIN-001 |
| ARCH-010-BACKGROUND-001 | background | Complete | 6 | ARCH-010-DATABASE-006, ARCH-010-DATABASE-001, ARCH-010-DATABASE-004, ARCH-010-SHARED-002, ARCH-007-BACKGROUND-008 |
| ARCH-010-BACKGROUND-002 | background | Complete | 3 | ARCH-010-BACKGROUND-011, ARCH-010-DATABASE-013, ARCH-007-BACKGROUND-003, ARCH-007-BACKGROUND-009 |
| ARCH-010-BACKGROUND-003 | background | Pending | 0 | ARCH-010-DATABASE-013, ARCH-010-BACKGROUND-001, ARCH-010-BACKGROUND-007, ARCH-010-SHARED-008, ARCH-007-BACKGROUND-008 |
| ARCH-010-BACKGROUND-004 | background | Complete | 3 | — |
| ARCH-010-BACKGROUND-005 | background | Complete | 3 | — |
| ARCH-010-BACKGROUND-006 | background | Pending | 0 | ARCH-010-DATABASE-013, ARCH-010-SHARED-008, ARCH-010-BACKGROUND-001, ARCH-010-BACKGROUND-003, ARCH-010-BACKGROUND-007, ARCH-010-BACKGROUND-004, ARCH-010-BACKGROUND-005 |
| ARCH-010-BACKGROUND-007 | background | Pending | 0 | ARCH-010-BACKGROUND-001, ARCH-010-BACKGROUND-002, ARCH-010-BACKGROUND-008, ARCH-010-BACKGROUND-009, ARCH-010-DATABASE-013, ARCH-010-SHARED-008, ARCH-008-BACKGROUND-001 |
| ARCH-010-BACKGROUND-008 | background | Complete | 3 | ARCH-010-BACKGROUND-002, ARCH-010-SHARED-008, ARCH-010-BACKGROUND-019 |
| ARCH-010-BACKGROUND-009 | background | **Ready** | 0 | ARCH-010-DATABASE-013, ARCH-010-SHARED-008, ARCH-010-BACKGROUND-002, ARCH-010-BACKGROUND-011, ARCH-007-BACKGROUND-003, ARCH-007-BACKGROUND-009, ARCH-010-BACKGROUND-019 |
| ARCH-010-BACKGROUND-010 | background | Pending | 0 | ARCH-010-DATABASE-013, ARCH-010-BACKGROUND-003, ARCH-010-BACKGROUND-007, ARCH-010-SHARED-008 |
| ARCH-010-BACKGROUND-011 | background | Complete | 4 | ARCH-010-DATABASE-013, ARCH-010-SHARED-008, ARCH-010-BACKGROUND-001, ARCH-007-BACKGROUND-003, ARCH-007-BACKGROUND-009 |
| ARCH-010-BACKGROUND-012 | background | Pending | 0 | ARCH-010-DATABASE-013, ARCH-010-BACKGROUND-007, ARCH-010-BACKGROUND-010, ARCH-010-BACKGROUND-009, ARCH-010-SHARED-008, ARCH-010-BACKGROUND-015 |
| ARCH-010-BACKGROUND-013 | background | Pending | 0 | ARCH-010-BACKGROUND-004, ARCH-010-BACKGROUND-005, ARCH-010-BACKGROUND-012 |
| ARCH-010-BACKGROUND-014 | background | Complete | 2 | ARCH-010-DATABASE-013, ARCH-010-BACKGROUND-011 |
| ARCH-010-BACKGROUND-015 | background | Complete | 4 | — |
| ARCH-010-BACKGROUND-016 | background | Superseded | 0 | ARCH-010-DATABASE-013, ARCH-010-BACKGROUND-007, ARCH-010-BACKGROUND-010, ARCH-010-BACKGROUND-015, ARCH-010-SHARED-008 |
| ARCH-010-BACKGROUND-017 | background | Superseded | 0 | ARCH-010-BACKGROUND-004, ARCH-010-BACKGROUND-005, ARCH-010-BACKGROUND-013, ARCH-010-BACKGROUND-016 |
| ARCH-010-BACKGROUND-018 | background | Pending | 0 | ARCH-010-BACKGROUND-004, ARCH-010-BACKGROUND-012 |
| ARCH-010-BACKGROUND-019 | background | Complete | 6 | ARCH-010-DATABASE-013, ARCH-010-BACKGROUND-002, ARCH-010-BACKGROUND-011, ARCH-010-BACKGROUND-014 |
| ARCH-010-BACKGROUND-020 | background | Complete | 1 | ARCH-010-SHARED-006 |
| ARCH-010-BACKGROUND-021 | background | Pending | 0 | ARCH-010-DATABASE-014, ARCH-010-BACKGROUND-015, ARCH-010-SHOPIFY-014 |
| ARCH-010-BACKGROUND-022 | background | Pending | 0 | ARCH-010-DATABASE-014, ARCH-010-BACKGROUND-014, ARCH-010-BACKGROUND-019, ARCH-010-BACKGROUND-021 |
| ARCH-010-DATABASE-001 | database | Complete | 2 | ARCH-007-DATABASE-006, ARCH-009-DATABASE-001 |
| ARCH-010-DATABASE-002 | database | Complete | 1 | ARCH-010-DATABASE-001, ARCH-007-DATABASE-005 |
| ARCH-010-DATABASE-003 | database | Complete | 1 | ARCH-010-DATABASE-001 |
| ARCH-010-DATABASE-004 | database | Complete | 2 | ARCH-010-DATABASE-002 |
| ARCH-010-DATABASE-005 | database | Complete | 2 | — |
| ARCH-010-DATABASE-006 | database | Complete | 3 | ARCH-007-DATABASE-002, ARCH-007-DATABASE-003 |
| ARCH-010-DATABASE-007 | database | Complete | 4 | — |
| ARCH-010-DATABASE-008 | database | Complete | 3 | — |
| ARCH-010-DATABASE-009 | database | Complete | 3 | ARCH-007-DATABASE-002 |
| ARCH-010-DATABASE-010 | database | Complete | 1 | ARCH-010-DATABASE-009 |
| ARCH-010-DATABASE-011 | database | Complete | 3 | ARCH-010-DATABASE-009, ARCH-010-DATABASE-010 |
| ARCH-010-DATABASE-012 | database | Superseded | 0 | ARCH-010-DATABASE-006 |
| ARCH-010-DATABASE-013 | database | Complete | 2 | ARCH-010-DATABASE-001, ARCH-010-DATABASE-002, ARCH-010-DATABASE-003, ARCH-010-DATABASE-004, ARCH-010-DATABASE-005, ARCH-010-DATABASE-006, ARCH-010-DATABASE-007, ARCH-010-DATABASE-008, ARCH-010-DATABASE-009, ARCH-010-DATABASE-010, ARCH-010-DATABASE-011 |
| ARCH-010-DATABASE-014 | database | Complete | 2 | ARCH-010-DATABASE-013 |
| ARCH-010-GATEWAY-001 | gateway | Complete | 2 | ARCH-002-GATEWAY-001 |
| ARCH-010-SHARED-001 | shared | Complete | 2 | ARCH-007-SHARED-006 |
| ARCH-010-SHARED-002 | shared | Complete | 1 | ARCH-010-SHARED-001 |
| ARCH-010-SHARED-003 | shared | Complete | 1 | ARCH-010-SHARED-001 |
| ARCH-010-SHARED-004 | shared | Complete | 0 | ARCH-010-SHARED-003 |
| ARCH-010-SHARED-005 | shared | Complete | 1 | — |
| ARCH-010-SHARED-006 | shared | Complete | 0 | ARCH-010-SHARED-005 |
| ARCH-010-SHARED-007 | shared | Complete | 2 | ARCH-010-SHARED-006, ARCH-010-BACKGROUND-020, ARCH-010-SHOPIFY-024 |
| ARCH-010-SHARED-008 | shared | Complete | 1 | ARCH-010-SHARED-007 |
| ARCH-010-SHOPIFY-001 | shopify | Complete | 3 | ARCH-007-SHOPIFY-001, ARCH-007-SHOPIFY-002 |
| ARCH-010-SHOPIFY-002 | shopify | Complete | 8 | ARCH-010-DATABASE-006, ARCH-010-SHOPIFY-001, ARCH-010-DATABASE-001, ARCH-010-DATABASE-004, ARCH-010-SHARED-002, ARCH-007-SHOPIFY-001, ARCH-007-SHOPIFY-002 |
| ARCH-010-SHOPIFY-003 | shopify | Pending | 0 | ARCH-010-DATABASE-013, ARCH-010-SHOPIFY-002, ARCH-010-BACKGROUND-002, ARCH-010-BACKGROUND-003, ARCH-008-SHOPIFY-001, ARCH-010-SHOPIFY-023 |
| ARCH-010-SHOPIFY-004 | shopify | Pending | 0 | ARCH-010-SHOPIFY-003, ARCH-010-DATABASE-013 |
| ARCH-010-SHOPIFY-005 | shopify | Superseded | 0 | ARCH-010-BACKGROUND-004, ARCH-010-BACKGROUND-005 |
| ARCH-010-SHOPIFY-006 | shopify | Pending | 0 | ARCH-010-DATABASE-013, ARCH-010-SHARED-008, ARCH-010-BACKGROUND-006 |
| ARCH-010-SHOPIFY-007 | shopify | Pending | 0 | ARCH-010-BACKGROUND-007, ARCH-010-DATABASE-013, ARCH-010-SHARED-008, ARCH-010-SHOPIFY-003, ARCH-010-SHOPIFY-004 |
| ARCH-010-SHOPIFY-008 | shopify | Pending | 0 | ARCH-010-SHOPIFY-009, ARCH-010-SHOPIFY-012, ARCH-010-BACKGROUND-009, ARCH-010-SHARED-008 |
| ARCH-010-SHOPIFY-009 | shopify | Pending | 0 | ARCH-010-DATABASE-013, ARCH-010-SHOPIFY-004, ARCH-010-SHOPIFY-023 |
| ARCH-010-SHOPIFY-010 | shopify | Superseded | 0 | ARCH-010-SHOPIFY-014 |
| ARCH-010-SHOPIFY-011 | shopify | Superseded | 0 | ARCH-010-SHOPIFY-013, ARCH-010-SHOPIFY-015 |
| ARCH-010-SHOPIFY-012 | shopify | Pending | 0 | ARCH-010-SHOPIFY-009, ARCH-010-SHOPIFY-013, ARCH-010-SHOPIFY-018, ARCH-010-SHOPIFY-014, ARCH-010-SHOPIFY-015, ARCH-010-SHOPIFY-007, ARCH-008-SHOPIFY-001 |
| ARCH-010-SHOPIFY-013 | shopify | Complete | 1 | ARCH-008-SHOPIFY-001 |
| ARCH-010-SHOPIFY-014 | shopify | Pending | 0 | ARCH-010-SHOPIFY-013, ARCH-010-SHOPIFY-007, ARCH-007-SHOPIFY-004, ARCH-010-SHOPIFY-018, ARCH-010-DATABASE-014 |
| ARCH-010-SHOPIFY-015 | shopify | Pending | 0 | ARCH-010-SHOPIFY-013, ARCH-010-SHARED-008, ARCH-010-BACKGROUND-010, ARCH-010-SHOPIFY-018 |
| ARCH-010-SHOPIFY-016 | shopify | Pending | 0 | ARCH-010-SHOPIFY-009, ARCH-010-SHOPIFY-012, ARCH-010-SHOPIFY-013, ARCH-010-SHOPIFY-018, ARCH-010-BACKGROUND-012, ARCH-010-BACKGROUND-013 |
| ARCH-010-SHOPIFY-017 | shopify | Superseded | 0 | ARCH-010-DATABASE-013, ARCH-010-SHARED-008, ARCH-010-SHOPIFY-012 |
| ARCH-010-SHOPIFY-018 | shopify | Complete | 3 | ARCH-010-DATABASE-013, ARCH-010-SHOPIFY-013, ARCH-010-SHOPIFY-023 |
| ARCH-010-SHOPIFY-019 | shopify | Superseded | 0 | ARCH-010-BACKGROUND-017, ARCH-010-SHOPIFY-009, ARCH-010-SHOPIFY-012, ARCH-010-SHOPIFY-018 |
| ARCH-010-SHOPIFY-020 | shopify | Pending | 0 | ARCH-010-SHOPIFY-009, ARCH-010-SHOPIFY-012, ARCH-010-SHOPIFY-021 |
| ARCH-010-SHOPIFY-021 | shopify | Pending | 0 | ARCH-010-DATABASE-013, ARCH-010-SHOPIFY-018, ARCH-010-ADMIN-004 |
| ARCH-010-SHOPIFY-022 | shopify | Pending | 0 | ARCH-010-SHOPIFY-021, ARCH-010-DATABASE-013 |
| ARCH-010-SHOPIFY-023 | shopify | Complete | 1 | ARCH-010-DATABASE-013, ARCH-010-SHARED-008, ARCH-010-SHOPIFY-002 |
| ARCH-010-SHOPIFY-024 | shopify | Complete | 1 | ARCH-010-SHARED-006, ARCH-010-SHOPIFY-002 |
| ARCH-010-SHOPIFY-025 | shopify | Pending | 0 | ARCH-010-DATABASE-014, ARCH-010-BACKGROUND-021, ARCH-010-BACKGROUND-022, ARCH-010-SHOPIFY-014, ARCH-010-SHARED-008 |
| ARCH-010-SHOPIFY-026 | shopify | Pending | 0 | ARCH-010-SHOPIFY-025, ARCH-010-SHOPIFY-012 |
| ARCH-010-SYSTEM-TEST-001 | system-test | Pending / manual-gated | 0 | ARCH-010-GATEWAY-001, ARCH-010-BACKGROUND-007, ARCH-010-BACKGROUND-009, ARCH-010-BACKGROUND-010, ARCH-010-BACKGROUND-019, ARCH-010-DATABASE-014, ARCH-010-BACKGROUND-021, ARCH-010-BACKGROUND-022, ARCH-010-SHOPIFY-012, ARCH-010-SHOPIFY-020 |
| ARCH-010-SYSTEM-TEST-002 | system-test | Pending / manual-gated | 0 | ARCH-010-BACKGROUND-006, ARCH-010-BACKGROUND-012, ARCH-010-BACKGROUND-013, ARCH-010-BACKGROUND-018, ARCH-010-SHOPIFY-006, ARCH-010-SHOPIFY-016 |
| ARCH-010-SYSTEM-TEST-003 | system-test | Pending / manual-gated | 0 | ARCH-010-DATABASE-014, ARCH-010-BACKGROUND-021, ARCH-010-BACKGROUND-022, ARCH-010-BACKGROUND-019, ARCH-010-SHOPIFY-025, ARCH-010-SHOPIFY-026, ARCH-010-ADMIN-003, ARCH-010-ADMIN-005, ARCH-010-ADMIN-006, ARCH-010-SHOPIFY-020, ARCH-010-SHOPIFY-021, ARCH-010-SHOPIFY-022 |
| ARCH-010-SYSTEM-TEST-004 | system-test | Pending / manual-gated | 0 | ARCH-010-SYSTEM-TEST-001, ARCH-010-SYSTEM-TEST-002, ARCH-010-SYSTEM-TEST-003, ARCH-010-SYSTEM-TEST-005 |
| ARCH-010-SYSTEM-TEST-005 | system-test | Pending / manual-gated | 0 | ARCH-010-DATABASE-013, ARCH-010-ADMIN-009 |
Current Ready frontier: `ARCH-010-BACKGROUND-009`, `ARCH-010-ADMIN-004`, `ARCH-010-ADMIN-008`.

`ARCH-010-SHOPIFY-002` is architect-accepted Complete at Attempt 8. `ARCH-010-BACKGROUND-001` is architect-accepted Complete at Attempt 6. Their accepted task histories are immutable; clean first-production conformance is owned by later Pending/Ready tasks.

Task-consolidation supersessions:

```text
BACKGROUND-016 -> BACKGROUND-012
BACKGROUND-017 -> BACKGROUND-013
SHOPIFY-010   -> SHOPIFY-014
SHOPIFY-011   -> SHOPIFY-015
SHOPIFY-019   -> SHOPIFY-016
```

`ARCH-010-DATABASE-012` remains Superseded by DATABASE-013, and `ARCH-010-SHOPIFY-005` remains Superseded by SHOPIFY-006.

For current sequencing use `ARCH-010-implementation-handoff.md`; individual task `depends_on` remains authoritative.

## ARCH-019 — merchant recovery experience (2026-09-20)

Current frontier: all ARCH-019 implementation tasks are architect-accepted/Complete: DATABASE-001 and SHOPIFY-001/003/006 at Attempt 1, SHOPIFY-002 at Attempt 3, SHOPIFY-004/005 at Attempt 2. SHOPIFY-006 accepted `39054cec`. SYSTEM-TEST-001 Ready at Attempt 0, explicitly developer-invoked after manual validation; not started. Architecture remains In Progress pending terminal integrated validation and final architect acceptance. Accepted dependency records are reconciled into SYSTEM-TEST-001; readiness does not authorize execution, deployment or unmerged dependency consumption.

[Architecture](ARCH-019-merchant-recovery-experience.md) · [Implementation handoff](ARCH-019-implementation-handoff.md)

## ARCH-020 — initial review definitions (2026-09-20)

Scoped addition only; earlier architecture rollups are unchanged. Source:
[ARCH-020 architecture](ARCH-020-commerce-agent-studio-mcp-capabilities.md) and
[handoff](ARCH-020-implementation-handoff.md). Individual task YAML is authoritative.
COMMERCE-001 is architect-accepted Complete at Attempt 3 (`d7c1c65`). The descendant-process cleanup correction passed focused functional validation; prior real Docker PostgreSQL/Redis readiness evidence is retained. COMMERCE-002 is architect-accepted Complete at Attempt 2 (`fb3362e`): development HTTP mutations and revoked-session recovery are corrected. Live Google OAuth remains developer-owned deployment validation. Downstream source consumption awaits developer integration or explicit accepted-commit approval; no task is promoted or launched. COMMERCE-001 remains accepted and integrated. Other task rows retain this branch snapshot; canonical task worktrees remain authoritative.

| Task | Domain | Status | Attempt | Dependencies |
|---|---|---|---:|---|
| ARCH-020-DATABASE-001 | database | complete | 2 | ARCH-016-DATABASE-001 |
| ARCH-020-SHARED-001 | shared | complete | 2 | ARCH-016-SHARED-001 |
| ARCH-020-COMMERCE-001 | commerce | complete | 3 | — |
| ARCH-020-COMMERCE-002 | commerce | complete | 2 | ARCH-020-COMMERCE-001 |
| ARCH-020-COMMERCE-003 | commerce | pending | 0 | ARCH-020-COMMERCE-002, ARCH-020-DATABASE-001, ARCH-020-SHARED-001, ARCH-020-COMMERCE-011 |
| ARCH-020-COMMERCE-004 | commerce | pending | 0 | ARCH-020-COMMERCE-003, ARCH-020-SHARED-001 |
| ARCH-020-COMMERCE-005 | commerce | pending | 0 | ARCH-020-COMMERCE-004, ARCH-020-COMMERCE-011 |
| ARCH-020-COMMERCE-006 | commerce | pending | 0 | ARCH-020-COMMERCE-005, ARCH-016-BACKGROUND-001, ARCH-016-DATABASE-001 |
| ARCH-020-COMMERCE-007 | commerce | pending | 0 | ARCH-020-COMMERCE-006 |
| ARCH-020-COMMERCE-008 | commerce | ready | 2 | ARCH-020-COMMERCE-002, ARCH-020-DATABASE-001, ARCH-020-SHARED-001 |
| ARCH-020-COMMERCE-009 | commerce | pending | 0 | ARCH-020-COMMERCE-008, ARCH-020-COMMERCE-007, ARCH-020-SHARED-001 |
| ARCH-020-COMMERCE-010 | commerce | pending | 0 | ARCH-020-COMMERCE-004, ARCH-020-COMMERCE-007, ARCH-020-COMMERCE-009 |
| ARCH-020-COMMERCE-011 | commerce | pending | 0 | ARCH-020-COMMERCE-002, ARCH-020-SHARED-001 |
| ARCH-020-BACKGROUND-001 | background | complete | 3 | ARCH-016-BACKGROUND-003, ARCH-020-SHARED-001, ARCH-020-DATABASE-001, ARCH-020-COMMERCE-001  |
| ARCH-020-BACKGROUND-002 | background | pending | 0 | ARCH-020-BACKGROUND-001, ARCH-020-COMMERCE-007 |
| ARCH-020-SHOPIFY-001 | shopify | complete | 1 | ARCH-020-SHARED-001, ARCH-016-SHOPIFY-002 |
| ARCH-020-GATEWAY-001 | gateway | pending | 0 | ARCH-020-COMMERCE-002, ARCH-020-BACKGROUND-001, ARCH-020-COMMERCE-008, ARCH-020-COMMERCE-011 |
| ARCH-020-GATEWAY-002 | gateway | pending | 0 | ARCH-020-GATEWAY-001, ARCH-020-COMMERCE-010, ARCH-020-BACKGROUND-002 |
| ARCH-020-COMMERCE-012 | commerce | pending | 0 | All other ARCH-020 implementation tasks; readiness checkpoint in task |
| ARCH-020-SYSTEM-TEST-001 | system-test | pending | 0 | ARCH-020-BACKGROUND-001, ARCH-020-BACKGROUND-002, ARCH-020-COMMERCE-001, ARCH-020-COMMERCE-002, ARCH-020-COMMERCE-003, ARCH-020-COMMERCE-004, ARCH-020-COMMERCE-005, ARCH-020-COMMERCE-006, ARCH-020-COMMERCE-007, ARCH-020-COMMERCE-008, ARCH-020-COMMERCE-009, ARCH-020-COMMERCE-010, ARCH-020-COMMERCE-011, ARCH-020-DATABASE-001, ARCH-020-GATEWAY-001, ARCH-020-GATEWAY-002, ARCH-020-SHARED-001, ARCH-020-SHOPIFY-001  , ARCH-020-COMMERCE-012  |

## Historical DATABASE-001 architect review — Attempt 1 — 2026-09-20

Attempt 1 is **Changes Requested**, task `ready`, attempt 1, claim cleared.
The implementation/report PRs are #33/#165 (0e992c4 / 312e350b). Preserve the
implementation and rehearsal history. Required corrections are the newer C16
CommerceRelease responseContract/responseContractHash persistence and negative
fixtures that currently permit unrelated constraint failures. The full correction
contract is in the task's Architect Review. C16 was incorporated by parent synchronization commit 7fef4689 from canonical
workspace commit a710df26; its semantic consumer requirements remain binding.

Guarded writes require READ COMMITTED or SERIALIZABLE with bounded transaction
retries; REPEATABLE READ is rejected. BACKGROUND-001 and COMMERCE-003 must honor
that database restriction when implementing grants/publication. No dependency is
promoted by this review; SYSTEM-TEST-001 remains terminal and manually invoked.
Other task states in this branch's older definition snapshot are not a fresh
review of their separate execution branches. Integrate latest parent main before
reclaiming this task, preserving its report, review and attempt metadata.

## DATABASE-001 architect acceptance — 2026-09-20

ARCH-020-DATABASE-001 is **Accepted / Complete, Attempt 2**. Implementation
30de940 (tested source a835207) and report 17c9f9ab satisfy R1 C16 response
persistence and R2 rejection-fixture isolation. Reviewed 298 distinct passing
checks per fresh/upgrade rehearsal, including controls; preservation covers
57 existing tables, 41 seeded rows and 217 indexes. Static/Prisma checks passed.
The previous Changes Requested section is historical and superseded.

No downstream promotion: canonical SHARED-001 is in_progress, COMMERCE-001 is
review, and COMMERCE-002/011 remain pending. BACKGROUND-001 and COMMERCE-003 still
have incomplete prerequisites. Terminal SYSTEM-TEST-001 remains pending/manual.
Other task table rows are branch-local snapshots, not fresh acceptance decisions.

Guarded consumers use READ COMMITTED or SERIALIZABLE with bounded whole-transaction
retries; REPEATABLE READ is rejected. Shared/Commerce own semantic response-schema
validation and canonical hash equality; Commerce owns atomic release assembly,
authorization and audit. Merge database PR #33 first, pin its final integrated
database-main commit in the parent, then merge parent PR #165. No main integration
or gitlink update is performed by this acceptance. ARCH-020 is not Implemented.

## Shared Attempt 1 architect review — 2026-09-20

ARCH-020-SHARED-001 returned to Ready with Changes Requested against implementation
34be970 and report f713caed: R1 whole-definition persistence size compatibility;
R2 malformed model-call error classification. Attempt 1 is preserved and the
claim is clear. Package 0.13.0 is published but not architect-accepted; corrections
require a new verified registry version. No downstream task is promoted.
See the canonical Shared task's latest Architect Review for the correction contract.
Parent main synchronization preserves DATABASE-001 Complete at Attempt 2 and
COMMERCE-001 Complete at Attempt 3 alongside this Shared correction contract.
Current branch frontier: 19 tasks, 2 Complete, 1 Ready, 16 Pending, 0 Blocked.
SHARED-001 remains Ready at Attempt 1 with no active claim. No next attempt is
claimed by conflict resolution. Architecture completion/system-test gates remain.


## Shared Attempt 2 acceptance — 2026-09-20

ARCH-020-SHARED-001 is **Accepted / Complete, Attempt 2** against implementation
a83bfc1 and report 595566ca. R1 storage-size compatibility and R2 malformed-model
classification are closed. Independently passed typecheck, 30 focused tests and
clean registry-consumer smoke; reviewed 160-pass/one-skipped full-suite evidence.
Verified registry artifact **@modainteract/moda-interact-shared@0.13.1**, with all
75 installed files matching publication files. Consumer tasks must use 0.13.1.
The earlier Shared correction/frontier record is historical and superseded.

BACKGROUND-001 (moda_background) and SHOPIFY-001 (moda_app) are newly Ready: all
listed dependencies are Complete. No task is claimed or launched. Preparation
must synchronize dedicated worktrees and verify dependency source availability.
Other pending tasks retain their existing gates. Current branch frontier:
**19 tasks, 3 Complete, 2 Ready, 14 Pending, 0 Blocked**. System testing remains
terminal/manual; ARCH-020 is not Implemented. No main merge or gitlink change.


## BACKGROUND-001 review scope amendments — 2026-09-20

BACKGROUND-001 remains **Review, Attempt 1**, with no active claim or acceptance.
User A1/A2 add deterministic shop/phone-country initial language and approved
initial/follow-up template selection, then substantive text/speech language;
and configurable OpenAI spoken-language transcription alongside retained Groq.
These are **scope amendments, not defects against the original task**. See the
canonical task's named A1-L01–L06/A2-V01–V07 cases and binding C6.2/C6.3.
Shared/Database phone-country provenance prerequisites require separate new-scope
materialisation/acceptance; Gateway owns hosted provider/model/secret wiring.
The submitted implementation/report and accepted prerequisite history remain.
No new attempt or downstream task is launched; expanded-scope acceptance pending.

## Shopify merchant preferences acceptance — 2026-09-20

SHOPIFY-001 is architect-accepted Complete at Attempt 1 (`4693bba`, report
`c5016d73`). Merchant eligibility, explicit idempotent saves and guarded form
behavior conform; architect reran 18 passing focused checks and reviewed six
passing PostgreSQL tests plus build/browser evidence. Existing repository-wide
typecheck/lint limitations remain documented. SYSTEM-TEST-001 remains Pending
until all its implementation dependencies are accepted, then explicitly
user-invoked; no task is launched. Developer integration remains separate.

Historical pre-acceptance snapshot: 19 tasks, 4 Complete, 1 Ready, 14 Pending; superseded for BACKGROUND-001 by the Attempt 3 acceptance below.
Other canonical task worktrees remain authoritative for concurrent progress;
this review does not overwrite their state. Prior readiness records are historical.
ARCH-020 caching addition: COMMERCE-012 is Pending (attempt 0), depends on all other implementation tasks and precedes SYSTEM-TEST-001. Active scope is 20 tasks; existing task execution states are not reset.

## Simplified language decision — 2026-09-20 (current)

The user withdrew phone-country inference: initialize from shop language, then
respond in clearly detected customer text/speech language. C6.2 and BACKGROUND-001
A1 specify this rule. Earlier phone-country/Review coordination notes are historical
and superseded. Both unclaimed provenance tasks were removed with their dependency
edges. BACKGROUND-001 is Ready, Attempt 1 retained, no active claim; A2 transcription
scope remains. All four retained prerequisites are accepted Complete. Active task
scope returns to 20; no automatic execution or expanded-scope acceptance occurred.


## BACKGROUND-001 Attempt 2 architect review — Changes Requested

Reviewed implementation 399cc2f and report 0ed91909. **Ready, Attempt 2 preserved,
claim cleared**, not accepted. R1 confuses earlier audio completion time with a
new message's sent time; R2 treats completion of the preceding reply as superseding
new audio. Both reproduce as ignored valid messages. The canonical task's latest
Architect Review contains the correction contract and validation expectations.
The original A1/A2 scope amendments are not retroactive defects; these findings
concern the submitted amended implementation. Simplified shop-language scope
remains; no phone-country prerequisites are restored. No downstream promotion or
new attempt is claimed. Older Background review/in-progress/readiness statements
are historical; this is the current decision. Architecture remains unaccepted.

## BACKGROUND-001 user-directed review hold

Current status: Review, Attempt 2, no active claim. User requested no re-preparation or new claim. This supersedes the prior Ready/preparation direction only; R1/R2 remain unresolved against implementation 399cc2f and acceptance remains withheld. No downstream promotion.

## BACKGROUND-001 return to Ready

Latest user instruction restores Ready for reviewed R1/R2 corrections, Attempt 2, executor/claimed_at null. This supersedes the preceding Review hold. Acceptance remains withheld; no preparation, new claim or downstream promotion is performed by this update.

## BACKGROUND-001 Attempt 3 architect acceptance — 2026-09-20

ARCH-020-BACKGROUND-001 is **Accepted / Complete, Attempt 3**, implementation
`4e42056`, report `7a3cf35d`. R1/R2 are resolved: persisted inbound ordering
replaces completion-time comparisons, and finishing an earlier reply does not
discard valid pending audio. Architect independently reran **133 passing tests**
and reviewed the submitted passing build and local real-SDK compatibility evidence.
The existing configurable OpenAI adapter and A1/A2 amendments are accepted.
Live audio-quality and PostgreSQL concurrency checks remain explicitly not run;
no deployed integration or acoustic-quality result is asserted.

This is the current decision and supersedes earlier BACKGROUND-001 Ready/Review
and Changes Requested notes. Other task states remain unchanged. BACKGROUND-002,
GATEWAY-001, COMMERCE-012 and SYSTEM-TEST-001 retain remaining dependency gates;
no dependent task is promoted or launched. Developer integration remains separate,
and ARCH-020 is not complete. See the task's latest Architect Review for limits.

## COMMERCE-008 Attempt 1 — Changes Requested — 2026-09-21

COMMERCE-008 is **Ready, Attempt 1 retained**, claim cleared, not accepted.
Reviewed implementation `865e16c` and report `a6df81c1`. Authenticated shell and
route scaffolding exist, but C17 StudioServices ports, authoring workflows,
record resolution and required navigation behavior remain unimplemented.
The task's latest Architect Review records R1–R3. Component/fixture behavior and
local browser evidence remain008-owned; real provider composition remains013-owned.
Readiness uses002, DATABASE-001 and SHARED-001, not the superseded service chain.
No new claim, downstream promotion, implementation edit or main integration.
Other canonical task states remain authoritative; ARCH-020 is not complete.

## COMMERCE-008 Attempt 2 — Changes Requested — 2026-09-21

COMMERCE-008 is **Ready, Attempt 2 retained**, claim cleared, not accepted.
Reviewed `6c4ecbc` / report `10fc0ae6` (PR3/171). Typed unavailable/not-found states
and shell improvements are retained. Remaining blockers are canonical port/data
mismatches, incomplete connected authoring/release workflows, unsafe unknown-outcome
retry, and exact-revision/navigation behavior. Latest task review records R1–R4.
C17 still allows fixture component acceptance; real adapters and readiness timing
failures are not the blocker. No new claim, downstream promotion, implementation
edit or main integration. Other task states remain unchanged.


## COMMERCE-008 Attempt 3 review — 2026-09-21

Current decision: Ready, Attempt3 retained, claim cleared; Changes Requested.
Reviewed00c40087 /826f871e.14 focused Studio tests pass independently;3 added
review cases fail (lost second tool binding, stale release validation unlocking,
fixture-valid definition rejected by Shared). A3-R1–R4 specify canonical query/
definition authoring, complete binding preservation, content-bound validation,
and actual persistent navigation/dirty guards. Static/no-op browser harness does
not prove page traversal. Preserve common component boundary and replay progress;
013 production composition remains separate. No promotion, claim or main merge.
