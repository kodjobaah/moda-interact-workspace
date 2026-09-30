#!/bin/bash

# Ensure we exit immediately if a command fails
set -e

# Define the exact relative path where the onboarding fragments live
FRAGMENTS_DIR="../moda-onboarding-redesign/i18n-fragments"

echo "🚀 Starting cross-directory locale file concatenation..."

# Safety check: make sure the fragments folder actually exists where we expect it
if [ ! -d "$FRAGMENTS_DIR" ]; then
    echo "❌ Error: Could not find the fragments folder at: $FRAGMENTS_DIR"
    echo "Make sure you are running this script from inside the 'locales' folder."
    exit 1
fi

# Track processed files
processed_count=0

# Loop directly through the onboarding files in the sibling directory
for extra_path in "$FRAGMENTS_DIR"/*.onboarding.json; do
    
    # Safety check: ensure files actually matched the glob pattern
    [ -e "$extra_path" ] || continue

    # Extract just the filename from the full path (e.g., "cs.onboarding.json")
    extra_file=$(basename "$extra_path")

    # Extract the core language prefix (e.g., gets "cs" from "cs.onboarding.json")
    lang_code=$(echo "$extra_file" | cut -d'.' -f1)
    core_file="${lang_code}.json"

    # If the main core file doesn't exist locally, create an empty JSON object
    if [ ! -f "$core_file" ]; then
        echo "📄 Core file $core_file not found in current directory. Initialising it."
        echo "{}" > "$core_file"
    fi

    echo "🔄 Merging: $FRAGMENTS_DIR/$extra_file ➔ ./$core_file"

    # Create a temporary file to hold the merged data safely
    tmp_file=$(mktemp)

    # Deeply merge the local core file with the external onboarding fragment
    jq -s 'reduce .[] as $item ({}; . * $item)' "$core_file" "$extra_path" > "$tmp_file"

    # Overwrite the original local core file with the freshly merged version
    mv "$tmp_file" "$core_file"

    ((processed_count++))
done

if [ "$processed_count" -eq 0 ]; then
    echo "⚠️ No onboarding fragment files found to process."
else
    echo "✅ Successfully combined $processed_count onboarding modules directly into your local core locale files!"
fi

