#!/usr/bin/env python3
"""Страницы для Google (SEO): /t/<трек>/ — страница каждого трека, /genre/<жанр>/ — страница жанра,
sitemap.xml, robots.txt. Данные: data/tracks.json, rank.json, meta.json, audio.json, social.json.
Запускается в GitHub Actions после build_data.py и audio_release.py."""
import html, json, os, re, datetime
SITE = "https://bodleasons.github.io"
REL = "https://github.com/bodleasons/bodleasons.github.io/releases/download/audio/"
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
e = lambda s: html.escape(str(s), quote=True)
DL = lambda i: f"https://drive.google.com/uc?export=download&id={i}"
TH = lambda i, w=600: f"https://lh3.googleusercontent.com/d/{i}=w{w}"

def load(p, d):
    try: return json.load(open(p))
    except Exception: return d

USES = {"Ambient & Chill": "vlogs, study videos, travel films and calm background",
        "Corporate & Business": "presentations, business videos, ads and explainer videos",
        "Electronic, EDM & Future Bass": "gaming videos, sport edits, workouts and energetic reels",
        "Epic & Cinematic": "trailers, intros, documentaries and dramatic moments",
        "Acoustic & Folk": "travel vlogs, family videos, weddings and lifestyle content",
        "Pop & Upbeat": "vlogs, ads, summer reels and happy moments",
        "Drum & Bass": "sport, racing, action edits and high-energy content",
        "Holiday & Christmas": "Christmas videos, holiday greetings and winter reels",
        "Rock": "sport, extreme, action and car videos", "Funk & Groove": "fashion, lifestyle and fun videos"}

CSS = """:root{--bg:#0b0b12;--panel:#14141f;--panel2:#1b1b29;--line:#26263a;--text:#ecebf5;--mute:#9a98b3;--a1:#7b5cff;--a2:#ff4fa3;--a3:#ff9a3d}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.6 Inter,system-ui,sans-serif}a{color:inherit}
.wrap{max-width:1000px;margin:0 auto;padding:0 20px}.grad{background:linear-gradient(90deg,var(--a1),var(--a2),var(--a3));-webkit-background-clip:text;background-clip:text;color:transparent}
header{border-bottom:1px solid var(--line)}header .wrap{display:flex;align-items:center;height:58px;gap:14px}.logo{font:700 19px "Space Grotesk",sans-serif;text-decoration:none}
header nav{margin-left:auto;display:flex;gap:14px;font-size:13px}header nav a{color:var(--mute);text-decoration:none}
.hero{display:grid;grid-template-columns:320px 1fr;gap:28px;padding:34px 0}@media(max-width:720px){.hero{grid-template-columns:1fr}}
.hero img{width:100%;aspect-ratio:1;object-fit:cover;border-radius:18px;background:var(--panel2)}
h1{font:700 clamp(28px,5vw,44px)/1.1 "Space Grotesk",sans-serif;margin:0 0 6px}h2{font:700 21px "Space Grotesk",sans-serif;margin:28px 0 10px}
.by{color:var(--mute);margin:0 0 16px}.lead{color:var(--mute)}audio{width:100%;margin:12px 0 4px}
.btns{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0}.btn{display:inline-flex;align-items:center;gap:7px;font:600 14px Inter,sans-serif;padding:11px 15px;border-radius:12px;border:1px solid var(--line);background:var(--panel2);color:var(--text);text-decoration:none;cursor:pointer}
.btn.main{background:linear-gradient(135deg,var(--a1),var(--a2));border:0;color:#fff}.btn.soc{background:#102a24;border-color:#1d4a3f}
.pl{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px;margin:10px 0 4px}.pl .btn{justify-content:center;font-size:13px;padding:9px 10px}
.pl .btn svg{width:16px;height:16px;flex:none}.plh{font:600 12px Inter,sans-serif;color:var(--mute);text-transform:uppercase;letter-spacing:.06em;margin:14px 0 0}
.box{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:16px 18px;margin:12px 0}.box p{margin:6px 0;color:var(--mute)}
dl{display:grid;grid-template-columns:max-content 1fr;gap:6px 16px;margin:0}dt{color:var(--mute)}dd{margin:0}
code{display:block;background:var(--bg);border:1px dashed #3a3a58;border-radius:10px;padding:10px 12px;white-space:pre-wrap;font:13px ui-monospace,Menlo,monospace}
.list{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px}.it{display:flex;gap:10px;align-items:center;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:8px;text-decoration:none}
.it img{width:48px;height:48px;border-radius:8px;object-fit:cover;background:var(--panel2)}.it span{font-size:14px}.it small{display:block;color:var(--mute);font-size:12px}
footer{border-top:1px solid var(--line);margin-top:40px;padding:22px 0 40px;color:var(--mute);font-size:13px}"""

