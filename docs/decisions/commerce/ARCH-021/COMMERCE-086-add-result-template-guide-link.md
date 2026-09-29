---
id: ARCH-021-COMMERCE-086
architecture_id: ARCH-021
title: Package and link the Result Template user guide
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 86
executor: copilot
claimed_at: 2026-09-29T19:51:24Z
attempt: 2
depends_on:
  - ARCH-021-COMMERCE-084
  - ARCH-021-COMMERCE-085
  - ARCH-021-COMMERCE-093
  - ARCH-021-COMMERCE-094
enables: []
created: 2026-09-28
updated: 2026-09-29
---

# Package and link the Result Template user guide

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Ship the approved non-developer Result Template guide as a deterministic Commerce application build asset and add one contextual link from Result Template authoring to the packaged manual, without changing Result Template grammar, validation, generation, rendering, authoring-state or persistence behaviour.

## Context

COMMERCE-084 owns the accepted Result Template grammar, validator, generator and renderer. COMMERCE-085 owns the Result Template authoring editor and available-result-data experience.

The manual is application-owned user documentation. It must not rely on an architect handoff path, a repository checkout accident, GitHub, an external documentation service or a manual deployment copy step.

The canonical source file supplied by `moda_architect` is:

```text
moda-interact-commerce/manuals/result-template-guide.html
```

The Commerce build must deterministically package that source to the static application destination:

```text
moda-interact-commerce/public/manuals/result-template-guide.html
```

The deployed application URL remains exactly:

```text
/manuals/result-template-guide.html
```

The generated `public/manuals/` directory is build output. The canonical manual is the source file under `manuals/`.

## Scope

Implementation repository:

```text
moda-interact-commerce/
```

Canonical manual source:

```text
manuals/result-template-guide.html
```

Generated application asset:

```text
public/manuals/result-template-guide.html
```

Required build implementation areas:

```text
scripts/package-manuals.mjs
scripts/manuals-packaged-smoke.mjs
package.json
.gitignore
```

Primary UI integration area after COMMERCE-085:

```text
src/studio/tools/authoring/result-template-tab.tsx
```

or the exact Result Template editor/header component introduced by COMMERCE-085.

Focused tests must cover both packaging and UI integration. Prefer:

```text
tests/manual-packaging.test.ts
tests/result-template-tab.test.tsx
```

If COMMERCE-085 renames the Result Template test file, extend its accepted replacement instead of creating a duplicate UI suite.

## Out of Scope

- Changing the accepted Result Template grammar.
- Changing parser, validator, generator or renderer behaviour.
- Changing CodeMirror/editor semantics.
- Changing generated Result Template content.
- Changing validation freshness or dirty-state semantics.
- Changing Test execution or Save/Review gating.
- Adding an external documentation service or CMS.
- Adding a database model for documentation.
- Fetching the guide from an external network source during build or runtime.
- Adding analytics/tracking for guide usage.
- Adding a generic documentation packaging framework beyond the explicit manual manifest required by this task.
- Changing Render/Gateway topology; the existing Commerce build command remains the deployment entry point.

## Requirements

### R1 — one canonical source file

The canonical source of the manual is exactly:

```text
manuals/result-template-guide.html
```

The task MUST NOT maintain a second committed copy under `public/`.

The source must retain:

```text
<title>Result Template Guide | Moda Commerce Studio</title>
```

and visible H1:

```text
Result Template Guide
```

The source must remain self-contained:

```text
HTML + CSS only
no JavaScript
no external fonts
no remote images
no remote stylesheets
no iframe
no external script/resource request
```

### R2 — generated `public/manuals` is build output

`public/manuals/` is generated only by the Commerce manual-packaging command.

Add exactly this ignore rule to `moda-interact-commerce/.gitignore`:

```gitignore
/public/manuals/
```

After this task, no file under `public/manuals/` may be a committed source-of-truth document.

The build may delete and recreate `public/manuals/` because it contains generated manual assets only.

### R3 — deterministic explicit manual manifest

Create:

```text
scripts/package-manuals.mjs
```

The script owns one explicit in-source manifest. For this task it contains exactly one entry equivalent to:

