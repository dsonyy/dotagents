---
name: create_pr
description: Commit all changes, create a pull request, and monitor CI checks
---

# Create Pull Request

You are tasked with committing all changes, creating a pull request, and monitoring CI checks.

## Process:

### 1. Analyze Changes

- Run `git status` to see all modified and untracked files
- Run `git diff --stat` to understand the scope of changes
- Run `git log --oneline -5` to understand commit message conventions

### 2. Create Branch and Commit

- Create a descriptive branch name based on the changes (e.g., `feat/feature-name`, `fix/bug-name`, `refactor/component-name`)
- Run `git checkout -b <branch-name>`
- Stage specific files with `git add <files>` (never use `-A` or `.` blindly)
- Create a commit with a clear message following conventional commits format:
  - `feat(scope): description` for new features
  - `fix(scope): description` for bug fixes
  - `refactor(scope): description` for refactoring
  - `docs(scope): description` for documentation
  - `test(scope): description` for tests
- Include a detailed body explaining what and why
- Add `Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>` at the end

### 3. Push and Create PR

- Push the branch: `git push -u origin <branch-name>`
- Create PR using `gh pr create` with:
  - Clear, concise title (under 70 characters)
  - Summary section with bullet points of key changes
  - Test plan section with checkboxes
  - Footer: `Generated with [Claude Code](https://claude.com/claude-code)`

### 4. Monitor CI Checks

- Wait 60 seconds for checks to start: `sleep 60`
- Poll checks with explicit timeout (max 5 minutes total):
  ```bash
  # Check every 60 seconds, max 5 iterations (5 minutes)
  for i in {1..5}; do
    gh pr checks <pr-number>
    # If all checks done (exit 0) or failed (exit 1), break
    if [ $? -eq 0 ]; then break; fi
    sleep 60
  done
  ```
- After loop, do final check: `gh pr checks <pr-number>`
- If checks still pending after 5 minutes, report status and continue to review step

### 5. Review Comments and Errors

After CI completes, check for review comments:

```bash
gh pr view <pr-number> --json reviews,comments,statusCheckRollup --jq '{
  reviews: [.reviews[] | {author: .author.login, state: .state, body: .body}],
  comments: [.comments[] | {author: .author.login, body: .body}],
  checks: [.statusCheckRollup[] | select(.conclusion != "SUCCESS" and .conclusion != "SKIPPED") | {name: .name, conclusion: .conclusion}]
}'
```

#### Evaluate Review Feedback

When reviewing automated feedback (e.g., from CodeQL, linters):

**Dismiss as overly paranoid if:**
- Suggestions are stylistic preferences without security/correctness impact
- Warnings about theoretical issues that don't apply to the specific context
- Generic advice that doesn't account for the codebase's conventions
- False positives from static analysis tools

**Address if:**
- Actual bugs or logic errors identified
- Real security vulnerabilities pointed out
- Breaking changes to public APIs
- Test failures or type errors
- Violations of documented project conventions

If issues need fixing:
1. Make the necessary changes locally
2. Create a NEW commit for each fix (NEVER amend - one commit per fix)
3. Push normally (never force push)
4. Wait for CI to re-run

### 6. Report Results

Summarize:
- PR URL
- All check statuses (pass/fail/skip)
- Any review comments and your assessment (addressed vs dismissed as paranoid)
- Whether the PR is ready for human review

## Example Output Format

```
PR created: https://github.com/org/repo/pull/123

CI Check Results:
| Check | Status |
|-------|--------|
| main | pass |
| CodeQL | pass |
| lint | pass |

Review Comments:
- [No issues requiring changes]

PR is ready for review.
```

## Important Notes

- **NEVER amend commits** - always create new commits for fixes
- **One commit per fix** - keep fixes separate and traceable
- **NEVER force push** - use regular push only
- Always wait for CI before declaring success
- Don't ignore legitimate failures - fix them
- Be judicious about what's "paranoid" vs what's a real issue
- If unsure about a review comment, ask the user
