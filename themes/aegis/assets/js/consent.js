(function () {
  "use strict";

  var STORAGE_KEY = "amid_consent";

  function readConsent() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function writeConsent(status) {
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ analytics: status, ts: new Date().toISOString(), v: 1 })
      );
    } catch (e) {}
  }

  // Best-effort cleanup so withdrawing consent actually removes GA's cookies
  // immediately, rather than just stopping future writes.
  function expireGaCookies() {
    try {
      var host = location.hostname;
      var domains = ["", "; domain=" + host, "; domain=." + host];
      document.cookie.split(";").forEach(function (c) {
        var name = c.split("=")[0].trim();
        if (/^_ga/.test(name) || /^_gid$/.test(name) || /^_gat/.test(name)) {
          domains.forEach(function (d) {
            document.cookie = name + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/" + d;
          });
        }
      });
    } catch (e) {}
  }

  function loadGa() {
    var el = document.getElementById("amid-ga");
    var id = el && el.getAttribute("data-ga-id");
    if (!id || window.__amidGaLoaded) return;
    window.__amidGaLoaded = true;

    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { dataLayer.push(arguments); };

    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(id);
    document.head.appendChild(s);

    gtag("js", new Date());
    gtag("config", id);
  }

  function revokeGa() {
    if (window.gtag) {
      gtag("consent", "update", { analytics_storage: "denied" });
    }
    expireGaCookies();
  }

  function setBannerVisible(visible) {
    var b = document.getElementById("amid-cookie-banner");
    if (b) b.hidden = !visible;
  }

  function applyConsent(status) {
    writeConsent(status);
    if (status === "granted") {
      loadGa();
    } else {
      revokeGa();
    }
    setBannerVisible(false);
  }

  document.addEventListener("click", function (e) {
    var t = e.target;
    while (t && t.nodeType === 1 && !t.hasAttribute("data-cookie-action")) t = t.parentNode;
    if (!t || t.nodeType !== 1) return;
    var action = t.getAttribute("data-cookie-action");
    if (action === "accept" || action === "reject") {
      applyConsent(action === "accept" ? "granted" : "denied");
    } else if (action === "manage") {
      setBannerVisible(true);
    }
  }, true);

  var existing = readConsent();
  if (existing && existing.analytics === "granted") {
    loadGa();
  } else if (!existing) {
    setBannerVisible(true);
  }
  // existing && existing.analytics === "denied": banner stays hidden, GA stays unloaded.
})();
