/**
 * GovCon Intel — Self-Hosted Analytics Tracker
 *
 * Zero-dependency, cookie-free, GDPR-friendly visitor tracking.
 * All data stored in localStorage. View stats at /stats.html.
 *
 * Tracks: page views, CTA clicks, referrers, time on page.
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'gc_analytics';
  var SESSION_KEY = 'gc_session';
  var startTime = Date.now();

  // ── Storage helpers ──

  function getStore() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || createStore();
    } catch (e) {
      return createStore();
    }
  }

  function createStore() {
    return { views: [], clicks: [], sessions: 0 };
  }

  function save(store) {
    try {
      // Keep last 90 days of data, cap at 5000 events to avoid quota issues
      var cutoff = Date.now() - 90 * 24 * 60 * 60 * 1000;
      store.views = (store.views || []).filter(function (v) { return v.ts > cutoff; }).slice(-5000);
      store.clicks = (store.clicks || []).filter(function (c) { return c.ts > cutoff; }).slice(-2000);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
    } catch (e) {
      // localStorage full — silently fail
    }
  }

  // ── Session tracking ──

  function trackSession() {
    var store = getStore();
    var session = sessionStorage.getItem(SESSION_KEY);
    if (!session) {
      store.sessions = (store.sessions || 0) + 1;
      sessionStorage.setItem(SESSION_KEY, '1');
      save(store);
    }
  }

  // ── Page view ──

  function trackPageView() {
    var store = getStore();
    store.views.push({
      ts: Date.now(),
      page: location.pathname,
      title: document.title,
      ref: document.referrer || '(direct)',
      ua: navigator.userAgent.substring(0, 120)
    });
    save(store);
  }

  // ── CTA clicks ──

  function trackClicks() {
    document.addEventListener('click', function (e) {
      var link = e.target.closest('a[href*="govconintelligence.substack.com"]');
      if (!link) return;
      var store = getStore();
      store.clicks.push({
        ts: Date.now(),
        page: location.pathname,
        text: (link.textContent || '').trim().substring(0, 80),
        href: link.href
      });
      save(store);
    });
  }

  // ── Time on page (logged as a view update) ──

  function trackTimeOnPage() {
    function flush() {
      var seconds = Math.round((Date.now() - startTime) / 1000);
      if (seconds < 2) return; // skip bounces under 2s
      var store = getStore();
      // Append a duration record
      store.views.push({
        ts: Date.now(),
        page: location.pathname,
        type: 'duration',
        seconds: seconds
      });
      save(store);
    }
    document.addEventListener('visibilitychange', function () {
      if (document.visibilityState === 'hidden') flush();
    });
    window.addEventListener('pagehide', flush);
  }

  // ── Init ──

  trackSession();
  trackPageView();
  trackClicks();
  trackTimeOnPage();
})();
