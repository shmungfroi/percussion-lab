"""Regression suite for Percussion Lab (formerly Percussion Technique Lab).

Usage:  python3 tests/run_tests.py            (needs: pip install playwright; Chrome)
        python3 tests/run_tests.py --stub     (serve tests/stub_notation.js in place of notation.js)
Serves the repo on a local port, drives index.html in headless Chrome and
prints PASS/FAIL per check. Screenshots go to tests/out/ (ignored by git).
"""
import datetime, functools, http.server, json, pathlib, re, socketserver, subprocess, sys, threading
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "tests" / "out"; OUT.mkdir(exist_ok=True)
KEY = "rbsc-oc-percussion-lab-v1"
# The real notation.js is used when it exists. The stub only checks the app's side of the interface.
STUB = "--stub" in sys.argv or not (ROOT / "notation.js").exists()
TODAY = datetime.date.today()
D = lambda n: (TODAY - datetime.timedelta(days=n)).isoformat()

def seed(sessions=None, draft=None, skills=None, tempos=None):
    s = {"version": 1, "teacher": "JO", "skills": skills or {}, "lessons": {"0": {"checks": [0, 1, 2], "date": D(20)}, "1": {"checks": [0]}},
         "goals": [{"id": "g1", "text": "Choose a tuned-percussion solo", "due": D(-30), "done": False}],
         "sessions": sessions if sessions is not None else [
             {"id": "s-a", "date": D(10), "minutes": 30, "checks": ["pulse", "diamond"], "focus": "332 rotations", "heard": "", "worked": "Clean at 80", "next": "Try 556", "evidence": "", "savedAt": "2026-01-01T00:00:00Z"},
             {"id": "s-b", "date": D(30), "minutes": 0, "checks": ["pulse"], "focus": "Back-dated", "heard": "", "worked": "x", "next": "", "evidence": "", "savedAt": "2026-02-01T00:00:00Z"},
             {"id": "s-c", "date": D(2), "minutes": 25, "checks": [], "focus": "Latest", "heard": "", "worked": "y", "next": "", "evidence": "", "savedAt": "2025-12-01T00:00:00Z"}],
         "rudimentChecks": {"1": {"done": True, "date": D(5)}},
         "draft": draft or {"date": TODAY.isoformat(), "checks": [], "minutes": "", "focus": "", "heard": "", "worked": "", "next": "", "evidence": ""},
         "created": 1}
    if tempos is not None: s["tempos"] = tempos
    return s

CREDIT = "The 40 International Drum Rudiments are the standard list published by the Percussive Arts Society. Notation follows the PAS 40 International Drum Rudiments as shown on the Vic Firth Rudiments poster, redrawn for this app."
results = []
def check(name, ok, detail=""):
    results.append((name, bool(ok), detail)); print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail and not ok else ""))

