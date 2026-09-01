/* Client behaviour: theme toggle, search (suggestions + results page),
   sortable tables and the random-page jump. No dependencies. */
(function () {
  'use strict';

  var BASE = window.WIKI_BASE || './';
  var root = document.documentElement;

  // ---------------------------------------------------------------- theme --
  var toggle = document.getElementById('theme-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var dark = root.classList.toggle('wgl-theme-dark');
      try { localStorage.setItem('wgl-theme', dark ? 'dark' : 'light'); } catch (e) { /* private mode */ }
    });
  }

  // --------------------------------------------------------------- search --
  var indexPromise = null;
  function loadIndex() {
    if (!indexPromise) {
      indexPromise = new Promise(function (resolve) {
        if (window.__WIKI_SEARCH__) { resolve(window.__WIKI_SEARCH__); return; }
        var el = document.createElement('script');
        el.src = BASE + 'assets/search-index.js';
        el.onload = function () { resolve(window.__WIKI_SEARCH__ || { docs: [] }); };
        el.onerror = function () { resolve({ docs: [] }); };
        document.head.appendChild(el);
      });
    }
    return indexPromise;
  }

  function tokenize(q) {
    return q.toLowerCase().split(/[^a-z0-9]+/).filter(Boolean);
  }

  /** Title matches beat heading matches beat body matches. */
  function score(doc, terms, raw) {
    var title = doc.t.toLowerCase();
    var s = 0;
    if (title === raw) s += 1000;
    if (title.indexOf(raw) === 0) s += 300;
    if (title.indexOf(raw) !== -1) s += 150;
    for (var i = 0; i < terms.length; i++) {
      var t = terms[i];
      if (title.indexOf(t) !== -1) s += 60;
      if (doc.b.indexOf(t) !== -1) s += 10;
      for (var h = 0; h < (doc.h || []).length; h++) {
        if (doc.h[h].text.toLowerCase().indexOf(t) !== -1) { s += 25; break; }
      }
    }
    if (s > 0 && doc.s) s -= 20;            // rank written pages above stubs
    return s;
  }

  function search(docs, query, limit) {
    var raw = query.trim().toLowerCase();
    if (!raw) return [];
    var terms = tokenize(raw);
    if (!terms.length) return [];
    var hits = [];
    for (var i = 0; i < docs.length; i++) {
      var s = score(docs[i], terms, raw);
      if (s > 0) hits.push({ doc: docs[i], score: s });
    }
    hits.sort(function (a, b) { return b.score - a.score || a.doc.t.localeCompare(b.doc.t); });
    return limit ? hits.slice(0, limit) : hits;
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function href(url) {
    return BASE + url.replace(/^\//, '');
  }

  /** A snippet centred on the first matching term, with the term marked. */
  function snippet(doc, terms) {
    var body = doc.b || '';
    var at = -1;
    for (var i = 0; i < terms.length && at === -1; i++) at = body.indexOf(terms[i]);
    if (at === -1) return esc(doc.d || body.slice(0, 180));
    var start = Math.max(0, at - 70);
    var text = (start > 0 ? '…' : '') + body.slice(start, start + 200) + '…';
    var out = esc(text);
    terms.forEach(function (t) {
      out = out.replace(new RegExp('(' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi'),
        '<mark>$1</mark>');
    });
    return out;
  }

  var input = document.getElementById('searchInput');
  var suggest = document.getElementById('searchSuggest');

  if (input && suggest) {
    var active = -1;
    var current = [];

    var render = function (hits, terms) {
      current = hits;
      active = -1;
      if (!hits.length) { suggest.hidden = true; suggest.innerHTML = ''; return; }
      suggest.innerHTML = '<ol>' + hits.map(function (h) {
        return '<li><a href="' + href(h.doc.u) + '">' +
          '<span class="suggest-title">' + esc(h.doc.t) + '</span>' +
          (h.doc.n ? '<span class="suggest-ns">' + esc(h.doc.n) + '</span>' : '') +
          '</a></li>';
      }).join('') + '</ol>';
      suggest.hidden = false;
    };

    var run = function () {
      var q = input.value;
      if (q.trim().length < 2) { suggest.hidden = true; return; }
      loadIndex().then(function (idx) {
        render(search(idx.docs, q, 8), tokenize(q));
      });
    };

    input.addEventListener('input', run);
    input.addEventListener('focus', run);
    document.addEventListener('click', function (e) {
      if (!suggest.contains(e.target) && e.target !== input) suggest.hidden = true;
    });
    input.addEventListener('keydown', function (e) {
      var items = suggest.querySelectorAll('li');
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        if (!items.length) return;
        e.preventDefault();
        if (active >= 0) items[active].classList.remove('is-active');
        active = e.key === 'ArrowDown'
          ? (active + 1) % items.length
          : (active - 1 + items.length) % items.length;
        items[active].classList.add('is-active');
      } else if (e.key === 'Enter') {
        if (active >= 0 && current[active]) {
          e.preventDefault();
          window.location.href = href(current[active].doc.u);
        }
      } else if (e.key === 'Escape') {
        suggest.hidden = true;
        input.blur();
      }
    });

    // "/" focuses search, the way the real wiki does.
    document.addEventListener('keydown', function (e) {
      if (e.key === '/' && document.activeElement !== input &&
          !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)) {
        e.preventDefault();
        input.focus();
        input.select();
      }
    });
  }

  // ------------------------------------------------- search results page --
  var resultsEl = document.getElementById('search-results');
  if (resultsEl) {
    var status = document.querySelector('#search-page .search-status');
    var q = new URLSearchParams(window.location.search).get('q') || '';
    if (input) input.value = q;
    if (!q.trim()) {
      if (status) status.textContent = 'Type a query in the search box above.';
    } else {
      loadIndex().then(function (idx) {
        var terms = tokenize(q);
        var hits = search(idx.docs, q, 100);
        if (status) {
          status.textContent = hits.length
            ? hits.length + ' result' + (hits.length === 1 ? '' : 's') + ' for “' + q + '”'
            : 'No results for “' + q + '”.';
        }
        resultsEl.innerHTML = hits.map(function (h) {
          return '<li><div class="result-title"><a href="' + href(h.doc.u) + '">' +
            esc(h.doc.t) + '</a></div>' +
            '<div class="result-url">' + esc(h.doc.u) + '</div>' +
            '<div class="result-snippet">' + snippet(h.doc, terms) + '</div></li>';
        }).join('');
      });
    }
  }

  // --------------------------------------------------------- random page --
  if (/\/wiki\/random\/?$/.test(window.location.pathname)) {
    loadIndex().then(function (idx) {
      var pool = idx.docs.filter(function (d) { return d.n !== 'wiki'; });
      if (!pool.length) return;
      window.location.replace(href(pool[Math.floor(Math.random() * pool.length)].u));
    });
  }

  // ------------------------------------------------------ sortable tables --
  function cellValue(row, i) {
    var cell = row.cells[i];
    var text = cell ? cell.textContent.trim() : '';
    var num = parseFloat(text.replace(/,/g, ''));
    return isNaN(num) || !/^[-+]?[\d.,]+$/.test(text) ? text.toLowerCase() : num;
  }

  Array.prototype.forEach.call(document.querySelectorAll('table.sortable'), function (table) {
    var head = table.tHead;
    if (!head) return;
    Array.prototype.forEach.call(head.rows[0].cells, function (th, i) {
      th.addEventListener('click', function () {
        var body = table.tBodies[0];
        var asc = !th.classList.contains('sort-asc');
        Array.prototype.forEach.call(head.rows[0].cells, function (o) {
          o.classList.remove('sort-asc', 'sort-desc');
        });
        th.classList.add(asc ? 'sort-asc' : 'sort-desc');
        var rows = Array.prototype.slice.call(body.rows);
        rows.sort(function (a, b) {
          var x = cellValue(a, i), y = cellValue(b, i);
          if (x < y) return asc ? -1 : 1;
          if (x > y) return asc ? 1 : -1;
          return 0;
        });
        rows.forEach(function (r) { body.appendChild(r); });
      });
    });
  });

  // ------------------------------------------------- wide table scrolling --
  Array.prototype.forEach.call(document.querySelectorAll('.mw-parser-output table'), function (t) {
    if (t.parentNode.classList.contains('table-scroll')) return;
    var wrap = document.createElement('div');
    wrap.className = 'table-scroll';
    t.parentNode.insertBefore(wrap, t);
    wrap.appendChild(t);
  });
}());
