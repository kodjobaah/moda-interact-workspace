---
id: ARCH-003-ADMIN-011
architecture_id: ARCH-003
title: Recompose Shopify Queues into main table and right details drawer
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 41
executor: copilot
claimed_at: 2026-09-04T22:06:39Z
attempt: 4
depends_on:
  - ARCH-003-ADMIN-010
  - ARCH-003-ADMIN-014
enables:
  - ARCH-003-ADMIN-012
created: 2026-09-04
updated: 2026-09-04
---

# Recompose Shopify Queues into main table and right details drawer

## Objective

Change the Shopify Queues page composition to match the approved reference:
queue table in the main content area and a right-hand `Queue details` drawer
opened by `View details`.

## Visual reference

`docs/architecture/ARCH-003-shopify-queues-approved-reference.png`

## Attempt 2 Architect Correction — TRUE OVERLAY, NO TABLE REFLOW

Attempt 1 is **not accepted** visually.

The current runtime implementation renders the queue-details `<aside>` as a
normal-flow sibling inside:

```text
flex ... lg:flex-row
  -> table flex-1
  -> aside lg:max-w-md
```

That is a side-by-side split layout, not a true overlay. When the drawer opens,
the table loses width and the queue columns are visibly compressed.

Rejected runtime reference:

`docs/architecture/ARCH-003-ADMIN-011-rejected-inflow-drawer.png`

Approved target reference:

`docs/architecture/ARCH-003-shopify-queues-approved-reference.png`

### Required desktop behavior

Opening `View details` MUST NOT change the layout width of the queue table.

Conceptually:

```text
BEFORE
┌─────────────────────────────────────────────────────────────┐
│ full-width queue table                                      │
└─────────────────────────────────────────────────────────────┘

AFTER
┌─────────────────────────────────────────────────────────────┐
│ full-width queue table                              ╔═══════╗│
│                                                     ║drawer ║│
│ table remains its original width beneath/behind     ║overlay║│
│ the independently positioned panel                 ║       ║│
└─────────────────────────────────────────────────────╚═══════╝┘
```

The drawer must therefore be outside normal table layout flow.

Accepted implementation shapes include:

- a portal to `document.body` with `position: fixed`; or
- an equivalent fixed-position panel whose containing block does not participate
  in the queue table's width calculation.

A second flex/grid column that consumes main-content width is explicitly
**not acceptable**.

### Drawer geometry

On desktop/laptop:

```text
position: fixed
right: 0
top/bottom: viewport edges (or equivalent full shell height)
z-index: above Admin content
width: approximately 440-560px, bounded by viewport
height: 100dvh / full available viewport
background: opaque
left border + elevated shadow
```

Exact Tailwind values may follow the existing design system, but the behavioral
contract above is mandatory.

On narrow screens the same drawer may become full-width.

### Scrolling

- drawer header/close affordance remains visible;
- only the drawer body should vertically scroll for long diagnostic content;
- opening the drawer must not introduce horizontal page overflow;
- the main queue table must retain its existing overflow-x behavior independently.

### State behavior

- selected queue row remains highlighted;
- closing the drawer must not mutate queue data;
- reopening the same queue may reuse already-loaded state;
- changing queue resets selected failed-job detail appropriately;
- APIs/readers remain unchanged in this task.

### Mandatory visual/runtime proof

Source assertions alone are NOT sufficient for Attempt 2.

Before returning to `review`, provide runtime evidence with a populated live
queue snapshot:

1. capture or inspect the table with drawer closed;
2. click `View details`;
3. capture or inspect the table with drawer open;
4. verify the table container width does not materially change.

If browser measurement is available, record:

```text
closed table width
open table width
difference <= 1px
```

If automated layout measurement is not available, include a runtime screenshot
showing the populated table with the fixed overlay open.

If neither runtime proof nor screenshot can be produced, return the task
`blocked` for visual verification rather than marking these criteria complete.

## Attempt 3 Architect Correction — FULL-WORKSPACE, RESIZABLE OVERLAY

Attempt 2 successfully removed table reflow and proved a fixed right overlay
with a stable 560px width.

That implementation is directionally correct but is **not yet accepted** because
the desired interaction has now been clarified further.

