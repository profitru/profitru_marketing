(function () {
  var form = document.getElementById("contact-form");
  if (!form) return;

  var statusEl = document.getElementById("contact-form-status");
  var submitBtn = form.querySelector('[type="submit"]');

  function apiBase() {
    var meta = document.querySelector('meta[name="contact-api-base"]');
    var v = meta && meta.getAttribute("content");
    return (v || "").replace(/\/$/, "");
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
    setStatus("pending", "Sending…");

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
          var successMsg =
            r.data.queued || r.data.email_sent === false
              ? "Message received. We will get back to you soon."
              : "Message sent. We will get back to you soon.";
          setStatus("success", successMsg);
          form.reset();
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
  });
})();
