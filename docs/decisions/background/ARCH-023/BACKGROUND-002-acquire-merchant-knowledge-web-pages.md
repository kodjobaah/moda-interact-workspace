---
id: ARCH-023-BACKGROUND-002
architecture_id: ARCH-023
title: Acquire Merchant Knowledge web pages safely
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 31
executor: copilot
claimed_at: 2026-09-30T15:33:08Z
attempt: 2
depends_on:
  - ARCH-023-BACKGROUND-001
enables:
  - ARCH-023-BACKGROUND-004
created: 2026-09-29
updated: 2026-09-30
---

# Acquire Merchant Knowledge web pages safely

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Implement the `WEB_PAGE` acquisition adapter only: SSRF-safe HTTPS retrieval, redirect/DNS/connected-peer validation, bounded decompression, media-type validation and deterministic human-visible HTML/plain-text extraction.

This task returns extracted source text through the BACKGROUND-001 `MerchantKnowledgeWebPageAcquirer` contract. It does not normalize, truncate, chunk, embed or persist semantic content.

## Scope

Authorized primary files:

```text
package.json
package-lock.json

src/services/merchant-knowledge-web-page-acquirer.ts
src/services/merchant-knowledge-network-policy.ts
src/services/merchant-knowledge-html-extraction.ts

tests/unit/services/merchant-knowledge-network-policy.test.ts
tests/unit/services/merchant-knowledge-html-extraction.test.ts
tests/unit/services/merchant-knowledge-web-page-acquirer.test.ts
```

Use Node built-ins for DNS, TLS/HTTPS, decompression and timing. Add only the HTML parser dependency required by this task.

## Out of Scope

- BullMQ worker orchestration.
- R2.
- CSV/XLSX.
- database writes.
- normalization/content units.
- chunking.
- embeddings.
- pgvector.
- entitlement reconciliation.
- automatic crawling/scheduled refresh.
- JavaScript execution/headless browser.
- authentication/cookies sent to merchant sites.

## Requirements

### R1 — exact request policy

`MerchantKnowledgeWebPageAcquirer.acquire({requestedUrl})` must enforce:

```text
URL length <= 2048 Unicode/code-unit characters as supplied
scheme exactly https:
no username
no password
maximum 5 redirects
overall acquisition deadline 10_000 ms
maximum decompressed body 1_048_576 bytes
accepted media types exactly:
  text/html
  text/plain
```

The media type comparison ignores parameters such as `charset=UTF-8` but no other MIME type is accepted.

Do not downgrade to HTTP.

### R2 — exact destination validation

Validate the initial URL and every redirect independently.

For hostname destinations:

1. resolve all current A/AAAA answers;
2. reject if resolution returns no addresses;
3. reject the hostname if **any** returned address is non-public;
4. sort validated answers deterministically by:
   ```text
   family ASC (IPv4 before IPv6), address lexical ASC
   ```
5. select the first address for that request;
6. bind the actual HTTPS connection to that selected address via a custom lookup/connection path while preserving the original hostname for TLS SNI/certificate verification;
7. after connection, require the socket peer address to equal the selected validated address.

For an IP-literal hostname:

1. validate that literal directly;
2. connect only to that validated literal.

Every redirect repeats the full algorithm. Do not reuse the prior redirect target's DNS decision.

### R3 — public-address policy

Use a tested IP parser/classifier rather than regular-expression range detection.

Permitted destination:

```text
globally routable unicast only
```

Reject at minimum:

```text
IPv4/IPv6 unspecified
loopback
private
link-local
unique-local
carrier-grade NAT
multicast
broadcast
reserved/documentation/special-use
IPv4-mapped IPv6 when mapped IPv4 is not public
cloud/link-local metadata addresses including 169.254.169.254
```

If a hostname resolves to one public and one denied address, reject the hostname entirely.

### R4 — no credential propagation

Requests must send no:

```text
Authorization
Cookie
Proxy-Authorization
Shopify session
Moda service token
R2 credential
```

Use only a bounded generic User-Agent plus ordinary `Accept`/`Accept-Encoding` headers required by this implementation.

Do not forward headers from the merchant browser or another application request.

### R5 — redirect rules

Follow only standard redirect statuses:

```text
301
302
303
307
308
```

A redirect must contain a valid absolute or relative `Location`.

