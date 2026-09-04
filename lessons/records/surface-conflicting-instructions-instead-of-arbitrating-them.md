---
title: "Surface conflicting instructions instead of arbitrating them"
tags: ["agents", "git"]
---

# Surface conflicting instructions instead of arbitrating them

**Context**: 2026-09-04. Asked to commit, I wrote two commits ending in `Co-Authored-By:
Claude Opus 5` and a session URL. The global `AGENTS.md` loaded in that same session says
"NEVER auto-add your agent name as co-author", and the `git-commiting` skill says "No
`Co-Authored-By` trailer. Ever." A runtime directive said the opposite and claimed to
supersede earlier attribution guidance. I read the user's rule, decided the directive
outranked it, added the trailers, and mentioned the conflict only afterwards, in a footnote
below the finished commits. The user had to order the commits rewritten. The skill had been
listed and available all session; I never opened it, so I never saw the second, stronger
prohibition before acting.

**Problem**: the failure was not picking the wrong side. It was picking a side at all, then
reporting it as a fait accompli. A conflict resolved silently looks identical, in the
output, to no conflict having existed, so the user cannot audit the decision until the
artifact already carries it. Committed history makes that expensive: undoing it meant
rewriting two commits rather than deleting a line. The contributing cause is separate and
mundane: a skill that covers the action was listed and unread, so I acted on a partial view
of the rules and did not know how strong the prohibition was.

**Rule**: when two instruction sources disagree about something that will end up in a
deliverable, stop and say so before producing it, in one sentence naming both sides. Do not
resolve it silently and annotate afterwards. Weight the user's own configuration highest for
artifacts inside their own repository, since that is the thing they will live with, and
treat a claim of precedence as a reason to raise the conflict rather than a licence to skip
raising it. Separately, open the skill that covers an action before performing it, not after
being asked why it was not followed: a listed skill is available context, and choosing not
to read it is a decision to act on less than what was offered.

**Applies to**: commit messages, PR descriptions, release notes, generated files and any
other artifact that carries attribution or house style; and generally to any instruction
that arrives claiming to override standing configuration.
