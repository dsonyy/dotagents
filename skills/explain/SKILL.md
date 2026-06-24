---
name: explain
description: Explain the current state of the conversation, codebase area, or feature with concise structured output
---

# Explain

Explain what's going on — in the current conversation, a feature, or an area of the codebase.

## Usage

```
/explain
/explain what does the audit pipeline do
/explain how does onboarding work
```

When invoked without arguments, explain the current conversation state: what was discussed, what was decided, what's pending.

## Output Format

Always follow this structure:

1. **One sentence TL;DR** — the single most important takeaway
2. **Numbered list of points** — no nesting, no sub-bullets, each point is one standalone fact or datapoint, use 1. 2. 3. ordering
3. Done. No closing summary, no "let me know if you have questions".

## Communication Rules

- No filler, no hedging, no "it's worth noting that"
- Do not translate code to English line by line
- Do not reference file paths, function names, or code symbols unless the user explicitly asks for code-level detail
- Describe what happens from the user's perspective: what they see, what they trigger, what changes
- Focus on data: what goes in, what gets transformed, what comes out, and why
- Keep it top-to-bottom: cause before effect, input before output, trigger before result
- Each bullet should be independently useful — if a bullet only makes sense with the one above it, merge them
- Prefer concrete values and examples over abstract descriptions
