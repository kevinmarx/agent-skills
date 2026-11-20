#!/usr/bin/env bash
# Set the title of the current tmux pane to describe current work
# Usage: bash set-title.sh "short task description"

title="${1:?Usage: set-title.sh \"short title\"}"

if [ -n "$TMUX" ] && [ -n "$TMUX_PANE" ]; then
    # Per-pane title (shown in the pane border), so splits keep their own titles
    tmux select-pane -t "$TMUX_PANE" -T "$title"
else
    # Not in tmux: fall back to the terminal title escape sequence
    printf '\033]2;%s\033\\' "$title"
fi

echo "Title set: $title"
