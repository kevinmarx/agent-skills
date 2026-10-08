---
name: km-burndown
version: 1.0.0
description: Turn a GitHub issue or accessible ticket into an evidence-backed, agent-ready burndown plan for /km-implement. Use when asked what remains on a ticket or to prepare a ticket for implementation; do not implement it.
---

# KM Burndown

Produce a current, self-contained plan that can be passed as
`/km-implement @<plan-file>`. This is **read-only investigation** except for
writing the handoff plan. Do not change source, queue builds, update tickets,
create PRs, or invoke `/km-implement` on the user's behalf.

## 1. Resolve the ticket and finish line

- Accept a GitHub issue URL, `owner/repo#number`, or `#number` when the current
  repository unambiguously identifies the owner and repo. For another ticket
  system, use an available authorized connector and record its stable URL and
  revision; if the ticket or repository cannot be resolved, ask rather than
  assuming. Use the correct GitHub host/account for the repository.
- Read the issue's current body, checklist, comments and timeline. Separate
  approved acceptance criteria and non-goals from draft designs, suggestions
  and unapproved scope. Record any named owner decision still needed; never
  interpret a proposed architecture or an unchecked box as an approval.
- Identify the target repository, its remote default branch, and the commit
  inspected. Read its root and relevant scoped instructions before proposing
  edits or validation. Resolve the requesting author from the task, not
  `@me`; check their relevant in-flight branches and PRs before assigning work
  already in progress. Respect repository access restrictions and do not read
  `.env` files.

## 2. Establish what is actually done

- Follow issue links and cross-references to dependencies, merged and open PRs,
  source commits, and related work. Search by relevant behavior and paths as
  well as the issue number; a PR may implement part of the work without closing
  the issue. Verify current PR state and whether merged code is on the
  inspected default branch.
- Read the current implementation and its existing tests/docs where needed to
  substantiate the call path and identify the remaining gap. Reuse existing
  owners; do not prescribe a second runner, publisher, store, or other
  lifecycle without source-backed need.
- When acceptance requires execution, deployment or durable readback, inspect
  the corresponding live run/artifact/configuration through authorized tools.
  Distinguish source-level coverage, a queued/green setup, an uploaded artifact,
  an executed case, confirmed cleanup, and verified publication/readback.
  Report the last observed build and its actual failure or success, not an
  earlier green run as if it proved the current implementation. Never print
  credentials, customer content or raw sensitive evidence in the plan.
- Mark each acceptance criterion **proven**, **partially implemented**,
  **not started**, **blocked**, or **unverified**. Give a source or run link
  for load-bearing claims; say what exact evidence is still missing. A
  completed PR is not proof of deployment or of a live acceptance criterion.

## 3. Convert gaps into executable work

Create bounded tasks, each with an objective, existing owner/path or named PR,
specific work, observable done condition, required evidence, and a stop/block
condition. Cover the complete path from inputs through effects, failure and
cleanup to publication and consumption when those belong to the finish line.
Distinguish code tasks from operator actions, design approvals and final
acceptance runs. Record unfinished open-PR work separately from new slices:
name the PR, its remaining acceptance criteria and its current owner. Do not
assign that work to a new default-branch slice. It can be continued in the
existing PR only when its owner authorizes that work and `/km-implement` can
verify an eligible same-task branch/worktree to resume; otherwise mark it as
an external hold. If a new slice needs the unmerged work, resolve whether to
fold the work into that existing PR or wait for its merge and re-snapshot the
baseline. Neither duplicating the PR nor publishing a dependent PR is a fix.

Group implementation tasks into the smallest **standalone vertical PR slices**
that `/km-implement` can build from the default branch. Each remaining
implementation requirement belongs to exactly one owner: an existing
in-flight PR or a new slice, never both. Dependencies between new code tasks
stay **inside** a slice; a planned PR must not require another planned PR to
merge first. Coalesce coupled producer/reader contracts or shared new
machinery when they cannot independently build, work and merge in any order.
Existing merged baseline work may be a prerequisite; an open PR is not.
Independent research may proceed in parallel even when the eventual code
belongs to one slice. One writing agent owns each slice/worktree. Do not
present a list of cross-PR dependencies as an agent-ready implementation plan.
If acceptance is already fully proven, return no implementation slices rather
than manufacturing work.

Preserve the ticket's non-goals and applicable repository contracts. Name
material unknowns, evidence gaps and owner decisions as holds on the
dependent work, not as permission to invent architecture or claim that
acceptance passed. Do not manufacture test commands, file paths, time estimates,
or a universal score when the evidence does not support them. Record relevant
rollout/rollback constraints and focused validation or live-proof commands
when source-backed; otherwise identify the specific command/proof gap.

## 4. Write the `/km-implement` handoff

When the host provides a persistent session workspace, write a Markdown plan
there using a unique name such as
`km-burndown-<repo>-<ticket>-<UTC>-<unique-id>.md`; otherwise use a
user-supplied output directory and a unique filename. Never overwrite an
existing plan, even at a user-supplied path; ask for a directory or a new
filename instead. If no durable location exists, return the entire plan inline
so it can be pasted into `/km-implement`. Do not silently add a plan file to
source control. Record the plan's as-of time, ticket URL and updated time,
target repository and default-branch SHA. Hash the finalized file's exact
bytes with SHA-256 and include that hash in the handoff invocation:
`/km-implement @<absolute-path> SHA-256: <hash>`. This is a plain-language
integrity instruction, not a command-line option. A mutable issue URL alone
is not a plan version; `/km-implement` must recheck volatile facts before
acting.

Use this structure, adapting the tables to the ticket:

```markdown
# Burndown: <ticket and title>
**Status:** Ready for implementation | Provisional — <named holds>
**As of:** <UTC> · **Ticket:** <URL, updated at> · **Repo/base:** <owner/repo, default branch @ SHA>

## Approved goal, acceptance criteria, non-goals and rollback constraints
## Verified baseline and progress
| Criterion | State | Evidence | Remaining proof |
| --- | --- | --- | --- |

## Implementation slices (independent PRs)
### S1 — <complete vertical outcome>
**Owns:** <criterion IDs and paths/PR, or "to investigate">
**Agent tasks (internal order/dependencies):** <bounded actions>
**Done when:** <implementation, negative paths, exact acceptance evidence>
**Independence:** <why it works without other planned PRs>

## In-flight PR work (not new slices)
## Operator actions, owner decisions and blockers
## Acceptance matrix and final readback
## Handoff to /km-implement
```

If multiple independent slices cannot be justified, give `/km-implement` one
coherent slice with internal tasks; do not force a PR per task. Mark a plan
**provisional** if scope-changing decisions or unsupported acceptance claims
remain. State which authorized work can proceed and which must wait for a named
decision. End with the exact existing `@<absolute-path>` to pass to
`/km-implement` and its expected SHA-256, or say to paste the inline plan.
Do not claim approval, successful live runs, or hands-free execution merely
by producing the plan.
