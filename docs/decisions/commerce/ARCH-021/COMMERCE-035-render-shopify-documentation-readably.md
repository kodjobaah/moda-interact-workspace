---
id: ARCH-021-COMMERCE-035
architecture_id: ARCH-021
title: Normalize and render Shopify documentation readably
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 35
executor: null
claimed_at: null
attempt: 3
depends_on:
  - ARCH-021-COMMERCE-034
enables:
  - ARCH-021-SYSTEM-TEST-001
created: 2026-09-24
updated: 2026-09-25
---

# Normalize and render Shopify documentation readably

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Replace raw Shopify documentation blobs with one safe, bounded, structured documentation contract so search results show readable plain-text excerpts and opened documents preserve meaningful headings, paragraphs, lists and code blocks without rendering raw HTML.

## Context

Manual validation of the Explore Documentation tab exposed two production defects.

Search uses pinned Shopify Dev MCP:

```text
learn_shopify_api
search_docs_chunks
```

and `lib/discovery/upstream.ts` currently maps the returned `content` directly to:

```text
UpstreamSearchItem.text
```

up to 2,000 characters.

`components/studio-workspace.tsx` then renders that value directly inside:

```tsx
<p>{item.text}</p>
```

Shopify search chunks can contain markdown links, code, JSON and HTML-like fragments. As a result the result list exposes syntax such as:

```text
[label](https://...)
{ "query": ... }
<...>
```

instead of a readable excerpt.

Opening a result is a separate path. `fetchShopifyDocument()` safely fetches the canonical `https://shopify.dev/docs/...` HTML and verifies a `main` or `article` container. However `lib/discovery/document.ts` reduces that container to one string with:

```text
readableText(...)
replace(/\s+/g, " ")
```

and the UI renders the complete value as one paragraph:

```tsx
<p>{document.text}</p>
```

This destroys headings, paragraph boundaries, lists, code/preformatted text and other useful reading structure.

The correction must preserve the existing security boundary: Shopify documentation is untrusted remote content. Do not use raw HTML injection.

## Scope

Primary files:

```text
lib/discovery/upstream.ts
lib/discovery/document.ts
lib/discovery/service.ts
src/studio/contracts.ts
src/commerce/integration/studio/services.ts
src/studio/discovery/shopify-documentation-explorer.tsx  # new required Client Component
src/studio/discovery/shopify-documentation-article.tsx   # new required pure renderer
components/studio-workspace.tsx
app/globals.css
tests/discovery-document.test.ts
tests/discovery.test.ts
tests/studio-services.test.ts
tests/studio-workspace.test.tsx
tests/shopify-documentation-explorer.test.tsx            # new required
tests/shopify-documentation-article.test.tsx             # new required
```

Additional directly affected documentation-only files may be changed when required by the normalized contract.

## Out of Scope

- Storefront schema browsing/query generation.
- COMMERCE-032/033/034 behavior.
- Live documentation editing.
- Rendering arbitrary remote HTML.
- A general-purpose browser/Markdown engine.
- Following arbitrary external links from remote content.
- Database/Shared/Background/Gateway changes.
- Shopify Admin API.
- Provider/model calls.
- A test-only documentation port/service/context/React prop in production code.

## Requirements

### R1 — separate search excerpts from full document content

The public Studio documentation contracts must distinguish:

```text
search result excerpt
full structured document
```

Search result DTO must contain at least:

```text
title
excerpt
sourceUrl
path
```

Do not call the search excerpt `text` if it can be confused with complete document content.

Full document DTO must contain at least:

```text
title
sourceUrl
blocks
relatedFieldPaths
```

Do not expose raw remote HTML to a Client Component.

### R2 — normalize search results to plain readable excerpts

Add one pure server-side normalization function for `search_docs_chunks.content`.

The resulting excerpt must:

1. decode common HTML entities;
2. remove HTML tags rather than displaying them;
3. convert Markdown links:
   ```text
   [label](url)
   ```
   to readable label text;
4. convert Markdown images:
   ```text
   ![alt](url)
   ```
   to alt text or omit them when alt is blank;
5. remove Markdown heading/list/fence markers;
6. preserve useful inline-code text but remove the backtick markup;
7. collapse whitespace;
8. omit zero-width/control characters other than ordinary spaces;
9. contain no executable/rendered HTML;
10. be bounded to at most 600 visible characters and at most 2 KiB UTF-8.

If normalization yields an empty excerpt, return a bounded fallback such as:

