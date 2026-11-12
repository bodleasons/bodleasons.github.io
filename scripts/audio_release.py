#!/usr/bin/env python3
"""Полные треки для плеера сайта (128 kbps) — в релиз GitHub «audio» (не занимает место сайта, без лимита 1 ГБ).
Источник: публичная папка Google Drive (data/tracks.json от build_data.py).
Какие треки обновить — по data/versions.json (его пишет Mac: время изменения полной MP3) против data/audio.json (что уже загружено).
Запускается в GitHub Actions после build_data.py. Нужны: ffmpeg, gh, переменная GH_TOKEN."""
import json, os, re, subprocess, sys, time, urllib.request
LIMIT = int(os.environ.get("AUDIO_LIMIT", "200"))         # треков за один запуск (остальные — в следующий)
UA = {"User-Agent": "Mozilla/5.0 (BoDleasons site builder)"}
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def get(url, tries=4):
    for i in range(tries):
        try: return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
        except Exception:
            if i == tries - 1: raise
            time.sleep(3 + i * 4)

def sh(*a, check=True): return subprocess.run(a, capture_output=True, text=True, check=check)

def main():
    tracks = json.load(open("data/tracks.json"))
    try: ver = json.load(open("data/versions.json"))
    except Exception: ver = {}
    try: done = json.load(open("data/audio.json"))
    except Exception: done = {}
    if sh("gh", "release", "view", "audio", check=False).returncode != 0:
        sh("gh", "release", "create", "audio", "--title", "Audio for the site player",
           "--notes", "Streaming copies (128 kbps) for bodleasons.github.io. Free downloads: https://bodleasons.github.io")
    # уже загруженные файлы релиза считаем готовыми (если audio.json не успел сохраниться)
    try:
        assets = json.loads(sh("gh", "release", "view", "audio", "--json", "assets").stdout).get("assets", [])
        for a in assets:
            s_ = a["name"][:-4] if a["name"].endswith(".mp3") else None
            if s_ and s_ not in done: done[s_] = ver.get(s_, "1")
    except Exception as e:
        print("список релиза не прочитан:", e)
    todo = [t for t in tracks if t.get("mp3") and str(done.get(slug(t["t"]))) != str(ver.get(slug(t["t"]), "1"))][:LIMIT]
    os.makedirs("/tmp/aud", exist_ok=True); n = 0
    for t in todo:
        s = slug(t["t"]); src = f"/tmp/aud/{s}.src.mp3"; out = f"/tmp/aud/{s}.mp3"
        try:
            data = get(f"https://drive.google.com/uc?export=download&id={t['mp3']}")
            if not (data[:3] == b"ID3" or data[:2] == b"\xff\xfb"): print("не MP3:", t["t"]); continue
            open(src, "wb").write(data)
            sh("ffmpeg", "-y", "-v", "error", "-i", src, "-map", "0:a", "-map_metadata", "-1", "-c:a", "libmp3lame", "-b:a", "128k", out)
            sh("gh", "release", "upload", "audio", out, "--clobber")
            if s in done or not os.path.exists(f"previews/{s}.mp3"):   # трек обновился — превью тоже пересобрать
                os.makedirs("previews", exist_ok=True)
                sh("ffmpeg", "-y", "-v", "error", "-i", src, "-t", "60", "-af", "afade=t=out:st=56:d=4", "-map", "0:a",
                   "-map_metadata", "-1", "-c:a", "libmp3lame", "-b:a", "64k", "-ac", "2", f"previews/{s}.mp3")
            done[s] = ver.get(s, "1"); n += 1
            if n % 20 == 0: json.dump(done, open("data/audio.json", "w"), separators=(",", ":"))
        except Exception as e:
            print("ошибка", t["t"], e)
        finally:
            for f in (src, out):
                if os.path.exists(f): os.remove(f)
    json.dump(done, open("data/audio.json", "w"), separators=(",", ":"))
    print(f"полных треков загружено: {n}, всего в релизе: {len(done)}, осталось: {sum(1 for t in tracks if str(done.get(slug(t['t']))) != str(ver.get(slug(t['t']), '1')))}")

if __name__ == "__main__":
    main()
