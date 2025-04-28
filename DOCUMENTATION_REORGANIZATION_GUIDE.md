# Documentation Reorganization Guide

This guide provides instructions for running the Claude Code session to reorganize Tekton's documentation.

## Preparation Checklist

Before starting the Claude Code session, ensure you have:

- [x] Created detailed instructions (DOCUMENTATION_REORGANIZATION_INSTRUCTIONS.md)
- [x] Prepared the Claude Code prompt (DOCUMENTATION_REORGANIZATION_PROMPT.md)
- [x] Outlined an execution plan (DOCUMENTATION_REORGANIZATION_EXECUTION_PLAN.md)
- [x] Renamed the current MetaData directory to OldMetaData
- [ ] Backed up all .md files (as mentioned in your prior response)

## Running the Claude Code Session

1. **Start a New Claude Code Session**
   - Launch Claude Code with sufficient tokens (recommend the largest available model)
   - This task requires extensive file access, creation, and modification

2. **Provide the Prompt**
   - Copy the contents of DOCUMENTATION_REORGANIZATION_PROMPT.md as your initial prompt
   - Ensure Claude confirms understanding of the task before proceeding

3. **Task Monitoring**
   - The reorganization is extensive and will require multiple steps
   - Claude will need to scan files, create directories, and migrate content
   - Break the task into manageable chunks when necessary
   - Request progress updates at regular intervals

4. **Addressing Ambiguities**
   - If Claude encounters ambiguous situations (e.g., uncertain content classification)
   - Ask Claude to explain the ambiguity and propose solutions
   - Provide clear direction on how to proceed

## Expected Workflow

Claude should follow this general workflow:

1. **Initial Scanning**
   - Claude will scan all .md files in the repository
   - Catalog existing documentation
   - Develop a migration plan

2. **Structure Creation**
   - Create the new directory structure
   - Set up standardized templates
   - Establish cross-reference patterns

3. **Content Migration**
   - Process each component's documentation systematically
   - Move valuable content to new locations
   - Update formatting and links

4. **Cleanup and Validation**
   - Archive historical documents
   - Delete outdated files
   - Verify new structure integrity

5. **Reporting**
   - Provide a summary of changes
   - Highlight new documentation structure
   - Recommend future maintenance approaches

## Important Considerations

1. **Processing Capacity**
   - This task involves processing many files
   - Claude may need to work in batches
   - Consider breaking the task by component if needed

2. **Documentation Quality**
   - Focus on structure first, then content quality
   - Standardization is a key goal
   - Preserve valuable content even if reformatting is required

3. **Decision Authority**
   - Claude has authority to create, modify, and delete documentation
   - For significant content decisions, Claude should explain reasoning
   - When uncertain about content value, Claude should preserve it

## Post-Session Tasks

After Claude completes the reorganization:

1. **Manual Verification**
   - Review key documentation files manually
   - Ensure README files display icons correctly
   - Check cross-component links

2. **Documentation Testing**
   - Test navigation through the documentation
   - Verify important information is accessible
   - Check for any broken links

3. **Feedback Integration**
   - Note any issues or improvements
   - Create tasks for addressing documentation gaps
   - Consider a follow-up session for refinements

## Session Initialization

To start the Claude Code session, use the following command:

```bash
claude -m claude-3-haiku-20240307 --file DOCUMENTATION_REORGANIZATION_PROMPT.md
```

For optimal results with larger context handling:

```bash
claude -m claude-3-opus-20240229 --file DOCUMENTATION_REORGANIZATION_PROMPT.md
```

This guide provides the framework for conducting the documentation reorganization using Claude Code. The process is designed to be systematic, thorough, and maintainable, resulting in a significantly improved documentation structure for the Tekton project.