# Profitru Marketing Site

Marketing website for [profitru.com](https://profitru.com). Primary calls-to-action go to the **[waitlist](waitlist.html)** (`/waitlist.html`); we notify users by email as capacity allows. **Log in** still points to [profitru.app](https://profitru.app/login) for existing accounts.

## Dual domain (`.in` and `.com`)

The same static files are often deployed to **`profitru.in`** and **`profitru.com`**. In this repo we treat **`https://profitru.com` as the canonical origin**:

- Every HTML page includes **`<link rel="canonical" href="https://profitru.com/...">`** (matching the URLs in `sitemap.xml`).
- **`robots.txt`** and **`sitemap.xml`** list the **`.com`** sitemap so Google discovers one preferred URL set.

**What you should configure outside the repo (strongly recommended):**

1. **301 redirects** from `https://profitru.in/*` to the matching `https://profitru.com/*` (or the reverse if you standardise on `.in`—then update canonicals, `sitemap.xml`, and `robots.txt` to match).
2. **Google Search Console**: add both hostname properties (Domain or URL-prefix) and use **URL Inspection** to confirm the canonical you want is selected after redirects propagate.

Without redirects, canonical tags still help, but **redirects avoid duplicate indexing** and odd snippets for the non-canonical host.

## Performance (frontend)

The static site is tuned for **Lighthouse / Core Web Vitals** without a bundler:

- **`styles.css`** and **`policies.css`** are **minified** (clean-css); **`main.js`** is **minified** (terser). Editability: use git history or run a formatter locally if you need readable sources again.
- **Homepage** loads **`styles.css` only** for above-the-fold CSS; the guides grid (`.policy-card`) lives in `styles.css` so the home path does not pay for an extra `policies.css` request.
- **Google Fonts** load with **`preload` + `media="print"` / `onload`** (non-render-blocking) and a reduced **Syne** weight set (`600;700;800`).
- **Google Analytics (gtag)** uses measurement ID `G-FC5BTBW68G` in `<head>` on each page.
- **Header logo** uses **`fetchpriority="high"`** on the homepage to help LCP.

**On the server/CDN**, set **long cache TTL** for hashed or versioned assets (`?v=…`), **Brotli/Gzip**, and HTTP/2 or HTTP/3 so Lighthouse’s “efficient cache” and transfer-size audits improve.

## Structure

See **[docs/STRUCTURE.md](docs/STRUCTURE.md)** for the full repository map (deploy root, duplicated nav, scripts, and what not to move without updating URLs).

- `index.html` — Single-page marketing site (seller-first narrative)
- `waitlist.html` — Private-beta waitlist form (POST `/api/waitlist` via [contact_server.py](contact_server.py))
- `styles.css` — UI system (Syne + Manrope, dark theme, emerald accent); minified in repo
- `nav-dropdown.css` / `nav-dropdown.js` — Header mega-menu (Product / Resources / Company dropdowns, stacked on mobile; load on every page with the main nav)
- `main.js` — Mobile nav + FAQ accordion + footer year
- `scripts/apply_mega_nav.py` — One-off or reference for re-applying the shared nav block across HTML (optional; nav is already in templates)
- `logos/` — Brand assets: **`logos/profitru/profitru-logo-horizontal.png`** (header/footer logo) and **`logos/profitru/profitru-favicon.png`** (tab icon + Apple touch; referenced directly in HTML, no build step). Also `marketplace/*.svg` (Amazon, Flipkart, Shopify, WooCommerce, PrestaShop from [Simple Icons](https://simpleicons.org/) CC0; Meesho wordmark).

## Sections (UX flow)

1. **Hero** — Multi-marketplace value prop, dual CTA, platform pills, product preview card
2. **Pain → outcome** — Three relatable seller problems mapped to Profitru outcomes
3. **How it works** — Three steps (connect → see profit → run ops)
4. **Product** — Feature tiles (analytics, inventory, returns, procurement, dispatch, GST)
5. **Demo** — Placeholder shell (replace with YouTube/Loom iframe)
6. **Why Profitru** — Early-access narrative: founder note + focus pillars + founding-cohort CTAs (add real case studies when you have them)
7. **Trust** — Data, India-first, support
8. **FAQ** — Accordion
9. **Footer CTA** — Waitlist + contact + email

## Deploy to profitru.com

### Option A: AWS S3 + CloudFront (recommended)

1. Create S3 bucket (e.g. `profitru-marketing`)
2. Enable static website hosting (set **Index document** to `index.html` so `blog/` resolves to `blog/index.html`)
3. Upload the **full** site tree: `index.html`, `styles.css`, `main.js`, `blog/**`, `amazon-profit-calculator/**`, other calculator folders, `policies/**`, `logos/**`, etc. Uploading only the homepage files will 404 every subdirectory URL.
4. Create CloudFront distribution pointing to S3
5. Add custom domain `profitru.com` in CloudFront
6. Point DNS A/CNAME for `profitru.com` to CloudFront

### Option B: Same Lightsail instance (nginx)

If you already have Lightsail for the app:

```bash
# On your Lightsail instance
sudo mkdir -p /var/www/profitru.com
# Copy the *entire* repo root into the web root (not only index.html):
#   index.html, styles.css, main.js, robots.txt, sitemap.xml,
#   blog/, amazon-profit-calculator/, flipkart-profit-calculator/, …, logos/, policies/
```

Use a **multi-page static** `location` block (this site is **not** a single-page app—do **not** fall back to `/index.html` for every missing URL):

```nginx
server {
    listen 80;
    server_name profitru.com www.profitru.com;
    root /var/www/profitru.com;
    index index.html;
    location / {
        try_files $uri $uri/ =404;
    }
}
```

A fuller example (TLS + asset caching + `.in` → `.com` redirect) lives in **[deploy/nginx.profitru-marketing.conf](deploy/nginx.profitru-marketing.conf)**.

**If `https://profitru.in/blog/` or `/amazon-profit-calculator/` returns 404 but localhost works:** the `.in` host usually has an **incomplete upload** (only top-level files) or **nginx `root`** points at the wrong folder. Re-sync the full tree or **301 redirect** `profitru.in` → `profitru.com` so both hostnames serve the same deployment.

To send **`profitru.in`** to the canonical host (recommended), add a separate `server` that only redirects (TLS certificates required for both names):

```nginx
server {
    listen 443 ssl;
    server_name profitru.in www.profitru.in;
    return 301 https://profitru.com$request_uri;
}
```

Same idea in **Cloudflare**: **Redirect Rules** (or Page Rules) from `profitru.in/*` to `https://profitru.com/$1`.

### Option C: Vercel / Netlify

1. Connect Profitru-Marketing repo
2. Build: none (static)
3. Output: root directory
4. Add custom domain `profitru.com`

## Customize

- **Demo video**: Replace the `.demo-shell` block with your YouTube/Loom iframe
- **Why Profitru section**: Refresh the founder note as the story evolves; add real quotes or logos when you have customers
- **Logo**: Optional `profitru-logo.png` + updated header/footer markup if you switch from the built-in P mark

## Preview locally

```bash
cd /Users/adeygifting/Workspace/Profitru-Marketing && python3 serve.py
```

Open `http://127.0.0.1:8080` (serves HTML with `charset=utf-8`).

## Contact form (email via SMTP)

The [contact.html](contact.html) page includes a form that POSTs JSON to `/api/contact`. A small Flask app sends mail to **support@profitru.com** (configurable) using SMTP.

1. Copy the environment template and add your provider credentials:

   ```bash
   cp .env.example .env
   ```

2. Create a virtualenv and install dependencies:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Run the combined static site + API:

   ```bash
   python contact_server.py
   ```

   Open `http://127.0.0.1:8080/contact.html` and submit the form. Submissions arrive with **Reply-To** set to the visitor’s address so you can reply from your inbox.

**Waitlist** ([waitlist.html](waitlist.html)) POSTs to `/api/waitlist`. Notifications go to `WAITLIST_TO_EMAIL` (defaults to `CONTACT_TO_EMAIL`, then `founder@profitru.com`). **Do not** deliver to the same mailbox as `SMTP_USER` after a spam event — Microsoft often blocks `support@` → `support@` loops. Auto-reply to the submitter is **off by default** (`WAITLIST_SEND_ACK=true` only after SPF/DKIM pass).

### Form spam protection

Public forms are targeted by bots. The API now includes:

- **Rate limiting** per IP (see `FORM_RATE_LIMIT_*` in `.env`)
- **Minimum fill time** (blocks instant bot POSTs)
- **Spam keyword / URL filtering** (silent reject — no email sent)
- **Optional Cloudflare Turnstile** — required by default (`FORM_REQUIRE_TURNSTILE=true`). Set **both** keys in the **server** `.env` (not just the Cloudflare dashboard):

  ```
  TURNSTILE_SITE_KEY=0x4AAAAAAA...
  TURNSTILE_SECRET_KEY=0x4AAAAAAA...
  WAITLIST_SEND_ACK=false
  ```

  The site key is loaded from `GET /api/form-config` (static HTML on nginx does not embed it). Verify deploy: `GET /api/health` → `"turnstile_configured": true`.

  Turnstile alone in Cloudflare is **not enough** until both keys are in `/home/profitru/profitru-marketing/.env` and `profitru-marketing` is restarted.
- **Emergency stop** — `FORM_SUBMISSIONS_ENABLED=false` stops all outbound form mail

If you see bounce floods from `Mail Delivery System`, disable `WAITLIST_SEND_ACK` and fix **SPF + DKIM** for `profitru.com` before re-enabling user acknowledgements.

For production, put the site behind a reverse proxy and run the app with a WSGI server, for example:

```bash
gunicorn -w 2 -b 127.0.0.1:8080 contact_server:app
```

If the marketing HTML is served from another host (CDN, S3), set the API base URL in [contact.html](contact.html) and [waitlist.html](waitlist.html) using the `<meta name="contact-api-base" content="https://your-api-host">` tag so `contact-form.js` and `waitlist-form.js` post to the correct origin.

### Production deployment

1. Upload the full static site to `/var/www/profitru-marketing` (not just `index.html`).
2. Copy `.env` with valid `SMTP_*` values to the server.
3. Install deps and run the API with gunicorn (see [deploy/profitru-marketing.service](deploy/profitru-marketing.service) — on the live server this unit is named `profitru-marketing.service`).
4. Point nginx at the static root and proxy `/api/` to `127.0.0.1:8080` (see [deploy/nginx.profitru-marketing.conf](deploy/nginx.profitru-marketing.conf)).
5. Check `GET /api/health` returns `{"ok": true, ...}`.

If SMTP is misconfigured, submissions are still saved under `data/submissions/*.jsonl` and the form returns success (`{"ok": true, "queued": true}`). Review those files and fix SMTP so email notifications resume.

**Office 365 / Microsoft 365:** use `SMTP_HOST=smtp.office365.com`, port `587`, STARTTLS enabled. Basic auth must be allowed for the mailbox, or use an app password if MFA is on. A `535 Authentication unsuccessful` error means the password or auth policy needs updating in `.env`.

**535 Authentication unsuccessful:** Microsoft rejected the SMTP login (different from **550 AS(42004)** sender block). Fix:

1. `SMTP_USER=info@profitru.com` (full address) and `CONTACT_FROM_EMAIL=info@profitru.com` (must match for Office 365).
2. If MFA is enabled on the mailbox, create an **app password** and put it in `SMTP_PASSWORD` (normal account password will not work).
3. Enable **Authenticated SMTP** for the mailbox: Exchange admin → **Recipients → Mailboxes** → select mailbox → **Email apps** → turn on **Authenticated SMTP**. Or PowerShell: `Set-CASMailbox -Identity info@profitru.com -SmtpClientAuthenticationDisabled $false`
4. If still failing, check tenant SMTP AUTH: `Get-TransportConfig | fl SmtpClientAuthenticationDisabled` (must be `False`).
5. Re-run on the server: `python scripts/test_smtp.py`

If Outlook shows *“sending email address was not recognized as a valid sender”* or **`550 5.1.8 Access denied, bad outbound sender AS(42004)`**, Microsoft has **blocked outbound mail from that mailbox** (usually after bot spam). Changing `WAITLIST_TO_EMAIL` alone does **not** fix this — the **sender** (`SMTP_USER`) is restricted.

**Fix option A — unblock `support@` (recommended long-term)**

1. [Microsoft 365 admin center](https://admin.microsoft.com) → **Email & collaboration** → **Review** → **Restricted users** — remove `support@profitru.com` if listed.
2. **Security** → **Email & collaboration** → **Threat policies** — check **Restricted entities** / outbound spam.
3. Open a Microsoft support ticket with the NDR text and error **AS(42004)** if the mailbox stays blocked after 24–48h.
4. Validate **SPF**, **DKIM**, and **DMARC** for `profitru.com` (DNS).
5. Keep `WAITLIST_SEND_ACK=false` until sending works reliably.

**Fix option B — send from a different mailbox (fast workaround)**

If `founder@profitru.com` is not restricted, on the **server** `.env`:

```env
SMTP_USER=founder@profitru.com
SMTP_PASSWORD=<founder app password>
CONTACT_FROM_EMAIL=founder@profitru.com
CONTACT_TO_EMAIL=founder@profitru.com
WAITLIST_TO_EMAIL=founder@profitru.com
```

Then `sudo systemctl restart profitru-marketing` and run `python scripts/test_smtp.py`.

Missed submissions may still be in `data/submissions/waitlist.jsonl` on the server when SMTP failed or mail bounced.
