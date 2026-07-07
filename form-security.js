(function () {
  var configuredSiteKey = "";
  var turnstileRequired = false;
  var formNonce = "";
  var waitlistSendAck = false;
  var widgets = {};

  function apiBase() {
    var meta = document.querySelector('meta[name="contact-api-base"]');
    var v = meta && meta.getAttribute("content");
    v = (v || "").trim().replace(/\/$/, "");
    if (v) return v;
    if (window.location && window.location.origin && window.location.origin !== "null") {
      return window.location.origin;
    }
    return "";
  }

  function turnstileSiteKey() {
    if (configuredSiteKey) return configuredSiteKey;
    var meta = document.querySelector('meta[name="turnstile-site-key"]');
    return meta && meta.getAttribute("content") ? meta.getAttribute("content").trim() : "";
  }

  function setSubmitEnabled(enabled) {
    document
      .querySelectorAll("#contact-form [type=submit], #waitlist-form [type=submit]")
      .forEach(function (btn) {
        btn.disabled = !enabled;
      });
  }

  function waitForTurnstile(maxMs) {
    return new Promise(function (resolve, reject) {
      if (window.turnstile) {
        resolve();
        return;
      }
      var start = Date.now();
      var timer = setInterval(function () {
        if (window.turnstile) {
          clearInterval(timer);
          resolve();
        } else if (Date.now() - start > maxMs) {
          clearInterval(timer);
          reject(new Error("Human verification failed to load. Refresh the page and try again."));
        }
      }, 50);
    });
  }

  function onTurnstileReady() {
    document.dispatchEvent(new CustomEvent("profitru-turnstile-ready"));
    setSubmitEnabled(true);
  }

  function onTurnstileInvalid() {
    setSubmitEnabled(false);
  }

  function turnstileAction(containerId) {
    if (containerId === "contact-turnstile") return "contact";
    if (containerId === "waitlist-turnstile") return "waitlist";
    return "";
  }

  function mountTurnstile(containerId) {
    var key = turnstileSiteKey();
    var container = document.getElementById(containerId);
    if (!key || !container || !window.turnstile || widgets[containerId]) return false;
    var action = turnstileAction(containerId);
    widgets[containerId] = window.turnstile.render(container, {
      sitekey: key,
      theme: "auto",
      appearance: "always",
      action: action,
      callback: onTurnstileReady,
      "expired-callback": onTurnstileInvalid,
      "error-callback": onTurnstileInvalid,
    });
    return true;
  }

  function applyConfig(cfg) {
    if (!cfg) return;
    if (cfg.turnstile_site_key) configuredSiteKey = cfg.turnstile_site_key.trim();
    turnstileRequired = !!cfg.turnstile_required;
    if (cfg.form_nonce) formNonce = cfg.form_nonce;
    waitlistSendAck = !!cfg.waitlist_send_ack;
  }

  function loadConfig() {
    var base = apiBase();
    if (!base) return Promise.resolve();
    return fetch(base + "/api/form-config", {
      headers: { Accept: "application/json" },
      credentials: "same-origin",
    })
      .then(function (res) {
        return res.ok ? res.json() : null;
      })
      .then(applyConfig)
      .catch(function () {
        /* keep defaults */
      });
  }

  function initTurnstileWidgets() {
    if (!turnstileSiteKey()) return Promise.resolve();
    var hasWidget =
      !!document.getElementById("contact-turnstile") ||
      !!document.getElementById("waitlist-turnstile");
    if (!hasWidget) return Promise.resolve();
    setSubmitEnabled(false);
    return waitForTurnstile(15000)
      .then(function () {
        mountTurnstile("contact-turnstile");
        mountTurnstile("waitlist-turnstile");
        if (window.ProfitruFormSecurity.turnstileToken()) {
          setSubmitEnabled(true);
        }
      })
      .catch(function (err) {
        var statusEl =
          document.getElementById("contact-form-status") ||
          document.getElementById("waitlist-form-status");
        if (statusEl) {
          statusEl.hidden = false;
          statusEl.textContent = err && err.message ? err.message : "Human verification failed to load.";
          statusEl.className = "contact-form-status contact-form-status--error";
        }
        setSubmitEnabled(false);
      });
  }

  window.ProfitruFormSecurity = {
    formStartedAt: Date.now(),
    apiBase: apiBase,
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
        form_nonce: formNonce,
      };
    },
    refreshSecurity: function () {
      return loadConfig().then(function () {
        window.ProfitruFormSecurity.resetTurnstile();
      });
    },
    waitlistSendAckEnabled: function () {
      return waitlistSendAck;
    },
    ensureReady: function () {
      if (!formNonce) {
        return Promise.reject(new Error("Form security is still loading. Wait a moment and try again."));
      }
      if (!window.ProfitruFormSecurity.isTurnstileRequired()) return Promise.resolve();
      if (window.ProfitruFormSecurity.turnstileToken()) return Promise.resolve();
      return new Promise(function (resolve, reject) {
        var timer = setTimeout(function () {
          reject(new Error("Complete the human verification check before submitting."));
        }, 15000);
        function done() {
          clearTimeout(timer);
          if (window.ProfitruFormSecurity.turnstileToken()) resolve();
          else reject(new Error("Complete the human verification check before submitting."));
        }
        document.addEventListener("profitru-turnstile-ready", done, { once: true });
      });
    },
    resetTurnstile: function () {
      if (widgets["contact-turnstile"] && window.turnstile) {
        window.turnstile.reset(widgets["contact-turnstile"]);
      }
      if (widgets["waitlist-turnstile"] && window.turnstile) {
        window.turnstile.reset(widgets["waitlist-turnstile"]);
      }
      if (window.ProfitruFormSecurity.isTurnstileRequired()) {
        setSubmitEnabled(false);
      }
    },
  };

  document.addEventListener("DOMContentLoaded", function () {
    loadConfig().finally(initTurnstileWidgets);
  });
})();
