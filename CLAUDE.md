# CLAUDE.md

## What is this repo?

A collection of agent skills — small, self-contained instructions for
Claude Code and GitHub Copilot CLI. Check each skill's README for supported
hosts; Copilot-specific modes are not available in Claude Code.

## Repo structure

```
<skill-name>/
  SKILL.md       # Required. Skill definition (frontmatter + agent instructions)
  README.md      # Required. Human-readable docs (install, usage, how it works)
  set-title.sh   # Scripts/code the skill uses
```

## Rules

- Every skill directory **must** have both a `SKILL.md` and a `README.md`
- `SKILL.md` is for the agent (frontmatter with name/version/description, then usage instructions)
- `README.md` is for humans (problem, solution, install steps, how it works)
- Skills should be minimal — one script, one purpose
- Scripts should output minimal text (the agent parses the output)
- Prompt-driven skills may include one standard-library validator/renderer when
  deterministic output contracts cannot be enforced reliably in prose alone;
  keep semantic extraction in the skill and cover the validator with fixtures.
- The top-level `README.md` should list all available skills

## Adding a new skill

1. Create a directory named after the skill
2. Add `SKILL.md` with frontmatter (`name`, `version`, `description`) and agent-facing instructions
3. Add `README.md` with human-facing documentation, including supported hosts
4. Add any scripts the skill needs
5. Update the top-level `README.md` to list the new skill

## Install

GitHub Copilot CLI discovers personal skills under `~/.copilot/skills/` or
`~/.agents/skills/`. Symlink a skill directory there without overwriting an
existing installation, then use `/skills reload` and `/skills info <skill-name>`.
Autopilot and fleet are session modes, not capabilities a skill can silently
enable or grant permissions for.

Copy any skill directory into `~/.claude/skills/`:

```bash
cp -r <skill-name> ~/.claude/skills/<skill-name>
```

Claude Code auto-discovers skills in that directory.
