// Cloudflare Worker entry. Static files are served straight from the assets
// (see wrangler.jsonc); only /api/* requests reach this code.
import { onRequestPost as subscribe, onRequestGet as subscribeGet } from './api/subscribe.js';
import { onRequestGet as exportCsv } from './api/export.js';

export default {
  async fetch(request, env, ctx) {
    const { pathname } = new URL(request.url);
    const c = { request, env, ctx };
    if (pathname === '/api/subscribe') return request.method === 'POST' ? subscribe(c) : subscribeGet(c);
    if (pathname === '/api/export' && request.method === 'GET') return exportCsv(c);
    if (pathname.startsWith('/api/')) return new Response('Not found', { status: 404 });
    return env.ASSETS.fetch(request);
  },
};