```text
No preview available.
```

Do not fetch every result page merely to build search excerpts.

### R3 — structured full-document contract

Normalize the verified Shopify `main`/`article` HTML into a bounded block model.

Support exactly these public block kinds for this checkpoint:

```text
HEADING
PARAGRAPH
LIST
CODE
BLOCKQUOTE
```

Required shape:

```text
HEADING:
  level: 2 | 3 | 4
  text: string

PARAGRAPH:
  text: string

LIST:
  ordered: boolean
  items: string[]

CODE:
  text: string

BLOCKQUOTE:
  text: string
```

Unknown/unsupported readable block containers may degrade to `PARAGRAPH`.

Do not expose tag names or raw HTML in the public block contract.

### R4 — preserve meaningful document structure

The HTML normalizer must preserve:

- heading boundaries;
- paragraph boundaries;
- ordered/unordered list-item boundaries;
- `<pre>` / code-block whitespace and newlines;
- blockquote boundaries.

Inline elements inside paragraphs/headings/list items may be flattened to readable text for this checkpoint.

For example:

```html
<h2>Create a customer</h2>
<p>Use <code>customerCreate</code>.</p>
<ul><li>Create</li><li>Activate</li></ul>
<pre>mutation Example { ... }</pre>
```

must normalize into four distinct blocks, not one concatenated string.

Do not globally run `replace(/\s+/g, " ")` across code/preformatted content.

### R5 — discard non-content/sensitive browser elements

Continue excluding at least:

```text
script
style
nav
footer
iframe
object
embed
form
noscript
template
```

Also exclude interactive/browser-only controls such as:

```text
button
input
select
textarea
svg
canvas
```

Their attributes/event handlers must never reach the public DTO.

### R6 — bounded output

Retain the current bounded-fetch/security behavior:

```text
max input:  1 MiB
max redirects: 2
canonical origin: https://shopify.dev/docs/
```

The structured serialized full-document output must remain bounded to:

```text
64 KiB UTF-8
```

Additionally enforce:

```text
maximum blocks:          256
maximum list items/block: 100
maximum normal text/block: 8 KiB UTF-8
maximum code block:      16 KiB UTF-8
```

Reject documents exceeding the bounds rather than silently truncating the opened document.

Search excerpts may be deliberately truncated because they are previews.

### R7 — mandatory documentation component boundary

The Documentation tab must be extracted from `components/studio-workspace.tsx`.

Create exactly these production UI modules:

```text
src/studio/discovery/shopify-documentation-explorer.tsx
src/studio/discovery/shopify-documentation-article.tsx
```

#### `ShopifyDocumentationExplorer`

This is the Documentation-tab Client Component.

It owns exactly:

```text
search query state
search-result state
opened-document state
documentation loading state
documentation error/status state
Search documentation action
Back to results action
opening a selected result
Open related schema fields action
```

It must invoke the same production named Server Actions directly:

```ts
import {
  searchDocumentation,
  getDocumentation,
} from "../server-actions";
```

or the correct relative path to that exact module.

Do not introduce:

```text
DocumentationPort
DocumentationServices
documentationActions prop
test-only callback registry
test-only React context/provider
NODE_ENV === "test" branch
```

The only production props allowed for this component are ordinary UI composition values genuinely used by production. For this checkpoint use:

```ts
type ShopifyDocumentationExplorerProps = {
  disabled: boolean;
  onOpenRelatedSchema: () => void;
};
```

`onOpenRelatedSchema` is a real production client-to-client callback used to switch the existing Explore tab. It is not a server boundary and is not test-only.

Tests must mock the same named `searchDocumentation` / `getDocumentation` module exports that production imports.

#### `ShopifyDocumentationArticle`

This is a pure structured-document renderer.

It owns exactly:

```text
document title
canonical Open on Shopify link
HEADING block rendering
PARAGRAPH block rendering
LIST block rendering
CODE block rendering
BLOCKQUOTE block rendering
```

Its production contract must be exactly the normalized document DTO (or a single `document` prop of that type):

```ts
type ShopifyDocumentationArticleProps = {
  document: DocumentationDocument;
};
```

It must:

- contain no provider/network/data-fetching code;
- import no Server Action;
- contain no sanitizer for raw HTML;
- receive no raw HTML;
- use no `dangerouslySetInnerHTML`.

#### `StudioWorkspace`

After this task, `components/studio-workspace.tsx` may:

