// Stores sign-ups, check requests and price watches from the site's forms in Workers KV (binding SIGNUPS).
const EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
const LIST_FORMS = new Set(['verified-list', 'signup']);

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' } });
const str = (d, k, n) => String(d.get(k) || '').trim().slice(0, n);

export async function onRequestPost({ request, env }) {
  if (!env.SIGNUPS) return json({ ok: false, error: 'storage not configured' }, 500);
  let data;
  try { data = await request.formData(); } catch { return json({ ok: false, error: 'bad request' }, 400); }
  if ((data.get('bot-field') || '').trim()) return json({ ok: true }); // honeypot: pretend success
  const form = str(data, 'form-name', 40);
  const email = str(data, 'email', 200).toLowerCase();
  const ts = new Date().toISOString();
  const id = crypto.randomUUID().slice(0, 8);
  const country = (request.cf && request.cf.country) || '';

  if (LIST_FORMS.has(form)) {
    if (!EMAIL.test(email)) return json({ ok: false, error: 'invalid' }, 400);
    const rec = { form, email, ts, type: str(data, 'type', 60), name: str(data, 'name', 120), company: str(data, 'company', 120), country };
    await env.SIGNUPS.put(`${form}:${ts}:${id}`, JSON.stringify(rec));
    return json({ ok: true });
  }

  if (form === 'check-request') {
    // "We don't track this yet - check it for me". Email is optional.
    const query = str(data, 'query', 300);
    if (!query || (email && !EMAIL.test(email))) return json({ ok: false, error: 'invalid' }, 400);
    const price = Number(str(data, 'price', 20).replace(/[^0-9.]/g, '')) || '';
    const rec = { form, email, ts, query, price, country };
    await env.SIGNUPS.put(`${form}:${ts}:${id}`, JSON.stringify(rec));
    return json({ ok: true });
  }

  if (form === 'watch') {
    // Price-drop alert. The record lives in KV metadata so the alert job can read every watch from one list call.
    const product = str(data, 'product', 120);
    const deal = str(data, 'deal', 160);
    const price = Number(str(data, 'price', 20));
    if (!EMAIL.test(email) || !/^[a-z0-9-]+$/.test(product) || !(price > 0)) return json({ ok: false, error: 'invalid' }, 400);
    const token = crypto.randomUUID().replace(/-/g, '');
    const meta = { e: email, p: product, d: deal, w: price, ts, t: token };
    await env.SIGNUPS.put(`watch:${product}:${id}`, '', { metadata: meta });
    return json({ ok: true });
  }

  return json({ ok: false, error: 'invalid' }, 400);
}

export const onRequestGet = () => json({ ok: false, error: 'POST only' }, 405);
