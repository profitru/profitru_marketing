(function () {
  function turnstileSiteKey() {
    var meta = document.querySelector('meta[name="turnstile-site-key"]');
    return meta && meta.getAttribute("content") ? meta.getAttribute("content").trim() : "";
  }

  function mountTurnstile(containerId) {
    var key = turnstileSiteKey();
    var container = document.getElementById(containerId);
    if (!key || !container || !window.turnstile) return;
    window.turnstile.render(container, { sitekey: key, theme: "auto" });
  }

  window.ProfitruFormSecurity = {
    formStartedAt: Date.now(),
    turnstileSiteKey: turnstileSiteKey,
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
  };

  document.addEventListener("DOMContentLoaded", function () {
    if (turnstileSiteKey()) {
      mountTurnstile("contact-turnstile");
      mountTurnstile("waitlist-turnstile");
    }
  });
})();
