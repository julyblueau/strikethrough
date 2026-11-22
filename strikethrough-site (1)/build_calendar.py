"""Retailer Black Friday 2026 sale windows and advertised discount depth.

Rows marked confirmed=Yes come from the retailer's own announcement or a dated
report of the live sale; the rest are ShopBack's editorial estimates from
prior-year patterns (retailers confirm terms close to the event).
"""
import json, pathlib, sys

SB = ("ShopBack – Black Friday 2026 sale calendar (estimates)",
      "https://www.shopback.com.au/blog/finance/australia-black-friday-2026-sale-calendar")
rows_in = [
    # retailer, sector, start, peak, min%, max%, confirmed, note, (source, url)
    ("Amazon AU", "Tech & appliances", "2026-11-17", "27–30 Nov", 20, 50, "Yes", "Sale runs 17–30 Nov", ("What Hi-Fi? – Amazon AU Black Friday", "https://www.whathifi.com/seasonal-sales/amazon-black-friday-sales-au")),
    ("The Good Guys", "Tech & appliances", "2026-11-19", "27 Nov", 15, 35, "No", "Price Beat button on many deals", SB),
    ("Kogan", "Tech & appliances", "2026-11-20", "27 Nov", 15, 50, "No", "Deepest prices for Kogan First members", SB),
    ("JB Hi-Fi", "Tech & appliances", "2026-11-23", "26–27 Nov", 15, 40, "No", "", SB),
    ("Harvey Norman", "Tech & appliances", "2026-11-23", "27–29 Nov", 20, 40, "No", "", SB),
    ("Officeworks", "Tech & appliances", "2026-11-23", "27–30 Nov", 15, 30, "No", "", SB),
    ("Bing Lee", "Tech & appliances", "2026-11-25", "27 Nov", 15, 35, "No", "Price-match focus", SB),
    ("eBay AU", "Marketplace", "2026-11-24", "27–30 Nov", 10, 30, "No", "Plus codes go deepest", SB),
    ("The Iconic", "Fashion & beauty", "2026-11-20", "27–29 Nov", 20, 50, "Yes", "'Hack Friday' window 20 Nov – 1 Dec", ("THE ICONIC – how to shop Black Friday", "https://www.theiconic.com.au/edition/how-to-shop-black-friday-advice")),
    ("ASOS AU", "Fashion & beauty", "2026-11-23", "27–30 Nov", 20, 60, "No", "", SB),
    ("Cotton On Group", "Fashion & beauty", "2026-11-23", "27 Nov", 30, 60, "No", "", SB),
    ("Uniqlo AU", "Fashion & beauty", "2026-11-23", "26–27 Nov", 15, 40, "No", "Select lines", SB),
    ("Country Road Group", "Fashion & beauty", "2026-11-25", "27–29 Nov", 25, 40, "No", "", SB),
    ("Myer", "Department store", "2026-11-25", "27–29 Nov", 20, 60, "No", "", SB),
    ("David Jones", "Department store", "2026-11-25", "27 Nov", 20, 50, "No", "Tiered spend bonuses", SB),
    ("Nike AU", "Sportswear", "2026-11-24", "27–30 Nov", 20, 40, "No", "Excludes many limited releases", SB),
    ("Adidas AU", "Sportswear", "2026-11-24", "27–30 Nov", 20, 40, "No", "", SB),
    ("lululemon AU", "Sportswear", "2026-11-27", "27–30 Nov", 10, 30, "No", "Select lines only", SB),
    ("Sephora / Mecca / Adore Beauty", "Fashion & beauty", "2026-11-24", "27–30 Nov", 15, 30, "No", "", SB),
    ("Chemist Warehouse", "Health & beauty", "2026-11-23", "27–29 Nov", 20, 50, "No", "", SB),
    ("Big W / Kmart / Target", "Discount department", "2026-11-23", "27 Nov", 15, 40, "No", "Toys and homewares deepest", SB),
    ("Koala", "Furniture & bedding", "2026-11-02", "to 30 Nov", 20, 35, "Yes", "Sale launched 2 Nov", ("Home Beautiful – Koala Black Friday 2026", "https://www.homebeautiful.com.au/shopping/koala-sales/")),
    ("Adairs", "Furniture & bedding", "2026-11-23", "27–30 Nov", 25, 50, "No", "Boxing Day usually deeper", SB),
    ("Freedom", "Furniture & bedding", "2026-11-23", "27–29 Nov", 20, 40, "No", "", SB),
    ("Amart Furniture", "Furniture & bedding", "2026-11-25", "27–29 Nov", 25, 40, "No", "", SB),
    ("BCF / Anaconda / Macpac / Kathmandu", "Outdoor", "2026-11-23", "27–29 Nov", 20, 50, "No", "Kathmandu better near Boxing Day", SB),
    ("Dan Murphy's / BWS / First Choice", "Liquor", "2026-11-24", "27–29 Nov", 15, 30, "No", "", SB),
]
rows = [{"retailer": r[0], "sector": r[1], "start": r[2], "peak": r[3],
         "min_pct": r[4], "max_pct": r[5], "confirmed": r[6], "note": r[7],
         "source": r[8][0], "source_url": r[8][1]} for r in rows_in]
rows.sort(key=lambda r: (r["start"], r["retailer"]))
meta = [{"label": "build_calendar.py", "value": pathlib.Path(__file__).read_text(), "type": "code", "lang": "python"}]
out = sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).parent / "calendar.json"
pathlib.Path(out).write_text(json.dumps({"rows": rows, "meta": meta}, ensure_ascii=False))
print(len(rows))
