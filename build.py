#!/usr/bin/env python3
"""用途：鼠大哥個人網站 v2（編輯式學術版面）。從 career-ops 的 cv.md 解析成結構化內容再排版。2026-11-26 鼠管家。
不公開：電話、推薦人聯絡方式、TOEFL。用法：python3 build.py → index.html"""
import html, os, re

CV = os.path.expanduser("~/Projects/career-ops/cv.md")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
SCHOLAR = os.environ.get("SCHOLAR_URL", "")
E = html.escape


def md(t):
    t = E(t.strip())
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    return t


def sections(raw):
    out = {}
    for chunk in re.split(r"\n## ", raw)[1:]:
        t, _, b = chunk.partition("\n"); out[t.strip()] = b
    return out


def bullets(body):
    items, cur = [], None
    for ln in body.splitlines():
        if re.match(r"^\s*- ", ln):
            cur = re.sub(r"^\s*- ", "", ln).strip(); items.append(cur)
        elif cur is not None and ln.startswith("  ") and ln.strip():
            items[-1] += " " + ln.strip()
        elif not ln.strip():
            cur = None
    return items


def para(body):
    ps = [p.strip().replace("\n", " ") for p in re.split(r"\n\s*\n", body) if p.strip() and not p.strip().startswith("-")]
    return ps


def jobs(body):
    """**Title — Org, Place (years)** 之後接說明段與 bullets。"""
    out = []
    for blk in re.split(r"\n(?=\*\*[^*]+\*\*\s*$)", "\n" + body, flags=re.M):
        blk = blk.strip()
        m = re.match(r"\*\*(.+?)\*\*\s*\n?(.*)", blk, re.S)
        if not m: continue
        head, rest = m.group(1), m.group(2)
        yrs = re.search(r"\(([^()]*\d{4}[^()]*)\)\s*$", head)
        years = yrs.group(1) if yrs else ""
        head = head[:yrs.start()].strip() if yrs else head
        role, _, org = head.partition(" — ")
        note = re.match(r"\*\((.+?)\)\*", rest.strip())
        desc = [p for p in para(rest) if not p.startswith("*(")]
        out.append({"role": role, "org": org, "years": years.replace("–Present", "–present"), "note": note.group(1) if note else "",
                    "desc": desc[:1], "items": bullets(rest)})
    return out


def year_of(s):
    m = re.search(r"\((\d{4})[^)]*\)", s); return m.group(1) if m else ""


def pub(s):
    y = year_of(s)
    first = "(first author)" in s or s.startswith("Tiunn")
    s2 = s.replace("*(first author)*", "").strip()
    s2 = re.sub(r"\b(Tiunn, H-L\.|Chang, H\. L\.)", r"§\1§", s2)
    h = md(s2).replace("§", "")
    h = re.sub(r"(Tiunn, H-L\.|Chang, H\. L\.)", r"<span class=me>\1</span>", h, count=1)
    return y, h, first


def main():
    raw = open(CV, encoding="utf-8").read()
    head = raw.split("\n## ")[0]
    S = sections(raw)
    name = re.search(r"^# (.+)$", head, re.M).group(1).strip()
    aka = (re.search(r"\*\((.+?)\)\*", head) or [None, ""])[1].replace("also known as ", "")
    tagline = (re.search(r"^\*\*(.+?)\*\*\s*$", head, re.M) or [None, ""])[1]
    profile = para(S.get("Profile", ""))
    cross = S.get("Cross-Domain Integration", "")
    cross_p = para(cross); cross_b = bullets(cross)

    def timeline(js, cls="tl"):
        r = []
        for j in js:
            items = "".join(f"<li>{md(i)}</li>" for i in j["items"])
            note = f'<p class=note>{md(j["note"])}</p>' if j["note"] else ""
            desc = "".join(f"<p>{md(d)}</p>" for d in j["desc"])
            r.append(f'<div class=row><div class=when>{E(j["years"])}</div><div class=what><h4>{md(j["role"])}</h4>'
                     f'<div class=org>{md(j["org"])}</div>{note}{desc}{"<ul>"+items+"</ul>" if items else ""}</div></div>')
        return f'<div class={cls}>{"".join(r)}</div>'

    def publist(items):
        r = []
        for s in sorted(items, key=lambda x: year_of(x), reverse=True):
            y, h, first = pub(s)
            r.append(f'<div class=row><div class=when>{y}</div><div class="what cite{" lead" if first else ""}">{h}</div></div>')
        return f'<div class=tl>{"".join(r)}</div>'

    def media(items):
        r = []
        for s in items:
            m = re.match(r"(.+?) \(([\d-]+)\)\. \"(.+?)\"", s)
            if m: r.append(f'<li><span class=outlet>{E(m.group(1))}</span><span class=hl>{E(m.group(3))}</span><span class=dt>{E(m.group(2)[:7])}</span></li>')
            else: r.append(f"<li>{md(s)}</li>")
        return "<ul class=media>" + "".join(r) + "</ul>"

    def simple(title):
        return "<ul class=plain>" + "".join(f"<li>{md(i)}</li>" for i in bullets(S.get(title, ""))) + "</ul>"

    edu = []
    for s in bullets(S.get("Education and Certification", "")):
        m = re.match(r"\*\*(.+?)\*\* — (.+?) \(([^)]+)\)(.*)", s)
        if m: edu.append(f'<div class=row><div class=when>{E(m.group(3))}</div><div class=what><h4>{E(m.group(1))}</h4><div class=org>{E(m.group(2))}</div><p>{md(m.group(4))}</p></div></div>')
    report = bullets(S.get("Policy Reports & Briefings", ""))
    feature = report[0] if report else ""
    ft = re.search(r"\*(.+?)\*", feature)

    links = [("Email", "mailto:hltiunnn@gmail.com"), ("LinkedIn", "https://www.linkedin.com/in/hltiunn"), ("GitHub", "https://github.com/hltiunn")]
    if SCHOLAR: links.insert(1, ("Google Scholar", SCHOLAR))
    linkhtml = "".join(f'<a href="{u}">{t}</a>' for t, u in links)
    nav = [("about", "About"), ("work", "Selected work"), ("experience", "Experience"), ("publications", "Publications"),
           ("media", "Media & talks"), ("education", "Education"), ("honors", "Honors")]
    navhtml = "".join(f'<a href="#{a}">{b}</a>' for a, b in nav)

    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(name)} | Health workforce and national security policy</title>