- own the existing `"docs" | "schema"` tab state;
- render `ShopifyDocumentationExplorer` when the Documentation tab is active;
- pass the real `disabled` value;
- pass `onOpenRelatedSchema={() => setTab("schema")}`.

It must no longer own:

```text
DocumentationItem[] state
DocumentationDocument state
documentation query state
documentation search/open functions
documentation result list markup
documentation article block markup
```

Do not move those responsibilities into another generic Studio component.

Search results rendered by `ShopifyDocumentationExplorer` must be readable result cards/list items containing:

```text
title
bounded excerpt
canonical source indication
Open/read action
```

Do not render a 2,000-character raw chunk as the result paragraph.

Opened documents rendered by `ShopifyDocumentationArticle` must use a semantic:

```tsx
<article>
```

with block-specific elements:

```text
HEADING    -> h3/h4/h5 or equivalent bounded hierarchy
PARAGRAPH  -> p
LIST       -> ul/ol + li
CODE       -> pre > code
BLOCKQUOTE -> blockquote
```

Add bounded documentation-reader CSS:

- readable line length (`max-width` around 70–80ch);
- normal paragraph spacing;
- list indentation;
- distinct headings;
- horizontally scrollable code blocks;
- code preserves whitespace;
- long unbroken content wraps safely outside code blocks.

Do not use `dangerouslySetInnerHTML`.

### R8 — canonical source link

Opened documentation may display an `Open on Shopify` link using the already canonicalized `sourceUrl`.

Requirements:

```text
target="_blank"
rel="noopener noreferrer"
```

Do not render links discovered inside remote HTML in this checkpoint.

### R9 — no raw markup regressions

Focused tests must prove search excerpts do not expose raw markup.

At minimum use search content containing all of:

```text
<h2>Heading</h2>
[Product](https://shopify.dev/docs/api/storefront/current/objects/Product)
`product`
```graphql
query X { shop { name } }
```
```

and prove the rendered search result:

- contains readable words;
- does not show `<h2>`;
- does not show `](https://`;
- does not show triple backticks.

### R10 — full-document structure regression

Use a verified HTML document containing:

```text
title
h2
two paragraphs
unordered list
ordered list
blockquote
pre/code with multiple lines
script/style noise
```

Prove the normalized block sequence and the React rendering preserve those distinct structures.

Also prove no script/style content appears.

### R11 — contract and composition parity

Tests must exercise the same normalization functions, DTOs, components and named Server Action boundary that production uses.

Do not create a richer documentation fixture shape that production never returns.

The in-memory Studio fixture must be updated to use the exact final public documentation DTO.

Component tests must:

- render the real `ShopifyDocumentationExplorer`;
- mock `searchDocumentation` and `getDocumentation` from the same named Server Action module imported by production;
- render the real `ShopifyDocumentationArticle`;
- never pass a test-only service/port/action bundle prop into either production component.

`StudioWorkspace` tests must prove that the Documentation tab composes `ShopifyDocumentationExplorer` rather than maintaining a second inline documentation implementation.

### R12 — do not broaden upstream trust

Keep the current upstream split:

```text
search:
  pinned Shopify Dev MCP search_docs_chunks

open:
  verified direct fetch from canonical shopify.dev/docs URL
```

Do not render MCP-provided full HTML as trusted content.

Do not replace the verified direct-document fetch with arbitrary URLs returned by search.

## Work Items

- [x] Add plain-text search-excerpt normalizer.
- [x] Replace `DocumentationItem.text` with bounded `excerpt`.
- [x] Add structured documentation block contract.
- [x] Refactor verified HTML extraction to preserve block structure.
- [x] Preserve code/pre whitespace.
- [x] Enforce structured-document bounds.
- [x] Update Studio service adapter/contracts.
- [x] Create `ShopifyDocumentationExplorer` with the exact production responsibilities/props in R7.
- [x] Create pure `ShopifyDocumentationArticle` with the exact production responsibilities/props in R7.
- [x] Remove documentation query/result/document/search/open/rendering state from `StudioWorkspace`.
- [x] Render search results as bounded readable cards/items in `ShopifyDocumentationExplorer`.
- [x] Render opened document as semantic structured article through `ShopifyDocumentationArticle`.
- [x] Add canonical `Open on Shopify` action in `ShopifyDocumentationArticle`.
- [x] Add readable documentation CSS.
- [x] Update in-memory fixtures to exact production DTO shape.
- [x] Mock the production named documentation Server Actions in component tests.
- [x] Add raw-markup, structured-rendering and component-boundary regressions.

