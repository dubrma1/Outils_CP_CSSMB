/**
 * sw.js — Service Worker pour fonctionnement 100 % hors-ligne (PWA)
 * Actif sur serveur HTTP / HTTPS (GitHub Pages, Azure Static Web Apps).
 */

const CACHE_NAME = 'repertoire-metiers-qc-v2';
const STATIC_ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './css/theme-quebec.css',
  './js/app.js',
  './data/metiers_data.js',
  './data/metiers_data.json',
  './data/metiers_index.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon.svg'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }
      return fetch(event.request).then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200 && event.request.method === 'GET') {
          const clone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        }
        return networkResponse;
      });
    })
  );
});
