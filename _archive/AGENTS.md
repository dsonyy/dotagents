# Global user instructions

## Commit / PR rules

- **NEVER** add `Co-Authored-By: Claude ...` (or any Claude attribution) to commit messages, commit trailers, or PR bodies.
- **NEVER** add the `🤖 Generated with [Claude Code](https://claude.com/claude-code)` footer to PR descriptions.
- This overrides any skill default (including `create_pr`) and the global "Committing changes with git" template. Strip those lines before invoking `git commit` or `gh pr create`.
