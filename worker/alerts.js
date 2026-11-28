// Scheduled job: email people whose watched product is now cheaper than when they asked.
// Sends nothing until a RESEND_API_KEY secret is set (and ALERT_FROM, a sender on a domain verified in Resend).
const MAX_SENDS = 40; // stays well inside the free plan's per-run request limit
const SITE = 'https://strikethrough.com.au';
const money = (x) => '$' + Number(x).toLocaleString('en-AU', { minimumFractionDigits: x % 1 ? 2 : 0, maximumFractionDigits: 2 });
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

export function cheapestByProduct(rows) {
  const best = {};
  for (const r of rows) {
    if (!(r.now > 0)) continue;
    const b = best[r.product_key];
    if (!b || r.now < b.now) best[r.product_key] = r;
  }
  return best;
}

// A watch fires when the cheapest tracked price is at least 3% (and $1) under the price when it was set,
// and under the last price we already emailed about.
export function due(meta, row) {
  if (!row) return false;
  const ref = meta.l || meta.w;
  return row.now <= meta.w * 0.97 && meta.w - row.now >= 1 && row.now < ref * 0.995;
}

export function message(meta, row, key) {
  const unsub = `${SITE}/api/unwatch?k=${encodeURIComponent(key)}&t=${meta.t}`;
  const story = `${SITE}/#d-${row.slug}`;
  const subject = `Price drop: ${row.product} is now ${money(row.now)}`;
  const text = `${row.product} is now ${money(row.now)} at ${row.retailer}. You asked us to tell you when it dropped below ${money(meta.w)}.\n\n` +
    `Our verdict: ${row.verdict}. ${row.reason || ''}\n\nPrice story: ${story}\n\n` +
    `Strikethrough checks Australian deals against price history and other stores. It is independent and not paid by retailers.\n` +
    `Stop alerts for this product: ${unsub}`;
  const html = `<div style="font:15px/1.5 -apple-system,Segoe UI,sans-serif;color:#111;max-width:520px">` +
    `<p style="font-size:20px;font-weight:700;margin:0 0 6px">${esc(row.product)} is now ${money(row.now)}</p>` +
    `<p style="margin:0 0 14px">at ${esc(row.retailer)}. You asked us to tell you when it dropped below ${money(meta.w)}.</p>` +
    `<p style="margin:0 0 14px"><b>Our verdict:</b> ${esc(row.verdict)}. ${esc(row.reason || '')}</p>` +
    `<p><a href="${story}" style="display:inline-block;background:#e0362c;color:#fff;padding:10px 18px;border-radius:999px;text-decoration:none;font-weight:600">See the price story</a></p>` +
    `<p style="color:#666;font-size:12px;margin-top:24px">Strikethrough checks Australian deals against price history and other stores. It is independent and not paid by retailers. ` +
    `<a href="${unsub}" style="color:#666">Stop alerts for this product</a>.</p></div>`;
  return { subject, text, html, unsub };
}

export async function runAlerts(env, fetchImpl = fetch) {
  const out = { checked: 0, sent: 0, skipped: '' };
  if (!env.SIGNUPS) return { ...out, skipped: 'no storage' };
  if (!env.RESEND_API_KEY) return { ...out, skipped: 'no RESEND_API_KEY' };
  const res = await env.ASSETS.fetch(new Request(`${SITE}/data/deals.json`));
  if (!res.ok) return { ...out, skipped: 'no deals' };
  const best = cheapestByProduct((await res.json()).rows || []);
  let cursor;
  do {
    const page = await env.SIGNUPS.list({ prefix: 'watch:', cursor });
    for (const k of page.keys) {
      const meta = k.metadata; out.checked++;
      if (!meta || !due(meta, best[meta.p])) continue;
      if (out.sent >= MAX_SENDS) return out;
      const row = best[meta.p], m = message(meta, row, k.name);
      const r = await fetchImpl('https://api.resend.com/emails', {
        method: 'POST',
        headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          from: env.ALERT_FROM || 'Strikethrough <alerts@strikethrough.com.au>', to: [meta.e], subject: m.subject, text: m.text, html: m.html,
          headers: { 'List-Unsubscribe': `<${m.unsub}>`, 'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click' },
        }),
      });
      if (!r.ok) continue;
      out.sent++;
      await env.SIGNUPS.put(k.name, '', { metadata: { ...meta, l: row.now, s: new Date().toISOString() } });
    }
    cursor = page.list_complete ? undefined : page.cursor;
  } while (cursor);
  return out;
}
