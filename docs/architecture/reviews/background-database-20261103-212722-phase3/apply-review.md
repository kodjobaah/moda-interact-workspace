# Apply the focused deep-dive review

This delivery is an analysis patch, not an accepted implementation patch. It adds only `docs/architecture/reviews/background-database-20261103-212722-phase3/` in the parent workspace. It does not depend on applying the earlier reassessment patch. The ZIP contains exactly the same patch file as the standalone download.

## Dedicated parent review worktree

From the **real parent-workspace checkout at the revision corresponding to the updated snapshot**, create a dedicated documentation review worktree once:

```bash
git worktree add \
  -b review/background-database-20261103-212722-phase3 \
  /Users/kwadwoadomafriyie/project/moda-interact-workspace-review-background-database-20261103-212722-phase3 \
  HEAD
```

The review cannot verify which real Git revision produced the ZIP; select that base in your actual checkout. This command creates a new review branch from that selected HEAD. If the named worktree/branch already exists, inspect and use it rather than creating or overwriting it again. No implementation-repository branch is needed for this documentation-only patch.

## Apply, inspect, commit and push

After downloading the patch into Downloads, run:

```bash
cd /Users/kwadwoadomafriyie/project/moda-interact-workspace-review-background-database-20261103-212722-phase3

test "$(git branch --show-current)" = "review/background-database-20261103-212722-phase3"
test -z "$(git status --porcelain)"

git apply --check --whitespace=error-all \
  ~/Downloads/BACKGROUND-DATABASE-DEEP-DIVE-20261103-212722-phase3-attempt3-analysis.patch

git apply --whitespace=error-all \
  ~/Downloads/BACKGROUND-DATABASE-DEEP-DIVE-20261103-212722-phase3-attempt3-analysis.patch

git diff --check

git add -- docs/architecture/reviews/background-database-20261103-212722-phase3
git diff --cached --check
git diff --cached --stat

git commit -m "review(background-database): record focused correction contracts"
git push origin review/background-database-20261103-212722-phase3
```

The two initial checks require the expected dedicated branch and a clean worktree/index; if either fails, inspect the existing state before applying anything. `git diff --cached --check` is included because newly added files are not inspected by an ordinary unstaged `git diff --check` until registered. Staging is restricted to the new review directory.

The documentation commit should contain ten new review/evidence files: the main review, three focused appendices, validation handoff, this apply guide, schema audit/script output, and the two PostgreSQL mechanism files. No application file or acceptance/task status belongs in that commit.

These are local handoff commands. The review environment has not created this real worktree, committed, pushed or merged either repository. Patch verification was performed in temporary Git repositories against a fresh extraction of the exact supplied ZIP; the separate validation record describes that evidence precisely.
