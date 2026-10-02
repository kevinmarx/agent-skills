# KM Implement

`km-implement` turns an approved plan into concrete todos and the smallest
complete, independently mergeable PRs, using Copilot fleet/subagents and
autopilot. It is a prompt-driven skill: no scripts, dependencies, or settings
changes are needed.

**No prerequisite PRs.** Every PR targets the discovered default branch and
works without sibling changes, safely merging in any order. Dependencies between
todos stay inside one PR. Shared new infrastructure or coupled behavior belongs
in the same complete slice; one larger coherent PR beats fake independence.

## Install for Copilot CLI

Personal skills are discovered in `~/.copilot/skills/` or `~/.agents/skills/`.
From this repository's usual checkout, create a non-overwriting symlink:

```bash
source="$HOME/workspace/km/skills/km-implement"
destination="$HOME/.copilot/skills/km-implement"
if [ ! -f "$source/SKILL.md" ]; then
  printf 'Skill source not found: %s\n' "$source" >&2
  false
elif [ -e "$destination" ] || [ -L "$destination" ]; then
  printf 'Existing install left unchanged: %s\n' "$destination"
else
  mkdir -p "$HOME/.copilot/skills" && ln -s "$source" "$destination"
fi
```

If the source lives in this worktree, set `source` to
`"$HOME/workspace/km/skills-worktrees/km-implement/km-implement"` instead.
Repository-scoped discovery also supports `.github/skills/` and `.agents/skills/`.
Alternatively, `copilot skill add DIRECTORY` registers a custom source;
`copilot skill list` inspects installed skills. The CLI also provides skill
remove/enable/disable commands. `~/.claude/skills/` is for Claude Code personal
installation, not Copilot personal discovery.

In Copilot, refresh and verify:

```text
/skills reload
/skills info km-implement
```

## Use

In the target repository, enable autopilot yourself if it is not already active,
then optionally use fleet:

```text
/autopilot
/fleet /km-implement @docs/plan.md
```

Without fleet, invoke `/km-implement @docs/plan.md`; native subagents can still
be used. Inputs may also be a local path, pasted plan, or accessible URL.
Shift+Tab cycles session modes. The skill cannot execute slash commands to
toggle its parent session, and will not launch a nested CLI to enable autopilot.

For a programmatic run with tool/path/URL permissions already granted:

```bash
copilot --autopilot --fleet -p 'Use /km-implement to implement @docs/plan.md'
```

Non-interactive runs need permissions granted before starting; otherwise needed
actions may be blocked. **Separate trusted-user choice:** the following permits
all tools, paths, and URLs. Use only if you explicitly accept that broad access;
the skill never grants it automatically.

```bash
copilot --allow-all --autopilot --fleet -p 'Use /km-implement to implement @docs/plan.md'
```

Autopilot defaults to five automatic continuations. Users can choose
`--max-autopilot-continues` and `--max-ai-credits` budgets. The skill preserves
existing limits and checkpoints on completion, stops, limits, or blockers;
hands-free uninterrupted completion is not guaranteed.

## Execution and handoff

The coordinator checks plan identity, approved scope, repository instructions,
existing work and author history; maps requirements to independent slices; and
uses isolated `users/kemarx/<plan>-<slice>` worktrees fetched from origin's default
branch. One writer owns each worktree. Each slice includes its complete behavior,
tests, docs, migrations, contracts, and rollout needs, with focused validation.

A compact ledger lives in the host session workspace, not source or commits.
The handoff maps requirements to PRs and distinguishes implementation, publication,
validation, CI, review/approval, and merging. Resume in the existing session
by referring to the plan and checkpoint; live heads/status are rechecked first.
Material unknowns block affected work rather than inventing scope. Creating plan
PRs does not authorize merging or deploying; CI/review driving is opt-in.

## References

- [Adding Copilot CLI skills](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)
- [Autopilot](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/autopilot)
- [Fleet](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/fleet)
