#!/usr/bin/env python3
"""Builds the privacy, terms and contact pages (privacy/, terms/, contact/). Edit the text here and re-run."""
import os, html

UPDATED = "29 November 2026"
OPERATOR = "Cameron Gibbens"
EMAIL = "hello@strikethrough.com.au"
SITE = "https://strikethrough.com.au"

CSS = """:root{color-scheme:dark;--bg:#0a0a0b;--ink:#f5f5f7;--mute:#a1a1a6;--line:#26262a;--soft:#141416;--red:#ff453a}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.65 Inter,system-ui,-apple-system,Segoe UI,sans-serif}
a{color:var(--ink)}header{border-bottom:1px solid var(--line)}.wrap{max-width:760px;margin:0 auto;padding:0 20px}
header .wrap{display:flex;align-items:center;justify-content:space-between;min-height:60px}
.logo{font:800 22px "Inter Tight",Inter,sans-serif;text-decoration:none;color:var(--ink)}.logo s{text-decoration-color:var(--red);text-decoration-thickness:3px}
main{padding:36px 0 60px}h1{font:800 clamp(30px,5vw,44px)/1.1 "Inter Tight",Inter,sans-serif;margin:0 0 6px}
h2{font:700 20px/1.3 "Inter Tight",Inter,sans-serif;margin:34px 0 8px}p,li{color:#d8d8dc}ul{padding-left:20px}
.meta{color:var(--mute);font-size:14px;margin:0 0 24px}.box{border:1px solid var(--line);background:var(--soft);border-radius:16px;padding:14px 16px;margin:18px 0}
footer{border-top:1px solid var(--line);padding:22px 0;color:var(--mute);font-size:14px}footer a{color:var(--mute);margin-right:16px}"""

def page(slug, title, desc, body):
    return f"""<!doctype html>
<html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} | Strikethrough</title><meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{SITE}/{slug}/"><meta name="theme-color" content="#0a0a0b">
<link rel="icon" href="/icons/icon-192.png"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@700;800&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<header><div class="wrap"><a class="logo" href="/">Strike<s>through</s></a><a href="/">Back to the deals</a></div></header>
<main><div class="wrap"><h1>{html.escape(title)}</h1><p class="meta">Last updated {UPDATED}</p>
{body}
</div></main>
<footer><div class="wrap"><a href="/privacy/">Privacy</a><a href="/terms/">Terms</a><a href="/contact/">Contact &amp; corrections</a><br>Strikethrough is an independent project run by {OPERATOR}.</div></footer>
</body></html>
"""

M = f'<a href="mailto:{EMAIL}">{EMAIL}</a>'

PRIVACY = f"""
<p>Strikethrough ("we", "us") is an independent deal-checking site run by {OPERATOR} in Melbourne, Australia. This policy explains what personal information we collect, why, and what you can do about it. Questions go to {M}.</p>

<h2>What we collect</h2>
<ul>
<li><b>Email sign-ups.</b> If you join a list or register interest in Strikethrough Pro, we keep your email address and anything else you choose to give in that form (such as your name, company or whether you're a shopper or a retailer), plus the date and the country your connection came from.</li>
<li><b>Price-drop alerts.</b> If you ask us to tell you when a product gets cheaper, we keep your email address, the product, the price at the time and when we last emailed you about it.</li>
<li><b>"Check a deal" requests.</b> What you type or paste into the Check a deal box is matched against our list in your browser and isn't sent to us, with two exceptions. If you ask us to check a product we don't track, we keep what you entered, any price, and your email if you give one. If you paste a shortened link (for example from the Google app or an Amazon short link), we send that link to our server to find the page it points to. We don't keep it.</li>
<li><b>Analytics.</b> We use Google Analytics (through Google Tag Manager), which uses cookies and similar technology to record how the site is used: pages viewed, the device and browser, approximate location, how you arrived, and actions such as clicking through to a retailer, running a check or signing up. We use this to see what's useful and improve the site. We don't use Google's advertising features with it.</li>
<li><b>Stored on your device.</b> The site saves a few things in your own browser only, such as the deals you've added to compare, whether you've closed a banner, and your email so you don't have to retype it. You can clear these in your browser settings.</li>
<li><b>Server logs.</b> Our hosting provider, Cloudflare, processes technical information such as IP addresses to deliver the site and protect it from abuse.</li>
</ul>

<h2>How we use it</h2>
<p>To send you what you asked for (alerts, list emails, a reply to your check request), to run and improve the site, and to keep it secure. We don't sell or rent your personal information, and we don't share it with retailers.</p>

<h2>Who else handles it</h2>
<p>We use a small number of service providers to run the site:</p>
<ul>
<li><b>Cloudflare</b> hosts the site and stores form submissions.</li>
<li><b>Google</b> provides analytics.</li>
<li><b>An email delivery service</b> (Resend) sends price-drop alerts once alerts are switched on.</li>
</ul>
<p>These providers may store or process information outside Australia, including in the United States. We only give them what they need to provide their service.</p>

<h2>Affiliate links</h2>
<p>Some links to retailers are affiliate links. When you click one, that retailer (for example Amazon) may set its own cookies to record the referral. That's handled under the retailer's own privacy policy, not this one. Affiliate commissions never change a verdict or a score.</p>

<h2>Emails and unsubscribing</h2>
<p>We only email you about what you signed up for. Every alert and list email has an unsubscribe link, and we act on unsubscribe requests straight away (and always within five working days). You can also email {M}.</p>

<h2>How long we keep it</h2>
<p>We keep list sign-ups and alerts until you unsubscribe or ask us to delete them. We keep check requests for up to 12 months.</p>

<h2>Your choices</h2>
<ul>
<li>Ask to see, correct or delete the personal information we hold about you by emailing {M}.</li>
<li>Opt out of Google Analytics with Google's <a href="https://tools.google.com/dlpage/gaoptout" rel="noopener">browser add-on</a>, or by blocking cookies in your browser.</li>
</ul>

<h2>Security</h2>
<p>We keep only what we need. Form submissions are stored with our hosting provider, and only Strikethrough can access the export. No system is perfectly secure, but we take reasonable steps to protect what we hold.</p>

<h2>Complaints</h2>
<p>If you have a concern about how we've handled your information, email {M} and we'll respond within 30 days. If you're not satisfied, you can contact the Office of the Australian Information Commissioner at <a href="https://www.oaic.gov.au" rel="noopener">oaic.gov.au</a>.</p>

<h2>Changes</h2>
<p>We'll update this page if what we collect or how we use it changes, and change the date at the top.</p>
"""

