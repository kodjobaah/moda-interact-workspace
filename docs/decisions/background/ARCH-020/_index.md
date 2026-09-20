# ARCH-020 background tasks

Architecture: [ARCH-020-commerce-agent-studio-mcp-capabilities.md](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).

Assigned agent: moda_background. Repository: moda-interact-background. Coordinator: moda_architect.

Definitions are on local main for review by explicit developer request. Individual task YAML is authoritative; no task is claimed or launched. Commerce submodule provisioning remains a prerequisite; the owner and route are defined in this packet.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [ARCH-020-BACKGROUND-001](BACKGROUND-001-integrate-the-generic-mcp-commerceagent-host.md) | Integrate the generic MCP CommerceAgent host | review | ARCH-016-BACKGROUND-003, ARCH-020-SHARED-001, ARCH-020-DATABASE-001, ARCH-020-COMMERCE-001 |
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
