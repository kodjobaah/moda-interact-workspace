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
status: complete
priority: 35
executor: null
claimed_at: null
attempt: 5
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
maximum blocks:          512
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
- [x] Ensure documentation search results have unique canonical `path` identities before React rendering.
- [x] Raise only the semantic document-block ceiling from 256 to 512 while retaining the 64 KiB serialized-output cap.
- [x] Make parser bound failures distinguish block-count/list/text/code causes from the final serialized-output bound.
- [x] Add duplicate-result and large-semantic-document regressions from developer manual validation.
- [x] Remove task-file conflict-marker residue and reconcile the final Validation record.

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
- [x] `DocumentationItem.path` values presented to `ShopifyDocumentationExplorer` are unique within one search result set.
- [x] Duplicate upstream/canonical search hits preserve the first-ranked result and do not render duplicate cards/React keys.
- [x] A semantic document with more than 256 but at most 512 small blocks can be opened when its serialized DTO remains under 64 KiB.
- [x] More than 512 semantic blocks still fail closed with a block-count-specific bounded error.
- [x] The existing 64 KiB serialized full-document output bound remains unchanged and enforced.
- [x] The task file contains no Git conflict markers.

## Validation

- [x] `npx vitest run tests/discovery-document.test.ts tests/discovery.test.ts tests/studio-services.test.ts tests/studio-workspace.test.tsx tests/shopify-documentation-explorer.test.tsx tests/shopify-documentation-article.test.tsx --reporter=verbose`
- [x] targeted ESLint for every Attempt 5 changed source/test file
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
- [x] duplicate-result identity audit:
  ```text
  rg -n "key=\{item\.path\}" src/studio/discovery/shopify-documentation-explorer.tsx
  ```
  expected: this key remains valid only because the production search boundary now guarantees unique `path` values; accompanying regression must prove that invariant.
- [x] conflict-marker audit:
  ```text
  ! rg -n "^(<<<<<<<|=======|>>>>>>>)" \
    docs/decisions/commerce/ARCH-021/COMMERCE-035-render-shopify-documentation-readably.md
  ```
  expected: PASS
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

Attempt 4 changed:

- `lib/discovery/document.ts`
- `lib/discovery/upstream.ts`
- `tests/discovery-document.test.ts`

Attempt 5 changed:

- `lib/discovery/document.ts`
- `src/commerce/integration/studio/services.ts`
- `tests/discovery-document.test.ts`
- `tests/studio-integration.test.ts`

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

Attempt 4 correction checklist, all implemented:

- Finding 1: parser attributes are retained only for server-side classification; hidden, accessibility-only and control nodes are excluded before DTO creation.
- Finding 2: local hash-link anchor helpers and semantic Shopify chrome, including version selectors and feedback controls, are removed without global prose stripping.
- Finding 3: decorative-only blocks and the duplicate top-level page H1 are omitted; consecutive identical short heading/paragraph blocks are collapsed locally.
- Finding 4: search excerpts receive bounded helper/chrome cleanup while retaining the real product sentence.
- Finding 5: representative collection-document and search regressions cover the manual-validation defect and visible anchor-helper form.

Attempt 5 correction checklist, all implemented:

- Finding 1: the Studio search service de-duplicates normalized canonical paths before returning `DocumentationItem[]`, preserving the first-ranked title/excerpt and unique result order; the React `key={item.path}` invariant is now server-enforced.
- Finding 2: the semantic document ceiling is 512 while the 64 KiB serialized service bound remains unchanged; parser errors distinguish text-block, code-block, list-item-count and 512-block failures from the service-level output error.
- Required regressions cover duplicate canonical hits, first-ranked retention, ordering, 300 accepted semantic blocks under 64 KiB, 513 rejected blocks, parser-bound causes and the existing serialized-output rejection.

Architect Review was preserved unchanged.

### Validation Results

- Focused Vitest command: PASS, 6 files and 78 tests.
- Duplicate-path Studio integration regression: PASS, 1 file and 10 tests.
- Targeted ESLint for `lib/discovery/document.ts`, `src/commerce/integration/studio/services.ts`, `tests/discovery-document.test.ts` and `tests/studio-integration.test.ts`: PASS, 0 errors and 0 warnings.
- `npm run typecheck`: exits 2 on unchanged unrelated Commerce/generated/database and integration/test baseline diagnostics; no diagnostics reference `lib/discovery/document.ts`, the changed `searchDocumentation` expression, `tests/discovery-document.test.ts` or `tests/studio-integration.test.ts`.
- Raw rendering audit: PASS for documentation rendering. The only matches are allowed unrelated `item.text` uses in MCP transport (`lib/discovery/upstream.ts`) and preview UI (`src/studio/preview/preview-screen.tsx`).
- StudioWorkspace ownership audit: PASS with no matches.
- Production test-seam audit: PASS with no matches.
- Component existence audit: PASS for both required modules.
- Duplicate-result identity audit: PASS; `key={item.path}` remains in the explorer and the Studio service regression proves unique canonical paths with first-ranked retention and stable order.
- Conflict-marker audit: PASS against the parent task report.
- `git diff --check`: PASS.

