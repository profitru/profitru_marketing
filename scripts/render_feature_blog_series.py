#!/usr/bin/env python3
"""Generate Profitru marketing feature-series blog HTML under blog/<slug>/index.html."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "blog"
DATE = "2026-04-14"
DATE_DISP = "14 April 2026"
CANON = "https://profitru.com/blog"

SERIES_ORDER = [
    "profitru-platform-overview",
    "sku-profit-calculation-india",
    "inventory-management-ecommerce",
    "procurement-reorder-planning",
    "dispatch-fulfilment-operations",
    "ecommerce-returns-qc",
    "spf-claims-reimbursement-tracking",
    "marketplace-data-export-csv",
    "warehouse-team-roles-access",
    "ai-profit-assistant-pro",
    "warehouse-management-software",
]


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
    )


def section(h2: str, paras: list[str], bullets: list[str] | None = None) -> str:
    parts = [f"<h2>{h2}</h2>"]
    parts.extend(f"<p>{p}</p>" for p in paras)
    if bullets:
        parts.append("<ul>")
        parts.extend(f"<li>{b}</li>" for b in bullets)
        parts.append("</ul>")
    return "\n        ".join(parts)


HEAD_TOP = """<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-FC5BTBW68G"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());

    gtag('config', 'G-FC5BTBW68G');
  </script>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="theme-color" content="#2563eb">
  <meta name="description" content="{meta_desc}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{canonical}">
  <meta property="og:type" content="article">
  <meta property="og:locale" content="en_IN">
  <meta property="og:title" content="{og_title}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="https://profitru.com/logos/profitru/profitru-logo-horizontal.png">
  <meta property="og:image:width" content="900">
  <meta property="og:image:height" content="400">
  <meta property="og:image:alt" content="Profitru logo">
  <meta property="og:description" content="{og_desc}">
  <meta property="og:site_name" content="Profitru">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{tw_title}">
  <meta name="twitter:description" content="{og_desc}">
  <script type="application/ld+json">
  {json_ld}
  </script>
  <script>
    (function () {{
      var key = "profitru-marketing-theme";
      var stored = localStorage.getItem(key);
      var theme = stored === "light" || stored === "dark" ? stored : window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
      document.documentElement.setAttribute("data-theme", theme);
      document.documentElement.style.colorScheme = theme === "dark" ? "dark" : "light";
      var meta = document.querySelector('meta[name="theme-color"]');
      if (meta) meta.setAttribute("content", theme === "dark" ? "#0f172a" : "#2563eb");
    }})();
  </script>
  <title>{doc_title}</title>
  <link rel="icon" type="image/png" href="../../logos/profitru/profitru-favicon.png?v=profitru-direct-2026-04" sizes="any">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&family=Syne:wght@600;700;800&display=swap">
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&family=Syne:wght@600;700;800&display=swap" rel="stylesheet" media="print" onload="this.media='all'">
  <noscript><link href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&family=Syne:wght@600;700;800&display=swap" rel="stylesheet"></noscript>
  <link rel="stylesheet" href="../../styles.css?v=profitru-2026-04-13-lineaccent">
  <link rel="stylesheet" href="../../policies.css?v=profitru-2026-04-13">
  <link rel="stylesheet" href="../../nav-dropdown.css?v=2026-04-25">
