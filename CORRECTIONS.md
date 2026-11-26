# Correction register — Percussion Technique Lab

Baseline: ChatGPT V2 ("3–3–2 TRACE / tonal lift"), first commit in this repo, untouched.

| # | Severity | Finding | Fix | Status |
|---|---|---|---|---|
| C1 | Critical | ChatGPT wrote literal `\n` characters (7 of them) into the CSS. Browsers read them as the letter "n", so these selectors matched nothing: `n n :root`, `n body`, `n h1, h2, h3…`, `n :root` (the whole V2 palette), plus the mobile rudiment layout and print rules. The page rendered light grey with near-invisible headings and labels. Present in V1 and V2. | Real line breaks. 0 dead rules after fix. | Fixed 25 Nov |
| C2 | Design | With C1 fixed, the Shmung Studio monospace body font would have switched on for the first time. | Middle ground, approved by Justin: sans for sentences; monospace for pills, chips, eyebrows, nav counts, rudiment numbers, level buttons, stat footers, lesson numbers, sources, date/number inputs. | Fixed 25 Nov |
| C3 | Structure | Vic Firth poster embedded as a 1.86 MB base64 string: 97% of the file, one unreadable line. | Moved to `assets/vic-firth-40-rudiments.jpg`. `scripts/build_single_file.py` rebuilds a one-file copy. Missing-image fallback message added. | Fixed 25 Nov |
| C4 | Data | Progress lives only in the browser where it was entered. A new link means empty progress. | Process: OC exports JSON from the old copy, and it's imported into the new one. | Waiting on OC's JSON |
| C5 | Minor | Import didn't validate `rudimentChecks`. | `validRudiments()`: keys 1–40, `done` boolean, optional `date` string. Older backups without it still import. | Fixed 25 Nov |
| C6 | Readability | Strand labels on skill cards used colours designed for a light theme (e.g. `#0e7b72`), nearly invisible on dark cards. Found while testing C1. | Same hues, lighter: `#5fd3c4`, `#8fb2e8`, `#f0a47e`, `#b9a0dc`, `#e0c070`. | Fixed 25 Nov |
| C7 | Regression | Independent check (Fable): print view went light-text-on-white once C1 switched the dark palette on, and C6's lighter strand colours made it worse. C2 had also wrongly made the free-text note box (`.skill-note`) monospace. | Print reset block: dark ink on white, light checkboxes, green labels. `.skill-note` back to sans. | Fixed 25 Nov |

| C8 | High (phone) | At 390 px the page was 650 px wide and scrolled sideways: the sidebar watermark escaped because `.sidebar` lost `position:relative` under 760 px. Pre-existing. | `position:relative` on `.sidebar` in the mobile query. All 5 panels now exactly screen width at 390 and 360 px. | Fixed 25 Nov |
| C9 | Medium | Remove / Delete buttons `#a44331` on dark grey, 1.68:1. Pre-existing. | `#ff9c88`, 5.07:1; hover 5.67:1. | Fixed 25 Nov |
| C10 | Low | Placeholders used the browser default grey (2.2–2.4:1); footer 4.46:1 at 11 px. Pre-existing. | Placeholders `#b1b2ad` (4.67–7.24:1 across input fills); footer `#b3b5ae` (7.08:1). | Fixed 25 Nov |
| C11 | Low | Goals panel: an unclosed wrapper put "Save, transfer and print" in the right-hand column. Plurals read "1 entries" / "1 teacher-verified skills". Pre-existing. | Goals and Journal are now the two columns; save/print section full width below. Singular forms for 1. | Fixed 25 Nov |

Tested headless (Chrome, 1366×900, 390×844 and print) and independently reviewed: no JS errors; original saved progress loads with identical counts; session save persists after reload; poster loads from assets and in the one-file build; valid, legacy and malformed imports behave correctly.

## 26 Nov 2026 pass: full audit register (C12–C29) and features F1, F2, F5, F6, F7

Decisions (Justin, 25 Nov): D1 levels are Not started / Exploring / Consistent / Applied. D2 moving a level up keeps teacher sign-off, moving it down clears it with a notice. D3 honour system, no PIN. D4 build F1, F2, F5, F6, F7 (F3, F4, F8 not built).

