(function () {
  var form = document.getElementById("contact-form");
  if (!form) return;

  var statusEl = document.getElementById("contact-form-status");
  var submitBtn = form.querySelector('[type="submit"]');

  function apiBase() {
    if (window.ProfitruFormSecurity && window.ProfitruFormSecurity.apiBase) {
      return window.ProfitruFormSecurity.apiBase();
    }
    var meta = document.querySelector('meta[name="contact-api-base"]');
    var v = meta && meta.getAttribute("content");
    v = (v || "").trim().replace(/\/$/, "");
    if (v) return v;
    return window.location && window.location.origin ? window.location.origin : "";
  }

  function setStatus(kind, text) {
    if (!statusEl) return;
    statusEl.hidden = false;
    statusEl.textContent = text;
    statusEl.className = "contact-form-status contact-form-status--" + kind;
    statusEl.setAttribute("role", "status");
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }
    if (submitBtn) submitBtn.disabled = true;
    setStatus("pending", "Sending\u2026");

    var submit = function () {
    var fd = new FormData(form);
    var payload = {
      name: (fd.get("name") || "").toString().trim(),
      email: (fd.get("email") || "").toString().trim(),
      phone: (fd.get("phone") || "").toString().trim(),
      subject: (fd.get("subject") || "").toString().trim(),
      message: (fd.get("message") || "").toString().trim(),
      company: (fd.get("company") || "").toString().trim(),
    };
    if (window.ProfitruFormSecurity) {
      Object.assign(payload, window.ProfitruFormSecurity.extraPayload());
    }

    fetch(apiBase() + "/api/contact", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(payload),
    })
      .then(function (res) {
        return res.text().then(function (text) {
          var data = null;
          if (text) {
            try {
              data = JSON.parse(text);
            } catch (parseErr) {
              data = null;
            }
          }
          return { ok: res.ok, status: res.status, data: data };
        });
      })
      .then(function (r) {
        if (r.ok && r.data && r.data.ok) {
          var successMsg;
          if (r.data.queued || r.data.email_sent === false) {
            successMsg =
              "Message received. Email notification is delayed; we still have your details and will follow up.";
          } else if (window.ProfitruFormSecurity && window.ProfitruFormSecurity.contactSendAckEnabled()) {
            successMsg =
              "Message sent. Check your email for a confirmation, and we will get back to you soon.";
          } else {
            successMsg = "Message sent. We will get back to you soon.";
          }
          setStatus("success", successMsg);
          form.reset();
          if (window.ProfitruFormSecurity) {
            window.ProfitruFormSecurity.formStartedAt = Date.now();
            window.ProfitruFormSecurity.refreshSecurity();
          }
        } else {
          var msg =
            (r.data && r.data.error) ||
            (r.status >= 500
              ? "Something went wrong. Please try again or email us directly."
              : "Could not send. Check the form and try again.");
          setStatus("error", msg);
        }
      })
      .catch(function () {
        setStatus(
          "error",
          "Network error. Check your connection or email support@profitru.com directly."
        );
      })
      .finally(function () {
        if (submitBtn) submitBtn.disabled = false;
      });
    };

    var ready = window.ProfitruFormSecurity
      ? window.ProfitruFormSecurity.ensureReady()
      : Promise.resolve();
    ready.then(submit).catch(function (err) {
      setStatus("error", err && err.message ? err.message : "Complete the security check and try again.");
      if (submitBtn) submitBtn.disabled = false;
    });
  });
})();