Attempt 3 must preserve the true-overlay/no-reflow behavior while changing the
drawer into a **full-workspace overlay that can be resized narrower by the
administrator**.

Attempt 2 runtime reference:

`docs/architecture/ARCH-003-ADMIN-011-attempt2-fixed-drawer-reference.png`

Approved overall visual language:

`docs/architecture/ARCH-003-shopify-queues-approved-reference.png`

### Definition of "whole viewable area"

On desktop/tablet widths where the persistent Admin sidebar is visible, opening
`View details` must initially cover the entire **Admin workspace to the right of
the sidebar**.

The sidebar itself remains visible and usable.

Conceptually:

```text
┌──────────────┬──────────────────────────────────────────────┐
│ Admin        │ Queue details overlay                        │
│ sidebar      │                                              │
│ remains      │ initially fills ALL workspace width          │
│ visible      │ and ALL viewport height                      │
│              │                                              │
└──────────────┴──────────────────────────────────────────────┘
```

The overlay should cover the main top header/search area as well as the page
content because it represents the active diagnostic workspace.

On small screens where the sidebar is not present, the overlay occupies the
entire viewport.

### Initial width

Every time `View details` opens:

```text
desktop:
  width = viewport width - visible Admin sidebar width

mobile:
  width = 100vw
```

Do not reopen at an old narrowed width.

Resizing is per-open-session UI state only unless a future task explicitly
introduces a saved user preference.

### Resizable behavior

On supported desktop widths, provide a visible or discoverable resize handle
along the overlay's left edge.

Dragging the handle horizontally must resize only the overlay:

```text
drag handle right  -> narrower overlay, underlying table becomes visible
drag handle left   -> wider overlay
```

The queue table underneath must remain at exactly the same layout width
throughout. Resizing the overlay must never participate in the table's flex/grid
calculation.

Use sensible bounds:

```text
minimum overlay width: approximately 28rem / 448px
maximum overlay width: full available Admin workspace
```

Exact design-system values may vary slightly, but the user must not be able to
resize the drawer below a usable diagnostic width or beyond the available
workspace.

### Maximize/reset control

Add a clear `Maximize`, `Expand`, or equivalent accessible action in the drawer
header.

It must restore:

```text
overlay width = full available Admin workspace
```

The existing Close action remains.

### Accessibility

The resize affordance must not be pointer-only.

Provide a keyboard-operable resize mechanism. A suitable implementation is a
focusable vertical separator/handle with:

```text
ArrowLeft   -> grow overlay by a bounded step
ArrowRight  -> shrink overlay by a bounded step
Home        -> minimum width
End         -> maximum/full-workspace width
```

Equivalent accessible keyboard semantics are acceptable.

Expose an appropriate accessible label such as:

```text
Resize queue details panel
```

### Responsive behavior

Below the desktop/tablet resizing breakpoint:

- overlay remains full viewport width;
- resize handle may be hidden/disabled;
- Close remains available;
- internal content remains scrollable.

### Scrolling and layering

Preserve Attempt 2 behavior:

- fixed positioning;
- opaque background;
- elevated z-index/shadow;
- full viewport height;
- fixed header/controls;
- independently scrollable drawer body;
- no horizontal document overflow.

### No reflow invariant

This remains mandatory.

Runtime measurement must prove:

```text
table width closed
table width overlay maximized
table width overlay narrowed

maximum difference <= 1px
```

### Mandatory runtime proof

Attempt 3 may return to review only after testing against a populated live queue
snapshot.

Required proof:

1. open Shopify Queues with real queue rows;
2. measure queue-table width with overlay closed;
3. open Queue details and verify it fills the Admin workspace;
4. measure queue-table width;
5. drag/resize overlay narrower;
6. measure queue-table width again;
7. activate Maximize and verify full workspace width is restored;
8. close and reopen, verifying it opens maximized again.

Record safe geometry, for example:

```text
viewport width
sidebar width
closed table width
maximized overlay width
narrowed overlay width
table width while maximized
table width while narrowed
```

No Redis URLs, credentials, job payloads, or secrets are required in this
evidence.

Source assertions alone are not sufficient.

## Attempt 4 Architect Correction — QUEUE NAME IS THE SWITCH CONTROL

