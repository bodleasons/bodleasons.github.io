/* bodleasons.com — shared player and UI (index, track pages, genre pages). Edit here, copy to Drive as _site_assets__site.js */
(function () {
  const SITE = 'https://bodleasons.com';
  const REL = 'https://github.com/bodleasons/bodleasons.github.io/releases/download/audio/';
  const B36 = '0123456789abcdefghijklmnopqrstuvwxyz';
  const slug = s => String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fmt = s => { s = Math.max(0, Math.round(s || 0)); return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0') };
  const DL = id => id ? 'https://drive.google.com/uc?export=download&id=' + id : '#';
  const TH = (id, w) => id ? 'https://lh3.googleusercontent.com/d/' + id + '=w' + (w || 120) : '';
  const credit = t => `Music: ${t.t} by BoDleasons\nFree download: ${SITE}/t/${t.s}/`;
  const useOf = n => /loop/i.test(n) ? 'seamless loop · background' : /short/i.test(n) ? 'Shorts, Reels, TikTok, ads' : /medium/i.test(n) ? 'promo, intro, short video' : 'YouTube video, full length';
  const USES = {"Ambient & Chill":"vlogs, study videos, travel films and calm background","Corporate & Business":"presentations, business videos, ads and explainer videos","Electronic, EDM & Future Bass":"gaming videos, sport edits, workouts and energetic reels","Epic & Cinematic":"trailers, intros, documentaries and dramatic moments","Acoustic & Folk":"travel vlogs, family videos, weddings and lifestyle content","Pop & Upbeat":"vlogs, ads, summer reels and happy moments","Drum & Bass":"sport, racing, action edits and high-energy content","Holiday & Christmas":"Christmas videos, holiday greetings and winter reels","Rock":"sport, extreme, action and car videos","Funk & Groove":"fashion, lifestyle and fun videos"};
  // genre order = demand (Content ID income and number of videos, genres_by_demand.csv, Nov 2026)
  const GORDER = ["Ambient & Chill","Corporate & Business","Pop & Upbeat","Acoustic & Folk","Epic & Cinematic","Electronic, EDM & Future Bass","Holiday & Christmas","Rock","Funk & Groove","Drum & Bass"];
  const I = {
    play: '<svg width="12" height="14" viewBox="0 0 12 14" aria-hidden="true"><path d="M1 1l10 6-10 6z" fill="currentColor"/></svg>',
    pause: '<svg width="12" height="14" viewBox="0 0 12 14" aria-hidden="true"><path d="M1 1h3.5v12H1zM7.5 1H11v12H7.5z" fill="currentColor"/></svg>',
    dl: '<svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true"><path d="M7 1v8M3.5 5.5L7 9l3.5-3.5M2 12.5h10" fill="none" stroke="currentColor" stroke-width="1.7"/></svg>',
    copy: '<svg width="15" height="15" viewBox="0 0 16 16" aria-hidden="true"><rect x="5" y="5" width="9" height="9" rx="2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M11 5V3a1 1 0 0 0-1-1H3a1 1 0 0 0-1 1v7a1 1 0 0 0 1 1h2" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>',
    zip: '<svg width="15" height="15" viewBox="0 0 16 16" aria-hidden="true"><path d="M2 4.5h12v9H2zM1.5 2.5h5l1.5 2" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M8 7v4M6.5 9.5L8 11l1.5-1.5" fill="none" stroke="currentColor" stroke-width="1.4"/></svg>',
    yt: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><rect y="4" width="24" height="16" rx="5" fill="#ff0000"/><path d="M10 8.5v7l6-3.5z" fill="#fff"/></svg>'
  };
  const TR = window.TR = window.TR || {};          // slug -> {s,t,g,mp3,zip,cover,src,d,v,p,sh,r}

  function waveHTML(t, n) {
    const p = t.p || '', out = [];
    for (let i = 0; i < n; i++) {
      const c = p ? p[Math.floor(i * p.length / n)] : 'k';
      const v = Math.max(0, B36.indexOf(c)) / 35;
      out.push(`<i style="height:${Math.round(12 + 88 * Math.pow(v, 1.3))}%"></i>`);
    }
    return `<div class="wave" data-w="${t.s}" title="Click to play from here">${out.join('')}</div>`;
  }
  function tagsOf(t) { return (USES[t.g] || '').split(', ').map(x => x.replace(/^and /, '')).slice(0, 2) }
  function versRows(t, withActs) {
    const v = [['Full', t.d]].concat(t.v || []);
    const rows = v.map(([n, d], i) => `<div class="vr">${i === 0 ? `<button class="pb pbx" data-play="${t.s}" aria-label="Play ${esc(t.t)}">${I.play}</button>` : (t.av || []).includes(n) ? `<button class="pb pbx" data-play="${t.s}" data-v="${esc(n)}" aria-label="Play ${esc(t.t)} ${esc(n)}">${I.play}</button>` : '<span class="ph" title="Inside the ZIP">ZIP</span>'}<span class="n">${esc(n)}</span><span class="u">${useOf(n)}</span><span class="d">${d ? fmt(d) : ''}</span></div>`).join('');
    if (!withActs) return rows;
    return rows + `<div class="ft">${t.zip ? `<a class="btn main" href="${DL(t.zip)}" rel="nofollow" data-gc="zip">${I.zip} All ${v.length} edits · ZIP</a>` : ''}<a class="btn" href="${DL(t.mp3)}" rel="nofollow" data-gc="mp3">${I.dl} Full MP3</a><button class="btn" data-copy="${t.s}">${I.copy} Copy credit</button>${t.sh ? `<a class="btn soc" href="${esc(t.sh)}" target="_blank" rel="noopener" data-gc="use-yt">${I.yt} Use in YT Shorts</a>` : ''}</div>`;
  }
  function hydrate(root) {
    (root || document).querySelectorAll('.wave[data-w]').forEach(w => { if (w.children.length) return; const t = TR[w.dataset.w]; if (!t) return; const max = +(w.dataset.n || 64), fit = Math.floor((w.clientWidth || 600) / 4), n = Math.max(24, Math.min(max, fit || max)); w.innerHTML = waveHTML(t, n).replace(/^<div[^>]*>|<\/div>$/g, '') });
  }
  function rowHTML(t) {
    const n = (t.v || []).length + 1, gs = t.g.split(',')[0];
    return `<div class="row" id="${t.s}" data-s="${t.s}">
<button class="pb desk pbx" data-play="${t.s}" aria-label="Play ${esc(t.t)}">${I.play}</button>
<div class="cvw"><img class="cv" loading="lazy" src="${TH(t.cover, 120)}" alt=""><button class="pb mob pbx" data-play="${t.s}" aria-label="Play ${esc(t.t)}">${I.play}</button></div>
<div class="tt"><a href="/t/${t.s}/">${esc(t.t)}</a><div class="sub">${esc(gs)} · <span class="mobdur">${fmt(t.d)} · </span>${n > 1 ? `<button class="edbtn" data-ed="${t.s}">${n} edits ▾</button>` : ''}</div></div>
<div class="tags">${tagsOf(t).map(x => `<span class="tag">${esc(x)}</span>`).join('')}</div>
<div class="wave" data-w="${t.s}" title="Click to play from here"></div>
<div class="dur">${fmt(t.d)}</div>
<div class="acts"><button class="btn ib dk" title="Copy credit" aria-label="Copy credit for ${esc(t.t)}" data-copy="${t.s}">${I.copy}</button>${t.zip ? `<a class="btn ib dk" title="All ${n} edits in one ZIP" aria-label="Download all edits ZIP" href="${DL(t.zip)}" rel="nofollow" data-gc="zip">${I.zip}</a>` : ''}<a class="btn main" href="${DL(t.mp3)}" rel="nofollow" data-gc="mp3" aria-label="Free download MP3">${I.dl}<span>MP3</span></a></div>
<div class="vp" id="vp-${t.s}" hidden></div>
</div>`;
  }

  /* ---------- player ---------- */
  const bar = document.createElement('div'); bar.className = 'bar'; bar.id = 'bar';
  bar.innerHTML = `<div class="wrap"><img id="bCv" alt=""><div class="meta"><a id="bT" href="/"></a><div id="bH"></div></div>
<div class="ctl"><button class="sk prev" aria-label="Previous" data-step="-1"><svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true"><path d="M12 1L4 7l8 6zM1 1h2v12H1z" fill="#ece8f7"/></svg></button><button class="pp" id="bPP" aria-label="Play or pause"></button><button class="sk" aria-label="Next" data-step="1"><svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true"><path d="M2 1l8 6-8 6zM11 1h2v12h-2z" fill="#ece8f7"/></svg></button></div>
<div class="prog"><span class="tm" id="bC">0:00</span><div class="track" id="bTr"><i id="bF"></i></div><span class="tm" id="bD">0:00</span></div>
<a class="btn main dlb" id="bDl" href="#" rel="nofollow" data-gc="mp3">${I.dl} Free MP3</a>
<button class="sk" id="bX" aria-label="Close player" style="border:0;background:transparent;width:36px;height:36px"><svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true"><path d="M1 1l10 10M11 1L1 11" stroke="#a39bbd" stroke-width="1.6"/></svg></button></div>`;
  const toastEl = document.createElement('div'); toastEl.className = 'toast'; toastEl.id = 'toast';
  const au = new Audio(); au.preload = 'none';
  let CUR = null, CURV = null;
  function $(id) { return document.getElementById(id) }
  function play(s, v) {
    const t = TR[s]; if (!t) return; v = v || null;
    if (CUR === s && CURV === v) { au.paused ? au.play() : au.pause(); return }
    CUR = s; CURV = v;
    const full = v ? REL.replace('/audio/', '/' + (t.ar || 'audio') + '/') + s + '__' + slug(v) + '.mp3' : (t.src || ('/previews/' + s + '.mp3'));
    let tries = 0; au.src = full; au.onerror = () => { if (CUR !== s || CURV !== v) return; const code = au.error && au.error.code; if (code === 1) return; if (v) { if (tries++ < 2) { setTimeout(() => { if (CUR === s && CURV === v) { au.src = full + '?t=' + Date.now(); au.play().catch(() => {}) } }, 700); return } toast('This edit could not load — try again or download the ZIP'); return } if (!au.src.includes('/previews/')) { au.src = '/previews/' + s + '.mp3'; au.play().catch(() => {}) } };
    au.play().catch(() => {});
    if (window.goatcounter && goatcounter.count) goatcounter.count({ path: 'play/' + s, title: 'play: ' + t.t, event: true });
    $('bCv').src = TH(t.cover, 120); const bt = $('bT'); bt.textContent = t.t + (v ? ' · ' + v : ''); bt.href = '/t/' + s + '/';
    $('bH').textContent = v ? 'Edit · from the Full Pack' : t.g + ' · by BoDleasons'; $('bDl').href = DL(t.mp3);
    bar.classList.add('on'); document.body.classList.add('hasbar'); mark();
  }
  function queue() { const q = []; document.querySelectorAll('[data-play]').forEach(b => { const s = b.dataset.play; if (q[q.length - 1] !== s && !q.includes(s)) q.push(s) }); return q }
  function step(d) { if (!CUR) return; const q = queue(); if (!q.length) return; const i = q.indexOf(CUR); play(q[(i + d + q.length) % q.length]) }
  function closeBar() { au.pause(); CUR = null; CURV = null; bar.classList.remove('on'); document.body.classList.remove('hasbar'); mark() }
  function mark() {
    const on = !au.paused;
    if ($('bPP')) $('bPP').innerHTML = on ? I.pause : I.play;
    document.querySelectorAll('.row').forEach(r => r.classList.toggle('on', r.dataset.s === CUR));
    document.querySelectorAll('.pbx,[data-play].pb').forEach(b => { const me = b.dataset.play === CUR && (b.dataset.v || null) === CURV; b.innerHTML = me && on ? I.pause : I.play; b.classList.toggle('on', me) });
  }
  au.addEventListener('play', mark); au.addEventListener('pause', mark); au.addEventListener('ended', () => step(1));
  au.addEventListener('timeupdate', () => {
    if (drag) return;
    const d = au.duration || (TR[CUR] || {}).d || 60, p = au.currentTime / d;
    $('bC').textContent = fmt(au.currentTime); $('bD').textContent = fmt(d); $('bF').style.width = (p * 100) + '%';
    document.querySelectorAll(`.wave[data-w="${CUR}"]`).forEach(w => { const b = w.children, n = Math.round(p * b.length); for (let i = 0; i < b.length; i++) b[i].classList.toggle('p', i < n && !CURV) });
  });
  function toast(t) { toastEl.textContent = t; toastEl.classList.add('on'); clearTimeout(toastEl._t); toastEl._t = setTimeout(() => toastEl.classList.remove('on'), 2600) }
  function copyText(c, msg) { (navigator.clipboard ? navigator.clipboard.writeText(c) : Promise.reject()).then(() => toast(msg + '\n' + c), () => prompt('Copy:', c)) }

  document.addEventListener('click', e => {
    const el = e.target.closest('[data-play],[data-copy],[data-ed],[data-step],#bPP,#bX,[data-copytext]');
    if (!el) return;
    if (el.dataset.play) { play(el.dataset.play, el.dataset.v) }
    else if (el.dataset.copy) { const t = TR[el.dataset.copy]; if (t) copyText(credit(t), 'Credit copied ✓') }
    else if (el.dataset.copytext) { copyText(el.dataset.copytext, 'Copied ✓') }
    else if (el.dataset.ed) { const p = $('vp-' + el.dataset.ed); if (p) { if (!p.innerHTML.trim() && TR[el.dataset.ed]) p.innerHTML = versRows(TR[el.dataset.ed], true); p.hidden = !p.hidden; mark() } }
    else if (el.dataset.step) { step(+el.dataset.step) }
    else if (el.id === 'bPP') { if (CUR) au.paused ? au.play() : au.pause() }
    else if (el.id === 'bX') { closeBar() }
  });
  /* drag to seek (waveform and player bar), like YouTube Music */
  let drag = null;
  function paint(p) { $('bF').style.width = (p * 100) + '%'; if (au.duration) $('bC').textContent = fmt(au.duration * p);
    document.querySelectorAll(`.wave[data-w="${CUR}"]`).forEach(w => { const b = w.children, n = Math.round(p * b.length); for (let i = 0; i < b.length; i++) b[i].classList.toggle('p', i < n && !CURV) }) }
  document.addEventListener('pointerdown', e => {
    const el = e.target.closest('.wave[data-w], #bTr'); if (!el || e.button > 0) return;
    const bar_ = el.id === 'bTr', s = bar_ ? CUR : el.dataset.w; if (!s) return;
    e.preventDefault();
    const r = el.getBoundingClientRect(), frac = ev => Math.min(1, Math.max(0, (ev.clientX - r.left) / r.width));
    let p = frac(e);
    if (!bar_ && (CUR !== s || CURV)) { CUR = null; play(s); au.addEventListener('loadedmetadata', () => { au.currentTime = au.duration * (drag ? drag.p : p) }, { once: true }) }
    drag = { el, p }; el.classList.add('drag'); paint(p);
    try { el.setPointerCapture(e.pointerId) } catch (_) {}
    const move = ev => { p = frac(ev); drag.p = p; paint(p) };
    const up = () => { el.removeEventListener('pointermove', move); el.removeEventListener('pointerup', up); el.removeEventListener('pointercancel', up); el.classList.remove('drag');
      if (au.duration && CUR === s) au.currentTime = au.duration * p; else if (bar_ && au.duration) au.currentTime = au.duration * p; drag = null };
    el.addEventListener('pointermove', move); el.addEventListener('pointerup', up); el.addEventListener('pointercancel', up);
  });
  document.addEventListener('DOMContentLoaded', () => { document.body.appendChild(bar); document.body.appendChild(toastEl); hydrate(); mark() });
  if (document.readyState !== 'loading') { document.body.appendChild(bar); document.body.appendChild(toastEl); setTimeout(() => { hydrate(); mark() }, 0) }

  window.BOD = { hydrate, slug, esc, fmt, DL, TH, I, TR, GORDER, USES, rowHTML, waveHTML, versRows, mark, play, credit, REL };
})();