### Branch and Topology Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-035`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-035`.
- Mirrored branch: `task/ARCH-021-COMMERCE-035`.
- Launcher claim commit: parent `88e2d8887e0a908edcc3e3de86e4693d526c3856`.
- Dependency `ARCH-021-COMMERCE-034`: complete.
- Database submodule: `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
- Implementation commit: `564ad58`, pushed to `origin/task/ARCH-021-COMMERCE-035`.
- No downstream task was started.

### Deviations

- Typecheck exits 2 on the documented unchanged Prisma/generated and unrelated Commerce integration/test diagnostics; no diagnostic references the Attempt 4-owned parser, upstream normalizer or focused test file.

### Assumptions

- The verified direct Shopify HTML fetch remains the only opened-document source, and the pinned MCP path remains search-only.

### Unresolved Issues

- None within the bounded Commerce-035 scope. The task is ready for architect review; no downstream task was started.

### Architectural Concerns

- None identified within the bounded Commerce-035 scope.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 5 resolves the two additional developer-manual-validation issues reported
while Attempt 4 was already running.

#### Duplicate documentation result identity

Architect review confirms the production Studio boundary now canonicalizes each
backend documentation `sourceUrl` to its documentation `path` and de-duplicates
before returning `DocumentationItem[]`:

```text
backend ranked hits
  -> canonical path
  -> first occurrence wins
  -> stable unique ordering
  -> ShopifyDocumentationExplorer
```

The existing React identity:

```tsx
key={item.path}
```

is therefore now valid because the server-side contract guarantees path
uniqueness.

The focused integration regression proves duplicate query/object hits collapse to
one result each, preserve the first-ranked title/excerpt and preserve unique result
order.

#### Parser/document bounds

The semantic block ceiling is now:

```text
512 blocks
```

while all other accepted safety bounds remain unchanged:

```text
HTML input:          1 MiB
redirects:           2
list items/block:    100
normal text/block:   8 KiB
code block:          16 KiB
serialized document: 64 KiB
```

Parser-level failure causes are now distinguishable:

```text
text block exceeded bounded size
code block exceeded bounded size
list exceeded bounded item count
document exceeded 512-block limit
```

and remain distinct from the final Studio/service transport guard:

```text
Documentation result exceeded the bounded size.
```

The final regressions prove:

```text
300 small semantic blocks
  -> parser accepts
  -> serialized DTO remains below 64 KiB

513 semantic blocks
  -> parser rejects with the 512-block-specific error

serialized DTO above 64 KiB
  -> service still rejects with the service-level bounded-size error
```

The 64 KiB service-output ceiling was not increased.

#### Previously accepted C035 behavior remains intact

Attempt 5 preserves all accepted documentation behavior from Attempts 1-4:

- search excerpts are safe bounded plain text;
- encoded HTML tags do not reappear as raw markup;
- Unicode excerpt truncation is code-point safe;
- `<br>` remains readable in paragraph and preformatted content;
- Shopify page chrome/accessibility helpers are filtered server-side;
- decorative/duplicate generated page blocks are cleaned up conservatively;
- opened documents remain structured `HEADING | PARAGRAPH | LIST | CODE |
  BLOCKQUOTE` DTOs;
- no remote/raw HTML reaches `dangerouslySetInnerHTML`;
- canonical opened-document origin remains `https://shopify.dev/docs/...`;
- `StudioWorkspace` does not contain a second documentation implementation;
- `ShopifyDocumentationExplorer` owns search/open state and uses the production
  named Server Actions;
- `ShopifyDocumentationArticle` remains a pure semantic renderer;
- no production documentation test port/service/context was introduced.

The task record contains no Git conflict-marker residue.

### Submitted validation

Attempt 5 reports:

```text
focused tests:     6 files / 78 passed
integration tests: 1 file / 10 passed
targeted ESLint:   PASS
source/UI audits:  PASS
conflict audit:    PASS
git diff --check:  PASS
typecheck:         unchanged unrelated baseline only
                   zero C035-owned diagnostics
```

Architect static review confirms the required duplicate-result and parser-bound
regressions are present in the submitted snapshot.

The archive does not contain installed dependencies suitable for independently
rerunning the full Vitest/ESLint/typecheck packet, so acceptance is based on the
submitted validation evidence plus direct source/test inspection.

Implementation reviewed:

```text
564ad58f
```

Final parent report supplied:

```text
cdc5d0cd
```

### Reviewed Files

- `lib/discovery/document.ts`
- `lib/discovery/upstream.ts`
- `lib/discovery/service.ts`
- `src/commerce/integration/studio/services.ts`
- `src/studio/discovery/shopify-documentation-explorer.tsx`
- `src/studio/discovery/shopify-documentation-article.tsx`
- `tests/discovery-document.test.ts`
- `tests/studio-integration.test.ts`
- task Completion Report
- Commerce ARCH-021 index/frontier
- terminal SYSTEM-TEST-001 dependency state

### Validation Reviewed

Architect directly confirmed in the submitted source:

```text
maxBlocks = 512
duplicate search paths are filtered via seenPaths before Studio response
text/code/list/block-count parser errors are distinct
64 KiB service-output guard remains unchanged
```

Architect directly confirmed regressions for:

```text
300 blocks accepted below 64 KiB
513 blocks rejected at parser
duplicate canonical query/object paths retain first occurrence and order
existing >64 KiB service-output rejection
```

### Architecture Conformance

Conforms.

C035 now safely normalizes, semantically cleans, bounds and renders Shopify
documentation while maintaining stable search-result identity and useful
diagnostics for bounded failures.

### Follow-up

`ARCH-021-COMMERCE-035` is Complete.

Every implementation dependency of terminal `ARCH-021-SYSTEM-TEST-001` is again
architect-accepted Complete, so `ARCH-021-SYSTEM-TEST-001` becomes Ready.

The developer may intentionally leave SYSTEM-TEST-001 Ready while manually
re-checking the real Shopify Collection query/object pages that originally
surfaced the formatting, duplicate-key and bounded-size defects.

If those real pages now fail with the **service-level** message:

```text
Documentation result exceeded the bounded size.
```

return that new manual evidence rather than increasing the 64 KiB transport bound
automatically.

Phase-3 implementation remains paused until terminal checkpoint
validation/reconciliation.

Do not start a Phase-3 implementation task from this acceptance.
