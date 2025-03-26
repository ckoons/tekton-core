#!/bin/bash
# commit-all.sh - Script to commit changes across all Tekton subprojects

COMMIT_MSG="$1"
if [ -z "$COMMIT_MSG" ]; then
  echo "Usage: ./commit-all.sh 'Your commit message'"
  exit 1
fi

# Get current directory for later
TEKTON_DIR=$(pwd)

# List of project directories
PROJECTS=("Codex" "Engram" "Ergon" "Rhetor" "Sophia" "Telos")

# Track which projects were changed
CHANGED=false

# Commit changes in each project
for PROJECT in "${PROJECTS[@]}"; do
  if [ -d "$PROJECT" ]; then
    cd "$PROJECT"
    
    # Check if there are changes
    if [[ -n $(git status -s) ]]; then
      echo "Committing changes in $PROJECT..."
      git add .
      git commit -m "$COMMIT_MSG"
      git push
      CHANGED=true
    else
      echo "No changes in $PROJECT"
    fi
    
    cd "$TEKTON_DIR"
  else
    echo "Warning: $PROJECT directory not found"
  fi
done

echo ""
if [ "$CHANGED" = true ]; then
  echo "✅ Changes committed and pushed to repositories"
else
  echo "ℹ️ No changes found in any project"
fi