| # | Severity | Finding | Fix | Status |
|---|---|---|---|---|
| C12 | High | Session date never refreshed; old drafts logged on the wrong day. | On open, and when the page comes back into view, an empty draft moves to today. A draft with content shows "Unsaved draft from …: Keep draft / Clear it, start today". | Fixed |
| C13 | High | Any level click wiped teacher verification. | D2: up keeps, down clears with a notice. | Fixed |
| C14 | High | Two tabs overwrote each other. | Every change re-reads storage first (`mutate`); `storage` events refresh the other tab. | Fixed |
| C15 | Medium | Skill note lost if the page closed before leaving the field. | Saves on every keystroke. | Fixed |
| C16 | Medium | Journal in entry order. | Sorted by session date, newest first (Today and journal). | Fixed |
| C17 | Medium | Focus jumped to the top after every tick. | `rerender()` restores focus, cursor, scroll and open/closed sections. | Fixed |
| C18 | Medium | Poster rebuilt on every search keystroke and tick. | Rudiment page shell built once; only the list and summary update. | Fixed |
| C19 | Medium | Print: journal collapsed, forms printed. | Entries expand for printing; forms, metronome, tempo inputs hidden. | Fixed |
| C20 | Low | Unnamed progress bars; tooltip contradicted label; no reduced motion. | Bars named; tooltips explain the same level name; `prefers-reduced-motion` respected. | Fixed |
| C21 | Low | "(0 min)". | "—"; new drafts prefilled 25 minutes. | Fixed |
| C22 | Polish | Three level vocabularies, Mastered/Demonstrated, nav ≠ titles, OC/you. | One level set (D1); "Demonstrated"; nav labels are page titles; student addressed as "you". | Fixed |
| C23 | Polish | Hero on every page; diamond repeated 3× as decoration. | Full hero on Today only; compact headers elsewhere; page-background diamond removed; the diamond is now a working warm-up tracker (cells fill as strands are ticked). Sidebar texture kept. | Fixed |
| C24 | Polish | Phone nav half hidden; Skills page 12,871 px tall. | Fixed bottom tab bar of 5. Skill cards put target, evidence and tempo in a collapsible section on phone: Skills page now 10,079 px at 390 px. | Fixed |
| C25 | Polish | Tap targets 19–39 px; 10–11 px text. | 44 px minimum for buttons, levels, rows; 12 px type floor (0 visible elements under 12 px at 360/390 px). | Fixed |
| C26 | Polish | Poster unreadable on phone. | "View full screen" overlay (fit / actual size, pinch-zoom); inline poster hidden on phone. | Fixed |
| C27 | Polish | Warm-up detached from the log; filler chips; toast over Save; no first run. | One "Today's session" card: step 1 warm-up, step 2 record. Filler chips removed. Toast at the top on phone. "Start here" shown until the first session. | Fixed |
| C28 | Polish | No current-lesson marker; "complete"/"completed". | First unfinished lesson marked "Next up"; chips read "2/3 done" or "Complete". | Fixed |
| C29 | Polish | ISO dates. | Shown as "25 Nov 2026" everywhere (stored as ISO). | Fixed |
| F1 | Feature | Progress only shown as totals. | 8-week minutes strip, last practised, week streak; functional warm-up diamond. | Built |
| F2 | Feature | No evidence report. | "Evidence report" page with date range: skills + sign-offs, pathway, rudiments, tempo log, goals, full journal. Prints cleanly / saves as PDF. | Built |
| F5 | Feature | Notation only on the whole poster. | Tap a rudiment: its notation cropped from the poster, Demonstrated tick, tempo log, prev/next. | Built |
| F6 | Feature | No tempo record. | Tempo log per skill and rudiment, best/last, sparkline, removable history. New optional data key `tempos` (old backups still load). | Built |
| F7 | Feature | No metronome. | Web Audio metronome on Today: 30–240 bpm, subdivisions 1–7, Rhythm Diamond groupings (3+3+2 family in quavers, 5+5+6 and 7+7+2 families in semiquavers) with accented group starts. | Built |

