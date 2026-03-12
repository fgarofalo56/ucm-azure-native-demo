---
name: save
description: Save current session context
---

Save current session context to memory files.

Update these files with what we've done so far this session:
- .claude/SESSION_KNOWLEDGE.md - Any new state info or discoveries
- .claude/DEVELOPMENT_LOG.md - Activity since last save
- .claude/FAILED_ATTEMPTS.md - Any new failures
- .claude/TOOL_REGISTRY.md - Any new tools

Also update Archon:
- Task statuses if changed
- "Session Context & Memory" document

Confirm what was saved. This is a checkpoint, not end of session.
