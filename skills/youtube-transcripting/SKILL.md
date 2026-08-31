---
name: youtube-transcript
description: Fetch the transcript of a YouTube video from its URL or ID, then optionally summarize it or produce a TL;DR. Use when the user gives a YouTube link (youtube.com/watch, youtu.be, /shorts/, /live/) or video ID and asks for a transcript, summary, TL;DR, key points, chapters, or quotes.
---

# YouTube Transcript & Summary

Pull the captions a YouTube video already has (creator-uploaded or auto-generated)
and turn them into a transcript, summary, or TL;DR. No speech-to-text is run — this
reads existing caption tracks, which is why it is fast and free.

## When to use

The user pastes a YouTube link or ID and wants any of: full transcript, TL;DR,
summary, key takeaways, chapter breakdown, quotes, or answers about the content.

## Workflow

1. **Get the transcript** by running the script:

   ```bash
   python3 scripts/fetch_transcript.py "<url-or-id>"
   ```

   Useful flags:
   - `--with-timestamps` — prefix each line with `[mm:ss]` (use when the user wants
     timestamped notes, chapters, or jump links).
   - `--json` — structured `{start, text}` segments for programmatic use.
   - `--lang es` — preferred caption language code (default `en`).

   The script tries `yt-dlp` first (robust; auto-downloads a local copy on first run
   if not installed), then falls back to a zero-dependency watch-page scrape.

2. **Do what the user asked** with the returned text:
   - *Transcript*: return it (offer to save to a file for long videos).
   - *TL;DR*: 2–4 sentence gist.
   - *Summary*: short intro + bulleted key points; add `[mm:ss]` anchors if you ran
     `--with-timestamps`.
   - *Chapters*: group segments into topic sections with start timestamps.

   For long transcripts, summarize directly from the script output — do not re-read
   the whole thing back to the user unless they asked for the raw transcript.

## Failure modes

- `ERROR: no transcript found` — the video has captions disabled, or YouTube
  token-gated the request. Mention captions may be off; the user can paste another
  link.
- First run downloads `yt-dlp` (~30 MB) to `~/.cache/youtube-transcript-skill/`.
  This needs network access and is a one-time cost.
- Private/age-restricted/region-locked videos may not be reachable.

## How it works (background)

YouTube videos carry caption tracks reachable via an internal `timedtext` URL found
in the watch page's `ytInitialPlayerResponse`. Since ~2024 those URLs are gated by a
signature/"pot" token and return empty without it. `yt-dlp` solves that challenge
(via the android-vr player client), which is why it is the primary strategy here.
Web tools like tactiq.io do the same thing server-side (plus rotating proxies).
