---
name: marketing-autoreason
description: "Use when marketing work needs adversarial iteration instead of a single rewrite: positioning, landing page copy, email hooks, brand voice docs, ad briefs, or launch messaging that should be judged with fresh isolated agents and evidence from prior performance."
---

# Marketing Autoreason

Use this skill when the task is qualitative and you need stronger output than a single "make it better" pass.

## Core Loop

1. Create candidate A from the initial prompt or draft.
2. Assign a fresh critic agent to tear A apart.
3. Assign a separate fresh author agent to write candidate B from the critique only.
4. Assign a fresh synthesizer to produce AB from A and B.
5. Send unchanged A, B, and AB to a blind judge panel.
6. Score the options with Borda count and promote the winner to the next round.
7. Repeat until one candidate survives two rounds without being replaced.

## Rules

- Every role is a fresh isolated agent.
- The critic never talks to the author.
- Judges never see the critic reasoning.
- Do not let later stages see more context than their role requires.
- Treat the loop as adversarial, not collaborative.

## When To Use Evidence

If you have campaign data, audience research, competitor copy, or brand rules, load that into the critique and judging stages.

See [knowledge-layer.md](references/knowledge-layer.md) for the evidence types to include and how to use them.

## Scoring

Use the blind judging rules in [judging-scorecard.md](references/judging-scorecard.md).

## Output

Return the winning candidate, the main reasons it survived, and the evidence used to ground the decision.
