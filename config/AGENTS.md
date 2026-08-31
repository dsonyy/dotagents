# Global AGENTS.md

## Never

- Never expose cross-tenant data or skip tenant/organization scoping.
- Never edit generated files by hand.
- NEVER use the em dash "—". Use plain dash "-" instead.
- NEVER auto-add your agent name as co-author, when writing commit messages, PRs and other deliverables
- Never hard-code user-facing strings or design-system colors.

## Writing

- Don't over-weight development cost in technical decisions. Do not underestimate AI coding speed nowadays.
- Prefer using "Sentence case text" over "Upper Case Text" in documents, UI elements unless otherwise noted.
- Avoid fillers, hedging, no "it's worth noting that"
- When asked for explanation, do not translate code to English line by line.
  Describe it like the human is not seeing the code but listening and build the mental model.
- Prefer top-to-bottom communication: cause before effect, input before output, trigger before result

## Coding philosophy

- When doing bug fixes, always start with reproducing the bug in an E2E setting as closely aligned with how an end user would experience it as possible.
  This makes sure you find the real problem so your fix will actually solve it.
- When end-to-end testing a product, be picky about the UI you see and be obsessed with pixel perfection.
  If something clearly looks off, even if it is not directly related to what you are doing, try to get it fixed along the way.
- Simplicity first. Minimum code that solves the problem. Nothing speculative.
  - No features beyond what was asked.
  - No abstractions for single-use code.
  - No "flexibility" or "configurability" that wasn't requested.
  - No error handling for impossible scenarios.
  - If you write 200 lines and it could be 50, rewrite it.
  - No comments. Code is the spec. Only annotate genuinely non-obvious logic — never _what_ the code does.
- Before any engineering decisions or implementation:
  - Don't assume. Don't hide confusion. Surface tradeoffs.
  - State your assumptions explicitly. If uncertain, ask.
  - If multiple interpretations exist, present them - don't pick silently.
  - If a simpler approach exists, say so. Push back when warranted.
  - If something is unclear, stop. Name what's confusing. Ask.
  - Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.
  - No Laziness: Find root causes. No temporary fixes. Senior developer standards.

## Workflow orchestration

- Spec-first: Enter plan mode for non-trivial tasks (3+ steps or architectural decisions).
- Subagent strategy: Use subagents liberally to keep main context clean. Offload research and parallel analysis. One task per subagent.
- Verification: Run tests, check build, suggest user verification. Ask: "Would a staff engineer approve this?"
- Elegance: For non-trivial changes, pause and ask "is there a more elegant way?" Skip for simple fixes.
- Autonomous bug fixing: When given a bug report, just fix it. Point at logs/errors, then resolve. Zero hand-holding.
