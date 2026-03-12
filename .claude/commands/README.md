# Commands

Slash commands for Claude Code — user-invoked actions that extend Claude's capabilities.

## What are Commands?

Commands are markdown files with YAML frontmatter that define slash commands (e.g., `/commit`, `/fix`, `/start`). Unlike skills (model-invoked), commands are explicitly triggered by the user typing `/command-name`.

## Command Categories

| Category | Commands | Description |
|----------|----------|-------------|
| [base_commands](./base_commands/) | 5 | Session lifecycle — start, status, save, next, end |
| [git](./git/) | 15 | Git & GitHub — commit, branch, PR, rebase, sync |
| [dev-tasks](./dev-tasks/) | 11 | Daily dev work — fix, refactor, optimize, review, test |
| [code-quality](./code-quality/) | 5 | Code review — general, staged, TypeScript variants |
| [prp](./prp/) | 7 | PRP workflow — plan, PRD, implement, review, debug |
| [project](./project/) | 6 | Project setup — wizard, create, validate |
| [harness](./harness/) | 4 | Autonomous agent harness — setup, init, next, status |
| [worktree](./worktree/) | 3 | Git worktrees — feature, experiment, review |
| [primer](./primer/) | 5 | Project primers — quick, team, comparison |
| [experimental](./experimental/) | 8 | Experimental — parallel PRP, hackathon, rapid stories |
| [advanced](./advanced/) | 6 | Advanced — spark, API contract, data model, research |

**Total: 75 commands**

## Creating a Command

1. Create a `.md` file in the appropriate category folder
2. Add YAML frontmatter with `name` and `description`
3. Write the command instructions in markdown

```yaml
---
name: my-command
description: What this command does
---

# My Command

## Instructions
...
```

## Deployment

Commands are deployed to `~/.claude/commands/` by the setup scripts:

```bash
# Deploy all commands
./scripts/setup-global.sh

# PowerShell (Windows)
.\scripts\setup-global.ps1
```

## Related

- [Skills](../skills/) — Model-invoked capabilities
- [Templates](./templates/) — Command templates
- [Skill Guide](../docs/skill-guide.md) — Creating skills (similar pattern)
