/* Elevated Line service worker -- cache-first shell, background refresh, self-update.
   CACHE name is stamped by build.py; a new build => new cache => old one purged. */
const CACHE = "elevated-line-20260912-1527";
const SHELL = ["./", "./index.html", "./manifest.webmanifest", "./icon-192.png", "./icon-512.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL))); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener("message", e => { if (e.data && e.data.type === "SKIP_WAITING") self.skipWaiting(); });
self.addEventListener("fetch", e => {
  const req = e.request; if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) {
    // fonts etc.: network, fall back to cache if we have it
    e.respondWith(caches.open(CACHE).then(c => fetch(req).then(r => { c.put(req, r.clone()); return r; }).catch(() => c.match(req))));
    return;
  }
  // same-origin shell: cache first, refresh in background
  e.respondWith(caches.open(CACHE).then(async c => {
    const cached = await c.match(req, {ignoreSearch: true});
    const net = fetch(req).then(r => { if (r && r.ok) c.put(req, r.clone()); return r; }).catch(() => null);
    return cached || (await net) || new Response("Offline and not cached yet.", {status: 503, headers: {"Content-Type": "text/plain"}});
  }));
});
