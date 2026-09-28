#!/bin/bash

echo "🔄 Force-removing all linked worktrees..."
# Loop through all worktrees except the main one
git worktree list | tail -n +2 | awk '{print $1}' | while read -r wt_path; do
    if [ -d "$wt_path" ] || [ -e "$wt_path" ]; then
        echo "🗑️ Removing worktree path: $wt_path"
        git worktree remove --force "$wt_path"
    fi
done

echo "🧹 Pruning administrative Git metadata..."
# Cleans up internal refs if you previously used 'rm -rf' manually
git worktree prune

echo "✅ All auxiliary worktrees removed."

