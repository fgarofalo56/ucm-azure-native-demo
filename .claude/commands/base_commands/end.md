---
name: end
description: End session protocol
---

Execute the END OF SESSION PROTOCOL defined in CLAUDE.md.

1. Update Memory Files:
   - SESSION_KNOWLEDGE.md with current state and discoveries
   - DEVELOPMENT_LOG.md with all activity from this session
   - FAILED_ATTEMPTS.md with any new failures and analysis
   - TOOL_REGISTRY.md with any tools created or modified

2. Update Archon:
   - Update task statuses
   - Update "Session Context & Memory" document

3. Update config.yaml:
   - Update the `updated_at` timestamp

4. Git Operations:
   - Stage and commit any uncommitted changes
   - Do NOT push unless explicitly requested

5. Provide Session Summary:
   - Session duration
   - Work completed
   - Work in progress
   - New discoveries
   - Failed attempts logged
   - Tools created/modified
   - Recommended next session focus

Confirm all memory files and Archon have been updated.
