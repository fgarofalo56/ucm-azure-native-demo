---
name: start
description: Initialize session and load context
---

Execute the mandatory startup checklist before we begin.

Run all 7 steps of the STARTUP PROTOCOL defined in CLAUDE.md:

1. Load or Create Project Configuration - Read .claude/config.yaml
2. Load Project Context Files - Read all .claude/*.md files
3. Load Archon Project Context - Query the master project, tasks, and documents
4. Review Git History & Existing Tools - Check what changed
5. Check References & Credentials - Verify docs and .env files
6. Review Tool Registry - Inventory all tools by status
7. Project Status Briefing - Output the full briefing with recommended next steps

Do not skip any steps. Actually execute the commands, don't just describe them.

End with the PROJECT STATUS BRIEFING and RECOMMENDED NEXT STEPS so I can choose what to work on.
