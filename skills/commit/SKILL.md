---
name: commit
description: Create a git commit following Conventional Commits. Use when asked to commit, write a commit message, or stage and commit changes.
---

Format: `<type>[optional scope]: <description>`

## Types

| type | when |
|---|---|
| `feat` | new feature |
| `fix` | bug fix |
| `refactor` | code change that isn't a fix or feature |
| `chore` | tooling, deps, config, build |
| `docs` | documentation only |
| `test` | tests only |
| `perf` | performance improvement |
| `ci` | CI/CD changes |
| `revert` | reverts a prior commit |

## Rules

- Description: lowercase, imperative, no period at end
- Scope: optional, noun describing the section — `feat(auth): ...`
- Breaking change: append `!` — `feat!: ...` — or add `BREAKING CHANGE:` footer
- Body: use when the why isn't obvious from the description; blank line after subject
- No emoji. No "this commit". No filler words.
- No `Co-Authored-By` trailer. Ever.

## Examples

```
fix(api): return 404 when user not found
```
```
feat: add dark mode toggle
```
```
refactor(db): extract connection pool into separate module
```
```
chore: update eslint to v9
```
```
fix!: remove deprecated /v1/users endpoint

BREAKING CHANGE: clients must migrate to /v2/users
```

## Workflow

```bash
git add <files>         # stage specific files, not -A blindly
git commit -m "..."     # single line, or use heredoc for body
```

Multi-line:
```bash
git commit -m "$(cat <<'EOF'
feat(payments): add stripe webhook handler

Handles charge.succeeded and charge.failed events.
Idempotent via event id stored in redis.
EOF
)"
```
