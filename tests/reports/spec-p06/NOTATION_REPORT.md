# Notation report: P4, the 40 PAS rudiments drawn as our own SVG

Built 26 Nov 2026. Files: `notation.js`, `tests/test_notation.py`, `tests/notation_preview.html`.
No poster, crop or third-party image was opened or traced. Every rudiment is a short text description (see the header of `notation.js`) drawn by a single renderer.

## How it is drawn (all rudiments)

- One-line percussion staff, percussion clef, time signature, start and end repeat signs. Stems up, flat beams.
- Sticking under every note in bold capitals. Grace-note sticking is in small italic lower case (`l`, `rr`) under the grace notes. The italic serif face keeps lower-case `l` from looking like a capital `I`.
- Accents (`>`) are under the notehead, between the staff and the sticking (on the notehead side, because stems are up).
- Flams: one small grace eighth note, played by the other hand. There is no acciaccatura slash: at this size the slash crossed the flag and read as an X.
- Drags: two small grace notes beamed as sixteenths, played by the other hand.
- Diddles inside roll rudiments: a sixteenth with one tremolo slash. That means two thirty-second strokes, and the sticking is written doubled (`RR`).
- Buzz: a `z` through the stem.
- Tuplets: an italic number above the beam (3 = triplet, 6 = sextuplet).
- Long rudiments wrap at a barline onto a second system. The default wrap width is 370 viewBox units, so sticking stays at least 10.5px tall in a 360px card; the tests measure this. There is no fixed size: the SVG uses `width="100%"`, `max-width` = 1.6 × its natural size, and `currentColor` throughout.
- `role="img"`, an `aria-label` and `<title>` giving the name, metre and full sticking, with accents and buzz spoken as words.

## Per rudiment

"Choice" marks the places where common editions differ.

