# Percussion Lab

*a Shmungfroi instrument* (formerly Percussion Technique Lab)

*Drumming rudiments, subdivision and practice journal for the elite percussionist in you.*

Offline practice and technique tracker for a Music Extension percussion student (HSC 2027), Rose Bay Secondary College.
Built in ChatGPT (Nov 2026), brought into Claude and GitHub on 25 Nov 2026.

## What's here

| Path | What it is |
|---|---|
| `index.html` | The app. Open it in a browser. |
| `fonts/` | Poiret One and Outfit (SIL Open Font Licence), the same files The Guitar Lab uses. Must sit next to `index.html`; without them the app falls back to the system font. |
| `notation.js` | Draws the 40 PAS International Drum Rudiments as SVG notation (`window.Rudiments`). Must sit next to `index.html`. Without it the app still runs and says the notation is missing. |
| `scripts/build_single_file.py` | Makes a one-file copy with the notation and the three fonts built in: `python3 scripts/build_single_file.py` → `dist/Percussion_Technique_Lab.html`. |
| `CORRECTIONS.md` | Correction register: what was fixed and why. |
| `tests/run_tests.py` | Regression suite for the app (headless Chrome via Playwright). Run before every push. |
| `tests/test_notation.py`, `tests/notation_preview.html` | Checks and a preview page for the notation. |
| `tests/stub_notation.js` | Test stand-in for `notation.js` (`python3 tests/run_tests.py --stub`). Never use it as the real file. |

## Where it runs

The app is built to work fully in three places: a claude.ai artifact link, a website (GitHub Pages) and a local file. Viewers that show the app inside a sandboxed frame block the browser's own confirm boxes, printing and file downloads, so the app does not depend on them:

- Every "are you sure?" is an in-page dialog. The app never calls `alert`, `confirm` or `prompt`.
- Export tries the host's downloads helper, then a normal download link, and always offers **Copy backup**. Import takes a file or pasted text.
- Print works from a normal page. Inside a frame the app shows where printing does work (`PAGES_URL` in `index.html`, empty until the site exists) and offers **Copy report as text**.

## Where the progress is stored

The app saves to the browser it's used in (localStorage key `rbsc-oc-percussion-lab-v1`). **No student progress is stored in this repo**, and `.gitignore` blocks `*.json` so exported backups are never committed by mistake.

Moving to a new device or a new link (local file → website) starts with empty progress. To carry it over: **Goals & journal → Export JSON backup** (or **Copy backup**) on the old one, then **Import backup** on the new one.

## Rules for editing (Claude or ChatGPT)

1. Don't change the saved-data shape (`version: 1`, `skills`, `lessons`, `goals`, `sessions`, `rudimentChecks`, `draft`, plus the optional `tempos` array and optional `studentCode` string added 26 Nov 2026) without a migration, or saved progress won't load.
2. CSS must use real line breaks. The original C1 fault was ChatGPT writing the two characters `\n` into the stylesheet, which silently disabled whole blocks of styling.
3. Typography: Poiret One for display (brand, page headings), Outfit for everything else; numbers tabular. No monospace, no all-caps letter-spaced labels. Colours come from the tokens at the top of the stylesheet (Garden black, ivory, gold; teal is this app's signature); keep the stylesheet as one layer, don't stack overrides.
4. Keep the notation code in `notation.js`, out of `index.html`. Use the build script when a one-file copy is needed.
5. Log every fix in `CORRECTIONS.md`.
6. Every change goes through `mutate()` (re-reads storage first) and redraws through `rerender()` (keeps focus and scroll).
7. No `alert()`, `confirm()` or `prompt()`, no bare `window.print()`, no download that has no copy-and-paste fallback. Use `ask()` / `dialog()`, `printReport()` and `copyText()`.
8. Run `python3 tests/run_tests.py` before pushing.
9. The Light / Dark / Auto choice is stored under its own key (`percussion-lab-theme`), never inside the saved progress.

## Privacy and copyright

This repo can be **public**.

- Students appear only as codes (the optional "Student code" setting), never by name. Don't put a student's name in the code, the docs, a commit message or a test.
- No student data is in the repo. Progress lives only in each student's browser and in the backups they export.
- No third-party copyrighted material is in the repo, apart from the two open-licensed fonts (Poiret One, Outfit; SIL OFL). The 40 International Drum Rudiments are the standard list published by the Percussive Arts Society; the notation is drawn for this app by `notation.js`. Don't add scans or other publishers' charts or engraving.
- The work is non-commercial.
