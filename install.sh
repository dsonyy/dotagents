#!/usr/bin/env bash
# Symlinks this repo into ~/.claude and ~/.codex. Idempotent: safe to re-run.
# Real files/dirs already at a destination are moved aside to <dest>.pre-dotfiles.bak.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

link() { # link <repo-relative-src> <abs-dest>
  local src="$REPO/$1" dest="$2"
  if [[ ! -e "$src" ]]; then echo "skip (no src): $1"; return; fi
  mkdir -p "$(dirname "$dest")"
  if [[ -e "$dest" && ! -L "$dest" ]]; then
    mv "$dest" "$dest.pre-dotfiles.bak"
    echo "backed up: $dest -> $dest.pre-dotfiles.bak"
  fi
  ln -sfn "$src" "$dest"
  echo "linked: $dest -> $src"
}

# --- agnostic: global instructions -> both tools ---
link AGENTS.md "$HOME/.claude/CLAUDE.md"
link AGENTS.md "$HOME/.codex/AGENTS.md"

# --- agnostic: skills ---
link skills "$HOME/.claude/skills"                 # Claude: whole dir
mkdir -p "$HOME/.codex/skills"                      # Codex: per-skill (.system is codex-managed)
for d in "$REPO"/skills/*/; do
  [[ -d "$d" ]] || continue
  ln -sfn "$d" "$HOME/.codex/skills/$(basename "$d")"
  echo "linked: $HOME/.codex/skills/$(basename "$d") -> $d"
done

# --- claude-specific ---
link .claude/settings.json   "$HOME/.claude/settings.json"
link .claude/agents          "$HOME/.claude/agents"
link .claude/hooks           "$HOME/.claude/hooks"
link .claude/sounds          "$HOME/.claude/sounds"
link .claude/.caveman-active "$HOME/.claude/.caveman-active"

# --- codex-specific ---
# (none authored yet; add .codex/agents/*.toml, .codex/prompts/*.md here later)

echo "done."
