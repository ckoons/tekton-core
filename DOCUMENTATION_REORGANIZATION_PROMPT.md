# Claude Code Prompt: Tekton Documentation Reorganization

## Task Overview

I need you to completely reorganize and standardize the documentation for the Tekton project. The goal is to create a more structured, consistent, and maintainable documentation system while preserving valuable existing content.

## Background

Tekton is a modular AI orchestration system with multiple components including:

1. Hermes - Service discovery and message bus
2. Engram - Memory and persistence
3. Rhetor - LLM interaction
4. Ergon - Agent management
5. Telos - Requirements management
6. Athena - Knowledge graph
7. Harmonia - Workflow orchestration
8. Prometheus - Planning system
9. Sophia - Machine learning
10. Codex - Code generation
11. Synthesis - Execution engine
12. Hephaestus - UI framework
13. Terma - Terminal interface

The codebase has accumulated various documentation files over time, but lacks consistency in structure and content. We need to reorganize this into a coherent system.

## The Task

First, review the DOCUMENTATION_REORGANIZATION_INSTRUCTIONS.md file, which provides detailed guidance on:
- The new documentation structure
- Standardization requirements
- Document format standards
- The implementation process
- Special focus areas
- Expected deliverables

Your task is to:

1. Scan all existing .md files in the Tekton repository
2. Create the new directory structure as specified
3. Migrate valuable content from existing documents to the new structure
4. Create standardized document templates for each component
5. Archive historical documents and delete outdated ones
6. Establish a comprehensive cross-reference system
7. Ensure all documentation follows the specified format standards

## Implementation Instructions

1. **Initial Scan**:
   - Use tools to find all .md files in the repository
   - Categorize them by component and topic
   - Identify key content to preserve

2. **Directory Structure Creation**:
   - Create the new directory structure as specified in the instructions
   - Note that the current MetaData directory has been renamed to OldMetaData
   - Create a new MetaData directory according to the specifications
   - Create ComponentDocumentation directories within each component
   - Create the TektonDocumentation directory at the project root

3. **Content Migration**:
   - Extract valuable content from existing documents
   - Reformat and reorganize according to new standards
   - Update references and links to use relative paths from the Tekton directory
   - Create the specified standardized documents for each component
   - Ensure all README.md files retain their icons

4. **Special Requirements**:
   - Create a comprehensive TektonOverview document
   - Organize development sprint documentation by branch/topic
   - Pay special attention to shared utilities documentation
   - Maintain CLAUDE.md files where they are useful

5. **Cleanup and Verification**:
   - Archive historical documents in MetaData/OriginalDocuments
   - Delete outdated and irrelevant files that serve no purpose
   - Verify all new links work
   - Check for consistency across all documents

## Important Guidelines

1. **Document Retention**:
   - Don't completely destroy documents
   - Consider all documents as potential input for new documentation
   - Move legacy docs to an OriginalDocument subdirectory or rename to indicate relevance

2. **Structure Approach**:
   - Use standardized structure as the baseline
   - Allow for flexible structure where needed for specific components

3. **Formatting**:
   - Include narrative intros at the top of documents for human readers
   - Use structured documents and bullet points
   - Include professional code examples and diagrams with explanatory captions
   - Use relative links from the Tekton directory

4. **Special Focus**:
   - Maintain README.md files with icons in all major directories
   - Create a comprehensive TektonOverview document
   - Organize development sprint documentation logically

## Deliverables

1. Complete new documentation structure
2. Standardized README.md files for all components
3. Component-specific documentation
4. Project-level documentation
5. Archive of valuable historical documents
6. Cross-reference system linking related documents
7. Documentation index for easy navigation

## Implementation Notes

- You have full authority to create, modify, and delete documentation files
- Prioritize creating a coherent structure first, then migrate content
- When in doubt about content relevance, preserve it in the archive
- Use clear, consistent naming conventions throughout
- Remember that the goal is to make documentation more accessible and maintainable

Once you've completed the reorganization, provide a summary of:
1. Changes made
2. Files created
3. Files archived
4. Files deleted
5. Recommendations for future documentation maintenance

This is a major organizational effort that will significantly improve the Tekton project's documentation. Take a systematic approach and ensure no valuable information is lost during the transition.