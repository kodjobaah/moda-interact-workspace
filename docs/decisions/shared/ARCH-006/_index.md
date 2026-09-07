# ARCH-006 Shared Tasks

Architecture: `docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

Assigned Agent: `moda_shared`

Coordinator: `moda_architect`

| Task | Description | Status | Dependencies |
|---|---|---|---|
| SHARED-001 | Merchant communications validation and BullMQ contracts | Complete | ARCH-005-SHARED-001, DATABASE-002 |
| SHARED-002 | Publish shared release `0.7.0` | Complete | SHARED-001 |
| SHARED-003 | Correct broken `merchant-communications/node` export | Complete | SHARED-002 |
| SHARED-004 | Publish corrected release `0.7.1` and verify from clean consumer | Complete | SHARED-003 |
| SHARED-005 | Standardise disposable PostgreSQL/Redis integration-test infrastructure | Complete | SHARED-004 |
| SHARED-006 | Publish reusable integration-test infrastructure release | Complete | SHARED-005 |

The individual task file YAML metadata is authoritative.

Architect finding on 2026-09-06: `0.7.0` is genuinely published but its new Node subpath export does not resolve to the files emitted by the accepted build. The historical SHARED-001/002 tasks remain Complete; remediation is SHARED-003 -> SHARED-004. Consumers that require ARCH-006 deterministic job-ID helpers are blocked until SHARED-004 is architect-accepted Complete.

Architect review on 2026-09-06: SHARED-003 is accepted Complete after independent review of the package-boundary correction. SHARED-004 is the only newly Ready task and remains the publication gate before blocked consumers may resume.

Architect review on 2026-09-06: SHARED-004 is accepted Complete. Registry publication and clean-consumer runtime verification establish `@modainteract/moda-interact-shared@0.7.1` as the corrected ARCH-006 consumer release. The architect, not the Shared agent, releases downstream consumer tasks.

Architect coordination on 2026-09-06: SHARED-005 is Ready as a parallel, non-gating quality-infrastructure task. Its Node-only testing subpath becomes the reusable home for disposable PostgreSQL/Redis lifecycle plus authoritative `prisma migrate deploy`; SHARED-006 owns publication. Product implementation tasks do not wait for this chain.


Architect review on 2026-09-06: SHARED-005 Attempt 1 is accepted Complete after independent review of the Node-only disposable PostgreSQL/Redis harness, authoritative caller-supplied `prisma migrate deploy` boundary, cleanup behavior, package-boundary validation and recorded live Docker migration validation. SHARED-006 is Ready for publication/clean-consumer verification. BACKGROUND-008 remains Pending until SHARED-006 is published and architect-accepted.

Architect review on 2026-09-06: SHARED-006 Attempt 1 is accepted Complete. `@modainteract/moda-interact-shared@0.7.2` is published and clean-consumer verified with the Node-only `testing/node` subpath. Publication changed only package version metadata; the SHARED-005 implementation remained unchanged. BACKGROUND-008 is released to Ready by `moda_architect`; product implementation remains independent of this quality-infrastructure chain.
