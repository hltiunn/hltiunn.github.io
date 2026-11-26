#!/usr/bin/env python3
"""用途：從 career-ops 的 cv.md 產生鼠大哥的個人網站（GitHub Pages 單頁）。2026-11-26 鼠管家。
公開前去掉：電話、推薦人的聯絡信箱（改「References available on request」）、TOEFL 分數。
用法：python3 build.py  → index.html（同資料夾）"""
import html, os, re

CV = os.path.expanduser("~/Projects/career-ops/cv.md")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
SKIP = {"References"}                     # 第三方聯絡資料不公開
NAV = [("about", "About"), ("research", "Research"), ("publications", "Publications"), ("policy", "Policy & Media"),
       ("experience", "Experience"), ("education", "Education"), ("honors", "Honors"), ("contact", "Contact")]
SEC_ID = {"Profile": "about", "Cross-Domain Integration": "research", "Research Interests": "research",
          "Peer-Reviewed Articles": "publications", "Book Chapters": "publications", "Conference Presentations": "publications",
          "Policy Reports & Briefings": "policy", "Op-Eds & Commentary": "policy", "Selected Media Coverage": "policy",
          "Invited Talks & Briefings": "policy", "Professional Experience": "experience",
          "Additional Experience — Legislative, Executive & Nonprofit": "experience", "Teaching and Mentoring": "experience",
          "Institutional Services": "experience", "Education and Certification": "education",
          "Fellowships & Honors": "honors", "Professional Memberships": "honors", "Skills": "honors", "Languages": "honors"}


def inline(t):
    t = html.escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    t = re.sub(r"\bTiunn, H-L\.", r"<b class=me>Tiunn, H-L.</b>", t)
    t = re.sub(r"\bChang, H\. L\.", r"<b class=me>Chang, H. L.</b>", t)
    return t


def md_block(lines):
    out, para, inlist = [], [], False
    def flush():
        nonlocal para
        if para: out.append("<p>" + inline(" ".join(x.strip() for x in para)) + "</p>"); para = []
    for ln in lines:
        s = ln.rstrip()
        if not s.strip():
            flush()
            if inlist: out.append("</ul>"); inlist = False
            continue
        if re.match(r"^\s*- ", s):
            flush()
            if not inlist: out.append("<ul>"); inlist = True
            out.append("<li>" + inline(re.sub(r"^\s*- ", "", s)) + "</li>")
        elif inlist and s.startswith("  "):
            out[-1] = out[-1][:-5] + " " + inline(s.strip()) + "</li>"
        else:
            if inlist: out.append("</ul>"); inlist = False
            para.append(s)
    flush()
    if inlist: out.append("</ul>")
    return "\n".join(out)


