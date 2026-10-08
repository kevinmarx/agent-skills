# Architect and Design

`km-architect-and-design` creates an evidence-backed technical design before
implementation. Use it for RFCs, ADRs, architecture proposals, migrations,
new systems, or substantial refactors.

## Problem

Design proposals often rely on assumed behavior, omit important failure paths,
or leave implementers guessing about compatibility and acceptance criteria.

## Solution

The skill inspects repository guidance and relevant implementation, compares
credible alternatives, and recommends one approach. It produces a design with
explicit requirements, trade-offs, interfaces, risks, validation criteria, and
open questions. When explicitly requested, it can file a verified
implementation ticket as the handoff to `/km-burndown`.

## Supported hosts

Claude Code and GitHub Copilot CLI. This is a prompt-only skill: it has no
scripts, dependencies, company-specific services, or required integrations.
It uses the tools and permissions available in the current host.

## Install

From the root of this checkout, create a non-overwriting symlink. For Copilot
CLI, use `~/.copilot/skills`; for Claude Code, set `skills_dir` to
`"$HOME/.claude/skills"` instead:

```bash
skills_dir="$HOME/.copilot/skills"
source="$(pwd)/km-architect-and-design"
destination="$skills_dir/km-architect-and-design"
if [ ! -f "$source/SKILL.md" ]; then
  printf 'Skill source not found: %s\n' "$source" >&2
  false
elif [ -e "$destination" ] || [ -L "$destination" ]; then
  printf 'Existing install left unchanged: %s\n' "$destination"
else
  mkdir -p "$skills_dir" && ln -s "$source" "$destination"
fi
```

Keep the checkout in place while using the symlink. In Copilot CLI, run
`/skills reload`, then `/skills info km-architect-and-design` to confirm
discovery. In Claude Code, start a new session after installation.

## Use

Invoke the skill with the intended outcome and any constraints:

```text
/km-architect-and-design Design a cache invalidation strategy for this repository. Write the proposal to docs/design/cache-invalidation.md.
```

For discussion without a file, ask for the design in chat instead. To file an
issue, explicitly authorize that action and name the target repository. A
design request alone does not publish anything:

```text
/km-architect-and-design Design a cache invalidation strategy and draft an implementation issue; do not file it.
/km-architect-and-design File the approved cache invalidation design as an implementation issue in owner/repo.
```

The skill follows the repository's design-document convention. When none
exists, a requested file goes under `docs/design/<kebab-case-topic>.md`.
It searches for an existing issue before publishing, follows the repository's
issue template, and verifies the created issue by reading it back. A ticket
must contain its goal, decisions and their approval status, acceptance
criteria, non-goals, and remaining holds; a local-only design path is not a
usable link. If the user authorized filing but not the unresolved decisions,
the ticket stays **Proposed/Draft** and is not an approved implementation plan.
If creation times out, the skill checks recent repository issues; an
unresolved outcome stops rather than risking a duplicate. A failed or
unverified publication returns the draft and blocker, not a burndown command.

The verified ticket URL becomes the next input; these commands are separate
user-initiated steps, not actions the architect skill performs:

```text
/km-burndown https://github.com/owner/repo/issues/1234
/km-implement @/absolute/path/to/plan.md Verify this file's SHA-256 is <hash> before acting; stop if it differs.
```

Burndown checks current code, PRs, and execution evidence before assigning
standalone PR slices. The architect ticket captures stable requirements, not
a second live task list or a required sequence of dependent PRs.

## How it works

1. Establish the outcome, constraints, success criteria, and non-goals.
2. Gather evidence from relevant source, tests, documentation, and current
   primary external sources when needed.
3. Evaluate alternatives, compatibility, data flows, and failure paths.
4. Author the design and record material decisions.
5. Review and refine the recommendation against the evidence.
6. Validate the document and report unresolved questions or blocked checks.
7. Only when authorized, publish and read back an implementation ticket; hand
   its URL to the user for `/km-burndown`.

The output includes the design, recommendation, supporting evidence,
validation results, and material uncertainties. The skill does not implement
the design, change production code or configuration, or create commits,
branches, pull requests, issues, or remote changes without explicit
authorization. Creating an issue does not authorize merging or deployment.

## References

- [Adding Copilot CLI skills](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
