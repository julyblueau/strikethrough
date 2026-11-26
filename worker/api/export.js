// Cloudflare Pages Function: download sign-ups as CSV.
// GET /api/export?key=<EXPORT_KEY>[&form=verified-list|signup]
// Needs the SIGNUPS KV binding and an EXPORT_KEY secret (16+ characters) in the Pages project settings.
const cell = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;

export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);
  const key = url.searchParams.get('key') || '';
  if (!env.EXPORT_KEY || env.EXPORT_KEY.length < 16 || key !== env.EXPORT_KEY) return new Response('Not found', { status: 404 });
  if (!env.SIGNUPS) return new Response('Storage not configured', { status: 500 });
  const form = url.searchParams.get('form') || '';
  const rows = [];
  let cursor;
  do {
    const page = await env.SIGNUPS.list({ prefix: form ? `${form}:` : undefined, cursor });
    for (const k of page.keys) {
      const v = await env.SIGNUPS.get(k.name);
      if (v) rows.push(JSON.parse(v));
    }
    cursor = page.list_complete ? undefined : page.cursor;
  } while (cursor);
  rows.sort((a, b) => a.ts.localeCompare(b.ts));
  const cols = ['ts', 'form', 'email', 'type', 'name', 'company', 'country'];
  const csv = [cols.join(','), ...rows.map((r) => cols.map((c) => cell(r[c])).join(','))].join('\n');
  return new Response(csv, {
    headers: { 'Content-Type': 'text/csv; charset=utf-8', 'Content-Disposition': `attachment; filename="strikethrough-signups${form ? '-' + form : ''}.csv"`, 'Cache-Control': 'no-store' },
  });
}