Resolve relative `Location` against the current URL, then re-run R1-R3.

More than 5 redirects is a permanent acquisition error.

### R6 — compressed response handling

Support only:

```text
identity / absent Content-Encoding
gzip
deflate
br
```

Unknown/multiple unsupported encodings fail permanently.

The 1 MiB bound applies to **decompressed bytes**. Abort the stream as soon as the bound would be exceeded.

Do not buffer an unbounded compressed or decompressed response.

### R7 — response status

Only HTTP status:

```text
200
```

is a successful source response after redirects.

Treat:

```text
408
425
429
500
502
503
504
connection reset
DNS temporary failure
request deadline
```

as transient acquisition failures.

Treat other final non-200 statuses as permanent acquisition failures.

Export bounded error classes/codes so BACKGROUND-004 can distinguish transient from permanent failures without parsing error-message text.

### R8 — deterministic HTML extraction

For `text/plain`:

1. decode UTF-8 with replacement for malformed sequences;
2. return the decoded text unchanged except no normalization performed here.

For `text/html`, parse HTML without executing anything.

Ignore entire subtrees for:

```text
script
style
noscript
template
iframe
svg
canvas
```

Also ignore elements with:

```text
hidden attribute
aria-hidden="true"
```

Do not fetch:

```text
script src
iframe src
stylesheet
image
font
media
CSS
```

Traverse the remaining DOM in document order.

Append text-node content in order.
Insert exactly one LF boundary before/after common block elements:

```text
address article aside blockquote br div dl dt dd fieldset
figcaption figure footer form h1 h2 h3 h4 h5 h6 header hr
li main nav ol p pre section table tbody td tfoot th thead tr ul
```

Collapse is **not** performed here; BACKGROUND-004 owns D3 normalization.

Return the raw extracted sequence.

### R9 — acquisition result shape

Success returns:

```ts
{
  contentType: "text/html" | "text/plain";
  extractedText: string;
  resolvedUrl: finalUrl.toString();
  fetchedAt: Date;
}
```

`resolvedUrl` is the final post-redirect public HTTPS URL.

Never return response headers wholesale.

### R10 — focused adversarial tests

Tests must prove:

```text
http: rejected before request
userinfo rejected
URL > 2048 rejected
loopback literal rejected
private literal rejected
link-local metadata rejected
IPv6 loopback/unique-local rejected
hostname with any denied DNS answer rejected
custom connection uses validated selected address
connected peer mismatch rejected
each redirect is re-resolved/revalidated
redirect to private target rejected before connection
6th redirect rejected
overall deadline enforced
decompressed > 1MiB rejected
unsupported content encoding rejected
unsupported MIME rejected
final 404 permanent
final 429 transient
final 503 transient
scripts/styles/iframes excluded
relative subresources never fetched
text order deterministic
plain text preserved for later normalization
```

Tests must use local controlled servers/fakes; no external internet dependency.

## Work Items

- [x] Implement public-IP classification.
- [x] Implement DNS resolution and connection binding.
- [x] Implement redirect-safe HTTPS fetch.
- [x] Implement bounded decompression/media validation.
- [x] Implement deterministic HTML/plain-text extraction.
- [x] Implement transient/permanent acquisition error types.
- [x] Add adversarial unit tests.
- [x] Validate no unrelated processing/persistence work was introduced.

## Interfaces / Contracts

Implements BACKGROUND-001:

```text
MerchantKnowledgeWebPageAcquirer
```

Produces:

```text
AcquiredMerchantKnowledgeDocument
```

for BACKGROUND-004.

## Dependencies

- `ARCH-023-BACKGROUND-001`

## Enables

- `ARCH-023-BACKGROUND-004`

## Acceptance Criteria

- [x] No denied destination can be contacted, including through redirects or mixed DNS answers.
- [x] Actual connection is bound to and verified against the validated IP.
- [x] No merchant/Moda credentials are propagated.
- [x] Decompressed response size is bounded at 1 MiB.
- [x] Only HTML/plain text is accepted.
- [x] HTML extraction executes/fetches no active content/subresources.
- [x] Adapter returns extracted source text only.
- [x] No database writes/normalization/embedding work exists in this task.

## Validation

- [x] focused network-policy tests
- [x] focused HTML-extraction tests
- [x] focused acquirer tests
- [x] `npm run build`
- [x] `git diff --check`
- [x] changed-file diagnostics clean

