"""Checks for notation.js: the 40 PAS rudiments drawn as our own SVG, matching the
reference chart (PAS 40 International Drum Rudiments as shown on the Vic Firth poster, 2016).

Usage:  python3 tests/test_notation.py      (needs: pip install playwright; Chrome)
Renders every rudiment to tests/out/notation/NN.png (desktop) and
tests/out/notation/360/NN.png (phone width) for visual review, and checks:
  - 40 entries, n = 1..40, names identical to the RUDIMENTS list in index.html
  - each SVG is well-formed XML, role="img", aria-label with name and sticking, a <title>
  - uses currentColor, no external resources, no fixed pixel size (scales to its box)
  - no time signature and no clef (the reference shows neither); opening thick-thin bar line,
    closing thin-thick bar line, five-line staff
  - per rudiment, counted from the reference chart: notes, accents, flam and drag graces, rests,
    ties, tuplet numbers, tremolo slashes, dots, "or" alternatives, second sticking row,
    32nd beams and partial (stub) beams
  - sticking letters only R/L (small r/l for grace and small letters), spaces and "etc."
  - at 360px the drawing fits its box and sticking text stays at least 10.5px tall
"""
import functools, http.server, pathlib, re, socketserver, sys, threading
import xml.etree.ElementTree as ET
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "tests" / "out" / "notation"
(OUT / "360").mkdir(parents=True, exist_ok=True)
SVGNS = "{http://www.w3.org/2000/svg}"

# Counted by eye from the reference chart, one rudiment at a time (27 Nov 2026).
# n: (notes, accents, flams, drags, rests, ties, tuplet numbers, tremolo slashes, dots, "or", second row)
EXPECT = {
    1: (16, 0, 0, 0, 0, 0, 0, 0, 0, 0, False),
    2: (8, 0, 0, 0, 0, 0, 2, 0, 0, 0, True),
    3: (14, 0, 0, 0, 0, 0, 2, 0, 0, 0, True),
    4: (1, 0, 0, 0, 0, 0, 0, 0, 0, 0, False),
    5: (12, 0, 0, 0, 0, 0, 4, 0, 0, 0, False),
    6: (1, 0, 0, 0, 0, 0, 0, 3, 0, 0, False),
    7: (10, 4, 0, 0, 0, 2, 2, 8, 0, 1, False),
    8: (9, 5, 0, 0, 1, 2, 0, 6, 0, 0, True),
    9: (14, 4, 0, 0, 1, 1, 2, 11, 1, 1, True),
    10: (8, 4, 0, 0, 0, 4, 0, 12, 0, 1, False),
    11: (19, 9, 0, 0, 2, 2, 4, 14, 0, 1, True),
    12: (19, 5, 0, 0, 2, 2, 4, 18, 0, 1, True),
    13: (4, 2, 0, 0, 0, 2, 0, 6, 2, 0, False),
    14: (7, 3, 0, 0, 0, 4, 0, 10, 2, 1, True),
    15: (4, 2, 0, 0, 0, 2, 0, 6, 0, 0, False),
    16: (8, 2, 0, 0, 0, 0, 0, 0, 0, 0, False),
    17: (12, 2, 0, 0, 0, 0, 0, 0, 0, 0, False),
    18: (16, 2, 0, 0, 0, 0, 0, 0, 0, 0, False),
    19: (12, 2, 0, 0, 0, 0, 0, 0, 0, 0, True),
    20: (8, 8, 8, 0, 0, 0, 0, 0, 0, 0, False),
    21: (6, 2, 2, 0, 0, 0, 2, 0, 0, 0, False),
    22: (8, 4, 4, 0, 0, 0, 0, 0, 0, 0, False),
    23: (5, 2, 2, 0, 0, 0, 0, 0, 0, 0, True),
    24: (8, 2, 2, 0, 0, 0, 0, 0, 0, 0, False),
    25: (8, 2, 2, 0, 0, 0, 0, 0, 0, 0, False),
    26: (12, 2, 2, 0, 0, 0, 0, 0, 0, 0, False),
    27: (8, 4, 4, 0, 0, 0, 0, 0, 0, 0, True),
    28: (12, 4, 4, 0, 0, 0, 4, 0, 0, 0, True),
    29: (8, 4, 4, 0, 0, 0, 0, 0, 0, 0, False),
    30: (8, 2, 2, 0, 0, 0, 2, 0, 0, 0, False),
    31: (4, 0, 0, 4, 0, 0, 0, 0, 0, 0, False),
    32: (12, 4, 0, 2, 1, 0, 3, 3, 0, 1, False),
    33: (20, 4, 0, 4, 1, 0, 0, 6, 2, 1, False),
    34: (17, 4, 0, 2, 1, 0, 0, 3, 0, 1, True),
    35: (8, 2, 0, 0, 0, 0, 0, 2, 0, 0, False),
    36: (10, 2, 0, 2, 0, 0, 0, 0, 0, 0, False),
    37: (12, 2, 0, 4, 0, 0, 0, 0, 0, 0, False),
    38: (8, 2, 0, 2, 0, 0, 2, 0, 0, 0, False),
    39: (10, 2, 0, 4, 0, 0, 2, 0, 0, 0, False),
    40: (12, 2, 0, 6, 0, 0, 2, 0, 0, 0, False),
}
FIELDS = ("notes", "accents", "flams", "drags", "rests", "ties", "tuplets", "slashes", "dots", "or", "row2")
THIRTYSECONDS = {1}  # #3 is sixteenth sextuplets (two beams) on the poster; corrected 27 Nov
STUBS = {8: 4, 9: 1, 14: 2, 33: 2}      # partial (stub) beams; none elsewhere
SPOT = {                                # exact sticking strings written under one note
    4: "R L R L R L R L etc.", 6: "R R L L R R L L R R L L R R L L etc.",
    15: "RRLLRRLLRRLLRRLL", 35: "R R", 31: "llR",
}
NAMES = {6: "Double Stroke Roll", 19: "Paradiddle–Diddle", 26: "Flam Paradiddle–Diddle", 31: "Drag (Ruff)",
         34: "Lesson 25", 36: "Drag Paradiddle #1", 37: "Drag Paradiddle #2"}

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

