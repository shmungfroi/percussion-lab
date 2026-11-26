/* notation.js: the 40 PAS International Drum Rudiments drawn as SVG notation.
 *
 * window.Rudiments = { list: [{n, name, family, group}], svg(n, opts) -> string }
 *
 * The notation follows the PAS 40 International Drum Rudiments as shown on the Vic Firth
 * Rudiments poster (2016): the same note values, beaming, tuplet numbers, tremolo slashes,
 * ties, accents, grace notes, rests, sticking rows and "or" alternatives. It is redrawn by
 * this file; no image of the poster is used. Like the poster: five-line staff, snare in the
 * third space, no clef, no time signature, opening thick-thin bar line, closing thin-thick.
 *
 * Every rudiment is a short text description, and one renderer draws them all.
 * Description language (tokens separated by spaces):
 *   [ ... ]   beam group                  !    inside a group: break the 2nd/3rd beams here
 *   3( ... )  tuplet with its number shown (3 or 6); may hold rests and beam groups
 *   |         a place where a long line may wrap (nothing is drawn)
 *   or        the italic "or" between two versions (also a wrap point)
 *   rest:     -e  -s  -q                   (eighth, sixteenth, quarter rest)
 *   note:     [f|d] VALUE [mods] [:ROW1[,ROW2]]
 *     f = flam grace (one small flagged note with a slash), d = drag grace (two small beamed notes)
 *     VALUE  w h q e s t = whole, half, quarter, eighth, sixteenth, thirty-second
 *     mods   .  dot      /  one tremolo slash per "/" (1, 2 or 3)      >  accent
 *            z  buzz (Z)  ~  tie (slur) to the next note
 *     ROW1, ROW2  the sticking written under this note in the first and second row.
 *            R L = normal letters; r l = the small letters (grace notes, small diddle letters);
 *            _ = a space; any other text (e.g. "etc.") is written as is.
 *            The first capital letter sits under the note head; small letters before it sit
 *            to its left (under the grace notes); the rest runs on to the right.
 *
 * Options for svg(n, opts):
 *   maxWidth  widest system in viewBox units before the line wraps at a "|" or "or" (default 370,
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
    dbl: ['Roll', 'Double stroke open roll rudiments'],
    diddle: ['Diddle', 'Diddle rudiments'],
    flam: ['Flam', 'Flam rudiments'],
    drag: ['Drag', 'Drag rudiments']
  };

  // [name, family key, description]. Order and names = RUDIMENTS in index.html (names as titled on the poster).
  var DATA = [
    ['Single Stroke Roll', 'single', '[t:R t:L t:R t:L t:R t:L t:R t:L] | [t:R t:L t:R t:L t:R t:L t:R t:L]'],
    ['Single Stroke Four', 'single', '[3( s:R,L s:L,R s:R,L ) e:L,R] | [3( s:R,L s:L,R s:R,L ) e:L,R]'],
    ['Single Stroke Seven', 'single', '[6( s:R,L s:L,R s:R,L s:L,R s:R,L s:L,R )] q:R,L | [6( s:R,L s:L,R s:R,L s:L,R s:R,L s:L,R )] q:R,L'],
    ['Multiple Bounce Roll', 'bounce', 'wz:R_L_R_L_R_L_R_L_etc.'],
    ['Triple Stroke Roll', 'bounce', '[3( s:R s:R s:R ) ! 3( s:L s:L s:L )] | [3( s:R s:R s:R ) ! 3( s:L s:L s:L )]'],
    ['Double Stroke Roll', 'dbl', 'w///:R_R_L_L_R_R_L_L_R_R_L_L_R_R_L_L_etc.'],
    ['Five Stroke Roll', 'dbl', '[e//~:RRLL e>:R] | [e//~:LLRR e>:L] or [3( e/:R e/:L e>:R )] | [3( e/:L e/:R e>:L )]'],
    ['Six Stroke Roll', 'dbl', '-s [s/:LL,RR s/:+RR,+LL s>:+L,+R] | [s>:R,L e//~:LLRR,RRLL s>:L,R] | [s>:R,L e//~:L,R s>:L,R]'],
    ['Seven Stroke Roll', 'dbl', '-s [s/:LL,RR s/:+RR,+LL s/:+LL,+RR] | [s>:+R,+L e.//~:LLRRLL,RRLLRR] q>:R,L or ' +
      '[3( s/:LL,RR s/:+RR,+LL s/:+LL,+RR ) e>:+R,+L] | [3( s/:LL,RR s/:+RR,+LL s/:+LL,+RR ) e>:+R,+L]'],
    ['Nine Stroke Roll', 'dbl', 'q///~:RRLLRRLL e>:R | q///~:LLRRLLRR e>:L or q///~:R q>:R | q///~:L q>:L'],
    ['Ten Stroke Roll', 'dbl', 'q///~:RRLLRRLL,LLRRLLRR [s>:R,L s>:L,R] -e | q///~:RRLLRRLL,LLRRLLRR [s>:R,L s>:L,R] -e or ' +
      '[3( e>:R,L e/ e/ )] | [3( e/ e/ e>:L,R )] | [3( e>:R,L e/ e/ )] | [3( e/ e/ e>:L,R )] q>:R,L'],
    ['Eleven Stroke Roll', 'dbl', 'q///~:RRLLRRLL,LLRRLLRR [s/:RR,LL s>:+L,+R] -e | q///~:RRLLRRLL,LLRRLLRR [s/:RR,LL s>:+L,+R] -e or ' +
      '[3( e>:R,L e/ e/ )] | [3( e/ e/ e/:L,R )] | [3( e>:R,L e/ e/ )] | [3( e/ e/ e/:L,R )] q>:R,L'],
    ['Thirteen Stroke Roll', 'dbl', 'q.///~:RRLLRRLLRRLL e>:R | q.///~:LLRRLLRRLLRR e>:L'],
    ['Fifteen Stroke Roll', 'dbl', 'q///~:RRLLRRLL,LLRRLLRR [e.//~:RRLLRR,LLRRLL s>:L,R] or ' +
      '[s>:R,L e.//~:LLRRLL,RRLLRR] q///~:RRLLRRLL,LLRRLLRR q>:R,L'],
    ['Seventeen Stroke Roll', 'dbl', 'h///~:RRLLRRLLRRLLRRLL q>:R | h///~:LLRRLLRRLLRRLLRR q>:L'],
    ['Single Paradiddle', 'diddle', '[s>:R s:L s:R s:R] | [s>:L s:R s:L s:L]'],
    ['Double Paradiddle', 'diddle', '[s>:R s:L s:R s:L s:R s:R] | [s>:L s:R s:L s:R s:L s:L]'],
    ['Triple Paradiddle', 'diddle', '[s>:R s:L s:R s:L s:R s:L s:R s:R] | [s>:L s:R s:L s:R s:L s:R s:L s:L]'],
    ['Paradiddle–Diddle', 'diddle', '[s>:R,L s:L,R s:R,L s:R,L s:L,R s:L,R] | [s>:R,L s:L,R s:R,L s:R,L s:L,R s:L,R]'],
    ['Flam', 'flam', '[fe>:lR fe>:rL] | [fe>:lR fe>:rL] | [fe>:lR fe>:rL] | [fe>:lR fe>:rL]'],
    ['Flam Accent', 'flam', '[3( fe>:lR e:L e:R )] | [3( fe>:rL e:R e:L )]'],
    ['Flam Tap', 'flam', '[fs>:lR s:R fs>:rL s:L] | [fs>:lR s:R fs>:rL s:L]'],
    ['Flamacue', 'flam', '[fs:lR,rL s>:L,R s:R,L s:L,R] | fq>:lR,rL'],
    ['Flam Paradiddle', 'flam', '[fs>:lR s:L s:R s:R] | [fs>:rL s:R s:L s:L]'],
    ['Single Flammed Mill', 'flam', '[fs>:lR s:R s:L s:R] | [fs>:rL s:L s:R s:L]'],
    ['Flam Paradiddle–Diddle', 'flam', '[fs>:lR s:L s:R s:R s:L s:L] | [fs>:rL s:R s:L s:L s:R s:R]'],
    ['Pataflafla', 'flam', '[fs>:lR,rL s:L,R s:R,L fs>:rL,lR] | [fs>:lR,rL s:L,R s:R,L fs>:rL,lR]'],
    ['Swiss Army Triplet', 'flam', '[3( fs>:lR,rL s:R,L s:L,R ) ! 3( fs>:lR,rL s:R,L s:L,R )] | [3( fs>:lR,rL s:R,L s:L,R ) ! 3( fs>:lR,rL s:R,L s:L,R )]'],
    ['Inverted Flam Tap', 'flam', '[fs>:lR s:L fs>:rL s:R] | [fs>:lR s:L fs>:rL s:R]'],
    ['Flam Drag', 'flam', '[3( fe>:lR s:L s:L e:R )] | [3( fe>:rL s:R s:R e:L )]'],
    ['Drag (Ruff)', 'drag', 'dq:llR | dq:rrL | dq:llR | dq:rrL'],
    ['Single Drag Tap', 'drag', '[de:llR e>:L] | [de:rrL e>:R] or 3( -e [e/:L e:R] ) | [3( e>:L e/:R e:L )] | [3( e>:R e/:L e:R )]'],
    ['Double Drag Tap', 'drag', '[de.:llR ds:llR e>:L] | [de.:rrL ds:rrL e>:R] or ' +
      '-s [s/:ll s:+R s/:+ll e:+R] | [s>:L s/:+rr s:+L s/:+rr e:+L] | [s>:R s/:+ll s:+R s/:+ll e:+R]'],
    ['Lesson 25', 'drag', '[ds:llR,rrL s:L,R e>:R,L] | [ds:llR,rrL s:L,R e>:R,L] or ' +
      '-s [s/:ll,rr s:R,L s:L,R] | [s>:R,L s/:ll,rr s:R,L s:L,R] | [s>:R,L s/:ll,rr s:R,L s:L,R]'],
    ['Single Dragadiddle', 'drag', '[s/>:R_R s:L s:R s:R] | [s/>:L_L s:R s:L s:L]'],
    ['Drag Paradiddle #1', 'drag', '[e>:R ds:llR s:L s:R s:R] | [e>:L ds:rrL s:R s:L s:L]'],
    ['Drag Paradiddle #2', 'drag', '[e>:R de:llR] | [ds:llR s:L s:R s:R] | [e>:L de:rrL] | [ds:rrL s:R s:L s:L]'],
    ['Single Ratamacue', 'drag', '[3( ds:llR s:L s:R ) e>:L] | [3( ds:rrL s:R s:L ) e>:R]'],
    ['Double Ratamacue', 'drag', '[de:llR 3( ds:llR s:L s:R ) e>:L] | [de:rrL 3( ds:rrL s:R s:L ) e>:R]'],
    ['Triple Ratamacue', 'drag', '[de:llR de:llR] | [3( ds:llR s:L s:R ) e>:L] | [de:rrL de:rrL] | [3( ds:rrL s:R s:L ) e>:R]']
  ];

  var BEAMS = { w: 0, h: 0, q: 0, e: 1, s: 2, t: 3 };
  var D32 = { w: 32, h: 16, q: 8, e: 4, s: 2, t: 1 };   // written length in 32nds
  var TUP = { 3: 2 / 3, 6: 4 / 6 };

  // ---- parser: description -> flat list of items -----------------------------------
  function parse(desc) {
    var tokens = desc.match(/\[|\]|\d+\(|\)|[^\s\[\]\(\)]+/g) || [];
    var items = [], group = null, gid = 0, tups = [], tid = 0, brk = false;
    tokens.forEach(function (t) {
      if (t === '[') { group = ++gid; brk = false; return; }
      if (t === ']') { group = null; return; }
      if (t === '!') { brk = true; return; }
      if (t === '|') { items.push({ kind: 'break' }); return; }
      if (t === 'or') { items.push({ kind: 'or' }); return; }
      var m = /^(\d+)\($/.exec(t);
      if (m) { if (!TUP[m[1]]) throw new Error('tuplet ' + m[1]); tups.push({ id: ++tid, n: +m[1] }); return; }
      if (t === ')') { tups.pop(); return; }
      var tup = tups.length ? tups[tups.length - 1] : null;
      m = /^-([qes])$/.exec(t);
      if (m) { items.push({ kind: 'rest', v: m[1], group: group, tup: tup, len: D32[m[1]] * (tup ? TUP[tup.n] : 1) }); return; }
      m = /^([fd]?)([whqest])([.\/>z~]*)(?::([^,]*)(?:,(.*))?)?$/.exec(t);
      if (!m) throw new Error('bad token ' + t);
      var mods = m[3];
      var it = {
        kind: 'note', grace: m[1], v: m[2], group: group, tup: tup,
        dot: mods.indexOf('.') >= 0, trem: (mods.match(/\//g) || []).length,
        accent: mods.indexOf('>') >= 0, buzz: mods.indexOf('z') >= 0, tie: mods.indexOf('~') >= 0,
        rows: [m[4] || '', m[5] || ''].map(function (s) { return s.replace(/^\+/, '').replace(/_/g, ' '); }),
        join: [m[4] || '', m[5] || ''].map(function (s) { return s.charAt(0) === '+'; }),
        brk: brk && !!group
      };
      it.len = D32[it.v] * (it.dot ? 1.5 : 1) * (tup ? TUP[tup.n] : 1);
      brk = false;
      items.push(it);
    });
    return items;
  }

  // ---- geometry (viewBox units) ---------------------------------------------------
  var G = {
    staffTop: 34, gap: 7,             // five lines, 7 apart; the snare note sits in the third space
    headRx: 4.7, headRy: 3.35, stemDx: 4.3,
    beamH: 3.3, beamStep: 5.6, stemTop: 17,
    graceScale: 0.62, flamLead: 14, dragLead: 22,
    markY: 9,                         // accents and tuplet numbers share this line
    stk: 13.5, stkSmall: 10.5, row1: 16, row2: 31
  };
  G.headY = G.staffTop + G.gap * 1.5;
  G.staffBot = G.staffTop + G.gap * 4;
  var STK_FONT = ' font-family="Helvetica, Arial, \'Liberation Sans\', \'Nimbus Sans\', sans-serif"';
  var SERIF = ' font-family="\'Times New Roman\', Times, \'Liberation Serif\', Georgia, serif"';
  var EM = { R: 0.722, L: 0.556, ' ': 0.278, e: 0.556, t: 0.278, c: 0.5, '.': 0.278 };

  function f(x) { return Math.round(x * 10) / 10; }
  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }

  function textBox(s) {
    // returns {left, width}: left = distance from the text start to the note's x
    if (!s) return null;
    var width = 0, left = null;
    for (var i = 0; i < s.length; i++) {
      var ch = s[i], small = ch === 'r' || ch === 'l', c = small ? ch.toUpperCase() : ch;
      var w = (EM[c] || 0.56) * (small ? G.stkSmall : G.stk);
      if (left === null && (ch === 'R' || ch === 'L')) left = width + w / 2;
      width += w;
    }
    return { left: left === null ? width / 2 : left, width: width };
  }

  // ---- drawing primitives -----------------------------------------------------------
  function ellipsePath(cx, cy, rx, ry, rot) {
    var a = rot * Math.PI / 180, dx = rx * Math.cos(a), dy = rx * Math.sin(a);
    return 'M' + f(cx - dx) + ' ' + f(cy - dy) + 'a' + rx + ' ' + ry + ' ' + rot + ' 1 0 ' + f(2 * dx) + ' ' + f(2 * dy) +
      'a' + rx + ' ' + ry + ' ' + rot + ' 1 0 ' + f(-2 * dx) + ' ' + f(-2 * dy) + 'z';
  }
  function head(x, y, v, s) {
    s = s || 1;
    if (v === 'w') return '<path fill-rule="evenodd" d="' + ellipsePath(x, y, 6.4, 3.9, 0) + ellipsePath(x, y, 3.4, 2.4, 60) + '"/>';
    if (v === 'h') return '<path fill-rule="evenodd" d="' + ellipsePath(x, y, G.headRx, G.headRy, -20) + ellipsePath(x, y, 4.1, 1.75, -26) + '"/>';
    return '<path d="' + ellipsePath(x, y, f(G.headRx * s), f(G.headRy * s), -20) + '"/>';
  }
  function line(x1, y1, x2, y2, w, cls) {
    return '<line' + (cls ? ' class="' + cls + '"' : '') + ' x1="' + f(x1) + '" y1="' + f(y1) + '" x2="' + f(x2) + '" y2="' + f(y2) + '" stroke="currentColor" stroke-width="' + w + '"/>';
  }
  function rect(x, y, w, h, cls) {
    return '<rect' + (cls || '') + ' x="' + f(x) + '" y="' + f(y) + '" width="' + f(w) + '" height="' + f(h) + '"/>';
  }
  function flag(sx, top, i, s) {
    s = s || 1;
    var y = top + i * 6 * s;
    return '<path class="flag" d="M' + f(sx) + ' ' + f(y) + 'c' + f(1 * s) + ' ' + f(5 * s) + ' ' + f(8.5 * s) + ' ' + f(6.5 * s) + ' ' + f(6.6 * s) + ' ' + f(16 * s) +
      'c' + f(0.8 * s) + ' ' + f(-6.2 * s) + ' ' + f(-4.6 * s) + ' ' + f(-8.6 * s) + ' ' + f(-6.6 * s) + ' ' + f(-10.4 * s) + 'z" stroke="none"/>';
  }
  function slash(cx, cy) {
    // tremolo slash: a thick oblique bar across the stem
    return '<path class="trem" d="M' + f(cx - 4.4) + ' ' + f(cy + 2.6) + 'L' + f(cx + 4.4) + ' ' + f(cy - 1.4) + 'L' + f(cx + 4.4) + ' ' + f(cy + 0.4) +
      'L' + f(cx - 4.4) + ' ' + f(cy + 4.4) + 'z" stroke="none"/>';
  }
  function accent(x, y) {
    return '<path class="accent" d="M' + f(x - 4.8) + ' ' + f(y - 3) + 'L' + f(x + 4.8) + ' ' + f(y) + 'L' + f(x - 4.8) + ' ' + f(y + 3) +
      '" fill="none" stroke="currentColor" stroke-width="0.85" stroke-linejoin="miter"/>';
  }
  function restGlyph(v, x, T) {
    var out = '';
    if (v === 'q') {
      return '<path d="M' + f(x - 2) + ' ' + f(T + 3) + 'l5 6.5-4 5 5 6.5c-4-2-7 0-5 4-5-3-3-8 1-7l-5-6.5 4-5z" stroke="none"/>';
    }
    var hooks = v === 's' ? 2 : 1, top = T + 10.5;
    for (var i = 0; i < hooks; i++) {
      var hy = top + i * 7, hx = x - i * 1.7;
      out += '<circle cx="' + f(hx - 2.4) + '" cy="' + f(hy) + '" r="2.1" stroke="none"/>';
      out += '<path d="M' + f(hx - 3.6) + ' ' + f(hy + 0.8) + 'Q' + f(hx + 0.4) + ' ' + f(hy + 3.4) + ' ' + f(hx + 3.2) + ' ' + f(hy - 1.6) + '" fill="none" stroke="currentColor" stroke-width="1.3"/>';
    }
    out += line(x + 3.2, top - 1.6, x - 1.8 - (hooks - 1) * 1.7, top + 12 + (hooks - 1) * 7, 1.3);
    return out;
  }
  function chars(s) {
    // [{c, small, w}] for each character of a sticking string
    return s.split('').map(function (ch) {
      var small = ch === 'r' || ch === 'l', c = small ? ch.toUpperCase() : ch;
      return { c: c, small: small, w: (EM[c] || 0.56) * (small ? G.stkSmall : G.stk) };
    });
  }
  // xs: left edge of each character (from letterX); y: baseline
  function stickText(xs, y, s, row) {
    var out = '';
    chars(s).forEach(function (ch, i) {
      out += '<tspan x="' + f(xs[i]) + '"' + (ch.small ? ' font-size="' + G.stkSmall + '" class="stk-small"' : '') + '>' + esc(ch.c) + '</tspan>';
    });
    return '<text class="stk" data-row="' + row + '" data-text="' + esc(s) + '" x="' + f(xs[0]) + '" y="' + f(y) + '" font-size="' + G.stk + '"' + STK_FONT + '>' + out + '</text>';
  }
  // Character positions for one row of a system. Letters of notes that are joined (a tie, or "+" in the
  // description) form one run, spread evenly from the first note's letters to the last note's, as on the poster.
  function letterX(notes, pos, r) {
    var res = {}, i = 0;
    var start = function (k) { return pos[k] - textBox(notes[k].rows[r]).left; };
    while (i < notes.length) {
      if (!notes[i].rows[r]) { i++; continue; }
      var j = i;
      // a tie joins sticking only when the tied note carries a multi-letter roll string; single letters stay under their own notes
      while (j + 1 < notes.length && notes[j + 1].rows[r] && ((notes[j].tie && chars(notes[j].rows[r]).length > 1) || notes[j + 1].join[r])) j++;
      var cs = [], owner = [];
      for (var k = i; k <= j; k++) chars(notes[k].rows[r]).forEach(function (c) { cs.push(c); owner.push(k); });
      var x0 = start(i), x1 = start(j) + textBox(notes[j].rows[r]).width;
      var natural = cs.reduce(function (a, c) { return a + c.w; }, 0);
      var extra = cs.length > 1 ? Math.max(0, Math.min(7, (x1 - x0 - natural) / (cs.length - 1))) : 0;
      var x = x0;
      cs.forEach(function (c, n) {
        (res[owner[n]] = res[owner[n]] || []).push(x);
        x += c.w + extra;
      });
      i = j + 1;
    }
    return res;
  }

  // ---- layout ---------------------------------------------------------------------------
  function advance(it) {
    if (it.kind === 'or') return 0;
    return 11 + 11 * Math.pow(it.len / 2, 0.6) + (it.dot ? 4 : 0);
  }
  function lead(it) {
    return it.kind === 'note' ? (it.grace === 'f' ? G.flamLead : it.grace === 'd' ? G.dragLead : 0) : 0;
  }
  // place a run of items starting at x0; returns positions and the end x
  function place(items, x0) {
    var x = x0, right = [-1e9, -1e9], pos = [], end = x0, tied = false;
    items.forEach(function (it) {
      if (it.kind === 'or') {
        var ox = Math.max(x + 8, right[0] + 10, right[1] + 10) + 8;
        pos.push(ox); x = ox + 18; end = Math.max(end, x); return;
      }
      var px = x + lead(it);
      if (it.kind === 'note') {
        it.rows.forEach(function (s, r) {
          var b = textBox(s);
          // letters that continue a tied roll run straight on; others keep a word gap
          if (b) px = Math.max(px, right[r] + (tied || it.join[r] ? 0.8 : 3.2) + b.left);
        });
        it.rows.forEach(function (s, r) {
          var b = textBox(s);
          if (b) right[r] = px - b.left + b.width;
        });
      }
      pos.push(px);
      tied = it.kind === 'note' && it.tie;
      x = px + advance(it);
      end = Math.max(end, x, right[0], right[1]);
    });
    return { pos: pos, end: end };
  }

  function chunksOf(items) {
    var chunks = [], cur = [];
    items.forEach(function (it) {
      if (it.kind === 'break') { if (cur.length) chunks.push(cur); cur = []; return; }
      cur.push(it);
      if (it.kind === 'or') { chunks.push(cur); cur = []; }
    });
    if (cur.length) chunks.push(cur);
    return chunks;
  }

  var START = 16, END = 14;
  function renderSystem(sys, top, first, last) {
    var items = [].concat.apply([], sys), T = top + G.staffTop, HY = top + G.headY;
    var p = place(items, START + 14), out = [], groups = {}, tups = {}, notes = [];
    var stemTop = top + G.stemTop, markY = top + G.markY;
    var nIdx = [], nPos = [];
    items.forEach(function (it, i) { if (it.kind === 'note') { nIdx.push(it); nPos.push(p.pos[i]); } });
    var LX = [letterX(nIdx, nPos, 0), letterX(nIdx, nPos, 1)];
    items.forEach(function (it, i) {
      var x = p.pos[i];
      it._x = x;
      if (it.kind === 'or') {
        out.push('<text class="or" x="' + f(x) + '" y="' + f(T - 4) + '" font-size="13" font-style="italic" text-anchor="middle"' + STK_FONT + '>or</text>');
        return;
      }
      if (it.tup) (tups[it.tup.id] = tups[it.tup.id] || { n: it.tup.n, xs: [] }).xs.push(it.kind === 'note' && it.v !== 'w' ? x + G.stemDx : x);
      if (it.kind === 'rest') {
        out.push('<g class="rest" data-v="' + it.v + '">' + restGlyph(it.v, x, T) + '</g>');
        return;
      }
      notes.push(it);
      var sx = x + G.stemDx, g = '<g class="note" data-v="' + it.v + '" data-dot="' + (it.dot ? 1 : 0) + '" data-trem="' + it.trem +
        '" data-accent="' + (it.accent ? 1 : 0) + '" data-grace="' + it.grace + '" data-tie="' + (it.tie ? 1 : 0) + '">';
      g += head(x, HY, it.v);
      var grouped = it.group && items.filter(function (o) { return o.group === it.group && o.kind === 'note'; }).length > 1;
      if (it.v !== 'w') {
        g += line(sx, HY - 1, sx, stemTop + (grouped ? 0.3 : 0), 1.1);
        if (!grouped) for (var k = 0; k < BEAMS[it.v]; k++) g += flag(sx, stemTop, k);
      }
      if (it.dot) g += '<circle class="dot" cx="' + f(x + 9) + '" cy="' + f(HY + 0.5) + '" r="1.5" stroke="none"/>';
      for (var t = 0; t < it.trem; t++) {
        g += it.v === 'w' ? slash(x, HY - 13 - t * 4.4) : slash(sx, HY - 9.6 - t * 4.4);
      }
      if (it.buzz) {
        // italic Z (buzz roll), drawn as a path so it looks the same in every browser
        var zx = x + 1, zy = T - 3.5;
        g += '<path class="buzz" d="M' + f(zx - 2.6) + ' ' + f(zy - 10.5) + 'L' + f(zx + 5) + ' ' + f(zy - 10.5) + 'L' + f(zx - 4.6) + ' ' + f(zy) + 'L' + f(zx + 3.2) + ' ' + f(zy) +
          '" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round" stroke-linecap="round"/>';
      }
      if (it.accent) g += accent(sx - 1, markY);
      // grace notes
      var gs = G.graceScale, gTop = HY - 16.5;
      if (it.grace === 'f') {
        var gx = x - 12.5, gsx = gx + G.stemDx * gs;
        g += '<g class="grace" data-n="1">' + head(gx, HY + 0.6, 'q', gs) + line(gsx, HY - 0.5, gsx, gTop, 0.9) + flag(gsx, gTop, 0, gs) +
          line(gsx - 3.6, HY - 4.6, gsx + 4.4, HY - 11.6, 0.8) + '</g>';
      } else if (it.grace === 'd') {
        var g1 = x - 20.5, g2 = x - 13, s1 = g1 + G.stemDx * gs, s2 = g2 + G.stemDx * gs;
        g += '<g class="grace" data-n="2">' + head(g1, HY + 0.6, 'q', gs) + head(g2, HY + 0.6, 'q', gs) +
          line(s1, HY - 0.5, s1, gTop, 0.9) + line(s2, HY - 0.5, s2, gTop, 0.9) +
          rect(s1 - 0.45, gTop, s2 - s1 + 0.9, 1.7) + rect(s1 - 0.45, gTop + 3.2, s2 - s1 + 0.9, 1.7) + '</g>';
      }
      var ni = notes.length - 1;
      [0, 1].forEach(function (r) {
        if (it.rows[r]) g += stickText(LX[r][ni], top + G.staffBot + (r ? G.row2 : G.row1), it.rows[r], r + 1);
      });
      out.push(g + '</g>');
      it._sx = sx;
      if (it.group) (groups[it.group] = groups[it.group] || []).push(it);
    });
    // ties: a curve under the note heads to the next note
    notes.forEach(function (it, i) {
      var nx = notes[i + 1];
      if (!it.tie || !nx) return;
      var x1 = it._x + (it.dot ? 6 : 3), x2 = nx._x - 3, y = HY + 5, mid = (x1 + x2) / 2, sag = Math.min(6, 2.5 + (x2 - x1) / 30);
      out.push('<path class="tie" d="M' + f(x1) + ' ' + f(y) + 'Q' + f(mid) + ' ' + f(y + sag + 1.4) + ' ' + f(x2) + ' ' + f(y) +
        'Q' + f(mid) + ' ' + f(y + sag) + ' ' + f(x1) + ' ' + f(y) + 'z" stroke="currentColor" stroke-width="0.5"/>');
    });
    // beams
    Object.keys(groups).forEach(function (k) {
      var ps = groups[k];
      if (ps.length < 2) return;
      var lv = ps.map(function (p) { return BEAMS[p.v]; });
      var maxL = Math.max.apply(null, lv);
      for (var level = 0; level < maxL; level++) {
        var y = stemTop + level * G.beamStep, i = 0;
        var joined = function (a) { return lv[a] > level && lv[a + 1] > level && !(level > 0 && ps[a + 1].brk); };
        while (i < ps.length) {
          if (lv[i] <= level) { i++; continue; }
          var j = i;
          while (j + 1 < ps.length && joined(j)) j++;
          var cls = ' class="beam" data-level="' + (level + 1) + '"';
          if (j > i) out.push(rect(ps[i]._sx - 0.55, y, ps[j]._sx - ps[i]._sx + 1.1, G.beamH, cls));
          else {
            var stub = 7, right = (i === 0) || (level > 0 && ps[i].brk);
            out.push(rect(right ? ps[i]._sx - 0.55 : ps[i]._sx - stub, y, stub + 0.55, G.beamH, cls + ' data-stub="' + (right ? 'r' : 'l') + '"'));
          }
          i = j + 1;
        }
      }
    });
    // tuplet numbers
    Object.keys(tups).forEach(function (k) {
      var t = tups[k], cx = (t.xs[0] + t.xs[t.xs.length - 1]) / 2;
      out.push('<text class="tuplet" x="' + f(cx) + '" y="' + f(markY + 4) + '" font-size="11.5" text-anchor="middle"' + SERIF + '>' + t.n + '</text>');
    });
    // staff, bar lines
    var xe = p.end + END, s = '';
    for (var l = 0; l < 5; l++) s += line(first ? START - 6 : START, T + l * G.gap, last ? xe : xe - 4, T + l * G.gap, 0.65, l ? '' : 'staff');
    if (first) s += rect(START - 6, T, 3.2, G.gap * 4, ' class="barline thick"') + line(START + 0.4, T, START + 0.4, T + G.gap * 4, 1, 'barline');
    else s += line(START, T, START, T + G.gap * 4, 1, 'barline');
    if (last) s += line(xe - 5.8, T, xe - 5.8, T + G.gap * 4, 1, 'barline') + rect(xe - 3.2, T, 3.2, G.gap * 4, ' class="barline thick"');
    return { svg: '<g class="system">' + s + out.join('') + '</g>', width: xe + 4 };
  }

  function build(n) {
    var d = DATA[n - 1];
    if (!d) return null;
    var items = parse(d[2]);
    var notes = items.filter(function (it) { return it.kind === 'note'; });
    var row = function (r) {
      return notes.map(function (it) { return it.rows[r] ? it.rows[r] + (r === 0 && it.accent ? '>' : '') : ''; }).filter(Boolean).join(' ');
    };
    return {
      n: n, name: d[0], family: FAM[d[1]][0], group: FAM[d[1]][1], items: items,
      sticking: row(0), sticking2: row(1), versions: items.filter(function (it) { return it.kind === 'or'; }).length + 1
    };
  }

  function systemHeight(r) {
    return G.staffBot + (r.sticking2 ? G.row2 : G.row1) + 7;
  }

  function svg(n, opts) {
    opts = opts || {};
    var r = build(n);
    if (!r) return '';
    var maxW = opts.maxWidth || 370;
    var chunks = chunksOf(r.items);
    // pack chunks into systems: add a chunk while the system still fits maxWidth
    var systems = [], cur = [];
    chunks.forEach(function (c) {
      var trial = cur.concat([c]);
      if (cur.length && place([].concat.apply([], trial), START + 14).end + END + 4 > maxW) { systems.push(cur); cur = [c]; }
      else cur = trial;
    });
    systems.push(cur);
    var sysH = systemHeight(r), body = [], W = 0;
    systems.forEach(function (sys, si) {
      var rs = renderSystem(sys, si * sysH, si === 0, si === systems.length - 1);
      W = Math.max(W, rs.width);
      body.push(rs.svg);
    });
    var H = systems.length * sysH;
    var label = opts.label || (r.name + '. Sticking: ' + r.sticking.replace(/>/g, ' accent') +
      (r.sticking2 ? '. Second sticking: ' + r.sticking2 : '') + (r.versions > 1 ? '. Two versions, joined by "or".' : ''));
    return '<svg xmlns="http://www.w3.org/2000/svg" class="rudiment-svg" viewBox="0 0 ' + f(W) + ' ' + f(H) + '" width="100%"' +
      ' style="max-width:' + Math.round(W * 1.6) + 'px;height:auto;display:block" role="img" aria-label="' + esc(label) + '"' +
      ' data-rudiment="' + r.n + '" data-systems="' + systems.length + '" fill="currentColor"' +
      ' font-family="system-ui, -apple-system, \'Segoe UI\', Helvetica, Arial, sans-serif">' +
      '<title>' + esc(label) + '</title>' +
      body.join('') + '</svg>';
  }

  var list = DATA.map(function (d, i) {
    return { n: i + 1, name: d[0], family: FAM[d[1]][0], group: FAM[d[1]][1] };
  });

  window.Rudiments = {
    list: list,
    svg: svg,
    // for tests and the preview page
    describe: function (n) { var d = DATA[n - 1]; return d ? d[2] : null; },
    parse: function (n) { var r = build(n); if (r) r.items = r.items.map(function (it) { var c = {}; for (var k in it) if (k[0] !== '_' && k !== 'tup') c[k] = it[k]; if (it.tup) c.tuplet = it.tup.n; return c; }); return r; },
    credit: 'The 40 International Drum Rudiments are the standard list published by the Percussive Arts Society. Notation follows the PAS 40 International Drum Rudiments as shown on the Vic Firth Rudiments poster, redrawn for this app.'
  };
})();
