#!/usr/bin/env python3
"""Migrate a Google-Docs HTML export (.html + images/) into Obsidian markdown.

Output (flat) under <vault>/sources/<slug>/ :
  - YYYY-MM.md            one file per month, dated entries demoted to ## YYYY-MM-DD
  - <topic-slug>.md       one file per non-date top-level (#) section
  - <slug>.md             index linking months + topics + the rolling preamble
Images -> <vault>/assets/  prefixed <slug>-  , referenced as ![[<slug>-imageN.png]].

Preserves: bold/italic/strikethrough, font color (<span style="color">), highlight
(== for yellow, <span style="background-color"> for colored), links, images.
Fences code; strips Google export artifacts (nbsp, redirect links, phantom paragraphs).

Usage:
  migrate.py --html path/to/export.html --slug techtree --vault /path/to/vault
"""
import argparse, html as H, os, re, shutil, subprocess, sys, urllib.parse, urllib.request, tarfile

PANDOC_VER = "3.1.11.1"

def ensure_pandoc():
    p = shutil.which("pandoc")
    if p:
        return p
    cache = os.path.expanduser("~/.cache/gdoc-obsidian")
    binp = f"{cache}/pandoc-{PANDOC_VER}/bin/pandoc"
    if os.path.exists(binp):
        return binp
    os.makedirs(cache, exist_ok=True)
    url = f"https://github.com/jgm/pandoc/releases/download/{PANDOC_VER}/pandoc-{PANDOC_VER}-linux-amd64.tar.gz"
    tgz = f"{cache}/pandoc.tgz"
    print(f"downloading pandoc {PANDOC_VER} (static, no root)...")
    urllib.request.urlretrieve(url, tgz)
    with tarfile.open(tgz) as t:
        t.extractall(cache)
    return binp

# ----------------------------------------------------------------------------
LINKBLUE = {'#1155cc', '#0000ee', '#0000ff', '#1264a3', '#0563c1', '#1a0dab', '#1155ff'}
MONO = ('courier', 'roboto mono', 'consolas', 'source code', 'mono')
DARKBG = {'#282c34', '#21252b', '#2f2f2f', '#1e1e1e', '#1d1f21', '#272822', '#011627', '#222222'}

def build_classmap(style):
    props = {}
    for m in re.finditer(r'\.(c\d+)\s*\{([^}]*)\}', style):
        b = m.group(2)
        fg = re.search(r'(?:^|;)\s*color:\s*(#[0-9a-fA-F]{6})', b)
        bg = re.search(r'background-color:\s*(#[0-9a-fA-F]{6})', b)
        fw = re.search(r'font-weight:\s*(\d+|bold)', b)
        fs = re.search(r'font-style:\s*italic', b)
        ff = re.search(r'font-family:\s*"?([^;"]+)', b)
        td = re.search(r'text-decoration:\s*([^;]+)', b)
        bold = bool(fw and (fw.group(1) == 'bold' or (fw.group(1).isdigit() and int(fw.group(1)) >= 600)))
        props[m.group(1)] = dict(
            fg=fg.group(1).lower() if fg else None, bg=bg.group(1).lower() if bg else None,
            bold=bold, ital=bool(fs), ff=(ff.group(1).lower() if ff else ''),
            strike=('line-through' in (td.group(1) if td else '')))
    return props

