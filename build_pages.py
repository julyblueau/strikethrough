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


def clip(text, n=158):
    """Trim a meta description to about n characters on a word boundary."""
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= n else text[: n - 1].rsplit(" ", 1)[0].rstrip(",.;:") + "…"


def head_common():
    return ('<link rel="icon" href="/icons/icon-192.png"><link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">'
            '<link rel="manifest" href="/manifest.webmanifest"><meta name="theme-color" content="#0a0a0b">'
            '<meta property="og:site_name" content="Strikethrough"><meta property="og:locale" content="en_AU">')


def faq_html(qas):
    return '<h2 class="s">Questions</h2>' + "".join(f'<details class="qa"><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in qas)


def faq_ld(qas):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qas]}


history = json.loads((HERE / "data" / "history.json").read_text()) if (HERE / "data" / "history.json").exists() else {}
CSS = """:root{color-scheme:dark;--bg:#0a0a0b;--ink:#f5f5f7;--mute:#a1a1a6;--line:#26262a;--red:#ff453a;--green:#30d158;--card:#121214}
*{box-sizing:border-box;min-width:0}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 Inter,system-ui,-apple-system,sans-serif;-webkit-font-smoothing:antialiased}
a{color:inherit}.w{max-width:1000px;margin:0 auto;padding:24px max(4vw,16px) 64px}
.logo{font-family:"Inter Tight",Inter,sans-serif;font-weight:700;letter-spacing:-.03em;font-size:24px;text-decoration:none}.logo s{text-decoration:none;position:relative}.logo s::after{content:"";position:absolute;left:-2px;right:-2px;top:52%;height:3px;background:var(--red);transform:rotate(-4deg)}
h1{font-family:"Inter Tight",Inter,sans-serif;font-weight:700;font-size:clamp(34px,5vw,54px);line-height:1.04;letter-spacing:-.03em;margin:28px 0 10px}
.lede{color:var(--mute);font-size:17px;max-width:62ch}.cta{display:inline-block;margin:14px 0 26px;padding:11px 20px;border-radius:999px;background:linear-gradient(180deg,#ff5a4f,#e0362c);color:#fff;text-decoration:none;font-weight:600}
.d{border:1px solid var(--line);background:var(--card);border-radius:20px;padding:12px;margin-bottom:12px;display:grid;grid-template-columns:96px minmax(0,1fr) auto;gap:6px 16px;align-items:start}
.pic{width:96px;height:72px;border-radius:12px;background:radial-gradient(ellipse 60% 55% at 50% 42%,#2e2e40,transparent 70%),#18181b;display:grid;place-items:center}.pic img{width:84%}
.d h2{font-size:17px;margin:0;font-weight:600}.p{font-family:"Inter Tight",Inter,sans-serif;font-weight:700;font-size:26px;white-space:nowrap;text-align:right}
.was{color:var(--mute);text-decoration:line-through;text-decoration-color:var(--red);font-size:15px;font-weight:400;margin-left:8px}
.m{color:var(--mute);font-size:14px;margin:0}.v{font-size:13px;font-weight:600}.good{color:var(--green)}.flag{color:var(--red)}.mid{color:var(--mute)}
.l{font-size:14px;display:flex;gap:14px;flex-wrap:wrap;margin:6px 0 0}.l a{text-decoration:underline}.cats{display:flex;flex-wrap:wrap;gap:8px;margin-top:30px}.cats a{border:1px solid var(--line);background:#141416;border-radius:999px;padding:7px 13px;text-decoration:none;font-size:14px}
.fine{color:var(--mute);font-size:13px;margin-top:28px;max-width:75ch}
.bc{color:var(--mute);font-size:14px;margin-top:22px}.bc a{color:var(--mute)}.d h2 a{text-decoration:none}.d h2 a:hover{text-decoration:underline}
table{width:100%;border-collapse:collapse;margin:14px 0;font-size:15px}th,td{text-align:left;padding:10px 8px;border-bottom:1px solid var(--line)}th{color:var(--mute);font-weight:500;font-size:13px}td.n{white-space:nowrap;font-variant-numeric:tabular-nums}
.sum{border:1px solid var(--line);background:var(--card);border-radius:20px;padding:16px 18px;margin:8px 0 18px}.sum .big{font-family:"Inter Tight",Inter,sans-serif;font-weight:700;font-size:34px}
h2.s{font-size:20px;margin:30px 0 6px}.qa{border-bottom:1px solid var(--line);padding:10px 0}.qa summary{cursor:pointer;font-weight:600;list-style:none}.qa summary::-webkit-details-marker{display:none}.qa summary::after{content:" +";color:var(--mute)}.qa[open] summary::after{content:" –"}.qa p{color:var(--mute);margin:8px 0 2px}.rel{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px;margin-top:10px}.rel a{border:1px solid var(--line);background:var(--card);border-radius:14px;padding:10px 12px;text-decoration:none;font-size:14px}.rel b{display:block;font-size:16px;margin-top:2px}
@media(max-width:600px){.d{grid-template-columns:72px minmax(0,1fr)}.pic{width:72px;height:56px}.p{grid-column:2;text-align:left}}"""

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
    title = f"Black Friday {cat} Deals, Checked | Strikethrough"
    desc = clip(f"{len(items)} {cat} deals from {len(rets)} Australian retailers, checked against price history "
                f"and other stores. {good} hold up. Best right now: {best['product']}, {money(best['now'])}.")
    body = []
    for r in items:
        lab, g = LABEL.get(r["verdict"], (r["verdict"], "mid"))
        href, is_aff = affiliate(r)
        any_aff = any_aff or is_aff
        rel = "sponsored nofollow noopener" if is_aff else "nofollow noopener"
        buy = f'<a href="{e(href)}" rel="{rel}" target="_blank">{e(r["link_label"])}</a>' if href else ""
        pic = f'<img src="{e(r["image"])}" alt="{e(r["product"])}" loading="lazy" referrerpolicy="no-referrer">' if r.get("image") else f'<img src="/art/{slug}.svg" alt="" loading="lazy">'
        body.append(f"""<article class="d"><div class="pic">{pic}</div><div><h2><a href="/price/{e(r['product_key'])}/">{e(r['product'])}</a></h2>
<p class="m">{e(r['retailer'])} · <span class="v {g}">{e(lab)}</span> · real {round(r['real_pct'])}% off</p>
<p class="m">{e(r['reason'])}</p>
<p class="l"><a href="/price/{e(r['product_key'])}/">Price check</a><a href="/#d-{e(r['slug'])}">Price story</a>{buy}</p></div>
<div class="p">{money(r['now'])}<span class="was">{money(r['was'])}</span></div></article>""")
    ld = {"@context": "https://schema.org", "@type": "ItemList", "name": f"Black Friday {cat} deals, checked",
          "url": f"{SITE}/deals/{slug}/", "numberOfItems": len(items), "itemListElement": []}
    for i, r in enumerate(items, 1):
        prod = {"@type": "Product", "name": r["product"], "brand": {"@type": "Brand", "name": r["brand"]}, "category": cat,
                "offers": {"@type": "Offer", "price": f"{r['now']:.2f}", "priceCurrency": "AUD",
                           "seller": {"@type": "Organization", "name": r["retailer"]}}}
        if r.get("link"):
            prod["offers"]["url"] = r["link"]
        if r.get("image"):
            prod["image"] = r["image"]
        ld["itemListElement"].append({"@type": "ListItem", "position": i, "url": f"{SITE}/price/{r['product_key']}/", "item": prod})
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Strikethrough", "item": f"{SITE}/"},
        {"@type": "ListItem", "position": 2, "name": f"{cat} deals", "item": f"{SITE}/deals/{slug}/"}]}
    flag = sum(1 for r in items if LABEL.get(r["verdict"], ("", ""))[1] == "flag")
    agg = {}
    for r in items:
        a = agg.setdefault(r["retailer"], [0, 0]); a[0] += r["real_pct"]; a[1] += 1
    ranked = sorted(((v[0] / v[1], k, v[1]) for k, v in agg.items() if v[1] >= 3), reverse=True)
    best_good = next((r for r in items if LABEL.get(r["verdict"], ("", ""))[1] == "good"), None)
    qas = [(f"How many Black Friday {cat} deals are genuine?",
            f"Of {len(items)} {cat} deals we checked, {good} hold up (a record low or the best price at any store we track) "
            f"and {flag} come with a catch, such as being cheaper at another store or a was-price we couldn't confirm. Checked {latest_h}.")]
    if ranked:
        top3 = ", ".join(f"{k} ({round(a)}% average real discount across {n} deals)" for a, k, n in ranked[:3])
        qas.append((f"Which retailer has the best {cat} discounts?", f"By average real discount, measured from the lowest was-price any store uses: {top3}."))
    if best_good:
        qas.append((f"What's the best {cat} deal right now?",
                    f"{best_good['product']} for {money(best_good['now'])} at {best_good['retailer']}: {best_good['reason']}"))
    ldjson = json.dumps([ld, crumbs, faq_ld(qas)], ensure_ascii=False).replace("</", "<\\/")
    other = "".join(f'<a href="/deals/{slugify(c)}/">{e(c)}</a>' for c in cats if c != cat)
    disc = f'<p class="fine">{e(aff.get("disclosure", ""))}</p>' if any(affiliate(r)[1] for r in items) else ""
    page = f"""<!DOCTYPE html>
<html lang="en-AU"><head><meta charset="utf-8">
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
}})(window,document,'script','dataLayer','GTM-N8LGLSV5');</script>
<!-- End Google Tag Manager -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-DBGC2DTVBK"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-DBGC2DTVBK');</script>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">{head_common()}
<link rel="canonical" href="{SITE}/deals/{slug}/"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="website"><meta property="og:url" content="{SITE}/deals/{slug}/"><meta property="og:image" content="{SITE}/og/{slug}.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:site_name" content="Strikethrough"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{SITE}/og/{slug}.jpg">
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>{CSS}</style>
<script type="application/ld+json">{ldjson}</script></head><body>
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-N8LGLSV5" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) --><div class="w">
<a class="logo" href="/">Strike<s>through</s></a>
<nav class="bc" aria-label="Breadcrumb"><a href="/">Home</a> › <span>{e(cat)}</span></nav>
<h1>Black Friday {e(cat)} deals, checked</h1>
<p class="lede">We checked {len(items)} {e(cat)} deal{'s' if len(items) != 1 else ''} from {e(', '.join(rets))} against price history and the same product at other stores. {good} hold up. Prices last checked {e(latest_h)}.</p>
<a class="cta" href="/#c-{slug}">Filter, compare and see price stories</a>
{''.join(body)}
{faq_html(qas)}
<div class="cats">{other}</div>
{disc}
<p class="fine">Prices come from retailer pages and dated deal reports, change through the day, and may be member-only or colour-specific. Always confirm the price at checkout. Strikethrough is independent and isn't paid by the retailers listed. <a href="/method/">Method</a> · <a href="/privacy/">Privacy</a> · <a href="/terms/">Terms</a> · <a href="/contact/">Contact &amp; corrections</a></p>
</div></body></html>"""
    out = HERE / "deals" / slug
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page)
    urls.append(f"{SITE}/deals/{slug}/")