Data shape: unchanged apart from the optional `tempos` array. Import validates it. Regression suite: `python3 tests/run_tests.py`.

### Independent check (Fable agent, 26 Nov 2026): 19 findings, all addressed

| # | Sev | Finding | Fix |
|---|---|---|---|
| IC1 | High | Typing 100–199 bpm in the metronome became 240. | Typed tempo only applies when 30–240 and the box is never rewritten mid-typing. |
| IC2 | Medium | 3+3+2 and 2+3+3 sounded the same once looping. | The bar's downbeat has its own, higher click and is marked in the grid. |
| IC3 | Medium | Back-dating a draft showed the "old draft" banner, or reset the date. | A hand-picked date is respected; future dates refused. |
| IC4 | Medium | Toasts hidden behind the rudiment/poster windows. | Toast layered above them. |
| IC5 | Medium | Report's default range skipped tempos logged before the first session. | Range starts at the earliest session or tempo; resets after import. |
| IC6 | Medium | Phone strip showed 6 weeks under "8 weeks". | All 8 weeks kept; alternate labels hidden on narrow phones. |
| IC7 | Medium | Goal ticks, section toggles and the slider under 44 px. | All 44 px; suite now checks Goals and Rudiments at 44 px. |
| IC8 | Medium | Print included the session form, empty note boxes, teacher box, orphan heading. | Hidden in print; filled notes print as text. |
| IC9 | Low | Old empty drafts showed minutes blank with a "25" placeholder. | Blank minutes on an empty draft become 25; placeholder "e.g. 25". |
| IC10 | Low | Half-typed goal or bpm wiped by any redraw. | Carried across redraws. |
| IC11 | Low | Rudiment 29 crop showed a sliver of 28. | Crop moved down 7 px (checked). |
| IC12 | Low | Focus dropped to the page after some actions; dialog had no focus loop. | Focus moved to a sensible next control; Tab stays inside open windows; closing the poster returns to the rudiment it came from. |
| IC13 | Low (pre-existing) | Unreadable saved data was silently replaced. | Copied to a backup key with a notice before anything is saved. |
| IC14 | Low | A damaged draft blanked the app. | Draft fields cleaned on load; import checks them; tempos validated on load too. |
| IC15 | Low | Tempo history closed after each log/delete in the rudiment window. | Open state restored after the window is rebuilt. |
| IC16 | Low | Metronome kept playing on other pages with no Stop. | Floating "Metronome on · Stop" control. |
| IC17 | Low | Leftover diamond watermarks; "Completed " with no date; streak capped at 8 weeks; save toast claimed success on a failed write; wording. | Watermark SVGs removed (file 117 → 111 KB); dates only shown when known; streak counts all weeks; honest failure toast; "8-lesson pathway"; phone tab "Goals". |
| IC18 | Check | The rebuild had added an unsupported claim that the poster was "reproduced with permission … for this student's private use". | My error. Removed; now reads "copyright Vic Firth / PAS; keep this copy private". |
| IC19 | Note | dist one-file copy stale. | Rebuilt before handover. |

Regression suite after fixes: 55/55 passed (headless Chrome, 1366 px, 390 px, 360 px, print media).

## 26 Nov 2026 pass: percussion register P1–P5 (spec: `tests/reports/spec-p06/SPEC.md`)

Aim: the app runs at full capacity wherever it is opened (a claude.ai artifact link, GitHub Pages, a local file), holds no third-party copyright, and names no student.

