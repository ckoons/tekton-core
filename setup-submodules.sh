#!/bin/bash
# setup-submodules.sh - Convert current structure to use Git submodules

# Get current directory
TEKTON_DIR=$(pwd)

# Check if we're in the Tekton directory
if [[ $(basename "$TEKTON_DIR") != "Tekton" ]]; then
  echo "Error: This script must be run from the Tekton directory"
  exit 1
fi

# List of projects to convert to submodules
PROJECTS=("Codex" "Engram" "Ergon" "Rhetor" "Sophia" "Telos")

# Initialize Tekton as git repository if not already
if [ ! -d ".git" ]; then
  echo "Initializing Tekton as a Git repository..."
  git init
  echo "# Tekton Project" > README.md
  echo "Master repository for the Tekton project ecosystem" >> README.md
  git add README.md
  git commit -m "Initial commit"
  
  # Add remote if Tekton repo exists on GitHub
  read -p "Does a Tekton repository exist on GitHub? (y/n): " has_remote
  if [[ $has_remote == "y" || $has_remote == "Y" ]]; then
    git remote add origin https://github.com/ckoons/Tekton.git
    git push -u origin main
  fi
fi

# Convert each project to a submodule
for PROJECT in "${PROJECTS[@]}"; do
  if [ -d "$PROJECT" ]; then
    echo "Converting $PROJECT to a submodule..."
    
    # Temporarily move the project
    mv "$PROJECT" "${PROJECT}_temp"
    
    # Add as submodule
    git submodule add https://github.com/ckoons/$PROJECT.git $PROJECT
    
    # If submodule is empty (new repo), copy files from temp
    if [ -z "$(ls -A "$PROJECT")" ]; then
      cp -r "${PROJECT}_temp/"* "$PROJECT/"
      cd "$PROJECT"
      git add .
      git commit -m "Add initial files"
      git push
      cd "$TEKTON_DIR"
    fi
    
    # Remove temp directory
    rm -rf "${PROJECT}_temp"
  else
    echo "$PROJECT directory not found, adding as a new submodule..."
    git submodule add https://github.com/ckoons/$PROJECT.git $PROJECT
  fi
done

# Commit the submodule additions
git add .
git commit -m "Set up project as submodules"

echo ""
echo "✅ Tekton project structure converted to use Git submodules"
echo ""
echo "Usage:"
echo "- To clone this repository with all submodules: git clone --recursive https://github.com/ckoons/Tekton.git"
echo "- To update all submodules to latest: git submodule update --remote"
echo "- To commit changes across all projects: ./commit-all.sh 'Your commit message'"