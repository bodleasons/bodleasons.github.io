#!/usr/bin/env python3
"""Страницы для Google (SEO): /t/<трек>/ — страница каждого трека, /genre/<жанр>/ — страница жанра,
sitemap.xml, robots.txt. Данные: data/tracks.json, rank.json, meta.json, audio.json, social.json, platforms.json, wave.json.
Дизайн 2026-11 (список строк, плеер внизу, версии трека). Общие стили и плеер: /assets/site.css, /assets/site.js.
Запускается в GitHub Actions после build_data.py и audio_release.py."""
import html, json, os, re, datetime
SITE = "https://bodleasons.com"
REL = "https://github.com/bodleasons/bodleasons.github.io/releases/download/audio/"
ASSET_V = "20261121c"
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
e = lambda s: html.escape(str(s), quote=True)
DL = lambda i: f"https://drive.google.com/uc?export=download&id={i}"
TH = lambda i, w=600: f"https://lh3.googleusercontent.com/d/{i}=w{w}" if i else ""
B36 = "0123456789abcdefghijklmnopqrstuvwxyz"

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
# порядок жанров = спрос (доход Content ID и число видео, genres_by_demand.csv, ноябрь 2026)
GORDER = ["Ambient & Chill", "Corporate & Business", "Pop & Upbeat", "Acoustic & Folk", "Epic & Cinematic",
          "Electronic, EDM & Future Bass", "Holiday & Christmas", "Rock", "Funk & Groove", "Drum & Bass"]

