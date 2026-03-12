---
name: repo-clone
description: Clone git repositories
---

Clone a GitHub repository using the gh CLI.

## Arguments

$ARGUMENTS

Parse arguments:
- "<owner/repo>": Clone by owner/repo
- "<url>": Clone by URL
- "list": List your repositories
- "fork <owner/repo>": Fork and clone

## Clone Repository

### Standard Clone
```bash
# By owner/repo
gh repo clone <owner>/<repo>

# By URL
gh repo clone https://github.com/<owner>/<repo>

# To specific directory
gh repo clone <owner>/<repo> <directory>
```

### Clone with Depth
```bash
# Shallow clone (faster, less history)
gh repo clone <owner>/<repo> -- --depth 1

# Recent history only
gh repo clone <owner>/<repo> -- --depth 10
```

### Fork and Clone
```bash
# Fork to your account and clone
gh repo fork <owner>/<repo> --clone

# Fork without cloning
gh repo fork <owner>/<repo>

# Fork to an organization
gh repo fork <owner>/<repo> --org <org-name>
```

## Post-Clone Setup

After cloning, suggest:

```bash
# Enter directory
cd <repo>

# Check remotes
git remote -v

# Install dependencies (detect package manager)
npm install     # if package.json
pip install -r requirements.txt  # if requirements.txt
bundle install  # if Gemfile
```

### For Forks: Setup Upstream
```bash
# Add upstream remote
git remote add upstream https://github.com/<original-owner>/<repo>.git

# Verify remotes
git remote -v
# origin    (your fork)
# upstream  (original repo)

# Sync fork with upstream
git fetch upstream
git merge upstream/main
```

## List Repositories

```bash
# Your repos
gh repo list

# Org repos
gh repo list <org-name>

# With filters
gh repo list --public
gh repo list --private
gh repo list --source  # non-forks only
gh repo list --fork    # forks only

# Search repos
gh repo list --json name,description --jq '.[] | select(.name | contains("keyword"))'
```

## View Repository Info

```bash
# View in browser
gh repo view <owner>/<repo> --web

# View details in terminal
gh repo view <owner>/<repo>
```

## Create Repository

```bash
# Create new repo from current directory
gh repo create <name> --public --source=. --push

# Create empty repo
gh repo create <name> --public

# Create private repo
gh repo create <name> --private

# Create with description
gh repo create <name> --public --description "My awesome project"

# Create from template
gh repo create <name> --template <owner>/<template-repo>
```

## Clone Recommendations

Based on the repo:
1. **Has package.json**: Suggest `npm install` or `yarn`
2. **Has requirements.txt**: Suggest `pip install -r requirements.txt`
3. **Has Makefile**: Suggest `make` or `make setup`
4. **Has .env.example**: Suggest `cp .env.example .env`
5. **Has docker-compose.yml**: Suggest `docker-compose up`

## Output

After cloning:
1. Repository name and description
2. Directory created
3. Detected language/framework
4. Suggested next steps (install deps, setup env)
5. Important files (README, CONTRIBUTING)
