const CACHE='shaffof-v1';
const FILES=[
  '/restoran/',
  '/restoran/index.html',
  '/restoran/login.html',
  '/restoran/register.html',
  '/restoran/dashboard.html',
  '/restoran/admin.html',
  '/restoran/oshxona.html',
  '/restoran/ofitsiant.html',
  '/restoran/mijoz.html',
];

self.addEventListener('install',e=>{
  e.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES)));
  self.skipWaiting();
});

self.addEventListener('activate',e=>{
  e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))));
  self.clients.claim();
});

self.addEventListener('fetch',e=>{
  e.respondWith(
    caches.match(e.request).then(cached=>{
      if(cached)return cached;
      return fetch(e.request).then(res=>{
        if(!res||res.status!==200||res.type!=='basic')return res;
        let clone=res.clone();
        caches.open(CACHE).then(c=>c.put(e.request,clone));
        return res;
      }).catch(()=>caches.match('/restoran/index.html'));
    })
  );
});