def counts(root):
    gs = list(root.iter(SVGNS + "g")); texts = list(root.iter(SVGNS + "text")); paths = list(root.iter(SVGNS + "path"))
    notes = [g for g in gs if g.get("class") == "note"]
    return {
        "notes": len(notes),
        "accents": sum(1 for p in paths if p.get("class") == "accent"),
        "flams": sum(1 for g in gs if g.get("class") == "grace" and g.get("data-n") == "1"),
        "drags": sum(1 for g in gs if g.get("class") == "grace" and g.get("data-n") == "2"),
        "rests": sum(1 for g in gs if g.get("class") == "rest"),
        "ties": sum(1 for p in paths if p.get("class") == "tie"),
        "tuplets": sum(1 for t in texts if t.get("class") == "tuplet"),
        "slashes": sum(1 for p in paths if p.get("class") == "trem"),
        "dots": sum(1 for c in root.iter(SVGNS + "circle") if c.get("class") == "dot"),
        "or": sum(1 for t in texts if t.get("class") == "or"),
        "row2": any(t.get("class") == "stk" and t.get("data-row") == "2" for t in texts),
    }

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
        check("names as titled on the reference chart (6, 19, 26, 31, 34, 36, 37)", all(lst[n - 1]["name"] == v for n, v in NAMES.items()),
              str([(n, lst[n - 1]["name"]) for n, v in NAMES.items() if lst[n - 1]["name"] != v]))
        check("every entry has a family", all(r.get("family") in ("Roll", "Diddle", "Flam", "Drag") for r in lst))
        check("unknown n returns empty string", pg.evaluate("Rudiments.svg(0)===''&&Rudiments.svg(41)===''"))

        per = {k: [] for k in ("xml", "a11y", "color", "external", "letters", "nometre", "bars", "counts", "beams32", "stubs", "spot", "wide")}
        for r in lst:
            n = r["n"]
            for mw, tag in ((None, ""), (2000, " one line")):
                s = pg.evaluate("([n,mw])=>Rudiments.svg(n, mw?{maxWidth:mw}:undefined)", [n, mw])
                try:
                    root = ET.fromstring(s)
                except ET.ParseError as e:
                    per["xml"].append(f"{n}{tag}: {e}"); continue
                got = counts(root)
                want = dict(zip(FIELDS, EXPECT[n]))
                diff = {k: (got[k], want[k]) for k in FIELDS if got[k] != want[k]}
                if diff: per["counts"].append(f"{n}{tag}: {diff}")
                if mw: continue
                label = root.get("aria-label") or ""
                if root.get("role") != "img" or r["name"] not in label or "Sticking" not in label or root.find(SVGNS + "title") is None:
                    per["a11y"].append(n)
                if root.get("fill") != "currentColor" or re.search(r'(fill|stroke)="#', s) or root.get("height") or root.get("width") != "100%":
                    per["color"].append(n)
                if re.search(r"href|url\(|<image|@import|http(?!://www\.w3\.org/2000/svg)", s):
                    per["external"].append(n)
                stk = [t for t in root.iter(SVGNS + "text") if t.get("class") == "stk"]
                if not stk or not all(re.fullmatch(r"[RLrl ]+( etc\.)?", t.get("data-text") or "") for t in stk):
                    per["letters"].append(n)
                if "timesig" in s or "data-metre" in s or "clef" in s:
                    per["nometre"].append(n)
                thick = [e for e in root.iter(SVGNS + "rect") if (e.get("class") or "").startswith("barline thick")]
                staff = [e for e in root.iter(SVGNS + "line") if e.get("class") == "staff"]
                if len(thick) != 2 or not staff:
                    per["bars"].append(n)
                lv3 = any(e.get("data-level") == "3" for e in root.iter(SVGNS + "rect"))
                if lv3 != (n in THIRTYSECONDS): per["beams32"].append(n)
                stubs = sum(1 for e in root.iter(SVGNS + "rect") if e.get("data-stub"))
                if stubs != STUBS.get(n, 0): per["stubs"].append(f"{n}: {stubs}")
                if n in SPOT and not any(t.get("data-text") == SPOT[n] for t in stk): per["spot"].append(n)
                vb = [float(v) for v in root.get("viewBox").split()]
                if vb[2] > 372: per["wide"].append(f"{n}: {vb[2]}")
            pg.locator(f"#r{n}").screenshot(path=str(OUT / f"{n:02d}.png"))

        check("every SVG is well-formed XML", not per["xml"], str(per["xml"]))
        check("role=img, aria-label with name and sticking, <title>", not per["a11y"], str(per["a11y"]))
        check("currentColor only, width 100%, no fixed height", not per["color"], str(per["color"]))
        check("no external resources", not per["external"], str(per["external"]))
        check("sticking text is R/L, small r/l, spaces and 'etc.' only", not per["letters"], str(per["letters"]))
        check("no time signature or clef (the reference shows none)", not per["nometre"], str(per["nometre"]))
        check("five-line staff, opening thick-thin and closing thin-thick bar lines", not per["bars"], str(per["bars"]))
        check("notes, accents, graces, rests, ties, tuplets, slashes, dots, 'or' and second rows match the reference (wrapped and one line)",
              not per["counts"], "; ".join(per["counts"][:6]))
        check("32nd-note (three) full beams only on 1", not per["beams32"], str(per["beams32"]))
        check("partial beams only where drawn (6 Stroke 4, 7 Stroke 1, 15 Stroke 2, Double Drag Tap 2)", not per["stubs"], str(per["stubs"]))
        check("multi-letter sticking under one note kept exactly (4, 6, 15, 31, 35)", not per["spot"], str(per["spot"]))
        check("default drawing stays within 370 units wide (wraps instead of squashing)", not per["wide"], str(per["wide"]))
        two = pg.evaluate("[2,3,8,9,11,12,14,19,23,27,28,34].every(n=>Rudiments.parse(n).sticking2.length>0)")
        check("second sticking row present on 2, 3, 8, 9, 11, 12, 14, 19, 23, 27, 28, 34", two)

        # phone width
        pm = b.new_page(viewport={"width": 390, "height": 800}, device_scale_factor=2)
        pm.goto(base + "?w=360"); pm.wait_for_timeout(200)
        dims = pm.evaluate("""()=>[...document.querySelectorAll('.card')].map(c=>{const s=c.querySelector('svg');const vb=s.viewBox.baseVal;
            const w=s.getBoundingClientRect().width;return {id:c.id,w,box:c.clientWidth,vbw:vb.width,font:13.5*w/vb.width,
            over:s.getBoundingClientRect().right>c.getBoundingClientRect().right+0.5}})""")
        small = [d["id"] for d in dims if d["font"] < 10.5 or d["over"]]
        check("at 360px every rudiment fits its box with sticking >= 10.5px", not small,
              str([(d["id"], round(d["font"], 1)) for d in dims if d["id"] in small]))
        f320 = pm.evaluate("""()=>{const box=document.createElement('div');box.style.width='320px';document.body.appendChild(box);let worst=99;
            for(let n=1;n<=40;n++){box.innerHTML=Rudiments.svg(n,{maxWidth:340});const s=box.querySelector('svg');const w=s.getBoundingClientRect().width;
            worst=Math.min(worst,13.5*w/s.viewBox.baseVal.width)}box.remove();return worst}""")
        check("in a 320px box (app phone setting) sticking text is at least 11px", f320 >= 11, str(round(f320, 2)))
        stray = pm.evaluate("""()=>{const box=document.createElement('div');box.style.width='320px';document.body.appendChild(box);const bad=[];
            for(let n=1;n<=40;n++){box.innerHTML=Rudiments.svg(n,{maxWidth:340});const sys=[...box.querySelectorAll('g.system')];const h=box.querySelector('svg').viewBox.baseVal.height/sys.length;
            sys.forEach((g,i)=>{const r=g.getBBox();if(r.y<i*h-0.5||r.y+r.height>(i+1)*h+0.5)bad.push(n+'/'+(i+1))})}box.remove();return bad}""")
        check("wrapped lines: every mark stays inside its own line", not stray, str(stray))
        for i in range(1, 41):
            pm.locator(f"#r{i}").screenshot(path=str(OUT / "360" / f"{i:02d}.png"))
        pd = b.new_page(viewport={"width": 1200, "height": 900})
        pd.goto(base + "?dark=1"); pd.wait_for_timeout(150)
        col = pd.evaluate("getComputedStyle(document.querySelector('.card svg')).color")
        check("dark background: notation takes the text colour", col == pd.evaluate("getComputedStyle(document.body).color"), col)
        pd.screenshot(path=str(OUT / "preview_dark.png"), full_page=True)
        pl = b.new_page(viewport={"width": 1200, "height": 900})
        pl.goto(base); pl.wait_for_timeout(150)
        col = pl.evaluate("getComputedStyle(document.querySelector('.card svg')).color")
        check("light background: notation takes the text colour", col == pl.evaluate("getComputedStyle(document.body).color") and col != pd.evaluate("getComputedStyle(document.body).color"), col)
        b.close()
    httpd.shutdown()
    fails = [n for n, ok in results if not ok]
    print(f"\n{len(results) - len(fails)}/{len(results)} passed")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
