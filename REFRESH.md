# Twice-daily deal refresh (runbook)

Run from the Strikethrough working session (repo at /home/claude/strikethrough, push access already set up).
Stop after 1 December 2026 (Australia/Sydney).

1. `git pull --rebase origin main`.
2. Research changes with WebSearch/WebFetch: re-fetch the pages in raw_deals.json "sources" (newest first) and search for new live Black Friday deals at JB Hi-Fi, Harvey Norman, The Good Guys, Amazon AU, Kogan, Myer, David Jones, The Iconic, Big W, Kmart, Target, Bing Lee, Adairs, Officeworks, Chemist Warehouse. Retailer catalogues (catalogue.jbhifi.com.au) are primary sources. Prefer pages from the last 48 hours.
3. OzBargain: WebFetch https://www.ozbargain.com.au/deals (page 2: ?page=1). Update "community" entries `"<key>|<retailer>"` = {votes, url (real /node/NNNN), posted, checked} for deals we track; add new deals from 100+ vote posts that state both sale and was/RRP price (source "OZB"). Skip vouchers, cashback, subscriptions, energy/telco, overseas stores.
4. Edit raw_deals.json (indent=2): row = [key, product, brand, category, retailer, was, now, history, prior_price, note, source_key, url?, image?].
   - Price rose since last run → history "higher_before", prior_price = old price, note "Was $X on <date>".
   - Price fell to a stated record low → history "low" with the source's wording in the note.
   - Reuse keys across retailers; add sources with today's date; retailers block only with URLs actually seen.
   - Remove ended deals. Existing categories only. Neutral wording, never "fake/misleading/scam".
4b. Today's best 3: check data/featured.json. Its ids (product_key@Retailer) must still be live and 'Record low'/'Cheapest tracked'; swap in stronger, cross-checked deals across 3 different categories and retailers when better ones appear, and update "updated".
5. Never edit affiliates.json (holds the Amazon tag strikethrough-22). `python3 build.py && python3 build_calendar.py && python3 build_pages.py`. Don't hand-edit data/history.json.
6. Commit "Deal data refresh <YYYY-MM-DD HH:MM AEDT>" (with the session attribution lines) and push to origin main. The site is on Cloudflare Workers (no deploy limit); the push deploys strikethrough.com.au within a couple of minutes. Cameron approved pushing live on 27 Nov. If the push fails, retry once, then report it.
7. (Optional) Publish the same files to the preview artifact 01eeea10-df26-478c-a70e-f1a30ea58e4a. Skip if it waits on an approval.
8. Report to Cameron: deal and retailer counts, what was added (with OzBargain votes), notable price moves (record lows, prices that went up), sales that opened, and that the push to the live site succeeded.
