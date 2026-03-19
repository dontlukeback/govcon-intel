/**
 * GovCon Intel — GA4 Analytics Wrapper
 *
 * Lightweight Google Analytics integration that:
 * - Tracks page views automatically
 * - Tracks CTA clicks (links to govconintelligence.substack.com)
 * - Tracks time on page
 * - Logs to console when no GA4 ID is set
 * - Supports Measurement Protocol (cookieless) mode
 *
 * Usage: Set window.GA4_ID = 'G-XXXXXXXXXX' before this script loads,
 *        or leave unset to run in console-only mode.
 */
(function () {
  'use strict';

  var GA_ID = window.GA4_ID || null;
  var DEBUG = !GA_ID;
  var startTime = Date.now();

  // ── Helpers ──

  function log(action, data) {
    if (DEBUG) {
      console.log('[GovCon Analytics]', action, data || '');
    }
  }

  // ── GA4 gtag loader ──

  function loadGA4() {
    if (!GA_ID) return;
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', GA_ID, { send_page_view: true });
  }

  function sendEvent(name, params) {
    log(name, params);
    if (window.gtag) {
      window.gtag('event', name, params);
    }
  }

  // ── Measurement Protocol fallback (cookieless) ──

  function sendMeasurementProtocol(name, params) {
    if (!GA_ID || !window.GA4_SECRET) return;
    var clientId = localStorage.getItem('gc_cid');
    if (!clientId) {
      clientId = Math.random().toString(36).substr(2) + Date.now().toString(36);
      localStorage.setItem('gc_cid', clientId);
    }
    var url = 'https://www.google-analytics.com/mp/collect?measurement_id=' + GA_ID + '&api_secret=' + window.GA4_SECRET;
    var body = {
      client_id: clientId,
      events: [{ name: name, params: params }]
    };
    navigator.sendBeacon(url, JSON.stringify(body));
  }

  // ── Track page view ──

  function trackPageView() {
    var data = {
      page: location.pathname,
      title: document.title,
      referrer: document.referrer || '(direct)'
    };
    sendEvent('page_view', data);
    sendMeasurementProtocol('page_view', data);
  }

  // ── Track CTA clicks ──

  function trackCTAClicks() {
    document.addEventListener('click', function (e) {
      var link = e.target.closest('a[href*="govconintelligence.substack.com"]');
      if (!link) return;
      var data = {
        link_url: link.href,
        link_text: (link.textContent || '').trim().substring(0, 100),
        page: location.pathname
      };
      sendEvent('cta_click', data);
      sendMeasurementProtocol('cta_click', data);
    });
  }

  // ── Track time on page ──

  function trackTimeOnPage() {
    function send() {
      var seconds = Math.round((Date.now() - startTime) / 1000);
      var data = { seconds: seconds, page: location.pathname };
      sendEvent('time_on_page', data);
      sendMeasurementProtocol('time_on_page', data);
    }
    // Send on visibility change (tab close/switch) and before unload
    document.addEventListener('visibilitychange', function () {
      if (document.visibilityState === 'hidden') send();
    });
    window.addEventListener('pagehide', send);
  }

  // ── Init ──

  loadGA4();
  trackPageView();
  trackCTAClicks();
  trackTimeOnPage();

  log('initialized', GA_ID ? '(GA4: ' + GA_ID + ')' : '(console-only mode — set window.GA4_ID to activate)');
})();
