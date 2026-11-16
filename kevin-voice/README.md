# kevin-voice

A prompt-only skill that teaches the agent to write in Kevin's voice.

## Problem

Agent-drafted emails, messages and docs come out longer, stiffer and more
padded than Kevin would write them. They add deadlines, recaps and asks he
didn't request, and every draft needs the same edits.

## Solution

`SKILL.md` is a voice guide built from about 40 of Kevin's sent emails and
from how he edited Claude's drafts. It covers greetings, sign-offs, length,
punctuation, tone by audience, common situations with real examples, what he
cuts from drafts, and a long-form target for posts and docs. It also lists
where the evidence is thin so the agent asks instead of guessing.

## Supported hosts

- Claude Code
- GitHub Copilot CLI

## Install

### Claude Code

```bash
cp -r kevin-voice ~/.claude/skills/kevin-voice
```

### GitHub Copilot CLI

```bash
ln -s "$(pwd)/kevin-voice" ~/.copilot/skills/kevin-voice
```

Then run `/skills reload` and `/skills info kevin-voice`.

## How it works

The skill triggers when the agent drafts or edits text on Kevin's behalf. To
make it reliable, add this line to your global agent instructions
(`~/.claude/CLAUDE.md` or `AGENTS.md`):

```
When writing anything on my behalf (emails, messages, posts, docs), use the kevin-voice skill first and follow it.
```

The "Paste-ready brief" section at the top of `SKILL.md` can also be pasted
into any chat tool that doesn't support skills.
