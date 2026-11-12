#!/usr/bin/env python3
"""Публикует в Telegram-канал трек дня — когда по расписанию (data/new.json) выходит видео с этим треком.
MP3 играет прямо в Telegram + обложка + ссылка на страницу трека на сайте. Каждый трек — не чаще раза в 3 дня.
Нужно: секрет TELEGRAM_BOT_TOKEN (GitHub → Settings → Secrets), канал в data/telegram_channel.txt (напр. @bodleasons_music).
Запускается в GitHub Actions после build_pages.py."""
import datetime, json, os, re, time, urllib.request, uuid
from zoneinfo import ZoneInfo
SITE = "https://bodleasons.github.io"
UA = {"User-Agent": "Mozilla/5.0 (BoDleasons site builder)"}
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def load(p, d):
    try: return json.load(open(p))
    except Exception: return d

def get(url):
    for i in range(4):
        try: return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
        except Exception:
            if i == 3: raise
            time.sleep(3 + 4 * i)

def send_audio(token, chat, audio, fname, title, caption, thumb=None):
    b = uuid.uuid4().hex; parts = []
    def field(k, v): parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    def file(k, name, data, ct):
        parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{k}"; filename="{name}"\r\nContent-Type: {ct}\r\n\r\n'.encode() + data + b"\r\n")
    field("chat_id", chat); field("title", title); field("performer", "BoDleasons")
    field("caption", caption); field("parse_mode", "HTML")
    file("audio", fname, audio, "audio/mpeg")
    if thumb: file("thumbnail", "cover.jpg", thumb, "image/jpeg")
    parts.append(f"--{b}--\r\n".encode())
    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendAudio", data=b"".join(parts),
                                 headers={"Content-Type": f"multipart/form-data; boundary={b}"})
    return json.loads(urllib.request.urlopen(req, timeout=300).read())

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    try: chat = open("data/telegram_channel.txt").read().strip()
    except Exception: chat = ""
    if not token or not chat: print("Telegram: нет токена или канала — пропуск"); return
    tracks = {slug(t["t"]): t for t in load("data/tracks.json", [])}
    social = load("data/social.json", {}); posted = load("data/telegram.json", {})
    now = datetime.datetime.now(ZoneInfo("Europe/Kyiv"))
    due = []
    for x in load("data/new.json", []):
        when = datetime.datetime.fromisoformat(f"{x['date']}T{x.get('time', '12:00')}:00").replace(tzinfo=ZoneInfo("Europe/Kyiv"))
        s = slug(x["track"])
        if when <= now and now - when < datetime.timedelta(hours=36) and s in tracks:
            last = posted.get(s)
            if not last or now - datetime.datetime.fromisoformat(last) > datetime.timedelta(days=3): due.append(s)
    for s in dict.fromkeys(due):
        t = tracks[s]; g = t["g"]
        tag = "#" + re.sub(r"[^A-Za-z0-9]", "", g.split(",")[0].split(" & ")[0])
        cap = (f"🎵 <b>{t['t']}</b> — BoDleasons\n{g} · free to use in your videos with credit\n\n"
               f"⬇️ Free download & all versions: {SITE}/t/{s}/\n")
        if social.get(s, {}).get("shorts"): cap += f"🎬 Use in YouTube Shorts: {social[s]['shorts']}\n"
        cap += f"🎧 500+ free tracks: {SITE}\n\n#BoDleasons {tag} #freemusic #backgroundmusic"
        try:
            audio = get(f"https://drive.google.com/uc?export=download&id={t['mp3']}")
            thumb = get(f"https://lh3.googleusercontent.com/d/{t['cover']}=w320") if t.get("cover") else None
            r = send_audio(token, chat, audio, f"{t['t']} - BoDleasons.mp3", t["t"], cap, thumb)
            print("Telegram:", t["t"], r.get("ok"))
            if r.get("ok"): posted[s] = now.isoformat(timespec="minutes")
        except Exception as e:
            print("Telegram ошибка", t["t"], e)
    json.dump(posted, open("data/telegram.json", "w"), indent=0)

if __name__ == "__main__":
    main()