def preprocess(src):
    style = re.search(r'<style[^>]*>(.*?)</style>', src, re.S)
    props = build_classmap(style.group(1) if style else '')

    def cls_props(cls):
        fg = bg = None; bold = ital = strike = mono = False
        for c in cls.split():
            p = props.get(c)
            if not p: continue
            if p['fg']: fg = p['fg']
            if p['bg']: bg = p['bg']
            bold |= p['bold']; ital |= p['ital']; strike |= p['strike']
            if any(k in p['ff'] for k in MONO): mono = True
        return fg, bg, bold, ital, strike, mono

    h = src[src.find('<body'):]
    h = re.sub(r'</?body[^>]*>', '', h)
    h = re.sub(r'<style[^>]*>.*?</style>', '', h, flags=re.S)
    h = re.sub(r'\sstyle="[^"]*"', '', h)
    h = re.sub(r'\s(?:id|name)="[^"]*"', '', h)
    h = re.sub(r'<a(?![^>]*href)[^>]*>(.*?)</a>', r'\1', h, flags=re.S)

    def plain(frag):
        t = re.sub(r'<br\s*/?>', '\n', frag)
        return H.unescape(re.sub(r'<[^>]+>', '', t))

    def p_is_code(pb):
        spans = re.findall(r'<span class="([^"]*)">(.*?)</span>', pb, re.S)
        if not spans: return False
        mono_len = tot = 0; dark = False
        for cls, inner in spans:
            _, bg, _, _, _, mono = cls_props(cls)
            txt = plain(inner); tot += len(txt)
            if mono: mono_len += len(txt)
            if bg in DARKBG: dark = True
        return tot > 0 and (dark or mono_len / tot >= 0.8)

    tokens = []; last = 0
    for m in re.finditer(r'<p class="[^"]*">.*?</p>', h, re.S):
        if m.start() > last: tokens.append(('raw', h[last:m.start()]))
        tokens.append(('p', m.group(0))); last = m.end()
    tokens.append(('raw', h[last:]))

    res = []; i = 0
    while i < len(tokens):
        kind, val = tokens[i]
        if kind == 'p' and p_is_code(val):
            lines = []; j = i
            while j < len(tokens):
                k, v = tokens[j]
                if k == 'p' and p_is_code(v):
                    lines.append(plain(re.sub(r'^<p class="[^"]*">|</p>$', '', v)).rstrip()); j += 1
                elif k == 'raw' and v.strip() == '': j += 1
                else: break
            res.append('<pre><code class="text">' + H.escape('\n'.join(lines).strip('\n')) + '</code></pre>')
            i = j
        else:
            res.append(val); i += 1
    h = ''.join(res)

    span_re = re.compile(r'<span class="([^"]*)">((?:(?!<span class=).)*?)</span>', re.S)
    def span_sub(m):
        cls, inner = m.group(1), m.group(2)
        fg, bg, bold, ital, strike, mono = cls_props(cls)
        if fg and fg in LINKBLUE: fg = None
        if fg:
            r, g, bl = int(fg[1:3], 16), int(fg[3:5], 16), int(fg[5:7], 16)
            if max(r, g, bl) < 0x50: fg = None
        t = inner
        if mono and t.strip(): t = '<code>' + t + '</code>'
        if strike: t = '<del>' + t + '</del>'
        if ital: t = '<em>' + t + '</em>'
        if bold: t = '<strong>' + t + '</strong>'
        st = []
        if fg and fg != '#000000': st.append('color:' + fg)
        if bg and bg not in DARKBG and bg != '#ffffff': st.append('background-color:' + bg)
        if st: t = '<span style="' + ';'.join(st) + '">' + t + '</span>'
        return t
    prev = None
    while prev != h:
        prev = h; h = span_re.sub(span_sub, h)
    h = re.sub(r'\sclass="c\d+(?:\s+c\d+)*"', '', h)
    return h

def gq(u):
    p = urllib.parse.urlparse(u.replace('&amp;', '&'))
    if p.netloc.endswith('google.com') and p.path == '/url':
        q = urllib.parse.parse_qs(p.query).get('q')
        if q: return q[0]
    return u

