# ARCH-020 background tasks

Architecture: [ARCH-020-commerce-agent-studio-mcp-capabilities.md](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).

Assigned agent: moda_background. Repository: moda-interact-background. Coordinator: moda_architect.

Definitions are on local main for review by explicit developer request. Individual task YAML is authoritative; no task is claimed or launched. Commerce submodule provisioning remains a prerequisite; the owner and route are defined in this packet.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [ARCH-020-BACKGROUND-001](BACKGROUND-001-integrate-the-generic-mcp-commerceagent-host.md) | Integrate the generic MCP CommerceAgent host | ready | ARCH-016-BACKGROUND-003, ARCH-020-SHARED-001, ARCH-020-DATABASE-001, ARCH-020-COMMERCE-001  |
| [ARCH-020-BACKGROUND-002](BACKGROUND-002-preserve-turn-safeguards-and-validate-offer-replies.md) | Preserve turn safeguards and validate offer replies | pending | ARCH-020-BACKGROUND-001, ARCH-020-COMMERCE-007 |

BACKGROUND-001 is in Review at Attempt 1; A1/A2 are new user scope amendments, with no acceptance or active claim.


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
