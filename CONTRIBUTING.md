# Contributing to Steer

I built Steer to enforce deterministic truth on probabilistic systems. I prioritize technical density over marketing polish. If you want to contribute, you must adhere to the "Anti-Slop" standard.

## The Anti-Slop Standard

1. Zero Emojis: Do not use emojis in code, logs, or pull request descriptions.
2. No Em Dashes: Use commas, parentheses, or periods.
3. First-Person Singular: Use "I" for logic descriptions, not "We."
4. Clinical Naming: Judges must be named after technical pathologies (e.g., SlopJudge, AmbiguityJudge). Avoid marketing terms like "SmartFilter" or "SafetyGuard."
5. High Entropy: Avoid "helpful assistant" personas in tests or examples. Use specific, high-stakes technical contexts.

## Pull Request Process

1. Every new Reality Lock must include a corresponding test case in the `tests/` or `examples/` directory.
2. Ensure no external API dependencies are added to core judges. Steer is local-first.
3. Refactor logic to use high-performance serialization (Pydantic v2).
