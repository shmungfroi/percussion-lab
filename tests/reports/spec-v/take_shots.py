"""Spec V evidence: screenshots of Percussion Lab (dark and light, 1366 and 390 px) and The Guitar Lab for comparison.

Usage:  python3 tests/reports/spec-v/take_shots.py [path to the Guitar Lab folder]
Output: tests/reports/spec-v/shots/*.png
Progress is seeded through localStorage the same way tests/run_tests.py does, so the screens are not empty.
"""
import functools, http.server, json, pathlib, socketserver, sys, threading
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(ROOT / "tests"))
import run_tests as T

SHOTS = HERE / "shots"; SHOTS.mkdir(exist_ok=True)
GUITAR = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / "guitar-lab"

def state():
    s = T.seed(tempos=[{"id": f"t{i}", "item": "rud:1", "bpm": b, "date": T.D(12 - i)} for i, b in enumerate((72, 76, 80, 84, 88, 96))])
    s["skills"] = SKILLS
    s["draft"]["checks"] = ["pulse", "diamond"]
    s["sessions"] += [{"id": f"s-x{i}", "date": T.D(d), "minutes": m, "checks": ["pulse"], "focus": "Paradiddle accents", "heard": "", "worked": "Even at 84", "next": "", "evidence": "", "savedAt": "2026-03-01T00:00:00Z"} for i, (d, m) in enumerate(((16, 20), (22, 35), (37, 15), (44, 40)))]
    s["rudimentChecks"].update({"2": {"done": True, "date": T.D(9)}, "16": {"done": True, "date": T.D(3)}})
    return s
SKILLS = {}

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

def serve(folder):
    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(folder)))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}/index.html"

def main():
    global SKILLS
    socketserver.ThreadingTCPServer.daemon_threads = True
    made = []
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        httpd, url = serve(ROOT)
        for scheme in ("dark", "light"):
            for w, h in ((1366, 900), (390, 844)):
                ctx = b.new_context(viewport={"width": w, "height": h}, color_scheme=scheme)
                pg = ctx.new_page(); pg.goto(url)
                if not SKILLS:
                    ids = pg.evaluate("[...new Set([...document.documentElement.innerHTML.matchAll(/\\{id:'([a-z0-9-]+)',s:'/g)].map(m=>m[1]))]")
                    SKILLS = {i: {"level": (n * 7) % 4, "verified": n % 5 == 2 and (n * 7) % 4 >= 2, "evidence": ""} for n, i in enumerate(ids)}
                pg.evaluate("([k,v])=>localStorage.setItem(k,v)", [T.KEY, json.dumps(state())]); pg.reload()
                pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
                for nav, name in (("today", "today"), ("skills", "technique"), ("rudiment-ref", "rudiments")):
                    pg.click(f"[data-nav={nav}]"); pg.wait_for_timeout(250)
                    f = SHOTS / f"percussion_{name}_{w}_{scheme}.png"; pg.screenshot(path=str(f), full_page=(w == 390 and False)); made.append(f)
                if w == 1366:
                    pg.click("[data-rud-open='21']"); pg.wait_for_timeout(300)
                    f = SHOTS / f"percussion_notation_{w}_{scheme}.png"; pg.screenshot(path=str(f)); made.append(f)
                ctx.close()
        httpd.shutdown()
        if (GUITAR / "index.html").exists():
            httpd, url = serve(GUITAR)
            for scheme in ("dark", "light"):
                for w, h in ((1366, 900), (390, 844)):
                    ctx = b.new_context(viewport={"width": w, "height": h}, color_scheme=scheme)
                    pg = ctx.new_page(); pg.goto(url); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(400)
                    f = SHOTS / f"guitar_{w}_{scheme}.png"; pg.screenshot(path=str(f)); made.append(f); ctx.close()
            httpd.shutdown()
        else: print("Guitar Lab folder not found; comparison shots skipped")
        b.close()
    for f in made: print(f.relative_to(ROOT))

if __name__ == "__main__":
    main()
