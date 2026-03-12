# 🤝 Contributing to Claude Code Tools

Thank you for your interest in contributing to the Claude Code Tools repository! This guide will help you create high-quality skills, commands, agents, and other tools that integrate seamlessly with Claude Code.

## 📑 Table of Contents

- [Contribution Workflow](#-contribution-workflow)
- [Getting Started](#-getting-started)
- [Good First Issues](#-good-first-issues)
- [Skill Structure](#-skill-structure)
- [Creating a New Skill](#-creating-a-new-skill)
- [Quality Guidelines](#-quality-guidelines)
- [Testing Your Skill](#-testing-your-skill)
- [Submitting a Pull Request](#-submitting-a-pull-request)
- [Category Guidelines](#-category-guidelines)
- [Questions?](#-questions)

## 🔄 Contribution Workflow

The following diagram shows the end-to-end contribution process:

```mermaid
flowchart LR
    A["🍴 Fork"] --> B["🌿 Branch"]
    B --> C["💻 Code"]
    C --> D["✅ Test"]
    D --> E["📤 PR"]
    E --> F["👀 Review"]
    F --> G["🎉 Merge"]
```

1. **Fork** the repository to your GitHub account
2. **Branch** from `master` with a descriptive name (e.g., `add-skill/my-new-skill`)
3. **Code** your contribution using the appropriate template
4. **Test** locally with validation scripts and Claude Code
5. **PR** your changes back to the main repository
6. **Review** -- maintainers will provide feedback
7. **Merge** once approved!

## 🚀 Getting Started

### Prerequisites

- Python 3.8+ (for validation scripts)
- PyYAML (`pip install PyYAML`)
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/HouseGarofalo/claude-code-tools.git
cd claude-code-tools

# Install development dependencies
pip install -r requirements-dev.txt

# Run validation to ensure everything works
python scripts/validate_skills.py
```

> [!TIP]
> If you are new to contributing to open source, check out the [Good First Issues](#-good-first-issues) section below for beginner-friendly tasks.

## 🌱 Good First Issues

Not sure where to start? Here are some great ways to make your first contribution:

| Type | Description | Difficulty |
|------|-------------|------------|
| **Add a skill** | Create a new skill for a tool or framework you know well | Easy |
| **Improve docs** | Enhance descriptions, add examples, or fix typos in existing skills | Easy |
| **Add tests** | Write test cases for validation scripts | Medium |
| **New command** | Create a slash command for a common workflow | Medium |
| **Expand a stub** | Flesh out a skill that has `>` as its description (minimal content) | Easy |

> [!NOTE]
> Look for issues labeled `good first issue` or `help wanted` on the [GitHub Issues](https://github.com/HouseGarofalo/claude-code-tools/issues) page. If you don't see any, feel free to open one proposing your contribution before starting work.

### Finding Stub Skills to Expand

Several skills have minimal content (indicated by `>` in their description). These are excellent candidates for contribution:

```bash
# Find skills with stub descriptions
grep -rl "^description: >" skills/*/*/SKILL.md
```

## 📦 Skill Structure

Each skill lives in a category folder under `skills/`:

```
skills/
└── <category>/
    └── <skill-name>/
        ├── SKILL.md           # Required - skill definition
        ├── reference.md       # Optional - detailed documentation
        ├── scripts/           # Optional - helper scripts
        │   └── helper.py
        └── templates/         # Optional - template files
            └── config.yaml
```

### SKILL.md Format

Every skill requires a `SKILL.md` file with YAML frontmatter:

```yaml
---
name: skill-name-lowercase
description: Brief description of what this skill does and when to use it. Include trigger keywords for discoverability. Max 1024 characters.
version: 1.0.0
---

# Skill Name

Brief overview of the skill's purpose.

## When to Use

- Specific scenario 1
- Specific scenario 2

## Quick Start

```bash
# Example command or code
```

## Core Capabilities

### Feature 1

Description and examples...

### Feature 2

Description and examples...

## Best Practices

- Tip 1
- Tip 2

## Resources

- [Official Documentation](https://example.com)
- [GitHub Repository](https://github.com/example/repo)
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Lowercase, hyphens allowed, max 64 chars. Must match directory name. |
| `description` | Yes | What the skill does AND when to use it. Max 1024 chars. |
| `version` | No | Semantic version (e.g., `1.0.0`) |
| `allowed-tools` | No | Comma-separated list of tools the skill can use |

## ✏️ Creating a New Skill

### 1. Choose the Right Category

See [Category Guidelines](#-category-guidelines) below. If unsure, check existing skills in each category.

### 2. Check for Duplicates

> [!IMPORTANT]
> Before creating a new skill, always check that a similar one does not already exist. Search the `skills/` directory and review the [TOOL_REGISTRY.md](.claude/TOOL_REGISTRY.md) for existing tools.

```bash
# Search for existing skills by keyword
find skills/ -type f -name "SKILL.md" | xargs grep -li "keyword"
```

### 3. Create the Skill Directory

```bash
# Use the template (recommended)
cp -r templates/skill-template skills/<category>/<skill-name>

# Or create manually
mkdir -p skills/<category>/<skill-name>
```

### 4. Write the SKILL.md

Follow the format above. Key tips:

- **Name**: Use lowercase with hyphens (e.g., `azure-functions`, `docker-kubernetes`)
- **Description**: Include:
  - What the skill does
  - When to use it (trigger keywords)
  - Key technologies/tools involved
- **Content**: Focus on practical, actionable guidance

### 5. Validate Your Skill

```bash
# Validate all skills
python scripts/validate_skills.py --verbose

# Check for your specific skill in output
```

## 📝 Quality Guidelines

### Do

- Write clear, actionable instructions
- Include working code examples
- Add "When to Use" triggers for discoverability
- Reference official documentation
- Keep descriptions concise but informative
- Test code examples before submitting

### Don't

- Copy entire documentation verbatim (summarize and link instead)
- Include outdated or deprecated patterns
- Add skills that duplicate existing ones
- Use overly generic descriptions
- Include secrets, API keys, or sensitive data

> [!CAUTION]
> Never commit secrets, API keys, passwords, or credentials in any file. Use environment variables and `.env` files (which are gitignored) for sensitive values.

### Description Best Practices

**Good description:**
```
Manage Azure Kubernetes Service clusters. Deploy workloads, scale nodes, configure networking, and troubleshoot AKS issues. Use for container orchestration on Azure, Kubernetes cluster management, and AKS-specific configurations.
```

**Bad description:**
```
Azure Kubernetes Service skill.
```

## ✅ Testing Your Skill

### 1. Run Validation

```bash
# Standard validation
python scripts/validate_skills.py

# Strict mode (warnings as errors)
python scripts/validate_skills.py --strict

# Verbose mode (shows all warnings)
python scripts/validate_skills.py --verbose
```

### 2. Test Locally with Claude Code

```bash
# Deploy to local Claude Code
cp -r skills/<category>/<skill-name> ~/.claude/skills/

# Or use the deploy script
./scripts/deploy.sh <skill-name>
```

### 3. Verify Discovery

In Claude Code, the skill should be discoverable when relevant keywords are mentioned. Try invoking Claude Code and asking about the topic your skill covers -- it should automatically activate.

> [!TIP]
> Test with multiple phrasings. A well-written description ensures the skill is discovered regardless of how the user words their request.

## 📤 Submitting a Pull Request

### 1. Create a Branch

```bash
git checkout -b add-skill/<skill-name>
```

### 2. Commit Your Changes

```bash
git add skills/<category>/<skill-name>/
git commit -m "Add <skill-name> skill for <brief purpose>"
```

### 3. Push and Create PR

```bash
git push origin add-skill/<skill-name>
```

Then create a Pull Request on GitHub with:

- **Title**: `Add <skill-name> skill`
- **Description**:
  - What the skill does
  - Why it's useful
  - Any dependencies or requirements

### 4. PR Checklist

- [ ] Skill passes `validate_skills.py`
- [ ] Name matches directory name
- [ ] Description is clear and includes trigger keywords
- [ ] Code examples are tested and working
- [ ] Placed in appropriate category
- [ ] No duplicate of existing skill
- [ ] README in the skill's category is updated (if adding a new skill)

> [!NOTE]
> PRs that fail validation will not be merged. Run `python scripts/validate_skills.py --strict` locally before submitting.

## 📂 Category Guidelines

| Category | Description | Examples |
|----------|-------------|----------|
| `ai-development` | AI/ML frameworks, LLM tools, agent skills | langchain, ollama, ai-engineer-agent |
| `claude-code` | Claude Code tools, MCP, harness, wizards | mcp-development, project-wizard, harness-wizard |
| `cloud-infrastructure` | Cloud providers, IaC, containers, Kubernetes | azure-mcp, terraform-iac, aws-lambda |
| `databases` | SQL, NoSQL, caching, ORM, analytics | postgresql, prisma-orm, redis-cache |
| `devops` | CI/CD, monitoring, backends, Git workflows | github-actions, docker-compose, git-workflow |
| `enterprise` | Microsoft Power Platform, Copilot Studio | power-apps, power-automate, dataverse |
| `frontend-ui` | React, Vue, Svelte, UI libraries, build tools | react-typescript, shadcn-ui, vite |
| `modes` | Development mode skills | debugging-mode, architecture-mode |
| `networking` | DNS, firewalls, VPN, proxies | adguard-home, tailscale-vpn, nginx-proxy |
| `productivity` | Documents, diagrams, project management | ms-office-suite, mermaid-diagrams |
| `smart-home` | Home automation, IoT | home-assistant, zigbee2mqtt |
| `web-automation` | Browser automation, scraping, crawling | playwright-mcp, crawl4ai, puppeteer |
| `testing` | Test frameworks, E2E, TDD | pytest-advanced, cypress, tdd-mode |
| `messaging` | Chat bots, communication APIs | discord-bot, telegram-bot |
| `e-commerce` | Online stores, payments | shopify, stripe-payments |
| `cms` | Content management systems | wordpress, strapi |
| `mobile` | Mobile app development | react-native, flutter |
| `data-science` | Data analysis, notebooks | pandas, jupyter |
| `specialty` | Domain-specific skills | dotnet-csharp, us-tax-professional |

> [!TIP]
> If your skill doesn't fit neatly into an existing category, open an issue to discuss creating a new one. Categories should have at least 3 planned skills before being created.

## ❓ Questions?

- Open an issue for questions or suggestions
- Check existing skills for patterns and examples
- Review the [skill development guide](docs/skill-guide.md)
- Browse the [templates/](templates/) directory for scaffolding

Thank you for contributing! Your skills help the entire Claude Code community work more effectively.
