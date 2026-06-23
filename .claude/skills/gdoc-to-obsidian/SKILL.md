---
name: gdoc-to-obsidian
description: Migrate a Google Docs export (HTML + images, optionally from a .zip) into a clean Obsidian markdown vault. Produces a flat per-month + per-topic file layout, strips Google export artifacts, maps rich formatting (font color, highlight, bold/italic/strikethrough, code) to Obsidian-supported markdown, and stores all images in one root /assets folder. Use when the user wants to import, migrate, or convert a Google Doc (or a doc exported as "Web Page" .html/.zip) into Obsidian/markdown, especially dated work logs, journals, or multi-tab specs.
---

# Google Doc → Obsidian migration

Converts a Google Docs HTML export into a clean, faithful Obsidian source folder.
The heavy lifting is in `scripts/migrate.py` (deterministic). This file covers the
workflow around it and the one judgment step (topic grouping).

## Workflow

### 1. Get the export (user action — cannot be skipped)
The Drive API / MCP export caps at **10 MB**, so large (image-heavy) docs cannot be
pulled programmatically. The user downloads it from the browser (no size limit):

> Google Doc → **File → Download → Web Page (.html, zipped)**

This bundles `export.html` + an `images/` folder. The Markdown download is worse —
it links images as ephemeral `googleusercontent` URLs instead of bundling them.
Then the user extracts the zip somewhere local.

**Verify completeness before converting:** if the Doc uses **tabs**, confirm all tabs
came through (count `<h1>`/images vs. expected). HTML export sometimes only captures
the active tab; if so, have the user re-export as **.docx** (also all-tabs + images)
and convert with `pandoc -f docx --extract-media` instead.

### 2. Run the migration
```bash
python3 scripts/migrate.py --html <path/to/export.html> --slug <name> --vault <vault-root>
```
- `--slug` = short source name (e.g. `techtree`); becomes the source folder name and the
  image filename prefix.
- `images/` must sit next to the `.html`.
- pandoc is required; the script auto-downloads a static binary to `~/.cache` if it is not
  on PATH (no root needed).

Output (flat) under `<vault>/sources/<slug>/`:
- `YYYY-MM.md` — one per month; dated entries become `## YYYY-MM-DD`.
- `<topic-slug>.md` — one per non-date top-level `#` section.
- `<slug>.md` — index linking months + topics + any preamble.
- Images → `<vault>/assets/<slug>-imageN.png`, referenced `![[<slug>-imageN.png]]`.

### 3. Review + group topics (judgment step)
The script emits **one topic file per top-level `#` heading**, which often over-fragments
(e.g. a "Security" spec split into "CSRF", "reCAPTCHA", "Inicjalizacja"…). After running:
1. List the generated non-date (topic) files.
2. With the user, **merge fragments into coherent themes** (concatenate related files into one,
   fix index links). This needs human judgment about what belongs together — propose a grouping
   and confirm, do not guess silently.
3. Spot-check rendering in Obsidian: colors, highlights, code fences, image embeds.

## What the script guarantees

**Layout:** flat (no nested `daily/`/`topics/` dirs); one shared root `assets/`.

**Formatting → Obsidian:**
- bold/italic/strikethrough → `**`, `*`, `~~`
- font color → `<span style="color:#hex">…</span>` (Obsidian renders inline HTML)
- highlight → `==…==` (yellow) or `<span style="background-color:#hex">…</span>` (colored)
- code → fenced blocks, **plain** (editor syntax-theme rainbow colors are dropped)
- links → clean `[text](url)`; images → `![[<slug>-imageN.png]]`

**Artifacts removed:** `&nbsp;`, phantom empty paragraphs, `google.com/url?q=` redirect
wrappers, leftover Google CSS classes/styles/anchors, pandoc `<!-- -->` list separators.
Near-black greys and default link-blue are treated as plain text, not emphasis.

## Conventions (consistency across imports)
- `sources/` is a **faithful archive** — keep the original `.html` if the user wants a frozen
  copy; cross-source reorganization belongs in a separate `wiki/` layer, not here.
- Always prefix asset filenames with the slug (collision-safe in one shared `/assets`).
- Prefer Obsidian embeds `![[name]]` (resolve by filename anywhere) over relative paths.

## Tuning the script
Edit `scripts/migrate.py` for source-specific cases:
- `MONO` / `DARKBG` — font-families / backgrounds that mark code blocks.
- `LINKBLUE` — color shades treated as default hyperlink color (not emphasis).
- code-detection thresholds and the SQL/JSON fence heuristic (`SQL`, `codeish`).
