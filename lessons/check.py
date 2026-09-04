#!/usr/bin/env python3
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQUIRED_SECTIONS = ("Context", "Rule", "Applies to")
INDEX_BASE_BYTES = 4096
INDEX_BYTES_PER_RECORD = 160
MAX_TAGS = 4

ROW = re.compile(r"^- \[(.+?)\]\(records/([a-z0-9-]+)\.md\) \| (.+)$")
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TAG_BLOCK = re.compile(r"^## Tags\b.*?^```\n(.*?)^```", re.M | re.S)
FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
TITLE = re.compile(r'^title:\s*"(.*)"$', re.M)
TAGS = re.compile(r"^tags:\s*\[(.*)\]$", re.M)
HEADING = re.compile(r"^# (.+)$", re.M)

errors = []


def fail(message):
    errors.append(message)


def as_set(tags):
    return ", ".join(sorted(tags))


def read_vocabulary():
    block = TAG_BLOCK.search((ROOT / "index.md").read_text())
    if not block:
        fail("index.md: no fenced tag block under a '## Tags' heading")
        return set()
    return {line.strip() for line in block.group(1).splitlines() if line.strip()}


def read_front_matter(source, where):
    block = FRONT_MATTER.match(source)
    if not block:
        fail(f"{where}: missing front matter")
        return None, None
    title = TITLE.search(block.group(1))
    tags = TAGS.search(block.group(1))
    if not title:
        fail(f"{where}: front matter has no quoted title")
    if not tags:
        fail(f"{where}: front matter has no tags array")
    if not title or not tags:
        return None, None
    parsed = [t.strip().strip('"') for t in tags.group(1).split(",") if t.strip()]
    return title.group(1), parsed


vocabulary = read_vocabulary()
index_source = (ROOT / "index.md").read_text()
catalog = index_source.split("## Catalog", 1)
if len(catalog) != 2:
    fail("index.md: no '## Catalog' heading")

for section in REQUIRED_SECTIONS:
    if len(catalog) == 2 and f"**{section}**" in catalog[1]:
        fail(f"index.md: catalog contains record prose ('**{section}**'). It holds rows only.")

rows = {}
for number, line in enumerate(index_source.splitlines(), start=1):
    if not line.startswith("- ["):
        continue
    row = ROW.match(line)
    if not row:
        fail(f"index.md:{number}: malformed row. Expected: - [Title](records/slug.md) | tag, tag")
        continue
    title, slug, tag_text = row.groups()
    if slug in rows:
        fail(f"index.md:{number}: duplicate row for '{slug}'")
    rows[slug] = (title, [t.strip() for t in tag_text.split(",")], number)

files = sorted(p.name for p in (ROOT / "records").glob("*.md"))
seen_titles = {}

for name in files:
    slug = name[:-3]
    where = f"records/{name}"
    if not SLUG.match(slug):
        fail(f"{where}: filename is not kebab-case")

    source = (ROOT / "records" / name).read_text()
    title, tags = read_front_matter(source, where)
    if title is None:
        continue

    if not 1 <= len(tags) <= MAX_TAGS:
        fail(f"{where}: has {len(tags)} tags, expected 1 to {MAX_TAGS}")
    for tag in tags:
        if tag not in vocabulary:
            fail(f"{where}: tag '{tag}' is not in the index tag list")

    if title in seen_titles:
        fail(f"{where}: duplicate title, already used by {seen_titles[title]}")
    seen_titles[title] = where

    heading = HEADING.search(source)
    if not heading or heading.group(1) != title:
        found = heading.group(1) if heading else "none"
        fail(f"{where}: H1 '{found}' does not match front matter title '{title}'")

    for section in REQUIRED_SECTIONS:
        if f"**{section}**:" not in source:
            fail(f"{where}: missing '**{section}**:' section")

    if slug not in rows:
        fail(f"{where}: has no row in index.md")
        continue

    row_title, row_tags, number = rows[slug]
    if row_title != title:
        fail(f"index.md:{number}: row title '{row_title}' does not match record title '{title}'")
    if as_set(row_tags) != as_set(tags):
        fail(f"index.md:{number}: row tags [{as_set(row_tags)}] do not match record tags [{as_set(tags)}]")

for slug, (_, _, number) in rows.items():
    if f"{slug}.md" not in files:
        fail(f"index.md:{number}: row points at records/{slug}.md, which does not exist")

budget = INDEX_BASE_BYTES + INDEX_BYTES_PER_RECORD * len(files)
size = len(index_source.encode())
if size > budget:
    fail(
        f"index.md is {size} bytes, over its {budget} byte budget for {len(files)} records. "
        "Shorten rows; do not raise the budget to fit prose."
    )

if errors:
    print(f"lessons: {len(errors)} problem{'s' if len(errors) > 1 else ''}\n", file=sys.stderr)
    for error in errors:
        print(f"  {error}", file=sys.stderr)
    sys.exit(1)

print(f"lessons: ok. {len(files)} record{'' if len(files) == 1 else 's'}, index {size}/{budget} bytes.")
