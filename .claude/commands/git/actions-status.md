---
name: actions-status
description: Check GitHub Actions status
---

Check GitHub Actions workflow status using the gh CLI.

## Arguments

$ARGUMENTS

Parse arguments:
- No args: Show recent workflow runs
- "list": List all workflows
- "run <workflow>": Trigger a workflow
- "view <run-id>": View specific run details
- "logs <run-id>": View run logs
- "watch": Watch current run in real-time
- "failed": Show only failed runs

## View Workflow Runs

### Recent Runs
```bash
# List recent runs for current branch
gh run list

# List runs for specific branch
gh run list --branch main

# List runs for specific workflow
gh run list --workflow "CI"

# Show only failed runs
gh run list --status failure

# Limit results
gh run list --limit 5
```

### View Run Details
```bash
# View specific run
gh run view <run-id>

# View with job details
gh run view <run-id> --verbose

# View in browser
gh run view <run-id> --web

# View current branch's latest run
gh run view
```

### View Logs
```bash
# View logs for a run
gh run view <run-id> --log

# View logs for specific job
gh run view <run-id> --log --job <job-id>

# View failed logs only
gh run view <run-id> --log-failed
```

### Watch Run
```bash
# Watch run in real-time
gh run watch <run-id>

# Watch and exit when done
gh run watch
```

## List Workflows

```bash
# List all workflows
gh workflow list

# View workflow file
gh workflow view <workflow-name>
```

## Trigger Workflows

```bash
# Run workflow on current branch
gh workflow run <workflow-name>

# Run on specific branch
gh workflow run <workflow-name> --ref <branch>

# Run with inputs
gh workflow run <workflow-name> -f input1=value1 -f input2=value2
```

## PR Checks

```bash
# View checks on current PR
gh pr checks

# View checks for specific PR
gh pr checks <pr-number>

# Wait for checks to complete
gh pr checks --watch

# Fail if any checks fail
gh pr checks --fail-on-failure
```

## Common Workflows Status

Show status for typical workflows:
- CI/Build
- Tests
- Linting
- Deploy
- Security Scan

## Interpreting Status

| Status | Meaning |
|--------|---------|
| `queued` | Waiting to run |
| `in_progress` | Currently running |
| `success` | Completed successfully |
| `failure` | One or more jobs failed |
| `cancelled` | Manually cancelled |
| `skipped` | Workflow skipped (condition not met) |

## Troubleshooting Failed Runs

When a run fails:

1. **View the failure:**
   ```bash
   gh run view <run-id> --log-failed
   ```

2. **Common issues:**
   - Test failures: Check test output
   - Lint errors: Check linting rules
   - Build errors: Check dependencies
   - Timeout: Check for infinite loops or slow tests
   - Secrets: Verify secrets are configured

3. **Re-run failed jobs:**
   ```bash
   gh run rerun <run-id> --failed
   ```

4. **Re-run entire workflow:**
   ```bash
   gh run rerun <run-id>
   ```

## Workflow Debugging

```bash
# Download run artifacts
gh run download <run-id>

# Download specific artifact
gh run download <run-id> -n <artifact-name>

# View run JSON for debugging
gh run view <run-id> --json jobs,conclusion,status
```

## Output

Show:
1. Recent workflow runs with status
2. Current branch CI status
3. Any failing jobs with summary
4. Time elapsed/remaining
5. Links to view in browser
