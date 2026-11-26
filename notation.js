/* notation.js: the 40 PAS International Drum Rudiments drawn as SVG notation.
 *
 * window.Rudiments = { list: [{n, name, family, group, metre}], svg(n, opts) -> string }
 *
 * Every rudiment is a short text description, and one renderer draws them all.
 * Description language (one string per rudiment, bars separated by "|"):
 *   [ ... ]   beam group            3( ... )  tuplet (3 = triplet, 6 = sextuplet)
 *   note:     [f|d] R|L  q|e|s|t  [> / z]
 *             f = flam (one grace note), d = drag (two grace notes); graces use the other hand
 *             q e s t = quarter, eighth, sixteenth, thirty-second (as written)
 *             >  accent    /  one tremolo slash (diddle: the note is played as two strokes)
 *             z  buzz (multiple bounce)
 *   rest:     -q -e -s
 * Durations are counted in 1/24 of a quarter note, so tuplets stay whole numbers.
 *
 * Options for svg(n, opts):
 *   maxWidth  widest system in viewBox units before bars wrap to a new system (default 370,
 *             which keeps sticking text at least 11px tall in a 320px-wide box)
 *   label     override the aria-label text
 * The SVG has no fixed size: it fills its container width (up to 1.6x natural size),
 * uses currentColor throughout and loads nothing external.
 */