```js
const MANUALS = [
  {
    source: "manuals/result-template-guide.html",
    destination: "public/manuals/result-template-guide.html",
  },
];
```

Mechanical representation may differ, but the source and destination paths MUST NOT differ.

The script MUST NOT:

```text
accept arbitrary source/destination paths from CLI arguments;
scan the repository for HTML files;
copy the entire manuals directory implicitly;
fetch network content;
read files outside the Commerce repository;
preserve stale files from an earlier package run.
```

### R4 — exact packaging algorithm

`package-manuals.mjs` MUST execute these steps in this order:

```text
1. Resolve the Commerce repository root from the script location, not from an assumed caller cwd.
2. Validate every manifest source resolves inside <repo>/manuals/.
3. Validate every manifest destination resolves inside <repo>/public/manuals/.
4. Fail non-zero before copying if:
     - a source is missing;
     - a source is not a regular file;
     - two entries use the same destination;
     - a resolved source/destination escapes its allowed root.
5. Remove <repo>/public/manuals recursively if it exists.
6. Recreate <repo>/public/manuals.
7. Copy each manifest source byte-for-byte to its destination.
8. Print one stable line per packaged manual:
     packaged manual: manuals/result-template-guide.html -> public/manuals/result-template-guide.html
9. Exit zero only after every manifest entry has been copied successfully.
```

Do not transform, minify or rewrite the HTML during packaging.

### R5 — packaged-manual smoke command

Create:

```text
scripts/manuals-packaged-smoke.mjs
```

It MUST resolve paths from its own script location and verify exactly:

```text
manuals/result-template-guide.html exists and is a regular file;
public/manuals/result-template-guide.html exists and is a regular file;
source bytes === packaged bytes;
packaged file contains the exact expected <title>;
packaged file contains the visible "Result Template Guide" heading;
```

Any failed condition exits non-zero with a bounded diagnostic naming the failed condition/path.

The smoke script MUST NOT create or repair the generated asset. It is validation only.

### R6 — exact package.json build integration

Add exactly these npm script names:

```json
"manuals:package": "node scripts/package-manuals.mjs",
"manuals:smoke": "node scripts/manuals-packaged-smoke.mjs"
```

Change `predev` from its current behaviour to semantically execute, in this order:

```text
npm run manuals:package
npm run manuals:smoke
npm run code-runtime:package
```

The resulting `predev` value must therefore be equivalent to:

```json
"predev": "npm run manuals:package && npm run manuals:smoke && npm run code-runtime:package"
```

Change `build` so its exact logical order is:

```text
1. npm run manuals:package
2. npm run manuals:smoke
3. npm run code-runtime:package
4. npm run code-runtime:smoke
5. npm run prisma:generate
6. next build --webpack
```

The resulting build value must therefore be equivalent to:

```json
"build": "npm run manuals:package && npm run manuals:smoke && npm run code-runtime:package && npm run code-runtime:smoke && npm run prisma:generate && next build --webpack"
```

Do not introduce `prebuild` or `postbuild` hooks for this task. Keep the complete production build order visible in the existing `build` command.

No dependency or package-lock change is required for the packaging scripts; use Node built-ins only.

### R7 — stale generated files cannot survive a build

The packaging behaviour MUST prove that an unmanifested stale file is removed.

Required regression:

```text
create public/manuals/stale-guide.html
run manuals:package
assert public/manuals/stale-guide.html no longer exists
assert public/manuals/result-template-guide.html exists
```

Do not implement stale cleanup by maintaining a second stale-file allow/deny list. Recreating the generated directory is the canonical cleanup mechanism.

### R8 — packaging fails closed when the source is unavailable

A missing canonical source manual is a build failure.

Required regression must demonstrate that the packaging operation fails non-zero and does not silently continue with an old generated copy.

The test may exercise the packaging implementation through an exported/internal helper or an isolated temporary repository fixture. Do not rename/delete the real source manual concurrently with other tests merely to provoke failure.

### R9 — manual content must match architect-accepted C084 grammar

Before implementation is marked Ready for Review, compare every grammar example in the canonical manual with architect-accepted COMMERCE-084.

The guide may document only constructs C084 actually accepts.