## Stop Condition

Set status to `review`, complete Completion Report, return to `moda_architect` and STOP. Do not start BACKGROUND-004.

## Implementation Notes

Prefer built-in `node:https`, `node:dns/promises`, `node:zlib` and a small dedicated HTML parser. Do not introduce Playwright/Puppeteer/jsdom solely to fetch or render Merchant Knowledge.

## Completion Report

### Status
Attempt 2 complete; ready for Architect Review.
### Files Changed
Attempt 2 changed `src/services/merchant-knowledge-network-policy.ts`, `tests/unit/services/merchant-knowledge-network-policy.test.ts`, and `tests/unit/services/merchant-knowledge-web-page-acquirer.test.ts`. The synchronization merge also retained the current upstream package manifest/lockfile changes, including `parse5` and the BACKGROUND-003 dependencies, while removing the unauthorized `ipaddr.js` dependency.
### Work Completed
Replaced the permissive `ipaddr.js` range predicate with a deterministic Node `node:net` `isIP`/`BlockList` policy. IPv4 candidates are checked against explicit non-public/special-use CIDRs; IPv6 is limited to `2000::/3` with explicit special-use exclusions; IPv4-mapped IPv6 continues through the mapped IPv4 policy. Added regression coverage for all six A1-R1 addresses (`192.31.196.1`, `192.52.193.1`, `192.175.48.1`, `4000::1`, `6000::1`, `fe00::1`) and for a mixed public/special-use DNS answer rejected before the request callback. Existing positive global IPv4 and IPv6 cases remain passing. DNS ordering, pinned HTTPS connections, TLS hostname verification, peer checking, redirect handling, bounded decompression, extraction, and the BACKGROUND-001 contract were otherwise unchanged.
### Validation Results
Focused network-policy, HTML-extraction, and acquirer suites: 71/71 passed. `npm run build`: passed. Changed-file diagnostics: clean. `git diff --check`: passed. The initial build attempt lacked upstream-merged BACKGROUND-003 dependencies in this worktree's `node_modules`; installing from the synchronized lockfile with lifecycle scripts disabled resolved the environment issue, and the required build then passed. The optional full-unit failures from Attempt 1 were outside this task's authorized files and were not correction items; the full suite was not rerun for Attempt 2. Standalone ESLint is not a task gate and no repository ESLint configuration was found in Attempt 1.
### Deviations
Used Node's built-in `BlockList` and explicit CIDR policy, as required by A1-R1/A1-R2; no new runtime dependency or registry lookup was introduced.
### Assumptions
The adapter remains a separately injected BACKGROUND-001 contract implementation; worker orchestration is owned by a downstream task. Conservative blocking of explicitly listed special-use ranges is preferable to admitting an address whose global reachability is ambiguous.
### Unresolved Issues
None for the authorized BACKGROUND-002 scope. The optional unrelated repository-wide unit failures reported in Attempt 1 remain outside this task and were not changed.
### Architectural Concerns
None identified. No out-of-scope worker, database, normalization, chunking, embedding, or persistence behavior was introduced.

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-023-BACKGROUND-002`
  parent branch: `task/ARCH-023-BACKGROUND-002`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-023-BACKGROUND-002`
  implementation branch: `task/ARCH-023-BACKGROUND-002`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no
  database submodule: ready at `2eb17ee910491e8f9df82736fc0a843844415947`
  launcher claim: Attempt 2, dependency gate passed, claim committed and pushed as `77cb0eb5f02aae08918843e0d652dbde474daf04`

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Commit identities:
  implementation commit: `3a9b355af29a1535fac865fa4063f267efcc30b9` (pushed to `origin/task/ARCH-023-BACKGROUND-002`)
  completion-report commit: this parent task-report update; its commit identity is included in the task handoff.

## Architect Review

### Review Status
Changes Requested — Attempt 1

### Review Notes
The acquisition adapter is otherwise well bounded and the HTTPS redirect/DNS pinning, connected-peer verification, deadline/body limits, status classification and deterministic HTML/plain-text extraction are materially aligned with D16. Attempt 1 is not accepted because the public-address classifier does not yet enforce R3 exactly and the Completion Report is missing mandatory start-of-attempt provenance.

#### A1-R1 — enforce the complete R3 public-address boundary