| # | Severity | Finding | Fix | Status |
|---|---|---|---|---|
| P1 | Must | Delete goal, delete journal entry, delete tempo, Import and "Clear it, start today" used the browser's `confirm()`. Sandboxed viewers block it, so those buttons silently did nothing. | One in-page dialog (`dialog()` / `ask()`, returns a Promise): labelled `alertdialog`, focus moves in and returns to the button that opened it, Tab stays inside, Escape or a tap outside cancels, sits above the rudiment window. All five `confirm()` calls replaced; no `alert`/`confirm`/`prompt` anywhere. The suite overrides all three to throw and checks Cancel and confirm for each. | Fixed 26 Nov |
| P2 | Must | Export used an `<a download>` link, which sandboxed viewers block; Import only took a file. | Export asks the host for its downloads helper (`window.claude?.use?.("downloads")`, then `save({filename, data})`; no other `window.claude` member is read; rejection and a 4-second no-answer are handled), otherwise uses the download link, then says what happened. **Copy backup** is always offered (export dialog and Goals page): clipboard from the click, or a read-only box with the JSON selected if the browser refuses. **Import backup** opens a dialog with "Choose a backup file" and a paste box; both go through the same validation and the P1 confirm. | Fixed 26 Nov |
| P3 | Must | Print / save as PDF used `window.print()`, which sandboxed viewers block. | Top-level pages still print. A framed copy (`window.self !== window.top`) shows a notice instead: "Printing works from the website copy", the `PAGES_URL` link (empty constant until the public site exists; a placeholder line shows until then), a reminder that progress must be carried across by backup, and **Copy report as text**. The report page also has Copy report as text at all times; the text version is built from the same data as the on-screen report (`reportData()`). | Fixed 26 Nov; `PAGES_URL` to be set in P6 |
| P4 | Must | The rudiment page showed a third-party publisher's poster (a 1.4 MB image) and cropped it for each rudiment's notation. Third-party copyright; it blocked a public repo and a student site. | `index.html` side: poster image deleted from the repo (`assets/` is gone), poster panel, full-screen poster window, crop maths and poster constants removed, every mention of the publisher removed from the app, README and build script. The rudiment window now shows `Rudiments.svg(n)` from `notation.js` (loaded by its own script tag) as inline SVG on a paper panel; a missing or broken `notation.js` gives a short notice and the tick and tempo log still work. Credit line added to the page and the rudiment window: "The 40 International Drum Rudiments are the standard list published by the Percussive Arts Society. Notation drawn for this app." `scripts/build_single_file.py` now builds `dist/Percussion_Technique_Lab.html` with `notation.js` inlined. Internal names `VIC_*` / `data-vic-*` renamed to `RUDIMENTS` / `data-rud-*`; saved-data key `rudimentChecks` unchanged. The notation drawings themselves are `notation.js` (separate builder). Note: the old poster is still in this repo's git history, which is why P6 starts a new public repo with clean history. | Fixed 26 Nov |
| P5 | Should | The student's initials were hard-coded in the page title, sidebar, Today heading, report title, backup file name and an import message. | New **Student code** setting on Goals & journal (under the backup buttons), stored as the optional `studentCode` string (default `''`, 12 characters at most, validated on import). With a code: page title, sidebar line, Today heading, report title (screen and text copy) and backup file name show it. Without one the text is neutral ("Percussion Technique Lab", "Percussion technique evidence", `Percussion_Progress_<date>.json`). Old data and old backups load unchanged. The storage keys keep their original names so existing progress still loads. | Fixed 26 Nov |

Data shape: unchanged apart from the optional `studentCode` string. Regression suite after P1–P5: 126/126 passed with the real `notation.js` (headless Chrome: 1366 px, 390 px, 360 px, print media, and inside a cross-origin sandboxed iframe); 125/125 with `--stub` (the stub run skips the name-match check).

Still open: P6 (new public repo with clean history, GitHub Pages, then set `PAGES_URL`). Not yet tried inside the real claude.ai artifact viewer; the suite stands in for it with a sandboxed iframe and a mock of the host's downloads helper.

## 27 Nov 2026: background trace restored

| # | Severity | Finding | Fix | Status |
|---|---|---|---|---|
| R1 | Design (Justin) | The C23 rebuild removed the page-background number diamond (the 2·3·3 / 3+3+2 trace). It is part of the Shmung design style, not template decoration. | Original `.page::before` trace restored exactly as in the ChatGPT baseline (600 px tile, 15% opacity; 470 px / 11% under 820 px; hidden in print). The working warm-up diamond on Today stays. New regression check. | Fixed |

Regression suite: 127/127; notation 15/15.

## 27 Nov 2026: family style (Spec V)

Visual layer only, so Percussion Lab reads as a sibling of The Guitar Lab. Layout, features, wording (apart from the brand and page title), saved-data shape, storage key, dialogs, export/import and print are unchanged. Spec: `tests/reports/spec-v/SPEC.md`; screenshots: `tests/reports/spec-v/shots/`.

