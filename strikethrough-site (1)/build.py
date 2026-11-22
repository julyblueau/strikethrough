"""Build the Black Friday AU deal tracker dataset.

Reads raw_deals.json (deals collected from retailer pages and deal trackers),
checks each deal three ways, and writes deals.json as {rows, meta}.

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
import sys
from collections import defaultdict

HERE = pathlib.Path(__file__).parent
raw = json.loads((HERE / "raw_deals.json").read_text())
SOURCES = raw["sources"]
HOUSE = raw["house_brands"]
COLS = ["key", "product", "brand", "category", "retailer", "was", "now",
        "history", "prior_price", "note", "src"]

deals = [dict(zip(COLS, d)) for d in raw["deals"]]
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
    h = d["history"]
    if h == "higher_before":
        verdict = "Cheaper before"
        reason = d["note"] or "Tracked at a lower price before."
        if prior:
            reason = f"{d['note']}. Today's price is {money(now - prior)} above that."
    elif beaten:
        verdict = "Beaten elsewhere"
        reason = f"{best['retailer']} has it for {money(best_now)} — {money(now - best_now)} less."
    elif h == "low":
        verdict = "Record low"
        reason = d["note"] or "Lowest tracked price."
    elif h == "near_low":
        verdict = "Near record low"
        reason = d["note"] or "Close to the lowest tracked price."
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
        reason = d["note"] or "Hits this price often."
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
        "history_note": d["note"],
        "prior_price": prior,
        "source": src["name"], "source_url": src["url"], "seen": src["date"],
        "product_key": d["key"],
    })

rows.sort(key=lambda r: -r["score"])
meta = [
    {"label": "build.py", "value": pathlib.Path(__file__).read_text(), "type": "code", "lang": "python"},
    {"label": "Input", "value": "raw_deals.json"},
    {"label": "Deals", "value": str(len(rows))},
]
out = sys.argv[1] if len(sys.argv) > 1 else HERE / "deals.json"
pathlib.Path(out).write_text(json.dumps({"rows": rows, "meta": meta}, ensure_ascii=False))
from collections import Counter
print(len(rows), "rows")
print(Counter(r["verdict"] for r in rows))
print(Counter(r["was_check"].split(" (")[0] for r in rows))
