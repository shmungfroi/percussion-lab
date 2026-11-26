/* TEST STUB ONLY. Not the real notation.
 * Stands in for notation.js so tests/run_tests.py can check the app's side of the
 * interface (window.Rudiments.list / .svg) when the real file is absent or when the
 * suite is run with --stub. Never copy this over notation.js. */
(function () {
  'use strict';
  var list = [];
  for (var n = 1; n <= 40; n++) list.push({ n: n, name: 'Stub rudiment ' + n, family: 'Stub' });
  window.Rudiments = {
    stub: true,
    list: list,
    svg: function (n) {
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 80" width="100%" style="max-width:640px;height:auto;display:block" role="img" aria-label="Stub notation ' + n + '">' +
        '<line x1="6" y1="40" x2="394" y2="40" stroke="currentColor" stroke-width="1.1"/>' +
        '<text x="200" y="30" text-anchor="middle" fill="currentColor" font-size="12">stub ' + n + '</text></svg>';
    }
  };
})();
