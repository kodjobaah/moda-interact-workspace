---
id: ARCH-032-GATEWAY-001
architecture_id: ARCH-032
title: Provision private standalone MCP runtime without traffic cutover
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-032-MCP-001
enables: []
created: 2026-10-10
updated: 2026-10-10
---

# Provision private standalone MCP runtime

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md`

## Objective

Add an infrastructure-only, private, independent `moda-interact-mcp` Render
service to both the test and production blueprints. No public MCP hostname,
HAProxy route, background URL change, Commerce MCP removal or live cutover.
This is a **follow-on** task, not included in MCP-001's source patch.

## Scope

Read first: `moda-interact-gateway/render.test.yaml`,
`moda-interact-gateway/render.production.yaml`,
`moda-interact-gateway/tests/validate-render-blueprints.sh`,
`docs/decisions/gateway/ARCH-026/GATEWAY-001-wire-hosted-merchant-api-topology.md`.

- Model a new private `pserv` (`moda-interact-mcp-test` and
  `moda-interact-mcp-production`) with the canonical MCP repository URL.
- Use the foundation's real `npm run build` / `npm run start` and private port;
  align with existing Render runtime and shared observability environment.
- Do not copy or expose API-owned WooCommerce credential keyrings.
- Do not deploy the stub while readiness is intentionally 503. Hold actual
  service launch/traffic until a later MCP task delivers real readiness,
  protocol/authorization and documented environment requirements.
- Add bounded Blueprint validation, deployment docs and negative checks.
- Do not alter `COMMERCE_MCP_URL`, public host routing, Commerce Studio,
  API, Background or MCP implementation source.

## Acceptance criteria

- Both environments have a single correctly named private MCP service,
  no public routes, and preserved existing topology/ingress behaviour.
- New readiness config is grounded in the actually implemented runtime,
  not invented. Infrastructure work does not allow premature deployment.
- Render topology/negative validation passes in the Gateway repository.
- Separate future architect-approved cutover remains mandatory.

## Completion report

Pending later assignment to moda_gateway after MCP readiness and dependency
review. No infrastructure files are modified by MCP-001.
