// GET /api/resolve?u=<short link>: follows redirects for a few known link shorteners (Google app share links,
// Amazon short links) and returns where they end up, so the Check a deal box can read the real product page.
// Only those hosts are fetched, and only their redirect headers are read.
const SHORT = /^(search\.app|share\.google|g\.co|goo\.gl|amzn\.to|amzn\.asia|a\.co)$/i;
const json = (b, s = 200) => new Response(JSON.stringify(b), { status: s, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' } });

export async function onRequestGet({ request }) {
  let cur;
  try { cur = new URL(new URL(request.url).searchParams.get('u') || ''); } catch { return json({ ok: false }, 400); }
  if (!/^https?:$/.test(cur.protocol) || !SHORT.test(cur.hostname)) return json({ ok: false }, 400);
  for (let hop = 0; hop < 5 && SHORT.test(cur.hostname); hop++) {
    let res;
    try { res = await fetch(cur.toString(), { redirect: 'manual', headers: { 'User-Agent': 'Mozilla/5.0 (Linux; Android 14) Strikethrough link check' } }); } catch { return json({ ok: false }, 502); }
    let next = res.headers.get('location');
    if (!next && res.status === 200 && (res.headers.get('content-type') || '').includes('text/html')) {
      // Some shorteners answer 200 with a meta refresh or a JS redirect instead of a Location header.
      const html = (await res.text()).slice(0, 20000);
      const m = html.match(/http-equiv=["']?refresh["']?[^>]*url=([^"'>\s]+)/i) || html.match(/location(?:\.href)?\s*=\s*["']([^"']+)["']/i) || html.match(/<a[^>]+href=["'](https?:\/\/[^"']+)["']/i);
      next = m && m[1].replace(/&amp;/g, '&');
    }
    if (!next) break;
    try { cur = new URL(next, cur); } catch { break; }
  }
  if (SHORT.test(cur.hostname)) return json({ ok: false }, 404);
  return json({ ok: true, url: cur.toString().slice(0, 2000) });
}
