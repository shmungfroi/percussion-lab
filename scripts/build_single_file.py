"""Build a self-contained copy of the app with the rudiment notation and the fonts built in.

Usage:  python3 scripts/build_single_file.py
Output: dist/Percussion_Lab.html  (one file, works offline)

The repo keeps the notation drawing code in notation.js so the app code stays
small and easy to edit. Run this whenever a one-file copy is needed, for
example to send to a student or to paste into a viewer that takes one file.
"""
import base64
import pathlib
import re

root = pathlib.Path(__file__).resolve().parent.parent
html = (root / "index.html").read_text(encoding="utf-8")
notation = root / "notation.js"
ref = '<script src="notation.js"></script>'
if html.count(ref) != 1:
    raise SystemExit("Expected exactly one notation.js script tag in index.html")
if not notation.exists():
    raise SystemExit("notation.js not found next to index.html")
# Keep the HTML parser from ending the script early on text inside the JavaScript.
js = notation.read_text(encoding="utf-8").replace("</script", "<\\/script").replace("<!--", "<\\!--")
html = html.replace(ref, "<script>\n" + js + "\n</script>")
# Spec V: the three family fonts go in as base64 so the one-file copy looks right offline.
def embed(m):
    font = root / "fonts" / m.group(1)
    if not font.exists():
        raise SystemExit(f"fonts/{m.group(1)} not found")
    return "url(data:font/ttf;base64," + base64.b64encode(font.read_bytes()).decode("ascii") + ")"
html, n = re.subn(r"url\(fonts/([\w-]+\.ttf)\)", embed, html)
if n != 3:
    raise SystemExit(f"Expected 3 font files in the @font-face rules, found {n}")
out = root / "dist" / "Percussion_Lab.html"
out.parent.mkdir(exist_ok=True)
out.write_text(html, encoding="utf-8")
print(f"Wrote {out.relative_to(root)} ({out.stat().st_size / 1e3:.0f} KB)")