</head>
<body>
  <a href="#main" class="skip-link">Skip to content</a>
  <div class="data-nodes-bg" aria-hidden="true">
    <svg class="data-nodes-bg__svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700" preserveAspectRatio="xMidYMid slice" role="presentation" focusable="false">
      <g class="data-nodes-bg__glow" aria-hidden="true"><circle cx="480" cy="295" r="120" /><circle cx="320" cy="480" r="90" /><circle cx="780" cy="160" r="70" /></g>
      <path class="data-nodes-bg__lines" fill="none" d="M40,95 L200,65 L380,115 L560,72 L740,98 L920,88 M75,270 L280,245 L480,295 L680,258 M900,275" />
      <g class="data-nodes-bg__nodes"><circle cx="480" cy="295" r="4.2" /></g>
    </svg>
  </div>

  <header class="nav" data-nav>
    <div class="nav-inner container--wide">
      <a href="/index.html" class="logo logo--tile" aria-label="Profitru home">
        <img src="../../logos/profitru/profitru-logo-horizontal.png?v=profitru-direct-2026-04" width="900" height="400" alt="Profitru logo &mdash; Turn data into profit." class="logo-img" fetchpriority="high" decoding="async">
      </a>
      <div class="nav-end">
        <nav class="nav-links nav-links--mega" id="nav-menu" aria-label="Primary">
          <div class="nav-mega" data-nav-dropdown>
            <button type="button" class="nav-mega__btn" id="nav-btn-product" aria-expanded="false" aria-controls="nav-panel-product" aria-haspopup="true">Product</button>
            <div class="nav-mega__panel" id="nav-panel-product" role="region" aria-labelledby="nav-btn-product" hidden>
              <div class="nav-mega__stack">
                <a href="/#pains">Problem</a>
                <a href="/#how">How it works</a>
                <a href="/#features">What you get</a>
                <a href="/#demo">See it in action</a>
                <a href="/#faq">FAQ</a>
                <a href="/#cta">Get started</a>
                <a href="/#built-for">Why Profitru</a>
              </div>
            </div>
          </div>
          <div class="nav-mega" data-nav-dropdown>
            <button type="button" class="nav-mega__btn" id="nav-btn-resources" aria-expanded="false" aria-controls="nav-panel-resources" aria-haspopup="true">Resources</button>
            <div class="nav-mega__panel" id="nav-panel-resources" role="region" aria-labelledby="nav-btn-resources" hidden>
              <div class="nav-mega__stack">
                <a href="/#guides">Guides hub</a>
                <a href="/blog/index.html">Blog</a>
              </div>
            </div>
          </div>
          <div class="nav-mega" data-nav-dropdown>
            <button type="button" class="nav-mega__btn" id="nav-btn-company" aria-expanded="false" aria-controls="nav-panel-company" aria-haspopup="true">Company</button>
            <div class="nav-mega__panel" id="nav-panel-company" role="region" aria-labelledby="nav-btn-company" hidden>
              <div class="nav-mega__stack">
                <a href="/contact.html">Contact</a>
                <a href="/policies/index.html">Policies &amp; legal</a>
              </div>
            </div>
          </div>
          <a href="/waitlist.html" class="btn btn-primary nav-mega__cta">Join the waitlist</a>
          <a href="https://bookings.cloud.microsoft/book/Proiftrudemo@profitru.com/" class="nav-mega__login" target="_blank" rel="noopener noreferrer">Book a demo</a>
          <a href="https://profitru.app/login" class="nav-mega__login">Log in</a>
        </nav>
        <button type="button" class="theme-toggle" data-theme-toggle="1" aria-label="Switch theme">
          <svg class="theme-toggle__moon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" /></svg>
          <svg class="theme-toggle__sun" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="4" /><path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32l1.41 1.41M2 12h2m16 0h2M4.93 19.07l1.41-1.41m11.32-11.32l1.41-1.41" /></svg>
        </button>
        <button type="button" class="nav-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="nav-menu"><span></span><span></span><span></span></button>
      </div>
    </div>
  </header>

  <main id="main" class="policies-hub">
    <div class="container policy-page__inner">
      <article class="policy-article">
        <p class="blog-card-meta">{DATE_DISP} &middot; {category}</p>
        <h1>{h1}</h1>
        <p class="policy-meta">{intro}</p>

        {body}

        <h2>Related on the blog &amp; guides</h2>
        <p>Channel economics: <a href="../multi-channel-margin-one-truth/index.html">multi-channel margin</a>, <a href="../amazon-payout-vs-real-profit/index.html">Amazon payouts</a>, <a href="../d2c-cod-and-margin/index.html">D2C COD &amp; RTO</a>. Operations hub: <a href="/blog/warehouse-management-software/index.html">warehouse &amp; marketplace operations</a>. Walkthroughs: <a href="/#guides">homepage guides</a>, <a href="../../amazon-profit-calculator/index.html">Amazon</a>, <a href="../../flipkart-profit-calculator/index.html">Flipkart</a>, <a href="../../ecommerce-profit-calculator/index.html">ecommerce</a>, <a href="../../multi-channel-profit-calculator/index.html">multi-channel</a> calculators.</p>
      </article>

      <nav class="seo-related" aria-labelledby="feat-series">
        <h2 id="feat-series">More in this feature series</h2>
        <div class="policies-grid" role="list">
{series_cards}
        </div>
      </nav>

      <nav class="seo-related" aria-labelledby="feat-guides">
        <h2 id="feat-guides">Profit guides on this site</h2>
        <div class="policies-grid" role="list">
          <a class="policy-card" href="/#guides" role="listitem"><h2>Homepage guides hub</h2><p>Structured walkthroughs from the main marketing page.</p><span class="policy-card__arrow">Open &rarr;</span></a>
          <a class="policy-card" href="../../amazon-profit-calculator/index.html" role="listitem"><h2>Amazon profit guide</h2><p>Fees, ads, returns, and unit economics.</p><span class="policy-card__arrow">Open &rarr;</span></a>
          <a class="policy-card" href="../../flipkart-profit-calculator/index.html" role="listitem"><h2>Flipkart profit guide</h2><p>Commissions, fulfilment, and GST alignment.</p><span class="policy-card__arrow">Open &rarr;</span></a>
          <a class="policy-card" href="../../ecommerce-profit-calculator/index.html" role="listitem"><h2>Ecommerce &amp; D2C profit</h2><p>Own-store margin beyond GMV.</p><span class="policy-card__arrow">Open &rarr;</span></a>
        </div>
      </nav>

      <nav class="seo-related" aria-labelledby="feat-more">
        <h2 id="feat-more">Strategy articles</h2>
        <div class="policies-grid" role="list">
          <a class="policy-card" href="../multi-channel-margin-one-truth/index.html" role="listitem"><h2>Multi-channel profit</h2><p>One margin definition everywhere.</p><span class="policy-card__arrow">Read &rarr;</span></a>
          <a class="policy-card" href="../amazon-payout-vs-real-profit/index.html" role="listitem"><h2>Amazon payout vs real profit</h2><p>What settlements still hide.</p><span class="policy-card__arrow">Read &rarr;</span></a>
          <a class="policy-card" href="../d2c-cod-and-margin/index.html" role="listitem"><h2>COD, RTO, and D2C margin</h2><p>Where ecommerce margin leaks.</p><span class="policy-card__arrow">Read &rarr;</span></a>
          <a class="policy-card" href="../index.html" role="listitem"><h2>All blog posts</h2><p>Blog hub</p><span class="policy-card__arrow">View &rarr;</span></a>
        </div>
      </nav>
    </div>

    <section class="section-cta contact-page-cta" aria-labelledby="feat-cta">
      <div class="container">
        <h2 id="feat-cta" class="cta-title">{cta_title}</h2>
        <p class="cta-desc">{cta_desc}</p>
        <div class="cta-actions">
          <a href="/waitlist.html" class="btn btn-primary btn-lg">Join the waitlist</a>
          <a href="/#features" class="btn btn-ghost btn-lg">What you get</a>
          <a href="../index.html" class="btn btn-ghost btn-lg">Back to blog</a>
        </div>
      </div>
    </section>
  </main>

  <footer class="footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-brand">
          <a href="/index.html" class="logo logo--tile" aria-label="Profitru home">
            <img src="../../logos/profitru/profitru-logo-horizontal.png?v=profitru-direct-2026-04" width="900" height="400" alt="Profitru logo &mdash; Turn data into profit." class="logo-img" decoding="async">
          </a>
          <p>Operational clarity for Indian sellers who list on marketplaces, run their own store, or both.</p>
        </div>
        <div class="footer-col">
          <h3>Product</h3>
          <a href="/waitlist.html">Join waitlist</a>
          <a href="https://profitru.app/login">Log in</a>
          <a href="/#demo">Demo</a>
        </div>
        <div class="footer-col">
          <h3>Guides</h3>
          <a href="../index.html">Blog</a>
          <a href="../../amazon-profit-calculator/index.html">Amazon profit</a>
          <a href="../../flipkart-profit-calculator/index.html">Flipkart profit</a>
          <a href="../../ecommerce-profit-calculator/index.html">Ecommerce profit</a>
          <a href="../../multi-channel-profit-calculator/index.html">Multi-channel profit</a>
        </div>
        <div class="footer-col">
          <h3>Legal</h3>
          <a href="../../policies/index.html">Policies &amp; legal</a>
          <a href="../../policies/privacy-policy.html">Privacy</a>
          <a href="../../policies/terms-of-service.html">Terms</a>
        </div>
        <div class="footer-col">
          <h3>Company</h3>
          <a href="../../contact.html">Contact</a>
          <a href="/#faq">FAQ</a>
        </div>
        <div class="footer-col">
          <h3>Social</h3>
          <a href="https://www.instagram.com/profitru.app/" rel="noopener noreferrer" target="_blank">Instagram</a>
          <a href="https://www.linkedin.com/in/profitru-app-0b4692402/" rel="noopener noreferrer" target="_blank">LinkedIn</a>
          <a href="https://x.com/profitruapps" rel="noopener noreferrer" target="_blank">X</a>
          <a href="https://www.threads.net/@profitru.app" rel="noopener noreferrer" target="_blank">Threads</a>
        </div>
      </div>
      <div class="footer-bottom">
        <span>&copy; <span id="year"></span> Profitru. All rights reserved.</span>
        <span>Marketing site &middot; App lives at profitru.app</span>
      </div>
    </div>
  </footer>
  <script src="../../main.js?v=profitru-2026-04-13" defer></script>
  <script src="../../nav-dropdown.js?v=2026-04-25" defer></script>
