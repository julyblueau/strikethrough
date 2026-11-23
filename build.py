"""Build the Black Friday AU deal tracker dataset.

Reads raw_deals.json (deals collected from retailer pages and deal trackers),
checks each deal three ways, and writes deals.json as {rows, meta} (for the
dashboard), data/deals.json as {rows} (for the site) and appends to
data/history.json, Strikethrough's own record of every price it has seen.

Checks:
  1. Price history  - what the tracking source says about past prices
                      (record low, near low, cheaper before, regular repeat).
  2. Cross-retailer - is the same product cheaper at another tracked retailer?
  3. Was-price      - is this retailer's "was" price more than 10% above the
                      lowest "was" price quoted by another retailer for the same
                      product? (a sign the claimed discount is padded)

Real discount = 1 - now / reference, where reference is the lower of:
  - the lowest "was" price any tracked retailer quotes for the product
  - a known recent typical price, when the source gives one
"""
import json
import pathlib
import re
import sys
import datetime
import urllib.parse
from collections import defaultdict
from zoneinfo import ZoneInfo

HERE = pathlib.Path(__file__).parent
raw = json.loads((HERE / "raw_deals.json").read_text())
SOURCES = raw["sources"]
HOUSE = raw["house_brands"]
COLS = ["key", "product", "brand", "category", "retailer", "was", "now",
        "history", "prior_price", "note", "src"]

RETAILERS = raw.get("retailers", {})
deals = [dict(zip(COLS + ["url", "image"], d + [""] * (13 - len(d)))) for d in raw["deals"]]
RUN = datetime.datetime.now(ZoneInfo("Australia/Sydney"))
RUN_TS = RUN.strftime("%Y-%m-%dT%H:%M")
HIST_PATH = HERE / "data" / "history.json"
HISTORY = json.loads(HIST_PATH.read_text()) if HIST_PATH.exists() else {}

def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def link_for(d):
    """Best link to the deal at the retailer: exact product page, else retailer search, else retailer page."""
    r = RETAILERS.get(d["retailer"], {})
    if d["url"]:
        return d["url"], f"View at {d['retailer']}", "product"
    if r.get("search"):
        return r["search"].replace("{q}", urllib.parse.quote_plus(d["product"])), f"Find it at {d['retailer']}", "search"
    if r.get("home"):
        return r["home"], r.get("home_label") or f"Shop {d['retailer']}", "store"
    return "", "", ""
by_key = defaultdict(list)
for d in deals:
    by_key[d["key"]].append(d)

INFLATE = 1.10      # was-price more than 10% above the lowest elsewhere
BEATEN = 1.02       # now-price more than 2% above the cheapest elsewhere
CHECK_RRP = 0.65    # claimed discount this deep with no history behind it

def money(x):
    return f"${x:,.0f}" if x >= 100 else f"${x:,.2f}"

