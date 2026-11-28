#!/usr/bin/env python3
"""Fetch OzBargain's public deals RSS feed and save a small JSON summary to data/ozb_feed.json.

Run by .github/workflows/ozbargain.yml every few hours. The site uses it to keep OzBargain vote
counts current, and the twice-daily refresh reads it for new deals. Standard library only.
"""
import json, re, sys, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

FEEDS = ["https://www.ozbargain.com.au/deals/feed"]
OUT = "data/ozb_feed.json"
OZB = "{https://www.ozbargain.com.au}"
DC = "{http://purl.org/dc/elements/1.1/}"

def num(v):
    try: return int(v)
    except (TypeError, ValueError): return 0

def parse(xml_bytes):
    root = ET.fromstring(xml_bytes)
    items = []
    for it in root.iter("item"):
        link = (it.findtext("link") or "").strip()
        m = re.search(r"/node/(\d+)", link)
        meta = it.find(OZB + "meta")
        a = meta.attrib if meta is not None else {}
        title = (it.findtext("title") or "").strip()
        when = it.findtext("pubDate") or ""
        try: when = parsedate_to_datetime(when).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception: pass
        items.append({
            "node": m.group(1) if m else "",
            "title": title[:300],
            "link": link,
            "url": a.get("url", ""),
            "votes": num(a.get("votes-pos")),
            "votes_neg": num(a.get("votes-neg")),
            "comments": num(a.get("comment-count")),
            "expiry": a.get("expiry", ""),
            "categories": [c.text for c in it.findall("category") if c.text][:5],
            "posted": when,
        })
    return items

def main():
    try:
        old = json.load(open(OUT))
    except Exception:
        old = {"items": []}
    by_node = {i["node"]: i for i in old.get("items", []) if i.get("node")}
    got = 0
    for url in FEEDS:
        req = urllib.request.Request(url, headers={"User-Agent": "Strikethrough deal checker (strikethrough.com.au)"})
        with urllib.request.urlopen(req, timeout=30) as r:
            for i in parse(r.read()):
                if i["node"]:
                    by_node[i["node"]] = i; got += 1
    if not got:
        print("feed returned no items; leaving file unchanged"); return 1
    items = sorted(by_node.values(), key=lambda i: i.get("posted", ""), reverse=True)[:300]
    if [ (i["node"], i["votes"]) for i in items ] == [ (i.get("node"), i.get("votes")) for i in old.get("items", []) ]:
        print("no changes"); return 0
    json.dump({"fetched": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "source": "OzBargain deals RSS", "items": items},
              open(OUT, "w"), indent=1, ensure_ascii=False)
    print(f"saved {len(items)} items ({got} from feed)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
