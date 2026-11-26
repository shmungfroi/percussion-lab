# Independent check: P1–P5 (branch p06-register)

Checked 26 Nov 2026 by a checker who did not build this. Inputs used: `SPEC.md`, `index.html`, `notation.js`, `scripts/build_single_file.py`, `README.md`. BUILD_REPORT.md, NOTATION_REPORT.md and the test files were not read.

Method: the folder was served with `python3 -m http.server` and driven with Python Playwright (Chromium). An init script replaced `confirm`, `alert` and `prompt` with functions that throw and log, and a native-dialog listener was attached to every page. Every rudiment was rendered with `Rudiments.svg(n)` at 700 px and at 360 px (`maxWidth:340`) and each image was looked at. The rudiment overlay was also checked in the app (dark UI) at 360, 390 and 1280 px.

## Verdicts

| ID | Verdict | Evidence |
|---|---|---|
| P1 | **PASS** | Goal delete, session delete, tempo delete, Clear draft and Import (both paste and file) all open the in-page `#dialog` (role `alertdialog`, focus starts on Cancel). Cancel keeps the data, Esc keeps the data, and the action button applies the change (goals 2→1, sessions → `[session-2]`, tempos 2→1, draft reset to today). Tab stayed inside the dialog for 5 presses. No native confirm/alert/prompt was called (the throwing overrides were never hit, no native dialog event) in a normal page or in the framed page. A source grep finds no `confirm(`, `alert(` or `prompt(` call. |
| P2 | **PASS** | **No `window.claude`:** a plain download of `AB_Percussion_Progress_2026-11-26.json` with all counts (2 sessions, 2 skills, 3 rudiment checks with 2 done, 2 tempos, 2 goals, 1 lesson). **Mocked `claude.use("downloads")`** (a Proxy that logs every property read): reads were only `use` and `use:downloads`. `save` was called once with `{filename:"XY_Percussion_Progress_…json", data:<string>}`, the counts were complete, no link download happened, and the status read "Backup saved as …". A rejected `save` shows "The backup file was not saved." When `use()` resolves to null the app falls back to the link download. **Copy backup** puts the full JSON on the clipboard. When the clipboard refuses, a read-only `#copyBox` opens with all 1836 characters selected and focused. **Round trip:** clear storage, paste the copied JSON, confirm: identical state (no differing keys) and the toast "Imported: 2 sessions, 2 skills, 2 rudiments." Cancelling the import confirmation reopens the import box with the pasted text kept. Bad JSON gives a clear message. Importing from a file also works. |
| P3 | **PASS** | Cross-origin iframe (host 127.0.0.1, app on localhost, `sandbox="allow-scripts allow-same-origin"`): `framed()` is true, `window.print` is **not** called, and the notice "Printing works from the website copy" appears with the PAGES_URL placeholder text, Copy backup and Copy report as text. Copy report passed the full report text to `clipboard.writeText` (first line "Percussion technique evidence") and showed the toast. With no clipboard permission in the frame, the fallback box opened with all 2210 characters selected. Outside a frame, `window.print` is called once and no notice appears. |
| P4 | **PASS** (Should items below) | The only network requests were `index.html` and `notation.js`. There is no "Vic Firth" (or "poster") in index.html, notation.js, README.md, scripts or the built dist file, and no image files are tracked. The credit line appears on the Rudiment library page and in every rudiment overlay, and the wording matches the spec. If notation.js is blocked, the overlay shows `#rudNotationMissing` and there are no errors. `build_single_file.py` inlines notation.js, and the output has no `notation.js` script tag. **Musical accuracy: 0 WRONG.** Sticking, lead-hand alternation, accents, flams, drags, diddles, buzz marks and tuplets are right in all 40, and every bar adds up to its time signature. 17 rudiments are EDITION-DEPENDENT (see the table below). |
| P5 | **PASS** | The setting is saved as `studentCode` ("AB"). It shows in `document.title` ("AB · Percussion Technique Lab"), the report heading and the plain-text report ("Q7: percussion technique evidence"), the backup file name (`AB_…`, `XY_…`) and the brand line. Clearing it brings back "Percussion Technique Lab" and "Performance development". Old data without the key loads and stays unchanged in storage (no key added, same counts). The import check accepts a missing or string `studentCode`. No "OC" appears anywhere in the visible UI. |
| Console | **PASS** | All tabs and all 40 overlays were opened at 360, 390 and 1280 px: 0 page errors, 0 console errors or warnings, no horizontal page scroll, and no overlay overflows sideways. The framed run had 0 page errors. Its one console error, a Clipboard permissions-policy message, came from the checker's own `readText()` probe, not from the app. |

## Per-rudiment musical check

The reference is the standard PAS International Drum Rudiments as commonly written. The PAS chart is published as images and could not be fetched from this environment (the proxy blocked it), so these verdicts come from the checker's own knowledge of the chart and of standard rudimental notation.