rows = []
for d in deals:
    peers = by_key[d["key"]]
    others = [p for p in peers if p is not d]
    was, now = float(d["was"]), float(d["now"])
    claimed = 1 - now / was
    min_was = min(float(p["was"]) for p in peers)
    best = min(peers, key=lambda p: float(p["now"]))
    best_now = float(best["now"])
    prior = float(d["prior_price"]) if d["prior_price"] else None
    did = f"{d['key']}@{d['retailer']}"
    note = d["note"]
    h = d["history"]
    # our own tracked history can override "no history" from the sources
    past = [pt for pt in HISTORY.get(did, []) if pt[0] != RUN_TS]
    if past:
        lowest = min(past, key=lambda pt: pt[1])
        days = {pt[0][:10] for pt in past}
        if lowest[1] < now * 0.99 and h != "higher_before":
            h, prior = "higher_before", float(lowest[1])
            when = datetime.date.fromisoformat(lowest[0][:10]).strftime("%-d %b")
            note = f"Strikethrough tracked it at {money(lowest[1])} on {when}"
        elif len(past) >= 3 and len(days) >= 2 and now <= lowest[1] and h in ("none", "repeat"):
            h = "low"
            first = datetime.date.fromisoformat(min(days)).strftime("%-d %b")
            note = f"Lowest price Strikethrough has tracked since {first}"
    house = d["brand"] in HOUSE.get(d["retailer"], [])

    reference = min_was
    ref_basis = "Lowest was-price across retailers" if others else "Retailer's was-price"
    if prior and d["history"] == "near_low" and prior < reference:
        reference, ref_basis = prior, "Recent typical price"
    real = 1 - now / reference

    # was-price check
    if others:
        if was > min_was * INFLATE:
            low_was_r = min(others, key=lambda p: float(p["was"]))
            was_check = f"Inflated vs {low_was_r['retailer']} ({money(float(low_was_r['was']))})"
        else:
            was_check = "Consistent across retailers"
    elif house:
        was_check = "House brand — can't cross-check"
    else:
        was_check = "Single retailer"

    # verdict, first rule that applies wins
    beaten = bool(others) and now > best_now * BEATEN
    if h == "higher_before":
        verdict = "Cheaper before"
        reason = note or "Tracked at a lower price before."
        if prior:
            reason = f"{note}. Today's price is {money(now - prior)} above that."
    elif beaten:
        verdict = "Beaten elsewhere"
        reason = f"{best['retailer']} has it for {money(best_now)} — {money(now - best_now)} less."
    elif h == "low":
        verdict = "Record low"
        reason = note or "Lowest tracked price."
    elif h == "near_low":
        verdict = "Near record low"
        reason = note or "Close to the lowest tracked price."
    elif others and best is d and real >= 0.10:
        verdict = "Cheapest tracked"
        reason = f"Lowest price of the {len(peers)} retailers tracked for this product."
    elif house and claimed >= 0.40:
        verdict = "Check the RRP"
        reason = "Retailer's own brand, so there's no other store to compare the was-price against."
    elif claimed >= CHECK_RRP:
        verdict = "Check the RRP"
        reason = f"Advertised at {claimed:.0%} off. We haven't found price history or another retailer to confirm the was-price yet."
    elif real < 0.10:
        verdict = "Token discount"
        reason = f"Only {real:.0%} below the reference price."
    elif h == "repeat":
        verdict = "Regular price drop"
        reason = note or "Hits this price often."
    else:
        verdict = "Unverified"
        reason = "Discount measured against the quoted was-price. No price history or second retailer found yet."
    reason = reason.strip()
    if reason and reason[-1] not in ".!?":
        reason += "."
    if others and not beaten and verdict not in ("Cheaper before", "Cheapest tracked"):
        if len(peers) > 1 and best is d:
            reason += f" Cheapest of {len(peers)} retailers tracked."
    if was_check.startswith("Inflated"):
        lw = min(others, key=lambda p: float(p["was"]))
        reason += f" Its was-price is {was / float(lw['was']) - 1:.0%} higher than at {lw['retailer']} ({money(float(lw['was']))}), so we measure the discount from {money(float(lw['was']))}."

    base = {"Record low": 72, "Near record low": 62, "Cheapest tracked": 52, "Regular price drop": 42,
            "Unverified": 38, "Check the RRP": 22, "Token discount": 12,
            "Beaten elsewhere": 18, "Cheaper before": 14}[verdict]
    span = {"Record low": 28, "Near record low": 28, "Cheapest tracked": 26, "Regular price drop": 20,
            "Unverified": 24}.get(verdict, 8)
    score = base + span * max(0.0, min(real / 0.5, 1.0))
    if was_check.startswith("Inflated"):
        score -= 8
    score = int(round(max(0, min(100, score))))

    src = SOURCES[d["src"]]
    rows.append({
        "id": f"{d['key']}@{d['retailer']}",
        "product": d["product"], "brand": d["brand"], "category": d["category"],
        "retailer": d["retailer"],
        "was": round(was, 2), "now": round(now, 2),
        "claimed_pct": round(claimed * 100, 1),
        "reference": round(reference, 2), "reference_basis": ref_basis,
        "real_pct": round(real * 100, 1),
        "verdict": verdict, "score": score, "was_check": was_check,
        "reason": reason.strip(),
        "retailers_tracked": len(peers),
        "best_price": round(best_now, 2), "best_retailer": best["retailer"],
        "history_note": note,
        "prior_price": prior,
        "source": src["name"], "source_url": src["url"], "seen": src["date"],
        "product_key": d["key"],
        "slug": slugify(d["key"] + "-" + d["retailer"]),
        "image": d["image"] if str(d["image"]).startswith("https://") else "",
        "link": link_for(d)[0], "link_label": link_for(d)[1], "link_kind": link_for(d)[2],
        "tracked_since": (HISTORY.get(did) or [[RUN_TS]])[0][0][:10],
    })

rows.sort(key=lambda r: -r["score"])
meta = [
    {"label": "build.py", "value": pathlib.Path(__file__).read_text(), "type": "code", "lang": "python"},
    {"label": "Input", "value": "raw_deals.json"},
    {"label": "Deals", "value": str(len(rows))},
]
# record this run in our own price history (one point per run when the price moved or 11+ hours passed)
for r in rows:
    pts = HISTORY.setdefault(r["id"], [])
    if not pts or pts[-1][1] != r["now"] or (RUN - datetime.datetime.fromisoformat(pts[-1][0]).replace(tzinfo=RUN.tzinfo)).total_seconds() > 11 * 3600:
        if not pts or pts[-1][0] != RUN_TS:
            pts.append([RUN_TS, r["now"]])
live = {r["id"] for r in rows}
HIST_PATH.parent.mkdir(exist_ok=True)
HIST_PATH.write_text(json.dumps({k: v for k, v in HISTORY.items() if k in live}, separators=(",", ":")))
(HERE / "data" / "deals.json").write_text(json.dumps({"rows": rows}, ensure_ascii=False))
out = sys.argv[1] if len(sys.argv) > 1 else HERE / "deals.json"
pathlib.Path(out).write_text(json.dumps({"rows": rows, "meta": meta}, ensure_ascii=False))
from collections import Counter
print(len(rows), "rows")
print(Counter(r["verdict"] for r in rows))
print(Counter(r["was_check"].split(" (")[0] for r in rows))