def main():
    raw = open(CV, encoding="utf-8").read()
    head, *rest = re.split(r"\n## ", raw)
    name = re.search(r"^# (.+)$", head, re.M).group(1).strip()
    aka = (re.search(r"\*\((.+?)\)\*", head) or [None, ""])[1]
    tagline = (re.search(r"^\*\*(.+?)\*\*\s*$", head, re.M) or [None, ""])[1]
    sections = {}
    for chunk in rest:
        title, _, body = chunk.partition("\n")
        title = title.strip()
        if title in SKIP: continue
        body = re.sub(r"(?m)^TOEFL.*$", "", body)
        sections[title] = body
    groups = {k: [] for k, _ in NAV}
    for t, b in sections.items():
        g = SEC_ID.get(t)
        if not g: continue
        groups[g].append(f'<h3>{html.escape(t)}</h3>\n{md_block(b.splitlines())}')
    groups["contact"].append('<p><a href="mailto:hltiunnn@gmail.com">hltiunnn@gmail.com</a> · '
                             '<a href="https://www.linkedin.com/in/hltiunn">LinkedIn</a> · Washington, DC &amp; Taipei</p>'
                             '<p class=muted>References available on request.</p>')
    nav = "".join(f'<a href="#{k}">{v}</a>' for k, v in NAV if groups[k])
    body = "".join(f'<section id="{k}"><h2>{v}</h2>{"".join(groups[k])}</section>' for k, v in NAV if groups[k])
    stats = '<div class=stats><div><b>162</b><span>citations</span></div><div><b>6</b><span>h-index</span></div><div><b>8</b><span>peer-reviewed articles</span></div><div><b>9+</b><span>international media outlets</span></div></div>'
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(name)} — Health Workforce &amp; National Security Policy</title>
<meta name="description" content="{html.escape(tagline)}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{{--bg:#fbfaf7;--ink:#1d2327;--sub:#5b6770;--acc:#1f4e79;--line:#e4e1da;--card:#fff}}
@media(prefers-color-scheme:dark){{:root{{--bg:#0f1418;--ink:#e6edf3;--sub:#93a1ad;--acc:#7fb3e6;--line:#26313a;--card:#151c22}}}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}
body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.65 Inter,-apple-system,"Segoe UI",sans-serif}}
header{{border-bottom:1px solid var(--line);background:var(--card)}}
.wrap{{max-width:880px;margin:0 auto;padding:0 22px}}
.hero{{padding:56px 22px 34px}}
h1{{font:600 40px/1.15 "Source Serif 4",Georgia,serif;margin:0}}
.aka{{color:var(--sub);margin:6px 0 14px}}.tag{{font-size:19px;color:var(--acc);font-weight:500;margin:0 0 20px}}
.links a{{display:inline-block;margin:0 10px 8px 0;padding:6px 14px;border:1px solid var(--line);border-radius:999px;color:var(--ink);text-decoration:none;font-size:14px}}
.links a:hover{{border-color:var(--acc);color:var(--acc)}}
nav{{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);z-index:9}}
nav .wrap{{display:flex;gap:18px;overflow-x:auto;padding-top:12px;padding-bottom:12px}}
nav a{{color:var(--sub);text-decoration:none;font-size:14px;font-weight:500;white-space:nowrap}}nav a:hover{{color:var(--acc)}}
.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:26px 0 4px}}
.stats div{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;text-align:center}}
.stats b{{display:block;font:600 26px "Source Serif 4",serif;color:var(--acc)}}.stats span{{font-size:13px;color:var(--sub)}}
section{{padding:34px 0 8px;border-bottom:1px solid var(--line)}}
h2{{font:600 26px "Source Serif 4",serif;margin:0 0 12px}}
h3{{font-size:13px;letter-spacing:.09em;text-transform:uppercase;color:var(--sub);margin:26px 0 8px}}
p{{margin:0 0 12px}}ul{{padding-left:20px;margin:0 0 14px}}li{{margin:6px 0}}
strong{{font-weight:600}}b.me{{font-weight:600;color:var(--acc)}}a{{color:var(--acc)}}.muted{{color:var(--sub)}}
footer{{padding:30px 0 50px;color:var(--sub);font-size:13px}}
@media(max-width:640px){{h1{{font-size:31px}}.stats{{grid-template-columns:repeat(2,1fr)}}}}
@media print{{nav,.links{{display:none}}body{{background:#fff;color:#000}}}}
</style></head><body>
<header><div class="wrap hero"><h1>{html.escape(name)}</h1><div class=aka>{html.escape(aka)}</div>
<p class=tag>{html.escape(tagline)}</p>
<div class=links><a href="mailto:hltiunnn@gmail.com">Email</a><a href="https://www.linkedin.com/in/hltiunn">LinkedIn</a><a href="https://github.com/hltiunn">GitHub</a><!--SCHOLAR--></div>
{stats}</div></header>
<nav><div class=wrap>{nav}</div></nav>
<main class=wrap>{body}</main>
<footer class=wrap>© {html.escape(name)} · Last updated November 2026</footer></body></html>"""
    open(OUT, "w", encoding="utf-8").write(page)
    print("wrote", OUT, len(page), "bytes;", sum(len(v) for v in groups.values()), "blocks")


if __name__ == "__main__":
    main()
