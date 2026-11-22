"""Build one static page per category, plus sitemap.xml and robots.txt.

Category pages are plain HTML that search engines can read without running
JavaScript: the checked deals for that category, each linking to its full price
story on the main page (/#d-<slug>) and to the retailer. Run after build.py.
"""
import html
import json
import pathlib
import re
import urllib.parse

HERE = pathlib.Path(__file__).parent
SITE = "https://strikethrough.com.au"
rows = json.loads((HERE / "data" / "deals.json").read_text())["rows"]
aff = json.loads((HERE / "affiliates.json").read_text()) if (HERE / "affiliates.json").exists() else {"retailers": {}}

LABEL = {
    "Record low": ("Record low", "good"), "Near record low": ("Near record low", "good"),
    "Cheapest tracked": ("Best price tracked", "good"), "Regular price drop": ("Often this price", "mid"),
    "Unverified": ("Not yet verified", "mid"), "Check the RRP": ("Was-price unconfirmed", "flag"),
    "Token discount": ("Small discount", "flag"), "Beaten elsewhere": ("Lower elsewhere", "flag"),
    "Cheaper before": ("Was cheaper recently", "flag"),
}


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def money(x):
    return f"${x:,.0f}" if x >= 100 or float(x).is_integer() else f"${x:,.2f}"


def affiliate(r):
    """Same rules as the main page: Amazon tag, or a network template with {url}."""
    url = r.get("link") or ""
    a = aff.get("retailers", {}).get(r["retailer"], {})
    if not url:
        return "", False
    if a.get("amazon_tag") and "amazon.com.au" in url:
        return url + ("&" if "?" in url else "?") + "tag=" + urllib.parse.quote(a["amazon_tag"]), True
    if a.get("template") and "{url}" in a["template"]:
        return a["template"].replace("{url}", urllib.parse.quote(url, safe="")), True
    return url, False


e = html.escape
CSS = """:root{color-scheme:light dark;--bg:light-dark(#fff,#0f1011);--ink:light-dark(#111,#f1f1ef);--mute:light-dark(#5d5d5a,#a3a3a0);--line:light-dark(#e6e5e1,#2a2b2d);--red:light-dark(#e10600,#ff5446);--green:light-dark(#0a8f4e,#3ccf86);--soft:light-dark(#f5f4f1,#18191b)}
*{box-sizing:border-box;min-width:0}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 Archivo,system-ui,sans-serif}
a{color:inherit}.w{max-width:1000px;margin:0 auto;padding:24px max(4vw,16px) 64px}
.logo{font-stretch:75%;font-weight:800;font-size:24px;text-decoration:none}.logo s{text-decoration:none;position:relative}.logo s::after{content:"";position:absolute;left:-2px;right:-2px;top:52%;height:3px;background:var(--red);transform:rotate(-4deg)}
h1{font-stretch:75%;font-weight:800;font-size:clamp(32px,5vw,48px);line-height:1.05;letter-spacing:-.02em;margin:28px 0 10px}
.lede{color:var(--mute);font-size:17px;max-width:62ch}.cta{display:inline-block;margin:14px 0 26px;padding:10px 18px;border-radius:999px;background:var(--ink);color:var(--bg);text-decoration:none;font-weight:600}
.d{border-top:1px solid var(--line);padding:16px 0;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:6px 16px}
.d h2{font-size:17px;margin:0}.p{font-stretch:75%;font-weight:800;font-size:28px;white-space:nowrap;text-align:right}
.was{color:var(--mute);text-decoration:line-through;text-decoration-color:var(--red);font-size:15px;font-weight:400;margin-left:8px}
.m{color:var(--mute);font-size:14px;margin:0}.v{font-size:13px;font-weight:600}.good{color:var(--green)}.flag{color:var(--red)}.mid{color:var(--mute)}
.l{font-size:14px;display:flex;gap:14px;flex-wrap:wrap}.l a{text-decoration:underline}.cats{display:flex;flex-wrap:wrap;gap:8px;margin-top:30px}.cats a{border:1px solid var(--line);border-radius:999px;padding:6px 12px;text-decoration:none;font-size:14px}
.fine{color:var(--mute);font-size:13px;margin-top:28px;max-width:75ch}"""

cats = sorted({r["category"] for r in rows})
latest = max(r["seen"] for r in rows)
latest_h = __import__("datetime").date.fromisoformat(latest).strftime("%-d %B %Y")
any_aff = False
urls = [SITE + "/"]
for cat in cats:
    slug = slugify(cat)
    items = sorted([r for r in rows if r["category"] == cat], key=lambda r: -r["score"])
    good = sum(1 for r in items if LABEL.get(r["verdict"], ("", ""))[1] == "good")
    rets = sorted({r["retailer"] for r in items})
    best = items[0]
    title = f"Black Friday {cat.lower()} deals, checked | Strikethrough"
    desc = (f"{len(items)} Black Friday {cat.lower()} deals from {', '.join(rets)} checked against price history "
            f"and other stores. {good} hold up. Best right now: {best['product']} for {money(best['now'])}.")
    body = []
    for r in items:
        lab, g = LABEL.get(r["verdict"], (r["verdict"], "mid"))
        href, is_aff = affiliate(r)
        any_aff = any_aff or is_aff
        rel = "sponsored nofollow noopener" if is_aff else "nofollow noopener"
        buy = f'<a href="{e(href)}" rel="{rel}" target="_blank">{e(r["link_label"])}</a>' if href else ""
        body.append(f"""<article class="d"><div><h2>{e(r['product'])}</h2>
<p class="m">{e(r['retailer'])} · <span class="v {g}">{e(lab)}</span> · real {round(r['real_pct'])}% off</p>
<p class="m">{e(r['reason'])}</p>
<p class="l"><a href="/#d-{e(r['slug'])}">Price story</a>{buy}</p></div>
<div class="p">{money(r['now'])}<span class="was">{money(r['was'])}</span></div></article>""")
    other = "".join(f'<a href="/deals/{slugify(c)}/">{e(c)}</a>' for c in cats if c != cat)
    disc = f'<p class="fine">{e(aff.get("disclosure", ""))}</p>' if any(affiliate(r)[1] for r in items) else ""
    page = f"""<!DOCTYPE html>
<html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE}/deals/{slug}/"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..900&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body><div class="w">
<a class="logo" href="/">Strike<s>through</s></a>
<h1>Black Friday {e(cat.lower())} deals, checked</h1>
<p class="lede">We checked {len(items)} {e(cat.lower())} deal{'s' if len(items) != 1 else ''} from {e(', '.join(rets))} against price history and the same product at other stores. {good} hold up. Prices last checked {e(latest_h)}.</p>
<a class="cta" href="/#c-{slug}">Filter, compare and see price stories</a>
{''.join(body)}
<div class="cats">{other}</div>
{disc}
<p class="fine">Prices come from retailer pages and dated deal reports, change through the day, and may be member-only or colour-specific. Always confirm the price at checkout. Strikethrough is independent and isn't paid by the retailers listed.</p>
</div></body></html>"""
    out = HERE / "deals" / slug
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page)
    urls.append(f"{SITE}/deals/{slug}/")

# remove pages for categories that no longer exist
for d in (HERE / "deals").iterdir():
    if d.is_dir() and d.name not in {slugify(c) for c in cats}:
        for f in d.iterdir():
            f.unlink()
        d.rmdir()

(HERE / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                  + "".join(f"  <url><loc>{u}</loc><lastmod>{latest}</lastmod></url>\n" for u in urls) + "</urlset>\n")
(HERE / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
print(len(cats), "category pages")
