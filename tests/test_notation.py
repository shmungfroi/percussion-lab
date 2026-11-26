"""Checks for notation.js (spec P4): the 40 PAS rudiments drawn as our own SVG.

Usage:  python3 tests/test_notation.py      (needs: pip install playwright; Chrome)
Renders every rudiment to tests/out/notation/NN.png (desktop) and
tests/out/notation/360/NN.png (phone width) for visual review, and checks:
  - 40 entries, n = 1..40, names identical to the RUDIMENTS (formerly VIC_RUDIMENTS) list in index.html
  - each SVG is well-formed XML, role="img", aria-label with name and sticking, a <title>
  - uses currentColor, no external resources, no fixed pixel size (scales to its box)
  - every note has a sticking letter under it (R/L, graces r/l)
  - every bar adds up to the rudiment's metre (durations in 1/24 of a quarter note)
  - at 360px the drawing fits its box and sticking text stays at least 10.5px tall
"""
import functools, http.server, pathlib, re, socketserver, sys, threading
import xml.etree.ElementTree as ET
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "tests" / "out" / "notation"
(OUT / "360").mkdir(parents=True, exist_ok=True)
SVGNS = "{http://www.w3.org/2000/svg}"

results = []
def check(name, ok, detail=""):
    results.append((name, bool(ok)))
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail and not ok else ""))

def app_names():
    src = (ROOT / "index.html").read_text(encoding="utf-8")
    m = re.search(r"const (?:VIC_)?RUDIMENTS=\[(.*?)\];", src, re.S)
    return re.findall(r"'((?:[^'\\]|\\.)*)'", m.group(1)) if m else []

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

def metre_units(m):
    a, b = m.split("/"); return int(a) * 96 // int(b)

def main():
    socketserver.ThreadingTCPServer.daemon_threads = True
    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{httpd.server_address[1]}/tests/notation_preview.html"
    names = app_names()
    with sync_playwright() as p:
        try: b = p.chromium.launch(channel="chrome")
        except Exception: b = p.chromium.launch()
        errors = []
        pg = b.new_page(viewport={"width": 1200, "height": 900}, device_scale_factor=2)
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto(base); pg.wait_for_timeout(200)
        check("notation.js loads without script errors", not errors, "; ".join(errors))
        lst = pg.evaluate("Rudiments.list")
        check("40 entries", len(lst) == 40, str(len(lst)))
        check("n runs 1..40 in order", [r["n"] for r in lst] == list(range(1, 41)))
        check("index.html RUDIMENTS list found (40 names)", len(names) == 40, str(len(names)))
        bad = [(r["n"], r["name"], names[i] if i < len(names) else None) for i, r in enumerate(lst) if i >= len(names) or r["name"] != names[i]]
        check("names match index.html order exactly", not bad, str(bad))
        check("every entry has a family", all(r.get("family") in ("Roll", "Diddle", "Flam", "Drag") for r in lst))
        check("unknown n returns empty string", pg.evaluate("Rudiments.svg(0)===''&&Rudiments.svg(41)===''"))

        per = {"xml": [], "a11y": [], "color": [], "external": [], "sticking": [], "metre": [], "fit360": []}
        for r in lst:
            n = r["n"]
            s = pg.evaluate("n=>Rudiments.svg(n)", n)
            try:
                root = ET.fromstring(s)
            except ET.ParseError as e:
                per["xml"].append(f"{n}: {e}"); continue
            label = root.get("aria-label") or ""
            info = pg.evaluate("n=>Rudiments.parse(n)", n)
            if root.get("role") != "img" or r["name"] not in label or "Sticking" not in label or root.find(SVGNS + "title") is None:
                per["a11y"].append(n)
            if root.get("fill") != "currentColor" or re.search(r'(fill|stroke)="#', s) or root.get("height") or root.get("width") != "100%":
                per["color"].append(n)
            if re.search(r"href|url\(|<image|@import|http(?!://www\.w3\.org/2000/svg)", s):
                per["external"].append(n)
            # sticking: one main sticking text per note, letters only R/L (graces r/l)
            notes = [g for g in root.iter(SVGNS + "g") if g.get("class") == "note"]
            stk = [t for t in root.iter(SVGNS + "text") if t.get("class") == "stk"]
            gstk = [t for t in root.iter(SVGNS + "text") if t.get("class") == "stk grace-stk"]
            graces = [g for g in root.iter(SVGNS + "g") if g.get("class") == "grace"]
            if not notes or len(stk) != len(notes) or len(gstk) != len(graces) or not all(re.fullmatch(r"(RR?|LL?)", t.text or "") for t in stk) \
               or not all(re.fullmatch(r"(rr?|ll?)", t.text or "") for t in gstk):
                per["sticking"].append(f"{n}: notes={len(notes)} stk={len(stk)}")
            # metre: every bar's notes + rests add up to the stated metre
            want = metre_units(r["metre"])
            for bi, bar in enumerate(g for g in root.iter(SVGNS + "g") if g.get("class") == "bar"):
                got = sum(float(g.get("data-dur")) for g in bar.iter(SVGNS + "g") if g.get("class") in ("note", "rest"))
                if abs(got - want) > 1e-6 or int(bar.get("data-metre-units")) != want:
                    per["metre"].append(f"{n} bar {bi+1}: {got} != {want}")
            if not info["bars"]:
                per["metre"].append(f"{n}: no bars")
            pg.locator(f"#r{n}").screenshot(path=str(OUT / f"{n:02d}.png"))

        check("every SVG is well-formed XML", not per["xml"], str(per["xml"]))
        check("role=img, aria-label with name and sticking, <title>", not per["a11y"], str(per["a11y"]))
        check("currentColor only, width 100%, no fixed height", not per["color"], str(per["color"]))
        check("no external resources", not per["external"], str(per["external"]))
        check("a sticking letter under every note (R/L, graces r/l)", not per["sticking"], str(per["sticking"]))
        check("every bar adds up to its metre", not per["metre"], str(per["metre"]))

        # phone width
        pm = b.new_page(viewport={"width": 390, "height": 800}, device_scale_factor=2)
        pm.goto(base + "?w=360"); pm.wait_for_timeout(200)
        dims = pm.evaluate("""()=>[...document.querySelectorAll('.card')].map(c=>{const s=c.querySelector('svg');const vb=s.viewBox.baseVal;
            const w=s.getBoundingClientRect().width;return {id:c.id,w,box:c.clientWidth,vbw:vb.width,font:13*w/vb.width,
            over:s.getBoundingClientRect().right>c.getBoundingClientRect().right+0.5}})""")
        small = [d["id"] for d in dims if d["font"] < 10.5 or d["over"]]
        check("at 360px every rudiment fits its box with sticking >= 10.5px", not small,
              str([(d["id"], round(d["font"], 1)) for d in dims if d["id"] in small]))
        for i in range(1, 41):
            pm.locator(f"#r{i}").screenshot(path=str(OUT / "360" / f"{i:02d}.png"))
        pd = b.new_page(viewport={"width": 1200, "height": 900})
        pd.goto(base + "?dark=1"); pd.wait_for_timeout(150)
        col = pd.evaluate("getComputedStyle(document.querySelector('.card svg')).color")
        check("dark background: notation takes the text colour", col == pd.evaluate("getComputedStyle(document.body).color"), col)
        pd.screenshot(path=str(OUT / "preview_dark.png"), full_page=True)
        b.close()
    httpd.shutdown()
    fails = [n for n, ok in results if not ok]
    print(f"\n{len(results) - len(fails)}/{len(results)} passed")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