Attempt 3 successfully implemented the full-workspace resizable overlay and is
accepted as the interaction base, but it is **not yet the final accepted
ADMIN-011 state**.

Runtime use of the narrowed overlay exposed one remaining usability problem:

- the underlying table's far-right `View details` action can become visible;
- the queue-name column may also be visible on the left;
- the action itself does not communicate which queue the user is about to
  select when the middle of the row is obscured by the overlay.

Attempt 4 must make the **queue name itself** the explicit queue-selection
control.

Runtime interaction reference:

`docs/architecture/ARCH-003-ADMIN-011-attempt3-resizable-overlay-reference.png`

### Required table interaction

Remove the separate `Actions` / `View details` column from the queue table.

Render each queue name as the accessible selection control, visually preserving
the queue-name treatment:

```text
checkout-events
order-events
pending-recovery-candidates
whatsapp-events
```

Conceptually:

```text
QUEUE NAME                         JOB LABEL     ...
checkout-events        <- click
order-events           <- click
pending-recovery...    <- click
whatsapp-events        <- click
```

Do not require the user to click an unlabeled/visually detached action at the
far right of a partially obscured row.

### Opening versus switching behavior

These are two distinct interactions and MUST behave differently.

#### A. Drawer is closed

Clicking a queue name:

```text
queue name click
  -> select queue
  -> open Queue details
  -> overlay opens maximized/full-workspace
```

This preserves the accepted Attempt 3 default-open behavior.

#### B. Drawer is already open and has been resized narrower

Clicking another visible queue name:

```text
narrowed overlay
  -> queue names exposed on left
  -> click another queue name
  -> selected queue changes
  -> drawer heading/content changes to new queue
  -> CURRENT DRAWER WIDTH IS PRESERVED
```

Do **not** call the equivalent of:

```text
setDrawerWidth(null)
```

when switching from one selected queue to another while the drawer is already
open.

The overlay must not jump back to maximized width merely because the selected
queue changes.

### Queue-scoped state reset

When switching queues, clear/reset only queue-specific diagnostic state that
would otherwise show stale information:

- selected failed job;
- failed-job detail;
- failed-job error/loading state as appropriate;
- failed-job list/request state as required by the existing data flow.

Then load the newly selected queue's failure data.

Do not reset:

- drawer width;
- overlay resize position;
- global queue snapshot;
- refresh preference.

### Selection visibility

The selected queue row/name must remain visually identifiable.

When a new queue name is clicked:

```text
old selected row -> normal
new selected row -> selected/highlighted
drawer queue name -> immediately reflects new queue
```

### Accessibility

The queue-name control must be keyboard accessible.

Use a real `button` or semantically equivalent interactive control with an
accessible name containing the queue identity, for example:

```text
Open checkout-events queue details
Open order-events queue details
```

Do not make the entire row pointer-only.

### Table density

Removing the separate Actions column is desirable and intentional. The recovered
horizontal space should remain available to the operational columns rather than
being replaced by another redundant control column.

### Mandatory runtime proof

Attempt 4 must be proven with populated live queue data.

Required sequence:

```text
1. Drawer closed.
2. Click checkout-events queue name.
3. Verify drawer opens maximized and shows checkout-events.
4. Resize drawer narrower until queue-name column is exposed.
5. Record current drawer width.
6. Click order-events queue name.
7. Verify drawer now shows order-events.
8. Verify drawer width is unchanged (difference <= 1px).
9. Verify order-events row is selected.
10. Click another visible queue name, e.g. whatsapp-events.
11. Verify heading/selection/data follow the new queue without maximizing.
12. Close drawer.
13. Click a queue name again.
14. Verify a fresh open is maximized as required by Attempt 3.
```

Source assertions alone are not sufficient.

## Scope

- preserve the current four-queue compact table and refresh controls;
- preserve row selection;
- introduce a right-side queue-details drawer shell;
- move queue-scoped presentation out of the inline-below-table composition;
- close the drawer without clearing/changing queue data;
- preserve read-only behavior;
- keep responsive behavior usable on laptop widths.

## Attempt 2 Work Items

