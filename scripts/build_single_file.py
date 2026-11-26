"""Build a self-contained copy of the app with the rudiment notation built in.

Usage:  python3 scripts/build_single_file.py
Output: dist/Percussion_Technique_Lab.html  (one file, works offline)

The repo keeps the notation drawing code in notation.js so the app code stays
small and easy to edit. Run this whenever a one-file copy is needed, for
example to send to a student or to paste into a viewer that takes one file.
"""
import pathlib

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
out = root / "dist" / "Percussion_Technique_Lab.html"
out.parent.mkdir(exist_ok=True)
out.write_text(html, encoding="utf-8")
print(f"Wrote {out.relative_to(root)} ({out.stat().st_size / 1e3:.0f} KB)")
