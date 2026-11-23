"""Render 1200x630 social share cards to og/*.jpg (home + one per category).

Text is evergreen so the cards don't go stale between data refreshes.
Needs playwright + Chromium. Run: python3 make_og.py
"""
import asyncio, html, json, os, pathlib, re

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "og"
OUT.mkdir(exist_ok=True)

GLOW = {'TVs & Home Theatre':'#5e5ce6','Headphones & Audio':'#ff7a3d','Computing & Gaming':'#0a84ff','Tablets & eReaders':'#30b06a','Phones & Wearables':'#ff375f','Smart Home':'#3aa8d8','Coffee Machines':'#c2752a','Kitchen Appliances':'#ff453a','Vacuums & Floorcare':'#8e5cf0','Hair & Beauty Tools':'#e0457a','Personal Care':'#3ab8c8','Air & Climate':'#2f8fd8','Cameras':'#ff8a1f','Furniture & Bedding':'#5fb83a','Fashion & Footwear':'#ff4f6a','Toys & LEGO':'#e0b400','Large Appliances':'#4a7fd8'}


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def card(title, sub, art, glow):
    svg = (ROOT / "art" / f"{art}.svg").read_text() if art else ""
    art_html = f'<div class="art">{svg}</div>' if svg else '<div class="tickets">' + "".join(
        f'<i class="{c}"></i>' for c in ("g", "m", "g", "f", "g", "m", "f", "g", "g", "m", "g", "f", "m", "g", "g", "f", "g", "m", "g", "g", "m", "f", "g", "m")) + "</div>"
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0}}
body{{width:1200px;height:630px;background:radial-gradient(ellipse 55% 70% at 80% 50%,{glow}55 0%,transparent 70%),#0a0a0b;color:#f5f5f7;font-family:Inter,sans-serif;display:grid;grid-template-columns:1fr 470px;align-items:center;padding:0 70px;gap:30px;overflow:hidden}}
.logo{{font:700 40px 'Inter Display',Inter;letter-spacing:-.03em;position:relative;display:inline-block}}
.logo s{{text-decoration:none;position:relative}}
.logo s::after{{content:"";position:absolute;left:-3px;right:-3px;top:52%;height:5px;background:#ff453a;transform:rotate(-4deg)}}
h1{{font:700 66px/1.02 'Inter Display',Inter;letter-spacing:-.035em;margin:34px 0 22px}}
p{{font-size:26px;line-height:1.35;color:#a1a1a6;max-width:26ch}}
.url{{margin-top:34px;font-size:22px;font-weight:600;color:#f5f5f7;display:inline-flex;gap:10px;align-items:center}}
.url b{{background:#ff453a;color:#fff;border-radius:999px;padding:6px 16px;font-size:20px}}
.art svg{{width:470px;height:auto;filter:drop-shadow(0 24px 34px rgba(0,0,0,.5))}}
.tickets{{display:grid;grid-template-columns:repeat(6,1fr);gap:12px}}
.tickets i{{height:74px;border-radius:6px 6px 12px 12px;display:block;position:relative}}
.tickets i::before{{content:"";position:absolute;left:50%;top:10px;width:10px;height:10px;margin-left:-5px;border-radius:50%;background:#0a0a0b}}
.tickets .g{{background:#30d158;box-shadow:0 0 24px rgba(48,209,88,.35)}}
.tickets .m{{box-shadow:inset 0 0 0 3px #636366}}
.tickets .f{{background:rgba(255,69,58,.15);box-shadow:inset 0 0 0 3px #ff453a}}
.tickets .f::after{{content:"";position:absolute;left:5px;right:5px;top:58%;height:4px;background:#ff453a;transform:rotate(-30deg)}}
</style></head><body><div>
<div class="logo">Strike<s>through</s></div>
<h1>{html.escape(title)}</h1><p>{html.escape(sub)}</p>
<div class="url">strikethrough.com.au <b>Black Friday 2026</b></div>
</div>{art_html}</body></html>"""


async def main():
    from playwright.async_api import async_playwright
    rows = json.load(open(ROOT / "data" / "deals.json"))["rows"]
    cats = sorted({r["category"] for r in rows})
    jobs = [("home", card("Which Black Friday deals are actually real?",
                          "Every was-price checked against price history and other Australian retailers.", None, "#ff453a"))]
    for c in cats:
        s = slugify(c)
        jobs.append((s, card(f"{c}: Black Friday deals, checked",
                             "See which discounts hold up, and where it's cheaper.", s if (ROOT / "art" / f"{s}.svg").exists() else None, GLOW.get(c, "#5e5ce6"))))
    async with async_playwright() as p:
        exe = "/usr/bin/google-chrome" if os.path.exists("/usr/bin/google-chrome") else None
        b = await p.chromium.launch(executable_path=exe) if exe else await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1200, "height": 630})
        for name, doc in jobs:
            await pg.set_content(doc)
            await pg.wait_for_timeout(80)
            await pg.screenshot(path=str(OUT / f"{name}.jpg"), type="jpeg", quality=86)
        await b.close()
    print(f"{len(jobs)} cards written to og/")


if __name__ == "__main__":
    asyncio.run(main())
