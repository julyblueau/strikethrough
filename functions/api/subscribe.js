// Cloudflare Pages Function: stores sign-ups from the two site forms in Workers KV.
// Needs a KV namespace bound as SIGNUPS (Pages project → Settings → Bindings).
const FORMS = new Set(['verified-list', 'signup']);
const EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' } });

export async function onRequestPost({ request, env }) {
  if (!env.SIGNUPS) return json({ ok: false, error: 'storage not configured' }, 500);
  let data;
  try { data = await request.formData(); } catch { return json({ ok: false, error: 'bad request' }, 400); }
  if ((data.get('bot-field') || '').trim()) return json({ ok: true }); // honeypot: pretend success
  const email = String(data.get('email') || '').trim().toLowerCase().slice(0, 200);
  const form = String(data.get('form-name') || '');
  if (!FORMS.has(form) || !EMAIL.test(email)) return json({ ok: false, error: 'invalid' }, 400);
  const ts = new Date().toISOString();
  const rec = {
    form, email, ts,
    type: String(data.get('type') || '').slice(0, 60),
    name: String(data.get('name') || '').slice(0, 120),
    company: String(data.get('company') || '').slice(0, 120),
    country: (request.cf && request.cf.country) || '',
  };
  const key = `${form}:${ts}:${crypto.randomUUID().slice(0, 8)}`;
  await env.SIGNUPS.put(key, JSON.stringify(rec));
  return json({ ok: true });
}

export const onRequestGet = () => json({ ok: false, error: 'POST only' }, 405);
