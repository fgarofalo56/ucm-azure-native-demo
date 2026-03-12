# 🏠 Base Commands

Core session management commands for starting, saving, and ending Claude Code sessions. These commands form the foundation of every working session and ensure project context is properly loaded, preserved, and synchronized with Archon.

## 📋 Commands

| Command | Description | What It Does |
|---------|-------------|--------------|
| [`/base_commands:start`](./start.md) | Initialize session and load context | Executes the full startup protocol: loads `config.yaml`, reads session knowledge, connects to Archon, reviews git history, and outputs a project status briefing |
| [`/base_commands:end`](./end.md) | End session protocol | Saves session state to `SESSION_KNOWLEDGE.md`, updates `DEVELOPMENT_LOG.md`, syncs Archon task statuses, commits uncommitted work, and outputs a session summary |
| [`/base_commands:next`](./next.md) | Get next available task | Queries Archon for `todo` tasks in the current project, ranks by priority, and recommends the best next task to work on |
| [`/base_commands:save`](./save.md) | Save current session context | Writes current session state to `SESSION_KNOWLEDGE.md` and Archon documents without ending the session -- useful for mid-session checkpoints |
| [`/base_commands:status`](./status.md) | Show project and task status | Displays tool inventory counts, Archon task breakdown by status, recent git activity, and current session context |

## 🔄 Typical Session Lifecycle

```
/start  -->  /next  -->  [work]  -->  /save  -->  [more work]  -->  /end
```

1. **`/start`** -- Always run this first. It loads all context so Claude knows what the project is, what was done last session, and what tasks are pending.
2. **`/next`** -- Ask for the next recommended task based on priority and status.
3. **`/save`** -- Periodically save context during long sessions (especially before `/compact` or `/clear`).
4. **`/end`** -- Run this when you are done. It persists everything and prepares the project for the next session.

## 💡 Usage Examples

### Starting a new session

```
> /start

STARTUP COMPLETE - SESSION READY

PROJECT CONFIG:
- Project ID: c12fc8b7-75f0-4bf2-b9cb-a63644faeeb7
- Project Title: Claude Code Tools - Master Project
...
AWAITING YOUR DIRECTION
```

### Saving mid-session

```
> /save

Session context saved to .claude/SESSION_KNOWLEDGE.md
Archon documents updated.
```

## 🔗 Related

- [Dev Tasks Commands](../dev-tasks/) -- Commands for fixing, refactoring, and reviewing code
- [Git Commands](../git/) -- Git and GitHub operations
- [Project Commands](../project/) -- Project scaffolding and wizards
- [PRP Commands](../prp/) -- Product Requirement Prompt workflow