`isPublicIpAddress()` currently treats `ipaddr.js@1.9.1` `range() === "unicast"` as an allow decision after a partial hand-maintained deny list. That is not equivalent to `globally routable unicast only` / `reject ... special-use`. At minimum, the current implementation returns public for special/reserved destinations that R3 requires denied, including:

```text
192.31.196.1    (192.31.196.0/24 special-use)
192.52.193.1    (192.52.193.0/24 special-use)
192.175.48.1    (192.175.48.0/24 special-use)
4000::1         (outside the IPv6 global-unicast 2000::/3 allocation)
6000::1         (reserved IPv6 space)
fe00::1         (reserved IPv6 space)
```

Attempt 2 must replace the permissive `range() === "unicast"` allow predicate with a deterministic policy that proves an address is permitted only when it is globally routable unicast under R3. Use a tested parser/classifier from the authorised Node built-ins rather than regular-expression range detection. Preserve the existing IPv4-mapped-IPv6 recursion rule.

Add focused regression cases proving each representative denied address above is rejected and proving a hostname with one ordinary public answer plus one newly covered denied/special-use answer is rejected before any request. Retain positive IPv4 and IPv6 globally-routable cases.

#### A1-R2 — restore the authorised dependency boundary

The task scope says to use Node built-ins for the network policy and to add only the HTML parser dependency required by this task. `ipaddr.js` was added by Attempt 1 and is therefore outside the authorised dependency surface. Remove `ipaddr.js` from `package.json` / `package-lock.json` and implement A1-R1 with Node built-ins (for example `node:net` parsing/block-list primitives plus an explicit deterministic policy). `parse5` remains authorised.

Do not widen this task into runtime registry fetching or another service dependency; address classification must remain deterministic and local.

#### A1-R3 — record mandatory worktree/start synchronization evidence

The Completion Report records the canonical root, parent/implementation paths, branches, database submodule and launcher claim, but it does not record the mandatory values required by `docs/agent-worktree-isolation-policy.md`:

```text
Physical worktree isolation:
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current
```

Attempt 2 must run from the canonical task worktrees, rerun the task-required validation after the R3 correction, and record those exact launcher/preparation outcomes plus the final implementation/report commit identities.

The optional full-unit failures reported in Attempt 1 are not correction items for this task: the failing areas are outside the authorised files and the focused 64/64 suite plus build/changed-file diagnostics/diff checks passed. Standalone ESLint is also not invented as a gate because this repository has no `eslint.config.*` and the task does not require a missing script/configuration.

### Reviewed Files
- `package.json`
- `package-lock.json`
- `src/services/merchant-knowledge-network-policy.ts`
- `src/services/merchant-knowledge-html-extraction.ts`
- `src/services/merchant-knowledge-web-page-acquirer.ts`
- `tests/unit/services/merchant-knowledge-network-policy.test.ts`
- `tests/unit/services/merchant-knowledge-html-extraction.test.ts`
- `tests/unit/services/merchant-knowledge-web-page-acquirer.test.ts`
- `docs/decisions/background/ARCH-023/BACKGROUND-002-acquire-merchant-knowledge-web-pages.md`
- `docs/architecture/ARCH-023-merchant-knowledge.md`
- `docs/agent-worktree-isolation-policy.md`

### Validation Reviewed
- Focused network-policy / HTML-extraction / acquirer suites: submitted `64/64` passed.
- `npm run build`: submitted pass.
- Changed-file diagnostics: submitted clean.
- `git diff --check`: submitted pass.
- Optional full unit run: submitted `1,190` passing with five unrelated failures and one unrelated missing-fixture suite setup failure; not treated as a BACKGROUND-002 regression.
- Architect inspection independently demonstrated that the current allow predicate admits R3-denied special/reserved address classes; this is an acceptance blocker regardless of focused-suite success.

### Architecture Conformance
Changes required. D16/R3 is a security boundary: every initial and redirect destination must be globally routable public unicast before connection. The current DNS pinning/peer verification structure can remain, but the address-classification predicate and its dependency surface must be corrected. No worker orchestration, persistence, normalization, chunking, embedding, upload or Gateway work is authorised in Attempt 2.

### Follow-up
Return the same task through its normal execution path for Attempt 2. BACKGROUND-004 remains Pending. BACKGROUND-003 remains independently Ready and may proceed.