The expected user-facing features currently include:

```text
value interpolation
for / else / endfor
if / elif / else / endif
comparisons: == != < <= > >=
boolean expressions: and or not
parentheses for grouping
numeric arithmetic: + - * / %
primitive literals where accepted
nested supported loops
```

If accepted C084 differs, do NOT alter C084 from this task and do NOT publish misleading help. Mark C086 Blocked and record the exact mismatch.

### R10 — one contextual Result Template guide link

Add exactly one persistent help link to the visible Result Template authoring surface.

Rendered link text:

```text
Open Result Template guide
```

Target:

```text
/manuals/result-template-guide.html
```

Semantics:

```tsx
<a
  href="/manuals/result-template-guide.html"
  target="_blank"
  rel="noopener noreferrer"
>
  Open Result Template guide
</a>
```

Do not use `window.open`, router navigation, a click Server Action or a button pretending to be a link.

Place it in the Result Template header/introductory area before the main editor controls. The link remains visible for `UNVALIDATED`, `VALIDATING`, `VALID`, `INVALID` and `STALE` states.

Opening/rendering the link MUST NOT mutate authoring state, validation revisions, dirty state, Test state or persistence state.

### R11 — production route is proven from the built application

After the normal production build succeeds, start the application with the repository's declared production start command:

```text
npm run start
```

against the built output on an available local test port/environment, then request:

```text
GET /manuals/result-template-guide.html
```

Prove:

```text
HTTP status = 200
Content-Type contains text/html
response contains <title>Result Template Guide | Moda Commerce Studio</title>
```

Use a bounded smoke process that terminates the spawned server after the assertion. Do not leave a background `next start` process running after validation.

If the normal production start requires environment values unrelated to static serving, use the repository's established test/build environment mechanism; do not weaken application authentication/configuration globally just to serve the manual.

### R12 — no manual deployment copy step

The task Completion Report must demonstrate this lifecycle:

```text
clean generated public/manuals directory
        -> npm run build
        -> generated manual exists
        -> production next start
        -> /manuals/result-template-guide.html returns 200
```

There must be no required action between `npm run build` and normal application startup that copies the manual.

Deleting an external architect/download handoff copy must have no effect on the built application because `manuals/result-template-guide.html` inside the Commerce repository is canonical.

## Work Items

- [x] Confirm COMMERCE-084 is Complete/Accepted and record the accepted grammar used by the guide.
- [x] Confirm COMMERCE-085 is Complete/Accepted and locate the final Result Template editor/header component.
- [x] Compare every manual example with the accepted C084 grammar; block on mismatch rather than publishing incorrect help.
- [x] Treat `manuals/result-template-guide.html` as the canonical source; do not keep a committed `public/manuals` copy.
- [x] Add `/public/manuals/` to `.gitignore`.
- [x] Implement the explicit one-entry `scripts/package-manuals.mjs` manifest and exact deterministic packaging algorithm.
- [x] Implement `scripts/manuals-packaged-smoke.mjs` as validation-only byte/title/heading verification.
- [x] Add `manuals:package` and `manuals:smoke` npm scripts using Node built-ins only.
- [x] Integrate manual packaging/smoke into `predev` in the required order.
- [x] Integrate manual packaging/smoke into `build` in the required order before existing code-runtime packaging, Prisma generation and `next build`.
- [x] Add regression proving stale generated manual files are removed.
- [x] Add regression proving a missing canonical source fails packaging rather than serving an old generated file.
- [x] Add exactly one `Open Result Template guide` link to the Result Template header/introductory area.
- [x] Add focused UI assertions for link text/href/target/rel and zero authoring-state mutation.
- [x] Run a clean manual-package smoke.
- [ ] Run the normal production build from a state with no `public/manuals` directory.
- [ ] Start the built application and prove the exact manual URL returns the packaged HTML with HTTP 200.
- [ ] Complete the Completion Report and STOP after the production gate is resolved.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-084
  accepted Result Template grammar

ARCH-021-COMMERCE-085
  accepted Result Template editor/header surface
