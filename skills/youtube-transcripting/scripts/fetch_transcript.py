#!/usr/bin/env python3
"""Fetch a YouTube video's transcript using existing captions (no speech-to-text).

This works like lightweight web tools (e.g. tactiq.io): it does NOT transcribe
audio. It pulls the caption track YouTube already has (creator-uploaded or
auto-generated) and converts it to plain text.

Two strategies, tried in order:
  1. yt-dlp  -- robust; solves YouTube's "pot"/signature token challenge that
                otherwise makes the raw caption URLs return empty. Auto-downloaded
                to a local cache if not already on PATH.
  2. stdlib  -- scrape the watch page for caption track URLs. Zero deps, but fails
                on videos/IPs that YouTube gates behind a token (returns empty).

Usage:
    python3 fetch_transcript.py <youtube-url-or-id> [--lang en] [--json] [--with-timestamps]
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
import urllib.error

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
CACHE_DIR = os.path.expanduser("~/.cache/youtube-transcript-skill")
YTDLP_URL = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_linux"


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def extract_video_id(s: str) -> str:
    s = s.strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", s):
        return s
    m = re.search(r"(?:v=|/embed/|youtu\.be/|/v/|/shorts/|/live/)([A-Za-z0-9_-]{11})", s)
    if m:
        return m.group(1)
    raise ValueError(f"Could not extract a video ID from: {s}")


def json3_to_segments(data: dict) -> list:
    segs = []
    for ev in data.get("events", []):
        text = "".join(s.get("utf8", "") for s in ev.get("segs", [])).replace("\n", " ").strip()
        if text:
            segs.append({"start": ev.get("tStartMs", 0) / 1000.0, "text": text})
    return segs


def fmt_ts(sec: float) -> str:
    h, m, s = int(sec // 3600), int((sec % 3600) // 60), int(sec % 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


# --------------------------------------------------------------------------- #
# strategy 1: yt-dlp
# --------------------------------------------------------------------------- #
def find_or_get_ytdlp():
    from shutil import which
    exe = which("yt-dlp")
    if exe:
        return exe
    cached = os.path.join(CACHE_DIR, "yt-dlp")
    if os.path.exists(cached) and os.access(cached, os.X_OK):
        return cached
    os.makedirs(CACHE_DIR, exist_ok=True)
    print("Downloading yt-dlp (one time)...", file=sys.stderr)
    req = urllib.request.Request(YTDLP_URL, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r, open(cached, "wb") as f:
        f.write(r.read())
    os.chmod(cached, 0o755)
    return cached


def try_ytdlp(video_id: str, lang: str):
    exe = find_or_get_ytdlp()
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "sub")
        # request both manual and auto subs; prefer the exact lang, accept variants.
        cmd = [
            exe, "--skip-download", "--write-subs", "--write-auto-subs",
            "--sub-langs", f"{lang},{lang}-orig,{lang}.*",
            "--sub-format", "json3", "-o", f"{out}.%(ext)s",
            f"https://www.youtube.com/watch?v={video_id}",
        ]
        subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        files = glob.glob(f"{out}*.json3")
        if not files:
            return None
        # prefer a manual track (e.g. sub.en.json3) over auto (sub.en-orig.json3).
        files.sort(key=lambda p: ("orig" in p or "auto" in p, len(p)))
        with open(files[0], encoding="utf-8") as f:
            return json3_to_segments(json.load(f))


# --------------------------------------------------------------------------- #
# strategy 2: stdlib watch-page scrape
# --------------------------------------------------------------------------- #
def try_stdlib(video_id: str, lang: str):
    req = urllib.request.Request(
        f"https://www.youtube.com/watch?v={video_id}&hl=en",
        headers={"User-Agent": UA, "Accept-Language": "en-US,en"},
    )
    html = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
    m = re.search(r"ytInitialPlayerResponse\s*=\s*(\{.+?\})\s*;\s*(?:var|</script>)", html)
    if not m:
        return None
    pr = json.loads(m.group(1))
    tracks = (pr.get("captions", {})
              .get("playerCaptionsTracklistRenderer", {})
              .get("captionTracks"))
    if not tracks:
        return None
    track = next((t for t in tracks if t.get("languageCode") == lang), None) \
        or next((t for t in tracks if t.get("languageCode", "").startswith(lang)), tracks[0])
    url = track["baseUrl"] + "&fmt=json3"
    body = urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": UA}), timeout=20).read()
    if not body:  # token-gated -> empty
        return None
    return json3_to_segments(json.loads(body))


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--lang", default="en", help="preferred language code (default en)")
    ap.add_argument("--json", action="store_true", help="output JSON segments")
    ap.add_argument("--with-timestamps", action="store_true", help="prefix [mm:ss]")
    args = ap.parse_args()

    try:
        vid = extract_video_id(args.url)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    segs, err = None, None
    for name, fn in (("yt-dlp", try_ytdlp), ("stdlib", try_stdlib)):
        try:
            segs = fn(vid, args.lang)
            if segs:
                break
        except Exception as e:  # noqa: BLE001 - try next strategy
            err = f"{name}: {type(e).__name__}: {e}"

    if not segs:
        print(f"ERROR: no transcript found. Last error: {err or 'no captions on this video'}",
              file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps({"video_id": vid, "segments": segs}, ensure_ascii=False, indent=2))
    elif args.with_timestamps:
        for s in segs:
            print(f"[{fmt_ts(s['start'])}] {s['text']}")
    else:
        print(" ".join(s["text"] for s in segs))


if __name__ == "__main__":
    main()