## Interfaces / Contracts

Changes only Commerce-local Studio documentation contracts.

Search:

```text
DocumentationItem:
  title
  excerpt
  sourceUrl
  path
```

Full document:

```text
DocumentationDocument:
  title
  sourceUrl
  blocks
  relatedFieldPaths
```

No cross-service contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-034

## Enables

- ARCH-021-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Search results no longer display raw HTML/Markdown syntax.
- [x] Search results show bounded readable excerpts.
- [x] Opened documentation is not rendered as one giant paragraph.
- [x] Headings, paragraphs, lists, code and blockquotes retain separate structure.
- [x] Code/preformatted text retains meaningful newlines/whitespace.
- [x] No raw HTML reaches `dangerouslySetInnerHTML`.
- [x] Non-content/script/style elements are absent from output.
- [x] Canonical source URL remains constrained to `shopify.dev/docs`.
- [x] Existing input/output/redirect bounds remain enforced.
- [x] Tests and fixtures consume the same final documentation DTO as production.
- [x] `StudioWorkspace` no longer owns documentation search/result/open-document state or document rendering markup.
- [x] `ShopifyDocumentationExplorer` uses the production named Server Action imports directly.
- [x] `ShopifyDocumentationArticle` is a pure renderer with no Server Action/provider/network dependency.
- [x] No production documentation port/service/action-bundle prop or test-only React context/provider is introduced.

## Validation

- [x] `npx vitest run tests/discovery-document.test.ts tests/discovery.test.ts tests/studio-services.test.ts tests/studio-workspace.test.tsx tests/shopify-documentation-explorer.test.tsx tests/shopify-documentation-article.test.tsx --reporter=verbose`
- [x] targeted ESLint for every Attempt 3 changed source/test file
- [x] `npm run typecheck` (unchanged unrelated baseline may be recorded; zero task-owned diagnostics required)
- [x] raw-rendering source audit:
  ```text
  rg -n "dangerouslySetInnerHTML|<p>\{document\.text\}</p>|item\.text" \
    components src/studio lib/discovery
  ```
  expected: no documentation-rendering matches; unrelated transport/preview `item.text` matches may be recorded explicitly.
- [x] `StudioWorkspace` ownership audit:
  ```text
  rg -n \
    "DocumentationItem|DocumentationDocument|searchDocumentation|getDocumentation|setItems|setDocument|async function search\(|async function open\(" \
    components/studio-workspace.tsx
  ```
  expected: no documentation implementation matches
- [x] production test-only seam audit:
  ```text
  rg -n \
    "DocumentationPort|DocumentationServices|documentationActions|NODE_ENV.*test|fixture.*Documentation|documentation.*fixture.*prop" \
    components src/studio
  ```
  expected: no production documentation test-injection matches
- [x] component existence audit:
  ```text
  test -f src/studio/discovery/shopify-documentation-explorer.tsx
  test -f src/studio/discovery/shopify-documentation-article.tsx
  ```
  expected: both pass
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return to `moda_architect` and STOP.

Do not start SYSTEM-TEST-001.

## Implementation Notes

Do not solve readability by increasing container width alone. The data contract currently destroys/forwards the wrong structure and must be corrected first.

Do not add a heavyweight generic HTML/Markdown rendering system unless the bounded requirements above genuinely cannot be met with the existing verified parser. This task needs a small safe documentation renderer, not a CMS.

Do not render remote HTML with `dangerouslySetInnerHTML`.

The full-document parser may flatten inline formatting for this checkpoint. Preserving block structure is the required outcome.


Do not leave a compatibility copy of the old Documentation-tab implementation in `StudioWorkspace`.

Do not create `TestShopifyDocumentationExplorer`, a test-only production context, or an injectable documentation service prop. Tests mock the same named Server Actions production imports.

Keep `ShopifyDocumentationArticle` deliberately dumb: it renders the normalized DTO and nothing else.

## Completion Report

### Status

Ready for Review

### Files Changed

Attempt 1 files remain as previously recorded. Attempt 2 changed:

- `lib/discovery/upstream.ts`
- `lib/discovery/document.ts`
- `tests/discovery-document.test.ts`

Attempt 3 changed:

- `tests/discovery-document.test.ts`

### Work Completed

Attempt 1 delivered the structured documentation contract, verified HTML block normalization and bounds, the extracted documentation components, semantic rendering, readable CSS, production fixture parity and component-boundary regressions.

