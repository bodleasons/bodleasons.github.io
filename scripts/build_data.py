#!/usr/bin/env python3
"""Собирает data/tracks.json и data/new.json из ПУБЛИЧНОЙ папки Google Drive «BoDleasons Free Music».
Запускается GitHub Actions (каждый день) — ничего не нужно делать руками.
Структура папки: <Жанр>/<Трек>/{<Трек> - BoDleasons.mp3, ... (All Versions).zip, cover.jpg}; в корне new_this_week.json."""
import json, os, re, sys, time, urllib.request, concurrent.futures as cf
ROOT = "1FQFmGJ5hXXaYXId8siVZ9YQ5q_8sAIZw"
UA = {"User-Agent": "Mozilla/5.0 (BoDleasons site builder)"}

def get(url, tries=4):
    for i in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        except Exception as e:
            if i == tries - 1: raise
            time.sleep(2 + i * 3)

def ls(fid):
    h = get(f"https://drive.google.com/embeddedfolderview?id={fid}").decode("utf-8", "replace")
    out = []
    for m in re.finditer(r'id="entry-([^"]+)"[\s\S]*?href="([^"]+)"[\s\S]*?class="flip-entry-title">([^<]+)<', h):
        name = m.group(3).strip().replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", '"')
        out.append({"id": m.group(1), "name": name, "folder": "/folders/" in m.group(2)})
    return out

def main():
    root = ls(ROOT)
    if not root: sys.exit("пустой корень — Drive не ответил, данные не трогаю")
    # файлы сайта лежат в корне папки: _site_<путь, где / заменён на __>, напр. _site_index.html → index.html
    for x in root:
        if not x["folder"] and x["name"].startswith("_site_"):
            path = x["name"][6:].replace("__", "/")
            try:
                data = get(f"https://drive.google.com/uc?export=download&id={x['id']}")
                if b"bodleasons-site" in data or not path.endswith(".html"):   # защита от страницы-ошибки Google
                    os.makedirs(os.path.dirname(path) or ".", exist_ok=True); open(path, "wb").write(data)
                    print("site:", path, len(data))
            except Exception as e:
                print("site file", path, "не скачан:", e)
    tracks = []
    genres = [x for x in root if x["folder"] and not x["name"].startswith("_")]
    jobs = []
    for g in genres:
        for t in ls(g["id"]):
            if t["folder"]: jobs.append((g["name"], t))
    def one(a):
        g, t = a; f = ls(t["id"])
        pick = lambda cond: next((z["id"] for z in f if cond(z["name"])), "")
        return {"t": t["name"], "g": g, "folder": t["id"],
                "mp3": pick(lambda n: n.endswith("BoDleasons.mp3")), "zip": pick(lambda n: n.endswith(".zip")),
                "cover": pick(lambda n: n == "cover.jpg")}
    with cf.ThreadPoolExecutor(8) as ex: tracks = list(ex.map(one, jobs))
    tracks = [x for x in tracks if x["mp3"]]
    tracks.sort(key=lambda x: (x["g"], x["t"].lower()))
    if len(tracks) < 100: sys.exit(f"подозрительно мало треков ({len(tracks)}) — данные не трогаю")
    json.dump(tracks, open("data/tracks.json", "w"), ensure_ascii=False, separators=(",", ":"))
    new = next((x for x in root if x["name"] == "new_this_week.json"), None)
    if new:
        try:
            data = json.loads(get(f"https://drive.google.com/uc?export=download&id={new['id']}"))
            json.dump(data, open("data/new.json", "w"), ensure_ascii=False, indent=0)
        except Exception as e:
            print("new_this_week.json не прочитан:", e)
    print("треков:", len(tracks))

if __name__ == "__main__":
    main()