def head(title, desc, url, img=""):
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{url}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}">{f'<meta property="og:image" content="{img}">' if img else ''}
<meta name="theme-color" content="#0b0b12"><link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<header><div class="wrap"><a class="logo" href="/"><b class="grad">BoDleasons</b> Free Music</a><nav><a href="/#all">All tracks</a><a href="/#license">How to use</a></nav></div></header>"""

FOOT = """<footer><div class="wrap">© BoDleasons — music by Bohdan Kuzmin · <a href="/">500+ free tracks</a> · <a href="https://t.me/bodleasons">Telegram</a> · <a href="mailto:bodleason.make@gmail.com">Licensing</a></div></footer>
<script>function cp(t){navigator.clipboard.writeText(t).then(()=>alert('Copied ✓'))}</script>
<script data-goatcounter="https://bodleasons.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
<script>document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a');if(!a||!window.goatcounter||!goatcounter.count)return;var h=a.href||'',n=null;
if(h.indexOf('drive.google.com/uc')>-1)n=(a.dataset.gc==='zip'||a.textContent.indexOf('Full Pack')>-1?'zip':'mp3');else if(h.indexOf('youtube.com/source')>-1)n='use-shorts';else if(h.indexOf('t.me/')>-1)n='telegram';
if(n){var t=(document.querySelector('h1')&&location.pathname.indexOf('/t/')===0)?document.querySelector('h1').textContent:((a.closest('.card')||{}).id||(window.CUR&&CUR.t)||'');goatcounter.count({path:n+'/'+t,title:n+': '+t,event:true})}},true);</script>
</body></html>"""

def fmt(s): s = int(s or 0); return f"{s // 60}:{s % 60:02d}"

def item(t, meta):
    s = slug(t["t"])
    return f'<a class="it" href="/t/{s}/"><img loading="lazy" src="{TH(t["cover"], 120) if t.get("cover") else ""}" alt=""><span>{e(t["t"])}<small>{e(t["g"])} · {fmt(meta.get(s, {}).get("dur"))}</small></span></a>'

def main():
    tracks = load("data/tracks.json", []); rank = load("data/rank.json", {}); meta = load("data/meta.json", {})
    audio = load("data/audio.json", {}); social = load("data/social.json", {}); plat = load("data/platforms.json", {})
    rk = lambda t: rank.get(t["t"], 10**9)
    today = datetime.date.today().isoformat(); urls = [(SITE + "/", "1.0")]
    bygenre = {}
    for t in tracks: bygenre.setdefault(t["g"], []).append(t)
    for t in tracks:
        s = slug(t["t"]); m = meta.get(s, {}); g = t["g"]; url = f"{SITE}/t/{s}/"
        uses = USES.get(g, "YouTube videos, Shorts, Reels and TikTok")
        title = f"{t['t']} — Free {g.split(',')[0].split(' & ')[0]} Background Music (MP3) | BoDleasons"
        desc = f"Download \"{t['t']}\" by BoDleasons for free: {g.lower()} background music for {uses}. Instant MP3 + Full Pack of edits. Free to use with credit."
        src = (REL + s + ".mp3") if s in audio else (f"/previews/{s}.mp3" if t.get("p") else "")
        so = social.get(s, {})
        socbtn = "".join(f'<a class="btn soc" href="{e(so[k])}" target="_blank" rel="noopener">{lab}</a>' for k, lab in
                         (("shorts", "▶ Use in YT Shorts"), ("tiktok", "♪ Use in TikTok"), ("reels", "◎ Use in Instagram Reels")) if so.get(k))
        vers = ", ".join(["Full"] + [v.replace(" Version", "") for v in m.get("v", [])])
        p = plat.get(s, {}); yt = (social.get(s) or {}).get("yt", "")
        ICO = {"sp": '<svg viewBox="0 0 24 24" fill="#1DB954"><circle cx="12" cy="12" r="11"/><path d="M7 9.5c3.5-1 7-.6 10 1M7.5 12.5c3-.8 5.8-.5 8.5 1M8 15.3c2.4-.6 4.6-.4 6.6.8" stroke="#000" stroke-width="1.6" fill="none" stroke-linecap="round"/></svg>',
               "ap": '<svg viewBox="0 0 24 24"><rect width="24" height="24" rx="6" fill="#fa2d48"/><path d="M15.5 6v8.2a2.3 2.3 0 1 1-1.3-2.1V8.3l-5 1.2v6.2a2.3 2.3 0 1 1-1.3-2.1V8.4z" fill="#fff"/></svg>',
               "yt": '<svg viewBox="0 0 24 24"><rect y="4" width="24" height="16" rx="5" fill="#ff0000"/><path d="M10 8.5v7l6-3.5z" fill="#fff"/></svg>',
               "dz": '<svg viewBox="0 0 24 24" fill="#a238ff"><rect x="1" y="15" width="4" height="4"/><rect x="7" y="11" width="4" height="8"/><rect x="13" y="7" width="4" height="12"/><rect x="19" y="3" width="4" height="16"/></svg>',
               "ig": '<svg viewBox="0 0 24 24" fill="none" stroke="#e1306c" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/></svg>',
               "tt": '<svg viewBox="0 0 24 24" fill="#fff"><path d="M14 3h3a4 4 0 0 0 4 4v3a7 7 0 0 1-4-1.3V15a6 6 0 1 1-6-6v3a3 3 0 1 0 3 3z"/></svg>'}
        listen = [("sp", "Spotify", p.get("sp") and f"https://open.spotify.com/track/{p['sp']}"),
                  ("ap", "Apple Music", p.get("ap") and f"https://music.apple.com/us/song/{p['ap']}"),
                  ("yt", "YouTube Music", yt and f"https://music.youtube.com/watch?v={yt}"),
                  ("dz", "Deezer", p.get("dz") and f"https://www.deezer.com/track/{p['dz']}")]
        usein = [("yt", "Use in YT Shorts", (social.get(s) or {}).get("shorts")),
                 ("ig", "Use in Reels", p.get("ig") and f"https://www.instagram.com/reels/audio/{p['ig']}/"),
                 ("tt", "Use in TikTok", p.get("tt") and (p["tt"] if str(p["tt"]).startswith("http") else f"https://www.tiktok.com/music/{p['tt']}"))]
        lb = "".join(f'<a class="btn" href="{e(u)}" target="_blank" rel="noopener" data-gc="listen-{k}">{ICO[k]} {n}</a>' for k, n, u in listen if u)
        ub = "".join(f'<a class="btn soc" href="{e(u)}" target="_blank" rel="noopener" data-gc="use-{k}">{ICO[k]} {n}</a>' for k, n, u in usein if u)
        platblock = (f'<p class="plh">Use in short videos</p><div class="pl">{ub}</div>' if ub else "") + (f'<p class="plh">Listen on</p><div class="pl">{lb}</div>' if lb else "")
        more = sorted([x for x in bygenre[g] if x is not t], key=rk)[:12]
        credit = e(json.dumps(f"Music: {t['t']} by BoDleasons\nFree download: {url}"))
        ld = {"@context": "https://schema.org", "@type": "MusicRecording", "name": t["t"], "url": url,
              "byArtist": {"@type": "MusicGroup", "name": "BoDleasons"}, "genre": g, "duration": f"PT{int(m.get('dur', 0)) // 60}M{int(m.get('dur', 0)) % 60}S",
              "inAlbum": {"@type": "MusicAlbum", "name": m.get("al", "Single")}, "image": TH(t["cover"]) if t.get("cover") else "",
              "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD", "url": DL(t["mp3"])}}
        page = head(title, desc, url, TH(t["cover"]) if t.get("cover") else "") + f"""