(function () {
  'use strict';

  var FAM = {
    single: ['Roll', 'Single stroke roll rudiments'],
    bounce: ['Roll', 'Multiple bounce roll rudiments'],
    dbl: ['Roll', 'Double stroke roll rudiments'],
    diddle: ['Diddle', 'Diddle rudiments'],
    flam: ['Flam', 'Flam rudiments'],
    drag: ['Drag', 'Drag rudiments']
  };

  // [name, family key, metre, description]. Order and names = VIC_RUDIMENTS in index.html.
  var DATA = [
    ['Single Stroke Roll', 'single', '2/4', '[Rs Ls Rs Ls] [Rs Ls Rs Ls]'],
    ['Single Stroke Four', 'single', '2/4', '[3(Rs Ls Rs) Le>] [3(Ls Rs Ls) Re>]'],
    ['Single Stroke Seven', 'single', '2/4', '[6(Rs Ls Rs Ls Rs Ls)] Rq> | [6(Ls Rs Ls Rs Ls Rs)] Lq>'],
    ['Multiple Bounce Roll', 'bounce', '2/4', '[Rsz Lsz Rsz Lsz] [Rsz Lsz Rsz Lsz]'],
    ['Triple Stroke Roll', 'bounce', '2/4', '[3(Rs Rs Rs) 3(Ls Ls Ls)] [3(Rs Rs Rs) 3(Ls Ls Ls)]'],
    ['Double Stroke Open Roll', 'dbl', '2/4', '[Rs Rs Ls Ls] [Rs Rs Ls Ls]'],
    ['Five Stroke Roll', 'dbl', '2/4', '[Rs/ Ls/ Re>] [Ls/ Rs/ Le>]'],
    ['Six Stroke Roll', 'dbl', '2/4', '[Rs> Ls/ Rs/ Ls>] [Rs> Ls/ Rs/ Ls>]'],
    ['Seven Stroke Roll', 'dbl', '2/4', '[3(Rs/ Ls/ Rs/) Le>] [3(Ls/ Rs/ Ls/) Re>]'],
    ['Nine Stroke Roll', 'dbl', '2/4', '[Rs/ Ls/ Rs/ Ls/] Re> -e | [Ls/ Rs/ Ls/ Rs/] Le> -e'],
    ['Ten Stroke Roll', 'dbl', '2/4', '[Rs/ Ls/ Rs/ Ls/] [Re> Le>]'],
    ['Eleven Stroke Roll', 'dbl', '2/4', '[Rs/ Ls/ Rs/ Ls/] [Rs/ Ls>] -e | [Ls/ Rs/ Ls/ Rs/] [Ls/ Rs>] -e'],
    ['Thirteen Stroke Roll', 'dbl', '2/4', '[Rs/ Ls/ Rs/ Ls/] [Rs/ Ls/ Re>] | [Ls/ Rs/ Ls/ Rs/] [Ls/ Rs/ Le>]'],
    ['Fifteen Stroke Roll', 'dbl', '2/4', '[Rs/ Ls/ Rs/ Ls/] [Rs/ Ls/ Rs/ Ls>] | [Ls/ Rs/ Ls/ Rs/] [Ls/ Rs/ Ls/ Rs>]'],
    ['Seventeen Stroke Roll', 'dbl', '3/4', '[Rs/ Ls/ Rs/ Ls/] [Rs/ Ls/ Rs/ Ls/] Re> -e | [Ls/ Rs/ Ls/ Rs/] [Ls/ Rs/ Ls/ Rs/] Le> -e'],
    ['Single Paradiddle', 'diddle', '2/4', '[Rs> Ls Rs Rs] [Ls> Rs Ls Ls]'],
    ['Double Paradiddle', 'diddle', '2/4', '[6(Rs> Ls Rs Ls Rs Rs)] [6(Ls> Rs Ls Rs Ls Ls)]'],
    ['Triple Paradiddle', 'diddle', '2/4', '[Rs> Ls Rs Ls] [Rs Ls Rs Rs] | [Ls> Rs Ls Rs] [Ls Rs Ls Ls]'],
    ['Paradiddle-Diddle', 'diddle', '2/4', '[6(Rs> Ls Rs Rs Ls Ls)] [6(Rs> Ls Rs Rs Ls Ls)]'],
    ['Flam', 'flam', '2/4', 'fRq fLq'],
    ['Flam Accent', 'flam', '2/4', '[3(fRe> Le Re)] [3(fLe> Re Le)]'],
    ['Flam Tap', 'flam', '2/4', '[fRs> Rs fLs> Ls] [fRs> Rs fLs> Ls]'],
    ['Flamacue', 'flam', '2/4', '[fRs Ls> Rs Ls] fRq'],
    ['Flam Paradiddle', 'flam', '2/4', '[fRs> Ls Rs Rs] [fLs> Rs Ls Ls]'],
    ['Single Flammed Mill', 'flam', '2/4', '[fRs> Rs Ls Rs] [fLs> Ls Rs Ls]'],
    ['Flam Paradiddle-Diddle', 'flam', '2/4', '[6(fRs> Ls Rs Rs Ls Ls)] [6(fLs> Rs Ls Ls Rs Rs)]'],
    ['Pataflafla', 'flam', '2/4', '[fRs Ls Rs fLs] [fRs Ls Rs fLs]'],
    ['Swiss Army Triplet', 'flam', '2/4', '[3(fRe> Re Le)] [3(fRe> Re Le)]'],
    ['Inverted Flam Tap', 'flam', '2/4', '[fRs> Ls fLs> Rs] [fRs> Ls fLs> Rs]'],
    ['Flam Drag', 'flam', '6/8', '[fRe> Ls Ls Re] [fLe> Rs Rs Le]'],
    ['Drag (Ruff)', 'drag', '2/4', 'dRq dLq'],
    ['Single Drag Tap', 'drag', '2/4', '[dRe Le>] [dLe Re>]'],
    ['Double Drag Tap', 'drag', '2/4', '[dRs dRs Le>] [dLs dLs Re>]'],
    ['Lesson 25', 'drag', '2/4', '[dRs Ls Re>] [dRs Ls Re>]'],
    ['Single Dragadiddle', 'drag', '2/4', '[Rs/> Ls Rs Rs] [Ls/> Rs Ls Ls]'],
    ['Drag Paradiddle #1', 'drag', '6/8', '[Re> dRs Ls Rs Rs] [Le> dLs Rs Ls Ls]'],
    ['Drag Paradiddle #2', 'drag', '2/4', '[Re> dRe] [dRs Ls Rs Rs] | [Le> dLe] [dLs Rs Ls Ls]'],
    ['Single Ratamacue', 'drag', '2/4', '[3(dRs Ls Rs) Le>] [3(dLs Rs Ls) Re>]'],
    ['Double Ratamacue', 'drag', '2/4', '[dRe 3(dRs Ls Rs)] Le> -e | [dLe 3(dLs Rs Ls)] Re> -e'],
    ['Triple Ratamacue', 'drag', '2/4', '[dRe dRe] [3(dRs Ls Rs) Le>] | [dLe dLe] [3(dLs Rs Ls) Re>]']
  ];

  var WRITTEN = { q: 24, e: 12, s: 6, t: 3 };
  var BEAMS = { q: 0, e: 1, s: 2, t: 3 };
  var TUPLET = { 3: [2, 3], 5: [4, 5], 6: [4, 6], 7: [4, 7] }; // n notes in the time of m

  function other(h) { return h === 'R' ? 'l' : 'r'; }

  // ---- parser: description -> bars of items -------------------------------------
  function parse(desc) {
    var tokens = desc.match(/\[|\]|\d+\(|\)|\||[^\s\[\]\(\)\|]+/g) || [];
    var bars = [], bar = [], group = null, tup = null, gid = 0, tid = 0;
    tokens.forEach(function (t) {
      if (t === '|') { bars.push(bar); bar = []; return; }
      if (t === '[') { group = ++gid; return; }
      if (t === ']') { group = null; return; }
      if (/^\d+\($/.test(t)) { var k = parseInt(t, 10); if (!TUPLET[k]) throw new Error('tuplet ' + k); tup = { id: ++tid, n: k }; return; }
      if (t === ')') { tup = null; return; }
      var m = /^-([qest])$/.exec(t);
      if (m) {
        bar.push({ kind: 'rest', v: m[1], dur: dur(m[1], tup), group: group, tup: tup });
        return;
      }
      m = /^([fd]?)([RL])([qest])([>\/z]*)$/.exec(t);
      if (!m) throw new Error('bad token ' + t);
      var mods = m[4];
      bar.push({
        kind: 'note', grace: m[1], hand: m[2], v: m[3], dur: dur(m[3], tup), group: group, tup: tup,
        accent: mods.indexOf('>') >= 0, diddle: mods.indexOf('/') >= 0, buzz: mods.indexOf('z') >= 0
      });
    });
    bars.push(bar);
    return bars;
  }
  function dur(v, tup) {
    var w = WRITTEN[v];
    if (!tup) return w;
    var r = TUPLET[tup.n];
    return w * r[0] / r[1];
  }
  function metreUnits(metre) {
    var p = metre.split('/');
    return parseInt(p[0], 10) * 96 / parseInt(p[1], 10);
  }
  function graceText(it) {
    if (it.grace === 'f') return other(it.hand);
    if (it.grace === 'd') return other(it.hand) + other(it.hand);
    return '';
  }
  function mainText(it) { return it.diddle ? it.hand + it.hand : it.hand; }
  function stickingOf(bars) {
    var out = [];
    bars.forEach(function (b) {
      b.forEach(function (it) {
        if (it.kind !== 'note') return;
        out.push(graceText(it) + mainText(it) + (it.accent ? '>' : '') + (it.buzz ? 'z' : ''));
      });
    });
    return out.join(' ');
  }

  // ---- geometry (viewBox units) ---------------------------------------------------
  var G = {
    sysH: 100, lineY: 54,       // staff line sits 54 below the system top
    stemLen: 32, beamH: 4.6, beamGap: 7.4,
    headRx: 5.7, headRy: 4.1, stemDx: 5.1,
    graceScale: 0.66,
    flamLead: 19, dragLead: 29,
    stickY: 36, accentY: 14
  };

  function itemWidth(it) {
    var body = Math.max(it.kind === 'rest' ? 16 : 18, 11 + it.dur * 1.35);
    if (it.kind === 'note' && it.diddle) body = Math.max(body, 25);
    var lead = it.kind === 'note' ? (it.grace === 'f' ? G.flamLead : it.grace === 'd' ? G.dragLead : 0) : 0;
    if (it.kind === 'note' && it.diddle && !it.grace) lead += 6;  // room for the two-letter sticking
    return { lead: lead, body: body };
  }

  var GRACE_FONT = ' class="stk grace-stk" font-style="italic" font-family="Georgia, \'Times New Roman\', serif"';
  function f(x) { return Math.round(x * 10) / 10; }
  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }

  // ---- drawing primitives -----------------------------------------------------------
  function head(x, y, s) {
    s = s || 1;
    return '<ellipse cx="' + f(x) + '" cy="' + f(y) + '" rx="' + f(G.headRx * s) + '" ry="' + f(G.headRy * s) +
      '" transform="rotate(-22 ' + f(x) + ' ' + f(y) + ')"/>';
  }
  function line(x1, y1, x2, y2, w) {
    return '<line x1="' + f(x1) + '" y1="' + f(y1) + '" x2="' + f(x2) + '" y2="' + f(y2) + '" stroke="currentColor" stroke-width="' + w + '"/>';
  }
  function rect(x, y, w, h) {
    return '<rect x="' + f(x) + '" y="' + f(y) + '" width="' + f(w) + '" height="' + f(h) + '"/>';
  }
  function flag(sx, top, i, s) {
    s = s || 1;
    var y = top + i * 7 * s;
    return '<path d="M' + f(sx) + ' ' + f(y) + 'c' + f(1 * s) + ' ' + f(5 * s) + ' ' + f(9 * s) + ' ' + f(7 * s) + ' ' + f(7.5 * s) + ' ' + f(17 * s) +
      'c' + f(0.6 * s) + ' ' + f(-6.5 * s) + ' ' + f(-4.5 * s) + ' ' + f(-9 * s) + ' ' + f(-7.5 * s) + ' ' + f(-10.5 * s) + 'z" stroke="none"/>';
  }
  function slash(sx, y) {
    // tremolo slash: a thick oblique bar through the stem
    return '<path d="M' + f(sx - 4.6) + ' ' + f(y + 1.2) + 'L' + f(sx + 4.6) + ' ' + f(y - 2.8) + 'L' + f(sx + 4.6) + ' ' + f(y - 0.2) +
      'L' + f(sx - 4.6) + ' ' + f(y + 3.8) + 'z" stroke="none"/>';
  }
  function buzz(sx, y) {
    return '<path d="M' + f(sx - 3.4) + ' ' + f(y - 3) + 'h6.8l-6.8 6h6.8" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>';
  }
  function accent(x, y) {
    return '<path d="M' + f(x - 5) + ' ' + f(y - 3.4) + 'L' + f(x + 5) + ' ' + f(y) + 'L' + f(x - 5) + ' ' + f(y + 3.4) +
      '" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="miter"/>';
  }
  function rest(v, x, y) {
    // eighth and sixteenth rests: dot-and-hook glyphs on a slanted stem
    var out = '<g class="rest-glyph">';
    var hooks = v === 's' ? 2 : 1, top = y - 6;
    for (var i = 0; i < hooks; i++) {
      var hy = top + i * 7, hx = x - i * 1.6;
      out += '<circle cx="' + f(hx - 2.2) + '" cy="' + f(hy) + '" r="2.4" stroke="none"/>';
      out += '<path d="M' + f(hx - 2.6) + ' ' + f(hy + 1.6) + 'Q' + f(hx + 1) + ' ' + f(hy + 2.6) + ' ' + f(hx + 3.6) + ' ' + f(hy - 1.4) + '" fill="none" stroke="currentColor" stroke-width="1.4"/>';
    }
    out += line(x + 3.6, top - 1.4, x - 1.2 - (hooks - 1) * 1.6, top + 14 + (hooks - 1) * 6, 1.4);
    if (v === 'q') out = '<path d="M' + f(x - 2) + ' ' + f(y - 12) + 'l5 6-4 5 5 6c-4-2-7 0-5 4-5-3-3-8 1-7l-5-6 4-5z" stroke="none"/>';
    return out + (v === 'q' ? '' : '</g>');
  }
  function text(x, y, s, size, extra) {
    return '<text x="' + f(x) + '" y="' + f(y) + '" font-size="' + size + '" text-anchor="middle"' + (extra || '') + '>' + esc(s) + '</text>';
  }

  // ---- layout and render ---------------------------------------------------------------
  function layoutBar(items) {
    var x = 12, placed = [];
    items.forEach(function (it) {
      var w = itemWidth(it);
      x += w.lead;
      placed.push({ it: it, x: x + 6 });
      x += w.body;
    });
    return { placed: placed, width: x + 2 };
  }

  function renderBar(bar, ox, top) {
    var L = top + G.lineY, beamTop = L - G.stemLen, out = [];
    var lay = layoutBar(bar.items);
    var groups = {}, tuplets = {};
    lay.placed.forEach(function (p) {
      var it = p.it, x = ox + p.x;
      p.ax = x;
      if (it.kind === 'rest') {
        out.push('<g class="rest" data-dur="' + it.dur + '">' + rest(it.v, x, L) + '</g>');
      } else {
        var sx = x + G.stemDx, g = '<g class="note" data-dur="' + it.dur + '">';
        g += head(x, L);
        var grouped = it.group && bar.items.filter(function (o) { return o.group === it.group && o.kind === 'note'; }).length > 1;
        g += line(sx, L - 1, sx, beamTop + (grouped ? 0.5 : 0), 1.3);
        if (!grouped) for (var i = 0; i < BEAMS[it.v]; i++) g += flag(sx, beamTop, i);
        var low = beamTop + Math.max(BEAMS[it.v], 1) * G.beamGap - (G.beamGap - G.beamH);
        var mid = (low + L - 4) / 2;
        if (it.diddle) g += slash(sx, mid - 1.5);
        if (it.buzz) g += buzz(sx, mid);
        if (it.accent) g += accent(x, L + G.accentY);
        // grace notes
        var gs = G.graceScale, gTop = L - 19.5;
        if (it.grace === 'f') {
          var gx = x - G.flamLead + 4, gsx = gx + G.stemDx * gs;
          g += '<g class="grace">' + head(gx, L, gs) + line(gsx, L - 1, gsx, gTop, 1) + flag(gsx, gTop, 0, gs) + '</g>';
          g += text(gx, L + G.stickY, other(it.hand), 11, GRACE_FONT);
        } else if (it.grace === 'd') {
          var g1 = x - G.dragLead + 4, g2 = g1 + 10, s1 = g1 + G.stemDx * gs, s2 = g2 + G.stemDx * gs;
          g += '<g class="grace">' + head(g1, L, gs) + head(g2, L, gs) + line(s1, L - 1, s1, gTop, 1) + line(s2, L - 1, s2, gTop, 1) +
            rect(s1 - 0.5, gTop, s2 - s1 + 1, 2.6) + rect(s1 - 0.5, gTop + 5, s2 - s1 + 1, 2.6) + '</g>';
          g += text((g1 + g2) / 2, L + G.stickY, other(it.hand) + other(it.hand), 11, GRACE_FONT);
        }
        g += text(x, L + G.stickY, mainText(it), 13, ' class="stk" font-weight="600"');
        out.push(g + '</g>');
        p.sx = sx;
        if (it.group) (groups[it.group] = groups[it.group] || []).push(p);
        if (it.tup) (tuplets[it.tup.id] = tuplets[it.tup.id] || { n: it.tup.n, ps: [] }).ps.push(p);
      }
    });
    // beams
    Object.keys(groups).forEach(function (k) {
      var ps = groups[k];
      if (ps.length < 2) return;
      var lv = ps.map(function (p) { return BEAMS[p.it.v]; });
      var maxL = Math.max.apply(null, lv);
      for (var level = 0; level < maxL; level++) {
        var y = beamTop + level * G.beamGap, i = 0;
        while (i < ps.length) {
          if (lv[i] <= level) { i++; continue; }
          var j = i;
          while (j + 1 < ps.length && lv[j + 1] > level) j++;
          if (j > i) out.push(rect(ps[i].sx - 0.65, y, ps[j].sx - ps[i].sx + 1.3, G.beamH));
          else {
            var stub = 7.5, right = (i === 0);
            out.push(rect(right ? ps[i].sx - 0.65 : ps[i].sx - stub, y, stub + 0.65, G.beamH));
          }
          i = j + 1;
        }
      }
    });
    // tuplet numbers
    Object.keys(tuplets).forEach(function (k) {
      var t = tuplets[k], a = t.ps[0], b = t.ps[t.ps.length - 1];
      var cx = (a.sx + b.sx) / 2;
      out.push(text(cx, beamTop - 5, String(t.n), 11.5, ' class="tuplet" font-style="italic" font-weight="700" font-family="Georgia, \'Times New Roman\', serif"'));
    });
    return { svg: out.join(''), width: lay.width };
  }

  function barline(x, L, kind) {
    var y1 = L - 12, y2 = L + 12, s = '';
    if (kind === 'end') {
      s += '<circle cx="' + f(x - 7) + '" cy="' + f(L - 5) + '" r="1.9" stroke="none"/><circle cx="' + f(x - 7) + '" cy="' + f(L + 5) + '" r="1.9" stroke="none"/>';
      s += line(x - 3, y1, x - 3, y2, 1.2) + rect(x, y1, 3.6, y2 - y1);
    } else if (kind === 'start') {
      s += rect(x, y1, 3.6, y2 - y1) + line(x + 6.6, y1, x + 6.6, y2, 1.2);
      s += '<circle cx="' + f(x + 10.6) + '" cy="' + f(L - 5) + '" r="1.9" stroke="none"/><circle cx="' + f(x + 10.6) + '" cy="' + f(L + 5) + '" r="1.9" stroke="none"/>';
    } else {
      s += line(x, y1, x, y2, 1.2);
    }
    return s;
  }

  function build(n) {
    var d = DATA[n - 1];
    if (!d) return null;
    var bars = parse(d[3]);
    return { n: n, name: d[0], family: FAM[d[1]][0], group: FAM[d[1]][1], metre: d[2], bars: bars, sticking: stickingOf(bars) };
  }

  function svg(n, opts) {
    opts = opts || {};
    var r = build(n);
    if (!r) return '';
    var maxW = opts.maxWidth || 370;
    var CLEF = 22, TIME = 22, START = 16, END = 12;
    var bars = r.bars.map(function (items) { return { items: items, width: layoutBar(items).width }; });
    // pack bars into systems
    var systems = [], cur = [], curW = 0;
    bars.forEach(function (b) {
      var head = systems.length === 0 ? CLEF + TIME + START : CLEF;
      if (cur.length && head + curW + b.width + END > maxW) { systems.push(cur); cur = []; curW = 0; }
      cur.push(b); curW += b.width;
    });
    systems.push(cur);

    var body = [], W = 0;
    systems.forEach(function (sys, si) {
      var top = si * G.sysH, L = top + G.lineY, x = 8;
      var s = '<g class="system">';
      s += rect(x, L - 10, 3, 20) + rect(x + 6, L - 10, 3, 20);  // percussion clef
      x += CLEF;
      if (si === 0) {
        var mp = r.metre.split('/');
        var tf = ' font-weight="700" font-family="Georgia, \'Times New Roman\', serif" class="timesig"';
        s += text(x + 4, L - 2, mp[0], 21, tf) + text(x + 4, L + 17, mp[1], 21, tf);
        x += TIME;
        s += barline(x - 6, L, 'start');
        x += START - 6;
      }
      sys.forEach(function (b, bi) {
        var rb = renderBar(b, x, top);
        var units = b.items.reduce(function (a, it) { return a + it.dur; }, 0);
        s += '<g class="bar" data-units="' + units + '" data-metre-units="' + metreUnits(r.metre) + '">' + rb.svg + '</g>';
        x += rb.width;
        var last = si === systems.length - 1 && bi === sys.length - 1;
        if (last) { x += END; s += barline(x - 4, L, 'end'); x += 2; }
        else if (bi === sys.length - 1) { s += barline(x, L, 'bar'); x += 2; }
        else { s += barline(x, L, 'bar'); }
      });
      // staff line drawn last-but-under: prepend
      s = s.replace('<g class="system">', '<g class="system">' + line(6, L, x, L, 1.1));
      W = Math.max(W, x + 6);
      body.push(s + '</g>');
    });
    var H = systems.length * G.sysH + 4;
    var label = opts.label || (r.name + ', ' + r.metre + ' time. Sticking: ' + r.sticking.replace(/>/g, ' accent').replace(/z/g, ' buzz'));
    return '<svg xmlns="http://www.w3.org/2000/svg" class="rudiment-svg" viewBox="0 0 ' + f(W) + ' ' + H + '" width="100%"' +
      ' style="max-width:' + Math.round(W * 1.6) + 'px;height:auto;display:block" role="img" aria-label="' + esc(label) + '"' +
      ' data-rudiment="' + r.n + '" data-metre="' + r.metre + '" fill="currentColor"' +
      ' font-family="system-ui, -apple-system, \'Segoe UI\', Helvetica, Arial, sans-serif">' +
      '<title>' + esc(label) + '</title>' +
      body.join('') + '</svg>';
  }

  var list = DATA.map(function (d, i) {
    return { n: i + 1, name: d[0], family: FAM[d[1]][0], group: FAM[d[1]][1], metre: d[2] };
  });

  window.Rudiments = {
    list: list,
    svg: svg,
    // for tests and the preview page
    describe: function (n) { var d = DATA[n - 1]; return d ? d[3] : null; },
    parse: function (n) { return build(n); },
    credit: 'The 40 International Drum Rudiments are the standard list published by the Percussive Arts Society. Notation drawn for this app.'
  };
})();
