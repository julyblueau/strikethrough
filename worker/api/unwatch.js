// GET /api/unwatch?k=<watch key>&t=<token>: one-click unsubscribe from a price-drop alert.
const page = (msg, status = 200) => new Response(
  `<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Strikethrough</title>` +
  `<body style="font:16px/1.5 system-ui,sans-serif;background:#0b0b0c;color:#f5f5f7;display:grid;place-items:center;min-height:90vh;margin:0">` +
  `<div style="max-width:420px;padding:24px;text-align:center"><p style="font-size:22px;font-weight:700;margin:0 0 8px">Strikethrough</p><p>${msg}</p>` +
  `<p><a style="color:#ff5a4f" href="/">Back to the deals</a></p></div></body>`,
  { status, headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store', 'X-Robots-Tag': 'noindex' } });

export async function onRequestGet({ request, env }) {
  const u = new URL(request.url);
  const k = u.searchParams.get('k') || '', t = u.searchParams.get('t') || '';
  if (!env.SIGNUPS || !/^watch:[a-z0-9-]+:[a-z0-9]+$/.test(k)) return page('That link has expired.', 404);
  const { metadata } = await env.SIGNUPS.getWithMetadata(k);
  if (!metadata) return page("You're already unsubscribed from this alert.");
  if (metadata.t !== t) return page('That link has expired.', 404);
  await env.SIGNUPS.delete(k);
  return page("Done. You won't get any more alerts for this product.");
}
