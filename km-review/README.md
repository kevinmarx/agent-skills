# km-review

A portable, multi-lens code reviewer for any git repository, meant to be
copied into a repo and tuned to it.

**Hosts:** Claude Code and GitHub Copilot CLI (any host that can run Python 3.9+
and launch parallel subagents).

## Problem

A single "review this diff" prompt produces confident, inconsistent output.
It reports speculative issues as blockers, misses entire risk areas, reviews
whatever happens to be checked out, and decides "LGTM" with no evidence
behind it.

## Solution

Split the review into phases. Models make the judgment calls. A small stdlib
script owns everything that must be deterministic.

| Phase | What happens | Owner |
|---|---|---|
| 0. Freeze | Require a clean worktree; capture base, merge-base, head SHA, file manifest, diff, and the repo guidance files (AGENTS.md, CONTRIBUTING.md, …) covering the changed paths into `.km-review/<head>/` with a digest | `review.py freeze` |
| 1. Select | Classify paths into **focused** or **panel** depth and compute minimum lenses. For panel depth the agent may add lenses with rationale; an invalid plan falls back to the full roster | `review.py select` / `validate-plan` + agent |
| 2. Lenses | `review.py prompts` writes one dispatch prompt per lens; specialist subagents run them in parallel, read-only, each returning a strict JSON result; one retry for missing or malformed results | subagents + `prompts` / `validate-lens` |
| 3. Synthesis | The generalist verifies every blocker against source, covers unowned seams, deduplicates by root cause, and resolves contradictions | generalist subagent |
| 4. Validate & fence | Enforce two independent confirmations per blocker, anchors on changed lines, follow-up outcomes for every prior blocker, and HEAD unchanged with a clean tree; compute status and decision | `review.py finalize` |
| 5. Hand off | Show `report.md`; in PR mode, post one marked comment only on request | agent |

Follow-up reviews (`freeze --prior`) require HEAD to have advanced from the
prior reviewed head. Prior findings are classified as `fixed`,
`still_present`, `obsolete`, or `not_verifiable` before any new demands are
made.

### Lenses

`security`, `correctness`, `architecture`, `contracts-and-data`,
`performance-concurrency`, `operations`, `behavioral-evidence`,
`docs-and-claims`, and the `generalist` (synthesis).

Every code change gets `correctness` and `behavioral-evidence`, docs get
`docs-and-claims`, and path terms add specialists. **Panel** depth (sensitive
paths, CI/infra, deletions, large changes, or an explicit request) lets the
orchestrator add more lenses with a written rationale.

### Key guarantees

- **Read-only reviewers:** no edits, no builds or tests, no posting.
- **Evidence-gated blockers:** a blocker needs a changed-line anchor, a
  concrete consequence, a required outcome, a verification path, and a
  counter-search.
- **Two-lens confirmation:** support counts only from lenses whose own raw
  result reported the same `root_cause_id`, or from a generalist that verified
  it. An unconfirmed blocker is downgraded and listed, never silently dropped.
- **Incomplete is not pass:** missing or malformed lens output marks the
  review `incomplete`. A moved HEAD marks it `stale`.
- **Readiness is not merge readiness:** CI and human approvals stay separate.

## Install

Claude Code (personal):

```bash
ln -s "$(pwd)/km-review" ~/.claude/skills/km-review
```

Per repository (template use): copy the directory into the repo and customize
it there:

```bash
cp -r km-review <repo>/.claude/skills/km-review     # Claude Code
cp -r km-review <repo>/.agents/skills/km-review     # Copilot CLI
```

Copilot CLI (personal): `ln -s "$(pwd)/km-review" ~/.copilot/skills/km-review`,
then `/skills reload`.

## Usage

```
/km-review                 # review current branch vs its base
/km-review deep            # force panel depth
/km-review the open PR     # include PR title/body; post only if asked
```

Re-review after fixing: run it again. The agent passes the prior
`aggregate.json` with `--prior`.

## Customizing for a repository

| To change… | Edit |
|---|---|
| Which paths trigger which lenses, panel depth rules | `selection-policy.json` |
| Add, remove, or rename a lens | `lens-manifest.json` + `lenses/<id>.md` (and any policy references to the id) |
| Repo-specific concerns, such as "all DB access goes through `repo/`" | the relevant `lenses/*.md`, or a new lens |
| Severity, evidence, and confirmation rules | `policy.md` (affects every lens) |

A lens file needs a **Responsibility**, an **Examine** list, and a **Not
yours** boundary. The shared policy and result contract supply the rest.
Rerun the tests after changing policy or manifest files.

## Validating it in your repo

Before relying on the template in a new repo, spend one review cycle
calibrating it:

1. **Precision:** review two or three recently merged, healthy changes. Expect
   `ready` with zero blockers. A blocker on code your team already trusts
   points to a lens or a policy rule to tune.
2. **Recall:** on a scratch branch, commit a "refactor" that plants two or
   three realistic bugs, such as an inverted guard, a removed validation
   check, or an off-by-one with no material impact, plus one harmless rename
   as a decoy. Expect each material bug as a confirmed blocker, the minor one
   as a suggestion, and nothing on the decoy.
3. **Follow-up:** fix one planted bug, commit, and re-run. Expect that bug as
   `fixed`, the others as `still_present` with the same `root_cause_id`, and
   no rediscovery of unchanged code.
4. **Selection:** check `selection.json` on a few real changes. Add path terms
   for the risks your repo actually has, and remove terms that cause noise.

Never check planted-bug commits into the repo. Run them in a throwaway
worktree.

## Files

```
km-review/
  SKILL.md               agent instructions (phases)
  policy.md              shared judgment rules for every lens
  result-contract.md     JSON shapes and aggregate rules
  lens-manifest.json     lens roster
  selection-policy.json  depth + path-trigger rules
  lenses/*.md            one prompt per lens
  review.py              freeze / select / validate-plan / prompts / validate-lens / finalize
  tests/test_review.py
```

## Tests

```bash
python3 -m unittest discover -s km-review/tests -p 'test_*.py'
```