| # | Severity | Finding | Fix | Status |
|---|---|---|---|---|
| V1 | Design | Colours were a mid-grey ChatGPT dark theme, dark only. | Garden tokens shared with The Guitar Lab (black `#0b0906`, card `#12100b`, ivory `#ece2c8`, muted `#9c927c`, rule `#2a2418`, gold `#c9a24a` / `#f0d48a`), written with the same `light-dark()` pattern, with a cream light theme (`#f7f1e3` / `#fffaf0`, ink `#2a2216`). Text contrast is checked at 4.5:1 or better on every page in both themes. | Fixed |
| V2 | Design | Lime `#b3ef66` was the accent everywhere, including the warm-up diamond and tempo sparkline drawn by JavaScript. | Teal is the app's signature (`#3fb6a8`; `#1b746b` on cream, 4.9:1 on the page and 5.3:1 on cards): progress bars, done states, selected level, main button, current section, ticked warm-up cells. Gold is for tips, numerals and small accents. Lime has 0 uses; the diamond and sparkline take their colours from the stylesheet (`rect.on`, `rect.cell`). The metronome's group-start marks stay orange because the on-screen help says "Orange tops". | Fixed |
| V3 | Design | System sans headings; heavy all-caps brand "PERCUSSION TECHNIQUE LAB". | `fonts/` Poiret One and Outfit with the Guitar Lab's `@font-face` rules ('G Poiret', 'G Outfit'). Poiret One on the brand, page headings, section headings and step / lesson numerals; Outfit elsewhere. Brand is "Percussion Lab" with "a Shmungfroi instrument" beneath; the student-code line stays. Page title is "Percussion Lab" ("Q7 · Percussion Lab" with a code). | Fixed |
| V4 | Design | Monospace on labels, chips, pills and numbers; all-caps letter-spaced eyebrows. Old rule C2 allowed monospace for numbers. | Every monospace font-family removed; numbers use Outfit with tabular figures. No `text-transform:uppercase` anywhere; small labels are sentence case at 12 to 13 px (the 12 px floor from C25 holds). README type rule updated. | Fixed |
| V5 | Design | Dashboard tells: 24% lime stripe on every card, boxy pills and chips, square nav dots, brown tip boxes, 4 to 7 px corners, and four generations of stacked overrides in the stylesheet. | Stylesheet rewritten as one layer (about 450 lines, one rule per line, tokens declared once). Stripe and nav dots removed; nav follows the Guitar Lab tabs (muted text, teal rule on the current section). Pills, chips and filter tabs are rounded with a quiet border. Tips and notices are a gold left rule on the card colour. Corners follow the Guitar Lab file: 16 px cards, 12 px buttons and rows, 10 px inputs, 6 px small parts, 999 px pills. A 4 px teal rule runs across the top as in the Guitar Lab. Every functional rule is kept: 44 px targets and 12 px floor (C25), phone tab bar (C24, C8), print (C19), focus ring, reduced motion, overlays and dialog (C26, P1, P2), notation paper panel (P4). | Fixed |
| V6 | Design (D7) | The number-diamond trace used lime and grey-green. | Same geometry, tile and position (600 px; 470 px under 820 px; hidden in print). Dark: 2s gold `#c9a24a`, 3s ivory `#ece2c8`, warm rule-toned grid, gold dashed line, 17% (12% on phones). Light: its own drawing with darker gold 2s and ink 3s at 20% (15%), so it still shows on cream. The warm-up diamond on Today uses the same family: teal filled cells, gold-ruled strand cells. | Fixed |
| V7 | Feature (small) | No light mode. | Follows the device by default. Light / Dark / Auto control in the sidebar footer (beside the brand on phones, since the footer is hidden there). Stored under its own key `percussion-lab-theme` (removed again on Auto), applied before first paint, never written into the progress object or the backup. The Guitar Lab has the `data-theme` hooks but no control yet, so this is the first one in the family. | Fixed |
| V8 | Design | Strand colours were pastel blue, peach and yellow from the old theme. | Rhythm Diamonds teal `#3fb6a8`, Subdivision & metre gold `#c9a24a`, Stick control & rudiments clay `#c98a5a`, Polyrhythm & independence violet `#a493d8`, Mallets Garden green `#8fbf6a`, as tokens (`--s-*`) with darker light-theme values so the strand names stay readable as text. | Fixed |