TERMS = f"""
<p>These terms apply to your use of strikethrough.com.au, run by {OPERATOR} ("Strikethrough", "we"). By using the site you agree to them.</p>

<h2>What the site does</h2>
<p>Strikethrough checks advertised deals from Australian retailers against price history and the same product at other stores, and gives each deal a verdict and a score. It's general information to help you compare prices. It isn't financial or purchasing advice, and it doesn't take your circumstances into account.</p>

<h2>Prices and accuracy</h2>
<p>Prices come from retailer websites, catalogues, published deal reports and community sites, and are checked at the times shown on the site. Prices, stock and offers change quickly and can differ by colour, size, membership or location. We work to keep information accurate, but it may be out of date or wrong. <b>Always confirm the price and details with the retailer before you buy.</b></p>

<h2>Our verdicts</h2>
<p>Verdicts such as "Record low", "Lower elsewhere" or "Was-price unconfirmed" are our assessment, made by the method described in <a href="/#how">How we check a deal</a>, using the information available to us on the date shown. A verdict compares prices. It isn't a statement that any retailer has acted unlawfully or intended to mislead. If you think a verdict is wrong, please tell us. See <a href="/contact/">Contact &amp; corrections</a>.</p>

<h2>Independence and affiliate links</h2>
<p>Strikethrough is independent. Retailers don't pay for verdicts, placement or scores. Some links are affiliate links, so we may earn a commission if you buy, at no extra cost to you. As an Amazon Associate, Strikethrough earns from qualifying purchases. Commissions never change a verdict or a score.</p>

<h2>Retailers and trademarks</h2>
<p>Strikethrough isn't affiliated with, endorsed by or sponsored by any retailer or brand on the site. Product names, brand names and retailer names are trademarks of their owners and are used only to identify the products and stores being compared.</p>

<h2>Alerts and emails</h2>
<p>Price-drop alerts and other emails are a free, best-efforts service. We can't guarantee that every price change will be caught or that an email will arrive before an offer ends.</p>

<h2>Using the site</h2>
<p>Please don't misuse the site, for example by sending automated or abusive requests, submitting false information through the forms, or trying to get around its security. We may block access that harms the site or other users.</p>

<h2>Liability</h2>
<p>Nothing in these terms excludes, restricts or modifies any right or remedy you have under the Australian Consumer Law or other law that can't be excluded. Otherwise, to the extent the law allows, the site is provided "as is", and we aren't liable for any loss arising from your use of the site or reliance on its information, including a purchase you make or don't make.</p>

<h2>Changes and governing law</h2>
<p>We may update these terms, and the date at the top will change when we do. These terms are governed by the laws of Victoria, Australia.</p>

<h2>Contact</h2>
<p>{M}</p>
"""

CONTACT = f"""
<p>Strikethrough is an independent project run by {OPERATOR} in Melbourne. The best way to reach us is by email: {M}.</p>

<div class="box"><b>Retailers and brands: corrections</b><br>
If you think a price, a was-price or a verdict about one of your products is wrong, email {M} with the product, the page or link on our site, and what's incorrect (a screenshot or a link to the current price helps). We aim to review corrections within two business days, and we'll update or remove anything we can't support. Corrections are free. We don't accept payment to change a verdict.</div>

<h2>Shoppers</h2>
<p>Spotted a deal we should check, or a price that's changed? Use the Check a deal box on the <a href="/">home page</a>, or email us.</p>

<h2>Strikethrough Pro</h2>
<p>For daily tracking of how competitors discount, see <a href="/#pro">Strikethrough Pro</a> or email us.</p>

<h2>Media</h2>
<p>For data, comment or the methodology behind the numbers, email {M}.</p>

<h2>Your data</h2>
<p>To unsubscribe, see or delete the information we hold about you, email us or see the <a href="/privacy/">privacy policy</a>.</p>
"""

for slug, title, desc, body in (
    ("privacy", "Privacy policy", "What personal information Strikethrough collects, why, and your choices.", PRIVACY),
    ("terms", "Terms of use", "The terms for using Strikethrough, an independent Australian deal checker.", TERMS),
    ("contact", "Contact & corrections", "Contact Strikethrough, or ask for a correction to a price or verdict.", CONTACT),
):
    os.makedirs(slug, exist_ok=True)
    open(f"{slug}/index.html", "w").write(page(slug, title, desc, body))
print("built privacy/, terms/, contact/")
