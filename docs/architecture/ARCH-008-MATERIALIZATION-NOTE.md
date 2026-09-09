# ARCH-008 materialisation note

ARCH-008 was authored from a supplied full-workspace snapshot rather than from the developer's canonical Git worktrees/remotes.

Therefore this overlay is **defined but not materialised**:

- no task branch is claimed to exist;
- no parent or implementation worktree is claimed to exist;
- no commit or push is claimed;
- no repository implementation code is changed by this overlay.

Apply the overlay at workspace root, review the documentation diff, and materialise executable tasks using the normal workspace task launcher. The launcher-resolved task worktree must then synchronise with current `origin/main` before implementation.

Because the supplied snapshot may predate some already-accepted ARCH-007 integrations, ARCH-008 task definitions use **capability preflights**. A task must verify its named ARCH-007 prerequisite capability is actually present in the synchronised task worktree. If it is absent, stop and report a parent-main integration/dependency gap. Do not recreate or cherry-pick unrelated prerequisite work inside ARCH-008.

This overlay intentionally does **not** rewrite `docs/architecture/_index.md` or architecture-wide current-state rollups whose canonical state cannot be established from the supplied snapshot. `moda_architect` should reconcile those in the canonical workspace during materialisation.