# ---- one page per product: /price/<product_key>/ ----
GTM_HEAD = """<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-N8LGLSV5');</script>
<!-- End Google Tag Manager -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-DBGC2DTVBK"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-DBGC2DTVBK');</script>"""
GTM_BODY = '<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-N8LGLSV5" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>'

by_key = {}
for r in rows:
    by_key.setdefault(r["product_key"], []).append(r)
keys_by_cat = {}
for k, rs in by_key.items():
    keys_by_cat.setdefault(rs[0]["category"], []).append(k)

price_dir = HERE / "price"
price_dir.mkdir(exist_ok=True)
made = set()
for key, rs in by_key.items():
    rs = sorted(rs, key=lambda r: r["now"])
    best, top = rs[0], max(rs, key=lambda r: r["score"])
    name, cat = best["product"], best["category"]
    cslug = slugify(cat)
    lab, g = LABEL.get(best["verdict"], (best["verdict"], "mid"))
    n = len(rs)
    lo, hi = min(r["now"] for r in rs), max(r["now"] for r in rs)
    seen = max(r["seen"] for r in rs)
    seen_h = __import__("datetime").date.fromisoformat(seen).strftime("%-d %B %Y")
    title = f"{name}: {money(best['now'])} at {best['retailer']} | Strikethrough"
    if len(title) > 65:
        title = f"{name} price check | Strikethrough"
    if len(title) > 65:
        title = f"{name} | Strikethrough"
    stores = f"{n} Australian stores" if n > 1 else best["retailer"]
    desc = clip(f"Is {name} at {money(best['now'])} a good deal? Lowest price we track is {money(best['now'])} at {best['retailer']} "
                f"({lab.lower()}), checked against price history and {stores}. Last checked {seen_h}.")
    if n > 1:
        verdict_line = (f"The lowest price we track is <b>{money(best['now'])} at {e(best['retailer'])}</b>, "
                        f"{money(hi - lo)} less than the highest ({money(hi)}). Our verdict: <span class=\"v {g}\">{e(lab)}</span>.")
    else:
        verdict_line = f"Tracked at <b>{e(best['retailer'])}</b> for <b>{money(best['now'])}</b>. Our verdict: <span class=\"v {g}\">{e(lab)}</span>."
    trs = []
    for r in rs:
        l2, g2 = LABEL.get(r["verdict"], (r["verdict"], "mid"))
        href, is_aff = affiliate(r)
        rel = "sponsored nofollow noopener" if is_aff else "nofollow noopener"
        go = f'<a href="{e(href)}" rel="{rel}" target="_blank">Shop</a>' if href else ""
        trs.append(f'<tr><td>{e(r["retailer"])}</td><td class="n"><b>{money(r["now"])}</b></td><td class="n">{money(r["was"])}</td>'
                   f'<td class="n">{round(r["real_pct"])}%</td><td><span class="v {g2}">{e(l2)}</span></td><td>{go}</td></tr>')
    # price history summary from the tracked series for the cheapest store
    hist = history.get(best["id"], [])
    hnote = ""
    if len(hist) >= 2:
        ph = [p[1] for p in hist]
        first = __import__("datetime").date.fromisoformat(hist[0][0][:10]).strftime("%-d %B")
        hnote = (f'<p class="m">We have tracked {e(best["retailer"])}\'s price since {first}: lowest {money(min(ph))}, '
                 f'highest {money(max(ph))}, now {money(best["now"])}.</p>')
    def note(r):
        extra = r.get("history_note") or ""
        txt = r.get("reason") or ""
        return txt + (" " + extra if extra and extra not in txt else "")
    reasons = "".join(f'<li>{e(r["retailer"])}: {e(note(r).strip())}</li>' for r in rs if note(r).strip())
    related = [k for k in sorted(keys_by_cat.get(cat, []), key=lambda k: -max(x["score"] for x in by_key[k])) if k != key][:6]
    rel_html = "".join(f'<a href="/price/{e(k)}/">{e(by_key[k][0]["product"])}<b>{money(min(x["now"] for x in by_key[k]))}</b></a>' for k in related)
    img = best.get("image") or ""
    pic = (f'<img src="{e(img)}" alt="{e(name)}" referrerpolicy="no-referrer" style="max-width:220px;border-radius:14px">' if img else "")
    prod = {"@context": "https://schema.org", "@type": "Product", "name": name, "brand": {"@type": "Brand", "name": best["brand"]},
            "category": cat, "url": f"{SITE}/price/{key}/",
            "offers": {"@type": "AggregateOffer", "priceCurrency": "AUD", "lowPrice": f"{lo:.2f}", "highPrice": f"{hi:.2f}", "offerCount": n,
                       "offers": [{"@type": "Offer", "price": f"{r['now']:.2f}", "priceCurrency": "AUD",
                                   "seller": {"@type": "Organization", "name": r["retailer"]}, **({"url": r["link"]} if r.get("link") else {})} for r in rs]}}
    if img:
        prod["image"] = img
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Strikethrough", "item": f"{SITE}/"},
        {"@type": "ListItem", "position": 2, "name": f"{cat} deals", "item": f"{SITE}/deals/{cslug}/"},
        {"@type": "ListItem", "position": 3, "name": name, "item": f"{SITE}/price/{key}/"}]}
    qas = [(f"What's the cheapest price for {name} in Australia right now?",
            f"{money(best['now'])} at {best['retailer']}, as of {seen_h}." + (f" Across the {n} stores we track, prices range from {money(lo)} to {money(hi)}." if n > 1 else ""))]
    before = [r for r in rs if r["verdict"] == "Cheaper before"]
    if before:
        b = before[0]
        qas.append((f"Has {name} been cheaper before?", f"Yes. {b['retailer']} has had it for less earlier this season. {b.get('reason') or ''}".strip()))
    elif len(hist) >= 2:
        qas.append((f"Has {name} been cheaper before?", f"Not in our tracking. {best['retailer']}'s lowest price since {first} is {money(min(ph))}, and it's {money(best['now'])} now."))
    if best.get("claimed_pct") and best.get("real_pct") is not None:
        same = abs(best["claimed_pct"] - best["real_pct"]) < 2
        qas.append((f"Is the advertised discount on {name} real?",
                    f"{best['retailer']} advertises {round(best['claimed_pct'])}% off. " + ("That matches what we measure against other stores' was-prices." if same else
                    f"Measured from the lowest was-price any store uses for this product, the real discount is {round(best['real_pct'])}%.")))
    ldjson = json.dumps([prod, crumbs, faq_ld(qas)], ensure_ascii=False).replace("</", "<\\/")
    has_aff = any(affiliate(r)[1] for r in rs)
    disc = f'<p class="fine">{e(aff.get("disclosure", ""))}</p>' if has_aff else ""
    page = f"""<!DOCTYPE html>
<html lang="en-AU"><head><meta charset="utf-8">
{GTM_HEAD}
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">{head_common()}
<link rel="canonical" href="{SITE}/price/{key}/"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="website"><meta property="og:url" content="{SITE}/price/{key}/"><meta property="og:image" content="{SITE}/og/{cslug}.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{SITE}/og/{cslug}.jpg">
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>{CSS}</style>
<script type="application/ld+json">{ldjson}</script></head><body>
{GTM_BODY}<div class="w">
<a class="logo" href="/">Strike<s>through</s></a>
<nav class="bc" aria-label="Breadcrumb"><a href="/">Home</a> › <a href="/deals/{cslug}/">{e(cat)}</a> › <span>{e(name)}</span></nav>
<h1>{e(name)}: is it a good deal?</h1>
<div class="sum"><div class="big">{money(best['now'])}</div><p class="m" style="margin-top:4px">{verdict_line}</p>{hnote}</div>
{pic}
<a class="cta" href="/#d-{e(top['slug'])}">See the price story and set a price-drop alert</a>
<h2 class="s">Prices at {'each store' if n > 1 else best['retailer']}</h2>
<table><thead><tr><th>Store</th><th>Now</th><th>Was</th><th>Real discount</th><th>Verdict</th><th></th></tr></thead><tbody>{''.join(trs)}</tbody></table>
<p class="m">Prices last checked <time datetime="{seen}">{e(seen_h)}</time>. "Real discount" is measured from the lowest was-price any store uses for this product, not each store's own.</p>
{f'<h2 class="s">Notes</h2><ul class="m">{reasons}</ul>' if reasons else ''}
{faq_html(qas)}
<h2 class="s">How we check</h2>
<p class="m">We compare the same product across Australian retailers and against its recent price history. A price more than 2% above the cheapest store is marked "Lower elsewhere". If one store's was-price is more than 10% above another's, we measure the discount from the lower one. <a href="/method/">More on our method</a>.</p>
{f'<h2 class="s">More {e(cat)} price checks</h2><div class="rel">{rel_html}</div>' if rel_html else ''}
{disc}
<p class="fine">Prices change through the day and may be member-only or colour-specific. Always confirm the price at checkout. Strikethrough is independent and isn't paid by the retailers listed. <a href="/method/">Method</a> · <a href="/privacy/">Privacy</a> · <a href="/terms/">Terms</a> · <a href="/contact/">Contact &amp; corrections</a></p>
</div></body></html>"""
    d = price_dir / key
    d.mkdir(exist_ok=True)
    (d / "index.html").write_text(page)
    made.add(key)
    urls.append(f"{SITE}/price/{key}/")