socketserver.ThreadingTCPServer.daemon_threads = True
class Quiet(http.server.SimpleHTTPRequestHandler):
    def handle(self):
        try: super().handle()
        except (BrokenPipeError, ConnectionResetError): pass
    def log_message(self, *a): pass
    def do_GET(self):
        # /__frame.html: the app inside a sandboxed iframe, as the artifact viewer shows it. Opened via "localhost" so the frame (127.0.0.1) is cross-origin.
        if self.path.startswith("/__frame.html"):
            body = (f'<!doctype html><body style="margin:0"><iframe sandbox="allow-scripts allow-same-origin" src="http://127.0.0.1:{self.server.server_address[1]}/index.html" style="width:1300px;height:860px;border:0"></iframe>').encode()
            self.send_response(200); self.send_header("Content-Type", "text/html"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
        if STUB and self.path.split("?")[0] == "/notation.js": self.path = "/tests/stub_notation.js"
        super().do_GET()

# P1: the app must never call the browser's own dialogs (blocked in sandboxed viewers). Any call throws and fails the run.
NO_NATIVE = "window._prints=0;window.print=()=>{window._prints++};for(const k of ['alert','confirm','prompt'])window[k]=()=>{throw new Error('native '+k+'() was called')}"

def main():
    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{httpd.server_address[1]}/index.html"
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", args=["--autoplay-policy=no-user-gesture-required"])
        errors = []; requests = []
        print("notation: " + ("tests/stub_notation.js (STUB)" if STUB else "notation.js"))
        def page_with(state, w=1366, h=900, ctx=None):
            ctx = ctx or b.new_context(viewport={"width": w, "height": h})
            ctx.add_init_script(NO_NATIVE); ctx.on("request", lambda r: requests.append(r.url))
            pg = ctx.new_page(); pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.goto(url, wait_until="domcontentloaded")
            if state is not None:
                pg.evaluate("([k,v])=>localStorage.setItem(k,v)", [KEY, json.dumps(state)]); pg.reload()
            pg.wait_for_timeout(150); return pg
        get = lambda pg: pg.evaluate(f"JSON.parse(localStorage.getItem('{KEY}'))")

        # Load + C16 + C21 + C29
        pg = page_with(seed())
        check("loads legacy data (no tempos key) without errors", not errors, ";".join(errors))
        txt = pg.inner_text("#panel-today")
        check("C29 dates shown as '25 Nov 2026' style", datetime.date.fromisoformat(D(2)).strftime("%-d %b %Y") in txt)
        pg.click("[data-nav=goals]")
        sums = pg.locator(".history-item summary").all_inner_texts()
        check("C16 journal sorted newest first", sums and "Latest" in sums[0] and "Back-dated" in sums[-1], str(sums))
        check("C21 zero minutes shown as —", "—" in sums[-1] and "(0 min)" not in " ".join(sums))
        pg.screenshot(path=str(OUT / "goals_1366.png"), full_page=True)

        # C12 stale empty draft resets; stale draft with text shows banner
        pg = page_with(seed(draft={"date": D(3), "checks": [], "minutes": "", "focus": "", "heard": "", "worked": "", "next": "", "evidence": ""}))
        check("C12 empty old draft moves to today", get(pg)["draft"]["date"] == TODAY.isoformat())
        pg = page_with(seed(draft={"date": D(3), "checks": ["pulse"], "minutes": "20", "focus": "old", "heard": "", "worked": "", "next": "", "evidence": ""}))
        check("C12 old draft with content shows banner", pg.locator(".draft-banner").count() == 1)
        pg.click("[data-action=draft-today]"); pg.click("#dialog [data-dlg=cancel]")
        check("P1 clear draft: Cancel keeps the draft", get(pg)["draft"]["focus"] == "old" and pg.locator(".draft-banner").count() == 1)
        pg.click("[data-action=draft-today]"); pg.click("#dialog [data-dlg=ok]")
        st = get(pg)["draft"]
        check("C12 'start today' clears the old draft", st["date"] == TODAY.isoformat() and not st["checks"] and st["minutes"] == "25")

        # P1 in-page confirm: dialog behaviour, then cancel and accept for each former confirm()
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        check("P1 no alert/confirm/prompt call in index.html", not re.search(r"(?<![\w$])(?:window\.)?(?:alert|confirm|prompt)\s*\(", html))
        pg = page_with(seed(tempos=[{"id": "t1", "item": "skill:d2", "bpm": 60, "date": D(3)}, {"id": "t2", "item": "rud:16", "bpm": 90, "date": D(1)}]))
        pg.click("[data-nav=goals]"); pg.focus("[data-goal-delete=g1]"); pg.keyboard.press("Enter")
        d = pg.locator("#dialog")
        check("P1 dialog opens as a labelled modal alertdialog", d.is_visible() and d.get_attribute("role") == "alertdialog" and d.get_attribute("aria-modal") == "true" and pg.inner_text("#" + d.get_attribute("aria-labelledby")) == "Remove goal" and "Remove this goal?" in pg.inner_text("#" + d.get_attribute("aria-describedby")))
        check("P1 dialog takes focus (on Cancel)", pg.evaluate("document.activeElement.dataset.dlg") == "cancel")
        seen = set()
        for _ in range(5):
            pg.keyboard.press("Tab"); seen.add(pg.evaluate("document.activeElement.closest('#dialog')?document.activeElement.dataset.dlg:'OUTSIDE'"))
        pg.keyboard.press("Shift+Tab"); seen.add(pg.evaluate("document.activeElement.closest('#dialog')?document.activeElement.dataset.dlg:'OUTSIDE'"))
        check("P1 Tab stays inside the dialog", seen == {"ok", "cancel"}, str(seen))
        pg.keyboard.press("Escape")
        check("P1 Escape cancels: dialog closed, goal kept", d.is_hidden() and len(get(pg)["goals"]) == 1)
        check("P1 focus returns to the button that opened it", pg.evaluate("document.activeElement.dataset.goalDelete") == "g1")
        pg.click("[data-goal-delete=g1]"); pg.mouse.click(5, 5)
        check("P1 tap outside cancels", d.is_hidden() and len(get(pg)["goals"]) == 1)
        pg.click("[data-goal-delete=g1]"); pg.click("#dialog [data-dlg=cancel]")
        check("P1 delete goal: Cancel keeps it", len(get(pg)["goals"]) == 1)
        pg.click("[data-goal-delete=g1]"); pg.click("#dialog [data-dlg=ok]")
        check("P1 delete goal: confirm removes it", len(get(pg)["goals"]) == 0 and d.is_hidden())
        pg.evaluate("document.querySelector(\"details[data-key='session:s-a']\").open=true")
        pg.click("[data-session-delete=s-a]"); pg.click("#dialog [data-dlg=cancel]")
        check("P1 delete session: Cancel keeps it", len(get(pg)["sessions"]) == 3)
        pg.click("[data-session-delete=s-a]"); pg.click("#dialog [data-dlg=ok]")
        check("P1 delete session: confirm removes it", [s["id"] for s in get(pg)["sessions"]] == ["s-b", "s-c"])
        pg.click("[data-nav=skills]"); pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
        pg.click("[data-tempo-del=t1]"); pg.click("#dialog [data-dlg=cancel]")
        check("P1 delete tempo: Cancel keeps it", len(get(pg)["tempos"]) == 2)
        pg.click("[data-tempo-del=t1]"); pg.click("#dialog [data-dlg=ok]")
        check("P1 delete tempo: confirm removes it", [t["id"] for t in get(pg)["tempos"]] == ["t2"])
        # tempo delete from inside the rudiment window: dialog sits on top, Escape closes only the dialog
        pg.click("[data-nav=rudiment-ref]"); pg.click("[data-rud-open='16']"); pg.evaluate("document.querySelectorAll('#rudOverlay details').forEach(d=>d.open=true)")
        pg.click("#rudOverlay [data-tempo-del=t2]"); pg.keyboard.press("Escape")
        check("P1 Escape closes the dialog but not the rudiment window under it", d.is_hidden() and pg.is_visible("#rudOverlay") and len(get(pg)["tempos"]) == 1)
        pg.click("#rudOverlay [data-tempo-del=t2]"); pg.click("#dialog [data-dlg=ok]")
        check("P1 delete tempo inside the rudiment window", get(pg)["tempos"] == [] and pg.is_visible("#rudOverlay"))
        pg.keyboard.press("Escape")

        # C13 / D2
        pg = page_with(seed(skills={"d1": {"level": 2, "verified": True, "verifiedAt": D(1), "initials": "JO", "evidence": ""}}))
        pg.click("[data-nav=skills]"); pg.click("[data-skill=d1][data-level='3']")
        s = get(pg)["skills"]["d1"]; check("C13 moving up keeps verification", s["level"] == 3 and s["verified"])
        pg.click("[data-skill=d1][data-level='2']")
        s = get(pg)["skills"]["d1"]; check("C13 moving down clears verification with notice", s["level"] == 2 and not s["verified"] and "removed" in pg.inner_text("#notification"))
        t = pg.get_attribute("[data-skill=d1][data-level='2']", "title"); txt2 = pg.inner_text("[data-skill=d1][data-level='2']")
        check("C20/C22 level label and tooltip agree", txt2 in t, f"{txt2} / {t}")
        check("C20 progress bars named", pg.locator(".progress:not([aria-label])").count() == 0)
        # C15 note saved on keystroke
        pg.evaluate("document.querySelectorAll(\"details.skill-more\").forEach(d=>d.open=true)"); pg.fill("[data-skill-note=d2]", "72 bpm clean"); pg.reload(); pg.wait_for_timeout(100)
        check("C15 note survives reload without leaving the field", get(pg)["skills"]["d2"]["evidence"] == "72 bpm clean")
        # F6 tempo log
        pg.click("[data-nav=skills]")
        for v in ("60", "66"):
            pg.fill("[data-tempo-input='skill:d2']", v); pg.click("[data-tempo-add='skill:d2']")
        tl = [t for t in get(pg)["tempos"] if t["item"] == "skill:d2"]
        check("F6 tempos logged", [t["bpm"] for t in tl] == [60, 66])
        check("F6 sparkline shows after two entries", pg.locator(".spark").count() >= 1)
        pg.screenshot(path=str(OUT / "skills_1366.png"))

        # C14 two tabs
        ctx = b.new_context(viewport={"width": 1366, "height": 900})
        a = page_with(seed(), ctx=ctx); bb = ctx.new_page(); bb.goto(url, wait_until="domcontentloaded"); bb.wait_for_timeout(100)
        bb.check("[data-warm=pulse]"); bb.fill("#sessionFocus", "from tab B"); bb.click("[data-action=save-session]")
        a.click("[data-nav=goals]"); a.check("[data-goal-check=g1]")
        st = get(a)
        check("C14 second tab's session survives first tab's edit", any(s["focus"] == "from tab B" for s in st["sessions"]) and st["goals"][0]["done"])
        a.wait_for_timeout(150)
        check("C14 other tab refreshes on change", "from tab B" in a.inner_text("#panel-goals"))

        # C17 focus kept after a tick
        pg = page_with(seed())
        pg.focus("[data-warm=rudiments]"); pg.keyboard.press("Space"); pg.wait_for_timeout(50)
        check("C17 focus stays on the ticked box", pg.evaluate("document.activeElement.dataset.warm") == "rudiments")
        check("F1 diamond fills ticked strand", pg.locator(".warm-diamond rect.on").count() == 1 and pg.evaluate("(()=>{const d=document.createElement('i');d.style.color='var(--teal)';document.body.append(d);const t=getComputedStyle(d).color;d.remove();const r=document.querySelector('.warm-diamond rect.on');r.style.transition='none';return getComputedStyle(r).fill===t&&['rgb(63, 182, 168)','rgb(27, 116, 107)'].includes(t)})()"))
        check("Shmung number-diamond trace on page background", "data:image/svg+xml" in pg.evaluate("getComputedStyle(document.querySelector('.page'),'::before').backgroundImage"))
        check("F1 8-week practice strip", pg.locator(".week").count() == 8)
        # save
        pg.fill("#sessionWorked", "Notes"); pg.click("[data-action=save-session]")
        check("session saves and draft resets", len(get(pg)["sessions"]) == 4 and get(pg)["draft"]["checks"] == [])

        # C18 rudiments
        pg.click("[data-nav=rudiment-ref]"); pg.wait_for_timeout(100)
        pg.evaluate("window._search=document.getElementById('rudimentSearch')")
        pg.fill("#rudimentSearch", "flam"); pg.check("[data-rud-check='20']")
        check("C18 page not rebuilt by search or tick", pg.evaluate("window._search===document.getElementById('rudimentSearch')"))
        check("C18 search filters", pg.locator(".rudiment-item").count() == 9, str(pg.locator(".rudiment-item").count()))
        check("C22 'Demonstrated' wording", "Mastered" not in pg.inner_text("#panel-rudiment-ref"))
        # F5 notation
        pg.click("[data-rud-open='21']")
        check("F5 notation dialog opens", pg.is_visible("#rudOverlay .notation svg") and "21. Flam Accent" in pg.inner_text("#rudTitle"))
        check("P4 notation is inline SVG drawn in the panel's ink colour, no image", pg.locator("#rudOverlay img").count() == 0 and pg.evaluate("(()=>{const s=document.querySelector('#rudNotation svg');const ink=getComputedStyle(s.parentElement).color;return ['rgb(23, 19, 12)','rgb(42, 34, 22)'].includes(ink)&&[s,...s.querySelectorAll('*')].every(e=>getComputedStyle(e).color===ink)&&s.getBoundingClientRect().height>30})()"))
        check("P4 PAS credit line on the page and in the rudiment window", pg.inner_text("#rudCredit") == CREDIT and CREDIT in pg.inner_text("#rudOverlay"))
        pg.wait_for_timeout(400); pg.screenshot(path=str(OUT / "rudiment_21.png"))
        pg.click("#rudOverlay [data-rud-step='1']"); check("F5 next rudiment", "22." in pg.inner_text("#rudTitle"))
        pg.keyboard.press("Escape"); check("F5 Escape closes", pg.is_hidden("#rudOverlay"))
        pg.fill("#rudimentSearch", ""); pg.click("[data-rud-open='1']"); shown = []
        for n in range(1, 41):
            shown.append(pg.locator("#rudNotation svg").count() == 1 and pg.inner_text("#rudTitle").startswith(f"{n}. "))
            if n < 40: pg.click("#rudOverlay [data-rud-step='1']")
        check("P4 all 40 rudiments show notation", all(shown) and len(shown) == 40 and not errors, str([i + 1 for i, s in enumerate(shown) if not s]))
        if not STUB:
            names = pg.evaluate("[window.Rudiments.list.length,...window.Rudiments.list.map(r=>r.n+'. '+r.name)]")
            pg.keyboard.press("Escape"); app = pg.evaluate("[...document.querySelectorAll('[data-rud-open]')].map(b=>b.getAttribute('aria-label').replace('Open notation: ',''))")
            check("P4 notation.js list matches the app's 40 names", names[0] == 40 and names[1:] == app, str([(a, c) for a, c in zip(names[1:], app) if a != c][:3]))
        pg.keyboard.press("Escape")

        # F7 metronome
        pg.click("[data-nav=today]"); pg.click(".metro > summary")
        check("F7 3+3+2 grid has 8 cells, 3 accents", pg.locator(".metro-grid i").count() == 8 and pg.locator(".metro-grid i.acc").count() == 3)
        pg.select_option("#metroPattern", "772")
        check("F7 7+7+2 grid has 16 cells", pg.locator(".metro-grid i").count() == 16)
        pg.click("#metroToggle"); pg.wait_for_timeout(700)
        check("F7 metronome runs", pg.get_attribute("#metroToggle", "aria-pressed") == "true" and not errors, ";".join(errors))
        pg.click("[data-nav=goals]")
        check("F7 floating Stop shows on other pages while playing", pg.is_visible("#metroFloat"))
        pg.click("#metroFloat button"); pg.click("[data-nav=today]")
        check("F7 floating Stop stops it", pg.get_attribute("#metroToggle", "aria-pressed") == "false")
        pg.fill("#metroBpm", ""); pg.type("#metroBpm", "120"); pg.dispatch_event("#metroBpm", "change")
        check("F7 typed tempo 120 stays 120", pg.input_value("#metroBpm") == "120" and "120" in pg.inner_text("#metroSummary"))
        check("F7 bar downbeat marked", pg.locator(".metro-grid i.bar").count() == 1)
        # back-dating doesn't trigger the stale-draft banner
        pg.fill("#sessionFocus", "back-dated work"); pg.fill("#sessionDate", D(1)); pg.dispatch_event("#sessionDate", "change")
        check("C12 back-dating a draft shows no banner", pg.locator(".draft-banner").count() == 0)
        pg.evaluate("document.dispatchEvent(new Event('visibilitychange'))")
        check("C12 back-dated draft keeps its date", get(pg)["draft"]["date"] == D(1))
        pg.click("[data-action=save-session]")
        check("back-dated session saved under its date", any(x["date"] == D(1) and x["focus"] == "back-dated work" for x in get(pg)["sessions"]))
        check("toast sits above overlays", pg.evaluate("+getComputedStyle(document.querySelector('.toast')).zIndex") > 50)
        pg.screenshot(path=str(OUT / "today_1366.png"), full_page=True)

        # F2 report
        pg.click("[data-go=report]")
        rt = pg.inner_text("#panel-report")
        check("F2 report range starts at earliest session or tempo", pg.input_value("#reportFrom") <= D(30))
        check("F2 report has every section", all(k in rt for k in ["Technique skills", "8-lesson pathway", "Rudiments demonstrated", "Tempo log", "Practice journal"]))
        # P3 print: top-level page prints; Copy report as text is always there
        pg.click("[data-action=print]")
        check("P3 top-level page calls window.print and shows no notice", pg.evaluate("window._prints") == 1 and pg.is_hidden("#dialog"))
        pg.evaluate("void(navigator.clipboard.writeText=()=>Promise.reject(new Error('blocked')))"); pg.click("#panel-report [data-action=copy-report]")
        rep = pg.input_value("#copyBox")
        check("P3 Copy report as text carries every section and the journal", all(k in rep for k in ["Percussion technique evidence", "TECHNIQUE SKILLS", "8-LESSON PATHWAY", "RUDIMENTS DEMONSTRATED (2 OF 40)", "1. Single Stroke Roll", "20. Flam", "TEMPO LOG", "GOALS", "PRACTICE JOURNAL", "332 rotations", "Do: Clean at 80", "Write: Try 556", "back-dated work"]) and "<" not in rep, rep[:200])
        pg.click("#dialog [data-dlg=close]")
        pg.emulate_media(media="print"); pg.screenshot(path=str(OUT / "report_print.png"), full_page=True)
        check("C19 print hides topline and controls", pg.is_hidden(".report-controls") and pg.is_hidden(".topline"))
        pg.emulate_media(media="screen")
        pg.click("[data-nav=goals]"); pg.emulate_media(media="print")
        check("C19 print hides the add-goal form", pg.is_hidden("#goalForm"))
        pg.emulate_media(media="screen")

        # Phone
        for w in (390, 360):
            pg = page_with(seed(), w=w, h=844)
            bad = []
            for tabname in ("today", "skills", "pathway", "goals", "rudiment-ref"):
                pg.click(f"[data-nav='{tabname}']"); pg.wait_for_timeout(80)
                sw = pg.evaluate("document.documentElement.scrollWidth")
                if sw > w: bad.append(f"{tabname} {sw}px")
                pg.screenshot(path=str(OUT / f"{tabname}_{w}.png"), full_page=(tabname != "rudiment-ref"))
            check(f"C8 no sideways scroll at {w}px", not bad, str(bad))
            pos = pg.evaluate("getComputedStyle(document.querySelector('.nav')).position")
            check(f"C24 bottom tab bar fixed at {w}px", pos == "fixed")
            pg.click("[data-nav=goals]")
            small_goals = pg.evaluate("""()=>[...document.querySelectorAll('.goal-tick,.history-item summary,.btn')].filter(e=>{const r=e.getBoundingClientRect();return r.height&&r.height<44}).length""")
            check(f"C25 goals page targets 44px ({w}px)", small_goals == 0, str(small_goals))
            pg.click("[data-nav=rudiment-ref]")
            small = pg.evaluate("""()=>{const out=[];for(const el of document.querySelectorAll('button,label,summary,input,select,[data-rud-open]')){const r=el.getBoundingClientRect();if(!r.width||!r.height)continue;if(el.type==='range'||el.closest('.hide')||el.closest('.metro-grid'))continue;if(el.matches('input[type=checkbox]')&&el.closest('label'))continue;if(el.tagName==='LABEL'&&!el.querySelector('input'))continue;if(r.height<44)out.push((el.className||el.tagName)+':'+Math.round(r.height))}return out}""")
            check(f"C25 tap targets at least 44px on rudiments page ({w}px)", not small, str(small[:8]))
            tiny = pg.evaluate("""()=>{let n=0;for(const el of document.querySelectorAll('body *')){if(!el.childNodes.length||![...el.childNodes].some(c=>c.nodeType===3&&c.textContent.trim()))continue;const r=el.getBoundingClientRect();if(!r.width)continue;if(parseFloat(getComputedStyle(el).fontSize)<12)n++}return n}""")
            check(f"C25 no visible text under 12px ({w}px)", tiny == 0, str(tiny))
        pg.click("[data-nav=rudiment-ref]"); wide = []
        for n in (15, 26, 40):
            pg.click(f"[data-rud-open='{n}']"); pg.wait_for_timeout(60)
            m = pg.evaluate("(()=>{const s=document.querySelector('#rudNotation svg').getBoundingClientRect(),b=document.querySelector('#rudNotation').getBoundingClientRect();return [document.documentElement.scrollWidth,b.right,s.width,s.height]})()")
            if m[0] > 360 or m[1] > 360 or m[2] < 200 or m[3] < 30: wide.append((n, m))
            if n == 15: pg.screenshot(path=str(OUT / "rudiment_15_360.png"))
            pg.keyboard.press("Escape")
        check("P4 notation fits a 360px phone (long rudiments 15, 26, 40)", not wide, str(wide))

        # P2 export: no window.claude -> plain download link, and Copy backup always offered
        ctx = b.new_context(viewport={"width": 1366, "height": 900}, accept_downloads=True); ctx.grant_permissions(["clipboard-read", "clipboard-write"])
        pg = page_with(seed(), ctx=ctx); pg.click("[data-nav=goals]")
        check("P2 window.claude is absent in this run", pg.evaluate("typeof window.claude") == "undefined")
        with pg.expect_download() as dl: pg.click("#panel-goals [data-action=export]")
        saved = json.loads(pathlib.Path(dl.value.path()).read_text())
        check("P2 export without window.claude downloads a JSON file", re.fullmatch(r"[\w-]*Percussion_Progress_\d{4}-\d\d-\d\d\.json", dl.value.suggested_filename) and len(saved["sessions"]) == 3 and saved["version"] == 1, dl.value.suggested_filename)
        check("P2 export dialog reports the download and offers Copy backup", "Download started" in pg.inner_text("#exportStatus") and pg.is_visible("#dialog [data-action=copy-backup]"))
        pg.click("#dialog [data-action=copy-backup]"); pg.wait_for_timeout(150)
        clip = json.loads(pg.evaluate("navigator.clipboard.readText()"))
        check("P2 Copy backup (in the export dialog) puts the JSON on the clipboard", len(clip["sessions"]) == 3 and "exportedAt" in clip and "copied" in pg.inner_text("#notification"))
        pg.click("#dialog [data-dlg=close]"); pg.evaluate("navigator.clipboard.writeText('')")
        pg.click("#panel-goals [data-action=copy-backup]"); pg.wait_for_timeout(150)
        backup_text = pg.evaluate("navigator.clipboard.readText()")
        check("P2 Copy backup button on the Goals page", json.loads(backup_text)["goals"][0]["id"] == "g1" and pg.is_hidden("#dialog"))
        with pg.expect_download() as dl: pg.click(".topline [data-action=export]")
        check("P2 topline Export progress downloads too", dl.value.suggested_filename.endswith(".json")); pg.keyboard.press("Escape")
        # clipboard refused, or missing altogether -> read-only box with the JSON selected
        for label, js in (("refused", "void(navigator.clipboard.writeText=()=>Promise.reject(new Error('blocked')))"), ("missing", "Object.defineProperty(navigator,'clipboard',{value:undefined,configurable:true})")):
            pg.evaluate(js); pg.click("#panel-goals [data-action=copy-backup]"); pg.wait_for_timeout(100)
            box = pg.evaluate("(()=>{const t=document.querySelector('#copyBox');return t&&{ro:t.readOnly,v:t.value,a:t.selectionStart,b:t.selectionEnd,f:document.activeElement===t}})()")
            check(f"P2 clipboard {label}: read-only box with the whole backup selected", box and box["ro"] and box["f"] and box["a"] == 0 and box["b"] == len(box["v"]) and len(json.loads(box["v"])["sessions"]) == 3, str(box)[:120])
            pg.click("#dialog [data-dlg=close]")
        # host downloads helper: window.claude.use("downloads") -> save({filename,data}); nothing else on window.claude is read
        HOST = "window._keys=[];window._saved=null;window._dl=0;window.claude=new Proxy({use:async n=>MODE==='null'?null:{save:async o=>{if(MODE==='reject')throw new Error('user cancelled');window._saved=o}}},{get(t,k){window._keys.push(String(k));return t[k]}});HTMLAnchorElement.prototype.click=function(){window._dl++}"
        for mode in ("ok", "reject", "null"):
            ctx = b.new_context(viewport={"width": 1366, "height": 900}); ctx.add_init_script("const MODE='%s';%s" % (mode, HOST))
            pg = page_with(seed(), ctx=ctx); pg.click(".topline [data-action=export]"); pg.wait_for_timeout(200)
            r = pg.evaluate("({keys:window._keys,saved:window._saved,dl:window._dl})"); status = pg.inner_text("#exportStatus")
            if mode == "ok":
                check("P2 host downloads: save({filename,data}) called with the JSON string, no link download", r["saved"] and r["saved"]["filename"].endswith(".json") and isinstance(r["saved"]["data"], str) and len(json.loads(r["saved"]["data"])["sessions"]) == 3 and r["dl"] == 0 and "saved as" in status, str(r)[:150])
                check("P2 only window.claude.use is read", set(r["keys"]) == {"use"}, str(r["keys"]))
            if mode == "reject":
                check("P2 host save rejected: handled, says so, Copy backup offered", "not saved" in status and pg.is_visible("#dialog [data-action=copy-backup]") and r["dl"] == 0 and not errors, status)
            if mode == "null":
                check("P2 host has no downloads helper (null): falls back to the download link", r["dl"] == 1 and "Download started" in status, str(r)[:150])

        # P5 student code: neutral by default, old data unchanged, code shown where the hard-coded initials were
        check("P5 no hard-coded student initials in index.html", not re.search(r"(?<![\w-])OC(?![\w-])", html) and "<title>Percussion Lab</title>" in html)
        ctx = b.new_context(viewport={"width": 1366, "height": 900}, accept_downloads=True)
        old = seed(skills={"d1": {"level": 2, "verified": True, "verifiedAt": D(1), "initials": "JO", "evidence": "clean"}}, tempos=[{"id": "t1", "item": "rud:16", "bpm": 90, "date": D(1)}])
        pg = page_with(old, ctx=ctx); st = get(pg)
        check("P5 old data (no studentCode) loads with nothing lost", "studentCode" not in old and len(st["sessions"]) == 3 and st["skills"]["d1"]["verified"] and st["rudimentChecks"]["1"]["done"] and st["lessons"]["0"]["checks"] == [0, 1, 2] and st["tempos"][0]["bpm"] == 90 and st["goals"][0]["id"] == "g1" and not errors)
        check("P5 neutral text without a code", pg.title() == "Percussion Lab" and pg.inner_text("#brandMeta").strip().lower() == "performance development" and pg.inner_text("#panel-today .hero .eyebrow").upper().startswith("HSC 2027 · " + datetime.date.today().strftime("%-d").upper()))
        pg.click("[data-go=report]"); check("P5 neutral report title without a code", pg.inner_text(".report-title h2") == "Percussion technique evidence")
        pg.click("[data-nav=goals]")
        with pg.expect_download() as dl: pg.click("#panel-goals [data-action=export]")
        check("P5 neutral backup file name without a code", re.fullmatch(r"Percussion_Progress_\d{4}-\d\d-\d\d\.json", dl.value.suggested_filename), dl.value.suggested_filename); pg.keyboard.press("Escape")
        pg.focus("#studentCode"); pg.keyboard.type("Q7")
        check("P5 student code saved as typed, focus kept, title and brand update at once", get(pg)["studentCode"] == "Q7" and pg.evaluate("document.activeElement.id") == "studentCode" and pg.title() == "Q7 · Percussion Lab" and "Q7 / performance development" in pg.inner_text("#brandMeta").replace("\n", " ").lower().replace("q7", "Q7"))
        pg.reload(); pg.wait_for_timeout(100); st2 = get(pg)
        check("P5 code survives reload; other data untouched", pg.title() == "Q7 · Percussion Lab" and "Q7" in pg.inner_text("#panel-today .hero .eyebrow") and st2["sessions"] == st["sessions"] and st2["skills"] == st["skills"] and st2["version"] == 1)
        pg.click("[data-go=report]"); check("P5 report shows the code", pg.inner_text(".report-title h2") == "Q7: percussion technique evidence")
        with pg.expect_download() as dl: pg.click(".topline [data-action=export]")
        exported = json.loads(pathlib.Path(dl.value.path()).read_text())
        check("P5 backup file name and contents carry the code", dl.value.suggested_filename.startswith("Q7_Percussion_Progress_") and exported["studentCode"] == "Q7", dl.value.suggested_filename); pg.keyboard.press("Escape")
        pg.click("[data-nav=goals]"); pg.fill("#studentCode", "<b>A/B"); pg.click("[data-go=report]")
        check("P5 odd characters are shown as text, kept out of file names", pg.inner_text(".report-title h2") == "<b>A/B: percussion technique evidence" and pg.locator(".report-title h2 b").count() == 0)
        with pg.expect_download() as dl: pg.click(".topline [data-action=export]")
        check("P5 file name stays safe", dl.value.suggested_filename.startswith("bAB_Percussion_Progress_"), dl.value.suggested_filename); pg.keyboard.press("Escape")
        pg.click("[data-nav=goals]"); pg.click("[data-action=import]"); pg.fill("#importText", json.dumps({**seed(), "studentCode": 7})); pg.click("[data-action=import-paste]")
        check("P5 import rejects a non-text student code", "Not a valid" in pg.inner_text("#notification")); pg.keyboard.press("Escape")
        pg.click("[data-action=import]"); pg.fill("#importText", json.dumps(exported)); pg.click("[data-action=import-paste]"); pg.click("#dialog [data-dlg=ok]"); pg.wait_for_timeout(150)
        check("P5 importing a backup with a code restores it", get(pg)["studentCode"] == "Q7" and pg.title().startswith("Q7"))
        pg.click("[data-nav=goals]"); pg.click("[data-action=import]"); pg.fill("#importText", json.dumps(old)); pg.click("[data-action=import-paste]"); pg.click("#dialog [data-dlg=ok]"); pg.wait_for_timeout(150)
        check("P5 importing an old backup (no code) works and goes neutral", get(pg)["studentCode"] == "" and pg.title() == "Percussion Lab" and len(get(pg)["sessions"]) == 3)

        # P4: notation.js missing -> short notice, everything else still works
        ctx = b.new_context(viewport={"width": 1366, "height": 900}); ctx.route("**/notation.js", lambda r: r.abort())
        pg = page_with(seed(), ctx=ctx); pg.click("[data-nav=rudiment-ref]"); pg.click("[data-rud-open='7']")
        check("P4 notation.js missing: notice instead of notation, no error", pg.evaluate("typeof window.Rudiments") == "undefined" and pg.is_visible("#rudNotationMissing") and pg.locator("#rudNotation").count() == 0 and not errors)
        pg.check("#rudOverlay [data-rud-check='7']"); pg.fill("#rudOverlay [data-tempo-input='rud:7']", "88"); pg.click("#rudOverlay [data-tempo-add='rud:7']")
        st = get(pg); check("P4 notation.js missing: tick and tempo log still work", st["rudimentChecks"]["7"]["done"] and st["tempos"][-1]["bpm"] == 88)
        # P4: a broken notation.js (svg throws / returns junk) is contained too
        ctx = b.new_context(viewport={"width": 1366, "height": 900}); ctx.route("**/notation.js", lambda r: r.fulfill(content_type="text/javascript", body="window.Rudiments={list:null,svg(n){if(n===2)return 42;throw new Error('boom')}}"))
        pg = page_with(seed(), ctx=ctx); pg.click("[data-nav=rudiment-ref]"); pg.click("[data-rud-open='1']"); one = pg.is_visible("#rudNotationMissing"); pg.click("#rudOverlay [data-rud-step='1']")
        check("P4 broken notation.js: notice, no error", one and pg.is_visible("#rudNotationMissing") and not errors, ";".join(errors))
        # P4: third-party poster gone from the app, the docs and the build
        # N1: the credit names the reference chart the notation follows; nothing else from it (no image, no VIC_ names).
        texts = {n: (ROOT / n).read_text(encoding="utf-8").replace("as shown on the Vic Firth Rudiments poster", "") for n in ("index.html", "README.md", "scripts/build_single_file.py")}
        hits = [f"{n}: {m.group(0)}" for n, s in texts.items() for m in re.finditer(r"(?i)vic[ _-]?firth|VIC_|poster|\.jpe?g", s)]
        check("P4 no Vic Firth / poster mention in index.html, README or build script beyond the notation credit", not hits, str(hits[:5]))
        check("P4 poster image file removed", not list(ROOT.glob("assets/*")) and not list(ROOT.glob("**/*.jpg")))
        if (ROOT / "notation.js").exists():
            out = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_single_file.py")], capture_output=True, text=True)
            ctx = b.new_context(viewport={"width": 1366, "height": 900}); ctx.route("**/notation.js", lambda r: r.abort())
            pg = ctx.new_page(); pg.on("pageerror", lambda e: errors.append(str(e))); pg.goto(url.replace("index.html", "dist/Percussion_Lab.html")); pg.click("[data-nav=rudiment-ref]"); pg.click("[data-rud-open='21']")
            check("P4 one-file build has the notation built in", out.returncode == 0 and pg.is_visible("#rudNotation svg") and not errors, out.stdout + out.stderr)
            one = (ROOT / "dist" / "Percussion_Lab.html").read_text(encoding="utf-8")
            ctx2 = b.new_context(viewport={"width": 1366, "height": 900}); got = []; ctx2.on("request", lambda r: got.append(r.url))
            ctx2.route("**/fonts/**", lambda r: r.abort()); pg2 = ctx2.new_page(); pg2.goto(url.replace("index.html", "dist/Percussion_Lab.html")); pg2.evaluate("document.fonts.ready"); pg2.wait_for_timeout(200)
            ok = pg2.evaluate("""['400 16px "G Poiret"','400 16px "G Outfit"','700 16px "G Outfit"'].every(x=>document.fonts.check(x))&&[...document.fonts].filter(f=>f.status==='loaded').length>=2""")
            check("V one-file build embeds the three fonts (base64), no font requests", one.count("data:font/ttf;base64,") == 3 and "url(fonts/" not in one and ok and not [u for u in got if "/fonts/" in u], str([u for u in got if "/fonts/" in u]))
            ctx2.close()
        else: print("SKIP one-file build check (no notation.js yet)")

        # P3 + spec standing rule: full capacity inside a sandboxed iframe (as in the artifact viewer)
        import re as _re
        html_blank = _re.sub(r"const PAGES_URL='[^']*';", "const PAGES_URL='';", html)
        html_pages = _re.sub(r"const PAGES_URL='[^']*';", "const PAGES_URL='https://example.org/percussion-lab/';", html); assert html_pages != html_blank
        for with_url in (False, True):
            ctx = b.new_context(viewport={"width": 1366, "height": 900})
            body = html_pages if with_url else html_blank
            ctx.route("**/index.html", (lambda b_: (lambda r: r.fulfill(body=b_, content_type="text/html")))(body))
            # The wrapper page is on another origin (localhost vs 127.0.0.1), like the viewer: the frame gets no clipboard, no modals, no print, no downloads.
            ctx.add_init_script(NO_NATIVE)
            pg = ctx.new_page(); pg.on("pageerror", lambda e: errors.append(str(e))); pg.goto(url.replace("127.0.0.1", "localhost").replace("index.html", "__frame.html"))
            fr = pg.frames[1]; fr.wait_for_selector("#panel-today .hero")
            fr.evaluate("([k,v])=>{localStorage.setItem(k,v);location.reload()}", [KEY, json.dumps(seed())]); pg.wait_for_timeout(300); fr.wait_for_selector("#panel-today .hero")
            fget = lambda: fr.evaluate(f"JSON.parse(localStorage.getItem('{KEY}'))")
            if not with_url:
                check("framed: saved progress loads in a sandboxed iframe", fr.evaluate("window.self!==window.top") and len(fget()["sessions"]) == 3 and "Latest" in fr.inner_text("#panel-today"))
                fr.click("[data-nav=goals]"); fr.click("[data-goal-delete=g1]"); fr.click("#dialog [data-dlg=ok]")
                check("framed: delete with in-page confirm works", fget()["goals"] == [])
                fr.click("#panel-goals [data-action=copy-backup]"); fr.wait_for_selector("#copyBox")
                check("framed: Copy backup falls back to the selectable box when the clipboard is blocked", len(json.loads(fr.input_value("#copyBox"))["sessions"]) == 3)
                fr.click("#dialog [data-dlg=close]")
                fr.click("[data-action=import]"); fr.fill("#importText", json.dumps(seed(sessions=[]))); fr.click("[data-action=import-paste]"); fr.click("#dialog [data-dlg=ok]"); fr.wait_for_timeout(150)
                check("framed: paste-import works", fget()["sessions"] == [] and len(fget()["goals"]) == 1)
            fr.click("[data-go=report]"); fr.click("[data-action=print]")
            notice = fr.inner_text("#dialog")
            if not with_url:
                check("P3 framed: print shows the 'website copy' notice instead of printing", "Printing works from the website copy" in notice and fr.evaluate("window._prints") == 0 and fr.is_visible("#dialog [data-action=copy-report]"), notice[:120])
                check("P3 framed: placeholder shown while PAGES_URL is empty", fr.locator("a#pagesLink").count() == 0 and fr.is_visible("#pagesLink"))
                pg.screenshot(path=str(OUT / "print_notice_framed.png"))
                fr.click("#dialog [data-action=copy-report]"); fr.wait_for_selector("#copyBox")
                check("P3 framed: Copy report as text gives the report", "PRACTICE JOURNAL" in fr.input_value("#copyBox"))
            else:
                check("P3 framed: notice links to PAGES_URL once it is set", fr.get_attribute("a#pagesLink", "href") == "https://example.org/percussion-lab/" and fr.get_attribute("a#pagesLink", "target") == "_blank")

        # P2 import by pasting
        pg = page_with(None); pg.click("[data-nav=goals]"); pg.click("[data-action=import]")
        check("P2 import dialog offers a file and a paste box", pg.is_visible("#dialog [data-action=import-file]") and pg.is_visible("#importText"))
        with pg.expect_file_chooser(): pg.click("#dialog [data-action=import-file]")
        check("P2 'Choose a backup file' opens the file picker", pg.is_hidden("#dialog"))
        pg.click("[data-action=import]"); pg.click("[data-action=import-paste]")
        check("P2 empty paste: asks for the text", "Paste the backup text" in pg.inner_text("#notification") and pg.is_visible("#importText"))
        pg.fill("#importText", backup_text[:200]); pg.click("[data-action=import-paste]")
        check("P2 cut-off paste rejected, dialog stays", "not a complete backup" in pg.inner_text("#notification") and pg.is_visible("#importText") and not (get(pg) or {}).get("sessions"))
        pg.fill("#importText", '{"version":2}'); pg.click("[data-action=import-paste]")
        check("P2 wrong-shape paste rejected", "Not a valid" in pg.inner_text("#notification") and not (get(pg) or {}).get("sessions"))
        pg.fill("#importText", backup_text); pg.click("[data-action=import-paste]"); pg.click("#dialog [data-dlg=cancel]")
        check("P2 paste-import: Cancel changes nothing and keeps the pasted text", not (get(pg) or {}).get("sessions") and pg.input_value("#importText") == backup_text)
        pg.click("[data-action=import-paste]"); pg.click("#dialog [data-dlg=ok]"); pg.wait_for_timeout(200)
        st = get(pg)
        check("P2 paste-import restores a copied backup (round trip)", len(st["sessions"]) == 3 and st["rudimentChecks"]["1"]["done"] and "exportedAt" not in st and "Imported: 3 sessions" in pg.inner_text("#notification"))

        # Import from a file
        # Spec V (27 Nov 2026): family style. Garden black / ivory / gold with The Guitar Lab; teal signature; Poiret One + Outfit.
        THEME_KEY = "percussion-lab-theme"
        LUM = "const lum=c=>{const v=c.match(/[\\d.]+/g).slice(0,3).map(x=>{x/=255;return x<=.03928?x/12.92:Math.pow((x+.055)/1.055,2.4)});return .2126*v[0]+.7152*v[1]+.0722*v[2]};const ratio=(a,b)=>{const x=lum(a),y=lum(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)};"
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        check("V2 lime retired: no #b3ef66 in index.html or notation.js", "b3ef66" not in html.lower() and "b3ef66" not in (ROOT / "notation.js").read_text(encoding="utf-8").lower())
        check("V4 no monospace font-family left in index.html", not re.search(r"(?i)monospace|consolas|sfmono|menlo", html))
        check("V5 one style layer: tokens declared once, no .card::before stripe, no nav dots", len(re.findall(r"--bg:#0b0906", html)) == 1 and ".card::before" not in html and ".card:before" not in html and "nav-dot" not in html)
        for scheme in ("dark", "light"):
            ctx = b.new_context(viewport={"width": 1366, "height": 900}, color_scheme=scheme)
            pg = page_with(seed(), ctx=ctx); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(200)
            cs = pg.evaluate("getComputedStyle(document.documentElement).colorScheme")
            bg = pg.evaluate("getComputedStyle(document.body).backgroundColor")
            check(f"V1 Auto follows the device ({scheme}): Garden background", bg == ("rgb(11, 9, 6)" if scheme == "dark" else "rgb(247, 241, 227)") and pg.locator("[data-theme-set=auto][aria-pressed=true]").count() == 1, f"{cs} {bg}")
            fam = pg.evaluate("""()=>{const f=s=>getComputedStyle(document.querySelector(s)).fontFamily;return {brand:f('.brand-title'),h1:f('#panel-today .hero h1'),h2:f('.section-title h2'),body:f('body'),
                mono:[...document.querySelectorAll('body, body *')].filter(e=>/mono|consolas|menlo|courier/i.test(getComputedStyle(e).fontFamily)).length,
                loaded:['400 16px "G Poiret"','400 16px "G Outfit"','700 16px "G Outfit"'].map(x=>document.fonts.check(x))}}""")
            check(f"V3 Poiret One on brand and headings, Outfit on body, fonts loaded ({scheme})", all("G Poiret" in fam[k] for k in ("brand", "h1", "h2")) and "G Outfit" in fam["body"] and all(fam["loaded"]), str(fam))
            pg.click("[data-nav=skills]")
            mono2 = pg.evaluate("[...document.querySelectorAll('body, body *, label, .chip, .pill, .levels button')].filter(e=>/mono|consolas|menlo|courier/i.test(getComputedStyle(e).fontFamily)).length")
            check(f"V4 no monospace in computed styles of body, labels, chips, pills ({scheme})", fam["mono"] == 0 and mono2 == 0, f"{fam['mono']} {mono2}")
            check(f"V3 brand reads 'Percussion Lab / a Shmungfroi instrument' ({scheme})", pg.inner_text(".brand-title").strip() == "Percussion Lab" and pg.inner_text(".brand-sub").strip() == "a Shmungfroi instrument" and pg.is_visible("#brandMeta"))
            caps = pg.evaluate("[...document.querySelectorAll('body *')].filter(e=>getComputedStyle(e).textTransform==='uppercase').length")
            check(f"V4 no upper-cased eyebrow labels ({scheme})", caps == 0, str(caps))
            tr = pg.evaluate("(()=>{const c=getComputedStyle(document.querySelector('.page'),'::before');return [c.backgroundImage,c.backgroundSize,c.opacity,c.display]})()")
            want = "%238a6a22" if scheme == "light" else "%23c9a24a"
            check(f"V6 number-diamond trace present, recoloured for {scheme}, 600px tile", "data:image/svg+xml" in tr[0] and want in tr[0] and "b3ef66" not in tr[0] and tr[1] == "600px 600px" and 0.05 < float(tr[2]) < 0.3 and tr[3] != "none", str(tr[1:]))
            low = pg.evaluate("()=>{" + LUM + """const bgOf=e=>{for(let n=e;n;n=n.parentElement){const c=getComputedStyle(n).backgroundColor;const m=c.match(/[\\d.]+/g);if(m&&(m.length<4||+m[3]===1)&&!c.startsWith('color('))return c}return getComputedStyle(document.body).backgroundColor};
                const out=[];for(const id of ['today','skills','pathway','goals','rudiment-ref']){document.querySelector('[data-nav='+id+']').click();
                for(const el of document.querySelectorAll('.sidebar *, .page *')){if(![...el.childNodes].some(c=>c.nodeType===3&&c.textContent.trim()))continue;const r=el.getBoundingClientRect();if(!r.width||!r.height)continue;const cs=getComputedStyle(el);if(!/^rgb/.test(cs.color)||!/^rgb/.test(bgOf(el)))continue;const k=ratio(cs.color,bgOf(el));if(k<4.5)out.push(id+' '+(el.className||el.tagName)+' '+k.toFixed(2))}}return [...new Set(out)]}""")
            check(f"V1 text contrast at least 4.5:1 on every page ({scheme})", not low, str(low[:8]))
            pg.click("[data-nav=skills]")
            strands = pg.evaluate("()=>{" + LUM + "return [...new Set([...document.querySelectorAll('.skill-card .eyebrow')].map(e=>getComputedStyle(e).color))].map(c=>[c,ratio(c,getComputedStyle(document.querySelector('.skill-card')).backgroundColor)])}")
            check(f"V8 five strand colours, each readable as text ({scheme})", len(strands) == 5 and all(k >= 4.5 for _, k in strands) and (scheme == "light" or [c for c, _ in strands] == ["rgb(63, 182, 168)", "rgb(201, 162, 74)", "rgb(201, 138, 90)", "rgb(164, 147, 216)", "rgb(143, 191, 106)"]), str(strands))
            pg.click("[data-nav=rudiment-ref]"); pg.click("[data-rud-open='21']")
            nk = pg.evaluate("()=>{" + LUM + "const n=document.querySelector('#rudNotation');if(!n)return 99;const c=getComputedStyle(n);return ratio(c.color,c.backgroundColor)}")
            check(f"V notation stays legible: ink on paper at least 7:1 ({scheme})", nk >= 7, str(nk))
            pg.keyboard.press("Escape")
            ctx.close()
        ctx = b.new_context(viewport={"width": 1366, "height": 900}, color_scheme="dark")
        pg = page_with(seed(), ctx=ctx); before = get(pg)
        pg.click("[data-theme-set=light]")
        check("V7 Light: color-scheme switches, cream background, button pressed", pg.evaluate("getComputedStyle(document.documentElement).colorScheme") == "light" and pg.evaluate("getComputedStyle(document.body).backgroundColor") == "rgb(247, 241, 227)" and pg.get_attribute("[data-theme-set=light]", "aria-pressed") == "true" and pg.get_attribute("[data-theme-set=auto]", "aria-pressed") == "false")
        check("V7 choice stored under its own key, progress object untouched", pg.evaluate(f"localStorage.getItem('{THEME_KEY}')") == "light" and get(pg) == before and "theme" not in json.dumps(get(pg)).lower())
        check("V6 trace follows the chosen theme", "%238a6a22" in pg.evaluate("getComputedStyle(document.querySelector('.page'),'::before').backgroundImage"))
        pg.reload(); pg.wait_for_timeout(150)
        check("V7 Light survives reload", pg.evaluate("document.documentElement.dataset.theme") == "light" and pg.evaluate("getComputedStyle(document.documentElement).colorScheme") == "light" and pg.get_attribute("[data-theme-set=light]", "aria-pressed") == "true")
        pg.click("[data-action=export]"); pg.wait_for_timeout(150)
        check("V7 theme never enters the backup", "theme" not in json.dumps(get(pg)).lower())
        if pg.is_visible("#dialog"): pg.keyboard.press("Escape")
        pg.click("[data-theme-set=dark]")
        check("V7 Dark: color-scheme switches back", pg.evaluate("getComputedStyle(document.documentElement).colorScheme") == "dark" and pg.evaluate("getComputedStyle(document.body).backgroundColor") == "rgb(11, 9, 6)" and pg.evaluate(f"localStorage.getItem('{THEME_KEY}')") == "dark")
        pg.click("[data-theme-set=auto]")
        check("V7 Auto: key removed, device setting followed again", pg.evaluate(f"localStorage.getItem('{THEME_KEY}')") is None and pg.evaluate("document.documentElement.dataset.theme") is None and pg.evaluate("getComputedStyle(document.documentElement).colorScheme") == "light dark" and get(pg) == before)
        ctx.close()
        ctx = b.new_context(viewport={"width": 390, "height": 844}, color_scheme="light")
        pg = page_with(seed(), ctx=ctx)
        sw = pg.evaluate("[...document.querySelectorAll('[data-theme-set]')].map(e=>{const r=e.getBoundingClientRect();return [Math.round(r.width),Math.round(r.height),r.right<=innerWidth]})")
        check("V7 theme control reachable on a phone, 44px targets, no sideways scroll", all(w >= 44 and h >= 44 and inside for w, h, inside in sw) and pg.evaluate("document.documentElement.scrollWidth") <= 390, str(sw))
        pg.emulate_media(media="print")
        pr = pg.evaluate("[getComputedStyle(document.body).backgroundColor,getComputedStyle(document.body).color,getComputedStyle(document.querySelector('.page'),'::before').display]")
        check("V print still dark ink on white, trace hidden (light theme)", pr == ["rgb(255, 255, 255)", "rgb(17, 17, 17)", "none"], str(pr))
        ctx.close()
        # Spec V independent-check fixes W1-W11 (27 Nov 2026)
        ids = page_with(None).evaluate("[...new Set([...document.documentElement.innerHTML.matchAll(/\\{id:'([a-z0-9-]+)',s:'/g)].map(m=>m[1]))]")
        for scheme in ("light", "dark"):
            ctx = b.new_context(viewport={"width": 1366, "height": 900}, color_scheme=scheme)
            pg = page_with(seed(skills={ids[0]: {"level": 0, "verified": False, "evidence": ""}, ids[1]: {"level": 3, "verified": True, "evidence": ""}}), ctx=ctx)
            pg.click("[data-nav=skills]")
            st = pg.evaluate("[0,1].map(i=>{const b=document.querySelectorAll('.skill-card')[i].querySelector('.levels button[aria-pressed=true]');const c=getComputedStyle(b);return [b.dataset.level,c.backgroundColor,c.borderTopColor]})")
            check(f"W1 selected 'Not started' is an outline, not a fill ({scheme})", st[0][0] == "0" and st[0][1] == "rgba(0, 0, 0, 0)" and st[0][2] != "rgba(0, 0, 0, 0)" and st[1][0] == "3" and st[1][1] != "rgba(0, 0, 0, 0)", str(st))
            cb = pg.evaluate("""()=>{const cs=getComputedStyle(document.documentElement);const card=getComputedStyle(document.body).backgroundColor;const i=document.querySelector('.skill-card input[type=checkbox]:not(:checked)');const j=document.querySelector('.skill-card input[type=checkbox]:checked');const a=getComputedStyle(i),c=getComputedStyle(j),r=i.getBoundingClientRect();const t=document.createElement('i');t.style.color=cs.getPropertyValue('--card');document.body.append(t);const want=getComputedStyle(t).color;t.remove();return [a.appearance,a.backgroundColor,want,c.backgroundColor,getComputedStyle(j,'::after').borderRightWidth,r.width,r.height]}""")
            check(f"W3 checkbox is custom: card fill unticked, teal with tick ticked, 20px ({scheme})", cb[0] == "none" and cb[1] == cb[2] and cb[3] != cb[1] and cb[4] != "0px" and cb[5] >= 20 and cb[6] >= 20, str(cb))
            pg.click("[data-nav=pathway]")
            ln = pg.evaluate("(()=>{const c=getComputedStyle(document.querySelector('.lesson-number'));return [c.fontFamily,c.fontVariantNumeric,c.fontWeight]})()")
            check(f"W2 lesson numbers in Outfit, tabular, regular ({scheme})", "Outfit" in ln[0] and "Poiret" not in ln[0] and "tabular" in ln[1] and ln[2] == "400", str(ln))
            pg.click("[data-nav=today]")
            h1 = pg.evaluate("getComputedStyle(document.querySelector('#panel-today h1')).color")
            check(f"W5 h1 colour ({scheme})", h1 == ("rgb(95, 71, 8)" if scheme == "light" else "rgb(240, 212, 138)"), h1)
            op = pg.evaluate("getComputedStyle(document.querySelector('.page'),'::before').opacity"); bp = pg.evaluate("getComputedStyle(document.querySelector('.page'),'::before').backgroundPosition")
            check(f"W4 trace opacity ({scheme}, desktop)", op == ("0.15" if scheme == "light" else "0.17"), op)
            check(f"W8 trace keeps the original Shmung placement ({scheme})", bp == "190px 115px", bp)
            pg.click("[data-nav=goals]")
            ws = pg.evaluate("getComputedStyle(document.querySelector('.history-item summary .note')).whiteSpace")
            check(f"W7 journal minutes never wrap ({scheme})", ws == "nowrap", ws)
            pg.click("[data-go=report]")
            cell = pg.evaluate("[...document.querySelectorAll('.report tbody tr')].map(r=>r.lastElementChild.innerText.trim()).filter(t=>t!=='—')")
            check(f"W9 verified without initials or date reads 'Verified' ({scheme})", "Verified" in cell and "·" not in cell and "" not in cell, str(cell))
            ctx.close()
        ctx = b.new_context(viewport={"width": 390, "height": 844}, color_scheme="light")
        pg = page_with(seed(), ctx=ctx)
        check("W4 trace opacity light, phone", pg.evaluate("getComputedStyle(document.querySelector('.page'),'::before').opacity") == "0.12")
        bt = pg.evaluate("[...document.querySelectorAll('.topline .actions .btn')].map(e=>{const r=e.getBoundingClientRect();return [Math.round(r.top),Math.round(r.right)]})")
        check("W10 phone: Export progress and Evidence report share one row, inside the screen", len(bt) == 2 and bt[0][0] == bt[1][0] and bt[1][1] <= 390, str(bt))
        ctx.close()
        ctx = b.new_context(viewport={"width": 1366, "height": 900}, color_scheme="dark")
        pg = page_with(seed(skills={ids[1]: {"level": 3, "verified": True, "evidence": ""}}), ctx=ctx)
        pg.click("[data-nav=skills]")
        pg.emulate_media(media="print")
        pc = pg.evaluate("(()=>{const c=document.querySelector('.skill-card input[type=checkbox]:checked');const s=getComputedStyle(c);return [s.appearance,s.backgroundColor,s.borderTopColor,s.printColorAdjust||s.webkitPrintColorAdjust]})()")
        check("W3 checkbox in print: custom, dark teal fill, colours kept", pc[0] == "none" and pc[1] == "rgb(20, 87, 79)" and pc[3] == "exact", str(pc))
        ctx.close()
        pg = page_with(None)
        f = OUT / "bad.json"; f.write_text("{\"version\": 1}"); pg.set_input_files("#importFile", str(f)); pg.wait_for_timeout(200)
        check("W11 invalid-backup toast uses the new name", "Not a valid Percussion Lab backup." in pg.inner_text("#notification"), pg.inner_text("#notification"))
        check("W11 no old name in the app or build script", "Percussion Technique Lab" not in (ROOT / "index.html").read_text(encoding="utf-8") and "Technique_Lab" not in (ROOT / "scripts" / "build_single_file.py").read_text(encoding="utf-8"))
        pg = page_with(None)
        f = OUT / "import.json"; f.write_text(json.dumps(seed(tempos=[{"id": "t1", "item": "rud:16", "bpm": 90, "date": D(1)}])))
        pg.set_input_files("#importFile", str(f)); pg.click("#dialog [data-dlg=cancel]")
        check("P1 import: Cancel leaves this browser's progress alone", not (get(pg) or {}).get("sessions"))
        pg.set_input_files("#importFile", str(f)); pg.click("#dialog [data-dlg=ok]"); pg.wait_for_timeout(200)
        st = get(pg); check("import restores sessions, skills, tempos", len(st["sessions"]) == 3 and st["tempos"][0]["bpm"] == 90)
        bad = seed(); bad["tempos"] = [{"id": "x", "item": "rud:99", "bpm": 90, "date": "x"}]; f.write_text(json.dumps(bad))
        pg.set_input_files("#importFile", str(f)); pg.wait_for_timeout(200)
        check("import rejects malformed tempos", "Not a valid" in pg.inner_text("#notification"))
        stray = sorted({u for u in requests if not re.match(r"http://(127\.0\.0\.1|localhost):\d+/(index\.html|notation\.js|__frame\.html|fonts/(PoiretOne-Regular|Outfit-Regular|Outfit-Bold)\.ttf)?$", u)})
        check("P4 no poster, image or third-party requests (only index.html, notation.js and the three same-origin fonts)", not stray and any(u.endswith("/notation.js") for u in requests), str(stray[:5]))
        check("no page errors anywhere", not errors, ";".join(errors[:3]))
        b.close()
    httpd.shutdown()
    passed = sum(1 for r in results if r[1]); print(f"\n{passed}/{len(results)} passed")
    sys.exit(0 if passed == len(results) else 1)

if __name__ == "__main__":
    main()
