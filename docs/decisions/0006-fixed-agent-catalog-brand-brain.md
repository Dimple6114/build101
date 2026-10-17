# 0006: Fixed agent catalog personalized by a Brand Brain

- Date: 2026-10-17
- Status: accepted

## Context

The idea says onboarding "creates a set of specialized agents". The options were letting an LLM generate agents and their prompts per business, a fixed catalog, or a hybrid.

## Decision

A **fixed catalog** ([architecture/agents.md](../architecture/agents.md)) (Asset Analyst, Brand Strategist, Content Strategist, Copywriter, Art Director, Feedback Classifier) coordinated by one orchestrator. Onboarding "creates the team" by producing a versioned **Brand Brain** (structured JSON) that every agent reads. From the owner's point of view, the team is theirs.

## Consequences

- Predictable, testable, and cheap to improve: one prompt fix helps every business.
- Personalization quality depends on the Brand Brain, so onboarding inputs and the Brand Strategist get extra care.
- Business-specific agents (e.g. a "menu agent" for restaurants) can be added later as optional catalog entries activated by category (hybrid), without changing the architecture.
