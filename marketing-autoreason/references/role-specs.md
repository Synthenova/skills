# Role Specs

Use fresh isolated agents for every role and round. Do not reuse a critic, author, synthesizer, or judge from a prior stage.

## Candidate A Author

Give this role the raw task plus any draft the user already has.

Output:

- One candidate only
- No self-critique
- No comparison against hypothetical alternatives

## Critic

Give this role only:

- The task goal
- Candidate A
- Any approved knowledge-layer evidence

Do not give the critic access to future stage prompts.

Output:

- What is generic or interchangeable
- What a competitor could claim word for word
- What is unsupported by evidence
- What is weak about the hook, payoff, or differentiation

## Candidate B Author

Give this role only:

- The task goal
- The critic output
- Any approved brand constraints needed to stay on brief

Do not show candidate A.

Output:

- A rewrite from scratch that responds to the critique
- No side-by-side commentary
- No references to candidate A

## Synthesizer

Give this role only:

- The task goal
- Unchanged candidate A
- Unchanged candidate B

Do not show the critic notes.

Output:

- One synthesis candidate that selectively combines the strongest parts of A and B
- A short note on what strengths it tried to preserve

## Blind Judges

Give each judge only:

- The task goal
- Candidate A
- Candidate B
- Candidate AB
- Any approved knowledge-layer evidence used for evaluation

Do not reveal which option was the incumbent, rewrite, or synthesis.

Output:

- Independent ranking of all three candidates
- Brief rationale tied to specificity, distinctiveness, payoff, voice, and evidence
- No awareness of other judges' reasoning

## Round Advancement

- Aggregate the judge rankings with Borda count.
- Promote the winner to the next round as the new candidate A.
- Stop after candidate A survives two rounds without replacement.