# remove product pages that are no longer tracked
for d in price_dir.iterdir():
    if d.is_dir() and d.name not in made:
        for f in d.iterdir():
            f.unlink()
        d.rmdir()

# ---- static links on the homepage (crawlable without JavaScript) ----
idx = HERE / "index.html"
ih = idx.read_text()
top_keys = sorted(by_key, key=lambda k: -max(x["score"] for x in by_key[k]))[:24]
links = ('<details class="fl"><summary>Browse deals by category</summary><p>'
         + " · ".join(f'<a href="/deals/{slugify(c)}/">{e(c)}</a>' for c in cats) + '</p></details>'
         + '<details class="fl"><summary>Popular price checks</summary><p>'
         + " · ".join(f'<a href="/price/{e(k)}/">{e(by_key[k][0]["product"])}</a>' for k in top_keys) + '</p></details>')
ng = sum(1 for r in rows if LABEL.get(r["verdict"], ("", ""))[1] == "good")
nf = sum(1 for r in rows if LABEL.get(r["verdict"], ("", ""))[1] == "flag")
nret = len({r["retailer"] for r in rows})
ih = re.sub(r'(<h1 class="disp" id="headline">).*?(</h1>)', lambda m: m.group(1) + f"{len(rows)} Black Friday deals checked. {ng} hold up." + m.group(2), ih, count=1, flags=re.S)
ih = re.sub(r'(<p class="lede" id="sub">).*?(</p>)', lambda m: m.group(1) + f"Every deal from {nret} Australian retailers, checked against price history and other stores. {nf} come with a catch. Prices last checked {latest_h}." + m.group(2), ih, count=1, flags=re.S)
ih = re.sub(r"<!--SEO-LINKS-->.*?<!--/SEO-LINKS-->", lambda m: "<!--SEO-LINKS-->" + links + "<!--/SEO-LINKS-->", ih, flags=re.S)
idx.write_text(ih)
print(len(made), "product pages")

# remove pages for categories that no longer exist
for d in (HERE / "deals").iterdir():
    if d.is_dir() and d.name not in {slugify(c) for c in cats}:
        for f in d.iterdir():
            f.unlink()
        d.rmdir()

urls += [f"{SITE}/{p}/" for p in ("method", "privacy", "terms", "contact")]
(HERE / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                  + "".join(f"  <url><loc>{u}</loc><lastmod>{latest}</lastmod></url>\n" for u in urls) + "</urlset>\n")
(HERE / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /share/\n\nSitemap: {SITE}/sitemap.xml\n")
print(len(cats), "category pages")
