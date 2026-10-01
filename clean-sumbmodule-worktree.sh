#!/bin/bash

echo "🔄 Traversing submodules to purge internal worktrees..."

# Execute worktree removal script inside every active submodule
git submodule foreach --recursive '
    echo "📦 Checking submodule: $name"
    
    # List all worktrees for this submodule, skip the first (primary) line
    git worktree list | tail -n +2 | awk '\''{print $1}'\'' | while read -r wt_path; do
        if [ -n "$wt_path" ]; then
            echo "  🗑️ Force removing submodule worktree: $wt_path"
            git worktree remove --force "$wt_path"
        fi
    done
    
    # Prune any lingering dead metadata links
    git worktree prune
'

echo "✅ Submodule worktree cleanup complete."