</body>
</html>
"""

SERIES_BLURBS: dict[str, tuple[str, str]] = {
    "profitru-platform-overview": ("Profitru platform overview", "How the product fits together for Indian ecommerce teams."),
    "sku-profit-calculation-india": ("SKU profit calculation", "Real margin per product and channel after fees, returns, and GST."),
    "inventory-management-ecommerce": ("Inventory management", "Stock you can trust across purchases, dispatch, and returns."),
    "procurement-reorder-planning": ("Procurement &amp; reorder planning", "Buy what velocity and margin justify&mdash;not spreadsheet guesses."),
    "dispatch-fulfilment-operations": ("Dispatch &amp; fulfilment", "From pick-pack to shipment status without ghost units."),
    "ecommerce-returns-qc": ("Returns &amp; QC", "Margin-aware returns, restock rules, and resellable vs damaged."),
    "spf-claims-reimbursement-tracking": ("SPF &amp; reimbursement claims", "Track claims next to operations and settlements."),
    "marketplace-data-export-csv": ("Platform exports &amp; CSV", "Bulk in from marketplace files; structured views out."),
    "warehouse-team-roles-access": ("Team roles &amp; access", "Finance, ops, and warehouse on one operational truth."),
    "ai-profit-assistant-pro": ("AI Profit Assistant (Pro)", "Signals on risk, demand, and margin leaks before they bite."),
    "warehouse-management-software": ("Warehouse &amp; marketplace ops", "End-to-end operations article for Indian sellers."),
}


def series_cards_html(current_slug: str) -> str:
    lines = []
    for slug in SERIES_ORDER:
        if slug == current_slug:
            continue
        title, blurb = SERIES_BLURBS[slug]
        lines.append(
            f'          <a class="policy-card" href="../{slug}/index.html" role="listitem"><h2>{title}</h2><p>{blurb}</p><span class="policy-card__arrow">Read &rarr;</span></a>'
        )
    return "\n".join(lines[:8])


def build_json_ld(headline: str, desc: str, url: str) -> str:
    return json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": headline,
            "datePublished": DATE,
            "dateModified": DATE,
            "author": {"@type": "Organization", "name": "Profitru"},
            "publisher": {"@type": "Organization", "name": "Profitru"},
            "mainEntityOfPage": url,
            "description": desc,
        },
        ensure_ascii=False,
    )


ARTICLES: dict[str, dict] = {
    "profitru-platform-overview": {
        "category": "Product",
        "h1": "Profitru platform overview for Indian ecommerce teams",
        "doc_title": "Profitru platform overview &mdash; Product blog | Profitru",
        "meta_desc": "How Profitru ties profit, inventory, procurement, returns, dispatch, claims, exports, team access, and AI signals into one system for Indian sellers\u2014without marketplace APIs.",
        "og_title": "Profitru platform overview | Profitru Blog",
        "og_desc": "One operational and margin story: bulk data, SKU profit, inventory, procurement, returns, dispatch, claims, exports, roles, and AI on Pro.",
        "tw_title": "Profitru platform overview | Profitru Blog",
        "json_headline": "Profitru platform overview for Indian ecommerce teams",
        "json_desc": "Feature map of Profitru for marketplace and D2C sellers in India.",
        "intro": """Profitru is a profit and operations workspace for sellers who list on <a href="../../amazon-profit-calculator/index.html">Amazon</a>, <a href="../../flipkart-profit-calculator/index.html">Flipkart</a>, other marketplaces, or <a href="../../ecommerce-profit-calculator/index.html">their own store</a>. This article is the map: how each capability connects to <a href="/#features">what you see on the homepage</a> and to the deeper posts in this series. Profitru uses <a href="/#faq">bulk uploads</a>, not live marketplace APIs, so you can start without engineering projects.""",
        "body": "\n        ".join(
            [
                section(
                    "The problem Profitru solves",
                    [
                        "Finance sees payouts, ops sees WMS rows, growth sees ad dashboards&mdash;and none of them share one SKU-level truth. That gap shows up as &ldquo;profitable&rdquo; SKUs that are actually bleeding once returns, GST, and dead stock are included.",
                        "Profitru is built to be the <a href=\"/#pains\">single command centre</a> Indian teams describe on the marketing site: structured data in, reconciled views out.",
                    ],
                    [
                        "SKU-level margin after fees, ads, returns, and tax treatment",
                        "Inventory that reflects purchases, dispatch, and returns",
                        "Procurement hints tied to velocity and profitability",
                        "Returns and QC that update stock and margin honestly",
                        "Dispatch visibility so channels and warehouse agree",
                        "Claim tracking next to operational events",
                        "Exports for finance and auditors",
                        "Role-appropriate access for warehouse and HQ",
                        "AI Profit Assistant on Pro for early warnings",
                    ],
                ),
                section(
                    "How data gets in",
                    [
                        "You export reports from marketplaces and tools you already use, then upload them in bulk. Profitru normalises and links those files so the same SKU and channel identifiers flow through profit, inventory, and operations views&mdash;see <a href=\"/blog/marketplace-data-export-csv/index.html\">platform exports &amp; CSV</a> for the practical workflow.",
                    ],
                ),
                section(
                    "Where to go next",
                    [
                        "Use the articles below as standalone deep reads, or start with <a href=\"/blog/sku-profit-calculation-india/index.html\">SKU profit calculation</a> if margin trust is your first gap. For warehouse-heavy teams, <a href=\"/blog/warehouse-management-software/index.html\">warehouse &amp; marketplace operations</a> ties the floor to finance.",
                    ],
                ),
            ]
        ),
        "cta_title": "See the full product story on your data",
        "cta_desc": "Trial Profitru with bulk uploads from the channels you already sell on.",
    },
    "sku-profit-calculation-india": {
        "category": "Product",
        "h1": "SKU profit calculation: real margin per channel in India",
        "doc_title": "SKU profit calculation for ecommerce &mdash; Profitru Blog",
        "meta_desc": "How to think about true SKU profit after marketplace fees, advertising, returns, COGS, and GST\u2014and how Profitru keeps one margin definition per channel.",
        "og_title": "SKU profit calculation | Profitru Blog",
        "og_desc": "Per-SKU, per-channel profit after fees, ads, returns, and GST\u2014not portal headline numbers.",
        "tw_title": "SKU profit calculation | Profitru Blog",
        "json_headline": "SKU profit calculation for Indian ecommerce sellers",
        "json_desc": "True margin per SKU and channel after fees, ads, returns, and GST.",
        "intro": """Portal dashboards optimise for their own scorecards. <a href="../multi-channel-margin-one-truth/index.html">Multi-channel profit</a> only works when every channel uses the same COGS, return attribution, and fee logic. Profitru&rsquo;s profit layer matches the <a href="/#demo">profit dashboard</a> story on the homepage: numbers you can defend in a purchase review.""",
        "body": "\n        ".join(
            [
                section(
                    "What &ldquo;real&rdquo; SKU profit includes",
                    [
                        "At minimum: landed cost (including inbound freight and duties where relevant), marketplace fees and promotions, advertising at the SKU or campaign level you can reasonably attribute, returns and refunds, and the tax treatment your accountant expects for your entity.",
                        "For Amazon India settlements specifically, pair this article with <a href=\"../amazon-payout-vs-real-profit/index.html\">what your payout row still hides</a> so you do not confuse cash timing with margin truth.",
                    ],
                    [
                        "Referral, closing, and fulfilment fees that vary by ASIN and season",
                        "Deal fees, coupons, and lightning allocations",
                        "Storage and aged-inventory charges where applicable",
                        "GST lines aligned to your filing approach (consult your CA for edge cases)",
                    ],
                ),
                section(
                    "Why channel-specific views still roll up",
                    [
                        "You need Flipkart net margin and Amazon net margin to be comparable, not identical. Fee structures differ; what must stay consistent is COGS, return cost, and how you attribute ads. Profitru keeps <a href=\"../../multi-channel-profit-calculator/index.html\">one framework</a> with channel-specific inputs.",
                    ],
                ),
                section(
                    "Operational inputs that finance usually forgets",
                    [
                        "Dead stock, liquidation, and QC failures belong in the same SKU story as gross sales. If inventory and returns live in a different tab, profit will always look better than reality&mdash;which is why Profitru links <a href=\"/blog/inventory-management-ecommerce/index.html\">inventory</a> and <a href=\"/blog/ecommerce-returns-qc/index.html\">returns</a> to the same SKU keys.",
                    ],
                ),
                section(
                    "Getting started",
                    [
                        "Upload the settlement, order, and catalog files you already export today; you do not need OAuth integrations. When the data is in, iterate on COGS and mappings until leadership agrees on one definition&mdash;then freeze it for the quarter.",
                    ],
                ),
            ]
        ),
        "cta_title": "Model SKU profit on your live catalogue",
        "cta_desc": "Start a trial and align finance, ops, and growth on one margin definition.",
    },
    "inventory-management-ecommerce": {
        "category": "Product",
        "h1": "Inventory management that matches marketplace reality",
        "doc_title": "Ecommerce inventory management &mdash; Profitru Blog",
        "meta_desc": "Track stock across purchases, dispatch, and returns so available quantity and margin models stay aligned for Indian ecommerce.",
        "og_title": "Inventory management for ecommerce | Profitru Blog",
        "og_desc": "Trustworthy stock: purchases, dispatch, returns, and QC in one loop.",
        "tw_title": "Ecommerce inventory | Profitru Blog",
        "json_headline": "Inventory management for ecommerce sellers in India",
        "json_desc": "Stock truth across purchases, dispatch, and returns.",
        "intro": """Overselling and silent stockouts are usually data problems, not people problems. Profitru&rsquo;s inventory story matches the <a href="/#demo">inventory &amp; returns</a> screen on the homepage: one trail from PO to dispatch to return disposition. Read alongside <a href=\"/blog/sku-profit-calculation-india/index.html\">SKU profit calculation</a> so units and rupees stay tied.""",
        "body": "\n        ".join(
            [
                section(
                    "The inventory loop",
                    [
                        "Healthy inventory answers three questions: what you physically have, what you have promised to channels, and what is unsellable but not yet written off. Spreadsheets rarely keep those three aligned after the first busy week.",
                    ],
                    [
                        "Inbound: POs, GRN, and supplier returns",
                        "Available: net of holds, QC failures, and channel reservations where you track them",
                        "Outbound: dispatch and carrier handover",
                        "Returns: resellable, refurbish, liquidate, or scrap",
                    ],
                ),
                section(
                    "Bundles and BOM",
                    [
                        "If you sell kits, your available quantity is constrained by the weakest component. Profitru expects you to model bundles explicitly so marketplace catalogue stock does not drift from component reality.",
                    ],
                ),
                section(
                    "Channel-specific nuance",
                    [
                        "FBA-style remote fulfilment, seller-fulfilled Prime, and hybrid models change where &ldquo;available&rdquo; lives. Your system should record the warehouse truth first, then map to each channel&rsquo;s promise&mdash;the same operational spine described in <a href=\"/blog/warehouse-management-software/index.html\">warehouse &amp; marketplace operations</a>.",
                    ],
                ),
                section(
                    "Cadence",
                    [
                        "Match upload cadence to how fast you turn SKUs. Fast fashion or high promo velocity may need daily settlement and dispatch files; stable catalogues may be fine with a few uploads per week. Consistency beats perfection.",
                    ],
                ),
            ]
        ),
        "cta_title": "Stop guessing what is sellable",
        "cta_desc": "Connect uploads so stock and profit use the same SKU graph.",
    },
    "procurement-reorder-planning": {
        "category": "Product",
        "h1": "Procurement and reorder planning tied to real velocity",
        "doc_title": "Procurement &amp; reorder planning &mdash; Profitru Blog",
        "meta_desc": "Plan purchase orders using sales velocity, profitability, and inventory truth\u2014not isolated spreadsheet forecasts.",
        "og_title": "Procurement &amp; reorder planning | Profitru Blog",
        "og_desc": "Reorder what earns; pause what only looks busy.",
        "tw_title": "Procurement planning | Profitru Blog",
        "json_headline": "Procurement and reorder planning for ecommerce sellers",
        "json_desc": "PO planning from velocity, margin, and inventory coverage.",
        "intro": """Procurement mistakes show up months later as markdowns and storage fees. Profitru aligns buying decisions with the <a href="/#demo">procurement &amp; decisions</a> storyline on the homepage: the same SKU profit and inventory coverage you already use for reporting. Start from <a href=\"/blog/sku-profit-calculation-india/index.html\">SKU profit</a> so you do not scale losers.""",
        "body": "\n        ".join(
            [
                section(
                    "Leading indicators vs lagging dashboards",
                    [
                        "GMV-heavy reports reward volume. Procurement should weight margin and return rates, especially for categories with high COD or fashion return profiles. Pull D2C nuance from <a href=\"../d2c-cod-and-margin/index.html\">COD, RTO, and margin</a> when relevant.",
                    ],
                ),
                section(
                    "Coverage and lead time",
                    [
                        "Express lead times in days of stock at current velocity, not containers or vague months. Include supplier MOQs and inbound transit so you do not optimistically double-count arriving stock.",
                    ],
                    [
                        "Safety stock for promo windows",
                        "Component coverage for bundles",
                        "End-of-life and clearance rules for slow movers",
                    ],
                ),
                section(
                    "Cross-functional approval",
                    [
                        "Finance may cap cash; ops may cap warehouse hours; growth may want promos. <a href=\"/blog/warehouse-team-roles-access/index.html\">Role-based access</a> keeps everyone looking at the same numbers while permissions stay appropriate.",
                    ],
                ),
            ]
        ),
        "cta_title": "Buy to margin, not to hype",
        "cta_desc": "Use Profitru to connect PO discipline with SKU economics.",
    },
    "dispatch-fulfilment-operations": {
        "category": "Product",
        "h1": "Dispatch and fulfilment operations without ghost units",
        "doc_title": "Dispatch &amp; fulfilment for ecommerce &mdash; Profitru Blog",
        "meta_desc": "Pick, pack, ship, and status visibility that keeps warehouse events aligned with channel promises and inventory.",
        "og_title": "Dispatch &amp; fulfilment | Profitru Blog",
        "og_desc": "From pick-pack to tracking IDs tied to SKU movement.",
        "tw_title": "Dispatch operations | Profitru Blog",
        "json_headline": "Dispatch and fulfilment operations for Indian ecommerce",
        "json_desc": "Operational dispatch aligned with inventory and channels.",
        "intro": """Dispatch is where customer promise meets the floor. When shipment files lag or SKUs are swapped, you get &ldquo;ghost&rdquo; inventory that breaks both <a href=\"/blog/inventory-management-ecommerce/index.html\">stock trust</a> and <a href=\"/blog/sku-profit-calculation-india/index.html\">profit</a>. This note expands the dispatch thread inside <a href=\"/blog/warehouse-management-software/index.html\">warehouse &amp; marketplace operations</a>.""",
        "body": "\n        ".join(
            [
                section(
                    "The dispatch record you actually need",
                    [
                        "Minimum viable traceability: order id, channel, SKU, quantity picked, pack station or batch, carrier, tracking id, and dispatch timestamp. Without those, you cannot reconcile returns or claims confidently.",
                    ],
                ),
                section(
                    "SLA and exception queues",
                    [
                        "Late cut-offs, partial picks, and inter-warehouse transfers should surface as exceptions, not buried rows. Exceptions are inputs to <a href=\"/blog/spf-claims-reimbursement-tracking/index.html\">claims</a> when carriers or marketplaces owe you money.",
                    ],
                ),
                section(
                    "Multi-channel cut-over",
                    [
                        "If the same physical unit can fulfil Amazon or Flipkart depending on priority rules, your system must record which promise consumed which stock. That is the same multi-channel discipline as <a href=\"../../multi-channel-profit-calculator/index.html\">one net margin story</a>, applied to operations.",
                    ],
                ),
            ]
        ),
        "cta_title": "Tighten dispatch without new integrations",
        "cta_desc": "Upload carrier and order files; keep ops and inventory aligned.",
    },
    "ecommerce-returns-qc": {
        "category": "Product",
        "h1": "Ecommerce returns, QC, and margin you can explain",
        "doc_title": "Returns &amp; QC for ecommerce &mdash; Profitru Blog",
        "meta_desc": "Model returns and quality checks so restock, scrap, and margin impacts are visible per SKU\u2014for marketplaces and D2C.",
        "og_title": "Ecommerce returns &amp; QC | Profitru Blog",
        "og_desc": "Returns that update inventory and profit honestly.",
        "tw_title": "Returns &amp; QC | Profitru Blog",
        "json_headline": "Ecommerce returns and QC for Indian sellers",
        "json_desc": "Return dispositions tied to inventory and SKU margin.",
        "intro": """Returns are not a single number; they are a workflow with financial outcomes. Profitru matches the homepage promise on <a href="/#features">returns that make sense</a>&mdash;tied to <a href=\"/blog/inventory-management-ecommerce/index.html\">inventory</a> and <a href=\"/blog/sku-profit-calculation-india/index.html\">profit</a>. For D2C, pair with <a href=\"../d2c-cod-and-margin/index.html\">COD and RTO</a>.""",
        "body": "\n        ".join(
            [
                section(
                    "Disposition buckets",
                    [
                        "Every return should land in a bucket with an inventory and margin consequence: resellable as new, open-box discount, refurbish, vendor return, liquidate, scrap, or donor. &ldquo;Returned&rdquo; alone is not enough for finance.",
                    ],
                    [
                        "QC checklist by category (electronics vs apparel vs consumables)",
                        "Photo or note evidence for disputes",
                        "Link to carrier or marketplace claim when damage is not your fault",
                    ],
                ),
                section(
                    "Timing and cut-offs",
                    [
                        "Return windows differ by channel and programme. Late postings create phantom stock if you recognise revenue early. Align accounting policy with ops reality&mdash;your CA remains the final word on recognition.",
                    ],
                ),
                section(
                    "Feeds profit models",
                    [
                        "Once dispositions are clean, return rate becomes a trustworthy input to <a href=\"/blog/procurement-reorder-planning/index.html\">procurement</a> and to channel mix decisions, not a debate in the hallway.",
                    ],
                ),
            ]
        ),
        "cta_title": "Make returns part of one SKU story",
        "cta_desc": "Structure QC outcomes so inventory and margin stay honest.",
    },
    "spf-claims-reimbursement-tracking": {
        "category": "Product",
        "h1": "SPF and reimbursement claims next to operations",
        "doc_title": "SPF &amp; reimbursement claims &mdash; Profitru Blog",
        "meta_desc": "Track marketplace claims and reimbursements alongside returns and dispatch so finance recovers what operations already proved.",
        "og_title": "SPF &amp; claims tracking | Profitru Blog",
        "og_desc": "Claims, returns, and settlements in one operational thread.",
        "tw_title": "Claims tracking | Profitru Blog",
        "json_headline": "SPF and reimbursement claim tracking for ecommerce",
        "json_desc": "Link claims to returns, dispatch, and settlements.",
        "intro": """Claims fail for two reasons: missing proof, or finance never hears ops finish the story. Profitru is designed so <a href=\"/blog/dispatch-fulfilment-operations/index.html\">dispatch</a> and <a href=\"/blog/ecommerce-returns-qc/index.html\">returns</a> events can sit beside claim status&mdash;and so you remember to read <a href=\"../amazon-payout-vs-real-profit/index.html\">what payouts still hide</a> for Amazon India.""",
        "body": "\n        ".join(
            [
                section(
                    "Evidence chain",
                    [
                        "Claims need SKU, quantity, rupee expectation, reason code, and linkage to inbound/outbound proof. If your WMS and finance inbox are different systems, evidence rots in email.",
                    ],
                ),
                section(
                    "Statuses finance can audit",
                    [
                        "Draft, filed, in review, approved, partially paid, rejected, and appealed should be explicit. Partial approvals are common; your model should not assume binary outcomes.",
                    ],
                ),
                section(
                    "Cadence and ownership",
                    [
                        "Assign an owner and a weekly review. Unclaimed losses are often a process problem, not a policy problem. Tie recovered amounts back to <a href=\"/blog/sku-profit-calculation-india/index.html\">SKU profit</a> so leadership sees impact.",
                    ],
                ),
            ]
        ),
        "cta_title": "Recover revenue without losing the paper trail",
        "cta_desc": "Track claims with the same uploads you already use for ops.",
    },
    "marketplace-data-export-csv": {
        "category": "Product",
        "h1": "Marketplace exports, CSV uploads, and structured truth",
        "doc_title": "Platform exports &amp; CSV workflows &mdash; Profitru Blog",
        "meta_desc": "How Profitru ingests bulk marketplace and ops files so you can start without APIs\u2014and keep a repeatable upload cadence.",
        "og_title": "Marketplace CSV &amp; exports | Profitru Blog",
        "og_desc": "Bulk data in from the files you already download.",
        "tw_title": "CSV uploads | Profitru Blog",
        "json_headline": "Marketplace data exports and CSV uploads for Profitru",
        "json_desc": "Bulk uploads instead of live integrations.",
        "intro": """Profitru deliberately uses <a href="/#faq">bulk uploads</a> instead of fragile marketplace OAuth. This article is the how: which exports matter, how often to refresh them, and how they feed <a href=\"/blog/profitru-platform-overview/index.html\">the rest of the platform</a>.""",
        "body": "\n        ".join(
            [
                section(
                    "What you typically export",
                    [
                        "Orders, settlements or payouts, inventory snapshots, returns, advertising where available, and tax summaries your CA recognises. Exact filenames change; the discipline does not.",
                    ],
                ),
                section(
                    "Normalisation and mapping",
                    [
                        "The first week is mapping SKUs, warehouses, and channel codes. Invest here once; shortcuts become expensive rework. <a href=\"/blog/warehouse-team-roles-access/index.html\">Access controls</a> help limit who can change mappings.",
                    ],
                ),
                section(
                    "Exports back out",
                    [
                        "Finance and partners often need CSV or spreadsheet views of reconciled profit and inventory. Plan exports the same way you plan uploads: versioned, dated, and owned.",
                    ],
                ),
            ]
        ),
        "cta_title": "Start with files you already have",
        "cta_desc": "No integrations required&mdash;upload and iterate weekly.",
    },
    "warehouse-team-roles-access": {
        "category": "Product",
        "h1": "Team roles, permissions, and one operational truth",
        "doc_title": "Warehouse &amp; finance user access &mdash; Profitru Blog",
        "meta_desc": "Give finance, warehouse, and growth the views they need without fragmenting SKU truth\u2014roles and accountability in Profitru.",
        "og_title": "Team roles &amp; access | Profitru Blog",
        "og_desc": "Finance, ops, and warehouse aligned on the same numbers.",
        "tw_title": "User roles | Profitru Blog",
        "json_headline": "Team roles and access for ecommerce operations",
        "json_desc": "Role-based access with shared operational truth.",
        "intro": """The homepage calls this <a href="/#features">one operational truth across teams</a>. In practice, that means permissions: who can change COGS mappings, who can approve dispositions, and who can only read dashboards. This article complements <a href=\"/blog/marketplace-data-export-csv/index.html\">CSV governance</a>.""",
        "body": "\n        ".join(
            [
                section(
                    "Why roles fail in spreadsheets",
                    [
                        "Shared drives multiply conflicting copies. Email approvals disappear. Profitru centralises numbers so arguments are about decisions, not about which file is newest.",
                    ],
                ),
                section(
                    "Suggested separation of duties",
                    [
                        "Finance owns chart-of-accounts level mappings and tax treatment sign-off.",
                        "Warehouse owns dispatch, returns QC, and physical adjustments with evidence.",
                        "Growth owns campaign tags and promo calendars that explain spikes&mdash;not silent overrides to margin.",
                    ],
                ),
                section(
                    "Audit trail mindset",
                    [
                        "Even without formal SOX, Indian brands benefit from knowing who changed a mapping and when. That trail makes <a href=\"/blog/spf-claims-reimbursement-tracking/index.html\">claims</a> and investor diligence less painful.",
                    ],
                ),
            ]
        ),
        "cta_title": "Put everyone on the same SKU graph",
        "cta_desc": "Use Profitru so permissions match how you actually run the business.",
    },
    "ai-profit-assistant-pro": {
        "category": "Product",
        "h1": "AI Profit Assistant on Pro: signals, not noise",
        "doc_title": "AI Profit Assistant (Pro) &mdash; Profitru Blog",
        "meta_desc": "How Profitru Pro uses AI-assisted signals to surface margin risk, demand shifts, and operational anomalies early.",
        "og_title": "AI Profit Assistant | Profitru Blog",
        "og_desc": "Early warnings on margin and operations\u2014built on your structured data.",
        "tw_title": "AI Profit Assistant | Profitru Blog",
        "json_headline": "AI Profit Assistant for ecommerce profit and operations",
        "json_desc": "AI-powered signals for Pro customers on Profitru.",
        "intro": """The <a href="/#demo">AI Profit Assistant</a> on the homepage is a Pro capability: it highlights risks and opportunities once your uploads give Profitru enough structure. It does not replace <a href=\"/blog/sku-profit-calculation-india/index.html\">SKU economics</a> or your CA; it prioritises what humans should look at this week.""",
        "body": "\n        ".join(
            [
                section(
                    "What good signals require",
                    [
                        "AI is only as grounded as the data model. Stable SKU mappings, clean return dispositions, and consistent upload cadence matter more than model buzzwords.",
                    ],
                ),
                section(
                    "Examples of useful prompts",
                    [
                        "SKUs where margin improved but return rate worsened (quality or listing problem?)",
                        "Channels where ad spend rose but net contribution fell",
                        "Inventory ageing buckets that conflict with procurement plans",
                    ],
                ),
                section(
                    "Human in the loop",
                    [
                        "Profitru assumes operators approve actions. The assistant proposes; your team decides, especially on procurement and pricing moves that touch customer trust.",
                    ],
                ),
            ]
        ),
        "cta_title": "Upgrade to structured data, then add AI",
        "cta_desc": "Start on Profitru; explore Pro when your baseline uploads are steady.",
    },
}


def render_one(slug: str, data: dict) -> None:
    canonical = f"{CANON}/{slug}/index.html"
    json_ld = build_json_ld(data["json_headline"], data["json_desc"], canonical)
    series_html = series_cards_html(slug)
    page = HEAD_TOP.format(
        meta_desc=esc(data["meta_desc"]),
        canonical=canonical,
        og_title=esc(data["og_title"]),
        og_desc=esc(data["og_desc"]),
        tw_title=esc(data["tw_title"]),
        json_ld=json_ld,
        doc_title=data["doc_title"],
        DATE_DISP=DATE_DISP,
        category=data["category"],
        h1=data["h1"],
        intro=data["intro"],
        body=data["body"],
        series_cards=series_html,
        cta_title=data["cta_title"],
        cta_desc=data["cta_desc"],
    )
    out_dir = BLOG / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(page, encoding="utf-8")
    print(f"Wrote {slug}/index.html")


def main() -> None:
    n = 0
    for slug in SERIES_ORDER:
        if slug == "warehouse-management-software":
            continue  # Hand-maintained page
        render_one(slug, ARTICLES[slug])
        n += 1
    print("Done:", n, "posts rendered (warehouse article unchanged)")


if __name__ == "__main__":
    main()