| # | Rudiment | Verdict | Note |
|---|---|---|---|
| 1 | Single Stroke Roll | OK | |
| 2 | Single Stroke Four | OK | 16th-note triplet, then an accented 8th. Lead alternates. |
| 3 | Single Stroke Seven | OK | Sextuplet, then an accented quarter. Lead alternates. |
| 4 | Multiple Bounce Roll | EDITION-DEPENDENT | Buzz marks on 16ths here. Some charts put the z on 8ths or quarters. |
| 5 | Triple Stroke Roll | EDITION-DEPENDENT | Plain 16th-note triplets RRR LLL. Some charts write 8th-note triplets with a slash. |
| 6 | Double Stroke Open Roll | EDITION-DEPENDENT | Written-out 16ths RRLL. Some charts write slashed 8ths. |
| 7 | Five Stroke Roll | EDITION-DEPENDENT | Two slashed 16ths, then an accented 8th. Some charts write a slashed 8th tied to an accented 8th. Sticking is correct. |
| 8 | Six Stroke Roll | OK | R> LL RR L>, same lead each time. (Engraving: see Could C1.) |
| 9 | Seven Stroke Roll | OK | |
| 10 | Nine Stroke Roll | EDITION-DEPENDENT | The release is an accented 8th plus an 8th rest. Some charts use an accented quarter, which sounds the same. |
| 11 | Ten Stroke Roll | EDITION-DEPENDENT | Shown with the right lead only. Some charts add the left-lead bar. |
| 12 | Eleven Stroke Roll | EDITION-DEPENDENT | Release placement: here a 16th on the "and" of 2 plus an 8th rest. Some charts place it differently. Sticking is correct. |
| 13 | Thirteen Stroke Roll | OK | |
| 14 | Fifteen Stroke Roll | EDITION-DEPENDENT | The release falls on the "a" of 2. Some charts put the release on the next downbeat. |
| 15 | Seventeen Stroke Roll | EDITION-DEPENDENT | Written in 3/4 here. Some charts use 2/4 with the release on the next downbeat. |
| 16 | Single Paradiddle | OK | |
| 17 | Double Paradiddle | EDITION-DEPENDENT | 2/4 sextuplets here. Some charts use 6/8 or 3/4 sixteenths. |
| 18 | Triple Paradiddle | OK | |
| 19 | Paradiddle-Diddle | EDITION-DEPENDENT | 2/4 sextuplets with the same lead each time (correct). Some charts use 6/8. |
| 20 | Flam | OK | |
| 21 | Flam Accent | OK | |
| 22 | Flam Tap | OK | |
| 23 | Flamacue | EDITION-DEPENDENT | The accent on the 2nd note (L) is correct. Some editions also accent the final flam, and some alternate the lead. |
| 24 | Flam Paradiddle | OK | |
| 25 | Single Flammed Mill | OK | |
| 26 | Flam Paradiddle-Diddle | OK | Lead alternates (lR… / rL…). |
| 27 | Pataflafla | EDITION-DEPENDENT | No accents here. Some editions accent the first and last flam. |
| 28 | Swiss Army Triplet | OK | |
| 29 | Inverted Flam Tap | OK | |
| 30 | Flam Drag | EDITION-DEPENDENT | 6/8 here (flam 8th, two 16ths, 8th). Some charts write 2/4 with triplet subdivision. Sticking lR LL R / rL RR L is correct. |
| 31 | Drag (Ruff) | OK | |
| 32 | Single Drag Tap | OK | The accent is on the tap. |
| 33 | Double Drag Tap | OK | |
| 34 | Lesson 25 | OK | |
| 35 | Single Dragadiddle | EDITION-DEPENDENT | The first note is a slashed 16th (RR) with an accent. Some charts write it as a grace-note drag on the first note. |
| 36 | Drag Paradiddle #1 | EDITION-DEPENDENT | 6/8 here. Some charts use 2/4 sextuplets with the first R as an 8th. The rhythm is the same either way. |
| 37 | Drag Paradiddle #2 | OK | |
| 38 | Single Ratamacue | OK | |
| 39 | Double Ratamacue | EDITION-DEPENDENT | The release is an 8th plus an 8th rest. Some charts use a quarter. |
| 40 | Triple Ratamacue | OK | |

## Readability (360 px and dark UI)

The notation sits on a light card with dark ink inside the dark app, so the contrast is good. In-app sizes at 360 px (sticking font size times the SVG scale):
- Main sticking is at least 11 px for every rudiment except #15 Seventeen Stroke Roll (10.3 px).
- Grace sticking (the small italic l/r) drops to 9.3–10.4 px on #36, #26, #33, #22 and #27.
- At 390 px every main sticking letter is at least 11.3 px.
- No horizontal overflow at any width.

## New problems

**Must:** none.

**Should**
- S1. The rudiment overlay background is `rgba(14,14,17,.94)`, so the page text behind it shows through around and between the overlay cards (seen at 360 and 1280 px: the library intro, filter buttons and progress text appear behind "Tempo log" and the credit). This hurts readability in the dark UI. This CSS predates P1–P5. Fix: make the overlay background opaque.
- S2. At 360 px, #15's sticking (10.3 px) and the grace-note sticking on #36, #26 and #33 (9.3–9.8 px) fall below the 11 px target stated in notation.js. Fix: wrap these onto two systems at a smaller `maxWidth`, or raise the grace font size.
- S3. Before P6 makes the repo public: the localStorage key `rbsc-oc-percussion-lab-v1` (also named in the README) still holds the student's initials. Renaming it needs a one-time read-old/write-new migration so saved progress isn't lost.

**Could**
- C1. #8 Six Stroke Roll: the accents at the end of beat 1 and the start of beat 2 almost touch, and the two beam groups nearly meet. Add a little space between beats.
- C2. The italic serif lowercase "l" for grace sticking can be misread as "I" or "1". A sans-serif or upright small "l" would read more clearly.
- C3. Where a flam falls in the middle of a beamed group (#22, #27, #29), the grace note's flag sits under the main beam. It is readable but cluttered.
- C4. In a sandbox without `allow-downloads`, Export still says "Download started: …" even though the browser blocks the file. The dialog's "No file? … Copy backup" covers this. Wording such as "If your browser allows it, a download has started" would be more accurate.