- [x] Remove the in-flow flex-sibling drawer composition.
- [x] Render Queue details as a fixed/portal overlay that does not consume table width.
- [x] Keep a stable desktop drawer width and full-height scrollable body.
- [x] Preserve close/selection/read-only behavior.
- [x] Add regression coverage preventing return to the flex-sibling layout.
- [x] Produce populated runtime visual/layout proof.
- [x] Run full Admin validation.
- [x] Return this same task to `review` and STOP.

## Attempt 3 Work Items

- [x] Change the default open width from fixed 560px to full available Admin workspace.
- [x] Add a left-edge drag resize handle on desktop.
- [x] Clamp resizing to a usable minimum and full-workspace maximum.
- [x] Add keyboard-accessible resizing.
- [x] Add Maximize/reset-to-full-width control.
- [x] Reset to maximized width whenever a drawer is newly opened.
- [x] Preserve fixed overlay/no-table-reflow behavior.
- [x] Preserve independent drawer-body scrolling.
- [x] Add focused interaction/regression tests.
- [x] Produce live populated runtime geometry proof.
- [x] Run full Admin validation.
- [x] Return this same task to `review` and STOP.

## Attempt 4 Work Items

- [x] Remove the separate Actions/View details table column.
- [x] Make each queue name the accessible queue-selection control.
- [x] Preserve maximized opening when no drawer is currently open.
- [x] Preserve current drawer width when switching queues while open.
- [x] Reset stale queue-specific failed-job/detail state on queue switch.
- [x] Preserve selected-row highlighting.
- [x] Add focused keyboard/interaction regression coverage.
- [x] Produce live populated switch-queue runtime proof.
- [x] Run full Admin validation.
- [x] Return this same task to `review` and STOP.

## Requirements

- selecting `View details` opens the drawer on the right;
- the selected row remains visually selected;
- the main queue table remains visible while the drawer is open on supported
  desktop widths;
- the old large inline failed-job/detail section must not remain duplicated
  beneath the table;
- this task builds the drawer composition/shell only; detailed metrics and
  recent-failure content are ADMIN-012;
- preserve all current APIs and server readers.

## Acceptance Criteria

- [x] `View details` opens a right-hand Queue details drawer.
- [x] Drawer has a visible close action.
- [x] Main queue table remains visible alongside the drawer on desktop.
- [x] Selected queue row is visually identifiable.
- [x] Inline duplicate queue-detail content is removed.
- [x] Existing refresh controls still work.
- [x] Full validation passes.
- [x] Drawer is outside normal queue-table layout flow.
- [x] Opening the drawer does not reduce the queue table container width.
- [x] Desktop drawer is fixed to the right and vertically independent.
- [x] Drawer body scrolls without expanding/compressing the main table.
- [x] Populated runtime screenshot/layout proof is recorded.
- [x] Drawer initially fills the entire Admin workspace to the right of the sidebar.
- [x] Mobile drawer initially fills the entire viewport.
- [x] Desktop drawer can be resized by dragging its left edge.
- [x] Resize interaction is keyboard-accessible.
- [x] Overlay width is clamped to a safe minimum and workspace maximum.
- [x] Maximize restores full workspace width.
- [x] Closing/reopening resets the overlay to maximized width.
- [x] Table width remains invariant closed, maximized, and narrowed.
- [x] Live populated runtime geometry proof is recorded.
- [x] Queue name is the visible/accessible selection control.
- [x] Separate Actions/View details column is removed.
- [x] Closed -> queue-name click opens maximized.
- [x] Open/narrowed -> another queue-name click preserves drawer width.
- [x] Selected row/name updates immediately on queue switch.
- [x] Queue-specific failed-job/detail state cannot leak from previous queue.
- [x] Keyboard activation of queue names works.
- [x] Live runtime proof shows queue switching at unchanged narrowed width.

## Completion Report

### Attempt 1

Historical: rejected in-flow split-pane implementation.

### Attempt 2

Historical: accepted true-overlay/no-table-reflow foundation.

### Attempt 3

Historical interaction base: full-workspace initial open, resizable overlay,
keyboard resizing, Maximize, and zero table reflow were successfully proven.

Attempt 3 runtime proof remains valid, but final ADMIN-011 acceptance is held for
the queue-switch interaction correction.

### Attempt 4 Status

Ready for Review.

### Attempt 4 Files Changed

