# Lens: docs-and-claims

## Responsibility

Repository documentation, runbooks, agent instructions (AGENTS.md, CLAUDE.md,
skills, prompts), PR title/body claims, and approved scope.

## Examine

- Accuracy: do changed docs match the code at this head? Do commands, flags,
  paths, and config keys actually exist?
- Staleness: does the code change make existing docs wrong? Search for the
  old names.
- PR claims: compare the title/body (if supplied) to the full diff. Flag
  overclaims (claims the diff does not deliver) and silent scope (significant
  changes the PR does not mention).
- Approved scope: if an issue, design, or acceptance criteria are referenced,
  does the change deliver them, and only them?
- Agent/model instructions: clear purpose, unambiguous, no contradictions with
  other instructions the same agent loads, no wording that grants unintended
  authority. Give exact replacement text for confusing passages.

Prose is reviewed for meaning, not linted for wording. An overclaim is fixed
by correcting the claim. That is a complete closure unless the claim was a
supported contract.

## Not yours

Code behavior beyond checking that docs describe it correctly.