Attempt 2 correction checklist, all implemented:

- Finding 1: `normalizeSearchExcerpt` decodes HTML entities before removing tags; regression added.
- Finding 2: excerpt truncation iterates Unicode code points and stops before the 600-code-point or 2 KiB UTF-8 bound; boundary regression added.
- Finding 3: `readableText` maps `<br>` to a space in normal text and a newline in preformatted text; paragraph/code regressions added.

Attempt 3 correction checklist, all implemented:

- Added `normalizeSearchExcerpt('')` fallback coverage.
- Added whitespace/control/stripped-markup normalized-empty fallback coverage.
- Reconciled the Work Items, Acceptance Criteria and Validation checklists with the submitted evidence.

Architect Review was preserved unchanged.

### Validation Results

- Focused Vitest command: PASS, 6 files and 71 tests.
- Targeted ESLint for `tests/discovery-document.test.ts`: PASS, 0 errors.
- `npm run typecheck`: exits 1 on unchanged unrelated baseline diagnostics; `C035_OWNED_DIAGNOSTICS=none` for `lib/discovery`, `components/studio-workspace`, documentation components and focused documentation tests.
- Raw rendering audit: PASS for documentation rendering. The only matches are allowed unrelated `item.text` uses in MCP transport (`lib/discovery/upstream.ts`) and preview UI (`src/studio/preview/preview-screen.tsx`).
- StudioWorkspace ownership audit: PASS with no matches.
- Production test-seam audit: PASS with no matches.
- Component existence audit: PASS for both required modules.
- `git diff --check`: PASS.

### Branch and Topology Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-035`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-035`.
- Mirrored branch: `task/ARCH-021-COMMERCE-035`.
- Launcher claim commit: parent `d461868dbbf4dc447bb9d090827c20dd50e63f0a`.
- Dependency `ARCH-021-COMMERCE-034`: complete.
- Database submodule: `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
- Implementation commit: `a03b618`, pushed to `origin/task/ARCH-021-COMMERCE-035`.
- No downstream task was started.

### Deviations

- Typecheck remains blocked by the documented unchanged Prisma/generated and unrelated Commerce integration/test diagnostics. No C035-owned diagnostic was reported.

### Assumptions

- The verified direct Shopify HTML fetch remains the only opened-document source, and the pinned MCP path remains search-only.

### Unresolved Issues

- None within the bounded Commerce-035 scope.

### Architectural Concerns

- None identified within the bounded Commerce-035 scope.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 2 correctly resolves all three production-code findings from Attempt 1.

Architect review confirms:

1. `normalizeSearchExcerpt()` now decodes HTML entities before removing decoded
   tags, so entity-encoded markup such as:

   ```text
   &lt;h2&gt;Heading&lt;/h2&gt;
   ```

   is reduced to readable plain text rather than resurfacing as `<h2>...</h2>`.

2. Search excerpt byte bounding now iterates Unicode code points and stops before
   the 2 KiB UTF-8 limit, so the previous UTF-16 code-unit truncation defect is
   removed.

3. `readableText()` now gives `<br>` explicit semantics:

   ```text
   normal text -> space
   preformatted text -> newline
   ```

   so paragraph words are not joined and code/preformatted line breaks remain
   readable.

4. The existing component/data architecture remains intact:

   ```text
   StudioWorkspace
     -> ShopifyDocumentationExplorer
         -> named searchDocumentation/getDocumentation
         -> ShopifyDocumentationArticle
   ```

   No raw-HTML renderer, documentation port/service bundle or test-only React
   context has been introduced.

The submitted focused packet reports 6 files / 70 tests passing, targeted ESLint,
all source/component audits and `git diff --check` passing, with zero C035-owned
typecheck diagnostics.

There is one remaining deterministic evidence/task-record blocker.

#### Finding — the explicitly required empty-excerpt regression is still absent

The Attempt 1 Architect Review required the Attempt 2 regression packet to prove
all of the following, including:

```text
3. empty normalized input returns `No preview available.`
```

The final `tests/discovery-document.test.ts` contains the new regressions for:

```text
entity-encoded tags
Unicode byte-bound truncation
paragraph/code <br> behavior
```

but contains no invocation such as:

```ts
normalizeSearchExcerpt('')
```

or another input that normalizes to empty, and no assertion for:

```text
No preview available.
```

The production source does currently contain:

```ts
if (!normalized) return 'No preview available.';
```

so this is an evidence gap rather than a newly discovered production design
problem.

The task record also returned with:

```text
Acceptance Criteria:
  Search results no longer display raw HTML/Markdown syntax   [ ]
  Search results show bounded readable excerpts               [ ]

