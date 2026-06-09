# Runbook: Dependabot Auto-Merge

This repo auto-merges **minor and patch** Dependabot updates via
`.github/workflows/dependabot-auto-merge.yml`. Major updates are ignored in
`.github/dependabot.yml` and left for manual review.

**No GitHub App, PAT, or secret is required.** `main` branch protection no
longer mandates a human review, so the workflow enables auto-merge with the
built-in `GITHUB_TOKEN`. All other gates remain in force.

---

## What still gates a merge

Even with auto-merge, a Dependabot PR only merges when **all** of these pass:

- Required status checks: `Test Backend`, `Test Frontend`,
  `Lint Backend (Python)`, `Lint Frontend (TypeScript)`, `Gitleaks Secret Scan`
- Strict "up to date with `main`" before merge (Dependabot auto-rebases to satisfy this)
- `enforce_admins` remains on

> `Validate Infrastructure` runs on PRs but is **not** required. It fails on
> Dependabot PRs because Azure OIDC federated login has no token in that context
> — expected, and it does not block merge.

## What changed to make this headless

The `required_pull_request_reviews` component was **removed** from `main` branch
protection (it required 1 approval + `require_last_push_approval`). GitHub does
not count `GITHUB_TOKEN` approvals toward required reviews, so keeping that rule
would have forced a separate App/PAT identity (which GitHub only lets you create
via the browser). Dropping the human-review requirement lets the workflow merge
on green CI with zero credentials.

**Trade-off:** human PRs to `main` also no longer require a mandatory approving
review. CI checks still gate everything.

---

## How it behaves

- **Minor / patch update** → workflow enables squash auto-merge; GitHub merges
  once required checks pass and the branch is up to date.
- **Major update** → not produced (ignored in `dependabot.yml`). If one appears
  via a security update, the workflow skips it and emits a notice; merge manually
  after review.
- **Grouped PRs** → `dependabot.yml` batches all minor/patch bumps per ecosystem
  into one monthly PR, so this usually runs on a single PR per ecosystem.

---

## Rollback — restore the human-review requirement

Run this to put the original review rule back (1 approval, dismiss stale,
require last-push approval):

```bash
gh api -X PUT \
  repos/fgarofalo56/ucm-azure-native-demo/branches/main/protection/required_pull_request_reviews \
  -F required_approving_review_count=1 \
  -F dismiss_stale_reviews=true \
  -F require_last_push_approval=true \
  -F require_code_owner_reviews=false
```

Then either delete `.github/workflows/dependabot-auto-merge.yml`, or switch it to
the App-token approach (an App is required because `GITHUB_TOKEN` approvals don't
satisfy required reviews — see git history of this file for that variant).

### Original protection (for reference)

```json
{
  "required_status_checks": {
    "strict": true,
    "checks": ["Test Backend", "Test Frontend", "Lint Backend (Python)",
               "Lint Frontend (TypeScript)", "Gitleaks Secret Scan"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_last_push_approval": true,
    "require_code_owner_reviews": false
  }
}
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
| ------- | ------------ | --- |
| Auto-merge enabled but PR never merges | A required check is failing, or branch is behind `main` | Check the PR's checks; Dependabot auto-rebases, or comment `@dependabot rebase` |
| Workflow doesn't run | PR not authored by `dependabot[bot]` | Expected — the job is guarded to Dependabot only |
| `gh pr merge` permission error | Workflow token lacks write | Confirm the `permissions:` block grants `contents: write` + `pull-requests: write` |
| Major bump opened a PR | A security update bypassed the version-ignore | Review and merge manually |

### Manual merge fallback

```bash
gh pr merge <N> --squash --delete-branch          # once CI is green
gh pr update-branch <N>                            # if BEHIND main (strict mode)
```
