# Spec V: family-style refinement (approved by Justin 27 Nov 2026, as recommended)

Aim: Percussion Lab reads as a sibling of The Guitar Lab ("a Shmungfroi instrument"), not a ChatGPT dashboard. **Visual layer only.** Layout, features, wording (except the brand line), saved-data shape, storage key and behaviour stay exactly as they are. Student-facing design must not look AI-generated.

Reference app: The Guitar Lab, `/home/claude/guitar-lab/index.html` (+ `fonts/`). Read its `:root` tokens, `@font-face`, light/dark handling and component styling before starting.

## Tokens (V1, V2, V7)
Use the Guitar Lab's light-dark token pattern: dark values default, `@supports (color:light-dark(#000,#fff))` block with `color-scheme:light dark`, `:root[data-theme=light]` / `[data-theme=dark]` overrides.
| Token | Dark | Light |
|---|---|---|
| bg | #0b0906 | #f7f1e3 |
| card | #12100b | #fffaf0 |
| ink | #ece2c8 | #2a2216 |
| muted | #9c927c | #6f634c |
| rule | #2a2418 | #d9cdb2 |
| gold | #c9a24a | #8a6a22 |
| gold-hi | #f0d48a | #7a5c12 |
| **teal (signature)** | #3fb6a8 | a darker teal that passes WCAG AA on #fffaf0 (≈#1f7d73) |
- Teal = Percussion Lab's signature: progress bars, done/complete states, selected level, primary button, active nav, ticked warm-up cells. Gold = secondary accents (tips, gold chips, brand line detail).
- Lime `#b3ef66` retired completely (0 uses at the end), including in JS-generated SVG (e.g. `diamondSVG` fill `#b3ef66`) — update the matching test selector.
- Light mode: follows the device setting by default; add a small Light / Dark / Auto control in the sidebar footer, same behaviour as The Guitar Lab if it has one, stored in localStorage under a **separate** key (never inside the saved progress object).

## Type (V3, V4)
- `fonts/` already contains PoiretOne-Regular.ttf, Outfit-Regular.ttf, Outfit-Bold.ttf (copied from the Guitar Lab; OFL). Use the same `@font-face` declarations ('G Poiret', 'G Outfit') with system fallbacks.
- Poiret One for display: brand, page h1/h2, hero title. Outfit for everything else, including labels, chips, pills, numbers (tabular-nums). Remove every monospace font-family (C2 rule in README to be updated: "Poiret One for display, Outfit for everything else; numbers tabular").
- Brand: "Percussion Lab" in Poiret with "a Shmungfroi instrument" beneath, replacing the all-caps heavy "PERCUSSION TECHNIQUE LAB". Keep the student-code/meta line. Page `<title>` → "Percussion Lab".
- No all-caps letter-spaced eyebrow shouting; small labels may stay small, sentence case or gentle small caps as in the Guitar Lab.

## Remove dashboard tells (V5)
- `.card::before` lime 24 % stripe: remove.
- Boxy monospace pills/chips: restyle like the Guitar Lab (rounded, quiet border, Outfit).
- Square nav dots: remove or replace with the Guitar Lab's nav treatment.
- Brown tip/notice boxes: re-tone to the gold family (gold left rule on card colour).
- Corners/spacing: match the Guitar Lab (6 / 12 / 999 px radii in its file).
- Strip the stacked ChatGPT override layers where possible: the stylesheet has several generations of overrides (base teal theme → lime dark theme → mid-grey overrides → later passes). Consolidate so the final CSS is one coherent layer. Keep every functional rule (C/F/P fixes: tap targets, 12 px floor, print, focus, reduced motion, sticky phone tab bar etc.).

## Number-diamond trace (V6, decision D7: must stay)
- Keep `.page::before` trace (same geometry, tile sizes 600 px / 470 px under 820 px, opacity tuned so it stays a faint trace in both themes, hidden in print).
- Recolour the SVG: the 2s gold (#c9a24a), the 3s ivory (#d8e2d3 → ivory #ece2c8), grid lines rule-toned, dashed line gold low opacity. In light mode use a light-mode variant (darker gold/ink lines at low opacity) so it remains visible on cream.
- Warm-up diamond on Today: same family colours (filled cells teal, outlines rule/gold).

## Strands (V8)
Remap STRANDS colours: Rhythm Diamonds teal #3fb6a8, Subdivision & metre gold #c9a24a, Stick control & rudiments clay (≈#c98a5a), Polyrhythm & independence violet #a493d8, Mallets Garden green #8fbf6a. Light-mode readable variants where used as text.

## Notation
`notation.js` draws with currentColor-style text colour; confirm notation stays legible in both themes (test_notation has a dark-background check; add the light equivalent if simple).

## Must not change
Saved-data shape, storage key, export/import, dialogs, print output (still dark ink on white), Pages/framed behaviour, any text other than brand/title, PAS credit, metronome audio.

## Tests and evidence
- `python3 tests/run_tests.py` and `python3 tests/test_notation.py` must pass. Update only selectors/assertions that encode the old look (lime fill; P4 "only index.html and notation.js" now also allows same-origin `fonts/*.ttf`). Add checks: no `#b3ef66` anywhere; no monospace font-family in computed styles of body/labels; Poiret on brand; theme toggle switches `color-scheme` and persists outside the progress object; trace present in both themes.
- `scripts/build_single_file.py`: one-file copy should embed the three fonts as base64 `@font-face` so it still looks right offline.
- Screenshots to `tests/reports/spec-v/shots/`: Today, Technique tracker, Rudiment library, at 1366 and 390 px, dark and light; plus the Guitar Lab at the same widths for comparison.
- Log V1–V8 in `CORRECTIONS.md` (27 Nov section) and update README type rule.
