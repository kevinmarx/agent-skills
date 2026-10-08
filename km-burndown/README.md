# KM Burndown

`/km-burndown <ticket>` turns a ticket's current state into a sourced task
plan for `/km-implement`. It checks the issue and its decisions, current
default-branch code, related merged/open PRs, and live execution or artifact
evidence when the ticket requires it. It reports what is implemented separately
from what has actually passed acceptance.

The output groups remaining code into independently mergeable, complete PR
slices, with concrete tasks and **internal** dependencies for agents. It also
names operator actions, owner decisions, proof gaps and the final acceptance
runs. If tasks need each other's new code, they stay in the same slice rather
than becoming prerequisite PRs. A draft ticket produces a provisional plan;
it does not grant approval to implement unresolved decisions.

## Use

From the target repository, supply a GitHub issue URL, `owner/repo#number`, or
an unambiguous `#number`:

```text
/km-burndown https://github.com/owner/repo/issues/1234
/km-burndown #1234
```

Enterprise GitHub issues use their own host. Other ticket systems need an
accessible connector and a stable ticket reference. Build/pipeline evidence is
queried only when it matters to the issue's acceptance criteria; this skill
does not queue a run or alter the ticket.

The skill writes a self-contained, dated Markdown handoff in the host's
persistent session workspace (or a requested output path), then gives the
exact `@` path and file hash. If no durable output location is available, it
prints the plan to paste into `/km-implement`:

```text
/km-implement @/absolute/path/to/km-burndown-repo-1234.md
```

Review any **Provisional** holds first; `/km-implement` will recheck the
plan's base and volatile PR/run status, and must not invent a missing owner
decision. `/km-burndown` is a planning skill, not an implementation, review,
deployment or automatic ticket-update command.

## Install

Supported hosts: GitHub Copilot CLI and Claude Code. In this repo's checkout,
symlink the skill directory without replacing an existing installation:

```bash
source="$HOME/workspace/km/claude-code-skills/km-burndown"
destination="$HOME/.copilot/skills/km-burndown"
if [ -e "$destination" ] || [ -L "$destination" ]; then
  printf 'Existing installation left unchanged: %s\n' "$destination"
else
  mkdir -p "$HOME/.copilot/skills" && ln -s "$source" "$destination"
fi
```

Use the actual worktree source path if the skill has not yet landed in the
usual checkout. In Copilot CLI, run `/skills reload` and
`/skills info km-burndown` after installing. For Claude Code, copy or symlink
`km-burndown/` to `~/.claude/skills/km-burndown`.