| # | Rudiment | Metre | As written | Choice / where editions differ |
|---|---|---|---|---|
| 1 | Single Stroke Roll | 2/4 | 8 sixteenths, R L R L … | Some editions use thirty-seconds or add "open–close–open". Kept the plain pulse. |
| 2 | Single Stroke Four | 2/4 | sixteenth triplet + accented eighth per beat, R L R L> / L R L R> | Some print it as a triplet pickup into the beat, or as 4 thirty-seconds. |
| 3 | Single Stroke Seven | 2/4 | sextuplet sixteenths + accented quarter; two bars (R lead, L lead) | Some write it as thirty-second triplets into an eighth. |
| 4 | Multiple Bounce Roll | 2/4 | sixteenths with `z`, R L R L | Some write a whole/half note with `z`. Sixteenths show the hand motion. |
| 5 | Triple Stroke Roll | 2/4 | sixteenth triplets RRR LLL | Standard. |
| 6 | Double Stroke Open Roll | 2/4 | sixteenths RR LL | Some use slashed eighths. Written out for clarity. |
| 7 | Five Stroke Roll | 2/4 | 2 slashed sixteenths + accented eighth: RR LL R> / LL RR L> | Older editions use an eighth-note roll tied to an accented eighth. **Choice: explicit diddle slashes, no tie.** |
| 8 | Six Stroke Roll | 2/4 | R> LL RR L> on one beat (sixteenth grid, diddles slashed) | Also seen as eighth + two slashed sixteenths + eighth. Chose the "1 e & a" drum-line form. |
| 9 | Seven Stroke Roll | 2/4 | slashed sixteenth triplet + accented eighth: RR LL RR L> / LL RR LL R> | Also seen in straight sixteenths starting on "e". Chose the triplet form. |
| 10 | Nine Stroke Roll | 2/4 | 4 slashed sixteenths, accented eighth on beat 2, eighth rest; two bars | Older editions: a quarter-note roll tied to an eighth. |
| 11 | Ten Stroke Roll | 2/4 | 4 slashed sixteenths + accented eighths R> L> | Standard. |
| 12 | Eleven Stroke Roll | 2/4 | 5 slashed sixteenths + accented sixteenth on "e" of 2, eighth rest; two bars | **Least settled.** Five diddles do not fit an even grid. Other editions start on "e", use triplets or show a pickup. |
| 13 | Thirteen Stroke Roll | 2/4 | 6 slashed sixteenths + accented eighth on "&" of 2; two bars | Older: a dotted-quarter roll tied to an eighth. |
| 14 | Fifteen Stroke Roll | 2/4 | 7 slashed sixteenths + accented sixteenth on "a" of 2; two bars | Also seen releasing on the next downbeat (needs a longer bar). |
| 15 | Seventeen Stroke Roll | 3/4 | 8 slashed sixteenths + accented eighth on beat 3, eighth rest; two bars (wraps) | Also seen as a 2/4 bar of roll tied over the barline. Chose 3/4 to avoid the tie. |
| 16 | Single Paradiddle | 2/4 | sixteenths R> L R R L> R L L | Standard. |
| 17 | Double Paradiddle | 2/4 | sextuplet sixteenths R> L R L R R / L> R L R L L | Also seen in 6/8 straight sixteenths. |
| 18 | Triple Paradiddle | 2/4 | two bars of sixteenths (R lead, L lead) | Often one 4/4 bar. Split into two 2/4 bars so it can wrap at 360px. |
| 19 | Paradiddle-Diddle | 2/4 | sextuplets R> L R R L L (×2) | Also seen in 6/8. |
| 20 | Flam | 2/4 | flammed quarters lR rL | Some use eighths. |
| 21 | Flam Accent | 2/4 | eighth-note triplets lR> L R / rL> R L | Also seen in 6/8. |
| 22 | Flam Tap | 2/4 | sixteenths lR> R rL> L | Standard. |
| 23 | Flamacue | 2/4 | lR L> R L sixteenths + flammed quarter lR | Last flam as an eighth in some books. Not alternated (as on most charts). |
| 24 | Flam Paradiddle | 2/4 | lR> L R R / rL> R L L | Standard. |
| 25 | Single Flammed Mill | 2/4 | lR> R L R / rL> L R L | Standard. |
| 26 | Flam Paradiddle-Diddle | 2/4 | sextuplets lR> L R R L L / rL> R L L R R | Standard. |
| 27 | Pataflafla | 2/4 | sixteenths lR L R rL (×2), flams unaccented | Many teachers add accents on both flams. Left plain. |
| 28 | Swiss Army Triplet | 2/4 | eighth-note triplets lR> R L (×2) | Also seen as sixteenth triplets. |
| 29 | Inverted Flam Tap | 2/4 | sixteenths lR> L rL> R | Standard. The grace comes from the hand that just tapped. |
| 30 | Flam Drag | 6/8 | flammed eighth, two sixteenths, eighth: lR> L L R / rL> R R L | **Choice:** the "drag" is written as a sixteenth double, not as grace notes. Some editions use 2/4 triplets. |
| 31 | Drag (Ruff) | 2/4 | drag quarters llR rrL | Some accent the main note. Left plain. |
| 32 | Single Drag Tap | 2/4 | eighths llR L> / rrL R> | **Unsure:** some editions accent the dragged note instead of the tap. |
| 33 | Double Drag Tap | 2/4 | sixteenth, sixteenth, eighth: llR llR L> | **Unsure:** accent position as for #32. |
| 34 | Lesson 25 | 2/4 | sixteenth, sixteenth, eighth: llR L R> (×2) | Standard. |
| 35 | Single Dragadiddle | 2/4 | slashed accented sixteenth + three sixteenths: RR> L R R / LL> R L L | Some show the first stroke as a drag (grace notes). Chose the diddle (as played). |
| 36 | Drag Paradiddle #1 | 6/8 | accented eighth + four sixteenths (drag on the first): R> llR L R R | **Choice:** 6/8 so each hand gets one dotted-quarter group. Others use 2/4 with a different grouping. |
| 37 | Drag Paradiddle #2 | 2/4 | accented eighth, dragged eighth, then dragged paradiddle in sixteenths: R> llR llR L R R; two bars (wraps) | **Unsure** of the sticking against the official chart. Some editions accent the second note as well. |
| 38 | Single Ratamacue | 2/4 | sixteenth triplet (drag on first) + accented eighth: llR L R L> | Standard. |
| 39 | Double Ratamacue | 2/4 | dragged eighth + ratamacue triplet, accent on beat 2, eighth rest; two bars (wraps) | Some write it as a pickup bar or in 6/8. |
| 40 | Triple Ratamacue | 2/4 | two dragged eighths + single ratamacue; two bars (wraps) | Standard. |

## Self-check (tests/test_notation.py)

The test is 15 checks, all passing on 26 Nov. It checks:

- there are 40 entries, n = 1..40, and the names equal the app's rudiment list (it reads `RUDIMENTS` or, in older copies, `VIC_RUDIMENTS`)
- every SVG is well-formed XML
- the SVG has role, aria-label and title, uses currentColor only, has no fixed height and loads nothing external
- there is one sticking letter per note, and one grace-sticking letter per grace group
- every bar's notes and rests add up to the metre
- every card fits a 360px box with sticking at least 10.5px tall
- in dark mode the notation follows the text colour

PNGs for review are in `tests/out/notation/` (desktop) and `tests/out/notation/360/`. I looked at all 40 at both sizes and fixed these:

- graces were too small and crowding the main note
- the flam grace slash read as an X
- grace stems ran into beams inside beamed groups
- two-letter diddle sticking was crowding its neighbours
- long rudiments were too small at 360px, so the default wrap width went from 440 to 370

## Open points for Justin

The notation is our own engraving of the standard stickings. Before the site goes public, compare #12, #30, #32, #33, #36 and #37 with the PAS chart you use in class. Each one is a one-line string in `notation.js`, so any change is quick.
