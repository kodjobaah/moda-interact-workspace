---
id: ARCH-010-SITE-001
architecture_id: ARCH-010
title: Update the public pricing page from the 2026 investor proposal
task_kind: implementation
domain: site
repository: moda-interact-site
assigned_agent: moda_site
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-26
updated: 2026-10-26
---

# Update the public pricing page from the 2026 investor proposal

## Architecture

Architecture ID:

ARCH-010

Architecture document:

docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md

Coordinator:

moda_architect

## Objective

Update the public Moda Interact site pricing presentation to reflect the proposal in `Moda_Interact_Investor_Report_Pricing_2026.pdf`, while making unmistakable that every displayed price, allowance and top-up is a planning assumption rather than a verified production offer or charge.

## Context

The current public pricing content uses GBP and older plan allowances and bundle quantities. The investor report proposes a USD catalogue for Shopify and WooCommerce. The workspace README and ARCH-010 product model document that the investor figures are not the current canonical runtime/provider configuration and have not been verified as live merchant charges.

The report is currently an untracked user-supplied PDF, not a durable task dependency. The developer must have the original report available when starting this task. If it is unavailable in the canonical implementation worktree or as a supplied artifact, stop and request it; do not infer or silently copy values from the existing page or summary text.

Read first:

- `docs/product/pricing-and-billing-model.md`
- `README.md` pricing note
- The supplied `Moda_Interact_Investor_Report_Pricing_2026.pdf`

## Scope

- Compare the proposed plan prices, included recovery credits, cycle/grant terms, bundle names, credit quantities and bundle prices in the PDF against the current public pricing content.
- Update the relevant public site pricing sections and any translations or page metadata required by the site's existing conventions.
- Clearly distinguish the investor proposal from current production/runtime billing and provider availability.
- Preserve the existing site structure, design conventions, accessibility and responsive behaviour.

## Out of Scope

- Changing Shopify or WooCommerce provider billing configuration, runtime entitlements, recovery-credit policy, product data or the canonical ARCH-010 model.
- Presenting any proposed report value as a verified live price, available provider offer, production allowance or guaranteed charge.
- Making pricing claims outside the report or changing unrelated pages/site content.
- Changing shared services, other repositories, or the PDF itself.

## Requirements

- Treat the PDF as the source for the proposed public presentation and verify every displayed value against it.
- Use USD consistently wherever the report specifies USD; preserve the report's distinctions between plan prices, included credits, lifetime Free credits, 30-day paid entitlement cycles and one-off bundles.
- Make the proposal status conspicuous near the pricing content, not only in a distant footer or metadata. State that the prices, allowances and top-ups are planning assumptions and are not verified production charges or confirmed live provider offers; availability, provider configuration, taxes and final terms remain subject to verification.
- Do not imply that the report changes current runtime behaviour. Keep the public presentation explicitly framed as proposed/planning pricing until a separate product/provider decision verifies it.
- Describe the recovery-credit unit and inclusions only to the extent supported by the report. Do not turn message, AI or provider-cost assumptions into guaranteed production terms.
- Follow the site's existing internationalisation and accessibility patterns for any changed content. If the site does not provide a translation for new wording, use its established fallback behaviour rather than leaving locale pages with contradictory pricing claims.

## Work Items

- [ ] Verify the PDF's proposed plan and bundle tables and compare them with the current site content.
- [ ] Update the public pricing presentation to the verified proposed USD values and terms.
- [ ] Add conspicuous planning-assumption and non-production-charge wording wherever needed to prevent a live-offer interpretation.
- [ ] Update relevant locale strings, page metadata and responsive/accessibility details following existing site conventions.
- [ ] Complete focused site validation and record commands/results below.

## Interfaces / Contracts

None. This is a public content/presentation task and does not change a runtime or provider contract.

## Dependencies

None. No runtime implementation task is a prerequisite because this task must not change canonical billing behaviour or claim that the proposal is live.

## Enables

None.

## Acceptance Criteria

- [ ] Every proposed price, included allowance, cycle/grant term, bundle quantity and bundle price shown on the site matches the supplied PDF.
- [ ] Currency and cycle wording are consistent with the PDF; no stale or conflicting pricing values remain in the affected public pricing presentation or its relevant locale strings.
- [ ] A clear, conspicuous statement identifies the figures as planning assumptions, not verified production charges or confirmed live provider offers.
- [ ] The presentation does not imply that runtime/provider configuration has changed or that merchants can currently purchase the listed plans or bundles.
- [ ] Existing site structure, accessibility, localization conventions and responsive layouts remain intact for the changed content.
- [ ] No files outside `moda-interact-site/` are changed.
- [ ] Required validation is complete, or any unavailable check and reason are recorded in the Completion Report.

## Validation

- [ ] Inspect the site repository's actual scripts/tooling and run the declared, relevant formatting/content validation checks; do not invent an npm script if none exists.
- [ ] Validate any changed locale data with the repository's existing validation method.
- [ ] Exercise the pricing page at desktop and mobile widths and in the relevant locale(s); verify the planning disclaimer, all tables, links and text remain readable and do not overlap.
- [ ] Search the affected pricing content and translations for stale GBP prices, allowances or bundle quantities from the previous presentation.

## Stop Condition

After completing the defined Work Items, Acceptance Criteria and required Validation, update the Completion Report, submit the task for developer review, and STOP. Do not change ARCH-010 runtime/product policy or begin follow-on work.

## Implementation Notes

- Keep the presentation within the existing public site design and content conventions; do not redesign unrelated parts of the site.
- The proposal table recorded in the workspace README is a useful cross-check, not a substitute for comparing the supplied PDF itself.
- Keep this task limited to `moda-interact-site/`. Any newly discovered product-policy or provider-verification requirement must be returned to `moda_architect` rather than resolved in site copy.

## Completion Report

### Status

Not Started

### Files Changed

Not Started

### Work Completed

Not Started

### Validation Results

Not Run

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

Not Reviewed

### Reviewed Files

Not Reviewed

### Validation Reviewed

Not Reviewed

### Architecture Conformance

Not Reviewed

### Follow-up

None
