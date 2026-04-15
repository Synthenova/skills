---
name: test-skill
description: Use when you need to smoke-test a skill folder, confirm the required files exist, or verify a skill is valid before import.
---

# Test Skill

Use this skill as a minimal smoke test for a skill package.

## Workflow

1. Confirm `SKILL.md` exists in the skill folder.
2. Check the frontmatter has `name` and `description`.
3. Verify any referenced files exist.
4. Run the local validator if available.
5. Report the result with the skill path and any missing pieces.