def postprocess(s, slug):
    s = s.replace(' ', ' ').replace('&nbsp;', ' ')
    s = re.sub(r'\((https://www\.google\.com/url\?[^)]*)\)', lambda m: '(' + gq(m.group(1)) + ')', s)
    s = re.sub(r'href="(https://www\.google\.com/url\?[^"]*)"', lambda m: 'href="' + gq(m.group(1)) + '"', s)
    s = re.sub(r'!\[[^\]]*\]\(images/(image\d+\.png)\)', lambda m: f'![[{slug}-{m.group(1)}]]', s)
    s = re.sub(r'<span style="background-color:#fff(?:f00|2cc)">(.*?)</span>', r'==\1==', s, flags=re.S)
    lines = [l.rstrip() for l in s.split('\n') if l.strip() != '<!-- -->']

    def strip_inline(t):
        t = re.sub(r'</?span[^>]*>', '', t)
        t = re.sub(r'</?(strong|em|del|code|a)[^>]*>', '', t)
        return re.sub(r'\s+', ' ', H.unescape(t.replace('**', '').replace('==', ''))).strip()
    for i, l in enumerate(lines):
        m = re.match(r'^(#{1,6})\s+(.*)$', l)
        if m: lines[i] = m.group(1) + ' ' + strip_inline(m.group(2))

    def code_clean(t):
        t = re.sub(r'</?span[^>]*>', '', t)
        t = re.sub(r'</?(strong|em|del|code|a)[^>]*>', '', t)
        return H.unescape(t.replace('**', '').replace('==', '')).rstrip()
    def structural(t):
        b = strip_inline(t)
        return (t.strip().startswith(('#', '- ', '* ', '+ ', '> ', '![', '|', '```', '---'))
                or bool(re.match(r'\d+\.\s', t.strip())) or b == '')
    def codeish(b):
        return bool(re.search(r'[;,(){}=]|::|\b(SELECT|FROM|WHERE|JOIN|AS|ON|AND|OR|INSERT|UPDATE|DELETE|CREATE|VALUES|SET|NULL)\b', b, re.I))
    SQL = re.compile(r'^(SELECT|WITH|INSERT\s+INTO|UPDATE\s|DELETE\s+FROM|CREATE\s+TABLE|ALTER\s+TABLE)\b', re.I)
    out = []; i = 0; n = len(lines)
    while i < n:
        if lines[i].lstrip().startswith('```'):          # pass existing fenced blocks through untouched
            out.append(lines[i]); i += 1
            while i < n and not lines[i].lstrip().startswith('```'):
                out.append(lines[i]); i += 1
            if i < n: out.append(lines[i]); i += 1
            continue
        if lines[i].strip() == '' or structural(lines[i]):
            out.append(lines[i]); i += 1; continue
        run = []; j = i
        while j < n:
            if lines[j].strip() == '':
                if j+1 < n and lines[j+1].strip() != '' and not structural(lines[j+1]): j += 1; continue
                break
            if structural(lines[j]): break
            run.append(lines[j]); j += 1
        braw = [strip_inline(x) for x in run]
        is_sql = bool(SQL.match(braw[0])) and len(run) >= 3
        is_json = braw[0] in ('{', '[') and len(run) >= 3 and braw[-1] in ('}', ']', '},', '],') \
                  and sum((':' in b or b in '{}[]') for b in braw)/len(braw) >= 0.6
        if is_sql or is_json:
            cut = len(run)
            while cut > 0 and not codeish(braw[cut-1]): cut -= 1
            if cut >= 3:
                out.append('```' + ('sql' if is_sql else 'json'))
                out += [code_clean(x) for x in run[:cut]]
                out.append('```'); out += run[cut:]; i = j; continue
        out.append(lines[i]); i += 1

    res = []; blank = False
    for l in out:
        if l == '':
            if not blank: res.append('')
            blank = True
        else: res.append(l); blank = False
    while res and res[0] == '': res.pop(0)
    while res and res[-1] == '': res.pop()
    return '\n'.join(res) + '\n'

def slugify(t):
    t = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', t)            # drop link urls
    t = re.sub(r'<[^>]+>', '', t).replace('**', '').replace('==', '')
    t = re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')
    return (t[:40].strip('-') or 'section')

