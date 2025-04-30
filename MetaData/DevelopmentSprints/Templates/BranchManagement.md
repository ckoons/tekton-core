# Tekton Branch Management Guide

This document outlines the branch management strategy for Tekton Development Sprints. It provides guidelines for creating, managing, and merging branches to ensure that development work is properly isolated and can be integrated smoothly.

## Overview

Tekton employs a branch-based development workflow to ensure that:

- Multiple Development Sprints can proceed in parallel without conflicts
- Changes can be reviewed and tested before integration
- Work is properly isolated to prevent unintended side effects
- History is preserved for future reference

Each Development Sprint must work on a dedicated branch. This isolation is crucial for maintaining the stability of the codebase while enabling parallel development efforts.

## Branch Naming Convention

Branches for Development Sprints should follow this naming convention:

```
sprint/[sprint-name]-[date]
```

Where:
- `[sprint-name]` is a brief, hyphenated name describing the sprint
- `[date]` is the sprint start date in YYMMDD format

Examples:
- `sprint/shared-code-250428`
- `sprint/github-utils-250505`
- `sprint/llm-integration-250512`

## Branch Creation Process

1. **Before creating a branch**:
   - Ensure the main branch is up to date
   - Verify that all submodules are in sync

2. **Branch creation**:
   - Create the branch from the latest main
   - Push the branch to the remote repository
   - Set up branch protection if applicable

### Command Line Example

```bash
# Ensure main is up to date
git checkout main
git pull
git submodule update --init --recursive

# Create the sprint branch
git checkout -b sprint/shared-code-250428
git push -u origin sprint/shared-code-250428
```

## Submodule Management

Since Tekton consists of multiple components that may exist as submodules, special attention is needed for branch management across these components:

1. **Main Repository Branch**:
   - Create a branch in the main Tekton repository first

2. **Component Repository Branches**:
   - For each component that will be modified, create a corresponding branch
   - Use the same branch naming convention for consistency

3. **Submodule References**:
   - Update submodule references in the main repository to point to the component branches

### Example for Component Branches

```bash
# Navigate to component directory
cd Ergon

# Create corresponding branch
git checkout -b sprint/shared-code-250428
git push -u origin sprint/shared-code-250428

# Return to main repository
cd ..

# Update submodule reference
git add Ergon
git commit -m "Update Ergon submodule reference to sprint/shared-code-250428"
```

## Branch Verification for Claude Sessions

Working Claude sessions must verify they are working on the correct branch before making any changes. This verification should be performed at the start of each session and after any significant operation.

### Branch Verification Commands

```bash
# Check current branch in main repository
git branch --show-current

# Verify each component's branch
for dir in */; do
  if [ -d "$dir/.git" ]; then
    echo "Checking $dir"
    (cd "$dir" && git branch --show-current)
  fi
done
```

## Handling Changes During a Sprint

1. **Committing Changes**:
   - Make frequent, atomic commits with clear messages
   - Follow the commit message format specified in project guidelines
   - Include the sprint name in commit messages for clarity

2. **Pushing Changes**:
   - Push changes to the remote branch regularly
   - Ensure submodule changes are pushed first, then update references

3. **Keeping Up with Main**:
   - If the sprint runs for an extended period, periodically merge or rebase from main
   - Address any conflicts that arise

## Merging Process

When a sprint is completed and ready to be integrated:

1. **Pre-Merge Checks**:
   - Ensure all tests pass
   - Verify documentation has been updated
   - Review the code for quality and adherence to guidelines

2. **Submodule Merges**:
   - Merge component branches into their respective main branches first
   - Update submodule references in the main repository

3. **Main Repository Merge**:
   - Create a pull request from the sprint branch to main
   - Address any review comments
   - Merge the pull request
   - Delete the sprint branch when no longer needed

### Merge Command Example

```bash
# For each component
cd Ergon
git checkout main
git pull
git merge --no-ff sprint/shared-code-250428
git push

# Return to main repository
cd ..
git add Ergon  # Update submodule reference
git commit -m "Update Ergon submodule reference to main"

# Now create PR for main repository or merge directly
git checkout main
git pull
git merge --no-ff sprint/shared-code-250428
git push
```

## Branch Cleanup

After a sprint is successfully completed and merged:

1. **Delete Remote Branches**:
   ```bash
   git push origin --delete sprint/shared-code-250428
   ```

2. **Delete Local Branches**:
   ```bash
   git branch -d sprint/shared-code-250428
   ```

3. **Clean up Component Branches**:
   - Follow the same process for each component repository

## Handling Merge Conflicts

If merge conflicts occur:

1. Identify the conflicting files
2. Resolve conflicts with careful attention to both sets of changes
3. Test thoroughly after resolution
4. Document any significant conflict resolution decisions

## Branch Protection Guidelines

For critical components or the main repository, consider these branch protection rules:

1. Require pull request reviews before merging
2. Require status checks to pass before merging
3. Require branches to be up to date before merging
4. Prevent force pushes on protected branches
5. Restrict who can push to matching branches

## Troubleshooting

### Incorrect Branch

If a Working Claude session discovers it's working on the wrong branch:

1. Stash any uncommitted changes:
   ```bash
   git stash
   ```

2. Switch to the correct branch:
   ```bash
   git checkout sprint/shared-code-250428
   ```

3. Apply stashed changes if appropriate:
   ```bash
   git stash apply
   ```

4. Verify the changes make sense in the new context before committing

### Submodule Issues

If submodules are not tracking the correct branches:

1. Check the current submodule status:
   ```bash
   git submodule status
   ```

2. Update submodule to the correct branch:
   ```bash
   cd Ergon
   git checkout sprint/shared-code-250428
   cd ..
   git add Ergon
   git commit -m "Update Ergon submodule reference"
   ```

## References

For more detailed Git information, consult:

- [Pro Git Book](https://git-scm.com/book/en/v2)
- [GitHub Documentation](https://docs.github.com/en)
- Tekton's CLAUDE.md for project-specific guidelines