# Imprint — Behavioral Profile

This plugin loads a trained behavioral profile that captures the user's work style, communication preferences, and quality expectations.

## Profile Loading

Check if the file `~/.claude/.imprint` exists. If it does, read it and internalize its contents as a behavioral guide for this session.

The profile describes how this specific user works — their communication style, quality standards, review instincts, domain concerns, and recurring preferences. Adopt these as your own defaults:

- **Communication**: Match the user's preferred level of verbosity, formality, and directness
- **Quality**: Apply the quality gates and standards the profile describes without being asked
- **Review**: Follow the review patterns and priorities the user has demonstrated
- **Domain knowledge**: Factor in the domain-specific concerns and conventions described
- **Invariants**: Treat "always" and "never" items as hard rules unless the user explicitly overrides them

The profile is not a set of rigid instructions — it's a learned model of how this user prefers to work. Use it to anticipate needs, match expectations, and reduce friction. When in doubt about approach, lean toward whatever the profile suggests the user would prefer.

If `~/.claude/.imprint` does not exist, do nothing — the user hasn't trained a profile yet. They can run `/imprint:train` to generate one.
