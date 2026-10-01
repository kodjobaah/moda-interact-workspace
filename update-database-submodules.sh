#!/usr/bin/env bash

set -euo pipefail

MODULES=(
  "moda-interact"
  "moda-interact-admin"
  "moda-interact-background"
  "moda-interact-commerce"
)

ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

COMMIT_MESSAGE="chore(database): update database submodule"

for MODULE in "${MODULES[@]}"; do
  echo
  echo "================================================================"
  echo "  $MODULE"
  echo "================================================================"

  MODULE_DIR="$ROOT_DIR/$MODULE"
  DATABASE_DIR="$MODULE_DIR/database"

  if [[ ! -d "$MODULE_DIR" ]]; then
    echo "ERROR: Module does not exist: $MODULE_DIR"
    exit 1
  fi

  if [[ ! -d "$DATABASE_DIR" ]]; then
    echo "ERROR: Database submodule does not exist: $DATABASE_DIR"
    exit 1
  fi

  # ------------------------------------------------------------
  # Verify parent repository
  # ------------------------------------------------------------
  cd "$MODULE_DIR"

  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "ERROR: $MODULE is not a Git repository."
    exit 1
  fi

  # Ignore the database submodule pointer when checking whether
  # the parent already has unrelated local modifications.
  PARENT_CHANGES="$(
    git status --porcelain |
      grep -vE '^[ MADRCU?!]{2} database(/|$)' ||
      true
  )"

  if [[ -n "$PARENT_CHANGES" ]]; then
    echo "ERROR: $MODULE has unrelated local changes:"
    echo
    echo "$PARENT_CHANGES"
    echo
    echo "Resolve/stash them before running this script."
    exit 1
  fi

  # ------------------------------------------------------------
  # Verify and update database submodule
  # ------------------------------------------------------------
  cd "$DATABASE_DIR"

  if [[ -n "$(git status --porcelain)" ]]; then
    echo "ERROR: $MODULE/database has local changes:"
    git status --short
    echo
    echo "Resolve/stash them before running this script."
    exit 1
  fi

  DATABASE_BRANCH="$(git branch --show-current)"

  if [[ -z "$DATABASE_BRANCH" ]]; then
    echo "ERROR: $MODULE/database is in detached HEAD state."
    echo "Check out the intended database branch before continuing."
    exit 1
  fi

  BEFORE_SHA="$(git rev-parse HEAD)"

  echo "Database branch : $DATABASE_BRANCH"
  echo "Before           : $BEFORE_SHA"

  git pull --ff-only

  AFTER_SHA="$(git rev-parse HEAD)"

  echo "After            : $AFTER_SHA"

  # ------------------------------------------------------------
  # Nothing changed
  # ------------------------------------------------------------
  if [[ "$BEFORE_SHA" == "$AFTER_SHA" ]]; then
    echo "No database update for $MODULE."
    continue
  fi

  # ------------------------------------------------------------
  # Commit the new database pointer in the parent repository
  # ------------------------------------------------------------
  cd "$MODULE_DIR"

  echo
  echo "Submodule update:"
  git diff --submodule=short -- database

  git add database

  if git diff --cached --quiet; then
    echo "No parent repository change to commit."
    continue
  fi

  git commit -m "$COMMIT_MESSAGE"

  echo
  echo "Pushing $MODULE..."
  git push

  echo
  echo "✓ $MODULE updated successfully."
done

cd "$ROOT_DIR"

echo
echo "================================================================"
echo "✓ All database submodules processed successfully."
echo "================================================================"