Validation:
  every item                                                  [ ]
```

despite the Completion Report claiming those validations passed.

The task protocol requires Work Items, Acceptance Criteria and Validation to
remain a durable representation of what has actually been proved.

### Attempt 3 deterministic correction

Reclaim the same task as Attempt 3.

No production-code change is authorized unless the missing regression exposes an
actual defect.

#### 1. Add the missing fallback regression

In:

```text
tests/discovery-document.test.ts
```

add a focused test that proves both an actually empty input and markup/control
content that normalizes to empty return exactly:

```text
No preview available.
```

At minimum:

```ts
expect(normalizeSearchExcerpt('')).toBe('No preview available.');
```

Also include one normalized-empty case such as whitespace / stripped markup so
the fallback is proved after normalization rather than only before it.

Do not change the fallback wording.

#### 2. Preserve all Attempt 2 regressions

Retain and keep passing:

```text
raw HTML + Markdown link/fence -> readable plain text
entity-encoded tags -> decoded then removed
Unicode excerpt <= 600 code points / <= 2 KiB / no dangling surrogate
<p>First<br>Second</p> -> "First Second"
<pre>line one<br>line two</pre> -> newline-preserving CODE
structured headings/paragraphs/lists/blockquote/code
script/style/browser-noise exclusion
64 KiB full-document rejection
```

#### 3. Re-run the exact Validation packet

Run:

```bash
npx vitest run \
  tests/discovery-document.test.ts \
  tests/discovery.test.ts \
  tests/studio-services.test.ts \
  tests/studio-workspace.test.tsx \
  tests/shopify-documentation-explorer.test.tsx \
  tests/shopify-documentation-article.test.tsx \
  --reporter=verbose
```

Run targeted ESLint for every Attempt 3 changed file.

Run:

```bash
npm run typecheck
```

The documented unchanged unrelated baseline remains permitted only when there are
zero C035-owned diagnostics.

Run every source/component audit already defined in the task and:

```bash
git diff --check
```

#### 4. Reconcile the task record

After the regression and validation pass:

- mark the regression Work Item `[x]`;
- mark the first two remaining Acceptance Criteria `[x]`;
- mark every Validation item `[x]` when its required evidence is satisfied;
- under the allowed typecheck rule, mark typecheck `[x]` when only the documented
  unchanged unrelated baseline remains and zero C035-owned diagnostics exist.

Update the Completion Report to distinguish:

```text
Attempt 1:
  structured documentation contract/component extraction

Attempt 2:
  encoded-tag order
  Unicode-safe bound
  <br> preservation

Attempt 3:
  missing fallback regression
  final checklist/evidence reconciliation
```

Record:

```text
Attempt 3 implementation/test commit
final parent report commit
focused test file/test count
ESLint
typecheck baseline + zero task-owned diagnostics
all source/component audits
git diff --check
clean/upstream branch state
database submodule synchronization
```

Return:

```yaml
status: review
executor: null
claimed_at: null
attempt: 3
```

and STOP.

Do not start `ARCH-021-SYSTEM-TEST-001`.

### Reviewed Files

- `lib/discovery/upstream.ts`
- `lib/discovery/document.ts`
- `tests/discovery-document.test.ts`
- `src/studio/discovery/shopify-documentation-explorer.tsx`
- `src/studio/discovery/shopify-documentation-article.tsx`
- `components/studio-workspace.tsx`
- task Completion Report

### Validation Reviewed

Submitted Attempt 2 evidence:

```text
focused tests: 6 files / 70 passed
targeted ESLint: PASS
raw-rendering audit: PASS with documented unrelated `item.text` matches
StudioWorkspace ownership audit: PASS
production documentation seam audit: PASS
component existence audit: PASS
git diff --check: PASS
typecheck: unchanged unrelated baseline only
           zero C035-owned diagnostics
```

Architect static review confirms the three Attempt 1 production defects are fixed.

Acceptance is blocked only on the explicitly required missing fallback regression
and final task-checklist reconciliation.

### Architecture Conformance

Production implementation conforms.

The remaining correction is deterministic regression/task evidence only.

### Follow-up

Reclaim the same task as Attempt 3.

`ARCH-021-SYSTEM-TEST-001` remains Pending until C035 is architect-accepted
Complete.
