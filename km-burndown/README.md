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

The skill writes a self-contained, dated Markdown handoff to a **new,
non-overwriting filename** in the host's persistent session workspace (or a
requested output directory), then gives the exact `@` path and SHA-256.
Pass both to `/km-implement`, which verifies the file before acting. If no
durable output location is available, paste the inline plan instead:

```text
/km-implement @/absolute/path/to/km-burndown-repo-1234-<unique-id>.md SHA-256: <hash>
```

Review any **Provisional** holds first; `/km-implement` will recheck the
plan's base and volatile PR/run status, and must not invent a missing owner
decision. Open PRs are tracked as in-flight work, not silently reassigned as
new default-branch PR slices; dependent new work waits for a verified
continuation or an updated baseline. `/km-burndown` is a planning skill, not
an implementation, review, deployment or automatic ticket-update command.

## Install

Supported hosts: GitHub Copilot CLI and Claude Code. From the root of the
checkout containing this skill, symlink it without replacing an existing
installation:

```bash
source="$(pwd -P)/km-burndown"
destination="$HOME/.copilot/skills/km-burndown"
if [ ! -f "$source/SKILL.md" ]; then
  printf 'Skill source not found: %s\n' "$source" >&2
  false
elif [ -e "$destination" ] || [ -L "$destination" ]; then
  printf 'Existing installation left unchanged: %s\n' "$destination"
else
  mkdir -p "$HOME/.copilot/skills" && ln -s "$source" "$destination"
fi
```

This works in the usual checkout or a worktree. In Copilot CLI, run
`/skills reload`, then `/skills info km-burndown` to verify discovery. For
Claude Code, copy or symlink `km-burndown/` to
`~/.claude/skills/km-burndown`.
