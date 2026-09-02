---
name: git-commiting
description: Create a git commit following Conventional Commits. Use when asked to commit, write a commit message, or stage and commit changes.
---

Format: `<type>[optional scope]: <description>`

## Types

| type       | when                                    |
| ---------- | --------------------------------------- |
| `feat`     | new feature                             |
| `fix`      | bug fix                                 |
| `refactor` | code change that isn't a fix or feature |
| `chore`    | tooling, deps, config, build            |
| `docs`     | documentation only                      |
| `test`     | tests only                              |
| `perf`     | performance improvement                 |
| `ci`       | CI/CD changes                           |
| `revert`   | reverts a prior commit                  |

## Rules

- Description: lowercase, imperative, no period at end
- Scope: optional, noun describing the section — `feat(auth): ...`
- Breaking change: append `!` — `feat!: ...` — or add `BREAKING CHANGE:` footer
- Body: use when the why isn't obvious from the description; blank line after subject
- No emoji. No "this commit". No filler words.
- No `Co-Authored-By` trailer. Ever.
- Prefer multiple smaller commits if the scope is easy to separate; one larger otherwise.
- Push after committing.
