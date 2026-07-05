(function () {
  var configuredSiteKey = "";
  var turnstileRequired = false;
  var widgets = {};

  function apiBase() {
    var meta = document.querySelector('meta[name="contact-api-base"]');
    var v = meta && meta.getAttribute("content");
    return (v || "").replace(/\/$/, "");
  }

  function turnstileSiteKey() {
    if (configuredSiteKey) return configuredSiteKey;
    var meta = document.querySelector('meta[name="turnstile-site-key"]');
    return meta && meta.getAttribute("content") ? meta.getAttribute("content").trim() : "";
  }

  function mountTurnstile(containerId) {
    var key = turnstileSiteKey();
    var container = document.getElementById(containerId);
    if (!key || !container || !window.turnstile || widgets[containerId]) return;
    widgets[containerId] = window.turnstile.render(container, {
      sitekey: key,
      theme: "auto",
      callback: function () {
        document.dispatchEvent(new CustomEvent("profitru-turnstile-ready"));
      },
    });
  }

  function loadConfig() {
    var base = apiBase();
    if (!base) return Promise.resolve();
    return fetch(base + "/api/form-config", { headers: { Accept: "application/json" } })
      .then(function (res) {
        return res.ok ? res.json() : null;
      })
      .then(function (cfg) {
        if (!cfg) return;
        if (cfg.turnstile_site_key) configuredSiteKey = cfg.turnstile_site_key.trim();
        turnstileRequired = !!cfg.turnstile_required;
      })
      .catch(function () {
        /* keep defaults */
      });
  }

  window.ProfitruFormSecurity = {
    formStartedAt: Date.now(),
    turnstileSiteKey: turnstileSiteKey,
    isTurnstileRequired: function () {
      return turnstileRequired || !!turnstileSiteKey();
    },
    mountTurnstile: mountTurnstile,
    turnstileToken: function () {
      var input = document.querySelector('input[name="cf-turnstile-response"]');
      return input ? input.value : "";
    },
    extraPayload: function () {
      return {
        form_started_at: window.ProfitruFormSecurity.formStartedAt,
        turnstile_token: window.ProfitruFormSecurity.turnstileToken(),
      };
    },
    ensureReady: function () {
      if (!window.ProfitruFormSecurity.isTurnstileRequired()) return Promise.resolve();
      if (window.ProfitruFormSecurity.turnstileToken()) return Promise.resolve();
      return new Promise(function (resolve, reject) {
        var timer = setTimeout(function () {
          reject(new Error("Security check timed out. Refresh and try again."));
        }, 15000);
        function done() {
          clearTimeout(timer);
          if (window.ProfitruFormSecurity.turnstileToken()) resolve();
          else reject(new Error("Complete the security check before submitting."));
        }
        document.addEventListener("profitru-turnstile-ready", done, { once: true });
      });
    },
  };

  document.addEventListener("DOMContentLoaded", function () {
    loadConfig().finally(function () {
      if (turnstileSiteKey()) {
        mountTurnstile("contact-turnstile");
        mountTurnstile("waitlist-turnstile");
      }
    });
  });
})();