ICO = {"sp": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="11" fill="#1DB954"/><path d="M7 9.5c3.5-1 7-.6 10 1M7.5 12.5c3-.8 5.8-.5 8.5 1M8 15.3c2.4-.6 4.6-.4 6.6.8" stroke="#000" stroke-width="1.6" fill="none" stroke-linecap="round"/></svg>',
       "ap": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect width="24" height="24" rx="6" fill="#fa2d48"/><path d="M15.5 6v8.2a2.3 2.3 0 1 1-1.3-2.1V8.3l-5 1.2v6.2a2.3 2.3 0 1 1-1.3-2.1V8.4z" fill="#fff"/></svg>',
       "yt": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect y="4" width="24" height="16" rx="5" fill="#ff0000"/><path d="M10 8.5v7l6-3.5z" fill="#fff"/></svg>',
       "ytm": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="11" fill="#ff0000"/><circle cx="12" cy="12" r="5.5" fill="none" stroke="#fff" stroke-width="1.4"/><path d="M10.5 9.5v5l4-2.5z" fill="#fff"/></svg>',
       "dz": '<svg viewBox="0 0 24 24" fill="#a238ff" aria-hidden="true"><rect x="1" y="15" width="4" height="4"/><rect x="7" y="11" width="4" height="8"/><rect x="13" y="7" width="4" height="12"/><rect x="19" y="3" width="4" height="16"/></svg>',
       "ig": '<svg viewBox="0 0 24 24" fill="none" stroke="#e1306c" stroke-width="2" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="#e1306c" stroke="none"/></svg>',
       "tt": '<svg viewBox="0 0 24 24" fill="#fff" aria-hidden="true"><path d="M14 3h3a4 4 0 0 0 4 4v3a7 7 0 0 1-4-1.3V15a6 6 0 1 1-6-6v3a3 3 0 1 0 3 3z"/></svg>',
       "tg": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="11" fill="#29a9eb"/><path d="M5.5 11.8l11.6-4.5c.5-.2 1 .1.8.9l-2 9.3c-.1.6-.5.8-1 .5l-3-2.2-1.5 1.4c-.2.2-.3.3-.6.3l.2-3.1 5.6-5c.2-.2 0-.3-.3-.1l-6.9 4.3-3-.9c-.6-.2-.6-.6.1-.9z" fill="#fff"/></svg>',
       "fb": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="11" fill="#1877f2"/><path d="M13.2 19v-5.8h2l.3-2.3h-2.3V9.5c0-.7.2-1.1 1.1-1.1h1.2V6.3a16 16 0 0 0-1.8-.1c-1.8 0-3 1.1-3 3.1v1.6H8.8v2.3h1.9V19z" fill="#fff"/></svg>',
       "sc": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M1 15.5a2 2 0 0 1 2-2h.3M4.3 17V12M6 17v-6M7.7 17V9.5M9.4 17V9M11 17V8.5" stroke="#ff5500" stroke-width="1.3" fill="none" stroke-linecap="round"/><path d="M12.5 17V8a5 5 0 0 1 8.4 3.2A3 3 0 0 1 20.5 17z" fill="#ff5500"/></svg>',
       "px": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect width="24" height="24" rx="6" fill="#00ab6c"/><text x="12" y="16.5" font-size="11" font-weight="700" text-anchor="middle" fill="#fff" font-family="Arial">px</text></svg>',
       "fma": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect width="24" height="24" rx="6" fill="#e5e5e5"/><text x="12" y="15.5" font-size="8.5" font-weight="700" text-anchor="middle" fill="#111" font-family="Arial">FMA</text></svg>',
       "gm": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2" y="5" width="20" height="14" rx="2.5" fill="#fff"/><path d="M2.5 6.5l9.5 7 9.5-7" fill="none" stroke="#ea4335" stroke-width="2"/></svg>',
       "al": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect width="24" height="24" rx="6" fill="#ffd400"/><path d="M12 5.5l5.2 13h-2.4l-1.1-2.9H10.3l-1.1 2.9H6.8zm-1 8h2l-1-2.7z" fill="#111"/></svg>'}

SOCIALS = [("yt", "YouTube", "https://www.youtube.com/@bodleasons"), ("ig", "Instagram", "https://www.instagram.com/bodleasons/"),
           ("tt", "TikTok", "https://www.tiktok.com/@bodleasons"), ("fb", "Facebook", "https://www.facebook.com/profile.php?id=61595615733055"),
           ("tg", "Telegram", "https://t.me/bodleasons"), ("gm", "Email", "mailto:bodleason.make@gmail.com")]

SEARCH_ICO = '<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><circle cx="7" cy="7" r="5" fill="none" stroke="#a39bbd" stroke-width="1.6"/><path d="M11 11l4 4" stroke="#a39bbd" stroke-width="1.6"/></svg>'

def head(title, desc, url, img="", extra=""):
    return f"""<!DOCTYPE html>
<!-- bodleasons-site -->
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{url}"><link rel="icon" href="/logo.png">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}">{f'<meta property="og:image" content="{img}">' if img else ''}
<meta name="theme-color" content="#0d0b16"><link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css?v={ASSET_V}">{extra}</head><body>
{HEADER}"""

HEADER = f"""<header><div class="wrap">
<a class="logo" href="/"><img src="/logo.png" alt="">BoDleasons<span>Free Music</span></a>
<form class="search desk" action="/" role="search">{SEARCH_ICO}<input name="q" id="q" type="search" placeholder="Search a track you heard… (e.g. Lo-Fi Chill)" aria-label="Search tracks" autocomplete="off"></form>
<nav class="top"><a href="/#all">Music</a><a href="/#genres">Genres</a><a href="/#license">How to use</a><a href="https://t.me/bodleasons" target="_blank" rel="noopener">Telegram</a></nav>
<a class="icobtn" href="/#search" aria-label="Search"><svg width="18" height="18" viewBox="0 0 16 16" aria-hidden="true"><circle cx="7" cy="7" r="5" fill="none" stroke="#ece8f7" stroke-width="1.6"/><path d="M11 11l4 4" stroke="#ece8f7" stroke-width="1.6"/></svg></a>
</div></header>"""

FOOTER = """<footer><div class="wrap" style="display:block">
<div class="ftop"><div style="flex:1 1 520px"><h4>Follow BoDleasons</h4><div class="follow">""" + "".join(
    f'<a href="{u}"{"" if u.startswith("mailto:") else " target=\"_blank\" rel=\"noopener\""} data-gc="follow-{k}">{ICO[k]}<span>{n}</span></a>' for k, n, u in SOCIALS) + """</div>
<p style="margin:12px 0 0;font-size:13px">Questions, commercial license or claim release: <a href="mailto:bodleason.make@gmail.com" style="text-decoration:underline">bodleason.make@gmail.com</a></p></div></div>
<div class="fbot"><span>© BoDleasons — music by Bohdan Kuzmin</span><span><a href="/">574+ free tracks</a> · <a href="/#license">How to use</a></span></div>
</div></footer>"""

GC = """<script data-goatcounter="https://bodleasons.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
<script>document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a');if(!a||!window.goatcounter||!goatcounter.count)return;var h=a.href||'',n=null;
if(h.indexOf('drive.google.com/uc')>-1)n=(a.dataset.gc==='zip'?'zip':'mp3');else if(h.indexOf('youtube.com/source')>-1)n='use-shorts';else if(h.indexOf('t.me/')>-1)n='telegram';else if(a.dataset.gc&&a.dataset.gc.indexOf('follow-')===0)n=a.dataset.gc;
if(n){var r=a.closest('.row,.nc');var t=r?(r.dataset.s||r.id):((document.querySelector('h1')&&location.pathname.indexOf('/t/')===0)?document.querySelector('h1').textContent:'');goatcounter.count({path:n+'/'+t,title:n+': '+t,event:true})}},true);</script>"""

def foot(tr):
    return FOOTER + f"""
<script>window.TR={json.dumps(tr, ensure_ascii=False, separators=(',', ':'))};</script>
<script src="/assets/site.js?v={ASSET_V}"></script>
{GC}
</body></html>"""

def fmt(s): s = int(s or 0); return f"{s // 60}:{s % 60:02d}"
def use_of(n): return "seamless loop · background" if "loop" in n.lower() else "Shorts, Reels, TikTok, ads" if "short" in n.lower() else "promo, intro, short video" if "medium" in n.lower() else "YouTube video, full length"
PLAY = '<svg width="12" height="14" viewBox="0 0 12 14" aria-hidden="true"><path d="M1 1l10 6-10 6z" fill="currentColor"/></svg>'
I_DL = '<svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true"><path d="M7 1v8M3.5 5.5L7 9l3.5-3.5M2 12.5h10" fill="none" stroke="currentColor" stroke-width="1.7"/></svg>'
I_COPY = '<svg width="15" height="15" viewBox="0 0 16 16" aria-hidden="true"><rect x="5" y="5" width="9" height="9" rx="2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M11 5V3a1 1 0 0 0-1-1H3a1 1 0 0 0-1 1v7a1 1 0 0 0 1 1h2" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>'
I_ZIP = '<svg width="15" height="15" viewBox="0 0 16 16" aria-hidden="true"><path d="M2 4.5h12v9H2zM1.5 2.5h5l1.5 2" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M8 7v4M6.5 9.5L8 11l1.5-1.5" fill="none" stroke="currentColor" stroke-width="1.4"/></svg>'

def wave(p, s, n):
    out = []
    for i in range(n):
        c = p[i * len(p) // n] if p else "k"
        v = max(0, B36.find(c)) / 35
        out.append(f'<i style="height:{round(12 + 88 * v ** 1.3)}%"></i>')
    return f'<div class="wave" data-w="{s}" title="Click to play from here">{"".join(out)}</div>'

def versrows(x, acts):
    v = [["Full", x["d"]]] + x["v"]
    out = []
    for i, (n, d) in enumerate(v):
        if i == 0: btn = f'<button class="pb pbx" data-play="{x["s"]}" aria-label="Play {e(x["t"])}">{PLAY}</button>'
        elif n in x.get("av", []): btn = f'<button class="pb pbx" data-play="{x["s"]}" data-v="{e(n)}" aria-label="Play {e(x["t"])} {e(n)}">{PLAY}</button>'
        else: btn = '<span class="ph" title="Inside the ZIP">ZIP</span>'
        out.append(f'<div class="vr">{btn}<span class="n">{e(n)}</span><span class="u">{use_of(n)}</span><span class="d">{fmt(d) if d else ""}</span></div>')
    rows = "".join(out)
    if not acts: return rows
    ft = '<div class="ft">'
    if x["zip"]: ft += f'<a class="btn main" href="{DL(x["zip"])}" rel="nofollow" data-gc="zip">{I_ZIP} All {len(v)} edits · ZIP</a>'
    ft += f'<a class="btn" href="{DL(x["mp3"])}" rel="nofollow" data-gc="mp3">{I_DL} Full MP3</a><button class="btn" data-copy="{x["s"]}">{I_COPY} Copy credit</button>'
    if x["sh"]: ft += f'<a class="btn soc" href="{e(x["sh"])}" target="_blank" rel="noopener" data-gc="use-yt">{ICO["yt"]} Use in YT Shorts</a>'
    return rows + ft + '</div>'

def row(x):
    n = len(x["v"]) + 1; s = x["s"]
    tags = [u.replace("and ", "", 1) if u.startswith("and ") else u for u in USES.get(x["g"], "").split(", ")][:2]
    return f"""<div class="row" id="{s}" data-s="{s}">
<button class="pb desk pbx" data-play="{s}" aria-label="Play {e(x['t'])}">{PLAY}</button>
<div class="cvw"><img class="cv" loading="lazy" src="{TH(x['cover'], 120)}" alt=""><button class="pb mob pbx" data-play="{s}" aria-label="Play {e(x['t'])}">{PLAY}</button></div>
<div class="tt"><a href="/t/{s}/">{e(x['t'])}</a><div class="sub">{e(x['g'].split(',')[0])} · <span class="mobdur">{fmt(x['d'])} · </span>{f'<button class="edbtn" data-ed="{s}">{n} edits ▾</button>' if n > 1 else ''}</div></div>
<div class="tags">{''.join(f'<span class="tag">{e(t)}</span>' for t in tags)}</div>
<div class="wave" data-w="{s}" title="Click to play from here"></div>
<div class="dur">{fmt(x['d'])}</div>
<div class="acts"><button class="btn ib dk" title="Copy credit" aria-label="Copy credit for {e(x['t'])}" data-copy="{s}">{I_COPY}</button>{f'<a class="btn ib dk" title="All {n} edits in one ZIP" aria-label="Download all edits ZIP" href="{DL(x["zip"])}" rel="nofollow" data-gc="zip">{I_ZIP}</a>' if x['zip'] else ''}<a class="btn main" href="{DL(x['mp3'])}" rel="nofollow" data-gc="mp3" aria-label="Free download MP3">{I_DL}<span>MP3</span></a></div>
<div class="vp" id="vp-{s}" hidden></div>
</div>"""

def main():
    tracks = load("data/tracks.json", []); rank = load("data/rank.json", {}); meta = load("data/meta.json", {})
    audio = load("data/audio.json", {}); social = load("data/social.json", {}); plat = load("data/platforms.json", {}); wv = load("data/wave.json", {}); av = load("data/audio_v.json", {})
    rk = lambda t: rank.get(t["t"], 10**9)
    today = datetime.date.today().isoformat(); urls = [(SITE + "/", "1.0")]
    X = {}
    for t in tracks:
        s = slug(t["t"]); m = meta.get(s, {}); w = wv.get(s, {})
        vers = w.get("v") or [[v.replace(" Version", ""), 0] for v in m.get("v", [])]
        X[s] = {"s": s, "t": t["t"], "g": t["g"], "mp3": t.get("mp3", ""), "zip": t.get("zip", ""), "cover": t.get("cover", ""),
                "d": w.get("d") or m.get("dur") or 0, "v": vers, "p": w.get("p", ""), "al": m.get("al", "Single"),
                "av": (av.get(s) or {}).get("v", []), "sh": (social.get(s) or {}).get("shorts", ""), "src": (REL + s + ".mp3") if s in audio else (f"/previews/{s}.mp3" if t.get("p") else "")}
    tr = lambda xs: {x["s"]: {k: x[k] for k in ("s", "t", "g", "mp3", "zip", "cover", "d", "v", "p", "sh", "src", "av")} for x in xs}
    bygenre = {}
    for t in tracks: bygenre.setdefault(t["g"], []).append(t)
    gorder = [g for g in GORDER if g in bygenre] + sorted(g for g in bygenre if g not in GORDER)
    for t in tracks:
        s = slug(t["t"]); x = X[s]; g = t["g"]; url = f"{SITE}/t/{s}/"
        uses = USES.get(g, "YouTube videos, Shorts, Reels and TikTok")
        title = f"{t['t']} — Free {g.split(',')[0].split(' & ')[0]} Background Music (MP3) | BoDleasons"
        desc = f"Download \"{t['t']}\" by BoDleasons for free: {g.lower()} background music for {uses}. Instant MP3 + Full Pack of edits. Free to use with credit."
        p = plat.get(s, {}); yt = (social.get(s) or {}).get("yt", "")
        listen = [("sp", "Spotify", p.get("sp") and f"https://open.spotify.com/track/{p['sp']}"),
                  ("ap", "Apple Music", p.get("ap") and f"https://music.apple.com/us/song/{p['ap']}"),
                  ("ytm", "YouTube Music", yt and f"https://music.youtube.com/watch?v={yt}"),
                  ("dz", "Deezer", p.get("dz") and f"https://www.deezer.com/track/{p['dz']}")]
        usein = [("yt", "Use in YT Shorts", x["sh"]),
                 ("ig", "Use in Reels", p.get("ig") and f"https://www.instagram.com/reels/audio/{p['ig']}/"),
                 ("tt", "Use in TikTok", p.get("tt") and (p["tt"] if str(p["tt"]).startswith("http") else f"https://www.tiktok.com/music/{p['tt']}"))]
        lb = "".join(f'<a class="btn" href="{e(u)}" target="_blank" rel="noopener" data-gc="listen-{k}">{ICO[k]} {n}</a>' for k, n, u in listen if u)
        ub = "".join(f'<a class="btn soc" href="{e(u)}" target="_blank" rel="noopener" data-gc="use-{k}">{ICO[k]} {n}</a>' for k, n, u in usein if u)
        more = sorted([y for y in bygenre[g] if y is not t], key=rk)[:12]
        if len(more) < 8:
            more += sorted([y for y in tracks if y["g"] != g], key=rk)[:8 - len(more)]
        mx = [X[slug(y["t"])] for y in more]
        cred = f"Music: {t['t']} by BoDleasons\nFree download: {url}"
        vnames = ", ".join(["Full"] + [v[0] for v in x["v"]])
        ld = {"@context": "https://schema.org", "@type": "MusicRecording", "name": t["t"], "url": url,
              "byArtist": {"@type": "MusicGroup", "name": "BoDleasons", "@id": SITE + "/#artist"}, "genre": g,
              "duration": f"PT{int(x['d']) // 60}M{int(x['d']) % 60}S",
              "inAlbum": {"@type": "MusicAlbum", "name": x["al"]}, "image": TH(t.get("cover")),
              "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD", "url": DL(t["mp3"])}}
        n_ed = len(x["v"]) + 1
        page = head(title, desc, url, TH(t.get("cover"))) + f"""
<main class="wrap">
<div class="crumbs"><a href="/">Music</a> › <a href="/genre/{slug(g)}/">{e(g)}</a> › {e(t['t'])}</div>
<div class="thero"><img src="{TH(t.get('cover'))}" alt="{e(t['t'])} — BoDleasons cover">
<div><h1>{e(t['t'])}</h1><p class="by">by BoDleasons · <a href="/genre/{slug(g)}/" style="text-decoration:underline;text-underline-offset:3px">{e(g)}</a> · {fmt(x['d'])}</p>
<p class="lead">Free {e(g.lower())} background music for {e(uses)}. Free to use in your videos with credit.</p></div></div>
<div class="bigp" data-s="{s}"><button class="pb" data-play="{s}" style="color:#0d0b16" aria-label="Play {e(t['t'])}">{PLAY}</button><div class="wave" data-w="{s}" data-n="160" title="Click to play from here"></div></div>
<div class="btns"><a class="btn main" href="{DL(t['mp3'])}" rel="nofollow" data-gc="mp3">{I_DL} Free Download MP3</a>{f'<a class="btn" href="{DL(t["zip"])}" rel="nofollow" data-gc="zip">{I_ZIP} Full Pack · {n_ed} edits (ZIP)</a>' if t.get('zip') else ''}<button class="btn" data-copy="{s}">{I_COPY} Copy credit</button></div>
<p class="note">Free to use with credit: paste the credit line into your video description. Monetized videos may get a Content ID claim — that's normal, your video stays up.</p>
{f'<p class="plh">Use in short videos</p><div class="pl">{ub}</div>' if ub else ''}{f'<p class="plh">Listen on</p><div class="pl">{lb}</div>' if lb else ''}
<div class="two">
<div><div class="sech" style="margin-top:0"><h2 style="font-size:17px">Edits — listen and download ({n_ed} in the Full Pack)</h2></div><div class="vp" style="margin:0">{versrows(x, False)}</div></div>
<div style="display:flex;flex-direction:column;gap:14px">
<div class="box"><h3>How to credit</h3><p style="margin:0">Paste into your video description:</p><code class="credit">{e(cred)}</code><button class="btn" data-copy="{s}">{I_COPY} Copy credit</button>
<p>A Content ID claim is not a strike — your video stays online. Want the claim released or a commercial license? Email the video link to <a href="mailto:bodleason.make@gmail.com" style="text-decoration:underline">bodleason.make@gmail.com</a>.</p></div>
<div class="box"><dl><dt>Track</dt><dd>{e(t['t'])}</dd><dt>Artist</dt><dd>BoDleasons (Bohdan Kuzmin)</dd><dt>Genre</dt><dd><a href="/genre/{slug(g)}/">{e(g)}</a></dd>
<dt>Album</dt><dd>{e(x['al'])}</dd><dt>Length</dt><dd>{fmt(x['d'])}</dd><dt>Versions</dt><dd>{e(vnames)} (no vocals)</dd><dt>License</dt><dd>Free with credit · YouTube Content ID registered</dd></dl></div>
</div></div>
<div class="sech"><h2>You may also like</h2><a href="/genre/{slug(g)}/">All {e(g.split(',')[0])} →</a></div>
<p style="margin:-6px 0 6px;font-size:13px;color:var(--mute)">Plays right here — you stay on this page.</p>
<div class="list">{''.join(row(y) for y in mx)}</div>
<p style="display:flex;gap:8px;flex-wrap:wrap;margin-top:18px"><a class="btn" href="/genre/{slug(g)}/">All {e(g)} tracks →</a><a class="btn" href="/">All {len(tracks)} free tracks →</a></p>
</main><script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>""" + foot(tr([x] + mx))
        os.makedirs(f"t/{s}", exist_ok=True); open(f"t/{s}/index.html", "w").write(page); urls.append((url, "0.8"))
    for g in gorder:
        ts = sorted(bygenre[g], key=rk); xs = [X[slug(y["t"])] for y in ts]
        gs = slug(g); url = f"{SITE}/genre/{gs}/"; uses = USES.get(g, "videos")
        chips = "".join(f'<a class="btn" href="/genre/{slug(o)}/">{e(o.split(",")[0])}</a>' for o in gorder if o != g)
        page = head(f"Free {g} Music for Videos — {len(ts)} tracks, MP3 download | BoDleasons",
                    f"{len(ts)} free {g.lower()} tracks by BoDleasons for {uses}. Instant MP3 download, free to use with credit.", url,
                    TH(ts[0].get("cover")) if ts else "") + f"""
<main class="wrap"><div class="crumbs"><a href="/">Music</a> › {e(g)}</div>
<h1 style="margin:0;font-size:clamp(28px,4vw,40px);font-weight:800;line-height:1.1">Free {e(g)} music for videos</h1>
<p class="lead">{len(ts)} tracks for {e(uses)}. Listen, download the MP3 in one click and use it with credit. Most popular first.</p>
<div class="pl" style="margin:16px 0 6px">{chips}</div>
<div class="list" style="margin-top:14px;border-top:1px solid var(--line);padding-top:6px">{''.join(row(y) for y in xs)}</div></main>""" + foot(tr(xs))
        os.makedirs(f"genre/{gs}", exist_ok=True); open(f"genre/{gs}/index.html", "w").write(page); urls.append((url, "0.9"))
    with open("sitemap.xml", "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for u, pr in urls: f.write(f"<url><loc>{u}</loc><lastmod>{today}</lastmod><priority>{pr}</priority></url>\n")
        f.write("</urlset>\n")
    open("robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    print("страниц треков:", len(tracks), "жанров:", len(bygenre))

if __name__ == "__main__":
    main()
