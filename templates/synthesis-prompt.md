You are analyzing a user's Claude Code session history to build a behavioral profile. The profile should capture how this person works — their communication style, quality standards, review instincts, and recurring preferences.

## Input

You will receive a batch of user messages extracted from Claude Code sessions across various projects. These are the user's actual words — typed messages and voice transcriptions.

## Task

Analyze the messages and produce a structured behavioral profile in markdown. Focus on patterns that repeat across sessions, not one-off requests.

### Sections to produce:

**Communication Style** — How they communicate: brevity vs detail, formality, use of voice, delegation comfort, question-asking patterns.

**Quality Standards** — What they care about in code quality: testing, type safety, accessibility, performance, design system compliance, visual verification, etc. Rank by how often each appears.

**Review Instincts** — How they approach code review: what they flag, their tone, use of conventional comments, approval patterns, common nitpicks.

**Work Patterns** — How they structure work: commit style, PR preferences, planning approach, tool usage patterns, sequential vs parallel task execution.

**Domain Expertise** — Areas of deep knowledge vs areas where they're learning. What domains they work in most.

**Invariants** — Hard rules they always enforce. Things they never allow. Non-negotiable quality gates.

**Delegation Style** — How they delegate to AI: level of autonomy granted, verification expectations, when they want to be asked vs when they want you to just do it.

### Rules:
- Only include patterns supported by multiple messages (not one-off requests)
- Mark low-confidence observations with [low confidence]
- Be specific — "prefers small commits" is better than "has git preferences"
- Quote representative messages when they illustrate a pattern clearly
- If a pattern appears in 5+ messages, treat it as high confidence
- Focus on actionable insights that would change how an AI assistant behaves