Notation: `notation.js` unchanged. It draws in `currentColor`; the app shows it as dark ink on a paper panel in both themes (ivory panel on dark, card colour on light; at least 7:1, checked). `test_notation.py` gained the light-background check.

One-file build: `scripts/build_single_file.py` now also embeds the three fonts as base64 `@font-face` sources (about 352 KB).

Tests changed only where they encoded the old look: lime fill selector, the notation ink colour, the page title, and P4's request list (now also allows the three same-origin `fonts/*.ttf`). New Spec V checks cover: no `#b3ef66`, no monospace (source and computed styles), Poiret on brand and headings, fonts loaded, no upper-casing, trace present and recoloured in both themes, contrast on every page in both themes, strand colours, notation legibility, the theme control (switches `color-scheme`, persists under its own key, never in the progress object or backup, 44 px on a phone), print still dark ink on white, and fonts embedded in the one-file build.

Data shape: unchanged. Regression suite: 158/158 (157/157 with `--stub`); notation 16/16.

## 27 Nov 2026: Spec V independent design check (W1 to W11)

Visual and wording fixes only; layout, saved-data shape and storage key unchanged. W6 layout: separate framework, not done.

| # | Severity | Finding | Fix | Status |
|---|---|---|---|---|
| W1 | Must | The selected level "Not started" was solid teal, identical to "Applied", so it read as an achievement. | Selected level 0 is an outline (teal border, ink text, no fill); Exploring and above keep the solid fill. Print has its own outline rule. | Fixed |
| W2 | Should | `.lesson-number` in Poiret One read "01" as "O1". | Outfit, tabular figures, regular weight, display gold (the darker light-theme gold, so it stays 4.5:1). | Fixed |
| W3 | Should | Unticked native checkboxes were grey-filled in dark mode and looked disabled. | All checkboxes use `appearance:none`: card fill, rule-family border (`--line2`), teal fill with a tick when checked, hover border, the global focus ring, 20 px (the existing size inside the 44 px rows). Both themes and print (colours forced on). | Fixed |
| W4 | Should | Light-mode page trace too loud. | Light opacity .20 to .15 (desktop) and .15 to .12 (phone). Dark unchanged. | Fixed |
| W5 | Should | Light-mode h1 (Poiret, `#7a5c12`) read thin. | New token `--gold-display`: `#5f4708` in light, `#f0d48a` in dark (unchanged). Used on h1 and the report title. | Fixed |
| W6 | n/a | Layout finding. | Separate framework, not done. | Not done |
| W7 | Nit | Journal summary minutes ("20 min") wrapped at 1366 px. | `white-space:nowrap` on that span. | Fixed |
| W8 | Should | Trace "3" numerals were cut into fragments in the 13 to 18 px gaps between cards. | Desktop `background-position` 190px 115px to 225px 390px, chosen by scoring numeral/card overlap on Today, Technique, Pathway, Goals, Rudiments and Report at 1366 (51 partial numerals down to about 11). Phones (tile 470 px) keep the old offset. | Fixed |
| W9 | Nit | Evidence report showed a lone "·" under Teacher sign-off for a skill verified without initials or date. | Shows "Verified" in that case. | Fixed |
| W10 | Should | On phones Export progress / Evidence report stacked on the right. | Top line is a column on phones; the two buttons share one row at equal width. | Fixed |
| W11 | Nit | Old name left in the invalid-backup toast and the one-file build name. | Toast reads "Not a valid Percussion Lab backup."; build output is `dist/Percussion_Lab.html` (script, README and test). No other user-visible "Percussion Technique Lab" in the app. | Fixed |

Tests: one check per item (W6 excepted) in `tests/run_tests.py`; `take_shots.py` now also shoots the Pathway page. Regression suite: 179/179 (178/178 with `--stub`); notation 16/16.