- `src/components/admin/queue-monitor.tsx`
- `tests/security/admin-queue-details-drawer.test.mjs`
- `tests/security/admin-queue-monitor.test.mjs`

### Attempt 4 Validation

- Removed the detached Actions/View details column and made each queue name a
  keyboard-accessible button with an explicit queue identity in its accessible
  name.
- Fresh queue-name opens reset the drawer to the full workspace; queue-name
  switches while the drawer is open preserve the current width.
- Queue switching aborts stale failed-job/detail requests and clears
  queue-specific failed-job, selected-job, detail, and error state before the
  new queue request begins.
- Kept the selected queue row highlighted and preserved the fixed,
  right-anchored, independently scrollable overlay and no-reflow behavior.
- Live populated runtime proof at 1440x900:
  - sidebar: 240px;
  - closed table: 1084px;
  - fresh `checkout-events` open: x=240px, width=1200px, height=900px;
  - drag-narrowed overlay: x=800px, width=640px, height=900px;
  - table while maximized and narrowed: 1084px;
  - clicking `order-events` preserved 640px and highlighted its row;
  - keyboard `Enter` on `whatsapp-events` preserved 640px, updated the drawer
    queue name, and highlighted its row;
  - close/reopen restored x=240px and width=1200px.
- Focused drawer tests: 3 passed.
- Existing queue-monitor regression file: 13 passed.
- `npm test`: 60 passed.
- `npm exec tsc -- --noEmit`: passed.
- `npm run lint`: passed with two existing `react-hooks/exhaustive-deps`
  warnings in `src/components/admin/queue-monitor.tsx`.
- `npm run build`: passed with existing multiple-lockfile workspace-root and
  optional BullMQ `@valkey/valkey-glide` warnings.
- `git diff --check`: passed.

### Work Completed

Attempt 4 completes the queue-name switch interaction correction without
changing APIs, Redis readers, queue semantics, pagination ownership, or the
diagnostic model.

### Deviations

None.

### Assumptions

- The persistent desktop Admin sidebar remains 240px (`w-60`) and the desktop
  breakpoint remains 768px.
- Drawer width is per-open-session UI state and is not persisted.

### Unresolved Issues

None.

### Architectural Concerns

None.

### Git / VCS

Implementation is ready for developer commit/push. The repository agent did not
commit or push.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 4 is architect-accepted Complete.

The reviewed implementation now satisfies the drawer-composition and
queue-switch interaction requirements:

- Queue details is a true fixed overlay and does not participate in queue-table
  layout flow;
- the table width remains invariant while the drawer is closed, maximized, or
  narrowed;
- the drawer opens across the full Admin workspace, is resizable, can be
  maximized, and is independently scrollable;
- resizing is keyboard accessible;
- queue names themselves are the visible selection controls;
- the separate Actions/View details column is removed;
- narrowing the drawer exposes identifiable queue names;
- switching queues while the drawer is open preserves the current drawer width;
- a fresh open resets the drawer to maximized width;
- switching queues aborts/clears stale queue-specific diagnostic state;
- selected-row highlighting follows the active queue.

Live Attempt 4 proof records a 640px narrowed drawer where switching from
`checkout-events` to `order-events` and then keyboard-selecting
`whatsapp-events` preserved the same drawer width.

### Reviewed Files

- `moda-interact-admin/src/components/admin/queue-monitor.tsx`
- `moda-interact-admin/tests/security/admin-queue-details-drawer.test.mjs`
- `moda-interact-admin/tests/security/admin-queue-monitor.test.mjs`
- `docs/decisions/admin/ARCH-003/ADMIN-011-recompose-queues-details-drawer.md`

### Validation Reviewed

Implementing-agent evidence records:

- full Admin tests: 60 passed;
- focused drawer tests: pass;
- TypeScript: pass;
- lint: pass with the two existing hook warnings;
- production build: pass;
- `git diff --check`: pass;
- live desktop/keyboard queue-switch proof: pass.

### Architecture Conformance

Accepted.

The drawer mechanics are now complete. New shop/status filtering requirements
are intentionally decomposed into subsequent server and UI tasks rather than
being folded back into ADMIN-011.

### Follow-up

`ARCH-003-ADMIN-015` is now Ready.

It must build the bounded generic queue-job list/filter server contract before
the UI is changed.
