---
name: auto_implement
description: End-to-end workflow — research, plan, and implement a feature in an isolated worktree
---

# Auto Implement

Automated end-to-end workflow for simple/linear features: research the codebase, create an implementation plan, and implement it — all in an isolated git worktree.

## Usage

```
/auto_implement <description of the feature or task>
/auto_implement Fix the rate limiter to support per-org limits
/auto_implement Add a new GraphQL mutation for server tagging
```

## Workflow

### Step 0: Create a worktree

Before doing anything, create an isolated worktree for this work:

1. Derive a short branch name from the task description (e.g., `feat/per-org-rate-limits`)
2. Use the EnterWorktree tool to create a worktree on that branch
3. All subsequent work happens inside the worktree

### Step 1: Research

Conduct codebase research to understand the area of code involved.

1. Read any files the user mentioned
2. Spawn parallel sub-agents (codebase-locator, codebase-analyzer, codebase-pattern-finder) to explore the relevant code
3. Wait for all agents to complete
4. Write findings to a research document: `docs/auto-implement/<branch-name>/01-research.md`
5. Present a brief summary to the user

The research document should contain:
- Summary of findings
- Key files and line references
- Existing patterns to follow
- Constraints or gotchas discovered

### Step 2: Plan

Create an implementation plan based on the research.

1. Read the research document from Step 1 fully
2. Analyze the task requirements against the research findings
3. Design an implementation approach with phases
4. Write the plan to `docs/auto-implement/<branch-name>/02-plan.md`
5. **STOP and present the plan to the user for approval**

The plan document should follow the standard plan template:
- Overview and desired end state
- What we're NOT doing (scope boundaries)
- Phased implementation with specific file changes
- Success criteria (automated: `just precommit`, and manual)

**Wait for the user to approve or adjust the plan before proceeding.**

### Step 3: Implement

Execute the approved plan.

1. Read the plan document from Step 2 fully
2. Implement each phase in order
3. After each phase, run `just precommit` to verify
4. Fix any lint/type/test issues before moving to the next phase
5. Update checkboxes in the plan document as phases complete
6. When all phases are done, run a final `just precommit`
7. Write a summary to `docs/auto-implement/<branch-name>/03-summary.md`

### Step 4: Create PR

After all phases are implemented and `just precommit` passes, automatically commit, push, and create a pull request:

1. Run `git status` and `git diff --stat` to review all changes
2. Run `git log --oneline -5` on the base branch to understand commit message conventions
3. Stage all relevant changed files with `git add <files>` (never use `-A` or `.` blindly — exclude secrets, `.env`, large binaries)
4. Create a commit following conventional commits format:
   - `feat(scope): description` / `fix(scope): description` / `refactor(scope): description`
   - Include a detailed body explaining what and why
   - End with `Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>`
5. Push the branch: `git push -u origin <branch-name>`
6. Create the PR using `gh pr create` with:
   - Clear, concise title (under 70 characters)
   - `## Summary` section with bullet points of key changes
   - `## Test plan` section with checkboxes for manual testing
   - Footer: `🤖 Generated with [Claude Code](https://claude.com/claude-code)`
7. Wait ~60 seconds, then poll CI checks (max 5 iterations, 60s apart):
   ```bash
   for i in {1..5}; do
     gh pr checks <pr-number>
     if [ $? -eq 0 ]; then break; fi
     sleep 60
   done
   ```
8. Check for review comments or CI failures:
   - If CI fails or reviewers flag real issues: fix locally, create a NEW commit (never amend), push, and re-check
   - Dismiss purely stylistic or false-positive feedback
9. If CI still pending after 5 minutes, report current status and move on

### Step 5: Report

Present the final status:
- PR URL
- What was implemented (files changed)
- All CI check statuses (pass/fail/pending)
- Any review comments and assessment (addressed vs dismissed)
- What needs manual testing
- Whether the PR is ready for human review

## Important Rules

1. **Always create a worktree first** — never modify the main working tree
2. **Always stop after Step 2** — the user must approve the plan before implementation begins
3. **Pass artifacts forward** — each step reads the markdown produced by the previous step
4. **Keep docs together** — all artifacts go in `docs/auto-implement/<branch-name>/`
5. **Run checks after each phase** — don't accumulate breakage
6. **Always create a PR** — after successful implementation, automatically commit, push, and open a PR
7. **Never amend commits** — always create new commits for fixes; one commit per fix
8. **Never force push** — use regular push only
9. **For complex features** — if during research you discover the task is too complex for a linear workflow, say so and recommend the user run `/research_codebase`, `/create_plan`, and `/implement_plan` separately with more interactive guidance
