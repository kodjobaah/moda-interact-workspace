# ARCH-007 BACKGROUND-010 Attempt 3 review note

Attempt 3 received **Changes Requested**.

Attempt 3 successfully fixed the previous BullMQ active-job deferral,
discriminated routing, persistence, provider-boundary and recovery-ordering
corrections.

Attempt 4 is limited to two final runtime corrections:

1. replace the architect's invalid colon-delimited BullMQ custom job-id contract
   with:

   `conversation-turn__<conversationId>__<observedVersion>`

2. make a clarification that resolves to one recovery construct a valid context
   from that recovery plus the standalone clarification fragments, and require
   current candidate ownership to match the durable clarification
   shop/customer pair.

The custom-job-id change corrects the task contract itself; it is not treated as
an Attempt 3 agent deviation.

Per developer instruction, Attempt 4 remains under the legacy no-branch,
no-commit, no-push workflow. The new mirrored feature-branch workflow starts
only after B010 is architect-accepted.