```

Application-owned manual source contract:

```text
Source: manuals/result-template-guide.html
```

Build packaging contract:

```text
Command:     npm run manuals:package
Validation:  npm run manuals:smoke
Generated:   public/manuals/result-template-guide.html
```

Static application URL contract:

```text
URL:   /manuals/result-template-guide.html
Title: Result Template Guide | Moda Commerce Studio
H1:    Result Template Guide
```

No database or cross-repository runtime contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-084
- ARCH-021-COMMERCE-085
- ARCH-021-COMMERCE-093
- ARCH-021-COMMERCE-094

## Enables

None.

## Acceptance Criteria

- [x] `manuals/result-template-guide.html` is the only committed canonical manual copy.
- [x] `/public/manuals/` is ignored as generated output.
- [x] `scripts/package-manuals.mjs` uses an explicit one-entry manifest and accepts no arbitrary copy paths.
- [x] Packaging resolves repository paths independently of the caller's current working directory.
- [x] Packaging removes stale `public/manuals` content before copying manifest entries.
- [x] Missing/invalid source, duplicate destination or path escape causes a non-zero packaging failure.
- [x] Packaged manual bytes equal canonical source bytes.
- [x] `manuals:package` and `manuals:smoke` exist with the exact responsibilities defined above.
- [x] `predev` packages/smokes manuals before existing code-runtime packaging.
- [x] `build` packages/smokes manuals before code-runtime packaging/smoke, Prisma generation and `next build --webpack`.
- [ ] The production build succeeds from a clean state where `public/manuals/` does not exist.
- [ ] The built application's normal `npm run start` serves `/manuals/result-template-guide.html` with HTTP 200 and HTML content.
- [ ] The served document contains the exact expected title.
- [ ] No post-build/manual/deployment copy step is needed (production build/start lifecycle not yet proven).
- [x] The manual remains self-contained and written for non-developers.
- [x] Every documented grammar example matches architect-accepted C084.
- [x] Result Template displays exactly one contextual `Open Result Template guide` link.
- [x] Link href is exactly `/manuals/result-template-guide.html`, target is `_blank`, and rel includes `noopener noreferrer`.
- [x] Link availability is independent of validation/Test/dirty state.
- [x] Opening/rendering the guide causes zero Tool/ToolRevision/audit/persistence mutation.
- [x] Existing Result Template editor, validation, generation and Test behaviour are unchanged.

## Validation

- [x] `test -f manuals/result-template-guide.html`
- [x] `grep -F '<title>Result Template Guide | Moda Commerce Studio</title>' manuals/result-template-guide.html`
- [x] verify the canonical source contains no `<script`, remote `<link`, remote `<img`, or `<iframe` resources
- [x] `rm -rf public/manuals && npm run manuals:package && npm run manuals:smoke`
- [x] run focused manual-packaging regressions including stale-file removal and missing-source failure
- [x] run the accepted C085 Result Template UI test with link assertions
- [x] focused UI assertion: accessible link name equals `Open Result Template guide`
- [x] focused UI assertion: href/target/rel equal the required contract
- [x] focused UI assertion: link remains present for stale/invalid template states
- [x] focused UI assertion: rendering/clicking the anchor causes no authoring-state or Server Action mutation
- [x] targeted ESLint for changed JS/React/test files
- [x] changed-file TypeScript diagnostics, or repository typecheck with baseline reconciliation
- [ ] run `npm run build` with `public/manuals/` absent at start and record success
- [ ] run bounded production-start HTTP smoke for `/manuals/result-template-guide.html`
- [x] `git diff --check`

## Stop Condition

After every Work Item, Acceptance Criterion and required Validation item is complete, set the task to `review`, complete the Completion Report and STOP. Do not modify C084/C085 or begin unrelated follow-on work.

## Implementation Notes

The manual source is intentionally separate from generated `public/` output so there is one committed source of truth while the application build explicitly owns distribution.

Do not depend on the developer remembering to copy the manual before deployment. `npm run build` is the packaging boundary.

Do not add a second user-facing copy of the guide in a modal/drawer or point users at GitHub/repository files.

The packaging scripts must use Node built-ins only and must be deterministic/re-runnable.

The current Next.js production start topology serves files from `public/`. This task therefore packages the canonical source into `public/manuals/` before `next build` and proves the normal built application serves it. If implementation discovers that the accepted deployment artifact omits `public/`, stop and return the deployment gap to `moda_architect`; do not silently invent a second serving mechanism inside this task.

## Completion Report

### Status

Attempt 1 is blocked at the production-build gate and remains `in_progress`.
Manual packaging, the authoring link and focused regressions are complete, but
R11/R12 cannot be proven until the separate Commerce route-import task
ARCH-021-COMMERCE-093 is materialized, accepted and completed. Per
`moda_architect`, C086 must not expand scope or move to `review` on this attempt.

### Files Changed

Implementation commit `c26c0ec` on `task/ARCH-021-COMMERCE-086`:

- `.gitignore`
- `package.json`
- `scripts/package-manuals.mjs`
- `scripts/manuals-packaged-smoke.mjs`
- `src/studio/tools/authoring/result-template-tab.tsx`
- `tests/manual-packaging.test.ts`
- `tests/result-template-tab.test.tsx`

The canonical source `manuals/result-template-guide.html` was unchanged; no
generated `public/manuals/` file is committed.

### Work Completed

Confirmed C084 and C085 are complete. The guide examples were checked against
C084's accepted scalar interpolation; bounded and nested `for` loops with
`else`; `if`/`elif`/`else`; comparisons; boolean operators and grouping;
numeric arithmetic; and primitive literals. No grammar mismatch was found.

Added the explicit one-entry Node-built-in packager and read-only smoke script,
integrated both into `predev` and `build`, and ignored generated
`/public/manuals/`. Added packaging regressions for stale cleanup, missing
source, invalid paths/duplicate destinations, non-regular sources and
read-only smoke. Added one persistent Result Template intro link and assertions
for URL/target/rel, invalid/stale visibility and zero authoring-state mutation.

### Validation Results

 - `npm run predev`: passed; manual package/smoke preceded existing code-runtime
   packaging.
 - Clean `npm run manuals:package && npm run manuals:smoke`: passed; generated
   output is ignored by Git.
 - Focused packaging, C085 UI and C084 authoring/generator/renderer/optionality
   regressions: 6 files, 43 tests passed.
 - Targeted ESLint and `git diff --check`: passed.
 - Changed-file TypeScript output has no C086-introduced diagnostics. The only
   remaining diagnostics in the touched UI file are the pre-existing C085
   `CommerceResultSchema.properties`/`required` errors in `ResultTreeNode`; the
   same lines exist at the C086 starting commit.
 - Canonical guide resource scan found no script, iframe, image, external
   stylesheet or remote URL reference.
 - Clean `npm run build` passed manual packaging/smoke, code-runtime
   packaging/smoke and Prisma generation, then failed during Next compilation
   on three imports in the untouched
   `app/api/studio/code-response/validate/route.ts`:
   `../../../../../../lib/preview/http`,
   `../../../../../../lib/preview/runtime`, and
   `../../../../../../src/commerce/preview/types`. The referenced modules
   exist in the Commerce repository; the route's six parent traversals resolve
   outside the repository (one level too far).
 - R11/R12 production build and `npm run start` HTTP smoke remain unverified;
   no HTTP 200/title assertion is claimed.

### Deviations

The production lifecycle cannot pass because of the unrelated route-import
defect. The route was not changed: it is outside C086 scope and
`moda_architect` directed that the correction be a separate task.

### Assumptions

None.

### Unresolved Issues

ARCH-021-COMMERCE-093 is the architect-directed task to correct the three
preview-validation route imports and verify the Commerce production build. Its
definition is not yet materialized, so it is not yet added to C086's
`depends_on` list.

After C093 is accepted and complete, `moda_architect` directed that C086 be
returned through the authorized Changes Requested path: add C093 as a
dependency, clear `executor` and `claimed_at`, preserve `attempt: 1`, and set
C086 to `ready`. The next authorized claim will be Attempt 2. Attempt 1's
evidence and implementation commit must be preserved.

### Architectural Concerns

The existing preview-validation route import-depth defect blocks the normal
Commerce build independently of C086. Correcting it here would cross the
declared task scope; the architect chose a separate Commerce-owned task.

## Architect Review

### Review Status

Blocked

### Review Notes

Attempt 1 is architect-reviewed as **Blocked by an out-of-scope Commerce build defect**, not by a C086 implementation defect.

The C086 implementation evidence is coherent:

- canonical manual source/package/smoke behavior is implemented;
- `predev` packages and verifies the manual before code-runtime packaging;
- the production `build` command includes manual package/smoke before the existing code-runtime/Prisma/Next build stages;
- stale generated manual cleanup and missing-source failure regressions pass;
- the Result Template guide link is present with the required href/target/rel and zero authoring-state mutation;
- focused packaging/UI/C084 compatibility packet passed 43 tests;
- targeted ESLint and `git diff --check` passed;
- changed-file diagnostics contain no C086-introduced TypeScript diagnostics.

The normal clean production build reaches the Next compilation stage and then fails in an **untouched file outside C086 scope**:

```text
app/api/studio/code-response/validate/route.ts
```

That route imports:

```ts
../../../../../../lib/preview/http
../../../../../../lib/preview/runtime
../../../../../../src/commerce/preview/types
```

From:

```text
app/api/studio/code-response/validate/
```

six parent traversals resolve one directory above the Commerce repository. The repository-local `lib/` and `src/` roots are five parent traversals away.

The three referenced modules exist. This is therefore a bounded route-import-depth defect, not a missing implementation capability and not permission to modify the route inside C086.

`ARCH-021-COMMERCE-093` is materialised by this architect review to own that correction and verify the normal Commerce production build.

C086 now explicitly depends on C093.

Do not modify the already-valid C086 manual packaging/link implementation while blocked.

### Reviewed Files

- `docs/decisions/commerce/ARCH-021/COMMERCE-086-add-result-template-guide-link.md`
- `moda-interact-commerce/package.json`
- `moda-interact-commerce/scripts/package-manuals.mjs`
- `moda-interact-commerce/scripts/manuals-packaged-smoke.mjs`
- `moda-interact-commerce/src/studio/tools/authoring/result-template-tab.tsx`
- `moda-interact-commerce/tests/manual-packaging.test.ts`
- `moda-interact-commerce/tests/result-template-tab.test.tsx`
- `moda-interact-commerce/app/api/studio/code-response/validate/route.ts`
- C086 Completion Report — Attempt 1

### Validation Reviewed

Submitted Attempt 1 evidence:

- `npm run predev`: passed;
- clean manual package + smoke: passed;
- focused six-file packet: 43 tests passed;
- targeted ESLint: passed;
- `git diff --check`: passed;
- changed-file TypeScript diagnostics: no C086-introduced diagnostics;
- clean `npm run build`: manual packaging/smoke, code-runtime packaging/smoke and Prisma generation passed; Next compilation then failed on the three over-deep imports in the untouched code-response validation route;
- R11/R12 production `npm run start` HTTP smoke is therefore not yet executable and is correctly left unclaimed.

The route path calculation independently confirms that five, not six, parent traversals are required to reach the Commerce repository root from the route directory.

### Architecture Conformance

C086 implementation conforms within its declared scope.

The route-import defect is now corrected by accepted C093. C086 remains blocked because the production build still cannot complete until the unrelated TypeScript diagnostics/build gate owned by C094 is corrected.

### Follow-up

1. C093 is Complete / Accepted and remains in `depends_on`.
2. Execute and architect-review `ARCH-021-COMMERCE-094`, which owns the unrelated TypeScript diagnostics and repository production-build gate.
3. After C094 is Complete, return this same C086 task to `ready` through the authorized Changes Requested path:
   - preserve `attempt: 1`;
   - preserve all Attempt 1 Completion Report evidence;
   - keep both C093 and C094 in `depends_on`;
   - clear execution claim;
   - make the next claim Attempt 2.
4. C086 Attempt 2 must rerun from a clean generated-manual state:
   - normal `npm run build`;
   - bounded `npm run start` smoke;
   - `GET /manuals/result-template-guide.html`;
   - HTTP 200 / HTML Content-Type / exact title assertion.
5. Do not repeat already-passed focused implementation work unless a relevant intervening change affects it.