def split_and_write(md, slug, vault):
    srcdir = f'{vault}/sources/{slug}'
    os.makedirs(srcdir, exist_ok=True)
    secs = []; cur = {'title': None, 'body': []}
    for l in md.split('\n'):
        m = re.match(r'^# (.+)$', l)
        if m:
            if cur['title'] is not None or cur['body']: secs.append(cur)
            cur = {'title': m.group(1), 'body': []}
        else: cur['body'].append(l)
    secs.append(cur)
    DATE = re.compile(r'^(20\d\d)-(\d\d)-\d\d')
    MONTH = re.compile(r'^(20\d\d)-(\d\d)(?!\d)')   # bare YYYY-MM heading -> same month bucket
    months = {}; topics = []; rolling = []
    for s in secs:
        t, body = s['title'], s['body']
        if t is None: rolling += body; continue
        m = DATE.match(t) or MONTH.match(t)
        if m: months.setdefault(f'{m.group(1)}-{m.group(2)}', []).append((t, body))
        else: topics.append((t, body))
    trim = lambda x: x.strip('\n')
    for mo in sorted(months):
        o = [f'# {mo}\n']
        for t, body in months[mo]:
            o += [f'## {t}', trim('\n'.join(body)), '']
        open(f'{srcdir}/{mo}.md', 'w').write('\n'.join(o).rstrip() + '\n')
    topic_files = []
    used = set(months.keys()) | {slug}        # never collide with month files or the index
    for t, body in topics:
        sl = slugify(t); base = sl; k = 2
        while sl in used: sl = f'{base}-{k}'; k += 1
        used.add(sl)
        open(f'{srcdir}/{sl}.md', 'w').write(f'# {strip_title(t)}\n\n' + trim('\n'.join(body)).rstrip() + '\n')
        topic_files.append((sl, strip_title(t)))
    idx = [f'# {slug}', '',
           f'Imported from a Google Doc. Images in `/assets` (prefixed `{slug}-`).', '',
           '## Daily log', '- ' + ' · '.join(f'[[{mo}]]' for mo in sorted(months, reverse=True)), '',
           '## Topics']
    idx += [f'- [[{sl}|{ti}]]' for sl, ti in topic_files]
    if [l for l in rolling if l.strip()]:
        idx += ['', '## Rolling / preamble', '', trim('\n'.join(rolling))]
    open(f'{srcdir}/{slug}.md', 'w').write('\n'.join(idx).rstrip() + '\n')
    return sorted(months), topic_files

def strip_title(t):
    t = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', t)
    return re.sub(r'<[^>]+>', '', t).replace('**', '').replace('==', '').strip() or 'Section'

def copy_assets(html_path, slug, vault):
    imgdir = os.path.join(os.path.dirname(html_path), 'images')
    adir = f'{vault}/assets'; os.makedirs(adir, exist_ok=True)
    n = 0
    if os.path.isdir(imgdir):
        for f in os.listdir(imgdir):
            if re.match(r'image\d+\.png$', f):
                shutil.copy(f'{imgdir}/{f}', f'{adir}/{slug}-{f}'); n += 1
    return n

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--html', required=True, help='path to the exported .html (images/ sibling folder)')
    ap.add_argument('--slug', required=True, help='source slug, e.g. techtree (asset prefix + folder)')
    ap.add_argument('--vault', required=True, help='Obsidian vault root')
    a = ap.parse_args()
    pandoc = ensure_pandoc()
    src = open(a.html, encoding='utf-8').read()
    pre = preprocess(src)
    raw = subprocess.run([pandoc, '-f', 'html', '-t', 'gfm', '--wrap=none'],
                         input=pre, capture_output=True, text=True, check=True).stdout
    clean = postprocess(raw, a.slug)
    months, topics = split_and_write(clean, a.slug, a.vault)
    imgs = copy_assets(a.html, a.slug, a.vault)
    print(f"OK -> {a.vault}/sources/{a.slug}/")
    print(f"  months: {months}")
    print(f"  topics: {[s for s, _ in topics]}")
    print(f"  images: {imgs} -> {a.vault}/assets/ (prefix {a.slug}-)")

if __name__ == '__main__':
    main()
