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
           "--notes", "Streaming copies (128 kbps) for bodleasons.com. Free downloads: https://bodleasons.com")
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


def versions():
    """Отдельные версии (Medium, Short…) из ZIP → релиз «audio» как <slug>__<версия>.mp3, чтобы их слушать прямо на сайте.
    Что загружено — data/audio_v.json {slug: {"k": ключ из versions.json, "v": [имена версий]}}. Сначала популярные треки."""
    import zipfile, io, glob, shutil
    VLIMIT = int(os.environ.get("AUDIO_V_LIMIT", "150"))
    tracks = json.load(open("data/tracks.json"))
    try: ver = json.load(open("data/versions.json"))
    except Exception: ver = {}
    try: rank = json.load(open("data/rank.json"))
    except Exception: rank = {}
    try: done = json.load(open("data/audio_v.json"))
    except Exception: done = {}
    tracks.sort(key=lambda t: rank.get(t["t"], 10**9))
    # у релиза GitHub лимит 1000 файлов: версии кладём в релизы edits1, edits2, … (в «audio» уже полные треки)
    counts = {}
    def rel_for(k):
        for i in range(1, 20):
            r = f"edits{i}"
            if r not in counts:
                if sh("gh", "release", "view", r, check=False).returncode != 0:
                    sh("gh", "release", "create", r, "--title", f"Track edits {i}", "--notes", "Edits (Medium/Short) for the bodleasons.com player.")
                    counts[r] = 0
                else:
                    try: counts[r] = len(json.loads(sh("gh", "release", "view", r, "--json", "assets").stdout).get("assets", []))
                    except Exception: counts[r] = 999
            if counts[r] + k <= 990: return r
        raise RuntimeError("нет места в релизах edits")
    todo = [t for t in tracks if t.get("zip") and str((done.get(slug(t["t"])) or {}).get("k")) != str(ver.get(slug(t["t"]), "1"))][:VLIMIT]
    n = 0
    for t in todo:
        s = slug(t["t"]); tmp = f"/tmp/av/{s}"; os.makedirs(tmp, exist_ok=True)
        try:
            data = get(f"https://drive.google.com/uc?export=download&id={t['zip']}")
            if data[:2] != b"PK":
                m = re.search(rb'name="uuid" value="([^"]+)"', data)            # большой файл: страница подтверждения Google
                if m: data = get(f"https://drive.usercontent.google.com/download?id={t['zip']}&export=download&confirm=t&uuid={m.group(1).decode()}")
            if data[:2] != b"PK": print("не ZIP:", t["t"]); continue
            names = []
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                for nm in z.namelist():
                    mv = re.search(r"\((.+?) Version\)", nm)
                    if not mv or nm.startswith("__MACOSX") or not nm.lower().endswith((".mp3", ".wav", ".m4a")): continue
                    v = mv.group(1); src = os.path.join(tmp, "src" + os.path.splitext(nm)[1]); out = os.path.join(tmp, f"{s}__{slug(v)}.mp3")
                    with z.open(nm) as a, open(src, "wb") as b: shutil.copyfileobj(a, b)
                    sh("ffmpeg", "-y", "-v", "error", "-i", src, "-map", "0:a", "-map_metadata", "-1", "-c:a", "libmp3lame", "-b:a", "128k", out)
                    names.append(v)
            outs = glob.glob(os.path.join(tmp, f"{s}__*.mp3"))
            r = (done.get(s) or {}).get("r") or rel_for(len(outs))
            if outs:
                sh("gh", "release", "upload", r, *outs, "--clobber")
                if r in counts and not (done.get(s) or {}).get("r"): counts[r] += len(outs)
            done[s] = {"k": ver.get(s, "1"), "v": names, "r": r}; n += 1
            if n % 10 == 0: json.dump(done, open("data/audio_v.json", "w"), separators=(",", ":"))
        except Exception as e:
            print("версии", t["t"], e)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    json.dump(done, open("data/audio_v.json", "w"), separators=(",", ":"))
    print(f"треков с версиями загружено: {n}, всего: {len(done)}, осталось: {sum(1 for t in tracks if t.get('zip') and str((done.get(slug(t['t'])) or {}).get('k')) != str(ver.get(slug(t['t']), '1')))}")

if __name__ == "__main__":
    main()
    versions()