<meta name="description" content="{E(tagline)}"><meta property="og:title" content="{E(name)}"><meta property="og:description" content="{E(tagline)}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Public+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{{--paper:#f6f3ec;--ink:#1c2128;--sub:#5f6873;--line:#ddd6c8;--navy:#173b5c;--rust:#9a4a2c}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}
body{{margin:0;background:var(--paper);color:var(--ink);font:16.5px/1.7 "Public Sans",-apple-system,sans-serif;-webkit-font-smoothing:antialiased}}
a{{color:var(--navy);text-decoration-thickness:1px;text-underline-offset:3px}}
.layout{{display:grid;grid-template-columns:330px 1fr;max-width:1180px;margin:0 auto;gap:64px;padding:0 40px}}
aside{{position:sticky;top:0;height:100vh;padding:64px 0 40px;display:flex;flex-direction:column}}
aside h1{{font:600 44px/1.05 Fraunces,Georgia,serif;letter-spacing:-.01em;margin:0}}
.aka{{color:var(--sub);font-size:14px;margin:10px 0 22px}}
.role{{font:400 19px/1.45 Fraunces,serif;color:var(--navy);margin:0 0 26px}}
.links{{display:flex;flex-direction:column;gap:6px;font-size:15px}}.links a{{text-decoration:none;font-weight:500}}.links a:hover{{text-decoration:underline}}
aside nav{{margin-top:auto;display:flex;flex-direction:column;gap:4px;border-top:1px solid var(--line);padding-top:18px}}
aside nav a{{color:var(--sub);text-decoration:none;font-size:14px}}aside nav a:hover{{color:var(--ink)}}
main{{padding:64px 0 80px;max-width:720px}}
section{{padding:0 0 56px}}
h2{{font:600 28px/1.2 Fraunces,serif;margin:0 0 22px;padding-top:8px}}
h3{{font:600 18px Fraunces,serif;margin:34px 0 12px}}
.lede{{font:400 24px/1.5 Fraunces,serif;margin:0 0 26px}}
.lede em{{color:var(--rust);font-style:italic}}
.question{{border-left:3px solid var(--rust);padding:4px 0 4px 20px;margin:28px 0;font:italic 400 21px/1.5 Fraunces,serif}}
.tools{{display:grid;grid-template-columns:repeat(3,1fr);gap:22px;margin:20px 0 0}}
.tools div{{border-top:2px solid var(--navy);padding-top:10px;font-size:15px}}.tools strong{{display:block;font-size:15px;margin-bottom:4px}}
.feature{{background:var(--navy);color:#f3efe6;padding:30px 32px;margin:0 0 30px}}
.feature .kind{{font-size:13px;opacity:.75}}.feature h3{{color:#fff;font-size:26px;line-height:1.25;margin:6px 0 10px}}.feature p{{margin:0;opacity:.9}}
.tl .row{{display:grid;grid-template-columns:118px 1fr;gap:20px;padding:16px 0;border-top:1px solid var(--line)}}
.when{{color:var(--sub);font-size:14px;font-variant-numeric:tabular-nums;padding-top:2px}}
.what h4{{margin:0;font-size:17px;font-weight:600}}.org{{color:var(--navy);font-size:15px}}.note{{color:var(--sub);font-size:14px;margin:2px 0}}
.what p{{margin:8px 0 0}}.what ul{{margin:8px 0 0;padding-left:18px}}.what li{{margin:5px 0}}
.cite{{font-size:15.5px}}.cite.lead{{border-left:3px solid var(--rust);padding-left:14px;margin-left:-17px}}.me{{font-weight:600;color:var(--ink);text-decoration:underline;text-decoration-color:var(--rust)}}
.media{{list-style:none;padding:0;margin:0}}.media li{{display:grid;grid-template-columns:150px 1fr 70px;gap:16px;padding:12px 0;border-top:1px solid var(--line);font-size:15.5px}}
.outlet{{font-weight:600}}.hl{{font-family:Fraunces,serif}}.dt{{color:var(--sub);font-size:14px;text-align:right}}
.plain{{padding-left:18px}}.plain li{{margin:7px 0}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:34px}}
footer{{color:var(--sub);font-size:13px;border-top:1px solid var(--line);padding-top:18px}}
@media(max-width:960px){{.layout{{grid-template-columns:1fr;gap:0;padding:0 22px}}aside{{position:static;height:auto;padding:44px 0 10px}}aside nav{{display:none}}
.links{{flex-direction:row;flex-wrap:wrap;gap:16px}}main{{padding-top:20px}}.tools,.cols{{grid-template-columns:1fr}}
.tl .row{{grid-template-columns:1fr;gap:2px}}.media li{{grid-template-columns:1fr}}.dt{{text-align:left}}aside h1{{font-size:36px}}}}
@media print{{aside{{position:static;height:auto}}aside nav{{display:none}}.layout{{display:block}}.feature{{color:#000;background:none;border:1px solid #000}}}}
</style></head><body><div class=layout>
<aside><h1>{E(name)}</h1><div class=aka>{E(aka)}</div><p class=role>{E(tagline)}</p><div class=links>{linkhtml}</div><nav>{navhtml}</nav></aside>
<main>
<section id=about><p class=lede>I study how critical national systems hold up under pressure: the <em>health workforce</em> that keeps American care running, and the <em>defense supply chains</em> that Taiwan and its partners depend on.</p>
<p>{md(profile[0]) if profile else ""}</p>
<p class=question>How does a critical system withstand shocks, and which policy levers build its resilience?</p>
{"".join(f"<p>{md(p)}</p>" for p in cross_p[1:2])}
<div class=tools>{"".join(f"<div>{md(b)}</div>" for b in cross_b)}</div></section>

<section id=work><h2>Selected work</h2>
<div class=feature><div class=kind>Flagship report, DSET, {year_of(feature) or "2025"}</div><h3>{E(ft.group(1)) if ft else ""}</h3>
<p>Lead author. Cited by Bloomberg, The Economist, Deutsche Welle, Al Jazeera and Nikkei Asia; presented at CNAS, AEI and GTI.</p></div>
<h3>Current research</h3>{timeline([j for j in jobs(S.get("Professional Experience","")) if "Mullan" in j["org"]][:1])}</section>

<section id=experience><h2>Experience</h2>{timeline([j for j in jobs(S.get("Professional Experience","")) if "Mullan" not in j["org"]])}
<h3>Legislative, executive and nonprofit</h3>{timeline(jobs(S.get("Additional Experience — Legislative, Executive & Nonprofit","")))}
<h3>Teaching and mentoring</h3>{simple("Teaching and Mentoring")}</section>

<section id=publications><h2>Publications</h2>
<h3>Peer-reviewed articles</h3>{publist(bullets(S.get("Peer-Reviewed Articles","")))}
<h3>Book chapters</h3>{publist(bullets(S.get("Book Chapters","")))}
<h3>Policy reports and commentary</h3>{publist(report + bullets(S.get("Op-Eds & Commentary","")))}
<h3>Conference presentations</h3>{publist(bullets(S.get("Conference Presentations","")))}</section>

<section id=media><h2>Media and talks</h2>{media(bullets(S.get("Selected Media Coverage","")))}
<h3>Invited talks and briefings</h3>{simple("Invited Talks & Briefings")}</section>

<section id=education><h2>Education</h2><div class=tl>{"".join(edu)}</div></section>

<section id=honors><h2>Honors and service</h2><div class=cols><div><h3>Fellowships and honors</h3>{simple("Fellowships & Honors")}</div>
<div><h3>Service</h3>{simple("Institutional Services")}</div></div>
<h3>Languages</h3><p>{md(para(S.get("Languages",""))[0]) if para(S.get("Languages","")) else ""}</p>
<h3>Memberships</h3><p>{md(" ".join(para(S.get("Professional Memberships",""))))}</p></section>

<footer>Contact: <a href="mailto:hltiunnn@gmail.com">hltiunnn@gmail.com</a>. References available on request. Updated November 2026.</footer>
</main></div></body></html>"""
    open(OUT, "w", encoding="utf-8").write(page)
    print("wrote", OUT, len(page))


if __name__ == "__main__":
    main()