<main class="wrap"><div class="hero">
<img src="{TH(t['cover']) if t.get('cover') else ''}" alt="{e(t['t'])} — BoDleasons cover">
<div><h1>{e(t['t'])}</h1><p class="by">by BoDleasons · {e(g)} · {fmt(m.get('dur'))}</p>
<p class="lead">Free {e(g.lower())} background music for {e(uses)}. Free to use in your videos with credit.</p>
{(f'<audio controls preload="metadata"><source src="{src}" type="audio/mpeg"><source src="/previews/{s}.mp3" type="audio/mpeg"></audio>' if src.startswith('http') else f'<audio controls preload="metadata" src="{src}"></audio>') if src else ''}
<div class="btns"><a class="btn main" href="{DL(t['mp3'])}" rel="nofollow">⬇ Free Download MP3</a>{f'<a class="btn" href="{DL(t["zip"])}" rel="nofollow" data-gc="zip">📦 Full Pack · {len(m.get("v", [])) + 1} edits (ZIP)</a>' if t.get('zip') else ''}
<button class="btn" onclick="cp({credit})" title="Copies a ready credit line for your video description">📋 Copy credit</button></div>
<p class="by" style="margin-top:8px">Free to use with credit: paste the credit line into your video description. Monetized videos may get a Content ID claim — that's normal, your video stays up.</p>
{platblock}
</div></div>
<div class="box"><dl><dt>Track</dt><dd>{e(t['t'])}</dd><dt>Artist</dt><dd>BoDleasons (Bohdan Kuzmin)</dd><dt>Genre</dt><dd><a href="/genre/{slug(g)}/">{e(g)}</a></dd>
<dt>Album</dt><dd>{e(m.get('al', 'Single'))}</dd><dt>Length</dt><dd>{fmt(m.get('dur'))}</dd><dt>Versions</dt><dd>{e(vers)} (no vocals)</dd><dt>License</dt><dd>Free with credit · YouTube Content ID registered</dd></dl></div>
<div class="box"><p><b>How to credit</b> — paste into your video description:</p><code>Music: {e(t['t'])} by BoDleasons
Free download: {url}</code><p>A Content ID claim is not a strike — your video stays online. Want the claim released or a commercial license? Email the video link to <a href="mailto:bodleason.make@gmail.com">bodleason.make@gmail.com</a>.</p></div>
<h2>More {e(g)} music</h2><div class="list">{''.join(item(x, meta) for x in more)}</div>
<p><a class="btn" href="/genre/{slug(g)}/">All {e(g)} tracks →</a> <a class="btn" href="/">All 500+ free tracks →</a></p>
</main><script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>""" + FOOT
        os.makedirs(f"t/{s}", exist_ok=True); open(f"t/{s}/index.html", "w").write(page); urls.append((url, "0.8"))
    for g, ts in bygenre.items():
        gs = slug(g); url = f"{SITE}/genre/{gs}/"; uses = USES.get(g, "videos")
        ts = sorted(ts, key=rk)
        page = head(f"Free {g} Music for Videos — {len(ts)} tracks, MP3 download | BoDleasons",
                    f"{len(ts)} free {g.lower()} tracks by BoDleasons for {uses}. Instant MP3 download, free to use with credit.", url) + f"""
<main class="wrap"><h1 style="margin-top:30px">Free {e(g)} music for videos</h1>
<p class="lead">{len(ts)} tracks for {e(uses)}. Listen, download the MP3 in one click and use it with credit. Most popular first.</p>
<div class="list">{''.join(item(x, meta) for x in ts)}</div></main>""" + FOOT
        os.makedirs(f"genre/{gs}", exist_ok=True); open(f"genre/{gs}/index.html", "w").write(page); urls.append((url, "0.9"))
    with open("sitemap.xml", "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for u, pr in urls: f.write(f"<url><loc>{u}</loc><lastmod>{today}</lastmod><priority>{pr}</priority></url>\n")
        f.write("</urlset>\n")
    open("robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    print("страниц треков:", len(tracks), "жанров:", len(bygenre))

if __name__ == "__main__":
    main()
